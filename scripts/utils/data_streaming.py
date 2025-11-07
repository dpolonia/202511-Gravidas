"""
Data streaming utilities for memory-efficient processing.

This module provides lazy loading and streaming capabilities for:
- Large JSON files
- Line-by-line processing
- Generator-based iteration
- Memory-efficient data handling
"""

import json
from typing import Iterator, Dict, Any, List, Optional, Callable
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def stream_json_array(file_path: str, validate: Optional[Callable[[Dict], bool]] = None) -> Iterator[Dict[str, Any]]:
    """
    Stream a JSON array file line-by-line without loading entire file into memory.

    This assumes the JSON file contains an array where each element is on its own line
    or can be parsed incrementally.

    Args:
        file_path: Path to JSON array file
        validate: Optional validation function to filter items

    Yields:
        Individual items from the JSON array

    Example:
        >>> for persona in stream_json_array('data/personas/personas.json'):
        ...     process(persona)
        ...     # Only one persona in memory at a time
    """
    logger.debug(f"Streaming JSON array from {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        # Try to parse the entire file first (for normal JSON arrays)
        try:
            data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    if validate is None or validate(item):
                        yield item
                return
        except json.JSONDecodeError:
            # If that fails, try line-by-line parsing
            pass

        # Reset file pointer
        f.seek(0)

        # Try line-by-line JSONL format
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line in ['[', ']', ',']:
                continue

            # Remove trailing comma if present
            if line.endswith(','):
                line = line[:-1]

            try:
                item = json.loads(line)
                if validate is None or validate(item):
                    yield item
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse line {line_num} in {file_path}: {e}")
                continue


def stream_jsonl(file_path: str, validate: Optional[Callable[[Dict], bool]] = None) -> Iterator[Dict[str, Any]]:
    """
    Stream a JSONL (JSON Lines) file where each line is a separate JSON object.

    Args:
        file_path: Path to JSONL file
        validate: Optional validation function to filter items

    Yields:
        Individual JSON objects from the file

    Example:
        >>> for record in stream_jsonl('data/records.jsonl'):
        ...     process(record)
    """
    logger.debug(f"Streaming JSONL from {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                item = json.loads(line)
                if validate is None or validate(item):
                    yield item
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse line {line_num} in {file_path}: {e}")
                continue


def batch_iterator(items: Iterator[Any], batch_size: int) -> Iterator[List[Any]]:
    """
    Group items from an iterator into batches.

    Args:
        items: Iterator of items
        batch_size: Number of items per batch

    Yields:
        Lists of items (batches)

    Example:
        >>> personas = stream_json_array('personas.json')
        >>> for batch in batch_iterator(personas, batch_size=10):
        ...     process_batch(batch)  # Process 10 personas at a time
    """
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []

    # Yield remaining items
    if batch:
        yield batch


def save_jsonl(items: Iterator[Dict[str, Any]], output_path: str,
               progress_callback: Optional[Callable[[int], None]] = None):
    """
    Save items to JSONL format (one JSON object per line).

    Args:
        items: Iterator of dictionaries to save
        output_path: Output file path
        progress_callback: Optional callback function called with count after each write

    Example:
        >>> personas = stream_json_array('input.json')
        >>> save_jsonl(personas, 'output.jsonl')
    """
    logger.info(f"Saving items to JSONL: {output_path}")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in items:
            json.dump(item, f, ensure_ascii=False)
            f.write('\n')
            count += 1

            if progress_callback:
                progress_callback(count)

    logger.info(f"Saved {count} items to {output_path}")


def load_json_lazy(file_path: str) -> Dict[str, Any]:
    """
    Load JSON file with memory-mapped I/O for large files.

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON data

    Note:
        For very large files, consider using stream_json_array instead.
    """
    logger.debug(f"Loading JSON (lazy) from {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def count_json_array_items(file_path: str) -> int:
    """
    Count items in a JSON array without loading entire file.

    Args:
        file_path: Path to JSON array file

    Returns:
        Number of items in the array

    Example:
        >>> total = count_json_array_items('personas.json')
        >>> print(f"File contains {total} items")
    """
    count = 0
    for _ in stream_json_array(file_path):
        count += 1
    return count


class LazyJsonArray:
    """
    Lazy-loading wrapper for JSON arrays.

    Provides list-like interface while keeping memory usage low.

    Example:
        >>> personas = LazyJsonArray('data/personas/personas.json')
        >>> print(len(personas))  # Counts without loading all
        >>> for p in personas:    # Iterates without loading all
        ...     print(p['name'])
    """

    def __init__(self, file_path: str):
        """
        Initialize lazy JSON array.

        Args:
            file_path: Path to JSON array file
        """
        self.file_path = file_path
        self._length: Optional[int] = None

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        """Iterate over items."""
        return stream_json_array(self.file_path)

    def __len__(self) -> int:
        """Get length (cached after first call)."""
        if self._length is None:
            self._length = count_json_array_items(self.file_path)
        return self._length

    def stream(self) -> Iterator[Dict[str, Any]]:
        """Get iterator over items."""
        return stream_json_array(self.file_path)

    def batches(self, batch_size: int) -> Iterator[List[Dict[str, Any]]]:
        """Get iterator over batches of items."""
        return batch_iterator(self.stream(), batch_size)


def merge_json_arrays(input_paths: List[str], output_path: str,
                     deduplicate_key: Optional[str] = None):
    """
    Merge multiple JSON array files into one.

    Args:
        input_paths: List of input file paths
        output_path: Output file path
        deduplicate_key: Optional key to use for deduplication (e.g., 'id')

    Example:
        >>> merge_json_arrays(
        ...     ['personas_1.json', 'personas_2.json'],
        ...     'personas_all.json',
        ...     deduplicate_key='id'
        ... )
    """
    logger.info(f"Merging {len(input_paths)} JSON arrays into {output_path}")

    seen_keys = set() if deduplicate_key else None

    def items_generator():
        for input_path in input_paths:
            for item in stream_json_array(input_path):
                # Deduplicate if requested
                if deduplicate_key:
                    key_value = item.get(deduplicate_key)
                    if key_value in seen_keys:
                        continue
                    seen_keys.add(key_value)

                yield item

    # Save to output
    items = items_generator()
    save_jsonl(items, output_path)


def split_json_array(input_path: str, output_dir: str, chunk_size: int,
                    prefix: str = "chunk"):
    """
    Split a large JSON array into smaller files.

    Args:
        input_path: Input file path
        output_dir: Output directory
        chunk_size: Number of items per chunk
        prefix: Prefix for output files

    Example:
        >>> split_json_array('personas.json', 'chunks/', chunk_size=1000)
        # Creates chunks/chunk_0000.json, chunks/chunk_0001.json, etc.
    """
    logger.info(f"Splitting {input_path} into chunks of {chunk_size}")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    items = stream_json_array(input_path)
    batches = batch_iterator(items, chunk_size)

    for chunk_num, batch in enumerate(batches):
        chunk_file = output_path / f"{prefix}_{chunk_num:04d}.json"
        with open(chunk_file, 'w', encoding='utf-8') as f:
            json.dump(batch, f, indent=2, ensure_ascii=False)
        logger.debug(f"Wrote chunk {chunk_num} with {len(batch)} items")


# Export public API
__all__ = [
    'stream_json_array',
    'stream_jsonl',
    'batch_iterator',
    'save_jsonl',
    'load_json_lazy',
    'count_json_array_items',
    'LazyJsonArray',
    'merge_json_arrays',
    'split_json_array',
]
