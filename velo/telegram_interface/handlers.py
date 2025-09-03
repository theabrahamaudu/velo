from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
# import velo.config as config
from velo.utils.tg_logs import tg_bot as logger


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("chat_id: %s", update.effective_chat.id)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Welcome to Velo! Your one stop marketing campaign AI agent."
    )

start_handler = CommandHandler("start", start)


async def new_campaign(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    logger.info("chat_id: %s", chat_id)
    await context.bot.send_message(
        chat_id=chat_id,
        text="You want an ad campaign for {}".format(
            update.effective_message.text[10:]
        )
    )

new_campaign_handler = CommandHandler("campaign", new_campaign)


async def regenerate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    logger.info("chat_id: %s", chat_id)
    await context.bot.send_message(
        chat_id=chat_id,
        text="Regenerating artefacts for task {}".format(chat_id)
    )

regeneration_handler = CommandHandler("regenerate", regenerate)
