from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler
)
from velo.agents.supervisor import Supervisor
from velo.utils.tg_logs import tg_bot as logger
from velo.types.agent import Message
from velo.utils.bot_handler_utils import load_images, load_results


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id  # type: ignore

    keyboard = [
        [InlineKeyboardButton(
            "Create Campaign",
            callback_data="new_campaign"
            )],
        [InlineKeyboardButton("Help", callback_data="help")],
        [InlineKeyboardButton("About Velo", callback_data="about")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "👋 <b>Welcome to Velo!</b>\n\n"
            "Your AI-powered assistant for ad campaigns.\n\n"
            "You can:\n"
            "• Generate ad campaigns with /campaign\n"
            "• Get help anytime with /help"
        ),
        parse_mode="HTML",
        reply_markup=reply_markup
    )

start_handler = CommandHandler("start", start)


async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # type: ignore

    if query.data == "new_campaign":  # type: ignore
        await context.bot.send_message(
            chat_id=update.effective_chat.id,  # type: ignore
            text="✍️ Please describe your campaign.\n\nExample:\n"
                 "<code>/campaign Create a summer ad campaign for eco-friendly water bottles</code>",  # noqa
            parse_mode="HTML"
        )
    elif query.data == "help":  # type: ignore
        await context.bot.send_message(
            chat_id=update.effective_chat.id,  # type: ignore
            text="🧭 <b>Help Menu</b>\n\n"
                 "Use <code>/campaign</code> to start a campaign",
            parse_mode="HTML"
        )
    elif query.data == "about":  # type: ignore
        await context.bot.send_message(
            chat_id=update.effective_chat.id,  # type: ignore
            text="🤖 <b>About Velo</b>\n\n"
                 "Velo is your AI-powered marketing copilot. It helps you generate ad campaigns, "  # noqa
                 "schedule content, and create visuals — all in minutes!",
            parse_mode="HTML"
        )

button_handler = CallbackQueryHandler(button_click)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🧭 <b>How to use Velo</b>\n\n"
        "1️⃣ To create a campaign, type:\n"
        "<code>/campaign Launch a skincare product for young adults</code>\n\n"
        "💡 Tip: Be specific! The more context you give, the better your campaign."  # noqa
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,  # type: ignore
        text=help_text,
        parse_mode="HTML"
    )

help_handler = CommandHandler("help", help_command)


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,  # type: ignore
        text=(
            "🤖 <b>About Velo</b>\n\n"
            "Velo is your AI-powered marketing copilot.\n"
            "It can:\n"
            "• Research audiences 👥\n"
            "• Generate ad content ✍️\n"
            "• Schedule posts 📅\n"
            "• Create visuals 🖼️\n\n"
            "Built for solo entrepreneurs and marketing teams."
        ),
        parse_mode="HTML"
    )

about_handler = CommandHandler("about", about)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,  # type: ignore
        text=str("🤔 I didn’t quite get that. Try <code>/start</code>" +
                 " to get started, <code>/help</code> for quick tips," +
                 " <code>/about</code> to learn more or" +
                 " start a campaign with <code>/campaign ...</code>"),
        parse_mode="HTML"
    )

unknown_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, unknown)


async def new_campaign(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id  # type: ignore
    prompt = update.effective_message.text[10:].strip()  # type: ignore
    logger.info("chat_id: %s", chat_id)

    if not prompt:
        await context.bot.send_message(
            chat_id=chat_id,
            text=str(
                "Please provide a prompt. Example:\n\n" +
                "<code>/campaign Create an ad campaign for" +
                " eco-friendly sneakers</code>"
            ),
            parse_mode="HTML"
        )
        return

    await context.bot.send_message(
        chat_id=chat_id,
        text=str(
            "Got it! Please wait whilst your campaign is being generated..." +
            " It should be ready in 2 to 5 mins 🕐"
        ),
        write_timeout=600,
        read_timeout=600,
        connect_timeout=600
    )
    try:
        supervisor = Supervisor(str(chat_id))
        campaign_id, _ = supervisor.start_w_tools(
            Message(
                role="user",
                content=prompt
            ),
            chat_id=chat_id
        )

        assert type(campaign_id) is int
        formatted_response = load_results(campaign_id)

        assert type(formatted_response) is str
        await context.bot.send_message(
            chat_id=chat_id,
            text="Here is your ad campaign!\n\n" + formatted_response,
            parse_mode="HTML",
            disable_web_page_preview=True,
            write_timeout=600,
            read_timeout=600,
            connect_timeout=600
        )

        images = load_images(str(chat_id), str(campaign_id))
        if images is not None:
            await context.bot.send_media_group(
                chat_id=chat_id,
                media=images,
                write_timeout=600,
                read_timeout=600,
                connect_timeout=600
            )

    except Exception as e:
        logger.error("error generating campaign: %s", e, exc_info=True)
        await context.bot.send_message(
            chat_id=chat_id,
            text=str(
                "Yikes! You'll have to try that again," +
                " our AI slop is lacking"
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
