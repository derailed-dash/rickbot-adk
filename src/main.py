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
"""

import uuid

from fastapi import FastAPI, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from google.adk.runners import Runner
from google.genai.types import Blob, Content, Part
from pydantic import BaseModel

from rickbot_agent.agent import get_agent
from rickbot_agent.services import get_artifact_service, get_session_service
from rickbot_utils.config import logger

APP_NAME = "rickbot_api"


class ChatRequest(BaseModel):
    """Request model for the chat endpoint."""

    prompt: str
    personality: str
    user_id: str = "api-user"  # Default user_id if not provided by client
    session_id: str | None = None


class ChatResponse(BaseModel):
    """Response model for the chat endpoint."""

    response: str
    session_id: str
    attachments: list[Part] | None = None  # Added for multimodal responses


logger.debug("Initialising FastAPI app...")
app = FastAPI()

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
    prompt: str = Form(...),
    personality: str = Form(...),
    user_id: str = Form("api-user"),
    session_id: str | None = Form(None),
    file: UploadFile | None = None, # Changed to None to make it truly optional
) -> ChatResponse:
    """Chat endpoint to interact with the Rickbot agent."""
    current_session_id = session_id if session_id else str(uuid.uuid4())

    # 1. Get the session, or create it if it doesn't exist
    session = await session_service.get_session(
        session_id=current_session_id, user_id=user_id, app_name=APP_NAME
    )
    if not session:
        session = await session_service.create_session(
            session_id=current_session_id, user_id=user_id, app_name=APP_NAME
        )

    # 2. Get the correct agent personality (lazily loaded and cached)
    agent = get_agent(personality)

    # 3. Construct the message parts
    parts = [Part.from_text(text=prompt)]

    # 4. Add any files to the message
    if file and file.filename: # Check if a file was actually provided
        file_content = await file.read()
        # Create a Part object for the agent to process
        parts.append(Part(inline_data=Blob(data=file_content, mime_type=file.content_type)))

    # 5. Associate the role with the message
    new_message = Content(role="user", parts=parts)

    # 6. Create the runner
    runner = Runner(
        agent=agent,
        app_name=APP_NAME,
        session_service=session_service,
        artifact_service=artifact_service,
    )

    # 7. Run the agent and extract response and attachments
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

    return ChatResponse(
        response=final_msg,
        session_id=current_session_id,
        attachments=response_attachments if response_attachments else None,
    )


@app.get("/")
def read_root():
    """Root endpoint for the API."""
    return {"Hello": "World"}
