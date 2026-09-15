from __future__ import annotations

import sqlite3
import threading
import logging
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel
from .schema import MIGRATIONS
from .models import (
    Project, Source, SourceAnalysis, Transcript, Candidate, Clip, Score,
    ClipMetadataRecord, Thumbnail, AIRun, ResearchResult, Upload, Schedule, ErrorRecord
)

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database connections and provides CRUD operations for shorts-clipper models."""
    
    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self._lock = threading.RLock()
        
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Returns a configured SQLite connection."""
        conn = sqlite3.connect(
            str(self.db_path),
            check_same_thread=False,
            isolation_level=None
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _init_db(self) -> None:
        """Initialize database schema and run migrations."""
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        version INTEGER PRIMARY KEY,
                        description TEXT,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                current_version = self.get_schema_version(conn)
                self.run_migrations(conn, current_version)
            finally:
                conn.close()

    def get_schema_version(self, conn: sqlite3.Connection) -> int:
        """Get the current schema version from the database."""
        row = conn.execute("SELECT MAX(version) as max_v FROM schema_migrations").fetchone()
        return row['max_v'] if row and row['max_v'] is not None else 0

    def run_migrations(self, conn: sqlite3.Connection, current_version: int) -> None:
        """Run pending migrations."""
        for version, description, sql in MIGRATIONS:
            if version > current_version:
                logger.info(f"Applying migration v{version}: {description}")
                try:
                    conn.executescript(sql)
                    conn.execute(
                        "INSERT INTO schema_migrations (version, description) VALUES (?, ?)",
                        (version, description)
                    )
                except Exception as e:
                    logger.error(f"Migration v{version} failed: {e}")
                    raise RuntimeError(f"Database migration failed: {e}") from e

    def _insert_model(self, table_name: str, model: BaseModel) -> None:
        """Helper to insert a Pydantic model into a table."""
        data = model.model_dump()
        for k, v in data.items():
            if hasattr(v, 'isoformat'):
                data[k] = v.isoformat()

        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data.keys()])
        values = tuple(data.values())

        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        with self._lock:
            conn = self._get_connection()
            try:
                conn.execute(query, values)
            finally:
                conn.close()

    def create_project(self, project: Project) -> None:
        """Create a new project."""
        self._insert_model("project", project)

    def get_project(self, project_id: str) -> Optional[Project]:
        """Retrieve a project by ID."""
        with self._lock:
            conn = self._get_connection()
            try:
                row = conn.execute("SELECT * FROM project WHERE id = ?", (project_id,)).fetchone()
                return Project(**dict(row)) if row else None
            finally:
                conn.close()

    def list_projects(self) -> List[Project]:
        """List all projects."""
        with self._lock:
            conn = self._get_connection()
            try:
                rows = conn.execute("SELECT * FROM project").fetchall()
                return [Project(**dict(row)) for row in rows]
            finally:
                conn.close()

    def get_or_create_source(self, project_id: str, url: str, source_type: str) -> Source:
        """Get an existing source by URL or create a new one."""
        with self._lock:
            conn = self._get_connection()
            try:
                row = conn.execute("SELECT * FROM source WHERE url = ?", (url,)).fetchone()
                if row:
                    return Source(**dict(row))
                
                new_source = Source(project_id=project_id, url=url, source_type=source_type)
                self.create_source(new_source)
                return new_source
            finally:
                conn.close()

    def create_source(self, source: Source) -> None:
        """Create a new source."""
        self._insert_model("source", source)

    def get_source(self, source_id: str) -> Optional[Source]:
        """Get source by ID."""
        with self._lock:
            conn = self._get_connection()
            try:
                row = conn.execute("SELECT * FROM source WHERE id = ?", (source_id,)).fetchone()
                return Source(**dict(row)) if row else None
            finally:
                conn.close()

    def record_error(self, stage: str, error_type: str, error_message: str, 
                     item_id: Optional[str] = None, retry_state: Optional[str] = None, 
                     recovery_action: Optional[str] = None, raw_error: Optional[str] = None) -> ErrorRecord:
        """Record a structured error in the database."""
        err = ErrorRecord(
            stage=stage,
            item_id=item_id,
            error_type=error_type,
            error_message=error_message,
            retry_state=retry_state,
            recovery_action=recovery_action,
            raw_error=raw_error
        )
        self._insert_model("error_record", err)
        return err
        
    def close(self) -> None:
        """Close database manager resources."""
        pass
