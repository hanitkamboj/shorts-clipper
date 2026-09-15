from __future__ import annotations

import datetime
from typing import Any
from pydantic import BaseModel, Field


class MetadataResult(BaseModel):
    title: str = Field(description="The suggested title for the clip")
    alternative_titles: list[str] = Field(default_factory=list, description="Alternative titles")
    description: str = Field(description="The suggested description for the clip")
    tags: list[str] = Field(default_factory=list, description="Relevant tags for the clip")
    hashtags: list[str] = Field(default_factory=list, description="Relevant hashtags for the clip")
    thumbnail_text: str = Field(default="", description="Text to place on the thumbnail")
    seo_score: float = Field(default=0.0, description="Estimated SEO score from 0.0 to 100.0")
    confidence: float = Field(default=0.0, description="Confidence in the generation from 0.0 to 1.0")


class ClipScore(BaseModel):
    hook_score: float = Field(description="Score for the opening hook (0-10)")
    curiosity: float = Field(description="Score for curiosity generation (0-10)")
    emotion: float = Field(description="Score for emotional impact (0-10)")
    narrative: float = Field(description="Score for narrative cohesion (0-10)")
    info_density: float = Field(description="Score for information density (0-10)")
    context: float = Field(description="Score for context independence (0-10)")
    retention: float = Field(description="Expected retention score (0-10)")
    overall: float = Field(description="Overall aggregate score (0-10)")
    reasoning: str = Field(description="Reasoning behind the scores")


class ResearchResult(BaseModel):
    related_terms: list[str] = Field(default_factory=list, description="Related terms to the query")
    trending_phrases: list[str] = Field(default_factory=list, description="Currently trending phrases")
    competitor_patterns: list[str] = Field(default_factory=list, description="Common patterns used by competitors")
    audience_language: str = Field(default="", description="Description of the target audience language style")
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now, description="When the research was conducted")
    method: str = Field(default="ai", description="Method used to perform research")


class TranscriptAnalysis(BaseModel):
    topics: list[str] = Field(default_factory=list, description="Main topics discussed")
    emotional_peaks: list[str] = Field(default_factory=list, description="Timestamps or segments of high emotional impact")
    hooks: list[str] = Field(default_factory=list, description="Potential hooks identified in the text")
    claims: list[str] = Field(default_factory=list, description="Factual claims made in the text")
    narrative_arcs: list[str] = Field(default_factory=list, description="Identified narrative arcs")
    key_moments: list[str] = Field(default_factory=list, description="Key moments or highlights")
