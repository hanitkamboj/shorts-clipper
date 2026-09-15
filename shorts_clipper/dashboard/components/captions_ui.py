from __future__ import annotations
try:
    import gradio as gr
except ImportError:
    gr = None

from shorts_clipper.captions.styles import CaptionStyle, get_style_config

def build_captions_tab() -> dict:
    """Full interactive Dynamic Captions Studio tab."""
    if gr is None:
        return {}

    with gr.Tab("📝 Captions"):
        gr.Markdown("### 📝 Dynamic Subtitle & Typography Studio")
        with gr.Row():
            with gr.Column(scale=2):
                style_dropdown = gr.Dropdown(
                    label="Caption Style Preset",
                    choices=[s.value for s in CaptionStyle],
                    value="mrbeast_like",
                    interactive=True,
                )
                font_name = gr.Dropdown(label="Font Family", choices=["Arial Black", "Montserrat", "Impact", "Inter Bold", "Roboto"], value="Arial Black", interactive=True)
                font_size = gr.Slider(label="Font Size", minimum=24, maximum=96, value=56, step=2)
                words_per_group = gr.Slider(label="Words Shown Concurrently", minimum=1, maximum=6, value=2, step=1)
                with gr.Row():
                    primary_color = gr.ColorPicker(label="Primary Text Color", value="#FFFFFF")
                    highlight_color = gr.ColorPicker(label="Karaoke Active Word Color", value="#FFE600")
                with gr.Row():
                    outline_color = gr.ColorPicker(label="Outline/Border Color", value="#000000")
                    outline_width = gr.Slider(label="Outline Thickness", minimum=0.0, maximum=8.0, value=3.5, step=0.5)
                animation_mode = gr.Dropdown(label="Word Pop Animation", choices=["pop", "fade", "slide", "none"], value="pop")
                uppercase = gr.Checkbox(label="Force ALL CAPS (High Energy)", value=True)
                btn_apply = gr.Button("⚡ Re-render Captions on Active Clip", variant="primary")

            with gr.Column(scale=3):
                gr.Markdown("#### 👁️ Real-time Typography Preview")
                preview_html = gr.HTML(
                    value="""
                    <div style="background: #111827; border-radius: 12px; padding: 40px; text-align: center; height: 380px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                        <p style="font-family: 'Arial Black', Impact, sans-serif; font-size: 42px; font-weight: 900; color: #FFFFFF; text-shadow: -2px -2px 0 #000, 2px -2px 0 #000, -2px 2px 0 #000, 2px 2px 0 #000; margin: 0; line-height: 1.2;">
                            WAIT UNTIL YOU SEE <span style="color: #FFE600; text-decoration: underline;">THIS SECRET</span>
                        </p>
                        <p style="color: #9ca3af; margin-top: 30px; font-size: 14px;">9:16 Center-Safe Position: Margin Bottom 90px</p>
                    </div>
                    """
                )
                caption_status = gr.Textbox(label="Subtitle Engine Status", value="ASS Subtitles compiled with libass GPU renderer. Ready.", interactive=False)

        def update_preview(style, font, size, prim, high, anim, caps):
            text_color = prim
            hi_color = high
            text = "WAIT UNTIL YOU SEE THIS SECRET" if caps else "Wait until you see this secret"
            html = f"""
            <div style="background: #111827; border-radius: 12px; padding: 40px; text-align: center; height: 380px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                <p style="font-family: '{font}', sans-serif; font-size: {int(size * 0.7)}px; font-weight: 900; color: {text_color}; text-shadow: -2px -2px 0 #000, 2px -2px 0 #000, -2px 2px 0 #000, 2px 2px 0 #000; margin: 0; line-height: 1.2;">
                    WAIT UNTIL YOU SEE <span style="color: {hi_color}; text-decoration: underline;">THIS SECRET</span>
                </p>
                <p style="color: #9ca3af; margin-top: 30px; font-size: 14px;">Style: {style.upper()} | Font: {font} | Animation: {anim}</p>
            </div>
            """
            return html

        for comp in [style_dropdown, font_name, font_size, primary_color, highlight_color, animation_mode, uppercase]:
            comp.change(update_preview, inputs=[style_dropdown, font_name, font_size, primary_color, highlight_color, animation_mode, uppercase], outputs=[preview_html])

    return {"style_dropdown": style_dropdown}
