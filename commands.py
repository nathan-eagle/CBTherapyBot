from config_characters import character_voices
import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils import get_main_menu_keyboard, log_interaction
from database import get_user, update_user
from config import FREE_INTERACTIONS

logger = logging.getLogger(__name__)

# Start Command


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user = get_user(user_id)
    free_left = max(FREE_INTERACTIONS - user['free_interactions_used'], 0)
    indecent_credits = user['indecent_credits']

    welcome_text = (
        f"Hey there {update.effective_user.first_name}! Welcome! 😈😈 \n\n"
        f"You've got {free_left} free interactions left.\n"
        f"If you run out, you just need to buy more Indecent Credits via the menu below.\n\n"
        f"⚠️ Hold tight! The first interaction might be a bit slow as the system warms up from a cold start. 🥱 \n\n"
    )

    await update.message.reply_text(welcome_text, reply_markup=get_main_menu_keyboard())
    logger.debug(f"Sent welcome message to user {user_id} with main menu.")

# Help Command


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

# Toggle Audio Mode


async def toggle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_data = context.user_data
    audio_enabled = user_data.get('audio_enabled', False)
    user_data['audio_enabled'] = not audio_enabled
    status = "enabled" if user_data['audio_enabled'] else "disabled"

    await update.message.reply_text(f"Audio responses have been {status}.", reply_markup=get_main_menu_keyboard())
    logger.debug(
        f"Audio responses have been {status} for user {update.effective_user.id}.")

    # Log interaction
    log_interaction(update.effective_user.username or update.effective_user.first_name,
                    f"Audio responses {status}", "Toggle audio")

# Balance Command


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

# Reset Free Interactions


async def reset_interactions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    update_user(user_id, free_interactions_used=0)
    await update.message.reply_text("Your free interactions have been reset to 10.", reply_markup=get_main_menu_keyboard())
    logger.debug(f"Reset free interactions for user {user_id}.")

# Toggle Decent/Indecent Mode


async def toggle_llm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user = get_user(user_id)
    current_llm = user['llm']

    # Toggle between 'Indecent' and 'Decent'
    new_llm = 'Decent' if current_llm == 'Indecent' else 'Indecent'
    update_user(user_id, llm=new_llm)

    status = "😇 Decent" if new_llm == 'Decent' else "😈 Indecent"
    await update.message.reply_text(f"LLM has been set to {status}.", reply_markup=get_main_menu_keyboard())
    logger.debug(f"Toggled LLM for user {user_id} to {new_llm}.")

    # Log interaction
    log_interaction(update.effective_user.username or update.effective_user.first_name,
                    f"LLM set to {status}", "Toggle LLM")

# Select Character and Assign Voice


async def select_character(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    full_text = update.message.text

    # Iterate through character_voices to find the selected character
    for character, data in character_voices.items():
        if character in full_text:
            new_voice = data["voice_id"]
            emoji = data["emoji"]

            # Update the user's voice_id in the database (prompt is determined dynamically)
            update_user(user_id, voice_id=new_voice)

            await update.message.reply_text(f"Character has been set to {emoji} {character}.", reply_markup=get_main_menu_keyboard())
            logger.debug(
                f"Character set to {character} (voice: {new_voice}) for user {user_id}.")

            # Log interaction
            log_interaction(update.effective_user.username or update.effective_user.first_name,
                            f"Character set to {emoji} {character}", "Select Character")
            return

    # Handle case where character is not recognized
    await update.message.reply_text("Character not recognized. Please select a valid character from the menu.")
    logger.error(
        f"Character not recognized in text: {full_text} for user {user_id}.")
