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

import json
import uuid
from collections.abc import AsyncGenerator
from os import getenv
from typing import Annotated

from fastapi import Depends, FastAPI, File, Form, HTTPException, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from google.adk.runners import Runner
from google.genai.types import Content, Part
from pydantic import BaseModel
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from rickbot_agent.agent import get_agent
from rickbot_agent.auth import verify_token
from rickbot_agent.auth_models import AuthUser
from rickbot_agent.personality import get_personalities
from rickbot_agent.services import get_artifact_service, get_session_service
from rickbot_utils.config import logger
from rickbot_utils.rate_limit import limiter

APP_NAME = "rickbot_api"


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
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/personas")
def get_personas(user: AuthUser = Depends(verify_token)) -> list[Persona]:
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


@app.post("/chat")
async def chat(
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
                logger.info(f"Session {current_session_id} calling tool: {fc.name}")
        if event.actions and event.actions.transfer_to_agent:
            logger.info(f"Session {current_session_id} transferring to agent: {event.actions.transfer_to_agent}")

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


@app.post("/chat_stream")
async def chat_stream(
    prompt: Annotated[str, Form()],
    session_id: Annotated[str | None, Form()] = None,
    personality: Annotated[str, Form()] = "Rick",
    user: AuthUser = Depends(verify_token),
    files: list[UploadFile] = File(default=[]),
) -> StreamingResponse:
    """Streaming chat endpoint to interact with the Rickbot agent."""
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
            async for event in runner.run_async(
                user_id=user_id,
                session_id=current_session_id,
                new_message=new_message,
            ):
                # logger.debug(f"Event received: {event}") # Too verbose

                if hasattr(event, "finish_reason") and event.finish_reason:
                    logger.debug(f"Event finish reason: {event.finish_reason}")

                # Check for tool calls
                if function_calls := event.get_function_calls():
                    for fc in function_calls:
                        logger.info(f"Tool Call: {fc.name}")
                        yield f"data: {json.dumps({'tool_call': {'name': fc.name, 'args': fc.args}})}\n\n"

                # Check for tool responses
                if function_responses := event.get_function_responses():
                    for fr in function_responses:
                        logger.info(f"Tool Response: {fr.name}")
                        yield f"data: {json.dumps({'tool_response': {'name': fr.name}})}\n\n"

                # Check for agent transfers
                if event.actions and event.actions.transfer_to_agent:
                    logger.info(f"Agent Transfer: {event.actions.transfer_to_agent}")
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

        except Exception as e:
            logger.error(f"Error in event generator: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/")
def read_root():
    """Root endpoint for the API."""
    return {"Hello": "World"}


@app.get("/artifacts/{filename}")
async def get_artifact(filename: str, user: AuthUser = Depends(verify_token)) -> Response:
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
