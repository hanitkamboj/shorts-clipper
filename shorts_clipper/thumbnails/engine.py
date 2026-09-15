from __future__ import annotations
import logging
import subprocess
import tempfile
import json
from dataclasses import dataclass
from pathlib import Path
from enum import StrEnum

log = logging.getLogger(__name__)

class ThumbnailMode(StrEnum):
    BEST_FACE = 'best_face'
    BEST_EMOTION = 'best_emotion'
    BEST_COMPOSITION = 'best_composition'
    FIRST_FRAME = 'first_frame'
    AI_SELECTED = 'ai_selected'
    MANUAL = 'manual'

@dataclass
class ThumbnailCandidate:
    frame_path: Path
    timestamp: float
    score: float
    face_count: int
    brightness: float
    contrast: float
    sharpness: float
    composition_score: float
    selection_reason: str

@dataclass
class ThumbnailResult:
    selected: ThumbnailCandidate
    candidates: list[ThumbnailCandidate]
    mode: ThumbnailMode

class ThumbnailEngine:
    def __init__(self, output_dir: Path = Path('thumbnails')):
        self._output_dir = output_dir
        self._output_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_candidates(self, video_path: Path, count: int = 10, clip_id: str = '') -> list[ThumbnailCandidate]:
        """Extract candidate thumbnail frames from a video."""
        video_path = Path(video_path).resolve()
        temp_dir = Path(tempfile.mkdtemp(prefix=f"thumb_{clip_id}_"))
        
        # Simple extraction at intervals as a fallback to scene detection
        # Try to get duration first
        duration = 0.0
        try:
            cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', str(video_path)]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            duration = float(res.stdout.strip())
        except Exception as e:
            log.warning(f"Could not get duration for {video_path}: {e}")
            duration = 10.0 # fallback

        interval = max(duration / (count + 1), 0.1)
        
        candidates = []
        for i in range(count):
            ts = interval * (i + 1)
            out_file = temp_dir / f"frame_{i:03d}.jpg"
            
            # extract frame
            cmd = ['ffmpeg', '-y', '-ss', str(ts), '-i', str(video_path), '-frames:v', '1', '-q:v', '2', str(out_file)]
            try:
                subprocess.run(cmd, capture_output=True, check=True)
                if out_file.exists():
                    stats = self._score_frame(out_file)
                    # Basic scoring based on stats
                    score = stats.get('brightness', 0) * 0.5 + stats.get('contrast', 0) * 0.5
                    
                    cand = ThumbnailCandidate(
                        frame_path=out_file,
                        timestamp=ts,
                        score=score,
                        face_count=0, # no OpenCV, keep 0
                        brightness=stats.get('brightness', 0.0),
                        contrast=stats.get('contrast', 0.0),
                        sharpness=0.0,
                        composition_score=0.5,
                        selection_reason='Interval extraction'
                    )
                    candidates.append(cand)
            except subprocess.CalledProcessError as e:
                log.warning(f"Error extracting frame at {ts}: {e}")

        return candidates
        
    def select_best(self, candidates: list[ThumbnailCandidate], mode: ThumbnailMode = ThumbnailMode.BEST_COMPOSITION) -> ThumbnailResult:
        """Select the best thumbnail from candidates."""
        if not candidates:
            raise ValueError("No candidates provided")
        
        # Sort by score descending
        sorted_candidates = sorted(candidates, key=lambda c: c.score, reverse=True)
        best = sorted_candidates[0]
        best.selection_reason = f"Selected based on highest score for {mode}"
        
        return ThumbnailResult(selected=best, candidates=candidates, mode=mode)
        
    def generate_thumbnail(self, video_path: Path, clip_id: str = '', mode: ThumbnailMode = ThumbnailMode.BEST_COMPOSITION) -> ThumbnailResult:
        """Full thumbnail generation pipeline."""
        candidates = self.extract_candidates(video_path, count=10, clip_id=clip_id)
        result = self.select_best(candidates, mode)
        
        # copy best to output dir
        best_path = self._output_dir / f"{clip_id}_thumb.jpg"
        result.selected.frame_path.rename(best_path)
        result.selected.frame_path = best_path
        return result
        
    def _score_frame(self, frame_path: Path) -> dict[str, float]:
        """Score a single frame for thumbnail quality using ffprobe."""
        stats = {'brightness': 0.0, 'contrast': 0.0}
        try:
            cmd = [
                'ffprobe', '-f', 'lavfi', '-i',
                f"movie={frame_path},signalstats",
                '-show_entries', 'frame_tags=lavfi.signalstats.YAVG,lavfi.signalstats.YVAR',
                '-of', 'json', '-v', 'error'
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(res.stdout)
            
            if 'frames' in data and len(data['frames']) > 0:
                tags = data['frames'][0].get('tags', {})
                yavg = float(tags.get('lavfi.signalstats.YAVG', 0))
                yvar = float(tags.get('lavfi.signalstats.YVAR', 0))
                
                # Normalize YAVG (0-255) to 0-1, penalize too dark or too bright
                brightness = yavg / 255.0
                b_score = 1.0 - abs(brightness - 0.5) * 2
                
                # Normalize variance as contrast proxy
                contrast = min(yvar / 5000.0, 1.0)
                
                stats['brightness'] = b_score
                stats['contrast'] = contrast
        except Exception as e:
            log.warning(f"Error scoring frame {frame_path}: {e}")
            
        return stats
