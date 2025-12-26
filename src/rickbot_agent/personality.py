"""
Configure personalities for Rickbot

We read a YAML file (data/personalities.yaml) to get the list of available characters.
For each character, dynamically load the corresponding system instruction, first by looking for a local text file and then,
if not found, by attempting to fetch it from Google Secret Manager.
"""

import logging
import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml  # pyyaml

from rickbot_utils.secret_utils import retrieve_secret

SCRIPT_DIR = Path(__file__).parent
logger = logging.getLogger(__name__)


def get_avatar(name: str) -> str:
    return str(SCRIPT_DIR / f"media/{name}.png")


@dataclass(unsafe_hash=True)
class Personality:
    """Represents a distinct chatbot personality, encapsulating its configuration."""

    name: str
    menu_name: str
    title: str
    overview: str
    welcome: str
    prompt_question: str
    temperature: float
    avatar: str = field(init=False)
    system_instruction: str = field(init=False)

    def __post_init__(self) -> None:
        self.avatar = get_avatar(self.name.lower())
        system_prompt_file = SCRIPT_DIR / "data/system_prompts" / f"{self.name.lower()}.txt"
        if os.path.exists(system_prompt_file):
            with open(system_prompt_file, encoding="utf-8") as f:
                self.system_instruction = f.read()
        else:
            logger.debug(f"Unable to find {system_prompt_file}. Attempting to retrieve from Secret Manager.")
            secret_name = f"{self.name.lower()}-system-prompt"
            try:
                google_project = os.environ.get("GOOGLE_CLOUD_PROJECT")
                if not google_project:
                    raise ValueError("GOOGLE_CLOUD_PROJECT environment variable not set, and local prompt file not found.")
                self.system_instruction = retrieve_secret(google_project, secret_name)
                logger.info("Successfully retrieved.")
            except Exception as e:
                logger.error(f"Unable to retrieve '{secret_name}' from Secret Manager.")

                # Check for Test Mode
                if os.environ.get("RICKBOT_TEST_MODE") == "true":
                    logger.warning(f"TEST MODE: Using dummy prompt for {self.name} because secret was not found.")
                    self.system_instruction = f"You are {self.name}. (DUMMY PROMPT FOR TESTING)"
                else:
                    raise ValueError(
                        f"{system_prompt_file} not found and could not access '{secret_name}' from Secret Manager: {e}"
                    ) from e

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(name={self.name!r},title={self.title!r},overview={self.overview!r},temperature={self.temperature!r})"
        )

    def __str__(self) -> str:
        return f"{self.name}: {self.overview}"


def _load_personalities(yaml_file: str) -> dict[str, Personality]:
    """Internal function to load personalities from a YAML file."""
    peeps: dict[str, Personality] = {}
    with open(yaml_file, encoding="utf-8") as f:
        peep_data = yaml.safe_load(f)
        for this_peep in peep_data:
            personality = Personality(**this_peep)
            peeps[personality.name] = personality
    return peeps


@lru_cache(maxsize=1)
def get_personalities() -> dict[str, Personality]:
    """
    Loads personalities from the YAML file and caches them.
    This function is the single entry point for accessing personalities.
    """
    yaml_path = str(SCRIPT_DIR / "data/personalities.yaml")
    return _load_personalities(yaml_path)
