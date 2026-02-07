"""Rickbot-ADK FastAPI Application

This module defines the main FastAPI application for the Rickbot-ADK project.
It serves as the API layer, providing a `/chat` endpoint for interacting with
the Rickbot agent personalities.

Key functionalities include:
- Initializing ADK services (InMemorySessionService, InMemoryArtifactService).
- Lazily loading agent personalities based on request.
- Handling multimodal input (text prompts and optional file uploads).
- Orchestrating agent interactions using the ADK Runner.
- Managing conversational sessions and artifacts.
- Returning multimodal responses (text and optional attachments).

Notes:
- As described in https://fastapi.tiangolo.com/tutorial/request-forms/ the HTTP protocol defines that:
  - Request data to an API would normally be sent as plain old JSON ("Body") data, encoded as application/json.
  - BUT, data that optionally includes files must be sent as Form data, not Body data.
  - Form data will be encoded with the media type application/x-www-form-urlencoded, if not included files;
    or multipart/form-data, if files are included.
"""

import asyncio
import json
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime
from os import getenv
from typing import Annotated, Any

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from rickbot_agent.agent import get_agent
from rickbot_agent.auth import verify_token, verify_credentials
from rickbot_agent.auth_middleware import AuthMiddleware
from rickbot_agent.auth_models import AuthUser, PersonaAccessDeniedException
from rickbot_agent.personality import get_personalities
from rickbot_agent.services import get_artifact_service, get_session_service, get_required_role, get_user_role

# ADK imports MUST happen after agent patch
from google.adk.runners import Runner
from google.genai.types import Content, Part

from rickbot_utils.config import logger
from rickbot_utils.rate_limit import limiter

APP_NAME = getenv("APP_NAME", "rickbot_api")

# SSE (Server-Sent Events) padding constant
# This forces network buffers to flush immediately, ensuring the UI receives
# "Thinking..." indicators without delay. 4KB is a common buffer size threshold.
SSE_FLUSH_PADDING_BYTES = 4096


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Custom handler for rate limit exceeded errors."""
    response = JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded: {exc.detail}"}
    )
    # Add Retry-After header (defaulting to 60s)
    response.headers["Retry-After"] = "60"
    return response


def persona_access_denied_handler(request: Request, exc: PersonaAccessDeniedException) -> JSONResponse:
    """Custom handler for persona access denial."""
    return JSONResponse(
        status_code=403,
        content={
            "error_code": "UPGRADE_REQUIRED",
            "detail": exc.detail,
            "required_role": exc.required_role,
            "personality": exc.personality,
        },
    )


# Override the default slowapi exception handler so that the middleware uses our custom response
limiter._exception_handler = rate_limit_exceeded_handler


class ChatResponse(BaseModel):
    """Response model for the chat endpoint."""

    response: str
    session_id: str
    attachments: list[Part] | None = None  # Support for multimodal response


class Persona(BaseModel):
    """Model for a chatbot personality."""

    name: str
    description: str
    avatar: str
    title: str
    overview: str
    welcome: str
    prompt_question: str


logger.debug("Initialising FastAPI app...")
app = FastAPI()

# Add Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)  # type: ignore
app.add_exception_handler(PersonaAccessDeniedException, persona_access_denied_handler)  # type: ignore
app.add_middleware(SlowAPIMiddleware)
# Note on Middleware Order:
# FastAPI/Starlette middlewares are executed LIFO (Last Added = First Executed).
# AuthMiddleware must execute FIRST to set request.state.user.
# Order of adding (LIFO):
# 1. AuthMiddleware
# Execution Order:
# Request -> AuthMiddleware -> SlowAPIMiddleware -> ...
app.add_middleware(AuthMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def check_persona_access(
    personality: Annotated[str, Form()] = "Rick",
    user: AuthUser = Depends(verify_token),
) -> None:
    """Dependency to check if the user has access to the requested persona."""
    required_role = get_required_role(personality)
    user_role = "standard"
    if user:
        # Sync user metadata (ID, email, name, last_logged_in)
        from rickbot_agent.services import sync_user_metadata
        sync_user_metadata(user.id, user.email, user.name)
        
        user_role = get_user_role(user.id)
        logger.info(f"RBAC Check: user_id='{user.id}', provider='{user.provider}', role='{user_role}', persona='{personality}', required='{required_role}'")

    if required_role == "supporter" and user_role != "supporter":
        logger.warning(f"RBAC DENIED: user_id='{user.id}', role='{user_role}' lacks required role '{required_role}' for '{personality}'")
        raise PersonaAccessDeniedException(personality, required_role)
        logger.info(f"Access Denied: user={user.id if user else 'anonymous'} to {personality}")
        raise PersonaAccessDeniedException(personality, required_role)


@app.get("/personas")
def get_personas(request: Request, user: AuthUser = Depends(verify_token)) -> list[Persona]:
    """Returns a list of available chatbot personalities."""
    personalities = get_personalities()
    return [
        Persona(
            name=p.name,
            description=p.menu_name,
            avatar=f"/avatars/{p.name.lower()}.png",
            title=p.title,
            overview=p.overview,
            welcome=p.welcome,
            prompt_question=p.prompt_question,
        )
        for p in personalities.values()
    ]


# Initialize services and runner on startup
logger.debug("Initialising services...")
session_service = get_session_service()
artifact_service = get_artifact_service()


async def _process_files(
    files: list[UploadFile],
    user_id: str,
    session_id: str,
    artifact_service,
) -> list[Part]:
    """Helper function to process uploaded files."""
    parts = []
    if files:
        for f in files:
            if not f.filename:
                continue
            logger.debug(f"Processing uploaded file: {f.filename} ({f.content_type})")
            file_content = await f.read()

            # Save as Artifact (User-scoped)
            # Note: if user uploads a file with the same name, it will be overwritten.
            artifact_filename = f"user:{f.filename}"
            mime_type = f.content_type or "application/octet-stream"
            artifact_part = Part.from_bytes(data=file_content, mime_type=mime_type)
            await artifact_service.save_artifact(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=session_id,
                filename=artifact_filename,
                artifact=artifact_part,
            )

            # Create a Part object for the agent to process
            parts.append(artifact_part)
    # No warning needed for empty list, only if files is explicitly None (which shouldn't happen with default=[])

    return parts


@app.post("/chat", dependencies=[Depends(check_persona_access)])
@limiter.limit("5 per minute")
async def chat(
    request: Request,
    prompt: Annotated[str, Form()],
    session_id: Annotated[str | None, Form()] = None,
    personality: Annotated[str, Form()] = "Rick",
    user: AuthUser = Depends(verify_token),
    files: list[UploadFile] = File(default=[]),
) -> ChatResponse:
    """Chat endpoint to interact with the Rickbot agent."""
    user_id = user.email  # Use email as user_id for ADK sessions
    logger.debug(
        f"Received chat request - "
        f"Personality: {personality}, User: {user.email}, Session ID: {session_id if session_id else 'None'}"
    )

    current_session_id = session_id if session_id else str(uuid.uuid4())

    # Get the session, or create it if it doesn't exist
    session = await session_service.get_session(session_id=current_session_id, user_id=user_id, app_name=APP_NAME)
    if not session:
        logger.debug(f"Creating new session: {current_session_id}")
        session = await session_service.create_session(session_id=current_session_id, user_id=user_id, app_name=APP_NAME)
    else:
        logger.debug(f"Found existing session: {current_session_id}")

    # Get the correct agent personality (lazily loaded and cached)
    logger.debug(f"Loading agent for personality: '{personality}'")
    agent = get_agent(personality)

    # Construct the message parts
    parts = [Part.from_text(text=prompt)]

    # Add any files to the message
    file_parts = await _process_files(files, user_id, current_session_id, artifact_service)
    parts.extend(file_parts)

    # Associate the role with the message
    new_message = Content(role="user", parts=parts)

    # Create the runner
    runner = Runner(
        agent=agent,
        app_name=APP_NAME,
        session_service=session_service,
        artifact_service=artifact_service,
    )

    # Run the agent and extract response and attachments
    logger.debug(f"Running agent for session: {current_session_id}")
    final_msg = ""
    response_attachments: list[Part] = []
    async for event in runner.run_async(
        user_id=user_id,
        session_id=current_session_id,
        new_message=new_message,
    ):
        # Log tool calls and transfers
        if function_calls := event.get_function_calls():
            for fc in function_calls:
                logger.debug(f"Session {current_session_id} calling tool: {fc.name}")
        if event.actions and event.actions.transfer_to_agent:
            logger.debug(f"Session {current_session_id} transferring to agent: {event.actions.transfer_to_agent}")

        if event.is_final_response() and event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    final_msg += part.text
                elif part.inline_data:  # Check for other types of parts (e.g., images)
                    response_attachments.append(part)

    logger.debug(f"Agent for session {current_session_id} finished.")
    logger.debug(f"Final message snippet: {final_msg[:100]}...")

    return ChatResponse(
        response=final_msg,
        session_id=current_session_id,
        attachments=response_attachments if response_attachments else None,
    )


@app.post("/chat_stream", dependencies=[Depends(check_persona_access)])
@limiter.limit("5 per minute")
async def chat_stream(
    request: Request,
    prompt: Annotated[str, Form()],
    session_id: Annotated[str | None, Form()] = None,
    personality: Annotated[str, Form()] = "Rick",
    user: AuthUser = Depends(verify_token),
    files: list[UploadFile] = File(default=[]),
) -> StreamingResponse:
    """Streaming chat endpoint to interact with the Rickbot agent."""
    logger.debug(f"DEBUG: chat_stream ENTERED. user={user.id}, personality={personality}")
    user_id = user.email  # Use email as user_id for ADK sessions
    logger.debug(
        f"Received chat stream request - "
        f"Personality: {personality}, User: {user.email}, Session ID: {session_id if session_id else 'None'}"
    )

    current_session_id = session_id if session_id else str(uuid.uuid4())

    # Get the session, or create it if it doesn't exist
    session = await session_service.get_session(session_id=current_session_id, user_id=user_id, app_name=APP_NAME)
    if not session:
        logger.debug(f"Creating new session: {current_session_id}")
        session = await session_service.create_session(session_id=current_session_id, user_id=user_id, app_name=APP_NAME)
    else:
        logger.debug(f"Found existing session: {current_session_id}")

    # Get the correct agent personality (lazily loaded and cached)
    logger.debug(f"Loading agent for personality: '{personality}'")
    agent = get_agent(personality)

    # Construct the message parts
    parts = [Part.from_text(text=prompt)]

    # Add any files to the message
    file_parts = await _process_files(files, user_id, current_session_id, artifact_service)
    parts.extend(file_parts)

    # Associate the role with the message
    new_message = Content(role="user", parts=parts)

    # Create the runner
    runner = Runner(
        agent=agent,
        app_name=APP_NAME,
        session_service=session_service,
        artifact_service=artifact_service,
    )

    async def event_generator() -> AsyncGenerator[str, None]:
        # Yield the session ID first
        yield f"data: {json.dumps({'session_id': current_session_id})}\n\n"

        try:
            # Create a queue for the events and the heartbeat
            queue: asyncio.Queue[Any] = asyncio.Queue()

            async def push_events():
                try:
                    async for event in runner.run_async(
                        user_id=user_id,
                        session_id=current_session_id,
                        new_message=new_message,
                    ):
                        await queue.put(event)
                    await queue.put(None)  # Signal completion
                except Exception as e:
                    logger.error(f"Error in runner.run_async: {e}", exc_info=True)
                    await queue.put(e)

            async def heartbeat():
                while True:
                    await asyncio.sleep(15)
                    await queue.put("heartbeat")

            # Start background tasks
            event_task = asyncio.create_task(push_events())
            heartbeat_task = asyncio.create_task(heartbeat())

            try:
                while True:
                    item = await queue.get()
                    if item is None:  # Done
                        break
                    if isinstance(item, Exception):
                        raise item
                    if item == "heartbeat":
                        # Send a comment as a heartbeat to keep the connection alive
                        logger.debug(f"[{datetime.now().isoformat()}] Sending SSE heartbeat")
                        yield ": heartbeat\n\n"
                        continue

                    event = item
                    timestamp = datetime.now().isoformat()
                    # Debug logging for event type
                    logger.debug(f"[{timestamp}] Received ADK event: {type(event).__name__}")
                    yield f"data: {json.dumps({'debug': {'event_type': type(event).__name__, 'ts': timestamp}})}\n\n"

                    if hasattr(event, "finish_reason") and event.finish_reason:
                        logger.debug(f"Event finish reason: {event.finish_reason}")

                    # Check for tool calls
                    if function_calls := event.get_function_calls():
                        for fc in function_calls:
                            logger.debug(f"Tool Call: {fc.name} Args: {fc.args}")
                            yield f"data: {json.dumps({'tool_call': {'name': fc.name, 'args': fc.args}})}\n\n"

                    # Check for tool responses
                    if function_responses := event.get_function_responses():
                        for fr in function_responses:
                            logger.debug(f"Tool Response: {fr.name}")
                            yield f"data: {json.dumps({'tool_response': {'name': fr.name}})}\n\n"

                    # Check for agent transfers
                    if event.actions and event.actions.transfer_to_agent:
                        logger.debug(f"Agent Transfer: {event.actions.transfer_to_agent}")
                        yield f"data: {json.dumps({'agent_transfer': event.actions.transfer_to_agent})}\n\n"

                    # For model responses, we want to stream the chunks
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.text:
                                yield f"data: {json.dumps({'chunk': part.text})}\n\n"
                            elif not (part.function_call or part.function_response):
                                logger.debug("Received part with no text data.")
                    else:
                        logger.debug("Event contained no content parts.")

            finally:
                heartbeat_task.cancel()
                try:
                    await heartbeat_task
                except asyncio.CancelledError:
                    pass
                if not event_task.done():
                    event_task.cancel()
                    try:
                        await event_task
                    except asyncio.CancelledError:
                        pass

        except asyncio.CancelledError:
            logger.info(f"Client disconnected or request cancelled for session: {current_session_id}")
            raise
        except Exception as e:
            logger.error(f"Error in event generator: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': 'An internal error occurred'})}\n\n"

        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            # Prevent caching by browsers and proxies
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            # Explicitly tell Nginx/Cloud Proxies NOT to buffer the stream.
            # Critical fix for "The Silence" problem.
            "X-Accel-Buffering": "no",
        },
    )

@app.get("/")
def read_root(request: Request):
    """Root endpoint for the API."""
    return {"Hello": "World"}


@app.get("/artifacts/{filename}")
async def get_artifact(filename: str, request: Request, user: AuthUser = Depends(verify_token)) -> Response:
    """Retrieves a saved artifact for the user."""
    user_id = user.email
    artifact_filename = f"user:{filename}"

    logger.debug(f"Retrieving artifact: {artifact_filename} for user: {user_id}")

    artifact = await artifact_service.load_artifact(
        app_name=APP_NAME,
        user_id=user_id,
        session_id="none",  # Ignored for user: scope
        filename=artifact_filename,
    )

    if not artifact or not artifact.inline_data:
        logger.warning(f"Artifact not found: {artifact_filename}")
        raise HTTPException(status_code=404, detail="Artifact not found")

    return Response(content=artifact.inline_data.data, media_type=artifact.inline_data.mime_type)
