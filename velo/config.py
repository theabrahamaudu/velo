import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import yaml
from velo.utils.types import (
    ContentGenOut,
    Email,
    Schedule,
    ScheduleGenOut,
    AudienceResearchOut,
    SocialPost
)

load_dotenv()
TG_TOKEN = os.getenv("TG_TOKEN", None)
TIMEZONE = os.getenv("TIMEZONE", "Africa/Lagos")
TIMEZONE_COMMON_NAME = os.getenv("TIMEZONE_COMMON_NAME", "Lagos")

with open("./config/config.yml", "r") as conf:
    config: dict = yaml.safe_load(conf)

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
AUDIENCE_JSON_FORMAT = AudienceResearchOut(
    keywords=["keyword 1", "keyword 2", "..."],
    interests=["interest 1", "interest 2", "..."],
    pain_points=["pain point 1", "pain point 2", "..."]
).model_dump_json(indent=2)
AUDIENCE_PROMPT = config["system_prompts"]["audience"] + AUDIENCE_JSON_FORMAT

# content agent
CONTENT_MODEL = config["models"]["content"]
CONTENT_JSON_FORMAT = ContentGenOut(
    ad_copies=["ad copy 1", "ad copy 2"],
    emails=[
        Email(
            title="email title 1",
            body="email body 1"
        ),
        Email(
            title="email title 2",
            body="email body 2"
        )
    ],
    social_posts=[
        SocialPost(
            platform="platform 1",
            post="post 1"
        ),
        SocialPost(
            platform="platfrom 2",
            post="post 2"
        )
    ]
).model_dump_json(indent=2)
CONTENT_PROMPT = config["system_prompts"]["content"] + CONTENT_JSON_FORMAT

# scheduler agent
SCHEDULER_MODEL = config["models"]["scheduler"]
SCHEDULER_JSON_FORMAT = ScheduleGenOut(
    schedule=[
        Schedule(
            platform="platform 1",
            datetime=datetime.now(timezone.utc),
            content_ref="ad copy 1"
        ),
        Schedule(
            platform="platform 2",
            datetime=datetime.now(timezone.utc),
            content_ref="ad copy 2"
        ),
        Schedule(
            platform="...",
            datetime=datetime.now(timezone.utc),
            content_ref="..."
        )
    ]
).model_dump_json(indent=2)
SCHEDULER_PROMPT = config["system_prompts"]["scheduler"] \
    + SCHEDULER_JSON_FORMAT
