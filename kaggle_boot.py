#!/usr/bin/env python3
"""AI Shorts Factory — Kaggle Bootstrap

Single-command startup for Kaggle notebooks:
    python kaggle_boot.py
"""
from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path

def main():
    print('='*50)
    print('AI SHORTS FACTORY')
    print('='*50)
    print()
    
    # 1. Detect environment
    from shorts_clipper.runtime import detect_runtime, select_profile, format_runtime_banner
    runtime = detect_runtime()
    profile = select_profile(runtime)
    print(format_runtime_banner(runtime, profile))
    
    # 2. Check/install missing dependencies
    _check_dependencies()
    
    # 3. Check FFmpeg
    if not runtime.ffmpeg_version:
        print('WARNING: FFmpeg not found. Some features will be limited.')
        _try_install_ffmpeg()
    
    # 4. Create required directories
    workspace = Path(os.environ.get('SHORTS_OUTPUT_DIR', 'workspace'))
    for subdir in ['projects', 'cache', 'models', 'transcripts', 'clips', 'thumbnails', 'metadata', 'research', 'uploads', 'schedules', 'logs', 'database']:
        (workspace / subdir).mkdir(parents=True, exist_ok=True)
    
    # 5. Initialize database
    from shorts_clipper.database import DatabaseManager
    db = DatabaseManager(workspace / 'database' / 'shorts_factory.db')
    print(f'Database: READY ({db.get_schema_version()})')
    db.close()
    
    # 6. Start dashboard
    print()
    is_kaggle = runtime.is_kaggle
    is_jupyter = runtime.is_jupyter
    
    from shorts_clipper.dashboard.app import launch_dashboard
    launch_dashboard(share=(is_kaggle or is_jupyter), port=7860)

def _check_dependencies():
    """Check and install missing Python dependencies."""
    required = ['gradio', 'pydantic']
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f'Installing missing dependencies: {missing}')
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q'] + missing)
        print('Dependencies installed.')

def _try_install_ffmpeg():
    """Try to install ffmpeg in Kaggle/Linux environments."""
    if sys.platform == 'linux':
        try:
            subprocess.run(['apt-get', 'update', '-qq'], check=False, capture_output=True)
            subprocess.run(['apt-get', 'install', '-y', '-qq', 'ffmpeg'], check=False, capture_output=True)
            print('FFmpeg installed successfully.')
        except Exception:
            print('Could not auto-install FFmpeg. Please install manually.')

if __name__ == '__main__':
    main()
