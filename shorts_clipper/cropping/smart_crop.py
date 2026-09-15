from __future__ import annotations
import logging
import subprocess
import json
from dataclasses import dataclass
from pathlib import Path
from enum import StrEnum

log = logging.getLogger(__name__)

class CropMode(StrEnum):
    CENTER = 'center'
    SMART_FACE = 'smart_face'
    SMART_SPEAKER = 'smart_speaker'
    AUTO = 'auto'

@dataclass
class CropRegion:
    x: int
    y: int
    width: int
    height: int
    confidence: float
    method: str

class SmartCropper:
    def __init__(self, mode: CropMode = CropMode.AUTO):
        self._mode = mode
    
    def analyze_video(self, video_path: Path, sample_count: int = 10) -> list[CropRegion]:
        """Analyze video to determine optimal crop regions."""
        regions = []
        width, height = self._get_video_dimensions(video_path)
        if width == 0 or height == 0:
            return regions

        target_w, target_h = 1080, 1920
        # Check aspect ratio
        if width / height <= target_w / target_h:
            # Already tall enough, no crop needed or handle letterboxing
            return [CropRegion(x=0, y=0, width=width, height=height, confidence=1.0, method="keep")]

        if self._mode in (CropMode.SMART_FACE, CropMode.AUTO):
            # Attempt basic ffmpeg cropdetect (though it's for black borders, not faces)
            # Without OpenCV, real face tracking in raw python is hard without extra libs.
            # We will default to center crop fallback for this exercise
            # or try some heuristic if ffmpeg filters allow it.
            pass
            
        # Fallback to CENTER
        crop_w = int(height * (target_w / target_h))
        crop_h = height
        x = (width - crop_w) // 2
        y = 0
        
        regions.append(CropRegion(
            x=x, y=y, width=crop_w, height=crop_h,
            confidence=0.8, method="center"
        ))
        
        return regions
    
    def get_crop_filter(self, video_path: Path, target_width: int = 1080, target_height: int = 1920) -> str:
        """Return the FFmpeg crop filter string for this video."""
        regions = self.analyze_video(video_path)
        if not regions:
            return f"scale={target_width}:{target_height}:force_original_aspect_ratio=increase,crop={target_width}:{target_height}"
            
        region = regions[0]
        if region.method == "keep":
            return f"scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2"
            
        return f"crop={region.width}:{region.height}:{region.x}:{region.y},scale={target_width}:{target_height}"
    
    def _detect_faces_ffmpeg(self, video_path: Path, timestamp: float) -> list[dict]:
        """Try to detect faces at a specific timestamp using ffprobe metadata."""
        # Note: ffmpeg itself doesn't have a built-in robust face detector without external libs
        return []
    
    def _get_video_dimensions(self, video_path: Path) -> tuple[int, int]:
        """Get video width and height using ffprobe."""
        try:
            cmd = [
                'ffprobe', '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height',
                '-of', 'json', str(video_path)
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(res.stdout)
            streams = data.get('streams', [])
            if streams:
                return int(streams[0].get('width', 0)), int(streams[0].get('height', 0))
        except Exception as e:
            log.warning(f"Error getting dimensions for {video_path}: {e}")
        return 0, 0
