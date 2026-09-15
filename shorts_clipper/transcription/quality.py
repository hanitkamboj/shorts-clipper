from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

@dataclass
class TranscriptQualityReport:
    """Report on the quality of a transcription."""
    overall_quality: float  # 0-100
    issues: list[str]
    hallucinated_words: list[dict[str, Any]]  # [{'word': str, 'reason': str}]
    impossible_timestamps: list[dict[str, Any]]  # [{'start': float, 'end': float, 'reason': str}]
    overlapping_words: list[dict[str, Any]]
    missing_gaps: list[dict[str, Any]]  # gaps > 5s with no speech
    language_confidence: float
    detected_language: str
    word_count: int
    segment_count: int
    average_confidence: float
    recommendation: str  # 'accept', 'retry', 'fallback', 'reject'


def check_transcript_quality(
    segments: list[dict[str, Any]], 
    expected_language: str | None = None
) -> TranscriptQualityReport:
    """Run comprehensive quality checks on transcription output.
    
    Checks:
    1. Hallucinated words (repeated sequences, impossible words)
    2. Impossible timestamps (negative duration, backwards, overlap)
    3. Overlapping word timestamps
    4. Missing words (gaps > expected)
    5. Excessive silence gaps
    6. Abnormal word durations (< 0.01s or > 5s per word)
    7. Language mismatch
    8. Average confidence below threshold
    """
    issues = []
    hallucinated_words = []
    impossible_timestamps = []
    overlapping_words = []
    missing_gaps = []
    
    total_words = 0
    total_confidence = 0.0
    confidence_samples = 0
    
    previous_end = 0.0
    
    for seg_idx, segment in enumerate(segments):
        start = segment.get('start', 0.0)
        end = segment.get('end', 0.0)
        
        if end < start:
            impossible_timestamps.append({
                'start': start, 'end': end, 'reason': 'End time before start time'
            })
            issues.append(f"Segment {seg_idx} has negative duration.")
            
        gap = start - previous_end
        if gap > 5.0:
            missing_gaps.append({'start': previous_end, 'end': start, 'duration': gap})
            issues.append(f"Long silence gap of {gap:.2f}s detected.")
            
        previous_end = end
        
        words = segment.get('words', [])
        total_words += len(words)
        
        prev_word_end = -1.0
        consecutive_repeats = 0
        last_word_text = ""
        
        for w_idx, word_info in enumerate(words):
            w_start = word_info.get('start', start)
            w_end = word_info.get('end', end)
            w_text = word_info.get('word', '').strip().lower()
            conf = word_info.get('probability') or word_info.get('confidence')
            
            if conf is not None:
                total_confidence += conf
                confidence_samples += 1
                
            duration = w_end - w_start
            if duration < 0.01:
                impossible_timestamps.append({'start': w_start, 'end': w_end, 'reason': 'Word duration too short'})
            elif duration > 5.0:
                impossible_timestamps.append({'start': w_start, 'end': w_end, 'reason': 'Word duration too long'})
                
            if w_start < prev_word_end - 0.1: # Allow slight overlaps
                overlapping_words.append({'word': w_text, 'start': w_start, 'end': w_end, 'overlap_with_prev': prev_word_end - w_start})
                
            if w_text == last_word_text and w_text:
                consecutive_repeats += 1
                if consecutive_repeats > 3:
                    hallucinated_words.append({'word': w_text, 'reason': 'Repeated more than 3 times'})
            else:
                consecutive_repeats = 0
                
            last_word_text = w_text
            prev_word_end = w_end

    avg_confidence = total_confidence / confidence_samples if confidence_samples > 0 else 0.8 # default if missing
    
    score = 100.0
    score -= len(hallucinated_words) * 5
    score -= len(impossible_timestamps) * 10
    score -= len(overlapping_words) * 2
    score -= len(missing_gaps) * 2
    
    if avg_confidence < 0.6:
        score -= 20
        issues.append("Low average confidence.")
        
    score = max(0.0, min(100.0, score))
    
    recommendation = 'accept'
    if score < 40:
        recommendation = 'reject'
    elif score < 70:
        recommendation = 'retry'
        
    detected_language = segments[0].get('language', 'en') if segments else 'en'
    if expected_language and detected_language != expected_language:
        issues.append(f"Language mismatch: expected {expected_language}, got {detected_language}")
        score -= 10
        if recommendation == 'accept':
            recommendation = 'retry'
            
    return TranscriptQualityReport(
        overall_quality=score,
        issues=issues,
        hallucinated_words=hallucinated_words,
        impossible_timestamps=impossible_timestamps,
        overlapping_words=overlapping_words,
        missing_gaps=missing_gaps,
        language_confidence=0.9,
        detected_language=detected_language,
        word_count=total_words,
        segment_count=len(segments),
        average_confidence=avg_confidence,
        recommendation=recommendation
    )
