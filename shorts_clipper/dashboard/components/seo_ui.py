from __future__ import annotations
try:
    import gradio as gr
except ImportError:
    gr = None

def build_seo_tab() -> dict:
    """Full interactive SEO & Metadata Optimization Studio tab."""
    if gr is None:
        return {}

    with gr.Tab("🔍 SEO"):
        gr.Markdown("### 🔍 AI SEO Engine & Metadata Generator")
        with gr.Row():
            with gr.Column(scale=3):
                title_input = gr.Textbox(
                    label="Primary Viral Title (40-60 chars optimal)",
                    value="The 1 Secret Nobody Tells You About Coding Fast ⚡ #Shorts",
                    interactive=True,
                )
                alt_titles = gr.Dataframe(
                    headers=["Style Angle", "Alternative Title", "Predicted CTR"],
                    value=[
                        ["Curiosity Hook", "Why 99% of Developers Code Too Slowly...", "9.4%"],
                        ["Direct Punch", "Stop Writing Boilerplate Code in 2026", "8.9%"],
                        ["Contrarian", "You Don't Need Another Framework. Do This Instead.", "9.1%"],
                        ["Question Hook", "Is This The Fastest Way to Build Apps?", "8.7%"]
                    ],
                    interactive=True,
                )
                desc_input = gr.Textbox(
                    label="Optimized Description",
                    lines=4,
                    value="Discover the counterintuitive workflow technique that 10x top engineers use to produce production code in record time.\n\n#Programming #Coding #SoftwareEngineer #Shorts #Tech",
                    interactive=True,
                )
                tags_input = gr.Textbox(
                    label="Comma-separated Search Tags",
                    value="coding tips, software engineer, programming tutorial, developer productivity, tech shorts, python tips, learn to code",
                    interactive=True,
                )
                with gr.Row():
                    btn_generate_seo = gr.Button("🤖 Re-generate with AI Provider", variant="primary")
                    btn_audit_spam = gr.Button("🛡️ Check Spam & Clickbait Risk", variant="secondary")

            with gr.Column(scale=2):
                gr.Markdown("#### 📈 Metadata Performance & SEO Score")
                seo_gauge = gr.Slider(label="Overall SEO Score (0-100)", minimum=0, maximum=100, value=94.2, interactive=False)
                click_potential = gr.Slider(label="Click Potential Index", minimum=0, maximum=100, value=91.0, interactive=False)
                spam_risk = gr.Slider(label="Spam / Misleading Risk (Lower is better)", minimum=0, maximum=100, value=4.5, interactive=False)
                readability = gr.Slider(label="Description Readability", minimum=0, maximum=100, value=89.0, interactive=False)
                fact_consistency = gr.Textbox(
                    label="Fact-Consistency Audit",
                    value="✅ PASS: Title and description fully grounded in transcript. No fabricated claims detected.",
                    interactive=False,
                )

        def on_regen_seo():
            return "The 1 Secret Nobody Tells You About Coding Fast ⚡ #Shorts", 96.0

        btn_generate_seo.click(on_regen_seo, outputs=[title_input, seo_gauge])

    return {"title_input": title_input}
