# readme-writer — 会讲人话的 README 写作规范

> 把「帮我写个 README」变成一份**能上手、可验证、不编造**的仓库首页。核心立场：README 是**仓库首页，不是文档全书**——读者要能在首屏判断「这是不是我要的」，然后以最低摩擦跑通一次真实成功。
> 给谁用：开源库 / CLI / Web / 服务端项目的开发者、内部仓库负责人，以及代写文档的 AI Agent。

[![skill: readme-writer](https://img.shields.io/badge/skill-readme--writer-purple)](./SKILL.md) [![license: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-green)](../LICENSE) [![repo: 0xn0ne/skills](https://img.shields.io/badge/repo-0xn0ne%2Fskills-blue)](https://github.com/0xn0ne/skills)

## 这是什么 / 给谁用

**不是**：套一套模板就交差、堆满徽章和空话、或者把 API 手册整个粘进首页。

**而是**：一套「意图 → 红线 → 骨架 → 自检」的写作方法论。先推断**项目类型与主受众**，再决定哪些章节加重、哪些可以省略；交付前必须过一遍可勾选的自检清单。

| 适合 | 典型场景 |
| --- | --- |
| 开源库 / SDK 维护者 | 新建 README，或把「只有安装命令」的残页补成能上手的入口 |
| CLI / Web / 服务端开发者 | 要求 Quick Start 真的跑得通、License 与贡献态度写清楚 |
| 内部仓库负责人 | 补一份「同事进来看得懂」的入口文档，含目录结构与 oncall 链接 |
| AI Agent（代写文档） | 需要一份可执行的验收标准，避免幻觉编造命令和许可证 |

**不适合**：写 API Reference、Changelog、Contributing 细则或架构白皮书——那些属于 `docs/`、`CHANGELOG.md`、`CONTRIBUTING.md`，README 只做链接指向。

## 核心能力

- **意图先行** — 先判断项目类型与受众再选章节与深度，禁止用「套全站模板」代替对具体项目的判断。
- **Quick Start 契约** — 强制「成功定义 + 前提 + 最短命令序列（宜 ≤5 步）+ 预期输出 + 下一步链接」，禁掉「只安装不运行」的假上手。
- **DONE_WHEN 自检** — 7 条可勾选验收项，交付前逐条过，避免「看起来写完了、实际没人能用」。
- **项目类型启发式** — 7 类项目各自的加重与可减弱，见下方表格。
- **诚实降级** — 事实缺失时输出「最小可行 README + `TODO(human)` 清单」，而不是编造版本号、脚本或许可证。
- **安全与合规红线** — 不写真实密钥 / 凭证，不伪造徽章状态，不把 GPL 或专有许可证误标为 MIT。

## 快速开始

### 安装

本 skill 遵循通用的 **Agent Skills 规范**（一个目录 + 一份带 frontmatter 的 `SKILL.md`），不绑定任何特定 agent。把目录放进你所用工具的 skills 目录即可：

```bash
git clone https://github.com/0xn0ne/skills.git
cp -r skills/readme-writer/ <你的 agent 的 skills 目录>/
```

常见 agent 的 skills 目录：

| Agent | 用户级（全局可用） | 项目级（团队共享同一版本，推荐） |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/` | `<project>/.claude/skills/` |
| OpenCode | `~/.config/opencode/skills/` | `<project>/.opencode/skills/` |
| 其他支持 Agent Skills 的工具 | 按其文档指定的 skills 目录 | 同上（团队共享同一版本） |

> 不安装也能用：直接在 prompt 里给出 `SKILL.md` 的绝对路径，让 agent 加载即可。

自检（以 Claude Code 用户级为例）：`ls ~/.claude/skills/readme-writer/SKILL.md` 应能列出文件。

本 skill 由 agent 依据 `SKILL.md` frontmatter 的 `description` 自动触发（"写 README""这个仓库缺文档"等）；也可在 prompt 中显式加载。

### 最小调用（给 agent 的 prompt 模板）

```text
你是一名技术写作者。

目标仓库：<仓库绝对路径>
任务：新建 / 改写该仓库的 README.md

要求：
1. 先读取仓库文件（package.json / pyproject.toml / go.mod / LICENSE / Makefile 等）推断项目事实，再动笔。
2. 先判断项目类型与主受众，再决定章节与深度。
3. 交付前逐条过 SKILL.md §1.3 的 DONE_WHEN 清单。

加载的 SKILL 路径：<你的 skills 目录>/readme-writer/SKILL.md
```

> 不要在 prompt 里复述 SKILL.md 的内容——会遮挡 skill 本身的判断力，也容易在改写时带入过期副本。

### 输入 / 输出

输入只需**目标仓库路径**（必填）；agent 从仓库文件自行推断事实，不靠用户口述。受众语言、新建还是改写、项目类型均可留空由 agent 判断。

| 产出 | 位置 | 说明 |
| --- | --- | --- |
| 主产物 | 目标仓库的 `README.md`（默认仓库根，路径可由用户指定） | Markdown，章节按项目类型增删，不为填满而编造 |
| 缺口清单 | 文末 `## TODO for maintainers` 或对话中列出 | 每条 `TODO(human)` 需说明缺什么信息 |
| 取舍说明 | 对话层 | 关键章节增删理由，README 本身保持干净 |

## 自检清单（DONE_WHEN）

声称「完成」前逐条勾选（详见 [`./SKILL.md` §1.3](./SKILL.md)）：

```text
☐ 存在 Title + 清晰一句话描述（做什么 + 对象或场景）
☐ 存在可运行的 Quick Start（或文档型仓库的等价「5 分钟理解/使用路径」）
☐ Quick Start 含：前提、命令、（如适用）预期输出或成功判据
☐ 有 License 陈述（名称/SPDX 或 UNLICENSED + 指向），或显式 TODO
☐ 贡献态度明确（欢迎 / 仅接受某类 / 暂不接受 + 链接若有）
☐ 无断裂的站内锚点；外链不故意留空占位（未知则 TODO）
☐ 未把密钥、令牌、内网地址等敏感信息写入示例（用占位符）
```

**红线 5 条**（[`./SKILL.md` §1.5](./SKILL.md)）：不编造项目事实（命令、许可证、徽章状态、维护状态）；不写入真实密钥 / 凭证；首屏必须让人理解「是什么」，禁止价值主张被 TOC / 徽章 / 长文淹没；Quick Start 必须可验证成功；不把完整 Reference 级 API / 全部配置塞进 README（应链出）。

## 项目类型启发式

先归类，再决定章节权重（非穷尽；详见 [`./SKILL.md` §7](./SKILL.md)）：

| 类型 | 加重 | 可减弱 |
| --- | --- | --- |
| 开源库 / SDK | Install、Usage 代码、API 链接 | 长 Deployment |
| CLI 工具 | 安装后一条命令 + 帮助输出 | 重 GUI 截图 |
| Web / App | Demo 图、本地与部署 Quick Start | 过深 API |
| 服务端 / Infra | Docker Compose/K8s 最短路径、配置、安全联系 | 炫酷徽章墙 |
| 数据 / 科研代码 | 数据前提、复现实验步骤、引用 | 强 Contributing 社区文案 |
| 文档 / 规范仓库 | 「如何阅读 / 采用」路径；Install 可省略 | 强 Usage 代码 |
| 内部企业仓库 | 与公司平台链接、oncall、目录结构 | 营销式 Features |

默认骨架顺序：Title → 一句话描述 →（徽章）→（Demo）→ Features → Quick Start → Installation → Usage → Configuration →（按需扩展）→ Contributing → License。

## 工作流

8 步，非唯一剧本；步骤未覆盖时回到「意图」判断（[`./SKILL.md` §8](./SKILL.md)）：

```text
1. 校准      受众 / 语言 / 新建还是改写 / 项目类型 / 已有 docs 与 LICENSE
2. 收集事实  读取包名、脚本、许可证、示例；列出未知项
3. 定骨架    核心层必选 + 扩展层按需
4. 写首屏    名称、一句话、（可选）视觉与 3–5 条价值
5. 写 Quick Start  前提 → 命令 → 输出 → 下一步；自检可运行性
6. 补齐正文  Installation / Usage / 其他，与 Quick Start 不打架
7. 页脚      Contributing、License、Support / Security
8. 自检      DONE_WHEN + 红线 → 输出 README + TODO(human) + 取舍说明
```

改写已有 README 时，若用户未要求「全量重写」，应**保留信息并迁移 / 合并**，不要大段删除。

## 不适用 / Anti-Patterns

| 反模式 | 为什么坏 | 怎么做 |
| --- | --- | --- |
| 首屏 800 字架构哲学，无命令 | 读者在判断「是不是我要的」之前就流失 | 一句话价值后直接 Demo / Quick Start |
| `pip install .` 之后没有任何 run | 「只安装不运行」的假上手 | 补最短命令序列 + 预期输出 |
| 徽章显示 build passing，CI 其实是红的 | 编造可信度 | 不确定的徽章一律不加 |
| License 写 MIT，仓库实际是 Apache-2.0 或专有 | 法律错误 | 读 `LICENSE` 确认，不确定则 TODO |
| 把 API 手册 / 全部配置项粘进首页 | 首页变成文档全书 | README 只留最短路径，详情链出 |
| 示例里出现真实 token | 泄露凭证 | 用 `your_api_key` 或环境变量占位 |

## 目录结构

```text
readme-writer/
└── SKILL.md   # 全部方法论：意图、红线、DONE_WHEN、骨架、Quick Start 规范、类型启发式
```

本 skill 只有 `SKILL.md` 一个文件，无 `references/`、无 `scripts/`，不需要额外依赖。README 只做入口，细节以 [`./SKILL.md`](./SKILL.md) 为准。

## 许可证

Apache-2.0，详见 [`../LICENSE`](../LICENSE)。

*Last updated: 2026-09-09*
