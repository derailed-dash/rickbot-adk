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

import uuid
import json
import asyncio
from typing import Annotated, AsyncGenerator

from fastapi import FastAPI, Form, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from google.adk.runners import Runner
from google.genai.types import Blob, Content, Part
from pydantic import BaseModel

from rickbot_agent.agent import get_agent
from rickbot_agent.services import get_artifact_service, get_session_service
from rickbot_utils.config import logger

APP_NAME = "rickbot_api"


class ChatResponse(BaseModel):
    """Response model for the chat endpoint."""

    response: str
    session_id: str
    attachments: list[Part] | None = None  # Support for multimodal response


logger.debug("Initialising FastAPI app...")
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services and runner on startup
logger.debug("Initialising services...")
session_service = get_session_service()
artifact_service = get_artifact_service()


@app.post("/chat")
async def chat(
    prompt: Annotated[str, Form()],
    session_id: Annotated[str | None, Form()] = None,
    personality: Annotated[str, Form()] = "Rick",
    user_id: Annotated[str, Form()] = "api-user",
    file: UploadFile | None = None,
) -> ChatResponse:
    """Chat endpoint to interact with the Rickbot agent."""
    logger.debug(f"Received chat request - "
                 f"Personality: {personality}, User ID: {user_id}, Session ID: {session_id if session_id else 'None'}")

    current_session_id = session_id if session_id else str(uuid.uuid4())

    # Get the session, or create it if it doesn't exist
    session = await session_service.get_session(
        session_id=current_session_id, user_id=user_id, app_name=APP_NAME
    )
    if not session:
        logger.debug(f"Creating new session: {current_session_id}")
        session = await session_service.create_session(
            session_id=current_session_id, user_id=user_id, app_name=APP_NAME
        )
    else:
        logger.debug(f"Found existing session: {current_session_id}")

    # Get the correct agent personality (lazily loaded and cached)
    logger.debug(f"Loading agent for personality: '{personality}'")
    agent = get_agent(personality)

    # Construct the message parts
    parts = [Part.from_text(text=prompt)]

    # Add any files to the message
    if file and file.filename:
        logger.debug(f"Processing uploaded file: {file.filename} ({file.content_type})")
        file_content = await file.read()
        # Create a Part object for the agent to process
        parts.append(Part(inline_data=Blob(data=file_content, mime_type=file.content_type)))
    elif file is not None:
        logger.warning(f"file was set to '{file}' - will not be processed")

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
    user_id: Annotated[str, Form()] = "api-user",
    file: UploadFile | None = None,
) -> StreamingResponse:
    """Streaming chat endpoint to interact with the Rickbot agent."""
    logger.debug(f"Received chat stream request - "
                 f"Personality: {personality}, User ID: {user_id}, Session ID: {session_id if session_id else 'None'}")

    current_session_id = session_id if session_id else str(uuid.uuid4())

    # Get the session, or create it if it doesn't exist
    session = await session_service.get_session(
        session_id=current_session_id, user_id=user_id, app_name=APP_NAME
    )
    if not session:
        logger.debug(f"Creating new session: {current_session_id}")
        session = await session_service.create_session(
            session_id=current_session_id, user_id=user_id, app_name=APP_NAME
        )
    else:
        logger.debug(f"Found existing session: {current_session_id}")

    # Get the correct agent personality (lazily loaded and cached)
    logger.debug(f"Loading agent for personality: '{personality}'")
    agent = get_agent(personality)

    # Construct the message parts
    parts = [Part.from_text(text=prompt)]

    # Add any files to the message
    if file and file.filename:
        logger.debug(f"Processing uploaded file: {file.filename} ({file.content_type})")
        file_content = await file.read()
        # Create a Part object for the agent to process
        parts.append(Part(inline_data=Blob(data=file_content, mime_type=file.content_type)))
    elif file is not None:
        logger.warning(f"file was set to '{file}' - will not be processed")

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

        async for event in runner.run_async(
            user_id=user_id,
            session_id=current_session_id,
            new_message=new_message,
        ):
             if event.is_model_response():
                 # For model responses, we want to stream the chunks
                 # Note: The `event` object in run_async might be a ModelResponseEvent or similar.
                 # Depending on ADK version, `event.content.parts` might contain full text or chunks.
                 # But ADK's `run_async` typically yields events as they happen.
                 # If `event` has text, we send it.
                 if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            yield f"data: {json.dumps({'chunk': part.text})}\n\n"

        yield f"data: {json.dumps({'done': True})}\n\n"


    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/")
def read_root():
    """Root endpoint for the API."""
    return {"Hello": "World"}
