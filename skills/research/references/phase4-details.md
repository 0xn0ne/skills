# Phase 4 Details

## narrative_sections mapping

Every workflow phase writes to a specific report chapter:

| Workflow Phase | narrative_sections key | Report Chapter |
|---|---|---|
| Phase 1 (Intent Frame + Conflict Audit) | `background-objectives` | Research Background & Objectives |
| Phase 2 (Research Plan + Dimension Matrix) | `methodology` | Methodology & Sources |
| Phase 3 (Progressive Research Reasoning) | `deep-insights` | Deep Insights & Attribution |
| Phase 4b (Contradictions) | `key-findings` | Key Findings & Analysis |
| Phase 4c (Dimension Discovery) | `key-findings` | Key Findings & Analysis |
| Phase 4d (Commercial Discovery) | `deep-insights` | Deep Insights & Attribution |
| Phase 4e (Pathways) | `deep-insights` | Deep Insights & Attribution |
| Phase 4f (Synthesis) | `deep-insights` | Deep Insights & Attribution |
| Phase 4g (Red Team) | `risk-assessment` | Risk Assessment |
| Phase 6 (Executive Summary) | `executive-summary` | Executive Summary |
| Phase 6 (Conclusions) | `recommendations` | Conclusions & Recommendations |
| Phase 6 (Implementation Roadmap) | `implementation-roadmap` | Implementation Roadmap |
| Phase 6 (Gaps) | `gaps-limitations` | Gaps, Limitations & Assumptions |

Work through each sub-phase in order. Each sub-phase specifies which `narrative_sections` key its content should be written to.

---

## 4a. Claims & Evidence Ledger

Turn evidence into claims. Assign every important claim a Claim ID.

**Claim grades:** A (2+ independent T1/T2), B (1+ T1/T2 + corroboration OR T4 Triangulation), C (plausible mixed), D (weak signal), F (unsupported/fabricated).

**Numeric variance rule (15%):** Extract raw values to `notes`. If variance >15%, set `disputed_data`. Details in `gate-specs.md`.

> ❌ Every claim needs non-empty text + at least one source in `primary_sources`. Claims in recommendations must have `verification_status: verified_directly` or `traced_back`.

---

## 4b. Contradictions & Tensions → `key-findings`

List at least 2 contradictions found across sources. For each:
- What sources disagree, and how
- Likely reason for the contradiction (methodology, timeframe, incentive, geography)
- Effect on the main conclusion

If no contradictions were found despite adversarial searching, document this as a potential blind spot — it is unusual and worth flagging.

---

## 4c. Dimension Discovery → `key-findings`

For every dimension in your analysis, classify:

- **Derived** (衍生维度): logically inferred from the user's framing — low discovery value, tag as `derived`
- **Source-discovered** (来源发现维度): found in T1/T2 sources, the user could not have predicted — high value, tag as `source_discovered` with source IDs

**Requirement:** At least 2 dimensions must be `source_discovered`. If you cannot meet this, document the gap and explain what searches were attempted.

For each source-discovered dimension, write: why it matters to the user's decision and what the user should do with this new information.

> ❌ Anti-pattern: Relabeling synonyms of the user's existing framing as "discoveries."

---

## 4d. Commercial Discovery → `deep-insights`

Answer for every research topic — mark unavailable answers as `[gap]`. Cover: value recipients, who pays, willingness-to-pay signal, competitive landscape, timing window, primary commercial risks, vendor/source bias.

> ❌ Skipping Commercial Discovery for "technical" topics is an anti-pattern. Document the gap if genuinely inapplicable.

> **Language note:** When writing Commercial Discovery content to the `deep-insights` narrative section, use the report language. For Chinese reports, translate field names: "价值接收方" (Value Recipients), "付费方" (Who Pays), "付费意愿信号" (Willingness-to-Pay Signal), "竞争格局" (Competitive Landscape), "时间窗口" (Timing Window), "商业风险" (Commercial Risks), "来源偏差" (Source Bias).

> **禁止使用货币符号：** 不要写 `$400`、`¥100`、`€200` 等。`$` 可能代表 USD/AUD/CAD/HKD，`¥` 可能代表 CNY/JPY。一律用明确货币名称：`400美元`、`100元人民币`、`200欧元` 或 `USD 400`、`CNY 100`、`EUR 200`。

---

## 4e. Multi-Directional Pathways → `deep-insights`

Use when research mode is Pathways/Decision/Commercial — or when evidence reveals genuine branching. For each pathway (2–3 max): premise, expected outcome, risks, evidence basis, confirming/disconfirming evidence. Write comparative summary.

### Pathways Anti-pattern

❌ **Do NOT write implementation roadmaps in Pathways.** Timeline, phase划分, resource requirements belong to Phase 6 `implementation-roadmap` section, not Phase 4e Pathways.

Pathways content should ONLY include:
- Pathway premise (前提条件)
- Expected outcome (预期结果)
- Risks (风险)
- Evidence basis (证据基础)
- Confirming/disconfirming evidence

If you find yourself writing "Phase 1: ... Phase 2: ... Phase 3: ..." in Pathways, STOP — that belongs in Implementation Roadmap.

Each Pathway must include a **第一个可执行步骤** (first action): If this path is chosen, what is the most important thing to do in the next 30 days? Include: who does it, what they do, what resources are needed. This cannot be generic ("start planning") — it must be specific and actionable.

---

## 4f. Synthesis → `deep-insights`

Integrate findings across all dimensions. Identify cross-dimensional tensions (e.g., technically feasible but commercially premature). State the main thesis using at least one of these keywords: *thesis / conclusion / decision / recommend / should / 立场 / 结论 / 建议*.

Include a "boundary conditions" block: under what circumstances would the main conclusion change?

> ✅ **推荐结构（参考 CCUS 报告 Deep Insights 格式）：**
> 阶段一：[初始认知建立]
> 阶段二：[关键数据发现]
> 阶段三：[反直觉/矛盾发现]
> 阶段四：[综合判断形成]
>
> 这不是技术推理专属，而是研究推进过程中理解深化的记录。对于非技术主题，4个维度对应：初始框架建立 → 数据结构发现 → 核心矛盾识别 → 综合判断形成。

---

## 4g. Red Team & Stress Test → `risk-assessment`

**Requirements:**
- At least 2 red_team_arguments (Decision-grade)
- Arguments must challenge the main conclusion, not minor peripheral concerns
- Arguments must span different perspectives — not two variations of the same objection

**Required perspectives (cover at least 2):**
- Technical: Does the core mechanism actually work as claimed?
- Commercial: Is the business case real or manufactured?
- Regulatory: What enforcement or policy shift would invalidate the conclusion?
- Behavioral: Will actual users / actors behave as assumed?

For each argument: `objection`, `evidence_claim_ids` (min 1), `source_ids` (min 1, T2+), `impact_if_true`, `response`, `residual_risk` (Low/Medium/High).

**Source-anchoring:** Every Red Team argument MUST be anchored by at least one T2+ source. Do not invent theoretical objections. If no contradicting source found after genuine search, document as blind spot.

> ❌ Anti-pattern: Red team arguments that amount to "there is uncertainty." The objection must be specific and falsifiable.

---

## 4h. Hypothesis Evolution

For every initial hypothesis set in Phase 2c Dimension Matrix, document its final state:

```markdown
Hypothesis [H1]: [original statement]
Initial state: [the original hypothesis]
Current state: [confirmed / falsified / mutated to: ___]
Mutation trigger: [Source ID (S_XXX) that forced the change]
Trigger claims: [Claim IDs (C_XXX) that supported/undermined]
Final confidence: [0-100%]
Notes: [why the hypothesis changed or stayed]
```

**Narrative writing note:** When writing hypothesis evolution content to the `deep-insights` narrative section, convert the technical status to natural language per report-template.md. Example: "最初认为 [initial_state]，但来自 [Source] 的证据表明 [current_state]，修正为 [mutated state]（置信度 [confidence]%）。" The technical fields above are for the ledger JSON only.

**Requirements:**
- Every hypothesis from Phase 2c Dimension Matrix MUST have a final status (no orphan `testing` hypotheses)
- If a hypothesis was falsified or mutated, you MUST link the `mutation_trigger` to the specific Source ID
- A `confirmed` hypothesis with confidence below 50% flags a quality issue — document why
- The script's `hypothesis_tracking` gate will verify these requirements mechanically

**Narrative section mapping:** Include Phase 4h hypothesis output in the `deep-insights` narrative section of the batch JSON `narrative_sections`.

---

## ❌ 内容污染反模式

不要在 narrative sections 末尾追加内部状态文字（"校验通过"、"T1/T2 比例满足"、"ADVISORY 报告"等）。这些文字会直接出现在生成的报告正文中，对读者完全无意义。内部验证内容只能写入 `phase-log`。

---

## Phase 4 Self-Check (output before Phase 5)

See `references/phase-checks.md` for the Phase 4 Self-Check template.

---

## Closure Search Requirements

Closure searches verify research completeness. Minimum 2 (non-strategic) or 3 (strategic topics).

**Two requirements (both must be satisfied):**
1. At least 1 **critical or refute** perspective
2. At least 1 **supportive, confirm, or alternative** perspective

**Field reference:**

| Field | Valid Values | Purpose |
|-------|-------------|---------|
| `search_direction` | `confirm`, `explore`, `refute`, `neutral` | What direction the search took |
| `perspective` | `supportive`, `neutral`, `critical`, `alternative` | What perspective the evidence represents |

> **Do NOT confuse these fields.** `alternative` is valid for `perspective` but NOT for `search_direction`. Using `alternative` as `search_direction` causes verification to fail with `invalid_search_direction`.
