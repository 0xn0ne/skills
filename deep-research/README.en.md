# Deep Research — Decision-Grade Research Skill

> Turn vague "research X" into a boardroom-ready decision report. 3-phase method (Task Card → Probe Search → 6-lens Decision) + Satisficing 4-C stop gate + 9 research tools, producing a **YES**/**NO**/**DEFER** + boundary conditions + counter-position + executable report.

[![version v9.0](https://img.shields.io/badge/version-v9.0-blue)](./SKILL.md) [![skill: deep-research](https://img.shields.io/badge/skill-deep--research-purple)](./SKILL.md) [![agent: opencode](https://img.shields.io/badge/agent-opencode-orange)](#) [![license: MIT](https://img.shields.io/badge/license-MIT-green)](#)

[简体中文](./README.md) | English

---

## Table of Contents

- [What is this / Who is it for](#what-is-this--who-is-it-for)
- [Value bullets](#value-bullets)
- [Quick start](#quick-start)
- [Workflow (3 phases + 9 tools)](#workflow-3-phases--9-tools)
- [Input / Output contract](#input--output-contract)
- [Before / After: why this skill](#before--after-why-this-skill)
- [Out-of-scope / Anti-patterns](#out-of-scope--anti-patterns)
- [Decision-grade features](#decision-grade-features)
- [Troubleshooting](#troubleshooting)
- [Versioning & upgrade](#versioning--upgrade)
- [References](#references)

---

## What is this / Who is it for

**Not**: a single-turn unconnected LLM answer; an "exploration" without evidence grading; an AI stream-of-consciousness you can't audit.

**Instead**: a **decision-grade deep-research framework** — splits a vague "research X" task into **Task Card → Probe Search → 6-lens Decision** 3 phases, terminates evidence collection via **Satisficing 4-C stop gate** (no infinite loops), terminates report quality via **8-item Decision-Readiness self-check** (including tool-data-fidelity audit), producing a report you can take straight to a decision meeting.

**Who is it for**:

| Role | Typical scenario |
| --- | --- |
| Decision-makers (CEO / PM / investor) | "Should we invest in X?" "Should we switch to vendor Y?" "Should we migrate off SaaS Z?" |
| Strategy researchers | Cross-domain opportunity scans, platform strategy, investability analyses |
| Tech leads | Vendor selection, architecture trade-offs, technical debt assessment |
| Founders | Product-market-fit validation, market entry, competitor analyses |

**Not for**: single-point fact lookup (use `web_search`), pure creative writing, real-time code debugging.

---

## Value bullets

- 🎯 **Task-card-first** — Frame phase mandates writing "goal / effort / audience / counter-evidence conditions" task card; Satisficing 4-C stop gate uses this checklist directly, killing the vague "I'll search until I'm satisfied" mode
- 🔍 **9 probe types + D1-D5 evaluation** — P1 scope / P2 primary / P3 comparison / P4 counter / P5 conflict / P6 risk / P7 temporal / P8 market / P9 decision; each round uses D1-D5 info-gain to decide "continue vs stop"
- 🧠 **ACH competing hypotheses** — list ≥ 2 mutually-exclusive hypotheses (e.g., "migrate / don't / defer"), grade all evidence by **diagnosticity** — high-diagnosticity can falsify alternatives, low-diagnosticity is background only
- 🛡️ **Independence principle** — hypothesis state transitions MUST be triggered by **external evidence**, not self-reasoning (kills "I thought about it, it's wrong" loops)
- 📊 **8-item self-check (incl. audit)** — pre-DELIVER mandatory: 30-sec retelling + verb-led opener + digit density + boundary conditions + explicit decision + Red Team + executable + **tool-data-fidelity (audit ≥5/7)**
- ⚖️ **4-level cognitive labels** — every claim tagged `[已确认]` / `[已公开]` / `[自推断]` / `[未验证]`; readers apply "trust-demotion" themselves
- 🔄 **Cross-platform** — Anthropic Claude Code / OpenCode / Cursor / Codex, all triggered via `SKILL.md` frontmatter

---

## Quick start

### Installation (3 ways)

```bash
# Method A · project-level (recommended) — team shares one version
git clone <skill-repo> ~/.config/opencode/skills/deep-research
```

### Minimal agent prompt template

```
You are a deep research consultant.

Research topic: [user's open-ended question]

Requirement: Produce a decision-grade deep research report.

Load this SKILL (absolute path): `.opencode/skills/deep-research/SKILL.md`

Follow the rules in SKILL.md strictly.
```

**Worked example**:

```
You are a deep research consultant.

Research topic: Should Apple replace OpenAI partnership with self-developed LLM in 2026 H2?

Requirement: Produce a decision-grade deep research report.

Load this SKILL: `.opencode/skills/deep-research/SKILL.md`
```

### Expected output

Output 1: `research/<topic-slug>-<YYYY-MM>.md` — 5-chapter structure + Sources Register + inline metadata

Output 2: `research/.cache/<topic-slug>-<YYYYMMDD>.json` — ledger (all evidence / hypothesis transitions / decision replayable)

Output 3: terminal print — explicit decision (**YES** / **NO** / **DEFER**) + 3-7 executable Who/What/When items + 3-5 Hold/Revert triggers

---

## Workflow (3 phases + 9 tools)

### 3-phase framework

```
┌─ Frame (Task card) ──┐   ┌─ Dig (Probe search) ──┐   ┌─ Decide (Decision) ──┐
│ • Goal / Effort      │ → │ • 9 probe types       │ → │ • 6-lens template    │
│ • Audience / Lens    │   │ • D1-D5 evaluation    │   │ • 8-item self-check  │
│ • Counter-evidence   │   │ • 4-C stop gate       │   │ • audit verification│
│ • Criteria checklist │   │ • ACH transitions     │   │ • Report delivery    │
└─────────────────────┘   └──────────────────────┘   └──────────────────────┘
```

### Phase 0 · Audience Detection (decision-grade **mandatory**)

Report audience determines output format naturally:

| Audience | Executive Summary focus | Section weights | Digit density |
| --- | --- | --- | --- |
| **Decision-makers** (CEO / board) | one-line verdict + boundaries + owners | Conclusions heaviest | ≥ 60 digits |
| **Practitioners** (PM / eng) | hypotheses + counter + rollout steps | Findings + Risks heavy | ≥ 40 digits |
| **Researchers / analysts** | methodology + evidence chain + data | Methodology + Sources heavy | ≥ 30 digits |

### Phase 1 · Frame · Task card (mandatory)

```markdown
## Task card
- Goal: what decision / understanding does the user need
- Effort: quick / standard / complex (decided after probe)
- Audience: decision-maker / practitioner / researcher / mixed
- Lens: decision / comparison / synthesis / scan / benchmark / exploratory
- Sub-lens (optional, 0-2): e.g., [comparison + exploratory]
- Scope & time boundaries: time / geography / industry scope
- Key evaluation criteria (must be checklist):
  - [ ] Claim X supported by ≥ 3 independent sources
  - [ ] Number Y anchored to ≥ 1 primary source
  - [ ] Counter-position Z has ≥ 1 representative view cited
  - [ ] Uncertainty explicitly marked
- Known constraints: budget / time / disallowed sources / risk tolerance
- Initial judgement: prior prediction (can be empty)
- Counter-evidence conditions: what would overturn the initial judgement
```

### Phase 2 · Dig · Probe search + Satisficing 4-C

**9 probe types**:

| Probe | Purpose | Example |
| --- | --- | --- |
| P1 scope | clarify boundaries & dimensions | "Industry mainstream categories, core metrics?" |
| P2 primary | anchor key facts/numbers | "What do official data / financials / regulators say?" |
| P3 comparison | find differences / benchmarks | "A vs B on price / performance / risk?" |
| P4 counter | actively seek disconfirmation | "Who disagrees? Why?" |
| P5 conflict | resolve source contradictions | "Time? scope? sample? definition?" |
| P6 risk | reveal hidden constraints | "Regulation / implementation / cost / supply chain risks?" |
| P7 temporal | verify latest state | "Recent policy / price / version / event changes?" |
| P8 market | surface real-world usage | "User complaints, adoption barriers?" |
| P9 decision | check action-readiness | "Sufficient to recommend / exclude / wait?" |

**D1-D5 info-gain assessment** (each round):

- D1 fills critical evidence gap → progress
- D2 **could change conclusion?** (Highest value)
- D3 resolves high-credibility conflict
- D4 surfaces key boundary conditions
- D5 upgrades claim to higher-credibility source

**Satisficing 4-C stop gate** (any one = stop):

| # | Condition | Tool check |
| --- | --- | --- |
| S1 | Task card criteria checklist all checked | agent review |
| S2 | Major disagreements resolved or explicitly unresolved | agent review |
| S3 | High-credibility counter found → hypothesis to 无效 (KILLED) | agent review |
| S4 | Workload hard ceiling reached (L1=20 / L2=50 / L3=80 search calls) | `check-stop` |

### Phase 3 · Decide · Decision + 8-item self-check

**8-item Decision-Readiness self-check** (mandatory before DELIVER):

```markdown
☐ 1. 30-sec retelling — Executive Summary paragraph 1 IS the answer
☐ 2. Verb-led opener — "Recommend upgrading" not "we think..."
☐ 3. Digit density — per-lens (decision ≥60 / practitioner ≥40 / research ≥30)
☐ 4. Boundary conditions — ≥ 1 Hold / Revert trigger
☐ 5. Explicit YES/NO/DEFER — decision lens mandatory
☐ 6. Counter honesty — Red Team + Steel-manned (named real opponent)
☐ 7. Executable — Who / What / When three-line
☐ 8. Tool-data-fidelity — `python3 scripts/research_tools.py audit` ≥5/7
```

Audit item 8 failure handling (choose 1):

- **Backfill ledger** (recommended) — re-run claim/round/hyp to populate, then write
- **DELAY** — tell user "tool calls failed, will give brief reply, full report later"
- **Disclose report** — end with `本报告数据来自 in-context 推理,仅供参考` disclosure

**FORBIDDEN**: audit failure + silent delivery = violates SOUL.md 4th anchor "data not persisted = data not real".

---

## Input / Output contract

### Input contract

| Field | Required | Notes |
| --- | --- | --- |
| `topic` | yes | Open question (not a "what is X" single-point query) |
| `Effort hint` | no | L1/L2/L3 — agent auto-selects based on task |
| `Audience preference` | no | Default = decision-maker (changeable in Frame) |
| `Geographic/time boundary` | no | "2026 H2 China market" etc. |

### Output contract (report template)

```markdown
# <Topic report>

## 0 · Meta
- Date / audience / effort / lens combo / main constraints

## 1 · Executive Summary — Answer: **YES/NO/DEFER**

## 2 · Key Findings (3-7 core evidence)

## 3 · Insights + Cross-Domain (2-4 cross-domain insights)

## 4 · Risks + Red Team (4-perspective + Steel-manned)

## 5 · Conclusions
- Explicit decision
- 3-7 Who/What/When executable items
- 3-5 Hold/Revert triggers

## 6 · Deviations + unresolved gaps
- [DEVIATIONS] — known assumption / data gaps
- [unresolved-gap] — uncovered issues

## Sources (≥ 5 independent sources with tier grading)
```

### Output file layout

```
research/
├── <topic-slug>-<YYYY-MM>.md     # main report
└── .cache/
    └── <topic-slug>-<YYYYMMDD>.json   # ledger (replayable)
```

**Never** write outside `research/` (SKILL.md §6 Output Discipline).

---

## Before / After: why this skill

| Dimension | Without this skill (raw LLM) | With this skill |
| --- | --- | --- |
| Report structure | 5-7 paragraph stream, no chapter discipline | 5-chapter forced structure + verification gate |
| Evidence chain | 5-10 cited sources, no grading | T1-T5 grading + 4 cognitive labels |
| Decision traceability | No claim-to-recommendation anchors | Every recommendation anchored to C#/S# in ledger |
| Counter perspective | 0 | Red Team ≥ 4 perspectives (tech / business / regulatory / behavioral) + Steel-manned |
| Verification | None | **8-item Decision-Readiness self-check** (incl. audit ≥5/7) |
| Long-context persistence | LLM context overflow on long research | Ledger persistence, no info loss |
| Stop discipline | "I'll search until I'm satisfied" | Satisficing 4-C stop gate, no overload |
| Hypothesis state | Vague "high/medium/low" + fake-precision digits | 有效 / 修正 / 无效 / 待定 4 states + 高/中/低 3 levels |
| R17b verification | Single-decision 7/7 + recommendation | R17b ledger: 18 sources + 14 claims + 7 findings + 5 hyp updates |

---

## Out-of-scope / Anti-patterns

### ❌ Don't use for

| Scenario | Why | Alternative |
| --- | --- | --- |
| Single-fact queries | "What's new in Python 3.13" needs no 6-lens | `web_search` direct |
| Real-time code debugging | LLM context doesn't preserve build state | IDE direct |
| Creative writing / fiction | No decision goal, evidence tracing is meaningless | Direct dialogue |
| User explicitly says "no network" | Skill defaults to web search | Honor user request |

### ❌ Don't do this (Anti-patterns)

| Anti-pattern | Why bad |
| --- | --- |
| ✗ Retelling SKILL content in agent prompt | Pollutes test, occludes SKILL value |
| ✗ Use L1/L2/L3 simultaneously for effort AND audience | Dimensional collapse — keep 3 dimensions independent (per #244) |
| ✗ Report headers using topic form ("Suggestions / Analysis / Conclusions") | Must use conclusion-embedded ("Recommend rust migration") (per #227) |
| ✗ "73% confidence" fake-precision digits | Replace with 高/中/低 qualitative |
| ✗ Audit failure + silent report delivery | Violates SOUL.md 4th anchor "data not persisted = data not real" |
| ✗ Cross-Domain as default chapter | Conditional on lens (per #245) |
| ✗ No Sources Register, just inline [Sn] | Tools can't inject metadata |
| ✗ Report > 50 KB | Indicates lack of focus — split into multiple focused reports |

### ✅ Recommended practice

- ✓ Agent prompt contains **only** topic + requirement + SKILL path (per #362)
- ✓ Frame phase preset Satisficing 4-C (per #254)
- ✓ ACH ≥ 2 mutual hypotheses + diagnosticity grading (per hypothesis-redteam.md)
- ✓ State transitions require external evidence (Independence principle)
- ✓ Pre-DELIVER audit ≥5/7
- ✓ Reports to `research/<slug>-<YYYY-MM>.md`

---

## Decision-grade features

### 1. Decision-ready: explicit verdict + boundaries

Every report MUST:

- State **YES / NO / DEFER** explicitly (decision lens mandatory)
- List ≥ 1 **Hold** condition (when to re-assess / escalate)
- List ≥ 1 **Revert** condition (when to reverse / cancel)
- **Who/What/When** three-line executable list (who does what by when)

### 2. Traceable: ledger persistence

Every key claim is written to `research/.cache/<topic>-<YYYYMMDD>.json`:

```json
{
  "claim_C1": {"text": "ARR $20B", "label": "已公开",
                "sources": ["S1","S5"], "round_n": 2},
  "hyp_history": [{"from":"ALIVE","to":"MUTATED",
                   "conf":60,"source":"S5",
                   "evidence_trigger":"ARR 反超 2.2x"}]
}
```

Replay anytime via `python3 scripts/research_tools.py audit`.

### 3. Auditable: 3-label system

Every data point carries **2 ratings**:

| Source tier (publisher reputation) | Cognitive label (claim credibility) |
|---|---|
| Primary / Secondary / Anecdotal | 已确认 / 已公开 / 自推断 / 未验证 |

Example sentence: `[S1: Apex AI 2026 financials] [Primary] [已确认]` vs `[S5: industry commentary] [Secondary] [自推断]`

Readers apply "trust demotion" — decisions can rely on [已确认 + Primary], inferences must be explicit.

### 4. ACH competing hypotheses upfront (anti confirmation-bias)

**Before** starting the report, list ≥ 2 **mutually-exclusive** hypotheses; grade all evidence by **diagnosticity**:

- **High-diagnosticity evidence** = supports only one hypothesis → can falsify others
- **Low-diagnosticity evidence** = supports multiple → background only

> ⚠️ Evidence supporting your preferred hypothesis often also supports the alternative. Low-diagnosticity evidence cannot "KILL" other hypotheses.

### 5. Independence principle (hypothesis state transitions)

**State transitions MUST be triggered by external evidence**, not self-reasoning:

```
✅ State: 有效 → 修正 (MUTATED)
  External evidence: S7 Motion migration-back-to-PG measurement + S15 iBuidl 2026 ADR
  → Independence principle satisfied

❌ State: 有效 → 无效 (KILLED)
  Self-reasoning: "I thought about it, this is wrong"
  → Violates Independence — should stay 有效 / 修正, or → 待定 (UNRESOLVED)

Independence principle is one of SOUL.md 1st-tier anchors.
```

---

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| Agent still uses old skill version after load | OpenCode caches SKILL in memory | Copy SKILL.md full content into prompt (temporary) / restart agent |
| audit shows `0/7` | Setup called but no claim/round actually invoked | Re-run each subcommand, verify "OK" line output |
| `[Sn]` references not detected by inline metadata | Sources Register not at document end | Add Sources section to markdown bottom (independent `## Sources` header) |
| `fcntl` ImportError on Windows | POSIX-only API (macOS / Linux) | Tool auto-degrades to unlocked write, may race — upgrade to Linux/macOS, or use WSL |
| Ledger written to wrong file | `Ledger().load()` selects by mtime | v8.1.8 fix (--ledger flag). Temp workaround: `python3 -c "from research_tools import Ledger; Ledger().setup(...)"` with explicit `load(filepath=...)` |
| Claim C# numbers duplicated | Multi-process concurrent, lock failed | CLI calls MUST be serial (SKILL.md §6 reminder) |
| Report too long > 50 KB | Insufficient focus | Split into multiple focused reports |

### Self-diagnostic commands

```bash
# Verify skill install is correct
ls ~/.config/opencode/skills/deep-research/SKILL.md
diff ~/.config/opencode/skills/deep-research/SKILL.md \
     <project>/.opencode/skills/deep-research/SKILL.md
# Should output empty (byte-identical)

# Verify tools work
python3 <skill>/scripts/research_tools.py --help
python3 <skill>/scripts/research_tools.py audit
# Should list 15 subcommands / show ledger summary

# Verify ledger integrity
python3 <skill>/scripts/research_tools.py audit
# Should output 7-item data-presence, ≥5/7 must ✓
```

---

## Versioning & upgrade

### Current version

**v9.0** (structural refactor)

| Dimension | Status |
| --- | --- |
| References | 3 (probe-search / hypothesis-redteam / report-rendering) |
| Tools subcommands | 15 (setup / source / round / finding / hyp [--id] / decide / summary / list / claim / claims-dump / suggest-label / check-stop / suggest-path / inline / audit) |
| Self-check items | 8 (SKILL.md §7, single authority) |
| Hypothesis state | 中文 4 states (有效 / 修正 / 无效 / 待定) + 3-level conf (高/中/低), multi-hypothesis (ACH) |
| Ledger schema | 2.0 (multi-hypotheses[]; reads legacy 1.0) |
| Workload ceilings | L1=20 / L2=50 / L3=80 search calls |

### Upgrade policy

- **PATCH** (8.1.x → 8.1.y): backward compatible, add subcommand, no output-format change
- **MINOR** (8.x → 8.y): may change schema; **WARNING** run R-golden-cases before adopting
- **MAJOR** (8 → 9): prompts rewritten — SKILL.md restructured (intent → red-lines → autonomy → process); see `CHANGELOG.md`

### Changelog

- **v9.0** (refactor): structural refactor per the refactor plan — single-authority consolidation (task card / 5-key signals / stop conditions / 8-item self-check each defined in exactly one place), red-lines as their own section, explicit autonomy zone, all version archaeology removed from agent-context files (→ `CHANGELOG.md`), fixed audit count + dead findings check + pseudo-precise `@66%` confidence leak, multi-hypothesis ledger schema (ACH).
- **v8.1.7** (2026-07-15): Remove 2 dead references + audit subcommand + 8-item self-check + SOUL.md 4th anchor
- **v8.1.6** (2026-07-15): R16 fidelity fix (audit subcommand + 8-item self-check)
- **v8.1.5** (2026-07-15): User micro-edits adopted + "other docs win" conflict resolution
- **v8.1.0** (2026-07-15): argparse refactor + cognitive-label CLI (claim / claims-dump / suggest-label)
- **v8.0.0** (2026-07-14): Comprehensive rewrite per 12-issue audit, renamed from `research` to `deep-research`

Full per-version detail in `CHANGELOG.md`; R1-R17 regression history in `tests/regression-log.md`.

---

## References

### Citations & acknowledgments

| Source | Use |
| --- | --- |
| [Anthropic Skills spec](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) | skill frontmatter / description / body structure |
| [Best-README-Template](https://github.com/othneildrew/Best-README-Template) | README section conventions |
| [Raymond-Hear/deep-research-prompt](https://github.com/Raymond-Hear/deep-research-prompt) | value bullet pattern / Before-After table |
| [anthropics/skills](https://github.com/anthropics/skills) | skill-creator / pdf / pptx / webapp-testing templates |
| [obra/superpowers](https://github.com/obra/superpowers) | subagent-driven-development process |

### Theoretical foundations

| Theory | Application |
| --- | --- |
| [Minto Pyramid Principle](https://barbaraminto.com/) (McKinsey / BCG / Bain) | bottom-line-up / pyramid structure |
| [Gopen & Swan 1990](https://www.americanscientist.org/blog/the-long-view/the-science-of-scientific-writing) | sentence-level 7 principles |
| [IMRaD](https://en.wikipedia.org/wiki/IMRaD) | academic / business report template |
| [SCR (Situation/Complication/Resolution)](https://www.mckinsey.com/) | McKinsey Executive Summary standard |
| [Anytime Algorithms](https://en.wikipedia.org/wiki/Anytime_algorithm) | iterative search (interruptible) |
| [Information Foraging Theory](https://en.wikipedia.org/wiki/Information_foraging) (Pirolli & Card) | marginal value signals |
| [Satisficing / Herbert Simon 1956](https://en.wikipedia.org/wiki/Satisficing) | "good enough" principle |
| [ACH (Analysis of Competing Hypotheses)](https://en.wikipedia.org/wiki/Analysis_of_Competing_Hypotheses) | US IC competing-hypothesis method |
| [ICD 203](https://www.dni.gov/index.php/who-we-are/organizations/ic-reform-modernization-efforts/icd-203) | US IC analysis standards (Red Team theory) |

### Tools & scripts

| Tool | Use |
| --- | --- |
| `python3 scripts/research_tools.py setup` | Initialize ledger |
| `python3 scripts/research_tools.py claim` | Record cognitive-labeled claim |
| `python3 scripts/research_tools.py hyp 有效` | Update hypothesis state (中文) |
| `python3 scripts/research_tools.py check-stop --effort L2` | 4-C stop gate check |
| `python3 scripts/research_tools.py audit` | Pre-DELIVER mandatory (8-item self-check #8) |
| `python3 scripts/research_tools.py inline --write <file>` | Auto-inject metadata |
| `python3 scripts/research_tools.py suggest-path "topic"` | Generate `research/<slug>.md` path |

### Test cases

See `tests/gold-cases.md` (14 gold cases) + `tests/regression-log.md` (R1-R17 history).

---

*Last updated: v9.0 refactor*
