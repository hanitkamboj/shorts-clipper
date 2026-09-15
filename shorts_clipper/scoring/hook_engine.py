from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

@dataclass
class HookAnalysis:
    """Analysis of the hook quality of a clip."""
    hook_score: float  # 0-100
    hook_type: str  # 'question', 'surprise', 'conflict', 'claim', 'promise', 'contradiction', 'emotion', 'generic'
    hook_reason: str
    first_second_score: float
    first_three_seconds_score: float
    first_sentence_score: float
    curiosity_score: float
    surprise_score: float

class HookEngine:
    """Analyzes the beginning of a clip for hook quality."""
    
    def analyze_hook(self, segments: list[dict[str, Any]], full_text: str = '') -> HookAnalysis:
        """Analyze the hook quality of the first few seconds."""
        if not segments and not full_text:
            return HookAnalysis(
                hook_score=0.0,
                hook_type='generic',
                hook_reason='No content provided.',
                first_second_score=0.0,
                first_three_seconds_score=0.0,
                first_sentence_score=0.0,
                curiosity_score=0.0,
                surprise_score=0.0
            )
            
        text = full_text or " ".join(seg.get('text', '') for seg in segments)
        text = text.strip()
        
        hook_type = 'generic'
        hook_reason = 'Starts with standard phrasing.'
        curiosity = 50.0
        surprise = 50.0
        
        if text.startswith('Why ') or text.startswith('How ') or '?' in text[:50]:
            hook_type = 'question'
            hook_reason = 'Presents an intriguing question immediately.'
            curiosity = 85.0
        elif 'never' in text[:50].lower() or 'secret' in text[:50].lower():
            hook_type = 'promise'
            hook_reason = 'Promises hidden or exclusive knowledge.'
            curiosity = 90.0
            
        score = (curiosity + surprise) / 2
        
        return HookAnalysis(
            hook_score=score,
            hook_type=hook_type,
            hook_reason=hook_reason,
            first_second_score=score * 0.9,
            first_three_seconds_score=score,
            first_sentence_score=score * 1.1,
            curiosity_score=curiosity,
            surprise_score=surprise
        )
