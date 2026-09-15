from __future__ import annotations

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS project (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    niche TEXT,
    language TEXT,
    default_duration INTEGER,
    output_format TEXT,
    caption_profile TEXT,
    upload_strategy TEXT,
    ai_provider TEXT,
    quality_threshold REAL,
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS source (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    url TEXT NOT NULL,
    source_type TEXT NOT NULL,
    video_id TEXT,
    title TEXT,
    channel TEXT,
    duration REAL,
    resolution TEXT,
    fps REAL,
    language TEXT,
    status TEXT,
    created_at TEXT,
    FOREIGN KEY(project_id) REFERENCES project(id)
);

CREATE TABLE IF NOT EXISTS source_analysis (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    speech_density REAL,
    speaker_count INTEGER,
    scene_count INTEGER,
    silence_ratio REAL,
    transcript_hash TEXT,
    analysis_json TEXT,
    created_at TEXT,
    FOREIGN KEY(source_id) REFERENCES source(id)
);

CREATE TABLE IF NOT EXISTS transcript (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    model_used TEXT,
    language TEXT,
    confidence REAL,
    word_count INTEGER,
    duration REAL,
    segments_json TEXT,
    created_at TEXT,
    FOREIGN KEY(source_id) REFERENCES source(id)
);

CREATE TABLE IF NOT EXISTS candidate (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    start_time REAL,
    end_time REAL,
    duration REAL,
    transcript_excerpt TEXT,
    status TEXT,
    created_at TEXT,
    FOREIGN KEY(source_id) REFERENCES source(id)
);

CREATE TABLE IF NOT EXISTS clip (
    id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL,
    project_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    start_time REAL,
    end_time REAL,
    duration REAL,
    file_path TEXT,
    file_hash TEXT,
    render_status TEXT,
    created_at TEXT,
    FOREIGN KEY(candidate_id) REFERENCES candidate(id),
    FOREIGN KEY(project_id) REFERENCES project(id),
    FOREIGN KEY(source_id) REFERENCES source(id)
);

CREATE TABLE IF NOT EXISTS score (
    id TEXT PRIMARY KEY,
    clip_id TEXT NOT NULL,
    hook_score REAL,
    context_score REAL,
    narrative_score REAL,
    info_score REAL,
    emotion_score REAL,
    audio_score REAL,
    visual_score REAL,
    caption_score REAL,
    seo_score REAL,
    thumbnail_score REAL,
    final_score REAL,
    scoring_method TEXT,
    details_json TEXT,
    created_at TEXT,
    FOREIGN KEY(clip_id) REFERENCES clip(id)
);

CREATE TABLE IF NOT EXISTS clip_metadata_record (
    id TEXT PRIMARY KEY,
    clip_id TEXT NOT NULL,
    title TEXT,
    alt_titles_json TEXT,
    description TEXT,
    tags_json TEXT,
    hashtags_json TEXT,
    thumbnail_text TEXT,
    seo_score REAL,
    confidence REAL,
    prompt_version TEXT,
    provider TEXT,
    created_at TEXT,
    FOREIGN KEY(clip_id) REFERENCES clip(id)
);

CREATE TABLE IF NOT EXISTS thumbnail (
    id TEXT PRIMARY KEY,
    clip_id TEXT NOT NULL,
    file_path TEXT,
    score REAL,
    selection_method TEXT,
    created_at TEXT,
    FOREIGN KEY(clip_id) REFERENCES clip(id)
);

CREATE TABLE IF NOT EXISTS ai_run (
    id TEXT PRIMARY KEY,
    clip_id TEXT NOT NULL,
    provider TEXT,
    model TEXT,
    prompt_version TEXT,
    input_summary TEXT,
    output_json TEXT,
    validation_status TEXT,
    latency_ms INTEGER,
    retry_count INTEGER,
    created_at TEXT,
    FOREIGN KEY(clip_id) REFERENCES clip(id)
);

CREATE TABLE IF NOT EXISTS research_result (
    id TEXT PRIMARY KEY,
    query TEXT,
    locale TEXT,
    results_json TEXT,
    ttl_seconds INTEGER,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS upload (
    id TEXT PRIMARY KEY,
    clip_id TEXT NOT NULL,
    platform TEXT,
    status TEXT,
    youtube_video_id TEXT,
    scheduled_at TEXT,
    published_at TEXT,
    error TEXT,
    retry_count INTEGER,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY(clip_id) REFERENCES clip(id)
);

CREATE TABLE IF NOT EXISTS schedule (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    clip_id TEXT NOT NULL,
    upload_id TEXT,
    scheduled_time TEXT,
    timezone TEXT,
    status TEXT,
    created_at TEXT,
    FOREIGN KEY(project_id) REFERENCES project(id),
    FOREIGN KEY(clip_id) REFERENCES clip(id),
    FOREIGN KEY(upload_id) REFERENCES upload(id)
);

CREATE TABLE IF NOT EXISTS error_record (
    id TEXT PRIMARY KEY,
    stage TEXT,
    item_id TEXT,
    error_type TEXT,
    error_message TEXT,
    retry_state TEXT,
    recovery_action TEXT,
    raw_error TEXT,
    created_at TEXT
);
"""

MIGRATIONS = [
    (1, "Initial schema", CREATE_TABLES_SQL),
]
