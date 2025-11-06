# Complete Tutorial: Testing the Pipeline from Scratch

## 🎯 Objective

This tutorial will guide you step-by-step to test the entire synthetic gravidas pipeline, from initial setup to generating interviews and analyzing results.

**Estimated time:** 30-60 minutes for complete test
**Estimated cost:** ~$3-5 USD for testing with 10 personas

---

## 📋 Prerequisites

### Verify Installations

```bash
# 1. Python (version 3.11+)
python --version
# Should show: Python 3.11.x or higher

# 2. Git
git --version
# Should show: git version 2.x

# 3. Conda (if using)
conda --version
```

### Directory Structure

Verify you're in the correct directory:

```bash
# Show current directory
pwd
# Should show something like: /home/your-user/202511-Gravidas

# List main files
ls -la
# Should show: scripts/, config/, data/, .env, etc.
```

---

## 🚀 Step 1: Update Code

### 1.1 Ensure Latest Version

```bash
# Switch to correct branch
git checkout claude/synthetic-gravidas-pipeline-011CUpt3YLnLffQE1REgHQoh

# Pull latest updates
git pull origin claude/synthetic-gravidas-pipeline-011CUpt3YLnLffQE1REgHQoh
```

**Expected output:**
```
Already on 'claude/synthetic-gravidas-pipeline-011CUpt3YLnLffQE1REgHQoh'
Already up to date.
```

### 1.2 Verify Available Scripts

```bash
# List scripts
ls -lh scripts/

# Check essential scripts
ls scripts/01b_generate_personas.py
ls scripts/02_generate_health_records.py
ls scripts/03_match_personas_records_enhanced.py
ls scripts/04_conduct_interviews.py
ls scripts/analyze_interviews.py
```

**All should exist!**

---

## 🔑 Step 2: Configure API Keys

### 2.1 Check .env File

```bash
# Verify .env exists
cat .env
```

**Should show:**
```bash
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
OPENAI_API_KEY=sk-proj-xxxxx
GOOGLE_API_KEY=AIzaSyxxxxx
```

### 2.2 Test API Connection

```bash
# Create quick test script
python3 << 'EOF'
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('ANTHROPIC_API_KEY')
if api_key and not api_key.startswith('your-'):
    print(f"✅ API Key found: {api_key[:20]}...")
else:
    print("❌ API Key not configured!")
EOF
```

**Expected output:**
```
✅ API Key found: sk-ant-api03-0M7wR...
```

---

## 📦 Step 3: Prepare Environment

### 3.1 Create Necessary Directories

```bash
# Create all data directories
mkdir -p data/personas
mkdir -p data/health_records
mkdir -p data/matched
mkdir -p data/interviews
mkdir -p data/analysis
mkdir -p logs

# Verify creation
ls -la data/
```

**Expected output:**
```
drwxr-xr-x  2 user user 4096 Nov  6 10:00 analysis
drwxr-xr-x  2 user user 4096 Nov  6 10:00 health_records
drwxr-xr-x  2 user user 4096 Nov  6 10:00 interviews
drwxr-xr-x  2 user user 4096 Nov  6 10:00 matched
drwxr-xr-x  2 user user 4096 Nov  6 10:00 personas
```

### 3.2 Clean Old Data (Optional)

```bash
# If you want to start completely fresh:
rm -f data/personas/*.json
rm -f data/health_records/*.json
rm -f data/matched/*.json
rm -f data/interviews/*.json
rm -f data/analysis/*.csv
rm -f logs/*.log

echo "✅ Environment clean and ready!"
```

---

## 🎭 Step 4: Generate Personas (SMALL TEST)

### 4.1 Minimum Test: 10 Personas

**⚠️ IMPORTANT:** Let's start with only 10 personas to test quickly!

```bash
# Generate 10 personas for testing
python scripts/01b_generate_personas.py --count 10

# Time: ~1-2 minutes
# Cost: ~$0.10
```

**Expected output:**
```
[INFO] === Synthetic Persona Generation Started ===
[INFO] Target: 10 personas
[INFO] Batch size: 100
[INFO] [Batch 1/1] Generating 10 personas...
[INFO]   ✅ Generated 10 valid personas (total: 10)
[INFO] ✅ Saved 10 personas to data/personas/personas.json
[INFO] ✅ Saved summary statistics to data/personas/personas_summary.json
[INFO] [SUCCESS] Generated 10 personas
[INFO] === Persona Generation Completed ===
```

### 4.2 Verify Generated Personas

```bash
# Verify file created
ls -lh data/personas/personas.json

# See how many personas were generated
python3 << 'EOF'
import json
with open('data/personas/personas.json', 'r') as f:
    personas = json.load(f)
print(f"✅ Total personas: {len(personas)}")
print(f"\nFirst persona:")
print(f"  - ID: {personas[0]['id']}")
print(f"  - Age: {personas[0]['age']}")
print(f"  - Education: {personas[0]['education']}")
print(f"  - Marital status: {personas[0]['marital_status']}")
print(f"  - Description: {personas[0]['description'][:100]}...")
EOF
```

**Expected output:**
```
✅ Total personas: 10

First persona:
  - ID: 1
  - Age: 28
  - Education: bachelors
  - Marital status: married
  - Description: Sarah is a 28-year-old elementary school teacher living in Boston. She has a bachelor'...
```

### 4.3 View Distributions

```bash
# View statistical summary
cat data/personas/personas_summary.json | python -m json.tool
```

**Expected output:**
```json
{
  "total_count": 10,
  "generation_method": "AI-generated (Claude)",
  "age_distribution": {
    "20-29": 4,
    "30-39": 3,
    "40-49": 2,
    "50-59": 1
  },
  "education_distribution": {
    "bachelors": 5,
    "masters": 3,
    "high_school": 2
  },
  ...
}
```

---

## 🏥 Step 5: Generate Health Records

### 5.1 Verify Synthea

```bash
# Check if Synthea exists
ls -la synthea/

# If it doesn't exist, you need to download it:
# See instructions in README.md
```

### 5.2 Generate 10 Records (Matching 10 Personas)

```bash
# Generate 10 health records
python scripts/02_generate_health_records.py --count 10

# Time: ~5-10 minutes
# Cost: Free (Synthea is local)
```

**Expected output:**
```
[INFO] === Health Record Generation Started ===
[INFO] Generating 10 pregnancy-related health records
[INFO] Running Synthea...
[INFO] Synthea output: ...
[INFO] Processing FHIR records...
[INFO] ✅ Processed 10 health records
[INFO] ✅ Saved to data/health_records/health_records.json
[INFO] [SUCCESS] Generated 10 health records
[INFO] === Health Record Generation Completed ===
```

### 5.3 Verify Generated Records

```bash
# Verify file created
ls -lh data/health_records/health_records.json

# View first record
python3 << 'EOF'
import json
with open('data/health_records/health_records.json', 'r') as f:
    records = json.load(f)

print(f"✅ Total records: {len(records)}")
print(f"\nFirst record:")
r = records[0]
print(f"  - Patient ID: {r['patient_id']}")
print(f"  - Age: {r['age']}")
print(f"  - Conditions: {len(r['conditions'])}")
print(f"  - Medications: {len(r['medications'])}")
print(f"  - Observations: {len(r['observations'])}")

# Show first condition
if r['conditions']:
    print(f"\n  First condition:")
    print(f"    - {r['conditions'][0]['display']}")
    print(f"    - Onset: {r['conditions'][0]['onset']}")
EOF
```

**Expected output:**
```
✅ Total records: 10

First record:
  - Patient ID: patient-1
  - Age: 28
  - Conditions: 2
  - Medications: 1
  - Observations: 15

  First condition:
    - Pregnancy
    - Onset: 2024-01-15
```

---

## 🔗 Step 6: Run Enhanced Matching

### 6.1 Execute Matching

```bash
# Perform optimized matching (Hungarian Algorithm)
python scripts/03_match_personas_records_enhanced.py

# Time: ~5 seconds (for 10x10)
# Cost: Free
```

**Expected output:**
```
[INFO] ============================================================
[INFO] ENHANCED PERSONA-RECORD MATCHING STARTED
[INFO] ============================================================
[INFO] ✅ Loaded 10 personas
[INFO] ✅ Loaded 10 health records
[INFO] Computing compatibility matrix for 10 personas × 10 records...
[INFO] Using weights: {'age': 0.4, 'education': 0.2, 'income': 0.15, 'marital_status': 0.15, 'occupation': 0.1}
[INFO] ✅ Compatibility matrix computed
[INFO] Running enhanced matching algorithm...
[INFO] ✅ Created 10 optimal matches
[INFO] Quality distribution:
[INFO]   - Excellent (≥0.85): X (X%)
[INFO]   - Good (≥0.75): X (X%)
[INFO] ✅ ENHANCED MATCHING COMPLETED SUCCESSFULLY
```

### 6.2 Analyze Matching Quality

```bash
# View detailed statistics
cat data/matched/matching_statistics.json | python -m json.tool
```

**Expected output:**
```json
{
  "total_matches": 10,
  "compatibility_scores": {
    "average": 0.89,
    "median": 0.91,
    "min": 0.75,
    "max": 0.96
  },
  "quality_distribution": {
    "excellent": 8,
    "excellent_pct": 80.0,
    "good": 2,
    "good_pct": 20.0
  },
  "age_differences": {
    "average": 1.2,
    "within_2_years": 9,
    "within_2_years_pct": 90.0
  }
}
```

### 6.3 View Individual Matches

```bash
# View first 3 matches with quality
python3 << 'EOF'
import json

with open('data/matched/match_quality_metrics.json', 'r') as f:
    metrics = json.load(f)

print("🎯 Top 3 Matches:\n")
for i, m in enumerate(metrics[:3], 1):
    print(f"{i}. Persona #{m['persona_idx']} ↔ Record #{m['record_idx']}")
    print(f"   Score: {m['compatibility_score']:.3f} ({m['quality_category']})")
    print(f"   Age: {m['persona_age']} vs {m['record_age']} (diff: {m['age_difference']})")
    print(f"   Breakdown:")
    for component, score in m['score_breakdown'].items():
        print(f"     - {component}: {score:.3f}")
    print()
EOF
```

**Expected output:**
```
🎯 Top 3 Matches:

1. Persona #0 ↔ Record #0
   Score: 0.952 (excellent)
   Age: 28 vs 28 (diff: 0)
   Breakdown:
     - age: 1.000
     - education: 0.880
     - income: 0.950
     - marital_status: 1.000
     - occupation: 0.900

2. Persona #1 ↔ Record #1
   Score: 0.915 (excellent)
   ...
```

---

## 🎤 Step 7: Conduct Interviews (TEST)

### 7.1 Test with 1 Interview First

```bash
# Do ONE interview to test
python scripts/04_conduct_interviews.py --count 1

# Time: ~1-2 minutes
# Cost: ~$0.37
```

**Expected output:**
```
[INFO] === Interview Script Started ===
[INFO] Loaded 10 matched persona-record pairs
[INFO] Will conduct 1 interviews
[INFO] Using provider: anthropic (model: claude-sonnet-4-5-20250929)
[INFO]
[INFO] [1/1] Interviewing Persona #1 (age 28)...
[INFO]   Turn 1/34...
[INFO]   Turn 10/34...
[INFO]   Turn 20/34...
[INFO]   Turn 30/34...
[INFO]   Turn 34/34...
[INFO]   ✅ Interview completed (34 turns, 18,672 words)
[INFO]   Cost: $0.37 (25,206 tokens)
[INFO]
[INFO] ✅ Completed 1 interviews
[INFO] Total cost: $0.37
[INFO] === Interview Script Completed ===
```

### 7.2 Verify Generated Interview

```bash
# List interviews
ls -lh data/interviews/

# View interview structure
python3 << 'EOF'
import json
import os

# List interview files
interviews = [f for f in os.listdir('data/interviews') if f.endswith('.json')]

if interviews:
    with open(f'data/interviews/{interviews[0]}', 'r') as f:
        interview = json.load(f)

    print(f"📄 Interview: {interviews[0]}")
    print(f"\n📊 Information:")
    print(f"  - Persona ID: {interview['persona_id']}")
    print(f"  - Persona age: {interview['persona_age']}")
    print(f"  - Patient ID (Synthea): {interview['synthea_patient_id']}")
    print(f"  - Total turns: {interview['metadata']['total_turns']}")
    print(f"  - Match quality: {interview['match_quality']['compatibility_score']:.3f}")
    print(f"  - Quality category: {interview['match_quality']['quality_category']}")

    print(f"\n💬 First 3 exchanges:")
    for i, turn in enumerate(interview['transcript'][:3], 1):
        speaker = turn['speaker']
        text = turn['text'][:100]
        print(f"  {i}. {speaker}: {text}...")
else:
    print("❌ No interviews found!")
EOF
```

**Expected output:**
```
📄 Interview: interview_00000.json

📊 Information:
  - Persona ID: 1
  - Persona age: 28
  - Patient ID (Synthea): patient-1
  - Total turns: 34
  - Match quality: 0.952
  - Quality category: excellent

💬 First 3 exchanges:
  1. Interviewer: Hello! Thank you for joining me today. I'd like to learn about your pregnancy...
  2. Persona: Hi! Thank you for having me. I'm Sarah, 28 years old, and I'm currently 34 weeks...
  3. Interviewer: That's wonderful, Sarah. How have you been feeling during your pregnancy?...
```

### 7.3 If 1 Interview Worked: Do 10!

```bash
# Now do 10 complete interviews
python scripts/04_conduct_interviews.py --count 10

# Time: ~15-20 minutes
# Cost: ~$3.70 (10 × $0.37)
```

**Notes during execution:**
- You'll see real-time progress
- Each interview takes ~1-2 minutes
- Total cost will be shown at the end

---

## 📊 Step 8: Analyze Results

### 8.1 Run Analysis

```bash
# Analyze all generated interviews
python scripts/analyze_interviews.py

# Time: ~10 seconds
# Cost: Free
```

**Expected output:**
```
[INFO] Analyzing interviews from data/interviews
[INFO] Found 10 interview files
[INFO] Processing interviews...
[INFO] ✅ Analyzed 10 interviews
[INFO] ✅ Saved summary to data/analysis/interview_summary.csv
[INFO]
[INFO] Summary Statistics:
[INFO]   - Total interviews: 10
[INFO]   - Average turns: 34
[INFO]   - Average words: 18,500
[INFO]   - Average cost: $0.37
[INFO]   - Total cost: $3.70
```

### 8.2 View CSV Results

```bash
# View first lines of CSV
head -5 data/analysis/interview_summary.csv | column -t -s,
```

**Or view formatted:**

```bash
# Use Python for better formatting
python3 << 'EOF'
import pandas as pd

df = pd.read_csv('data/analysis/interview_summary.csv')

print("📊 Interview Summary:\n")
print(f"Total interviews: {len(df)}")
print(f"\n📈 Statistics:")
print(f"  - Average age: {df['persona_age'].mean():.1f} years")
print(f"  - Average turns: {df['total_turns'].mean():.1f}")
print(f"  - Average words: {df['total_words'].mean():.0f}")
print(f"  - Average cost: ${df['cost_usd'].mean():.2f}")
print(f"  - Total cost: ${df['cost_usd'].sum():.2f}")

print(f"\n🎯 Match Quality:")
print(df[['persona_id', 'persona_age', 'compatibility_score', 'quality_category']].head(10).to_string(index=False))

print(f"\n💰 Costs per interview:")
print(df[['persona_id', 'total_turns', 'cost_usd']].head(10).to_string(index=False))
EOF
```

**Expected output:**
```
📊 Interview Summary:

Total interviews: 10

📈 Statistics:
  - Average age: 32.5 years
  - Average turns: 34.2
  - Average words: 18,450
  - Average cost: $0.37
  - Total cost: $3.70

🎯 Match Quality:
persona_id  persona_age  compatibility_score  quality_category
         1           28                0.952         excellent
         2           35                0.915         excellent
         3           29                0.890         excellent
       ...

💰 Costs per interview:
persona_id  total_turns  cost_usd
         1           34      0.37
         2           35      0.38
         3           33      0.36
       ...
```

---

## 🎯 Step 9: Final Validation

### 9.1 Success Checklist

Run this final script to validate everything:

```bash
python3 << 'EOF'
import json
import os
from pathlib import Path

print("=" * 60)
print("🔍 FINAL PIPELINE VALIDATION")
print("=" * 60)

checks = []

# 1. Personas
if Path('data/personas/personas.json').exists():
    with open('data/personas/personas.json', 'r') as f:
        personas = json.load(f)
    checks.append(("✅", f"Personas generated: {len(personas)}"))
else:
    checks.append(("❌", "Personas NOT found"))

# 2. Health Records
if Path('data/health_records/health_records.json').exists():
    with open('data/health_records/health_records.json', 'r') as f:
        records = json.load(f)
    checks.append(("✅", f"Health records generated: {len(records)}"))
else:
    checks.append(("❌", "Health records NOT found"))

# 3. Matched Pairs
if Path('data/matched/matched_personas.json').exists():
    with open('data/matched/matched_personas.json', 'r') as f:
        matches = json.load(f)
    checks.append(("✅", f"Matches created: {len(matches)}"))
else:
    checks.append(("❌", "Matches NOT found"))

# 4. Quality Metrics
if Path('data/matched/matching_statistics.json').exists():
    with open('data/matched/matching_statistics.json', 'r') as f:
        stats = json.load(f)
    avg_score = stats['compatibility_scores']['average']
    checks.append(("✅", f"Average matching score: {avg_score:.3f}"))
else:
    checks.append(("⚠️", "Matching statistics not found"))

# 5. Interviews
interview_files = list(Path('data/interviews').glob('interview_*.json'))
if interview_files:
    checks.append(("✅", f"Interviews conducted: {len(interview_files)}"))
else:
    checks.append(("❌", "Interviews NOT found"))

# 6. Analysis
if Path('data/analysis/interview_summary.csv').exists():
    import pandas as pd
    df = pd.read_csv('data/analysis/interview_summary.csv')
    total_cost = df['cost_usd'].sum()
    checks.append(("✅", f"Analysis complete - Total cost: ${total_cost:.2f}"))
else:
    checks.append(("❌", "Analysis NOT found"))

# Show results
print("\n📋 Results:\n")
for status, message in checks:
    print(f"  {status} {message}")

# Count
success = sum(1 for s, _ in checks if s == "✅")
total = len(checks)

print("\n" + "=" * 60)
print(f"🎯 RESULT: {success}/{total} steps completed")
print("=" * 60)

if success == total:
    print("\n🎉 COMPLETE SUCCESS! Pipeline working perfectly!")
    print("\n✨ Next steps:")
    print("  1. Review interview quality")
    print("  2. Adjust parameters if needed")
    print("  3. Scale to 100, 1000, or 10000 interviews!")
elif success >= total - 1:
    print("\n✅ Almost there! Pipeline is 95% functional.")
    print("   Review pending items above.")
else:
    print("\n⚠️  Some issues found.")
    print("   Review errors above and re-run missing steps.")
EOF
```

**Expected output (complete success):**
```
============================================================
🔍 FINAL PIPELINE VALIDATION
============================================================

📋 Results:

  ✅ Personas generated: 10
  ✅ Health records generated: 10
  ✅ Matches created: 10
  ✅ Average matching score: 0.915
  ✅ Interviews conducted: 10
  ✅ Analysis complete - Total cost: $3.70

============================================================
🎯 RESULT: 6/6 steps completed
============================================================

🎉 COMPLETE SUCCESS! Pipeline working perfectly!

✨ Next steps:
  1. Review interview quality
  2. Adjust parameters if needed
  3. Scale to 100, 1000, or 10000 interviews!
```

---

## 📁 Final File Structure

After completing the tutorial, you'll have:

```
202511-Gravidas/
├── data/
│   ├── personas/
│   │   ├── personas.json (10 personas)
│   │   └── personas_summary.json
│   ├── health_records/
│   │   └── health_records.json (10 records)
│   ├── matched/
│   │   ├── matched_personas.json (10 pairs)
│   │   ├── match_quality_metrics.json
│   │   └── matching_statistics.json
│   ├── interviews/
│   │   ├── interview_00000.json
│   │   ├── interview_00001.json
│   │   └── ... (10 files)
│   └── analysis/
│       └── interview_summary.csv
├── logs/
│   ├── 01b_generate_personas.log
│   ├── 02_generate_health_records.log
│   ├── 03_match_personas_records_enhanced.log
│   └── 04_conduct_interviews.log
└── ...
```

---

## 🎓 Next Steps

### Option 1: Review Quality

```bash
# Read a complete interview
cat data/interviews/interview_00000.json | python -m json.tool | less

# View detailed analysis
cat data/analysis/interview_summary.csv
```

### Option 2: Scale Gradually

```bash
# Scale to 100 personas
python scripts/01b_generate_personas.py --count 100
python scripts/02_generate_health_records.py --count 100
python scripts/03_match_personas_records_enhanced.py
python scripts/04_conduct_interviews.py --count 100

# Expected cost: ~$37
# Time: ~2-3 hours
```

### Option 3: Adjust Parameters

**Modify matching quality:**
```bash
# Edit scripts/03_match_personas_records_enhanced.py
# Adjust weights around line 250:
weights = {
    'age': 0.50,            # Increase age importance
    'education': 0.15,      # Reduce education
    'income': 0.15,
    'marital_status': 0.15,
    'occupation': 0.05
}
```

**Change AI model:**
```bash
# Edit config/config.yaml
active_model: "claude-3-haiku"  # Cheaper ($0.10/interview)
# or
active_model: "claude-4.1-opus"  # More expensive but better quality
```

### Option 4: Full Production

```bash
# Complete pipeline: 20K personas → 10K records → 10K interviews

# 1. Generate 20K personas (2-3 hours, $20-40)
python scripts/01b_generate_personas.py --count 20000

# 2. Generate 10K records (30-60 min, free)
python scripts/02_generate_health_records.py --count 10000

# 3. Enhanced matching (5-15 min, free)
python scripts/03_match_personas_records_enhanced.py

# 4. Interviews (6 days or use batch API, $3,700 or $1,870)
python scripts/04_conduct_interviews.py --count 10000
# OR with batch mode (50% discount):
python scripts/04_conduct_interviews.py --count 10000 --batch-mode

# 5. Final analysis
python scripts/analyze_interviews.py
```

---

## 🐛 Troubleshooting

### Issue: "API key not found"

```bash
# Check .env file
cat .env | grep ANTHROPIC

# Reload
source .env

# Test
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('ANTHROPIC_API_KEY'))"
```

### Issue: "No module named 'anthropic'"

```bash
# Install dependencies
pip install -r requirements.txt

# Or individually
pip install anthropic openai google-generativeai python-dotenv pyyaml
```

### Issue: "Synthea not found"

```bash
# Download Synthea
# See README.md for instructions

# Or check path
ls -la synthea/
```

### Issue: "Low match quality scores"

```bash
# Regenerate personas with more diversity
python scripts/01b_generate_personas.py --count 50

# Or adjust matching weights
# Edit scripts/03_match_personas_records_enhanced.py
```

---

## 📊 Success Metrics

**You'll be successful if:**

✅ **All 6 steps completed** (personas, records, matching, interviews, analysis)
✅ **Average matching score > 0.80** (good) or **> 0.85** (excellent)
✅ **80%+ excellent/good matches** in quality distribution
✅ **Natural and coherent interviews** when manually reviewed
✅ **Cost within expected** (~$0.37 per interview with Claude Sonnet)

**Benchmarks:**
- 10 interviews: $3.70, 30 minutes
- 100 interviews: $37, 2-3 hours
- 1,000 interviews: $370, 15 hours
- 10,000 interviews: $3,700, 6 days (or $1,870 with batch)

---

## 🎉 Conclusion

Congratulations! If you made it this far, you've successfully tested the entire pipeline:

1. ✅ **Persona generation** with AI
2. ✅ **Health record generation** with Synthea
3. ✅ **Optimized matching** with Hungarian Algorithm
4. ✅ **Interviews** with Claude
5. ✅ **Results analysis**

**Pipeline is ready for production!** 🚀

---

## 📚 Additional Documentation

- `QUICK_START.md` - Quick reference commands
- `TUTORIAL_ENHANCED_MATCHING.md` - Detailed matching tutorial
- `docs/HUNGARIAN_ALGORITHM.md` - Algorithm explanation
- `README.md` - Project overview

---

*Tutorial created for 202511-Gravidas Pipeline*
*Last updated: 2025-11-06*
*Tested with Python 3.11, Claude Sonnet 4.5*
