from pathlib import Path
from openai import OpenAI
client = OpenAI()

speech_file_path = Path(__file__).parent / "speech.mp3"
response = client.audio.speech.create(
  model="tts-1",
  voice="alloy",
  input="Cock. Fuck. Shit. Bitch. Motherfucker. Asshole."
)

response.stream_to_file(speech_file_path)
print(f"Speech saved to {speech_file_path}")