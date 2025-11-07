#!/usr/bin/env python3
"""
Progressive Synthea health record generation with milestone tracking.

This script generates health records in batches with progress reporting every 100 records.
Designed to avoid the stalling issues seen with large single runs.
"""

import os
import subprocess
import time
import logging
from pathlib import Path
import sys

# Setup logging
Path('logs').mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/02b_progressive_health_records.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def count_existing_records():
    """Count existing FHIR records."""
    fhir_dir = Path("synthea/output/fhir")
    if fhir_dir.exists():
        return len(list(fhir_dir.glob("*.json")))
    return 0

def run_synthea_batch(batch_size: int, start_seed: int = None):
    """Run Synthea for a specific batch size."""
    try:
        cmd = [
            "./run_synthea",
            "-p", str(batch_size),  # Population size for this batch
            "-g", "F",              # Female only
            "-a", "12-60",          # Age range
            "Massachusetts"         # State
        ]
        
        if start_seed:
            cmd.extend(["-s", str(start_seed)])  # Use seed for reproducibility
        
        logger.info(f"🚀 Starting Synthea batch: {batch_size} records")
        logger.info(f"Command: {' '.join(cmd)}")
        
        # Change to synthea directory
        os.chdir("synthea")
        
        # Run Synthea
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Monitor process
        stdout, stderr = process.communicate()
        
        # Return to original directory
        os.chdir("..")
        
        if process.returncode == 0:
            logger.info(f"✅ Batch completed successfully")
            return True
        else:
            logger.error(f"❌ Batch failed with return code {process.returncode}")
            logger.error(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        os.chdir("..")  # Ensure we return to original directory
        logger.error(f"Exception during Synthea batch: {e}")
        return False

def main():
    """Generate health records progressively to 1000 total."""
    target_total = 1000
    batch_size = 100
    
    logger.info("=== PROGRESSIVE SYNTHEA HEALTH RECORD GENERATION ===")
    
    # Count existing records
    existing_count = count_existing_records()
    logger.info(f"📊 Existing records: {existing_count}")
    
    if existing_count >= target_total:
        logger.info(f"🎯 Target already reached! {existing_count} >= {target_total}")
        return
    
    # Calculate how many more we need
    remaining = target_total - existing_count
    logger.info(f"🎯 Target: {target_total} records")
    logger.info(f"📝 Need: {remaining} more records")
    
    # Generate in batches of 100
    batches_needed = (remaining + batch_size - 1) // batch_size
    logger.info(f"📦 Batches to run: {batches_needed} (×{batch_size} records each)")
    
    for batch_num in range(1, batches_needed + 1):
        current_count = count_existing_records()
        
        # Calculate this batch size (might be smaller for last batch)
        this_batch_size = min(batch_size, target_total - current_count)
        
        logger.info(f"\n🔄 BATCH {batch_num}/{batches_needed}")
        logger.info(f"   Current: {current_count} records")
        logger.info(f"   Generating: {this_batch_size} records") 
        logger.info(f"   Will have: {current_count + this_batch_size} records")
        
        # Run this batch
        success = run_synthea_batch(this_batch_size, start_seed=1000 + batch_num)
        
        if not success:
            logger.error(f"❌ Batch {batch_num} failed, stopping")
            break
        
        # Verify progress
        new_count = count_existing_records()
        generated_this_batch = new_count - current_count
        
        logger.info(f"✅ BATCH {batch_num} COMPLETE!")
        logger.info(f"   Generated: {generated_this_batch} records")
        logger.info(f"   Total now: {new_count} records")
        logger.info(f"   Progress: {new_count}/{target_total} ({100*new_count/target_total:.1f}%)")
        
        # Check if we've reached target
        if new_count >= target_total:
            logger.info(f"🎉 TARGET REACHED! Generated {new_count} records")
            break
        
        # Brief pause between batches
        logger.info("⏳ Pausing 5 seconds before next batch...")
        time.sleep(5)
    
    final_count = count_existing_records()
    logger.info(f"\n🏁 GENERATION COMPLETE!")
    logger.info(f"   Final count: {final_count} records")
    logger.info(f"   Target: {target_total} records")
    logger.info(f"   Success: {'✅ YES' if final_count >= target_total else '❌ NO'}")

if __name__ == "__main__":
    main()