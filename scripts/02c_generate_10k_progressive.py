#!/usr/bin/env python3
"""
Large-scale progressive Synthea health record generation with frequent progress tracking.

This script generates 10,000 health records in batches of 100 with progress reporting 
every 100 records to monitor performance and avoid stalling.
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
        logging.FileHandler('logs/02c_10k_progressive.log'),
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

def run_synthea_batch(batch_size: int, batch_num: int):
    """Run Synthea for a specific batch size."""
    try:
        cmd = [
            "./run_synthea",
            "-p", str(batch_size),  # Population size for this batch
            "-g", "F",              # Female only
            "-a", "12-60",          # Age range
            "-s", str(2000 + batch_num),  # Unique seed for each batch
            "Massachusetts"         # State
        ]
        
        logger.info(f"🚀 Starting batch {batch_num}: {batch_size} records")
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
        
        # Monitor process with timeout
        try:
            stdout, stderr = process.communicate(timeout=300)  # 5 min timeout per batch
        except subprocess.TimeoutExpired:
            process.kill()
            os.chdir("..")
            logger.error(f"❌ Batch {batch_num} timed out after 5 minutes")
            return False
        
        # Return to original directory
        os.chdir("..")
        
        if process.returncode == 0:
            logger.info(f"✅ Batch {batch_num} completed successfully")
            return True
        else:
            logger.error(f"❌ Batch {batch_num} failed with return code {process.returncode}")
            if stderr:
                logger.error(f"STDERR: {stderr[:500]}")  # Truncate long error messages
            return False
            
    except Exception as e:
        os.chdir("..")  # Ensure we return to original directory
        logger.error(f"Exception during batch {batch_num}: {e}")
        return False

def main():
    """Generate 10,000 health records progressively with echo every 100."""
    target_total = 10000
    batch_size = 100
    echo_every = 100  # Report every 100 records
    
    logger.info("=== 10K PROGRESSIVE SYNTHEA GENERATION (ECHO EVERY 100) ===")
    
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
    
    # Generate in batches
    batches_needed = (remaining + batch_size - 1) // batch_size
    logger.info(f"📦 Batches to run: {batches_needed} (×{batch_size} records each)")
    logger.info(f"📢 Progress updates: Every {echo_every} records")
    
    start_time = time.time()
    last_echo_count = existing_count
    
    for batch_num in range(1, batches_needed + 1):
        current_count = count_existing_records()
        
        # Calculate this batch size (might be smaller for last batch)
        this_batch_size = min(batch_size, target_total - current_count)
        
        logger.info(f"\n🔄 BATCH {batch_num}/{batches_needed}")
        logger.info(f"   Current: {current_count} records")
        logger.info(f"   Generating: {this_batch_size} records") 
        
        # Run this batch
        success = run_synthea_batch(this_batch_size, batch_num)
        
        if not success:
            logger.error(f"❌ Batch {batch_num} failed, stopping")
            break
        
        # Verify progress
        new_count = count_existing_records()
        generated_this_batch = new_count - current_count
        
        # Check if we should echo progress
        if new_count - last_echo_count >= echo_every or new_count >= target_total:
            elapsed = time.time() - start_time
            rate = new_count / elapsed * 60 if elapsed > 0 else 0
            
            logger.info(f"📢 ECHO UPDATE: {new_count} records generated")
            logger.info(f"   Progress: {new_count}/{target_total} ({100*new_count/target_total:.1f}%)")
            logger.info(f"   Rate: {rate:.1f} records/minute")
            logger.info(f"   Elapsed: {elapsed/60:.1f} minutes")
            
            last_echo_count = new_count
        
        logger.info(f"✅ Batch {batch_num}: +{generated_this_batch} → {new_count} total")
        
        # Check if we've reached target
        if new_count >= target_total:
            logger.info(f"🎉 TARGET REACHED! Generated {new_count} records")
            break
        
        # Brief pause between batches
        time.sleep(2)
    
    final_count = count_existing_records()
    total_elapsed = time.time() - start_time
    final_rate = final_count / total_elapsed * 60 if total_elapsed > 0 else 0
    
    logger.info(f"\n🏁 GENERATION COMPLETE!")
    logger.info(f"   Final count: {final_count} records")
    logger.info(f"   Target: {target_total} records")
    logger.info(f"   Total time: {total_elapsed/60:.1f} minutes") 
    logger.info(f"   Average rate: {final_rate:.1f} records/minute")
    logger.info(f"   Success: {'✅ YES' if final_count >= target_total else '❌ NO'}")

if __name__ == "__main__":
    main()