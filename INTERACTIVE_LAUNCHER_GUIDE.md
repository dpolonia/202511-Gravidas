# Interactive Workflow Launcher Guide

## 🎨 Visual Menu-Based Interface

No more command-line arguments! Just select from beautiful interactive menus.

---

## 🚀 Quick Start

Simply run:
```bash
python run_interactive_workflow.py
```

That's it! The launcher will guide you through every option.

---

## 📋 Menu Flow

### Welcome Screen
```
================================================================================
                  GRAVIDAS INTERACTIVE WORKFLOW LAUNCHER
================================================================================

Welcome!
This interactive launcher will guide you through configuring and running
the complete Gravidas synthetic data generation workflow.

You'll be asked to select:
  1. Workflow scale (number of personas, records, interviews)
  2. AI provider (Anthropic, OpenAI, Google, xAI)
  3. AI model (specific model within provider)
  4. Interview protocol (topic/focus area)
  5. Additional options

Press Ctrl+C at any time to cancel

Press Enter to begin...
```

---

### Step 1: Select Workflow Scale

You'll see a menu like this:

```
>>> Step 1: Select Workflow Scale

1. Quick Test - 10 personas, 10 records, 3 interviews (~7 min, $0.05)
2. Small Run - 25 personas, 25 records, 10 interviews (~30 min, $0.50)
3. Medium Run - 50 personas, 50 records, 25 interviews (~1.5 hrs, $2)
4. Standard Run - 100 personas, 100 records, 50 interviews (~3 hrs, $10)
5. Large Run - 500 personas, 500 records, 200 interviews (~15 hrs, $60)
6. Production Run - 1000 personas, 1000 records, 500 interviews (~40 hrs, $150)
7. Custom - Enter custom values

Select scale [1-7]:
```

**Just type the number and press Enter!**

If you choose **Custom (7)**, you'll be asked:
```
Number of personas (default 100): 150
Number of health records (default 150): 150
Number of interviews (default 50): 75
```

---

### Step 2: Select AI Provider

```
>>> Step 2: Select AI Provider

1. Anthropic Claude - Best for medical quality, nuanced responses
2. OpenAI GPT - Broad knowledge, structured outputs
3. Google Gemini - Fastest, large context, cost-effective
4. xAI Grok - Research applications, reasoning

Select provider [1-4]:
```

**Type 1, 2, 3, or 4**

---

### Step 3: Select Model

The menu changes based on your provider choice!

#### If you chose Anthropic (1):
```
>>> Step 3: Select Anthropic Model

1. claude-haiku-4-5 [Fast & Cheap] - $1/$5 per 1M tokens - Fastest Claude
2. claude-sonnet-4-5 [Recommended] - $3/$15 per 1M tokens - Best balance
3. claude-sonnet-4-5-20250929 [Specific Version] - $3/$15 per 1M tokens
4. claude-opus-4-1 [Premium Quality] - $15/$75 per 1M tokens - Highest quality
5. Use default - Let system choose best model

Select model [1-5]:
```

#### If you chose Google (3):
```
>>> Step 3: Select Google Model

1. gemini-2.5-flash [Recommended] - $0.15/$1.25 per 1M tokens - FASTEST
2. gemini-2.5-pro [High Quality] - $1.25/$10 per 1M tokens - Most capable
3. gemini-2.5-pro-long [Extended Context] - $2.50/$15 per 1M tokens - 200k+ context
4. gemini-3-pro-preview [Preview] - Next generation - Pricing TBD
5. Use default - Let system choose best model

Select model [1-5]:
```

---

### Step 4: Select Interview Protocol

```
>>> Step 4: Select Interview Protocol

1. Prenatal Care - Routine prenatal visits and care
2. High-Risk Pregnancy - Complications and advanced monitoring
3. Mental Health - Psychological wellbeing, mood disorders
4. Genetic Counseling - Genetic risks and family history
5. Postpartum Care - Post-birth recovery and newborn care
6. Pregnancy Experience - Overall pregnancy journey

Select interview protocol [1-6]:
```

---

### Step 5: Additional Options

```
>>> Step 5: Additional Options

Continue on error?
  If a stage fails, should the workflow continue with remaining stages?
  1. No  - Stop on first error (recommended)
  2. Yes - Continue even if stages fail

Select option [1-2]:
```

---

### Configuration Summary

After all selections, you'll see a summary:

```
================================================================================
                     WORKFLOW CONFIGURATION SUMMARY
================================================================================

Data Generation:
  Personas:       100
  Health Records: 100
  Interviews:     50

AI Configuration:
  Provider:       Anthropic
  Model:          claude-sonnet-4-5

Interview Settings:
  Protocol:       Prenatal Care

Options:
  Continue on error: No

Output:
  Results will be saved to: data/
  Archive will be created in: archives/

Estimated Time: 3.2 hours
Estimated Cost: $10.50 (approximate)

================================================================================
Ready to start workflow. This will begin generating data.
================================================================================

Start workflow now? [Y/n]:
```

Type **Y** and press Enter to start!

---

## 🎯 Example Usage Sessions

### Session 1: Quick Test
```
Step 1: Select scale [1-7]: 1
Step 2: Select provider [1-4]: 3
Step 3: Select model [1-5]: 1
Step 4: Select protocol [1-6]: 1
Step 5: Continue on error [1-2]: 1
Start workflow now? [Y/n]: Y
```
**Result:** Quick test with Google Gemini Flash

---

### Session 2: High-Quality Clinical Study
```
Step 1: Select scale [1-7]: 4
Step 2: Select provider [1-4]: 1
Step 3: Select model [1-5]: 4
Step 4: Select protocol [1-6]: 2
Step 5: Continue on error [1-2]: 1
Start workflow now? [Y/n]: Y
```
**Result:** Standard run with Claude Opus, high-risk pregnancy protocol

---

### Session 3: Custom Budget Run
```
Step 1: Select scale [1-7]: 7
  Number of personas (default 100): 200
  Number of health records (default 200): 200
  Number of interviews (default 50): 100
Step 2: Select provider [1-4]: 3
Step 3: Select model [1-5]: 1
Step 4: Select protocol [1-6]: 3
Step 5: Continue on error [1-2]: 2
Start workflow now? [Y/n]: Y
```
**Result:** Custom 200-persona study with Gemini, mental health focus

---

## 💡 Features

✅ **No Command-Line Arguments** - Just type numbers
✅ **Visual Menus** - Color-coded, easy to read
✅ **Cost & Time Estimates** - See before you run
✅ **Configuration Summary** - Review before starting
✅ **Smart Defaults** - Recommended options highlighted
✅ **Validation** - Can't enter invalid choices
✅ **Cancellable** - Press Ctrl+C anytime to quit
✅ **Error Handling** - Clear messages if something goes wrong

---

## 🆚 Comparison: Interactive vs Command-Line

### Old Way (Command-Line):
```bash
python run_complete_workflow.py \
  --personas 100 \
  --records 100 \
  --interviews 50 \
  --provider anthropic \
  --model claude-sonnet-4-5 \
  --protocol Script/interview_protocols/prenatal_care.json
```
**Need to remember:** All arguments, model names, file paths

### New Way (Interactive):
```bash
python run_interactive_workflow.py
```
**Just select:** Numbers from menus!

---

## 🎨 Color Coding

The interactive launcher uses colors to make things clear:

- **Cyan/Blue** - Headers and sections
- **Green** - Options and success messages
- **Yellow** - Prompts and warnings
- **Red** - Errors
- **Bold** - Important text

---

## 🔧 Keyboard Controls

| Key | Action |
|-----|--------|
| `1-9` | Select menu option |
| `Enter` | Confirm selection |
| `Ctrl+C` | Cancel/Exit |
| `Y/n` | Confirm/cancel final start |

---

## 📝 Tips

1. **Start with Quick Test** - Always test first with option 1
2. **Use Recommended Models** - Look for [Recommended] tag
3. **Review Summary** - Double-check before confirming
4. **Check Estimates** - Time and cost shown before starting
5. **Save Archives** - Results automatically archived

---

## 🚨 Troubleshooting

**Q: I made a mistake in selection, can I go back?**
A: Press Ctrl+C to cancel and start over.

**Q: What if I enter an invalid number?**
A: You'll be prompted to try again with a valid range.

**Q: Can I see what command will run?**
A: Yes! It's shown just before execution starts.

**Q: Where do results go?**
A: Same as command-line version - `data/` and `archives/`

---

## 🎯 Which Launcher to Use?

### Use Interactive Launcher When:
- You're new to the system
- You want to explore options
- You prefer visual menus
- You want to see cost/time estimates
- You're running one-off experiments

### Use Command-Line When:
- You know exactly what you want
- You're scripting/automating
- You're running multiple variations
- You want to save commands in scripts

**Both launchers produce identical results!**

---

## 📚 Related Documentation

- **Command-Line Version:** `run_complete_workflow.py --help`
- **Customization Guide:** `WORKFLOW_CUSTOMIZATION_GUIDE.md`
- **Quick Reference:** `WORKFLOW_QUICK_REFERENCE.md`
- **Project Overview:** `RPATRICIO.md`

---

## ✨ Try It Now!

```bash
python run_interactive_workflow.py
```

**Select option 1 for Quick Test to verify everything works!**

---

*Interactive Workflow Launcher - Making synthetic data generation as easy as 1-2-3!*
