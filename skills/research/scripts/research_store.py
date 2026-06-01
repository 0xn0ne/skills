#!/usr/bin/env python3
"""
Research storage and verification.

This script keeps the human-readable markdown file, but adds a structured ledger
beside it. The ledger is the single source of truth for sources, claims, Trust
Badge, ratios, and report status.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import UTC, date, datetime
from urllib.parse import urlparse
from typing import Dict, Optional

SECTIONS_ORDER = [
    "Executive Summary",
    "Research Background & Objectives",
    "Methodology & Sources",
    "Key Findings & Analysis",
    "Deep Insights & Attribution",
    "Conclusions & Recommendations",
    "Risk Assessment",
    "Implementation Roadmap",
    "Gaps, Limitations & Assumptions",
    "Appendix: Trust Badge",
    "Appendix: Evidence Ledger",
    "Appendix: Sources",
    "Appendix: Verification Gates",
    "Appendix: Phase Check Log",
]

SECTION_MAP = {
    "executive-summary": "Executive Summary",
    "background-objectives": "Research Background & Objectives",
    "methodology": "Methodology & Sources",
    "key-findings": "Key Findings & Analysis",
    "deep-insights": "Deep Insights & Attribution",
    "recommendations": "Conclusions & Recommendations",
    "risk-assessment": "Risk Assessment",
    "implementation-roadmap": "Implementation Roadmap",
    "gaps-limitations": "Gaps, Limitations & Assumptions",
    "gaps": "Gaps, Limitations & Assumptions",
    "limitations": "Gaps, Limitations & Assumptions",
    "assumption-ledger": "Gaps, Limitations & Assumptions",
    "sources": "Appendix: Sources",
    "phase-log": "Appendix: Phase Check Log",
    "constraint-log": "Appendix: Phase Check Log",
    # Legacy mappings (backward compatibility)
    "intent-frame": "Research Background & Objectives",
    "research-question": "Research Background & Objectives",
    "research-plan": "Methodology & Sources",
    "technical-reasoning": "Deep Insights & Attribution",
    "search-log": "Appendix: Phase Check Log",
    "evidence-ledger": "Appendix: Evidence Ledger",
    "evidence-matrix": "Appendix: Evidence Ledger",
    "contradictions": "Key Findings & Analysis",
    "dimension-discovery": "Key Findings & Analysis",
    "commercial-discovery": "Deep Insights & Attribution",
    "synthesis": "Deep Insights & Attribution",
    "red-team": "Risk Assessment",
    "hypothesis-evolution": "Deep Insights & Attribution",
    "recommendations-narrative": "Conclusions & Recommendations",
}

T1T2_TYPES = {"T1_Academic", "T1_Official", "T2_Creator", "T2_Data"}
VALID_SOURCE_TYPES = T1T2_TYPES | {"T3_Synthesis", "T4_Community", "T5_Recap"}
VALID_ACCESS = {"reachable", "uniquely_identifiable", "timed_out", "unreachable", "unverified"}
VALID_TRACE = {"original", "traced", "as_cited_not_verified", "unverified"}
VALID_GRADES = {"A", "B", "C", "D", "F"}
VALID_CONFIDENCE = {"High", "Medium", "Low"}
VALID_VERIFICATION = {"verified_directly", "traced_back", "unverified", "gap", "disputed_data"}
VALID_HYPOTHESIS_STATUS = {"testing", "confirmed", "falsified", "mutated"}
VALID_PUBLISHER_TYPES = {"official", "company", "individual", "media", "community", "academic", "unknown"}
NUMERIC_RE = re.compile(r"(\d|%|\$|￥|¥|\bUSD\b|\bRMB\b|万|亿|CAGR|ROI|CAC|LTV|percent|percentage)", re.IGNORECASE)
NARRATIVE_SECTIONS = {
    "executive-summary": "Executive Summary",
    "background-objectives": "Research Background & Objectives",
    "methodology": "Methodology & Sources",
    "key-findings": "Key Findings & Analysis",
    "deep-insights": "Deep Insights & Attribution",
    "recommendations": "Conclusions & Recommendations",
    "risk-assessment": "Risk Assessment",
    "implementation-roadmap": "Implementation Roadmap",
    "gaps-limitations": "Gaps, Limitations & Assumptions",
    "phase-log": "Appendix: Phase Check Log",
}

REQUIRED_NARRATIVE_SECTIONS = ["executive-summary", "key-findings", "recommendations", "gaps-limitations"]
REQUIRED_IF_RECOMMENDATIONS = ["recommendations"]
REQUIRED_DECISION_GRADE_SECTIONS = ["background-objectives", "methodology", "deep-insights", "risk-assessment", "implementation-roadmap"]
REQUIRED_COMMERCIAL_SECTIONS = ["deep-insights"]
THESIS_KEYWORDS = [
    "thesis",
    "conclusion",
    "decision",
    "recommend",
    "should",
    "bottom.line",
    "current position",
    "立场",
    "结论",
    "建议",
    "决策",
    "应该",
]
EDGE_CASE_KEYWORDS = [
    "edge case",
    "failure mode",
    "risk",
    "if not",
    "alternative scenario",
    "corner case",
    "edge cases",
    "failure modes",
    "risks",
    "风险",
    "边缘情况",
    "失败模式",
    "如果不是",
    "极端情况",
]

COMMERCIAL_SCOPE_KEYWORDS = {
    "commercial",
    "market",
    "product",
    "business",
    "competitor",
    "customer",
    "revenue",
    "sales",
    "marketing",
    "growth",
    "adoption",
    "penetration",
}
STRATEGIC_SCOPE_KEYWORDS = {
    "decision",
    "strategic",
    "invest",
    "build",
    "buy",
    "adopt",
    "procurement",
    "operations",
    "architecture",
    "technology selection",
}

STRONG_SOURCE_TYPES = {"T1_Academic", "T1_Official", "T2_Data"}

CJK_PATTERN = re.compile(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\u3400-\u4dbf]")
THESIS_PATTERN = re.compile(
    r"\b(thesis|conclusion|decision|recommend|should|bottom.line|current position)\b|(立场|结论|建议|决策|应该)",
    re.IGNORECASE,
)
EDGE_CASE_PATTERN = re.compile(
    r"(edge cases?|failure modes?|risks?|if not|alternative scenario|corner case|边缘情况|失败模式|风险|如果不是|极端情况)",
    re.IGNORECASE,
)

VALID_SEARCH_DIRECTIONS = {"confirm", "explore", "refute", "neutral"}
VALID_PERSPECTIVES = {"supportive", "neutral", "critical", "alternative"}
VALID_EFFECTS = {"strengthened", "weakened", "changed", "no_material_change"}
VALID_SUBQUESTION_STATUS = {"answered", "partial", "gap_identified", "unanswered"}
VALID_SUBQUESTION_PRIORITY = {"high", "medium", "low"}
VALID_SUBQUESTION_LOOP_ACTION = {"continue_research", "continue_synthesis", "ask_user", "none"}
VALID_MODULE_STATUS = {"complete", "partial", "gap"}
VALID_MODULE_LANGUAGE = {"en", "zh", "mixed", None}
VALID_PROMPT_ITEM_STATUS = {"mapped", "gap_identified", "unmapped"}
VALID_PROMPT_ITEM_PRIORITY = {"high", "medium", "low"}

BACKGROUND_KEYWORDS = {"background", "unused", "context", "historical", "note-only"}

RUNTIME_TOPIC_KEYWORDS = {
    "prompt",
    "prompting",
    "prompt-engineering",
    "system-prompt",
    "user-prompt",
    "inference",
    "runtime",
    "推理",
    "prompt设计",
    "prompt优化",
    "prompt技巧",
    "chatbot",
    "conversation",
    "指令",
    "instruct",
    "instruction-following",
}
TRAINING_STAGE_KEYWORDS = {
    "training",
    "alignment",
    "rlhf",
    "fine-tuning",
    "fine-tune",
    "训练",
    "微调",
    "preference-learning",
    "reinforcement-learning",
}
TRAINING_ACTION_KEYWORDS = {
    "训练层面",
    "微调",
    "fine-tun",
    "alignment构建",
    "rlhf",
    "train model",
    "model developer",
    "model training",
    "preference data",
    "reward model",
    "模型开发",
    "模型训练",
    "构建alignment",
}
ACTOR_SCOPE_KEYWORDS = {
    "prompt_engineer": {"prompt", "prompting", "prompt-engineering", "system-prompt", "指令设计", "prompt设计"},
    "model_developer": {"training", "alignment", "rlhf", "fine-tun", "训练", "微调", "模型开发", "model developer"},
    "user": {"use", "using", "apply", "如何", "怎么", "使用"},
    "provider": {"deploy", "serve", "api", "inference", "部署", "服务"},
}
SOURCE_DOMINANCE_THRESHOLD = 0.6
MIN_CLAIMS_FOR_SOURCE_DOMINANCE = 4

_RUNTIME_KW_PATTERN = r"(?:" + "|".join(RUNTIME_TOPIC_KEYWORDS) + ")"
_TRAINING_KW_PATTERN = r"(?:" + "|".join(TRAINING_STAGE_KEYWORDS) + ")"
RUNTIME_TOPIC_PATTERN = re.compile(_RUNTIME_KW_PATTERN, re.IGNORECASE)
TRAINING_STAGE_PATTERN = re.compile(_TRAINING_KW_PATTERN, re.IGNORECASE)

SCOPE_KEYWORDS_STRATEGIC = {
    "decision",
    "commercial",
    "strategic",
    "invest",
    "build",
    "buy",
    "adopt",
    "market",
    "product",
    "procurement",
    "operations",
}

STRATEGIC_KEYWORDS = SCOPE_KEYWORDS_STRATEGIC
TASK_TYPE_KEYWORDS = {
    "market_analysis": {"market", "市场规模", "市场份额", "market size", "market share", "行业分析", "industry analysis", "tam", "sam", "som"},
    "competitive_intel": {"competitor", "竞争", "竞品", "competitive", "benchmark", "对标", "versus", "vs", "对比分析"},
    "supply_chain": {"supply chain", "供应链", "supplier", "供应商", "procurement", "采购", "vendor", "制造商"},
    "policy_analysis": {"policy", "政策", "regulation", "监管", "compliance", "合规", "法律", "law", "法规"},
    "investment_feasibility": {"invest", "投资", "roi", "irr", "npv", "feasibility", "可行性", "估值", "valuation", "dd", "due diligence"},
    "technology_evaluation": {"technology", "技术", "stack", "architecture", "framework", "platform", "evaluate", "评估", "选型"},
    "strategic_planning": {"strategy", "战略", "strategic", "roadmap", "路线图", "plan", "规划", "go-to-market", "gtm"},
}

TASK_TYPE_FRAMEWORKS = {
    "market_analysis": {"dimensions": ["market_size", "growth_drivers", "competitive_landscape", "customer_segments", "regulatory_environment"], "min_sources": 8},
    "competitive_intel": {"dimensions": ["feature_comparison", "pricing", "market_positioning", "strengths_weaknesses", "strategic_direction"], "min_sources": 6},
    "supply_chain": {"dimensions": ["supplier_landscape", "cost_structure", "risk_concentration", "alternative_sources", "logistics"], "min_sources": 6},
    "policy_analysis": {"dimensions": ["current_regulations", "enforcement_trend", "stakeholder_positions", "compliance_requirements", "timeline"], "min_sources": 5},
    "investment_feasibility": {"dimensions": ["market_opportunity", "financial_model", "team_capability", "competitive_moat", "exit_scenarios", "risk_factors"], "min_sources": 8},
    "technology_evaluation": {"dimensions": ["capability", "maturity", "ecosystem", "performance", "cost", "migration_path"], "min_sources": 6},
    "strategic_planning": {"dimensions": ["current_state", "market_dynamics", "capabilities", "options", "resource_requirements", "timeline"], "min_sources": 6},
}

# Chinese keyword equivalents for dimension names — used by task_type_framework gate
# so Chinese-language narratives pass without requiring English dimension keywords.
# Keywords are ordered from most specific (exact phrase) to most general (single word).
# The gate uses substring matching: "客户" matches "人形机器人客户" because "客户" is a substring.
DIMENSION_ZH_KEYWORDS: Dict[str, list] = {
    "market_size": ["市场规模", "市场容量", "market size", "市场", "规模", "容量", "万亿", "亿"],
    "growth_drivers": ["增长驱动", "增长因素", "驱动因素", "增长", "驱动", "动力", "growth"],
    "competitive_landscape": ["竞争格局", "竞争环境", "竞争态势", "竞争", "格局", "态势"],
    "customer_segments": ["客户群体", "用户群体", "目标客户", "用户画像", "客户", "用户", "目标市场", "消费群体", "客群", "buyer", "customer", "segment"],
    "regulatory_environment": ["监管环境", "政策环境", "法规环境", "监管政策", "监管", "政策", "法规", "合规", "法律", "regulatory", "regulation", "policy"],
    "feature_comparison": ["功能对比", "特性对比", "功能比较", "功能", "特性", "feature", "comparison"],
    "pricing": ["定价", "价格", "收费", "费用", "price", "pricing"],
    "market_positioning": ["市场定位", "产品定位", "定位", "positioning"],
    "strengths_weaknesses": ["优势", "劣势", "优劣势", "strengths", "weaknesses"],
    "strategic_direction": ["战略方向", "战略规划", "战略", "strategy"],
    "supplier_landscape": ["供应商格局", "供应商", "供应链", "supplier", "vendor"],
    "cost_structure": ["成本结构", "成本构成", "成本", "cost"],
    "risk_concentration": ["风险集中", "集中度", "风险", "集中"],
    "alternative_sources": ["替代来源", "替代方案", "替代", "来源", "alternative"],
    "logistics": ["物流", "运输", "配送", "logistics", "delivery"],
    "current_regulations": ["现行法规", "监管政策", "法律法规", "法规", "监管", "政策"],
    "enforcement_trend": ["执法趋势", "执行趋势", "执法", "执行"],
    "stakeholder_positions": ["利益相关方", "stakeholder", "各方立场", "相关方", "立场"],
    "compliance_requirements": ["合规要求", "合规", "要求", "compliance"],
    "timeline": ["时间线", "时间表", "路线图", "时间", "路线", "规划", "timeline"],
    "market_opportunity": ["市场机会", "市场机遇", "机会", "机遇", "潜力", "opportunity"],
    "financial_model": ["财务模型", "财务分析", "财务", "营收", "利润", "收入", "盈利", "销售额", "revenue", "profit", "income", "financial"],
    "team_capability": ["团队能力", "团队", "能力", "team"],
    "competitive_moat": ["竞争壁垒", "护城河", "壁垒", "门槛", "竞争优势", "moat", "barrier", "advantage"],
    "exit_scenarios": ["退出场景", "退出策略", "退出", "exit"],
    "risk_factors": ["风险因素", "风险", "因素", "risk"],
    "capability": ["能力", "功能", "capabilities", "capable", "able", "feature", "function", "产能", "ton", "吨", "capacity", "titer", "密度", "density", "yield"],
    "maturity": ["成熟度", "成熟", "mature", "production-ready", "stable", "established"],
    "ecosystem": ["生态", "生态系统", "ecosystems", "社区", "工具", "community", "tooling"],
    "performance": ["性能", "表现", "performant", "latency", "throughput", "speed", "成本", "cost", "efficiency", "效率", "viability", "活率"],
    "cost": ["成本", "价格", "费用", "costs", "pricing", "expense", "investment", "overhead"],
    "migration_path": ["迁移路径", "迁移", "migration", "商业化路径", "commercialization", "路径", "阶段", "phase", "deployment", "scaling"],
    "current_state": ["现状", "当前状态", "现状"],
    "market_dynamics": ["市场动态", "市场趋势", "动态", "趋势"],
    "capabilities": ["能力", "功能", "capability"],
    "options": ["选项", "选择", "方案", "option"],
    "resource_requirements": ["资源需求", "资源", "需求"],
}

T4_TRIANGULATION_MIN_SOURCES = 3

MULTI_QUESTION_PATTERN = re.compile(r"[?？]")
MULTI_QUESTION_KEYWORDS = {
    "compare",
    "should",
    "whether",
    "adopt",
    "procurement",
    "strategy",
    "是否",
    "要不要",
    "如何",
    "比较",
    "评估",
    "或者说",
}

SUPPLIER_ONLY_TYPES = {"T2_Creator", "T3_Synthesis", "T4_Community", "T5_Recap"}
STRONG_COMMERCIAL_SOURCE_TYPES = {"T1_Academic", "T1_Official", "T2_Data"}
WEAK_CLAIM_GRADES = {"D", "F"}
CD_DOMINANCE_THRESHOLD = 0.6
MIN_AB_CLAIMS_FOR_DECISION = 1
MIN_CLAIMS_FOR_CD_DOMINANCE = 4


def _find_project_root(start: Optional[str] = None) -> str:
    current = start or os.getcwd()
    while current != "/":
        markers = [".git", "pyproject.toml", "package.json", "Cargo.toml", "go.mod"]
        if any(os.path.exists(os.path.join(current, m)) for m in markers):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return os.getcwd()


def _storage_dir() -> str:
    # Priority 1: explicit workspace override (via --workspace flag)
    ws = os.environ.get("RESEARCH_WORKSPACE", "").strip()
    if ws:
        dr_dir = os.path.join(ws, ".research")
        os.makedirs(dr_dir, exist_ok=True)
        return dr_dir
    # Priority 2: walk up from CWD looking for project markers
    root = _find_project_root()
    dr_dir = os.path.join(root, ".research")
    os.makedirs(dr_dir, exist_ok=True)
    return dr_dir


def _slug(topic: str) -> str:
    return topic.lower().replace(" ", "-").replace("/", "-")


def _base_slug(topic: str) -> str:
    """Strip trailing date pattern (YYYYMMDD) from slug before appending today's date."""
    import re
    s = _slug(topic)
    return re.sub(r'-\d{8}$', '', s)


def _topic_filepath(topic: str) -> str:
    today = date.today().strftime("%Y%m%d")
    return os.path.join(_storage_dir(), f"{_base_slug(topic)}-{today}.temp.md")


def _final_report_filepath(topic: str) -> str:
    today = date.today().strftime("%Y%m%d")
    return os.path.join(_storage_dir(), f"{_base_slug(topic)}-{today}.final.md")


def _advisory_report_filepath(topic: str) -> str:
    today = date.today().strftime("%Y%m%d")
    return os.path.join(_storage_dir(), f"{_base_slug(topic)}-{today}.advisory.md")


def _ledger_filepath(topic: str) -> str:
    today = date.today().strftime("%Y%m%d")
    return os.path.join(_storage_dir(), f"{_base_slug(topic)}-{today}.ledger.json")


def _section_heading(section_key: str) -> str:
    return SECTION_MAP.get(section_key, section_key)


def _now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _empty_ledger(topic: str, scope: str = "", created_cwd: str = "") -> dict:
    return {
        "ledger_version": "3.5",
        "topic": topic,
        "scope": scope,
        "created_at": _now(),
        "updated_at": _now(),
        "sources": {},
        "claims": {},
        "hypotheses": {},
        "task_type": "",
        "recommendations": {},
        "closure_searches": {},
        "red_team_arguments": [],
        "subquestions": {},
        "modules": {},
        "prompt_items": {},
        "verification": {
            "status": "NOT_RUN",
            "report_status": "Draft — ledger unverified",
            "use_without_rereading_confidence": "Low",
            "gates": {},
            "failure_status": None,
            "failure_reason": None,
            "failure_stage": None,
        },
        "report_config": {
            "narrative_sections": {},
            "last_generated_at": None,
            "generation_hash": None,
            "generated_report_path": None,
            "created_cwd": created_cwd,
            "storage_dir": _storage_dir(),
        },
    }


def _load_ledger(topic: str) -> dict:
    path = _ledger_filepath(topic)
    if not os.path.exists(path):
        print(f"Error: ledger not found: {path}. Run init first.", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        ledger = json.load(f)
    if "report_config" not in ledger:
        ledger["report_config"] = {
            "narrative_sections": {},
            "last_generated_at": None,
            "generation_hash": None,
            "generated_report_path": None,
        }
    if "closure_searches" not in ledger:
        ledger["closure_searches"] = {}
    if "red_team_arguments" not in ledger:
        ledger["red_team_arguments"] = []
    if "subquestions" not in ledger:
        ledger["subquestions"] = {}
    if "modules" not in ledger:
        ledger["modules"] = {}
    if "prompt_items" not in ledger:
        ledger["prompt_items"] = {}
    if "hypotheses" not in ledger:
        ledger["hypotheses"] = {}
    if "task_type" not in ledger:
        ledger["task_type"] = ""
    ver = ledger.get("ledger_version")
    if ver not in ("3.0", "3.1", "3.2", "3.3", "3.4", "3.5"):
        ledger["ledger_version"] = "3.5"
    if "failure_status" not in ledger.get("verification", {}):
        ledger.setdefault("verification", {})["failure_status"] = None
    if "failure_reason" not in ledger.get("verification", {}):
        ledger.setdefault("verification", {})["failure_reason"] = None
    if "failure_stage" not in ledger.get("verification", {}):
        ledger.setdefault("verification", {})["failure_stage"] = None
    if "created_cwd" not in ledger.get("report_config", {}):
        ledger["report_config"]["created_cwd"] = None
    if "storage_dir" not in ledger.get("report_config", {}):
        ledger["report_config"]["storage_dir"] = _storage_dir()
    return ledger


def _save_ledger(topic: str, ledger: dict) -> None:
    ledger["updated_at"] = _now()
    with open(_ledger_filepath(topic), "w", encoding="utf-8") as f:
        json.dump(ledger, f, ensure_ascii=False, indent=2, sort_keys=True)


def _ledger_hash(ledger: dict) -> str:
    sanitized = json.loads(json.dumps(ledger, ensure_ascii=False, sort_keys=True))
    report_config = sanitized.setdefault("report_config", {})
    report_config["last_generated_at"] = None
    report_config["generation_hash"] = None
    report_config["generated_report_path"] = None
    sanitized["updated_at"] = None
    # Normalize verification fields added by _load_ledger but not persisted
    verification = sanitized.setdefault("verification", {})
    verification["failure_status"] = None
    verification["failure_reason"] = None
    verification["failure_stage"] = None
    payload = json.dumps(sanitized, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


_TEMPLATE = """# Research: {topic}
Date: {date} | Scope: {scope} | Status: **WORKING TEMPLATE — NOT FINAL REPORT**

## Executive Summary
_(To be filled — write LAST, after all other sections)_

## Research Background & Objectives
_(To be filled)_

## Methodology & Sources
_(To be filled)_

## Key Findings & Analysis
_(To be filled — organized by dimension, not by search round)_

## Deep Insights & Attribution
_(To be filled — Why + What next, hypothesis evolution)_

## Conclusions & Recommendations
_(To be filled — SMART, prioritized, short/mid/long term)_

## Risk Assessment
_(To be filled — probability × impact matrix, red team arguments)_

## Implementation Roadmap
_(To be filled — phased with milestones, MVP)_

## Gaps, Limitations & Assumptions
_(To be filled)_

## Appendix
_Generated from ledger when possible: Trust Badge, Evidence Ledger, Sources, Verification Gates, Phase Check Log._
"""


def _split_csv(value: str) -> list[str]:
    if not value:
        return []
    return [x.strip() for x in value.split(",") if x.strip()]


def _parsed_url(url: str):
    if not url:
        return urlparse("")
    return urlparse(url if re.match(r"^https?://", url) else "https://" + url)


def _domain(url: str) -> str:
    parsed = _parsed_url(url)
    return (parsed.netloc or "").lower().removeprefix("www.")


def _path(url: str) -> str:
    return (_parsed_url(url).path or "/").rstrip("/") or "/"


def _domain_matches(domain: str, official_domain: str) -> bool:
    if not domain or not official_domain:
        return False
    official = official_domain.lower().removeprefix("www.")
    return domain == official or domain.endswith("." + official)


def _official_source_valid(src: dict) -> bool:
    if src.get("publisher_type") != "official":
        return False
    official = (src.get("official_domain") or "").lower().removeprefix("www.")
    if not official:
        return False
    url = src.get("url") or src.get("citation") or ""
    domain = src.get("url_domain") or _domain(url)
    if "/" not in official:
        return _domain_matches(domain, official)
    official_domain, official_path = official.split("/", 1)
    official_path = "/" + official_path.strip("/")
    return _domain_matches(domain, official_domain) and _path(url).lower().startswith(official_path)


def cmd_init(args):
    filepath = _topic_filepath(args.topic)
    ledger_path = _ledger_filepath(args.topic)
    if (os.path.exists(filepath) or os.path.exists(ledger_path)) and not args.force:
        print(f"Research artifacts already exist: {filepath} / {ledger_path}")
        print("Use --force to overwrite, or add-source/add-claim/append to add content.")
        return

    task_type = args.task_type or _detect_task_type(args.topic, args.scope or "")
    ledger = _empty_ledger(args.topic, args.scope or "", os.getcwd())
    ledger["task_type"] = task_type
    content = _TEMPLATE.format(topic=args.topic, date=date.today().isoformat(), scope=args.scope or "(not specified)")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    _save_ledger(args.topic, ledger)
    print(f"Created: {filepath}")
    print(f"Ledger:  {ledger_path}")


def cmd_add_source(args):
    if args.type not in VALID_SOURCE_TYPES:
        print(f"Error: invalid source type {args.type}", file=sys.stderr)
        sys.exit(1)
    if args.access_status not in VALID_ACCESS:
        print(f"Error: invalid access status {args.access_status}", file=sys.stderr)
        sys.exit(1)
    if args.trace_status not in VALID_TRACE:
        print(f"Error: invalid trace status {args.trace_status}", file=sys.stderr)
        sys.exit(1)
    if args.publisher_type not in VALID_PUBLISHER_TYPES:
        print(f"Error: invalid publisher type {args.publisher_type}", file=sys.stderr)
        sys.exit(1)
    ledger = _load_ledger(args.topic)
    ledger["sources"][args.id] = {
        "id": args.id,
        "type": args.type,
        "title": args.title,
        "url": args.url or "",
        "citation": args.citation or "",
        "language": args.language,
        "publisher": args.publisher or "",
        "publisher_type": args.publisher_type,
        "official_domain": args.official_domain or "",
        "url_domain": _domain(args.url or args.citation or ""),
        "access_status": args.access_status,
        "trace_status": args.trace_status,
        "access_date": args.access_date or date.today().isoformat(),
        "used_for": _split_csv(args.used_for),
        "notes": args.notes or "",
    }
    _save_ledger(args.topic, ledger)
    print(f"Added source {args.id}")


def cmd_add_claim(args):
    if args.grade not in VALID_GRADES:
        print(f"Error: invalid grade {args.grade}", file=sys.stderr)
        sys.exit(1)
    if args.confidence not in VALID_CONFIDENCE:
        print(f"Error: invalid confidence {args.confidence}", file=sys.stderr)
        sys.exit(1)
    if args.verification_status not in VALID_VERIFICATION:
        print(f"Error: invalid verification status {args.verification_status}", file=sys.stderr)
        sys.exit(1)
    ledger = _load_ledger(args.topic)
    numeric = (
        args.numeric
        or args.numeric_mode == "true"
        or (args.numeric_mode == "auto" and NUMERIC_RE.search(args.claim) is not None)
    )
    ledger["claims"][args.id] = {
        "id": args.id,
        "claim": args.claim,
        "grade": args.grade,
        "confidence": args.confidence,
        "primary_sources": _split_csv(args.primary_sources),
        "corroboration_sources": _split_csv(args.corroboration_sources),
        "contradiction_checked": args.contradiction_checked.lower() == "true",
        "verification_status": args.verification_status,
        "used_in": _split_csv(args.used_in),
        "numeric": bool(numeric),
        "notes": args.notes or "",
    }
    _save_ledger(args.topic, ledger)
    print(f"Added claim {args.id}")


def cmd_add_recommendation(args):
    ledger = _load_ledger(args.topic)
    ledger["recommendations"][args.id] = {
        "id": args.id,
        "text": args.text,
        "claim_ids": _split_csv(args.claim_ids),
        "type": args.type,
        "notes": args.notes or "",
    }
    _save_ledger(args.topic, ledger)
    print(f"Added recommendation {args.id}")


def cmd_add_hypothesis(args):
    if args.status not in VALID_HYPOTHESIS_STATUS:
        print(f"Error: invalid hypothesis status {args.status}", file=sys.stderr)
        sys.exit(1)
    ledger = _load_ledger(args.topic)
    ledger["hypotheses"][args.id] = {
        "id": args.id,
        "initial_state": args.initial_state,
        "current_state": args.current_state or args.initial_state,
        "mutation_trigger": args.mutation_trigger or "",
        "trigger_claim_ids": _split_csv(args.trigger_claim_ids),
        "status": args.status,
        "confidence": args.confidence,
        "notes": args.notes or "",
    }
    _save_ledger(args.topic, ledger)
    print(f"Added hypothesis {args.id}")


def cmd_add_closure_search(args):
    if args.search_direction not in VALID_SEARCH_DIRECTIONS:
        print(f"Error: invalid search_direction {args.search_direction}", file=sys.stderr)
        sys.exit(1)
    if args.perspective not in VALID_PERSPECTIVES:
        print(f"Error: invalid perspective {args.perspective}", file=sys.stderr)
        sys.exit(1)
    if args.effect_on_conclusion not in VALID_EFFECTS:
        print(f"Error: invalid effect_on_conclusion {args.effect_on_conclusion}", file=sys.stderr)
        sys.exit(1)
    ledger = _load_ledger(args.topic)
    ledger.setdefault("closure_searches", {})[args.id] = {
        "id": args.id,
        "trigger": args.trigger or "",
        "search_direction": args.search_direction,
        "perspective": args.perspective,
        "source_ids": _split_csv(args.source_ids),
        "new_evidence": args.new_evidence or "",
        "effect_on_conclusion": args.effect_on_conclusion,
        "counterintuitive_angle": args.counterintuitive_angle or "",
        "alternative_hypothesis": args.alternative_hypothesis or "",
        "decision_impact": args.decision_impact or "",
    }
    _save_ledger(args.topic, ledger)
    print(f"Added closure search {args.id}")


def cmd_add_red_team(args):
    ledger = _load_ledger(args.topic)
    if not isinstance(ledger.get("red_team_arguments"), list):
        ledger["red_team_arguments"] = []
    ledger["red_team_arguments"].append({
        "argument": args.argument,
        "target_claim_ids": _split_csv(args.target_claim_ids),
        "severity": args.severity,
        "counter_evidence": args.counter_evidence or "",
    })
    _save_ledger(args.topic, ledger)
    print(f"Added red team argument (total: {len(ledger['red_team_arguments'])})")


def cmd_set_dimensions(args):
    dims = [d.strip() for d in args.dimensions.split(",") if d.strip()]
    if len(dims) < 3:
        print(f"Error: at least 3 dimensions required, got {len(dims)}", file=sys.stderr)
        sys.exit(1)
    ledger = _load_ledger(args.topic)
    ledger["dimensions"] = dims
    _save_ledger(args.topic, ledger)
    print(f"Set dimensions: {dims}")


def _auto_correct_source_type(raw_type: str) -> str:
    """Auto-correct common source type mistakes."""
    if not raw_type:
        return "T3_Synthesis"
    t = raw_type.strip()
    t = re.sub(r"^T(\d)[_\s]+([A-Za-z])", r"T\1_\2", t)
    MAPPING = {
        "t1academic": "T1_Academic",
        "t2academic": "T2_Academic",
        "t1official": "T1_Official",
        "t2official": "T2_Official",
        "t1_data": "T2_Data",
        "t2_data": "T2_Data",
        "t1creator": "T2_Creator",
        "t2creator": "T2_Creator",
        "t3synthesis": "T3_Synthesis",
        "t4community": "T4_Community",
        "t5recap": "T5_Recap",
        "t1": "T1_Academic",
        "t2": "T2_Data",
        "t3": "T3_Synthesis",
        "t4": "T4_Community",
        "t5": "T5_Recap",
        "academic": "T1_Academic",
        "official": "T1_Official",
        "data": "T2_Data",
        "creator": "T2_Creator",
        "synthesis": "T3_Synthesis",
        "community": "T4_Community",
        "recap": "T5_Recap",
    }
    lower_t = t.lower()
    if lower_t in MAPPING:
        return MAPPING[lower_t]
    return t


def _auto_correct_access_status(raw: str) -> str:
    """Normalize access status values."""
    if not raw:
        return "unverified"
    MAPPING = {
        "verified": "reachable",
        "verified_directly": "reachable",
        "accessible": "reachable",
        "open": "reachable",
        "confirmed": "reachable",
        "unverified": "unverified",
        "unreachable": "unreachable",
        "timed_out": "timed_out",
    }
    lower = raw.lower().strip()
    if lower in MAPPING:
        return MAPPING[lower]
    VALID = {"reachable", "uniquely_identifiable", "timed_out", "unreachable", "unverified"}
    return raw if raw in VALID else "unverified"


def _auto_correct_trace_status(raw: str) -> str:
    """Normalize trace status values."""
    if not raw:
        return "unverified"
    MAPPING = {
        "verified": "original",
        "verified_directly": "original",
        "traced_back": "traced",
        "cited": "traced",
        "referenced": "traced",
        "as_cited": "as_cited_not_verified",
        "unverified": "unverified",
    }
    lower = raw.lower().strip()
    if lower in MAPPING:
        return MAPPING[lower]
    VALID = {"original", "traced", "as_cited_not_verified", "unverified"}
    return raw if raw in VALID else "unverified"


def _normalize_source(raw: dict) -> dict:
    url = raw.get("url") or raw.get("citation") or ""
    raw_type = raw.get("type", "")
    corrected_type = _auto_correct_source_type(raw_type)
    corrected_access = _auto_correct_access_status(raw.get("access_status", ""))
    corrected_trace = _auto_correct_trace_status(raw.get("trace_status", ""))
    return {
        "id": raw["id"],
        "type": corrected_type,
        "title": raw.get("title", ""),
        "url": raw.get("url", ""),
        "citation": raw.get("citation", ""),
        "language": raw.get("language", "en"),
        "publisher": raw.get("publisher", ""),
        "publisher_type": raw.get("publisher_type", "unknown"),
        "official_domain": raw.get("official_domain", ""),
        "url_domain": raw.get("url_domain") or _domain(url),
        "access_status": corrected_access,
        "trace_status": corrected_trace,
        "access_date": raw.get("access_date", date.today().isoformat()),
        "used_for": raw.get("used_for", []),
        "notes": raw.get("notes", ""),
    }


def _normalize_claim(raw: dict) -> dict:
    raw_vstatus = raw.get("verification_status", "unverified")
    VER_MAP = {
        "verified": "verified_directly",
        "verified_directly": "verified_directly",
        "traced_back": "traced_back",
        "traced": "traced_back",
        "unverified": "unverified",
        "gap": "gap",
        "": "unverified",
    }
    corrected_vstatus = VER_MAP.get(raw_vstatus.lower().strip(), raw_vstatus) if raw_vstatus else "unverified"
    if corrected_vstatus not in VALID_VERIFICATION:
        corrected_vstatus = "unverified"
    claim_text = raw.get("claim", "")
    numeric = raw.get("numeric")
    if numeric is None or numeric == "auto":
        numeric = NUMERIC_RE.search(claim_text) is not None
    return {
        "id": raw["id"],
        "claim": claim_text,
        "grade": raw.get("grade", "C"),
        "confidence": raw.get("confidence", "Medium"),
        "primary_sources": raw.get("primary_sources", []),
        "corroboration_sources": raw.get("corroboration_sources", []),
        "contradiction_checked": bool(raw.get("contradiction_checked", False)),
        "verification_status": corrected_vstatus,
        "used_in": raw.get("used_in", []),
        "numeric": bool(numeric),
        "notes": raw.get("notes", ""),
    }


def _normalize_recommendation(raw: dict) -> dict:
    return {
        "id": raw["id"],
        "text": raw.get("text", ""),
        "claim_ids": raw.get("claim_ids", []),
        "type": raw.get("type", "validation"),
        "notes": raw.get("notes", ""),
    }


def _normalize_closure_search(raw: dict) -> dict:
    return {
        "id": raw["id"],
        "trigger": raw.get("trigger", ""),
        "search_direction": raw.get("search_direction", "neutral"),
        "perspective": raw.get("perspective", "neutral"),
        "source_ids": raw.get("source_ids", []),
        "new_evidence": raw.get("new_evidence", ""),
        "effect_on_conclusion": raw.get("effect_on_conclusion", "no_material_change"),
        "counterintuitive_angle": raw.get("counterintuitive_angle", ""),
        "alternative_hypothesis": raw.get("alternative_hypothesis", ""),
        "decision_impact": raw.get("decision_impact", ""),
    }


def _normalize_subquestion(raw: dict) -> dict:
    return {
        "id": raw["id"],
        "question": raw.get("question", ""),
        "source_excerpt": raw.get("source_excerpt", ""),
        "priority": raw.get("priority", "medium"),
        "status": raw.get("status", "unanswered"),
        "answered_by": raw.get("answered_by", []),
        "narrative_ref": raw.get("narrative_ref", ""),
        "module_ref": raw.get("module_ref", ""),
        "gap_note": raw.get("gap_note", ""),
        "loop_action": raw.get("loop_action", "none"),
    }


def _normalize_module(raw: dict) -> dict:
    return {
        "id": raw["id"],
        "subquestion_id": raw.get("subquestion_id", ""),
        "title": raw.get("title", ""),
        "content": raw.get("content", ""),
        "claim_ids": raw.get("claim_ids", []),
        "status": raw.get("status", "partial"),
        "language": raw.get("language"),
    }


def _normalize_prompt_item(raw: dict) -> dict:
    return {
        "id": raw["id"],
        "text": raw.get("text", ""),
        "source_excerpt": raw.get("source_excerpt", ""),
        "priority": raw.get("priority", "medium"),
        "mapped_subquestions": raw.get("mapped_subquestions", []),
        "status": raw.get("status", "unmapped"),
        "gap_note": raw.get("gap_note", ""),
    }


def _normalize_hypothesis(raw: dict) -> dict:
    return {
        "id": raw["id"],
        "initial_state": raw.get("initial_state", ""),
        "current_state": raw.get("current_state", ""),
        "mutation_trigger": raw.get("mutation_trigger", ""),
        "trigger_claim_ids": raw.get("trigger_claim_ids", []),
        "status": raw.get("status", "testing"),
        "confidence": raw.get("confidence", 0),
        "notes": raw.get("notes", ""),
    }


def _detect_task_type(topic: str, scope: str) -> str:
    """Auto-detect research task type from topic and scope keywords."""
    combined = (topic + " " + scope).lower()
    scores = {}
    for task_type, keywords in TASK_TYPE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in combined)
        if score > 0:
            scores[task_type] = score
    if not scores:
        return ""
    return max(scores, key=scores.get)


def cmd_import_ledger(args):
    with open(args.input, "r", encoding="utf-8") as f:
        payload = json.load(f)
    topic = args.topic or payload.get("topic")
    if not topic:
        print("Error: topic required either in JSON or --topic", file=sys.stderr)
        sys.exit(1)
    if args.init_if_missing and not os.path.exists(_ledger_filepath(topic)):
        _save_ledger(topic, _empty_ledger(topic, payload.get("scope", "")))
    ledger = _load_ledger(topic)
    if payload.get("scope"):
        ledger["scope"] = payload["scope"]
    for src in payload.get("sources", []):
        norm = _normalize_source(src)
        if norm["type"] not in VALID_SOURCE_TYPES:
            msg = f"Error: invalid source type {norm['type']} for {norm['id']}"
            if args.loose:
                print(f"WARNING: {msg}", file=sys.stderr)
            else:
                print(f"{msg}", file=sys.stderr)
                sys.exit(1)
        if norm["access_status"] not in VALID_ACCESS or norm["trace_status"] not in VALID_TRACE:
            msg = f"Error: invalid access/trace status for {norm['id']}"
            if args.loose:
                print(f"WARNING: {msg}", file=sys.stderr)
            else:
                print(f"{msg}", file=sys.stderr)
                sys.exit(1)
        if norm["publisher_type"] not in VALID_PUBLISHER_TYPES:
            msg = f"Error: invalid publisher_type for {norm['id']}"
            if args.loose:
                print(f"WARNING: {msg}", file=sys.stderr)
            else:
                print(f"{msg}", file=sys.stderr)
                sys.exit(1)
        ledger["sources"][norm["id"]] = norm
    for claim in payload.get("claims", []):
        norm = _normalize_claim(claim)
        if norm["grade"] not in VALID_GRADES or norm["confidence"] not in VALID_CONFIDENCE:
            msg = f"Error: invalid claim grade/confidence for {norm['id']}"
            if args.loose:
                print(f"WARNING: {msg}", file=sys.stderr)
            else:
                print(f"{msg}", file=sys.stderr)
                sys.exit(1)
        if norm["verification_status"] not in VALID_VERIFICATION:
            msg = f"Error: invalid verification status for {norm['id']}"
            if args.loose:
                print(f"WARNING: {msg}", file=sys.stderr)
            else:
                print(f"{msg}", file=sys.stderr)
                sys.exit(1)
        ledger["claims"][norm["id"]] = norm
    for rec in payload.get("recommendations", []):
        norm = _normalize_recommendation(rec)
        if norm["type"] not in {"action", "validation", "research_next", "advisory"}:
            msg = f"Error: invalid recommendation type for {norm['id']}"
            if args.loose:
                print(f"WARNING: {msg}", file=sys.stderr)
            else:
                print(f"{msg}", file=sys.stderr)
                sys.exit(1)
        ledger["recommendations"][norm["id"]] = norm
    for section, content in payload.get("narrative_sections", {}).items():
        mapped_section = section
        if section not in NARRATIVE_SECTIONS:
            # Try to find a NARRATIVE_SECTIONS key via SECTION_MAP reverse mapping
            heading = SECTION_MAP.get(section)
            if heading:
                for ns_key, ns_heading in NARRATIVE_SECTIONS.items():
                    if ns_heading == heading:
                        mapped_section = ns_key
                        break
            if mapped_section == section:
                # Still not found after mapping
                msg = f"Error: invalid narrative section {section}"
                if args.loose:
                    print(f"WARNING: {msg}", file=sys.stderr)
                    continue  # Skip, don't import
                else:
                    print(f"{msg}", file=sys.stderr)
                    sys.exit(1)
            else:
                print(f"WARNING: mapped legacy section '{section}' -> '{mapped_section}'", file=sys.stderr)
        ledger.setdefault("report_config", {}).setdefault("narrative_sections", {})[mapped_section] = content
    if payload.get("report_config", {}).get("report_language"):
        ledger.setdefault("report_config", {})["report_language"] = payload["report_config"]["report_language"]
    for cs in payload.get("closure_searches", []):
        norm = _normalize_closure_search(cs)
        if norm["search_direction"] not in VALID_SEARCH_DIRECTIONS:
            msg = f"Error: invalid search_direction {norm['search_direction']} for {norm['id']}"
            if args.loose:
                print(f"WARNING: {msg}", file=sys.stderr)
            else:
                print(f"{msg}", file=sys.stderr)
                sys.exit(1)
        if norm["perspective"] not in VALID_PERSPECTIVES:
            msg = f"Error: invalid perspective {norm['perspective']} for {norm['id']}"
            if args.loose:
                print(f"WARNING: {msg}", file=sys.stderr)
            else:
                print(f"{msg}", file=sys.stderr)
                sys.exit(1)
        if norm["effect_on_conclusion"] not in VALID_EFFECTS:
            msg = f"Error: invalid effect_on_conclusion {norm['effect_on_conclusion']} for {norm['id']}"
            if args.loose:
                print(f"WARNING: {msg}", file=sys.stderr)
            else:
                print(f"{msg}", file=sys.stderr)
                sys.exit(1)
        ledger["closure_searches"][norm["id"]] = norm
    if payload.get("red_team_arguments"):
        ledger["red_team_arguments"] = payload["red_team_arguments"]
    _raw_pi = payload.get("prompt_items", [])
    if isinstance(_raw_pi, dict):
        _pi_list = []
        for _pid, _pval in _raw_pi.items():
            if isinstance(_pval, dict):
                _pval["id"] = _pid
                _pi_list.append(_pval)
            elif isinstance(_pval, str):
                _pi_list.append({"id": _pid, "text": _pval})
        payload["prompt_items"] = _pi_list
    elif not isinstance(_raw_pi, list):
        payload["prompt_items"] = []
    for sq in payload.get("subquestions", []):
        norm = _normalize_subquestion(sq)
        if norm["status"] not in VALID_SUBQUESTION_STATUS:
            msg = f"Error: invalid subquestion status {norm['status']} for {norm['id']}"
            if args.loose:
                print(f"WARNING: {msg}", file=sys.stderr)
            else:
                print(f"{msg}", file=sys.stderr)
                sys.exit(1)
        if norm["priority"] not in VALID_SUBQUESTION_PRIORITY:
            msg = f"Error: invalid subquestion priority {norm['priority']} for {norm['id']}"
            if args.loose:
                print(f"WARNING: {msg}", file=sys.stderr)
            else:
                print(f"{msg}", file=sys.stderr)
                sys.exit(1)
        if norm["loop_action"] not in VALID_SUBQUESTION_LOOP_ACTION:
            msg = f"Error: invalid loop_action {norm['loop_action']} for {norm['id']}"
            if args.loose:
                print(f"WARNING: {msg}", file=sys.stderr)
            else:
                print(f"{msg}", file=sys.stderr)
                sys.exit(1)
        ledger["subquestions"][norm["id"]] = norm
    for mod in payload.get("modules", []):
        norm = _normalize_module(mod)
        if norm["status"] not in VALID_MODULE_STATUS:
            msg = f"Error: invalid module status {norm['status']} for {norm['id']}"
            if args.loose:
                print(f"WARNING: {msg}", file=sys.stderr)
            else:
                print(f"{msg}", file=sys.stderr)
                sys.exit(1)
        if norm["language"] not in VALID_MODULE_LANGUAGE:
            msg = f"Error: invalid module language {norm['language']} for {norm['id']}"
            if args.loose:
                print(f"WARNING: {msg}", file=sys.stderr)
            else:
                print(f"{msg}", file=sys.stderr)
                sys.exit(1)
        ledger["modules"][norm["id"]] = norm
    for pi in payload.get("prompt_items", []):
        norm = _normalize_prompt_item(pi)
        if norm["status"] not in VALID_PROMPT_ITEM_STATUS:
            msg = f"Error: invalid prompt_item status {norm['status']} for {norm['id']}"
            if args.loose:
                print(f"WARNING: {msg}", file=sys.stderr)
            else:
                print(f"{msg}", file=sys.stderr)
                sys.exit(1)
        if norm["priority"] not in VALID_PROMPT_ITEM_PRIORITY:
            msg = f"Error: invalid prompt_item priority {norm['priority']} for {norm['id']}"
            if args.loose:
                print(f"WARNING: {msg}", file=sys.stderr)
            else:
                print(f"{msg}", file=sys.stderr)
                sys.exit(1)
        ledger["prompt_items"][norm["id"]] = norm
    for hyp in payload.get("hypotheses", []):
        norm = _normalize_hypothesis(hyp)
        if norm["status"] not in VALID_HYPOTHESIS_STATUS:
            msg = f"Error: invalid hypothesis status {norm['status']} for {norm['id']}"
            if args.loose:
                print(f"WARNING: {msg}", file=sys.stderr)
            else:
                print(f"{msg}", file=sys.stderr)
                sys.exit(1)
        ledger["hypotheses"][norm["id"]] = norm
    if "dimensions" in payload:
        batch_dims = payload["dimensions"]
        if isinstance(batch_dims, list) and len(batch_dims) >= 3:
            ledger["dimensions"] = batch_dims
    _save_ledger(topic, ledger)
    print(
        f"Imported ledger batch for topic {topic}: {len(payload.get('sources', []))} sources, {len(payload.get('claims', []))} claims, {len(payload.get('recommendations', []))} recommendations, {len(payload.get('closure_searches', []))} closure_searches, {len(payload.get('subquestions', []))} subquestions, {len(payload.get('modules', []))} modules, {len(payload.get('prompt_items', []))} prompt_items, {len(payload.get('hypotheses', []))} hypotheses"
    )


def _check_numeric_variance(claim: dict) -> Optional[dict]:
    """Check if numeric claim has conflicting values across sources.
    Returns None if no variance issue, or a dict with variance details."""
    import json as _json
    notes = claim.get("notes", "")
    raw_values = []

    try:
        if "raw_values" in notes:
            for line in notes.split("\n"):
                line = line.strip()
                if line.startswith("raw_values:"):
                    rest = line[len("raw_values:"):].strip()
                    raw_values = _json.loads(rest)
                    break
                elif line.startswith("{"):
                    parsed = _json.loads(line)
                    if "raw_values" in parsed:
                        raw_values = parsed["raw_values"]
                        break
    except (ValueError, TypeError):
        pass

    if not raw_values or len(raw_values) < 2:
        return None

    numbers = []
    for rv in raw_values:
        v = rv.get("value")
        if isinstance(v, (int, float)) and v > 0:
            numbers.append(v)

    if len(numbers) < 2:
        return None

    mean_val = sum(numbers) / len(numbers)
    if mean_val == 0:
        return None
    max_deviation = max(abs(n - mean_val) / mean_val for n in numbers)

    VARIANCE_THRESHOLD = 0.15
    if max_deviation > VARIANCE_THRESHOLD:
        return {
            "violation": "numeric_variance_exceeded",
            "values": raw_values,
            "mean": round(mean_val, 2),
            "max_deviation_pct": round(max_deviation * 100, 1),
            "threshold_pct": VARIANCE_THRESHOLD * 100,
            "recommendation": "Tag claim verification_status as disputed_data and document discrepancy in contradictions"
        }
    return None


def _verify_ledger(ledger: dict, dynamic_threshold: Optional[str] = None) -> dict:
    sources = ledger.get("sources", {})
    claims = ledger.get("claims", {})
    recommendations = ledger.get("recommendations", {})
    gates = {}
    violations = []

    # Empty ledger detection - fail fast if no research was conducted
    if not sources and not claims and ledger.get("verification", {}).get("status") == "NOT_RUN":
        empty_violation = {
            "violation": "empty_ledger_no_research",
            "reason": "Ledger is empty with no sources or claims; research not completed",
        }
        gates["empty_ledger"] = {"status": "FAIL", "violations": [empty_violation]}
        violations.append({"gate": "empty_ledger", **empty_violation})
        return {
            "status": "FAIL",
            "report_status": "Draft — ledger empty, research not completed",
            "use_without_rereading_confidence": "Low",
            "gates": gates,
            "violations": violations,
            "verified_at": _now(),
            "failure_status": "empty_ledger",
            "failure_reason": "empty_ledger_no_research",
            "failure_stage": "verify",
        }

    # access/trace consistency
    access_trace_violations = []
    access_trace_warnings = []
    for sid, src in sources.items():
        access = src.get("access_status")
        trace = src.get("trace_status")
        if access in {"timed_out", "unreachable", "unverified"} and trace in {"original", "traced"}:
            access_trace_violations.append({"source_id": sid, "access_status": access, "trace_status": trace})
        if src.get("type") == "T1_Official":
            if src.get("publisher_type") != "official":
                access_trace_violations.append(
                    {
                        "source_id": sid,
                        "violation": "T1_Official_requires_publisher_type_official",
                        "publisher_type": src.get("publisher_type"),
                    }
                )
            elif src.get("official_domain") and not _official_source_valid(src):
                # Domain mismatch is a warning, not a failure — agents may set brand domain
                # while URL is on GitHub/docs subdomain. Still valid as official source.
                access_trace_warnings.append(
                    {
                        "source_id": sid,
                        "violation": "T1_Official_domain_mismatch",
                        "url_domain": src.get("url_domain"),
                        "official_domain": src.get("official_domain"),
                        "note": "Warning only — domain mismatch does not block verification",
                    }
                )
            elif not src.get("official_domain"):
                access_trace_violations.append({"source_id": sid, "violation": "T1_Official_missing_official_domain"})
    gates["access_trace_consistency"] = {
        "status": "PASS" if not access_trace_violations else "FAIL",
        "violations": access_trace_violations,
        "warnings": access_trace_warnings,
    }
    violations.extend([{"gate": "access_trace_consistency", **v} for v in access_trace_violations])

    # T1/T2 ratio
    typed_sources = [s for s in sources.values() if s.get("type") in VALID_SOURCE_TYPES]
    numerator_sources = [
        s
        for s in typed_sources
        if s.get("type") in T1T2_TYPES
        and s.get("trace_status") in {"original", "traced"}
        and s.get("access_status") in {"reachable", "uniquely_identifiable"}
        and (s.get("type") != "T1_Official" or _official_source_valid(s))
    ]
    denominator = len(typed_sources)
    numerator = len(numerator_sources)
    ratio = numerator / denominator if denominator else 0.0
    threshold = 0.5
    threshold_name = "default"
    if dynamic_threshold == "breaking":
        threshold = 0.3
        threshold_name = "breaking"
    elif dynamic_threshold == "emergent":
        threshold = 0.35
        threshold_name = "emergent"
    elif dynamic_threshold == "commercial":
        threshold = 0.20
        threshold_name = "commercial"
    elif dynamic_threshold == "practitioner":
        threshold = 0.10
        threshold_name = "practitioner"
    ratio_status = "PASS" if denominator and ratio >= threshold else "FAIL"
    gates["t1t2_ratio"] = {
        "status": ratio_status,
        "numerator": numerator,
        "denominator": denominator,
        "ratio": round(ratio, 4),
        "threshold": threshold,
        "threshold_name": threshold_name,
        "numerator_sources": [s["id"] for s in numerator_sources],
        "excluded_sources": [s["id"] for s in typed_sources if s not in numerator_sources],
    }
    if ratio_status == "FAIL":
        violations.append(
            {
                "gate": "t1t2_ratio",
                "numerator": numerator,
                "denominator": denominator,
                "ratio": ratio,
                "threshold": threshold,
            }
        )

    # claim source references exist + grade rules + content integrity
    claim_violations = []
    for sid, src in sources.items():
        for cid in src.get("used_for", []):
            if cid and cid not in claims:
                claim_violations.append(
                    {"source_id": sid, "claim_id": cid, "violation": "source_used_for_claim_missing"}
                )
    for cid, claim in claims.items():
        claim_sources = claim.get("primary_sources", []) + claim.get("corroboration_sources", [])
        for sid in claim_sources:
            if sid and sid not in sources:
                claim_violations.append({"claim_id": cid, "source_id": sid, "violation": "source_missing"})
        if not (claim.get("claim") or "").strip():
            claim_violations.append({"claim_id": cid, "violation": "empty_claim_text"})
        primary = [sources[sid] for sid in claim.get("primary_sources", []) if sid in sources]
        if not primary or all(not p or not str(p).strip() for p in claim.get("primary_sources", [])):
            claim_violations.append({"claim_id": cid, "violation": "missing_primary_sources"})
        primary = [sources[sid] for sid in claim.get("primary_sources", []) if sid in sources]
        t1t2_primary = [
            s
            for s in primary
            if s.get("type") in T1T2_TYPES
            and s.get("trace_status") in {"original", "traced"}
            and s.get("access_status") in {"reachable", "uniquely_identifiable"}
            and (s.get("type") != "T1_Official" or _official_source_valid(s))
        ]
        if claim.get("grade") == "A" and len(t1t2_primary) < 2:
            claim_violations.append({"claim_id": cid, "violation": "A_grade_needs_two_T1T2_primary"})
        if claim.get("grade") == "B" and len(t1t2_primary) < 1:
            all_claim_sources = [sources[sid] for sid in (claim.get("primary_sources", []) + claim.get("corroboration_sources", [])) if sid in sources]
            t4_sources = [s for s in all_claim_sources if s.get("type") == "T4_Community"]
            if t4_sources and not t1t2_primary:
                t4_domains = [s.get("url_domain", "") for s in t4_sources]
                unique_domains = set(d for d in t4_domains if d)
                if len(unique_domains) < T4_TRIANGULATION_MIN_SOURCES:
                    claim_violations.append({
                        "claim_id": cid,
                        "violation": "B_grade_T4_triangulation_insufficient_domains",
                        "unique_domains": len(unique_domains),
                        "required": T4_TRIANGULATION_MIN_SOURCES,
                        "reason": f"B grade via T4 triangulation requires {T4_TRIANGULATION_MIN_SOURCES}+ independent domains, found {len(unique_domains)}"
                    })
            else:
                claim_violations.append({"claim_id": cid, "violation": "B_grade_needs_one_T1T2_primary"})
        if (
            claim.get("numeric")
            and claim.get("grade") in {"D", "F"}
            and any(x in claim.get("used_in", []) for x in ["ExecutiveAnswer", "Recommendations"])
        ):
            claim_violations.append({"claim_id": cid, "violation": "D_or_F_numeric_used_in_action_surface"})
        if claim.get("verification_status") == "unverified":
            used_in = claim.get("used_in", [])
            if "ExecutiveAnswer" in used_in:
                claim_violations.append({"claim_id": cid, "violation": "unverified_claim_used_in_decision"})
            if "Recommendations" in used_in:
                claim_violations.append({"claim_id": cid, "violation": "unverified_claim_used_in_recommendation"})
        if claim.get("verification_status") == "disputed_data":
            used_in = claim.get("used_in", [])
            if "ExecutiveAnswer" in used_in or "Recommendations" in used_in:
                has_high_risk_caveat = "high risk" in claim.get("notes", "").lower() or "高风险" in claim.get("notes", "").lower()
                if not has_high_risk_caveat:
                    claim_violations.append({
                        "claim_id": cid,
                        "violation": "disputed_data_used_without_high_risk_caveat",
                        "used_in": used_in
                    })
    gates["claim_source_integrity"] = {
        "status": "PASS" if not claim_violations else "FAIL",
        "violations": claim_violations,
    }
    violations.extend([{"gate": "claim_source_integrity", **v} for v in claim_violations])

    # recommendation trace + content integrity
    rec_violations = []
    for rid, rec in recommendations.items():
        if not (rec.get("text") or "").strip():
            rec_violations.append({"recommendation_id": rid, "violation": "empty_recommendation_text"})
        if not rec.get("claim_ids"):
            rec_violations.append({"recommendation_id": rid, "violation": "empty_claim_ids"})
        for cid in rec.get("claim_ids", []):
            if cid not in claims:
                rec_violations.append({"recommendation_id": rid, "claim_id": cid, "violation": "claim_missing"})
            elif claims[cid].get("grade") == "F":
                rec_violations.append({"recommendation_id": rid, "claim_id": cid, "violation": "F_grade_claim_used"})
            elif claims[cid].get("verification_status") == "unverified" and rec.get("type") in ("action", "advisory"):
                rec_violations.append(
                    {"recommendation_id": rid, "claim_id": cid, "violation": "unverified_claim_in_action_advisory"}
                )
            elif not claims[cid].get("contradiction_checked") and rec.get("type") in ("action", "advisory"):
                rec_violations.append(
                    {
                        "recommendation_id": rid,
                        "claim_id": cid,
                        "violation": "contradiction_unchecked_in_action_advisory",
                    }
                )
        if ratio_status == "FAIL" and rec.get("type") == "action":
            rec_violations.append({"recommendation_id": rid, "violation": "action_recommendation_with_failed_ratio"})
    gates["recommendation_trace"] = {"status": "PASS" if not rec_violations else "FAIL", "violations": rec_violations}
    violations.extend([{"gate": "recommendation_trace", **v} for v in rec_violations])

    # research closure gate
    # Normalize closure_searches: handle both dict and list formats
    _cs_raw = ledger.get("closure_searches", {})
    if isinstance(_cs_raw, list):
        _cs_normalized = {}
        for i, cs_item in enumerate(_cs_raw):
            if isinstance(cs_item, dict):
                _cs_normalized[cs_item.get("id", f"CS{i+1:02d}")] = cs_item
            else:
                _cs_normalized[f"CS{i+1:02d}"] = {"trigger": str(cs_item)}
        closure_searches = _cs_normalized
        ledger["closure_searches"] = closure_searches  # persist fix
    elif isinstance(_cs_raw, dict):
        closure_searches = _cs_raw
    else:
        closure_searches = {}
    scope = ledger.get("scope", "").lower()
    topic = ledger.get("topic", "").lower()
    is_strategic = any(kw in scope or kw in topic for kw in SCOPE_KEYWORDS_STRATEGIC)
    min_closure = 3 if is_strategic else 2
    closure_violations = []
    for csid, cs in closure_searches.items():
        if not cs.get("trigger"):
            closure_violations.append(
                {"closure_search_id": csid, "violation": "missing_required_field", "field": "trigger"}
            )
        if not cs.get("search_direction"):
            closure_violations.append(
                {"closure_search_id": csid, "violation": "missing_required_field", "field": "search_direction"}
            )
        elif cs.get("search_direction") not in VALID_SEARCH_DIRECTIONS:
            closure_violations.append(
                {
                    "closure_search_id": csid,
                    "violation": "invalid_search_direction",
                    "value": cs.get("search_direction"),
                }
            )
        if not cs.get("perspective"):
            closure_violations.append(
                {"closure_search_id": csid, "violation": "missing_required_field", "field": "perspective"}
            )
        elif cs.get("perspective") not in VALID_PERSPECTIVES:
            closure_violations.append(
                {"closure_search_id": csid, "violation": "invalid_perspective", "value": cs.get("perspective")}
            )
        source_ids = cs.get("source_ids", [])
        if not source_ids:
            closure_violations.append({"closure_search_id": csid, "violation": "empty_source_ids"})
        for sid in source_ids:
            if sid and sid not in sources:
                closure_violations.append({"closure_search_id": csid, "source_id": sid, "violation": "source_missing"})
        if not cs.get("new_evidence"):
            closure_violations.append(
                {"closure_search_id": csid, "violation": "missing_required_field", "field": "new_evidence"}
            )
        if not cs.get("effect_on_conclusion"):
            closure_violations.append(
                {"closure_search_id": csid, "violation": "missing_required_field", "field": "effect_on_conclusion"}
            )
        elif cs.get("effect_on_conclusion") not in VALID_EFFECTS:
            closure_violations.append(
                {"closure_search_id": csid, "violation": "invalid_effect", "effect": cs.get("effect_on_conclusion")}
            )
    closure_count = len(closure_searches)
    if closure_count < min_closure:
        closure_violations.append(
            {"violation": "insufficient_closure_searches", "found": closure_count, "required": min_closure}
        )
    if closure_count > 0:
        all_nmc = all(cs.get("effect_on_conclusion") == "no_material_change" for cs in closure_searches.values())
        if all_nmc:
            closure_violations.append({"violation": "all_closure_no_material_change"})
        has_critical_refute = any(
            cs.get("perspective") in ("critical",) or cs.get("search_direction") == "refute"
            for cs in closure_searches.values()
        )
        if not has_critical_refute:
            closure_violations.append({"violation": "missing_critical_refute_closure"})
        has_supportive_confirm_alt = any(
            cs.get("perspective") in ("supportive", "alternative") or cs.get("search_direction") in ("confirm",)
            for cs in closure_searches.values()
        )
        if not has_supportive_confirm_alt:
            closure_violations.append({"violation": "missing_supportive_confirm_alternative_closure"})
        has_meaningful_effect = any(
            cs.get("effect_on_conclusion") in ("strengthened", "weakened", "changed")
            for cs in closure_searches.values()
        )
        if not has_meaningful_effect:
            closure_violations.append({"violation": "no_meaningful_effect"})
        if is_strategic:
            for csid, cs in closure_searches.items():
                is_critical_refute = cs.get("perspective") == "critical" or cs.get("search_direction") == "refute"
                if is_critical_refute and not cs.get("alternative_hypothesis"):
                    closure_violations.append(
                        {"closure_search_id": csid, "violation": "critical_refute_missing_alternative_hypothesis"}
                    )
                effect = cs.get("effect_on_conclusion", "")
                if effect in ("strengthened", "weakened", "changed") and not cs.get("decision_impact"):
                    closure_violations.append(
                        {
                            "closure_search_id": csid,
                            "violation": "meaningful_effect_missing_decision_impact",
                            "effect": effect,
                        }
                    )
            has_decision_impact = any(cs.get("decision_impact") for cs in closure_searches.values())
            if not has_decision_impact:
                closure_violations.append({"violation": "strategic_scope_requires_decision_impact"})
    gates["research_closure"] = {
        "status": "PASS" if not closure_violations else "FAIL",
        "violations": closure_violations,
        "closure_count": closure_count,
        "minimum_required": min_closure,
        "is_strategic_scope": is_strategic,
    }
    violations.extend([{"gate": "research_closure", **v} for v in closure_violations])

    # narrative_completeness gate
    narrative_completeness_violations = []
    narrative = ledger.get("report_config", {}).get("narrative_sections", {})
    recommendations = ledger.get("recommendations", {})
    for section in REQUIRED_NARRATIVE_SECTIONS:
        content = narrative.get(section, "").strip()
        if not content or content == "_(not supplied)_" or len(content) < 5:
            narrative_completeness_violations.append(
                {"section": section, "violation": "required_section_missing_or_blank"}
            )
    if recommendations and not narrative.get("recommendations", "").strip():
        narrative_completeness_violations.append(
            {"section": "recommendations", "violation": "recommendations_present_but_narrative_missing"}
        )
    combined = topic + " " + scope
    is_decision_grade = any(kw in combined for kw in STRATEGIC_SCOPE_KEYWORDS | {"decision", "commercial"})
    is_commercial = any(kw in combined for kw in COMMERCIAL_SCOPE_KEYWORDS)
    if is_decision_grade:
        for section in REQUIRED_DECISION_GRADE_SECTIONS:
            content = narrative.get(section, "").strip()
            if not content or content == "_(not supplied)_" or len(content) < 5:
                narrative_completeness_violations.append(
                    {
                        "section": section,
                        "violation": "decision_grade_required_section_missing",
                        "reason": "decision_grade_scope_requires_this_section",
                    }
                )
    if is_commercial:
        for section in REQUIRED_COMMERCIAL_SECTIONS:
            content = narrative.get(section, "").strip()
            if not content or content == "_(not supplied)_" or len(content) < 5:
                narrative_completeness_violations.append(
                    {"section": section, "violation": "commercial_scope_required_section_missing"}
                )
    gates["narrative_completeness"] = {
        "status": "PASS" if not narrative_completeness_violations else "FAIL",
        "violations": narrative_completeness_violations,
    }
    violations.extend([{"gate": "narrative_completeness", **v} for v in narrative_completeness_violations])

    # thesis_narrative gate
    thesis_violations = []
    all_narrative_text = " ".join(narrative.get(s, "") for s in narrative)
    has_thesis = bool(THESIS_PATTERN.search(all_narrative_text))
    if not has_thesis:
        thesis_violations.append({"violation": "thesis_decision_narrative_missing"})
    gates["thesis_narrative"] = {"status": "PASS" if not thesis_violations else "FAIL", "violations": thesis_violations}
    violations.extend([{"gate": "thesis_narrative", **v} for v in thesis_violations])

    # edge_cases gate
    edge_violations = []
    all_narrative_text = " ".join(narrative.get(s, "") for s in narrative)
    has_edge_cases = bool(EDGE_CASE_PATTERN.search(all_narrative_text))
    if not has_edge_cases:
        edge_violations.append({"violation": "edge_cases_failure_modes_missing"})
    gates["edge_cases"] = {"status": "PASS" if not edge_violations else "FAIL", "violations": edge_violations}
    violations.extend([{"gate": "edge_cases", **v} for v in edge_violations])

    # subquestion_coverage gate
    subquestion_coverage_violations = []
    coverage_loop_violations = []
    subquestions = ledger.get("subquestions", {})
    modules = ledger.get("modules", {})
    claims = ledger.get("claims", {})
    loop_plan = []

    if subquestions:
        for sid, sq in subquestions.items():
            if not (sq.get("question") or "").strip():
                subquestion_coverage_violations.append({"subquestion_id": sid, "violation": "empty_question_field"})
            if not (sq.get("source_excerpt") or "").strip():
                subquestion_coverage_violations.append({"subquestion_id": sid, "violation": "empty_source_excerpt"})
            status = sq.get("status", "unanswered")
            priority = sq.get("priority", "medium")
            if status == "unanswered" and priority == "high":
                subquestion_coverage_violations.append(
                    {
                        "subquestion_id": sid,
                        "violation": "high_priority_unanswered",
                        "priority": priority,
                        "status": status,
                    }
                )
            if status == "unanswered" and priority == "medium":
                subquestion_coverage_violations.append(
                    {
                        "subquestion_id": sid,
                        "violation": "medium_priority_unanswered",
                        "priority": priority,
                        "status": status,
                    }
                )
            if status == "answered":
                if not sq.get("answered_by"):
                    subquestion_coverage_violations.append(
                        {"subquestion_id": sid, "violation": "answered_missing_answered_by"}
                    )
                if not sq.get("narrative_ref") and not sq.get("module_ref"):
                    subquestion_coverage_violations.append(
                        {"subquestion_id": sid, "violation": "answered_missing_module_narrative_ref"}
                    )
                answered_by = sq.get("answered_by", [])
                for cid in answered_by:
                    if cid and cid not in claims:
                        subquestion_coverage_violations.append(
                            {"subquestion_id": sid, "claim_id": cid, "violation": "answered_by_claim_missing"}
                        )
            if status == "partial":
                if not sq.get("gap_note"):
                    subquestion_coverage_violations.append(
                        {"subquestion_id": sid, "violation": "partial_missing_gap_note"}
                    )
                if not sq.get("loop_action") or sq.get("loop_action") == "none":
                    subquestion_coverage_violations.append(
                        {"subquestion_id": sid, "violation": "partial_missing_loop_action"}
                    )
            if status == "gap_identified":
                if not sq.get("gap_note"):
                    subquestion_coverage_violations.append(
                        {"subquestion_id": sid, "violation": "gap_identified_missing_gap_note"}
                    )
                if not sq.get("narrative_ref") and not sq.get("module_ref"):
                    subquestion_coverage_violations.append(
                        {"subquestion_id": sid, "violation": "gap_identified_missing_narrative_module_ref"}
                    )
            module_ref = sq.get("module_ref", "")
            if module_ref and module_ref not in modules:
                subquestion_coverage_violations.append(
                    {"subquestion_id": sid, "module_ref": module_ref, "violation": "module_ref_missing"}
                )
        for mid, mod in modules.items():
            subq_ref = mod.get("subquestion_id", "")
            if subq_ref and subq_ref not in subquestions:
                subquestion_coverage_violations.append(
                    {"module_id": mid, "subquestion_id": subq_ref, "violation": "module_subquestion_id_invalid"}
                )
            for cid in mod.get("claim_ids", []):
                if cid and cid not in claims:
                    subquestion_coverage_violations.append(
                        {"module_id": mid, "claim_id": cid, "violation": "module_claim_missing"}
                    )
        if subquestion_coverage_violations:
            for v in subquestion_coverage_violations:
                sq_id = v.get("subquestion_id", "")
                loop_action = "continue_research"
                if sq_id and sq_id in subquestions:
                    la = subquestions[sq_id].get("loop_action", "none")
                    if la != "none":
                        loop_action = la
                loop_plan.append(
                    {"subquestion_id": sq_id, "violation": v.get("violation", ""), "loop_action": loop_action}
                )
    gates["subquestion_coverage"] = {
        "status": "PASS" if not subquestion_coverage_violations else "FAIL",
        "violations": subquestion_coverage_violations,
    }
    violations.extend([{"gate": "subquestion_coverage", **v} for v in subquestion_coverage_violations])

    # prompt_item_coverage gate
    prompt_item_coverage_violations = []
    prompt_items = ledger.get("prompt_items", {})
    subquestions = ledger.get("subquestions", {})

    # Strategic topic detection: requires prompt_items for multi-question/strategic topics
    topic_lower = ledger.get("topic", "").lower()
    scope_lower = ledger.get("scope", "").lower()
    combined_text = topic_lower + " " + scope_lower
    is_strategic = any(kw in combined_text for kw in STRATEGIC_KEYWORDS)
    has_multi_question = bool(MULTI_QUESTION_PATTERN.search(ledger.get("topic", "") + ledger.get("scope", "")))
    has_multi_q_keywords = any(kw in combined_text for kw in MULTI_QUESTION_KEYWORDS)
    requires_prompt_items = is_strategic or has_multi_question or has_multi_q_keywords

    if requires_prompt_items and not prompt_items:
        prompt_item_coverage_violations.append(
            {
                "violation": "strategic_topic_requires_prompt_items",
                "reason": "Topic or scope is strategic/multi-question but has no prompt_items",
            }
        )

    # Detect prompt_items in narrative but not at top level
    narrative = ledger.get("report_config", {}).get("narrative_sections", {})
    for section_key, section_content in narrative.items():
        if isinstance(section_content, str):
            if '"prompt_items"' in section_content or "'prompt_items'" in section_content:
                if not prompt_items:
                    prompt_item_coverage_violations.append(
                        {
                            "violation": "prompt_items_wrong_location",
                            "section": section_key,
                            "reason": "prompt_items JSON found in narrative but top-level prompt_items is empty",
                        }
                    )

    if prompt_items:
        for pid, pi in prompt_items.items():
            priority = pi.get("priority", "medium")
            status = pi.get("status", "unmapped")
            mapped_subquestions = pi.get("mapped_subquestions", [])
            gap_note = pi.get("gap_note", "")
            if priority in ("high", "medium") and status == "unmapped":
                prompt_item_coverage_violations.append(
                    {
                        "prompt_item_id": pid,
                        "violation": "high_medium_prompt_item_unmapped",
                        "priority": priority,
                        "status": status,
                    }
                )
            if status == "gap_identified" and not gap_note:
                prompt_item_coverage_violations.append(
                    {"prompt_item_id": pid, "violation": "gap_identified_prompt_item_missing_gap_note"}
                )
            for sq_id in mapped_subquestions:
                if sq_id and sq_id not in subquestions:
                    prompt_item_coverage_violations.append(
                        {
                            "prompt_item_id": pid,
                            "subquestion_id": sq_id,
                            "violation": "mapped_subquestion_does_not_exist",
                        }
                    )
    gates["prompt_item_coverage"] = {
        "status": "PASS" if not prompt_item_coverage_violations else "FAIL",
        "violations": prompt_item_coverage_violations,
    }
    violations.extend([{"gate": "prompt_item_coverage", **v} for v in prompt_item_coverage_violations])

    # claim_subquestion_trace gate
    claim_subquestion_trace_violations = []
    if subquestions:
        for cid, claim in claims.items():
            used_in = claim.get("used_in", [])
            grade = claim.get("grade", "C")
            notes = claim.get("notes", "").lower()
            is_background = any(kw in notes for kw in BACKGROUND_KEYWORDS)
            if is_background:
                continue
            is_actionable = "ExecutiveAnswer" in used_in or "Recommendations" in used_in
            is_high_grade = grade in ("A", "B", "C")
            if is_actionable or is_high_grade:
                covered = False
                for sid, sq in subquestions.items():
                    if cid in sq.get("answered_by", []):
                        covered = True
                        break
                if not covered:
                    for mid, mod in modules.items():
                        if cid in mod.get("claim_ids", []):
                            covered = True
                            break
                if not covered:
                    claim_subquestion_trace_violations.append(
                        {
                            "claim_id": cid,
                            "violation": "orphan_claim_not_mapped_to_subquestion",
                            "used_in": used_in,
                            "grade": grade,
                        }
                    )
    gates["claim_subquestion_trace"] = {
        "status": "PASS" if not claim_subquestion_trace_violations else "FAIL",
        "violations": claim_subquestion_trace_violations,
    }
    violations.extend([{"gate": "claim_subquestion_trace", **v} for v in claim_subquestion_trace_violations])

    # coverage_loop gate (computed after subquestion and prompt_item gates)
    coverage_loop_violations = []
    combined_loop_plan = list(loop_plan)
    if subquestions and subquestion_coverage_violations:
        coverage_loop_violations.append(
            {"violation": "subquestion_coverage_failed", "missing_count": len(subquestion_coverage_violations)}
        )
    if prompt_items and prompt_item_coverage_violations:
        coverage_loop_violations.append(
            {"violation": "prompt_item_coverage_failed", "missing_count": len(prompt_item_coverage_violations)}
        )
    for v in prompt_item_coverage_violations:
        pi_id = v.get("prompt_item_id", "")
        combined_loop_plan.append(
            {"prompt_item_id": pi_id, "violation": v.get("violation", ""), "loop_action": "continue_research"}
        )
    gates["coverage_loop"] = {
        "status": "PASS" if not coverage_loop_violations else "FAIL",
        "violations": coverage_loop_violations,
        "loop_plan": combined_loop_plan if coverage_loop_violations else [],
    }
    violations.extend([{"gate": "coverage_loop", **v} for v in coverage_loop_violations])

    # language_alignment gate
    language_violations = []
    report_lang = ledger.get("report_config", {}).get("report_language") or ledger.get("report_language", "")
    topic = ledger.get("topic", "")
    all_narrative_text = " ".join(narrative.get(s, "") for s in narrative)
    cjk_ratio = len(CJK_PATTERN.findall(all_narrative_text)) / max(len(all_narrative_text), 1)
    if cjk_ratio > 0.3 and report_lang == "en":
        language_violations.append(
            {
                "violation": "language_mismatch_cjk_content_en_language",
                "cjk_ratio": round(cjk_ratio, 3),
                "report_language": report_lang,
            }
        )
    elif cjk_ratio < 0.1 and report_lang == "zh":
        language_violations.append(
            {
                "violation": "language_mismatch_en_content_zh_language",
                "cjk_ratio": round(cjk_ratio, 3),
                "report_language": report_lang,
            }
        )
    gates["language_alignment"] = {
        "status": "PASS" if not language_violations else "FAIL",
        "violations": language_violations,
    }
    violations.extend([{"gate": "language_alignment", **v} for v in language_violations])

    # scope_fidelity gate: detect runtime vs training stage drift
    scope_fidelity_violations = []
    topic_lower = ledger.get("topic", "").lower()
    scope_lower = ledger.get("scope", "").lower()
    combined_topic = topic_lower + " " + scope_lower
    is_runtime_topic = bool(RUNTIME_TOPIC_PATTERN.search(combined_topic))
    is_training_topic = bool(TRAINING_STAGE_PATTERN.search(combined_topic))

    if is_runtime_topic and not is_training_topic and subquestions and prompt_items:
        runtime_subq_count = 0
        training_subq_count = 0
        runtime_claim_count = 0
        training_claim_count = 0

        for sid, sq in subquestions.items():
            q_lower = sq.get("question", "").lower()
            is_sq_runtime = bool(RUNTIME_TOPIC_PATTERN.search(q_lower))
            is_sq_training = bool(TRAINING_STAGE_PATTERN.search(q_lower))
            if is_sq_runtime:
                runtime_subq_count += 1
            if is_sq_training:
                training_subq_count += 1
            for cid in sq.get("answered_by", []):
                if cid in claims:
                    if is_sq_runtime:
                        runtime_claim_count += 1
                    if is_sq_training:
                        training_claim_count += 1

        total_subq = runtime_subq_count + training_subq_count
        if total_subq > 0 and training_subq_count > runtime_subq_count:
            scope_fidelity_violations.append(
                {
                    "violation": "runtime_topic_drifted_to_training_stage",
                    "reason": f"Runtime topic has {training_subq_count} training-stage subquestions vs {runtime_subq_count} runtime subquestions",
                    "training_subquestions": training_subq_count,
                    "runtime_subquestions": runtime_subq_count,
                    "recommendation": "Re-frame Q1 to address runtime/prompt-engineering aspects, keep training content as background",
                }
            )

        if runtime_claim_count > 0 and training_claim_count > runtime_claim_count:
            if not any(
                v.get("violation") == "runtime_topic_drifted_to_training_stage" for v in scope_fidelity_violations
            ):
                scope_fidelity_violations.append(
                    {
                        "violation": "runtime_topic_claims_from_training_stage",
                        "reason": f"Runtime topic has {training_claim_count} claims from training-stage vs {runtime_claim_count} from runtime",
                        "training_claims": training_claim_count,
                        "runtime_claims": runtime_claim_count,
                    }
                )

    gates["scope_fidelity"] = {
        "status": "PASS" if not scope_fidelity_violations else "FAIL",
        "violations": scope_fidelity_violations,
    }
    violations.extend([{"gate": "scope_fidelity", **v} for v in scope_fidelity_violations])

    # recommendation_actor_scope gate: action recommendations must match actor scope
    rec_actor_violations = []
    topic_lower = ledger.get("topic", "").lower()
    scope_lower = ledger.get("scope", "").lower()
    combined_topic = topic_lower + " " + scope_lower
    is_runtime_topic = bool(RUNTIME_TOPIC_PATTERN.search(combined_topic))

    for rid, rec in recommendations.items():
        rec_text_lower = (rec.get("text", "") + " " + rec.get("notes", "")).lower()
        rec_type = rec.get("type", "validation")

        if rec_type == "action":
            has_training_action = any(kw in rec_text_lower for kw in TRAINING_ACTION_KEYWORDS)
            is_marked_background = any(
                kw in rec.get("notes", "").lower() for kw in ["background", "advisory", "note-only", "context"]
            )

            if is_runtime_topic and has_training_action and not is_marked_background:
                rec_actor_violations.append(
                    {
                        "recommendation_id": rid,
                        "violation": "training_action_for_runtime_topic",
                        "reason": "Action recommendation contains training-level action for runtime prompt topic",
                        "recommendation_text": rec.get("text", "")[:100],
                        "recommendation_type": rec_type,
                        "suggestion": "Mark as advisory/background or re-frame for runtime actions (prompt_engineer scope)",
                    }
                )

    gates["recommendation_actor_scope"] = {
        "status": "PASS" if not rec_actor_violations else "FAIL",
        "violations": rec_actor_violations,
    }
    violations.extend([{"gate": "recommendation_actor_scope", **v} for v in rec_actor_violations])

    # source_dominance gate: detect when one source dominates A/B claims
    source_dom_violations = []
    ab_claims_by_source = {}
    for cid, claim in claims.items():
        if claim.get("grade") in ("A", "B"):
            for sid in claim.get("primary_sources", []):
                if sid not in ab_claims_by_source:
                    ab_claims_by_source[sid] = 0
                ab_claims_by_source[sid] += 1

    total_ab_claims = sum(ab_claims_by_source.values())
    if total_ab_claims >= MIN_CLAIMS_FOR_SOURCE_DOMINANCE and ab_claims_by_source:
        max_count = max(ab_claims_by_source.values())
        max_source = max(ab_claims_by_source, key=ab_claims_by_source.get)
        dominance_ratio = max_count / total_ab_claims
        if dominance_ratio > SOURCE_DOMINANCE_THRESHOLD:
            source_dom_violations.append(
                {
                    "violation": "source_dominance_exceeded",
                    "dominant_source": max_source,
                    "dominant_claim_count": max_count,
                    "total_ab_claims": total_ab_claims,
                    "dominance_ratio": round(dominance_ratio, 3),
                    "threshold": SOURCE_DOMINANCE_THRESHOLD,
                    "recommendation": "Ensure primary sources are balanced; investigate if research is over-reliant on one source",
                }
            )
        gates["source_dominance"] = {
            "status": "WARNING" if source_dom_violations else "PASS",
            "violations": source_dom_violations,
        }
    else:
        gates["source_dominance"] = {
            "status": "PASS",
            "violations": [],
            "note": f"Skipped (only {total_ab_claims} A/B claims, minimum {MIN_CLAIMS_FOR_SOURCE_DOMINANCE})",
        }

    # numeric_evidence_strength gate: exact numeric claims supporting recommendations need strong evidence
    numeric_violations = []
    for cid, claim in claims.items():
        if not claim.get("numeric"):
            continue
        if "Recommendations" not in claim.get("used_in", []) and "ExecutiveAnswer" not in claim.get("used_in", []):
            continue
        primary = [sources[sid] for sid in claim.get("primary_sources", []) if sid in sources]
        corroboration = [sources[sid] for sid in claim.get("corroboration_sources", []) if sid in sources]
        all_sources = primary + corroboration
        has_strong = any(s.get("type") in STRONG_SOURCE_TYPES for s in all_sources)
        has_caveat = (
            "caveat" in claim.get("notes", "").lower()
            or "indicative" in claim.get("notes", "").lower()
            or "weak" in claim.get("notes", "").lower()
        )
        if len(all_sources) >= 2:
            continue
        if has_strong:
            continue
        if has_caveat:
            continue
        numeric_violations.append(
            {
                "claim_id": cid,
                "violation": "numeric_claim_single_weak_source",
                "source_count": len(all_sources),
                "types": [s.get("type") for s in all_sources],
            }
        )
    gates["numeric_evidence_strength"] = {
        "status": "PASS" if not numeric_violations else "FAIL",
        "violations": numeric_violations,
    }
    violations.extend([{"gate": "numeric_evidence_strength", **v} for v in numeric_violations])

    # red_team_quality gate: check red_team_arguments schema completeness
    red_team_quality_violations = []
    rt_args = ledger.get("red_team_arguments", [])
    if rt_args:
        for rta in rt_args:
            if not rta.get("id"):
                red_team_quality_violations.append({"violation": "red_team_argument_missing_id"})
            if not rta.get("objection"):
                red_team_quality_violations.append(
                    {"violation": "red_team_argument_missing_objection", "id": rta.get("id")}
                )
            if not rta.get("response"):
                red_team_quality_violations.append(
                    {"violation": "red_team_argument_missing_response", "id": rta.get("id")}
                )
            if not rta.get("residual_risk"):
                red_team_quality_violations.append(
                    {"violation": "red_team_argument_missing_residual_risk", "id": rta.get("id")}
                )
    if not rt_args:
        red_team_quality_violations.append({"violation": "red_team_arguments_required"})
    elif len(rt_args) < 2:
        red_team_quality_violations.append(
            {"violation": "red_team_arguments_min_2", "found": len(rt_args)}
        )
    gates["red_team_quality"] = {
        "status": "PASS" if not red_team_quality_violations else "FAIL",
        "violations": red_team_quality_violations,
    }
    violations.extend([{"gate": "red_team_quality", **v} for v in red_team_quality_violations])

    # claim_grade_distribution gate: Decision-grade requires adequate A/B claims
    claim_dist_violations = []
    claim_grades = [c.get("grade", "C") for c in claims.values()]
    ab_count = sum(1 for g in claim_grades if g in ("A", "B"))
    c_count = sum(1 for g in claim_grades if g == "C")
    d_count = sum(1 for g in claim_grades if g == "D")
    f_count = sum(1 for g in claim_grades if g == "F")
    total_claims = len(claim_grades)
    combined_topic = topic + " " + scope
    is_decision_grade_rt = any(kw in combined_topic for kw in STRATEGIC_SCOPE_KEYWORDS | {"decision", "commercial"})
    is_decision_scope = is_decision_grade_rt or any(
        kw in combined_topic for kw in {"decision", "commercial", "strategic", "invest", "build", "buy", "adopt"}
    )

    if is_decision_scope and total_claims >= MIN_CLAIMS_FOR_CD_DOMINANCE:
        cd_total = c_count + d_count + f_count
        cd_ratio = cd_total / total_claims if total_claims > 0 else 0
        if ab_count == 0:
            claim_dist_violations.append(
                {
                    "violation": "zero_ab_claims_for_decision_grade",
                    "ab_count": ab_count,
                    "total_claims": total_claims,
                    "reason": "Decision-grade scope requires at least some A/B-grade claims; all claims are C/D/F",
                }
            )
        elif cd_ratio > CD_DOMINANCE_THRESHOLD:
            claim_dist_violations.append(
                {
                    "violation": "cd_claims_dominate_decision_grade",
                    "ab_count": ab_count,
                    "c_count": c_count,
                    "d_count": d_count,
                    "f_count": f_count,
                    "cd_ratio": round(cd_ratio, 3),
                    "threshold": CD_DOMINANCE_THRESHOLD,
                    "reason": f"C/D/F claims ({cd_total}/{total_claims} = {cd_ratio:.1%}) exceed {CD_DOMINANCE_THRESHOLD:.0%} threshold",
                }
            )
    elif is_decision_scope and total_claims > 0 and ab_count == 0:
        claim_dist_violations.append(
            {
                "violation": "zero_ab_claims_for_decision_grade",
                "ab_count": ab_count,
                "total_claims": total_claims,
                "reason": "Decision-grade scope requires at least some A/B-grade claims; no A/B claims found",
            }
        )
    gates["claim_grade_distribution"] = {
        "status": "PASS" if not claim_dist_violations else "FAIL",
        "violations": claim_dist_violations,
    }
    violations.extend([{"gate": "claim_grade_distribution", **v} for v in claim_dist_violations])

    # weak_claim_usage gate: D/F/unverified claims cannot support recommendations/red_team/core thesis
    weak_claim_violations = []
    rt_claim_ids = set()
    if rt_args:
        for rta in rt_args:
            for cid in rta.get("evidence_claim_ids", []):
                rt_claim_ids.add(cid)

    for cid, claim in claims.items():
        grade = claim.get("grade", "C")
        ver_status = claim.get("verification_status", "unverified")
        used_in = claim.get("used_in", [])
        notes_lower = claim.get("notes", "").lower()
        is_weak = grade in WEAK_CLAIM_GRADES or ver_status == "unverified"
        is_background = any(kw in notes_lower for kw in BACKGROUND_KEYWORDS)
        is_redteam = cid in rt_claim_ids

        if not is_weak:
            continue

        for usage in used_in:
            if usage in ("Recommendations", "ExecutiveAnswer"):
                if is_background and is_redteam:
                    continue
                weak_claim_violations.append(
                    {
                        "claim_id": cid,
                        "grade": grade,
                        "verification_status": ver_status,
                        "violation": "weak_claim_in_action_surface",
                        "usage": usage,
                        "reason": f"{grade}-grade/verification={ver_status} claim cannot support {usage} unless marked as background with caveat",
                    }
                )
            elif usage == "RedTeam" and not is_background:
                weak_claim_violations.append(
                    {
                        "claim_id": cid,
                        "grade": grade,
                        "verification_status": ver_status,
                        "violation": "weak_claim_in_redteam_without_caveat",
                        "usage": usage,
                        "reason": f"{grade}-grade/verification={ver_status} claim in RedTeam requires background/caveat marker",
                    }
                )
    gates["weak_claim_usage"] = {
        "status": "PASS" if not weak_claim_violations else "FAIL",
        "violations": weak_claim_violations,
    }
    violations.extend([{"gate": "weak_claim_usage", **v} for v in weak_claim_violations])

    # commercial_source_diversity gate: commercial reports need diverse source types
    commercial_gate_violations = []
    is_commercial_scope = any(kw in combined_topic for kw in COMMERCIAL_SCOPE_KEYWORDS)

    if is_commercial_scope and sources:
        numeric_claims_list = [
            (cid, c)
            for cid, c in claims.items()
            if c.get("numeric")
            and ("Recommendations" in c.get("used_in", []) or "ExecutiveAnswer" in c.get("used_in", []))
        ]
        if numeric_claims_list:
            supplier_only_numeric = 0
            diverse_numeric = 0
            for cid, c in numeric_claims_list:
                claim_sources = [sources.get(sid) for sid in c.get("primary_sources", []) if sid in sources]
                claim_sources += [sources.get(sid) for sid in c.get("corroboration_sources", []) if sid in sources]
                source_types = set(s.get("type", "") for s in claim_sources if s)
                has_strong = bool(source_types & STRONG_COMMERCIAL_SOURCE_TYPES)
                has_supplier_only = source_types.issubset(SUPPLIER_ONLY_TYPES) if source_types else True
                if has_supplier_only or not has_strong:
                    supplier_only_numeric += 1
                else:
                    diverse_numeric += 1

            total_numeric = supplier_only_numeric + diverse_numeric
            if supplier_only_numeric > 0 and diverse_numeric == 0:
                commercial_gate_violations.append(
                    {
                        "violation": "all_numeric_claims_supplier_only",
                        "supplier_only_count": supplier_only_numeric,
                        "diverse_count": diverse_numeric,
                        "reason": "All key numeric commercial claims rely on supplier/vendor/creator sources with no official/data/user-demand diversity",
                    }
                )
            elif supplier_only_numeric > 0 and supplier_only_numeric / max(total_numeric, 1) > 0.5:
                commercial_gate_violations.append(
                    {
                        "violation": "majority_numeric_claims_supplier_only",
                        "supplier_only_count": supplier_only_numeric,
                        "diverse_count": diverse_numeric,
                        "ratio": round(supplier_only_numeric / max(total_numeric, 1), 3),
                        "reason": "Majority of key numeric commercial claims rely on weak supplier sources",
                    }
                )

        source_type_counts = {"strong": 0, "weak": 0}
        for src in sources.values():
            if src.get("type") in STRONG_COMMERCIAL_SOURCE_TYPES:
                source_type_counts["strong"] += 1
            elif src.get("type") in SUPPLIER_ONLY_TYPES:
                source_type_counts["weak"] += 1
        total_sources = source_type_counts["strong"] + source_type_counts["weak"]
        if total_sources > 0 and source_type_counts["weak"] / total_sources > 0.8:
            if not commercial_gate_violations:
                commercial_gate_violations.append(
                    {
                        "violation": "commercial_sources_overwhelmingly_supplier",
                        "strong_count": source_type_counts["strong"],
                        "weak_count": source_type_counts["weak"],
                        "weak_ratio": round(source_type_counts["weak"] / total_sources, 3),
                        "reason": "Commercial scope has >80% supplier/vendor/creator sources, no official/data diversity",
                    }
                )
    gates["commercial_source_diversity"] = {
        "status": "PASS" if not commercial_gate_violations else "FAIL",
        "violations": commercial_gate_violations,
    }
    violations.extend([{"gate": "commercial_source_diversity", **v} for v in commercial_gate_violations])

    # vendor_bias gate: detect when competitive claims rely solely on vendor sources
    vendor_bias_violations = []
    for cid, claim in claims.items():
        if claim.get("grade") not in ("A", "B"):
            continue
        if "Recommendations" not in claim.get("used_in", []) and "ExecutiveAnswer" not in claim.get("used_in", []):
            continue
        primary = [sources[sid] for sid in claim.get("primary_sources", []) if sid in sources]
        if not primary:
            continue
        # Check if all primary sources for a competitive claim are vendor/company blogs
        all_vendor = all(s.get("publisher_type") in ("company",) and s.get("type") == "T2_Creator" for s in primary)
        corroboration = [sources[sid] for sid in claim.get("corroboration_sources", []) if sid in sources]
        has_independent_corroboration = any(
            s.get("publisher_type") not in ("company",) or s.get("type") != "T2_Creator" for s in corroboration
        )
        if all_vendor and not has_independent_corroboration:
            # Check if this claim makes comparative assertions (contains competitor-like language)
            claim_text = (claim.get("claim") or "").lower()
            has_comparison = any(
                kw in claim_text
                for kw in (
                    "faster",
                    "slower",
                    "better",
                    "worse",
                    "superior",
                    "inferior",
                    "outperform",
                    "cheaper",
                    "more expensive",
                    "recommended over",
                    "preferred",
                    "versus",
                    "vs",
                    "比",
                    "优于",
                    "超过",
                    "更快",
                    "更便宜",
                )
            )
            if has_comparison:
                vendor_bias_violations.append(
                    {
                        "claim_id": cid,
                        "violation": "competitive_claim_vendor_only",
                        "primary_publisher_types": [s.get("publisher_type") for s in primary],
                        "reason": "Competitive/comparative claim relies solely on vendor sources without independent corroboration",
                    }
                )
    gates["vendor_bias"] = {
        "status": "PASS" if not vendor_bias_violations else "FAIL",
        "violations": vendor_bias_violations,
    }
    violations.extend([{"gate": "vendor_bias", **v} for v in vendor_bias_violations])

    # source_diversity gate: ensure cross-tier evidence
    source_diversity_violations = []
    tier_types_found = set(s.get("type", "") for s in sources.values() if s.get("type"))
    if len(tier_types_found) < 3:
        source_diversity_violations.append(
            {
                "violation": "insufficient_source_tier_diversity",
                "tiers_found": sorted(tier_types_found),
                "tiers_needed": 3,
                "suggestion": "Include sources from at least 3 different tiers (e.g., T1_Academic + T2_Data + T3_Synthesis)",
            }
        )
    gates["source_diversity"] = {
        "status": "PASS" if not source_diversity_violations else "FAIL",
        "violations": source_diversity_violations,
    }
    violations.extend([{"gate": "source_diversity", **v} for v in source_diversity_violations])

    # cross_validation gate: numeric claims used in recommendations need corroboration
    cross_val_violations = []
    for cid, claim in claims.items():
        if not claim.get("numeric"):
            continue
        if "Recommendations" not in claim.get("used_in", []) and "ExecutiveAnswer" not in claim.get("used_in", []):
            continue
        primary = [sources[sid] for sid in claim.get("primary_sources", []) if sid in sources]
        corroboration = [sources[sid] for sid in claim.get("corroboration_sources", []) if sid in sources]
        # T1 primary counts as independently verified
        has_t1_primary = any(s.get("type", "").startswith("T1") for s in primary)
        if has_t1_primary:
            continue
        # Need at least 1 corroboration source or 2+ primary sources from different domains
        if corroboration:
            continue
        if len(primary) >= 2:
            domains = set(s.get("url_domain", "") for s in primary if s.get("url_domain"))
            if len(domains) >= 2:
                continue
        cross_val_violations.append(
            {
                "claim_id": cid,
                "violation": "numeric_claim_uncorroborated",
                "primary_count": len(primary),
                "corroboration_count": len(corroboration),
                "reason": "Numeric claim used in recommendations lacks independent corroboration from different source domains",
            }
        )
    for cid, claim in claims.items():
        if not claim.get("numeric"):
            continue
        if "Recommendations" not in claim.get("used_in", []) and "ExecutiveAnswer" not in claim.get("used_in", []):
            continue
        variance_issue = _check_numeric_variance(claim)
        if variance_issue:
            variance_issue["claim_id"] = cid
            cross_val_violations.append(variance_issue)
    gates["cross_validation"] = {
        "status": "PASS" if not cross_val_violations else "FAIL",
        "violations": cross_val_violations,
    }
    violations.extend([{"gate": "cross_validation", **v} for v in cross_val_violations])

    # hypothesis_tracking gate
    hypothesis_tracking_violations = []
    hypotheses = ledger.get("hypotheses", {})
    if hypotheses:
        has_confirmed_or_falsified = any(h.get("status") in ("confirmed", "falsified") for h in hypotheses.values())
        if not has_confirmed_or_falsified:
            hypothesis_tracking_violations.append({
                "violation": "all_hypotheses_still_testing",
                "reason": "Hypotheses exist but none have status confirmed or falsified; all are still testing"
            })
        for hid, hyp in hypotheses.items():
            if hyp.get("status") == "confirmed" and hyp.get("confidence", 0) < 50:
                hypothesis_tracking_violations.append({
                    "hypothesis_id": hid,
                    "violation": "confirmed_hypothesis_low_confidence",
                    "confidence": hyp.get("confidence"),
                    "reason": "Confirmed hypothesis has confidence below 50%"
                })
            if not hyp.get("trigger_claim_ids"):
                hypothesis_tracking_violations.append({
                    "hypothesis_id": hid,
                    "violation": "hypothesis_missing_trigger_claims",
                    "reason": "Hypothesis has no trigger_claim_ids"
                })
    gates["hypothesis_tracking"] = {
        "status": "PASS" if not hypothesis_tracking_violations else "FAIL",
        "violations": hypothesis_tracking_violations,
    }
    violations.extend([{"gate": "hypothesis_tracking", **v} for v in hypothesis_tracking_violations])

    # --- Helper: check if a dimension is covered in narrative text ---
    def _check_dimension(dim: str, narrative_text: str) -> bool:
        """Check if a dimension is covered in narrative text.

        For standard dimensions (in DIMENSION_ZH_KEYWORDS), use the keyword list.
        For custom Chinese dimensions, split into 2+ character substrings and check those.
        """
        # 1. Check standard dimension keywords
        zh_keywords = DIMENSION_ZH_KEYWORDS.get(dim, [])
        if any(kw in narrative_text for kw in zh_keywords):
            return True
        # 2. Check English parts (split by underscore)
        dim_parts = dim.replace("_", " ").split()
        if any(part in narrative_text for part in dim_parts):
            return True
        # 3. For custom Chinese dimensions not in DIMENSION_ZH_KEYWORDS:
        #    split into 2+ character substrings and check those
        if not zh_keywords and not any(c.isascii() for c in dim):
            # Chinese compound word — split into overlapping 2-char chunks
            for i in range(len(dim) - 1):
                chunk = dim[i:i+2]
                if chunk in narrative_text:
                    return True
        return False

    def _get_dimension_hints(dim: str) -> list:
        """Get hint keywords for a dimension."""
        kw = DIMENSION_ZH_KEYWORDS.get(dim, [])
        if kw:
            return kw[:8]
        # For custom Chinese dimensions, return the 2-char chunks as hints
        if not any(c.isascii() for c in dim):
            return [dim[i:i+2] for i in range(len(dim) - 1)]
        return [dim.replace("_", " ")]

    # task_type_framework gate
    task_type_framework_violations = []
    narrative = ledger.get("report_config", {}).get("narrative_sections", {})
    task_type = ledger.get("task_type", "")
    agent_dimensions = [d for d in ledger.get("dimensions", []) if isinstance(d, str) and d.strip()]

    if agent_dimensions:
        # Agent declared dimensions — use them directly
        if len(agent_dimensions) < 3:
            task_type_framework_violations.append({
                "violation": "insufficient_dimensions",
                "found": len(agent_dimensions),
                "required": 3,
                "reason": f"At least 3 dimensions required, found {len(agent_dimensions)}"
            })
        else:
            all_narrative_text = " ".join(narrative.get(s, "") for s in narrative).lower()
            missing_dimensions = []
            for dim in agent_dimensions:
                if not _check_dimension(dim, all_narrative_text):
                    missing_dimensions.append(dim)
            if missing_dimensions:
                dim_hints = {dim: _get_dimension_hints(dim) for dim in missing_dimensions}
                task_type_framework_violations.append({
                    "violation": "task_type_dimensions_not_covered",
                    "task_type": task_type or "custom",
                    "missing_dimensions": missing_dimensions,
                    "required_dimensions": agent_dimensions,
                    "reason": f"Research requires coverage of: {', '.join(missing_dimensions)}",
                    "hint": {dim: f"Include keywords like: {', '.join(kws)}" for dim, kws in dim_hints.items()},
                })
    elif task_type and task_type in TASK_TYPE_FRAMEWORKS:
        # Fall back to TASK_TYPE_FRAMEWORKS for backward compatibility
        framework = TASK_TYPE_FRAMEWORKS[task_type]
        all_narrative_text = " ".join(narrative.get(s, "") for s in narrative).lower()
        missing_dimensions = []
        for dim in framework.get("dimensions", []):
            if not _check_dimension(dim, all_narrative_text):
                missing_dimensions.append(dim)
        if missing_dimensions:
            dim_hints = {dim: _get_dimension_hints(dim) for dim in missing_dimensions}
            task_type_framework_violations.append({
                "violation": "task_type_dimensions_not_covered",
                "task_type": task_type,
                "missing_dimensions": missing_dimensions,
                "required_dimensions": framework["dimensions"],
                "reason": f"Task type '{task_type}' framework requires coverage of: {', '.join(missing_dimensions)}",
                "hint": {dim: f"Include keywords like: {', '.join(kws)}" for dim, kws in dim_hints.items()},
            })
        min_sources = framework.get("min_sources", 5)
        if len(sources) < min_sources:
            task_type_framework_violations.append({
                "violation": "task_type_insufficient_sources",
                "task_type": task_type,
                "found": len(sources),
                "required": min_sources,
                "reason": f"Task type '{task_type}' requires at least {min_sources} sources, found {len(sources)}"
            })
    gates["task_type_framework"] = {
        "status": "PASS" if not task_type_framework_violations else "FAIL",
        "violations": task_type_framework_violations,
        "task_type": task_type,
        "dimensions": agent_dimensions,
    }
    violations.extend([{"gate": "task_type_framework", **v} for v in task_type_framework_violations])

    # status
    scope_fidelity_fail = bool(scope_fidelity_violations)
    rec_actor_fail = bool(rec_actor_violations)
    source_dom_warning = bool(source_dom_violations)
    claim_dist_fail = bool(claim_dist_violations)
    weak_claim_fail = bool(weak_claim_violations)
    commercial_gate_fail = bool(commercial_gate_violations)

    if access_trace_violations:
        report_status = "Draft — requires source repair"
    elif claim_violations or rec_violations or closure_violations:
        report_status = "Draft — ledger inconsistent"
    elif subquestion_coverage_violations or prompt_item_coverage_violations or claim_subquestion_trace_violations:
        report_status = "Draft — coverage incomplete"
    elif scope_fidelity_fail:
        report_status = "Partial — runtime topic drifted to training-stage conclusions"
    elif rec_actor_fail:
        report_status = "Partial — recommendation actor scope mismatch"
    elif claim_dist_fail:
        report_status = "Partial — insufficient A/B-grade claims for decision-grade"
    elif weak_claim_fail:
        report_status = "Partial — weak claims used in action surfaces"
    elif commercial_gate_fail:
        report_status = "Partial — commercial evidence relies on supplier-only sources"
    elif ratio_status == "FAIL":
        has_advisory = any(rec.get("type") == "advisory" for rec in recommendations.values())
        report_status = (
            "Advisory Research — evidence below decision threshold" if has_advisory else "Evidence Gap Report"
        )
    elif source_dom_warning:
        report_status = "Decision-grade (with source dominance warning)"
    else:
        report_status = "Decision-grade"
    confidence = "Medium" if report_status == "Decision-grade" else "Low"
    return {
        "status": "PASS" if not violations else "FAIL",
        "report_status": report_status,
        "use_without_rereading_confidence": confidence,
        "gates": gates,
        "violations": violations,
        "verified_at": _now(),
    }


def cmd_verify(args):
    ledger = _load_ledger(args.topic)
    # Allow task-type override at verify time
    if getattr(args, "task_type", None):
        ledger["task_type"] = args.task_type
    verification = _verify_ledger(ledger, args.dynamic_threshold)
    ledger["verification"] = verification
    _save_ledger(args.topic, ledger)
    # Add provenance to output
    report_config = ledger.get("report_config", {})
    provenance = {
        "created_cwd": report_config.get("created_cwd"),
        "storage_dir": report_config.get("storage_dir"),
    }
    output = {**verification, **provenance}
    print(json.dumps(output, ensure_ascii=False, indent=2))
    if verification["status"] == "FAIL" and args.strict:
        sys.exit(1)


def _trust_badge_markdown(ledger: dict) -> str:
    verification = ledger.get("verification", {})
    ratio = verification.get("gates", {}).get("t1t2_ratio", {})
    report_status = verification.get("report_status", "Draft — ledger unverified")
    conf = verification.get("use_without_rereading_confidence", "Low")
    if not ratio:
        ratio_text = "NOT VERIFIED"
    elif ratio.get("denominator"):
        ratio_text = f"{ratio.get('numerator')}/{ratio.get('denominator')} = {ratio.get('ratio') * 100:.1f}%"
    else:
        ratio_text = "NOT VERIFIED"

    sources = ledger.get("sources", {})
    claims = ledger.get("claims", {})
    source_type_counts = {"T1": 0, "T2": 0, "T3": 0, "T4": 0, "T5": 0}
    for src in sources.values():
        stype = src.get("type", "")
        if stype.startswith("T1"):
            source_type_counts["T1"] += 1
        elif stype.startswith("T2"):
            source_type_counts["T2"] += 1
        elif stype.startswith("T3"):
            source_type_counts["T3"] += 1
        elif stype.startswith("T4"):
            source_type_counts["T4"] += 1
        elif stype.startswith("T5"):
            source_type_counts["T5"] += 1
    grade_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for claim in claims.values():
        grade = claim.get("grade", "C")
        if grade in grade_counts:
            grade_counts[grade] += 1

    ab_count = grade_counts["A"] + grade_counts["B"]
    cd_count = grade_counts["C"] + grade_counts["D"] + grade_counts["F"]
    total_claims = ab_count + cd_count
    ab_ratio = ab_count / total_claims if total_claims > 0 else 0
    weak_evidence_warning = ""
    if cd_count > 0 and ab_count == 0:
        weak_evidence_warning = (
            "WARNING: No A/B-grade claims; all claims are C/D/F grade. Evidence is weak for decision support."
        )
    elif cd_count > ab_count:
        weak_evidence_warning = f"WARNING: C/D/F claims ({cd_count}) exceed A/B claims ({ab_count}). Evidence may be insufficient for strong recommendations."

    lines = [
        "## Trust Badge (generated from ledger)",
        f"- Report status: {report_status}",
        f"- T1/T2 ratio: {ratio_text}",
        f"- Threshold: {ratio.get('threshold_name', 'unknown')} ({ratio.get('threshold', 'unknown')})",
        f"- Use-without-rereading-sources confidence: {conf}",
        "",
        "### Evidence Mix Summary",
        f"- Source tier distribution: T1={source_type_counts['T1']}, T2={source_type_counts['T2']}, T3={source_type_counts['T3']}, T4={source_type_counts['T4']}, T5={source_type_counts['T5']}",
        f"- Claim grade distribution: A={grade_counts['A']}, B={grade_counts['B']}, C={grade_counts['C']}, D={grade_counts['D']}, F={grade_counts['F']}",
        f"- A/B claim ratio: {ab_count}/{total_claims} = {ab_ratio:.1%}",
    ]
    if weak_evidence_warning:
        lines.append(f"- **⚠️ {weak_evidence_warning}**")
    lines.extend(
        [
            "",
            "### Trust Badge Source Count Table",
            "| Source ID | Type | Access status | Trace status | Count in numerator? | Reason |",
            "|---|---|---|---|---|---|",
        ]
    )
    numerator_set = set(ratio.get("numerator_sources", [])) if ratio else set()
    for sid, src in sorted(sources.items()):
        count = "yes" if sid in numerator_set else "no"
        reason = (
            "T1/T2 + original/traced + publisher/domain valid"
            if count == "yes"
            else f"type={src.get('type')}, trace={src.get('trace_status')}, publisher={src.get('publisher_type')}, domain={src.get('url_domain')}"
        )
        lines.append(
            f"| {sid} | {src.get('type')} | {src.get('access_status')} | {src.get('trace_status')} | {count} | {reason} |"
        )
    if verification.get("violations"):
        lines.extend(["", "### Verification Violations"])
        for v in verification["violations"]:
            lines.append(f"- `{v.get('gate')}`: {json.dumps(v, ensure_ascii=False)}")
    return "\n".join(lines)


def _sources_markdown(ledger: dict) -> str:
    lines = [
        "## Sources (generated from ledger)",
        "<!-- GENERATED: sources -->",
        "| Source ID | Type | Title | Publisher | Domain | Access | Trace | Used for |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for sid, src in sorted(ledger.get("sources", {}).items()):
        title = src.get("title", "").replace("|", "\\|")
        publisher = src.get("publisher") or src.get("publisher_type") or "unknown"
        url = src.get("url") or src.get("citation") or ""
        title_text = f"[{title}]({url})" if url and url.startswith(("http://", "https://")) else title
        lines.append(
            f"| {sid} | {src.get('type')} | {title_text} | {publisher} | {src.get('url_domain', '')} | "
            f"{src.get('access_status')} | {src.get('trace_status')} | {', '.join(src.get('used_for', [])) or '-'} |"
        )
    return "\n".join(lines)


def _question_coverage_table_markdown(ledger: dict) -> str:
    subquestions = ledger.get("subquestions", {})
    modules = ledger.get("modules", {})
    if not subquestions:
        return ""
    lines = [
        "## Question Coverage Table (generated from ledger)",
        "<!-- GENERATED: question-coverage-table -->",
        "| ID | Priority | Status | Answered By | Gap Note | Loop Action |",
        "|---|---|---|---|---|---|",
    ]
    for sid, sq in sorted(subquestions.items()):
        answered_by = ", ".join(sq.get("answered_by", [])) or "-"
        gap_note = sq.get("gap_note", "")
        if gap_note:
            gap_note = gap_note[:50] + ("..." if len(gap_note) > 50 else "")
        loop_action = sq.get("loop_action", "none")
        lines.append(
            f"| {sid} | {sq.get('priority', 'medium')} | {sq.get('status', 'unanswered')} | "
            f"{answered_by} | {gap_note} | {loop_action} |"
        )
    lines.append("")
    for mid, mod in sorted(modules.items()):
        subq_id = mod.get("subquestion_id", "")
        title = mod.get("title", mid)
        lines.append(f"### Module: {title}")
        content = mod.get("content", "")
        status = mod.get("status", "partial")
        claim_ids = ", ".join(mod.get("claim_ids", [])) or "-"
        lines.append(f"- Status: {status} | Subquestion: {subq_id} | Claims: {claim_ids}")
        if content:
            lines.extend(["", content, ""])
    return "\n".join(lines)


def _prompt_item_coverage_table_markdown(ledger: dict) -> str:
    prompt_items = ledger.get("prompt_items", {})
    if not prompt_items:
        return ""
    lines = [
        "## Prompt Item Coverage Table (generated from ledger)",
        "<!-- GENERATED: prompt-item-coverage-table -->",
        "| ID | Priority | Status | Mapped Subquestions | Gap Note |",
        "|---|---|---|---|---|",
    ]
    for pid, pi in sorted(prompt_items.items()):
        mapped = ", ".join(pi.get("mapped_subquestions", [])) or "-"
        gap_note = pi.get("gap_note", "")
        if gap_note:
            gap_note = gap_note[:50] + ("..." if len(gap_note) > 50 else "")
        lines.append(
            f"| {pid} | {pi.get('priority', 'medium')} | {pi.get('status', 'unmapped')} | " f"{mapped} | {gap_note} |"
        )
    return "\n".join(lines)


def _modules_markdown(ledger: dict) -> str:
    modules = ledger.get("modules", {})
    subquestions = ledger.get("subquestions", {})
    if not modules:
        return ""
    lines = [
        "## Modules (generated from ledger)",
        "<!-- GENERATED: modules -->",
        "",
    ]
    for mid, mod in sorted(modules.items()):
        subq_id = mod.get("subquestion_id", "")
        title = mod.get("title", mid)
        status = mod.get("status", "partial")
        claim_ids = ", ".join(mod.get("claim_ids", [])) or "-"
        subq_ref = subquestions.get(subq_id, {})
        subq_question = subq_ref.get("question", "") if subq_ref else ""
        lines.append(f"### Module: {title}")
        lines.append(f"**Subquestion:** {subq_question}  ")
        lines.append(f"**Status:** {status} | **Subquestion ID:** {subq_id} | **Claims:** {claim_ids}")
        content = mod.get("content", "")
        if content:
            lines.extend(["", content, ""])
        lines.append("")
    return "\n".join(lines)


def _hypotheses_markdown(ledger: dict) -> str:
    hypotheses = ledger.get("hypotheses", {})
    if not hypotheses:
        return ""
    lines = [
        "## Hypotheses (generated from ledger)",
        "<!-- GENERATED: hypotheses -->",
        "| ID | Status | Confidence | Mutation Trigger | Trigger Claims | Notes |",
        "|---|---|---|---|---|---|",
    ]
    for hid, hyp in sorted(hypotheses.items()):
        notes = hyp.get("notes", "").replace("|", "\\|")
        if len(notes) > 50:
            notes = notes[:50] + "..."
        lines.append(
            f"| {hid} | {hyp.get('status', 'testing')} | {hyp.get('confidence', 0)}% | "
            f"{hyp.get('mutation_trigger', '-')} | {', '.join(hyp.get('trigger_claim_ids', [])) or '-'} | {notes} |"
        )
    return "\n".join(lines)


def _evidence_markdown(ledger: dict) -> str:
    lines = [
        "## Evidence Ledger (generated from ledger)",
        "<!-- GENERATED: evidence-ledger -->",
        "| Claim ID | Grade | Confidence | Numeric | Primary sources | Corroboration | Verification | Claim |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for cid, claim in sorted(ledger.get("claims", {}).items()):
        text = claim.get("claim", "").replace("|", "\\|")
        lines.append(
            f"| {cid} | {claim.get('grade')} | {claim.get('confidence')} | {'yes' if claim.get('numeric') else 'no'} | "
            f"{', '.join(claim.get('primary_sources', [])) or '-'} | {', '.join(claim.get('corroboration_sources', [])) or '-'} | "
            f"{claim.get('verification_status')} | {text} |"
        )
    return "\n".join(lines)


def _recommendations_trace_markdown(ledger: dict) -> str:
    lines = [
        "## Recommendation Trace (generated from ledger)",
        "<!-- GENERATED: recommendation-trace -->",
        "| Rec ID | Type | Claim IDs | Text |",
        "|---|---|---|---|",
    ]
    for rid, rec in sorted(ledger.get("recommendations", {}).items()):
        text = rec.get("text", "").replace("|", "\\|")
        lines.append(f"| {rid} | {rec.get('type')} | {', '.join(rec.get('claim_ids', [])) or '-'} | {text} |")
    return "\n".join(lines)


def _closure_searches_markdown(ledger: dict) -> str:
    closure_searches = ledger.get("closure_searches", {})
    verification = ledger.get("verification", {})
    closure_gate = verification.get("gates", {}).get("research_closure", {})
    lines = [
        "## Research Closure (generated from ledger)",
        "<!-- GENERATED: research-closure -->",
        f"- Closure search count: {len(closure_searches)}",
        f"- Minimum required: {closure_gate.get('minimum_required', 'unknown')}",
        f"- Strategic scope: {closure_gate.get('is_strategic_scope', False)}",
        "",
        "| ID | Trigger | Search Direction | Perspective | Source IDs | Effect | New Evidence |",
        "|---|---|---|---|---|---|---|",
    ]
    for csid, cs in sorted(closure_searches.items()):
        trigger = cs.get("trigger", "").replace("|", "\\|")
        evidence = cs.get("new_evidence", "").replace("|", "\\|")
        lines.append(
            f"| {csid} | {trigger} | {cs.get('search_direction', '')} | {cs.get('perspective', '')} | "
            f"{', '.join(cs.get('source_ids', [])) or '-'} | {cs.get('effect_on_conclusion', '')} | {evidence} |"
        )
    return "\n".join(lines)


def _verification_markdown(ledger: dict) -> str:
    verification = ledger.get("verification", {})
    lines = [
        "## Verification Gates (generated from ledger)",
        "<!-- GENERATED: verification-gates -->",
        f"- Verify status: {verification.get('status', 'NOT_RUN')}",
        f"- Report status: {verification.get('report_status', 'Draft — ledger unverified')}",
        f"- Verified at: {verification.get('verified_at', 'not verified')}",
        "",
        "| Gate | Status | Violation count |",
        "|---|---|---|",
    ]
    for gate, data in sorted(verification.get("gates", {}).items()):
        lines.append(f"| {gate} | {data.get('status')} | {len(data.get('violations', []))} |")
    if verification.get("violations"):
        lines.extend(["", "### Raw violations"])
        lines.append("```json")
        lines.append(json.dumps(verification.get("violations", []), ensure_ascii=False, indent=2))
        lines.append("```")
    return "\n".join(lines)


def _generated_report_markdown(ledger: dict) -> str:
    narrative = ledger.get("report_config", {}).get("narrative_sections", {})
    report_hash = _ledger_hash(ledger)
    lines = [
        f"# Research: {ledger.get('topic')}",
        f"<!-- GENERATED_REPORT: true -->",
        f"<!-- LEDGER_HASH: {report_hash} -->",
        f"<!-- GENERATED_AT: {_now()} -->",
        "",
    ]
    # Narrative sections first (reader-centric order: Executive Summary → Background → Methodology → Findings → Insights → Recommendations → Risk → Roadmap → Gaps)
    for key, heading in NARRATIVE_SECTIONS.items():
        content = narrative.get(key, "_(not supplied)_")
        # Normalize literal \n strings (from batch JSON) to actual newlines
        if isinstance(content, str):
            content = content.replace("\\n", "\n")
            # Strip ALL ## level headings from narrative content (script generates them)
            # Agent should only write ### and lower level headings
            lines_content = content.split("\n")
            filtered = [l for l in lines_content if not l.strip().startswith("## ")]
            content = "\n".join(filtered).strip()
        lines.extend([f"## {heading}", content, ""])
    # Appendix: generated artifacts (Trust Badge, Evidence, Sources, Verification)
    lines.extend([
        "## Appendix",
        "",
        "### Trust Badge",
        "",
        _trust_badge_markdown(ledger),
        "",
        "### Evidence Ledger",
        "",
        _evidence_markdown(ledger),
        "",
        "### Hypotheses",
        "",
        _hypotheses_markdown(ledger),
        "",
        "### Recommendations Trace",
        "",
        _recommendations_trace_markdown(ledger),
        "",
        "### Sources",
        "",
        _sources_markdown(ledger),
        "",
        "### Closure Searches",
        "",
        _closure_searches_markdown(ledger),
        "",
        "### Verification Gates",
        "",
        _verification_markdown(ledger),
        "",
        "### Coverage",
        "",
        _question_coverage_table_markdown(ledger),
        "",
        _prompt_item_coverage_table_markdown(ledger),
        "",
        _modules_markdown(ledger),
        "",
    ])
    return "\n".join(lines)


def cmd_trust_badge(args):
    ledger = _load_ledger(args.topic)
    if getattr(args, "task_type", None):
        ledger["task_type"] = args.task_type
    if ledger.get("verification", {}).get("status") == "NOT_RUN":
        verification = _verify_ledger(ledger, args.dynamic_threshold)
        ledger["verification"] = verification
        _save_ledger(args.topic, ledger)
    elif args.dynamic_threshold:
        existing = ledger.get("verification", {}).get("gates", {}).get("t1t2_ratio", {}).get("threshold_name")
        if existing and existing != args.dynamic_threshold:
            print(
                f"Error: existing verification used threshold '{existing}', but trust-badge requested '{args.dynamic_threshold}'. Re-run verify with the intended threshold first.",
                file=sys.stderr,
            )
            sys.exit(1)
    print(_trust_badge_markdown(ledger))


def cmd_update_narrative(args):
    if args.section not in NARRATIVE_SECTIONS:
        print(f"Error: invalid narrative section {args.section}", file=sys.stderr)
        sys.exit(1)
    content = args.content
    if not content and args.content_file:
        with open(args.content_file, "r", encoding="utf-8") as f:
            content = f.read()
    if not content:
        print("Error: --content or --content-file required", file=sys.stderr)
        sys.exit(1)
    ledger = _load_ledger(args.topic)
    ledger.setdefault("report_config", {}).setdefault("narrative_sections", {})[args.section] = content
    _save_ledger(args.topic, ledger)
    print(f"Updated narrative section {args.section}")


def cmd_generate_report(args):
    ledger = _load_ledger(args.topic)
    # Allow task-type override at report generation time
    if getattr(args, "task_type", None):
        ledger["task_type"] = args.task_type
    verification = _verify_ledger(ledger, args.dynamic_threshold)
    # Preserve failure fields added by _load_ledger
    for f in ("failure_status", "failure_reason", "failure_stage"):
        if f in ledger.get("verification", {}):
            verification[f] = ledger["verification"][f]
    ledger["verification"] = verification
    _save_ledger(args.topic, ledger)
    if verification["status"] == "FAIL":
        if getattr(args, 'fail_on_violations', False):
            print(json.dumps({"status": "FAIL", "verification": verification}, indent=2, ensure_ascii=False))
            sys.exit(1)
        else:
            print(json.dumps(verification, ensure_ascii=False, indent=2), file=sys.stderr)
            print("Warning: verification failed; generating report anyway.", file=sys.stderr)
    output = args.output or _final_report_filepath(args.topic)
    content = _generated_report_markdown(ledger)
    with open(output, "w", encoding="utf-8") as f:
        f.write(content)
    ledger.setdefault("report_config", {})["last_generated_at"] = _now()
    ledger["report_config"]["generation_hash"] = _ledger_hash(ledger)
    ledger["report_config"]["generated_report_path"] = output
    _save_ledger(args.topic, ledger)
    print(f"Generated report: {output}")
    print(f"Ledger: {_ledger_filepath(args.topic)}")
    print(f"Generation hash: {ledger['report_config']['generation_hash']}")


def _advisory_report_markdown(ledger: dict) -> str:
    narrative = ledger.get("report_config", {}).get("narrative_sections", {})
    report_hash = _ledger_hash(ledger)
    verification = ledger.get("verification", {})
    report_status = verification.get("report_status", "Advisory Research")
    failed_gates = [
        gname
        for gname, gdata in verification.get("gates", {}).items()
        if gdata.get("status") in ("FAIL", "WARNING") and gname not in SKIPPED_GATES
    ]
    failure_summary = ", ".join(failed_gates) if failed_gates else "unknown evidence threshold"

    # Build dynamic executive summary based on specific failures
    exec_lines = [
        "This advisory report was generated because verification failed due to:",
    ]
    if "t1t2_ratio" in failed_gates:
        ratio_data = verification.get("gates", {}).get("t1t2_ratio", {})
        exec_lines.append(
            f"- **Insufficient high-quality sources**: T1/T2 ratio {ratio_data.get('ratio', 0):.0%} (requires ≥50%)"
        )
    if "claim_grade_distribution" in failed_gates:
        cd_data = verification.get("gates", {}).get("claim_grade_distribution", {})
        cd_violations = cd_data.get("violations", [])
        if cd_violations:
            v = cd_violations[0]
            exec_lines.append(f"- **Weak claim evidence**: {v.get('reason', 'C/D/F claims dominate')}")
    if "commercial_source_diversity" in failed_gates:
        comm_data = verification.get("gates", {}).get("commercial_source_diversity", {})
        comm_violations = comm_data.get("violations", [])
        if comm_violations:
            v = comm_violations[0]
            exec_lines.append(
                f"- **Supplier-dominated sources**: {v.get('reason', 'Commercial sources lack diversity')}"
            )
    if "numeric_evidence_strength" in failed_gates:
        exec_lines.append("- **Weak numeric evidence**: Key numeric claims lack corroboration from strong sources")
    if "cross_validation" in failed_gates:
        exec_lines.append("- **Insufficient cross-validation**: Numeric claims lack independent corroboration")
    if not any(
        k in failed_gates
        for k in (
            "t1t2_ratio",
            "claim_grade_distribution",
            "commercial_source_diversity",
            "numeric_evidence_strength",
            "cross_validation",
        )
    ):
        exec_lines.append(f"- Evidence threshold failures: {failure_summary}")
    exec_lines.extend(
        [
            "",
            "**DO NOT use this report for go/no-go decisions.** All conclusions are directional and require independent validation.",
            "Recommendations below are validation/exploration actions only — not decision-grade guidance.",
            "",
        ]
    )

    lines = [
        f"# Advisory Research Report: {ledger.get('topic')}",
        f"<!-- ADVISORY_REPORT: true -->",
        f"<!-- LEDGER_HASH: {report_hash} -->",
        f"<!-- GENERATED_AT: {_now()} -->",
        f"<!-- STATUS: NON-FINAL — ADVISORY ONLY -->",
        "",
        "## ⚠️ ADVISORY REPORT — NOT FINAL — DO NOT DECIDE BASED ON THIS REPORT",
        "This report was generated because verification failed due to evidence threshold.",
        "It is NOT a decision-grade report. Treat all conclusions as hypotheses requiring validation.",
        "",
        _trust_badge_markdown(ledger),
        "",
    ]
    lines.extend(exec_lines)

    for key, heading in NARRATIVE_SECTIONS.items():
        content_val = narrative.get(key, "_(not supplied)_")
        if isinstance(content_val, str):
            content_val = content_val.replace("\\n", "\n")
            # Strip ALL ## level headings from narrative content (script generates them)
            lines_content = content_val.split("\n")
            filtered = [l for l in lines_content if not l.strip().startswith("## ")]
            content_val = "\n".join(filtered).strip()
        lines.extend([f"## {heading}", content_val, ""])
        # Insert decision-impact warning before recommendations
        if key == "recommendations":
            lines.extend(
                [
                    "",
                    "---",
                    "## ⚠️ DECISION IMPACT: NONE — Advisory Only",
                    "The following recommendations are **validation and exploration actions only**.",
                    "They must not be treated as decision-grade guidance.",
                    "Before acting on any recommendation below, collect sufficient A/B-grade evidence",
                    "and re-run verification to produce a `.final.md` decision-grade report.",
                    "",
                ]
            )

    lines.extend(
        [
            "",
            "---",
            "## Advisory Limitations (Auto-generated)",
            f"- Failed gates: {failure_summary}",
            f"- Report status: {report_status}",
            "- Action recommendations: **BLOCKED** (evidence insufficient)",
            "- Usable for: hypothesis generation, research direction, identifying evidence gaps",
            "- NOT usable for: go/no-go decisions, budget allocation, strategic pivots",
            "",
        ]
    )

    # Vendor Source Transparency: document T3_Synthesis commercial sources and their claims
    vendor_sources = []
    for sid, src in ledger.get("sources", {}).items():
        if src.get("type") == "T3_Synthesis" and src.get("publisher_type") == "company":
            claims_supported = []
            for cid, claim in ledger.get("claims", {}).items():
                if sid in claim.get("primary_sources", []) or sid in claim.get("corroboration_sources", []):
                    claims_supported.append(cid)
            vendor_sources.append(
                {
                    "source_id": sid,
                    "title": src.get("title", ""),
                    "domain": src.get("url_domain", ""),
                    "claims_supported": claims_supported,
                }
            )
    if vendor_sources:
        lines.extend(
            [
                "",
                "## Vendor Source Transparency",
                "The following sources are T3_Synthesis type from commercial domains and may have commercial bias:",
                "",
            ]
        )
        for vs in vendor_sources:
            domain_note = "(vendor/competitor site - may have commercial bias)" if vs["domain"] else ""
            claims_str = ", ".join(vs["claims_supported"]) if vs["claims_supported"] else "none"
            lines.append(f"- **{vs['source_id']}**: {vs['title']} {domain_note}")
            lines.append(f"  - Domain: `{vs['domain']}`")
            lines.append(f"  - Supports claims: {claims_str}")
        lines.append("")

    lines.extend(
        [
            _question_coverage_table_markdown(ledger),
            "",
            _prompt_item_coverage_table_markdown(ledger),
            "",
            _modules_markdown(ledger),
            "",
            _evidence_markdown(ledger),
            "",
            _hypotheses_markdown(ledger),
            "",
            _recommendations_trace_markdown(ledger),
            "",
            _closure_searches_markdown(ledger),
            "",
            _sources_markdown(ledger),
            "",
            _verification_markdown(ledger),
            "",
        ]
    )

    # Chat-friendly summary for advisory reports
    claims = ledger.get("claims", {})
    recommendations = ledger.get("recommendations", {})
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Advisory Summary")
    lines.append("")
    lines.append(
        "This section is for reference only. When validate-report returns FAIL, output only the 6-bullet template in chat (Report, Ledger, verify, report_status, validate-report, advisory_failures). Do not copy this summary to chat."
    )
    lines.append("")
    top_claims = sorted(
        claims.items(), key=lambda x: {"A": 0, "B": 1, "C": 2, "D": 3, "F": 4}.get(x[1].get("grade", "F"), 4)
    )[:3]
    if top_claims:
        lines.append("**Key claims (highest grade):**")
        for cid, claim in top_claims:
            lines.append(f"- [{claim.get('grade', '?')}] {claim.get('claim', 'No text')[:100]}")
    lines.append("")
    lines.append("**Recommendations: advisory only — not action recommendations.**")
    for rid, rec in recommendations.items():
        if rec.get("type") == "advisory":
            lines.append(f"- {rec.get('text', 'No text')[:120]}")

    return "\n".join(lines)


def _advisory_report_markdown_with_hash(ledger: dict, frozen_hash: str) -> str:
    """Generate advisory report using a pre-computed frozen hash to avoid hash mismatch on validate."""
    content = _advisory_report_markdown(ledger)
    # Override the LEDGER_HASH in the content with the frozen hash
    content = re.sub(r"<!-- LEDGER_HASH: [a-f0-9]+ -->", f"<!-- LEDGER_HASH: {frozen_hash} -->", content)
    return content


# Advisory-safe gates: evidence weakness that can be documented in advisory report
ADVISORY_SAFE_GATES = {
    "t1t2_ratio",
    "claim_grade_distribution",
    "commercial_source_diversity",
    "numeric_evidence_strength",
    "vendor_bias",
    "cross_validation",
    "source_diversity",
    "hypothesis_tracking",
    "task_type_framework",
}
# Structural gates: failure means report is incomplete/inconsistent, not eligible for advisory
STRUCTURAL_GATES = {
    "access_trace_consistency",
    "claim_source_integrity",
    "recommendation_trace",
    "research_closure",
    "narrative_completeness",
    "thesis_narrative",
    "edge_cases",
    "subquestion_coverage",
    "prompt_item_coverage",
    "coverage_loop",
    "language_alignment",
    "scope_fidelity",
    "recommendation_actor_scope",
    "weak_claim_usage",
    "red_team_quality",
    "claim_subquestion_trace",
    "empty_ledger",
}
# source_dominance is WARNING-only, never blocks advisory
SKIPPED_GATES = {"source_dominance"}


def _advisory_eligible(verification: dict) -> tuple[bool, list[str], list[str]]:
    """Check if verification failure is eligible for advisory report.

    Returns (eligible, advisory_failures, structural_failures).
    """
    gates = verification.get("gates", {})
    failing = set()
    for gate_name, gate_data in gates.items():
        if gate_name in SKIPPED_GATES:
            continue
        if gate_data.get("status") in ("FAIL", "WARNING"):
            failing.add(gate_name)

    advisory_failures = sorted(failing & ADVISORY_SAFE_GATES)
    structural_failures = sorted(failing & STRUCTURAL_GATES)
    eligible = len(structural_failures) == 0 and len(advisory_failures) > 0
    return eligible, advisory_failures, structural_failures


def cmd_generate_advisory_report(args):
    ledger = _load_ledger(args.topic)
    # Allow task-type override at advisory report generation time
    if getattr(args, "task_type", None):
        ledger["task_type"] = args.task_type
    verification = _verify_ledger(ledger, args.dynamic_threshold)
    ledger["verification"] = verification
    # Compute and freeze the hash BEFORE saving or generating report content
    frozen_hash = _ledger_hash(ledger)
    ledger["report_config"] = ledger.get("report_config", {})
    ledger["report_config"]["generation_hash"] = frozen_hash
    _save_ledger(args.topic, ledger)

    # Check if FAIL is only due to evidence weakness and advisory-allowed conditions
    if verification["status"] == "PASS":
        print("Error: ledger passes verification; use generate-report for final reports.", file=sys.stderr)
        sys.exit(1)

    # Check recommendations: only advisory/validation allowed
    rec_violations = []
    for rid, rec in ledger.get("recommendations", {}).items():
        if rec.get("type") == "action":
            rec_violations.append({"recommendation_id": rid, "violation": "action_recommendation_in_advisory"})
    if rec_violations:
        print("Error: advisory report cannot contain action recommendations.", file=sys.stderr)
        print(json.dumps({"violations": rec_violations}, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)

    # Check advisory eligibility: must have advisory-safe failures and no structural failures
    eligible, advisory_failures, structural_failures = _advisory_eligible(verification)
    if not eligible:
        if structural_failures:
            print(
                f"Error: structural failures block advisory report: {', '.join(structural_failures)}", file=sys.stderr
            )
        else:
            print(
                "Error: no advisory-safe evidence failures found; nothing to generate advisory report for.",
                file=sys.stderr,
            )
        print(f"Advisory-safe gates: {ADVISORY_SAFE_GATES}", file=sys.stderr)
        sys.exit(1)

    output = args.output or _advisory_report_filepath(args.topic)
    # Build report using the frozen hash
    content = _advisory_report_markdown_with_hash(ledger, frozen_hash)
    with open(output, "w", encoding="utf-8") as f:
        f.write(content)
    ledger["report_config"]["last_generated_at"] = _now()
    ledger["report_config"]["generated_report_path"] = output
    _save_ledger(args.topic, ledger)
    print(f"Generated advisory report: {output}")
    print(f"Ledger: {_ledger_filepath(args.topic)}")
    print(f"Generation hash: {ledger['report_config']['generation_hash']}")
    print(f"Advisory failures (documented): {', '.join(advisory_failures)}")
    print("WARNING: This is an ADVISORY report, NOT a decision-grade final report.")
    print("Advisory reports are non-final and require further validation before any action.")


def _extract_ledger_hash(report_content: str) -> Optional[str]:
    match = re.search(r"<!-- LEDGER_HASH: ([a-f0-9]+) -->", report_content)
    return match.group(1) if match else None


def cmd_validate_report(args):
    ledger = _load_ledger(args.topic)
    # Allow task-type override at validation time
    if getattr(args, "task_type", None):
        ledger["task_type"] = args.task_type
    is_advisory = getattr(args, "advisory", False)

    if is_advisory:
        report_path = args.report or _advisory_report_filepath(args.topic)
    else:
        report_path = args.report or ledger.get("report_config", {}).get("generated_report_path")

    if not report_path or not os.path.exists(report_path):
        print(f"Error: report not found: {report_path}", file=sys.stderr)
        sys.exit(1)
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
    violations = []

    if is_advisory:
        if "<!-- ADVISORY_REPORT: true -->" not in content:
            violations.append({"type": "NOT_ADVISORY_REPORT", "message": "missing advisory report marker"})
    else:
        if "<!-- GENERATED_REPORT: true -->" not in content:
            violations.append({"type": "REPORT_NOT_GENERATED", "message": "missing generated report marker"})

    actual_hash = _ledger_hash(ledger)
    report_hash = _extract_ledger_hash(content)
    if report_hash != actual_hash:
        if not is_advisory:
            violations.append(
                {"type": "GENERATION_HASH_MISMATCH", "report_hash": report_hash, "ledger_hash": actual_hash}
            )
        else:
            violations.append(
                {"type": "GENERATION_HASH_MISMATCH", "report_hash": report_hash, "ledger_hash": actual_hash}
            )

    if not is_advisory:
        required_markers = [
            "<!-- GENERATED: evidence-ledger -->",
            "<!-- GENERATED: recommendation-trace -->",
            "<!-- GENERATED: sources -->",
            "<!-- GENERATED: verification-gates -->",
        ]
        for marker in required_markers:
            if marker not in content:
                violations.append({"type": "GENERATED_SECTION_MISSING", "marker": marker})
        if "Trust Badge" in content and "## Trust Badge (generated from ledger)" not in content:
            violations.append(
                {"type": "MANUAL_TRUST_BADGE", "message": "Trust Badge text is not the generated ledger badge"}
            )

    # Use stored threshold for replay if user didn't specify one
    replay_threshold = args.dynamic_threshold
    if not replay_threshold:
        stored_verification = ledger.get("verification", {})
        stored_t1t2 = stored_verification.get("gates", {}).get("t1t2_ratio", {})
        stored_threshold_name = stored_t1t2.get("threshold_name")
        if stored_threshold_name and stored_threshold_name != "default":
            replay_threshold = stored_threshold_name

    verification = _verify_ledger(ledger, replay_threshold)
    replay_semantic = {
        "status": verification.get("status"),
        "report_status": verification.get("report_status"),
        "use_without_rereading_confidence": verification.get("use_without_rereading_confidence"),
        "gates": verification.get("gates"),
        "violations": verification.get("violations"),
    }
    stored = ledger.get("verification", {})
    stored_semantic = {
        "status": stored.get("status"),
        "report_status": stored.get("report_status"),
        "use_without_rereading_confidence": stored.get("use_without_rereading_confidence"),
        "gates": stored.get("gates"),
        "violations": stored.get("violations"),
    }
    if replay_semantic != stored_semantic:
        violations.append({"type": "VERIFY_REPLAY_MISMATCH", "replay": replay_semantic, "stored": stored_semantic})
    if replay_semantic.get("status") != "PASS" and not is_advisory:
        violations.append({"type": "VERIFICATION_STATUS_NOT_PASS", "status": replay_semantic.get("status")})
    if violations:
        result = {"status": "FAIL", "report": report_path, "violations": violations, "advisory": is_advisory}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if args.strict:
            sys.exit(1)
    else:
        print(
            json.dumps(
                {"status": "PASS", "report": report_path, "ledger_hash": actual_hash, "advisory": is_advisory},
                ensure_ascii=False,
                indent=2,
            )
        )


def cmd_set_task_type(args):
    """Set or update the task_type field in an existing ledger."""
    if args.task_type not in TASK_TYPE_KEYWORDS:
        print(f"Error: invalid task type '{args.task_type}'", file=sys.stderr)
        print(f"Valid types: {', '.join(sorted(TASK_TYPE_KEYWORDS.keys()))}", file=sys.stderr)
        sys.exit(1)
    ledger = _load_ledger(args.topic)
    old_type = ledger.get("task_type", "")
    ledger["task_type"] = args.task_type
    _save_ledger(args.topic, ledger)
    print(f"Task type set to '{args.task_type}' (was: '{old_type or '(empty)'}')")
    print(f"Framework: {TASK_TYPE_FRAMEWORKS.get(args.task_type, {})}")


def cmd_append(args):
    filepath = _topic_filepath(args.topic)
    if not os.path.exists(filepath):
        print(f"Error: file not found: {filepath}", file=sys.stderr)
        print("Run 'init' first.", file=sys.stderr)
        sys.exit(1)
    heading = SECTION_MAP.get(args.section, args.section)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    pattern = re.compile(r"(## " + re.escape(heading) + r"\n)", re.MULTILINE)
    match = pattern.search(content)
    if not match:
        print(f"Error: section '{heading}' not found in file.", file=sys.stderr)
        sys.exit(1)
    insert_pos = match.end()
    new_content = content[:insert_pos] + "\n" + args.content + "\n" + content[insert_pos:]
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Appended to '{heading}' in {filepath}")


def cmd_replace(args):
    filepath = _topic_filepath(args.topic)
    if not os.path.exists(filepath):
        print(f"Error: file not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    heading = SECTION_MAP.get(args.section, args.section)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    pattern = re.compile(r"(## " + re.escape(heading) + r"\n)(.*?)(?=\n## \d+\. |\Z)", re.MULTILINE | re.DOTALL)
    match = pattern.search(content)
    if not match:
        print(f"Error: section '{heading}' not found.", file=sys.stderr)
        sys.exit(1)
    new_content = content[: match.start(1)] + match.group(1) + "\n" + args.content + "\n" + content[match.end(2) :]
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"Replaced '{heading}' in {filepath}")


def cmd_finalize(args):
    ledger = _load_ledger(args.topic)
    if ledger.get("verification", {}).get("status") != "PASS":
        print("Error: cannot finalize until ledger verification PASS. Run verify.", file=sys.stderr)
        print(f"Current report status: {ledger.get('verification', {}).get('report_status')}", file=sys.stderr)
        sys.exit(1)
    filepath = _topic_filepath(args.topic)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(r"\| Status: [^\n]+", "| Status: complete", content, count=1)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Finalized: {filepath}")


def cmd_show(args):
    filepath = _topic_filepath(args.topic)
    if not os.path.exists(filepath):
        print(f"Error: file not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    with open(filepath, "r", encoding="utf-8") as f:
        print(f.read())


def cmd_show_ledger(args):
    print(json.dumps(_load_ledger(args.topic), ensure_ascii=False, indent=2))


def cmd_list(args):
    storage_dir = _storage_dir()
    files = sorted(f for f in os.listdir(storage_dir) if f.endswith(".md")) if os.path.isdir(storage_dir) else []
    if not files:
        print("No research files found.")
        return
    for fname in files:
        print(fname)


def main():
    # Pre-extract --workspace from anywhere in argv (before argparse sees it)
    # so agents can write either:
    #   research_store.py --workspace /path init --topic X
    #   research_store.py init --topic X --workspace /path
    argv = sys.argv[1:]
    ws_val = ""
    cleaned = []
    i = 0
    while i < len(argv):
        if argv[i] == "--workspace" and i + 1 < len(argv):
            ws_val = argv[i + 1]
            i += 2
        elif argv[i].startswith("--workspace="):
            ws_val = argv[i].split("=", 1)[1]
            i += 1
        else:
            cleaned.append(argv[i])
            i += 1
    if ws_val:
        os.environ["RESEARCH_WORKSPACE"] = os.path.abspath(ws_val.strip())

    parser = argparse.ArgumentParser(description="Research storage and verification in .research/")
    parser.add_argument("--workspace", default="", help="Override output directory (files go to <workspace>/.research/)")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("init", help="Create markdown file and structured ledger")
    p.add_argument("--topic", required=True)
    p.add_argument("--scope", default="")
    p.add_argument("--force", action="store_true")
    p.add_argument("--task-type", choices=sorted(TASK_TYPE_KEYWORDS.keys()), default=None)

    p = sub.add_parser("append", help="Append markdown content to a section")
    p.add_argument("--topic", required=True)
    p.add_argument("--section", required=True, choices=list(SECTION_MAP.keys()))
    p.add_argument("--content", required=True)

    p = sub.add_parser("replace", help="Replace markdown section")
    p.add_argument("--topic", required=True)
    p.add_argument("--section", required=True, choices=list(SECTION_MAP.keys()))
    p.add_argument("--content", required=True)

    p = sub.add_parser("add-source", help="Add/update structured source")
    p.add_argument("--topic", required=True)
    p.add_argument("--id", required=True)
    p.add_argument("--type", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--url", default="")
    p.add_argument("--citation", default="")
    p.add_argument("--language", default="en")
    p.add_argument("--publisher", default="")
    p.add_argument("--publisher-type", default="unknown", choices=sorted(VALID_PUBLISHER_TYPES))
    p.add_argument("--official-domain", default="")
    p.add_argument("--access-status", required=True, choices=sorted(VALID_ACCESS))
    p.add_argument("--trace-status", required=True, choices=sorted(VALID_TRACE))
    p.add_argument("--access-date", default="")
    p.add_argument("--used-for", default="")
    p.add_argument("--notes", default="")

    p = sub.add_parser("add-claim", help="Add/update structured claim")
    p.add_argument("--topic", required=True)
    p.add_argument("--id", required=True)
    p.add_argument("--claim", required=True)
    p.add_argument("--grade", required=True, choices=sorted(VALID_GRADES))
    p.add_argument("--confidence", required=True, choices=sorted(VALID_CONFIDENCE))
    p.add_argument("--primary-sources", default="")
    p.add_argument("--corroboration-sources", default="")
    p.add_argument("--contradiction-checked", default="false")
    p.add_argument("--verification-status", required=True, choices=sorted(VALID_VERIFICATION))
    p.add_argument("--used-in", default="")
    p.add_argument("--numeric", action="store_true")
    p.add_argument("--numeric-mode", choices=["auto", "true", "false"], default="auto")
    p.add_argument("--notes", default="")

    p = sub.add_parser("add-recommendation", help="Add/update recommendation trace")
    p.add_argument("--topic", required=True)
    p.add_argument("--id", required=True)
    p.add_argument("--text", required=True)
    p.add_argument("--claim-ids", default="")
    p.add_argument("--type", choices=["action", "validation", "research_next", "advisory"], default="validation")
    p.add_argument("--notes", default="")

    p = sub.add_parser("add-hypothesis", help="Add/update a hypothesis")
    p.add_argument("--topic", required=True)
    p.add_argument("--id", required=True)
    p.add_argument("--initial-state", required=True)
    p.add_argument("--current-state", default="")
    p.add_argument("--mutation-trigger", default="")
    p.add_argument("--trigger-claim-ids", default="")
    p.add_argument("--status", required=True, choices=sorted(VALID_HYPOTHESIS_STATUS))
    p.add_argument("--confidence", type=int, default=0)
    p.add_argument("--notes", default="")

    p = sub.add_parser("add-closure-search", help="Add a closure search")
    p.add_argument("--topic", required=True)
    p.add_argument("--id", required=True)
    p.add_argument("--trigger", default="")
    p.add_argument("--search-direction", required=True, choices=sorted(VALID_SEARCH_DIRECTIONS))
    p.add_argument("--perspective", required=True, choices=sorted(VALID_PERSPECTIVES))
    p.add_argument("--source-ids", default="")
    p.add_argument("--new-evidence", default="")
    p.add_argument("--effect-on-conclusion", required=True, choices=sorted(VALID_EFFECTS))
    p.add_argument("--counterintuitive-angle", default="")
    p.add_argument("--alternative-hypothesis", default="")
    p.add_argument("--decision-impact", default="")

    p = sub.add_parser("add-red-team", help="Add a red team argument")
    p.add_argument("--topic", required=True)
    p.add_argument("--argument", required=True)
    p.add_argument("--target-claim-ids", default="")
    p.add_argument("--severity", choices=["low", "medium", "high", "critical"], default="medium")
    p.add_argument("--counter-evidence", default="")

    p = sub.add_parser("set-dimensions", help="Set analysis dimensions for task_type_framework gate")
    p.add_argument("--topic", required=True)
    p.add_argument("--dimensions", required=True, help="Comma-separated dimension names (min 3)")

    p = sub.add_parser("verify", help="Run mechanical verification gates")
    p.add_argument("--topic", required=True)
    p.add_argument("--dynamic-threshold", choices=["breaking", "emergent", "commercial", "practitioner"], default=None)
    p.add_argument("--strict", action="store_true")
    p.add_argument("--task-type", choices=sorted(TASK_TYPE_KEYWORDS.keys()), default=None)

    p = sub.add_parser("import-ledger", help="Batch import sources, claims, recommendations, and narrative from JSON")
    p.add_argument("--input", required=True)
    p.add_argument("--topic", default="")
    p.add_argument("--init-if-missing", action="store_true")
    p.add_argument("--loose", action="store_true", help="Warn instead of exit on non-critical errors")

    p = sub.add_parser("trust-badge", help="Generate Trust Badge from verified ledger")
    p.add_argument("--topic", required=True)
    p.add_argument("--dynamic-threshold", choices=["breaking", "emergent", "commercial", "practitioner"], default=None)
    p.add_argument("--task-type", choices=sorted(TASK_TYPE_KEYWORDS.keys()), default=None)

    p = sub.add_parser("update-narrative", help="Update a free narrative section in the ledger")
    p.add_argument("--topic", required=True)
    p.add_argument("--section", required=True, choices=sorted(NARRATIVE_SECTIONS.keys()))
    p.add_argument("--content", default="")
    p.add_argument("--content-file", default="", help="Read content from file (avoids shell $ interpolation)")

    p = sub.add_parser("set-task-type", help="Set or update the task_type field in an existing ledger")
    p.add_argument("--topic", required=True)
    p.add_argument("--task-type", required=True, choices=sorted(TASK_TYPE_KEYWORDS.keys()))

    p = sub.add_parser("generate-report", help="Generate final report from ledger")
    p.add_argument("--topic", required=True)
    p.add_argument("--output", default="")
    p.add_argument("--verify-first", action="store_true")
    p.add_argument("--fail-on-violations", action="store_true")
    p.add_argument("--dynamic-threshold", choices=["breaking", "emergent", "commercial", "practitioner"], default=None)
    p.add_argument("--task-type", choices=sorted(TASK_TYPE_KEYWORDS.keys()), default=None, help="Override task type for framework gate")

    p = sub.add_parser(
        "generate-advisory-report",
        help="Generate advisory report when verification fails due to evidence threshold only",
    )
    p.add_argument("--topic", required=True)
    p.add_argument("--output", default="")
    p.add_argument("--dynamic-threshold", choices=["breaking", "emergent", "commercial", "practitioner"], default=None)
    p.add_argument("--task-type", choices=sorted(TASK_TYPE_KEYWORDS.keys()), default=None, help="Override task type for framework gate")

    p = sub.add_parser("validate-report", help="Validate generated report against ledger")
    p.add_argument("--topic", required=True)
    p.add_argument("--report", default="")
    p.add_argument("--dynamic-threshold", choices=["breaking", "emergent", "commercial", "practitioner"], default=None)
    p.add_argument("--task-type", choices=sorted(TASK_TYPE_KEYWORDS.keys()), default=None, help="Override task type for framework gate")
    p.add_argument("--strict", action="store_true")
    p.add_argument("--advisory", action="store_true", help="Validate advisory report instead of final report")

    p = sub.add_parser("finalize", help="Mark research as complete only if verification passed")
    p.add_argument("--topic", required=True)

    p = sub.add_parser("show", help="Print markdown file")
    p.add_argument("--topic", required=True)

    p = sub.add_parser("show-ledger", help="Print structured ledger")
    p.add_argument("--topic", required=True)

    sub.add_parser("list", help="List research files")

    args = parser.parse_args(cleaned)
    if not args.command:
        parser.print_help()
        sys.exit(1)
    cmds = {
        "init": cmd_init,
        "append": cmd_append,
        "replace": cmd_replace,
        "add-source": cmd_add_source,
        "add-claim": cmd_add_claim,
        "add-recommendation": cmd_add_recommendation,
        "add-hypothesis": cmd_add_hypothesis,
        "add-closure-search": cmd_add_closure_search,
        "add-red-team": cmd_add_red_team,
        "set-dimensions": cmd_set_dimensions,
        "import-ledger": cmd_import_ledger,
        "verify": cmd_verify,
        "trust-badge": cmd_trust_badge,
        "update-narrative": cmd_update_narrative,
        "set-task-type": cmd_set_task_type,
        "generate-report": cmd_generate_report,
        "generate-advisory-report": cmd_generate_advisory_report,
        "validate-report": cmd_validate_report,
        "finalize": cmd_finalize,
        "show": cmd_show,
        "show-ledger": cmd_show_ledger,
        "list": cmd_list,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
