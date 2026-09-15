from __future__ import annotations

import os
import sys
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List


@dataclass
class RuntimeInfo:
    """Dataclass holding information about the current runtime environment and hardware."""
    has_gpu: bool
    gpu_name: Optional[str]
    has_cuda: bool
    cuda_version: Optional[str]
    vram_gb: float
    ram_gb: float
    cpu_cores: int
    disk_free_gb: float
    ffmpeg_version: Optional[str]
    ffmpeg_encoders: List[str]
    python_version: str
    is_kaggle: bool
    is_jupyter: bool
    is_local: bool


def detect_runtime() -> RuntimeInfo:
    """
    Detects hardware capabilities and runtime environment.
    Gracefully handles failures for all detection routines.
    """
    has_gpu = False
    gpu_name = None
    has_cuda = False
    cuda_version = None
    vram_gb = 0.0

    try:
        import torch
        has_cuda = torch.cuda.is_available()
        has_gpu = has_cuda
        if has_cuda:
            gpu_name = torch.cuda.get_device_name(0)
            vram_bytes = torch.cuda.get_device_properties(0).total_memory
            vram_gb = vram_bytes / (1024 ** 3)
            if hasattr(torch.version, 'cuda'):
                cuda_version = torch.version.cuda
    except Exception:
        pass

    ram_gb = 0.0
    try:
        import psutil
        ram_gb = psutil.virtual_memory().total / (1024 ** 3)
    except ImportError:
        pass

    cpu_cores = os.cpu_count() or 1

    disk_free_gb = 0.0
    try:
        disk_usage = shutil.disk_usage('.')
        disk_free_gb = disk_usage.free / (1024 ** 3)
    except Exception:
        pass

    ffmpeg_version = None
    ffmpeg_encoders = []
    try:
        # Check ffmpeg version
        result = subprocess.run(
            ['ffmpeg', '-version'], 
            capture_output=True, 
            text=True, 
            check=False
        )
        if result.returncode == 0:
            first_line = result.stdout.split('\n')[0]
            parts = first_line.split()
            if len(parts) > 2:
                ffmpeg_version = parts[2]

        # Check ffmpeg encoders
        enc_result = subprocess.run(
            ['ffmpeg', '-encoders'], 
            capture_output=True, 
            text=True, 
            check=False
        )
        if enc_result.returncode == 0:
            for line in enc_result.stdout.split('\n'):
                line = line.strip()
                # Encodes typically start with 'V' for Video, 'A' for Audio, etc.
                if line.startswith('V'):
                    parts = line.split()
                    if len(parts) >= 2:
                        ffmpeg_encoders.append(parts[1])
    except Exception:
        pass

    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    is_kaggle = 'KAGGLE_KERNEL_RUN_TYPE' in os.environ or Path('/kaggle/working').exists()

    is_jupyter = False
    try:
        if 'ipykernel' in sys.modules or 'IPython' in sys.modules:
            is_jupyter = True
    except Exception:
        pass

    is_local = not is_kaggle

    return RuntimeInfo(
        has_gpu=has_gpu,
        gpu_name=gpu_name,
        has_cuda=has_cuda,
        cuda_version=cuda_version,
        vram_gb=vram_gb,
        ram_gb=ram_gb,
        cpu_cores=cpu_cores,
        disk_free_gb=disk_free_gb,
        ffmpeg_version=ffmpeg_version,
        ffmpeg_encoders=ffmpeg_encoders,
        python_version=python_version,
        is_kaggle=is_kaggle,
        is_jupyter=is_jupyter,
        is_local=is_local
    )
