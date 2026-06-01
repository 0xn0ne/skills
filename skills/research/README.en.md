<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/Tests-45%20Topics%20%E2%9C%85-brightgreen)

</div>

<!-- PROJECT LOGO -->
<div align="center">
  <h1>Research Skill</h1>
  <p><strong>Deep Research with Mechanical Verification</strong></p>
  <p>Think Freely · Record Structurally · Verify Mechanically · Report Honestly</p>
</div>

---

## Language

[简体中文](./README.md) | English

---

## Table of Contents

<details>
<summary>Expand Table of Contents</summary>

- [Introduction](#introduction)
- [Core Philosophy](#core-philosophy)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Workflow](#workflow)
- [Experimental Data](#experimental-data)
- [Known Gaps](#known-gaps)
- [File Structure](#file-structure)
- [Acknowledgments](#acknowledgments)

</details>

---

## Introduction

Research Skill is not a search engine wrapper — it is a **research consultant + mechanical verification** system.

It enables AI Agents to work like professional research analysts: first understand the user's real needs, then conduct multi-dimensional deep research, and finally ensure report quality through structured ledgers and script-based verification.

**Core Problem Solved:**

| Traditional Search Skills | Research Skill |
|---|---|
| Directly answer surface questions | First determine if the question is correct, then answer |
| Agent self-checks report quality | Script-based mechanical verification with 26 gates |
| Single-round search output | 4-round progressive search (50+ queries) |
| No source traceability | Structured ledger, every conclusion traceable |
| No hypothesis validation | Hypotheses must evolve (confirmed/falsified/mutated) |

---

## Core Philosophy

```
Think freely. Record structurally. Verify mechanically. Report honestly.
```

### Three-Layer Design

```
┌─────────────────────────────────────────────┐
│  SOUL.md — Identity Layer                   │
│  "You are a research consultant,            │
│   not a search engine"                      │
│  Defines: Intent Archaeologist ·            │
│           Strategic Research Consultant     │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  SKILL.md — Control Layer                   │
│  7-Phase Workflow · 14 Hard Rules ·         │
│  3 Operating Zones                          │
│  Zone A: Free Exploration                   │
│  Zone B: Structural Guidance                │
│  Zone C: Hard Gates (No Free Judgment)      │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  research_store.py — Verification Layer     │
│  26 Verification Gates ·                    │
│  Structured Ledger · Auto-Generated Report  │
│  Commands: init → add-source → verify →     │
│            report                           │
└─────────────────────────────────────────────┘
```

### Division of Responsibilities

| Task | Owner |
|---|---|
| User intent inference | Agent |
| Research dimension discovery | Agent |
| Commercial/strategic insights | Agent |
| Contradiction explanation | Agent |
| Source & recommendation recording | Agent writes to structured ledger |
| T1/T2 ratio calculation | Script |
| Trust Badge generation | Script |
| Report status capping | Script verification result |
| Final report | `generate-report` command |

---

## Architecture

### Research Workflow Overview

```
User Question
    │
    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Phase 0-1   │    │  Phase 2     │    │  Phase 3     │
│  Intent      │───▶│  Research    │───▶│  4-Round     │
│  Analysis    │    │  Plan        │    │  Search      │
│  Contradiction│   │  Dimension   │    │  50+ Queries │
│  Detection   │    │  Matrix      │    │  Progressive │
│  Audience    │    │  Hypothesis  │    │  Deepening   │
└──────────────┘    └──────────────┘    └──────┬───────┘
                                               │
                                               ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Phase 6     │    │  Phase 5     │    │  Phase 4     │
│  Report      │◀───│  Mechanical  │◀───│  Synthesis   │
│  Generation  │    │  Verification│    │  Hypothesis  │
│  Self-Review │    │  26 Gates    │    │  Evolution   │
│  Delivery    │    │  Trust Badge │    │  Red Team    │
└──────────────┘    └──────────────┘    └──────────────┘
```

### Source Tier System

```
┌─────────────────────────────────────────────┐
│  T1 — Highest Credibility                   │
│  ├── T1_Academic  Peer-reviewed papers      │
│  ├── T1_Official  Official docs, filings    │
│  └── T1_Data      Authoritative datasets    │
├─────────────────────────────────────────────┤
│  T2 — Professional Credibility              │
│  ├── T2_Creator   Practitioner writeups     │
│  └── T2_Data      Industry data             │
├─────────────────────────────────────────────┤
│  T3 — Synthesis Credibility                 │
│  └── T3_Synthesis Expert reviews            │
├─────────────────────────────────────────────┤
│  T4 — Community Credibility                 │
│  └── T4_Community Forums, social posts      │
├─────────────────────────────────────────────┤
│  T5 — Reference Credibility                 │
│  └── T5_Recap      Tutorials, summaries     │
└─────────────────────────────────────────────┘
```

### Claim Quality Grades

| Grade | Requirement | Use Case |
|---|---|---|
| **A** | 2+ T1/T2 primary sources | Supports action recommendations |
| **B** | 1+ T1/T2 primary source | Supports directional judgment |
| **C** | 1+ any source | Reference information |
| **D** | Weak evidence or single source | Background only |
| **F** | Unverified or falsified | Red team material |

---

## Quick Start

### Prerequisites

- Python 3.8+
- Any supported AI Agent platform

### 30-Second Deployment

```bash
# Clone the repository
git clone https://github.com/your-org/research-skill.git
cd research-skill

# Verify installation
python3 scripts/research_store.py --help

# Done! Now you can use it in your Agent
```

### Platform Adaptation

#### OpenCode

Place the skill directory under `.opencode/skills/`:

```bash
cp -r research-skill ~/.opencode/skills/research
```

Confirm the skill is loaded in `opencode.json`:

```json
{
  "skills": {
    "research": {
      "path": "~/.opencode/skills/research",
      "enabled": true
    }
  }
}
```

#### Claude Code / Codex

Place the skill directory under `.skills/` in your project root:

```bash
mkdir -p .skills
cp -r research-skill .skills/research
```

Reference the skill path in your conversation:

```
Please use the workflow in .skills/research/SKILL.md to research [topic]
```

#### Other Agent Platforms

Any Agent platform that supports file reading can use this skill. Just ensure the Agent can:

1. Read `SKILL.md` to understand the workflow
2. Execute `scripts/research_store.py` for verification
3. Write to `.research/` directory for report storage

### Usage Example

```
User: Research the industrialization progress of solid-state batteries

Agent Internal Flow:
1. Read SKILL.md → Load workflow
2. Phase 0: Identify audience (technical decision-maker)
3. Phase 1: Analyze intent (tech selection + investment reference)
4. Phase 2: Create research plan (5 dimensions)
5. Phase 3: 4-round search, 50+ queries
6. Phase 4: Extract 20+ claims, hypothesis evolution
7. Phase 5: Verify → Decision-grade PASS
8. Phase 6: Generate report → .research/*.final.md
9. Deliver: Return report path + 3 bullet summary
```

---

## Workflow

### 7 Phases Overview

| Phase | Name | Core Task | Output |
|---|---|---|---|
| Phase 0 | Audience Detection | Identify reader role, adapt report style | Audience tag |
| Phase 1 | Intent Analysis | Uncover underlying needs, detect contradictions | Intent Frame |
| Phase 2 | Research Plan | Dimension matrix, hypothesis design | Research blueprint |
| Phase 3 | 4-Round Search | R1 Discovery → R2 Quantitative → R3 Implementation → R4 Verification | 50+ sources |
| Phase 4 | Synthesis | Claims grading, hypothesis evolution, red team debate | Structured ledger |
| Phase 5 | Mechanical Verification | 26 verification gates | Trust Badge |
| Phase 6 | Report Generation | Generate report, self-review optimization | Final report |
| Phase 7 | Delivery | Return path + status + 3 bullets | Delivery receipt |

### 4-Round Search Strategy

```
Round 1: Discovery
  ├── Frameworks, concepts, terminology
  ├── 2+ sources per dimension
  └── Minimum 15 searches

Round 2: Quantitative
  ├── Numbers, benchmarks, thresholds
  ├── Risk factors
  └── Minimum 15 searches

Round 3: Implementation
  ├── How-to, cross-domain insights
  ├── Hypothesis status changes
  └── Minimum 10 searches

Round 4: Verification
  ├── Stress-test, cross-validation
  ├── Expert disagreements
  └── Minimum 10 searches
```

### 26 Verification Gates

| Category | Gate | Description |
|---|---|---|
| **Structure** | `access_trace_consistency` | Source access status consistency |
| | `claim_source_integrity` | Claim source completeness |
| | `recommendation_trace` | Recommendation traceability |
| | `narrative_completeness` | Narrative section completeness |
| | `empty_ledger` | Ledger non-empty |
| **Quality** | `t1t2_ratio` | T1/T2 source ratio ≥ 50% |
| | `claim_grade_distribution` | A/B grade claim distribution |
| | `source_dominance` | Single source contribution ≤ 60% |
| | `source_diversity` | Source types ≥ 3 |
| | `numeric_evidence_strength` | Numeric evidence strength |
| **Logic** | `thesis_narrative` | Thesis-narrative consistency |
| | `edge_cases` | Edge case coverage |
| | `research_closure` | Closure search completeness |
| | `scope_fidelity` | Semantic drift detection |
| **Language** | `language_alignment` | Content language matches declaration |
| **Red Team** | `red_team_quality` | Red team debate quality |
| **Hypothesis** | `hypothesis_tracking` | Hypothesis evolution tracking |
| **Coverage** | `subquestion_coverage` | Subquestion coverage |
| | `prompt_item_coverage` | Prompt item coverage |
| | `claim_subquestion_trace` | Claim-subquestion mapping |
| **Commercial** | `commercial_source_diversity` | Commercial source diversity |
| | `vendor_bias` | Vendor bias detection |
| | `cross_validation` | Cross-validation |
| **Other** | `weak_claim_usage` | Weak claim usage |
| | `recommendation_actor_scope` | Recommendation actor scope |
| | `language_alignment` | Language alignment |

---

## Experimental Data

### Test Overview

9 rounds of systematic testing covering 45 research topics across 35+ industries.

| Round | Topics | Success Rate | Key Finding |
|---|---|---|---|
| R1-R5 | 25 | 40-60% | Baseline established, script bugs found |
| R6-R7 | 10 | 20-40% | Fix verification, report quality improved |
| R8 | 5 | 40% | Step-by-step import API effective |
| R9 | 5 | **100%** | All passed, first 100% success |

### Core Metric Improvements

| Metric | Before | After | Improvement |
|---|---|---|---|
| Phase Check Log written | 0% | 100% | +100% |
| Red Team in ledger | 0% | 100% | +100% |
| source_excerpt non-empty | 80% | 100% | +20% |
| Hypothesis diversity | Low | High | Significant |
| Overall success rate | 40% | 100% (R9) | +60% |

### Best Report Cases

**CCUS Carbon Capture (R6)**
- Verification: Decision-grade PASS
- T1/T2 ratio: 68.2% (15/22 sources)
- Claims: 5 A-grade, 11 B-grade, 4 C-grade
- Hypothesis evolution: 1 falsified + 3 mutated

**Sodium-Ion Battery Industrialization (R9)**
- Verification: Decision-grade PASS (26/26 gates)
- Key finding: CATL 175Wh/kg + 10,000 cycles
- Cost reduced to 0.35-0.40 CNY/Wh

### Dynamic Thresholds

Different scenarios use different T1/T2 ratio thresholds:

| Threshold | T1/T2 Ratio | Use Case |
|---|---|---|
| `default` | 50% | Standard scenarios |
| `commercial` | 20% | Vendor comparison, market analysis |
| `practitioner` | 10% | Emerging tech, no academic literature |
| `emergent` | 35% | Rapidly evolving fields |
| `breaking` | 30% | Breaking news |

---

## Known Gaps

### 1. JSON Construction Complexity

**Problem:** Complex topics produce batch JSON exceeding 30,000 characters, making reliable single-build construction nearly impossible for LLMs.

**Data:** ~60% of failures in R1-R8 stemmed from JSON construction errors (escaping, formatting, missing fields).

**Mitigation:** Step-by-step import API (`add-source`, `add-claim`, etc.) provided — each step verified independently, failure only affects one record.

**Residual:** Some Agents still prefer one-time batch JSON construction over step-by-step import.

### 2. Gate Gaming

**Problem:** Agents downgrade B-grade claims to C-grade to pass `claim_source_integrity` gate.

**Data:** In R6, an Agent wrote "all downgraded to C to meet claim_source_integrity" in Self-Check.

**Mitigation:** Explicit prohibition added to SKILL.md: "Never downgrade claim grades for gate compliance."

**Residual:** Cannot fully prevent implicit downgrading behavior.

### 3. Shallow Implementation Recommendations

**Problem:** Some reports' Implementation Roadmaps contain only directional suggestions ("should increase investment") without concrete first steps.

**Data:** In R5, 3/5 reports lacked executable steps within 30 days.

**Mitigation:** Added 5 implementation depth checks (30-day first step, responsible party, MVP definition, etc.).

**Residual:** Agent understanding of "what constitutes a good implementation recommendation" still needs improvement.

### 4. Chat Compliance

**Problem:** Agents tend to output report content in chat rather than just returning the delivery receipt.

**Data:** ~33% of failures came from chat compliance violations.

**Mitigation:** SKILL.md explicitly states "Chat is a delivery receipt" with strict delivery templates.

**Residual:** This is an Agent behavioral habit that cannot be fully solved through documentation.

### 5. task_type_framework Keyword Matching

**Problem:** Gate regex may fail to match industry-specific vocabulary (e.g., biotech, food science terms).

**Data:** In R9, the carbon fiber composites report triggered Advisory mode due to `cross_validation` gate.

**Mitigation:** SKILL.md guides Agents to proactively annotate with standard keywords in narratives.

**Residual:** Keyword matching logic still has room for optimization.

---

## File Structure

```
research-skill/
├── SKILL.md                    # Control layer: workflow definition
├── SOUL.md                     # Identity layer: Agent role definition
├── README.md                   # Chinese documentation
├── README.en.md                # English documentation (this file)
├── scripts/
│   └── research_store.py       # Verification layer: ledger & gate script
├── assets/
│   └── batch-ledger-template.json  # Batch import template
├── references/
│   ├── audience-guide.md       # Audience adaptation guide
│   ├── domain-analysis.md      # Domain analysis requirements
│   ├── fallback.md             # Fallback when script unavailable
│   ├── field-reference.md      # Field reference documentation
│   ├── gate-specs.md           # Gate specification
│   ├── phase-checks.md         # Phase check templates
│   ├── phase4-details.md       # Phase 4 detailed guide
│   ├── report-template.md      # Report template
│   ├── search-strategy.md      # Search strategy guide
│   └── task-type-frameworks.md # Task type frameworks
└── .research/                  # Research output directory (auto-generated)
    ├── *.final.md              # Final report
    ├── *.advisory.md           # Advisory report
    ├── *.ledger.json           # Structured ledger
    └── *.temp.md               # Working template
```

## Report Status

| Status | Meaning | Decision-Ready?|
|---|---|---|
| `Decision-grade` | Ledger verified, main recommendations evidence-backed | Yes |
| `Advisory Research` | Evidence below threshold, but structurally complete | Reference only |
| `Evidence Gap Report` | Research valuable, but evidence insufficient | No |
| `Partial` | Some findings useful, but cannot support main decision | No |
| `Draft — ledger inconsistent` | Ledger inconsistency | No |

---

## Acknowledgments

This skill's design was inspired by:

- [Best-README-Template](https://github.com/othneildrew/Best-README-Template) — README structure reference
- Structured research methodology — from years of enterprise consulting and academic research practice
- Mechanical verification philosophy — from CI/CD gate practices in software engineering

---

<div align="center">
  <p><strong>Think Freely · Record Structurally · Verify Mechanically · Report Honestly</strong></p>
  <p><a href="#readme-top">Back to Top</a></p>
</div>
