# Batch JSON Field Reference

Every field below is **exact** — the script rejects unknown or misspelled fields. Use `$SKILL_DIR/assets/batch-ledger-template.json` as your starting template.

## Common Mistakes — READ THIS FIRST

| Mistake | Wrong | Correct |
|---------|-------|---------|
| JSON format | `{"sources": {"S1": {...}}}` (dict) | `{"sources": [{"id": "S1", ...}]}` (list) |
| Hypothesis confidence | `"confidence": "High"` (string) | `"confidence": 85` (integer 0-100) |
| Source type field | `"tier": "T1_Academic"` | `"type": "T1_Academic"` |
| Claim text field | `"claim_text": "..."` | `"claim": "..."` |
| Claim sources field | `"source_ids": [...]` | `"primary_sources": [...]` |
| Recommendation text | `"recommendation": "..."` | `"text": "..."` |
| prompt_item status | `"status": "pending"` | `"status": "unmapped"` (or `mapped`, `gap_identified`) |
| subquestion status | `"status": "open"` | `"status": "unanswered"` (or `answered`, `partial`, `gap_identified`) |
| 忘记填used_for | `"used_for": []` 或省略 | `"used_for": ["C1", "C3"]` — 每个 source 必须列出它支撑的 claim IDs |

**All collections must be LISTS in batch JSON.** The `import-ledger` command converts them to dicts keyed by ID internally.

## Top-level

| Field | Type | Required | Notes |
|---|---|---|---|
| `topic` | string | ✅ | Slug format, e.g. `"vector-db-comparison-2026"` |
| `scope` | string | ✅ | One-line scope description |
| `task_type` | string | ✅ | See `task-type-frameworks.md` for valid values |
**Batch JSON format:** Sources, claims, recommendations, hypotheses, closure_searches, prompt_items, subquestions are all **lists** in the batch JSON. The `import-ledger` command converts them to dicts keyed by ID internally. Always use list format in your batch JSON file.
| `claims` | list | ✅ | List of claim objects |
| `recommendations` | list | ✅ | List of recommendation objects |
| `hypotheses` | list | ✅ | List of hypothesis objects |
| `closure_searches` | list | ✅ | List of closure search objects |
| `prompt_items` | list | — | Required for strategic/multi-question topics |
| `subquestions` | list | — | Used with prompt_items for structured coverage |
| `narrative_sections` | dict | ✅ | Keys are section IDs (see narrative_sections keys below) |

## Source object

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | ✅ | e.g. `"S1"`, `"S2"` |
| `title` | string | ✅ | Source title |
| `url` | string | ✅ | Full URL |
| `type` | string | ✅ | Tier: `T1_Academic`, `T1_Official`, `T2_Creator`, `T2_Data`, `T3_Synthesis`, `T4_Community`, `T5_Recap` — **NOT `tier`** |
| `publisher` | string | ✅ | Publisher name |
| `publisher_type` | string | ✅ | **Constrained values:** `official`, `company`, `individual`, `media`, `community`, `academic`, `unknown`. Map external types: news→media, review→media, blog→individual, product_page→company, docs→official, forum→community, paper→academic. |
| `official_domain` | string | — | Domain for T1_Official verification |
| `access_status` | string | ✅ | `reachable`, `uniquely_identifiable`, `timed_out`, `unreachable`, `unverified` |
| `trace_status` | string | ✅ | `original` (directly fetched), `traced` (verified via redirect), `as_cited_not_verified` (default — does NOT count toward T1/T2 ratio). **Sources must be `original` or `traced` to count toward T1/T2 threshold.** |
| `notes` | string | — | Key findings or quotes |
| `language` | string | — | `"en"`, `"zh"`, etc. |
| `used_for` | list | — | Claim IDs this source supports |

### T2_Creator vs T3_Synthesis Distinction

| Criterion | T2_Creator | T3_Synthesis |
|-----------|-----------|-------------|
| **Author** | Practitioner who did the work (engineer, founder, researcher) | Analyst/journalist/reporter summarizing others' work |
| **Content type** | Postmortem, engineering blog, official earnings call, founder's letter | News article, market research report, analyst synthesis, media coverage |
| **Example** | Netflix tech blog about their architecture | TechCrunch article about Netflix's architecture |
| **Example** | Tesla's 10-K SEC filing | Bloomberg article about Tesla's financials |
| **Example** | Ginkgo Bioworks official technology page | Sohu article summarizing Ginkgo's technology |

> **Key test:** Is the author the person/entity who did the work? If yes → T2_Creator. If the author is reporting on someone else's work → T3_Synthesis. Company official marketing materials (not technical docs or filings) should be classified as T3_Synthesis, not T2_Creator.

## Claim object

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | ✅ | e.g. `"C1"` |
| `claim` | string | ✅ | Clear factual statement — **NOT `claim_text` or `text`** |
| `grade` | string | ✅ | `A`, `B`, `C`, `D`, `F` |
| `confidence` | string | ✅ | `High`, `Medium`, `Low` |
| `primary_sources` | list | ✅ | List of source IDs — **NOT `source_ids` or `evidence`** |
| `corroboration_sources` | list | — | Additional supporting source IDs |
| `verification_status` | string | ✅ | `verified_directly`, `traced_back`, `unverified` |
| `numeric` | bool | — | `true` if claim contains numeric data |
| `contradiction_checked` | bool | ✅ | Must be `true` for all claims |
| `notes` | string | — | Additional context |

## Recommendation object

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | ✅ | e.g. `"R1"` |
| `text` | string | ✅ | Specific actionable recommendation — **NOT `recommendation`** |
| `type` | string | ✅ | `advisory` for advisory reports; `action` only for decision-grade; `research_next` for gaps requiring future investigation (not blocked in advisory mode). **Advisory reports reject `type: "action"` but accept `research_next`.** |
| `claim_ids` | list | ✅ | Supporting claim IDs — **NOT `evidence`** |
| `notes` | string | — | Additional context |

## Hypothesis object

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | ✅ | e.g. `"H1"` |
| `initial_state` | string | ✅ | Original hypothesis statement |
| `current_state` | string | ✅ | Current state description |
| `status` | string | ✅ | `confirmed`, `falsified`, `mutated`, `testing` |
| `confidence` | int | ✅ | **Numeric 0-100** — NOT a string |
| `mutation_trigger` | string | — | Source ID that forced the change |
| `trigger_claim_ids` | list | — | Claim IDs that supported/undermined |
| `notes` | string | — | Why it changed or stayed |

### Hypothesis Status Selection Guide

| Status | When to Use | Example |
|--------|-------------|---------|
| `confirmed` | Evidence supports the original hypothesis as stated | H1: "Market will reach $X by 2025" → evidence confirms $X |
| `falsified` | Evidence directly contradicts the original hypothesis | H1: "Market will reach $X" → evidence shows market is $X/2 |
| `mutated` | Evidence forces a meaningful revision of the hypothesis | H1: "Digital will REPLACE traditional" → evidence shows digital SUPPLEMENTS traditional |

> **Key distinction:** `falsified` = the original statement was wrong. `mutated` = the original statement was incomplete or framed wrong, and has been revised to a better version. If the narrative says "最初认为X，但证据表明Y", the status is `mutated` (not `confirmed`).

## Closure search object

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | ✅ | e.g. `"CS1"` |
| `trigger` | string | ✅ | What prompted this search |
| `search_direction` | string | ✅ | `confirm`, `explore`, `refute`, `neutral` |
| `perspective` | string | ✅ | `critical`, `alternative`, `supportive` |
| `source_ids` | list | — | Sources found |
| `new_evidence` | string | — | What it revealed |
| `effect_on_conclusion` | string | — | `strengthened`, `weakened`, `neutral`, `no_material_change` |
| `counterintuitive_angle` | string | — | Why this angle was unexpected |
| `alternative_hypothesis` | string | — | What alternative this tests |
| `decision_impact` | string | — | How this affects the final recommendation |

## Prompt item object

Required for strategic/multi-question topics — topic contains: decision, commercial, strategic, invest, build, buy, adopt, market, product, procurement, operations, or contains `?`/`？`, or contains compare/should/whether.

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | ✅ | e.g. `"PI1"` |
| `text` | string | ✅ | The original user question or sub-question |
| `source_excerpt` | string | — | Relevant source excerpt |
| `priority` | string | ✅ | `high`, `medium`, `low` |
| `mapped_subquestions` | list | ✅ | Subquestion IDs that address this prompt item |
| `status` | string | ✅ | `unmapped`, `mapped`, `gap_identified` |
| `gap_note` | string | — | Why this prompt item is unanswered |

## Subquestion object

Used with prompt_items for structured coverage tracking.

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | string | ✅ | e.g. `"SQ1"` |
| `question` | string | ✅ | The sub-question text |
| `source_excerpt` | string | ✅ | Relevant source excerpt — **Required: must be non-empty or the subquestion_coverage gate fails** |
| `priority` | string | ✅ | `high`, `medium`, `low` |
| `status` | string | ✅ | `unanswered`, `answered`, `partial`, `gap_identified` |
| `answered_by` | list | — | **Claim IDs** (not source IDs) that answer this subquestion |
| `narrative_ref` | string | — | Narrative section key where answer appears |
| `module_ref` | string | — | Module ID if using modules |
| `gap_note` | string | — | Why this subquestion is unanswered |
| `loop_action` | string | — | `continue_research`, `continue_synthesis`, `ask_user`, `none` |

## narrative_sections keys

Must be one of: `executive-summary`, `background-objectives`, `methodology`, `key-findings`, `deep-insights`, `recommendations`, `risk-assessment`, `implementation-roadmap`, `gaps-limitations`.

See Phase 4 mapping table in SKILL.md for which workflow content goes where.

## report_config nesting

The script reads narrative sections from `report_config.narrative_sections` when generating reports. If your batch JSON has `narrative_sections` at the top level, the `import-ledger` command will nest it correctly. But if you manually construct the ledger file, ensure the structure is: `{ "report_config": { "narrative_sections": { ... } } }`.

## Important: narrative_sections Write Location

In the batch JSON, **always write narrative content to the top-level `narrative_sections` key** — NOT to `report_config.narrative_sections`. The `import-ledger` command automatically moves top-level `narrative_sections` content into `report_config.narrative_sections` during import.

The `report_config.narrative_sections` field in the template exists as a structural placeholder and should be left empty. If you write content directly into `report_config.narrative_sections`, it may be overwritten by the import process.
