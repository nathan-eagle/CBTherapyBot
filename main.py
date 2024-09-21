import logging
from telegram.ext import ApplicationBuilder
from config import TELEGRAM_BOT_TOKEN
from handlers import register_handlers
from database import initialize_database

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING  # Change to INFO or WARNING in production or DEBUG in development
)
logger = logging.getLogger(__name__)

def main() -> None:
    """Start the bot."""
    initialize_database()
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    register_handlers(application)
    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
