# Task Type Frameworks

## Task Types

`market_analysis` · `competitive_intel` · `supply_chain` · `policy_analysis` · `investment_feasibility` · `technology_evaluation` · `strategic_planning`

The script auto-detects from topic/scope keywords. The `--task-type` flag is included in all script commands. Verify auto-detection: if the auto-detected task_type doesn't match the actual research, override with `--task-type <correct_type>`.

## Required Dimensions per Task Type

Phase 2c Dimension Matrix MUST include all required dimensions for the detected type. The mechanical gate `task_type_framework` verifies this.

| Task Type | Required Dimensions |
|---|---|
| `market_analysis` | market_size, growth_drivers, competitive_landscape, customer_segments, regulatory_environment |
| `competitive_intel` | feature_comparison, pricing, market_positioning, strengths_weaknesses, strategic_direction |
| `supply_chain` | supplier_landscape, cost_structure, risk_concentration, alternative_sources, logistics |
| `policy_analysis` | current_regulations, enforcement_trend, stakeholder_positions, compliance_requirements, timeline |
| `investment_feasibility` | market_opportunity, financial_model, team_capability, competitive_moat, exit_scenarios, risk_factors |
| `technology_evaluation` | capability, maturity, ecosystem, performance, cost, migration_path |
| `strategic_planning` | current_state, market_dynamics, capabilities, options, resource_requirements, timeline |

## Auto-Detection Keywords

| Task Type | Keywords |
|---|---|
| `market_analysis` | market, 市场规模, 市场份额, market size, market share, 行业分析, industry analysis, tam, sam, som |
| `competitive_intel` | competitor, 竞争, 竞品, competitive, benchmark, 对标, versus, vs, 对比分析 |
| `supply_chain` | supply chain, 供应链, supplier, 供应商, procurement, 采购, vendor, 制造商 |
| `policy_analysis` | policy, 政策, regulation, 监管, compliance, 合规, 法律, law, 法规 |
| `investment_feasibility` | invest, 投资, roi, irr, npv, feasibility, 可行性, 估值, valuation, dd, due diligence |
| `technology_evaluation` | technology, 技术, stack, architecture, framework, platform, evaluate, 评估, 选型 |
| `strategic_planning` | strategy, 战略, strategic, roadmap, 路线图, plan, 规划, go-to-market, gtm |

## Strategic Topic Detection

The script requires `prompt_items` for strategic/multi-question topics. A topic is strategic if it contains:

**STRATEGIC_KEYWORDS:** decision, commercial, strategic, invest, build, buy, adopt, market, product, procurement, operations

**MULTI_QUESTION_KEYWORDS:** compare, should, whether

**MULTI_QUESTION_PATTERN:** topic contains `?` or `？`

When any of these are detected in topic+scope, prompt_items and subquestions are required in the batch JSON.
