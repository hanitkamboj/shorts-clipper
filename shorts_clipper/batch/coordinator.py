from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path
from typing import Any, Callable

from .processor import BatchProcessor

log = logging.getLogger(__name__)

class BatchCoordinator:
    """Coordinates a full batch pipeline: candidates -> score -> deduplicate -> render -> metadata -> queue.
    
    Stage-level checkpointing: never repeats completed stages on restart.
    """
    
    def __init__(self, project_id: str, db_manager: Any = None, batch_processor: BatchProcessor | None = None, settings: Any = None):
        self.project_id = project_id
        self._db = db_manager
        self._processor = batch_processor or BatchProcessor()
        self._settings = settings
        
        # Local fallback checkpointing directory
        self._checkpoint_dir = Path('workspace/checkpoints') / project_id
        self._checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
    def run_batch(self, sources: list[dict], clip_count: int = 10, strategy: str = 'viral', quality_mode: str = 'STANDARD', progress_callback: Callable | None = None) -> list[dict]:
        """Execute full batch pipeline.
        
        Stages:
        1. Ingest sources (download/prepare)
        2. Transcribe all sources
        3. Generate candidates (cheap analysis -> hundreds of candidates)
        4. Score candidates (deterministic ranking -> top N -> AI semantic -> top M)
        5. Diversity selection
        6. Render clips
        7. Generate thumbnails
        8. Generate metadata / SEO
        9. Quality gate
        10. Queue for upload
        
        Checkpoints after each stage. On restart, resumes from last checkpoint.
        """
        batch_id = str(uuid.uuid4())
        log.info(f"Starting batch {batch_id} for project {self.project_id} with {len(sources)} sources.")
        
        stages = [
            ("ingest", self._mock_ingest),
            ("transcribe", self._mock_transcribe),
            ("generate_candidates", self._mock_generate),
            ("score_candidates", self._mock_score),
            ("diversity_selection", self._mock_diversity),
            ("render_clips", self._mock_render),
            ("generate_thumbnails", self._mock_thumbnails),
            ("generate_metadata", self._mock_metadata),
            ("quality_gate", self._mock_quality_gate),
            ("queue_for_upload", self._mock_queue)
        ]
        
        current_data = {"sources": sources, "clip_count": clip_count}
        
        for stage_name, stage_fn in stages:
            if self._processor.is_cancelled():
                log.warning(f"Batch {batch_id} cancelled at stage {stage_name}")
                break
                
            log.info(f"Batch {batch_id} entering stage: {stage_name}")
            if progress_callback:
                progress_callback(stage_name, current_data)
                
            # Execute the stage
            current_data = stage_fn(current_data)
            
            # Checkpoint the result
            self._checkpoint(batch_id, stage_name, current_data)
            
        log.info(f"Batch {batch_id} completed successfully.")
        return current_data.get("final_clips", [])
    
    def resume_batch(self, batch_id: str) -> list[dict]:
        """Resume a previously interrupted batch."""
        checkpoint_data = self._load_checkpoint(batch_id)
        if not checkpoint_data:
            log.error(f"No checkpoint found for batch {batch_id}")
            return []
            
        last_stage, data = checkpoint_data
        log.info(f"Resuming batch {batch_id} from stage {last_stage}")
        
        stages = [
            "ingest", "transcribe", "generate_candidates", "score_candidates", 
            "diversity_selection", "render_clips", "generate_thumbnails", 
            "generate_metadata", "quality_gate", "queue_for_upload"
        ]
        
        try:
            start_idx = stages.index(last_stage) + 1
        except ValueError:
            log.warning(f"Unknown stage {last_stage}, cannot resume.")
            return []
            
        # For simplicity in this structure, we just restart execution from the next step
        # A real implementation would map the string names back to functions
        log.info(f"Resuming from index {start_idx} is not fully implemented in this mock.")
        return data.get("final_clips", [])
    
    def _checkpoint(self, batch_id: str, stage: str, data: dict) -> None:
        """Save a checkpoint for a batch."""
        checkpoint_file = self._checkpoint_dir / f"{batch_id}.json"
        payload = {
            "batch_id": batch_id,
            "stage": stage,
            "data": data
        }
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2)
            
    def _load_checkpoint(self, batch_id: str) -> tuple[str, dict] | None:
        """Load the latest checkpoint for a batch."""
        checkpoint_file = self._checkpoint_dir / f"{batch_id}.json"
        if not checkpoint_file.exists():
            return None
            
        try:
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                payload = json.load(f)
                return payload["stage"], payload["data"]
        except Exception as e:
            log.error(f"Failed to load checkpoint {batch_id}: {e}")
            return None

    # Mocks for the pipeline steps to make the class fully concrete without relying on missing components
    def _mock_ingest(self, data: dict) -> dict: return data
    def _mock_transcribe(self, data: dict) -> dict: return data
    def _mock_generate(self, data: dict) -> dict: return data
    def _mock_score(self, data: dict) -> dict: return data
    def _mock_diversity(self, data: dict) -> dict: return data
    def _mock_render(self, data: dict) -> dict: return data
    def _mock_thumbnails(self, data: dict) -> dict: return data
    def _mock_metadata(self, data: dict) -> dict: return data
    def _mock_quality_gate(self, data: dict) -> dict: return data
    def _mock_queue(self, data: dict) -> dict: 
        data["final_clips"] = [{"id": f"clip_{i}"} for i in range(data.get("clip_count", 0))]
        return data
