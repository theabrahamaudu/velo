import os
from dotenv import load_dotenv
import yaml

load_dotenv()
TG_TOKEN = os.getenv("TG_TOKEN", None)
TIMEZONE = os.getenv("TIMEZONE", "Africa/Lagos")
TIMEZONE_COMMON_NAME = os.getenv("TIMEZONE_COMMON_NAME", "Lagos")

with open("./config/config.yml", "r") as conf:
    config: dict = yaml.safe_load(conf)

OLLAMA_URL = config["ollama"]["url"]

# supervisor
SUPERVISOR_MODEL = config["models"]["supervisor"]
SUPERVISOR_PROMPT = config["system_prompts"]["supervisor"]

# audience agent
AUDIENCE_MODEL = config["models"]["audience"]
AUDIENCE_PROMPT = config["system_prompts"]["audience"]
