import logging
from telegram import Update
from telegram.ext import ContextTypes
from utils import get_main_menu_keyboard, log_interaction
from database import get_user, update_user
from config import FREE_INTERACTIONS

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user = get_user(user_id)
    free_left = max(FREE_INTERACTIONS - user['free_interactions_used'], 0)
    indecent_credits = user['indecent_credits']

    # Ensure audio is off by default
    context.user_data['audio_enabled'] = False

    welcome_text = (
        f"Hey there {update.effective_user.first_name}. What's on your mind?\n\n"
   )

    await update.message.reply_text(welcome_text, reply_markup=get_main_menu_keyboard())
    logger.debug(f"Sent welcome message to user {user_id} with main menu.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "You can control me by using the menu below or by sending these commands:\n"
        "/start - Welcome message with main menu\n"
        "/help - This help message\n"
        "/audio - Toggle audio responses on/off\n"
        #"/buy - Purchase additional Indecent Credits\n"
        #"/balance - Check your current balance\n\n"
        "\nBy default, the bot replies with text. Use /audio to receive voice messages. When audio is enabled, you can toggle between 4 different voices.\n"
        "\nStick with OpenAI initially. Expect a long wait time when using the custom Hermes llm for the first time. Cold boots can take up to 2 minutes. Hermes has *no* guardrails, so use at your own risk.\n"
        "\nFeedback is welcome! Please reach out to @natecow on Telegram with any issues or suggestions.\n"
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
    
    # Log the specific selection
    log_interaction(update.effective_user.username or update.effective_user.first_name, f"Audio responses {status}", "Toggle audio")


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

async def toggle_llm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user = get_user(user_id)
    current_llm = user['llm']
    
    # Toggle between 'Indecent' and 'Decent'
    new_llm = 'Decent' if current_llm == 'Indecent' else 'Indecent'
    update_user(user_id, llm=new_llm)
    
    status = "😇 OpenAI" if new_llm == 'Decent' else "🥳 Hermes"
    await update.message.reply_text(f"LLM has been set to {status}.", reply_markup=get_main_menu_keyboard())
    logger.debug(f"Toggled LLM for user {user_id} to {new_llm}.")
    
    # Log the specific selection
    log_interaction(update.effective_user.username or update.effective_user.first_name, f"LLM set to {status}", "Toggle LLM")

async def toggle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    user = get_user(user_id)
    current_voice = user['voice_id']
    
    # Toggle between 'Carter', 'Natasha', 'Onyx', and 'Nova'
    if current_voice == "pSfivq1mIHnYTVwluxnz":  # Carter
        new_voice = "PB6BdkFkZLbI39GHdnbQ"  # Natasha
        voice_name = "Natasha"
        emoji = "👱‍♀️"
    elif current_voice == "PB6BdkFkZLbI39GHdnbQ":  # Natasha
        new_voice = "onyx"  # Onyx (OpenAI)
        voice_name = "Onyx"
        emoji = "👨‍🦱"
    elif current_voice == "onyx":  # Onyx
        new_voice = "nova"  # Nova (OpenAI)
        voice_name = "Nova"
        emoji = "👩‍🦱"
    else:
        new_voice = "pSfivq1mIHnYTVwluxnz"  # Carter
        voice_name = "Carter"
        emoji = "👱‍♂️"
    
    update_user(user_id, voice_id=new_voice)
    
    await update.message.reply_text(f"Voice has been set to {emoji} {voice_name}.", reply_markup=get_main_menu_keyboard())
    logger.debug(f"Toggled voice for user {user_id} to {voice_name}.")
    
    # Log the specific selection
    log_interaction(update.effective_user.username or update.effective_user.first_name, f"Voice set to {voice_name}", "Toggle voice")

async def reset_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    # Clear the conversation history
    context.user_data['conversation_history'] = []
    await update.message.reply_text(
        "Conversation history has been reset.",
        reply_markup=get_main_menu_keyboard()
    )