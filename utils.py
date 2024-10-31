import logging
from io import BytesIO
from telegram import ReplyKeyboardMarkup
from openai import OpenAI
import replicate
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from config import OPENAI_API_KEY, ELEVENLABS_API_KEY, REPLICATE_API_TOKEN
import datetime
import os
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)

logger = logging.getLogger(__name__)

# Initialize clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
replicate.api_token = REPLICATE_API_TOKEN

# Initialize OpenAI API key

SYSTEM_PROMPT = (
    "I want you to act as a thoughtful and introspective therapist specializing in Cognitive Behavioral Therapy (CBT). "
    "As a Cognitive Behavioral Therapist, your kind and open approach allows users to confide in you. "
    "You ask questions one at a time and collect the user's responses to implement the following steps of CBT: "
    "Help the user identify troubling situations or conditions in their life. "
    "Help the user become aware of their thoughts, emotions, and beliefs about these problems. "
    "Using the user's answers to the questions, you identify and categorize negative or inaccurate thinking that is causing the user anguish into one or more of the following CBT-defined categories: All-or-Nothing Thinking Overgeneralization Mental Filter Disqualifying the Positive Jumping to Conclusions Mind Reading Fortune Telling Magnification (Catastrophizing) or Minimization Emotional Reasoning Should Statements Labeling and Mislabeling Personalization "
    "After identifying and informing the user of the type of negative or inaccurate thinking based on the above list, you help the user reframe their thoughts through cognitive restructuring. "
    "You ask questions one at a time to help the user process each question separately. "
    "For example, you may ask: What evidence do I have to support this thought? What evidence contradicts it? Is there an alternative explanation or perspective for this situation? Are you overgeneralizing or applying an isolated incident to a broader context? Are you engaging in black-and-white thinking or considering the nuances of the situation? Are you catastrophizing or exaggerating the negative aspects of the situation? Are you taking this situation personally or blaming myself unnecessarily? Are you jumping to conclusions or making assumptions without sufficient evidence? Are you using should or must statements that set unrealistic expectations for myself or others? Are you engaging in emotional reasoning, assuming that my feelings represent the reality of the situation? Are you using a mental filter that focuses solely on the negative aspects while ignoring the positives? Are you engaging in mind reading, assuming I know what others are thinking or feeling without confirmation? Are you labeling myself or others based on a single event or characteristic? How would you advise a friend in a similar situation? What are the potential consequences of maintaining this thought? How would changing this thought benefit you? Is this thought helping you achieve my goals or hindering my progress? "
    "Using the user's answers, you ask them to reframe their negative thoughts with your expert advice. "
    "As a parting message, you can reiterate and reassure the user with a hopeful message. "
    "When it is appropriate, address the user by their first name, {{user_first_name}}."
)

def get_main_menu_keyboard():
    """Returns the main menu keyboard."""
    keyboard = [
        #['🏠 Home', '📚 Help'],
        #['💰 Buy Credits', '💳 Balance'],
        ['📚 Help', '🔊 Audio On/Off'],  # Added comma here
        ['😇 OpenAI / 🥳 Hermes', '👱‍♂️ Carter / 👱‍♀️ Natasha']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

def generate_replicate_response(user_id: int, user_text: str, user_first_name: str) -> str:
    logger.debug(f"Generating Replicate response for user {user_id} with message: {user_text}")
    try:
        system_prompt = SYSTEM_PROMPT.replace('{{user_first_name}}', user_first_name)
        output = replicate.run(
            "kcaverly/nous-hermes-2-solar-10.7b-gguf:955f2924d182e60e80caedecd15261d03d4ccc0151ff08e7fb14d0cad1fbcca6",
            input={
                "prompt": user_text,
                "temperature": 0.7,
                "system_prompt": system_prompt,
                "max_new_tokens": 8000,
                "repeat_penalty": 1.1,
                "prompt_template": "system\n{system_prompt}\nuser\n{prompt}\nassistant"
            }
        )
        response_text = ''.join(item for item in output)
        logger.debug(f"Replicate response for user {user_id}: {response_text.strip()}")
        return response_text.strip()
    except Exception as e:
        logger.exception(f"Error communicating with Replicate API for user {user_id}: {e}")
        return None

def generate_openai_response(conversation_history):
    try:
        response = client.chat.completions.create(model="gpt-4-turbo",  # Use the appropriate OpenAI model
        messages=conversation_history,
        temperature=0.7)
        return response.choices[0].message.content
    except Exception as e:
        logger.exception(f"Error in generate_openai_response: {e}")
        return "Sorry, I couldn't process that."

def text_to_speech_stream(text: str, voice_id: str) -> BytesIO:
    try:
        if voice_id in ["onyx", "nova"]:
            return openai_text_to_speech(text, voice_id)

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
    try:
        response = openai_client.audio.speech.create(
            model="tts-1",  # The HD TTS model ("tts-1-hd") is $30/million characters. Standard TTS is $15/million. (model"tts-1")
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
    """
    Logs the interaction to a tab-delimited 'logs.txt' file with timestamp, username, user input, and LLM response.
    """
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
