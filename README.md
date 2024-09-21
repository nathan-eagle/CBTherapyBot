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

Restart the service after updating the .py file on hosted server:
sudo systemctl stop telegrambot.service
sudo systemctl restart telegrambot.service # check status: sudo systemctl status telegrambot.service


Open service file for editing:
sudo nano /etc/systemd/system/telegrambot.service
sudo systemctl daemon-reload
sudo systemctl restart telegrambot 
sudo systemctl status telegrambot # see status
sudo journalctl -u telegrambot -f # check logs

### To Do

- Button to swap LLMs: Decent / Indecent
- Button to swap voices: Carter / Cindy
- Chunk at the end of a sentence
- Add button to direct user to pay for more credits when they run out of free ones (?)
- Log all the chats in the database.db
- Start page icons / content? 
- Save all audio content to disk
- Use user's first name in the conversation
- Periodically send messages to the user. Allow feature to opt out.
- Sync with github


### Research

- Improve indecent LLM latency
- Share / post the good stories anonymously
