"""
Configure personalities for Rickbot

We read a YAML file (data/personalities.yaml) to get the list of available characters.
For each character, dynamically load the corresponding system instruction, first by looking for a local text file and then,
if not found, by attempting to fetch it from Google Secret Manager.
"""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml  # pyyaml

from .secret_utils import retrieve_secret

SCRIPT_DIR = Path(__file__).parent
logger = logging.getLogger(__name__)


def get_avatar(name: str) -> str:
    return str(SCRIPT_DIR / f"media/{name}.png")


@dataclass(unsafe_hash=True) # Allow this to be hashable even though mutated through __post_init__
class Personality:
    """Represents a distinct chatbot personality, encapsulating its configuration.

    This dataclass holds all the attributes that define how a specific
    personality (e.g., Rick, Yoda) looks, behaves, and responds. It includes
    user-facing text, behavioral settings for the LLM, and paths to media assets.
    The system instruction is loaded dynamically upon initialization.
    """

    name: str  # The internal identifier for the personality (e.g., 'rick').
    menu_name: str  # The user-facing name for UI menus (e.g., 'Rick Sanchez').
    title: str  # The title displayed at the top of the chat window.
    overview: str  # A brief, user-facing description of the character.
    welcome: str  # The initial greeting message from the agent
    prompt_question: str  # A sample question to prompt the user for input.
    temperature: float
    avatar: str = field(init=False)
    system_instruction: str = field(init=False)

    def __post_init__(self) -> None:
        self.avatar = get_avatar(self.name.lower())

        # Retrieve the prompt from the system_prompts folder
        # If the prompt doesn't exist, try retrieving from Secret Manager
        system_prompt_file = (
            SCRIPT_DIR / "data/system_prompts" / f"{self.name.lower()}.txt"
        )
        if os.path.exists(system_prompt_file):
            with open(system_prompt_file, encoding="utf-8") as f:
                self.system_instruction = f.read()
        else:
            logger.info(
                f"Unable to find {system_prompt_file}. Attempting to retrieve from Secret Manager."
            )
            try:
                google_project = os.environ.get("GOOGLE_CLOUD_PROJECT")
                secret_name = f"{self.name.lower()}-system-prompt"
                self.system_instruction = retrieve_secret(google_project, secret_name)  # type: ignore
                logger.info("Successfully retrieved.")
            except Exception as e:
                logger.error(f"Unable to retrieve '{secret_name}' from Secret Manager.")
                raise ValueError(
                    f"{system_prompt_file} not found and could not access '{secret_name}' from Secret Manager: {e}"
                ) from e

    def __repr__(self) -> str:
        return self.name


def load_personalities(yaml_file: str) -> dict[str, Personality]:
    """Load personalities from a YAML file."""
    peeps: dict[str, Personality] = {}
    with open(yaml_file, encoding="utf-8") as f:
        peep_data = yaml.safe_load(f)
        for this_peep in peep_data:
            personality = Personality(**this_peep)
            peeps[personality.name] = personality
    return peeps


# Load personalities from the YAML file
personalities = load_personalities(str(SCRIPT_DIR / "data/personalities.yaml"))
