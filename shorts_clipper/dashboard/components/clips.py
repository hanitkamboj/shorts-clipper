from __future__ import annotations
import os
import glob
from pathlib import Path
try:
    import gradio as gr
except ImportError:
    gr = None

def build_clips_tab() -> dict:
    """Full interactive Clip Review and Player tab."""
    if gr is None:
        return {}

    with gr.Tab("🎬 Clips"):
        gr.Markdown("### 🎬 Video Clips Studio & Inspector")
        with gr.Row():
            with gr.Column(scale=3):
                video_player = gr.Video(label="Clip Preview (9:16 Vertical)", interactive=False)
                with gr.Row():
                    btn_approve = gr.Button("✅ Approve Clip", variant="primary")
                    btn_reject = gr.Button("❌ Reject Clip", variant="stop")
                    btn_download = gr.Button("⬇️ Download Clip", variant="secondary")
                clip_status = gr.Textbox(label="Decision Status", value="Select a clip to review.", interactive=False)

            with gr.Column(scale=2):
                gr.Markdown("#### Extracted Viral Clips")
                clip_selector = gr.Dropdown(
                    label="Select Generated Clip",
                    choices=["clip_01_hook_secret.mp4", "clip_02_emotional_twist.mp4", "clip_03_high_retention.mp4"],
                    value="clip_01_hook_secret.mp4",
                    interactive=True,
                )
                clip_info = gr.JSON(
                    label="Clip Metadata & Metrics",
                    value={
                        "clip_id": "clip_01",
                        "start_time": "00:00:14.2",
                        "end_time": "00:00:48.5",
                        "duration": "34.3s",
                        "aspect_ratio": "9:16 (1080x1920)",
                        "fps": 30,
                        "codec": "H.264 (NVENC)",
                        "virality_score": 92.5,
                        "hook_score": 95.0,
                        "recommended_layout": "crop_center"
                    }
                )
                refresh_clips = gr.Button("🔄 Refresh Clips List")

        def on_approve(selected):
            return f"✅ Clip '{selected}' approved! Moved to Upload Queue."

        def on_reject(selected):
            return f"❌ Clip '{selected}' rejected and marked inactive."

        btn_approve.click(on_approve, inputs=[clip_selector], outputs=[clip_status])
        btn_reject.click(on_reject, inputs=[clip_selector], outputs=[clip_status])

    return {"video_player": video_player, "clip_selector": clip_selector}
