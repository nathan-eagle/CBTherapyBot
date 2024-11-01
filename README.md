# CBT Telegram Bot

This is a Telegram bot that interacts with users by generating responses using OpenAI's GPT models and converts text responses to speech using ElevenLabs. The bot allows users to toggle audio responses, check their balance, purchase credits, and more.

## Features

- **Text and Audio Responses**: Users can receive responses in text or audio format.
- **Credit System**: Users have free interactions and can purchase additional credits. (easter egg: type /reset to reset your free interactions)
- **Menu Navigation**: Easy-to-use menu for navigating bot features.
- **OpenAI Integration**: Utilizes GPT models to generate dynamic responses.
- **ElevenLabs Integration**: Converts text responses to natural-sounding speech.

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- A Telegram bot token
- OpenAI API key
- ElevenLabs API key
- Replicate API key


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

To sync with remote branch when edits are made to both:
git fetch origin
git checkout main
git pull origin main

If there are merge conflicts between your local changes and the changes from the remote repository, Git will prompt you to resolve them. Open the conflicting files, resolve the issues manually, and then:
git add <file_with_conflict>
git commit
git push origin main # or git pull --rebase origin main #  to push the local updates back to the remote branch


To delete all local changes and reset to the remote branch:
git reset --hard
git fetch origin
git reset --hard origin/main

To make changes to the remote branch:
git checkout main
git pull --no-rebase origin main # Resolve any merge conflicts if prompted
git add .
git commit -m "Merged changes from origin/main"
git push origin main

### To Do


- Make memory persist across sessions
- Periodically send messages to (paying) users. Allow feature to opt out


### Research

- Alternatives to Replicate: Runpod: https://www.runpod.io/serverless-gpu, Fly: https://fly.io/gpu



### Costs

- ElevenLabs TTS: ~$150 / 1M characters(3k character story =~$0.50) ** need to double check **
- OpenAI TTS: $15 / 1M characters (3k character story = $0.05)
- Replicate: $0.000575 / second (~20 secs/story = $0.01)