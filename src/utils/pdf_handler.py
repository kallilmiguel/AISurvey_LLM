import PyPDF2
import re
from typing import Dict, List, Optional
import fitz  # PyMuPDF
import os
from config.settings import TEMP_DIR

class PDFHandler:
    def __init__(self):
        self.section_keywords = {
            'introduction': ['introduction', '1. introduction', 'i. introduction'],
            'background': ['background', 'related work', 'literature review', '2. background', 'ii. background'],
            'methodology': ['methodology', 'method', 'proposed method', 'approach', '3. methodology', 'iii. methodology'],
            'results': ['results', 'evaluation', 'experiments', 'experimental results', '4. results', 'iv. results'],
            'discussion': ['discussion', '5. discussion', 'v. discussion'],
            'conclusion': ['conclusion', 'conclusions', 'concluding remarks', '6. conclusion', 'vi. conclusion']
        }

    def extract_text_with_formatting(self, pdf_path: str) -> str:
        """Extract text while preserving some formatting using PyMuPDF"""
        doc = fitz.open(pdf_path)
        text_with_formatting = []
        
        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            # Check if text is bold or size is larger (potential section header)
                            if span["flags"] & 2**4 or span["size"] > 10:  # 2**4 is bold flag
                                text_with_formatting.append(f"\n### {span['text']} ###\n")
                            else:
                                text_with_formatting.append(span['text'])
        
        doc.close()
        return " ".join(text_with_formatting)

    def identify_section_boundaries(self, text: str) -> Dict[str, tuple]:
        """Identify the start and end positions of each section"""
        text = text.lower()
        sections = {}
        
        # Find all potential section headers
        for section_type, keywords in self.section_keywords.items():
            for keyword in keywords:
                matches = list(re.finditer(r'\n### .*?' + keyword + '.*? ###\n', text, re.IGNORECASE))
                if matches:
                    # Take the first occurrence of each section type
                    if section_type not in sections:
                        start_pos = matches[0].start()
                        sections[section_type] = (start_pos, None)
                    break
        
        # Sort sections by their start position
        sorted_sections = sorted(sections.items(), key=lambda x: x[1][0])
        
        # Set end positions
        for i in range(len(sorted_sections) - 1):
            current_section = sorted_sections[i][0]
            next_section = sorted_sections[i + 1][0]
            sections[current_section] = (sections[current_section][0], sections[next_section][0])
        
        # Set the end position of the last section
        if sorted_sections:
            last_section = sorted_sections[-1][0]
            sections[last_section] = (sections[last_section][0], len(text))
        
        return sections

    def extract_section_content(self, text: str, start: int, end: int) -> str:
        """Extract the content of a section given its boundaries"""
        section_content = text[start:end].strip()
        # Remove the section header
        section_content = re.sub(r'\n### .*? ###\n', '', section_content, 1)
        return section_content

    def process_pdf(self, pdf_path: str) -> Dict[str, str]:
        """Process a PDF file and return a dictionary of sections and their content"""
        # Extract text with formatting
        text = self.extract_text_with_formatting(pdf_path)
        
        # Identify section boundaries
        sections = self.identify_section_boundaries(text)
        
        # Extract content for each section
        section_contents = {}
        for section_name, (start, end) in sections.items():
            content = self.extract_section_content(text, start, end)
            section_contents[section_name] = content
        
        return section_contents

class PDFBatchProcessor:
    def __init__(self):
        self.pdf_handler = PDFHandler()
        os.makedirs(TEMP_DIR, exist_ok=True)

    async def process_uploaded_files(self, files: List[str]) -> Dict[str, List[str]]:
        """Process multiple PDF files and organize their sections"""
        all_sections = {
            'introduction': [],
            'background': [],
            'methodology': [],
            'results': [],
            'discussion': [],
            'conclusion': []
        }

        for file_path in files:
            try:
                sections = self.pdf_handler.process_pdf(file_path)
                for section_name, content in sections.items():
                    if section_name in all_sections:
                        all_sections[section_name].append(content)
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                continue

        return all_sections

    def validate_pdf_count(self, files: List[str]) -> bool:
        """Validate that the number of PDFs is within the acceptable range"""
        return 1 <= len(files) <= 10