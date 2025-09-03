import os

env = os.environ

TG_TOKEN = env.get("TG_TOKEN", None)
TIMEZONE = env.get("TIMEZONE", "Africa/Lagos")
TIMEZONE_COMMON_NAME = env.get("TIMEZONE_COMMON_NAME", "Lagos")