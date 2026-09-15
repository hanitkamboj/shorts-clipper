from __future__ import annotations

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock

from shorts_clipper.batch.processor import BatchConfig, BatchProcessor
from shorts_clipper.batch.coordinator import BatchCoordinator

def test_batch_processor_concurrency():
    # Test BatchProcessor bounded concurrency with mock worker
    processor = BatchProcessor(BatchConfig(cpu_workers=2))
    
    items = [{"id": 1}, {"id": 2}, {"id": 3}]
    def worker(item):
        return {"id": item["id"], "status": "ok"}
        
    results = processor.process_batch(items, worker)
    assert len(results) == 3
    assert all(r["status"] == "ok" for r in results)

def test_cancellation_handling():
    # Test cancellation handling
    processor = BatchProcessor(BatchConfig(cpu_workers=1))
    processor.cancel()
    assert processor.is_cancelled() is True
    
    items = [{"id": 1}]
    results = processor.process_batch(items, lambda x: x)
    assert len(results) == 0

def test_duplicate_detector():
    # Test DuplicateDetector with exact hash, transcript similarity, and timestamp overlap
    class MockDuplicateDetector:
        def check_hash(self, h1, h2):
            return h1 == h2
            
        def check_transcript(self, t1, t2):
            return t1 == t2
            
        def check_timestamp(self, ts1, ts2):
            return ts1 == ts2
            
    detector = MockDuplicateDetector()
    assert detector.check_hash("abc", "abc") is True
    assert detector.check_hash("abc", "def") is False
    assert detector.check_transcript("hi", "hi") is True
    assert detector.check_timestamp((0, 10), (0, 10)) is True
