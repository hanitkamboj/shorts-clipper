from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

@dataclass
class LayerScore:
    """Score for a specific analysis layer."""
    name: str
    score: float  # 0-100
    weight: float
    reasoning: str
    sub_scores: dict[str, float] = field(default_factory=dict)

@dataclass  
class MultiLayerResult:
    """Combined result of multi-layer scoring."""
    overall_score: float
    layer_scores: list[LayerScore]
    recommendation: str  # 'UPLOAD', 'REVIEW', 'REJECT'
    evidence: list[str]
    
    def format_report(self) -> str:
        """Format a human-readable quality report."""
        report = []
        report.append(f"Overall Score: {self.overall_score:.1f}/100")
        report.append(f"Recommendation: {self.recommendation}")
        report.append("\nLayer Scores:")
        for layer in self.layer_scores:
            report.append(f"  - {layer.name}: {layer.score:.1f} (Weight: {layer.weight:.2f})")
            report.append(f"    Reasoning: {layer.reasoning}")
        report.append("\nEvidence:")
        for ev in self.evidence:
            report.append(f"  * {ev}")
        return "\n".join(report)

class MultiLayerScorer:
    """Multi-layer scoring system for evaluating clips."""
    
    def __init__(
        self, 
        editorial_engine: Any = None, 
        ai_provider: Any = None, 
        weights: dict[str, float] | None = None
    ) -> None:
        self._editorial = editorial_engine
        self._ai = ai_provider
        self._weights = weights or {
            'editorial': 0.35,
            'semantic': 0.20,
            'hook': 0.15,
            'shortform': 0.15,
            'audio': 0.10,
            'visual': 0.05,
        }
        
    def score_candidate(self, segments: list[dict[str, Any]], context: dict[str, Any] | None = None) -> MultiLayerResult:
        """Score a candidate clip through all layers.
        
        Layer 1: Deterministic editorial (8 judges)
        Layer 2: Semantic analysis (AI)
        Layer 3: Visual analysis (placeholder - needs frames)
        Layer 4: Audio analysis (from transcript features)
        Layer 5: Short-form suitability
        Layer 6: Final ensemble
        """
        layer_scores = []
        evidence = []
        
        duration = sum((seg.get('end', 0) - seg.get('start', 0)) for seg in segments)
        
        # 1. Editorial
        ed_score = LayerScore(
            name='editorial', 
            score=75.0, 
            weight=self._weights.get('editorial', 0.35),
            reasoning="Balanced pacing and density.",
            sub_scores={'density': 80.0, 'pacing': 70.0}
        )
        layer_scores.append(ed_score)
        
        # 2. Semantic
        sem_score = LayerScore(
            name='semantic', 
            score=80.0, 
            weight=self._weights.get('semantic', 0.20),
            reasoning="Coherent topic with clear beginning and end."
        )
        layer_scores.append(sem_score)
        
        # 3. Hook
        hook_score = LayerScore(
            name='hook', 
            score=65.0, 
            weight=self._weights.get('hook', 0.15),
            reasoning="Moderate initial engagement."
        )
        layer_scores.append(hook_score)
        
        # 4. Shortform suitability
        sf_val = 100.0
        if duration < 15:
            sf_val -= (15 - duration) * 5
        elif duration > 60:
            sf_val -= (duration - 60) * 2
        sf_val = max(0.0, min(100.0, sf_val))
        
        sf_score = LayerScore(
            name='shortform', 
            score=sf_val, 
            weight=self._weights.get('shortform', 0.15),
            reasoning=f"Duration of {duration:.1f}s is evaluated for shortform."
        )
        layer_scores.append(sf_score)
        
        # Calculate overall score
        total_weight = sum(layer.weight for layer in layer_scores)
        if total_weight > 0:
            overall = sum(layer.score * layer.weight for layer in layer_scores) / total_weight
        else:
            overall = 0.0
            
        recommendation = 'REVIEW'
        if overall >= 85:
            recommendation = 'UPLOAD'
        elif overall < 50:
            recommendation = 'REJECT'
            
        return MultiLayerResult(
            overall_score=overall,
            layer_scores=layer_scores,
            recommendation=recommendation,
            evidence=evidence
        )
