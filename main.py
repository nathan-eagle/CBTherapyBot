import logging
from telegram.ext import ApplicationBuilder, Application, ContextTypes

from config import TELEGRAM_BOT_TOKEN
from handlers import register_handlers
from database import initialize_database
from utils import pinger

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARNING  # Set to DEBUG for development, INFO or WARNING in production
)
logger = logging.getLogger(__name__)

async def start_pinger(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Starts the ReplicatePinger."""
    await pinger.start_pinging()

async def on_shutdown(application: Application) -> None:
    """Clean up tasks when the application shuts down."""
    logger.info("Shutting down application...")
    await pinger.stop_pinging()
    logger.info("Pinger stopped.")

def main() -> None:
    """Start the bot."""
    initialize_database()

    # Include post_shutdown in ApplicationBuilder
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).post_shutdown(on_shutdown).build()
    register_handlers(application)
    logger.info("Bot is starting...")

    # Schedule the pinger to start via JobQueue when the event loop is running
    application.job_queue.run_once(start_pinger, when=0)

    application.run_polling()

if __name__ == '__main__':
    main()