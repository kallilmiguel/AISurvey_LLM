from transformers import AutoModelForCausalLM, AutoTokenizer
from config.settings import DEEPSEEK_MODEL

class DeepSeekAgent:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(DEEPSEEK_MODEL)
        self.model = AutoModelForCausalLM.from_pretrained(DEEPSEEK_MODEL)

    async def generate_section(self, summary, section_name):
        prompt = f"Generate a detailed {section_name} section based on this summary: \n\n{summary}"
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(**inputs)
        return self.tokenizer.decode(outputs[0])
    
    