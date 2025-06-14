# Claude Prompt for Building ACP Evals Framework

## Context

You are building an evaluation framework for the Agent Communication Protocol (ACP) and BeeAI Framework. This framework addresses a critical gap: there is currently no standardized way to benchmark agent performance, measure quality, or compare different agent implementations in the ACP/BeeAI ecosystem.

## Key Research Insights to Apply

### 1. Token Usage is Primary (Anthropic Research)
- Token usage explains 80% of performance variance in agent systems
- Multi-agent systems use ~15x more tokens than single agents
- **Implementation Priority**: Make token metrics the #1 priority

### 2. Context Engineering Principles (Cognition Research)
- Share full agent traces, not just individual messages
- Actions carry implicit decisions that can conflict
- Single-threaded linear patterns often outperform parallel multi-agent systems
- **Implementation Focus**: Build trace-based evaluation with handoff quality metrics

### 3. Architecture Patterns Matter (LangChain Research)
- Different patterns (supervisor, swarm, linear) have significant trade-offs
- Context degradation happens quickly with irrelevant information
- "Telephone game" effects in supervisor patterns cause information loss
- **Implementation Need**: Architecture-specific benchmarks and comparison tools

### 4. Small But Effective Evaluation Sets (Anthropic)
- 20 carefully chosen test cases can reveal dramatic performance differences
- LLM-as-judge with single rubric call is more consistent than multiple calls
- **Implementation Approach**: Start with 20-30 high-impact test cases

## Your Implementation Tasks

### Phase 0: Token-First MVP (Start Here)

1. **Create Base Infrastructure**
   - Set up the repository structure as defined in `acp-evals-setup.md`
   - Implement the base classes in `python/src/acp_evals/base.py`
   - Focus on `MetricResult` and `TokenUsage` dataclasses

2. **Implement Token Usage Metric** (PRIORITY #1)
   ```
   python/src/acp_evals/metrics/token_usage.py
   ```
   - Use tiktoken for accurate token counting
   - Track tokens by: agent/subagent, tool calls, message types
   - Calculate costs based on model pricing
   - Include efficiency score (value per token)
   - Break down usage by agent for multi-agent systems

3. **Create Context Scaling Benchmark**
   ```
   python/src/acp_evals/benchmarks/context_scaling.py
   ```
   - Start with 5-10 core tasks that have clear answers
   - Add distractor contexts progressively (0, 1, 3, 5, 10 distractors)
   - Measure accuracy degradation and latency increase
   - This tests how agents handle irrelevant information

4. **Build LLM-as-Judge Evaluator**
   ```
   python/src/acp_evals/evaluators/llm_judge.py
   ```
   - Single LLM call with unified rubric (not multiple calls)
   - Rubric criteria: accuracy (40%), completeness (30%), efficiency (30%)
   - Return JSON with scores 0.0-1.0 and pass/fail
   - Make it work with any ACP-compatible agent

5. **Create Evaluation Example**
   ```
   examples/python/evaluate_with_insights.py
   ```
   - Connect to local ACP agent (http://localhost:8000)
   - Run context scaling benchmark
   - Display results with rich tables
   - Show key insights: token costs, degradation rates, efficiency

### Testing Strategy

1. **Use Existing ACP Examples**
   - Test against agents in `acp/examples/python/basic/`
   - Start with simple echo or Q&A agents
   - Ensure compatibility with ACP's event system

2. **Validate Token Metrics**
   - Compare token counts with actual API usage
   - Verify cost calculations match real bills
   - Test with different models (GPT-4, Claude, etc.)

3. **Benchmark Quality**
   - Each test case should reveal something specific
   - Distractors should be realistic but clearly irrelevant
   - Expected answers should be unambiguous

### Key Implementation Guidelines

1. **Every Evaluation Must Track Tokens**
   - No evaluation runs without token metrics
   - Always show cost projections
   - Track context window utilization

2. **Use ACP's Event System**
   - Leverage `RunCreatedEvent`, `MessageCreatedEvent`, etc.
   - Don't create new tracking mechanisms
   - Preserve full traces for analysis

3. **Start Small, Iterate Fast**
   - MVP with 1 metric, 1 benchmark, 1 evaluator
   - Test on real agents immediately
   - Get feedback before expanding

4. **Architecture Awareness**
   - Design benchmarks that work for both single and multi-agent
   - But measure them separately
   - Document which patterns work best for which tasks

5. **Production Considerations**
   - Handle errors gracefully (they compound in agent systems)
   - Support checkpoint/resume for long evaluations
   - Make it easy to run (`pip install acp-evals && acp-evals evaluate`)

### What NOT to Do

1. Don't build large benchmark suites initially - 20 cases are enough
2. Don't assume multi-agent is always better - test this assumption
3. Don't track metrics without token usage - it's 80% of the story
4. Don't make multiple LLM calls for evaluation - use single rubric call
5. Don't ignore context degradation - it's a major real-world issue

### Design for Future Extensibility

While focusing on the MVP, keep in mind that the framework should eventually support:
- **Domain-specific evaluation**: Users creating custom benchmarks for their use cases
- **Trace-based learning**: Generating evaluation datasets from actual agent usage
- **Synthetic data generation**: Creating test cases on demand for specific domains
- **Adaptive benchmarking**: Adjusting difficulty based on agent capabilities

Design your base classes and interfaces to be extensible without requiring major refactoring later.

### Success Criteria

Your MVP is successful when:
1. You can measure token usage and costs for any ACP agent
2. You can demonstrate performance degradation with added context
3. You can automatically evaluate agent outputs with LLM-as-judge
4. You can compare single-agent vs multi-agent on the same task
5. Results clearly show cost/performance trade-offs

### Next Steps After MVP

Once the MVP is working:
1. Add handoff quality metrics for multi-agent systems
2. Implement supervisor and swarm pattern comparisons
3. Create more sophisticated benchmarks (tool use, reasoning chains)
4. Build visualization dashboard
5. Share findings with the ACP community

## Remember

- Token usage explains 80% of performance variance - make it visible
- Multi-agent systems cost 15x more - help developers understand when it's worth it
- Context matters - measure it, compress it, preserve it
- Small tests work - don't overcomplicate

Start with the token metric, test it on a real agent, then build from there. The goal is to give the ACP/BeeAI community practical tools to understand and optimize their agent systems.