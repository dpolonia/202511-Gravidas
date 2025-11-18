#!/usr/bin/env python3
"""
FHIR to Semantic Tree Extractor

This module handles extraction of semantic healthcare profiles from FHIR records.
It converts clinical data into structured semantic trees for matching with personas.

Functions:
- Map SNOMED codes to semantic healthcare categories
- Extract medication profiles with pregnancy safety assessment
- Analyze healthcare utilization patterns
- Classify pregnancy risk levels
- Build complete HealthRecordSemanticTree from FHIR data
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from scripts.utils.semantic_tree import (
    HealthRecordSemanticTree,
    ClinicCondition,
    MedicationProfile,
    HealthcareUtilizationProfile,
    PregnancyProfile
)

logger = logging.getLogger(__name__)


# ==================== SNOMED CODE MAPPING ====================

# Pregnancy-related SNOMED codes with semantic categories
PREGNANCY_SNOMED_CATEGORIES = {
    # Pregnancy status/management
    "pregnancy": {
        "77386006": ("Pregnancy", "pregnancy_related", 1, 5),
        "72892002": ("Normal pregnancy", "pregnancy_related", 1, 5),
        "289256004": ("Pregnancy on oral contraceptive", "pregnancy_related", 2, 4),
        "102872000": ("Pregnancy on intrauterine contraceptive device", "pregnancy_related", 2, 4),
        "237238006": ("Pregnancy with uncertain dates", "pregnancy_related", 2, 3),
    },
    # Prenatal care
    "prenatal_care": {
        "249166004": ("Antenatal care", "pregnancy_related", 1, 5),
        "424441002": ("Prenatal initial visit", "pregnancy_related", 1, 5),
        "424619006": ("Prenatal visit", "pregnancy_related", 1, 5),
        "169560008": ("Antenatal care: second trimester", "pregnancy_related", 1, 5),
        "169561007": ("Antenatal care: third trimester", "pregnancy_related", 1, 5),
    },
    # Pregnancy complications
    "pregnancy_complications": {
        "15938005": ("Gestational diabetes mellitus", "complication", 3, 3),
        "48194001": ("Pregnancy-induced hypertension", "complication", 3, 3),
        "398254007": ("Pre-eclampsia", "complication", 4, 2),
        "237292005": ("Threatened miscarriage", "complication", 4, 1),
        "47200007": ("High risk pregnancy", "complication", 3, 2),
    },
    # Pregnancy-related procedures
    "pregnancy_procedures": {
        "177141003": ("Normal delivery procedure", "pregnancy_related", 1, 5),
        "386639001": ("Cesarean section", "pregnancy_related", 2, 4),
        "11466000": ("Cesarean delivery", "pregnancy_related", 2, 4),
        "289257008": ("Finding of stage of labor", "pregnancy_related", 1, 5),
    },
    # Chronic conditions relevant to pregnancy
    "chronic_pregnancy_relevant": {
        "73211009": ("Diabetes mellitus", "chronic", 3, 4),
        "38341003": ("Hypertension", "chronic", 2, 4),
        "195967001": ("Asthma", "chronic", 2, 3),
        "40733004": ("Infectious disease", "chronic", 2, 3),
        "25544004": ("Myopia", "chronic", 1, 1),  # Low pregnancy relevance
    },
    # Mental health
    "mental_health": {
        "35646001": ("Bipolar disorder", "chronic", 3, 3),
        "66344007": ("Depression", "chronic", 2, 4),
        "62106050": ("Generalized anxiety disorder", "chronic", 2, 4),
        "191736004": ("Postpartum depression", "complication", 3, 2),
    },
}

# Flatten SNOMED mapping for quick lookup
SNOMED_FULL_MAP = {}
for category, codes in PREGNANCY_SNOMED_CATEGORIES.items():
    for code, (display, cat_type, severity, pregnancy_rel) in codes.items():
        SNOMED_FULL_MAP[code] = {
            'display': display,
            'category': cat_type,
            'severity': severity,
            'pregnancy_relevance': pregnancy_rel
        }

# Default handling for unknown codes
DEFAULT_SNOMED_MAP = {
    'display': 'Unknown condition',
    'category': 'acute',
    'severity': 2,
    'pregnancy_relevance': 2
}


# ==================== MEDICATION SAFETY FOR PREGNANCY ====================

MEDICATION_PREGNANCY_SAFETY = {
    # Pregnancy-safe medications (Category A/B)
    "safe": [
        "prenatal vitamin", "folic acid", "iron supplement", "calcium",
        "penicillin", "acetaminophen", "prenatal vitamin with dha"
    ],
    # Use with caution (Category C)
    "caution": [
        "antidepressant", "antihistamine", "ibuprofen", "decongestant",
        "allergy medication", "asthma inhaler", "diabetes medication"
    ],
    # Avoid during pregnancy (Category D/X)
    "avoid": [
        "tetracycline", "isotretinoin", "warfarin", "ace inhibitor",
        "methotrexate", "thalidomide", "finasteride", "misoprostol",
        "valproic acid", "lisinopril", "enalapril"
    ]
}

# Medication categories
MEDICATION_CATEGORIES_MAP = {
    "prenatal": ["prenatal", "folic", "vitamin d", "calcium"],
    "cardiovascular": ["beta blocker", "ace inhibitor", "statin", "aspirin"],
    "endocrine": ["insulin", "metformin", "glibenclamide", "thyroid"],
    "mental_health": ["antidepressant", "ssri", "antipsychotic", "anxiolytic"],
    "anti_infective": ["antibiotic", "antiviral", "antifungal", "penicillin"],
    "gastrointestinal": ["antacid", "proton pump", "h2 blocker"],
    "respiratory": ["bronchodilator", "corticosteroid", "inhaler"],
    "neurological": ["anticonvulsant", "pain relief", "seizure"],
    "other": []
}


def categorize_medication(med_display: str) -> str:
    """Categorize medication into standard categories."""
    med_lower = med_display.lower()

    for category, keywords in MEDICATION_CATEGORIES_MAP.items():
        if category != "other":
            if any(keyword in med_lower for keyword in keywords):
                return category

    return "other"


def assess_pregnancy_safety(med_display: str) -> str:
    """Assess pregnancy safety of a medication."""
    med_lower = med_display.lower()

    for safe_med in MEDICATION_PREGNANCY_SAFETY["safe"]:
        if safe_med in med_lower:
            return "safe"

    for avoid_med in MEDICATION_PREGNANCY_SAFETY["avoid"]:
        if avoid_med in med_lower:
            return "contraindicated"

    for caution_med in MEDICATION_PREGNANCY_SAFETY["caution"]:
        if caution_med in med_lower:
            return "use_with_caution"

    return "compatible"


# ==================== HEALTHCARE UTILIZATION ====================

def analyze_healthcare_utilization(encounters: List[Dict[str, Any]]) -> HealthcareUtilizationProfile:
    """
    Analyze healthcare utilization patterns from encounters.

    Returns:
        HealthcareUtilizationProfile object
    """
    if not encounters:
        return HealthcareUtilizationProfile(
            visit_frequency="rare",
            primary_care_engagement=1,
            specialist_utilization=1,
            preventive_care_visits=0,
            emergency_visits=0,
            inpatient_stays=0,
            estimated_healthcare_access=1
        )

    # Categorize encounters
    preventive_count = 0
    emergency_count = 0
    inpatient_count = 0
    primary_care_count = 0
    specialist_count = 0

    for encounter in encounters:
        encounter_type = (encounter.get('type') or '').lower()

        if any(word in encounter_type for word in ['preventive', 'wellness', 'checkup', 'routine']):
            preventive_count += 1
            primary_care_count += 1
        elif any(word in encounter_type for word in ['emergency', 'urgent']):
            emergency_count += 1
        elif any(word in encounter_type for word in ['inpatient', 'hospital', 'admission']):
            inpatient_count += 1
        elif any(word in encounter_type for word in ['specialist', 'consultation']):
            specialist_count += 1
        else:
            primary_care_count += 1

    total_visits = len(encounters)

    # Determine visit frequency
    if total_visits <= 2:
        visit_frequency = "rare"
        healthcare_access = 1
    elif total_visits <= 5:
        visit_frequency = "occasional"
        healthcare_access = 2
    elif total_visits <= 10:
        visit_frequency = "regular"
        healthcare_access = 3
    elif total_visits <= 20:
        visit_frequency = "frequent"
        healthcare_access = 4
    else:
        visit_frequency = "very_frequent"
        healthcare_access = 5

    # Calculate engagement scores (1-5)
    primary_engagement = min(5, max(1, 1 + (primary_care_count / max(1, total_visits)) * 4))
    specialist_util = min(5, max(1, 1 + (specialist_count / max(1, total_visits)) * 4))

    return HealthcareUtilizationProfile(
        visit_frequency=visit_frequency,
        primary_care_engagement=int(primary_engagement),
        specialist_utilization=int(specialist_util),
        preventive_care_visits=preventive_count,
        emergency_visits=emergency_count,
        inpatient_stays=inpatient_count,
        estimated_healthcare_access=healthcare_access
    )


# ==================== VITAL SIGNS EXTRACTION ====================

# LOINC codes for pregnancy-specific vitals
PREGNANCY_VITAL_CODES = {
    # Gestational age
    '18185-9': 'gestational_age',  # Gestational age at birth
    '49051-6': 'gestational_age',  # Gestational age in weeks
    '11884-4': 'gestational_age',  # Gestational age Estimated

    # Blood pressure
    '8480-6': 'bp_systolic',  # Systolic blood pressure
    '8462-4': 'bp_diastolic',  # Diastolic blood pressure

    # Fetal heart rate
    '11616-0': 'fetal_heart_rate',  # Fetal heart rate detected by auscultation
    '55283-6': 'fetal_heart_rate',  # Fetal heart rate by US
    '8867-4': 'heart_rate',  # Heart rate (general)

    # Weight and height
    '29463-7': 'body_weight',  # Body weight
    '8302-2': 'body_height',  # Body height
    '39156-5': 'bmi',  # Body mass index
}


def extract_vitals_from_observations(observations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extract pregnancy-related vital signs from FHIR observations.

    Args:
        observations: List of parsed observation dictionaries

    Returns:
        Dictionary with vital signs:
        - gestational_age_weeks
        - blood_pressure_systolic
        - blood_pressure_diastolic
        - fetal_heart_rate
        - maternal_weight_kg
        - maternal_height_cm
        - maternal_bmi
        - weight_history (list of weight measurements for tracking gain)
    """
    vitals = {
        'gestational_age_weeks': None,
        'blood_pressure_systolic': None,
        'blood_pressure_diastolic': None,
        'fetal_heart_rate': None,
        'maternal_weight_kg': None,
        'maternal_height_cm': None,
        'maternal_bmi': None,
        'weight_history': []
    }

    # Sort observations by date (most recent first)
    dated_obs = [o for o in observations if o.get('effective_date')]
    sorted_obs = sorted(dated_obs, key=lambda x: x['effective_date'], reverse=True)

    # Track all weights for calculating weight gain
    weights = []

    # Extract latest of each vital type
    for obs in sorted_obs:
        obs_code = obs.get('code', '')
        value = obs.get('value')

        if value is None or not isinstance(value, (int, float)):
            continue

        vital_type = PREGNANCY_VITAL_CODES.get(obs_code)

        if vital_type == 'gestational_age' and vitals['gestational_age_weeks'] is None:
            vitals['gestational_age_weeks'] = float(value)

        elif vital_type == 'bp_systolic' and vitals['blood_pressure_systolic'] is None:
            vitals['blood_pressure_systolic'] = float(value)

        elif vital_type == 'bp_diastolic' and vitals['blood_pressure_diastolic'] is None:
            vitals['blood_pressure_diastolic'] = float(value)

        elif vital_type == 'fetal_heart_rate' and vitals['fetal_heart_rate'] is None:
            vitals['fetal_heart_rate'] = float(value)

        elif vital_type == 'body_weight':
            # Keep track of all weights
            weights.append({
                'value': float(value),
                'date': obs.get('effective_date', '')
            })
            if vitals['maternal_weight_kg'] is None:
                vitals['maternal_weight_kg'] = float(value)

        elif vital_type == 'body_height' and vitals['maternal_height_cm'] is None:
            vitals['maternal_height_cm'] = float(value)

        elif vital_type == 'bmi' and vitals['maternal_bmi'] is None:
            vitals['maternal_bmi'] = float(value)

    # Calculate weight gain if we have multiple weights
    if len(weights) >= 2:
        # Sort by date (oldest first)
        weights_sorted = sorted(weights, key=lambda x: x['date'])
        earliest_weight = weights_sorted[0]['value']
        latest_weight = weights_sorted[-1]['value']
        vitals['weight_history'] = weights
        vitals['weight_gain_kg'] = latest_weight - earliest_weight
    else:
        vitals['weight_gain_kg'] = None

    return vitals


# ==================== PREGNANCY RISK ASSESSMENT ====================

def calculate_pregnancy_risk_level(
    conditions: List[Dict[str, Any]],
    age: int,
    comorbidity_index: float
) -> int:
    """
    Calculate pregnancy risk level (1-5) based on clinical profile.

    Risk factors:
    - High-risk pregnancy codes
    - Comorbidities and complications
    - Age factors
    - Comorbidity burden

    Returns:
        Risk level 1-5 (1=low_risk, 5=very_high_risk)
    """
    risk_score = 0

    # Base age risk
    if age < 18 or age > 40:
        risk_score += 1
    if age < 15 or age > 45:
        risk_score += 1

    # Analyze conditions
    high_risk_conditions = [
        "47200007",  # High risk pregnancy
        "48194001",  # Pregnancy-induced hypertension
        "398254007",  # Pre-eclampsia
        "15938005",  # Gestational diabetes
    ]

    serious_conditions = [
        "73211009",  # Diabetes
        "38341003",  # Hypertension
        "35646001",  # Bipolar disorder
        "66344007",  # Depression
    ]

    high_risk_count = sum(1 for cond in conditions if cond.get('code') in high_risk_conditions)
    serious_count = sum(1 for cond in conditions if cond.get('code') in serious_conditions)

    risk_score += min(3, high_risk_count * 2)  # High risk conditions
    risk_score += min(2, serious_count)  # Serious conditions

    # Comorbidity burden
    if comorbidity_index > 0.7:
        risk_score += 2
    elif comorbidity_index > 0.4:
        risk_score += 1

    # Convert to 1-5 scale
    risk_level = min(5, max(1, 1 + (risk_score // 2)))

    return risk_level


def extract_pregnancy_profile(
    conditions: List[Dict[str, Any]],
    encounters: List[Dict[str, Any]],
    observations: List[Dict[str, Any]],
    age: int,
    comorbidity_index: float
) -> PregnancyProfile:
    """Extract pregnancy-specific profile from health record."""

    # Check for pregnancy codes
    pregnancy_codes = []
    complication_indicators = []
    obstetric_history = []
    prenatal_care_indicators = []

    for condition in conditions:
        code = condition.get('code', '')
        category = SNOMED_FULL_MAP.get(code, {}).get('category', 'acute')

        if category == "pregnancy_related":
            pregnancy_codes.append(condition.get('display', 'Unknown'))
        elif category == "complication":
            complication_indicators.append(condition.get('display', 'Unknown'))

    # Infer prenatal care from encounters
    for encounter in encounters:
        encounter_type = (encounter.get('type') or '').lower()
        if any(word in encounter_type for word in ['prenatal', 'antenatal', 'pregnancy']):
            prenatal_care_indicators.append(encounter_type)

    # Extract vital signs from observations first (needed for pregnancy stage detection)
    vitals = extract_vitals_from_observations(observations)

    # Infer pregnancy stage based on gestational age
    pregnancy_stage = None
    gestational_age = vitals.get('gestational_age_weeks')

    if pregnancy_codes or prenatal_care_indicators:
        if gestational_age:
            # Map gestational age to trimester
            # Trimester 1: 1-13 weeks
            # Trimester 2: 14-27 weeks
            # Trimester 3: 28-42 weeks
            if gestational_age <= 13:
                pregnancy_stage = "trimester_1"
            elif gestational_age <= 27:
                pregnancy_stage = "trimester_2"
            elif gestational_age <= 42:
                pregnancy_stage = "trimester_3"
            else:
                # Post-term pregnancy (>42 weeks)
                pregnancy_stage = "trimester_3"  # Treat as late third trimester
        else:
            # Fallback to default if no gestational age available
            pregnancy_stage = "trimester_1"

    # Calculate risk level
    risk_level = calculate_pregnancy_risk_level(conditions, age, comorbidity_index)

    return PregnancyProfile(
        has_pregnancy_codes=len(pregnancy_codes) > 0,
        pregnancy_stage=pregnancy_stage,
        complication_indicators=complication_indicators,
        obstetric_history_indicators=obstetric_history,
        prenatal_care_indicators=prenatal_care_indicators,
        risk_level=risk_level,
        # Vital signs
        gestational_age_weeks=vitals['gestational_age_weeks'],
        blood_pressure_systolic=vitals['blood_pressure_systolic'],
        blood_pressure_diastolic=vitals['blood_pressure_diastolic'],
        fetal_heart_rate=vitals['fetal_heart_rate'],
        maternal_weight_kg=vitals['maternal_weight_kg'],
        maternal_height_cm=vitals['maternal_height_cm'],
        maternal_bmi=vitals['maternal_bmi'],
        weight_gain_kg=vitals.get('weight_gain_kg')
    )


# ==================== COMORBIDITY INDEX ====================

def calculate_comorbidity_index(conditions: List[Dict[str, Any]]) -> float:
    """
    Calculate comorbidity index (0.0-1.0) representing disease burden.

    Based on severity and number of chronic conditions.
    """
    if not conditions:
        return 0.0

    chronic_conditions = []
    acute_conditions = []

    for cond in conditions:
        code = cond.get('code', '')
        info = SNOMED_FULL_MAP.get(code, DEFAULT_SNOMED_MAP)
        category = info.get('category', 'acute')
        severity = info.get('severity', 2)

        if category == "chronic":
            chronic_conditions.append(severity)
        elif category == "acute":
            acute_conditions.append(severity)

    # Calculate index
    chronic_score = sum(chronic_conditions) / max(1, len(chronic_conditions) * 5)
    acute_score = sum(acute_conditions) / max(1, len(acute_conditions) * 5) * 0.3

    comorbidity = min(1.0, chronic_score + acute_score)

    return comorbidity


def calculate_condition_categories(conditions: List[Dict[str, Any]]) -> Tuple[Dict[str, int], int, int]:
    """
    Categorize conditions and count by type.

    Returns:
        Tuple of (category_counts, chronic_count, acute_count)
    """
    categories = {
        "pregnancy_related": 0,
        "chronic": 0,
        "acute": 0,
        "complication": 0,
        "preventive": 0
    }

    chronic_count = 0
    acute_count = 0

    for cond in conditions:
        code = cond.get('code', '')
        info = SNOMED_FULL_MAP.get(code, DEFAULT_SNOMED_MAP)
        category = info.get('category', 'acute')

        categories[category] = categories.get(category, 0) + 1

        if category == "chronic":
            chronic_count += 1
        elif category == "acute":
            acute_count += 1

    return categories, chronic_count, acute_count


def extract_clinical_conditions(fhir_conditions: List[Dict[str, Any]]) -> List[ClinicCondition]:
    """
    Extract and categorize clinical conditions from FHIR format.

    Returns:
        List of ClinicCondition objects
    """
    conditions = []

    for fhir_cond in fhir_conditions:
        code = fhir_cond.get('code', '')
        display = fhir_cond.get('display', 'Unknown condition')
        onset = fhir_cond.get('onset', None)

        # Look up in SNOMED map
        info = SNOMED_FULL_MAP.get(code, DEFAULT_SNOMED_MAP)

        condition = ClinicCondition(
            code=code,
            display=display,
            category=info.get('category', 'acute'),
            severity=info.get('severity', 2),
            pregnancy_relevance=info.get('pregnancy_relevance', 2),
            onset_date=onset
        )

        conditions.append(condition)

    return conditions


def extract_medication_profile(medications: List[Dict[str, Any]]) -> MedicationProfile:
    """Extract medication profile from FHIR medications."""

    if not medications:
        return MedicationProfile(
            medication_categories=[],
            pregnancy_safety="safe",
            chronic_vs_acute="acute",
            medication_count=0
        )

    categories = {}
    safety_statuses = []
    med_count = len(medications)

    for med in medications:
        # Robust null-checking: handle None values explicitly
        display = (med.get('display') or '').lower()

        # Categorize
        category = categorize_medication(display)
        categories[category] = categories.get(category, 0) + 1

        # Safety
        safety = assess_pregnancy_safety(display)
        safety_statuses.append(safety)

    # Determine overall pregnancy safety
    if any(s == "contraindicated" for s in safety_statuses):
        overall_safety = "contraindicated"
    elif any(s == "avoid" for s in safety_statuses):
        overall_safety = "avoid"
    elif any(s == "use_with_caution" for s in safety_statuses):
        overall_safety = "use_with_caution"
    else:
        overall_safety = "safe"

    # Determine chronic vs acute
    chronic_vs_acute = "chronic" if med_count > 3 else "acute"

    return MedicationProfile(
        medication_categories=list(categories.keys()),
        pregnancy_safety=overall_safety,
        chronic_vs_acute=chronic_vs_acute,
        medication_count=med_count
    )


def determine_health_status(
    conditions: List[Dict[str, Any]],
    chronic_count: int,
    acute_count: int,
    comorbidity_index: float
) -> str:
    """Determine overall health status classification."""

    if comorbidity_index > 0.8 or (chronic_count > 5):
        return "complex"
    elif comorbidity_index > 0.6 or (chronic_count > 3):
        return "poor"
    elif comorbidity_index > 0.4 or (chronic_count > 1):
        return "fair"
    elif comorbidity_index > 0.2:
        return "good"
    else:
        return "excellent"


# ==================== MAIN EXTRACTION FUNCTION ====================

def build_semantic_tree_from_fhir(fhir_data: Dict[str, Any], patient_id: str, age: int) -> HealthRecordSemanticTree:
    """
    Build complete HealthRecordSemanticTree from FHIR record.

    Args:
        fhir_data: Parsed FHIR bundle data
        patient_id: Patient ID from FHIR
        age: Patient age

    Returns:
        Complete HealthRecordSemanticTree object
    """

    # Extract conditions, medications, encounters, observations from FHIR
    conditions_raw = []
    medications_raw = []
    encounters_raw = []
    observations_raw = []

    # Parse FHIR bundle entries
    entries = fhir_data.get('entry', [])
    for entry in entries:
        resource = entry.get('resource', {})
        resource_type = resource.get('resourceType', '')

        if resource_type == 'Condition':
            conditions_raw.append({
                'code': resource.get('code', {}).get('coding', [{}])[0].get('code'),
                'display': resource.get('code', {}).get('coding', [{}])[0].get('display'),
                'onset': resource.get('onsetDateTime', '')
            })

        elif resource_type == 'MedicationRequest':
            medications_raw.append({
                'code': resource.get('medicationCodeableConcept', {}).get('coding', [{}])[0].get('code'),
                'display': resource.get('medicationCodeableConcept', {}).get('coding', [{}])[0].get('display'),
            })

        elif resource_type == 'Encounter':
            encounters_raw.append({
                'type': resource.get('type', [{}])[0].get('coding', [{}])[0].get('display', ''),
                'period_start': resource.get('period', {}).get('start'),
                'period_end': resource.get('period', {}).get('end')
            })

        elif resource_type == 'Observation':
            # Parse observation with robust null-checking
            try:
                coding = resource.get('code', {}).get('coding', [])
                if not coding:
                    continue

                obs_code = coding[0].get('code', '')
                obs_display = coding[0].get('display', '')
                effective_date = resource.get('effectiveDateTime', '')

                # Handle observations with components (like blood pressure)
                components = resource.get('component', [])
                if components:
                    for comp in components:
                        comp_coding = comp.get('code', {}).get('coding', [])
                        if comp_coding:
                            comp_code = comp_coding[0].get('code', '')
                            comp_display = comp_coding[0].get('display', '')
                            comp_value_qty = comp.get('valueQuantity', {})

                            observations_raw.append({
                                'code': comp_code,
                                'display': comp_display,
                                'value': comp_value_qty.get('value'),
                                'unit': comp_value_qty.get('unit', ''),
                                'effective_date': effective_date,
                                'parent_code': obs_code
                            })
                else:
                    # Handle observations with direct values
                    value_qty = resource.get('valueQuantity', {})
                    value_codeable = resource.get('valueCodeableConcept', {})
                    value_string = resource.get('valueString', '')

                    # Determine value
                    value = None
                    unit = ''

                    if value_qty:
                        value = value_qty.get('value')
                        unit = value_qty.get('unit', '')
                    elif value_codeable:
                        # For coded values, use display text
                        coding = value_codeable.get('coding', [])
                        if coding:
                            value = coding[0].get('display', '')
                    elif value_string:
                        value = value_string

                    observations_raw.append({
                        'code': obs_code,
                        'display': obs_display,
                        'value': value,
                        'unit': unit,
                        'effective_date': effective_date,
                        'parent_code': None
                    })

            except (IndexError, KeyError, AttributeError) as e:
                logger.warning(f"Error parsing observation: {e}")
                continue

    # Extract semantic components
    clinical_conditions = extract_clinical_conditions(conditions_raw)
    medication_profile = extract_medication_profile(medications_raw)
    healthcare_utilization = analyze_healthcare_utilization(encounters_raw)
    comorbidity_index = calculate_comorbidity_index(conditions_raw)
    condition_categories, chronic_count, acute_count = calculate_condition_categories(conditions_raw)
    pregnancy_profile = extract_pregnancy_profile(conditions_raw, encounters_raw, observations_raw, age, comorbidity_index)
    health_status = determine_health_status(conditions_raw, chronic_count, acute_count, comorbidity_index)

    # Build semantic tree
    semantic_tree = HealthRecordSemanticTree(
        patient_id=patient_id,
        age=age,
        conditions=clinical_conditions,
        condition_categories=condition_categories,
        chronic_disease_count=chronic_count,
        acute_condition_count=acute_count,
        comorbidity_index=comorbidity_index,
        medications=medication_profile,
        healthcare_utilization=healthcare_utilization,
        pregnancy_profile=pregnancy_profile,
        overall_health_status=health_status
    )

    return semantic_tree
