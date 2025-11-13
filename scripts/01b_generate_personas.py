#!/usr/bin/env python3
"""
Generate synthetic personas using AI models with semantic tree structures.

This script:
1. Generates 20,000 diverse female personas (age 12-60)
2. Ensures demographic distribution (age, education, income, marital status)
3. Creates rich persona descriptions including healthcare dimensions
4. Extracts healthcare attributes (health consciousness, healthcare access, etc.)
5. Builds semantic trees for each persona
6. Saves personas with complete semantic tree structures

Semantic Tree Branches Generated:
- Demographics: Age, gender, location, ethnicity
- Socioeconomic: Education, income, employment, insurance
- HealthProfile: Health consciousness, healthcare access, pregnancy readiness, conditions
- Behavioral: Physical activity, nutrition, smoking, alcohol, sleep
- Psychosocial: Mental health, stress, social support, marital status

Usage:
    python scripts/01b_generate_personas.py --count 20000
    python scripts/01b_generate_personas.py --count 100 --output data/personas
"""

import json
import logging
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import random
import os
from datetime import datetime as dt
import re

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import yaml
    import anthropic
except ImportError:
    print("ERROR: Required packages not installed.")
    print("Please run: pip install anthropic pyyaml python-dotenv")
    sys.exit(1)

# Import common loaders and semantic tree utilities
from utils.common_loaders import load_config
from utils.semantic_tree import (
    PersonaSemanticTree,
    DemographicsNode,
    SocioeconomicNode,
    HealthProfileNode,
    BehavioralNode,
    PsychosocialNode
)

# Setup logging
Path('logs').mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/01b_generate_personas.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class PersonaGenerator:
    """Generate realistic personas using Claude."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the persona generator."""
        # Get API key - expand environment variables
        config_key = config.get('api_keys', {}).get('anthropic', {}).get('api_key', '')
        
        # Expand environment variables in config
        if config_key and config_key.startswith('${') and config_key.endswith('}'):
            env_var_name = config_key[2:-1]  # Remove ${ and }
            config_key = os.getenv(env_var_name, '')
        
        env_key = os.getenv('ANTHROPIC_API_KEY', '')

        if config_key and not config_key.startswith('your-'):
            api_key = config_key
        else:
            api_key = env_key

        if not api_key:
            raise ValueError("No Anthropic API key found in config or environment")

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-haiku-20240307"  # Fast and cheap for generation

    def generate_batch(self, count: int, batch_size: int = 100) -> str:
        """Generate a batch of personas with healthcare dimensions."""
        prompt = f"""Generate {batch_size} diverse, realistic female personas for a pregnancy study. Each persona should be a woman aged 12-60 who could potentially be pregnant or considering pregnancy.

For each persona, provide comprehensive information including:

DEMOGRAPHIC & SOCIOECONOMIC:
1. Name, age, gender (female)
2. Location (urban/suburban/rural area and city/region)
3. Education level (specify: no degree, high school, bachelors, masters, doctorate)
4. Income bracket (low, lower_middle, middle, upper_middle, high)
5. Current occupation and employment status
6. Marital/relationship status
7. Insurance status (insured, underinsured, uninsured, medicaid, medicare, private)

HEALTH & PREGNANCY DIMENSIONS:
8. Health consciousness level (sedentary/low engagement to very health-conscious)
9. Healthcare access perception (limited access vs. regular healthcare provider)
10. Current health conditions (any chronic or acute conditions mentioned)
11. Medications currently taking (if any)
12. Physical activity level (sedentary to very active)
13. Smoking/alcohol/substance use status
14. Pregnancy planning status (not planning, uncertain, planning, actively trying)
15. Social support for pregnancy (family/partner support, isolation, strong network)
16. Mental health status and stress level
17. Any reproductive history relevant to pregnancy

Format each persona as a comprehensive paragraph (5-7 sentences) that integrates both demographic and healthcare information naturally. Make them diverse in:
- Age (range 12-60, but focus on 18-45)
- Education levels
- Income levels
- Occupations
- Health consciousness
- Healthcare access
- Pregnancy readiness
- Presence/absence of health conditions
- Social support levels
- Geographic locations (urban/suburban/rural)

Example format:
"Maria is a 32-year-old accountant living in rural Colorado with a master's degree and upper-middle income. She is married with strong family support and actively trying to conceive. Maria exercises regularly and is very health-conscious, maintaining good preventive care with her primary physician. She has no chronic conditions, doesn't smoke, and drinks occasionally. She is low-stress and well-supported by her extended family in the area."

Generate exactly {batch_size} personas, each as a separate numbered paragraph. Number them 1-{batch_size}. Ensure each persona includes healthcare dimensions naturally woven into the description."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=6000,  # Increased for more detailed personas
                temperature=0.9,  # High temperature for diversity
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Failed to generate personas: {e}")
            raise


# ==================== HEALTHCARE ATTRIBUTE EXTRACTION ====================

def extract_location_type(text: str) -> str:
    """Extract location type from persona description."""
    text_lower = text.lower()
    if any(word in text_lower for word in ['urban', 'city', 'downtown', 'metropolitan', 'metropolitan area']):
        return 'urban'
    elif any(word in text_lower for word in ['suburb', 'suburban', 'outskirts', 'town']):
        return 'suburban'
    elif any(word in text_lower for word in ['rural', 'countryside', 'farm', 'small town', 'remote']):
        return 'rural'
    else:
        return random.choice(['urban', 'suburban', 'rural'])


def extract_health_consciousness(text: str) -> int:
    """
    Extract health consciousness level (1-5) from persona description.
    1=very low, 2=low, 3=moderate, 4=high, 5=very high
    """
    text_lower = text.lower()

    # Very high consciousness indicators
    if any(word in text_lower for word in ['very health-conscious', 'health nut', 'fitness enthusiast',
                                             'strict diet', 'meditates', 'wellness coach', 'marathons',
                                             'nutrition expert', 'preventive care']):
        return 5

    # High consciousness
    if any(word in text_lower for word in ['health-conscious', 'exercises regularly', 'fitness',
                                             'runs', 'yoga', 'gym', 'wellness', 'healthy lifestyle',
                                             'salads', 'organic']):
        return 4

    # Moderate consciousness
    if any(word in text_lower for word in ['occasional exercise', 'tries to stay healthy',
                                             'some physical activity', 'balanced diet', 'tries to eat well']):
        return 3

    # Low consciousness
    if any(word in text_lower for word in ['sedentary', 'busy lifestyle', 'limited time for exercise',
                                             'doesn\'t prioritize fitness', 'fast food']):
        return 2

    # Very low consciousness
    if any(word in text_lower for word in ['very sedentary', 'no exercise', 'inactive',
                                             'poor diet', 'unhealthy habits']):
        return 1

    return random.randint(2, 4)  # Default moderate


def extract_healthcare_access(text: str) -> int:
    """
    Extract healthcare access level (1-5) from persona description.
    1=very limited, 2=limited, 3=moderate, 4=good, 5=excellent
    """
    text_lower = text.lower()

    # Excellent access
    if any(word in text_lower for word in ['private physician', 'primary care doctor', 'regular healthcare provider',
                                             'good insurance', 'excellent coverage', 'specialist access', 'preventive visits']):
        return 5

    # Good access
    if any(word in text_lower for word in ['has insurance', 'primary care', 'healthcare provider',
                                             'medical care', 'can afford healthcare']):
        return 4

    # Moderate access
    if any(word in text_lower for word in ['some healthcare', 'limited insurance', 'medicaid',
                                             'occasional visits', 'community clinic']):
        return 3

    # Limited access
    if any(word in text_lower for word in ['limited access', 'underinsured', 'cannot afford',
                                             'uninsured', 'no insurance', 'rare visits']):
        return 1

    return 3  # Default moderate


def extract_pregnancy_readiness(text: str) -> int:
    """
    Extract pregnancy readiness/planning status (1-5) from persona description.
    1=not ready, 2=uncertain, 3=neutral, 4=planning, 5=actively trying
    """
    text_lower = text.lower()

    # Actively trying
    if any(word in text_lower for word in ['actively trying', 'trying to conceive', 'trying for baby',
                                             'wants to get pregnant', 'baby planning', 'baby-making']):
        return 5

    # Planning
    if any(word in text_lower for word in ['plans to have children', 'planning to conceive',
                                             'considering pregnancy', 'baby plans', 'wants children']):
        return 4

    # Neutral
    if any(word in text_lower for word in ['open to', 'may have children', 'if the time is right',
                                             'considering', 'undecided']):
        return 3

    # Uncertain
    if any(word in text_lower for word in ['uncertain about', 'hasn\'t decided', 'unclear about',
                                             'unsure about', 'focusing on career']):
        return 2

    # Not ready
    if any(word in text_lower for word in ['doesn\'t want children', 'no plans for pregnancy',
                                             'childfree', 'not interested in', 'prefers no children']):
        return 1

    return random.randint(3, 4)  # Default neutral to planning


def extract_social_support(text: str) -> int:
    """
    Extract social support strength (1-5) from persona description.
    1=isolated, 2=limited, 3=moderate, 4=strong, 5=very strong
    """
    text_lower = text.lower()

    # Very strong
    if any(word in text_lower for word in ['strong family support', 'tight-knit family', 'extended family',
                                             'very supportive partner', 'strong network', 'close community']):
        return 5

    # Strong
    if any(word in text_lower for word in ['family support', 'supportive partner', 'good network',
                                             'supportive friends', 'married with']):
        return 4

    # Moderate
    if any(word in text_lower for word in ['some support', 'has friends', 'has family',
                                             'partner support', 'community involvement']):
        return 3

    # Limited
    if any(word in text_lower for word in ['limited support', 'few close', 'works alone',
                                             'isolated', 'limited social circle']):
        return 2

    # Isolated
    if any(word in text_lower for word in ['no support', 'isolated', 'alone', 'no close relationships']):
        return 1

    return 3  # Default moderate


def extract_mental_health_status(text: str) -> int:
    """
    Extract mental health status (1-5) from persona description.
    1=significant concerns, 2=some concerns, 3=moderate, 4=good, 5=excellent
    """
    text_lower = text.lower()

    # Excellent
    if any(word in text_lower for word in ['mentally healthy', 'positive outlook', 'well-balanced',
                                             'emotional stability', 'resilient']):
        return 5

    # Good
    if any(word in text_lower for word in ['good mental health', 'stable', 'handles stress well',
                                             'coping well', 'optimistic']):
        return 4

    # Moderate
    if any(word in text_lower for word in ['average stress', 'manages stress', 'some challenges',
                                             'balanced']):
        return 3

    # Some concerns
    if any(word in text_lower for word in ['anxiety', 'depression', 'stressed', 'overwhelmed']):
        return 2

    # Significant concerns
    if any(word in text_lower for word in ['severe anxiety', 'clinical depression', 'mental illness',
                                             'significant mental health']):
        return 1

    return 3  # Default moderate


def extract_stress_level(text: str) -> int:
    """
    Extract stress level (1-5) from persona description.
    1=very high, 2=high, 3=moderate, 4=low, 5=very low
    """
    text_lower = text.lower()

    # Very low stress
    if any(word in text_lower for word in ['low-stress', 'relaxed', 'minimal stress',
                                             'stress-free', 'calm lifestyle']):
        return 5

    # Low stress
    if any(word in text_lower for word in ['manages stress well', 'low stress',
                                             'handles pressure', 'peaceful']):
        return 4

    # Moderate stress
    if any(word in text_lower for word in ['average stress', 'moderate stress',
                                             'busy but balanced', 'some pressure']):
        return 3

    # High stress
    if any(word in text_lower for word in ['high stress', 'stressful', 'demanding job',
                                             'overworked', 'overwhelmed']):
        return 2

    # Very high stress
    if any(word in text_lower for word in ['very stressful', 'extremely busy', 'crisis',
                                             'burnout', 'severe stress']):
        return 1

    return 3  # Default moderate


def extract_physical_activity_level(text: str) -> int:
    """
    Extract physical activity level (1-5) from persona description.
    1=sedentary, 2=low, 3=moderate, 4=high, 5=very high
    """
    text_lower = text.lower()

    # Very high
    if any(word in text_lower for word in ['marathons', 'competitive athlete', 'very active',
                                             'intensive training', 'daily workouts']):
        return 5

    # High
    if any(word in text_lower for word in ['exercises regularly', 'fitness', 'gym', 'runs',
                                             'yoga', 'active lifestyle', 'regular exercise']):
        return 4

    # Moderate
    if any(word in text_lower for word in ['occasional exercise', 'some physical activity',
                                             'weekend activities', 'tries to stay active']):
        return 3

    # Low
    if any(word in text_lower for word in ['limited exercise', 'sedentary job', 'little physical activity',
                                             'desk job']):
        return 2

    # Sedentary
    if any(word in text_lower for word in ['sedentary', 'inactive', 'no exercise', 'very little activity']):
        return 1

    return 3  # Default moderate


def extract_smoking_status(text: str) -> str:
    """Extract smoking status from persona description."""
    text_lower = text.lower()

    if any(word in text_lower for word in ['smoker', 'smokes', 'smoking', 'cigarettes', 'pack a day']):
        return 'current'
    elif any(word in text_lower for word in ['former smoker', 'quit smoking', 'used to smoke', 'ex-smoker']):
        return 'former'
    else:
        return 'never'


def extract_alcohol_consumption(text: str) -> str:
    """Extract alcohol consumption status from persona description."""
    text_lower = text.lower()

    if any(word in text_lower for word in ['heavy drinker', 'drinks heavily', 'alcoholic',
                                             'drinks daily', 'significant alcohol']):
        return 'heavy'
    elif any(word in text_lower for word in ['drinks moderately', 'moderate drinker', 'weekly drinks',
                                              'socially drinks', 'cocktails']):
        return 'moderate'
    elif any(word in text_lower for word in ['occasional drinker', 'occasionally drinks', 'rarely drinks',
                                              'socially', 'occasional alcohol']):
        return 'occasional'
    else:
        return 'never'


def extract_health_conditions(text: str) -> List[str]:
    """Extract reported health conditions from persona description."""
    text_lower = text.lower()

    conditions = []
    condition_keywords = {
        'diabetes': ['diabetes', 'diabetic', 'type 2', 'glucose'],
        'hypertension': ['hypertension', 'high blood pressure', 'hypertensive'],
        'asthma': ['asthma', 'asthmatic', 'respiratory'],
        'thyroid': ['thyroid', 'hypothyroid', 'hyperthyroid'],
        'depression': ['depression', 'depressed', 'clinical depression'],
        'anxiety': ['anxiety disorder', 'anxiety', 'anxious'],
        'obesity': ['obese', 'obesity'],
        'heart_disease': ['heart disease', 'cardiac', 'heart condition'],
        'autoimmune': ['autoimmune', 'lupus', 'rheumatoid'],
        'pcos': ['pcos', 'polycystic ovary', 'hormonal imbalance'],
        'endometriosis': ['endometriosis'],
        'fibroids': ['fibroids'],
    }

    for condition, keywords in condition_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            conditions.append(condition)

    return conditions


def parse_generated_personas(text: str, start_id: int) -> List[Dict[str, Any]]:
    """Parse generated persona text into structured format."""
    personas = []

    lines = text.strip().split('\n')

    current_text = ""
    current_number = None

    for line in lines:
        # Check if line starts with a number
        match = re.match(r'^(\d+)\.\s+(.+)$', line.strip())
        if match:
            # Save previous persona if exists
            if current_text:
                persona = parse_single_persona(current_text, start_id + current_number - 1)
                if persona:
                    personas.append(persona)

            current_number = int(match.group(1))
            current_text = match.group(2)
        else:
            # Continuation of current persona
            current_text += " " + line.strip()

    # Don't forget last persona
    if current_text and current_number:
        persona = parse_single_persona(current_text, start_id + current_number - 1)
        if persona:
            personas.append(persona)

    return personas


def build_semantic_tree_for_persona(text: str, persona_id: int, basic_data: Dict[str, Any]) -> PersonaSemanticTree:
    """Build a semantic tree for the persona with extracted healthcare attributes."""

    # Extract healthcare dimensions
    location_type = extract_location_type(text)
    health_consciousness = extract_health_consciousness(text)
    healthcare_access = extract_healthcare_access(text)
    pregnancy_readiness = extract_pregnancy_readiness(text)
    social_support = extract_social_support(text)
    mental_health_status = extract_mental_health_status(text)
    stress_level = extract_stress_level(text)
    physical_activity_level = extract_physical_activity_level(text)
    smoking_status = extract_smoking_status(text)
    alcohol_consumption = extract_alcohol_consumption(text)
    health_conditions = extract_health_conditions(text)

    # Infer employment status
    text_lower = text.lower()
    if any(word in text_lower for word in ['unemployed', 'without work', 'looking for']):
        employment_status = 'unemployed'
    elif any(word in text_lower for word in ['self-employed', 'freelance', 'own business']):
        employment_status = 'self_employed'
    elif any(word in text_lower for word in ['student', 'university', 'college']):
        employment_status = 'student'
    elif any(word in text_lower for word in ['homemaker', 'stay-at-home', 'housewife']):
        employment_status = 'homemaker'
    elif any(word in text_lower for word in ['retired']):
        employment_status = 'retired'
    elif any(word in text_lower for word in ['disabled', 'disability']):
        employment_status = 'disabled'
    else:
        employment_status = 'employed'

    # Infer insurance status
    if any(word in text_lower for word in ['uninsured', 'no insurance', 'without insurance']):
        insurance_status = 'uninsured'
    elif any(word in text_lower for word in ['medicaid']):
        insurance_status = 'medicaid'
    elif any(word in text_lower for word in ['medicare']):
        insurance_status = 'medicare'
    elif any(word in text_lower for word in ['private insurance', 'private coverage', 'has insurance']):
        insurance_status = 'private'
    elif any(word in text_lower for word in ['underinsured', 'limited insurance']):
        insurance_status = 'underinsured'
    else:
        insurance_status = 'insured'

    # Infer occupation category
    text_lower = text.lower()
    if any(word in text_lower for word in ['doctor', 'nurse', 'teacher', 'engineer', 'lawyer', 'professor', 'scientist']):
        occupation_category = 'professional'
    elif any(word in text_lower for word in ['manager', 'director', 'executive', 'ceo', 'president']):
        occupation_category = 'executive'
    elif any(word in text_lower for word in ['electrician', 'plumber', 'mechanic', 'carpenter', 'skilled']):
        occupation_category = 'skilled_trade'
    elif any(word in text_lower for word in ['retail', 'cashier', 'clerk', 'assistant', 'service']):
        occupation_category = 'service'
    elif any(word in text_lower for word in ['homemaker', 'stay-at-home', 'housewife']):
        occupation_category = 'homemaker'
    elif any(word in text_lower for word in ['student']):
        occupation_category = 'student'
    else:
        occupation_category = 'other'

    # Infer family planning attitudes
    if any(word in text_lower for word in ['wants children', 'wants to have', 'plans to have', 'trying to conceive']):
        family_planning_attitudes = 'wants_children'
    elif any(word in text_lower for word in ['doesn\'t want', 'no plans', 'childfree']):
        family_planning_attitudes = 'does_not_want'
    elif any(word in text_lower for word in ['uncertain', 'undecided', 'hasn\'t decided']):
        family_planning_attitudes = 'uncertain'
    else:
        family_planning_attitudes = 'uncertain'

    # Infer relationship stability
    if any(word in text_lower for word in ['stable', 'strong relationship', 'very supportive', 'secure']):
        relationship_stability = 5
    elif any(word in text_lower for word in ['supportive', 'good relationship']):
        relationship_stability = 4
    elif any(word in text_lower for word in ['married', 'partnered']):
        relationship_stability = 3
    elif any(word in text_lower for word in ['dating', 'single']):
        relationship_stability = 2
    else:
        relationship_stability = 3

    # Infer financial stress
    if any(word in text_lower for word in ['wealthy', 'affluent', 'no financial stress']):
        financial_stress = 1  # Very low
    elif any(word in text_lower for word in ['comfortable', 'stable financially', 'secure']):
        financial_stress = 2
    elif any(word in text_lower for word in ['middle income', 'moderate', 'balanced budget']):
        financial_stress = 3
    elif any(word in text_lower for word in ['struggling', 'paycheck to paycheck', 'financial strain']):
        financial_stress = 4
    elif any(word in text_lower for word in ['very poor', 'destitute', 'severe financial stress']):
        financial_stress = 5
    else:
        financial_stress = 3

    # Infer substance use
    if any(word in text_lower for word in ['drug use', 'heroin', 'cocaine', 'methamphetamine', 'opioid addiction']):
        substance_use = 'significant'
    elif any(word in text_lower for word in ['marijuana', 'cannabis', 'occasional drug use']):
        substance_use = 'moderate'
    elif any(word in text_lower for word in ['experimented', 'tried']):
        substance_use = 'minimal'
    else:
        substance_use = 'none'

    # Infer nutrition awareness
    if any(word in text_lower for word in ['nutritionist', 'nutrition expert', 'strict diet', 'organic food']):
        nutrition_awareness = 5
    elif any(word in text_lower for word in ['health-conscious', 'healthy diet', 'balanced diet']):
        nutrition_awareness = 4
    elif any(word in text_lower for word in ['tries to eat well', 'some attention']):
        nutrition_awareness = 3
    elif any(word in text_lower for word in ['fast food', 'junk food', 'doesn\'t cook']):
        nutrition_awareness = 2
    elif any(word in text_lower for word in ['poor diet', 'very unhealthy eating']):
        nutrition_awareness = 1
    else:
        nutrition_awareness = 3

    # Sleep quality
    if any(word in text_lower for word in ['excellent sleep', 'well-rested', 'sleeps well']):
        sleep_quality = 5
    elif any(word in text_lower for word in ['good sleep', 'adequate rest']):
        sleep_quality = 4
    elif any(word in text_lower for word in ['average sleep', 'manages']):
        sleep_quality = 3
    elif any(word in text_lower for word in ['poor sleep', 'sleep issues', 'insomnia']):
        sleep_quality = 2
    elif any(word in text_lower for word in ['severe sleep issues', 'chronic insomnia']):
        sleep_quality = 1
    else:
        sleep_quality = 3

    # Build the semantic tree
    semantic_tree = PersonaSemanticTree(
        persona_id=persona_id,

        demographics=DemographicsNode(
            age=basic_data['age'],
            gender='female',
            location_type=location_type,
            ethnicity=None,  # Not extracted from text
            language_primary='English'
        ),

        socioeconomic=SocioeconomicNode(
            education_level=basic_data['education'],
            income_bracket=basic_data['income_level'],
            occupation_category=occupation_category,
            employment_status=employment_status,
            insurance_status=insurance_status
        ),

        health_profile=HealthProfileNode(
            health_consciousness=health_consciousness,
            healthcare_access=healthcare_access,
            pregnancy_readiness=pregnancy_readiness,
            reported_health_conditions=health_conditions,
            medication_history=[],  # Not specifically extracted, inferred from conditions
            allergies=[],  # Not extracted from text
            surgery_history=[],  # Not extracted from text
            reproductive_history=None,  # Could be inferred but not explicitly extracted
            family_medical_history=[]
        ),

        behavioral=BehavioralNode(
            physical_activity_level=physical_activity_level,
            nutrition_awareness=nutrition_awareness,
            smoking_status=smoking_status,
            alcohol_consumption=alcohol_consumption,
            substance_use=substance_use,
            sleep_quality=sleep_quality
        ),

        psychosocial=PsychosocialNode(
            mental_health_status=mental_health_status,
            stress_level=stress_level,
            social_support=social_support,
            marital_status=basic_data['marital_status'],
            relationship_stability=relationship_stability,
            financial_stress=financial_stress,
            family_planning_attitudes=family_planning_attitudes
        )
    )

    return semantic_tree


def parse_single_persona(text: str, persona_id: int) -> Dict[str, Any] | None:
    """Parse a single persona text into structured format with semantic tree."""
    import re

    # Extract age
    age_match = re.search(r'(\d+)-year-old', text)
    if not age_match:
        age_match = re.search(r'age[:\s]+(\d+)', text, re.IGNORECASE)

    age = int(age_match.group(1)) if age_match else random.randint(18, 45)

    # Extract name (usually first word or two)
    name_match = re.search(r'^([A-Z][a-z]+)\s+(?:is|works|lives)', text)
    name = name_match.group(1) if name_match else f"Person{persona_id}"

    # Infer education
    text_lower = text.lower()
    if 'doctorate' in text_lower or 'phd' in text_lower or 'ph.d' in text_lower:
        education = 'doctorate'
    elif 'master' in text_lower or "master's" in text_lower:
        education = 'masters'
    elif 'bachelor' in text_lower or "bachelor's" in text_lower or 'college degree' in text_lower:
        education = 'bachelors'
    elif 'high school' in text_lower:
        education = 'high_school'
    elif 'no degree' in text_lower or 'dropped out' in text_lower:
        education = 'no_degree'
    else:
        education = 'unknown'

    # Infer income
    if any(word in text_lower for word in ['wealthy', 'affluent', 'high income', 'executive', 'luxury']):
        income_level = 'high'
    elif any(word in text_lower for word in ['upper-middle', 'upper middle', 'professional', 'well-paid']):
        income_level = 'upper_middle'
    elif any(word in text_lower for word in ['middle income', 'middle-income', 'moderate income', 'average income']):
        income_level = 'middle'
    elif any(word in text_lower for word in ['lower-middle', 'lower middle', 'working class', 'modest income']):
        income_level = 'lower_middle'
    elif any(word in text_lower for word in ['low income', 'low-income', 'struggling', 'paycheck to paycheck']):
        income_level = 'low'
    else:
        income_level = 'middle'  # Default

    # Infer marital status
    if 'married' in text_lower:
        marital_status = 'married'
    elif any(word in text_lower for word in ['single', 'unmarried', 'never married']):
        marital_status = 'single'
    elif any(word in text_lower for word in ['partner', 'partnered', 'domestic partnership', 'long-term relationship']):
        marital_status = 'partnered'
    elif any(word in text_lower for word in ['divorced', 'separated']):
        marital_status = 'divorced'
    elif 'widowed' in text_lower:
        marital_status = 'widowed'
    else:
        marital_status = 'unknown'

    # Extract occupation (look for common patterns)
    occupation_match = re.search(r'(?:works as|employed as|job as a|is a|occupation:|works at)\s+(?:a|an)?\s*([a-z\s]+?)(?:\.|,|at|in|and|with)', text_lower)
    occupation = occupation_match.group(1).strip() if occupation_match else 'unknown'

    # Build basic data dict for tree construction
    basic_data = {
        'age': age,
        'education': education,
        'income_level': income_level,
        'marital_status': marital_status,
        'occupation': occupation
    }

    # Build semantic tree
    try:
        semantic_tree = build_semantic_tree_for_persona(text, persona_id, basic_data)
    except Exception as e:
        logger.warning(f"Failed to build semantic tree for persona {persona_id}: {e}")
        semantic_tree = None

    return {
        'id': persona_id,
        'name': name,
        'age': age,
        'gender': 'female',
        'description': text.strip(),
        'education': education,
        'occupation': occupation,
        'marital_status': marital_status,
        'income_level': income_level,
        'semantic_tree': semantic_tree.to_dict() if semantic_tree else None,
        'raw_data': {'generated': True, 'timestamp': dt.now().isoformat()}
    }


def generate_personas(target_count: int, batch_size: int = 100) -> List[Dict[str, Any]]:
    """Generate target number of personas."""
    logger.info(f"=== Generating {target_count} Synthetic Personas ===")

    # Load config
    config = load_config()

    # Initialize generator
    generator = PersonaGenerator(config)

    all_personas = []
    batches_needed = (target_count + batch_size - 1) // batch_size

    for batch_num in range(batches_needed):
        personas_needed = min(batch_size, target_count - len(all_personas))
        logger.info(f"[Batch {batch_num + 1}/{batches_needed}] Generating {personas_needed} personas...")

        try:
            # Generate batch
            generated_text = generator.generate_batch(personas_needed, batch_size)

            # Parse personas
            batch_personas = parse_generated_personas(generated_text, len(all_personas) + 1)

            # Filter for valid personas (age 12-60, female)
            valid_personas = [
                p for p in batch_personas
                if p['age'] >= 12 and p['age'] <= 60 and p['gender'] == 'female'
            ]

            all_personas.extend(valid_personas)
            logger.info(f"  ✅ Generated {len(valid_personas)} valid personas (total: {len(all_personas)})")

            if len(all_personas) >= target_count:
                break

        except Exception as e:
            logger.error(f"  ❌ Batch {batch_num + 1} failed: {e}")
            continue

    return all_personas[:target_count]


def save_personas(personas: List[Dict[str, Any]], output_path: str):
    """Save personas to JSON file with semantic tree information."""
    output_file = Path(output_path) / "personas.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(personas, f, indent=2, ensure_ascii=False)

    logger.info(f"✅ Saved {len(personas)} personas to {output_file}")

    # Save summary statistics
    summary_file = Path(output_path) / "personas_summary.json"
    summary = {
        'total_count': len(personas),
        'generation_method': 'AI-generated (Claude) with Semantic Trees',
        'semantic_trees_included': True,
        'age_distribution': {},
        'education_distribution': {},
        'marital_status_distribution': {},
        'income_distribution': {},
        'semantic_tree_statistics': {
            'health_consciousness_distribution': {},
            'healthcare_access_distribution': {},
            'pregnancy_readiness_distribution': {},
            'social_support_distribution': {},
            'mental_health_status_distribution': {},
            'physical_activity_distribution': {},
            'smoking_status_distribution': {},
            'alcohol_consumption_distribution': {},
            'employment_status_distribution': {},
            'insurance_status_distribution': {},
            'with_health_conditions_count': 0
        }
    }

    # Calculate distributions
    for persona in personas:
        age_bracket = f"{(persona['age'] // 10) * 10}-{(persona['age'] // 10) * 10 + 9}"
        summary['age_distribution'][age_bracket] = summary['age_distribution'].get(age_bracket, 0) + 1
        summary['education_distribution'][persona['education']] = summary['education_distribution'].get(persona['education'], 0) + 1
        summary['marital_status_distribution'][persona['marital_status']] = summary['marital_status_distribution'].get(persona['marital_status'], 0) + 1
        summary['income_distribution'][persona['income_level']] = summary['income_distribution'].get(persona['income_level'], 0) + 1

        # Add semantic tree statistics if available
        if persona.get('semantic_tree'):
            tree = persona['semantic_tree']

            # Health dimensions
            hc = tree.get('health_profile', {}).get('health_consciousness', 0)
            summary['semantic_tree_statistics']['health_consciousness_distribution'][hc] = \
                summary['semantic_tree_statistics']['health_consciousness_distribution'].get(hc, 0) + 1

            ha = tree.get('health_profile', {}).get('healthcare_access', 0)
            summary['semantic_tree_statistics']['healthcare_access_distribution'][ha] = \
                summary['semantic_tree_statistics']['healthcare_access_distribution'].get(ha, 0) + 1

            pr = tree.get('health_profile', {}).get('pregnancy_readiness', 0)
            summary['semantic_tree_statistics']['pregnancy_readiness_distribution'][pr] = \
                summary['semantic_tree_statistics']['pregnancy_readiness_distribution'].get(pr, 0) + 1

            ss = tree.get('psychosocial', {}).get('social_support', 0)
            summary['semantic_tree_statistics']['social_support_distribution'][ss] = \
                summary['semantic_tree_statistics']['social_support_distribution'].get(ss, 0) + 1

            mh = tree.get('psychosocial', {}).get('mental_health_status', 0)
            summary['semantic_tree_statistics']['mental_health_status_distribution'][mh] = \
                summary['semantic_tree_statistics']['mental_health_status_distribution'].get(mh, 0) + 1

            pa = tree.get('behavioral', {}).get('physical_activity_level', 0)
            summary['semantic_tree_statistics']['physical_activity_distribution'][pa] = \
                summary['semantic_tree_statistics']['physical_activity_distribution'].get(pa, 0) + 1

            # Categorical
            smoking = tree.get('behavioral', {}).get('smoking_status', 'unknown')
            summary['semantic_tree_statistics']['smoking_status_distribution'][smoking] = \
                summary['semantic_tree_statistics']['smoking_status_distribution'].get(smoking, 0) + 1

            alcohol = tree.get('behavioral', {}).get('alcohol_consumption', 'unknown')
            summary['semantic_tree_statistics']['alcohol_consumption_distribution'][alcohol] = \
                summary['semantic_tree_statistics']['alcohol_consumption_distribution'].get(alcohol, 0) + 1

            employment = tree.get('socioeconomic', {}).get('employment_status', 'unknown')
            summary['semantic_tree_statistics']['employment_status_distribution'][employment] = \
                summary['semantic_tree_statistics']['employment_status_distribution'].get(employment, 0) + 1

            insurance = tree.get('socioeconomic', {}).get('insurance_status', 'unknown')
            summary['semantic_tree_statistics']['insurance_status_distribution'][insurance] = \
                summary['semantic_tree_statistics']['insurance_status_distribution'].get(insurance, 0) + 1

            # Health conditions
            conditions = tree.get('health_profile', {}).get('reported_health_conditions', [])
            if conditions:
                summary['semantic_tree_statistics']['with_health_conditions_count'] += 1

    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    logger.info(f"✅ Saved summary statistics to {summary_file}")

    # Log semantic tree summary
    logger.info("=" * 60)
    logger.info("SEMANTIC TREE GENERATION SUMMARY")
    logger.info("=" * 60)
    if summary['semantic_tree_statistics']['health_consciousness_distribution']:
        logger.info(f"Health Consciousness distribution: {summary['semantic_tree_statistics']['health_consciousness_distribution']}")
        logger.info(f"Healthcare Access distribution: {summary['semantic_tree_statistics']['healthcare_access_distribution']}")
        logger.info(f"Pregnancy Readiness distribution: {summary['semantic_tree_statistics']['pregnancy_readiness_distribution']}")
        logger.info(f"Personas with health conditions: {summary['semantic_tree_statistics']['with_health_conditions_count']}")
    logger.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Generate synthetic personas using AI')
    parser.add_argument('--count', type=int, default=20000, help='Number of personas to generate')
    parser.add_argument('--output', type=str, default='data/personas', help='Output directory')
    parser.add_argument('--batch-size', type=int, default=100, help='Personas per API call')
    args = parser.parse_args()

    logger.info("=== Synthetic Persona Generation Started ===")
    logger.info(f"Target: {args.count} personas")
    logger.info(f"Batch size: {args.batch_size}")

    try:
        # Generate personas
        personas = generate_personas(args.count, args.batch_size)

        if len(personas) < args.count:
            logger.warning(f"Generated {len(personas)} personas, target was {args.count}")

        # Save results
        save_personas(personas, args.output)

        logger.info(f"[SUCCESS] Generated {len(personas)} personas")
        logger.info("=== Persona Generation Completed ===")

    except Exception as e:
        logger.error(f"Script failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
