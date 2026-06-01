# Research Report Template

## Design Principles

1. **结论前置** — Executive Summary first, Trust Badge in appendix
2. **信息密度** — Every sentence delivers value; no filler
3. **数据量化** — "市场规模达1200亿" not "市场很大"
4. **因果闭环** — Every conclusion traces back to evidence
5. **可执行性** — Recommendations include who/when/how/resources
6. **呼吸感** — 数据不堆砌，段落有节奏，每个数据点有上下文

---

## Report Structure

### 1. Executive Summary (执行摘要)

**Purpose:** Enable decision-makers to act without reading the full report.

**Requirements:**
- Written LAST, after all other sections are complete
- Maximum 1 page (300-500 words)
- Conclusion-first: lead with the answer, not the process

**Template:**
```markdown
## Executive Summary

**调研背景：** [一句话说明为什么做这次调研]

**核心发现：**

1. [最重要的发现 — 一句话结论，不超过40字]
   - 关键数据：[数值]（来源：[source]）
   - 决策含义：[这个发现意味着什么]

2. [第二重要发现]
   - 关键数据：[数值]（来源：[source]）
   - 决策含义：[这个发现意味着什么]

3. [第三重要发现]
   - 关键数据：[数值]（来源：[source]）
   - 决策含义：[这个发现意味着什么]

**核心建议：**
- 短期（30天内）：[具体行动]
- 中期（3-6个月）：[具体行动]

**预期价值：** [量化收益或决策影响]
```

**Quality gates:**
- Contains at least 3 quantified claims
- Each finding has a source reference
- Recommendations are actionable (who/what/when)
- No jargon without explanation
- **一页纸检查：** Executive Summary 必须在一页内（300-500字）让读者理解整个报告的核心逻辑和结论。如果不能，重新提炼直到能。

**Anti-patterns:**
- ❌ 一个段落堆砌 5+ 个括号数据注释
- ❌ 一个句子包含 3+ 个并列分句（中文句子建议不超过 60 字）
- ❌ 在 Executive Summary 中描述调研过程（只放结论）
- ❌ 使用"我们认为"等弱化语言（直接陈述结论）

---

### 2. Research Background & Objectives (调研背景与目的)

**Purpose:** Establish why this research matters and what it aims to solve.

**Transition from Executive Summary:**
> 以上发现基于以下调研背景与分析框架得出。

**Template:**
```markdown
## 调研背景与目的

### 宏观环境
[行业现状、政策环境、技术趋势 — 2-3段]

### 当前挑战
[面临的具体瓶颈或机遇 — 用数据说明]

### 调研目标
本次调研聚焦以下核心问题：
1. [具体、可衡量的目标1]
2. [具体、可衡量的目标2]
3. [具体、可衡量的目标3]

### 适用范围
- 时间范围：[如：2024-2026年数据]
- 地域范围：[如：中国大陆A股市场]
- 对象范围：[如：市值50亿以上的科技股]
```

**Quality gates:**
- Goals are specific and measurable (not "了解市场情况")
- Scope boundaries are explicit
- Background includes at least 1 quantified market data point

---

### 3. Methodology & Sources (调研方法与样本说明)

**Purpose:** Establish credibility through transparency.

**Transition from Background:**
> 基于上述调研目标，我们采用以下方法进行系统性分析。

**Template:**
```markdown
## 调研方法与样本说明

### 数据来源
| 来源类型 | 数量 | 代表性说明 |
|---------|------|-----------|
| 学术论文 (T1) | N | [覆盖的期刊/会议] |
| 官方文档 (T1) | N | [哪些机构的官方资料] |
| 行业报告 (T2) | N | [哪些咨询公司/研究机构] |
| 社区讨论 (T4) | N | [哪些平台的讨论] |

### 调研方法
- [方法1：如多源交叉验证]
- [方法2：如定量数据分析]
- [方法3：如专家意见综合]

### 局限性声明
- [局限1：如样本量限制]
- [局限2：如数据时效性]
- [局限3：如地域覆盖不完整]

### 分析框架
[使用了哪些分析模型：SWOT/PEST/波特五力/决策矩阵等]
```

**Quality gates:**
- T1/T2 ratio ≥ 50% (or documented reason for lower)
- At least 3 source tier types
- Limitations are explicitly stated (builds trust)

---

### 4. Key Findings & Analysis (核心发现与现状分析)

**Purpose:** Present what was found, organized by logical dimensions.

**Structure:** Organize by dimension, NOT by search round.

**Transition from Methodology:**
> 以下为核心发现，按 [N] 个维度组织分析。

**Template:**
```markdown
## 核心发现与现状分析

### 核心对比矩阵

> 以下是所有对比对象在关键维度上的直观对比。

| 维度 | [对象A] | [对象B] | [对象C] | 评估 |
|------|---------|---------|---------|------|
| [维度1] | [数据] | [数据] | [数据] | [优劣判断] |
| [维度2] | [数据] | [数据] | [数据] | [优劣判断] |
| [维度3] | [数据] | [数据] | [数据] | [优劣判断] |
| 综合评估 | [一句话] | [一句话] | [一句话] | — |

### 维度1：[维度名称]
**现状概述：** [1-2句总结]

| 指标 | 数值 | 来源 | 置信度 |
|------|------|------|--------|
| [指标1] | [数值] | [source] | [H/M/L] |
| [指标2] | [数值] | [source] | [H/M/L] |

**关键发现：**
- [发现1 — 量化描述]
- [发现2]

**数据可视化建议：** [建议用什么图表展示：柱状图/趋势图/饼图等]

### 维度2：[维度名称]
[同样结构]

### 有效性证据（案例/基准）
> 至少包含 1 个真实案例或基准测试结果，证明所讨论方案/技术/策略在实际中的效果。

| 案例/基准 | 来源 | 关键指标 | 效果 |
|-----------|------|---------|------|
| [案例名称] | [source] | [指标: 数值] | [优/中/差] |

### 交叉验证
[不同来源的数据是否一致？不一致的原因是什么？]
```

**Quality gates:**
- **必须包含核心对比矩阵**（对比类报告必须有一页纸的对比总览表）
- **必须包含有效性证据**（至少 1 个真实案例或基准测试结果，证明所讨论方案/技术/策略在实际中的效果）
- At least 2 dimensions covered
- Each dimension has quantified data
- Cross-validation between sources documented
- Visual design guidance for each dimension

---

### 5. Deep Insights & Attribution (归因分析与深层洞察)

**Purpose:** Move from "What" to "Why" and "What next".

**Transition from Key Findings:**
> 上述发现揭示了以下深层规律与因果关系。

**Template:**
```markdown
## 归因分析与深层洞察

### 驱动因素分析
[What is driving the trends observed in Key Findings?]

| 驱动因素 | 影响程度 | 证据来源 | 趋势方向 |
|---------|---------|---------|---------|
| [因素1] | 高/中/低 | [source] | ↑/↓/→ |
| [因素2] | 高/中/低 | [source] | ↑/↓/→ |

### 因果链条
[Finding → Cause → Effect → Implication]

### 趋势预判
| 时间维度 | 趋势判断 | 置信度 | 判断依据 |
|---------|---------|--------|---------|
| 短期(1年内) | [判断] | H/M/L | [依据] |
| 中期(1-3年) | [判断] | H/M/L | [依据] |
| 长期(3-5年+) | [判断] | H/M/L | [依据] |

### 跨领域洞察
[What methods or insights from adjacent domains apply here?]

### 假设演进
| 假设 | 初始判断 | 最终结论 | 关键证据 | 变化原因 |
|------|---------|---------|---------|---------|
| H1 | [原始假设，如"X技术将成为主流"] | [确认/修正/推翻] | [source/claim] | [为什么变了/没变] |
| H2 | [原始假设] | [确认/修正/推翻] | [source/claim] | [为什么变了/没变] |
```

**Quality gates:**
- At least 2 cause-effect chains documented
- Trend predictions have confidence levels
- Hypothesis evolution is tracked with triggers
- **假设演进使用叙述语言**（"最初认为X，但证据表明Y"），不要使用技术标记（MODIFIED/FALSIFIED）in the narrative section. The ledger JSON hypotheses use technical status fields (`confirmed`/`falsified`/`mutated`) for machine verification — this is correct and expected. The narrative report should translate these into natural language: e.g., "最初认为 X，但来自 [Source] 的证据表明 Y，修正为 Z（置信度 N%）。"

---

### 6. Conclusions & Recommendations (结论与对策建议)

**Purpose:** Convert insights into actionable decisions.

**Transition from Deep Insights:**
> 基于以上深层分析，我们得出以下结论与行动建议。

**Template:**
```markdown
## 结论与对策建议

### 核心结论
[1-2 paragraph synthesis. Must use keywords: thesis/conclusion/recommend/should/结论/建议]

### 边界条件
Under what circumstances would the main conclusion change?
- [条件1]
- [条件2]

### 行动建议

#### 短期（30天内）
| 序号 | 行动项 | 责任方 | 资源需求 | 预期产出 | 成功指标 |
|------|--------|--------|---------|---------|---------|
| 1 | [具体行动] | [谁] | [资源] | [产出] | [KPI] |

#### 中期（1-6个月）
| 序号 | 行动项 | 责任方 | 资源需求 | 预期产出 | 成功指标 |
|------|--------|--------|---------|---------|---------|
| 1 | [具体行动] | [谁] | [资源] | [产出] | [KPI] |

#### 长期（6个月+）
| 序号 | 行动项 | 责任方 | 资源需求 | 预期产出 | 成功指标 |
|------|--------|--------|---------|---------|---------|
| 1 | [具体行动] | [谁] | [资源] | [产出] | [KPI] |

### 不推荐的选项
[Explicitly state what should NOT be done and why]

### 决策框架
> 帮助读者根据自身条件选择最优路径的结构化决策工具。

**决策矩阵：**
| 条件 | 推荐路径 | 置信度 | 说明 |
|------|---------|--------|------|
| [条件1: 如"资源有限"] | [路径A] | H/M/L | [为什么] |
| [条件2: 如"追求最高收益"] | [路径B] | H/M/L | [为什么] |
| [条件3: 如"风险厌恶"] | [路径C] | H/M/L | [为什么] |

> **Decision framework completeness:** Every decision framework must include a "do nothing / status quo" row showing the cost of inaction. A decision matrix that only evaluates action options without quantifying the cost of NOT acting is incomplete. The status quo option provides the baseline against which all alternatives are measured.

**决策流程：**
[用文字或流程图描述决策路径：如果X，选A；如果Y，选B；否则选C]
```

**Quality gates:**
- Recommendations follow SMART principle
- Each recommendation has a responsible party
- Short/mid/long term breakdown exists
- "Not recommended" options are explicitly stated
- Decision framework with at least 2 conditional paths (if X → path A, if Y → path B)

---

### 7. Risk Assessment (风险识别)

**Purpose:** Identify and quantify risks.

**Transition from Conclusions:**
> 上述建议的实施面临以下风险，需提前制定缓解措施。

**Template:**
```markdown
## 风险识别

### 风险矩阵
| 风险 | 发生概率 | 影响程度 | 风险等级 | 缓解措施 |
|------|---------|---------|---------|---------|
| [风险1] | 高/中/低 | 高/中/低 | 红/黄/绿 | [措施] |
| [风险2] | 高/中/低 | 高/中/低 | 红/黄/绿 | [措施] |

### Red Team Arguments
For each argument:
- **Objection:** [Specific, falsifiable challenge to main conclusion]
- **Evidence basis:** [Source IDs supporting the objection]
- **Impact if true:** [What happens if this objection is correct]
- **Response:** [How to address or mitigate]
- **Residual risk:** [Low/Medium/High]

### 盲点声明
[What we don't know — areas where evidence is insufficient]
```

**Quality gates:**
- At least 2 risks identified
- Each risk has probability × impact assessment
- Red Team arguments are source-anchored (T2+ sources)
- Blind spots are explicitly documented

---

### 8. Implementation Roadmap (实施路径)

**Purpose:** Provide a phased execution plan.

**Transition from Risk Assessment:**
> 在充分考虑上述风险后，建议按以下路径分阶段实施。

**Template:**
```markdown
## 实施路径

### Phase 1：[名称]（[时间范围]）
**目标：** [阶段目标]
**关键动作：**
- [ ] [行动1]
- [ ] [行动2]
**里程碑：** [可验证的里程碑]
**资源需求：** [人力/资金/工具]

### Phase 2：[名称]（[时间范围]）
[同样结构]

### MVP（最小可行方案）
[If resources are limited, what is the minimum viable approach?]

### 决策点
[At what points should we re-evaluate and potentially pivot?]

### 工具与平台推荐
> 针对本调研主题，列出实施所需的具体工具、平台、框架或库。

| 类别 | 工具/平台 | 用途 | 适用场景 | 备注 |
|------|----------|------|---------|------|
| [类别1] | [工具名称] | [具体用途] | [什么情况下用] | [成本/门槛] |
| [类别2] | [工具名称] | [具体用途] | [什么情况下用] | [成本/门槛] |

### 资源需求分析
> 评估实施方案所需的各类资源投入。

| 资源类型 | 需求量 | 说明 |
|----------|--------|------|
| 时间 | [预估时间] | [关键时间节点] |
| 资金 | [预估成本] | [主要成本构成] |
| 技能 | [所需技能] | [学习曲线/培训需求] |
| 人力 | [所需人数] | [关键角色] |
| 基础设施 | [硬件/软件/服务] | [具体需求] |
```

**Quality gates:**
- At least 2 phases defined
- Each phase has clear milestones
- MVP is identified
- Decision points are specified
- At least 1 tool/platform recommended (generic — applies to any domain)
- Resource requirements cover at least 3 types (time, cost, skills, manpower, infrastructure)

### Implementation Roadmap — 质量门

> ✅ **参考格式：** 细胞农业报告 Implementation Roadmap 的表格格式 — Phase 1/2/3、责任人列表、资源需求、成功指标、MVP 定义、决策触发点、工具推荐表——完整覆盖了所有要素。

每个实施步骤必须通过"落地检验"——问自己：一个昨天才接手这个项目的人，能从这段话里知道明天第一件事做什么吗？

**实施深度检验（每个阶段至少满足以下 5 项中的 3 项）：**

1. **执行主体具名：** 不是"相关机构"，是"采购团队" / "CFO" / "政府事务负责人" / "技术负责人"
2. **第一步骤可执行：** 30天内最重要的一个具体动作（打哪个电话、签哪个协议、做哪个测试）
3. **资源已量化：** 时间成本、资金成本、人力投入中至少一项有数字
4. **决策触发点明确：** 什么具体事件/数据触发进入下一阶段（不是"视情况而定"）
5. **成功指标可验证：** 如何判断这个阶段结束了（里程碑、数据阈值、交付物）

如果无法做到以上任意 3 项，说明这条建议还处在战略层，应该移到 Conclusions & Recommendations，而不是放在 Implementation Roadmap。

### MVP（最小可行方案）— 必填

如果决策方资源受限，当前最低成本的第一步是什么？要求：
- 一段话，不超过 100 字
- 包含：做什么 + 谁做 + 花多少时间/钱 + 如何验证结果

---

### 9. Gaps, Limitations & Assumptions (局限性与假设)

**Purpose:** Transparency about what the research doesn't cover.

**Template:**
```markdown
## 局限性与假设

### 未验证的假设
| 假设 | 验证方法 | 状态 | 影响 |
|------|---------|------|------|
| [假设1] | [方法] | 未验证 | [如果假设错误会怎样] |

### 数据空白
| 缺失数据 | 重要性 | 获取方式 | 建议 |
|---------|--------|---------|------|
| [数据1] | 高/中/低 | [如何获取] | [下一步] |

### 范围外议题
[What was explicitly excluded from this research and why]

### 偏差风险
- 选择偏差：[description]
- 时效偏差：[description]
- 来源偏差：[description]
```

---

### Appendix (附录)

**附录导读：**

| 附录板块 | 目标读者 | 用途 | 何时需要查看 |
|---------|---------|------|------------|
| Trust Badge | 审计人员、质量管理者 | 验证报告通过的质检门 | 需要确认报告可信度时 |
| Evidence Ledger | 研究人员、事实核查员 | 追溯每个结论的证据链 | 对某个结论有疑问时 |
| Source List | 研究人员、合规人员 | 查看所有数据来源的详情 | 需要引用原始来源时 |
| Verification Gates | 技术人员、质量管理者 | 查看每个质检门的详细结果 | 需要了解报告质量细节时 |
| Phase Check Log | 研究人员、项目管理者 | 查看研究过程的审计轨迹 | 需要了解研究决策过程时 |

**Contains (generated by script):**
- Trust Badge (verification metadata)
- Evidence Ledger (all claims with grades)
- Source List (all sources with tiers)
- Verification Gates (all gate results)
- Phase Check Log (research process audit trail)

**Optional narrative appendix:**
- 原始数据表
- 术语表
- 方法论详情
- 访谈纪要

---

## Writing Quality Standards

### Language
- **量化优先**：用数字替代形容词。"市场份额达23%" not "市场份额较高"
- **结论先行**：每段第一句是结论，后面是支撑
- **因果清晰**：避免"A和B相关"，要说明"A导致B，因为..."
- **主动语态**："我们发现..." not "被发现..."

### Sentence Length
- **中文句子**：建议不超过 60 字，复杂句不超过 80 字
- **英文句子**：建议不超过 25 words，复杂句不超过 40 words
- **并列分句**：一个句子中不超过 2 个并列分句
- **数据堆砌**：一个段落中不超过 3 个括号注释

### Section Transitions
每个章节的第一段应包含过渡句，连接上一章节的结论：
- Executive Summary → Background: "以上发现基于以下调研背景与分析框架得出。"
- Background → Methodology: "基于上述调研目标，我们采用以下方法进行系统性分析。"
- Methodology → Key Findings: "以下为核心发现，按 [N] 个维度组织分析。"
- Key Findings → Deep Insights: "上述发现揭示了以下深层规律与因果关系。"
- Deep Insights → Conclusions: "基于以上深层分析，我们得出以下结论与行动建议。"
- Conclusions → Risk: "上述建议的实施面临以下风险，需提前制定缓解措施。"
- Risk → Roadmap: "在充分考虑上述风险后，建议按以下路径分阶段实施。"

### Metadata Consistency
**报告状态一致性校验（Phase 7 必须执行）：**
- 报告标题中的状态标识（ADVISORY / Decision-grade）必须与正文、Trust Badge 中的状态一致
- T1/T2 比率在正文、Methodology、Trust Badge 中必须一致
- ADVISORY 报告中不得出现"决策级"、"Decision-grade"等标识
- ADVISORY 报告中的建议必须是"验证/探索型"，不得包含直接行动建议

### Visual Design
- 每个图表上方有一句结论性标题
- 表格不超过3种主色
- 使用Mermaid流程图展示复杂关系
- 编号系统统一（1. / 1.1 / 1.1.1）

### Evidence Standards
- 事实标注引用（[source ID]）
- 观点明确标注为观点
- 争议性数据标注争议原因
- 时效性数据标注采集时间
