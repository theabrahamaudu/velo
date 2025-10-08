import os
from dotenv import load_dotenv
import yaml
from velo.utils.types import (
    ContentGenOut,
    ScheduleGenOut,
    AudienceResearchOut
)

load_dotenv()

# telegram
TG_TOKEN = os.getenv("TG_TOKEN", None)
TIMEZONE = os.getenv("TIMEZONE", "Africa/Lagos")
TIMEZONE_COMMON_NAME = os.getenv("TIMEZONE_COMMON_NAME", "Lagos")

# database
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:\
    {DB_PORT}/{DB_NAME}"

with open("./config/config.yml", "r") as conf:
    config: dict = yaml.safe_load(conf)

# model urls
OLLAMA_URL = config["ollama"]["url"]
SD_URL = config["sd"]["url"]

# supervisor
SUPERVISOR_MODEL = config["models"]["supervisor"]
SUPERVISOR_PROMPT = config["system_prompts"]["supervisor"]

# creative agent
CREATIVE_MODEL = config["sd"]["model"]
CREATIVES_PATH = config["sd"]["output_path"]

# audience agent
AUDIENCE_MODEL = config["models"]["audience"]
AUDIENCE_JSON_FORMAT = AudienceResearchOut.model_json_schema()
AUDIENCE_PROMPT = config["system_prompts"]["audience"] + \
    str(AUDIENCE_JSON_FORMAT)

# content agent
CONTENT_MODEL = config["models"]["content"]
CONTENT_JSON_FORMAT = ContentGenOut.model_json_schema()
CONTENT_PROMPT = config["system_prompts"]["content"] + str(CONTENT_JSON_FORMAT)

# scheduler agent
SCHEDULER_MODEL = config["models"]["scheduler"]
SCHEDULER_JSON_FORMAT = ScheduleGenOut.model_json_schema()
SCHEDULER_PROMPT = config["system_prompts"]["scheduler"] \
    + str(SCHEDULER_JSON_FORMAT)
