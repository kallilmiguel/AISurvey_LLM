# src/models/survey_model.py

import asyncio
from typing import List, Dict, Optional
import os
import json
import time
from datetime import datetime
from ..agents.gemini_agent import GeminiAgent
from ..agents.deepseek_agent import DeepSeekAgent
from config.settings import OUTPUT_DIR, TEMP_DIR

class SurveyGenerator:
    def __init__(self):
        self.gemini_agent = GeminiAgent()
        self.deepseek_agent = DeepSeekAgent()
        self.section_order = [
            'introduction',
            'background',
            'methodology',
            'results',
            'discussion',
            'conclusion'
        ]
        
        # Create output directory if it doesn't exist
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(TEMP_DIR, exist_ok=True)

    def save_summaries_to_temp(self, summaries: Dict[str, str], research_area: str) -> str:
        """Save summaries to a readable JSON file in the temp directory"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"summaries_{timestamp}.json"
        filepath = os.path.join(TEMP_DIR, filename)

        output_data = {
            "timestamp": datetime.now().isoformat(),
            "research_area": research_area,
            "summaries": summaries
        }

        with open(filepath, "w", encoding='utf-8') as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)

        return filepath
    
    def read_summaries_from_temp(self, filepath: str) -> Dict[str, str]:
        """Read summaries from a Json file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data["summaries"]

    def generate_section_prompt(self, section_name: str, summary: str, research_area: str) -> str:
        """Generate appropriate prompts for each section"""
        prompts = {
            'introduction': f"""
                Generate a comprehensive introduction section for a survey paper about {research_area}.
                Use this summary as a basis: {summary}
                
                The introduction should:
                1. Provide context and motivation for the research area
                2. Highlight the significance of the topic
                3. Present the main challenges and open problems
                4. Outline the structure of the survey
                
                Format the output in LaTeX.
            """,
            
            'background': f"""
                Create a detailed background/literature review section for a survey paper about {research_area}.
                Base it on this summary: {summary}
                
                The background should:
                1. Present the theoretical foundations
                2. Discuss key concepts and definitions
                3. Review historical developments
                4. Identify major research trends
                
                Format the output in LaTeX.
            """,
            
            'methodology': f"""
                Generate a methodology section for a survey paper about {research_area}.
                Based on this summary: {summary}
                
                The methodology should:
                1. Categorize and compare different approaches
                2. Analyze technical aspects
                3. Present frameworks and architectures
                4. Discuss advantages and limitations
                
                Format the output in LaTeX.
            """,
            
            'results': f"""
                Create a comprehensive results section for a survey paper about {research_area}.
                Using this summary: {summary}
                
                The results should:
                1. Present key findings and insights
                2. Compare different approaches
                3. Discuss performance metrics
                4. Analyze trends and patterns
                
                Format the output in LaTeX.
            """,
            
            'discussion': f"""
                Generate a discussion section for a survey paper about {research_area}.
                Based on this summary: {summary}
                
                The discussion should:
                1. Synthesize key findings
                2. Identify research gaps
                3. Present challenges and opportunities
                4. Suggest future research directions
                
                Format the output in LaTeX.
            """,
            
            'conclusion': f"""
                Create a conclusion section for a survey paper about {research_area}.
                Using this summary: {summary}
                
                The conclusion should:
                1. Summarize main findings
                2. Highlight key contributions
                3. Discuss implications
                4. Suggest future work
                
                Format the output in LaTeX.
            """
        }
        
        return prompts.get(section_name, "")

    def generate_latex_header(self, research_area: str) -> str:
        """Generate LaTeX header with proper formatting"""
        current_date = datetime.now().strftime("%B %Y")
        
        return f"""\\documentclass[11pt,a4paper]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{amsmath}}
\\usepackage{{amsfonts}}
\\usepackage{{amssymb}}
\\usepackage{{graphicx}}
\\usepackage{{hyperref}}
\\usepackage{{natbib}}
\\usepackage{{doi}}

\\title{{A Comprehensive Survey on {research_area}}}
\\author{{Generated by AI Survey Generator}}
\\date{{{current_date}}}

\\begin{{document}}

\\maketitle

\\begin{{abstract}}
This survey provides a comprehensive overview of recent advances in {research_area}.
It synthesizes findings from multiple research papers, presenting key developments,
methodologies, and future directions in the field.
\\end{{abstract}}

"""

    def generate_latex_footer(self) -> str:
        """Generate LaTeX footer"""
        return "\n\\end{document}"

    def process_section(self, section_name: str, summary: str, research_area: str) -> str:
        """Process a single section using DeepSeek"""
        prompt = self.generate_section_prompt(section_name, summary, research_area)
        section_content = self.deepseek_agent.generate_section(prompt, section_name)
        return section_content

    async def generate_survey(self, pdf_files: List[str], research_area: str) -> str:
        """Main method to generate the complete survey"""
        try:
            # Step 1: Process PDFs and get summaries using Gemini
            section_summaries = self.gemini_agent.process_pdf(pdf_files)

            if not section_summaries:
                raise ValueError("Failed to generate section summaries")
            
            summaries_filepath = self.save_summaries_to_temp(section_summaries, research_area)
            print(f"Summaries saved to: {summaries_filepath}")
            
            # Step 2: Generate LaTeX content for each section using DeepSeek
            latex_sections = {}
            for section_name in self.section_order:
                if section_name in section_summaries:
                    try:
                        summary = section_summaries[section_name]
                        latex_content = self.process_section(
                            section_name, 
                            summary, 
                            research_area
                        )
                        latex_sections[section_name] = latex_content
                        print(f"Section {section_name} generated by DeepSeek!")
                        await asyncio.sleep(1)
                    except Exception as e:
                        print(f"Error generating section {section_name}: {str(e)}")
                        continue

            if not latex_sections:
                raise ValueError("Failed to generate any LaTeX sections")
            
            # Step 3: Combine all sections into a complete LaTeX document
            header = self.generate_latex_header(research_area)
            footer = self.generate_latex_footer()
            
            full_content = [header]
            for section_name in self.section_order:
                if section_name in latex_sections:
                    full_content.append(latex_sections[section_name])
            full_content.append(footer)
            
            # Step 4: Save the complete survey
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{research_area}_survey_{timestamp}.tex"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(full_content))
            
            return filepath
            
        except Exception as e:
            print(f"Error generating survey: {str(e)}")
            raise

    async def validate_survey_length(self, filepath: str) -> bool:
        """Validate that the survey meets length requirements"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                # Rough estimation of pages (about 40 lines per page)
                num_lines = len(content.split('\n'))
                estimated_pages = num_lines / 40
                return 40 <= estimated_pages <= 50
        except Exception as e:
            print(f"Error validating survey length: {str(e)}")
            return False

class SurveyProgress:
    """Helper class to track survey generation progress"""
    def __init__(self):
        self.total_steps = len(SurveyGenerator().section_order) + 2  # sections + pdf processing + compilation
        self.current_step = 0
        self.status_message = ""

    def update(self, message: str):
        self.current_step += 1
        self.status_message = message

    @property
    def progress_percentage(self) -> float:
        return (self.current_step / self.total_steps) * 100