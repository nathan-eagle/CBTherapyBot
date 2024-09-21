import logging
from telegram import Update
from telegram.ext import (
    CommandHandler, MessageHandler, CallbackQueryHandler,
    PreCheckoutQueryHandler, ContextTypes, filters
)
from config import MENU_OPTIONS
from commands import start, help_command, toggle_audio, balance, reset_interactions
from messages import handle_message, menu_handler
from payments import pre_checkout_callback, successful_payment_callback, process_purchase_button, buy

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
