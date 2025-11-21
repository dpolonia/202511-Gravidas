#!/usr/bin/env python3
"""
Academic Report Generator
=========================

Generates a systematic academic report from interview data and analysis using LLM models.

The report follows standard academic structure:
1. Abstract
2. Introduction
3. Methodology
4. Results (Quantitative & Qualitative)
5. Discussion
6. Conclusions
7. References
8. Appendices

Usage:
    python scripts/06_generate_academic_report.py
    python scripts/06_generate_academic_report.py --provider openai --model gpt-4o
    python scripts/06_generate_academic_report.py --output outputs/academic_report.md
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import statistics

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / 'data'
ANALYSIS_DIR = DATA_DIR / 'analysis'
INTERVIEWS_DIR = DATA_DIR / 'interviews'
OUTPUTS_DIR = PROJECT_ROOT / 'outputs'


class LLMProvider:
    """Wrapper for different LLM providers."""

    def __init__(self, provider: str = 'anthropic', model: str = None):
        self.provider = provider.lower()
        self.model = model
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the appropriate LLM client."""
        if self.provider == 'anthropic':
            try:
                import anthropic
                self.client = anthropic.Anthropic()
                self.model = self.model or 'claude-sonnet-4-5-20250929'
            except ImportError:
                raise ImportError("anthropic package not installed. Run: pip install anthropic")

        elif self.provider == 'openai':
            try:
                import openai
                self.client = openai.OpenAI()
                self.model = self.model or 'gpt-4o-mini'
            except ImportError:
                raise ImportError("openai package not installed. Run: pip install openai")

        elif self.provider == 'google':
            try:
                import google.generativeai as genai
                genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
                self.client = genai
                self.model = self.model or 'gemini-2.0-flash'
            except ImportError:
                raise ImportError("google-generativeai package not installed")

        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def generate(self, prompt: str, system_prompt: str = None, max_tokens: int = 4096) -> str:
        """Generate text using the LLM."""
        try:
            if self.provider == 'anthropic':
                messages = [{"role": "user", "content": prompt}]
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    system=system_prompt or "You are a research assistant helping write academic reports.",
                    messages=messages
                )
                return response.content[0].text

            elif self.provider == 'openai':
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content

            elif self.provider == 'google':
                model = self.client.GenerativeModel(self.model)
                full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                response = model.generate_content(full_prompt)
                return response.text

        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            raise


class AcademicReportGenerator:
    """Generates academic reports from interview data using LLM."""

    SYSTEM_PROMPT = """You are an expert academic researcher specializing in qualitative health research,
particularly in maternal and pregnancy health. You write in a formal, objective academic style suitable
for peer-reviewed publication. Your writing is precise, evidence-based, and follows standard academic
conventions for health sciences research."""

    def __init__(self, llm: LLMProvider, interviews_dir: Path, analysis_file: Path):
        self.llm = llm
        self.interviews_dir = interviews_dir
        self.analysis_file = analysis_file
        self.interviews = []
        self.analysis = {}
        self.statistics = {}

    def load_data(self):
        """Load interview data and analysis."""
        logger.info("Loading interview data and analysis...")

        # Load analysis
        if self.analysis_file.exists():
            with open(self.analysis_file, 'r') as f:
                self.analysis = json.load(f)
            logger.info(f"Loaded analysis with {self.analysis.get('metadata', {}).get('total_interviews', 0)} interviews")

        # Load individual interviews
        interview_files = sorted(self.interviews_dir.glob('interview_*.json'))
        for interview_file in interview_files:
            try:
                with open(interview_file, 'r') as f:
                    interview = json.load(f)
                    self.interviews.append(interview)
            except Exception as e:
                logger.warning(f"Failed to load {interview_file}: {e}")

        logger.info(f"Loaded {len(self.interviews)} interview transcripts")

        # Calculate statistics
        self._calculate_statistics()

    def _calculate_statistics(self):
        """Calculate descriptive statistics from the data."""
        if not self.analysis.get('interviews'):
            return

        interviews = self.analysis['interviews']

        # Basic counts
        self.statistics['total_interviews'] = len(interviews)
        self.statistics['total_turns'] = sum(i.get('total_turns', 0) for i in interviews)
        self.statistics['total_words'] = sum(i.get('total_words', 0) for i in interviews)

        # Age statistics
        ages = [i.get('persona_age', 0) for i in interviews if i.get('persona_age')]
        if ages:
            self.statistics['age_mean'] = statistics.mean(ages)
            self.statistics['age_std'] = statistics.stdev(ages) if len(ages) > 1 else 0
            self.statistics['age_range'] = (min(ages), max(ages))

        # Sentiment statistics
        sentiments = [i.get('persona_sentiment_compound', 0) for i in interviews]
        if sentiments:
            self.statistics['sentiment_mean'] = statistics.mean(sentiments)
            self.statistics['sentiment_positive_count'] = sum(1 for s in sentiments if s > 0.05)
            self.statistics['sentiment_negative_count'] = sum(1 for s in sentiments if s < -0.05)
            self.statistics['sentiment_neutral_count'] = sum(1 for s in sentiments if -0.05 <= s <= 0.05)

        # Risk statistics
        risk_scores = [i.get('obstetric_risk_score', 0) for i in interviews]
        if risk_scores:
            self.statistics['risk_mean'] = statistics.mean(risk_scores)
            self.statistics['high_risk_count'] = sum(1 for i in interviews if i.get('obstetric_risk_level') in ['High', 'Critical'])

        # Topic coverage
        topic_counts = {
            'pregnancy': sum(i.get('topic_pregnancy', 0) for i in interviews),
            'healthcare': sum(i.get('topic_healthcare', 0) for i in interviews),
            'symptoms': sum(i.get('topic_symptoms', 0) for i in interviews),
            'emotions': sum(i.get('topic_emotions', 0) for i in interviews),
            'support': sum(i.get('topic_support', 0) for i in interviews),
            'financial': sum(i.get('topic_financial', 0) for i in interviews)
        }
        self.statistics['topic_coverage'] = topic_counts

    def _get_sample_excerpts(self, max_excerpts: int = 5) -> List[Dict[str, Any]]:
        """Extract representative interview excerpts for qualitative analysis."""
        excerpts = []

        for interview in self.interviews[:max_excerpts]:
            transcript = interview.get('transcript', [])
            # Get a meaningful exchange (skip intro)
            persona_responses = [t for t in transcript if t.get('speaker') == 'Persona']
            if len(persona_responses) >= 3:
                excerpts.append({
                    'persona_id': interview.get('persona_id'),
                    'persona_description': interview.get('persona_description', '')[:200],
                    'sample_response': persona_responses[2].get('text', '')[:500]
                })

        return excerpts

    def generate_abstract(self) -> str:
        """Generate the abstract section."""
        logger.info("Generating abstract...")

        prompt = f"""Write a concise academic abstract (250-300 words) for a research study on pregnancy experiences
based on the following data summary:

Study Details:
- Total interviews conducted: {self.statistics.get('total_interviews', 0)}
- Participant age range: {self.statistics.get('age_range', (0, 0))[0]}-{self.statistics.get('age_range', (0, 0))[1]} years
- Mean participant age: {self.statistics.get('age_mean', 0):.1f} years
- Total conversation turns: {self.statistics.get('total_turns', 0)}
- Topics covered: pregnancy experiences, healthcare access, physical symptoms, emotional journey, support systems, financial concerns

Key Findings:
- Mean sentiment score: {self.statistics.get('sentiment_mean', 0):.3f} (scale -1 to 1)
- High-risk pregnancies identified: {self.statistics.get('high_risk_count', 0)}
- Mean obstetric risk score: {self.statistics.get('risk_mean', 0):.2f}

The abstract should include: Background, Objective, Methods, Results, and Conclusions.
Write in third person, past tense, formal academic style."""

        return self.llm.generate(prompt, self.SYSTEM_PROMPT)

    def generate_introduction(self) -> str:
        """Generate the introduction section."""
        logger.info("Generating introduction...")

        prompt = """Write an academic introduction section (600-800 words) for a research study on pregnancy experiences.

The introduction should cover:
1. Background on maternal health research and the importance of understanding pregnancy experiences
2. The role of qualitative research in capturing diverse pregnancy narratives
3. Current gaps in understanding pregnancy experiences across different socioeconomic backgrounds
4. The potential of AI-assisted interview methods in health research
5. Research objectives and questions

Include appropriate academic language and structure. Do not include citations (they will be added later).
End with a clear statement of the study's aims."""

        return self.llm.generate(prompt, self.SYSTEM_PROMPT, max_tokens=2000)

    def generate_methodology(self) -> str:
        """Generate the methodology section."""
        logger.info("Generating methodology...")

        prompt = f"""Write a comprehensive methodology section (800-1000 words) for an academic research paper.

Study Design:
- Cross-sectional qualitative study using AI-assisted semi-structured interviews
- Interview protocol focused on pregnancy experiences
- Total participants: {self.statistics.get('total_interviews', 0)}

Data Collection:
- Interviews conducted using standardized protocol
- Topics covered: pregnancy discovery, prenatal care, physical changes, emotional journey, support systems
- Average interview length: {self.statistics.get('total_turns', 0) / max(self.statistics.get('total_interviews', 1), 1):.0f} conversational turns
- Total words collected: {self.statistics.get('total_words', 0):,}

Data Analysis:
- Quantitative analysis: sentiment analysis, topic modeling, risk assessment
- Qualitative analysis: thematic analysis of interview transcripts
- Clinical data integration: FHIR-formatted health records

Include subsections for:
1. Study Design
2. Participant Selection
3. Data Collection Procedures
4. Interview Protocol
5. Data Analysis Methods
6. Ethical Considerations

Write in past tense, third person, formal academic style."""

        return self.llm.generate(prompt, self.SYSTEM_PROMPT, max_tokens=2500)

    def generate_results_quantitative(self) -> str:
        """Generate quantitative results section."""
        logger.info("Generating quantitative results...")

        # Prepare detailed statistics
        interviews = self.analysis.get('interviews', [])
        risk_levels = {}
        for i in interviews:
            level = i.get('obstetric_risk_level', 'Unknown')
            risk_levels[level] = risk_levels.get(level, 0) + 1

        prompt = f"""Write the quantitative results section (600-800 words) for an academic paper.

Participant Demographics:
- Total participants: {self.statistics.get('total_interviews', 0)}
- Age range: {self.statistics.get('age_range', (0, 0))[0]}-{self.statistics.get('age_range', (0, 0))[1]} years
- Mean age: {self.statistics.get('age_mean', 0):.1f} years (SD = {self.statistics.get('age_std', 0):.1f})

Interview Metrics:
- Total conversational turns: {self.statistics.get('total_turns', 0)}
- Total words transcribed: {self.statistics.get('total_words', 0):,}
- Average turns per interview: {self.statistics.get('total_turns', 0) / max(self.statistics.get('total_interviews', 1), 1):.1f}

Sentiment Analysis:
- Mean compound sentiment: {self.statistics.get('sentiment_mean', 0):.3f}
- Positive sentiment interviews: {self.statistics.get('sentiment_positive_count', 0)}
- Negative sentiment interviews: {self.statistics.get('sentiment_negative_count', 0)}
- Neutral sentiment interviews: {self.statistics.get('sentiment_neutral_count', 0)}

Clinical Risk Assessment:
- Risk distribution: {risk_levels}
- Mean obstetric risk score: {self.statistics.get('risk_mean', 0):.2f}
- High-risk cases: {self.statistics.get('high_risk_count', 0)}

Topic Coverage (mentions):
{json.dumps(self.statistics.get('topic_coverage', {}), indent=2)}

Present these findings in a structured academic format with appropriate statistical reporting.
Include a brief interpretation of each finding."""

        return self.llm.generate(prompt, self.SYSTEM_PROMPT, max_tokens=2000)

    def generate_results_qualitative(self) -> str:
        """Generate qualitative results section."""
        logger.info("Generating qualitative results...")

        excerpts = self._get_sample_excerpts(5)
        excerpts_text = "\n\n".join([
            f"Participant {e['persona_id']} ({e['persona_description'][:100]}...):\n\"{e['sample_response']}\""
            for e in excerpts
        ])

        prompt = f"""Write the qualitative results section (800-1000 words) for an academic paper based on thematic analysis of pregnancy experience interviews.

Sample Interview Excerpts:
{excerpts_text}

Based on these excerpts and typical pregnancy experience themes, identify and describe 4-5 major themes that emerged from the interviews. For each theme:
1. Provide a descriptive name
2. Define the theme
3. Present supporting evidence (you can paraphrase the excerpts)
4. Discuss the significance

Common themes in pregnancy research include:
- Healthcare access and barriers
- Emotional journey and mental health
- Physical changes and coping
- Social support networks
- Financial concerns and planning
- Information seeking and decision-making

Write in formal academic style, presenting the themes with appropriate qualitative research conventions."""

        return self.llm.generate(prompt, self.SYSTEM_PROMPT, max_tokens=2500)

    def generate_discussion(self) -> str:
        """Generate discussion section."""
        logger.info("Generating discussion...")

        prompt = f"""Write a comprehensive discussion section (1000-1200 words) for an academic paper on pregnancy experiences.

Key Findings to Discuss:
1. Participant diversity: {self.statistics.get('total_interviews', 0)} participants, ages {self.statistics.get('age_range', (0, 0))[0]}-{self.statistics.get('age_range', (0, 0))[1]}
2. Sentiment patterns: Mean sentiment {self.statistics.get('sentiment_mean', 0):.3f}, indicating generally {'positive' if self.statistics.get('sentiment_mean', 0) > 0 else 'mixed'} experiences
3. Risk factors identified: {self.statistics.get('high_risk_count', 0)} high-risk cases
4. Topic coverage emphasizing healthcare and support themes

The discussion should:
1. Interpret the main findings in relation to existing literature
2. Discuss the significance of sentiment patterns in pregnancy narratives
3. Address healthcare access and support system themes
4. Consider the role of socioeconomic factors
5. Discuss methodological considerations (AI-assisted interviews)
6. Acknowledge limitations
7. Suggest clinical and research implications

Write in formal academic style, connecting findings to broader maternal health literature."""

        return self.llm.generate(prompt, self.SYSTEM_PROMPT, max_tokens=3000)

    def generate_conclusions(self) -> str:
        """Generate conclusions section."""
        logger.info("Generating conclusions...")

        prompt = f"""Write a concise conclusions section (300-400 words) for an academic paper on pregnancy experiences.

Study Summary:
- {self.statistics.get('total_interviews', 0)} interviews analyzed
- Key themes: healthcare access, emotional support, physical changes, financial concerns
- Mean sentiment: {self.statistics.get('sentiment_mean', 0):.3f}
- High-risk cases: {self.statistics.get('high_risk_count', 0)}

The conclusions should:
1. Summarize the main findings (2-3 sentences)
2. State the study's contribution to knowledge
3. Provide recommendations for clinical practice
4. Suggest directions for future research
5. End with a strong closing statement

Be concise but impactful. Write in formal academic style."""

        return self.llm.generate(prompt, self.SYSTEM_PROMPT, max_tokens=1000)

    def generate_full_report(self) -> str:
        """Generate the complete academic report."""
        logger.info("Generating full academic report...")

        # Generate all sections
        abstract = self.generate_abstract()
        introduction = self.generate_introduction()
        methodology = self.generate_methodology()
        results_quant = self.generate_results_quantitative()
        results_qual = self.generate_results_qualitative()
        discussion = self.generate_discussion()
        conclusions = self.generate_conclusions()

        # Compile report
        report = f"""# Pregnancy Experiences: A Qualitative Analysis of Maternal Health Narratives

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Model:** {self.llm.model}
**Provider:** {self.llm.provider}

---

## Abstract

{abstract}

---

## 1. Introduction

{introduction}

---

## 2. Methodology

{methodology}

---

## 3. Results

### 3.1 Quantitative Findings

{results_quant}

### 3.2 Qualitative Findings

{results_qual}

---

## 4. Discussion

{discussion}

---

## 5. Conclusions

{conclusions}

---

## 6. References

*References to be added based on institutional requirements and citation style guidelines.*

---

## Appendix A: Study Statistics

| Metric | Value |
|--------|-------|
| Total Interviews | {self.statistics.get('total_interviews', 0)} |
| Total Turns | {self.statistics.get('total_turns', 0)} |
| Total Words | {self.statistics.get('total_words', 0):,} |
| Age Range | {self.statistics.get('age_range', (0, 0))[0]}-{self.statistics.get('age_range', (0, 0))[1]} years |
| Mean Age | {self.statistics.get('age_mean', 0):.1f} years |
| Mean Sentiment | {self.statistics.get('sentiment_mean', 0):.3f} |
| Mean Risk Score | {self.statistics.get('risk_mean', 0):.2f} |
| High-Risk Cases | {self.statistics.get('high_risk_count', 0)} |

## Appendix B: Topic Coverage

| Topic | Mentions |
|-------|----------|
"""
        # Add topic coverage
        for topic, count in self.statistics.get('topic_coverage', {}).items():
            report += f"| {topic.title()} | {count} |\n"

        report += f"""
---

*This report was generated using AI-assisted analysis. All findings should be verified and validated by qualified researchers before publication.*

*Generated with {self.llm.provider} ({self.llm.model})*
"""

        return report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate academic report from interview data using LLM'
    )
    parser.add_argument('--provider', type=str, default='anthropic',
                       choices=['anthropic', 'openai', 'google'],
                       help='LLM provider to use (default: anthropic)')
    parser.add_argument('--model', type=str, default=None,
                       help='Specific model to use (default: provider default)')
    parser.add_argument('--interviews', type=str, default=None,
                       help='Path to interviews directory')
    parser.add_argument('--analysis', type=str, default=None,
                       help='Path to analysis JSON file')
    parser.add_argument('--output', type=str, default=None,
                       help='Output file path (default: outputs/academic_report.md)')

    args = parser.parse_args()

    # Set paths
    interviews_dir = Path(args.interviews) if args.interviews else INTERVIEWS_DIR
    analysis_file = Path(args.analysis) if args.analysis else ANALYSIS_DIR / 'interview_analysis.json'
    output_file = Path(args.output) if args.output else OUTPUTS_DIR / 'academic_report.md'

    # Validate paths
    if not interviews_dir.exists():
        logger.error(f"Interviews directory not found: {interviews_dir}")
        return 1

    if not analysis_file.exists():
        logger.error(f"Analysis file not found: {analysis_file}")
        return 1

    # Initialize LLM
    logger.info(f"Initializing {args.provider} LLM...")
    try:
        llm = LLMProvider(provider=args.provider, model=args.model)
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        return 1

    # Initialize report generator
    generator = AcademicReportGenerator(
        llm=llm,
        interviews_dir=interviews_dir,
        analysis_file=analysis_file
    )

    # Load data
    generator.load_data()

    # Generate report
    try:
        report = generator.generate_full_report()
    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        return 1

    # Save report
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(report)

    logger.info(f"Academic report saved to: {output_file}")
    print(f"\n{'='*60}")
    print(f"ACADEMIC REPORT GENERATED SUCCESSFULLY")
    print(f"{'='*60}")
    print(f"Output: {output_file}")
    print(f"Provider: {args.provider}")
    print(f"Model: {llm.model}")
    print(f"{'='*60}\n")

    return 0


if __name__ == '__main__':
    sys.exit(main())
