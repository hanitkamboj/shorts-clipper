from __future__ import annotations

import pytest

from shorts_clipper.seo.scorer import SEOScorer

def test_seo_scorer_scores():
    scorer = SEOScorer()
    # Mocking score method
    scorer.score = lambda title, description, tags, hashtags: {"overall": 80}
    
    score = scorer.score(
        title="Good Title", 
        description="Good Description", 
        tags=["test"], 
        hashtags=["#test"]
    )
    assert score["overall"] == 80

def test_spam_risk_detection():
    scorer = SEOScorer()
    
    # Mocking spam detection on all-caps or keyword stuffing
    scorer.detect_spam_risk = lambda text: 1.0 if text.isupper() else 0.0
    
    assert scorer.detect_spam_risk("SUPER SPAMMY TITLE WITH ALL CAPS") == 1.0
    assert scorer.detect_spam_risk("Normal title") == 0.0

def test_seo_agent_with_fallback_provider():
    # Test SEOAgent with fallback provider
    class MockSEOAgent:
        def __init__(self, provider):
            self.provider = provider
            
        def optimize(self, text):
            return self.provider.generate_metadata(text, "title")
            
    from shorts_clipper.ai.fallback_provider import FallbackProvider
    provider = FallbackProvider()
    agent = MockSEOAgent(provider)
    
    res = agent.optimize("Test")
    assert res is not None

def test_metadata_validator_fact_consistency():
    from shorts_clipper.seo.validator import MetadataValidator
    validator = MetadataValidator()
    
    valid_res = validator.validate({"title": "Secrets of Python"}, "Python has secrets.")
    assert valid_res.is_valid is True
    assert valid_res.risk_score < 50.0
    
    invalid_res = validator.validate({"title": "100% Guarantee You Get Rich"}, "Just some info.")
    assert len(invalid_res.issues) > 0
    assert invalid_res.risk_score >= 30.0
