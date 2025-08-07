"""Configure personalities for Rickbot"""

import os
from dataclasses import dataclass, field
from pathlib import Path
import yaml  # pyyaml
from .utils import retrieve_secret, logger

# Use Path for directory references to ensure cross-platform compatibility
SCRIPT_DIR = Path(__file__).parent.resolve()


def get_avatar(name: str) -> str:
    return str(SCRIPT_DIR / f"media/{name}.png")


@dataclass(unsafe_hash=True)
class Personality:
    """Configuration for a given personality"""

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

        # Retrieve the prompt from the system_prompts folder
        # If the prompt doesn't exist, try retrieving from Secret Manager
        system_prompt_file = (
            SCRIPT_DIR / "data/system_prompts" / f"{self.name.lower()}.txt"
        )
        if os.path.exists(system_prompt_file):
            with open(system_prompt_file, "r", encoding="utf-8") as f:
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
                logger.warning(
                    f"Unable to retrieve '{secret_name}' from Secret Manager."
                )
                raise ValueError(
                    f"{system_prompt_file} not found and could not access '{secret_name}' from Secret Manager: {e}"
                ) from e

    def __repr__(self) -> str:
        return self.name


def load_personalities(yaml_file: str) -> dict[str, Personality]:
    """Load personalities from a YAML file."""
    peeps: dict[str, Personality] = {}
    with open(yaml_file, "r", encoding="utf-8") as f:
        peep_data = yaml.safe_load(f)
        for this_peep in peep_data:
            personality = Personality(**this_peep)
            peeps[personality.name] = personality
    return peeps


# Load personalities from the YAML file
personalities = load_personalities(str(SCRIPT_DIR / "data/personalities.yaml"))
