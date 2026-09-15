from __future__ import annotations

import json
import re
import time
from typing import Any

from .provider import AIProvider, ProviderError, QuotaExhaustedError
from .schemas import MetadataResult, ClipScore, ResearchResult, TranscriptAnalysis


class GeminiProvider:
    """A provider that connects to Google's Gemini API."""
    
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model = model
        self._client = None

    @property
    def client(self) -> Any:
        if self._client is None:
            # Lazy import to avoid hard dependency on module load
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except ImportError:
                raise ProviderError("google-genai package is not installed")
        return self._client

    @property
    def name(self) -> str:
        return f"gemini-{self.model}"

    def _extract_json(self, text: str) -> str:
        """Extract JSON from markdown fenced code blocks if present."""
        match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if match:
            return match.group(1)
        return text

    def _generate(self, prompt: str) -> dict[str, Any]:
        from google.genai import errors
        
        max_retries = 3
        base_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )
                
                text = response.text
                json_str = self._extract_json(text)
                return json.loads(json_str)
                
            except errors.APIError as e:
                # 429 Too Many Requests
                if e.code == 429:
                    if "quota" in str(e).lower():
                        raise QuotaExhaustedError(f"Gemini API quota exhausted: {e}")
                    
                    if attempt < max_retries - 1:
                        time.sleep(base_delay * (2 ** attempt))
                        continue
                    raise ProviderError(f"Gemini API rate limit exceeded after {max_retries} attempts: {e}")
                raise ProviderError(f"Gemini API error: {e}")
            except json.JSONDecodeError as e:
                if attempt < max_retries - 1:
                    continue
                raise ProviderError(f"Failed to parse JSON from Gemini after {max_retries} attempts: {e}")
            except Exception as e:
                raise ProviderError(f"Unexpected error from Gemini: {e}")
                
        raise ProviderError("Failed to generate content from Gemini")

    def generate_metadata(
        self, 
        transcript_text: str, 
        source_title: str = '', 
        source_channel: str = '', 
        niche: str = 'general'
    ) -> MetadataResult:
        prompt = (
            f"Generate metadata for a short video clip based on this transcript:\n\n{transcript_text}\n\n"
            f"Source title: {source_title}\nSource channel: {source_channel}\nNiche: {niche}\n\n"
            "Respond in pure JSON matching this schema exactly: {\"title\": \"string\", \"alternative_titles\": [\"string\"], "
            "\"description\": \"string\", \"tags\": [\"string\"], \"hashtags\": [\"string\"], \"thumbnail_text\": \"string\", "
            "\"seo_score\": 0.0, \"confidence\": 0.0}"
        )
        result = self._generate(prompt)
        return MetadataResult(**result)
        
    def score_clip(self, transcript_text: str, clip_context: dict[str, Any] | None = None) -> ClipScore:
        prompt = (
            f"Score this video clip transcript based on its potential to go viral:\n\n{transcript_text}\n\n"
            "Respond in pure JSON matching this schema exactly: {\"hook_score\": 0.0, \"curiosity\": 0.0, \"emotion\": 0.0, "
            "\"narrative\": 0.0, \"info_density\": 0.0, \"context\": 0.0, \"retention\": 0.0, \"overall\": 0.0, \"reasoning\": \"string\"}"
        )
        result = self._generate(prompt)
        return ClipScore(**result)
        
    def research(self, query: str, locale: str = 'en') -> ResearchResult:
        prompt = (
            f"Research trends and related topics for the query: '{query}' in locale '{locale}'.\n\n"
            "Respond in pure JSON matching this schema exactly: {\"related_terms\": [\"string\"], \"trending_phrases\": [\"string\"], "
            "\"competitor_patterns\": [\"string\"], \"audience_language\": \"string\"}"
        )
        result = self._generate(prompt)
        return ResearchResult(**result)
        
    def analyze_transcript(self, transcript_text: str) -> TranscriptAnalysis:
        prompt = (
            f"Analyze this transcript and extract key structural elements:\n\n{transcript_text}\n\n"
            "Respond in pure JSON matching this schema exactly: {\"topics\": [\"string\"], \"emotional_peaks\": [\"string\"], "
            "\"hooks\": [\"string\"], \"claims\": [\"string\"], \"narrative_arcs\": [\"string\"], \"key_moments\": [\"string\"]}"
        )
        result = self._generate(prompt)
        return TranscriptAnalysis(**result)
        
    def is_available(self) -> bool:
        if not self.api_key:
            return False
        try:
            import google.genai
            return True
        except ImportError:
            return False
