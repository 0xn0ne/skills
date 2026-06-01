# Audience Adaptation Guide

## Purpose

The same research findings should be presented differently depending on who reads the report. This guide defines how to adapt the report structure, emphasis, and language for different audiences.

---

## Audience Detection

Detect audience from the user's prompt. Look for these signals:

| Signal | Audience |
|--------|----------|
| "帮我看看" / "帮我调研" / "analyze" | General — use default structure |
| "给老板看" / "给领导汇报" / "for executives" | Executives |
| "投资" / "估值" / "回报" / "investor" / "ROI" | Investors |
| "技术选型" / "架构" / "implementation" / "developer" | Developers/Researchers |
| "产品" / "运营" / "用户" / "product" / "user" | Product/Operations |
| "论文" / "学术" / "academic" / "paper" | Academic |
| "投标" / "提案" / "proposal" / "bid" | Proposal/Bid |

If no clear signal, use **General** audience.

---

## Audience Profiles

### General (default)
**Reading scenario:** Needs to understand the topic and make informed decisions.

| Section | Emphasis | Length |
|---------|----------|--------|
| Executive Summary | ★★★ | 1 page |
| Background | ★★ | 1-2 pages |
| Methodology | ★ | 0.5 page |
| Key Findings | ★★★ | 3-5 pages |
| Deep Insights | ★★ | 2-3 pages |
| Recommendations | ★★★ | 2-3 pages |
| Risk Assessment | ★★ | 1 page |
| Roadmap | ★★ | 1 page |
| Appendix | ★ | As needed |

**Implementation Depth:** 三个层级：今天能做、本月能做、本季度能做

---

### Executives (高管/领导人)
**Reading scenario:** Decision meeting, extremely time-constrained. May only read Executive Summary.

**Adaptation:**
- **Lead with conclusions** — Executive Summary is 80% of the value
- **Quantify everything** — ROI, timeline, resource requirements
- **Reduce process detail** — Skip Methodology, minimize Background
- **Clear action items** — Who does what by when
- **Include "don't do" options** — What to avoid and why

| Section | Emphasis | Length |
|---------|----------|--------|
| Executive Summary | ★★★★★ | 1-2 pages (expand) |
| Background | ★ | 0.5 page (condense) |
| Methodology | Skip | — |
| Key Findings | ★★ | 1-2 pages (top-level only) |
| Deep Insights | ★★ | 1 page (key drivers only) |
| Recommendations | ★★★★★ | 2-3 pages (expand) |
| Risk Assessment | ★★★ | 1 page |
| Roadmap | ★★★ | 1 page |
| Appendix | Skip | — |

**Implementation Depth:** 短期行动必须有ROI数字、责任人、时间线；每条建议写成"谁在什么时间做什么、预期结果是什么"

**Language adjustments:**
- Use business language, not technical jargon
- Lead every section with the conclusion
- Use bullet points, not paragraphs
- Include a "Bottom Line Up Front" (BLUF) at the top

---

### Investors (金融/投资工作者)
**Reading scenario:** Investment analysis, focus on returns and risks.

**Adaptation:**
- **Financial metrics** — Market size, growth rate, valuation, ROI
- **Risk quantification** — Probability × impact, downside scenarios
- **Competitive landscape** — Market share, positioning, moats
- **Exit scenarios** — How to realize returns
- **Minimize technical details** — Focus on business outcomes

| Section | Emphasis | Length |
|---------|----------|--------|
| Executive Summary | ★★★★★ | 1 page |
| Background | ★★ | 1 page (market focus) |
| Methodology | ★ | 0.5 page |
| Key Findings | ★★★★ | 3-4 pages (financial focus) |
| Deep Insights | ★★★ | 2-3 pages (market drivers) |
| Recommendations | ★★★★ | 2-3 pages (investment actions) |
| Risk Assessment | ★★★★★ | 2 pages (expand) |
| Roadmap | ★★ | 1 page |
| Appendix | ★★ | Financial models, data tables |

**Implementation Depth:** 投资决策触发条件（估值/里程碑/退出时机）；尽调清单；"不投资"的替代方案

**Language adjustments:**
- Use financial terminology (NPV, IRR, CAGR, TAM/SAM/SOM)
- Quantify all claims with monetary values where possible
- Include sensitivity analysis
- State assumptions explicitly

---

### Developers/Researchers (科技/研发人员)
**Reading scenario:** Technical evaluation, focus on feasibility and implementation.

**Adaptation:**
- **Technical depth** — Architecture, performance benchmarks, code examples
- **Comparison tables** — Feature-by-feature comparison
- **Implementation details** — How to actually do it
- **Minimize market narrative** — Focus on technical merits
- **Include code/config examples** — Where applicable

| Section | Emphasis | Length |
|---------|----------|--------|
| Executive Summary | ★★★ | 0.5 page |
| Background | ★ | 0.5 page (technical context) |
| Methodology | ★★ | 1 page (technical approach) |
| Key Findings | ★★★★ | 4-5 pages (technical depth) |
| Deep Insights | ★★★★ | 3-4 pages (architecture, performance) |
| Recommendations | ★★★ | 2 pages (technical actions) |
| Risk Assessment | ★★ | 1 page (technical risks) |
| Roadmap | ★★★ | 1-2 pages (implementation phases) |
| Appendix | ★★★ | Code samples, configs, benchmarks |

**Implementation Depth:** 具体工具版本、API端点、配置参数、已知坑；不能只写"使用X技术"而不说怎么用

**Language adjustments:**
- Use technical terminology precisely
- Include code snippets where relevant
- Provide benchmark data with methodology
- Compare specific tools/frameworks/versions

---

### Academic (学术/科研)
**Reading scenario:** Literature review, methodology validation, reproducibility.

**Adaptation:**
- **Rigorous methodology** — Detailed research design
- **Citation quality** — All claims traced to peer-reviewed sources
- **Limitations section** — Expanded, honest assessment
- **Reproducibility** — Enough detail to replicate
- **Statistical rigor** — Significance tests, confidence intervals

| Section | Emphasis | Length |
|---------|----------|--------|
| Executive Summary | ★★ | 0.5 page (abstract style) |
| Background | ★★★ | 2-3 pages (literature review) |
| Methodology | ★★★★★ | 2-3 pages (expand significantly) |
| Key Findings | ★★★★ | 4-5 pages (with statistical rigor) |
| Deep Insights | ★★★ | 2-3 pages (theoretical implications) |
| Recommendations | ★★ | 1 page (future research directions) |
| Risk Assessment | ★★ | 1 page (methodology limitations) |
| Roadmap | ★ | 0.5 page |
| Appendix | ★★★★ | Full data, methodology details, ethics statement |

**Implementation Depth:** 未来研究议程；数据收集方案；复现所需的具体条件

**Language adjustments:**
- Use academic conventions (hedging, citation format)
- Include confidence intervals and p-values where applicable
- State limitations prominently
- Distinguish correlation from causation explicitly

---

### Product/Operations (产品/运营人员)
**Reading scenario:** Execution planning, focus on user impact and implementation path.

**Adaptation:**
- **User-centric** — Focus on user needs, behavior, journey
- **Actionable insights** — What to build, how to prioritize
- **Competitive features** — Feature comparison matrix
- **Timeline** — When to deliver what
- **Minimize theory** — Focus on practical execution

| Section | Emphasis | Length |
|---------|----------|--------|
| Executive Summary | ★★★★ | 1 page |
| Background | ★★ | 1 page (user/market context) |
| Methodology | ★ | 0.5 page |
| Key Findings | ★★★★ | 3-4 pages (user/market focus) |
| Deep Insights | ★★★ | 2 pages (user behavior drivers) |
| Recommendations | ★★★★ | 2-3 pages (product actions) |
| Risk Assessment | ★★ | 1 page |
| Roadmap | ★★★★ | 2 pages (product roadmap) |
| Appendix | ★ | Feature specs, competitive matrix |

**Implementation Depth:** 功能优先级矩阵（四象限）；用户测试设计；发布检查清单

---

### Gaming (游戏开发者)
**Reading scenario:** Game design reference, focus on mechanics, monetization, player psychology.

**Adaptation:**
- **Game-specific analysis** — Core loop, monetization model, player retention
- **Technical stack** — Engine compatibility, performance constraints, platform requirements
- **Market data** — Genre trends, player demographics, revenue models
- **Case studies** — Successful/failed games with structured analysis

| Section | Emphasis | Length |
|---------|----------|--------|
| Executive Summary | ★★★ | 1 page |
| Background | ★★ | 1 page (market/genre context) |
| Methodology | ★ | 0.5 page |
| Key Findings | ★★★★ | 3-4 pages (mechanics, monetization, player data) |
| Deep Insights | ★★★ | 2 pages (player psychology, market trends) |
| Recommendations | ★★★ | 2 pages (design actions) |
| Risk Assessment | ★★ | 1 page |
| Roadmap | ★★★ | 1-2 pages (development phases) |
| Appendix | ★ | Technical specs, competitive analysis |

---

### Creative (创作/内容人员)
**Reading scenario:** Inspiration, trend identification, tool evaluation.

**Adaptation:**
- **Trend analysis** — Content format evolution, platform algorithm changes
- **Tool comparison** — Creative tools, AI assistants, workflow optimization
- **Platform-specific** — Algorithm logic, content policies, monetization
- **Case studies** — Successful creators/content with structured analysis

| Section | Emphasis | Length |
|---------|----------|--------|
| Executive Summary | ★★★ | 1 page |
| Background | ★★ | 1 page (industry/platform context) |
| Methodology | ★ | 0.5 page |
| Key Findings | ★★★★ | 3-4 pages (trends, tools, platforms) |
| Deep Insights | ★★★ | 2 pages (content evolution, audience behavior) |
| Recommendations | ★★★ | 2 pages (creative actions) |
| Risk Assessment | ★★ | 1 page |
| Roadmap | ★★ | 1 page |
| Appendix | ★ | Tool specs, platform data |

---

## Section Reordering by Audience

The script generates sections in a fixed order. For audience-specific emphasis, the agent should:

1. **Expand** sections that matter most (add detail, examples, data)
2. **Condense** sections that matter less (summarize in 1-2 sentences)
3. **Never skip** required sections — mark as "[简要说明]" instead

---

## Language Adaptation

| Audience | Tone | Jargon Level | Sentence Style |
|----------|------|-------------|----------------|
| Executives | Confident, direct | Business jargon OK | Short, punchy |
| Investors | Analytical, cautious | Financial terms | Precise, quantified |
| Developers | Technical, precise | Technical terms OK | Detailed, structured |
| Academic | Hedged, rigorous | Academic conventions | Complex, nuanced |
| Product | Action-oriented | Product terms | Clear, actionable |
| Gaming | Energetic, specific | Game dev terms | Concrete, example-driven |
| Creative | Inspirational, trend-aware | Content/platform terms | Visual, trend-forward |
