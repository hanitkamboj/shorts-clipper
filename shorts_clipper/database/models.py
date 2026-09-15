from __future__ import annotations

from datetime import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, Field

def _generate_uuid() -> str:
    return str(uuid.uuid4())

def _utcnow() -> datetime:
    return datetime.utcnow()

class Project(BaseModel):
    id: str = Field(default_factory=_generate_uuid)
    name: str
    niche: Optional[str] = None
    language: str = "en"
    default_duration: Optional[int] = 60
    output_format: str = "1080x1920"
    caption_profile: Optional[str] = None
    upload_strategy: Optional[str] = None
    ai_provider: str = "openai"
    quality_threshold: float = 7.0
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)

class Source(BaseModel):
    id: str = Field(default_factory=_generate_uuid)
    project_id: str
    url: str
    source_type: str
    video_id: Optional[str] = None
    title: Optional[str] = None
    channel: Optional[str] = None
    duration: Optional[float] = None
    resolution: Optional[str] = None
    fps: Optional[float] = None
    language: Optional[str] = "en"
    status: str = "pending"
    created_at: datetime = Field(default_factory=_utcnow)

class SourceAnalysis(BaseModel):
    id: str = Field(default_factory=_generate_uuid)
    source_id: str
    speech_density: Optional[float] = None
    speaker_count: Optional[int] = None
    scene_count: Optional[int] = None
    silence_ratio: Optional[float] = None
    transcript_hash: Optional[str] = None
    analysis_json: Optional[str] = None
    created_at: datetime = Field(default_factory=_utcnow)

class Transcript(BaseModel):
    id: str = Field(default_factory=_generate_uuid)
    source_id: str
    model_used: str
    language: str
    confidence: Optional[float] = None
    word_count: Optional[int] = None
    duration: Optional[float] = None
    segments_json: str
    created_at: datetime = Field(default_factory=_utcnow)

class Candidate(BaseModel):
    id: str = Field(default_factory=_generate_uuid)
    source_id: str
    start_time: float
    end_time: float
    duration: float
    transcript_excerpt: str
    status: str = "pending"
    created_at: datetime = Field(default_factory=_utcnow)

class Clip(BaseModel):
    id: str = Field(default_factory=_generate_uuid)
    candidate_id: str
    project_id: str
    source_id: str
    start_time: float
    end_time: float
    duration: float
    file_path: Optional[str] = None
    file_hash: Optional[str] = None
    render_status: str = "pending"
    created_at: datetime = Field(default_factory=_utcnow)

class Score(BaseModel):
    id: str = Field(default_factory=_generate_uuid)
    clip_id: str
    hook_score: float
    context_score: float
    narrative_score: float
    info_score: float
    emotion_score: float
    audio_score: Optional[float] = None
    visual_score: Optional[float] = None
    caption_score: Optional[float] = None
    seo_score: Optional[float] = None
    thumbnail_score: Optional[float] = None
    final_score: float
    scoring_method: str
    details_json: str
    created_at: datetime = Field(default_factory=_utcnow)

class ClipMetadataRecord(BaseModel):
    id: str = Field(default_factory=_generate_uuid)
    clip_id: str
    title: str
    alt_titles_json: str
    description: str
    tags_json: str
    hashtags_json: str
    thumbnail_text: Optional[str] = None
    seo_score: Optional[float] = None
    confidence: Optional[float] = None
    prompt_version: Optional[str] = None
    provider: str
    created_at: datetime = Field(default_factory=_utcnow)

class Thumbnail(BaseModel):
    id: str = Field(default_factory=_generate_uuid)
    clip_id: str
    file_path: str
    score: Optional[float] = None
    selection_method: str
    created_at: datetime = Field(default_factory=_utcnow)

class AIRun(BaseModel):
    id: str = Field(default_factory=_generate_uuid)
    clip_id: str
    provider: str
    model: str
    prompt_version: str
    input_summary: str
    output_json: str
    validation_status: str
    latency_ms: Optional[int] = None
    retry_count: int = 0
    created_at: datetime = Field(default_factory=_utcnow)

class ResearchResult(BaseModel):
    id: str = Field(default_factory=_generate_uuid)
    query: str
    locale: str
    results_json: str
    ttl_seconds: int
    created_at: datetime = Field(default_factory=_utcnow)

class Upload(BaseModel):
    id: str = Field(default_factory=_generate_uuid)
    clip_id: str
    platform: str
    status: str
    youtube_video_id: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    error: Optional[str] = None
    retry_count: int = 0
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)

class Schedule(BaseModel):
    id: str = Field(default_factory=_generate_uuid)
    project_id: str
    clip_id: str
    upload_id: Optional[str] = None
    scheduled_time: datetime
    timezone: str = "UTC"
    status: str = "pending"
    created_at: datetime = Field(default_factory=_utcnow)

class ErrorRecord(BaseModel):
    id: str = Field(default_factory=_generate_uuid)
    stage: str
    item_id: Optional[str] = None
    error_type: str
    error_message: str
    retry_state: Optional[str] = None
    recovery_action: Optional[str] = None
    raw_error: Optional[str] = None
    created_at: datetime = Field(default_factory=_utcnow)
