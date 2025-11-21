#!/usr/bin/env python3
"""
Journal Selector and Paper Formatter
=====================================

Recommends suitable journals for publication based on research content,
displays journal metadata, and generates papers according to journal guidelines.

Features:
- Journal recommendation based on research topic analysis
- Comprehensive journal metadata (OA, APC, ASJC, ISSN, Q, IF)
- Interactive journal selection
- Journal-specific paper formatting

Usage:
    python scripts/07_journal_selector.py
    python scripts/07_journal_selector.py --report outputs/academic_report.md
    python scripts/07_journal_selector.py --auto-select  # Select top recommendation
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
import re
import requests

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Scopus API configuration
SCOPUS_API_KEY = os.getenv('SCOPUS_API_KEY', '794f87fe4933b144dd95702b217fcb50')
SCOPUS_BASE_URL = "https://api.elsevier.com"

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUTS_DIR = PROJECT_ROOT / 'outputs'


class ScopusClient:
    """Client for Scopus API to fetch journal metrics."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or SCOPUS_API_KEY
        self.headers = {
            'X-ELS-APIKey': self.api_key,
            'Accept': 'application/json'
        }

    def search_journal(self, issn: str) -> Optional[Dict[str, Any]]:
        """Search for journal by ISSN and get metrics."""
        try:
            # Serial Title API for journal info
            url = f"{SCOPUS_BASE_URL}/content/serial/title"
            params = {'issn': issn.replace('-', '')}

            response = requests.get(url, headers=self.headers, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if 'serial-metadata-response' in data:
                    entries = data['serial-metadata-response'].get('entry', [])
                    if entries:
                        return self._parse_journal_entry(entries[0])
            else:
                logger.debug(f"Scopus API returned {response.status_code} for ISSN {issn}")

        except requests.exceptions.RequestException as e:
            logger.debug(f"Scopus API request failed: {e}")

        return None

    def _parse_journal_entry(self, entry: Dict) -> Dict[str, Any]:
        """Parse Scopus journal entry."""
        result = {
            'title': entry.get('dc:title', ''),
            'issn': entry.get('prism:issn', ''),
            'eissn': entry.get('prism:eIssn', ''),
            'publisher': entry.get('dc:publisher', ''),
            'source_id': entry.get('source-id', ''),
        }

        # Get SJR and SNIP metrics
        sjr_list = entry.get('SJRList', {}).get('SJR', [])
        if sjr_list:
            latest_sjr = sjr_list[-1] if isinstance(sjr_list, list) else sjr_list
            result['sjr'] = float(latest_sjr.get('$', 0))
            result['sjr_year'] = latest_sjr.get('@year', '')

        snip_list = entry.get('SNIPList', {}).get('SNIP', [])
        if snip_list:
            latest_snip = snip_list[-1] if isinstance(snip_list, list) else snip_list
            result['snip'] = float(latest_snip.get('$', 0))

        # CiteScore
        citescore_list = entry.get('citeScoreYearInfoList', {}).get('citeScoreYearInfo', [])
        if citescore_list:
            for cs in citescore_list:
                if cs.get('@status') == 'Complete':
                    result['citescore'] = float(cs.get('citeScore', 0))
                    result['citescore_year'] = cs.get('@year', '')
                    break

        # Subject areas (ASJC)
        subject_area = entry.get('subject-area', [])
        if subject_area:
            if isinstance(subject_area, list):
                result['asjc_codes'] = [sa.get('@code', '') for sa in subject_area]
                result['asjc_areas'] = [sa.get('$', '') for sa in subject_area]
            else:
                result['asjc_codes'] = [subject_area.get('@code', '')]
                result['asjc_areas'] = [subject_area.get('$', '')]

        # Open Access status
        result['open_access'] = entry.get('openaccess', '0') == '1'

        return result

    def get_journal_metrics(self, source_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed metrics for a journal by Scopus source ID."""
        try:
            url = f"{SCOPUS_BASE_URL}/content/serial/title/sourceId/{source_id}"

            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if 'serial-metadata-response' in data:
                    entries = data['serial-metadata-response'].get('entry', [])
                    if entries:
                        return self._parse_journal_entry(entries[0])

        except requests.exceptions.RequestException as e:
            logger.debug(f"Scopus metrics request failed: {e}")

        return None

    def enrich_journal(self, journal: 'Journal') -> 'Journal':
        """Enrich journal data with Scopus metrics."""
        scopus_data = self.search_journal(journal.issn)

        if scopus_data:
            # Update with Scopus data if available
            if scopus_data.get('citescore'):
                journal.citescore = scopus_data['citescore']
            if scopus_data.get('asjc_codes'):
                journal.asjc_codes = scopus_data['asjc_codes']
                journal.asjc_areas = scopus_data.get('asjc_areas', journal.asjc_areas)
            if 'open_access' in scopus_data:
                journal.open_access = scopus_data['open_access']

            logger.info(f"  Enriched {journal.name} with Scopus data")

        return journal


@dataclass
class Journal:
    """Journal metadata container."""
    name: str
    issn: str
    eissn: str
    publisher: str
    open_access: bool
    apc_usd: Optional[int]  # Article Processing Charge in USD
    asjc_codes: List[str]  # All Science Journal Classification codes
    asjc_areas: List[str]  # Human-readable ASJC areas
    quartile: str  # Q1, Q2, Q3, Q4
    impact_factor: float
    citescore: float
    h_index: int
    scope: str
    word_limit: Optional[int]
    abstract_limit: int
    keywords_limit: int
    reference_style: str
    sections: List[str]
    url: str
    submission_url: str
    review_time_weeks: int  # Average review time


# Curated database of maternal health journals
JOURNAL_DATABASE = [
    Journal(
        name="BMC Pregnancy and Childbirth",
        issn="1471-2393",
        eissn="1471-2393",
        publisher="BioMed Central (Springer Nature)",
        open_access=True,
        apc_usd=2890,
        asjc_codes=["2729", "2735"],
        asjc_areas=["Obstetrics and Gynecology", "Pediatrics, Perinatology and Child Health"],
        quartile="Q1",
        impact_factor=3.2,
        citescore=5.1,
        h_index=98,
        scope="Research on pregnancy, childbirth, labor, breastfeeding, maternal health, perinatal care",
        word_limit=None,
        abstract_limit=350,
        keywords_limit=10,
        reference_style="Vancouver",
        sections=["Background", "Methods", "Results", "Discussion", "Conclusions"],
        url="https://bmcpregnancychildbirth.biomedcentral.com/",
        submission_url="https://www.editorialmanager.com/bprc/",
        review_time_weeks=8
    ),
    Journal(
        name="Midwifery",
        issn="0266-6138",
        eissn="1532-3099",
        publisher="Elsevier",
        open_access=False,
        apc_usd=3450,  # For OA option
        asjc_codes=["2729", "2911"],
        asjc_areas=["Obstetrics and Gynecology", "Nursing (Midwifery)"],
        quartile="Q1",
        impact_factor=2.8,
        citescore=4.8,
        h_index=89,
        scope="Midwifery care, pregnancy, childbirth, women's health, reproductive health",
        word_limit=5000,
        abstract_limit=250,
        keywords_limit=6,
        reference_style="APA",
        sections=["Introduction", "Methods", "Findings", "Discussion", "Conclusion"],
        url="https://www.journals.elsevier.com/midwifery",
        submission_url="https://www.editorialmanager.com/midi/",
        review_time_weeks=10
    ),
    Journal(
        name="Women and Birth",
        issn="1871-5192",
        eissn="1878-1799",
        publisher="Elsevier",
        open_access=False,
        apc_usd=3200,
        asjc_codes=["2729", "2911"],
        asjc_areas=["Obstetrics and Gynecology", "Nursing (Midwifery)"],
        quartile="Q1",
        impact_factor=2.9,
        citescore=4.5,
        h_index=67,
        scope="Midwifery, maternity care, women's health, pregnancy outcomes",
        word_limit=5000,
        abstract_limit=250,
        keywords_limit=6,
        reference_style="APA",
        sections=["Introduction", "Methods", "Results", "Discussion", "Conclusion"],
        url="https://www.journals.elsevier.com/women-and-birth",
        submission_url="https://www.editorialmanager.com/wombi/",
        review_time_weeks=12
    ),
    Journal(
        name="Journal of Midwifery & Women's Health",
        issn="1526-9523",
        eissn="1542-2011",
        publisher="Wiley",
        open_access=False,
        apc_usd=3800,
        asjc_codes=["2729", "2911"],
        asjc_areas=["Obstetrics and Gynecology", "Nursing (Midwifery)"],
        quartile="Q1",
        impact_factor=2.4,
        citescore=4.2,
        h_index=72,
        scope="Midwifery practice, women's health across lifespan, pregnancy care",
        word_limit=4500,
        abstract_limit=300,
        keywords_limit=5,
        reference_style="AMA",
        sections=["Introduction", "Methods", "Results", "Discussion", "Conclusions"],
        url="https://onlinelibrary.wiley.com/journal/15422011",
        submission_url="https://mc.manuscriptcentral.com/jmwh",
        review_time_weeks=10
    ),
    Journal(
        name="Maternal and Child Health Journal",
        issn="1092-7875",
        eissn="1573-6628",
        publisher="Springer",
        open_access=False,
        apc_usd=3290,
        asjc_codes=["2735", "2729"],
        asjc_areas=["Pediatrics, Perinatology and Child Health", "Obstetrics and Gynecology"],
        quartile="Q2",
        impact_factor=2.5,
        citescore=4.0,
        h_index=95,
        scope="Maternal health, child health, public health, health disparities, perinatal care",
        word_limit=6000,
        abstract_limit=250,
        keywords_limit=6,
        reference_style="Vancouver",
        sections=["Introduction", "Methods", "Results", "Discussion", "Conclusion"],
        url="https://www.springer.com/journal/10995",
        submission_url="https://www.editorialmanager.com/maci/",
        review_time_weeks=12
    ),
    Journal(
        name="PLOS ONE",
        issn="1932-6203",
        eissn="1932-6203",
        publisher="Public Library of Science",
        open_access=True,
        apc_usd=1931,
        asjc_codes=["1000"],
        asjc_areas=["Multidisciplinary"],
        quartile="Q1",
        impact_factor=3.7,
        citescore=5.8,
        h_index=400,
        scope="All areas of science and medicine including maternal health research",
        word_limit=None,
        abstract_limit=300,
        keywords_limit=None,
        reference_style="Vancouver",
        sections=["Introduction", "Materials and Methods", "Results", "Discussion"],
        url="https://journals.plos.org/plosone/",
        submission_url="https://www.editorialmanager.com/pone/",
        review_time_weeks=16
    ),
    Journal(
        name="BMJ Open",
        issn="2044-6055",
        eissn="2044-6055",
        publisher="BMJ Publishing Group",
        open_access=True,
        apc_usd=2415,
        asjc_codes=["2700"],
        asjc_areas=["Medicine (General)"],
        quartile="Q1",
        impact_factor=2.9,
        citescore=5.0,
        h_index=145,
        scope="Medical research including obstetrics, maternal health, health services",
        word_limit=4000,
        abstract_limit=300,
        keywords_limit=5,
        reference_style="Vancouver",
        sections=["Introduction", "Methods", "Results", "Discussion"],
        url="https://bmjopen.bmj.com/",
        submission_url="https://mc.manuscriptcentral.com/bmjopen",
        review_time_weeks=10
    ),
    Journal(
        name="International Journal of Gynecology & Obstetrics",
        issn="0020-7292",
        eissn="1879-3479",
        publisher="Wiley (FIGO)",
        open_access=False,
        apc_usd=3500,
        asjc_codes=["2729"],
        asjc_areas=["Obstetrics and Gynecology"],
        quartile="Q2",
        impact_factor=2.5,
        citescore=3.9,
        h_index=102,
        scope="Obstetrics, gynecology, maternal-fetal medicine, global women's health",
        word_limit=3500,
        abstract_limit=250,
        keywords_limit=6,
        reference_style="Vancouver",
        sections=["Introduction", "Materials and Methods", "Results", "Discussion", "Conclusion"],
        url="https://obgyn.onlinelibrary.wiley.com/journal/18793479",
        submission_url="https://mc.manuscriptcentral.com/ijgo",
        review_time_weeks=8
    ),
    Journal(
        name="Reproductive Health",
        issn="1742-4755",
        eissn="1742-4755",
        publisher="BioMed Central (Springer Nature)",
        open_access=True,
        apc_usd=2790,
        asjc_codes=["2729", "2735"],
        asjc_areas=["Obstetrics and Gynecology", "Pediatrics, Perinatology and Child Health"],
        quartile="Q1",
        impact_factor=3.1,
        citescore=4.8,
        h_index=75,
        scope="Reproductive health, family planning, maternal health, sexual health",
        word_limit=None,
        abstract_limit=350,
        keywords_limit=10,
        reference_style="Vancouver",
        sections=["Background", "Methods", "Results", "Discussion", "Conclusions"],
        url="https://reproductive-health-journal.biomedcentral.com/",
        submission_url="https://www.editorialmanager.com/reph/",
        review_time_weeks=10
    ),
    Journal(
        name="Journal of Perinatal Medicine",
        issn="0300-5577",
        eissn="1619-3997",
        publisher="De Gruyter",
        open_access=False,
        apc_usd=2500,
        asjc_codes=["2735", "2729"],
        asjc_areas=["Pediatrics, Perinatology and Child Health", "Obstetrics and Gynecology"],
        quartile="Q2",
        impact_factor=2.3,
        citescore=3.5,
        h_index=68,
        scope="Perinatal medicine, fetal medicine, neonatology, obstetrics",
        word_limit=4000,
        abstract_limit=250,
        keywords_limit=6,
        reference_style="Vancouver",
        sections=["Introduction", "Materials and Methods", "Results", "Discussion"],
        url="https://www.degruyter.com/journal/key/jpme/html",
        submission_url="https://mc.manuscriptcentral.com/jpm",
        review_time_weeks=8
    ),
    Journal(
        name="Birth: Issues in Perinatal Care",
        issn="0730-7659",
        eissn="1523-536X",
        publisher="Wiley",
        open_access=False,
        apc_usd=3600,
        asjc_codes=["2729", "2911"],
        asjc_areas=["Obstetrics and Gynecology", "Nursing (Midwifery)"],
        quartile="Q1",
        impact_factor=3.0,
        citescore=4.6,
        h_index=85,
        scope="Perinatal care, childbirth, labor, maternity services, birth outcomes",
        word_limit=5000,
        abstract_limit=250,
        keywords_limit=5,
        reference_style="APA",
        sections=["Introduction", "Methods", "Results", "Discussion", "Conclusion"],
        url="https://onlinelibrary.wiley.com/journal/1523536x",
        submission_url="https://mc.manuscriptcentral.com/birth",
        review_time_weeks=12
    ),
    Journal(
        name="BMC Women's Health",
        issn="1472-6874",
        eissn="1472-6874",
        publisher="BioMed Central (Springer Nature)",
        open_access=True,
        apc_usd=2490,
        asjc_codes=["2729"],
        asjc_areas=["Obstetrics and Gynecology"],
        quartile="Q2",
        impact_factor=2.4,
        citescore=3.8,
        h_index=62,
        scope="Women's health, reproductive health, maternal health, gynecology",
        word_limit=None,
        abstract_limit=350,
        keywords_limit=10,
        reference_style="Vancouver",
        sections=["Background", "Methods", "Results", "Discussion", "Conclusions"],
        url="https://bmcwomenshealth.biomedcentral.com/",
        submission_url="https://www.editorialmanager.com/bwhe/",
        review_time_weeks=10
    ),
    # Management and Healthcare Operations Research Journals
    Journal(
        name="Health Care Management Science",
        issn="1386-9620",
        eissn="1572-9389",
        publisher="Springer",
        open_access=False,
        apc_usd=3290,
        asjc_codes=["1408", "2719"],
        asjc_areas=["Strategy and Management", "Health Policy"],
        quartile="Q1",
        impact_factor=2.5,
        citescore=5.2,
        h_index=58,
        scope="Healthcare management, operations research, health systems optimization, resource allocation",
        word_limit=8000,
        abstract_limit=250,
        keywords_limit=6,
        reference_style="APA",
        sections=["Introduction", "Literature Review", "Methods", "Results", "Discussion", "Conclusion"],
        url="https://www.springer.com/journal/10729",
        submission_url="https://www.editorialmanager.com/hcms/",
        review_time_weeks=12
    ),
    Journal(
        name="International Journal of Health Planning and Management",
        issn="0749-6753",
        eissn="1099-1751",
        publisher="Wiley",
        open_access=False,
        apc_usd=3500,
        asjc_codes=["1408", "2719", "2739"],
        asjc_areas=["Strategy and Management", "Health Policy", "Public Health, Environmental and Occupational Health"],
        quartile="Q2",
        impact_factor=2.1,
        citescore=3.9,
        h_index=52,
        scope="Health planning, health management, health services organization, policy implementation",
        word_limit=7000,
        abstract_limit=300,
        keywords_limit=6,
        reference_style="Vancouver",
        sections=["Introduction", "Methods", "Results", "Discussion", "Conclusions"],
        url="https://onlinelibrary.wiley.com/journal/10991751",
        submission_url="https://mc.manuscriptcentral.com/ijhpm",
        review_time_weeks=14
    ),
    Journal(
        name="Journal of Healthcare Management",
        issn="1096-9012",
        eissn="1944-8988",
        publisher="ACHE (Wolters Kluwer)",
        open_access=False,
        apc_usd=3000,
        asjc_codes=["1408", "2719"],
        asjc_areas=["Strategy and Management", "Health Policy"],
        quartile="Q2",
        impact_factor=1.8,
        citescore=3.5,
        h_index=45,
        scope="Healthcare administration, management practices, leadership, organizational improvement",
        word_limit=6000,
        abstract_limit=200,
        keywords_limit=5,
        reference_style="AMA",
        sections=["Introduction", "Methods", "Results", "Discussion", "Practical Implications"],
        url="https://journals.lww.com/jhmonline/",
        submission_url="https://www.editorialmanager.com/jhm/",
        review_time_weeks=10
    ),
    Journal(
        name="BMC Health Services Research",
        issn="1472-6963",
        eissn="1472-6963",
        publisher="BioMed Central (Springer Nature)",
        open_access=True,
        apc_usd=2790,
        asjc_codes=["2719", "1408"],
        asjc_areas=["Health Policy", "Strategy and Management"],
        quartile="Q1",
        impact_factor=2.7,
        citescore=4.5,
        h_index=135,
        scope="Health services research, healthcare delivery, health systems, quality improvement",
        word_limit=None,
        abstract_limit=350,
        keywords_limit=10,
        reference_style="Vancouver",
        sections=["Background", "Methods", "Results", "Discussion", "Conclusions"],
        url="https://bmchealthservres.biomedcentral.com/",
        submission_url="https://www.editorialmanager.com/bhsr/",
        review_time_weeks=10
    ),
    Journal(
        name="Health Policy and Planning",
        issn="0268-1080",
        eissn="1460-2237",
        publisher="Oxford University Press",
        open_access=False,
        apc_usd=3650,
        asjc_codes=["2719", "1408"],
        asjc_areas=["Health Policy", "Strategy and Management"],
        quartile="Q1",
        impact_factor=3.2,
        citescore=5.8,
        h_index=125,
        scope="Health policy, health planning, health systems strengthening, implementation research",
        word_limit=7000,
        abstract_limit=300,
        keywords_limit=6,
        reference_style="Vancouver",
        sections=["Introduction", "Methods", "Results", "Discussion", "Conclusion"],
        url="https://academic.oup.com/heapol",
        submission_url="https://mc.manuscriptcentral.com/heapol",
        review_time_weeks=16
    ),
    Journal(
        name="Operations Research for Health Care",
        issn="2211-6923",
        eissn="2211-6931",
        publisher="Elsevier",
        open_access=False,
        apc_usd=2500,
        asjc_codes=["1408", "1803"],
        asjc_areas=["Strategy and Management", "Management Science and Operations Research"],
        quartile="Q2",
        impact_factor=1.9,
        citescore=4.1,
        h_index=32,
        scope="Operations research in healthcare, optimization, simulation, decision support systems",
        word_limit=8000,
        abstract_limit=250,
        keywords_limit=6,
        reference_style="APA",
        sections=["Introduction", "Literature Review", "Methodology", "Results", "Discussion", "Conclusions"],
        url="https://www.journals.elsevier.com/operations-research-for-health-care",
        submission_url="https://www.editorialmanager.com/orhc/",
        review_time_weeks=12
    ),
]


class JournalRecommender:
    """Recommends journals based on research content."""

    # Keywords for different research areas
    TOPIC_KEYWORDS = {
        "qualitative": ["qualitative", "interviews", "themes", "experiences", "narratives", "phenomenology"],
        "quantitative": ["statistical", "regression", "correlation", "cohort", "randomized", "trial"],
        "maternal_health": ["pregnancy", "maternal", "prenatal", "antenatal", "postpartum", "obstetric"],
        "midwifery": ["midwife", "midwifery", "birth", "labor", "childbirth", "delivery"],
        "mental_health": ["anxiety", "depression", "mental health", "psychological", "emotional"],
        "public_health": ["disparities", "access", "policy", "population", "community", "social determinants"],
        "clinical": ["clinical", "treatment", "diagnosis", "intervention", "outcomes", "complications"],
        "perinatal": ["perinatal", "neonatal", "fetal", "newborn", "infant"],
        "management": ["management", "administration", "organization", "operations", "efficiency",
                      "optimization", "resources", "planning", "strategy", "decision-making",
                      "leadership", "workflow", "process", "improvement", "quality"],
        "health_services": ["health services", "healthcare delivery", "health systems", "service quality",
                           "patient satisfaction", "care coordination", "utilization", "accessibility"],
    }

    def __init__(self, journals: List[Journal] = None, use_scopus: bool = False,
                 min_quartile: str = "Q2"):
        # Filter journals by quartile (Q1 and Q2 only by default)
        all_journals = journals or JOURNAL_DATABASE
        valid_quartiles = ["Q1"] if min_quartile == "Q1" else ["Q1", "Q2"]
        self.journals = [j for j in all_journals if j.quartile in valid_quartiles]
        self.use_scopus = use_scopus
        self.scopus_client = ScopusClient() if use_scopus else None

        if use_scopus:
            self._enrich_journals_from_scopus()

    def _enrich_journals_from_scopus(self):
        """Fetch latest metrics from Scopus for all journals."""
        logger.info("Fetching journal metrics from Scopus API...")
        for journal in self.journals:
            try:
                self.scopus_client.enrich_journal(journal)
            except Exception as e:
                logger.debug(f"Failed to enrich {journal.name}: {e}")
        logger.info("Scopus enrichment complete.")

    def analyze_content(self, text: str) -> Dict[str, float]:
        """Analyze research content to identify topic areas."""
        text_lower = text.lower()
        scores = {}

        for topic, keywords in self.TOPIC_KEYWORDS.items():
            count = sum(text_lower.count(kw) for kw in keywords)
            scores[topic] = count

        # Normalize scores
        max_score = max(scores.values()) if scores.values() else 1
        if max_score > 0:
            scores = {k: v / max_score for k, v in scores.items()}

        return scores

    def score_journal(self, journal: Journal, topic_scores: Dict[str, float],
                      preferences: Dict[str, Any] = None) -> Tuple[float, Dict[str, float]]:
        """Score a journal based on topic match and preferences."""
        preferences = preferences or {}

        component_scores = {}

        # Check if management focus is preferred
        prefer_management = preferences.get("prefer_management", True)  # Default to True

        # Topic relevance (40% weight)
        topic_relevance = 0.0
        if "2729" in journal.asjc_codes:  # Obstetrics and Gynecology
            topic_relevance += 0.4 * topic_scores.get("maternal_health", 0)
            topic_relevance += 0.3 * topic_scores.get("clinical", 0)
        if "2911" in journal.asjc_codes:  # Midwifery
            topic_relevance += 0.5 * topic_scores.get("midwifery", 0)
            topic_relevance += 0.3 * topic_scores.get("qualitative", 0)
        if "2735" in journal.asjc_codes:  # Pediatrics/Perinatology
            topic_relevance += 0.4 * topic_scores.get("perinatal", 0)
        if "1000" in journal.asjc_codes:  # Multidisciplinary
            topic_relevance += 0.3  # Base score for multidisciplinary

        # Management and Health Services ASJC codes (preferred)
        has_management = any(code.startswith("14") or code == "1803" for code in journal.asjc_codes)
        has_health_policy = "2719" in journal.asjc_codes
        if has_management or has_health_policy:
            topic_relevance += 0.5 * topic_scores.get("management", 0)
            topic_relevance += 0.4 * topic_scores.get("health_services", 0)
            if prefer_management:
                topic_relevance += 0.25  # Bonus for management journals when preferred

        component_scores["topic_relevance"] = min(topic_relevance, 1.0)

        # Impact factor score (20% weight)
        if_score = min(journal.impact_factor / 5.0, 1.0)  # Normalize to max IF ~5
        component_scores["impact_factor"] = if_score

        # Quartile score (15% weight)
        quartile_scores = {"Q1": 1.0, "Q2": 0.7, "Q3": 0.4, "Q4": 0.2}
        component_scores["quartile"] = quartile_scores.get(journal.quartile, 0.3)

        # Open access preference (10% weight)
        prefer_oa = preferences.get("prefer_open_access", False)
        if prefer_oa:
            component_scores["open_access"] = 1.0 if journal.open_access else 0.3
        else:
            component_scores["open_access"] = 0.7  # Neutral

        # APC consideration (10% weight)
        max_apc = preferences.get("max_apc", 5000)
        if journal.apc_usd and journal.apc_usd > max_apc:
            component_scores["apc"] = 0.2
        elif journal.open_access and journal.apc_usd:
            component_scores["apc"] = max(0.3, 1.0 - (journal.apc_usd / 5000))
        else:
            component_scores["apc"] = 0.8  # Subscription journals score well here

        # Review time (5% weight)
        component_scores["review_time"] = max(0.2, 1.0 - (journal.review_time_weeks / 20))

        # Calculate weighted total
        weights = {
            "topic_relevance": 0.40,
            "impact_factor": 0.20,
            "quartile": 0.15,
            "open_access": 0.10,
            "apc": 0.10,
            "review_time": 0.05
        }

        total_score = sum(component_scores[k] * weights[k] for k in weights)

        return total_score, component_scores

    def recommend(self, text: str, top_n: int = 5,
                  preferences: Dict[str, Any] = None) -> List[Tuple[Journal, float, Dict[str, float]]]:
        """Recommend top N journals for the given research content."""
        topic_scores = self.analyze_content(text)

        journal_scores = []
        for journal in self.journals:
            score, components = self.score_journal(journal, topic_scores, preferences)
            journal_scores.append((journal, score, components))

        # Sort by score descending
        journal_scores.sort(key=lambda x: x[1], reverse=True)

        return journal_scores[:top_n]


class JournalPaperFormatter:
    """Formats papers according to journal guidelines."""

    def __init__(self, llm_provider=None):
        self.llm = llm_provider

    def _init_llm(self, provider: str = 'anthropic', model: str = None):
        """Initialize LLM if not already done."""
        if self.llm:
            return

        try:
            if provider == 'anthropic':
                import anthropic
                self.client = anthropic.Anthropic()
                self.model = model or 'claude-sonnet-4-5-20250929'
                self.provider = 'anthropic'
            elif provider == 'openai':
                import openai
                self.client = openai.OpenAI()
                self.model = model or 'gpt-4o-mini'
                self.provider = 'openai'
        except ImportError as e:
            logger.error(f"Failed to import LLM library: {e}")
            raise

    def _generate(self, prompt: str, system_prompt: str, max_tokens: int = 4096) -> str:
        """Generate text using LLM."""
        if self.provider == 'anthropic':
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        elif self.provider == 'openai':
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content

    def format_paper(self, source_report: str, journal: Journal,
                     provider: str = 'anthropic', model: str = None) -> str:
        """Format paper according to journal guidelines."""
        self._init_llm(provider, model)

        logger.info(f"Formatting paper for {journal.name}...")

        system_prompt = f"""You are an expert academic editor specializing in formatting research papers
for peer-reviewed journals. You are formatting a paper for submission to {journal.name}.

Journal Guidelines:
- Publisher: {journal.publisher}
- Reference Style: {journal.reference_style}
- Abstract Limit: {journal.abstract_limit} words
- Word Limit: {journal.word_limit or 'No specific limit'}
- Keywords: Maximum {journal.keywords_limit}
- Required Sections: {', '.join(journal.sections)}

Your task is to reformat the provided research content to match these guidelines exactly."""

        prompt = f"""Please reformat the following research paper for submission to {journal.name}.

JOURNAL REQUIREMENTS:
1. Reference Style: {journal.reference_style}
2. Abstract: Maximum {journal.abstract_limit} words, structured if required
3. Keywords: Exactly {journal.keywords_limit} keywords
4. Sections: Must include: {', '.join(journal.sections)}
5. Word Limit: {journal.word_limit or 'No specific limit'} words for main text

FORMATTING RULES FOR {journal.reference_style} STYLE:
{"- Vancouver: Numbered references in order of appearance, square brackets [1]" if journal.reference_style == "Vancouver" else ""}
{"- APA: Author-date citations (Author, Year), alphabetical reference list" if journal.reference_style == "APA" else ""}
{"- AMA: Superscript numbers, references listed in citation order" if journal.reference_style == "AMA" else ""}

SOURCE CONTENT:
{source_report}

Please output the reformatted paper with:
1. Title
2. Abstract (within word limit)
3. Keywords
4. All required sections
5. References section (properly formatted)
6. Any required declarations (Ethics, Funding, Conflicts)

Format as clean markdown suitable for journal submission."""

        formatted = self._generate(prompt, system_prompt, max_tokens=8000)

        # Add journal-specific header
        header = f"""# Paper Formatted for: {journal.name}

**Target Journal:** {journal.name}
**ISSN:** {journal.issn} | **eISSN:** {journal.eissn}
**Publisher:** {journal.publisher}
**Impact Factor:** {journal.impact_factor} | **Quartile:** {journal.quartile}
**Open Access:** {'Yes' if journal.open_access else 'No'}
{f'**APC:** ${journal.apc_usd:,} USD' if journal.apc_usd else ''}
**Submission URL:** {journal.submission_url}

**Formatting Applied:**
- Reference Style: {journal.reference_style}
- Abstract Limit: {journal.abstract_limit} words
- Sections: {', '.join(journal.sections)}

---

"""
        return header + formatted


def display_journal_table(recommendations: List[Tuple[Journal, float, Dict]]):
    """Display journals in a formatted table."""
    print("\n" + "=" * 120)
    print("RECOMMENDED JOURNALS FOR YOUR RESEARCH")
    print("=" * 120)

    print(f"\n{'#':<3} {'Journal Name':<45} {'Q':<4} {'IF':<6} {'OA':<5} {'APC (USD)':<12} {'Score':<8}")
    print("-" * 120)

    for i, (journal, score, components) in enumerate(recommendations, 1):
        oa_status = "Yes" if journal.open_access else "No"
        apc_str = f"${journal.apc_usd:,}" if journal.apc_usd else "N/A"
        print(f"{i:<3} {journal.name[:44]:<45} {journal.quartile:<4} {journal.impact_factor:<6.1f} {oa_status:<5} {apc_str:<12} {score:.2f}")

    print("-" * 120)


def display_journal_details(journal: Journal, score: float, components: Dict[str, float]):
    """Display detailed information about a journal."""
    print(f"\n{'=' * 80}")
    print(f"JOURNAL DETAILS: {journal.name}")
    print(f"{'=' * 80}")

    print(f"\n{'IDENTIFIERS':-^40}")
    print(f"  ISSN:        {journal.issn}")
    print(f"  eISSN:       {journal.eissn}")
    print(f"  Publisher:   {journal.publisher}")

    print(f"\n{'METRICS':-^40}")
    print(f"  Impact Factor:  {journal.impact_factor}")
    print(f"  CiteScore:      {journal.citescore}")
    print(f"  H-Index:        {journal.h_index}")
    print(f"  Quartile:       {journal.quartile}")

    print(f"\n{'ACCESS & COSTS':-^40}")
    print(f"  Open Access:    {'Yes' if journal.open_access else 'No'}")
    if journal.apc_usd:
        print(f"  APC:            ${journal.apc_usd:,} USD")
    else:
        print(f"  APC:            N/A (subscription)")

    print(f"\n{'CLASSIFICATION (ASJC)':-^40}")
    for code, area in zip(journal.asjc_codes, journal.asjc_areas):
        print(f"  {code}: {area}")

    print(f"\n{'SUBMISSION GUIDELINES':-^40}")
    print(f"  Word Limit:     {journal.word_limit or 'No limit'}")
    print(f"  Abstract:       {journal.abstract_limit} words")
    print(f"  Keywords:       Max {journal.keywords_limit}")
    print(f"  Ref. Style:     {journal.reference_style}")
    print(f"  Sections:       {', '.join(journal.sections)}")
    print(f"  Review Time:    ~{journal.review_time_weeks} weeks")

    print(f"\n{'LINKS':-^40}")
    print(f"  Journal URL:    {journal.url}")
    print(f"  Submit:         {journal.submission_url}")

    print(f"\n{'MATCH SCORE BREAKDOWN':-^40}")
    for component, value in components.items():
        bar = "█" * int(value * 20) + "░" * (20 - int(value * 20))
        print(f"  {component:20} [{bar}] {value:.2f}")
    print(f"  {'TOTAL SCORE':20} {score:.2f}")

    print(f"\n{'SCOPE':-^40}")
    print(f"  {journal.scope}")


def interactive_selection(recommendations: List[Tuple[Journal, float, Dict]]) -> Optional[Journal]:
    """Interactive journal selection."""
    display_journal_table(recommendations)

    while True:
        print("\nOptions:")
        print("  Enter 1-{} to see journal details".format(len(recommendations)))
        print("  Enter 's1'-'s{}' to SELECT a journal".format(len(recommendations)))
        print("  Enter 'q' to quit without selection")

        choice = input("\nYour choice: ").strip().lower()

        if choice == 'q':
            return None

        if choice.startswith('s'):
            try:
                idx = int(choice[1:]) - 1
                if 0 <= idx < len(recommendations):
                    selected = recommendations[idx][0]
                    print(f"\n✓ Selected: {selected.name}")
                    return selected
            except ValueError:
                pass

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(recommendations):
                display_journal_details(*recommendations[idx])
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Invalid input. Please try again.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Recommend journals and format papers for submission'
    )
    parser.add_argument('--report', type=str, default=None,
                       help='Path to academic report file')
    parser.add_argument('--analysis', type=str, default=None,
                       help='Path to interview analysis JSON')
    parser.add_argument('--output', type=str, default=None,
                       help='Output path for formatted paper')
    parser.add_argument('--auto-select', action='store_true',
                       help='Automatically select top recommendation')
    parser.add_argument('--prefer-oa', action='store_true',
                       help='Prefer open access journals')
    parser.add_argument('--max-apc', type=int, default=5000,
                       help='Maximum APC in USD (default: 5000)')
    parser.add_argument('--provider', type=str, default='anthropic',
                       choices=['anthropic', 'openai'],
                       help='LLM provider for formatting')
    parser.add_argument('--model', type=str, default=None,
                       help='Specific LLM model to use')
    parser.add_argument('--list-journals', action='store_true',
                       help='List all journals in database')
    parser.add_argument('--fetch-scopus', action='store_true',
                       help='Fetch latest metrics from Scopus API')
    parser.add_argument('--scopus-key', type=str, default=None,
                       help='Scopus API key (default: from env or built-in)')
    parser.add_argument('--objective', type=str, default=None,
                       help='Publication objective (e.g., "healthcare management", "clinical practice", "policy")')
    parser.add_argument('--prefer-management', action='store_true', default=True,
                       help='Prefer management/operations research journals (default: True)')
    parser.add_argument('--interviews', type=str, default=None,
                       help='Path to interviews directory for additional content analysis')

    args = parser.parse_args()

    # Set Scopus API key if provided
    if args.scopus_key:
        global SCOPUS_API_KEY
        SCOPUS_API_KEY = args.scopus_key

    # List journals mode
    if args.list_journals:
        print("\n" + "=" * 100)
        print("MATERNAL HEALTH JOURNAL DATABASE")
        print("=" * 100)
        for j in JOURNAL_DATABASE:
            oa = "OA" if j.open_access else "Sub"
            print(f"\n{j.name}")
            print(f"  ISSN: {j.issn} | IF: {j.impact_factor} | {j.quartile} | {oa}")
            print(f"  Areas: {', '.join(j.asjc_areas)}")
        return 0

    # Load source content
    report_path = Path(args.report) if args.report else OUTPUTS_DIR / 'academic_report.md'

    if not report_path.exists():
        logger.error(f"Report file not found: {report_path}")
        logger.info("Run the academic report generator first:")
        logger.info("  python scripts/06_generate_academic_report.py")
        return 1

    with open(report_path, 'r') as f:
        report_content = f.read()

    # Load interview analysis data if available
    analysis_content = ""
    analysis_path = Path(args.analysis) if args.analysis else PROJECT_ROOT / 'data' / 'analysis' / 'interview_analysis.json'
    if analysis_path.exists():
        try:
            with open(analysis_path, 'r') as f:
                analysis_data = json.load(f)
            # Extract key themes and topics from analysis
            if isinstance(analysis_data, dict):
                themes = analysis_data.get('themes', [])
                topics = analysis_data.get('topics', [])
                analysis_content = f"\n\nKey themes: {', '.join(themes) if themes else 'N/A'}"
                analysis_content += f"\nMain topics: {', '.join(topics) if topics else 'N/A'}"
            logger.info(f"Loaded interview analysis from: {analysis_path}")
        except Exception as e:
            logger.debug(f"Could not load analysis: {e}")

    # Load interview content if directory specified
    interviews_content = ""
    interviews_path = Path(args.interviews) if args.interviews else PROJECT_ROOT / 'data' / 'interviews'
    if interviews_path.exists() and interviews_path.is_dir():
        try:
            interview_files = list(interviews_path.glob('interview_*.json'))
            for ifile in interview_files[:5]:  # Sample up to 5 interviews
                with open(ifile, 'r') as f:
                    interview = json.load(f)
                if isinstance(interview, dict):
                    # Extract key content from interview
                    exchanges = interview.get('exchanges', [])
                    for ex in exchanges[:3]:  # First few exchanges
                        if isinstance(ex, dict):
                            interviews_content += f" {ex.get('response', '')}"
            logger.info(f"Loaded {len(interview_files)} interviews for analysis")
        except Exception as e:
            logger.debug(f"Could not load interviews: {e}")

    # Combine all content for analysis
    combined_content = report_content + analysis_content + interviews_content

    # Add publication objective to content if specified
    if args.objective:
        combined_content = f"Publication objective: {args.objective}\n\n" + combined_content
        logger.info(f"Publication objective: {args.objective}")

    # Initialize recommender (with optional Scopus enrichment)
    recommender = JournalRecommender(use_scopus=args.fetch_scopus)
    preferences = {
        "prefer_open_access": args.prefer_oa,
        "max_apc": args.max_apc,
        "prefer_management": args.prefer_management
    }

    # Get recommendations
    logger.info("Analyzing research content...")
    recommendations = recommender.recommend(combined_content, top_n=10, preferences=preferences)

    # Select journal
    if args.auto_select:
        selected_journal = recommendations[0][0]
        print(f"\n✓ Auto-selected: {selected_journal.name}")
    else:
        selected_journal = interactive_selection(recommendations)

    if not selected_journal:
        print("No journal selected. Exiting.")
        return 0

    # Format paper
    print(f"\nFormatting paper for {selected_journal.name}...")
    formatter = JournalPaperFormatter()

    try:
        formatted_paper = formatter.format_paper(
            report_content,
            selected_journal,
            provider=args.provider,
            model=args.model
        )
    except Exception as e:
        logger.error(f"Failed to format paper: {e}")
        return 1

    # Save output
    output_path = Path(args.output) if args.output else OUTPUTS_DIR / f"paper_{selected_journal.issn.replace('-', '')}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write(formatted_paper)

    print(f"\n{'=' * 60}")
    print("PAPER FORMATTED SUCCESSFULLY")
    print(f"{'=' * 60}")
    print(f"Journal:  {selected_journal.name}")
    print(f"Output:   {output_path}")
    print(f"{'=' * 60}\n")

    return 0


if __name__ == '__main__':
    sys.exit(main())
