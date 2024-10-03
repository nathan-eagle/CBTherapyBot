# TelegramBot

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

### Model Porting from HuggingFace to Replicate
sudo apt-get update
#sudo apt-get upgrade -y # takes a long time, may not be needed

#curl -fsSL https://get.docker.com -o get-docker.sh # Docker will be installed with cog maybe? 
#sudo sh get-docker.sh

<!-- No need for nvidia-docker on Replicate bc Cog will use the nvidia-docker base image ??
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | \
  sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker -->


sudo curl -o /usr/local/bin/cog -L https://github.com/replicate/cog/releases/latest/download/cog_`uname -s`_`uname -m`
sudo chmod +x /usr/local/bin/cog

mkdir new_project
cd new_project

cog init # this creates cog.yaml and predict.py

sudo apt-get install git-lfs
git lfs install

git clone https://huggingface.co/TheDrummer/Moistral-11B-v3-GGUF models #WRONG. We just want a single model. FIX!

Edit cog.yaml. Remove the mdkir and cp models. potentially remove python packages and other unnecessary stuff not used in predict.py. FIX!

Edit predict.py. Edit model_paty, max_tokesn = -1, n_gpu_layers, add system prompt or prompt_template? FIX! 

Test locally: cog predict -i prompt="Q: Answer the following yes/no question by reasoning step-by-step. Can a dog drive a car?"

Push: 
cog login
cog push r8.im/natecow76/indecentlit

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

- Add image when they choose a character 

- Start ping at /start message rather than first interaction and remove first ping immediately after first interaction.
- Clear command to reset the conversation /clear Reset your AI (robot icon)


- Chunk at the end of a sentence for long stories
- Save all audio content to disk
- Periodically send messages to (paying) users. Allow feature to opt out.




### Research

- Improve indecent LLM latency
- Share / post the good stories anonymously - add a share button 
- Pricing: Character based pricing, and text only based pricing. 
- Add a "tip" button for users to tip the character
- Alternatives to Replicate: Runpod: https://www.runpod.io/serverless-gpu, Fly: https://fly.io/gpu



### Costs

- ElevenLabs TTS: ~$150 / 1M characters(3k character story =~$0.50) ** need to double check **
- OpenAI TTS: $15 / 1M characters (3k character story = $0.05)
- Replicate: $0.000575 / second (~20 secs/story = $0.01)