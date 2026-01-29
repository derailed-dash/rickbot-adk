import os
import pytest

def test_dockerfiles_exist():
    """Verify that the required Dockerfiles for the sidecar architecture exist."""
    project_root = os.getcwd()
    required_files = [
        "Dockerfile.react_fe",
        "Dockerfile.api_sidecar"
    ]
    for file_name in required_files:
        file_path = os.path.join(project_root, file_name)
        assert os.path.exists(file_path), f"{file_name} is missing from the project root."

def test_streamlit_dockerfile_exists():
    """Verify that the legacy Streamlit Dockerfile exists."""
    assert os.path.exists("Dockerfile"), "The legacy Streamlit Dockerfile is missing."
