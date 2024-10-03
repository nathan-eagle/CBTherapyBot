from cog import BasePredictor, Input
from llama_cpp import Llama
import os

class Predictor(BasePredictor):
    def setup(self):
        """Load the model into memory"""
        model_path = "/src/models/moistral-11b-v3.Q4_0.gguf"
        self.llm = Llama(model_path=model_path, n_gpu_layers=100)

    def predict(
        self,
        prompt: str = Input(description="Input prompt"),
        max_tokens: int = Input(description="Maximum number of tokens to generate", default=256),
        temperature: float = Input(description="Generation temperature", default=0.7),
        top_p: float = Input(description="Top-p sampling value", default=0.9),
    ) -> str:
        """Run a single prediction"""
        output = self.llm(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            repeat_penalty=1.1,
        )
        return output["choices"][0]["text"]