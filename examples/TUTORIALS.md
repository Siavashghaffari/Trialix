# Trialix Tutorials

Welcome to the Trialix tutorial series! These interactive tutorials will teach you how to use Trialix for clinical trial enrichment analysis through hands-on examples and real-world scenarios.

## 📚 Tutorial Overview

### Tutorial 1: Basic Workflow (30 minutes)
**File:** `tutorial_01_basic_workflow.py`

**What you'll learn:**
- How to load and validate clinical trial data
- How to identify predictive biomarkers
- How to interpret odds ratios, p-values, and AUC
- How to optimize biomarker cutoffs
- How to generate enrollment criteria
- How to visualize and export results

**Who should take this:**
- First-time Trialix users
- Biostatisticians new to enrichment analysis
- Anyone wanting a comprehensive introduction

**Key takeaways:**
- Complete workflow from data to recommendations
- Understanding what the statistics mean
- How enrichment improves trial efficiency

---

### Tutorial 2: Optimizing Enrollment Criteria (45 minutes)
**File:** `tutorial_02_optimizing_criteria.py`

**What you'll learn:**
- How to balance response rate vs. enrollment feasibility
- Comparing maximum, moderate, and minimal enrichment strategies
- Trade-offs between trial efficiency and recruitment
- How to choose the right strategy for your trial
- Sample size and feasibility calculations

**Who should take this:**
- Trial designers planning Phase III studies
- Clinical operations teams
- Anyone making enrollment strategy decisions

**Key takeaways:**
- Enrichment is a spectrum, not binary
- More enrichment ≠ always better
- Data-driven strategy selection

---

### Tutorial 3: Interpreting Statistical Results (40 minutes)
**File:** `tutorial_03_interpreting_results.py`

**What you'll learn:**
- Deep dive into odds ratios and confidence intervals
- What AUC really means and when to trust it
- Understanding p-values and multiple testing
- Red flags indicating unreliable results
- How to communicate statistics to non-statisticians

**Who should take this:**
- Anyone presenting results to clinical teams
- Statisticians wanting to improve communication
- Regulatory affairs professionals
- People who want to truly understand the statistics

**Key takeaways:**
- When to trust (and not trust) your results
- How to spot false positives and overfitting
- Plain-language explanations of complex statistics

---

### Tutorial 4: Complete Case Study (60 minutes)
**File:** `tutorial_04_complete_case_study.py`

**What you'll learn:**
- End-to-end scenario: rescuing a failed Phase IIb trial
- Finding responder subgroups in heterogeneous data
- Designing Phase III enrichment strategy
- Cost-benefit analysis and ROI calculations
- Creating board presentations
- Real-world decision making

**Who should take this:**
- Anyone working on real trial programs
- Leadership teams making go/no-go decisions
- People wanting to see Trialix in action
- Those who learn best from realistic scenarios

**Key takeaways:**
- How enrichment can salvage failed programs
- Complete workflow from failure to success
- Business implications of enrichment strategies

---

## 🚀 Getting Started

### Prerequisites

1. **Install Trialix:**
   ```bash
   pip install trialix
   ```

2. **Download sample data:**
   ```bash
   # The oncology_trial.csv file should be in the examples/ folder
   # If not, generate it:
   python examples/generate_sample_data.py
   ```

3. **Choose your tutorial:**
   - **New to Trialix?** Start with Tutorial 1
   - **Already familiar?** Jump to Tutorial 2 or 3
   - **Want a real example?** Go straight to Tutorial 4

### Running the Tutorials

All tutorials are interactive Python scripts. Run them from the command line:

```bash
# Tutorial 1
python examples/tutorial_01_basic_workflow.py

# Tutorial 2
python examples/tutorial_02_optimizing_criteria.py

# Tutorial 3
python examples/tutorial_03_interpreting_results.py

# Tutorial 4
python examples/tutorial_04_complete_case_study.py
```

Each tutorial will:
- Explain concepts step-by-step
- Show code examples
- Display results
- Pause for you to review (press Enter to continue)
- Generate outputs you can examine

---

## 📖 Tutorial Structure

Each tutorial follows this format:

1. **Introduction** - Scenario and learning objectives
2. **Step-by-step walkthrough** - Interactive analysis with explanations
3. **Results interpretation** - What the numbers mean
4. **Practical insights** - How to apply to your work
5. **Summary** - Key takeaways and next steps

---

## 💡 Learning Path Recommendations

### For Beginners:
```
Tutorial 1 → Tutorial 3 → Tutorial 4 → Tutorial 2
```
Learn basics → Understand statistics → See real application → Optimize strategies

### For Experienced Users:
```
Tutorial 2 → Tutorial 4
```
Jump straight to optimization and real-world scenarios

### For Presenters/Communicators:
```
Tutorial 3 → Tutorial 1 → Tutorial 4
```
Focus on interpretation and communication

---

## 🎯 After Completing the Tutorials

You'll be ready to:

1. **Analyze your own data:**
   ```python
   from trialix import TrialEnrichment

   analyzer = TrialEnrichment(data="your_data.csv", outcome="response")
   analyzer.load_data()
   biomarkers = analyzer.find_biomarkers()
   criteria = analyzer.suggest_criteria()
   ```

2. **Make informed decisions:**
   - Choose appropriate enrichment strategies
   - Balance scientific and business considerations
   - Present results confidently to stakeholders

3. **Avoid common pitfalls:**
   - Recognize statistical red flags
   - Validate findings appropriately
   - Consider feasibility constraints

---

## 📊 Tutorial Outputs

Each tutorial generates output files you can examine:

### Tutorial 1:
- `tutorial_01_results/` - Analysis results (CSV, JSON, TXT)
- `tutorial_01_plots/` - Visualizations (PNG)

### Tutorial 2:
- Console output showing strategy comparisons
- No files generated (focuses on concepts)

### Tutorial 3:
- Console output with interpretation guidance
- No files generated (educational focus)

### Tutorial 4:
- `tutorial_04_board_presentation/` - Complete presentation package
- `tutorial_04_board_presentation/plots/` - Board-ready visualizations

---

## ❓ Common Questions

**Q: Do I need to complete tutorials in order?**
A: Not required, but Tutorial 1 provides foundation. See "Learning Path Recommendations" above.

**Q: How long does each tutorial take?**
A: 30-60 minutes each, but you can pause and resume anytime.

**Q: Can I use my own data?**
A: Yes! After completing tutorials, simply replace `oncology_trial.csv` with your data file.

**Q: Do tutorials modify my data?**
A: No. All tutorials work on copies and only create output files.

**Q: I got stuck. Where can I get help?**
A: Check the main README.md or open an issue on GitHub.

---

## 🔍 What's Different About Each Tutorial?

| Tutorial | Focus | Best For | Difficulty |
|----------|-------|----------|------------|
| **1: Basic Workflow** | Complete introduction | First-time users | ⭐ Beginner |
| **2: Optimizing Criteria** | Strategy selection | Trial designers | ⭐⭐ Intermediate |
| **3: Interpreting Results** | Statistical literacy | Communicators | ⭐⭐ Intermediate |
| **4: Case Study** | Real-world application | Decision makers | ⭐⭐⭐ Advanced |

---

## 🎓 Learning Objectives by Tutorial

### Tutorial 1: Basic Workflow
- [ ] Load and validate trial data
- [ ] Run biomarker discovery analysis
- [ ] Interpret statistical outputs
- [ ] Generate enrollment criteria
- [ ] Create visualizations
- [ ] Export results for stakeholders

### Tutorial 2: Optimizing Criteria
- [ ] Understand enrichment trade-offs
- [ ] Compare multiple strategies
- [ ] Calculate feasibility metrics
- [ ] Make data-driven strategy choices
- [ ] Consider business implications

### Tutorial 3: Interpreting Results
- [ ] Explain odds ratios correctly
- [ ] Interpret confidence intervals
- [ ] Understand p-values and multiple testing
- [ ] Evaluate AUC for clinical utility
- [ ] Identify unreliable results
- [ ] Communicate to non-statisticians

### Tutorial 4: Case Study
- [ ] Analyze trial failure causes
- [ ] Identify responder subgroups
- [ ] Design rescue strategy
- [ ] Calculate costs and ROI
- [ ] Create board presentation
- [ ] Make go/no-go recommendations

---

## 💪 Hands-On Exercises

After each tutorial, try these exercises with your own data:

**After Tutorial 1:**
- Load your own trial data
- Identify top 3 biomarkers
- Generate one enrichment strategy

**After Tutorial 2:**
- Create 3 different strategies
- Calculate feasibility for each
- Choose the best one

**After Tutorial 3:**
- Review your biomarker results
- Check for red flags
- Write plain-language summary

**After Tutorial 4:**
- Apply full workflow to your data
- Create presentation for your team
- Calculate ROI for your program

---

## 📝 Notes

- All tutorials use the same sample dataset (`oncology_trial.csv`)
- Results are reproducible (fixed random seed in data generation)
- Tutorials are self-contained and can be run independently
- Interactive pauses allow time to understand concepts
- Generated outputs can be used as templates for your work

---

## 🚀 Ready to Start?

```bash
# Start with Tutorial 1
python examples/tutorial_01_basic_workflow.py
```

**Happy Learning!** 🎉

---

*For more information, see the main [README.md](../README.md) or visit the [GitHub repository](https://github.com/Siavashghaffari/Trialix/Trialix).*
