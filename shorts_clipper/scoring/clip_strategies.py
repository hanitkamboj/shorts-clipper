from __future__ import annotations

from enum import StrEnum

class ClipStrategy(StrEnum):
    """Presets for clip scoring strategies."""
    VIRAL = 'viral'
    EDUCATIONAL = 'educational'
    STORY = 'story'
    PODCAST = 'podcast'
    NEWS = 'news'
    MOTIVATIONAL = 'motivational'
    FUNNY = 'funny'
    CONTROVERSIAL = 'controversial'
    CUSTOM = 'custom'

def get_strategy_weights(strategy: ClipStrategy) -> dict[str, float]:
    """Return editorial weight configuration for a strategy."""
    base_weights = {
        'editorial': 0.35,
        'semantic': 0.20,
        'hook': 0.15,
        'shortform': 0.15,
        'audio': 0.10,
        'visual': 0.05,
    }
    
    if strategy == ClipStrategy.VIRAL:
        return {
            'editorial': 0.20,
            'semantic': 0.10,
            'hook': 0.40,
            'shortform': 0.20,
            'audio': 0.05,
            'visual': 0.05,
        }
    elif strategy == ClipStrategy.EDUCATIONAL:
        return {
            'editorial': 0.30,
            'semantic': 0.40,
            'hook': 0.10,
            'shortform': 0.10,
            'audio': 0.05,
            'visual': 0.05,
        }
    elif strategy == ClipStrategy.STORY:
        return {
            'editorial': 0.40,
            'semantic': 0.30,
            'hook': 0.10,
            'shortform': 0.10,
            'audio': 0.05,
            'visual': 0.05,
        }
    elif strategy == ClipStrategy.PODCAST:
        return {
            'editorial': 0.30,
            'semantic': 0.30,
            'hook': 0.20,
            'shortform': 0.10,
            'audio': 0.10,
            'visual': 0.0,
        }
        
    return base_weights
