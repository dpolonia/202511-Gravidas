#!/usr/bin/env python3
"""
Create 100 optimal persona-health record matches with progress tracking.

Since we have 10 personas and 7,350 health records, we'll create multiple matches
per persona to reach 100 total matches, reporting progress every 10 matches.
"""

import json
import logging
import sys
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
from scipy.optimize import linear_sum_assignment
import random

# Setup logging
Path('logs').mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/03_matching_100_progressive.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def load_personas(personas_file: str) -> List[Dict[str, Any]]:
    """Load personas from JSON file."""
    logger.info(f"Loading personas from {personas_file}")
    with open(personas_file, 'r', encoding='utf-8') as f:
        personas = json.load(f)
    logger.info(f"✅ Loaded {len(personas)} personas")
    return personas

def load_health_records(max_records: int = 1000) -> List[Dict[str, Any]]:
    """Load health records from Synthea FHIR output (limited for performance)."""
    logger.info(f"Loading up to {max_records} health records from synthea/output/fhir/")
    
    fhir_dir = Path("synthea/output/fhir")
    health_records = []
    
    # Get list of FHIR files and limit to max_records
    fhir_files = list(fhir_dir.glob("*.json"))
    if len(fhir_files) > max_records:
        logger.info(f"Found {len(fhir_files)} files, sampling {max_records} for matching")
        # Sample files evenly across the dataset
        import random
        random.seed(42)  # For reproducible results
        fhir_files = random.sample(fhir_files, max_records)
    
    for i, fhir_file in enumerate(fhir_files):
        try:
            with open(fhir_file, 'r', encoding='utf-8') as f:
                fhir_data = json.load(f)
            
            # Extract patient info from FHIR bundle
            patient_data = None
            for entry in fhir_data.get('entry', []):
                if entry.get('resource', {}).get('resourceType') == 'Patient':
                    patient_data = entry['resource']
                    break
            
            if patient_data:
                # Create simplified health record (without storing full FHIR data for memory efficiency)
                record = {
                    'id': f"patient_{i+1}",
                    'fhir_file': fhir_file.name,
                    'patient_id': patient_data.get('id'),
                    'gender': patient_data.get('gender', 'unknown'),
                    'birthDate': patient_data.get('birthDate'),
                    'name': patient_data.get('name', [{}])[0].get('given', ['Unknown'])[0] + ' ' + 
                            patient_data.get('name', [{}])[0].get('family', 'Unknown'),
                    'conditions_count': len([e for e in fhir_data.get('entry', []) 
                                           if e.get('resource', {}).get('resourceType') == 'Condition']),
                    'encounters_count': len([e for e in fhir_data.get('entry', []) 
                                           if e.get('resource', {}).get('resourceType') == 'Encounter'])
                    # Note: removed 'fhir_data' to save memory during matching
                }
                health_records.append(record)
                
        except Exception as e:
            logger.warning(f"Could not parse {fhir_file}: {e}")
        
        # Progress update every 100 files
        if (i + 1) % 100 == 0:
            logger.info(f"  Processed {i + 1}/{len(fhir_files)} files...")
    
    logger.info(f"✅ Loaded {len(health_records)} health records")
    return health_records

def calculate_match_score(persona: Dict[str, Any], health_record: Dict[str, Any]) -> float:
    """Calculate compatibility score between persona and health record."""
    score = 0.0
    
    # Age compatibility (if we can extract age from birthDate)
    try:
        from datetime import datetime
        if health_record.get('birthDate'):
            birth_year = int(health_record['birthDate'][:4])
            current_year = datetime.now().year
            record_age = current_year - birth_year
            persona_age = persona.get('age', 25)
            
            age_diff = abs(record_age - persona_age)
            if age_diff <= 2:
                score += 0.4
            elif age_diff <= 5:
                score += 0.3
            elif age_diff <= 10:
                score += 0.2
            else:
                score += 0.1
    except:
        score += 0.2  # Default if can't parse age
    
    # Gender compatibility
    if health_record.get('gender', '').lower() == 'female':
        score += 0.3
    
    # Health complexity preference (more conditions = more interesting for interview)
    conditions_count = health_record.get('conditions_count', 0)
    if conditions_count >= 5:
        score += 0.2
    elif conditions_count >= 2:
        score += 0.15
    else:
        score += 0.1
    
    # Encounters count (more encounters = more healthcare experience)
    encounters_count = health_record.get('encounters_count', 0)
    if encounters_count >= 10:
        score += 0.1
    elif encounters_count >= 5:
        score += 0.05
    
    # Add some randomization to avoid ties
    score += random.uniform(-0.05, 0.05)
    
    return min(score, 1.0)  # Cap at 1.0

def create_matches_progressive(personas: List[Dict[str, Any]], 
                             health_records: List[Dict[str, Any]], 
                             target_matches: int = 100) -> List[Dict[str, Any]]:
    """Create optimal matches with progress tracking every 10 matches."""
    
    logger.info(f"🎯 Creating {target_matches} optimal matches")
    logger.info(f"📊 Using {len(personas)} personas and {len(health_records)} health records")
    
    matches_per_persona = target_matches // len(personas)
    extra_matches = target_matches % len(personas)
    
    logger.info(f"📝 Strategy: {matches_per_persona} matches per persona, +{extra_matches} extra")
    
    all_matches = []
    
    for persona_idx, persona in enumerate(personas):
        # Calculate how many matches this persona should get
        persona_match_count = matches_per_persona
        if persona_idx < extra_matches:
            persona_match_count += 1
        
        logger.info(f"\n👤 PERSONA {persona_idx + 1}/{len(personas)}: {persona.get('description', 'Unknown')[:50]}...")
        logger.info(f"   Creating {persona_match_count} matches")
        
        # Calculate scores for this persona against all health records
        scores = []
        for record in health_records:
            score = calculate_match_score(persona, record)
            scores.append(score)
        
        # Get the top matches for this persona
        top_indices = np.argsort(scores)[-persona_match_count:][::-1]  # Best matches first
        
        # Create matches for this persona
        for rank, record_idx in enumerate(top_indices):
            match = {
                'match_id': len(all_matches) + 1,
                'persona_id': persona.get('id', persona_idx + 1),
                'persona': persona,
                'health_record_id': health_records[record_idx]['id'],
                'health_record': health_records[record_idx],
                'match_score': scores[record_idx],
                'rank_for_persona': rank + 1,
                'persona_index': persona_idx,
                'record_index': record_idx
            }
            all_matches.append(match)
            
            # Progress update every 10 matches
            if len(all_matches) % 10 == 0:
                logger.info(f"📢 PROGRESS UPDATE: {len(all_matches)}/{target_matches} matches created ({100*len(all_matches)/target_matches:.1f}%)")
                logger.info(f"   Latest match: {match['persona']['description'][:30]}... → {match['health_record']['name']} (score: {match['match_score']:.3f})")
    
    # Sort by match score for final ranking
    all_matches.sort(key=lambda x: x['match_score'], reverse=True)
    
    # Update final rankings
    for i, match in enumerate(all_matches):
        match['overall_rank'] = i + 1
    
    logger.info(f"\n🎉 MATCHING COMPLETE: {len(all_matches)} total matches created")
    return all_matches

def save_matches(matches: List[Dict[str, Any]], output_dir: str):
    """Save matches to JSON file."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save full matches
    matches_file = output_path / "matched_personas.json"
    with open(matches_file, 'w', encoding='utf-8') as f:
        json.dump(matches, f, indent=2, ensure_ascii=False, default=str)
    
    logger.info(f"✅ Saved {len(matches)} matches to {matches_file}")
    
    # Save summary statistics
    summary = {
        'total_matches': len(matches),
        'personas_used': len(set(m['persona_id'] for m in matches)),
        'score_statistics': {
            'highest': max(m['match_score'] for m in matches),
            'lowest': min(m['match_score'] for m in matches),
            'average': sum(m['match_score'] for m in matches) / len(matches)
        },
        'matches_per_persona': {},
        'top_10_matches': [
            {
                'rank': m['overall_rank'],
                'persona': m['persona']['description'][:50] + "...",
                'patient': m['health_record']['name'],
                'score': round(m['match_score'], 3)
            }
            for m in matches[:10]
        ]
    }
    
    # Count matches per persona
    for match in matches:
        persona_desc = match['persona']['description'][:30] + "..."
        if persona_desc not in summary['matches_per_persona']:
            summary['matches_per_persona'][persona_desc] = 0
        summary['matches_per_persona'][persona_desc] += 1
    
    summary_file = output_path / "matching_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ Saved matching summary to {summary_file}")

def main():
    """Main matching execution."""
    logger.info("=== 100 PROGRESSIVE PERSONA-HEALTH RECORD MATCHING ===")
    
    try:
        # Load data
        personas = load_personas("data/personas_combined/personas.json")
        health_records = load_health_records()
        
        # Validate inputs
        if len(personas) == 0:
            raise ValueError("No personas found!")
        if len(health_records) == 0:
            raise ValueError("No health records found!")
        
        # Create matches (78 personas = 78 matches for 1:1 ratio)
        matches = create_matches_progressive(personas, health_records, target_matches=len(personas))
        
        # Save results
        save_matches(matches, "data/matched")
        
        logger.info(f"🎯 SUCCESS: Created {len(matches)} optimal matches!")
        logger.info("📁 Results saved in data/matched/")
        logger.info("🔄 Ready for interview phase!")
        
    except Exception as e:
        logger.error(f"❌ Matching failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()