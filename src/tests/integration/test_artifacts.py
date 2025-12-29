import os
import subprocess
import threading
import time

import pytest
import requests
from requests.exceptions import RequestException

# PORT for this specific test to avoid conflicts
PORT = 8002
BASE_URL = f"http://127.0.0.1:{PORT}"
CHAT_URL = f"{BASE_URL}/chat"
ARTIFACT_URL = f"{BASE_URL}/artifacts"


def log_output(pipe, prefix):
    for line in iter(pipe.readline, ""):
        print(f"[{prefix}] {line.strip()}")


@pytest.fixture(scope="module")
def server():
    """Start the FastAPI server for the duration of the module."""
    command = ["uv", "run", "fastapi", "run", "src/main.py", "--port", str(PORT)]
    env = os.environ.copy()
    env["RICKBOT_TEST_MODE"] = "true"
    env["NEXT_PUBLIC_ALLOW_MOCK_AUTH"] = "true"

    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, env=env, cwd=os.getcwd()
    )

    threading.Thread(target=log_output, args=(process.stdout, "STDOUT"), daemon=True).start()
    threading.Thread(target=log_output, args=(process.stderr, "STDERR"), daemon=True).start()

    # Wait for server to start
    start_time = time.time()
    ready = False
    while time.time() - start_time < 30:
        try:
            response = requests.get(BASE_URL + "/", timeout=1)
            if response.status_code == 200:
                ready = True
                break
        except RequestException:
            pass
        time.sleep(1)

    if not ready:
        process.terminate()
        pytest.fail("Server failed to start in 30 seconds")

    yield process
    process.terminate()
    process.wait()


def test_file_upload_saves_artifact(server):
    """Test that file upload saves the file as an ADK Artifact and it can be retrieved."""
    headers = {"Authorization": "Bearer mock:123:test@example.com:Tester"}

    # We use a unique filename to avoid collision with other tests if any
    filename = f"test_artifact_{int(time.time())}.txt"
    file_content = b"Hello ADK Artifacts!"

    files = {"files": (filename, file_content, "text/plain")}
    data = {"prompt": "Describe this file.", "personality": "Rick"}

    print(f"Uploading file {filename}...")
    response = requests.post(CHAT_URL, data=data, files=files, headers=headers)
    assert response.status_code == 200, f"Upload failed: {response.text}"

    print(f"Retrieving artifact {filename}...")
    # Now try to retrieve the artifact
    # Note: ArtifactService is user-scoped in our design
    get_response = requests.get(f"{ARTIFACT_URL}/{filename}", headers=headers)
    assert get_response.status_code == 200, f"Retrieval failed: {get_response.text}"
    assert get_response.content == file_content
