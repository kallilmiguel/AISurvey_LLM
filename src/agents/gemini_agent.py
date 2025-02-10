import google.generativeai as genai
from config.settings import GEMINI_API_KEY, GEMINI_MODEL

class GeminiAgent:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL)

    async def summarize_section(self, content, section_name):
        prompt = f"Summarize the following {section_name} section: \n\n{content}"
        response = await self.model.generate_content(prompt)

        return response.text
    
    async def process_pdf(self, pdf_content):
        pass
    