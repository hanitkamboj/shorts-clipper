from __future__ import annotations

import logging
import sqlite3
import threading
import time
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger(__name__)

@dataclass
class QuotaState:
    uploads_today: int = 0
    api_calls_today: int = 0
    estimated_quota_remaining: int = 10000
    failed_requests_today: int = 0
    last_upload_time: float | None = None
    next_upload_time: float | None = None
    is_paused: bool = False
    pause_reason: str = ''
    reset_time: float = 0.0  # Next daily reset

class QuotaManager:
    """Track API quota usage and prevent exceeding limits."""
    
    def __init__(self, db_path: Path = Path('workspace/database/quota.db')):
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._lock = threading.RLock()
        self._ensure_table()
        self._ensure_reset()
    
    def _ensure_table(self) -> None:
        with self._lock:
            with self._conn:
                self._conn.execute('''
                    CREATE TABLE IF NOT EXISTS quota (
                        id INTEGER PRIMARY KEY CHECK (id = 1),
                        uploads_today INTEGER NOT NULL DEFAULT 0,
                        api_calls_today INTEGER NOT NULL DEFAULT 0,
                        estimated_quota_remaining INTEGER NOT NULL DEFAULT 10000,
                        failed_requests_today INTEGER NOT NULL DEFAULT 0,
                        last_upload_time REAL,
                        next_upload_time REAL,
                        is_paused INTEGER NOT NULL DEFAULT 0,
                        pause_reason TEXT NOT NULL DEFAULT '',
                        reset_time REAL NOT NULL DEFAULT 0
                    )
                ''')
                # Initialize the single row if it doesn't exist
                self._conn.execute('''
                    INSERT OR IGNORE INTO quota (id, reset_time)
                    VALUES (1, ?)
                ''', (self._next_reset_time(),))

    def _next_reset_time(self) -> float:
        """Calculate the next midnight UTC for daily quota reset."""
        now = time.time()
        # Simplistic midnight UTC calculation (24 hours = 86400 seconds)
        seconds_since_epoch = int(now)
        seconds_since_midnight = seconds_since_epoch % 86400
        return now + (86400 - seconds_since_midnight)

    def _ensure_reset(self) -> None:
        """Check if quota needs to be reset based on time."""
        state = self.get_state()
        if time.time() >= state.reset_time:
            self.reset_daily()

    def record_upload(self) -> None:
        """Record a successful upload."""
        self._ensure_reset()
        now = time.time()
        with self._lock:
            with self._conn:
                self._conn.execute('''
                    UPDATE quota SET 
                        uploads_today = uploads_today + 1,
                        estimated_quota_remaining = MAX(0, estimated_quota_remaining - 1600),
                        last_upload_time = ?
                    WHERE id = 1
                ''', (now,))

    def record_api_call(self, provider: str = 'youtube') -> None:
        """Record a standard API call."""
        self._ensure_reset()
        # Cost assumes typical API call cost
        cost = 1 if provider == 'youtube' else 0
        with self._lock:
            with self._conn:
                self._conn.execute('''
                    UPDATE quota SET 
                        api_calls_today = api_calls_today + 1,
                        estimated_quota_remaining = MAX(0, estimated_quota_remaining - ?)
                    WHERE id = 1
                ''', (cost,))

    def record_failure(self) -> None:
        """Record an API or upload failure."""
        self._ensure_reset()
        with self._lock:
            with self._conn:
                self._conn.execute('''
                    UPDATE quota SET failed_requests_today = failed_requests_today + 1 WHERE id = 1
                ''')

    def can_upload(self) -> tuple[bool, str]:
        """Check if an upload is allowed by quota and status."""
        self._ensure_reset()
        state = self.get_state()
        
        if state.is_paused:
            return False, f"Uploads are paused: {state.pause_reason}"
        
        # YouTube allows ~6 uploads per day on average tier
        if state.uploads_today >= 6:
            return False, "Daily upload limit reached."
            
        if state.estimated_quota_remaining < 1600:
            return False, "Insufficient API quota remaining for an upload."
            
        return True, ""

    def can_call_api(self, provider: str = 'youtube') -> tuple[bool, str]:
        """Check if standard API calls are allowed."""
        self._ensure_reset()
        state = self.get_state()
        
        if state.is_paused:
            return False, f"API calls are paused: {state.pause_reason}"
            
        if state.estimated_quota_remaining <= 0:
            return False, "Daily API quota exhausted."
            
        return True, ""

    def pause(self, reason: str) -> None:
        """Pause all quota-consuming operations."""
        with self._lock:
            with self._conn:
                self._conn.execute('UPDATE quota SET is_paused = 1, pause_reason = ? WHERE id = 1', (reason,))

    def resume(self) -> None:
        """Resume quota-consuming operations."""
        with self._lock:
            with self._conn:
                self._conn.execute('UPDATE quota SET is_paused = 0, pause_reason = "" WHERE id = 1')

    def get_state(self) -> QuotaState:
        """Get the current quota state."""
        with self._lock:
            cursor = self._conn.execute('SELECT * FROM quota WHERE id = 1')
            row = cursor.fetchone()
            return QuotaState(
                uploads_today=row['uploads_today'],
                api_calls_today=row['api_calls_today'],
                estimated_quota_remaining=row['estimated_quota_remaining'],
                failed_requests_today=row['failed_requests_today'],
                last_upload_time=row['last_upload_time'],
                next_upload_time=row['next_upload_time'],
                is_paused=bool(row['is_paused']),
                pause_reason=row['pause_reason'],
                reset_time=row['reset_time']
            )

    def reset_daily(self) -> None:
        """Reset the daily quotas immediately."""
        with self._lock:
            with self._conn:
                self._conn.execute('''
                    UPDATE quota SET 
                        uploads_today = 0,
                        api_calls_today = 0,
                        estimated_quota_remaining = 10000,
                        failed_requests_today = 0,
                        reset_time = ?
                    WHERE id = 1
                ''', (self._next_reset_time(),))
