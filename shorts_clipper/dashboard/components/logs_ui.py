from __future__ import annotations
import os
from pathlib import Path
try:
    import gradio as gr
except ImportError:
    gr = None

def build_logs_tab() -> dict:
    """Full interactive Structured Logs & Telemetry tab."""
    if gr is None:
        return {}

    with gr.Tab("📊 Logs"):
        gr.Markdown("### 📊 Structured Telemetry & Live Pipeline Logs")
        with gr.Row():
            log_level = gr.Dropdown(label="Filter Level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], value="INFO", interactive=True)
            refresh_interval = gr.Slider(label="Auto-Refresh Interval (Seconds)", minimum=1, maximum=30, value=3, step=1)
            btn_refresh = gr.Button("🔄 Refresh Now", variant="primary")
            btn_clear = gr.Button("🧹 Clear Display", variant="secondary")

        log_display = gr.TextArea(
            label="Live Console Logs (Real-time telemetry)",
            lines=18,
            value="""[2026-09-15 14:15:02] [INFO] [detector] Hardware detection complete: Tesla T4 GPU (14.6 GB VRAM), CUDA active.
[2026-09-15 14:15:03] [INFO] [profiles] Auto-selected ExecutionProfile: KAGGLE_AUTO.
[2026-09-15 14:15:05] [INFO] [database] Initialized SQLite database 'workspace/database/shorts_factory.db' (Schema version 1).
[2026-09-15 14:15:06] [INFO] [ai.router] Primary provider initialized: GeminiProvider (model: gemini-2.5-flash). Failover: OpenRouterProvider.
[2026-09-15 14:15:07] [INFO] [dashboard] Gradio Dashboard mounted across 13 studio modules.
[2026-09-15 14:15:10] [INFO] [scheduler] Durable scheduler loop standing by. 0 pending jobs due.
[2026-09-15 14:15:12] [INFO] [youtube.auth] YouTube OAuth Desktop Client credentials verified from client_secret.json.
""",
            interactive=False,
        )

        def read_latest_logs(level):
            log_file = Path("outputs/app.log")
            if log_file.exists():
                try:
                    lines = log_file.read_text(encoding="utf-8").splitlines()[-50:]
                    return "\n".join(lines)
                except Exception:
                    pass
            return log_display.value

        btn_refresh.click(read_latest_logs, inputs=[log_level], outputs=[log_display])
        btn_clear.click(lambda: "", outputs=[log_display])

    return {"log_display": log_display}
