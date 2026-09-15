from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

@dataclass
class DuplicateCheckResult:
    is_duplicate: bool
    reason: str
    matched_clip_id: str | None = None
    similarity_score: float = 0.0

class DuplicateDetector:
    def __init__(self, db_manager: Any = None):
        self._db = db_manager
    
    def check(self, clip_path: Path | None = None, transcript: str = '', source_video_id: str = '', start_time: float = 0.0, end_time: float = 0.0) -> DuplicateCheckResult:
        """Check for duplicates using multiple strategies.
        
        1. Exact file hash (if file provided)
        2. Transcript similarity (Jaccard/word overlap)
        3. Timestamp overlap (same source, overlapping times)
        4. Source video ID (check if already processed)
        """
        # 1. Timestamp overlap
        if source_video_id and end_time > start_time:
            ts_result = self.check_timestamp_overlap(source_video_id, start_time, end_time)
            if ts_result and ts_result.is_duplicate:
                return ts_result

        # 2. Exact File Hash
        if clip_path and clip_path.exists():
            file_hash = self.compute_file_hash(clip_path)
            # Without a real DB, we can't reliably look this up globally, 
            # but in a real scenario we'd query the DB for this hash
            if self._db and hasattr(self._db, 'find_clip_by_hash'):
                matched_id = self._db.find_clip_by_hash(file_hash)
                if matched_id:
                    return DuplicateCheckResult(
                        is_duplicate=True,
                        reason="Exact file hash match",
                        matched_clip_id=matched_id,
                        similarity_score=1.0
                    )

        # 3. Transcript Similarity
        if transcript and self._db and hasattr(self._db, 'get_recent_transcripts'):
            # Fetch recently generated transcripts from DB to compare against
            recent_clips = self._db.get_recent_transcripts(limit=100)
            for clip_id, past_transcript in recent_clips:
                score = self.compute_transcript_similarity(transcript, past_transcript)
                if score > 0.85:  # 85% overlap is highly likely a duplicate
                    return DuplicateCheckResult(
                        is_duplicate=True,
                        reason="High transcript similarity",
                        matched_clip_id=clip_id,
                        similarity_score=score
                    )

        return DuplicateCheckResult(is_duplicate=False, reason="No duplicates found")
    
    def compute_file_hash(self, file_path: Path) -> str:
        """SHA256 hash of video file."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Read and update hash in chunks of 4K
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            log.error(f"Failed to compute file hash for {file_path}: {e}")
            return ""
    
    def compute_transcript_similarity(self, text1: str, text2: str) -> float:
        """Jaccard word-level similarity."""
        if not text1 or not text2:
            return 0.0
            
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0.0
            
        return len(intersection) / len(union)
    
    def check_timestamp_overlap(self, source_id: str, start: float, end: float, min_overlap: float = 10.0) -> DuplicateCheckResult | None:
        """Check if another clip from the same source overlaps significantly."""
        if not self._db or not hasattr(self._db, 'get_clips_by_source'):
            return None
            
        existing_clips = self._db.get_clips_by_source(source_id)
        
        for clip in existing_clips:
            clip_start = getattr(clip, 'start_time', 0.0)
            clip_end = getattr(clip, 'end_time', 0.0)
            clip_id = getattr(clip, 'id', 'unknown')
            
            # Calculate overlap duration
            overlap_start = max(start, clip_start)
            overlap_end = min(end, clip_end)
            overlap_duration = max(0.0, overlap_end - overlap_start)
            
            if overlap_duration >= min_overlap:
                # We have a significant overlap
                return DuplicateCheckResult(
                    is_duplicate=True,
                    reason=f"Timestamp overlap of {overlap_duration:.1f}s",
                    matched_clip_id=clip_id,
                    similarity_score=1.0
                )
                
        return None
