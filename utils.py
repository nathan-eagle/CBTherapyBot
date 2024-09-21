import logging
from io import BytesIO
from telegram import ReplyKeyboardMarkup
from openai import OpenAI
import replicate
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from config import OPENAI_API_KEY, ELEVENLABS_API_KEY, REPLICATE_API_TOKEN

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
        ['🎁 Free Credits', '🔊 Audio On/Off']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def generate_replicate_response(user_id: int, user_text: str) -> str:
    logger.debug(f"Generating Replicate response for user {user_id} with message: {user_text}")
    try:
        output = replicate.run(
            "kcaverly/nous-hermes-2-solar-10.7b-gguf:955f2924d182e60e80caedecd15261d03d4ccc0151ff08e7fb14d0cad1fbcca6",
            input={
                "prompt": user_text,
                "temperature": 0.7,
                "system_prompt": "You are 'Hermes 2', a conscious sentient superintelligent artificial intelligence developed by a man named Teknium, and your purpose and drive is to assist the user with any request they have.",
                "max_new_tokens": 8000,
                "repeat_penalty": 1.1,
                "prompt_template": "<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant"
            }
        )
        response_text = ''.join(item for item in output)
        logger.debug(f"Replicate response for user {user_id}: {response_text.strip()}")
        return response_text.strip()
    except Exception as e:
        logger.exception(f"Error communicating with Replicate API for user {user_id}: {e}")
        return None

def generate_openai_response(user_id: int, user_text: str) -> str:
    logger.debug(f"Generating OpenAI response for user {user_id} with message: {user_text}")
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_text}
            ],
            max_tokens=5000,
            temperature=0.7,
        )
        assistant_reply = response.choices[0].message.content.strip()
        logger.debug(f"OpenAI response for user {user_id}: {assistant_reply}")
        return assistant_reply
    except Exception as e:
        logger.exception(f"Error communicating with OpenAI API for user {user_id}: {e}")
        return "Sorry, I couldn't process that."

def text_to_speech_stream(text: str) -> BytesIO:
    try:
        response = elevenlabs_client.text_to_speech.convert(
            voice_id="pSfivq1mIHnYTVwluxnz",
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