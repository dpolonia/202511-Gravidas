# Quick Start Guide - Enhanced Matching Pipeline

## ✨ You Have: 20K Personas Downloaded

## 🚀 Next Steps (Quick Reference)

### 1️⃣ Generate Health Records (~30-60 min)
```bash
python scripts/02_generate_health_records.py --count 10000
```

### 2️⃣ Run Enhanced Matching (~5-15 min)
```bash
python scripts/03_match_personas_records_enhanced.py
```

### 3️⃣ Review Match Quality
```bash
cat data/matched/matching_statistics.json | python -m json.tool
```

### 4️⃣ Test Interviews (1-10 interviews)
```bash
# Test with 1 interview first
python scripts/04_conduct_interviews.py --count 1

# Or test with 10
python scripts/04_conduct_interviews.py --count 10
```

### 5️⃣ Analyze Results
```bash
python scripts/analyze_interviews.py
cat data/analysis/interview_summary.csv
```

---

## 📊 Quick Stats

**With 20K Persona Pool:**
- Expected match quality: 85-95% excellent/good
- Age matching: <1 year average difference
- Interview cost: $0.37 each (Claude Sonnet)
- Total for 10K interviews: ~$3,700 (or $1,870 with batch API)

---

## 💡 Cost Comparison

| Model | Cost/Interview | 10K Total | Quality |
|-------|----------------|-----------|---------|
| Claude Haiku | $0.10 | $1,000 | Good |
| Claude Sonnet | $0.37 | $3,700 | Excellent |
| Claude Opus | $1.50 | $15,000 | Premium |

---

## 🎯 Recommended Path

**For First Time:**
```bash
# 1. Generate records (60 min)
python scripts/02_generate_health_records.py --count 10000

# 2. Match with quality metrics (10 min)
python scripts/03_match_personas_records_enhanced.py

# 3. Test with 10 interviews (10 min)
python scripts/04_conduct_interviews.py --count 10

# 4. Analyze (1 min)
python scripts/analyze_interviews.py

# 5. Review results, then scale up!
```

---

## 📖 Full Tutorial

See `TUTORIAL_ENHANCED_MATCHING.md` for complete detailed instructions.

---

## 🆘 Quick Troubleshooting

**API Key Issues:**
```bash
# Check .env file
cat .env | grep ANTHROPIC_API_KEY
```

**Match Quality Low (<0.75):**
- Expand persona pool to 30K-50K
- Adjust weights in matching script

**Rate Limits:**
- Add delays between interviews
- Use batch mode for large runs

**Memory Issues:**
- Process in smaller batches
- Reduce persona pool size

---

## ✅ Success Checklist

After running these commands, you'll have:
- ✅ 10K pregnancy health records
- ✅ 10K optimal matches (from 20K pool)
- ✅ Match quality report
- ✅ Sample interviews
- ✅ Interview analysis CSV

**Total Time:** ~2-3 hours
**Total Cost:** $3.70 (for 10 test interviews)

Ready to scale to full 10K! 🚀
