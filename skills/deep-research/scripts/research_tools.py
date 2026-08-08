#!/usr/bin/env python3
"""
research_tools.py — deep-research skill 工具集

持久化研究状态机 (Ledger) + markdown 报告 inline 元数据注入 + 认知标签/工作量/路径助手。
对外暴露 Python API + CLI 双向入口。

⚠️  使用注意:同一 ledger 上的 CLI 调用必须**串行** (sequential),等前一个完成再发下一个。
   fcntl.flock 保证 POSIX 跨进程并发安全,但跨进程竞争 + 时序在边界条件下仍可能丢数据。
   这是 SKILL.md §2 的工程红线。

╔═══════════════════════════════════════════════════════════════════════╗
  CLI 用法
╚═══════════════════════════════════════════════════════════════════════╝

  # ── ledger 长上下文持久化 ──
  python3 research_tools.py setup            <topic> [hypothesis] [initial_conf]
  python3 research_tools.py source           <sid> <url> --tier --title --date
  python3 research_tools.py round            <n> <signal_json> [summary]
  python3 research_tools.py finding          <text> [--claims C1,C2,C3] [--sources S1,S2] [--round N]
  python3 research_tools.py hyp              <state> <conf> <trigger> [--id H1|H2] [source] [reason]
  python3 research_tools.py decide           <decision> [recommendation] [boundary]
  python3 research_tools.py summary          [filepath]
  python3 research_tools.py list

  # ── 认知标签 / 工作量助手 / 路径助手 ──
  python3 research_tools.py claim            <text> <label> [--sources S1,S2] [--round N]
  python3 research_tools.py claims-dump      [--label LABEL]
  python3 research_tools.py suggest-label    [--sources S1,S2]
  python3 research_tools.py check-stop       [--effort L1|L2|L3]
  python3 research_tools.py suggest-path     <topic>
  python3 research_tools.py audit            # 验证 ledger 真的写入了数据 (交付门第 8 项)

  # ── inline 元数据注入 ──
  python3 research_tools.py inline <file.md> [--write]

╔═══════════════════════════════════════════════════════════════════════╗
  Python API
╚═══════════════════════════════════════════════════════════════════════╝

  from research_tools import Ledger, inline_metadata

  l = Ledger()                                          # 默认 research/.cache/
  l.setup("Python 3.13", "升级推荐...", initial_conf="高")
  l.add_source("S1", "https://docs.python.org/...", "Primary",
               "What's New", "2024-10")
  l.add_round(1, {"新检测":"Y", "新深度":"Y", "新比较":"N",
                  "新视角":"Y", "新维度":"N"}, summary="PEP 703 + 744")
  l.add_hypothesis_update("修正", "中", "5-10% FT 损失",
                          source="S5", mutation_reason="需 ≥3.13.7")
  # 多假设 (ACH):用 hid 区分 H1/H2/H3
  l.add_hypothesis_update("无效", "低", "出口管制已生效", hid="H2")
  print(l.summary())

  # Inject inline metadata into a written report
  inline_metadata("research/my-report.md", write=True)

╔═══════════════════════════════════════════════════════════════════════╗
  契约 (术语以 SKILL.md §4.2 为唯一权威)
╚═══════════════════════════════════════════════════════════════════════╝
  storage_dir            默认 "research/.cache/" (CWD 下,自动 mkdir)
  source tier            Primary | Secondary | Anecdotal  (= 一手 / 二手 / 传闻)
  hypothesis state       有效 | 修正 | 无效 | 待定  (内部存 ALIVE/MUTATED/KILLED/UNRESOLVED)
  hypothesis conf        高 | 中 | 低 | 未知  (内部存 100/66/33/0;summary() 反查回三档标签)
  decision label         YES | NO | DEFER
  Round                  1 轮 = 1 次成功的搜索工具调用;硬上限 L1=20 / L2=50 / L3=80
  信号测试 (每轮)       新检测 / 新深度 / 新比较 / 新视角 / 新维度 (Y/N),
                         Sum ≥ 1 = 该轮有推进,Sum = 0 = 加速到上限
  schema_version         2.0  (多假设 hypotheses[];兼容读旧 1.0 单假设格式)
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
import argparse

try:
    import fcntl  # POSIX-only (macOS, Linux). Windows falls back to unlocked writes.
    _HAS_FCNTL = True
except ImportError:
    fcntl = None  # type: ignore
    _HAS_FCNTL = False


# ═══════════════════════════════════════════════════════════════════════════
#  Section A · 持久化状态机 (Ledger)
# ═══════════════════════════════════════════════════════════════════════════


_save_counter = 0


# Internal confidence is stored as int (100/66/33/0) for backward compat with
# the 4-state schema, but reports must show qualitative labels (高/中/低/未知),
# NEVER pseudo-precise numbers like 66% (SKILL.md §2 red line). This is the
# single place that reverse-maps the stored int back to a label.
_CONF_LABEL = {100: "高", 66: "中", 33: "低", 0: "未知"}


def _conf_int_to_label(n) -> str:
    """Reverse-map internal confidence int → mandated 3-level qualitative label."""
    if isinstance(n, str):
        return n  # already a label string
    if n is None:
        return "未知"
    # Exact canonical values first
    if n in _CONF_LABEL:
        return _CONF_LABEL[n]
    # Legacy arbitrary int (0-100): bucket into the three levels
    if n >= 80:
        return "高"
    if n >= 40:
        return "中"
    if n > 0:
        return "低"
    return "未知"


class Ledger:
    """One-file ledger for a single research topic. Auto-persists on every mutation."""

    def __init__(self, storage_dir: str = "research/.cache"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.state = {
            "schema_version": "2.0",
            "created_at": datetime.now().isoformat(),
            "topic": "",
            "hypothesis": {
                "claim": "",
                "state": "ALIVE",
                "initial_conf": 50,
                "current_conf": 50,
                "history": [],
            },
            "hypotheses": {},   # multi-hypothesis (ACH): {"H1": {claim,state,conf,history}, ...}
            "rounds": [],
            "sources": {},
            "findings": [],
            "claims": [],
            "decisions": None,
            "updated_at": None,
        }
        self._current_filepath: Path | None = None

    # ── Setup ──────────────────────────────────────────────────────────

    def setup(self, topic: str, hypothesis: str = "", initial_conf: "int|str" = 50) -> "Ledger":
        """Initialize or update a ledger for a single research topic.

        initial_conf can be:
        - int (0-100): legacy numeric form, kept for backward compat
        - str: one of "高" / "中" / "低" / "未知" (3-level confidence).
          Stored as int internally (100/66/33/0) for backward compat with
          the 4-state schema. Hypothesis-redteam.md mandates 3-level
          qualitative labels, NOT pseudo-precise numbers like 73%.
        """
        if isinstance(initial_conf, str):
            label_map = {"高": 100, "中": 66, "低": 33, "未知": 0}
            if initial_conf not in label_map:
                raise ValueError(
                    f"initial_conf must be int 0-100 or one of {list(label_map.keys())}, "
                    f"got {initial_conf!r}. "
                    f"Tip: use 高/中/低/未知 for qualitative, or int 0-100 for numeric.")
            initial_conf = label_map[initial_conf]
        elif not (0 <= initial_conf <= 100):
            raise ValueError(
                f"initial_conf must be 0-100, got {initial_conf}. "
                f"Tip: use 高/中/低/未知 instead of numbers.")
        self.state["topic"] = topic
        self.state["hypothesis"]["claim"] = hypothesis
        self.state["hypothesis"]["initial_conf"] = initial_conf
        self.state["hypothesis"]["current_conf"] = initial_conf
        # Initialize multi-hypothesis slot H1 (mirrors the legacy single hypothesis)
        self.state["hypotheses"] = {
            "H1": {
                "claim": hypothesis,
                "state": "ALIVE",
                "conf": initial_conf,
                "history": [],
            }
        }
        slug = self._slugify(topic)
        date_str = datetime.now().strftime("%Y%m%d")
        self._current_filepath = self.storage_dir / f"{slug}-{date_str}.json"
        self._save()
        return self

    # ── Mutations ──────────────────────────────────────────────────────

    def add_source(self, sid: str, url: str = "", tier: str = "二手",
                   title: str = "", date: str = "") -> "Ledger":
        """Record a source. tier ∈ {Primary, Secondary, Anecdotal}
        OR Chinese aliases {一手, 二手, 传闻} — always normalized to Chinese
        for consistency across summary/audit/suggest-label/inline."""
        _TIER_EN_TO_ZH = {"Primary": "一手", "Secondary": "二手", "Anecdotal": "传闻"}
        _VALID_TIERS = set(_TIER_EN_TO_ZH.keys()) | set(_TIER_EN_TO_ZH.values())
        if tier not in _VALID_TIERS:
            raise ValueError(
                f"tier must be one of {sorted(_VALID_TIERS)}, got {tier!r}")
        tier = _TIER_EN_TO_ZH.get(tier, tier)  # normalize EN → ZH
        if sid in self.state.get("sources", {}):
            print(f"Warning: source {sid} already exists, overwriting.",
                  file=sys.stderr)
        self.state["sources"][sid] = {
            "url": url, "tier": tier, "title": title, "date": date
        }
        self._save()
        return self

    def add_round(self, n: int, signal_test: dict, summary: str = "") -> "Ledger":
        """Record a research round with 5-signal progress check.

        signal_test keys (JSON key 与 SKILL.md §4.2 完全一致, each "Y"/"N"):
          新检测 = 是否补齐了 Must-have 证据缺口?
          新深度 = 是否把关键主张升级到更高级来源?
          新比较 = 是否发现或解决了来源冲突?
          新视角 = 是否可能改变结论、推荐或排序?
          新维度 = 是否发现新的边界条件、约束或风险?

        Sum ≥ 1 = 该轮有推进;Sum = 0 → 下一 probe 必须 pivot;
        连续 2 轮 Sum=0 且无高风险未决项 → 进 Decide (SKILL.md §4.2 S5).
        """
        required = {"新检测", "新深度", "新比较", "新视角", "新维度"}
        missing = required - set(signal_test.keys())
        if missing:
            raise ValueError(
                f"signal_test missing keys: {missing}. "
                f"Use: {{\"新检测\":\"Y\",\"新深度\":\"Y\",\"新比较\":\"N\",\"新视角\":\"N\",\"新维度\":\"N\"}}")
        if not isinstance(n, int) or n < 1:
            raise ValueError(
                f"round number must be a positive integer, got {n!r}. "
                f"Tip: rounds are numbered 1, 2, 3...")
        # Normalize values to uppercase Y/N; ignore extra keys beyond the 5
        normalized = {}
        for k in required:
            v = str(signal_test[k]).strip().upper()
            if v not in ("Y", "N"):
                raise ValueError(
                    f"signal_test['{k}'] must be 'Y' or 'N', got {signal_test[k]!r}. "
                    f"Note: lowercase y/n are auto-normalized.")
            normalized[k] = v
        self.state["rounds"].append({
            "n": n,
            "signal_test": normalized,
            "summary": summary,
            "timestamp": datetime.now().isoformat(),
        })
        self._save()
        return self

    def add_finding(self, text: str, sources: list | None = None,
                    round_n: int | None = None,
                    claim_ids: list | None = None) -> "Ledger":
        """Record a key finding — a structural conclusion built from claims.

        Workflow (SKILL.md §4):
          Dig phase    → claim (atomic verifiable facts with cognitive labels)
          Decide phase → finding (chapter-anchor conclusions, each backed by ≥2 claims)

        Each finding maps to one Key Findings section in the report.
        """
        # Validate claim IDs exist
        if claim_ids:
            existing = {c["id"] for c in self.state.get("claims", []) if c.get("id")}
            missing = [c for c in claim_ids if c not in existing]
            if missing:
                print(f"Warning: claim IDs not found in ledger: {missing}. "
                      f"Finding recorded but references may be broken.",
                      file=sys.stderr)
        fid = f"F{len(self.state['findings']) + 1}"
        # Dedup claim IDs while preserving order
        seen = set()
        unique_claims = []
        for c in (claim_ids or []):
            if c not in seen:
                seen.add(c)
                unique_claims.append(c)
        self.state["findings"].append({
            "id": fid,
            "text": text,
            "sources": sources or [],
            "round": round_n,
            "claims": unique_claims,
        })
        self._save()
        return self

    def add_hypothesis_update(self, state: str, conf: "int|str", evidence_trigger: str,
                              source: str = "", mutation_reason: str = "",
                              hid: str = "H1") -> "Ledger":
        """Update a hypothesis. state ∈ {有效, 修正, 无效, 待定} (中文为主).

        conf accepts int 0-100 (legacy) or one of "高"/"中"/"低"/"未知".
        Per hypothesis-redteam.md: 3-level qualitative labels are mandated;
        pseudo-precise numbers like 73% should not appear in reports.

        hid selects which competing hypothesis (ACH) to update: "H1" (default,
        the main hypothesis) or "H2"/"H3" (alternative hypotheses). H1 is
        mirrored to the legacy single-hypothesis slot for backward compat.
        """
        _STATE_ZH_TO_INTERNAL = {
            "有效": "ALIVE", "修正": "MUTATED", "无效": "KILLED", "待定": "UNRESOLVED",
        }
        # agent 输入中文,工具内部规范成英文存储;也保留英文入口方便既有 ledger
        _VALID_INPUT = set(_STATE_ZH_TO_INTERNAL.keys()) | set(_STATE_ZH_TO_INTERNAL.values())
        if state not in _VALID_INPUT:
            raise ValueError(
                f"state must be one of {sorted(_VALID_INPUT)}, got {state!r}")
        internal_state = _STATE_ZH_TO_INTERNAL.get(state, state)
        if isinstance(conf, str):
            label_map = {"高": 100, "中": 66, "低": 33, "未知": 0}
            if conf not in label_map:
                raise ValueError(
                    f"conf must be int 0-100 or one of {list(label_map.keys())}, got {conf!r}. "
                    f"Tip: use 高/中/低/未知 — never use %, floats, or strings like 'high'.")
            conf = label_map[conf]
        elif not (0 <= conf <= 100):
            raise ValueError(
                f"conf must be 0-100, got {conf}. "
                f"Tip: use 高/中/低/未知 instead of numeric values.")
        now = datetime.now().isoformat()
        # ── Multi-hypothesis slot (hypotheses[hid]) ──
        if not hid or not hid.strip():
            raise ValueError("hid must be a non-empty string like 'H1', 'H2', 'H3'")
        hid = hid.strip().upper()  # normalize h1→H1
        hyps = self.state.setdefault("hypotheses", {})
        slot = hyps.get(hid, {"claim": "", "state": "ALIVE", "conf": 50, "history": []})
        slot.setdefault("history", []).append({
            "from_state": slot.get("state", "ALIVE"),
            "to_state": internal_state,
            "conf": conf,
            "evidence_trigger": evidence_trigger,
            "source": source,
            "mutation_reason": mutation_reason,
            "timestamp": now,
        })
        slot["state"] = internal_state
        slot["conf"] = conf
        slot["evidence_trigger"] = evidence_trigger
        slot["source"] = source
        slot["mutation_reason"] = mutation_reason
        hyps[hid] = slot
        # ── Legacy single-hypothesis mirror (H1 only, backward compat) ──
        if hid == "H1":
            prev_state = self.state["hypothesis"]["state"]
            self.state["hypothesis"]["history"].append({
                "from_state": prev_state,
                "to_state": internal_state,
                "conf": conf,
                "evidence_trigger": evidence_trigger,
                "source": source,
                "mutation_reason": mutation_reason,
                "timestamp": now,
            })
            self.state["hypothesis"]["state"] = internal_state
            self.state["hypothesis"]["current_conf"] = conf
            self.state["hypothesis"]["evidence_trigger"] = evidence_trigger
            self.state["hypothesis"]["source"] = source
            self.state["hypothesis"]["mutation_reason"] = mutation_reason
        self._save()
        return self

    def add_claim(self, text: str, label: str,
                  sources: list | None = None, round_n: int | None = None) -> "Ledger":
        """Record a claim with cognitive status label.

        label ∈ {已确认, 已公开, 自推断, 未验证}
        Cognitive labels classify the epistemic status of a claim itself
        (different from source tier which classifies the publisher's
        reputation).

        Examples:
          - 已确认: ≥2 primary-tier sources AND cross-referenced
          - 已公开: primary-tier single source = public announcement
          - 自推断: agent's synthesis from multiple sources
          - 未验证: anecdotal / single weak source / contradictory

        Note: CID is assigned inside _save() under fcntl.flock so concurrent
        calls do not produce duplicate IDs (v8.1.1 fix).
        """
        _VALID_LABELS = {"已确认", "已公开", "自推断", "未验证"}
        if label == "auto":
            label = self.suggest_label(sources or [])
        elif label not in _VALID_LABELS:
            raise ValueError(
                f"label must be one of {sorted(_VALID_LABELS)} or 'auto', got {label!r}")
        # cid: None → _save() assigns under file lock to prevent races
        self.state.setdefault("claims", []).append({
            "id": None,
            "text": text,
            "label": label,
            "sources": sources or [],
            "round_n": round_n,
            "added_at": datetime.now().isoformat(),
        })
        self._save()
        return self

    def suggest_label(self, sources: list | None = None) -> str:
        """Heuristic cognitive-label suggestion based on source tiers.

        Rules:
          - No sources → 未验证 (nothing to base a claim on)
          - All sources primary-tier + ≥2 sources → 已确认
          - Any source primary-tier → 已公开
          - Any source secondary-tier → 自推断 (need synthesis to back claim)
          - Only anecdotal / unknown sources → 未验证
        """
        if not sources:
            return "未验证"
        # Look up tier of each source id (S1, S2, ...)
        missing = [s for s in sources if s not in self.state.get("sources", {})]
        if missing:
            print(f"Warning: sources not in ledger: {missing}. "
                  f"They will be ignored by suggest_label(); defaults to 未验证.",
                  file=sys.stderr)
        tiers = []
        for sid in sources:
            src = self.state.get("sources", {}).get(sid)
            if src and src.get("tier"):
                tiers.append(_normalize_tier(src["tier"]))
        if not tiers:
            return "未验证"  # no usable source info
        if all(t == "一手" for t in tiers) and len(tiers) >= 2:
            return "已确认"
        if "一手" in tiers:
            return "已公开"
        if "二手" in tiers:
            return "自推断"
        return "未验证"

    def claims_dump(self, label_filter: str | None = None) -> str:
        """Return claims formatted for paste-into-report, grouped by label.

        Output structure:
          ## 已确认 (N claims)
          - C1: <text> [S1, S2]
          - C2: <text> [S3]

          ## 已公开 (M claims)
          ...

        If label_filter is set, only that label's claims are shown.
        """
        claims = self.state.get("claims", [])
        if not claims:
            return "(no claims recorded)"
        # Group by label, preserving insertion order
        grouped: dict[str, list] = {}
        label_order = ["已确认", "已公开", "自推断", "未验证"]
        for c in claims:
            grouped.setdefault(c["label"], []).append(c)
        lines = []
        labels_to_show = [label_filter] if label_filter else label_order
        for lbl in labels_to_show:
            if lbl not in grouped:
                continue
            cs = grouped[lbl]
            lines.append(f"## {lbl} ({len(cs)} claim{'s' if len(cs) != 1 else ''})")
            for c in cs:
                src_str = f" [{', '.join(c['sources'])}]" if c['sources'] else ""
                lines.append(f"- **{c['id']}**: {c['text']}{src_str}")
            lines.append("")
        # ── Findings section (Decide phase output) ──
        findings = self.state.get("findings", [])
        if findings:
            lines.append("## Findings (structural conclusions → report sections)")
            for f in findings:
                claim_list = f.get("claims", [])
                claim_str = f" (claims: {', '.join(claim_list)})" if claim_list else ""
                lines.append(f"- **{f['id']}**: {f['text']}{claim_str}")
            lines.append("")
        return "\n".join(lines).rstrip()

    def add_decision(self, decision: str, recommendation: str = "",
                     boundary: str = "") -> "Ledger":
        """Record final decision. decision ∈ {YES, NO, DEFER}."""
        if decision not in ("YES", "NO", "DEFER"):
            raise ValueError(f"decision must be YES/NO/DEFER, got {decision!r}")
        if self.state.get("decisions"):
            prev = self.state["decisions"]["decision"]
            print(f"Warning: overwriting previous decision ({prev}).",
                  file=sys.stderr)
        self.state["decisions"] = {
            "decision": decision,
            "recommendation": recommendation,
            "boundary": boundary,
            "finalized_at": datetime.now().isoformat(),
        }
        self._save()
        return self

    # ── Load / Inspect ─────────────────────────────────────────────────

    def load(self, filepath: str | None = None, topic: str | None = None) -> "Ledger":
        """Load state from file.

        Resolution order:
          1. Explicit filepath wins (for `summary <file>` direct access).
          2. topic: glob storage for files whose name starts with the slug.
             Multiple matches → ValueError; zero matches → FileNotFoundError.
          3. Neither: ALWAYS refuse if any ledgers exist — caller must use
             --topic. This prevents agent laziness and multi-ledger collision.
             Run `list` to see available topic slugs.
        """
        if filepath:
            path = Path(filepath)
        elif topic:
            slug = self._slugify(topic)
            matches = sorted(self.storage_dir.glob(f"{slug}*.json"))
            if len(matches) == 1:
                path = matches[0]
            elif len(matches) > 1:
                raise ValueError(
                    f"Multiple ledgers match topic '{topic}': {[m.name for m in matches]}. "
                    f"Use a more specific topic name.")
            else:
                raise FileNotFoundError(
                    f"No ledger matching topic '{topic}' (slug='{slug}') in {self.storage_dir}. "
                    f"Run: python3 research_tools.py list  to see available topics.")
        else:
            files = sorted(self.storage_dir.glob("*.json"), reverse=True)
            if files:
                topics = [f.stem.rsplit("-2", 1)[0] for f in files]
                raise ValueError(
                    f"{len(files)} ledger(s) in {self.storage_dir}. "
                    f"Always use --topic <slug> to select your ledger. "
                    f"Available: {topics}")
            else:
                raise FileNotFoundError(
                    f"No ledger files in {self.storage_dir}. "
                    f"Run: python3 research_tools.py setup <topic> <hypothesis> <高/中/低/未知>")

        with open(path, "r", encoding="utf-8") as f:
            self.state = json.load(f)
        self._current_filepath = path
        # Minimal schema validation
        if not isinstance(self.state, dict):
            raise ValueError(
                f"Ledger file corrupt: expected JSON object, got {type(self.state).__name__}. "
                f"Backup the file, then re-run setup to start a new ledger.")
        required = {"topic", "hypothesis", "rounds", "sources", "findings"}
        missing = required - set(self.state.keys())
        if missing:
            raise ValueError(
                f"Ledger file corrupt: missing keys {missing}. "
                f"This may be an incompatible version. Backup the file, then re-run setup.")
        if not isinstance(self.state.get("hypothesis"), dict):
            raise ValueError(
                f"Ledger file corrupt: 'hypothesis' is not a dict. "
                f"Backup the file, then re-run setup to start a new ledger.")
        # Backward compat: migrate old single-hypothesis schema → multi-hypothesis
        self._migrate_hypotheses()
        return self

    def _migrate_hypotheses(self) -> None:
        """Ensure the multi-hypothesis slot exists (schema 1.0 → 2.0 compat).

        Old ledgers have only a single 'hypothesis' dict. On load, if
        'hypotheses' is missing or lacks H1, seed it from the legacy slot.
        The migration lives in memory; it persists on the next mutation.
        """
        hyps = self.state.setdefault("hypotheses", {})
        legacy = self.state.get("hypothesis", {})
        if "H1" not in hyps and legacy:
            hyps["H1"] = {
                "claim": legacy.get("claim", ""),
                "state": legacy.get("state", "ALIVE"),
                "conf": legacy.get("current_conf", legacy.get("initial_conf", 50)),
                "history": legacy.get("history", []),
            }
        if self.state.get("schema_version", "1.0") != "2.0":
            self.state["schema_version"] = "2.0"

    def summary(self) -> str:
        """Generate a condensed summary for context recovery (load-bearing)."""
        s = self.state
        lines = [
            f"# Topic: {s['topic']}",
            f"# Hypothesis (H1): {s['hypothesis'].get('claim', '')}",
            f"# State: {s['hypothesis']['state']} @ {_conf_int_to_label(s['hypothesis']['current_conf'])} "
            f"(initial {_conf_int_to_label(s['hypothesis']['initial_conf'])})",
            f"# Rounds: {len(s['rounds'])} | Sources: {len(s['sources'])} | "
            f"Findings: {len(s['findings'])} | Claims: {len(s.get('claims', []))} | "
            f"Hyp mutations: {len(s['hypothesis']['history'])}",
        ]
        if s.get("decisions"):
            lines.append(f"# Decision: {s['decisions']['decision']} — {s['decisions']['recommendation']}")
        lines.append("")
        lines.append("## Sources (top 10):")
        for sid, src in list(s["sources"].items())[:10]:
            title = src.get("title") or src.get("url") or ""
            lines.append(f"  [{sid}] {src['tier']}: {title[:80]}")
        lines.append("")
        lines.append("## Findings:")
        if not s["findings"]:
            lines.append("  (none yet — use finding in Decide phase to group claims into report sections)")
        for f in s["findings"]:
            claim_list = f.get("claims", [])
            claim_str = f" (claims: {', '.join(claim_list)})" if claim_list else ""
            lines.append(f"  - {f['id']}: {f['text'][:70]}{claim_str}")
        if s.get("claims"):
            lines.append("")
            lines.append("## Claims by cognitive label:")
            for label in ("已确认", "已公开", "自推断", "未验证"):
                cs = [c for c in s["claims"] if c["label"] == label]
                if cs:
                    lines.append(f"  [{label}] ({len(cs)})")
                    for c in cs[:5]:
                        lines.append(f"    - {c['id']}: {c['text'][:60]}")
                    if len(cs) > 5:
                        lines.append(f"    ... and {len(cs) - 5} more")
        # ── All hypotheses (ACH multi-hypothesis; never leak conf as %) ──
        hyps = s.get("hypotheses", {})
        if hyps:
            lines.append("")
            lines.append("## Hypotheses:")
            for hid in sorted(hyps):
                h = hyps[hid]
                claim = h.get("claim") or ("(main)" if hid == "H1" else "")
                lines.append(f"  {hid}. {claim} → {h.get('state', '?')} "
                             f"@ {_conf_int_to_label(h.get('conf'))} "
                             f"({len(h.get('history', []))} mutations)")
                for ev in h.get("history", []):
                    lines.append(
                        f"    - {ev.get('from_state', '?')} → {ev.get('to_state', '?')} "
                        f"({_conf_int_to_label(ev.get('conf'))}): "
                        f"{ev.get('evidence_trigger', '')[:60]}"
                    )
        elif s["hypothesis"]["history"]:
            lines.append("")
            lines.append("## Hypothesis evolution:")
            for h in s["hypothesis"]["history"]:
                lines.append(
                    f"  - {h['from_state']} → {h['to_state']} "
                    f"({_conf_int_to_label(h.get('conf'))}): "
                    f"{h['evidence_trigger'][:60]} — {h.get('mutation_reason', '')[:40]}"
                )
        return "\n".join(lines)

    def filepath(self) -> Path | None:
        """Return current ledger file path (for debugging)."""
        return self._current_filepath

    # ── Internal ───────────────────────────────────────────────────────

    def _assign_claim_cids(self, canonical_claims: list) -> int:
        """Assign C# IDs to pending claims with id=None.

        Extracted so both fcntl and Windows paths can call it.
        Returns number of newly assigned CIDs.
        """
        def _next_cid_seq(existing: set) -> int:
            n = 1
            while f"C{n}" in existing:
                n += 1
            return n

        existing_ids = {c["id"] for c in canonical_claims
                        if c.get("id") and isinstance(c["id"], str)}
        pending_claims = self.state.get("claims", [])
        new_assigned = 0
        for c in pending_claims:
            if not c.get("id"):
                cid_n = _next_cid_seq(existing_ids)
                c["id"] = f"C{cid_n}"
                existing_ids.add(c["id"])
                new_assigned += 1
        self.state["claims"] = pending_claims
        return new_assigned

    def _save(self):
        """Persist state atomically with cross-process file lock.

        Concurrency model:
          - Lock file (fcntl.flock) serializes writers — concurrent CLI
            invocations on the same ledger queue instead of clobbering.
          - Under the lock we re-read the canonical file and merge our
            pending mutation into it (compare-and-swap style).
          - Write to a unique tmp file (PID + counter) then atomic rename.

        Without the lock, parallel CLI calls lose updates: thread A loads
        state X, thread B loads state X, both modify and save — last
        writer wins, A's changes are gone. fcntl.flock guarantees
        serialization across processes on POSIX (incl. macOS).
        """
        if not self._current_filepath:
            return
        self.state["updated_at"] = datetime.now().isoformat()
        lock_path = self._current_filepath.with_suffix(".lock")

        def _merge_and_write(merged_state: dict) -> bool:
            """Write merged_state to canonical file. Returns success."""
            global _save_counter
            counter = _save_counter
            _save_counter = counter + 1
            pid = os.getpid() & 0xFFFF
            tmp = self._current_filepath.with_suffix(f".tmp.{pid}.{counter}")
            try:
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(merged_state, f, ensure_ascii=False, indent=2)
                tmp.replace(self._current_filepath)
                return True
            except OSError:
                if tmp.exists():
                    tmp.unlink()
                return False

        def _canonical_or_empty() -> dict:
            """Read canonical file as JSON, or return fresh state template."""
            if self._current_filepath.exists():
                try:
                    return json.loads(self._current_filepath.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    pass
            # Fallback: build a fresh state skeleton matching __init__
            return {
                "schema_version": "2.0",
                "created_at": datetime.now().isoformat(),
                "topic": "",
                "hypothesis": {
                    "claim": "",
                    "state": "ALIVE",
                    "initial_conf": 50,
                    "current_conf": 50,
                    "history": [],
                },
                "hypotheses": {},
                "rounds": [],
                "sources": {},
                "findings": [],
                "claims": [],
                "decisions": None,
                "updated_at": None,
            }

        if not _HAS_FCNTL:
            # Windows fallback: best-effort write without cross-process lock.
            # Concurrent CLI calls on Windows may experience lost updates.
            self._assign_claim_cids(_canonical_or_empty().get("claims", []))
            if not _merge_and_write(self.state):
                raise OSError(f"Failed to write ledger to {self._current_filepath}")
            return
        try:
            with open(lock_path, "w", encoding="utf-8") as lf:
                fcntl.flock(lf.fileno(), fcntl.LOCK_EX)
                # Under the lock: re-read canonical and merge our pending
                # mutation into it (compare-and-swap).
                # NOTE: scalar fields (hypothesis state/conf, decisions) use
                # last-writer-wins merge. This is only safe under the
                # SKILL.md §2 serial-call constraint. List/dict fields
                # (sources, rounds, findings, claims, hypotheses.history)
                # use additive merge so concurrent writes to different
                # fields don't lose data.
                canonical = _canonical_or_empty()
                # Assign C# IDs to newly-added claims under lock
                self._assign_claim_cids(canonical.get("claims", []))
                # Use our state as the authoritative version (it has the
                # new mutation), but merge in fields we don't track — i.e.
                # anything we never modified, keep canonical. This is safe
                # because mutations always touch specific fields (sources,
                # rounds, findings, hypothesis, decisions), not the whole
                # document.
                merged = {**canonical, **self.state,
                          "sources": {**canonical.get("sources", {}),
                                      **self.state.get("sources", {})},
                          "rounds": (canonical.get("rounds", []) +
                                     [r for r in self.state.get("rounds", [])
                                      if r not in canonical.get("rounds", [])]),
                          "findings": (canonical.get("findings", []) +
                                       [f for f in self.state.get("findings", [])
                                        if f not in canonical.get("findings", [])]),
                          "claims": (canonical.get("claims", []) +
                                     [c for c in self.state.get("claims", [])
                                      if c not in canonical.get("claims", [])]),
                          "hypothesis": {
                              **canonical.get("hypothesis", {}),
                              **self.state.get("hypothesis", {}),
                              "history": (canonical.get("hypothesis", {}).get("history", []) +
                                          [h for h in self.state.get("hypothesis", {}).get("history", [])
                                           if h not in canonical.get("hypothesis", {}).get("history", [])]),
                          },
                          "hypotheses": {**canonical.get("hypotheses", {}),
                                         **self.state.get("hypotheses", {})},
                          "decisions": self.state.get("decisions") or canonical.get("decisions")}
                if not _merge_and_write(merged):
                    raise OSError(f"Failed to write ledger to {self._current_filepath}")
        except OSError:
            # If lock acquisition fails, fall back to direct write with
            # unique tmp file. Last writer wins in this rare path.
            if not _merge_and_write(self.state):
                raise OSError(f"Failed to write ledger to {self._current_filepath}")

    @staticmethod
    def _slugify(text: str) -> str:
        """Canonical slug — single source of truth for ledger + report paths.

        Used by both Ledger._slugify (ledger filename) and _suggest_path
        (report path) so --topic matching always works.
        Caps at 50 **visible chars** (CJK counts as 1) to avoid path length issues.
        """
        slug = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", text.lower()).strip("-")
        # Cap at 50 chars — sufficient for any reasonable topic name
        if len(slug) > 50:
            slug = slug[:50].rstrip("-")
        return slug or "research"


# ═══════════════════════════════════════════════════════════════════════════
#  Section B · Inline 元数据注入
# ═══════════════════════════════════════════════════════════════════════════


# Inline citation pattern — single-id only ([Sn]); see inline_metadata() docstring.
_CITATION_RE = re.compile(r'\[S(\d+)\]')
# Inline claim reference [C#] and finding reference [F#] (v8.2 expansion).
_CLAIM_INLINE_RE = re.compile(r'\[C(\d+)\]')
_FINDING_INLINE_RE = re.compile(r'\[F(\d+)\]')

# Column-name heuristics (English + Chinese)
_TITLE_KEYS = ('title', '标题', '名称', 'source', '来源标题')
_TIER_KEYS = ('tier', 'type', 'level', 'credibility', '类型', '可信度', '可信')
_DATE_KEYS = ('date', '日期', '时间', '发布时间', '时新')
_URL_KEYS = ('url', '链接', 'link')

# Date format trimmer — keep only YYYY-MM / YYYY-MM-DD / YYYY-Qx / YYYY.
# Date pattern: longest match first (alternation is left-preferential).
# Order matters: \d{4}-\d{2}-\d{2} must be tried before bare \d{4}, otherwise
# "2026-07-06" would match just "2026".
_DATE_NORMALIZE_RE = re.compile(
    r'(\d{4}-\d{2}-\d{2}|\d{4}-\d{2}|\d{4}-Q[1-4])')


def _short_title(title: str, max_len: int = 28) -> str:
    """Trim title to ~max_len chars at word boundary."""
    title = title.strip()
    if len(title) <= max_len:
        return title
    cut = title[:max_len]
    last_space = cut.rfind(' ')
    if last_space > max_len * 0.6:
        cut = cut[:last_space]
    return cut + '...'


def _normalize_date(date: str) -> str:
    """Extract clean date from various formats."""
    m = _DATE_NORMALIZE_RE.search(date)
    return m.group(0) if m else date.strip()[:10]


def _normalize_tier(tier: str) -> str:
    """Tier vocabulary normalization (Primary/Secondary/Anecdotal → 一手/二手/传闻)."""
    t = tier.strip().lower()
    if t in ('primary', '一手', '官方', 'high', '高', 't1'):
        return '一手'
    if t in ('secondary', '二手', '媒体', 'mid', '中', 't2'):
        return '二手'
    if t in ('anecdotal', 'ugc', '传闻', 'low', '低', 't3'):
        return '传闻'
    return t[:8]


def _find_sources_section(content: str) -> str:
    """Locate Sources Register section by header; return its body only.

    Matches any markdown header containing sources/source/来源/参考 keywords.
    Cuts at the next same-or-higher-level header.
    """
    header_pat = re.compile(
        r'^\s*#{1,6}\s+.*?(sources?|source\s+(?:list|register)|来源|参考).*?\s*$',
        re.IGNORECASE)
    lines = content.split('\n')
    body_start = None
    for i, line in enumerate(lines):
        if header_pat.match(line):
            body_start = i + 1
            break
    if body_start is None:
        return ''
    start_header_level = len(lines[body_start - 1].split()[0])
    for j in range(body_start, len(lines)):
        m = re.match(r'^\s*(#{1,6})\s', lines[j])
        if m and len(m.group(1)) <= start_header_level:
            return '\n'.join(lines[body_start:j])
    return '\n'.join(lines[body_start:])


def _parse_sources_table(content: str) -> dict:
    """Parse markdown table-form Sources Register."""
    sources: dict = {}
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.startswith('|'):
            i += 1
            continue

        # Header row
        header_cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(header_cells) < 2:
            i += 1
            continue

        # Separator row (must be the next line)
        i += 1
        if i >= len(lines):
            break
        sep_line = lines[i].rstrip()
        sep_chars = sep_line.replace('|', '').replace(' ', '')
        if not (sep_line.startswith('|') and set(sep_chars) <= {'-', ':'} and sep_chars):
            i += 1
            continue
        i += 1

        # Map header to column index
        col_title = col_tier = col_date = col_url = -1
        for j, h in enumerate(header_cells):
            hl = h.lower()
            if any(k in hl for k in _TITLE_KEYS):
                col_title = j
            elif any(k in hl for k in _TIER_KEYS):
                col_tier = j
            elif any(k in hl for k in _DATE_KEYS):
                col_date = j
            elif any(k in hl for k in _URL_KEYS):
                col_url = j

        if col_title < 0:
            # Fallback: use the first unclassified column as title
            # (agent may name it 用途/描述/desc/notes etc.)
            assigned = {col_url, col_tier, col_date}
            for j, h in enumerate(header_cells):
                if j not in assigned and j > 0:
                    col_title = j
                    break
            if col_title < 0:
                col_title = 0  # last resort: first column after ID

        # Data rows
        while i < len(lines) and lines[i].rstrip().startswith('|'):
            row_cells = [c.strip() for c in lines[i].rstrip().strip('|').split('|')]
            if not row_cells:
                i += 1
                continue
            m = re.match(r'^S(\d+)\s*$', row_cells[0])
            if not m:
                i += 1
                continue
            sid = f"S{m.group(1)}"
            entry: dict = {}
            if col_title < len(row_cells):
                # Title might be a markdown link — strip [text](url) → text
                title = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', row_cells[col_title])
                entry['title'] = title
            if 0 <= col_tier < len(row_cells):
                entry['tier'] = row_cells[col_tier]
            if 0 <= col_date < len(row_cells):
                entry['date'] = row_cells[col_date]
            if 0 <= col_url < len(row_cells):
                entry['url'] = row_cells[col_url]
            sources[sid] = entry
            i += 1
    return sources


def _parse_sources_list(content: str) -> dict:
    """Parse list-form Sources Register (e.g. `**S1** title (date, tier)`)."""
    section = _find_sources_section(content)
    if not section:
        return {}
    sources: dict = {}
    sid_pat = re.compile(r'\*\*\s*S(\d+)\s*\*\*|^S(\d+)[\.\):\s]')
    date_pat = _DATE_NORMALIZE_RE
    tier_pat = re.compile(
        r'(tier[\s:=]+)?\b(一手|二手|传闻|primary|secondary|anecdotal|high|medium|low)\b',
        re.IGNORECASE)

    for line in section.split('\n'):
        m = sid_pat.search(line)
        if not m:
            continue
        sid_num = m.group(1) or m.group(2)
        sid = f"S{sid_num}"
        if sid in sources:
            continue
        desc = line[m.end():].strip().lstrip(' :-—')
        if not desc:
            continue
        # Common list-form pattern: "title (date, tier)" — split on the
        # outer parentheses first. Fall back to inline search if no parens.
        entry = {'title': desc}
        m_paren = re.match(r'^(.*?)\s*\(([^)]*)\)\s*$', desc)
        if m_paren:
            entry['title'] = m_paren.group(1).strip().rstrip(',')
            paren_content = m_paren.group(2)
            dm = date_pat.search(paren_content)
            if dm:
                entry['date'] = dm.group(0)
            tm = tier_pat.search(paren_content)
            if tm:
                entry['tier'] = tm.group(2)
        else:
            # Fallback: search desc for date first, then tier on the
            # already-modified title to avoid index space confusion.
            dm = date_pat.search(desc)
            if dm:
                entry['date'] = dm.group(0)
                entry['title'] = (desc[:dm.start()] + desc[dm.end():]).strip(' ()-,—')
            # Re-search tier on the (possibly shortened) title, not raw desc
            tm = tier_pat.search(entry['title'])
            if tm:
                entry['tier'] = tm.group(2)
                start = tm.start()
                end = tm.end()
                if start > 0 and entry['title'][start-1:start] in ' :,(':
                    start -= 1
                entry['title'] = (entry['title'][:start] + entry['title'][end:]).strip(' ()-,—')
        sources[sid] = entry
    return sources


def _parse_sources(content: str) -> dict:
    """Parse Sources Register from markdown — table first, list fallback."""
    sources = _parse_sources_table(content)
    return sources if sources else _parse_sources_list(content)


def _expand_citation(match: re.Match, sources: dict) -> str:
    """Replace single [Sn] with [Sn: title | tier, date] if source is known."""
    sid = f"S{match.group(1)}"
    src = sources.get(sid)
    if not src:
        return match.group(0)

    parts = []
    if src.get('tier'):
        parts.append(f"tier={_normalize_tier(src['tier'])}")
    if src.get('date'):
        parts.append(_normalize_date(src['date']))
    if src.get('title'):
        title = _short_title(src['title'])
        return f"[{sid}: {title}" + (f" | {', '.join(parts)}" if parts else "") + "]"
    return f"[{sid}: {', '.join(parts)}]" if parts else f"[{sid}]"


def _expand_claim_inline(match: re.Match, claims: dict) -> str:
    """Replace [C#] with [C#: <label>] (cognitive label only).

    Claim text is already in the report body — re-printing it would bloat
    the inline annotation. Label is the compact epistemic hint readers
    need to interpret the claim.
    """
    cid = f"C{match.group(1)}"
    c = claims.get(cid)
    if not c:
        return match.group(0)
    return f"[{cid}: {c['label']}]"


def _expand_finding_inline(match: re.Match, findings: dict) -> str:
    """Replace [F#] with [F#: C1,C2,...] showing the linked claim IDs.

    Findings are chapter-anchors; the linked claim IDs reveal which claims
    back the section, which is the structural information a reader loses
    once the claims-dump block is gone from the rendered report.
    """
    fid = f"F{match.group(1)}"
    f = findings.get(fid)
    if not f or not f.get("claims"):
        return match.group(0)
    return f"[{fid}: {','.join(f['claims'])}]"


def inline_metadata(filepath: str | Path, write: bool = False,
                    topic: str | None = None) -> int:
    """Inject inline metadata into a markdown report.

    Reads `filepath`, parses the Sources Register (table or list form),
    replaces each single `[Sn]` inline citation with full metadata
    `[Sn: title | tier=..., 2026-05-31]`.

    Also loads the ledger (via `topic` if provided) and expands:
      - `[C#]` → `[C#: <label>]`     — cognitive label only (claim text is already in body)
      - `[F#]` → `[F#: C1,C2,...]`   — linked claim IDs (chapter structure)

    Args:
        filepath: Path to markdown report.
        write:    If True, overwrite the file. If False, print to stdout.
        topic:    Topic slug for ledger lookup (required for [C#]/[F#]
                  expansion when multiple ledgers exist in .cache/).

    Returns:
        Number of inline references replaced (S + C + F combined).

    Idempotent: running twice yields the same result (already-replaced
    references are not double-processed).

    Single-id only: `[Sn]`/`[Cn]`/`[Fn]` are matched; `[S1, S2]`, `[S1-S5]`,
    `[Sn][]` combinations are left unchanged (over-engineering vs. cost trade-off).
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}. "
            f"Use: python3 research_tools.py suggest-path <topic> --mkdir  to get the correct path.")

    content = path.read_text(encoding="utf-8")
    sources = _parse_sources(content)

    # Load ledger for [C#]/[F#] expansion AND as [S#] fallback.
    # If topic is missing/ambiguous we warn and continue — [S#] expansion
    # still works from the markdown's own Sources Register.
    claims: dict = {}
    findings: dict = {}
    try:
        ledger = Ledger().load(topic=topic)
        claims = {c["id"]: c for c in ledger.state.get("claims", []) if c.get("id")}
        findings = {f["id"]: f for f in ledger.state.get("findings", [])}
        # If markdown had no Sources Register, use ledger sources as fallback
        if not sources:
            for sid, sdata in ledger.state.get("sources", {}).items():
                sources[sid] = sdata
    except (FileNotFoundError, ValueError) as e:
        print(f"Warning: ledger not loaded: {e}",
              file=sys.stderr)
        if not sources:
            print("         [S#]/[C#]/[F#] will be left unchanged; "
                  "pass --topic to enable.", file=sys.stderr)

    if not sources:
        print(f"Warning: no Sources Register parsed from {path}", file=sys.stderr)
        print("         inline [Sn] will be left unchanged.", file=sys.stderr)

    # Three independent passes — letter prefixes (S/C/F) don't overlap,
    # so sequential substitution is safe and counts remain accurate.
    content, s_count = _CITATION_RE.subn(
        lambda m: _expand_citation(m, sources), content)
    content, c_count = _CLAIM_INLINE_RE.subn(
        lambda m: _expand_claim_inline(m, claims), content)
    content, f_count = _FINDING_INLINE_RE.subn(
        lambda m: _expand_finding_inline(m, findings), content)
    new_content = content
    replaced_count = s_count + c_count + f_count

    if write:
        path.write_text(new_content, encoding="utf-8")
        print(f"Updated {path} ({len(sources)} sources parsed; "
              f"{s_count} [S#], {c_count} [C#], {f_count} [F#] expanded)",
              file=sys.stderr)
    else:
        sys.stdout.write(new_content)

    return replaced_count


# ═══════════════════════════════════════════════════════════════════════════
#  Section C · CLI 调度 (argparse-based)
# ═══════════════════════════════════════════════════════════════════════════


# SKILL.md §4.2 stop conditions: S4 (workload cap) is mechanical.
_WORKLOAD_MAX = {"L1": 20, "L2": 50, "L3": 80}


def _check_stop(ledger: "Ledger", effort: str = "L2") -> str:
    """Evaluate stop conditions from ledger state (SKILL.md §4.2 S1-S7).

    Only S4 (workload cap) is mechanical — the agent's chosen effort level
    determines the hard cap (L1=20 / L2=50 / L3=80). S1/S2/S3/S5/S6/S7 are
    judgment calls and listed as 'agent review needed'.

    Output: human-readable status block aligned with SKILL.md §4.2.
    """
    if effort not in _WORKLOAD_MAX:
        raise ValueError(f"effort must be one of {list(_WORKLOAD_MAX)}, got {effort!r}")
    rounds = len(ledger.state.get("rounds", []))
    findings = len(ledger.state.get("findings", []))
    claims = len(ledger.state.get("claims", []))
    chosen_cap = _WORKLOAD_MAX[effort]
    at_cap = rounds >= chosen_cap
    lines = [
        f"# Stop Check (effort={effort}, cap={chosen_cap} rounds)",
        f"# Rounds: {rounds} | Findings: {findings} | Claims: {claims}",
        f"#",
        f"# S1 (Must-have 全部满足)            : agent review needed",
        f"# S2 (主要分歧已解决/标为未决)      : agent review needed",
        f"# S3 (颠覆性反证 → 假设无效)        : agent review needed",
        f"# S4 (round 硬上限)                 : see below",
        f"# S5 (连续 2 probe 零增益)          : agent review needed",
        f"# S6 (缺用户偏好/预算/约束 → 问用户): agent review needed",
        f"# S7 (最新状态无法验证)             : agent review needed",
        f"#",
    ]
    for level, max_r in _WORKLOAD_MAX.items():
        marker = "✓" if rounds >= max_r else " "
        marker_now = " ← current" if level == effort else ""
        lines.append(f"#   [{marker}] {level} = {rounds}/{max_r} rounds{marker_now}")
    lines.append(f"#")
    if at_cap:
        lines.append(f"# → {effort} effort 已达硬上限({rounds}/{chosen_cap}),必须进 Decide")
    else:
        lines.append(f"# → 未达 {effort} effort 上限({rounds}/{chosen_cap}),可继续 Dig")
    return "\n".join(lines)


def _suggest_path(topic: str, mkdir: bool = False) -> str:
    """Return canonical output path: research/<slug>-<YYYY-MM>.md.

    Slug rules (kept identical to Ledger._slugify for consistency):
      - lowercase
      - keep ASCII alphanumerics and CJK (\u4e00-\u9fff)
      - collapse other chars to single '-'
      - strip leading/trailing '-'
      - cap at 50 chars
      - if everything stripped, fall back to 'research'

    Args:
        topic: research topic name
        mkdir: if True, also creates the parent 'research/' directory
               (and reports creation status to stderr)
    """
    slug = Ledger._slugify(topic)
    month = datetime.now().strftime("%Y-%m")
    path = f"research/{slug}-{month}.md"
    if mkdir:
        research_dir = Path("research")
        if research_dir.exists():
            print(f"  ℹ  directory exists: {research_dir.absolute()}",
                  file=sys.stderr)
        else:
            research_dir.mkdir(parents=True)
            print(f"  ✓ created directory: {research_dir.absolute()}",
                  file=sys.stderr)
        # Report whether the file already exists
        file_path = Path(path)
        if file_path.exists():
            print(f"  ⚠  file exists: {path} (will overwrite if written)",
                  file=sys.stderr)
        else:
            print(f"  ℹ  file does not exist: {path} (safe to create)",
                  file=sys.stderr)
    return path


def _suggest_label(ledger: "Ledger", sources: list[str]) -> str:
    """CLI wrapper around Ledger.suggest_label()."""
    return ledger.suggest_label(sources)


def _build_parser() -> argparse.ArgumentParser:
    """Build the argparse parser with 14 subcommands."""
    parser = argparse.ArgumentParser(
        prog="research_tools",
        description="deep-research skill utilities: ledger + inline metadata + helpers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    # Common parent (--topic) for any subcommand that loads a ledger.
    # Subcommands NOT needing a ledger (setup / list / suggest-path) omit
    # this parent. With multiple ledgers in .cache/, omitting --topic in
    # those handlers would still trip Ledger.load()'s ValueError — the
    # parent just exposes the flag so the user CAN pass it.
    _common = argparse.ArgumentParser(add_help=False)
    _common.add_argument("--topic", "-t", default=None,
                         help="Topic slug to select ledger when multiple exist in "
                              ".cache/ (run 'list' to see available topics)")

    # ── ledger core (8 subcommands) ──────────────────────────────────────
    p_setup = sub.add_parser("setup", help="Initialize a new ledger for a research topic")
    # Custom type: accept int 0-100 or one of 高/中/低/未知 (label string).
    # Return raw string and let Ledger.setup() decide.
    def _conf_or_label(arg: str):
        return arg  # passthrough

    p_setup.add_argument("topic", help="Research topic name")
    p_setup.add_argument("hypothesis", nargs="?", default="", help="Initial hypothesis claim")
    p_setup.add_argument("initial_conf", nargs="?", default=50, type=_conf_or_label,
                         help="Initial confidence: int 0-100 OR 高/中/低/未知 (default: 50)")

    p_source = sub.add_parser("source", help="Record a source (S#)", parents=[_common])
    p_source.add_argument("sid", help="Source ID (e.g. S1)")
    p_source.add_argument("url", help="Source URL")
    p_source.add_argument("--tier", default="二手",
                          choices=["Primary", "Secondary", "Anecdotal",
                                   "一手", "二手", "传闻"],
                          help="Source tier (中英均可, default: Secondary)")
    p_source.add_argument("--title", default="", help="Source title")
    p_source.add_argument("--date", default="", help="Source date (YYYY-MM-DD)")

    p_round = sub.add_parser("round", help="Record a probe-search round", parents=[_common])
    p_round.add_argument("n", type=int, help="Round number")
    p_round.add_argument("signal_json", help="5-question evidence JSON")
    p_round.add_argument("summary", nargs="?", default="", help="Round summary")

    p_finding = sub.add_parser("finding",
                             help="Record a structural finding (Decide phase; groups claims into a report section)",
                             parents=[_common])
    p_finding.add_argument("text", help="Finding text — becomes a Key Findings section anchor")
    p_finding.add_argument("--claims", default="",
                           help="Comma-separated claim IDs that support this finding (C1,C2,C3)")
    p_finding.add_argument("--sources", default="", help="Additional source IDs not already in claims")
    p_finding.add_argument("--round", type=int, default=None, help="Round number")

    p_hyp = sub.add_parser("hyp", help="Update hypothesis state", parents=[_common])
    p_hyp.add_argument("state", choices=["ALIVE", "MUTATED", "KILLED", "UNRESOLVED",
                                          "有效", "修正", "无效", "待定"],
                        help="Hypothesis state (中文为主:有效/修正/无效/待定)")
    p_hyp.add_argument("conf", help="Confidence: int 0-100 OR 高/中/低/未知")
    p_hyp.add_argument("trigger", help="What triggered this update")
    p_hyp.add_argument("source", nargs="?", default="", help="Source ID")
    p_hyp.add_argument("reason", nargs="?", default="", help="Mutation reason")
    p_hyp.add_argument("--id", dest="hid", default="H1",
                        help="Which hypothesis to update (H1 main, H2/H3 ACH alternatives; default H1)")

    p_decide = sub.add_parser("decide", help="Record final decision", parents=[_common])
    p_decide.add_argument("decision", choices=["YES", "NO", "DEFER"])
    p_decide.add_argument("recommendation", nargs="?", default="", help="Recommendation text")
    p_decide.add_argument("boundary", nargs="?", default="", help="Boundary conditions")

    # ── ledger read (2 subcommands) ──────────────────────────────────────
    p_summary = sub.add_parser("summary", help="Show ledger summary for context recovery",
                               parents=[_common])
    p_summary.add_argument("filepath", nargs="?", default=None, help="Specific ledger file")

    p_list = sub.add_parser("list", help="List all ledgers in research/.cache/")

    p_audit = sub.add_parser("audit",
                             help="Show ledger data counts + data-presence gate (use to verify "
                                  "tool usage before final report)",
                             parents=[_common])

    # ── cognitive labels (3 subcommands, v8.1) ───────────────────────────
    p_claim = sub.add_parser("claim",
                             help="Record a claim with cognitive status label",
                             parents=[_common])
    p_claim.add_argument("text", help="Claim text")
    p_claim.add_argument("label",
                         choices=["已确认", "已公开", "自推断", "未验证", "auto"],
                         help='Cognitive label (or "auto" to suggest from sources)')
    p_claim.add_argument("--sources", default="", help="Comma-separated source IDs (S1,S2)")
    p_claim.add_argument("--round", type=int, default=None, help="Round number")

    p_claims_dump = sub.add_parser("claims-dump",
                                   help="Print all claims grouped by cognitive label",
                                   parents=[_common])
    p_claims_dump.add_argument("--label", default=None,
                              choices=["已确认", "已公开", "自推断", "未验证"],
                              help="Filter to a single label")

    p_suggest_label = sub.add_parser("suggest-label",
                                     help="Heuristic cognitive-label suggestion from source tiers",
                                     parents=[_common])
    p_suggest_label.add_argument("--sources", default="",
                                 help="Comma-separated source IDs to base suggestion on")

    # ── workload + path helpers (2 subcommands) ──────────────────────────
    p_check = sub.add_parser("check-stop", help="Evaluate SKILL.md §4.2 stop conditions (S1-S7)",
                             parents=[_common])
    p_check.add_argument("--effort", default="L2", choices=["L1", "L2", "L3"],
                         help="Current effort level (default L2)")

    p_path = sub.add_parser("suggest-path",
                            help="Generate canonical output path: research/<slug>-<YYYY-MM>.md. "
                                 "With --mkdir, also creates the parent research/ directory.")
    p_path.add_argument("topic", help="Research topic name")
    p_path.add_argument("--mkdir", "-m", action="store_true",
                        help="Create parent research/ directory if missing and report status")

    # ── inline metadata (1 subcommand) ───────────────────────────────────
    p_inline = sub.add_parser("inline", help="Inject inline metadata into markdown report",
                              parents=[_common])
    p_inline.add_argument("file", help="Path to markdown report")
    p_inline.add_argument("--write", "-w", action="store_true",
                          help="Write changes back to file (default: print to stdout)")

    return parser


def _cmd_setup(args):
    # initial_conf: accepts int 0-100 OR one of 高/中/低/未知. argparse
    # default=50 is int; argparse type=_conf_or_label returns string when
    # provided. Try int conversion, else pass label through.
    raw = args.initial_conf
    if isinstance(raw, int):
        conf = raw  # default 50 is int; also covers explicit int
    else:
        try:
            conf = int(raw)
        except (ValueError, TypeError):
            conf = raw  # label string, Ledger.setup() validates
    l = Ledger().setup(args.topic, args.hypothesis, conf)
    print(f"setup ledger: {l.filepath()}")
    slug = Ledger._slugify(args.topic)
    print(f"  → topic slug: '{slug}' — 后续命令可用 --topic '{slug}' "
          f"选定此 ledger（同目录多调研时必需）")


def _cmd_source(args):
    l = Ledger().load(topic=getattr(args, "topic", None))
    l.add_source(args.sid, args.url, args.tier, args.title, args.date)
    print(f"added source {args.sid}: {args.title or args.url[:60]}")


def _cmd_round(args):
    signal_test = json.loads(args.signal_json)
    l = Ledger().load(topic=getattr(args, "topic", None))
    l.add_round(args.n, signal_test, args.summary)
    required = {"新检测", "新深度", "新比较", "新视角", "新维度"}
    yes_count = sum(1 for k in required
                   if str(signal_test.get(k, "")).strip().upper() == "Y")
    print(f"added round #{args.n}: sum={yes_count}/5")


def _cmd_finding(args):
    claim_ids = [c for c in args.claims.split(",") if c] if args.claims else []
    sources = [s for s in args.sources.split(",") if s] if args.sources else []
    l = Ledger().load(topic=getattr(args, "topic", None))
    fid = f"F{len(l.state['findings']) + 1}"
    l.add_finding(args.text, sources, args.round, claim_ids)
    # Display deduped claims from the stored finding (add_finding deduplicates)
    stored = l.state["findings"][-1]
    display_claims = stored.get("claims", [])
    claim_str = f" (claims: {', '.join(display_claims)})" if display_claims else ""
    print(f"added finding {fid}: {args.text[:60]}{claim_str}")


def _cmd_hyp(args):
    conf = args.conf
    try:
        conf_int = int(conf)
        conf = conf_int
    except ValueError:
        pass  # label string, add_hypothesis_update validates
    l = Ledger().load(topic=getattr(args, "topic", None))
    hid = getattr(args, "hid", "H1")
    l.add_hypothesis_update(args.state, conf, args.trigger, args.source, args.reason, hid=hid)
    # Display normalized hid (uppercase)
    display_hid = hid.strip().upper() if hid else "H1"
    # NEVER display confidence as a pseudo-precise % — always the 3-level label
    conf_disp = conf if isinstance(conf, str) else _conf_int_to_label(conf)
    print(f"updated hypothesis {display_hid} → {args.state} @ {conf_disp}")


def _cmd_decide(args):
    l = Ledger().load(topic=getattr(args, "topic", None))
    l.add_decision(args.decision, args.recommendation, args.boundary)
    boundary_str = f" (boundary: {args.boundary})" if args.boundary else ""
    print(f"recorded decision: {args.decision} — {args.recommendation}{boundary_str}")


def _cmd_summary(args):
    l = Ledger()
    l.load(filepath=args.filepath, topic=getattr(args, "topic", None))
    print(l.summary())


def _cmd_list(args):
    l = Ledger()
    files = sorted(l.storage_dir.glob("*.json"), reverse=True)
    if not files:
        print(f"(no ledgers in {l.storage_dir})")
        return
    for f in files:
        print(f.relative_to("."))


def _cmd_claim(args):
    sources = [s for s in args.sources.split(",") if s] if args.sources else []
    l = Ledger().load(topic=getattr(args, "topic", None))
    label = args.label
    if label == "auto":
        label = l.suggest_label(sources)
        print(f"auto-suggested label: {label}", file=sys.stderr)
    n_before = len(l.state.get("claims", []))
    l.add_claim(args.text, label, sources, args.round)
    # CID is now assigned inside _save() under lock; read the last one back
    last = l.state.get("claims", [])[-1] if l.state.get("claims") else {"id": "?"}
    cid = last.get("id") if last.get("id") else f"C{n_before + 1}"
    print(f"added claim {cid} [{label}]: {args.text[:60]}")


def _cmd_claims_dump(args):
    l = Ledger().load(topic=getattr(args, "topic", None))
    print(l.claims_dump(args.label))


def _cmd_suggest_label(args):
    sources = [s for s in args.sources.split(",") if s] if args.sources else []
    l = Ledger().load(topic=getattr(args, "topic", None))
    print(l.suggest_label(sources))


def _cmd_check_stop(args):
    l = Ledger().load(topic=getattr(args, "topic", None))
    print(_check_stop(l, effort=args.effort))


def _cmd_suggest_path(args):
    print(_suggest_path(args.topic, mkdir=args.mkdir))


def _cmd_inline(args):
    inline_metadata(args.file, write=args.write,
                    topic=getattr(args, "topic", None))


def _cmd_audit(args):
    """Print ledger data counts + data-presence gate.

    Verifies the ledger actually has data before writing the final report —
    catches the failure where an agent claims tool usage but only called
    setup(). SKILL.md §7 item 8 requires running this and meeting its
    pass threshold before DELIVER.
    """
    l = Ledger().load(topic=getattr(args, "topic", None))
    s = l.state
    n_sources = len(s.get("sources", {}))
    n_rounds = len(s.get("rounds", []))
    n_findings = len(s.get("findings", []))
    n_claims = len(s.get("claims", []))
    # Total hypothesis mutations across all tracked hypotheses (ACH multi-hyp)
    hyps = s.get("hypotheses", {})
    n_hyp = (sum(len(h.get("history", [])) for h in hyps.values())
             or len(s.get("hypothesis", {}).get("history", [])))
    n_hyp_ids = len(hyps)
    n_decisions = 1 if s.get("decisions") else 0

    print(f"# Topic: {s.get('topic', '(unset)')}")
    print(f"# Sources: {n_sources}  |  Rounds: {n_rounds}  |  Findings: {n_findings}  "
          f"|  Claims: {n_claims}  |  Hyp updates: {n_hyp} ({n_hyp_ids} hypotheses)  "
          f"|  Decisions: {n_decisions}")
    print()

    # Data-presence gate. findings is shown for visibility but NOT gated —
    # claims is the authoritative unit (SKILL.md §6); findings is secondary.
    gated = [
        ("sources",     5, n_sources),
        ("rounds",      3, n_rounds),
        ("claims",      3, n_claims),
        ("hyp_updates", 1, n_hyp),   # only expected when hypothesis module enabled (SKILL.md §5)
    ]
    n_gated = len(gated)
    n_pass = sum(1 for _, t, a in gated if a >= t)
    # Allow one contextual miss (e.g. a scan/benchmark lens legitimately has
    # no hypothesis tracking), so the threshold is n_gated - 1.
    required = max(n_gated - 1, 1)
    print(f"# {n_gated}-item data-presence gate ({n_pass}/{n_gated} pass; "
          f"≥ {required} required):")
    for label, threshold, actual in gated:
        ok = "✓" if actual >= threshold else "✗"
        print(f"  {ok}  {label:14s}  {actual:3d}  (≥ {threshold})")
    verdict = "PASS" if n_pass >= required else "FAIL"
    note = "" if n_pass >= required else "  → §7 item 8 failed: backfill ledger / DELAY / declare degraded (SKILL.md §7)"
    print(f"# Verdict: {verdict}{note}")
    # ── Finding support check (advisory, not gated) ──
    findings = s.get("findings", [])
    if findings:
        weak = [f["id"] for f in findings if len(f.get("claims", [])) < 2]
        if weak:
            print(f"# ⚠ {', '.join(weak)}: finding(s) with < 2 supporting claims — "
                  f"consider linking more claims before finalizing")


_CMD_DISPATCH = {
    "setup": _cmd_setup,
    "source": _cmd_source,
    "round": _cmd_round,
    "finding": _cmd_finding,
    "hyp": _cmd_hyp,
    "decide": _cmd_decide,
    "summary": _cmd_summary,
    "list": _cmd_list,
    "claim": _cmd_claim,
    "claims-dump": _cmd_claims_dump,
    "suggest-label": _cmd_suggest_label,
    "check-stop": _cmd_check_stop,
    "suggest-path": _cmd_suggest_path,
    "inline": _cmd_inline,
    "audit": _cmd_audit,
}


def main(argv=None):
    """CLI dispatcher. Routes subcommand to Ledger or inline_metadata.

    All expected errors (ValueError, FileNotFoundError, JSON errors) are
    caught and shown as clean one-line stderr messages — never raw tracebacks.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        sys.exit(0)
    handler = _CMD_DISPATCH.get(args.command)
    if not handler:
        parser.print_help()
        sys.exit(1)
    try:
        handler(args)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        # MUST come before ValueError — JSONDecodeError is a ValueError subclass
        print(f"Error: invalid JSON in argument or file: {e}. "
              f"Check quotes/brackets. Common cause: missing quotes around JSON, "
              f"or trailing comma.",
              file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
