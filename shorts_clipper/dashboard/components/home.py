from __future__ import annotations
import logging

logger = logging.getLogger(__name__)

try:
    import gradio as gr
except ImportError:
    gr = None
    logger.warning("Gradio not installed. Dashboard components will not be available.")

def build_home_tab() -> dict:
    if gr is None:
        return {}
        
    components = {}
    
    with gr.Tab("🏠 Dashboard"):
        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("### 📊 System Status")
                components["runtime_info"] = gr.Markdown("Loading system information...")
                
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ Current Run")
                components["run_status"] = gr.Markdown("Status: Idle")
                components["queue_summary"] = gr.Markdown("Total: 0 | Completed: 0 | Failed: 0 | Pending: 0")
        
        with gr.Row():
            components["progress_bar"] = gr.Slider(minimum=0, maximum=100, value=0, label="Operation Progress", interactive=False)
            
        with gr.Row():
            gr.Markdown("### ⚡ GPU Utilization")
            components["gpu_util"] = gr.Markdown("GPU utilization data not available.")
            
        with gr.Row():
            components["btn_new_project"] = gr.Button("New Project", variant="primary")
            components["btn_start_processing"] = gr.Button("Start Processing", variant="primary")
            components["btn_view_queue"] = gr.Button("View Queue")
            
    return components
