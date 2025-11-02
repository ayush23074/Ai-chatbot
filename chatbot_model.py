# chatbot_model.py
# Lightweight wrapper around a causal language model (transformers)


from prompt_toolkit import prompt
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from typing import List


class ChatbotModel:
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium", device: str = None, max_history: int = 3):
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name).to(self.device)
        self.max_history = max_history


    def build_prompt(self, history: List[dict]) -> str:
        # history: list of {"role":"user"/"bot","text":...}
        parts = []
        for turn in history[-(self.max_history*2 or None):]:
            prefix = "User: " if turn["role"] == "user" else "Bot: "
            parts.append(prefix + turn["text"].strip())
        parts.append("Bot:")
        return "\n".join(parts)


    def generate(self, history: List[dict], max_new_tokens: int = 64, temperature: float = 0.8) -> str:
        prompt = self.build_prompt(history)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        with torch.no_grad():
            out = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=temperature,
                pad_token_id=self.tokenizer.eos_token_id,
                top_p=0.9,
            )
        decoded = self.tokenizer.decode(out[0], skip_special_tokens=True)
        # The model will return the whole prompt + reply; extract reply
        if decoded.startswith(prompt):
            reply = decoded[len(prompt):].strip()
        else:
        # fallback
            reply = decoded
        # If model repeats user text, try a simple cleanup
        reply = reply.split("User:")[-1].strip()
        # truncate to first line or a few sentences
        reply = reply.split('\n')[0].strip()
        return reply


# Example usage when running standalone:
if __name__ == '__main__':
    bot = ChatbotModel()
    history = [{"role":"user","text":"Hello!"}]
    print(bot.generate(history))