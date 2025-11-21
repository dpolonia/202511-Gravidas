"""
Risk Factor Extraction Module
===============================

Identifies pregnancy risk factors automatically from interview transcripts.
Provides clinical risk stratification, alerts, and decision support information.

⚠️ MEDICAL DISCLAIMER:
This module is for RESEARCH and SCREENING purposes only. It does NOT replace
clinical judgment or medical assessment. All risk assessments should be validated
by qualified healthcare professionals.

Capability #11 of 11 Advanced NLP Enhancements
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict, Counter
import numpy as np

logger = logging.getLogger(__name__)

# Try to import transformers for BioBERT/ClinicalBERT
try:
    from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
    import torch
    TRANSFORMERS_AVAILABLE = True
    logger.info("✓ Transformers available for clinical NER")
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not available. Using pattern-based risk extraction.")

# Clinical Risk Factor Categories
PREGNANCY_RISK_FACTORS = {
    # Maternal demographic/social risk factors
    'demographic': {
        'advanced_maternal_age': {
            'patterns': [r'\b(35|36|37|38|39|40|41|42|43|44|45)\s*years?\s*old',
                        r'\bolder (mother|mom|pregnancy)'],
            'keywords': ['35 years', '40 years', 'advanced age', 'older mother'],
            'severity': 'moderate',
            'weight': 1.2
        },
        'young_maternal_age': {
            'patterns': [r'\b(15|16|17|18|19)\s*years?\s*old',
                        r'\bteenage (pregnancy|mother)'],
            'keywords': ['teenage', 'young mother', '17 years'],
            'severity': 'moderate',
            'weight': 1.1
        },
        'low_socioeconomic': {
            'patterns': [r'\bcan\'?t afford', r'\bno insurance', r'\bunemployed'],
            'keywords': ['financial stress', 'no insurance', 'can\'t afford', 'poverty'],
            'severity': 'moderate',
            'weight': 0.9
        },
        'poor_social_support': {
            'patterns': [r'\bno (support|help|family)', r'\balone', r'\bisolated'],
            'keywords': ['alone', 'isolated', 'no support', 'no family'],
            'severity': 'moderate',
            'weight': 1.0
        }
    },

    # Medical history risk factors
    'medical_history': {
        'previous_preterm_birth': {
            'patterns': [r'\bprevious preterm', r'\bearly delivery before', r'\bborn early'],
            'keywords': ['previous preterm', 'premature birth history', 'early delivery'],
            'severity': 'high',
            'weight': 2.0
        },
        'previous_pregnancy_loss': {
            'patterns': [r'\bmiscarriage', r'\bstillbirth', r'\blost (a )?bab(y|ies)',
                        r'\bpregnancy loss'],
            'keywords': ['miscarriage', 'stillbirth', 'pregnancy loss', 'lost baby'],
            'severity': 'moderate',
            'weight': 1.3
        },
        'previous_cesarean': {
            'patterns': [r'\bprevious c-?section', r'\bhad (a )?cesarean'],
            'keywords': ['previous cesarean', 'c-section', 'prior surgery'],
            'severity': 'moderate',
            'weight': 1.1
        },
        'chronic_hypertension': {
            'patterns': [r'\bhigh blood pressure', r'\bhypertension', r'\bBP (high|elevated)'],
            'keywords': ['hypertension', 'high blood pressure', 'chronic BP'],
            'severity': 'high',
            'weight': 1.8
        },
        'diabetes_preexisting': {
            'patterns': [r'\btype [12] diabetes', r'\bdiabetic (before|prior to) pregnancy'],
            'keywords': ['type 1 diabetes', 'type 2 diabetes', 'preexisting diabetes'],
            'severity': 'high',
            'weight': 1.9
        },
        'thyroid_disorder': {
            'patterns': [r'\bhypothyroid', r'\bhyperthyroid', r'\bthyroid (disease|disorder|problem)'],
            'keywords': ['hypothyroid', 'hyperthyroid', 'thyroid disease'],
            'severity': 'moderate',
            'weight': 1.2
        },
        'autoimmune_disease': {
            'patterns': [r'\blupus', r'\brheumatoid arthritis', r'\bautoimmune'],
            'keywords': ['lupus', 'autoimmune', 'rheumatoid arthritis'],
            'severity': 'high',
            'weight': 1.7
        }
    },

    # Current pregnancy complications
    'pregnancy_complications': {
        'gestational_diabetes': {
            'patterns': [r'\bgestational diabetes', r'\bGDM', r'\bblood sugar (high|elevated)',
                        r'\bglucose (test|screening) (failed|abnormal)'],
            'keywords': ['gestational diabetes', 'GDM', 'high blood sugar'],
            'severity': 'high',
            'weight': 1.8
        },
        'preeclampsia': {
            'patterns': [r'\bpreeclampsia', r'\bhigh blood pressure (and|with) protein',
                        r'\bPIH'],
            'keywords': ['preeclampsia', 'pregnancy-induced hypertension', 'PIH'],
            'severity': 'critical',
            'weight': 2.5
        },
        'placenta_previa': {
            'patterns': [r'\bplacenta previa', r'\bplacenta (covering|blocking)'],
            'keywords': ['placenta previa', 'low-lying placenta'],
            'severity': 'high',
            'weight': 2.0
        },
        'placental_abruption': {
            'patterns': [r'\bplacental abruption', r'\bplacenta (detached|separated)'],
            'keywords': ['placental abruption', 'placenta detached'],
            'severity': 'critical',
            'weight': 2.8
        },
        'intrauterine_growth_restriction': {
            'patterns': [r'\bIUGR', r'\bgrowth restriction', r'\bbaby (too )?small',
                        r'\bgrowth (behind|slow)'],
            'keywords': ['IUGR', 'growth restriction', 'small baby', 'growth delay'],
            'severity': 'high',
            'weight': 2.0
        },
        'preterm_labor': {
            'patterns': [r'\bpreterm labor', r'\bearly labor', r'\bcontractions before',
                        r'\bcervix (dilating|opening) early'],
            'keywords': ['preterm labor', 'early contractions', 'premature labor'],
            'severity': 'critical',
            'weight': 2.3
        },
        'multiple_gestation': {
            'patterns': [r'\btwins', r'\btriplets', r'\bmultiples', r'\bmore than one baby'],
            'keywords': ['twins', 'triplets', 'multiple gestation', 'multiples'],
            'severity': 'high',
            'weight': 1.8
        }
    },

    # Behavioral/lifestyle risk factors
    'lifestyle': {
        'smoking': {
            'patterns': [r'\bsmok(e|ing)', r'\bcigarettes?', r'\btobacco'],
            'keywords': ['smoking', 'cigarettes', 'tobacco', 'vaping'],
            'severity': 'high',
            'weight': 1.9
        },
        'alcohol_use': {
            'patterns': [r'\bdrink(ing)? (alcohol|wine|beer)', r'\balcohol'],
            'keywords': ['drinking', 'alcohol', 'wine', 'beer'],
            'severity': 'high',
            'weight': 2.0
        },
        'substance_use': {
            'patterns': [r'\bdrug (use|abuse)', r'\bsubstance (use|abuse)',
                        r'\b(marijuana|cocaine|opioids)'],
            'keywords': ['drug use', 'substance abuse', 'marijuana', 'opioids'],
            'severity': 'critical',
            'weight': 2.5
        },
        'inadequate_nutrition': {
            'patterns': [r'\bnot eating (enough|well)', r'\bskipping meals',
                        r'\bmalnutrition'],
            'keywords': ['not eating', 'poor nutrition', 'skipping meals'],
            'severity': 'moderate',
            'weight': 1.3
        },
        'obesity': {
            'patterns': [r'\bobese', r'\bBMI (over|above) (30|35|40)',
                        r'\bsignificant(ly)? overweight'],
            'keywords': ['obesity', 'BMI over 30', 'significantly overweight'],
            'severity': 'high',
            'weight': 1.6
        }
    },

    # Mental health risk factors
    'mental_health': {
        'depression': {
            'patterns': [r'\bdepression', r'\bdepressed', r'\bsuicidal'],
            'keywords': ['depression', 'depressed', 'severe sadness'],
            'severity': 'high',
            'weight': 1.7
        },
        'anxiety': {
            'patterns': [r'\bsevere anxiety', r'\bpanic attacks', r'\boverwhelming (worry|stress)'],
            'keywords': ['severe anxiety', 'panic attacks', 'extreme stress'],
            'severity': 'moderate',
            'weight': 1.4
        },
        'domestic_violence': {
            'patterns': [r'\babuse(d)?', r'\bdomestic violence', r'\bunsafe (at )?home',
                        r'\bpartner (hits|hurts)'],
            'keywords': ['abuse', 'domestic violence', 'unsafe home', 'violence'],
            'severity': 'critical',
            'weight': 2.8
        }
    },

    # Inadequate prenatal care
    'prenatal_care': {
        'late_prenatal_care': {
            'patterns': [r'\bfirst (visit|appointment) (at|in) (third|3rd) trimester',
                        r'\blate (to )?prenatal care', r'\bno prenatal care'],
            'keywords': ['late prenatal care', 'no prenatal care', 'missed appointments'],
            'severity': 'high',
            'weight': 1.8
        },
        'missed_appointments': {
            'patterns': [r'\bmissed (many|several|multiple) appointments',
                        r'\bnot attending (appointments|visits)'],
            'keywords': ['missed appointments', 'no follow-up', 'skipped visits'],
            'severity': 'moderate',
            'weight': 1.3
        }
    }
}

# Risk severity weights
SEVERITY_WEIGHTS = {
    'critical': 3.0,
    'high': 2.0,
    'moderate': 1.0,
    'low': 0.5
}


def extract_risk_factors(text: str, context: str = 'pregnancy') -> Dict[str, Any]:
    """
    Extract pregnancy risk factors from text.

    Args:
        text: Interview transcript or clinical note
        context: 'pregnancy', 'antepartum', 'postpartum'

    Returns:
        Dictionary with extracted risk factors:
        {
            'risk_factors': {
                'gestational_diabetes': {
                    'category': 'pregnancy_complications',
                    'severity': 'high',
                    'confidence': 0.85,
                    'evidence': ['blood sugar high', ...]
                },
                ...
            },
            'risk_score': 12.5,
            'risk_level': 'high',
            'critical_alerts': [...],
            'num_risk_factors': 3
        }
    """
    text_lower = text.lower()

    detected_risks = {}
    total_risk_score = 0.0

    # Scan through all risk factor categories
    for category, risk_factors in PREGNANCY_RISK_FACTORS.items():
        for risk_name, risk_data in risk_factors.items():
            matches = []
            confidence = 0.0

            # Check patterns
            for pattern in risk_data.get('patterns', []):
                if re.search(pattern, text_lower):
                    matches.append(f"pattern:{pattern[:40]}...")
                    confidence += 0.3

            # Check keywords
            for keyword in risk_data.get('keywords', []):
                if keyword in text_lower:
                    matches.append(f"keyword:{keyword}")
                    confidence += 0.2

            # If risk factor detected
            if matches:
                confidence = min(confidence, 1.0)
                severity = risk_data.get('severity', 'moderate')
                weight = risk_data.get('weight', 1.0)

                # Calculate risk contribution
                risk_contribution = confidence * weight * SEVERITY_WEIGHTS[severity]

                detected_risks[risk_name] = {
                    'category': category,
                    'severity': severity,
                    'confidence': float(confidence),
                    'evidence': matches[:5],  # Top 5 evidence items
                    'risk_contribution': float(risk_contribution)
                }

                total_risk_score += risk_contribution

    # Identify critical alerts
    critical_alerts = [
        risk_name for risk_name, data in detected_risks.items()
        if data['severity'] == 'critical'
    ]

    # Determine overall risk level
    if total_risk_score >= 15.0 or len(critical_alerts) > 0:
        risk_level = 'critical'
    elif total_risk_score >= 10.0:
        risk_level = 'high'
    elif total_risk_score >= 5.0:
        risk_level = 'moderate'
    else:
        risk_level = 'low'

    return {
        'risk_factors': detected_risks,
        'risk_score': float(total_risk_score),
        'risk_level': risk_level,
        'critical_alerts': critical_alerts,
        'num_risk_factors': len(detected_risks),
        'risk_by_category': _group_risks_by_category(detected_risks),
        'extraction_method': 'pattern-based'
    }


def analyze_clinical_risk(interview_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comprehensive clinical risk analysis of an interview.

    Args:
        interview_data: Interview dictionary with 'transcript' field

    Returns:
        Complete clinical risk assessment
    """
    # Extract full interview text
    transcript = interview_data.get('transcript', [])

    if isinstance(transcript, list):
        full_text = ' '.join([turn.get('text', '') for turn in transcript])
    else:
        full_text = str(transcript)

    # Extract risk factors
    risk_analysis = extract_risk_factors(full_text, context='pregnancy')

    # Generate clinical recommendations
    recommendations = _generate_clinical_recommendations(risk_analysis)

    # Calculate risk stratification
    stratification = _stratify_risk(risk_analysis)

    # Generate risk summary
    summary = _generate_risk_summary(risk_analysis)

    return {
        'risk_analysis': risk_analysis,
        'recommendations': recommendations,
        'stratification': stratification,
        'summary': summary,
        'requires_immediate_attention': (
            risk_analysis['risk_level'] == 'critical' or
            len(risk_analysis['critical_alerts']) > 0
        ),
        'disclaimer': 'Risk assessment for research purposes only. Clinical validation required.'
    }


def track_risk_trajectory(risk_assessments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Track risk factors over multiple timepoints.

    Args:
        risk_assessments: List of risk assessments over time

    Returns:
        Longitudinal risk analysis
    """
    if not risk_assessments:
        return {'error': 'No risk assessments provided'}

    # Track risk scores over time
    risk_scores = []
    risk_levels = []
    all_risk_factors = set()

    for assessment in risk_assessments:
        risk_analysis = assessment.get('risk_analysis', {})
        risk_scores.append(risk_analysis.get('risk_score', 0.0))
        risk_levels.append(risk_analysis.get('risk_level', 'low'))

        # Collect all risk factors
        for risk_name in risk_analysis.get('risk_factors', {}).keys():
            all_risk_factors.add(risk_name)

    # Track each risk factor's presence over time
    risk_factor_timeline = {}
    for risk_name in all_risk_factors:
        timeline = []
        for assessment in risk_assessments:
            risk_analysis = assessment.get('risk_analysis', {})
            present = risk_name in risk_analysis.get('risk_factors', {})
            timeline.append(present)
        risk_factor_timeline[risk_name] = timeline

    # Calculate trends
    risk_trend = _calculate_risk_trend(risk_scores)

    # Identify new, resolved, and persistent risks
    new_risks = _identify_new_risks(risk_factor_timeline)
    resolved_risks = _identify_resolved_risks(risk_factor_timeline)
    persistent_risks = _identify_persistent_risks(risk_factor_timeline)

    return {
        'num_assessments': len(risk_assessments),
        'risk_scores': risk_scores,
        'risk_levels': risk_levels,
        'risk_trend': risk_trend,
        'trend_direction': _categorize_trend(risk_trend),
        'new_risks': new_risks,
        'resolved_risks': resolved_risks,
        'persistent_risks': persistent_risks,
        'current_risk_score': risk_scores[-1] if risk_scores else 0.0,
        'peak_risk_score': max(risk_scores) if risk_scores else 0.0,
        'risk_factor_timeline': risk_factor_timeline
    }


def calculate_combined_risk_score(risk_factors: Dict[str, Any],
                                  modifiers: Optional[Dict[str, float]] = None) -> float:
    """
    Calculate combined risk score with optional modifiers.

    Args:
        risk_factors: Dictionary of detected risk factors
        modifiers: Optional risk modifiers (e.g., {'protective_factors': -2.0})

    Returns:
        Combined risk score
    """
    base_score = sum(rf['risk_contribution'] for rf in risk_factors.values())

    if modifiers:
        for modifier, value in modifiers.items():
            base_score += value

    return max(0.0, float(base_score))


def compare_risk_profiles(interviews: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compare risk profiles across multiple interviews.

    Args:
        interviews: List of interview dictionaries

    Returns:
        Comparative risk analysis
    """
    if not interviews:
        return {'error': 'No interviews provided'}

    all_risk_analyses = []
    risk_score_distribution = []
    risk_level_counts = Counter()
    all_detected_risks = Counter()

    for interview in interviews:
        analysis = analyze_clinical_risk(interview)
        risk_analysis = analysis['risk_analysis']

        all_risk_analyses.append(risk_analysis)
        risk_score_distribution.append(risk_analysis['risk_score'])
        risk_level_counts[risk_analysis['risk_level']] += 1

        # Count all risk factors
        for risk_name in risk_analysis['risk_factors'].keys():
            all_detected_risks[risk_name] += 1

    return {
        'num_interviews': len(interviews),
        'average_risk_score': float(np.mean(risk_score_distribution)),
        'risk_score_range': {
            'min': float(min(risk_score_distribution)),
            'max': float(max(risk_score_distribution)),
            'std': float(np.std(risk_score_distribution))
        },
        'risk_level_distribution': dict(risk_level_counts),
        'most_common_risks': all_detected_risks.most_common(10),
        'high_risk_percentage': (
            (risk_level_counts['high'] + risk_level_counts['critical']) /
            len(interviews) * 100
        ) if interviews else 0.0
    }


# Helper functions

def _group_risks_by_category(risk_factors: Dict[str, Any]) -> Dict[str, List[str]]:
    """Group risk factors by category."""
    grouped = defaultdict(list)

    for risk_name, risk_data in risk_factors.items():
        category = risk_data['category']
        grouped[category].append(risk_name)

    return dict(grouped)


def _generate_clinical_recommendations(risk_analysis: Dict[str, Any]) -> List[str]:
    """Generate clinical recommendations based on risk factors."""
    recommendations = []

    risk_factors = risk_analysis.get('risk_factors', {})
    risk_level = risk_analysis.get('risk_level', 'low')

    # General recommendations
    if risk_level in ['critical', 'high']:
        recommendations.append('Increased prenatal visit frequency recommended')
        recommendations.append('Consider maternal-fetal medicine consultation')

    # Specific recommendations by risk factor
    if 'gestational_diabetes' in risk_factors:
        recommendations.append('Blood glucose monitoring and dietary counseling required')

    if 'preeclampsia' in risk_factors:
        recommendations.append('Close blood pressure monitoring and protein assessment')
        recommendations.append('Educate on warning signs (headache, visual changes)')

    if 'preterm_labor' in risk_factors:
        recommendations.append('Assess cervical length, consider tocolytics if indicated')

    if 'depression' in risk_factors or 'anxiety' in risk_factors:
        recommendations.append('Mental health screening and support services')

    if 'smoking' in risk_factors or 'substance_use' in risk_factors:
        recommendations.append('Substance use counseling and cessation support')

    if 'domestic_violence' in risk_factors:
        recommendations.append('Safety assessment and social work consultation URGENT')

    if not recommendations:
        recommendations.append('Continue routine prenatal care')

    return recommendations


def _stratify_risk(risk_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Stratify patient into risk categories."""
    risk_score = risk_analysis.get('risk_score', 0.0)
    risk_level = risk_analysis.get('risk_level', 'low')
    critical_alerts = risk_analysis.get('critical_alerts', [])

    # Determine care level
    if critical_alerts or risk_level == 'critical':
        care_level = 'high_risk_specialist'
        visit_frequency = 'weekly_or_more'
    elif risk_level == 'high':
        care_level = 'high_risk'
        visit_frequency = 'biweekly'
    elif risk_level == 'moderate':
        care_level = 'moderate_risk'
        visit_frequency = 'every_3_weeks'
    else:
        care_level = 'low_risk'
        visit_frequency = 'monthly_standard'

    return {
        'risk_stratification': care_level,
        'recommended_visit_frequency': visit_frequency,
        'specialist_referral_needed': care_level in ['high_risk_specialist', 'high_risk'],
        'monitoring_intensity': 'intensive' if critical_alerts else 'standard'
    }


def _generate_risk_summary(risk_analysis: Dict[str, Any]) -> str:
    """Generate human-readable risk summary."""
    num_risks = risk_analysis.get('num_risk_factors', 0)
    risk_level = risk_analysis.get('risk_level', 'low')
    critical_alerts = risk_analysis.get('critical_alerts', [])

    summary = f"Risk Level: {risk_level.upper()}. "

    if num_risks == 0:
        summary += "No significant risk factors identified."
    elif num_risks == 1:
        summary += "1 risk factor identified."
    else:
        summary += f"{num_risks} risk factors identified."

    if critical_alerts:
        summary += f" CRITICAL ALERT: {', '.join(critical_alerts).replace('_', ' ')}."

    risk_by_category = risk_analysis.get('risk_by_category', {})
    if risk_by_category:
        categories = list(risk_by_category.keys())
        summary += f" Risk factors in: {', '.join(categories).replace('_', ' ')}."

    return summary


def _calculate_risk_trend(risk_scores: List[float]) -> float:
    """Calculate risk trend over time."""
    if len(risk_scores) < 2:
        return 0.0

    x = np.arange(len(risk_scores))
    y = np.array(risk_scores)

    slope = np.polyfit(x, y, 1)[0]

    return float(slope)


def _categorize_trend(trend_value: float) -> str:
    """Categorize risk trend."""
    if trend_value > 0.5:
        return 'increasing'
    elif trend_value < -0.5:
        return 'decreasing'
    else:
        return 'stable'


def _identify_new_risks(timeline: Dict[str, List[bool]]) -> List[str]:
    """Identify newly appeared risk factors."""
    new_risks = []

    for risk_name, presence in timeline.items():
        # New if not present initially but present at end
        if not presence[0] and presence[-1]:
            new_risks.append(risk_name)

    return new_risks


def _identify_resolved_risks(timeline: Dict[str, List[bool]]) -> List[str]:
    """Identify resolved risk factors."""
    resolved = []

    for risk_name, presence in timeline.items():
        # Resolved if present initially but not at end
        if presence[0] and not presence[-1]:
            resolved.append(risk_name)

    return resolved


def _identify_persistent_risks(timeline: Dict[str, List[bool]]) -> List[str]:
    """Identify persistent risk factors."""
    persistent = []

    for risk_name, presence in timeline.items():
        # Persistent if present in all timepoints
        if all(presence):
            persistent.append(risk_name)

    return persistent


def check_installation() -> Dict[str, bool]:
    """Check if required packages are installed."""
    return {
        'transformers': TRANSFORMERS_AVAILABLE,
        'has_risk_extraction': True,  # Pattern-based always available
        'clinical_models_available': False  # Would need BioBERT/ClinicalBERT
    }


if __name__ == '__main__':
    # Test the module
    test_interview = {
        'transcript': [
            {
                'speaker': 'interviewer',
                'text': 'Can you tell me about your pregnancy history?'
            },
            {
                'speaker': 'persona',
                'text': 'I\'m 38 years old and this is my first pregnancy. I have type 2 diabetes that I\'ve had for 5 years. I\'ve also been diagnosed with gestational diabetes during this pregnancy and my blood sugar has been high.'
            },
            {
                'speaker': 'interviewer',
                'text': 'I see. Are there any other concerns?'
            },
            {
                'speaker': 'persona',
                'text': 'I\'ve been feeling really depressed and anxious. I also smoke about 5 cigarettes a day, though I\'ve been trying to quit. I don\'t have much family support - I\'m pretty isolated.'
            },
            {
                'speaker': 'interviewer',
                'text': 'Thank you for sharing that. We\'ll make sure to address these concerns.'
            }
        ]
    }

    print("Risk Factor Extraction Module Test")
    print("=" * 50)

    # Check installation
    status = check_installation()
    print(f"Risk extraction available: {status['has_risk_extraction']}")
    print(f"Transformers available: {status['transformers']}")
    print()

    # Analyze clinical risk
    print("Analyzing test interview for risk factors...")
    result = analyze_clinical_risk(test_interview)

    risk = result['risk_analysis']
    print(f"\nRISK ASSESSMENT:")
    print(f"  Overall Risk Score: {risk['risk_score']:.1f}")
    print(f"  Risk Level: {risk['risk_level'].upper()}")
    print(f"  Number of Risk Factors: {risk['num_risk_factors']}")

    if risk['critical_alerts']:
        print(f"  ⚠️ CRITICAL ALERTS: {', '.join(risk['critical_alerts'])}")

    print(f"\nIDENTIFIED RISK FACTORS:")
    for risk_name, risk_data in risk['risk_factors'].items():
        print(f"  - {risk_name.replace('_', ' ').title()}")
        print(f"    Category: {risk_data['category']}")
        print(f"    Severity: {risk_data['severity']}")
        print(f"    Confidence: {risk_data['confidence']:.2f}")

    print(f"\nRISK BY CATEGORY:")
    for category, risks in risk['risk_by_category'].items():
        print(f"  {category.replace('_', ' ').title()}: {len(risks)} risk(s)")

    print(f"\nCLINICAL RECOMMENDATIONS:")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"  {i}. {rec}")

    print(f"\nRISK STRATIFICATION:")
    strat = result['stratification']
    print(f"  Care Level: {strat['risk_stratification']}")
    print(f"  Visit Frequency: {strat['recommended_visit_frequency']}")
    print(f"  Specialist Referral: {strat['specialist_referral_needed']}")

    print(f"\nSUMMARY:")
    print(f"  {result['summary']}")

    print(f"\n⚠️ DISCLAIMER: {result['disclaimer']}")
