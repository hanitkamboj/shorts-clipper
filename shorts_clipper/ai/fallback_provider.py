from __future__ import annotations

import re
import datetime
from typing import Any

from .provider import AIProvider
from .schemas import MetadataResult, ClipScore, ResearchResult, TranscriptAnalysis


class FallbackProvider:
    """A deterministic fallback provider that uses heuristics instead of external APIs."""
    
    @property
    def name(self) -> str:
        return "fallback"

    def generate_metadata(
        self, 
        transcript_text: str, 
        source_title: str = '', 
        source_channel: str = '', 
        niche: str = 'general'
    ) -> MetadataResult:
        sentences = [s.strip() for s in re.split(r'[.!?]+', transcript_text) if s.strip()]
        
        title = sentences[0] if sentences else (source_title or "Untitled Clip")
        if len(title) > 60:
            title = title[:57] + "..."
            
        description = " ".join(sentences[:3]) if sentences else "A short clip."
        
        words = re.findall(r'\b\w{5,}\b', transcript_text.lower())
        unique_words = list(dict.fromkeys(words))
        tags = unique_words[:10]
        hashtags = [f"#{tag}" for tag in unique_words[:5]]
        
        return MetadataResult(
            title=title,
            alternative_titles=[f"{title} - Part 2", f"{source_channel} Highlight"],
            description=description,
            tags=tags,
            hashtags=hashtags,
            thumbnail_text=title[:20],
            seo_score=50.0,
            confidence=1.0
        )
        
    def score_clip(self, transcript_text: str, clip_context: dict[str, Any] | None = None) -> ClipScore:
        word_count = len(transcript_text.split())
        question_marks = transcript_text.count('?')
        exclamations = transcript_text.count('!')
        
        # Simple heuristics
        base_score = min(10.0, word_count / 20.0)
        hook_score = min(10.0, 5.0 + (question_marks + exclamations) * 0.5)
        
        overall = (base_score + hook_score) / 2
        
        return ClipScore(
            hook_score=hook_score,
            curiosity=min(10.0, question_marks * 1.5),
            emotion=min(10.0, exclamations * 1.5),
            narrative=base_score,
            info_density=base_score,
            context=5.0,
            retention=overall,
            overall=overall,
            reasoning="Scored using local heuristics (word count, punctuation)."
        )
        
    def research(self, query: str, locale: str = 'en') -> ResearchResult:
        return ResearchResult(
            related_terms=[f"{query} tips", f"{query} guide"],
            trending_phrases=[f"best {query}"],
            competitor_patterns=["Top 10 lists", "How-to guides"],
            audience_language="Informal",
            timestamp=datetime.datetime.now(),
            method="local_heuristic"
        )
        
    def analyze_transcript(self, transcript_text: str) -> TranscriptAnalysis:
        sentences = [s.strip() for s in re.split(r'[.!?]+', transcript_text) if s.strip()]
        
        return TranscriptAnalysis(
            topics=["General Discussion"],
            emotional_peaks=[sentences[i] for i, s in enumerate(sentences) if '!' in s][:3],
            hooks=[sentences[0]] if sentences else [],
            claims=["Various points discussed in the text"],
            narrative_arcs=["Beginning to end"],
            key_moments=sentences[:3] if sentences else []
        )
        
    def is_available(self) -> bool:
        return True
