from __future__ import annotations

import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

log = logging.getLogger(__name__)

@dataclass
class BatchConfig:
    gpu_workers: int = 1
    cpu_workers: int = 2
    metadata_concurrency: int = 3
    upload_concurrency: int = 1
    quality_threshold: float = 75.0
    diversity_threshold: float = 0.3
    max_candidates: int = 500
    max_final_clips: int = 100

@dataclass
class BatchProgress:
    total_items: int = 0
    completed: int = 0
    failed: int = 0
    in_progress: int = 0
    current_stage: str = ''
    current_item: str = ''
    stages_completed: list[str] = field(default_factory=list)
    errors: list[dict] = field(default_factory=list)

class BatchProcessor:
    """Resource-aware batch processor that never overwhelms the system."""
    
    def __init__(self, config: BatchConfig | None = None):
        self._config = config or BatchConfig()
        self._progress = BatchProgress()
        self._cancelled = threading.Event()
        self._lock = threading.RLock()
    
    def process_batch(self, items: list[dict], process_fn: Callable, stage: str = 'processing', max_workers: int | None = None) -> list[dict]:
        """Process a batch of items with bounded concurrency.
        
        Uses ThreadPoolExecutor with configurable worker count.
        Records progress, handles failures per-item (never stops entire batch).
        Supports cancellation.
        """
        if not items:
            return []

        if self._cancelled.is_set():
            return []

        if max_workers is None:
            max_workers = self._config.cpu_workers
        
        with self._lock:
            self._progress.total_items = len(items)
            self._progress.completed = 0
            self._progress.failed = 0
            self._progress.in_progress = 0
            self._progress.current_stage = stage
            self._progress.errors.clear()

        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_item = {}
            for item in items:
                future = executor.submit(self._process_single, item, process_fn)
                future_to_item[future] = item
                with self._lock:
                    self._progress.in_progress += 1

            for future in as_completed(future_to_item):
                item = future_to_item[future]
                
                with self._lock:
                    self._progress.in_progress -= 1
                    self._progress.current_item = str(item.get('id', 'unknown'))

                if self._cancelled.is_set():
                    log.info("Batch processing cancelled, ignoring remaining results.")
                    continue

                try:
                    result = future.result()
                    results.append(result)
                    with self._lock:
                        self._progress.completed += 1
                except Exception as exc:
                    item_id = item.get('id', 'unknown')
                    error_info = {"item_id": item_id, "stage": stage, "error": str(exc)}
                    log.error(f"Item {item_id} failed in stage {stage}: {exc}", exc_info=True)
                    with self._lock:
                        self._progress.failed += 1
                        self._progress.errors.append(error_info)

        with self._lock:
            if stage not in self._progress.stages_completed and not self._cancelled.is_set():
                self._progress.stages_completed.append(stage)
            self._progress.current_item = ''

        return results
        
    def _process_single(self, item: dict, process_fn: Callable) -> Any:
        """Wrapper to allow early exit on cancellation."""
        if self._cancelled.is_set():
            raise RuntimeError("Processing cancelled")
        return process_fn(item)

    def get_progress(self) -> BatchProgress:
        """Returns a snapshot of the current batch progress."""
        with self._lock:
            # Return a copy to avoid concurrent modification issues
            return BatchProgress(
                total_items=self._progress.total_items,
                completed=self._progress.completed,
                failed=self._progress.failed,
                in_progress=self._progress.in_progress,
                current_stage=self._progress.current_stage,
                current_item=self._progress.current_item,
                stages_completed=list(self._progress.stages_completed),
                errors=list(self._progress.errors)
            )

    def cancel(self) -> None:
        """Signal the batch processor to stop starting new items."""
        log.warning("Cancelling batch processing.")
        self._cancelled.set()

    def is_cancelled(self) -> bool:
        """Check if the batch processor is currently cancelled."""
        return self._cancelled.is_set()
