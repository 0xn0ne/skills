# Systematic Search Strategy Guide

This guide provides a structured approach to searching that ensures breadth, depth, and discovery of domain-specific knowledge.

## Search Angles Matrix

For each research dimension, search from ALL applicable angles:

| Angle | Query Pattern | Purpose |
|---|---|---|
| **Framework Discovery** | "[domain] frameworks", "[domain] methodologies", "[domain] best practices" | Discover existing structured approaches |
| **Quantitative Data** | "[metric] optimal threshold", "[metric] benchmark", "[metric] average" | Find specific numbers and standards |
| **Risk Factors** | "[domain] risks", "[domain] failure modes", "[domain] pitfalls" | Identify what can go wrong |
| **Case Studies** | "[topic] case study", "[topic] real example", "[topic] success story" | Learn from real-world examples |
| **Implementation** | "[approach] implementation guide", "[approach] tools", "[approach] tutorial" | Find practical how-to details |
| **Cross-Domain** | "[method] applied to [other domain]", "analogous to [related field]" | Borrow insights from adjacent fields |
| **Expert Opinion** | "[topic] expert interview", "[topic] practitioner blog", "[topic] postmortem" | Get insider perspectives |
| **Contradicting** | "[claim] wrong", "[claim] criticism", "[claim] alternative" | Challenge your assumptions |
| **Recent Developments** | "[topic] 2025", "[topic] latest research", "[topic] new approach" | Stay current |
| **Historical Context** | "[topic] history", "[topic] evolution", "[topic] timeline" | Understand how we got here |

## Progressive Deepening Pattern

### Round 1: Discovery (What exists?)
- Search for frameworks, methodologies, best practices
- Search for terminology and concepts
- Search for expert opinions and practitioner experience
- Search for case studies and real examples
- **Mindset**: "I don't know what I don't know. Let me discover."

### Round 2: Quantification (What numbers?)
- Search for specific thresholds, benchmarks, optimal values
- Search for risk factors and failure modes
- Search for contradicting evidence
- Search for quantitative case studies
- **Mindset**: "What are the specific numbers? What can go wrong?"

### Round 3: Implementation (How to do it?)
- Search for implementation details, tools, data sources
- Search for cross-domain applications
- Search for regulatory/compliance requirements
- Search for alternative approaches
- **Mindset**: "How do I actually do this? What else could work?"

### Round 4: Validation (Is it correct?)
- Search for stress-test results and known limitations
- Search for independent verification
- Search for expert disagreements and controversies
- Search for recent developments
- **Mindset**: "Am I wrong? What has changed?"

## Cross-Domain Search Strategy

When searching for cross-domain insights:

1. **Identify adjacent domains**: What fields deal with similar problems?
   - Example: Stock selection → Risk management, asset allocation, behavioral finance
   - Example: Code optimization → Algorithm design, systems programming, hardware architecture

2. **Search for method transfer**: "[method from domain A] applied to [domain B]"
   - Example: "machine learning applied to stock selection"
   - Example: "SIMD optimization applied to image processing"

3. **Search for analogous problems**: "similar to [problem in other domain]"
   - Example: "similar to portfolio optimization"
   - Example: "similar to signal processing"

## Query Construction Tips

### Good Queries
- Specific: "Fama-French five factor model A-share market empirical"
- Framework-oriented: "GARP strategy quantitative threshold"
- Risk-focused: "equity pledge risk A-share market trigger mechanism"

### Bad Queries
- Too broad: "stock market investing"
- Confirmation-biased: "why my strategy is the best"
- Redundant: "best stock strategy" + "top stock strategy" + "good stock strategy"

## Search Volume Targets

| Round | Minimum Searches | Focus |
|---|---|---|
| Round 1 | 15 | Discovery |
| Round 2 | 15 | Quantification |
| Round 3 | 10 | Implementation |
| Round 4 | 10 | Validation |
| **Total** | **50** | |

For complex or broad topics, aim for 80+ searches across 4 rounds.

## Regional Source Strategy

For non-English topics:
- Round 1: At least 3 regional searches (CSDN/知乎/掘金 for Chinese)
- Round 2: At least 2 regional searches for quantitative data
- Round 3: At least 1 regional search for implementation details
- Round 4: At least 1 regional search for validation

## Quality Checks

After each round, verify:
- [ ] Covered all applicable search angles for this round
- [ ] Found at least 1 framework/methodology
- [ ] Found at least 2 quantitative data points
- [ ] Found at least 1 contradicting perspective
- [ ] Regional sources included (if non-English topic)

## T1/T2 Source Hunting Protocol

**Trigger:** At the start of Round 3, check T1/T2 ratio. If < 20%, execute this protocol before continuing.

### Mandatory T1/T2 Search Sequence

1. **Google Scholar**: `"[topic] 2025 OR 2026"` — at least 3 searches
2. **arXiv**: `"[topic] preprint"` — for technical/scientific topics
3. **SSRN**: `"[topic] working paper"` — for business/economics topics
4. **Government sites**: `site:gov "[data type]"` — for policy/statistics topics
5. **Industry associations**: Search the relevant industry association's official reports/white papers

### When to Stop

Only after completing ALL 5 search types above with no results can you record "industry characteristics导致无 T1/T2 来源" in gaps-limitations and adopt commercial/practitioner threshold.

> **Do NOT declare "no T1/T2 sources exist" after only searching news and general web.** Academic databases, government sites, and industry associations are the primary source of T1/T2 materials.
