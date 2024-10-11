from cog import BasePredictor, Input
from llama_cpp import Llama
import os

class Predictor(BasePredictor):
    def setup(self):
        """Load the model into memory and system prompt."""
        model_path = "models/Moistral-11B-v3-Q5_K_M.gguf"
        self.llm = Llama(model_path=model_path, n_gpu_layers=100)
        
        # Option A: Hardcoded system prompt
        self.system_prompt = "You are an AI assistant that provides concise and accurate answers."

    def predict(
        self,
        prompt: str = Input(description="Input prompt"),
        max_tokens: int = Input(description="Maximum number of tokens to generate", default=256),
        temperature: float = Input(description="Generation temperature", default=0.7),
        top_p: float = Input(description="Top-p sampling value", default=0.9),
        system_prompt: str = Input(description="System prompt", default=None),
    ) -> str:
        """Run a single prediction with an optional system prompt."""
        
        # Determine the final system prompt
        final_system_prompt = system_prompt if system_prompt else self.system_prompt
        
        # Combine system and user prompts using a template
        combined_prompt = (
            f"{final_system_prompt}\n\n"
            f"User: {prompt}\n"
            f"AI:"
        )
        
        output = self.llm(
            prompt=combined_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            repeat_penalty=1.1,
        )
        return output["choices"][0]["text"]

