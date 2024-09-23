# TelegramBot

This is a Telegram bot that interacts with users by generating responses using OpenAI's GPT models and converts text responses to speech using ElevenLabs. The bot allows users to toggle audio responses, check their balance, purchase credits, and more.

## Features

- **Text and Audio Responses**: Users can receive responses in text or audio format.
- **Credit System**: Users have free interactions and can purchase additional credits.
- **Menu Navigation**: Easy-to-use menu for navigating bot features.
- **OpenAI Integration**: Utilizes GPT models to generate dynamic responses.
- **ElevenLabs Integration**: Converts text responses to natural-sounding speech.

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- A Telegram bot token
- OpenAI API key
- ElevenLabs API key



### Deployment Service
Remember to delete the .db file (which removes all user data) before deploying changes that impact the database.

Restart the service after updating the .py file on hosted server:
sudo systemctl stop telegrambot.service
sudo systemctl restart telegrambot.service # check status: sudo systemctl status telegrambot.service


Open service file for editing:
sudo nano /etc/systemd/system/telegrambot.service
sudo systemctl daemon-reload
sudo systemctl restart telegrambot 
sudo systemctl status telegrambot # see status
sudo journalctl -u telegrambot -f # check logs

Git Commands:
Check out the Desired Branch
Pull the Latest Changes from Remote
Make Your Changes Locally
Stage (Add) Your Changes
Commit Your Changes
Push Your Changes to GitHub

git checkout main
git pull --no-rebase origin main # Resolve any merge conflicts if prompted
git add .
git commit -m "Merged changes from origin/main"
git push origin main

### To Do

- Button to swap LLMs: Decent / Indecent
- Button to swap between: OpenAI TTS / ElevenLabs
- Button to swap voices: (if 11Labs: Carter / Cindy) / (else OpenAI: ?/?)
- Chunk at the end of a sentence for long stories
- Log all the chats in the database.db
- Save all audio content to disk
X Use user's first name in the conversation
- Periodically send messages to the user. Allow feature to opt out.
- https://platform.openai.com/docs/guides/text-to-speech/quickstart

### Research

- Improve indecent LLM latency
- Share / post the good stories anonymously
