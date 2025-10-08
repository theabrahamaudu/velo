from telegram.ext import ApplicationBuilder
import velo.config as config
from velo.utils.tg_logs import tg_bot as logger
from velo.telegram_interface.handlers import (
    start_handler,
    new_campaign_handler,
    regeneration_handler
)


def start_bot():
    tg_bot = ApplicationBuilder().token(str(config.TG_TOKEN)).build()

    tg_bot.add_handlers([
        start_handler,
        new_campaign_handler,
        regeneration_handler
    ])
    try:
        tg_bot.run_polling()
        logger.info("bot service started")
    except Exception as e:
        logger.error("error starting bot service: %s", e)
        tg_bot.run_polling()
        logger.info("bot service started")
