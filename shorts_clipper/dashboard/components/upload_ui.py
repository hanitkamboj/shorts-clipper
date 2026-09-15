from __future__ import annotations
try:
    import gradio as gr
except ImportError:
    gr = None

def build_upload_tab() -> dict:
    """Full interactive Upload Queue & YouTube Dispatch tab."""
    if gr is None:
        return {}

    with gr.Tab("📤 Upload Queue"):
        gr.Markdown("### 📤 YouTube Shorts Upload Queue & Quota Dispatcher")
        with gr.Row():
            with gr.Column(scale=3):
                queue_table = gr.Dataframe(
                    headers=["Job ID", "Clip Title", "Platform", "Privacy", "Status", "Scheduled Time"],
                    value=[
                        ["job_001", "The 1 Secret Nobody Tells You About Coding Fast ⚡", "YouTube Shorts", "public", "READY", "Immediate"],
                        ["job_002", "Stop Writing Boilerplate Code in 2026", "YouTube Shorts", "public", "QUEUED", "2026-09-16 14:00 UTC"],
                        ["job_003", "Why 99% of Developers Code Too Slowly...", "YouTube Shorts", "unlisted", "QUEUED", "2026-09-17 18:30 UTC"]
                    ],
                    interactive=True,
                )
                with gr.Row():
                    btn_start_upload = gr.Button("🚀 Start Upload Processing", variant="primary")
                    btn_pause_queue = gr.Button("⏸️ Pause Queue", variant="secondary")
                    btn_retry_failed = gr.Button("🔄 Retry Failed Jobs", variant="secondary")
                    btn_clear_done = gr.Button("🧹 Clear Completed", variant="secondary")

                upload_status = gr.Textbox(label="Uploader Dispatch Status", value="Queue active. Authenticated with YouTube Channel 'Shorts Factory'.", interactive=False)

            with gr.Column(scale=2):
                gr.Markdown("#### 📊 Daily YouTube API Quota Monitor")
                quota_slider = gr.Slider(label="Estimated Quota Used Today (1,600 / 10,000)", minimum=0, maximum=10000, value=1600, interactive=False)
                uploads_count = gr.Number(label="Shorts Uploaded Today", value=1, interactive=False)
                remaining_uploads = gr.Number(label="Estimated Safe Uploads Remaining Today", value=5, interactive=False)
                quota_alert = gr.Textbox(label="Quota State", value="✅ HEALTHY: 8,400 quota units available before auto-pause.", interactive=False)

        def on_start_upload():
            return "🚀 Upload initialized: Uploading 'job_001' to YouTube Shorts with resumable chunks..."

        btn_start_upload.click(on_start_upload, outputs=[upload_status])

    return {"queue_table": queue_table}
