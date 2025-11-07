"""
Checkpointing utilities for resumable pipeline operations.

This module provides:
- Save/restore pipeline state
- Resume from last checkpoint
- Automatic checkpoint creation
- Progress recovery on failure
"""

import json
import pickle
from typing import Any, Dict, Optional, List
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Checkpoint:
    """
    Checkpoint manager for resumable operations.

    Example:
        >>> checkpoint = Checkpoint('interview_pipeline', checkpoint_dir='checkpoints/')
        >>> if checkpoint.exists():
        ...     state = checkpoint.load()
        ...     start_index = state['last_completed_index'] + 1
        ... else:
        ...     start_index = 0
        >>>
        >>> for i in range(start_index, total):
        ...     process_item(i)
        ...     checkpoint.save({'last_completed_index': i, 'total_cost': cost})
    """

    def __init__(self, operation_name: str, checkpoint_dir: str = 'checkpoints/',
                 format: str = 'json'):
        """
        Initialize checkpoint manager.

        Args:
            operation_name: Name of the operation (used for checkpoint filename)
            checkpoint_dir: Directory to store checkpoints
            format: Format to use ('json' or 'pickle')
        """
        self.operation_name = operation_name
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.format = format

        # Checkpoint file path
        ext = 'json' if format == 'json' else 'pkl'
        self.checkpoint_file = self.checkpoint_dir / f"{operation_name}.{ext}"

    def save(self, state: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None):
        """
        Save checkpoint state.

        Args:
            state: State dictionary to save
            metadata: Optional metadata (timestamp added automatically)
        """
        checkpoint_data = {
            'operation': self.operation_name,
            'timestamp': datetime.now().isoformat(),
            'state': state,
            'metadata': metadata or {}
        }

        try:
            if self.format == 'json':
                with open(self.checkpoint_file, 'w') as f:
                    json.dump(checkpoint_data, f, indent=2)
            else:
                with open(self.checkpoint_file, 'wb') as f:
                    pickle.dump(checkpoint_data, f)

            logger.info(f"Saved checkpoint for {self.operation_name}")
        except (IOError, pickle.PickleError, json.JSONEncodeError) as e:
            logger.error(f"Failed to save checkpoint: {e}")

    def load(self) -> Optional[Dict[str, Any]]:
        """
        Load checkpoint state.

        Returns:
            State dictionary or None if checkpoint doesn't exist
        """
        if not self.exists():
            return None

        try:
            if self.format == 'json':
                with open(self.checkpoint_file, 'r') as f:
                    checkpoint_data = json.load(f)
            else:
                with open(self.checkpoint_file, 'rb') as f:
                    checkpoint_data = pickle.load(f)

            logger.info(f"Loaded checkpoint for {self.operation_name} from {checkpoint_data['timestamp']}")
            return checkpoint_data['state']
        except (IOError, pickle.PickleError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return None

    def exists(self) -> bool:
        """Check if checkpoint exists."""
        return self.checkpoint_file.exists()

    def delete(self):
        """Delete checkpoint file."""
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()
            logger.info(f"Deleted checkpoint for {self.operation_name}")

    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """
        Get checkpoint metadata without loading full state.

        Returns:
            Metadata dictionary or None
        """
        if not self.exists():
            return None

        try:
            if self.format == 'json':
                with open(self.checkpoint_file, 'r') as f:
                    checkpoint_data = json.load(f)
            else:
                with open(self.checkpoint_file, 'rb') as f:
                    checkpoint_data = pickle.load(f)

            return {
                'operation': checkpoint_data['operation'],
                'timestamp': checkpoint_data['timestamp'],
                'metadata': checkpoint_data.get('metadata', {})
            }
        except (IOError, pickle.PickleError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load checkpoint metadata: {e}")
            return None


class AutoCheckpoint:
    """
    Automatic checkpointing with configurable intervals.

    Example:
        >>> auto_checkpoint = AutoCheckpoint('my_operation', save_interval=10)
        >>> for i in range(100):
        ...     result = process_item(i)
        ...     auto_checkpoint.update({'last_index': i, 'results': results})
        ...     # Automatically saves every 10 updates
    """

    def __init__(self, operation_name: str, checkpoint_dir: str = 'checkpoints/',
                 save_interval: int = 10, format: str = 'json'):
        """
        Initialize auto-checkpoint manager.

        Args:
            operation_name: Operation name
            checkpoint_dir: Checkpoint directory
            save_interval: Number of updates between saves
            format: Format to use ('json' or 'pickle')
        """
        self.checkpoint = Checkpoint(operation_name, checkpoint_dir, format)
        self.save_interval = save_interval
        self.update_count = 0
        self.current_state: Dict[str, Any] = {}

    def update(self, state: Dict[str, Any], force_save: bool = False):
        """
        Update state and save if interval reached.

        Args:
            state: State dictionary (merged with current state)
            force_save: Force save even if interval not reached
        """
        self.current_state.update(state)
        self.update_count += 1

        if force_save or self.update_count >= self.save_interval:
            self.checkpoint.save(self.current_state)
            self.update_count = 0

    def load(self) -> Optional[Dict[str, Any]]:
        """Load last checkpoint state."""
        state = self.checkpoint.load()
        if state:
            self.current_state = state
        return state

    def finalize(self):
        """Save final state and clean up."""
        if self.current_state:
            self.checkpoint.save(self.current_state)
        self.checkpoint.delete()


class BatchCheckpoint:
    """
    Checkpoint manager for batch processing operations.

    Saves after each batch and allows resuming from last completed batch.

    Example:
        >>> checkpoint = BatchCheckpoint('interview_batches')
        >>> completed_batches = checkpoint.get_completed_batches()
        >>>
        >>> for batch_id, batch in enumerate(all_batches):
        ...     if batch_id in completed_batches:
        ...         continue  # Skip completed batches
        ...
        ...     results = process_batch(batch)
        ...     checkpoint.mark_batch_complete(batch_id, results)
    """

    def __init__(self, operation_name: str, checkpoint_dir: str = 'checkpoints/'):
        """
        Initialize batch checkpoint manager.

        Args:
            operation_name: Operation name
            checkpoint_dir: Checkpoint directory
        """
        self.checkpoint = Checkpoint(f"{operation_name}_batches", checkpoint_dir)
        self.completed_batches: Dict[int, Any] = {}

        # Load existing checkpoint
        state = self.checkpoint.load()
        if state:
            self.completed_batches = state.get('completed_batches', {})

    def mark_batch_complete(self, batch_id: int, result: Optional[Any] = None):
        """
        Mark a batch as completed.

        Args:
            batch_id: Batch identifier
            result: Optional result data to store
        """
        self.completed_batches[batch_id] = {
            'completed_at': datetime.now().isoformat(),
            'result': result
        }

        # Save checkpoint
        self.checkpoint.save({
            'completed_batches': self.completed_batches,
            'last_batch_id': batch_id
        })

        logger.debug(f"Marked batch {batch_id} as complete")

    def get_completed_batches(self) -> List[int]:
        """
        Get list of completed batch IDs.

        Returns:
            List of completed batch IDs
        """
        return list(self.completed_batches.keys())

    def is_batch_complete(self, batch_id: int) -> bool:
        """
        Check if a batch is complete.

        Args:
            batch_id: Batch identifier

        Returns:
            True if batch is complete
        """
        return batch_id in self.completed_batches

    def get_batch_result(self, batch_id: int) -> Optional[Any]:
        """
        Get result for a completed batch.

        Args:
            batch_id: Batch identifier

        Returns:
            Batch result or None
        """
        batch_data = self.completed_batches.get(batch_id)
        if batch_data:
            return batch_data.get('result')
        return None

    def get_progress(self, total_batches: int) -> Dict[str, Any]:
        """
        Get progress information.

        Args:
            total_batches: Total number of batches

        Returns:
            Progress dictionary with completed count and percentage
        """
        completed = len(self.completed_batches)
        return {
            'completed': completed,
            'total': total_batches,
            'percentage': (completed / total_batches * 100) if total_batches > 0 else 0,
            'remaining': total_batches - completed
        }

    def clear(self):
        """Clear all completed batches."""
        self.completed_batches.clear()
        self.checkpoint.delete()


def checkpoint_manager(operation_name: str, checkpoint_dir: str = 'checkpoints/'):
    """
    Context manager for automatic checkpointing.

    Args:
        operation_name: Operation name
        checkpoint_dir: Checkpoint directory

    Example:
        >>> with checkpoint_manager('my_operation') as cp:
        ...     state = cp.load() or {'index': 0}
        ...     for i in range(state['index'], 100):
        ...         process_item(i)
        ...         cp.save({'index': i})
    """
    checkpoint = Checkpoint(operation_name, checkpoint_dir)

    class CheckpointContext:
        def __enter__(self):
            return checkpoint

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is not None:
                # Save checkpoint on error for recovery
                logger.info(f"Saving checkpoint due to error: {exc_type.__name__}")

    return CheckpointContext()


# Export public API
__all__ = [
    'Checkpoint',
    'AutoCheckpoint',
    'BatchCheckpoint',
    'checkpoint_manager',
]
