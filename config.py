import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')

# Constants
FREE_INTERACTIONS = 10
CREDIT_COST_PER_SECOND_AUDIO = .833
CREDIT_COST_PER_1000_CHARS = 1

# Replicate ping settings
PING_REPLICATE = False # this is a flag of the state indicator of the pinger
PING_FREQUENCY = 60    # in seconds
PING_TIMEOUT = 600      # in seconds

# Menu options
MENU_OPTIONS = [
    '💰 Buy Credits',
    '🔊 Audio On/Off',
    '💀 Nova',
    '💔 Carter',
    '💋 Natasha',
    '🔥 Onyx'
]

# Credit packages
CREDIT_PACKAGES = {
    'purchase_50_credits': {'credits': 50},
    'purchase_100_credits': {'credits': 100},
    'purchase_500_credits': {'credits': 500},
    'purchase_1000_credits': {'credits': 1000},
}