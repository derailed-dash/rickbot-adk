import json
import os
import subprocess
import threading
import time

import pytest
import requests
from requests.exceptions import RequestException

# PORT for this specific test to avoid conflicts
PORT = 8001
BASE_URL = f"http://127.0.0.1:{PORT}"
STREAM_URL = f"{BASE_URL}/chat_stream"


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
    env["BACKEND_ALLOW_MOCK_AUTH"] = "true"

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


def test_tool_status_in_stream(server):
    """Test that tool calls are reported in the stream."""
    headers = {"Authorization": "Bearer mock:123:test@example.com:Tester"}
    # We ask something that triggers a tool. Dazbot uses Search.
    # We'll use Dazbot to increase chances of tool call.
    data = {"prompt": "Please use your search tool to find the current stock price of GOOGL.", "personality": "Rick"}

    response = requests.post(STREAM_URL, data=data, headers=headers, stream=True)
    assert response.status_code == 200

    found_tool_call = False
    for line in response.iter_lines():
        if line:
            decoded = line.decode("utf-8")
            if decoded.startswith("data: "):
                payload = json.loads(decoded[6:])
                print(f"Received payload: {payload}")
                if "tool_call" in payload:
                    found_tool_call = True
                    break

    assert found_tool_call, (
        "No tool_call event received in the stream. Note: This test requires the LLM to actually decide to use a tool."
    )
