import os

import uvicorn
from google.adk.cli.fast_api import get_fast_api_app

from rickbot_agent.config import get_config, logger

config = get_config()
logger.debug(config)


app = get_fast_api_app(
    agents_dir=os.path.dirname(os.path.abspath(__file__)),
    session_service_uri="", # use in-memory
    artifact_service_uri="", # use in-memory
    allow_origins=["*"],
    web=True,
    # trace_to_cloud=True
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
