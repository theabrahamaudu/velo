from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from velo.agents.supervisor import Supervisor
from velo.utils.tg_logs import tg_bot as logger
from velo.utils.types import Message


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("chat_id: %s", update.effective_chat.id)  # type: ignore
    await context.bot.send_message(
        chat_id=update.effective_chat.id,  # type: ignore
        text="Welcome to Velo! Your one stop marketing campaign AI agent."
    )

start_handler = CommandHandler("start", start)


async def new_campaign(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id  # type: ignore
    prompt = update.effective_message.text[10:]  # type: ignore
    logger.info("chat_id: %s", chat_id)

    supervisor = Supervisor()
    response = supervisor.start_w_tools(
        Message(
            role="user",
            content=prompt
        )
    )

    await context.bot.send_message(
        chat_id=chat_id,
        text="Here is your ad campaign:\n\n {}".format(
            response
        ),
        write_timeout=600,
        read_timeout=600,
        connect_timeout=600
    )

new_campaign_handler = CommandHandler("campaign", new_campaign)


async def regenerate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id  # type: ignore
    logger.info("chat_id: %s", chat_id)
    await context.bot.send_message(
        chat_id=chat_id,
        text="Regenerating artefacts for task {}".format(chat_id),
        write_timeout=600,
        read_timeout=600,
        connect_timeout=600
    )

regeneration_handler = CommandHandler("regenerate", regenerate)
