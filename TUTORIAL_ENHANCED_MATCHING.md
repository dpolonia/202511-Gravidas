# Enhanced Matching Pipeline Tutorial

## 🎯 Overview

You've successfully downloaded 20,000 personas! This tutorial will guide you through using the enhanced matching system to create high-quality persona-health record pairs for interviews.

**What You'll Accomplish:**
- Generate 10,000 pregnancy health records
- Match them with the best 10,000 personas from your 20K pool
- Analyze match quality metrics
- Conduct AI-powered interviews
- Analyze interview results

**Expected Time:** 2-4 hours (depending on system speed)

---

## 📋 Prerequisites

✅ **Completed:**
- Downloaded 20,000 female personas from FinePersonas dataset
- Set up API keys in `.env` file

✅ **Check Your Setup:**
```bash
# 1. Verify personas are downloaded
ls -lh data/personas/personas.json
# Should show ~20K personas (check file size)

# 2. Verify personas count
python3 << EOF
import json
with open('data/personas/personas.json', 'r') as f:
    personas = json.load(f)
print(f"✅ Total personas: {len(personas)}")
EOF

# 3. Check API keys are configured
cat .env | grep API_KEY
```

---

## 🚀 Step-by-Step Pipeline

### Step 1: Generate Pregnancy Health Records (10K)

Generate 10,000 synthetic health records using Synthea:

```bash
# Generate 10,000 pregnancy-related health records
python scripts/02_generate_health_records.py --count 10000

# Expected output:
# [INFO] Generating 10,000 health records
# [INFO] Running Synthea...
# [INFO] ✅ Generated 10,000 health records
```

**What This Does:**
- Uses Synthea to generate realistic FHIR-compliant health records
- Focuses on pregnancy-related conditions and observations
- Includes: conditions, medications, procedures, encounters, vital signs

**Time Required:** 30-60 minutes (depends on system speed)

**Verify Success:**
```bash
# Check generated records
ls -lh data/health_records/health_records.json

# Count records
python3 << EOF
import json
with open('data/health_records/health_records.json', 'r') as f:
    records = json.load(f)
print(f"✅ Total health records: {len(records)}")
EOF
```

---

### Step 2: Run Enhanced Matching (20K → 10K)

Now use the enhanced matching algorithm to select the best 10,000 personas from your 20K pool:

```bash
# Run enhanced matching with quality metrics
python scripts/03_match_personas_records_enhanced.py

# Expected output:
# [INFO] ENHANCED PERSONA-RECORD MATCHING STARTED
# [INFO] Loaded 20000 personas and 10000 health records
# [INFO] ✅ Large pool mode: Selecting best 10000 matches from 20000 personas
# [INFO] Computing compatibility matrix...
# [INFO] Running enhanced matching algorithm...
# [INFO] Quality distribution:
#   - Excellent (≥0.85): X (X%)
#   - Good (≥0.75): X (X%)
#   - Fair (≥0.65): X (X%)
#   - Poor (<0.65): X (X%)
# [INFO] ✅ ENHANCED MATCHING COMPLETED SUCCESSFULLY
```

**What This Does:**
- Computes compatibility scores for all 20K personas × 10K records (200M comparisons!)
- Uses weighted scoring algorithm:
  - **Age (40%)**: Most critical for medical accuracy
  - **Education (20%)**: Demographic diversity
  - **Income (15%)**: Socioeconomic representation
  - **Marital Status (15%)**: Pregnancy context
  - **Occupation (10%)**: Lifestyle factors
- Selects the optimal 10,000 matches using Hungarian algorithm
- Generates comprehensive quality reports

**Time Required:** 5-15 minutes (depending on system)

**Output Files:**
```
data/matched/
├── matched_personas.json           # 10K matched pairs with quality info
├── match_quality_metrics.json      # Detailed quality breakdown per match
└── matching_statistics.json        # Overall quality analysis
```

---

### Step 3: Analyze Match Quality 📊

Review the quality metrics to ensure good matches:

```bash
# View overall statistics
cat data/matched/matching_statistics.json | python -m json.tool

# Quick quality summary
python3 << 'EOF'
import json
with open('data/matched/matching_statistics.json', 'r') as f:
    stats = json.load(f)

print("=" * 60)
print("MATCH QUALITY SUMMARY")
print("=" * 60)
print(f"Total Matches: {stats['total_matches']}")
print(f"\nCompatibility Scores:")
print(f"  Average: {stats['compatibility_scores']['average']:.3f}")
print(f"  Median:  {stats['compatibility_scores']['median']:.3f}")
print(f"  Min:     {stats['compatibility_scores']['min']:.3f}")
print(f"  Max:     {stats['compatibility_scores']['max']:.3f}")
print(f"\nQuality Distribution:")
print(f"  Excellent (≥0.85): {stats['quality_distribution']['excellent']} ({stats['quality_distribution']['excellent_pct']:.1f}%)")
print(f"  Good (≥0.75):      {stats['quality_distribution']['good']} ({stats['quality_distribution']['good_pct']:.1f}%)")
print(f"  Fair (≥0.65):      {stats['quality_distribution']['fair']} ({stats['quality_distribution']['fair_pct']:.1f}%)")
print(f"  Poor (<0.65):      {stats['quality_distribution']['poor']} ({stats['quality_distribution']['poor_pct']:.1f}%)")
print(f"\nAge Matching:")
print(f"  Average difference: {stats['age_differences']['average']:.2f} years")
print(f"  Within 2 years:     {stats['age_differences']['within_2_years']} ({stats['age_differences']['within_2_years_pct']:.1f}%)")
print(f"  Within 5 years:     {stats['age_differences']['within_5_years']} ({stats['age_differences']['within_5_years_pct']:.1f}%)")
print("=" * 60)
EOF
```

**What to Look For:**
- ✅ **Average score ≥ 0.80**: Good overall quality
- ✅ **80%+ excellent/good matches**: High-quality dataset
- ✅ **Age differences < 3 years average**: Accurate age matching
- ⚠️ **< 60% excellent/good**: May need to adjust weights or expand pool

**Understanding Quality Categories:**
- **Excellent (≥0.85)**: Near-perfect demographic match, ideal for interviews
- **Good (≥0.75)**: Strong match, very suitable for interviews
- **Fair (≥0.65)**: Acceptable match, usable but not optimal
- **Poor (<0.65)**: Weak match, consider excluding or regenerating

---

### Step 4: Conduct Interviews 🎤

Run interviews with your high-quality matched pairs:

```bash
# Option A: Test with 1 interview first
python scripts/04_conduct_interviews.py --count 1

# Option B: Run 10 interviews (recommended for testing)
python scripts/04_conduct_interviews.py --count 10

# Option C: Full batch (10K interviews - will take hours!)
python scripts/04_conduct_interviews.py --count 10000
```

**Interview Configuration:**
- Uses Claude Sonnet 4.5 by default (excellent quality, good cost)
- ~34 conversation turns per interview
- Cost: ~$0.37 per interview
- Includes complete traceability (persona + health record sources)

**Time & Cost Estimates:**

| Interview Count | Time Estimate | Cost Estimate |
|----------------|---------------|---------------|
| 1 interview    | ~1 minute     | $0.37         |
| 10 interviews  | ~10 minutes   | $3.70         |
| 100 interviews | ~1.5 hours    | $37.00        |
| 1,000 interviews | ~15 hours   | $370.00       |
| 10,000 interviews | ~6 days    | $3,700.00     |

**Monitor Progress:**
```bash
# Check interview files as they're created
ls -lh data/interviews/

# Count completed interviews
ls data/interviews/*.json | wc -l

# Watch progress in real-time
tail -f logs/04_conduct_interviews.log
```

**Sample Interview Output:**
```json
{
  "persona_id": 1,
  "persona_age": 28,
  "synthea_patient_id": "patient-5243",
  "match_quality": {
    "compatibility_score": 0.94,
    "quality_category": "excellent"
  },
  "transcript": [
    {
      "speaker": "Interviewer",
      "text": "Tell me about your pregnancy journey..."
    },
    {
      "speaker": "Persona",
      "text": "Well, I'm 28 years old and 34 weeks pregnant..."
    }
  ]
}
```

---

### Step 5: Analyze Interview Results 📈

Analyze your completed interviews:

```bash
# Analyze all interviews
python scripts/analyze_interviews.py

# View summary
cat data/analysis/interview_summary.csv
```

**Analysis Outputs:**
- `interview_summary.csv`: Comprehensive data with:
  - Persona demographics and match quality
  - Interview metrics (turns, words, topics)
  - Cost tracking (tokens, USD)
  - Clinical data (conditions, medications, vitals)
  - Traceability (source files for persona and health record)

**Key Metrics to Review:**
1. **Quality vs. Cost Correlation**: Do higher match quality scores produce better interviews?
2. **Topic Coverage**: Are all key topics (pregnancy, healthcare, support, emotions) covered?
3. **Persona Response Depth**: Average response length and emotional expression
4. **Clinical Accuracy**: Do personas reference their health conditions naturally?

---

## 🎓 Advanced Usage

### Adjusting Match Quality Weights

If you want to prioritize different factors, modify the weights in `scripts/03_match_personas_records_enhanced.py`:

```python
# Default weights
weights = {
    'age': 0.40,           # Age compatibility
    'education': 0.20,      # Education level
    'income': 0.15,         # Income level
    'marital_status': 0.15, # Marital status
    'occupation': 0.10      # Occupation compatibility
}

# Example: Prioritize age and marital status more
weights = {
    'age': 0.50,           # Increased
    'education': 0.15,      # Decreased
    'income': 0.10,         # Decreased
    'marital_status': 0.20, # Increased
    'occupation': 0.05      # Decreased
}
```

Then re-run matching:
```bash
python scripts/03_match_personas_records_enhanced.py
```

---

### Using Different AI Models

Switch models to balance cost vs. quality:

**Budget Option - Claude Haiku:**
```bash
# Edit config/config.yaml
active_model: "claude-3-haiku"

# Cost: ~$0.10 per interview (75% cheaper)
# Quality: Good for testing, acceptable for production
```

**Premium Option - Claude Opus:**
```bash
# Edit config/config.yaml
active_model: "claude-4.1-opus"

# Cost: ~$1.50 per interview (4x more expensive)
# Quality: Exceptional depth and nuance
```

**Alternative Providers:**
```bash
# OpenAI GPT-5
active_provider: "openai"
active_model: "gpt-5"

# Google Gemini
active_provider: "google"
active_model: "gemini-2.5-pro"
```

---

### Batch Processing for Scale

For 10K interviews, use batch mode to save costs:

```bash
# Generate batch request file
python scripts/04_conduct_interviews.py --count 10000 --batch-mode

# Upload to Anthropic batch API (50% cost reduction!)
# Expected cost: $1,870 instead of $3,700
```

---

## 📊 Expected Results

### With 20K Persona Pool:

**Match Quality Improvements (vs. 10K pool):**
- Average compatibility score: **+0.05 to +0.10** increase
- Excellent matches (≥0.85): **80-95%** (vs. 60-70% with 10K)
- Age differences: **Reduced by 30-50%**
- Better socioeconomic diversity

**Interview Quality Improvements:**
- More natural responses (personas better aligned with health records)
- Reduced inconsistencies between persona and medical history
- Better representation across demographics

---

## 🔍 Troubleshooting

### Issue: Low Match Quality Scores

**Problem:** Average compatibility score < 0.75

**Solutions:**
1. Expand persona pool further (30K-50K)
2. Adjust matching weights to prioritize your key factors
3. Regenerate health records with different parameters
4. Check persona and record distributions match

```bash
# Check distributions
python3 << 'EOF'
import json
with open('data/personas/personas.json', 'r') as f:
    personas = json.load(f)

with open('data/health_records/health_records.json', 'r') as f:
    records = json.load(f)

# Age distribution
persona_ages = [p['age'] for p in personas]
record_ages = [r['age'] for r in records]

print(f"Personas age range: {min(persona_ages)}-{max(persona_ages)}, avg: {sum(persona_ages)/len(persona_ages):.1f}")
print(f"Records age range: {min(record_ages)}-{max(record_ages)}, avg: {sum(record_ages)/len(record_ages):.1f}")
EOF
```

### Issue: API Rate Limits

**Problem:** "Rate limit exceeded" errors during interviews

**Solutions:**
1. Add delays between requests:
```python
# In scripts/04_conduct_interviews.py
import time
time.sleep(1)  # 1 second delay between interviews
```

2. Use batch mode (no rate limits)
3. Spread interviews over multiple days

### Issue: High Interview Costs

**Problem:** Costs exceeding budget

**Solutions:**
1. Switch to cheaper model (Claude Haiku: $0.10/interview)
2. Use batch API (50% discount)
3. Reduce interview length (modify protocol)
4. Start with smaller sample (100-1000 interviews)

---

## 📝 Next Steps

### Option 1: Small-Scale Testing (Recommended First)
```bash
# Test with 100 interviews
python scripts/04_conduct_interviews.py --count 100
python scripts/analyze_interviews.py

# Review results, tune parameters, then scale up
```

### Option 2: Medium-Scale Production
```bash
# Run 1,000 interviews (~$370)
python scripts/04_conduct_interviews.py --count 1000
python scripts/analyze_interviews.py

# Suitable for research papers, pilot studies
```

### Option 3: Full-Scale Deployment
```bash
# Run all 10,000 interviews (~$3,700 or $1,870 with batch)
python scripts/04_conduct_interviews.py --count 10000 --batch-mode

# Wait for batch completion (12-24 hours)
python scripts/download_batch_results.py

# Analyze complete dataset
python scripts/analyze_interviews.py
```

---

## 🎉 Success Checklist

After completing this tutorial, you should have:

- ✅ 20,000 high-quality personas downloaded
- ✅ 10,000 pregnancy health records generated
- ✅ 10,000 optimal matches with quality metrics
- ✅ Match quality report showing excellent/good matches
- ✅ Sample interviews completed and analyzed
- ✅ Understanding of cost/quality tradeoffs
- ✅ Ready to scale to full 10K interview dataset

---

## 📚 Additional Resources

### Documentation Files:
- `README.md` - Project overview and setup
- `docs/matching_algorithm.md` - Detailed matching algorithm explanation
- `docs/interview_protocols.md` - Interview question design
- `config/config.yaml` - Configuration reference

### Log Files:
- `logs/01_retrieve_personas.log` - Persona retrieval logs
- `logs/02_generate_health_records.log` - Synthea generation logs
- `logs/03_match_personas_records_enhanced.log` - Matching algorithm logs
- `logs/04_conduct_interviews.log` - Interview execution logs

### Output Files:
- `data/matched/match_quality_metrics.json` - Per-match quality details
- `data/matched/matching_statistics.json` - Overall quality statistics
- `data/analysis/interview_summary.csv` - Complete interview analysis

---

## 🆘 Getting Help

If you encounter issues:

1. **Check logs**: All scripts write detailed logs to `logs/` directory
2. **Verify data**: Use the verification commands provided above
3. **Review config**: Ensure `config/config.yaml` and `.env` are correct
4. **Check quality metrics**: Low match quality may indicate data issues

**Common Issues:**
- **Memory errors**: Reduce batch size or process in chunks
- **API errors**: Check API keys and rate limits
- **Matching errors**: Verify persona and record counts match expectations

---

## 🎯 Summary

You now have a complete enhanced matching pipeline:

1. **20K Persona Pool** → Better match selection
2. **Enhanced Matching** → Quality-scored optimal pairs
3. **Quality Metrics** → Validate and tune matching
4. **High-Quality Interviews** → More natural, accurate responses

The enhanced matching system ensures that each of your 10,000 interviews uses the best possible persona from your 20K pool, resulting in higher quality, more realistic interview data for your research.

**Estimated Total Time:** 2-4 hours setup + interview time (varies by count)
**Estimated Total Cost:** $0-$3,700 (depending on interview count and model choice)

Good luck with your synthetic gravidas pipeline! 🚀
