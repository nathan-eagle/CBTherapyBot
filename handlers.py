import logging
from telegram import Update
from telegram.ext import (
    CommandHandler, MessageHandler, CallbackQueryHandler,
    PreCheckoutQueryHandler, ContextTypes, filters
)
from config import MENU_OPTIONS
from commands import start, help_command, toggle_audio, balance, reset_interactions, toggle_llm, toggle_voice
from messages import handle_message, menu_handler
from payments import pre_checkout_callback, successful_payment_callback, process_purchase_button, buy
from utils import get_main_menu_keyboard, log_interaction

logger = logging.getLogger(__name__)

def register_handlers(application):
    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("audio", toggle_audio))
    application.add_handler(CommandHandler("buy", buy))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("reset", reset_interactions))

    # Register message handlers
    application.add_handler(MessageHandler(filters.Regex(f"^({'|'.join(MENU_OPTIONS)})$"), menu_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex(f"^({'|'.join(MENU_OPTIONS)})$"), handle_message))

    # Register payment handlers
    application.add_handler(PreCheckoutQueryHandler(pre_checkout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    # Register callback query handler for purchase buttons
    application.add_handler(CallbackQueryHandler(process_purchase_button, pattern='^purchase_\\d+_credits$'))

    # Register the error handler
    application.add_error_handler(error_handler)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all exceptions."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "An unexpected error occurred. Please try again later."
            )
        except Exception as e:
            logger.exception(f"Failed to send error message to user: {e}")

# Update the menu_handler to handle new menu options
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    user_id = update.effective_user.id
    logger.debug(f"Received menu button press from user {user_id}: {user_text}")

    from commands import start, help_command, balance, reset_interactions, toggle_audio, toggle_llm, toggle_voice
    from payments import buy

    # Log the menu button press
    log_interaction(update.effective_user.username or update.effective_user.first_name, user_text, "Menu button press")

    if user_text == '🏠 Home':
        await start(update, context)
    elif user_text == '📚 Help':
        await help_command(update, context)
    elif user_text == '💰 Buy Credits':
        await buy(update, context)
    elif user_text == '💳 Balance':
        await balance(update, context)
    elif user_text == '🎁 Free Credits':
        await reset_interactions(update, context)
    elif user_text == '🔊 Audio On/Off':
        await toggle_audio(update, context)
    elif user_text == '😇 Decent / 😈 Indecent':
        await toggle_llm(update, context)
    elif user_text == '👱‍♂️ Carter / 👱‍♀️ Natasha':
        await toggle_voice(update, context)
    else:
        await update.message.reply_text("Please choose an option from the menu below.", reply_markup=get_main_menu_keyboard())
        logger.debug(f"User {user_id} sent an unexpected input: {user_text}")
