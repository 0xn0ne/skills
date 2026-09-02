# Changelog

> 本文件是维护者的版本记录，**不进入 agent 上下文**。
> agent 执行时只读 `SKILL.md` + 按需加载的 `references/`，版本考古集中在这里。

## v9.0（重构版）

按《deep-research技能重构规划》执行的结构性重构。改动半径与原则：

- **意图置顶 / 红线单独成节 / 自主区显式授权**：SKILL.md 重写为 v9.0（意图 → 5 条红线 → 自主区 → 流程）。SKILL.md 不再含 changelog / 查找表等维护者考古。
- **单一权威**：每个概念只在一处定义。
  - 任务卡：SKILL.md §4.1（probe-search 删除了自家模板，保留增量字段指引）。
  - 5-key 信号表：SKILL.md §4.2（probe-search 的 D1-D5 表与 research_tools.py 全部对齐到同一套 key：`新检测/新深度/新比较/新视角/新维度`）。
  - 停止条件：SKILL.md §4.2 的 S1-S7（probe-search 删除 C1-C7 重复表，只保留各 S 条件的细化判据）。
  - 交付自检：SKILL.md §7 的 8 项（report-rendering 删除了独立的 7 项自检节）。
- **删除全部版本考古**：references 与 SOUL.md 中的 `v8.1.x 起/修订` 行内注释、墓碑段落（"本节原列…已删除"）、`R15 实测` 等维护者注释全部移除。版本号不再跨文件漂移。
- **修正 lens 权重表**：删除与"Cross-Domain 是固定子模块"矛盾的独立列；"假设追踪"列与 SKILL.md §5 启用条件逐格对齐（探索 = ✓）。
- **research_tools.py 修 bug**（P0）：
  - `audit`：文案 "7-item / ≥5/7" 与实际 checks 数对齐；`findings` 阈值 0 恒过的死检查已修。
  - `summary()`：置信度从伪精确的 `@ 66%` 改为三档标签反查（`@ 中`），消除内部映射泄漏。
  - `add_round()` docstring 与 SKILL.md §4.2 的 5 key 语义表同步。
  - Ledger schema 升级为多假设（`hypotheses`），`hyp` 子命令支持 `--id H2`，兼容读旧单假设格式（修复 ACH ≥2 假设与单假设 schema 的脱节）。
- **reference 文件加目录**（长参考文件官方建议）。

## v8.1.x（历史）

- **v8.1.8**：`Ledger().load()` 按 mtime 选最新文件的边界修复（`--ledger` 参数）。
- **v8.1.7**（2026-07-15）：删 2 dead references + audit subcommand + 8-item self-check + SOUL.md 第 4 锚点。
- **v8.1.6**（2026-07-15）：R16 fidelity fix（audit subcommand + 8-item self-check）。
- **v8.1.5**（2026-07-15）：用户微调全采用 + "其他文档优先"冲突解决。假设状态改为中文 4 态为主（有效/修正/无效/待定），弃用置信度百分比。
- **v8.1.2**：`已确认` 定义统一为"≥2 一手 + 全部一手"（以 suggest-label 工具为准）。
- **v8.1.3**：用户额外指定内容（代码/时间线/TCO…）的章节位置自主权。
- **v8.1.0**（2026-07-15）：argparse 重构 + 认知标签 CLI 化（claim / claims-dump / suggest-label）。
- **v8.0.0**（2026-07-14）：基于 12-问题审计全面重写，从 `research` 改名为 `deep-research`。

完整 R1-R17 回归历史见 `tests/regression-log.md`。
