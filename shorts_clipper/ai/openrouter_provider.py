from __future__ import annotations

import json
import urllib.request
import urllib.error
from typing import Any

from .provider import AIProvider, ProviderError, QuotaExhaustedError
from .schemas import MetadataResult, ClipScore, ResearchResult, TranscriptAnalysis


class OpenRouterProvider:
    """A provider that connects to OpenRouter via its OpenAI-compatible API."""
    
    def __init__(
        self, 
        api_key: str, 
        model: str = "openai/gpt-3.5-turbo", 
        base_url: str = "https://openrouter.ai/api/v1"
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")

    @property
    def name(self) -> str:
        return f"openrouter-{self.model}"

    def _generate(self, prompt: str) -> dict[str, Any]:
        url = f"{self.base_url}/chat/completions"
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/shorts-clipper",
            "X-Title": "Shorts Clipper",
            "Content-Type": "application/json"
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers=headers
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                content = result["choices"][0]["message"]["content"]
                return json.loads(content)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                raise QuotaExhaustedError(f"OpenRouter rate limit or quota exhausted: {e.read().decode()}")
            raise ProviderError(f"HTTP error from OpenRouter ({e.code}): {e.read().decode()}")
        except urllib.error.URLError as e:
            raise ProviderError(f"Failed to connect to OpenRouter: {e}")
        except (KeyError, json.JSONDecodeError) as e:
            raise ProviderError(f"Failed to parse response from OpenRouter: {e}")
            
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
        return bool(self.api_key)
