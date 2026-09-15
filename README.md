<div align="center">

# 🎬 AI Shorts Factory

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Gradio](https://img.shields.io/badge/UI-Gradio-orange.svg)](https://gradio.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An automated, AI-powered clipping and publishing engine that turns long-form content into high-quality, engaging short-form videos.

</div>

---

## 🌟 What is AI Shorts Factory?

**AI Shorts Factory** (formerly `shorts-clipper`) is a production-grade pipeline designed to intelligently analyze, clip, reframe, caption, and publish videos. By leveraging state-of-the-art AI models for transcription, multi-layered editorial scoring, and smart cropping, it ensures that only the most engaging clips make it to your audience.

---

## ✨ Core Features

- **Gradio Dashboard**: An intuitive, web-based UI for managing sources, reviewing clips, and monitoring schedules.
- **8-Judge Editorial Engine**: Multi-layer scoring system evaluating hook quality, narrative arc, visual interest, and virality potential.
- **Smart Cropping**: AI-driven facial and object tracking to automatically reframe landscape videos into perfectly centered 9:16 vertical shorts.
- **Dynamic Caption Engine**: Generate engaging, customizable, and perfectly timed subtitles tailored to different styles.
- **Thumbnail Generation**: Automatically capture and design compelling thumbnails for maximum click-through rates.
- **SEO Research Agent**: AI-powered keyword and metadata optimization for maximum organic reach.
- **Durable Scheduler & Quota Manager**: Built-in SQLite-backed task queue ensuring robust API quota management and scheduled publishing.
- **Batch Processor & Coordinator**: Effortlessly queue multiple videos and process them overnight or in the background.

---

## 🚀 Kaggle-Native Deployment

Running the AI Shorts Factory on Kaggle is the easiest way to access free GPU acceleration for intensive tasks like Whisper transcription and video rendering.

1. **Open a New Notebook**: Go to Kaggle and create a new notebook.
2. **Enable GPU**: In the right sidebar under "Settings > Accelerator", select `GPU T4 x2` or `GPU P100`.
3. **Set Secrets**: In the "Add-ons > Secrets" menu, add `GEMINI_API_KEY`, `OPENROUTER_API_KEY`, and any YouTube API credentials.
4. **Import the Notebook**: You can upload the provided `kaggle/AI_Shorts_Factory.ipynb` directly, or simply clone the repo and run `python kaggle_boot.py` to get the public Gradio link.

---

## ⚙️ Setup & Configuration

### Step 1: Gemini API Setup
1. Visit the [Google AI Studio](https://aistudio.google.com/).
2. Generate an API key.
3. Add `GEMINI_API_KEY=your_key_here` to your `.env` file.

### Step 2: OpenRouter Setup (Optional for Alternative LLMs)
1. Sign up at [OpenRouter](https://openrouter.ai/).
2. Create an API key and fund your account if necessary.
3. Add `OPENROUTER_API_KEY=your_key_here` to your `.env` file.

### Step 3: YouTube OAuth2 & Google Cloud Setup
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project and enable the **YouTube Data API v3**.
3. Configure the OAuth consent screen and create OAuth 2.0 Client IDs (Desktop application).
4. Download the `client_secrets.json` and place it in the project root.
5. The first time you upload, you will be prompted to authenticate via a browser link.

---

## 💻 CLI Usage

AI Shorts Factory comes with a powerful CLI for automation and headless operation.

```bash
# Launch the Gradio dashboard locally
python -m shorts_clipper serve

# Process a single video immediately
python -m shorts_clipper clip --url "https://youtube.com/..." --output-dir ./clips

# Run in fully autonomous mode
python -m shorts_clipper autopilot --playlist "https://youtube.com/playlist..."

# Run system diagnostics
python -m shorts_clipper doctor

# Prepare for Kaggle environment
python -m shorts_clipper kaggle

# Manage and download local AI models
python -m shorts_clipper models
```

---

## 🏗️ Architecture Overview

The system is built on a modular, event-driven architecture using Python 3.11+.

- **Video Processing**: Managed by `ffmpeg` and local AI tracking models for cropping.
- **AI Brain**: Powered by Gemini 1.5 Pro/Flash for transcript analysis and scoring.
- **Storage**: SQLite for robust state management and job queuing.
- **UI**: Gradio-based frontend for seamless user interaction.

*For more details, see [ARCHITECTURE.md](ARCHITECTURE.md).*

---

## 🔑 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API Key for core AI tasks | Yes |
| `OPENROUTER_API_KEY`| OpenRouter API Key for alternative LLMs | No |
| `YOUTUBE_CLIENT_SECRET_FILE`| Path to YouTube OAuth client secret JSON | No |
| `LOG_LEVEL` | Logging level (`INFO`, `DEBUG`, `WARNING`) | No |
| `DB_PATH` | Path to SQLite database (default: `clipper.db`) | No |
| `MAX_CONCURRENT_JOBS`| Number of parallel processing tasks | No |

---

## ❓ Troubleshooting & FAQ

**Q: FFmpeg errors during cropping?**  
A: Ensure FFmpeg is installed and added to your system PATH. You can verify this by running `python -m shorts_clipper doctor`.

**Q: Gradio dashboard isn't loading on Kaggle?**  
A: Ensure you pass `--share` to the boot script or set `share=True` in the Python API. Check the console output for the public `*.gradio.live` link.

**Q: I keep hitting API rate limits?**  
A: The Durable Scheduler manages quotas automatically. If you hit limits, the system will pause and resume when the quota resets.
