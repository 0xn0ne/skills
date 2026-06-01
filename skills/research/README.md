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
  <p>自由探索 · 结构记录 · 机械验证 · 诚实报告</p>
</div>

---

## 语言

简体中文 | [English](./README.en.md)

---

## 目录

<details>
<summary>展开目录</summary>

- [技能简介](#技能简介)
- [核心理念](#核心理念)
- [架构设计](#架构设计)
- [快速上手](#快速上手)
- [工作流程](#工作流程)
- [实验数据](#实验数据)
- [现存 Gap](#现存-gap)
- [文件结构](#文件结构)
- [引用与致谢](#引用与致谢)

</details>

---

## 技能简介

Research Skill 不是一个搜索引擎封装，而是一个**研究顾问 + 机械验证**系统。

它让 AI Agent 能够像专业研究分析师一样工作：先理解用户的真实需求，再进行多维度深度研究，最后通过结构化账本和脚本验证确保报告质量可信赖。

**解决的核心问题：**

| 传统搜索技能 | Research Skill |
|---|---|
| 直接回答表面问题 | 先判断问题是否正确，再回答 |
| Agent 自检报告质量 | 脚本机械验证 26 道门控 |
| 单轮搜索输出 | 4 轮渐进式搜索（50+ 次） |
| 无来源追溯 | 结构化账本，每条结论可溯源 |
| 无假设验证 | 假设必须有演进（confirmed/falsified/mutated） |

---

## 核心理念

```
Think freely. Record structurally. Verify mechanically. Report honestly.
```

### 三层设计

```
┌─────────────────────────────────────────────┐
│  SOUL.md — 身份层                            │
│  "你是一个研究顾问，不是搜索引擎"            │
│  定义：意图考古学家 · 战略研究顾问           │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  SKILL.md — 控制层                           │
│  7 阶段工作流 · 14 条硬规则 · 3 个操作区     │
│  Zone A: 自由探索  Zone B: 结构引导          │
│  Zone C: 硬门控（不可自由判断）              │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  research_store.py — 验证层                  │
│  26 道验证门控 · 结构化账本 · 自动生成报告   │
│  命令：init → add-source → verify → report   │
└─────────────────────────────────────────────┘
```

### 分工原则

| 任务 | 负责方 |
|---|---|
| 用户意图推断 | Agent |
| 研究维度发现 | Agent |
| 商业/战略洞察 | Agent |
| 矛盾解释 | Agent |
| 来源、推荐记录 | Agent 写入结构化账本 |
| T1/T2 比例计算 | 脚本 |
| Trust Badge 生成 | 脚本 |
| 报告状态封顶 | 脚本验证结果决定 |
| 最终报告 | `generate-report` 生成 |

---

## 架构设计

### 研究流程概览

```
用户提问
    │
    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Phase 0-1   │    │  Phase 2     │    │  Phase 3     │
│  意图分析     │───▶│  研究计划     │───▶│  四轮搜索     │
│  矛盾检测     │    │  维度矩阵     │    │  50+ 次搜索   │
│  受众识别     │    │  假设设计     │    │  渐进式深化   │
└──────────────┘    └──────────────┘    └──────┬───────┘
                                               │
                                               ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Phase 6     │    │  Phase 5     │    │  Phase 4     │
│  报告生成     │◀───│  机械验证     │◀───│  综合分析     │
│  自检优化     │    │  26 道门控    │    │  假设演进     │
│  最终交付     │    │  Trust Badge │    │  红队辩论     │
└──────────────┘    └──────────────┘    └──────────────┘
```

### 来源分级体系

```
┌─────────────────────────────────────────────────────┐
│  T1 — 最高可信度                                     │
│  ├── T1_Academic  同行评审论文、预印本               │
│  ├── T1_Official  官方文档、法规、财报               │
│  └── T1_Data      权威数据集、政府统计               │
├─────────────────────────────────────────────────────┤
│  T2 — 专业可信度                                     │
│  ├── T2_Creator   从业者文章、工程博客、事后分析     │
│  └── T2_Data      行业数据、一手市场数据             │
├─────────────────────────────────────────────────────┤
│  T3 — 综合可信度                                     │
│  └── T3_Synthesis  专家综述、分析师报告              │
├─────────────────────────────────────────────────────┤
│  T4 — 社区可信度                                     │
│  └── T4_Community  论坛、Issue Tracker、社交媒体     │
├─────────────────────────────────────────────────────┤
│  T5 — 参考可信度                                     │
│  └── T5_Recap      教程、新闻摘要、博客回顾          │
└─────────────────────────────────────────────────────┘
```

### Claim 质量分级

| 等级 | 要求 | 用途 |
|---|---|---|
| **A** | 2+ T1/T2 主要来源 | 支撑行动建议 |
| **B** | 1+ T1/T2 主要来源 | 支撑方向判断 |
| **C** | 1+ 任意来源 | 参考信息 |
| **D** | 弱证据或单一来源 | 仅作背景 |
| **F** | 未验证或被证伪 | 红队材料 |

---

## 快速上手

### 前置条件

- Python 3.8+
- 支持的 AI Agent 平台（任选其一）

### 30 秒部署

```bash
# 克隆仓库
git clone https://github.com/your-org/research-skill.git
cd research-skill

# 验证安装
python3 scripts/research_store.py --help

# 完成！现在可以在 Agent 中使用了
```

### 平台适配

#### OpenCode

将技能目录放到 `.opencode/skills/` 下：

```bash
cp -r research-skill ~/.opencode/skills/research
```

在 `opencode.json` 中确认技能已加载：

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

将技能目录放到项目根目录的 `.skills/` 下：

```bash
mkdir -p .skills
cp -r research-skill .skills/research
```

在对话中引用技能路径：

```
请使用 .skills/research/SKILL.md 中的流程帮我研究 [主题]
```

#### 其他 Agent 平台

任何支持文件读取的 Agent 平台都可以使用。只需确保 Agent 能够：

1. 读取 `SKILL.md` 了解工作流程
2. 执行 `scripts/research_store.py` 进行验证
3. 写入 `.research/` 目录保存报告

### 使用示例

```
用户: 帮我研究一下固态电池的产业化进展

Agent 内部流程:
1. 读取 SKILL.md → 加载工作流
2. Phase 0: 识别受众（技术决策者）
3. Phase 1: 分析意图（技术选型 + 投资参考）
4. Phase 2: 制定研究计划（5 个维度）
5. Phase 3: 4 轮搜索，50+ 次查询
6. Phase 4: 提取 20+ 条 claims，假设演进
7. Phase 5: 验证 → Decision-grade PASS
8. Phase 6: 生成报告 → .research/*.final.md
9. 交付: 返回报告路径 + 3 条摘要
```

---

## 工作流程

### 7 个阶段详解

| 阶段 | 名称 | 核心任务 | 产出 |
|---|---|---|---|
| Phase 0 | 受众识别 | 识别读者角色，适配报告风格 | 受众标签 |
| Phase 1 | 意图分析 | 挖掘底层需求，检测矛盾 | Intent Frame |
| Phase 2 | 研究计划 | 维度矩阵，假设设计 | 研究蓝图 |
| Phase 3 | 四轮搜索 | R1 发现 → R2 量化 → R3 实施 → R4 验证 | 50+ 来源 |
| Phase 4 | 综合分析 | Claims 分级，假设演进，红队辩论 | 结构化账本 |
| Phase 5 | 机械验证 | 26 道门控验证 | Trust Badge |
| Phase 6 | 报告生成 | 生成报告，自检优化 | 最终报告 |
| Phase 7 | 交付 | 返回路径 + 状态 + 3 条摘要 | 交付回执 |

### 四轮搜索策略

```
Round 1: Discovery（发现）
  ├── 框架、概念、术语
  ├── 每个维度 2+ 来源
  └── 最少 15 次搜索

Round 2: Quantitative（量化）
  ├── 数字、基准、阈值
  ├── 风险因素
  └── 最少 15 次搜索

Round 3: Implementation（实施）
  ├── 落地细节、跨领域洞察
  ├── 假设状态变化
  └── 最少 10 次搜索

Round 4: Verification（验证）
  ├── 压力测试、交叉验证
  ├── 专家分歧
  └── 最少 10 次搜索
```

### 26 道验证门控

| 类别 | 门控 | 说明 |
|---|---|---|
| **结构** | `access_trace_consistency` | 来源访问状态一致性 |
| | `claim_source_integrity` | Claim 来源完整性 |
| | `recommendation_trace` | 推荐可追溯性 |
| | `narrative_completeness` | 叙事章节完整性 |
| | `empty_ledger` | 账本非空 |
| **质量** | `t1t2_ratio` | T1/T2 来源比例 ≥ 50% |
| | `claim_grade_distribution` | A/B 级 claim 分布 |
| | `source_dominance` | 单一来源贡献不超过 60% |
| | `source_diversity` | 来源类型 ≥ 3 种 |
| | `numeric_evidence_strength` | 数字证据强度 |
| **逻辑** | `thesis_narrative` | 论点与叙事一致 |
| | `edge_cases` | 边界情况覆盖 |
| | `research_closure` | 终止搜索完整性 |
| | `scope_fidelity` | 语义漂移检测 |
| **语言** | `language_alignment` | 内容语言与声明一致 |
| **红队** | `red_team_quality` | 红队辩论质量 |
| **假设** | `hypothesis_tracking` | 假设演进追踪 |
| **覆盖** | `subquestion_coverage` | 子问题覆盖 |
| | `prompt_item_coverage` | 提示项覆盖 |
| | `claim_subquestion_trace` | Claim 与子问题映射 |
| **商业** | `commercial_source_diversity` | 商业来源多样性 |
| | `vendor_bias` | 供应商偏见检测 |
| | `cross_validation` | 交叉验证 |
| **其他** | `weak_claim_usage` | 弱 claim 使用 |
| | `recommendation_actor_scope` | 推荐执行者范围 |
| | `language_alignment` | 语言对齐 |

---

## 实验数据

### 测试总览

经过 9 轮系统性测试，覆盖 45 个研究主题、35+ 个行业。

| 轮次 | 主题数 | 成功率 | 关键发现 |
|---|---|---|---|
| R1-R5 | 25 | 40-60% | 基线建立，发现脚本 Bug |
| R6-R7 | 10 | 20-40% | 修复验证，报告质量提升 |
| R8 | 5 | 40% | 分步导入 API 生效 |
| R9 | 5 | **100%** | 全部通过，首次 100% |

### 核心指标改进

| 指标 | 修复前 | 修复后 | 改进 |
|---|---|---|---|
| Phase Check Log 写入 | 0% | 100% | +100% |
| Red Team 写入账本 | 0% | 100% | +100% |
| source_excerpt 非空 | 80% | 100% | +20% |
| 假设多样性 | 低 | 高 | 显著提升 |
| 总体成功率 | 40% | 100% (R9) | +60% |

### 最佳报告案例

**CCUS 碳捕集（R6）**
- 验证状态：Decision-grade PASS
- T1/T2 比例：68.2%（15/22 来源）
- Claims：5 A-grade, 11 B-grade, 4 C-grade
- 假设演进：1 falsified + 3 mutated

**钠离子电池产业化（R9）**
- 验证状态：Decision-grade PASS（26/26 门控全通过）
- 关键发现：宁德时代 175Wh/kg + 10000 次循环
- 成本降至 0.35-0.40 元/Wh

### 动态阈值

不同场景使用不同的 T1/T2 比例阈值：

| 阈值 | T1/T2 比例 | 适用场景 |
|---|---|---|
| `default` | 50% | 标准场景 |
| `commercial` | 20% | 供应商对比、市场分析 |
| `practitioner` | 10% | 新兴技术、无学术文献 |
| `emergent` | 35% | 快速演进的新兴领域 |
| `breaking` | 30% | 突发新闻 |

---

## 现存 Gap

### 1. JSON 构建复杂度

**问题：** 复杂课题的 batch JSON 超过 30,000 字符，一次性构建对 LLM 来说几乎不可能可靠完成。

**数据：** R1-R8 中约 60% 的失败案例源于 JSON 构建错误（转义、格式、字段缺失）。

**应对：** 已提供分步导入 API（`add-source`, `add-claim` 等），每步独立验证，失败只影响单条记录。

**残留：** 部分 Agent 仍倾向于一次性构建 batch JSON，而非分步导入。

### 2. Gate Gaming

**问题：** Agent 为通过 `claim_source_integrity` 门控，主动将 B 级 claim 降为 C 级。

**数据：** R6 中发现 Agent 在 Self-Check 中写"all downgraded to C to meet claim_source_integrity"。

**应对：** 已在 SKILL.md 中明确禁止，并添加了"严禁为 gate compliance 降低 claim 级别"规则。

**残留：** 无法完全防止 Agent 的隐性降级行为。

### 3. 实施建议空洞

**问题：** 部分报告的 Implementation Roadmap 只有方向性建议（"应该加大投入"），缺少具体第一步。

**数据：** R5 中 3/5 报告缺少 30 天内可执行的具体步骤。

**应对：** 已添加 5 项实施深度检查（30 天第一步、执行主体、MVP 定义等）。

**残留：** Agent 对"什么叫好的实施建议"的理解仍需提升。

### 4. Chat 合规性

**问题：** Agent 倾向于在聊天中输出报告内容，而非仅返回交付回执。

**数据：** 约 33% 的失败案例来自 chat 合规违规。

**应对：** 已在 SKILL.md 中明确"Chat is a delivery receipt"，并提供严格的交付模板。

**残留：** 这是 Agent 行为习惯问题，无法通过文档完全解决。

### 5. task_type_framework 关键词匹配

**问题：** Gate 的正则表达式可能无法匹配到行业特定词汇（如生物技术、食品科学词汇）。

**数据：** R9 中碳纤维复合材料报告因 `cross_validation` 门控触发 Advisory 模式。

**应对：** 已在 SKILL.md 中指导 Agent 在叙事中主动使用标准关键词进行标注。

**残留：** 关键词匹配逻辑仍有优化空间。

---

## 文件结构

```
research-skill/
├── SKILL.md                    # 控制层：工作流定义
├── SOUL.md                     # 身份层：Agent 角色定义
├── README.md                   # 本文件
├── scripts/
│   └── research_store.py       # 验证层：账本与门控脚本
├── assets/
│   └── batch-ledger-template.json  # 批量导入模板
├── references/
│   ├── audience-guide.md       # 受众适配指南
│   ├── domain-analysis.md      # 领域分析要求
│   ├── fallback.md             # 脚本不可用时的降级方案
│   ├── field-reference.md      # 字段参考文档
│   ├── gate-specs.md           # 门控规格说明
│   ├── phase-checks.md         # 阶段检查模板
│   ├── phase4-details.md       # Phase 4 详细指南
│   ├── report-template.md      # 报告模板
│   ├── search-strategy.md      # 搜索策略指南
│   └── task-type-frameworks.md # 任务类型框架
└── .research/                  # 研究输出目录（自动生成）
    ├── *.final.md              # 最终报告
    ├── *.advisory.md           # 咨询报告
    ├── *.ledger.json           # 结构化账本
    └── *.temp.md               # 工作模板
```

---

## 报告状态

| 状态 | 含义 | 可用于决策？|
|---|---|---|
| `Decision-grade` | 账本通过验证，主建议有证据支持 | 是 |
| `Advisory Research` | 证据强度不足，但结构完整 | 仅供参考 |
| `Evidence Gap Report` | 研究有价值，但证据不足 | 否 |
| `Partial` | 部分发现有用，但不能支持主决策 | 否 |
| `Draft — ledger inconsistent` | 账本不一致 | 否 |

---

## 引用与致谢

本技能的设计灵感来自：

- [Best-README-Template](https://github.com/othneildrew/Best-README-Template) — README 结构参考
- 结构化研究方法论 — 来自多年企业咨询与学术研究实践
- 机械验证理念 — 来自软件工程中的 CI/CD 门控实践

---

<div align="center">
  <p><strong>自由探索 · 结构记录 · 机械验证 · 诚实报告</strong></p>
  <p><a href="#readme-top">回到顶部</a></p>
</div>
