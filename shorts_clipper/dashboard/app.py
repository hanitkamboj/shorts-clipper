from __future__ import annotations
import logging
import socket
import os

logger = logging.getLogger(__name__)

try:
    import gradio as gr
except ImportError:
    gr = None
    logger.warning("Gradio not installed. Please install gradio to use the dashboard.")

from .components.home import build_home_tab
from .components.sources import build_sources_tab
from .components.settings_ui import build_settings_tab
from .components.providers import build_providers_tab


def get_free_port(start_port: int = 7860, max_port: int = 7900) -> int:
    """Find a free port starting from start_port."""
    for port in range(start_port, max_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            res = sock.connect_ex(('localhost', port))
            if res != 0:
                return port
    return start_port

def create_app():
    """Create the Gradio Blocks app with all tabs."""
    if gr is None:
        logger.error("Cannot create app: Gradio is not installed.")
        return None
        
    theme = gr.themes.Default(primary_hue="blue", secondary_hue="slate")
    
    with gr.Blocks(title="Shorts Clipper AI", theme=theme) as app:
        gr.Markdown("# 🎬 Shorts Clipper AI Factory")
        
        components = {}
        
        components.update(build_home_tab())
        components.update(build_sources_tab())
        
        # Placeholders
        with gr.Tab("🎬 Clips"):
            gr.Markdown("### Clip Review (Coming Soon)")
        with gr.Tab("🤖 AI Scores"):
            gr.Markdown("### AI Scoring Details (Coming Soon)")
        with gr.Tab("📝 Captions"):
            gr.Markdown("### Caption Style Selection (Coming Soon)")
        with gr.Tab("🖼️ Thumbnails"):
            gr.Markdown("### Thumbnail Review (Coming Soon)")
        with gr.Tab("🔍 SEO"):
            gr.Markdown("### SEO Scores and Metadata (Coming Soon)")
        with gr.Tab("📤 Upload Queue"):
            gr.Markdown("### Upload Management (Coming Soon)")
        with gr.Tab("📅 Scheduler"):
            gr.Markdown("### Scheduling (Coming Soon)")
        with gr.Tab("✅ Published"):
            gr.Markdown("### Published Clips (Coming Soon)")
            
        components.update(build_settings_tab())
        components.update(build_providers_tab())
        
        with gr.Tab("📊 Logs"):
            gr.Markdown("### Structured Logs Viewer (Coming Soon)")
            
    return app

def launch_dashboard(share: bool = False, port: int = 7860):
    """Launch the dashboard, handling port conflicts and share gracefully."""
    app = create_app()
    if app is None:
        print("Failed to launch dashboard: Gradio is not installed.")
        return
        
    actual_port = get_free_port(port)
    
    # Auto-enable share in known cloud environments
    is_cloud = os.environ.get("KAGGLE_KERNEL_RUN_TYPE") or os.environ.get("JUPYTER_SERVER_URL")
    if is_cloud:
        share = True
        
    print(f"Starting Gradio dashboard on port {actual_port}...")
    try:
        app.launch(server_port=actual_port, share=share)
    except Exception as e:
        logger.warning(f"Failed to launch with share={share}: {e}")
        if share:
            logger.info("Attempting to launch without share...")
            try:
                app.launch(server_port=actual_port, share=False)
            except Exception as e2:
                logger.error(f"Failed to launch dashboard entirely: {e2}")
