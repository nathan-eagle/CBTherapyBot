import logging
import asyncio
import math
from telegram import Update
from telegram.ext import ContextTypes
from utils import (
    get_main_menu_keyboard,
    generate_replicate_response,
    generate_openai_response,
    text_to_speech_stream
)
from database import get_user, increment_free_interactions, update_user
from config import FREE_INTERACTIONS, CREDIT_COST_PER_SECOND_AUDIO, CREDIT_COST_PER_1000_CHARS
from payments import send_invoice
from pydub import AudioSegment
from io import BytesIO

logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    user_id = update.effective_user.id
    user_first_name = update.effective_user.first_name  # Extract first name
    logger.debug(f"Received message from user {user_id}: {user_text} (First Name: {user_first_name})")

    user = get_user(user_id)
    audio_enabled = context.user_data.get('audio_enabled', False)

    # Generate the response text
    response_text = await asyncio.get_event_loop().run_in_executor(
        None, generate_replicate_response, user_id, user_text, user_first_name
    )

    if not response_text:
        response_text = await asyncio.get_event_loop().run_in_executor(
            None, generate_openai_response, user_id, user_text, user_first_name
        )

    if response_text == "Sorry, I couldn't process that." or not response_text:
        await update.message.reply_text(
            response_text, reply_markup=get_main_menu_keyboard()
        )
        return

    # Initialize credits_needed
    credits_needed = 0

    # Handle audio response
    if audio_enabled:
        audio_bytes = text_to_speech_stream(response_text)
        if audio_bytes is None:
            logger.error(f"Failed to generate audio for user {user_id}")
            await update.message.reply_text(
                "Sorry, I couldn't generate an audio response.",
                reply_markup=get_main_menu_keyboard()
            )
            return

        # Use pydub to calculate audio duration
        audio = AudioSegment.from_file(BytesIO(audio_bytes.getvalue()), format="mp3")
        duration_seconds = audio.duration_seconds
        credits_needed = math.ceil(duration_seconds * CREDIT_COST_PER_SECOND_AUDIO)
    else:
        num_chars = len(response_text)
        credits_needed = math.ceil(num_chars / 1000) * CREDIT_COST_PER_1000_CHARS


    # Check and deduct credits
    if user['free_interactions_used'] < FREE_INTERACTIONS:
        increment_free_interactions(user_id)
    elif user['indecent_credits'] >= credits_needed:
        # Deduct credits from user's balance
        new_credits = user['indecent_credits'] - credits_needed
        update_user(user_id, indecent_credits=new_credits)
        logger.debug(
            f"Deducted {credits_needed} credits from user {user_id}. New balance: {new_credits}"
        )
    else:
        await update.message.reply_text(
            "You don't have enough Indecent Credits. Please purchase more to continue.",
            reply_markup=get_main_menu_keyboard()
        )
        await send_invoice(update, context, credits_needed)
        return

    # Send the response
    if audio_enabled:
        try:
            await update.message.reply_voice(voice=audio_bytes)
        except Exception as e:
            logger.exception(f"Error sending audio response to user {user_id}: {e}")
            await update.message.reply_text(
                "Sorry, I couldn't send the audio response.",
                reply_markup=get_main_menu_keyboard()
            )
    else:
        message_chunks = [
            response_text[i:i+4000] for i in range(0, len(response_text), 4000)
        ]
        for chunk in message_chunks:
            await update.message.reply_text(chunk, reply_markup=get_main_menu_keyboard())

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    user_id = update.effective_user.id
    logger.debug(f"Received menu button press from user {user_id}: {user_text}")

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
    else:
        await update.message.reply_text("Please choose an option from the menu below.", reply_markup=get_main_menu_keyboard())
        logger.debug(f"User {user_id} sent an unexpected input: {user_text}")
