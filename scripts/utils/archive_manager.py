#!/usr/bin/env python3
"""
Archive Manager for Gravidas Workflow Runs
==========================================

Manages archiving of workflow runs with timestamped directories and run summaries.

Structure:
    archive/
    ├── run_YYYYMMDD_HHMMSS/
    │   ├── data/
    │   │   ├── personas/
    │   │   ├── health_records/
    │   │   ├── matched/
    │   │   ├── interviews/
    │   │   ├── analysis/
    │   │   └── validation/
    │   ├── outputs/
    │   ├── logs/
    │   └── config/
    ├── RUN_SUMMARY.md          # Latest run summary
    └── run_history.json        # All runs history
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List


class ArchiveManager:
    """Manages workflow run archiving."""

    def __init__(self, base_dir: str = "archive"):
        """
        Initialize the archive manager.

        Args:
            base_dir: Base directory for archives (default: "archive")
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.base_dir / "run_history.json"
        self.summary_file = self.base_dir / "RUN_SUMMARY.md"

        # Current run info
        self.run_id: Optional[str] = None
        self.run_dir: Optional[Path] = None
        self.run_config: Dict[str, Any] = {}
        self.run_results: Dict[str, Any] = {}

    def create_run(self, config: Dict[str, Any]) -> Path:
        """
        Create a new timestamped run directory.

        Args:
            config: Configuration dictionary for this run

        Returns:
            Path to the run directory
        """
        # Generate timestamp-based run ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_id = f"run_{timestamp}"
        self.run_dir = self.base_dir / self.run_id
        self.run_config = config.copy()
        self.run_config['run_id'] = self.run_id
        self.run_config['start_time'] = datetime.now().isoformat()

        # Create directory structure
        subdirs = [
            "data/personas",
            "data/health_records",
            "data/matched",
            "data/interviews",
            "data/analysis",
            "data/validation",
            "outputs",
            "logs",
            "config"
        ]

        for subdir in subdirs:
            (self.run_dir / subdir).mkdir(parents=True, exist_ok=True)

        # Save initial config
        config_file = self.run_dir / "config" / "run_config.json"
        with open(config_file, 'w') as f:
            json.dump(self.run_config, f, indent=2, default=str)

        return self.run_dir

    def get_data_paths(self) -> Dict[str, Path]:
        """
        Get paths for data directories within the current run.

        Returns:
            Dictionary mapping data type to path
        """
        if not self.run_dir:
            raise RuntimeError("No active run. Call create_run() first.")

        return {
            'personas': self.run_dir / "data" / "personas",
            'health_records': self.run_dir / "data" / "health_records",
            'matched': self.run_dir / "data" / "matched",
            'interviews': self.run_dir / "data" / "interviews",
            'analysis': self.run_dir / "data" / "analysis",
            'validation': self.run_dir / "data" / "validation",
            'outputs': self.run_dir / "outputs",
            'logs': self.run_dir / "logs",
            'config': self.run_dir / "config"
        }

    def record_stage_result(self, stage_name: str, result: Dict[str, Any]):
        """
        Record the result of a workflow stage.

        Args:
            stage_name: Name of the stage
            result: Result dictionary with success, time, output, etc.
        """
        if 'stages' not in self.run_results:
            self.run_results['stages'] = {}

        self.run_results['stages'][stage_name] = {
            **result,
            'timestamp': datetime.now().isoformat()
        }

    def finalize_run(self, success: bool, total_time: float,
                     additional_results: Optional[Dict[str, Any]] = None) -> Path:
        """
        Finalize the run and generate summary.

        Args:
            success: Whether the overall run was successful
            total_time: Total execution time in seconds
            additional_results: Any additional results to include

        Returns:
            Path to the run summary file
        """
        if not self.run_dir:
            raise RuntimeError("No active run. Call create_run() first.")

        # Compile final results
        self.run_results['success'] = success
        self.run_results['total_time_seconds'] = total_time
        self.run_results['end_time'] = datetime.now().isoformat()

        if additional_results:
            self.run_results.update(additional_results)

        # Calculate summary statistics
        stages = self.run_results.get('stages', {})
        successful_stages = sum(1 for s in stages.values() if s.get('success', False))
        total_stages = len(stages)

        self.run_results['summary'] = {
            'total_stages': total_stages,
            'successful_stages': successful_stages,
            'failed_stages': total_stages - successful_stages,
            'success_rate': (successful_stages / total_stages * 100) if total_stages > 0 else 0
        }

        # Save detailed results to run directory
        results_file = self.run_dir / "outputs" / "run_results.json"
        with open(results_file, 'w') as f:
            json.dump({
                'config': self.run_config,
                'results': self.run_results
            }, f, indent=2, default=str)

        # Generate and save run summary
        summary_content = self._generate_summary()

        # Save summary in run directory
        run_summary_file = self.run_dir / "RUN_SUMMARY.md"
        with open(run_summary_file, 'w') as f:
            f.write(summary_content)

        # Update root summary (latest run)
        with open(self.summary_file, 'w') as f:
            f.write(summary_content)

        # Update history
        self._update_history()

        return run_summary_file

    def _generate_summary(self) -> str:
        """Generate markdown summary of the run."""
        config = self.run_config
        results = self.run_results
        stages = results.get('stages', {})
        summary = results.get('summary', {})

        # Format duration
        total_time = results.get('total_time_seconds', 0)
        duration_str = f"{total_time:.1f} seconds"
        if total_time >= 60:
            duration_str = f"{total_time/60:.1f} minutes ({total_time:.1f}s)"

        # Build summary markdown
        md = f"""# Gravidas Workflow Run Summary

## Run Information

| Property | Value |
|----------|-------|
| **Run ID** | `{config.get('run_id', 'N/A')}` |
| **Status** | {'SUCCESS' if results.get('success') else 'FAILED'} |
| **Start Time** | {config.get('start_time', 'N/A')} |
| **End Time** | {results.get('end_time', 'N/A')} |
| **Duration** | {duration_str} |

## Configuration

### Workflow Parameters

| Parameter | Value |
|-----------|-------|
| **Provider** | {config.get('provider', 'N/A')} |
| **Model** | {config.get('model', 'default')} |
| **Personas** | {config.get('personas', 'N/A')} |
| **Health Records** | {config.get('records', 'N/A')} |
| **Interviews** | {config.get('interviews', 'N/A')} |
| **Protocol** | {config.get('protocol', 'N/A')} |

## Results Summary

| Metric | Value |
|--------|-------|
| **Total Stages** | {summary.get('total_stages', 0)} |
| **Successful** | {summary.get('successful_stages', 0)} |
| **Failed** | {summary.get('failed_stages', 0)} |
| **Success Rate** | {summary.get('success_rate', 0):.1f}% |

## Stage Results

| Stage | Status | Duration |
|-------|--------|----------|
"""
        # Add stage results
        for stage_name, stage_info in stages.items():
            status = "SUCCESS" if stage_info.get('success') else "FAILED"
            time_taken = stage_info.get('time', 0)
            md += f"| {stage_name} | {status} | {time_taken:.2f}s |\n"

        # Add output locations
        if self.run_dir:
            md += f"""
## Output Locations

All outputs are stored in: `{self.run_dir}`

| Data Type | Location |
|-----------|----------|
| Personas | `{self.run_dir}/data/personas/` |
| Health Records | `{self.run_dir}/data/health_records/` |
| Matched Pairs | `{self.run_dir}/data/matched/` |
| Interviews | `{self.run_dir}/data/interviews/` |
| Analysis | `{self.run_dir}/data/analysis/` |
| Validation | `{self.run_dir}/data/validation/` |
| Outputs | `{self.run_dir}/outputs/` |
| Logs | `{self.run_dir}/logs/` |

### Key Files

- **Run Configuration**: `{self.run_dir}/config/run_config.json`
- **Run Results**: `{self.run_dir}/outputs/run_results.json`
- **This Summary**: `{self.run_dir}/RUN_SUMMARY.md`
"""

        # Add timestamp
        md += f"""
---
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        return md

    def _update_history(self):
        """Update the run history file."""
        # Load existing history
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
            except (json.JSONDecodeError, IOError):
                history = []

        # Add current run
        run_entry = {
            'run_id': self.run_id,
            'directory': str(self.run_dir),
            'start_time': self.run_config.get('start_time'),
            'end_time': self.run_results.get('end_time'),
            'success': self.run_results.get('success', False),
            'total_time_seconds': self.run_results.get('total_time_seconds', 0),
            'config_summary': {
                'provider': self.run_config.get('provider'),
                'model': self.run_config.get('model'),
                'personas': self.run_config.get('personas'),
                'records': self.run_config.get('records'),
                'interviews': self.run_config.get('interviews')
            },
            'stages_summary': self.run_results.get('summary', {})
        }

        history.append(run_entry)

        # Save updated history
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2, default=str)

    def copy_to_archive(self, source_path: str, dest_subdir: str) -> Path:
        """
        Copy a file or directory to the archive.

        Args:
            source_path: Source file or directory path
            dest_subdir: Destination subdirectory within run dir

        Returns:
            Path to the copied file/directory
        """
        if not self.run_dir:
            raise RuntimeError("No active run. Call create_run() first.")

        source = Path(source_path)
        dest_dir = self.run_dir / dest_subdir
        dest_dir.mkdir(parents=True, exist_ok=True)

        if source.is_file():
            dest = dest_dir / source.name
            shutil.copy2(source, dest)
        elif source.is_dir():
            dest = dest_dir / source.name
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(source, dest)
        else:
            raise FileNotFoundError(f"Source not found: {source_path}")

        return dest

    def list_runs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List recent runs from history.

        Args:
            limit: Maximum number of runs to return

        Returns:
            List of run entries (most recent first)
        """
        if not self.history_file.exists():
            return []

        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
            return list(reversed(history))[:limit]
        except (json.JSONDecodeError, IOError):
            return []

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """
        Get details of a specific run.

        Args:
            run_id: The run ID to look up

        Returns:
            Run entry dictionary or None if not found
        """
        runs = self.list_runs(limit=1000)  # Get all runs
        for run in runs:
            if run.get('run_id') == run_id:
                return run
        return None

    def cleanup_old_runs(self, keep_count: int = 10):
        """
        Remove old run directories, keeping only the most recent.

        Args:
            keep_count: Number of recent runs to keep
        """
        if not self.history_file.exists():
            return

        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError):
            return

        if len(history) <= keep_count:
            return

        # Get runs to remove (oldest first)
        runs_to_remove = history[:-keep_count]

        for run in runs_to_remove:
            run_dir = Path(run.get('directory', ''))
            if run_dir.exists():
                try:
                    shutil.rmtree(run_dir)
                    print(f"Removed old run: {run_dir}")
                except Exception as e:
                    print(f"Failed to remove {run_dir}: {e}")

        # Update history
        history = history[-keep_count:]
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2, default=str)


def get_archive_manager(base_dir: str = "archive") -> ArchiveManager:
    """Get or create an archive manager instance."""
    return ArchiveManager(base_dir)


# Command-line interface for archive management
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Manage workflow run archives')
    parser.add_argument('--list', '-l', type=int, nargs='?', const=10,
                       help='List recent runs (default: 10)')
    parser.add_argument('--info', '-i', type=str,
                       help='Show details of a specific run ID')
    parser.add_argument('--cleanup', '-c', type=int, nargs='?', const=10,
                       help='Cleanup old runs, keeping N most recent (default: 10)')
    parser.add_argument('--base-dir', '-d', type=str, default='archive',
                       help='Base archive directory (default: archive)')

    args = parser.parse_args()

    manager = ArchiveManager(args.base_dir)

    if args.list:
        runs = manager.list_runs(limit=args.list)
        if not runs:
            print("No runs found.")
        else:
            print(f"\nRecent {len(runs)} runs:\n")
            print(f"{'Run ID':<25} {'Status':<10} {'Duration':<15} {'Personas':<10}")
            print("-" * 65)
            for run in runs:
                status = "SUCCESS" if run.get('success') else "FAILED"
                duration = f"{run.get('total_time_seconds', 0):.1f}s"
                personas = run.get('config_summary', {}).get('personas', 'N/A')
                print(f"{run.get('run_id', 'N/A'):<25} {status:<10} {duration:<15} {personas:<10}")

    elif args.info:
        run = manager.get_run(args.info)
        if run:
            print(f"\nRun Details: {args.info}\n")
            print(json.dumps(run, indent=2, default=str))
        else:
            print(f"Run not found: {args.info}")

    elif args.cleanup:
        print(f"Cleaning up old runs, keeping {args.cleanup} most recent...")
        manager.cleanup_old_runs(keep_count=args.cleanup)
        print("Done.")

    else:
        parser.print_help()
