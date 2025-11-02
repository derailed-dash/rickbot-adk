"""Main FastAPI application for the Rickbot-ADK API."""

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    """Root endpoint for the API."""
    return {"Hello": "World"}
