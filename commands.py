import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils import get_main_menu_keyboard
from database import get_user, update_user
from config import FREE_INTERACTIONS

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user = get_user(user_id)
    free_left = max(FREE_INTERACTIONS - user['free_interactions_used'], 0)
    indecent_credits = user['indecent_credits']

    welcome_text = (
        f"Hey there {update.effective_user.first_name}! I'm Denzel. Are you ready to hear something indecent? 😈😈 \n\n"
        f"You have {free_left} free interactions left.\n"
        f"You currently have {indecent_credits} Indecent Credits.\n\n"
        f"Use the menu below to navigate through my features."
    )

    await update.message.reply_text(welcome_text, reply_markup=get_main_menu_keyboard())
    logger.debug(f"Sent welcome message to user {user_id} with main menu.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "You can control me by using the menu below or by sending these commands:\n\n"
        "/start - Welcome message with main menu\n"
        "/help - This help message\n"
        "/audio - Toggle audio responses on/off\n"
        "/buy - Purchase additional Indecent Credits\n"
        "/balance - Check your current balance\n\n"
        "By default, I reply with text. Use /audio to receive voice messages."
    )
    await update.message.reply_text(help_text, reply_markup=get_main_menu_keyboard())
    logger.debug("Sent help message to user.")

async def toggle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_data = context.user_data
    audio_enabled = user_data.get('audio_enabled', False)
    user_data['audio_enabled'] = not audio_enabled
    status = "enabled" if user_data['audio_enabled'] else "disabled"
    await update.message.reply_text(f"Audio responses have been {status}.", reply_markup=get_main_menu_keyboard())
    logger.debug(f"Audio responses have been {status} for user {update.effective_user.id}.")


async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user = get_user(user_id)
    indecent_credits = user['indecent_credits']
    free_left = max(FREE_INTERACTIONS - user['free_interactions_used'], 0)

    balance_text = (
        f"You have {free_left} free interactions left.\n"
        f"You currently have {indecent_credits} Indecent Credits."
    )
    await update.message.reply_text(balance_text, reply_markup=get_main_menu_keyboard())
    logger.debug(f"Displayed balance to user {user_id}.")

async def reset_interactions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    update_user(user_id, free_interactions_used=0)
    await update.message.reply_text("Your free interactions have been reset to 10.", reply_markup=get_main_menu_keyboard())
    logger.debug(f"Reset free interactions for user {user_id}.")
