# Deep Research — 决策级深度调研技能

> 把模糊的"研究一下 X"变成可拍板的决策级报告。3 阶段方法(任务卡 → 探针搜索 → 6-lens 决策)+ Satisficing 4-C 停止门 + 9 项研究工具,产出 **WH**/**NO**/**DEFER** + 边界条件 + 反方立场的可执行报告。

[![version v9.0](https://img.shields.io/badge/version-v9.0-blue)](./SKILL.md) [![skill: deep-research](https://img.shields.io/badge/skill-deep--research-purple)](./SKILL.md) [![agent: opencode](https://img.shields.io/badge/agent-opencode-orange)](#) [![license: MIT](https://img.shields.io/badge/license-MIT-green)](#)

简体中文 | [English](./README.en.md)

---

## 目录

- [这是什么 / 给谁用](#这是什么--给谁用)
- [价值榜](#价值榜)
- [快速开始](#快速开始)
- [工作流(3 阶段 + 9 项工具)](#工作流3-阶段--9-项工具)
- [输入 / 输出契约](#输入--输出契约)
- [Before / After:为什么用这个 Skill](#before--after为什么用这个-skill)
- [不适用 / Anti-Patterns](#不适用--anti-patterns)
- [决策级特性:可拍板 / 可追溯 / 可审计](#决策级特性可拍板--可追溯--可审计)
- [故障排查](#故障排查)
- [版本与升级](#版本与升级)
- [参考资料](#参考资料)

---

## 这是什么 / 给谁用

**不是**:不联网的单轮 LLM 回答,不带证据分级的"调研",不可审计的 AI 流水文。

**而是**:一套**决策级 deep-research 框架**——把模糊的"研究 X"任务拆成 **任务卡 → 探针搜索 → 6-lens 决策** 三阶段,以 **Satisficing 4-C 停止门**(避免无限搜索)终结证据收集,以 **8 项 Decision-Readiness 自检**(含工具数据保真)终结报告质量,产出你能直接拿去拍板的报告。

**适合谁**:

| 角色 | 典型场景 |
| --- | --- |
| 决策者(CEO/PM/投资人) | "该不该投 X 公司?" "该不该换供应商 Y?" "该从 SaaS Z 迁到自建吗?" |
| 战略研究员 | 跨域机会扫描、平台战略、可投资性分析 |
| 技术负责人 | 选型决策、架构 trade-off、技术债务评估 |
| 创业者 | 产品要不要做、市场进入、竞品分析 |

**不适合**:单点事实查询(用 `web_search` 即可)、纯创意写作、实时代码调试。

---

## 价值榜

- 🎯 **任务卡先行** — Frame 阶段强制写"目标 / 工作量 / 受众 / 反方条件"任务卡,Satisficing 4-C 停止门直接基于此 checklist,杜绝"我会搜到满意为止"
- 🔍 **9 类探针 + D1-D5 评估** — P1 范围 / P2 一手 / P3 对比 / P4 反方 / P5 冲突 / P6 风险 / P7 时效 / P8 市场 / P9 决策,每轮用 D1-D5 信息增益评估"继续 vs 停"
- 🧠 **ACH 竞争假设前置** — 列 ≥2 个互斥假设(例如"迁 vs 不迁 vs 推迟"),所有证据按"诊断性"分级,可诊断 = 真伪判据,不可诊断 = 仅作背景
- 🛡️ **独立性原则** — 假设状态迁移必须有**外部证据**触发,纯自我推理不能改状态(防止"我看了一下,这个不对"型循环论证)
- 📊 **8 项自检(含 audit)** — DELIVER 前必过:30 秒复述 + 动词主导 + 数字密度 + 边界 + 显式决策 + Red Team + 可执行 + **工具数据保真(audit ≥5/7)**
- ⚖️ **4 档认知标签** — 每条证据都标 [已确认] / [已公开] / [自推断] / [未验证],读者可按"信任降级"使用
- 🔄 **跨平台兼容** — Anthropic Claude Code / OpenCode / Cursor / Codex,均按 `SKILL.md` frontmatter 触发

---

## 快速开始

### 安装(3 种方式)

```bash
# 方式 A · 项目级(推荐)— 团队共享同一版本
git clone <skill-repo> ~/.config/opencode/skills/deep-research
```

### 最小调用(给 Agent 的 prompt 模板)

```
你是一名深度调研顾问。

研究主题:[用户给的开放问题]

要求:做一份决策级深度调研报告。

加载的 SKILL 路径(绝对路径): `.opencode/skills/deep-research/SKILL.md`

严格按 SKILL.md 的规则执行。
```

**完整版**(给 User 看,不需要改):

```
你是一名深度调研顾问。

研究主题:Apple 在 2026 H2 是否应自研 LLM 替代 OpenAI 合作

要求:做一份决策级深度调研报告。

加载 SKILL(必须): `.opencode/skills/deep-research/SKILL.md`
```

### 预期输出

输出 1:`research/<topic-slug>-<YYYY-MM>.md`(在 CWD `research/` 下,5 章结构 + Sources Register,带 inline 元数据)

输出 2:ledger 写到 `research/.cache/<topic-slug>-<YYYYMMDD>.json`(所有证据 / 假设迁移 / 决策可回放)

输出 3:终端打印 — 显式决策(**YES** / **NO** / **DEFER**)+ 3-7 条 Who/What/When 可执行项 + 3-5 条 Holds / Reverts 触发条件

---

## 工作流(3 阶段 + 9 项工具)

### 3 阶段框架

```
┌─ Frame(任务卡)──┐    ┌─ Dig(探针搜索)──┐    ┌─ Decide(决策)──┐
│ • 目标 / 工作量  │ →  │ • 9 类探针      │ →  │ • 6-lens 模板   │
│ • 受众 / 类型    │    │ • D1-D5 评估     │    │ • 8 项自检      │
│ • 反方条件       │    │ • 4-C 停止门     │    │ • audit 验证    │
│ • 评价标准清单   │    │ • ACH 假设迁移   │    │ • 报告输出     │
└─────────────────┘    └─────────────────┘    └────────────────┘
```

### Phase 0 · Audience Detection(决策级**强制**)

报告给谁看 → 输出格式自然调整:

| 受众 | Executive Summary 重点 | 章节权重 | 数字密度 |
| --- | --- | --- | --- |
| **决策者(CEO/board)** | 一句话拍板 + 边界 + 责任人 | 结论最重 | ≥ 60 数字 |
| **实务者(PM/eng)** | 假设 + 反方 + 实施步骤 | Findings + Risks 重 | ≥ 40 数字 |
| **研究者 / 分析师** | 方法论 + 证据链 + 数据 | Methodology + Sources 重 | ≥ 30 数字 |

### Phase 1 · Frame · 任务卡(必写)

```markdown
## 任务卡
- 目标:用户最终要做什么决定 / 获得什么认知
- 工作量:快速 / 标准 / 复杂(probe 后定)
- 受众:决策者 / 实务人员 / 研究者 / 混合
- 任务类型:决策 / 比较 / 证据综述 / 现状扫描 / 基准评测 / 探索
- 副类型(可选,0-2 个):如 [比较 + 探索]
- 范围与时间边界:可执行的时间 / 地理 / 行业范围
- 关键评价标准(必须可勾选):
  - [ ] 主张 X 由 ≥3 个独立来源支持
  - [ ] 数字 Y 已锚到 ≥1 个一手来源
  - [ ] 反方 Z 至少 1 个代表观点被引用
  - [ ] 不确定性已被显式标注
- 已知约束:预算 / 时间 / 禁用来源 / 风险偏好
- 初始判断:对答案的预判(可空)
- 反方条件:什么证据会推翻初始判断
```

### Phase 2 · Dig · 探针搜索 + Satisficing 4-C

**9 类探针**:

| Probe | 目的 | 典型问题 |
| --- | --- | --- |
| P1 范围 | 明确问题边界和主要维度 | "这个领域的主流分类、核心指标是什么?" |
| P2 一手 | 锚定关键事实和数字 | "官方数据、财报、监管文件怎么说?" |
| P3 对比 | 找差异、优劣、benchmark | "A 与 B 在价格、性能、风险上差在哪?" |
| P4 反方 | 主动寻找反证和批评 | "谁不同意?反对理由是什么?" |
| P5 冲突解释 | 解决来源矛盾 | "冲突来自时间、口径、样本还是定义?" |
| P6 风险 | 发现隐藏约束 | "法规、实施、成本、兼容性、供应链风险是什么?" |
| P7 时效 | 确认最新状态 | "最近是否有政策、价格、版本、事件变化?" |
| P8 市场 | 发现真实使用反馈 | "用户抱怨、采购障碍、市场接受度如何?" |
| P9 决策 | 判断是否足够行动 | "现在是否足以推荐、排除、等待或继续验证?" |

**D1-D5 信息增益评估**(每轮探针后):

- D1 补齐关键缺口 → 推进完成度
- D2 **改变结论**?(Highest value)
- D3 解决高可信冲突
- D4 发现关键边界条件
- D5 把主张升级到更高质量来源

**Satisficing 4-C 停止门**(任一即停):

| # | 条件 | 工具检查 |
| --- | --- | --- |
| S1 | 任务卡关键标准 checklist 全部勾选 | agent 评估 |
| S2 | 主要分歧已解决或显式未决 | agent 评估 |
| S3 | 高可信度反方出现 → 假设转 无效 | agent 评估 |
| S4 | 达到工作量硬上限(L1=20 / L2=50 / L3=80 搜索调用) | `check-stop` |

### Phase 3 · Decide · 决策 + 8 项自检

**8 项 Decision-Readiness 自检**(DELIVER 前必过):

```markdown
☐ 1. 30 秒复述测试 — Executive Summary 第一段就是答案
☐ 2. 动词主导开篇 — 不是"我们认为...",而是"建议升级"
☐ 3. 数字密度 — 按 lens 不同(决策类 ≥60 数字 / 实务类 ≥40 / 研究类 ≥30)
☐ 4. 边界条件 — 至少 1 个 Hold/Revert 触发条件
☐ 5. 显式 YES/NO/DEFER — 决策类 lens 强制
☐ 6. 反方诚实 — Red Team + Steel-manned(具体对手身份)
☐ 7. 可执行 — Who / What / When 三段
☐ 8. 工具数据保真 — `python3 scripts/research_tools.py audit` ≥5/7
```

未通过第 8 项的处置(3 选 1):

- **回填 ledger**(推荐)— 重跑 claim/round/hyp 补全数据,再写报告
- **DELAY** 报告 — 告诉用户"工具调用未成功,先简要答复"
- **改口报告** — 在末尾显式声明"本报告数据来自 in-context 推理,仅供参考"

**禁止**:audit 失败 + 沉默发报告 = 违反诚实底线。

---

## 输入 / 输出契约

### 输入契约

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `topic` | ✓ | 研究主题(开放问题,不是"WebSocket 是什么"型单点查询) |
| `工作量预期` | × | L1(快速)/ L2(标准)/ L3(复杂),agent 根据任务自动选 |
| `受众偏好` | × | 默认 = 决策者(可在 Frame 阶段调整) |
| `地理/时间边界` | × | "2026 H2 中国市场"等 |

### 输出契约(report 模板)

```markdown
# <Topic 报告>

## 0 · 元信息
- 报告日期 / 受众 / 工作量 / lens 组合 / 主要限制

## 1 · Executive Summary — 答:**WH/NO/DFFRR**(一句话拍板)

## 2 · Key Findings(3-7 条核心证据)

## 3 · Insights + Cross-Domain(2-4 段跨域启示)

## 4 · Risks + Red Team(4 视角 + Steel-manned)

## 5 · Conclusions
- 显式决策
- 3-7 条 Who/What/When 可执行项
- 3-5 条 Holds / Reverts 触发条件

## 6 · 偏差说明 + 未解缺口
- [DEVIATIONS] — 已知 assumption / 数据缺口
- [unresolved-gap] — 未覆盖问题

## Sources(≥ 5 个独立来源,带 tier 评级)
```

### 输出文件位置

```
research/
├── <topic-slug>-<YYYY-MM>.md     # 报告主文档
└── .cache/
    └── <topic-slug>-<YYYYMMDD>.json   # ledger(所有证据可回放)
```

**绝不允许**写到 `research/` 以外的路径(SKILL.md §6 Output Discipline)。

---

## Before / After:为什么用这个 Skill

| 维度 | 不使用(裸 LLM) | 使用本 skill |
| --- | --- | --- |
| 报告结构 | 5-7 段流水文,无章节 | 5 章节强制结构 + 验证 gate |
| 证据链 | 引用源 5-10 个,不分级 | T1-T5 分级 + ≥ 标注 4 档认知标签 |
| 决策可追溯 | 决策建议无 claim 引用 | 每个推荐都有 C#/S# 锚定到 ledger |
| 对抗视角 | 0 | Red Team ≥ 4 视角(技术/商业/监管/行为)+ Steel-manned |
| 验证 | 无 | **8 项 Decision-Readiness 自检**(含 audit ≥5/7) |
| 持续上下文 | 长研究后 LLM context 溢出 | Ledger 持久化,信息不回退 |
| 流程纪律 | "我会搜到满意为止" | Satisficing 4-C 停止门,防过载 |
| Hypothesis 状态 | 模糊"高/中/低" + 数字伪精度 | 有效/修正/无效/待定 4 态 + 高/中/低 3 档 |
| R17 实测认可 | 单论 7/7 + 决策 | R17 ledger: 18 sources + 14 claims + 7 findings / R17b: 26 sources + 34 claims |

---

## 不适用 / Anti-Patterns

### ❌ 不要用在

| 场景 | 原因 | 替代方案 |
| --- | --- | --- |
| 单点事实查询 | "Python 3.13 有什么新特性"无需 6-lens | `web_search` 即可 |
| 实时代码调试 | LLM context 不会保存构建状态 | 直接 IDE |
| 创意写作 / 故事创作 | 没有"决策"目标,事实溯源无意义 | 直接对话 |
| 用户明确"不要联网" | Skill 默认启用 web 搜索 | Honor user request |

### ❌ 不要这么做(Anti-Patterns)

| 反模式 | 为什么坏 |
| --- | --- |
| ✗ 给 Agent prompt 时复述 SKILL 内容 | 污染测试,SKILL 价值被 prompt 遮挡 |
| ✗ 用 L1/L2/L3 同时表达难度和受众 | 一维标签坍缩,3 维度独立(per #244) |
| ✗ 报告章节按"建议 / 分析 / 结论" 主题型标题 | 必须用"结论:推荐 rust"嵌入式标题(per #227) |
| ✗ 用"73% confidence"伪精度数字 | 改 用"高/中/低" 3 档定性 |
| ✗ audit 失败 + 沉默发报告 | 违反 SOUL.md 第 4 锚点 "数据未持久化 = 数据未存在" |
| ✗ 把"跨域"作为默认章节 | 必须按 lens 条件启用(per #245) |
| ✗ 不写 Sources Register,直接 inline [Sn] | Tools 无法注入 metadata |
| ✗ 一份报告超 50 KB | 表明缺乏 focus,应该拆分 |

### ✅ 推荐做法

- ✓ Prompt 中只给主题 + 要求 + SKILL 路径,不复述(per #362)
- ✓ Frame 阶段预设 Satisficing 4-C(per #254)
- ✓ ACH ≥2 互斥假设 + 诊断性证据(per hypothesis-redteam.md)
- ✓ 状态迁移必须有外部证据触发(独立性原则)
- ✓ DELIVER 前 audit ≥5/7
- ✓ 报告写到 `research/<slug>-<YYYY-MM>.md`

---

## 决策级特性:可拍板 / 可追溯 / 可审计

### 1. 可拍板:显式决策 + 边界

每份报告必须:

- 显式给出 **YES / NO / DEFER**(决策类 lens 强制)
- 至少 1 条 **Hold 条件**(何时重新评估 / 升级动作)
- 至少 1 条 **Revert 条件**(何时反向 / 撤销动作)
- **Who/What/When** 三段可执行清单(谁负责做什么,什么时候完成)

### 2. 可追溯:Ledger 持久化

每个关键主张都被写入 `research/.cache/<topic>-<YYYYMMDD>.json`:

```json
{
  "claim_C1": {"text": "ARR $20B", "label": "已公开",
                "sources": ["S1","S5"], "round_n": 2},
  "hyp_history": [{"from":"ALIVE","to":"MUTATED",
                   "conf":60,"source":"S5",
                   "evidence_trigger":"ARR 反超 2.2x"}]
}
```

随时可用 `python3 scripts/research_tools.py audit` 回放所有证据。

### 3. 可审计:三标签体系

每个数据点有 **2 个评级**(来源 tier + 认知标签):

| 来源 tier(发布者声誉) | 认知标签(主张本身的可信度) |
|---|---|
| 一手 / 二手 / 传闻 | 已确认 / 已公开 / 自推断 / 未验证 |

报告句例:`[S1: Apex AI 2026 财报] [一手] [已确认]` vs `[S5: 行业评论] [二手] [自推断]`

读者按"信任降级"使用 — 决策可以基于 [已确认 + 一手],推断应该明示。

### 4. ACH 竞争假设前置(防确认偏误)

报告 **开始前** 先列 ≥ 2 个**互斥**假设,所有证据按"诊断性"分级:

- **高诊断性证据** = 只支持某个假设,可证伪其他 → 用于 kill
- **低诊断性证据** = 同时支持多个 → 仅作背景

> ⚠️ 支持你偏好假设的证据,往往也支持替代假设。低诊断性证据不能拿来"无效"别人。

### 5. 独立性原则(假设状态迁移)

**状态迁移只能由外部证据触发**,自我推理不能改状态:

```
✅ 状态: 有效 → 修正(MUTATED)
  外部证据: S7 Motion 迁回 PG 实测 + S15 iBuidl 2026 ADR
  → 满足独立性原则

❌ 状态: 有效 → 无效(KILLED)
  自我推理: "我重新想了想,这个不对"
  → 违反独立性原则 — 应保持有效 / 修正,或转 待定

独立性原则是 SOUL.md 第 1 条底线之一。
```

---

## 故障排查

| 症状 | 原因 | 解决 |
| --- | --- | --- |
| 加载 SKILL 后 agent 还是用旧版 | OpenCode 内存缓存 SKILL | 把 SKILL.md 的完整内容复制到 prompt(临时) / 重启 agent |
| audit 失败 `0/7` | 调用 setup 没真调用过 claim/round | 重跑每个 subcommand,验证有 OK 输出 |
| 报告找不到 `[Sn]` 引用 inline metadata | Sources Register 不在文档末尾 | 把 Sources 段加到 markdown 末尾(独立 `## Sources` 标题) |
| `fcntl` ImportError on Windows | macOS/Linux POSIX-only API | 工具自动降级为 unlocked write,可能有 race — 升级到 Linux / macOS,或在 WSL 内跑 |
| Ledger 写到旧文件 | `Ledger().load()` 按 mtime 选最新 | v8.1.8 fix(--ledger 参数)。临时方案:用 `python3` import 直接传 `load(filepath=...)` |
| claim C# 重复编号 | 多 proess 并发,lock 失败 | CLI 调用必须 serial(SKILL.md §6 reminder) |
| 报告过长 > 50 KB | 没收紧核心主张 | 拆分为多份聚焦报告 |

### 自诊断命令

```bash
# 验证 skill 安装是否正确
ls ~/.config/opencode/skills/deep-research/SKILL.md
diff ~/.config/opencode/skills/deep-research/SKILL.md \
     <project>/.opencode/skills/deep-research/SKILL.md
# 应该输出空(byte-identical)

# 验证工具可用
python3 <skill>/scripts/research_tools.py --help
python3 <skill>/scripts/research_tools.py audit
# 应输出 15 subcommand 列表

# 验证 ledger 完整性
python3 <skill>/scripts/research_tools.py audit
# 应输出 7-item data-presence,≥5/7 必须 ✓
```

---

## 版本与升级

### 当前版本

**v9.0**(重构版)

| 维度 | 状态 |
| --- | --- |
| References | 3 个(probe-search / hypothesis-redteam / report-rendering) |
| Tools subcommand | 15 个(setup / source / round / finding / hyp [--id] / decide / summary / list / claim / claims-dump / suggest-label / check-stop / suggest-path / inline / audit) |
| Self-check items | 8 项(SKILL.md §7,唯一权威) |
| 假设状态 | 中文 4 态(有效 / 修正 / 无效 / 待定)+ 三档置信(高/中/低),多假设(ACH) |
| Ledger schema | 2.0(多假设 hypotheses[];兼容读旧 1.0) |
| 工作量上限 | L1=20 / L2=50 / L3=80 搜索调用 |

### 升级策略

- **PATCH**(8.1.x → 8.1.y):向后兼容,tool 个数加,不影响输出格式
- **MINOR**(8.x → 8.y):可能改 schema,**WARNING**:使用前跑 R-golden-cases 验证
- **MAJOR**(8 → 9):prompt 已重写——SKILL.md 重构(意图 → 红线 → 自主区 → 流程);详见 `CHANGELOG.md`

### changelog

- **v9.0**(重构):按重构规划做结构性重构——单一权威收敛(任务卡 / 5-key 信号 / 停止条件 / 8 项自检各只在一处定义)、红线单独成节、自主区显式授权、agent 上下文文件中的版本考古全部移除(→ `CHANGELOG.md`)、修复 audit 计数与死检查 + 伪精确 `@66%` 置信泄漏、多假设 ledger schema(ACH)。
- **v8.1.7**(2026-07-15):删 2 dead references + audit subcommand + 8-item self-check + SOUL.md 第 4 锚点
- **v8.1.6**(2026-07-15):R16 fidelity fix(audit subcommand + 8-item self-check)
- **v8.1.5**(2026-07-15):用户微调全采用 + "其他文档优先"冲突解决
- **v8.1.0**(2026-07-15):argparse 重构 + 认知标签 CLI 化(claim / claims-dump / suggest-label)
- **v8.0.0**(2026-07-14):基于 12-问题审计全面重写,从 `research` 改名为 `deep-research`

逐版本细节见 `CHANGELOG.md`;R1-R17 回归历史见 `tests/regression-log.md`。

---

## 参考资料

### 引用与致谢

| 来源 | 用途 |
| --- | --- |
| [Anthropic Skills 规范](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) | skill frontmatter / description / body 结构 |
| [Best-README-Template](https://github.com/othneildrew/Best-README-Template) | README 章节规范 |
| [Raymond-Hear/deep-research-prompt](https://github.com/Raymond-Hear/deep-research-prompt) | value bullet 写法 / Before-After 表 |
| [anthropics/skills](https://github.com/anthropics/skills) | skill-creator / pdf / pptx / webapp-testing 模板 |
| [obra/superpowers](https://github.com/obra/superpowers) | subagent-driven-development 流程 |

### 学术依据

| 理论 | 应用 |
| --- | --- |
| [Minto Pyramid Principle](https://barbaraminto.com/)(McKinsey / BCG / Bain) | 结论先行 / 金字塔结构 |
| [Gopen & Swan 1990](https://www.americanscientist.org/blog/the-long-view/the-science-of-scientific-writing) | 句级 7 原则 |
| [IMRaD](https://en.wikipedia.org/wiki/IMRaD) | 学术 / 商业报告通用模板 |
| [SCR(Situation/Complication/Resolution)](https://www.mckinsey.com/) | McKinsey Executive Summary 标准 |
| [Anytime Algorithms](https://en.wikipedia.org/wiki/Anytime_algorithm) | 迭代搜索(可中断) |
| [Information Foraging Theory](https://en.wikipedia.org/wiki/Information_foraging)(Pirolli & Card) | 边际价值信号 |
| [Satisficing / Herbert Simon 1956](https://en.wikipedia.org/wiki/Satisficing) | 满意即可原则 |
| [ACH(Analysis of Competing Hypotheses)](https://en.wikipedia.org/wiki/Analysis_of_Competing_Hypotheses) | 美国情报竞争假设方法 |
| [ICD 203](https://www.dni.gov/index.php/who-we-are/organizations/ic-reform-modernization-efforts/icd-203) | 美情报分析标准(Red Team 理论依据) |

### 工具与脚本

| 工具 | 用途 |
| --- | --- |
| `python3 scripts/research_tools.py setup` | 初始化 ledger |
| `python3 scripts/research_tools.py claim` | 记录认知标签主张 |
| `python3 scripts/research_tools.py hyp 有效` | 更新假设状态(中文) |
| `python3 scripts/research_tools.py check-stop --effort L2` | 4-C 停止门检查 |
| `python3 scripts/research_tools.py audit` | DELIVER 前必跑(8-item self-check 第 8) |
| `python3 scripts/research_tools.py inline --write <file>` | 自动注入 metadata |
| `python3 scripts/research_tools.py suggest-path "topic"` | 生成 `research/<slug>.md` 路径 |

### 验证用例

详细见 `tests/gold-cases.md`(14 个金标用例)+ `tests/regression-log.md`(R1-R17 历史)。

---

*Last updated: v9.0 refactor*
