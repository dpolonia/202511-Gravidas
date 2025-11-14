#!/usr/bin/env python3
"""
Semantic Tree Utilities for Persona-Record Matching

This module provides data structures and utilities for:
1. Defining semantic trees for personas and health records
2. Comparing semantic trees hierarchically
3. Calculating similarity scores between semantic structures
4. Validating semantic tree completeness and consistency

Semantic trees organize person attributes hierarchically:
- Personas: Demographics → Socioeconomic → Health Profile → Behavioral → Psychosocial
- Health Records: Patient Demographics → Clinical Profile → Utilization → Risk Factors → Pregnancy Specific

This enables more nuanced matching than simple categorical comparison.
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class HealthConsciousness(Enum):
    """Health consciousness level scale (1-5)."""
    VERY_LOW = 1
    LOW = 2
    MODERATE = 3
    HIGH = 4
    VERY_HIGH = 5


class HealthcareAccess(Enum):
    """Healthcare access level."""
    VERY_LIMITED = 1
    LIMITED = 2
    MODERATE = 3
    GOOD = 4
    EXCELLENT = 5


class PregnancyReadiness(Enum):
    """Pregnancy readiness/planning status."""
    NOT_READY = 1
    SOMEWHAT_UNCERTAIN = 2
    NEUTRAL = 3
    PLANNING = 4
    ACTIVELY_TRYING = 5


class PregnancyRiskLevel(Enum):
    """Pregnancy risk classification based on medical history."""
    LOW_RISK = 1
    MODERATE_RISK = 2
    ELEVATED_RISK = 3
    HIGH_RISK = 4
    VERY_HIGH_RISK = 5


class SocialSupport(Enum):
    """Social support strength scale."""
    ISOLATED = 1
    LIMITED = 2
    MODERATE = 3
    STRONG = 4
    VERY_STRONG = 5


# ==================== PERSONA SEMANTIC TREE ====================

@dataclass
class PregnancyIntentionsNode:
    """Pregnancy-specific intentions and history for persona."""
    trying_duration: int = 0  # Months actively trying to conceive (0 if not trying)
    gravida: int = 0  # Total number of pregnancies (including current)
    para: int = 0  # Number of births after 20 weeks gestation
    previous_complications: List[str] = field(default_factory=list)  # e.g., ["gestational_diabetes", "preeclampsia"]
    previous_delivery_methods: List[str] = field(default_factory=list)  # e.g., ["vaginal", "cesarean"]
    miscarriage_count: int = 0  # Number of pregnancy losses before 20 weeks
    abortion_count: int = 0  # Number of elective terminations
    ectopic_count: int = 0  # Number of ectopic pregnancies
    fertility_treatments: bool = False  # Currently using or has used fertility treatments
    fertility_treatment_types: List[str] = field(default_factory=list)  # e.g., ["IVF", "IUI", "Clomid"]
    preconception_care: bool = False  # Currently receiving preconception counseling
    contraception_current: Optional[str] = None  # Current contraception method
    contraception_history: List[str] = field(default_factory=list)  # Previous methods
    breastfeeding_history: bool = False  # Has previously breastfed
    breastfeeding_duration_months: int = 0  # Average duration of breastfeeding
    pregnancy_spacing_preference: Optional[str] = None  # e.g., "2-3 years", "close together", "no preference"
    partner_support_for_pregnancy: int = 3  # 1-5 scale for partner support

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def validate(self) -> bool:
        """Validate pregnancy intentions node."""
        if self.gravida < 0 or self.para < 0:
            logger.warning("Gravida and para must be non-negative")
        if self.para > self.gravida:
            logger.warning(f"Para ({self.para}) cannot exceed gravida ({self.gravida})")
        if not (1 <= self.partner_support_for_pregnancy <= 5):
            logger.warning(f"Partner support should be 1-5, got {self.partner_support_for_pregnancy}")
        if self.trying_duration < 0:
            logger.warning(f"Trying duration must be non-negative, got {self.trying_duration}")
        return True

@dataclass
class DemographicsNode:
    """Demographics branch of semantic tree."""
    age: int
    gender: str  # "female"
    location_type: str  # "urban", "suburban", "rural"
    ethnicity: Optional[str] = None
    language_primary: str = "English"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def validate(self) -> bool:
        """Validate demographics node."""
        if not (12 <= self.age <= 60):
            logger.warning(f"Age {self.age} outside typical range [12-60]")
        if self.gender != "female":
            logger.warning(f"Gender {self.gender} unexpected for pregnancy study")
        if self.location_type not in ["urban", "suburban", "rural"]:
            logger.warning(f"Unknown location type: {self.location_type}")
        return True


@dataclass
class SocioeconomicNode:
    """Socioeconomic branch of semantic tree."""
    education_level: str  # "no_degree", "high_school", "bachelors", "masters", "doctorate"
    income_bracket: str  # "low", "lower_middle", "middle", "upper_middle", "high"
    occupation_category: str  # "service", "skilled_trade", "professional", "executive", "student", "homemaker", "unemployed"
    employment_status: str  # "employed", "self_employed", "unemployed", "student", "homemaker", "retired", "disabled"
    insurance_status: str  # "insured", "underinsured", "uninsured", "medicaid", "medicare", "private"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def validate(self) -> bool:
        """Validate socioeconomic node."""
        valid_education = ["no_degree", "unknown", "high_school", "bachelors", "masters", "doctorate"]
        valid_income = ["low", "lower_middle", "middle", "upper_middle", "high"]
        valid_employment = ["employed", "self_employed", "unemployed", "student", "homemaker", "retired", "disabled"]

        if self.education_level not in valid_education:
            logger.warning(f"Unknown education level: {self.education_level}")
        if self.income_bracket not in valid_income:
            logger.warning(f"Unknown income bracket: {self.income_bracket}")
        if self.employment_status not in valid_employment:
            logger.warning(f"Unknown employment status: {self.employment_status}")
        return True


@dataclass
class HealthProfileNode:
    """Health profile branch of semantic tree."""
    health_consciousness: int  # 1-5 (HealthConsciousness enum)
    healthcare_access: int  # 1-5 (HealthcareAccess enum)
    pregnancy_readiness: int  # 1-5 (PregnancyReadiness enum)
    reported_health_conditions: List[str] = field(default_factory=list)  # e.g., "diabetes", "hypertension"
    medication_history: List[str] = field(default_factory=list)  # medication types
    allergies: List[str] = field(default_factory=list)
    surgery_history: List[str] = field(default_factory=list)
    reproductive_history: Optional[str] = None  # e.g., "nulliparous", "multiparous", "previous_miscarriage"
    family_medical_history: List[str] = field(default_factory=list)  # conditions in family

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def validate(self) -> bool:
        """Validate health profile node."""
        for scale_val, name in [(self.health_consciousness, "health_consciousness"),
                                 (self.healthcare_access, "healthcare_access"),
                                 (self.pregnancy_readiness, "pregnancy_readiness")]:
            if not (1 <= scale_val <= 5):
                logger.warning(f"{name} should be 1-5, got {scale_val}")
        return True


@dataclass
class BehavioralNode:
    """Behavioral and lifestyle branch of semantic tree."""
    physical_activity_level: int  # 1-5: sedentary to very_active
    nutrition_awareness: int  # 1-5: poor to excellent
    smoking_status: str  # "never", "former", "current"
    alcohol_consumption: str  # "never", "occasional", "moderate", "heavy"
    substance_use: str  # "none", "minimal", "moderate", "significant"
    sleep_quality: int  # 1-5: very_poor to excellent

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def validate(self) -> bool:
        """Validate behavioral node."""
        for scale_val, name in [(self.physical_activity_level, "physical_activity_level"),
                                 (self.nutrition_awareness, "nutrition_awareness"),
                                 (self.sleep_quality, "sleep_quality")]:
            if not (1 <= scale_val <= 5):
                logger.warning(f"{name} should be 1-5, got {scale_val}")
        return True


@dataclass
class PsychosocialNode:
    """Psychosocial branch of semantic tree."""
    mental_health_status: int  # 1-5: significant_concerns to excellent
    stress_level: int  # 1-5: very_high to very_low
    social_support: int  # 1-5: isolated to very_strong
    marital_status: str  # "single", "married", "partnered", "divorced", "widowed"
    relationship_stability: int  # 1-5: very_unstable to very_stable
    financial_stress: int  # 1-5: very_high to none
    family_planning_attitudes: str  # "wants_children", "uncertain", "does_not_want", "not_applicable"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def validate(self) -> bool:
        """Validate psychosocial node."""
        for scale_val, name in [(self.mental_health_status, "mental_health_status"),
                                 (self.stress_level, "stress_level"),
                                 (self.social_support, "social_support"),
                                 (self.relationship_stability, "relationship_stability"),
                                 (self.financial_stress, "financial_stress")]:
            if not (1 <= scale_val <= 5):
                logger.warning(f"{name} should be 1-5, got {scale_val}")
        return True


@dataclass
class PersonaSemanticTree:
    """Complete semantic tree for a persona."""
    persona_id: int
    demographics: DemographicsNode
    socioeconomic: SocioeconomicNode
    health_profile: HealthProfileNode
    behavioral: BehavioralNode
    psychosocial: PsychosocialNode
    pregnancy_intentions: PregnancyIntentionsNode

    def to_dict(self) -> Dict[str, Any]:
        """Convert complete tree to dictionary."""
        return {
            'persona_id': self.persona_id,
            'demographics': self.demographics.to_dict(),
            'socioeconomic': self.socioeconomic.to_dict(),
            'health_profile': self.health_profile.to_dict(),
            'behavioral': self.behavioral.to_dict(),
            'psychosocial': self.psychosocial.to_dict(),
            'pregnancy_intentions': self.pregnancy_intentions.to_dict()
        }

    def validate(self) -> bool:
        """Validate all branches."""
        self.demographics.validate()
        self.socioeconomic.validate()
        self.health_profile.validate()
        self.behavioral.validate()
        self.psychosocial.validate()
        self.pregnancy_intentions.validate()
        return True


# ==================== HEALTH RECORD SEMANTIC TREE ====================

@dataclass
class ClinicCondition:
    """Semantic categorization of a clinical condition."""
    code: str  # SNOMED code
    display: str  # Human-readable name
    category: str  # "chronic", "acute", "pregnancy_related", "complication", "preventive"
    severity: int  # 1-5: mild to critical
    pregnancy_relevance: int  # 1-5: not_relevant to critical
    onset_date: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MedicationProfile:
    """Organized medication information."""
    medication_categories: List[str]  # e.g., ["antihypertensive", "antidiabetic"]
    pregnancy_safety: str  # "contraindicated", "avoid", "use_with_caution", "compatible", "safe"
    chronic_vs_acute: str  # "chronic", "acute", "mixed"
    medication_count: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HealthcareUtilizationProfile:
    """Healthcare utilization patterns from encounters."""
    visit_frequency: str  # "rare", "occasional", "regular", "frequent", "very_frequent"
    primary_care_engagement: int  # 1-5
    specialist_utilization: int  # 1-5
    preventive_care_visits: int  # count
    emergency_visits: int  # count
    inpatient_stays: int  # count
    estimated_healthcare_access: int  # 1-5 inferred from utilization

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PregnancyProfile:
    """Pregnancy-specific clinical indicators."""
    has_pregnancy_codes: bool
    pregnancy_stage: Optional[str]  # "preconception", "trimester_1", "trimester_2", "trimester_3", "postpartum"
    complication_indicators: List[str]  # e.g., ["gestational_diabetes", "pre_eclampsia"]
    obstetric_history_indicators: List[str]  # e.g., ["previous_cesarean", "previous_miscarriage"]
    prenatal_care_indicators: List[str]  # e.g., ["antenatal_visits", "ultrasound"]
    risk_level: int  # 1-5: low_risk to very_high_risk

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HealthRecordSemanticTree:
    """Complete semantic tree for a health record."""
    patient_id: str
    age: int
    conditions: List[ClinicCondition]
    condition_categories: Dict[str, int]  # count by category
    chronic_disease_count: int
    acute_condition_count: int
    comorbidity_index: float  # 0.0 to 1.0
    medications: MedicationProfile
    healthcare_utilization: HealthcareUtilizationProfile
    pregnancy_profile: PregnancyProfile
    overall_health_status: str  # "excellent", "good", "fair", "poor", "complex"

    def to_dict(self) -> Dict[str, Any]:
        """Convert complete tree to dictionary."""
        return {
            'patient_id': self.patient_id,
            'age': self.age,
            'conditions': [c.to_dict() for c in self.conditions],
            'condition_categories': self.condition_categories,
            'chronic_disease_count': self.chronic_disease_count,
            'acute_condition_count': self.acute_condition_count,
            'comorbidity_index': self.comorbidity_index,
            'medications': self.medications.to_dict(),
            'healthcare_utilization': self.healthcare_utilization.to_dict(),
            'pregnancy_profile': self.pregnancy_profile.to_dict(),
            'overall_health_status': self.overall_health_status
        }

    def validate(self) -> bool:
        """Validate health record tree."""
        if not (0.0 <= self.comorbidity_index <= 1.0):
            logger.warning(f"Comorbidity index {self.comorbidity_index} outside [0.0-1.0]")
        if not (1 <= self.pregnancy_profile.risk_level <= 5):
            logger.warning(f"Pregnancy risk level {self.pregnancy_profile.risk_level} outside [1-5]")
        return True


# ==================== SEMANTIC SIMILARITY FUNCTIONS ====================

def calculate_demographics_similarity(
    persona_demo: DemographicsNode,
    record_age: int
) -> float:
    """
    Calculate similarity between persona demographics and record age.

    Args:
        persona_demo: Persona demographics node
        record_age: Age from health record

    Returns:
        Similarity score 0.0-1.0
    """
    age_diff = abs(persona_demo.age - record_age)

    if age_diff == 0:
        return 1.0
    elif age_diff <= 2:
        return 0.95 - (age_diff / 2.0) * 0.15
    elif age_diff <= 5:
        return 0.80 - ((age_diff - 2) / 3.0) * 0.20
    else:
        return max(0.0, 0.60 - ((age_diff - 5) / 10.0) * 0.60)


def calculate_socioeconomic_similarity(
    persona_socio: SocioeconomicNode,
    record_utilization: HealthcareUtilizationProfile
) -> float:
    """
    Calculate similarity between persona socioeconomic profile and
    inferred health access from record utilization.

    Returns:
        Similarity score 0.0-1.0
    """
    # Map socioeconomic to expected healthcare access
    access_map = {
        "low": 1,
        "lower_middle": 2,
        "middle": 3,
        "upper_middle": 4,
        "high": 5
    }

    persona_access_expected = access_map.get(persona_socio.income_bracket, 3)
    record_access_actual = record_utilization.estimated_healthcare_access

    # Calculate difference
    diff = abs(persona_access_expected - record_access_actual)

    # Convert to similarity score
    if diff == 0:
        return 1.0
    elif diff == 1:
        return 0.85
    elif diff == 2:
        return 0.65
    else:
        return max(0.3, 1.0 - (diff * 0.2))


def calculate_health_profile_similarity(
    persona_health: HealthProfileNode,
    record_tree: HealthRecordSemanticTree
) -> float:
    """
    Calculate similarity between persona health profile and actual health record.

    Considers: health consciousness alignment, condition expectations, readiness.

    Returns:
        Similarity score 0.0-1.0
    """
    similarities = []

    # Health consciousness vs. healthcare utilization
    hc_sim = 1.0 - abs(persona_health.health_consciousness - record_tree.healthcare_utilization.primary_care_engagement) / 5.0
    similarities.append(hc_sim)

    # Healthcare access expectation vs. actual access
    access_sim = 1.0 - abs(persona_health.healthcare_access - record_tree.healthcare_utilization.estimated_healthcare_access) / 5.0
    similarities.append(access_sim)

    # Pregnancy readiness vs. pregnancy profile/risk
    # Higher readiness should align with lower-risk pregnancy profiles
    readiness_to_risk_adjust = (persona_health.pregnancy_readiness - 1) / 4.0  # 0.0 to 1.0
    risk_to_readiness_adjust = 1.0 - (record_tree.pregnancy_profile.risk_level - 1) / 4.0  # 1.0 to 0.0
    readiness_sim = 1.0 - abs(readiness_to_risk_adjust - risk_to_readiness_adjust)
    similarities.append(readiness_sim)

    # Average similarities
    return sum(similarities) / len(similarities)


def calculate_behavioral_similarity(
    persona_behavioral: BehavioralNode,
    record_tree: HealthRecordSemanticTree
) -> float:
    """
    Calculate similarity between persona behavioral profile and
    inferred behaviors from health record.

    Returns:
        Similarity score 0.0-1.0
    """
    similarities = []

    # Physical activity vs. health status
    activity_health_map = {1: 1, 2: 2, 3: 3, 4: 4, 5: 4}  # map to health status
    activity_inferred = activity_health_map.get(persona_behavioral.physical_activity_level, 3)

    health_status_map = {"excellent": 5, "good": 4, "fair": 3, "poor": 2, "complex": 1}
    health_status_actual = health_status_map.get(record_tree.overall_health_status, 3)

    activity_sim = 1.0 - abs(activity_inferred - health_status_actual) / 5.0
    similarities.append(activity_sim)

    # Smoking status and other risky behaviors should be consistent with chronic disease burden
    smoking_risk = {"never": 1, "former": 2, "current": 3}.get(persona_behavioral.smoking_status, 2)
    disease_burden = record_tree.chronic_disease_count / max(1, 10)  # normalize to 0-1

    risk_sim = 1.0 - abs((smoking_risk / 3.0) - min(disease_burden, 1.0))
    similarities.append(risk_sim)

    # Average
    return sum(similarities) / len(similarities)


def calculate_psychosocial_similarity(
    persona_psycho: PsychosocialNode,
    record_tree: HealthRecordSemanticTree
) -> float:
    """
    Calculate similarity between persona psychosocial profile and
    inferred psychosocial factors from health record.

    Returns:
        Similarity score 0.0-1.0
    """
    similarities = []

    # Marital status + relationship stability should reflect in healthcare utilization patterns
    # Stable relationships tend to have better healthcare engagement
    stability_sim = persona_psycho.relationship_stability / 5.0
    access_sim = record_tree.healthcare_utilization.estimated_healthcare_access / 5.0

    marriage_alignment = 1.0 - abs(stability_sim - access_sim)
    similarities.append(marriage_alignment)

    # Financial stress should correlate with healthcare access and utilization
    no_stress = (5 - persona_psycho.financial_stress) / 4.0  # inverted to 0-1
    good_access = record_tree.healthcare_utilization.estimated_healthcare_access / 5.0

    financial_sim = 1.0 - abs(no_stress - good_access) * 0.5
    similarities.append(financial_sim)

    # Social support should enhance health outcomes
    support_sim = persona_psycho.social_support / 5.0
    health_sim = 1.0 - min(record_tree.comorbidity_index, 1.0)

    support_health_alignment = 1.0 - abs(support_sim - health_sim)
    similarities.append(support_health_alignment)

    # Average
    return sum(similarities) / len(similarities)


def calculate_semantic_tree_similarity(
    persona_tree: PersonaSemanticTree,
    record_tree: HealthRecordSemanticTree,
    weights: Optional[Dict[str, float]] = None
) -> Tuple[float, Dict[str, float]]:
    """
    Calculate comprehensive semantic similarity between persona and health record trees.

    Args:
        persona_tree: PersonaSemanticTree object
        record_tree: HealthRecordSemanticTree object
        weights: Optional custom weights for tree branches

    Returns:
        Tuple of (total_similarity, component_similarities)
    """
    if weights is None:
        weights = {
            'demographics': 0.25,
            'socioeconomic': 0.15,
            'health_profile': 0.30,
            'behavioral': 0.15,
            'psychosocial': 0.15
        }

    components = {}

    # Calculate each component similarity
    components['demographics'] = calculate_demographics_similarity(
        persona_tree.demographics,
        record_tree.age
    )

    components['socioeconomic'] = calculate_socioeconomic_similarity(
        persona_tree.socioeconomic,
        record_tree.healthcare_utilization
    )

    components['health_profile'] = calculate_health_profile_similarity(
        persona_tree.health_profile,
        record_tree
    )

    components['behavioral'] = calculate_behavioral_similarity(
        persona_tree.behavioral,
        record_tree
    )

    components['psychosocial'] = calculate_psychosocial_similarity(
        persona_tree.psychosocial,
        record_tree
    )

    # Calculate weighted total
    total_similarity = sum(components[key] * weights[key] for key in weights.keys())

    return total_similarity, components


# ==================== SERIALIZATION ====================

def persona_tree_to_json(tree: PersonaSemanticTree) -> str:
    """Serialize persona semantic tree to JSON."""
    return json.dumps(tree.to_dict(), indent=2)


def health_tree_to_json(tree: HealthRecordSemanticTree) -> str:
    """Serialize health record semantic tree to JSON."""
    return json.dumps(tree.to_dict(), indent=2)


def persona_tree_from_dict(data: Dict[str, Any]) -> PersonaSemanticTree:
    """Deserialize persona semantic tree from dictionary."""
    # Handle backward compatibility - old personas may not have pregnancy_intentions
    pregnancy_intentions_data = data.get('pregnancy_intentions', {})
    if not pregnancy_intentions_data:
        pregnancy_intentions = PregnancyIntentionsNode()
    else:
        pregnancy_intentions = PregnancyIntentionsNode(**pregnancy_intentions_data)

    return PersonaSemanticTree(
        persona_id=data['persona_id'],
        demographics=DemographicsNode(**data['demographics']),
        socioeconomic=SocioeconomicNode(**data['socioeconomic']),
        health_profile=HealthProfileNode(**data['health_profile']),
        behavioral=BehavioralNode(**data['behavioral']),
        psychosocial=PsychosocialNode(**data['psychosocial']),
        pregnancy_intentions=pregnancy_intentions
    )


def health_tree_from_dict(data: Dict[str, Any]) -> HealthRecordSemanticTree:
    """Deserialize health record semantic tree from dictionary."""
    conditions = [ClinicCondition(**c) for c in data.get('conditions', [])]
    medications = MedicationProfile(**data['medications'])
    utilization = HealthcareUtilizationProfile(**data['healthcare_utilization'])
    pregnancy = PregnancyProfile(**data['pregnancy_profile'])

    return HealthRecordSemanticTree(
        patient_id=data['patient_id'],
        age=data['age'],
        conditions=conditions,
        condition_categories=data.get('condition_categories', {}),
        chronic_disease_count=data.get('chronic_disease_count', 0),
        acute_condition_count=data.get('acute_condition_count', 0),
        comorbidity_index=data.get('comorbidity_index', 0.0),
        medications=medications,
        healthcare_utilization=utilization,
        pregnancy_profile=pregnancy,
        overall_health_status=data.get('overall_health_status', 'fair')
    )
