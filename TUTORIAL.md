# Synthetic Gravidas Pipeline - Complete Tutorial

This tutorial guides you through the entire process of generating 10,000 synthetic pregnant personas with matched health records and conducting AI-powered interviews.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Step 1: Retrieve Personas](#step-1-retrieve-personas)
4. [Step 2: Setup and Run Synthea](#step-2-setup-and-run-synthea)
5. [Step 3: Match Personas to Health Records](#step-3-match-personas-to-health-records)
6. [Step 4: Conduct AI Interviews](#step-4-conduct-ai-interviews)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Usage](#advanced-usage)

---

## Prerequisites

### Software Requirements

- **Python 3.8+**: Check with `python --version`
- **Java 11+**: Required for Synthea. Check with `java -version`
- **Git**: For cloning Synthea repository
- **At least one AI API key**: Claude, OpenAI, or Gemini

### System Requirements

- **Disk Space**: At least 10GB free for data storage
- **RAM**: 8GB minimum, 16GB recommended
- **Internet Connection**: For downloading datasets and API calls

---

## Initial Setup

### 1. Install Python Dependencies

```bash
# Navigate to project directory
cd /home/user/202511-Gravidas

# Install required packages
pip install -r requirements.txt
```

### 2. Configure API Keys

Edit the configuration file with your API keys:

```bash
# Open config file in your editor
nano config/config.yaml
```

Replace the placeholder API keys with your actual keys:

```yaml
api_keys:
  claude:
    api_key: "sk-ant-xxxxxxxxxxxxx"  # Your actual Claude API key
  openai:
    api_key: "sk-xxxxxxxxxxxxx"      # Your actual OpenAI API key
  gemini:
    api_key: "xxxxxxxxxxxxx"         # Your actual Gemini API key
```

**Note**: You only need to configure the API key for the AI provider you plan to use.

### 3. Create Log Directory

```bash
mkdir -p logs
```

---

## Step 1: Retrieve Personas

This step downloads 10,000 female personas in fertile age (12-60 years) from the HuggingFace FinePersonas dataset.

### Run the Script

```bash
python scripts/01_retrieve_personas.py
```

### What This Does

1. Connects to HuggingFace dataset repository
2. Filters personas by:
   - Gender: Female
   - Age range: 12-60 years
   - Quality checks
3. Downloads 10,000 personas
4. Saves to `data/personas/personas.json`

### Expected Output

```
[INFO] Connecting to HuggingFace dataset...
[INFO] Filtering personas (age 12-60, female)...
[INFO] Found 45,231 matching personas
[INFO] Selecting 10,000 personas...
[INFO] Saving to data/personas/personas.json
[SUCCESS] Retrieved 10,000 personas
```

### Verify Results

```bash
# Check the file was created
ls -lh data/personas/personas.json

# View first few entries
python -c "import json; data=json.load(open('data/personas/personas.json')); print(json.dumps(data[:2], indent=2))"
```

---

## Step 2: Setup and Run Synthea

Synthea generates realistic synthetic patient health records. We'll configure it to generate pregnancy-related records.

### 2.1 Install Synthea

```bash
# Clone Synthea repository
cd /home/user/202511-Gravidas
git clone https://github.com/synthetichealth/synthea.git
cd synthea

# Test installation (on Linux/Mac)
./run_synthea -h

# On Windows, use:
# .\run_synthea.bat -h
```

If you see the help text, Synthea is installed correctly.

### 2.2 Configure Synthea for Pregnancy Records

See [docs/SYNTHEA_SETUP.md](docs/SYNTHEA_SETUP.md) for detailed configuration instructions.

Quick configuration:

```bash
# Edit Synthea properties
cd /home/user/202511-Gravidas/synthea
nano src/main/resources/synthea.properties
```

Enable pregnancy module:

```properties
# Enable specific modules
generate.only_modules = pregnancy,prenatal_care,maternal_health
```

### 2.3 Generate Health Records

```bash
# Return to project directory
cd /home/user/202511-Gravidas

# Run the health records generation script
python scripts/02_generate_health_records.py
```

### What This Does

1. Reads the downloaded personas
2. Generates matching demographic profiles for Synthea
3. Runs Synthea 10,000 times with pregnancy-focused modules
4. Filters records by pregnancy-related SNOMED codes:
   - 77386006 (Pregnancy)
   - 72892002 (Normal pregnancy)
   - 249166004 (Antenatal care)
   - And others
5. Converts FHIR records to simplified JSON format
6. Saves to `data/health_records/`

### Expected Output

```
[INFO] Loading personas from data/personas/personas.json
[INFO] Found 10,000 personas
[INFO] Generating health records with Synthea...
[PROGRESS] Generated 1000/10000 records...
[PROGRESS] Generated 2000/10000 records...
...
[SUCCESS] Generated 10,000 health records
[INFO] Records saved to data/health_records/
```

**Note**: This step may take 2-4 hours depending on your system.

### Verify Results

```bash
# Check health records directory
ls -lh data/health_records/

# Count generated files
ls data/health_records/*.json | wc -l
```

---

## Step 3: Match Personas to Health Records

This step intelligently matches each persona to a health record based on age compatibility and socioeconomic factors.

### Run the Matching Script

```bash
python scripts/03_match_personas_records.py
```

### What This Does

1. Loads all 10,000 personas
2. Loads all 10,000 health records
3. Calculates compatibility scores based on:
   - **Age Compatibility (60% weight)**:
     - Exact match: 100%
     - Within 2 years: 90%
     - Within 5 years: 70%
     - Beyond 5 years: Lower scores
   - **Socioeconomic Factors (40% weight)**:
     - Education level
     - Occupation category
     - Income bracket
     - Marital status
4. Creates optimal matches using weighted algorithm
5. Saves matched pairs to `data/matched/matched_personas.json`

### Expected Output

```
[INFO] Loading 10,000 personas...
[INFO] Loading 10,000 health records...
[INFO] Computing compatibility matrix...
[INFO] Running matching algorithm (weighted)...
[PROGRESS] Matched 1000/10000 pairs...
[PROGRESS] Matched 2000/10000 pairs...
...
[SUCCESS] Matched 10,000 persona-record pairs
[INFO] Average age difference: 1.3 years
[INFO] Average socioeconomic similarity: 0.87
[INFO] Saved to data/matched/matched_personas.json
```

### Verify Results

```bash
# Check matched data file
ls -lh data/matched/matched_personas.json

# View sample matched pair
python -c "import json; data=json.load(open('data/matched/matched_personas.json')); print(json.dumps(data[0], indent=2))"
```

---

## Step 4: Conduct AI Interviews

Now we can conduct structured interviews with our synthetic personas using their combined persona and health record data.

### 4.1 Prepare Interview Protocol

Interview protocols are stored in `Script/interview_protocols/`. A default protocol is provided.

View the default protocol:

```bash
cat Script/interview_protocols/prenatal_care.json
```

### 4.2 Choose Your AI Provider

You can use Claude, OpenAI, or Gemini. Edit the config or use command-line arguments.

### 4.3 Run Interviews

**Using Claude:**
```bash
python scripts/04_conduct_interviews.py \
  --model claude \
  --protocol Script/interview_protocols/prenatal_care.json \
  --count 10
```

**Using OpenAI:**
```bash
python scripts/04_conduct_interviews.py \
  --model openai \
  --protocol Script/interview_protocols/prenatal_care.json \
  --count 10
```

**Using Gemini:**
```bash
python scripts/04_conduct_interviews.py \
  --model gemini \
  --protocol Script/interview_protocols/prenatal_care.json \
  --count 10
```

### Command-Line Arguments

- `--model`: AI provider (claude, openai, or gemini)
- `--protocol`: Path to interview protocol JSON file
- `--count`: Number of interviews to conduct (default: 10)
- `--output`: Output directory (default: data/interviews/)
- `--batch-size`: Parallel interview count (default: 10)

### What This Does

1. Loads matched persona-record pairs
2. Loads the interview protocol
3. For each selected persona:
   - Creates a context with persona details and health history
   - Initializes AI model with system prompt
   - Conducts structured interview following protocol questions
   - Records responses
   - Saves complete transcript
4. Saves all interviews to `data/interviews/`

### Expected Output

```
[INFO] Loading matched personas...
[INFO] Loading interview protocol: prenatal_care.json
[INFO] Using AI provider: claude (claude-3-5-sonnet-20241022)
[INFO] Conducting 10 interviews...

[INTERVIEW 1/10] Persona: Emma Johnson, Age: 28
[AI] Hello Emma, thank you for joining me today...
[Progress] Question 1/15 completed...
[SUCCESS] Interview 1 completed. Saved to data/interviews/interview_0001.json

[INTERVIEW 2/10] Persona: Maria Garcia, Age: 32
...
```

### Verify Results

```bash
# List interview transcripts
ls -lh data/interviews/

# View a sample interview
cat data/interviews/interview_0001.json | python -m json.tool | head -50
```

---

## Troubleshooting

### Common Issues

#### 1. HuggingFace Connection Errors

**Error**: `ConnectionError: Unable to reach HuggingFace`

**Solution**:
- Check internet connection
- Verify HuggingFace is accessible: https://huggingface.co
- If using private datasets, ensure token is configured in config.yaml

#### 2. Synthea Java Errors

**Error**: `java.lang.OutOfMemoryError`

**Solution**:
Increase Java heap size:
```bash
export JAVA_OPTS="-Xmx4g"
./run_synthea
```

#### 3. API Rate Limits

**Error**: `RateLimitError: API rate limit exceeded`

**Solution**:
- Reduce `batch_size` in config.yaml
- Add delays between API calls
- Upgrade API plan for higher limits

#### 4. Insufficient Disk Space

**Error**: `OSError: No space left on device`

**Solution**:
- Free up disk space
- Change data paths in config.yaml to larger drive
- Reduce target persona count

---

## Advanced Usage

### Custom Interview Protocols

Create your own interview protocol JSON file:

```json
{
  "name": "Custom Protocol",
  "version": "1.0",
  "description": "Your custom interview questions",
  "questions": [
    {
      "id": "q1",
      "text": "Your question here",
      "type": "open-ended",
      "required": true
    }
  ]
}
```

Save to `Script/interview_protocols/custom_protocol.json` and use:

```bash
python scripts/04_conduct_interviews.py \
  --protocol Script/interview_protocols/custom_protocol.json
```

### Batch Processing All Personas

To interview all 10,000 personas:

```bash
python scripts/04_conduct_interviews.py \
  --model claude \
  --protocol Script/interview_protocols/prenatal_care.json \
  --count 10000 \
  --batch-size 50
```

**Warning**: This will consume significant API credits and take many hours.

### Filtering Personas for Interviews

Edit `scripts/04_conduct_interviews.py` to add filters:

```python
# Only interview personas in specific age range
filtered_personas = [p for p in personas if 25 <= p['age'] <= 35]

# Only interview personas with specific conditions
filtered_personas = [p for p in personas if 'diabetes' in p['health_record']['conditions']]
```

### Exporting Results

Export interviews to CSV for analysis:

```bash
python scripts/utils/export_interviews.py \
  --input data/interviews/ \
  --output data/interviews_export.csv
```

---

## Next Steps

- Analyze interview results
- Train ML models on synthetic data
- Create visualization dashboards
- Extend interview protocols
- Integrate with other research tools

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review documentation in `docs/`
3. Open an issue on GitHub

---

## Summary

You've now completed the entire pipeline:

1. ✅ Retrieved 10,000 female personas (age 12-60)
2. ✅ Generated 10,000 pregnancy-related health records
3. ✅ Matched personas to records by age and socioeconomic factors
4. ✅ Conducted AI-powered interviews with synthetic personas

Your synthetic gravidas dataset is ready for research and analysis!
