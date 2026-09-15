from __future__ import annotations
import logging

logger = logging.getLogger(__name__)

try:
    import gradio as gr
except ImportError:
    gr = None

def build_sources_tab() -> dict:
    if gr is None:
        return {}
        
    components = {}
    
    with gr.Tab("📥 Sources"):
        with gr.Row():
            with gr.Column():
                components["source_mode"] = gr.Dropdown(
                    label="Source Mode",
                    choices=["Single URL", "Multiple URLs", "Playlist", "Channel", "Search Query", "Local Video", "Uploaded File"],
                    value="Single URL"
                )
                components["urls_input"] = gr.TextArea(label="URLs (one per line)", placeholder="Paste URLs here...")
                components["file_upload"] = gr.File(label="Upload Batch Manifest (CSV/TXT/JSON)")
                
                components["project_name"] = gr.Textbox(label="Project Name", placeholder="My Awesome Project")
                components["niche"] = gr.Textbox(label="Niche/Topic", placeholder="e.g. Gaming, Tech, Finance")
                
            with gr.Column():
                components["language"] = gr.Dropdown(
                    label="Language",
                    choices=["Auto", "English", "Hindi", "Hinglish", "Spanish", "French", "German"],
                    value="Auto"
                )
                components["duration"] = gr.Dropdown(
                    label="Duration Preset",
                    choices=["15s", "20s", "30s", "45s", "60s", "90s", "3min", "AI Choose Best"],
                    value="60s"
                )
                components["clip_count"] = gr.Slider(minimum=1, maximum=250, step=1, value=5, label="Clip Count")
                
                components["quality"] = gr.Radio(
                    label="Quality Preset",
                    choices=["STANDARD", "HIGH", "MAXIMUM"],
                    value="STANDARD"
                )
                
                components["strategy"] = gr.Dropdown(
                    label="Strategy Preset",
                    choices=["VIRAL", "EDUCATIONAL", "STORY", "PODCAST", "NEWS", "MOTIVATIONAL", "FUNNY", "CONTROVERSIAL", "CUSTOM"],
                    value="VIRAL"
                )
                
        with gr.Row():
            components["btn_analyze"] = gr.Button("Analyze Sources")
            components["btn_generate"] = gr.Button("Generate Clips", variant="primary")
            
        with gr.Row():
            components["status_output"] = gr.Textbox(label="Status", interactive=False, lines=5)
            
    return components
