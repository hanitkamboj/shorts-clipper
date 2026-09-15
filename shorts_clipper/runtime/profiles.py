from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from shorts_clipper.runtime.detector import RuntimeInfo


class ExecutionProfile(Enum):
    """Available execution profiles based on hardware and environment."""
    ULTRA_LOW = auto()
    CPU = auto()
    GPU_SMALL = auto()
    GPU_MEDIUM = auto()
    GPU_LARGE = auto()
    KAGGLE_AUTO = auto()
    CUSTOM = auto()


@dataclass
class ProfileConfig:
    """Configuration associated with an ExecutionProfile."""
    whisper_model: str
    whisper_device: str
    whisper_compute_type: str
    max_gpu_workers: int
    max_cpu_workers: int
    max_metadata_concurrency: int
    max_upload_concurrency: int
    video_codec: str
    video_preset: str
    batch_size: int


def select_profile(runtime: RuntimeInfo) -> ExecutionProfile:
    """
    Auto-select an appropriate execution profile based on hardware runtime info.
    """
    if runtime.is_kaggle:
        return ExecutionProfile.KAGGLE_AUTO

    if not runtime.has_gpu or runtime.vram_gb < 2:
        if runtime.ram_gb > 0 and runtime.ram_gb < 4 or runtime.cpu_cores <= 2:
            return ExecutionProfile.ULTRA_LOW
        return ExecutionProfile.CPU

    if runtime.vram_gb < 6:
        return ExecutionProfile.GPU_SMALL
    elif runtime.vram_gb < 12:
        return ExecutionProfile.GPU_MEDIUM
    else:
        return ExecutionProfile.GPU_LARGE


def get_profile_config(profile: ExecutionProfile) -> ProfileConfig:
    """
    Returns the associated configuration and sensible defaults for a given profile.
    """
    if profile == ExecutionProfile.ULTRA_LOW:
        return ProfileConfig(
            whisper_model="tiny",
            whisper_device="cpu",
            whisper_compute_type="int8",
            max_gpu_workers=0,
            max_cpu_workers=1,
            max_metadata_concurrency=1,
            max_upload_concurrency=1,
            video_codec="libx264",
            video_preset="ultrafast",
            batch_size=1
        )
    elif profile == ExecutionProfile.CPU:
        return ProfileConfig(
            whisper_model="base",
            whisper_device="cpu",
            whisper_compute_type="int8",
            max_gpu_workers=0,
            max_cpu_workers=2,
            max_metadata_concurrency=2,
            max_upload_concurrency=2,
            video_codec="libx264",
            video_preset="veryfast",
            batch_size=2
        )
    elif profile == ExecutionProfile.GPU_SMALL:
        return ProfileConfig(
            whisper_model="small",
            whisper_device="cuda",
            whisper_compute_type="float16",
            max_gpu_workers=1,
            max_cpu_workers=4,
            max_metadata_concurrency=3,
            max_upload_concurrency=2,
            video_codec="h264_nvenc",
            video_preset="fast",
            batch_size=4
        )
    elif profile == ExecutionProfile.GPU_MEDIUM:
        return ProfileConfig(
            whisper_model="medium",
            whisper_device="cuda",
            whisper_compute_type="float16",
            max_gpu_workers=2,
            max_cpu_workers=6,
            max_metadata_concurrency=5,
            max_upload_concurrency=3,
            video_codec="h264_nvenc",
            video_preset="medium",
            batch_size=8
        )
    elif profile == ExecutionProfile.GPU_LARGE:
        return ProfileConfig(
            whisper_model="large-v3",
            whisper_device="cuda",
            whisper_compute_type="float16",
            max_gpu_workers=4,
            max_cpu_workers=8,
            max_metadata_concurrency=10,
            max_upload_concurrency=4,
            video_codec="h264_nvenc",
            video_preset="slow",
            batch_size=16
        )
    elif profile == ExecutionProfile.KAGGLE_AUTO:
        return ProfileConfig(
            whisper_model="medium",
            whisper_device="cuda",
            whisper_compute_type="float16",
            max_gpu_workers=2,
            max_cpu_workers=4,
            max_metadata_concurrency=5,
            max_upload_concurrency=3,
            video_codec="libx264",
            video_preset="fast",
            batch_size=8
        )
    else:  # CUSTOM or fallback
        return ProfileConfig(
            whisper_model="base",
            whisper_device="cpu",
            whisper_compute_type="float32",
            max_gpu_workers=1,
            max_cpu_workers=2,
            max_metadata_concurrency=1,
            max_upload_concurrency=1,
            video_codec="libx264",
            video_preset="fast",
            batch_size=1
        )
