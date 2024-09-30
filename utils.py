import logging
from io import BytesIO
from telegram import ReplyKeyboardMarkup
from openai import OpenAI
import replicate
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from config import OPENAI_API_KEY, ELEVENLABS_API_KEY, REPLICATE_API_TOKEN
from config_characters import character_voices  # Character voices config
import datetime
import os

logger = logging.getLogger(__name__)

# Initialize clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
replicate.api_token = REPLICATE_API_TOKEN


def get_main_menu_keyboard():
    """Returns the main menu keyboard."""
    keyboard = [
        ['🏠 Home', '📚 Help'],
        ['💰 Buy Credits', '💳 Balance'],
        ['🎁 Free Credits', '🔊 Audio On/Off'],
        ['😇 Decent / 😈 Indecent'],
        ['💀 Nova'],
        ['💔 Carter'],
        ['💋 Natasha'],
        ['🔥 Onyx']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)


def generate_replicate_response(user_id: int, user_text: str, user_first_name: str, voice_id: str, character_prompt: str) -> str:
    """Generates a response using the Replicate API with character-specific prompt."""
    logger.debug(
        f"Generating Replicate response for user {user_id} with message: {user_text}")

    try:
        # Use the character-specific prompt in the system prompt
        system_prompt = f"{character_prompt} Address the user by their first name, {user_first_name}."

        # Generate the replicate response
        output = replicate.run(
            "kcaverly/nous-hermes-2-solar-10.7b-gguf:955f2924d182e60e80caedecd15261d03d4ccc0151ff08e7fb14d0cad1fbcca6",
            input={
                "prompt": f"{system_prompt}\nUser: {user_text}",
                "temperature": 0.7,
                "system_prompt": system_prompt,
                "max_new_tokens": 8000,
                "repeat_penalty": 1.1,
            }
        )

        response_text = ''.join(item for item in output)
        logger.debug(
            f"Replicate response for user {user_id}: {response_text.strip()}")
        return response_text.strip()

    except Exception as e:
        logger.exception(
            f"Error communicating with Replicate API for user {user_id}: {e}")
        return None


def generate_openai_response(user_id: int, user_text: str, user_first_name: str, character_prompt: str) -> str:
    """Generates a response using the OpenAI API."""
    logger.debug(
        f"Generating OpenAI response for user {user_id} with message: {user_text}")
    try:
        system_message = f"{character_prompt} Address the user by their first name, {user_first_name}."
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_text}
            ],
            max_tokens=5000,
            temperature=0.7,
        )
        assistant_reply = response.choices[0].message.content.strip()
        logger.debug(f"OpenAI response for user {user_id}: {assistant_reply}")
        return assistant_reply
    except Exception as e:
        logger.exception(
            f"Error communicating with OpenAI API for user {user_id}: {e}")
        return "Sorry, I couldn't process that."


def text_to_speech_stream(text: str, voice_id: str) -> BytesIO:
    """Handles audio generation using the correct TTS provider based on voice_id."""
    try:
        if voice_id in ["onyx", "nova"]:  # OpenAI voices
            return openai_text_to_speech(text, voice_id)

        # For ElevenLabs voices
        response = elevenlabs_client.text_to_speech.convert(
            voice_id=voice_id,
            optimize_streaming_latency="0",
            output_format="mp3_22050_32",
            text=text,
            model_id="eleven_turbo_v2",
            voice_settings=VoiceSettings(
                stability=0.0,
                similarity_boost=1.0,
                style=0.0,
                use_speaker_boost=True,
            ),
        )

        audio_stream = BytesIO()
        for chunk in response:
            if chunk:
                audio_stream.write(chunk)
        audio_stream.seek(0)
        return audio_stream
    except Exception as e:
        logger.exception(f"Error in text_to_speech_stream: {e}")
        return None


def openai_text_to_speech(text: str, voice: str) -> BytesIO:
    """Converts text to speech using OpenAI's TTS service."""
    try:
        response = openai_client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )

        audio_stream = BytesIO()
        audio_stream.write(response.content)
        audio_stream.seek(0)
        return audio_stream
    except Exception as e:
        logger.exception(f"Error in openai_text_to_speech: {e}")
        return None


def log_interaction(username: str, user_input: str, llm_response: str) -> None:
    """Logs the interaction to a tab-delimited 'logs.txt' file with timestamp, username, user input, and LLM response."""
    timestamp = datetime.datetime.utcnow().isoformat()
    log_line = f"{timestamp}\t{username}\t{user_input}\t{llm_response}\n"
    try:
        if os.path.exists("logs.txt"):
            with open("logs.txt", "r+", encoding="utf-8") as log_file:
                existing_logs = log_file.read()
                log_file.seek(0, 0)
                log_file.write(log_line + existing_logs)
        else:
            with open("logs.txt", "w", encoding="utf-8") as log_file:
                log_file.write(log_line)
        logger.debug(f"Logged interaction for user {username}")
    except Exception as e:
        logger.exception(f"Failed to write log: {e}")
