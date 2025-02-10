import gradio as gr
import asyncio
from src.models.survey_model import SurveyGenerator, SurveyProgress

class GradioInterface:
    def __init__(self):
        self.survey_generator = SurveyGenerator()
        self.progress = SurveyProgress()

        async def generate_survey_with_progress(self, pdf_files, research_area):
            try:
                # Update progress
                self.progress_update("Processing PDF files...")
                yield self.progress.status_message, self.progress.progress_percentage

                # Generate survey
                filepath = await self.survey_generator.generate_survey(pdf_files, research_area)

                # Validate survey length
                if not await self.survey_generator.validate_survey_length(filepath):
                    raise ValueError("Generated survey does not meet length requirements")
                
                self.progress.update("Survey generation complete!")
                yield self.progress.status_message, self.progress.progress_percentage

                return filepath
            
            except Exception as e:
                self.progress.update(f"Error: {str(e)}")
                yield self.progress.status_message, self.progress.progress_percentage

        def create_interface(self):
            with gr.Blocks() as interface:
                gr.Markdown("# Research Survey Generatos")

                with gr.Row():
                    pdf_files = gr.File(
                        file_count="multiple",
                        label="Upload PDF Files (max 10 papers)"
                    )
                    research_area = gr.Textbox(
                        label="Research Area",
                        placeholder="Enter the research area..."
                    )
                
                with gr.Row():
                    status = gr.Textbox(label="Status")
                    progress = gr.Slider(
                        minimum=0,
                        maximum=100,
                        value=0,
                        label="Progress"
                    )

                generate_btn = gr.Button("Generate Survey")
                output = gr.File(label="Generated Survey (TEX)")

                generate_btn.click(
                    fn=self.survey_generator.generate_survey,
                    inputs=[pdf_files, research_area],
                    outputs=output
                )

            return interface
        
        def launch(self):
            interface = self.create_interface()
            interface.launch()