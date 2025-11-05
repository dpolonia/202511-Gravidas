# Batch API Guide

## Overview

Batch API allows you to process large volumes of interviews at **50% cost savings** compared to real-time API calls. The tradeoff is a ~24 hour processing time.

**When to use Batch API:**
- Running 100+ interviews
- Cost optimization is priority
- 24 hour turnaround is acceptable
- Processing large datasets

**When to use Real-time API:**
- Running <100 interviews
- Need immediate results
- Interactive/iterative development
- Testing and debugging

---

## Cost Comparison

### Example: 10,000 Interviews

| Provider | Model | Real-time Cost | Batch Cost | Savings |
|----------|-------|----------------|------------|---------|
| Anthropic | Claude 4.5 Sonnet | $390 | $195 | **$195** (50%) |
| OpenAI | GPT-5 | $625 | $312.50 | **$312.50** (50%) |
| Google | Gemini 2.5 Pro | $312 | $156 | **$156** (50%) |

---

## Using Batch API

### Step 1: Enable Batch Mode

Run the interactive launcher and select batch mode when prompted:

```bash
python scripts/interactive_interviews.py
```

When you select a model with batch support (marked with 🔄 BATCH), you'll see:

```
💡 Batch API Available!
   - 50% cost savings
   - ~24 hour turnaround time
   - Ideal for large volumes (100+ interviews)

Use Batch API? (yes/no):
```

Type `yes` to enable batch mode.

### Step 2: Generate Batch Request File

The script will create a batch request file instead of running interviews:

```
✓ Created batch request file: data/batch_requests/batch_request_anthropic_20250105_143022.jsonl
✓ 10000 interview requests prepared

Next steps:
  1. Submit batch file to anthropic API
  2. Wait for processing (~24 hours)
  3. Download results when ready
```

---

## Provider-Specific Instructions

### Anthropic Claude Batch API

#### 1. Submit Batch Request

```bash
# Install Anthropic CLI
pip install anthropic[cli]

# Submit batch
anthropic batches create \
  --input-file data/batch_requests/batch_request_anthropic_20250105_143022.jsonl \
  --output-file data/batch_results/batch_output_anthropic_20250105_143022.jsonl
```

#### 2. Check Status

```bash
# Check batch status
anthropic batches list

# Get specific batch details
anthropic batches get <batch_id>
```

#### 3. Download Results

Results are automatically written to the output file when processing completes (~24 hours).

**Official Documentation:** https://docs.anthropic.com/en/api/batch-processing

---

### OpenAI Batch API

#### 1. Upload Input File

```bash
# Install OpenAI CLI
pip install openai[cli]

# Upload batch input file
openai api files.create \
  -f data/batch_requests/batch_request_openai_20250105_143022.jsonl \
  -p batch
```

This returns a `file-xxxxx` ID.

#### 2. Create Batch Job

```bash
# Create batch job
openai api batches.create \
  -f <file-xxxxx> \
  -e /v1/chat/completions \
  -c 24h
```

This returns a `batch-xxxxx` ID.

#### 3. Check Status

```bash
# Check batch status
openai api batches.retrieve -i <batch-xxxxx>
```

#### 4. Download Results

```bash
# When status is "completed", download output
openai api files.content -i <output-file-id> > data/batch_results/batch_output_openai.jsonl
```

**Official Documentation:** https://platform.openai.com/docs/guides/batch

---

### Google Gemini Batch API

#### 1. Submit via Vertex AI

```bash
# Requires Google Cloud SDK
gcloud ai models batch-predict \
  --model=gemini-2-5-pro \
  --input-uri=gs://your-bucket/batch_request.jsonl \
  --output-uri=gs://your-bucket/batch_results/ \
  --region=us-central1
```

#### 2. Upload Input File to GCS

```bash
# Upload batch file to Google Cloud Storage
gsutil cp data/batch_requests/batch_request_google_20250105_143022.jsonl \
  gs://your-bucket/batch_request.jsonl
```

#### 3. Monitor Job

```bash
# Check job status
gcloud ai operations describe <operation-id> \
  --region=us-central1
```

#### 4. Download Results

```bash
# Download results from GCS
gsutil cp gs://your-bucket/batch_results/* \
  data/batch_results/
```

**Official Documentation:** https://cloud.google.com/vertex-ai/docs/predictions/batch-predictions

---

## Batch Request File Format

The generated batch request file (`.jsonl`) contains one JSON object per line:

```json
{"custom_id": "interview_0", "persona_id": 0, "persona": {...}, "health_record": {...}, "system_message": "...", "first_question": "..."}
{"custom_id": "interview_1", "persona_id": 1, "persona": {...}, "health_record": {...}, "system_message": "...", "first_question": "..."}
```

### Fields

- `custom_id`: Unique identifier for the interview
- `persona_id`: Index in the matched personas file
- `persona`: Full persona data
- `health_record`: Health record data
- `system_message`: Interview system prompt
- `first_question`: First interview question

---

## Processing Batch Results

Once the batch completes, you'll have a results file. The format varies by provider:

### Anthropic Results

```json
{"custom_id": "interview_0", "type": "message", "message": {"content": [{"text": "..."}]}}
```

### OpenAI Results

```json
{"id": "batch-req-0", "custom_id": "interview_0", "response": {"body": {"choices": [{"message": {"content": "..."}}]}}}
```

### Converting to Interview Format

Create a script to convert batch results to the standard interview JSON format:

```python
import json

with open('data/batch_results/batch_output_anthropic.jsonl', 'r') as f:
    for line in f:
        result = json.loads(line)
        interview_id = result['custom_id']
        response = result['message']['content'][0]['text']

        # Save as standard interview format
        interview = {
            'persona_id': int(interview_id.split('_')[1]),
            'timestamp': '2025-01-05T14:30:22',
            'provider': 'anthropic',
            'model': 'claude-sonnet-4-5-20250929',
            'transcript': [
                {'role': 'assistant', 'content': response}
            ]
        }

        with open(f'data/interviews/{interview_id}.json', 'w') as out:
            json.dump(interview, out, indent=2)
```

---

## Troubleshooting

### Batch Not Available

**Error:** Model doesn't support batch API

**Solution:** Only these models support batch:
- Anthropic: All Claude 4.x models
- OpenAI: GPT-5, GPT-5 mini, GPT-5 nano, GPT-4.1
- Google: Gemini 2.5 Pro, Gemini 2.5 Flash

### File Upload Fails

**Error:** Authentication failed

**Solution:** Ensure API keys are configured:

```bash
# Anthropic
export ANTHROPIC_API_KEY="your-key"

# OpenAI
export OPENAI_API_KEY="your-key"

# Google (requires service account)
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
```

### Batch Takes Too Long

**Issue:** Processing longer than 24 hours

**Reasons:**
- High API load (peak times)
- Very large batches (10,000+ requests)
- Provider-specific delays

**Solution:** Check provider status pages for incidents

---

## Best Practices

### 1. Test with Small Batches First

Before submitting 10,000 interviews, test with 10:

```bash
python scripts/interactive_interviews.py
# Select: 10 interviews, batch mode enabled
```

Verify the batch request file format is correct.

### 2. Split Large Batches

For 10,000+ interviews, split into multiple batches:

```bash
# Batch 1: Interviews 0-4999
python scripts/04_conduct_interviews.py \
  --provider anthropic \
  --model claude-sonnet-4-5-20250929 \
  --count 5000 \
  --start-index 0 \
  --batch

# Batch 2: Interviews 5000-9999
python scripts/04_conduct_interviews.py \
  --provider anthropic \
  --model claude-sonnet-4-5-20250929 \
  --count 5000 \
  --start-index 5000 \
  --batch
```

### 3. Monitor Progress

Set up monitoring to check batch status:

```bash
# Create a monitoring script
while true; do
  anthropic batches get <batch_id>
  sleep 3600  # Check every hour
done
```

### 4. Backup Batch Files

Always keep copies of batch request files:

```bash
# Backup before submitting
cp data/batch_requests/*.jsonl backups/
```

---

## Cost Savings Calculator

| Interviews | Real-time Cost (Claude 4.5 Sonnet) | Batch Cost | Savings |
|------------|-------------------------------------|------------|---------|
| 100 | $3.90 | $1.95 | $1.95 |
| 500 | $19.50 | $9.75 | $9.75 |
| 1,000 | $39.00 | $19.50 | $19.50 |
| 5,000 | $195.00 | $97.50 | $97.50 |
| 10,000 | $390.00 | $195.00 | **$195.00** |

**Formula:**
- Input tokens: 3,000 per interview
- Output tokens: 2,000 per interview
- Claude 4.5 Sonnet: $3/$15 per 1M tokens (real-time)
- Claude 4.5 Sonnet: $1.5/$7.5 per 1M tokens (batch)

---

## FAQ

**Q: Can I cancel a batch?**
A: Yes, use `anthropic batches cancel <batch_id>` or equivalent for your provider.

**Q: Can I get results faster than 24 hours?**
A: Sometimes batches complete in 6-12 hours, but 24 hours is typical.

**Q: What happens if a batch fails?**
A: You can resubmit failed requests. Check the error field in results.

**Q: Can I mix providers in one batch?**
A: No, each batch file is provider-specific.

**Q: Is batch mode suitable for real-time chat?**
A: No, use real-time API for interactive applications.

---

## Summary

**Batch API is ideal when:**
- ✅ Running 100+ interviews
- ✅ Cost is more important than speed
- ✅ You can wait 24 hours
- ✅ Processing large datasets

**Use Real-time API when:**
- ✅ Need results immediately
- ✅ Running <100 interviews
- ✅ Testing and debugging
- ✅ Interactive development

**Cost Savings:** Up to **50% discount** on all API calls

**Processing Time:** ~24 hours (typical)

**Next Steps:**
1. Run `python scripts/interactive_interviews.py`
2. Enable batch mode when prompted
3. Follow provider-specific submission instructions above
4. Wait for results (~24 hours)
5. Process batch output files
