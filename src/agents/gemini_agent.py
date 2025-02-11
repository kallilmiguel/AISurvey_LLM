import google.generativeai as genai
from ..utils.pdf_handler import PDFBatchProcessor
from ..utils.rate_limiter import rate_limit, RateLimiter
from typing import Dict, List
from config.settings import (
    GEMINI_API_KEY, 
    GEMINI_MODEL,
    GEMINI_REQUESTS_PER_MINUTE,
    RETRY_ATTEMPTS,
    RETRY_DELAY
)
import time

class GeminiAgent:
    def __init__(self):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        self.pdf_processor = PDFBatchProcessor()
        self.rate_limiter = RateLimiter(GEMINI_REQUESTS_PER_MINUTE)
        self.requests_count = 0

    @rate_limit
    def summarize_section(self, contents: List[str], section_name: str):
        """ Summarize multiple versions of the same section from different papers"""
        combined_content = "\n\n".join(contents)
        prompt = f"""
        Analyze and summarize the following {section_name} section from multiple research papers.
        Focus on:
        1. Common themes and patterns
        2. Key methodologies or findings
        3. important contrasts or complementary information.
        4. Synthesis of the main ideas

        Content:
        {combined_content}

        Please provide a comprehensive summary that can serve as a foundation for a survey paper section.
        """
        response = self.model.generate_content(prompt)
        self.requests_count+=1
        print(self.requests_count)
        return response.text 
    
    def process_pdf(self, pdf_files: List[str]) -> Dict[str, str]:
        """Process multiple PDF files and generate summaries for each section"""
        # Validate PDF count
        if not self.pdf_processor.validate_pdf_count(pdf_files):
            raise ValueError("Number of PDF files must be between 1 and 10")
        
        # Process all PDFs and organize sections
        all_sections = self.pdf_processor.process_uploaded_files(pdf_files)

        
        # Generate summaries for each section
        section_summaries = {}
        for section_name, contents in all_sections.items():
            if contents: #Only process sections that have content
                summary = self.summarize_section(contents, section_name)
                section_summaries[section_name] = summary

        return section_summaries

