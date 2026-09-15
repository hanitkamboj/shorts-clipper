from __future__ import annotations

import logging
import os
from typing import Any

from .provider import AIProvider, ProviderError
from .schemas import MetadataResult, ClipScore, ResearchResult, TranscriptAnalysis
from .fallback_provider import FallbackProvider
from .gemini_provider import GeminiProvider
from .openrouter_provider import OpenRouterProvider
from .ollama_provider import OllamaProvider


logger = logging.getLogger(__name__)


class AIProviderRouter:
    """Routes requests through a chain of AI providers with automatic failover."""
    
    def __init__(self, providers: list[AIProvider] | None = None):
        if not providers:
            providers = [FallbackProvider()]
        self.providers = providers
        self._availability_cache: dict[str, bool] = {}
        
    def _is_provider_available(self, provider: AIProvider) -> bool:
        """Check if provider is available, caching the result."""
        if provider.name not in self._availability_cache:
            try:
                self._availability_cache[provider.name] = provider.is_available()
            except Exception as e:
                logger.warning(f"Error checking availability of {provider.name}: {e}")
                self._availability_cache[provider.name] = False
        return self._availability_cache[provider.name]

    def generate_metadata(
        self, 
        transcript_text: str, 
        source_title: str = '', 
        source_channel: str = '', 
        niche: str = 'general'
    ) -> MetadataResult:
        errors = []
        for provider in self.providers:
            if not self._is_provider_available(provider):
                continue
                
            try:
                logger.debug(f"Attempting generate_metadata with {provider.name}")
                result = provider.generate_metadata(transcript_text, source_title, source_channel, niche)
                logger.info(f"Successfully generated metadata using {provider.name}")
                return result
            except Exception as e:
                logger.warning(f"Provider {provider.name} failed on generate_metadata: {e}")
                errors.append(f"{provider.name}: {str(e)}")
                
        raise ProviderError(f"All providers failed. Errors: {'; '.join(errors)}")

    def score_clip(self, transcript_text: str, clip_context: dict[str, Any] | None = None) -> ClipScore:
        errors = []
        for provider in self.providers:
            if not self._is_provider_available(provider):
                continue
                
            try:
                logger.debug(f"Attempting score_clip with {provider.name}")
                result = provider.score_clip(transcript_text, clip_context)
                logger.info(f"Successfully scored clip using {provider.name}")
                return result
            except Exception as e:
                logger.warning(f"Provider {provider.name} failed on score_clip: {e}")
                errors.append(f"{provider.name}: {str(e)}")
                
        raise ProviderError(f"All providers failed. Errors: {'; '.join(errors)}")

    def research(self, query: str, locale: str = 'en') -> ResearchResult:
        errors = []
        for provider in self.providers:
            if not self._is_provider_available(provider):
                continue
                
            try:
                logger.debug(f"Attempting research with {provider.name}")
                result = provider.research(query, locale)
                logger.info(f"Successfully researched using {provider.name}")
                return result
            except Exception as e:
                logger.warning(f"Provider {provider.name} failed on research: {e}")
                errors.append(f"{provider.name}: {str(e)}")
                
        raise ProviderError(f"All providers failed. Errors: {'; '.join(errors)}")

    def analyze_transcript(self, transcript_text: str) -> TranscriptAnalysis:
        errors = []
        for provider in self.providers:
            if not self._is_provider_available(provider):
                continue
                
            try:
                logger.debug(f"Attempting analyze_transcript with {provider.name}")
                result = provider.analyze_transcript(transcript_text)
                logger.info(f"Successfully analyzed transcript using {provider.name}")
                return result
            except Exception as e:
                logger.warning(f"Provider {provider.name} failed on analyze_transcript: {e}")
                errors.append(f"{provider.name}: {str(e)}")
                
        raise ProviderError(f"All providers failed. Errors: {'; '.join(errors)}")


def create_default_router(settings: Any) -> AIProviderRouter:
    """
    Factory function to create an AI provider router from application settings.
    Expects settings to have gemini_api_key, openrouter_api_key, etc.
    """
    if os.environ.get("MOCK_AI", "").lower() in ("true", "1", "yes"):
        logger.info("MOCK_AI is enabled. Using fallback provider only.")
        return AIProviderRouter([FallbackProvider()])
        
    providers: list[AIProvider] = []
    
    # Add Gemini if configured
    gemini_key = getattr(settings, "gemini_api_key", os.environ.get("GEMINI_API_KEY"))
    if gemini_key:
        model = getattr(settings, "gemini_model", "gemini-2.5-flash")
        providers.append(GeminiProvider(api_key=gemini_key, model=model))
        
    # Add OpenRouter if configured
    openrouter_key = getattr(settings, "openrouter_api_key", os.environ.get("OPENROUTER_API_KEY"))
    if openrouter_key:
        model = getattr(settings, "openrouter_model", "openai/gpt-3.5-turbo")
        providers.append(OpenRouterProvider(api_key=openrouter_key, model=model))
        
    # Add Ollama if configured
    use_ollama = getattr(settings, "use_ollama", os.environ.get("USE_OLLAMA", "").lower() == "true")
    if use_ollama:
        ollama_url = getattr(settings, "ollama_base_url", "http://localhost:11434")
        ollama_model = getattr(settings, "ollama_model", "llama3")
        providers.append(OllamaProvider(base_url=ollama_url, model=ollama_model))
        
    # Always append fallback as last resort
    providers.append(FallbackProvider())
    
    return AIProviderRouter(providers)
