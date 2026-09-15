from __future__ import annotations
try:
    import gradio as gr
except ImportError:
    gr = None

from shorts_clipper.thumbnails.engine import ThumbnailMode

def build_thumbnails_tab() -> dict:
    """Full interactive Thumbnail Engine Studio tab."""
    if gr is None:
        return {}

    with gr.Tab("🖼️ Thumbnails"):
        gr.Markdown("### 🖼️ High-CTR Thumbnail Studio & Keyframe Inspector")
        with gr.Row():
            with gr.Column(scale=2):
                mode_dropdown = gr.Dropdown(
                    label="Auto-Selection Strategy",
                    choices=[m.value for m in ThumbnailMode],
                    value="best_face",
                    interactive=True,
                )
                text_overlay = gr.Textbox(label="High-CTR Text Overlay (Optional)", placeholder="e.g., DON'T DO THIS!", value="NEVER AGAIN!")
                overlay_color = gr.ColorPicker(label="Text Banner Color", value="#FFCC00")
                font_size = gr.Slider(label="Overlay Text Size", minimum=20, maximum=80, value=48)
                extract_count = gr.Slider(label="Sample Frame Extraction Density", minimum=5, maximum=30, value=12, step=1)
                btn_generate_thumb = gr.Button("🎨 Re-Score & Extract Thumbnails", variant="primary")

            with gr.Column(scale=3):
                gr.Markdown("#### 📸 Best Candidate Keyframe")
                thumb_preview = gr.Image(label="Active Thumbnail (1080x1920 9:16)", interactive=False)
                with gr.Row():
                    score_face = gr.Number(label="Face Clarity Score", value=95.4, interactive=False)
                    score_contrast = gr.Number(label="Contrast Score", value=88.2, interactive=False)
                    score_sharpness = gr.Number(label="Motion Blur/Sharpness", value=92.1, interactive=False)
                thumb_status = gr.Textbox(label="Frame Extraction Log", value="Extracted 12 scene-change keyframes. Highest composite CTR frame selected at 00:00:23.4.", interactive=False)

    return {"mode_dropdown": mode_dropdown}
