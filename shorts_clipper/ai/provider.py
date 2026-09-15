from __future__ import annotations

from typing import Any, Protocol

from .schemas import MetadataResult, ClipScore, ResearchResult, TranscriptAnalysis


class ProviderError(Exception):
    """Base exception for provider errors."""
    pass


class QuotaExhaustedError(ProviderError):
    """Exception raised when a provider's quota is exhausted."""
    pass


class AIProvider(Protocol):
    """Protocol defining the interface for AI providers."""
    
    @property
    def name(self) -> str:
        """The name of the provider."""
        ...
        
    def generate_metadata(
        self, 
        transcript_text: str, 
        source_title: str = '', 
        source_channel: str = '', 
        niche: str = 'general'
    ) -> MetadataResult:
        """Generate metadata for a clip based on its transcript."""
        ...
        
    def score_clip(self, transcript_text: str, clip_context: dict[str, Any] | None = None) -> ClipScore:
        """Score a clip based on its transcript and context."""
        ...
        
    def research(self, query: str, locale: str = 'en') -> ResearchResult:
        """Perform research on a given query."""
        ...
        
    def analyze_transcript(self, transcript_text: str) -> TranscriptAnalysis:
        """Analyze a full transcript to extract topics, hooks, and key moments."""
        ...
        
    def is_available(self) -> bool:
        """Check if the provider is currently available and configured."""
        ...
