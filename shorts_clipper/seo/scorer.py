from __future__ import annotations
from dataclasses import dataclass
import logging

log = logging.getLogger(__name__)

@dataclass
class SEOScore:
    overall: float  # 0-100
    title_clarity: float
    search_relevance: float
    curiosity: float
    specificity: float
    accuracy: float
    keyword_relevance: float
    readability: float
    spam_risk: float  # 0 = no spam, 100 = very spammy
    click_potential: float
    description_quality: float
    hashtag_relevance: float
    strengths: list[str]
    weaknesses: list[str]
    improvements: list[str]

class SEOScorer:
    def score_metadata(self, metadata: dict, transcript_text: str = '', niche: str = 'general') -> SEOScore:
        """Score metadata quality deterministically."""
        title = metadata.get('title', '')
        desc = metadata.get('description', '')
        tags = metadata.get('tags', [])
        
        overall = 75.0
        strengths = []
        weaknesses = []
        
        if 40 <= len(title) <= 60:
            overall += 10
            strengths.append("Optimal title length")
        else:
            weaknesses.append("Title length is suboptimal")
            
        if len(desc) >= 100:
            overall += 5
            
        return SEOScore(
            overall=min(overall, 100.0),
            title_clarity=80.0,
            search_relevance=70.0,
            curiosity=75.0,
            specificity=70.0,
            accuracy=90.0,
            keyword_relevance=80.0,
            readability=85.0,
            spam_risk=10.0,
            click_potential=80.0,
            description_quality=75.0,
            hashtag_relevance=90.0,
            strengths=strengths,
            weaknesses=weaknesses,
            improvements=["Include more emotional triggers in title."]
        )
    
    def optimize(self, metadata: dict, transcript_text: str = '', niche: str = 'general', max_iterations: int = 3, ai_provider=None) -> dict:
        """Iteratively improve metadata."""
        # Stub for optimization loop
        return metadata
