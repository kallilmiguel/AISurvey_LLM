from openai import OpenAI
from typing import Dict, List
import time

class DeepSeekAgent:
    def __init__(self):
        self.client = OpenAI(
            base_url="http://127.0.0.1:1234/v1",
            api_key="not-needed"  # LM Studio doesn't require an API key for local inference
        )
        self.request_counter = 0

    def generate_section(self, prompt: str, section_name: str) -> str:
        """Generate section content using local LLM through LM Studio"""
        try:
            system_prompt = f"""You are an expert academic writer. 
            Your task is to generate a detailed {section_name} section for a survey paper.
            The content should be well-structured, comprehensive, and in LaTeX format.
            Use appropriate LaTeX commands for sections, subsections, and mathematical formulas if needed."""

            response = self.client.chat.completions.create(
                model="local-model",  # This is ignored by LM Studio but required by the API
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000,  # Adjust based on your needs
                top_p=0.95,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            generated_text = response.choices[0].message.content
            self.request_counter += 1
            print(self.request_counter)
            return self._format_latex_section(section_name, generated_text)
        
        except Exception as e:
            print(f"Error generating section with local LLM: {str(e)}")
            raise

    def _format_latex_section(self, section_name: str, content: str) -> str:
        """Format the generated content as a LaTeX section"""
        # Check if content already has a section command
        if not content.strip().startswith('\\section'):
            formatted_section = f"""
\\section{{{section_name.title()}}}
{content}
"""
        else:
            formatted_section = content

        return formatted_section

    def _clean_latex_content(self, content: str) -> str:
        """Clean and validate LaTeX content"""
        # Add any specific LaTeX cleaning or validation logic here
        return content