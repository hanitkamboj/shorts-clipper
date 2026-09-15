from __future__ import annotations
import logging

logger = logging.getLogger(__name__)

try:
    import gradio as gr
except ImportError:
    gr = None

def build_settings_tab() -> dict:
    if gr is None:
        return {}
        
    components = {}
    
    with gr.Tab("⚙️ Settings"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 🎤 Audio & Captions")
                components["whisper_model"] = gr.Dropdown(
                    label="Whisper Model",
                    choices=["tiny", "base", "small", "medium", "large-v3"],
                    value="base"
                )
                components["whisper_accuracy"] = gr.Radio(
                    label="Whisper Accuracy",
                    choices=["FAST", "BALANCED", "HIGH", "MAXIMUM"],
                    value="BALANCED"
                )
                components["caption_style"] = gr.Dropdown(
                    label="Caption Style",
                    choices=["CLEAN", "BOLD", "KARAOKE", "MRBEAST_LIKE", "PODCAST", "MINIMAL", "CUSTOM"],
                    value="BOLD"
                )
                
                gr.Markdown("### 🎥 Video Processing")
                components["crop_mode"] = gr.Dropdown(
                    label="Crop Mode",
                    choices=["center", "smart_face", "smart_speaker", "auto"],
                    value="smart_face"
                )
                components["thumbnail_mode"] = gr.Dropdown(
                    label="Thumbnail Mode",
                    choices=["best_face", "best_emotion", "best_composition", "first_frame", "ai_selected"],
                    value="ai_selected"
                )
                
            with gr.Column():
                gr.Markdown("### 🚀 Publishing")
                components["upload_mode"] = gr.Radio(
                    label="Upload Mode",
                    choices=["Manual", "Review", "Auto Upload", "Auto Schedule", "Auto Publish"],
                    value="Review"
                )
                
                gr.Markdown("### 💻 System Options")
                components["output_dir"] = gr.Textbox(label="Output Directory", value="output/")
                components["cache_dir"] = gr.Textbox(label="Cache Directory", value="cache/")
                components["max_workers"] = gr.Slider(minimum=1, maximum=16, step=1, value=4, label="Max Workers")
                components["quality_threshold"] = gr.Slider(minimum=0, maximum=100, step=1, value=75, label="Quality Threshold")
                components["timezone"] = gr.Dropdown(label="Timezone", choices=["UTC", "America/New_York", "Europe/London", "Asia/Kolkata"], value="UTC")
                
        with gr.Row():
            components["btn_save_settings"] = gr.Button("Save Settings", variant="primary")
            
    return components
