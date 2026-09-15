from __future__ import annotations

import json
import urllib.request
import urllib.error
from typing import Any

from .provider import AIProvider, ProviderError
from .schemas import MetadataResult, ClipScore, ResearchResult, TranscriptAnalysis


class OllamaProvider:
    """A provider that connects to a local Ollama instance."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    @property
    def name(self) -> str:
        return f"ollama-{self.model}"

    def _generate(self, prompt: str) -> dict[str, Any]:
        url = f"{self.base_url}/api/generate"
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                response_text = result.get("response", "")
                return json.loads(response_text)
        except urllib.error.URLError as e:
            raise ProviderError(f"Failed to connect to Ollama: {e}")
        except json.JSONDecodeError as e:
            raise ProviderError(f"Failed to parse JSON from Ollama: {e}")
            
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
            "Respond in pure JSON matching this schema: {\"title\": \"string\", \"alternative_titles\": [\"string\"], "
            "\"description\": \"string\", \"tags\": [\"string\"], \"hashtags\": [\"string\"], \"thumbnail_text\": \"string\", "
            "\"seo_score\": 0.0, \"confidence\": 0.0}"
        )
        result = self._generate(prompt)
        return MetadataResult(**result)
        
    def score_clip(self, transcript_text: str, clip_context: dict[str, Any] | None = None) -> ClipScore:
        prompt = (
            f"Score this video clip transcript based on its potential to go viral:\n\n{transcript_text}\n\n"
            "Respond in pure JSON matching this schema: {\"hook_score\": 0.0, \"curiosity\": 0.0, \"emotion\": 0.0, "
            "\"narrative\": 0.0, \"info_density\": 0.0, \"context\": 0.0, \"retention\": 0.0, \"overall\": 0.0, \"reasoning\": \"string\"}"
        )
        result = self._generate(prompt)
        return ClipScore(**result)
        
    def research(self, query: str, locale: str = 'en') -> ResearchResult:
        prompt = (
            f"Research trends and related topics for the query: '{query}' in locale '{locale}'.\n\n"
            "Respond in pure JSON matching this schema: {\"related_terms\": [\"string\"], \"trending_phrases\": [\"string\"], "
            "\"competitor_patterns\": [\"string\"], \"audience_language\": \"string\"}"
        )
        result = self._generate(prompt)
        return ResearchResult(**result)
        
    def analyze_transcript(self, transcript_text: str) -> TranscriptAnalysis:
        prompt = (
            f"Analyze this transcript and extract key structural elements:\n\n{transcript_text}\n\n"
            "Respond in pure JSON matching this schema: {\"topics\": [\"string\"], \"emotional_peaks\": [\"string\"], "
            "\"hooks\": [\"string\"], \"claims\": [\"string\"], \"narrative_arcs\": [\"string\"], \"key_moments\": [\"string\"]}"
        )
        result = self._generate(prompt)
        return TranscriptAnalysis(**result)
        
    def is_available(self) -> bool:
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=2) as response:
                return response.status == 200
        except Exception:
            return False
