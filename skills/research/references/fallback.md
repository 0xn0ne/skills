# Script Unavailable Fallback Protocol

This fallback exists for genuine environmental failures, not for convenience.

## Before Claiming Script Unavailable

Complete ALL of these steps:

1. Ensure `$SKILL_DIR` is resolved (PATH RESOLUTION section in SKILL.md).
2. Run probe commands:
   ```bash
   python $SKILL_DIR/scripts/research_store.py --help
   python $SKILL_DIR/scripts/research_store.py verify --help
   ```
3. Try `--loose` if the script runs but import fails.
4. Only if all three fail, provide raw command evidence for each attempt:

```markdown
Script unavailable evidence:
Attempt [N]:
- Exact command: [full command with absolute path]
- Working directory: [pwd output]
- Raw stdout: [full output]
- Raw stderr: [full output]
- Exit code: [number]
```

## Requirements

- Minimum 3 attempts with full evidence required
- Without this evidence, your output is INVALID

## Output Format

Title your fallback output: `# Draft Research Notes — Ledger Unverified`

**Forbidden phrases:** Trust Badge, Executive Answer, Decision-grade, Final report, action recommendations

## What to Include in Fallback Output

1. Phase 0 Audience Detection (audience type and adaptation notes — no script required)
2. Phase 1 Intent Frame (pre-search only)
3. Phase 2 Research Plan (hypotheses formed without evidence)
4. Phase 3 NOT REACHABLE (document why)
5. Phase 4-7 NOT REACHABLE (document why)
6. What would be needed to complete the research
