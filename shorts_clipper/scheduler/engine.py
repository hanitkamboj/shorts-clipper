from __future__ import annotations

import logging
import sqlite3
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import StrEnum
from pathlib import Path
from typing import Any, Callable, Optional

log = logging.getLogger(__name__)

class ScheduleStatus(StrEnum):
    PENDING = 'pending'
    READY = 'ready'
    EXECUTING = 'executing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    SKIPPED = 'skipped'

@dataclass
class ScheduledItem:
    id: str
    clip_id: str
    scheduled_time: datetime  # UTC
    timezone: str  # e.g. 'Asia/Kolkata'
    status: ScheduleStatus = ScheduleStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    error: str = ''
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

class SchedulerEngine:
    """Durable scheduler that persists to SQLite and survives process restarts."""
    
    def __init__(self, db_path: Path | str = Path('workspace/database/scheduler.db'), **kwargs: Any):
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = self._connect()
        self._ensure_table()
        self._lock = threading.RLock()
        self._running = False
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
    
    def schedule_clip(self, clip_id: str, scheduled_time: datetime, timezone_str: str = 'UTC') -> ScheduledItem:
        """Schedule a single clip for execution."""
        self._validate_schedule_time(scheduled_time)
        
        item_id = str(uuid.uuid4())
        item = ScheduledItem(
            id=item_id,
            clip_id=clip_id,
            scheduled_time=scheduled_time,
            timezone=timezone_str
        )
        
        with self._lock:
            with self._conn:
                self._conn.execute(
                    '''
                    INSERT INTO schedule 
                    (id, clip_id, scheduled_time, timezone, status, retry_count, max_retries, error, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        item.id, item.clip_id, item.scheduled_time.timestamp(), item.timezone,
                        item.status.value, item.retry_count, item.max_retries, item.error,
                        item.created_at, item.updated_at
                    )
                )
        return item
    
    def schedule_batch(self, clip_ids: list[str], start_time: datetime, interval_minutes: int = 15, timezone_str: str = 'UTC') -> list[ScheduledItem]:
        """Schedule multiple clips at regular intervals.
        
        Example: 100 clips starting at 18:00, every 15 minutes.
        Generates: 18:00, 18:15, 18:30, 18:45, 19:00, ...
        """
        items = []
        current_time = start_time
        
        for clip_id in clip_ids:
            item = self.schedule_clip(clip_id, current_time, timezone_str)
            items.append(item)
            current_time += timedelta(minutes=interval_minutes)
            
        return items
    
    def get_due_items(self) -> list[ScheduledItem]:
        """Get items that are due for execution (scheduled_time <= now)."""
        now_ts = datetime.now(timezone.utc).timestamp()
        
        with self._lock:
            cursor = self._conn.execute(
                '''
                SELECT id, clip_id, scheduled_time, timezone, status, retry_count, max_retries, error, created_at, updated_at
                FROM schedule
                WHERE status IN (?, ?) AND scheduled_time <= ?
                ''',
                (ScheduleStatus.PENDING.value, ScheduleStatus.READY.value, now_ts)
            )
            return [self._row_to_item(row) for row in cursor.fetchall()]
    
    def mark_executing(self, item_id: str) -> None:
        """Mark an item as currently executing."""
        self._update_status(item_id, ScheduleStatus.EXECUTING)

    def mark_completed(self, item_id: str) -> None:
        """Mark an item as successfully completed."""
        self._update_status(item_id, ScheduleStatus.COMPLETED)

    def mark_failed(self, item_id: str, error: str) -> None:
        """Mark an item as failed, incrementing retry count."""
        now = time.time()
        with self._lock:
            with self._conn:
                cursor = self._conn.execute('SELECT retry_count, max_retries FROM schedule WHERE id = ?', (item_id,))
                row = cursor.fetchone()
                if row:
                    retry_count, max_retries = row
                    new_retry_count = retry_count + 1
                    status = ScheduleStatus.FAILED if new_retry_count >= max_retries else ScheduleStatus.PENDING
                    
                    self._conn.execute(
                        '''
                        UPDATE schedule 
                        SET status = ?, error = ?, retry_count = ?, updated_at = ?
                        WHERE id = ?
                        ''',
                        (status.value, error, new_retry_count, now, item_id)
                    )

    def cancel(self, item_id: str) -> None:
        """Cancel a scheduled item."""
        self._update_status(item_id, ScheduleStatus.CANCELLED)

    def reschedule(self, item_id: str, new_time: datetime) -> None:
        """Reschedule an item to a new time."""
        self._validate_schedule_time(new_time)
        now = time.time()
        with self._lock:
            with self._conn:
                self._conn.execute(
                    '''
                    UPDATE schedule 
                    SET scheduled_time = ?, status = ?, updated_at = ?
                    WHERE id = ?
                    ''',
                    (new_time.timestamp(), ScheduleStatus.PENDING.value, now, item_id)
                )
    
    def list_all(self, limit: int = 100) -> list[ScheduledItem]:
        """List all items, up to the given limit."""
        with self._lock:
            cursor = self._conn.execute('SELECT * FROM schedule ORDER BY scheduled_time ASC LIMIT ?', (limit,))
            return [self._row_to_item(row) for row in cursor.fetchall()]

    def list_pending(self) -> list[ScheduledItem]:
        """List all pending items."""
        return self.list_by_status(ScheduleStatus.PENDING)

    def list_by_status(self, status: ScheduleStatus) -> list[ScheduledItem]:
        """List items by a specific status."""
        with self._lock:
            cursor = self._conn.execute('SELECT * FROM schedule WHERE status = ? ORDER BY scheduled_time ASC', (status.value,))
            return [self._row_to_item(row) for row in cursor.fetchall()]
    
    def start_background_loop(self, execute_callback: Callable[[ScheduledItem], None], check_interval_seconds: float = 60.0) -> None:
        """Start a background thread that checks for due items periodically.
        Does NOT use sleep() loop - uses threading.Event.wait() for interruptibility.
        """
        if self._running:
            return
            
        self._running = True
        self._stop_event.clear()
        
        def _loop() -> None:
            log.info("Scheduler background loop started.")
            while not self._stop_event.is_set():
                try:
                    due_items = self.get_due_items()
                    for item in due_items:
                        if self._stop_event.is_set():
                            break
                        self.mark_executing(item.id)
                        try:
                            execute_callback(item)
                        except Exception as e:
                            log.error(f"Error executing scheduled item {item.id}: {e}", exc_info=True)
                            self.mark_failed(item.id, str(e))
                except Exception as e:
                    log.error(f"Error checking for due items: {e}", exc_info=True)
                
                # Wait for the interval, or until stop is requested
                self._stop_event.wait(timeout=check_interval_seconds)
            log.info("Scheduler background loop stopped.")

        self._thread = threading.Thread(target=_loop, daemon=True, name="SchedulerLoop")
        self._thread.start()
    
    def stop(self) -> None:
        """Stop the background loop."""
        self._running = False
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
    
    def _validate_schedule_time(self, scheduled_time: datetime) -> None:
        """Ensure scheduled time is in the future and valid."""
        if scheduled_time.tzinfo is None:
            log.warning("Scheduled time has no timezone info, assuming UTC.")
            scheduled_time = scheduled_time.replace(tzinfo=timezone.utc)
            
        if scheduled_time < datetime.now(timezone.utc):
            log.warning("Scheduled time is in the past, it will execute immediately upon checking.")
    
    def _connect(self) -> sqlite3.Connection:
        """Establish SQLite connection."""
        conn = sqlite3.connect(self._db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_table(self) -> None:
        """Create necessary tables if they don't exist."""
        with self._connect() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS schedule (
                    id TEXT PRIMARY KEY,
                    clip_id TEXT NOT NULL,
                    scheduled_time REAL NOT NULL,
                    timezone TEXT NOT NULL,
                    status TEXT NOT NULL,
                    retry_count INTEGER NOT NULL DEFAULT 0,
                    max_retries INTEGER NOT NULL DEFAULT 3,
                    error TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            ''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_status_time ON schedule (status, scheduled_time)')

    def _update_status(self, item_id: str, status: ScheduleStatus) -> None:
        """Helper to update item status."""
        now = time.time()
        with self._lock:
            with self._conn:
                self._conn.execute(
                    'UPDATE schedule SET status = ?, updated_at = ? WHERE id = ?',
                    (status.value, now, item_id)
                )

    def _row_to_item(self, row: sqlite3.Row) -> ScheduledItem:
        """Convert a SQLite row to a ScheduledItem."""
        return ScheduledItem(
            id=row['id'],
            clip_id=row['clip_id'],
            scheduled_time=datetime.fromtimestamp(row['scheduled_time'], tz=timezone.utc),
            timezone=row['timezone'],
            status=ScheduleStatus(row['status']),
            retry_count=row['retry_count'],
            max_retries=row['max_retries'],
            error=row['error'] or '',
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
        
    def close(self) -> None:
        """Stop processing and close DB connection."""
        self.stop()
        if self._conn:
            self._conn.close()
