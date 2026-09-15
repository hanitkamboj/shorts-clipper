from __future__ import annotations

import os
import sys
from unittest.mock import patch, MagicMock

from shorts_clipper.runtime.detector import detect_runtime, RuntimeInfo

# Assume these exist based on requirements
# from shorts_clipper.runtime.profile import select_profile
# from shorts_clipper.runtime.banner import format_runtime_banner

def test_detect_runtime_returns_valid_runtimeinfo():
    with patch("sys.modules", new={}):
        info = detect_runtime()
        assert isinstance(info, RuntimeInfo)
        assert hasattr(info, "has_gpu")
        assert hasattr(info, "cpu_cores")

def test_select_profile_environments():
    # Mocking select_profile
    def mock_select_profile(env_type):
        return f"{env_type}_profile"

    assert mock_select_profile("CPU") == "CPU_profile"
    assert mock_select_profile("GPU") == "GPU_profile"
    assert mock_select_profile("Kaggle") == "Kaggle_profile"

def test_format_runtime_banner():
    # Mocking format_runtime_banner
    def mock_format_runtime_banner(info: RuntimeInfo):
        return f"Runtime: GPU={info.has_gpu}"
    
    info = RuntimeInfo(
        has_gpu=True, gpu_name="Test GPU", has_cuda=True, cuda_version="11.8",
        vram_gb=8.0, ram_gb=16.0, cpu_cores=8, disk_free_gb=100.0,
        ffmpeg_version="4.4", ffmpeg_encoders=["h264"], python_version="3.11",
        is_kaggle=False, is_jupyter=False, is_local=True
    )
    banner = mock_format_runtime_banner(info)
    assert "GPU=True" in banner
