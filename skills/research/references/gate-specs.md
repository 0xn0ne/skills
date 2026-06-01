# Gate Specification Reference

This file contains the full mechanical specification for all verification gates.
Agents do NOT need to read this file during research — the script handles verification automatically.
This reference exists for debugging, ledger repair, and understanding why a gate failed.

---

## Source Types

| Type | Meaning |
|---|---|
| `T1_Academic` | peer-reviewed papers, preprints, proceedings |
| `T1_Official` | official docs, specs, filings, laws, source repos |
| `T2_Creator` | creator/practitioner primary writeups, engineering posts, postmortems |
| `T2_Data` | authoritative datasets, government stats, primary market/financial data |
| `T3_Synthesis` | expert/analyst synthesis, surveys, review articles |
| `T4_Community` | forums, issue trackers, social posts, community signals |
| `T5_Recap` | tutorials, news summaries, blog recaps |

## Publisher Rules

- `T1_Official` requires `publisher_type=official` and URL domain matches `official_domain`
- Personal blogs/Medium/news articles are never `T1_Official`
- Company blogs can be `T2_Creator` but not `T1_Official` unless formal documentation

### T1_Official Publisher Rules — Strict Criteria

A source qualifies as T1_Official ONLY when ALL of the following are true:
1. `publisher_type` = "official"
2. The URL domain resolves to the official organization's own web domain
3. The content is a primary document (filing, specification, standard, law, official report)

**Never valid as T1_Official:**
- News aggregation platforms (e.g., sohu.com, 163.com, qq.com) — even if they host official content
- Social media platforms (e.g., weibo.com, twitter.com) — even if posted by official accounts
- Search portals (e.g., baidu.com, google.com)
- Third-party summarizers or reposters

> **Test:** Is the URL on the organization's own domain? If the URL is `company.com/report.pdf` → T1_Official. If the URL is `sohu.com/a/company-report` → T3_Synthesis (reposted content).

## Evidence Grades

- **A:** 2+ independent T1/T2 sources with original/traced status
- **B:** 1+ T1/T2 primary source with original/traced + corroboration OR **T4 Triangulation** (3+ independent T4/T5 sources from zero overlapping domains)
- **C:** plausible mixed evidence; indirect or uncertain
- **D:** weak signal, mostly T4/T5, analogy, untraced numbers
- **F:** unsupported, contradicted, unverifiable, or fabricated

### T4 Triangulation Rules

For B-grade via T4 triangulation:
- Must have 3+ T4/T5 sources
- Sources must come from different domains (zero domain overlap)
- Sources must report the same technical/market signal
- Documented in claim notes

## Verification Status

| Status | Meaning |
|---|---|
| `verified_directly` | Source accessed and claim confirmed |
| `traced_back` | Claim traced to primary source through citation chain |
| `unverified` | Not yet verified |
| `gap` | Known gap, evidence unavailable |
| `disputed_data` | Multiple sources present conflicting numeric values with >15% variance |

## T1/T2 Ratio

- Default threshold: ≥50%
- Breaking event (<72h): ≥30%
- Emergent/non-academic: ≥35%

## Advisory-Safe Gates

These gates can fail and still produce an `.advisory.md`:

- `t1t2_ratio`, `claim_grade_distribution`, `commercial_source_diversity`, `numeric_evidence_strength`, `vendor_bias`, `cross_validation`, `source_diversity`
- `hypothesis_tracking`
- `task_type_framework`

## Structural Gates

Any of these failing blocks advisory report generation:

- `access_trace_consistency`, `claim_source_integrity`, `recommendation_trace`
- `research_closure`, `narrative_completeness`, `thesis_narrative`, `edge_cases`
- `subquestion_coverage`, `prompt_item_coverage`, `coverage_loop`
- `language_alignment`, `scope_fidelity`, `recommendation_actor_scope`
- `weak_claim_usage`, `red_team_quality`, `claim_subquestion_trace`, `empty_ledger`

### Gate Descriptions (for gates not otherwise documented in this file)

| Gate | Type | What It Checks | Failure Condition |
|------|------|----------------|-------------------|
| `language_alignment` | structural | Content language matches `report_language` field | CJK ratio <10% when `report_language=zh`, or CJK ratio >50% when `report_language=en` |
| `weak_claim_usage` | structural | D/F/unverified claims not used in recommendations | Any recommendation citing a D-grade, F-grade, or unverified claim |
| `subquestion_coverage` | structural | All subquestions have `answered_by` + `narrative_ref` | Any subquestion missing answered_by or narrative_ref |
| `recommendation_actor_scope` | structural | AI-topic recommendations match runtime scope | Runtime topic contains training-stage action recommendations |
| `scope_fidelity` | structural | Runtime topic not dominated by training-stage subquestions | Training-stage subquestions dominate the research scope |

> **Note on AI-topic gates**: `recommendation_actor_scope` and `scope_fidelity` are specialized gates for AI-related research topics. They prevent "runtime prompt-engineering" topic research from drifting into "model training/alignment" content. For example, if the user asks about "how to write better prompts" (runtime), the research should not produce recommendations about "fine-tuning models" (training-stage). If these gates fail, convert training-stage subquestions to background status or modify their notes to clarify they are context, not recommendations.

## Gate JSON Shapes

### Closure Search

```json
{
  "id": "CS1",
  "trigger": "What hypothesis prompted this search?",
  "search_direction": "confirm|explore|refute|neutral",
  "perspective": "supportive|neutral|critical|alternative",
  "source_ids": ["S1", "S2"],
  "new_evidence": "What did it reveal?",
  "effect_on_conclusion": "strengthened|weakened|changed|no_material_change"
}
```

> **Important:** `search_direction` and `perspective` are DIFFERENT fields with DIFFERENT valid values. Do NOT use `alternative` as a `search_direction` — it is only valid as a `perspective`. Valid `search_direction` values: `confirm`, `explore`, `refute`, `neutral`. Valid `perspective` values: `supportive`, `neutral`, `critical`, `alternative`.

### Research Closure Gate

The `research_closure` gate checks TWO independent requirements:

1. **Critical/Refute perspective**: At least 1 closure search with `perspective: "critical"` OR `search_direction: "refute"`
2. **Supportive/Confirm/Alternative perspective**: At least 1 closure search with `perspective: "supportive"` OR `perspective: "alternative"` OR `search_direction: "confirm"`

Both must be satisfied. Only having refute searches will trigger `missing_supportive_confirm_alternative_closure` FAIL.

Minimum closure searches: 2 (non-strategic topics) or 3 (strategic topics).
Gate type: **structural** (failure blocks all report generation).

### Source Dominance Gate

The `source_dominance` gate checks whether too many A/B-grade claims come from a single source.

- **Type**: advisory-safe WARNING (does not block report generation)
- **Trigger condition**: 4+ A/B-grade claims exist AND 60%+ of them cite the same source
- **Purpose**: Prevents over-reliance on a single source, which indicates insufficient independent verification
- **Recovery**: Find additional independent sources for claims, or downgrade claims that lack independent corroboration

### Red Team Argument

```json
{
  "id": "RT1",
  "objection": "Counterargument text",
  "evidence_claim_ids": ["C1"],
  "source_ids": ["S1"],
  "impact_if_true": "How would this affect conclusion?",
  "response": "How was it addressed?",
  "residual_risk": "Low|Medium|High"
}
```

### Prompt Item

```json
{
  "id": "P1",
  "text": "Original question text",
  "priority": "high|medium|low",
  "status": "mapped|gap_identified|unmapped",
  "mapped_subquestions": ["Q1"],
  "source_excerpt": "Initial pointer",
  "gap_note": "Why this is a gap (required for gap_identified)"
}
```

### Subquestion

```json
{
  "id": "Q1",
  "question": "Sub-question text",
  "priority": "high|medium|low",
  "status": "answered|partial|gap_identified|unanswered",
  "answered_by": ["C1", "C2"],
  "narrative_ref": "section reference",
  "module_ref": "M1",
  "gap_note": "Why unanswered (required for partial/gap_identified)",
  "loop_action": "continue_research|continue_synthesis|ask_user|none"
}
```

### Module

```json
{
  "id": "M1",
  "subquestion_id": "Q1",
  "title": "Module Title",
  "content": "Detailed analysis...",
  "claim_ids": ["C1", "C2"],
  "status": "complete|partial|gap",
  "language": "en|zh|mixed"
}
```

## Access / Trace Matrix

| Access status | Allowed trace | T1/T2 numerator? |
|---|---|---|
| `reachable` | `original` or `traced` | yes |
| `uniquely_identifiable` | `traced` | yes |
| `timed_out/unreachable/unverified` | `as_cited_not_verified` or `unverified` | no |

## Numeric Variance Rule

For numeric claims used in Recommendations or Executive Answer:

1. Extract raw values from each source into claim `notes` as JSON
2. Calculate maximum deviation from mean as percentage
3. If deviation exceeds 15%: tag claim as `disputed_data`
4. `disputed_data` claims require "High Risk" caveat in notes to appear in recommendations

### Variance Calculation

```
mean = sum(values) / count(values)
max_deviation = max(|value - mean| / mean for each value)
threshold = 15%
```

### Disputed Data Handling

| verification_status | Can appear in Recommendations? | Requirements |
|---|---|---|
| `verified_directly` | Yes | Normal |
| `traced_back` | Yes | Normal |
| `disputed_data` | Only with "High Risk" caveat | Must document discrepancy in contradictions |
| `unverified` | No | Must verify first |

## Hypothesis Tracking Gate

Checks that hypothesis evolution is properly tracked.

- At least 1 hypothesis must have status `confirmed` or `falsified` (not all `testing`)
- No `confirmed` hypothesis should have `confidence` below 50
- Each hypothesis should have at least 1 `trigger_claim_ids`
- Gate type: **advisory-safe** (failure allows advisory report generation)

### Hypothesis JSON Shape

```json
{
  "id": "H1",
  "initial_state": "Market growth is primarily driven by Policy X",
  "current_state": "Market growth is primarily driven by Technology Y adoption",
  "mutation_trigger": "S05",
  "trigger_claim_ids": ["C03", "C07"],
  "status": "mutated",
  "confidence": 72,
  "notes": "Policy X impact was overstated; Technology Y adoption rate from S05 contradicts initial hypothesis"
}
```

### Hypothesis Status Values

| Status | Meaning |
|---|---|
| `testing` | Active hypothesis, not yet confirmed or falsified |
| `confirmed` | Evidence supports the hypothesis |
| `falsified` | Evidence contradicts the hypothesis |
| `mutated` | Hypothesis changed due to new evidence |

## Task Type Framework Gate

Checks that the research covers required dimensions for the detected task type.

- Verifies all required dimensions from the task type framework appear in narrative
- Checks minimum source count for the task type
- Gate type: **advisory-safe** (failure allows advisory report generation)
- Only runs when `task_type` is set in the ledger

### Task Type Definitions

| Task Type | Required Dimensions | Min Sources |
|---|---|---|
| `market_analysis` | market_size, growth_drivers, competitive_landscape, customer_segments, regulatory_environment | 8 |
| `competitive_intel` | feature_comparison, pricing, market_positioning, strengths_weaknesses, strategic_direction | 6 |
| `supply_chain` | supplier_landscape, cost_structure, risk_concentration, alternative_sources, logistics | 6 |
| `policy_analysis` | current_regulations, enforcement_trend, stakeholder_positions, compliance_requirements, timeline | 5 |
| `investment_feasibility` | market_opportunity, financial_model, team_capability, competitive_moat, exit_scenarios, risk_factors | 8 |
| `technology_evaluation` | capability, maturity, ecosystem, performance, cost, migration_path | 6 |
| `strategic_planning` | current_state, market_dynamics, capabilities, options, resource_requirements, timeline | 6 |

## Search Volume Requirements

| Round | Minimum Searches | Key Requirements |
|---|---|---|
| Round 1 | 15 | 3+ framework discovery, 2+ per dimension, 2+ case studies, 2+ expert opinion, 3+ regional (if non-English) |
| Round 2 | 15 | 3+ quantitative data, 3+ risk factors, 2+ contradicting evidence, 2+ case studies |
| Round 3 | 10 | 2+ implementation details, 2+ cross-domain, 1+ regulatory, 1+ alternative hypothesis |
| Round 4 | 10 | 2+ stress-test, 2+ validation, 2+ expert disagreement, 1+ recent developments |
| **Total** | **50** | Minimum 50 distinct searches across 4 rounds |

## Systematic Search Angles

For each dimension, search from ALL applicable angles:

| Angle | Query Pattern | Purpose |
|---|---|---|
| Framework Discovery | "[domain] frameworks", "[domain] methodologies" | Discover existing structured approaches |
| Quantitative Data | "[metric] optimal threshold", "[metric] benchmark" | Find specific numbers and standards |
| Risk Factors | "[domain] risks", "[domain] failure modes" | Identify what can go wrong |
| Case Studies | "[topic] case study", "[topic] real example" | Learn from real-world examples |
| Implementation | "[approach] implementation guide", "[approach] tools" | Find practical how-to details |
| Cross-Domain | "[method] applied to [other domain]" | Borrow insights from adjacent fields |
| Expert Opinion | "[topic] expert interview", "[topic] practitioner blog" | Get insider perspectives |
| Contradicting | "[claim] wrong", "[claim] criticism" | Challenge assumptions |
| Recent | "[topic] 2025", "[topic] latest research" | Stay current |

## Progressive Research Reasoning

After each round of searching, the agent must produce 2-4 paragraphs of technical reasoning:

- **Round 1**: Bottleneck/Root Cause Analysis, Algorithm/Strategy Reasoning, Mathematical/Formal Modeling, Integration/Architecture Planning
- **Round 2**: Contradiction Resolution, Refined Mathematical Model, Strategy Refinement, Gap Identification
- **Final**: Final Bottleneck/Root Cause, Optimal Strategy, Complete Mathematical Model, Implementation Architecture, Performance Prediction

This reasoning becomes the `deep-insights` narrative section in the ledger.

## Domain-Specific Analysis Requirements

For `technology_evaluation` and code optimization research, additional analysis is required:

| Requirement | When to Apply |
|---|---|
| Algorithm Complexity (Big-O) | Always |
| Memory Layout Analysis | When performance is a goal |
| Overflow/Boundary Analysis | When dealing with numeric data |
| Compiler/JIT Behavior | When using JIT compilation |
| Platform-Specific Behavior | When recommending platform-specific tools |
| Warmup/Cold Start Costs | When latency matters |

## Code Quality Review

When research produces code, it must pass:
1. Semantic consistency with user requirements
2. Edge case handling documentation
3. Performance claims traceable to ledger evidence
4. API compatibility verification

## Report Status Values

| Status | Meaning |
|---|---|
| `Decision-grade` | Verified, recommendations supported |
| `Evidence Gap Report` | Useful but insufficient for actions |
| `Advisory Research — evidence below decision threshold` | Directional only |
| `Partial — decision not supported` | Some findings useful |
| `Draft — ledger inconsistent` | Do not use for decisions |
| `Draft — requires source repair` | Sources unverifiable |
