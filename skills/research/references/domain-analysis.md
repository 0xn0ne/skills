# Domain-Specific Analysis Requirements

When the detected task type is `technology_evaluation` or involves code optimization, apply these additional analysis requirements.

## Technology Evaluation Analysis

| Analysis Requirement | What to Produce | When to Apply |
|---|---|---|
| **Algorithm Complexity** | Big-O analysis of current vs proposed approaches | Always |
| **Memory Layout Analysis** | Cache line alignment, SIMD compatibility, GC pressure | When performance is a goal |
| **Overflow/Boundary Analysis** | Cross-channel overflow, integer overflow, boundary conditions | When dealing with numeric data |
| **Compiler/JIT Behavior** | Numba/Cython/LLVM specific optimizations and pitfalls | When using JIT compilation |
| **Platform-Specific Behavior** | Windows/Linux/Mac differences, API availability | When recommending platform-specific tools |
| **Warmup/Cold Start Costs** | JIT compilation time, cache warming, first-run penalties | When latency matters |

## Code Quality Review

When research produces code, the code MUST pass these checks before delivery:

1. **Semantic Consistency**: Code logic must match the user's requirements exactly — verify every formula, every boundary condition, every return value
2. **Edge Case Handling**: Document how the code handles: empty inputs, out-of-bounds access, overflow, underflow, NaN/Inf
3. **Performance Claims Verification**: If the code claims X speedup, the claim must be traceable to evidence in the ledger (not just theoretical)
4. **API Compatibility**: Verify that recommended APIs/libraries exist in the target environment

## Mathematical Formula Requirements

For technical research, every key relationship MUST be expressed as a formula or pseudocode:

```
# Bad: "The similarity is calculated based on the difference"
# Good: S_i = 1 - |C_found - C_target| / 0xFFFFFF
# Good: S_total = Σ(S_i) / N, where S_i = 0 if out of bounds
```

## Progressive Research Reasoning Template

After each round of searching, produce 2-4 paragraphs of technical reasoning:

### Round 1 Reasoning
1. **Bottleneck/Root Cause Analysis**: Where is the actual bottleneck or core issue? Does it match the user's assumption?
2. **Algorithm/Strategy Reasoning**: What specific technical approaches emerged? Why? What are their complexity characteristics?
3. **Mathematical/Formal Modeling**: What mathematical relationships or formal models describe the problem space?
4. **Integration/Architecture Planning**: How would the promising approaches combine into a coherent solution?

### Round 2 Reasoning
1. **Contradiction Resolution**: What contradictions emerged? How do you resolve them?
2. **Refined Mathematical Model**: Update formulas, constraints, complexity analyses. Are there edge cases (overflow, boundary conditions, cache effects)?
3. **Strategy Refinement**: How has your recommended approach changed? What implementation details are now clearer?
4. **Gap Identification**: What critical technical details are still missing?

### Final Synthesis
1. **Final Bottleneck/Root Cause**: Definitive answer with evidence
2. **Optimal Strategy**: Recommended approach with specific technical justification
3. **Complete Mathematical Model**: Final formulas, constraints, boundary conditions, edge cases
4. **Implementation Architecture**: How solution components fit together, with specific libraries/tools/APIs
5. **Performance Prediction**: Realistic improvement based on evidence, with assumptions documented
