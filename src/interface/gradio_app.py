import gradio as gr
from src.models.survey_model import SurveyGenerator

class GradioInterface:
    def __init__(self):
        self.survey_generatos = SurveyGenerator()

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
                
                generate_btn = gr.Button("Generate Survey")
                output =- gr.File(label="Generated Survey (TEX)")

                generate_btn.click(
                    fn=self.survey_generatos.generate_survey,
                    inputs=[pdf_files, research_area],
                    outputs=output
                )

            return interface
        
        def launch(self):
            interface = self.create_interface()
            interface.launch()