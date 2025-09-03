import os
from dotenv import load_dotenv

load_dotenv()
TG_TOKEN = os.getenv("TG_TOKEN", None)
TIMEZONE = os.getenv("TIMEZONE", "Africa/Lagos")
TIMEZONE_COMMON_NAME = os.getenv("TIMEZONE_COMMON_NAME", "Lagos")
