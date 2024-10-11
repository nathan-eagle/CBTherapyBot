#Instructions for pushing to Replicate
# ### Model Porting from HuggingFace to Replicate
# log into Lambda Labs, launch instance, and ssh in. (take 5 minutes to boot)

# sudo apt-get update # 20 seconds
# #sudo apt-get upgrade -y # takes a long time, may not be needed

# #curl -fsSL https://get.docker.com -o get-docker.sh # Docker will be installed with cog maybe? 
# #sudo sh get-docker.sh #takes 30 seconds



# sudo curl -o /usr/local/bin/cog -L https://github.com/replicate/cog/releases/latest/download/cog_`uname -s`_`uname -m`
# sudo chmod +x /usr/local/bin/cog

# mkdir new_project
# cd new_project

# cog init # this creates cog.yaml and predict.py



# <!-- git lfs install # Only if you want all the model! -->

# sudo apt-get install git-lfs
# git clone https://huggingface.co/TheDrummer/Moistral-11B-v3-GGUF models
# cd models
# git lfs pull --include="Moistral-11B-v3-Q5_K_M.gguf"
# cd ..

# Edit cog.yaml. Figure out how to get the model to run on GPU in Replicate! 

# Edit predict.py. Edit model_paty, max_tokesn = -1, 

# sudo usermod -aG docker $USER
# newgrp docker

# Test locally: 
# cog predict -i prompt="Q: Answer the following yes/no question by reasoning step-by-step. Can a dog drive a car?"

# Push: Make sure you are in the new project directory!
# cog login
# cog push r8.im/natecow76/indecentlit


from cog import BasePredictor, Input, ConcatenateIterator
from llama_cpp import Llama

PROMPT_TEMPLATE = "<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant"
SYSTEM_PROMPT = "You are a master of storytelling."


class Predictor(BasePredictor):
    def setup(self) -> None:
        """Load the model into memory to make running multiple predictions efficient"""
        self.model = Llama(
            model_path="./models/Moistral-11B-v3-Q5_K_M.gguf",
            n_gpu_layers=-1,
            n_ctx=4096,
            n_threads=1,
            main_gpu=0,
        )

    def predict(
        self,
        prompt: str = Input(description="Instruction for model"),
        system_prompt: str = Input(
            description="System prompt for the model, helps guides model behaviour.",
            default=SYSTEM_PROMPT,
        ),
        prompt_template: str = Input(
            description="Template to pass to model. Override if you are providing multi-turn instructions.",
            default=PROMPT_TEMPLATE,
        ),
        max_new_tokens: int = Input(
            description="Maximum new tokens to generate.", default=-1
        ),
        repeat_penalty: float = Input(
            description="This parameter plays a role in controlling the behavior of an AI language model during conversation or text generation. Its purpose is to discourage the model from repeating itself too often by increasing the likelihood of following up with different content after each response. By adjusting this parameter, users can influence the model's tendency to either stay within familiar topics (lower penalty) or explore new ones (higher penalty). For instance, setting a high repeat penalty might result in more varied and dynamic conversations, whereas a low penalty could be suitable for scenarios where consistency and predictability are preferred.",
            default=1.1,
        ),
        temperature: float = Input(
            description="This parameter used to control the 'warmth' or responsiveness of an AI model based on the LLaMA architecture. It adjusts how likely the model is to generate new, unexpected information versus sticking closely to what it has been trained on. A higher value for this parameter can lead to more creative and diverse responses, while a lower value results in safer, more conservative answers that are closer to those found in its training data. This parameter is particularly useful when fine-tuning models for specific tasks where you want to balance between generating novel insights and maintaining accuracy and coherence.",
            default=0.7,
        ),
    ) -> ConcatenateIterator[str]:
        """Run a single prediction on the model"""

        full_prompt = prompt_template.replace("{prompt}", prompt).replace(
            "{system_prompt}", system_prompt
        )

        for output in self.model(
            full_prompt,
            stream=True,
            repeat_penalty=repeat_penalty,
            max_tokens=max_new_tokens,
            temperature=temperature,
        ):
            yield output["choices"][0]["text"]