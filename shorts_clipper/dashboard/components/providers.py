from __future__ import annotations
import logging

logger = logging.getLogger(__name__)

try:
    import gradio as gr
except ImportError:
    gr = None

def build_providers_tab() -> dict:
    if gr is None:
        return {}
        
    components = {}
    
    with gr.Tab("🔌 Providers"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 🧠 AI Providers")
                components["ai_provider"] = gr.Dropdown(
                    label="Active AI Provider",
                    choices=["Gemini", "OpenRouter", "Ollama", "Fallback/Offline"],
                    value="Gemini"
                )
                
                with gr.Group():
                    gr.Markdown("#### Gemini Settings")
                    components["gemini_api_key"] = gr.Textbox(label="API Key", type="password")
                    components["gemini_model"] = gr.Dropdown(label="Model", choices=["gemini-1.5-flash", "gemini-1.5-pro"], value="gemini-1.5-flash")
                
                with gr.Group():
                    gr.Markdown("#### OpenRouter Settings")
                    components["openrouter_api_key"] = gr.Textbox(label="API Key", type="password")
                    components["openrouter_model"] = gr.Textbox(label="Model", value="anthropic/claude-3-haiku")
                    components["openrouter_base_url"] = gr.Textbox(label="Base URL", value="https://openrouter.ai/api/v1")
                
                with gr.Group():
                    gr.Markdown("#### Ollama Settings")
                    components["ollama_base_url"] = gr.Textbox(label="Base URL", value="http://localhost:11434")
                    components["ollama_model"] = gr.Textbox(label="Model", value="llama3")
                
                gr.Markdown("#### Failover Chain")
                components["failover_chain"] = gr.CheckboxGroup(
                    label="Provider Chain Order",
                    choices=["Gemini", "OpenRouter", "Ollama"],
                    value=["Gemini", "OpenRouter"]
                )
                
            with gr.Column():
                gr.Markdown("### 📺 YouTube Integration")
                components["yt_status"] = gr.Markdown("Status: **Not Connected**")
                components["yt_channel"] = gr.Markdown("Channel: None")
                with gr.Row():
                    components["btn_yt_connect"] = gr.Button("Connect YouTube")
                    components["btn_yt_disconnect"] = gr.Button("Disconnect")
                    
                gr.Markdown("### 🛠️ Actions")
                components["btn_test_provider"] = gr.Button("Test Provider")
                components["test_output"] = gr.Textbox(label="Test Output", interactive=False)
                components["btn_save_providers"] = gr.Button("Save Provider Settings", variant="primary")
                
    return components
