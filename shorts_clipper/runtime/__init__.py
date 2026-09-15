from __future__ import annotations

from shorts_clipper.runtime.detector import RuntimeInfo, detect_runtime
from shorts_clipper.runtime.profiles import (
    ExecutionProfile,
    ProfileConfig,
    select_profile,
    get_profile_config,
)

__all__ = [
    "RuntimeInfo",
    "detect_runtime",
    "ExecutionProfile",
    "ProfileConfig",
    "select_profile",
    "get_profile_config",
    "format_runtime_banner",
]


def format_runtime_banner(info: RuntimeInfo, profile: ExecutionProfile) -> str:
    """Format runtime and profile information into a clean display banner."""
    env = "Kaggle" if info.is_kaggle else ("Jupyter" if info.is_jupyter else "Local")

    gpu_str = info.gpu_name if info.has_gpu else "None"
    vram_str = f"{info.vram_gb:.1f} GB" if info.has_gpu else "N/A"
    cuda_str = "Available" if info.has_cuda else "Unavailable"
    cpu_str = f"{info.cpu_cores} cores"
    ram_str = f"{info.ram_gb:.1f} GB" if info.ram_gb > 0 else "Unknown"
    disk_str = f"{info.disk_free_gb:.0f} GB"

    ffmpeg_ver = info.ffmpeg_version if info.ffmpeg_version else "Not Found"
    # Match requirement format like '7.x'
    if ffmpeg_ver != "Not Found" and "." in ffmpeg_ver:
        # Avoid crashing if the version is strangely formatted
        parts = ffmpeg_ver.split(".")
        if len(parts) > 0 and parts[0].isdigit():
            ffmpeg_ver = f"{parts[0]}.x"

    lines = [
        "Runtime",
        "────────────────────────────",
        f"Environment: {env}",
        f"GPU: {gpu_str}",
        f"VRAM: {vram_str}",
        f"CUDA: {cuda_str}",
        f"CPU: {cpu_str}",
        f"RAM: {ram_str}",
        f"Disk Free: {disk_str}",
        f"FFmpeg: {ffmpeg_ver}",
        f"Execution Profile: {profile.name}"
    ]
    return "\n".join(lines)
