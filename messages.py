import logging
from commands import character_voices
from commands import toggle_llm, select_character
import asyncio
import math
from telegram import Update
from telegram.ext import ContextTypes
from utils import (
    get_main_menu_keyboard,
    generate_replicate_response,
    generate_openai_response,
    text_to_speech_stream,
    log_interaction
)
from database import get_user, increment_free_interactions, update_user
from config import FREE_INTERACTIONS, CREDIT_COST_PER_SECOND_AUDIO, CREDIT_COST_PER_1000_CHARS
from pydub import AudioSegment
from io import BytesIO

logger = logging.getLogger(__name__)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    user_id = update.effective_user.id
    user_first_name = update.effective_user.first_name
    username = update.effective_user.username or user_first_name
    logger.debug(
        f"Received message from user {user_id}: {user_text} (Username: {username})"
    )

    # Retrieve the user profile data (voice_id and character_prompt)
    user = get_user(user_id)
    
    # Initialize audio_enabled to True by default
    if 'audio_enabled' not in context.user_data:
        context.user_data['audio_enabled'] = True  # Enable audio by default
    audio_enabled = context.user_data.get('audio_enabled', True)

    # Retrieve the LLM mode (Decent or Indecent) and voice_id from the user profile
    user_llm = user.get('llm', 'Indecent')  # Default to 'Indecent'
    voice_id = user.get('voice_id', 'PB6BdkFkZLbI39GHdnbQ')  # Default to Natasha

    # Get the character data (prompt and voice) based on the selected voice_id
    character_data = next(
        (data for name, data in character_voices.items()
         if data['voice_id'] == voice_id), None
    )
    if not character_data:
        await update.message.reply_text("Sorry, I couldn't determine your selected character.", reply_markup=get_main_menu_keyboard())
        return

    character_prompt = character_data['prompt'].format(user_name=user_first_name)  # Format the prompt

    # Generate the response text based on the user's selected LLM
    if user_llm == 'Decent':
        response_text = await generate_openai_response(user_id, user_text, user_first_name, character_prompt)
    else:
        response_text = await generate_replicate_response(user_id, user_text, user_first_name, character_prompt)

    if not response_text or response_text == "Sorry, I couldn't process that.":
        await update.message.reply_text("Sorry, I couldn't process that.", reply_markup=get_main_menu_keyboard())
        return

    # Handle audio response
    credits_needed = 0
    if audio_enabled:
        # Use the character's voice_id for TTS (text-to-speech)
        audio_bytes = text_to_speech_stream(response_text, voice_id)
        if audio_bytes is None:
            logger.error(f"Failed to generate audio for user {user_id}")
            await update.message.reply_text("Sorry, I couldn't generate an audio response.", reply_markup=get_main_menu_keyboard())
            return

        # Calculate audio duration and credits needed
        audio = AudioSegment.from_file(
            BytesIO(audio_bytes.getvalue()), format="mp3")
        duration_seconds = audio.duration_seconds
        credits_needed = math.ceil(
            duration_seconds * CREDIT_COST_PER_SECOND_AUDIO)
    else:
        num_chars = len(response_text)
        credits_needed = math.ceil(num_chars / 1000) * \
            CREDIT_COST_PER_1000_CHARS

    # Check and deduct credits
    if user['free_interactions_used'] < FREE_INTERACTIONS:
        increment_free_interactions(user_id)
    elif user['indecent_credits'] >= credits_needed:
        new_credits = user['indecent_credits'] - credits_needed
        update_user(user_id, indecent_credits=new_credits)
        logger.debug(
            f"Deducted {credits_needed} credits from user {user_id}. New balance: {new_credits}")
    else:
        await update.message.reply_text("You don't have enough Indecent Credits. Please purchase more to continue.", reply_markup=get_main_menu_keyboard())
        return

    # Log the interaction
    log_interaction(username, user_text, response_text)

    # Send the response as audio or text
    if audio_enabled:
        try:
            await update.message.reply_voice(voice=audio_bytes)
        except Exception as e:
            logger.exception(
                f"Error sending audio response to user {user_id}: {e}")
            await update.message.reply_text("Sorry, I couldn't send the audio response.", reply_markup=get_main_menu_keyboard())
    else:
        # Send the response in chunks if it's too long for one message
        message_chunks = [response_text[i:i + 4000]
                          for i in range(0, len(response_text), 4000)]
        for chunk in message_chunks:
            await update.message.reply_text(chunk, reply_markup=get_main_menu_keyboard())

# Menu Handler to handle various button clicks


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    user_id = update.effective_user.id
    logger.debug(
        f"Received menu button press from user {user_id}: {user_text}")

    from commands import start, help_command, balance, reset_interactions, toggle_audio
    from payments import buy

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
    elif user_text in ['💀 Nova', '💔 Carter', '💋 Natasha', '🔥 Onyx']:
        # Handle character selection
        await select_character(update, context, user_text)
    else:
        await update.message.reply_text("Please choose an option from the menu below.", reply_markup=get_main_menu_keyboard())
        logger.debug(f"User {user_id} sent an unexpected input: {user_text}")