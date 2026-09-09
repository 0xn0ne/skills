# skills — Agent Skills 合集

> 一组遵循通用 **Agent Skills 规范**的 AI agent 技能集：每个 skill 是一个目录 + 一份带 frontmatter 的 `SKILL.md`，覆盖编码、代码审计、CLI 接口设计、深度调研、正式文档写作与 README 写作。不绑定任何特定 agent——Claude Code、OpenCode、Cursor、Codex 或任何支持该规范的工具都能加载。

[![license: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-green)](./LICENSE) [![spec: Agent Skills](https://img.shields.io/badge/spec-Agent%20Skills-blue)](https://docs.claude.com/en/docs/agents-and-tools/agent-skills) [![repo: 0xn0ne/skills](https://img.shields.io/badge/repo-0xn0ne%2Fskills-blue)](https://github.com/0xn0ne/skills)

---

## 技能一览

| Skill | 干什么 | 典型场景 |
| --- | --- | --- |
| [coding](./coding/) | 编码自律框架：先理解后实施、外科手术式修改、硬红线约束 | 开发新功能、修 bug、重构防 diff 蔓延 |
| [code-audit](./code-audit/) | 只读代码审计：7 维度 + P0/P1/P2 分级，问题定位到行号 | PR Review、合并前风险把关、技术债盘点 |
| [cli-design](./cli-design/) | 把 CLI 当公共契约治理：接口盘点、命名一致、弃用有周期 | 新增命令/标志、重构存量 CLI、弃用治理 |
| [deep-research](./deep-research/) | 决策级深度调研：任务卡 → 探针搜索 → 6-lens 决策，产出可拍板报告 | 选型决策、竞品/投资调研、战略分析 |
| [document-architect](./document-architect/) | 正式工作文档写作：报告 / 方案 / SOW / 制度 / 汇报 / 复盘 | 年度汇报、SOW 编制、项目复盘 |
| [readme-writer](./readme-writer/) | README 写作方法论：按项目类型定制 + 可验证的验收清单 | 新建仓库缺 README、改写现有文档 |

每个 skill 目录内均有独立的 `README.md`（是什么 / 怎么装 / 怎么调用）与 `SKILL.md`（完整规则），部分 skill 附带 `references/` 深度参考与 `scripts/` 工具脚本。

---

## 快速开始

### 安装（通用）

SKILL 遵循通用的 Agent Skills 规范（一个目录 + 一份带 frontmatter 的 `SKILL.md`）。把想要的 skill 目录复制进你所用工具的 skills 目录即可：

```bash
git clone https://github.com/0xn0ne/skills.git
cp -r skills/<skill-name>/ <你的 agent 的 skills 目录>/
```

常见 agent 的 skills 目录：

| Agent | 用户级（全局可用） | 项目级（团队共享同一版本，推荐） |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/` | `<project>/.claude/skills/` |
| OpenCode | `~/.config/opencode/skills/` | `<project>/.opencode/skills/` |
| 其他支持 Agent Skills 的工具 | 按其文档指定的 skills 目录 | 同上（团队共享同一版本） |

> **不安装也能用**：直接在 prompt 里给出 `SKILL.md` 的绝对路径，让 agent 加载即可。

自检（以 Claude Code 用户级为例）：`ls ~/.claude/skills/<skill-name>/SKILL.md`

### 调用方式

- **自动触发**：agent 读取 `SKILL.md` frontmatter 的 `description`，命中任务类型时自动加载（各 skill 的触发词见其 README）。
- **显式加载**：在 prompt 中给出 `SKILL.md` 绝对路径并要求严格执行，适合强制启用或调试。
- **prompt 纪律**：只给需求 + 路径 + 约束，**不要复述 SKILL 正文规则**——复述会稀释 skill 自身的约束力。

---

## 目录结构

```
skills/
├── coding/               # 编码自律框架
│   ├── SKILL.md
│   └── references/       # 代码组织 / 原则取舍
├── code-audit/           # 只读代码审计
│   ├── SKILL.md
│   └── references/       # 审计维度清单
├── cli-design/           # CLI 接口设计与治理
│   └── SKILL.md
├── deep-research/        # 决策级深度调研
│   ├── SKILL.md
│   ├── README.md / README.en.md
│   ├── references/       # 探针搜索 / 假设红队 / 报告渲染
│   └── scripts/          # research_tools.py（ledger / audit 工具链）
├── document-architect/   # 正式工作文档写作
│   ├── SKILL.md
│   └── references/       # 文体指南 / 风格指南 / 范例 / 表格规范
└── readme-writer/        # README 写作方法论
    └── SKILL.md
```

---

## 贡献

欢迎通过 Issue / PR 补充新 skill 或改进现有规则。新增 skill 请保持结构：`SKILL.md`（必填 frontmatter：`name` + `description`，description 写清触发场景）+ 可选 `references/`、`scripts/`，并附一份 README。

## 许可证

[Apache-2.0](./LICENSE)

---

*Last updated: 2026-09-09*
