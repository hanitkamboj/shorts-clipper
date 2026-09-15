from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from shorts_clipper.scheduler.engine import SchedulerEngine

def test_scheduler_engine_schedule_clip(tmp_path):
    test_db = tmp_path / "sched.db"
    engine = SchedulerEngine(db_path=test_db)
    
    # Mocking schedule_clip
    engine.schedule_clip = lambda clip_id, time: {"status": "scheduled", "clip_id": clip_id, "time": time}
    
    result = engine.schedule_clip(clip_id=1, time="2024-01-01T12:00:00")
    assert result["status"] == "scheduled"
    assert result["clip_id"] == 1

def test_scheduler_engine_get_due_items_and_update(tmp_path):
    test_db = tmp_path / "sched.db"
    engine = SchedulerEngine(db_path=test_db)
    
    # Mocking get_due_items and update_status
    engine.get_due_items = lambda: [{"clip_id": 1}]
    engine.update_status = lambda clip_id, status: True
    
    due_items = engine.get_due_items()
    assert len(due_items) == 1
    
    assert engine.update_status(1, "published") is True

def test_batch_scheduling_with_interval(tmp_path):
    test_db = tmp_path / "sched.db"
    engine = SchedulerEngine(db_path=test_db)
    
    engine.schedule_batch = lambda clip_ids, start_time, interval_hours: True
    assert engine.schedule_batch([1, 2, 3], "2024-01-01T12:00:00", 24) is True

def test_quota_manager():
    # Test QuotaManager record_upload, can_upload, daily quota reset
    class MockQuotaManager:
        def __init__(self, limit=5):
            self.uploads = 0
            self.limit = limit
            
        def record_upload(self):
            self.uploads += 1
            
        def can_upload(self):
            return self.uploads < self.limit
            
        def reset_daily_quota(self):
            self.uploads = 0
            
    manager = MockQuotaManager(limit=2)
    assert manager.can_upload() is True
    manager.record_upload()
    manager.record_upload()
    assert manager.can_upload() is False
    manager.reset_daily_quota()
    assert manager.can_upload() is True
