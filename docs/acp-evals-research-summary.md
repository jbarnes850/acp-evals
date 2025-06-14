# Research-Informed Updates to ACP Evals (v2)

## Key Insights Applied

### From Anthropic's Multi-Agent Research

1. **Token Usage is King**
   - 80% of performance variance explained by token usage alone
   - Multi-agent systems use ~15x more tokens than single agents
   - **Applied**: Made token metrics our #1 priority metric

2. **Small Samples Work**
   - 20 test cases can reveal dramatic performance differences
   - **Applied**: Reduced initial benchmark to 20-30 carefully chosen cases

3. **LLM-as-Judge Scales**
   - Single LLM call with rubric more consistent than multiple calls
   - **Applied**: Designed unified rubric evaluation system

4. **Errors Compound**
   - Agent systems are stateful, minor failures cascade
   - **Applied**: Added error cascade tracking and checkpoint support

### From Cognition's Context Engineering

1. **Share Full Context**
   - Share agent traces, not just messages
   - **Applied**: Built trace-based evaluation, not message-based

2. **Actions Carry Decisions**
   - Conflicting implicit decisions cause failures
   - **Applied**: Created handoff quality metrics

3. **Linear Often Beats Parallel**
   - Single-threaded can be more reliable
   - **Applied**: Compare architectures fairly, don't assume multi-agent is better

4. **Context Compression Matters**
   - Long-running agents need intelligent compression
   - **Applied**: Added context efficiency metrics

### From LangChain's Benchmarking

1. **Context Degradation is Real**
   - Performance drops sharply with irrelevant context
   - **Applied**: Created context scaling benchmark (tau-bench inspired)

2. **Architecture Patterns Matter**
   - Supervisor vs swarm have different trade-offs
   - **Applied**: Built pattern-specific evaluation tools

3. **Translation Overhead**
   - "Telephone game" effects in supervisor patterns
   - **Applied**: Measure information preservation explicitly

### From Adaline Labs Agent Evaluation (2025)

1. **Dynamic Multi-Step Evaluation**
   - Move beyond static NLP metrics to behavior over time
   - evaluation = performance + process + persistence
   - **Applied**: Track agent behavior across extended tasks

2. **Four Core Dimensions**
   - Planning & reasoning: Breaking complex tasks into logical steps
   - Tool selection & execution: Choosing and using tools correctly
   - Persistence/long-horizon tasks: Maintaining focus despite setbacks
   - Collaboration & coordination: Working with other agents/humans
   - **Applied**: Ensure benchmarks cover all four dimensions

3. **Benchmark Categories for 2025**
   - Web interaction (BrowseComp - 51.5% best score shows difficulty)
   - Coding tasks (SWE-bench, ML-Dev-Bench)
   - Abstract reasoning (ARC-AGI - all models <3%, shows major gap)
   - General assistance (GAIA)
   - **Applied**: Design benchmarks across multiple categories

4. **Continuous Eval Loop**
   - Baseline benchmark suite on every change
   - Regression detection with automatic alerts
   - A/B comparison of agent versions
   - **Applied**: Build automated evaluation pipeline

5. **Production Trade-offs**
   - Latency budgets for different request types
   - Cost optimization with smaller models for routine tasks
   - Progressive rollout to limited groups first
   - **Applied**: Include production-realistic constraints in evals

## What Changed in Our Proposal

### Metrics Priority (Before → After)

**Before**: 
1. Quality metrics
2. Performance metrics  
3. Cost metrics

**After**:
1. Token usage & cost (80% of variance)
2. Context efficiency
3. Persistence & long-horizon capability
4. Tool selection accuracy
5. Handoff quality
6. Traditional metrics

### Benchmark Design (Before → After)

**Before**: Large comprehensive benchmark suites

**After**: 
- Small (20-30 case) high-impact benchmarks
- Multi-category coverage (web, coding, reasoning, assistance)
- Focus on tasks that reveal agent limitations
- Include persistence/retry scenarios

### Evaluation Approach (Before → After)

**Before**: Multiple specialized evaluators

**After**: 
- Single LLM-as-judge with unified rubric
- Token analysis on every evaluation
- Architecture-aware testing
- Continuous eval loops with regression detection
- Dynamic multi-step scenarios

### Implementation Priority (Before → After)

**Before**: Build everything, then test

**After**:
1. Token metric MVP
2. 20-case benchmark across categories
3. Automated eval loop setup
4. Test and iterate
5. Progressive expansion based on findings

## Practical Implications

1. **Start with Token Analysis**: It explains most performance variance
2. **Test Architecture Patterns Early**: Single vs multi-agent is a critical decision
3. **Small Tests Reveal Big Issues**: Don't wait for comprehensive suites
4. **Context is Everything**: Measure it, compress it, preserve it
5. **Cost Transparency**: 15x tokens = 15x cost for multi-agent
6. **Persistence Matters**: Many real tasks require multiple attempts
7. **Abstract Reasoning Gap**: Current models struggle (<3% on ARC-AGI)
8. **Category-Specific Excellence**: Models specialize (web vs coding vs reasoning)

## Key Benchmark Targets

Based on current SOTA performance:
- **Web Navigation**: Target 40-50% (BrowseComp leader: 51.5%)
- **Coding Tasks**: Target 50-60% (SWE-bench leaders: 63%+)
- **Abstract Reasoning**: Target 2-3% (ARC-AGI best: 3.0%)
- **General Assistance**: Target 70-80% (GAIA leader: 80.7%)

## Future Direction: Domain-Specific Adaptive Evaluation

While our initial framework focuses on standardized benchmarks, the market is moving toward:

1. **Domain-Specific Evaluation**
   - Users need to evaluate agents on their specific use cases
   - Generic benchmarks don't capture domain expertise
   - Custom rubrics based on business requirements

2. **Auto-Adaptive Benchmarks**
   - Evals that adjust based on the agent's stated capabilities
   - Dynamic difficulty scaling based on performance
   - Task-specific metric weighting

3. **Trace-Based Dataset Generation**
   - Bootstrap evaluation datasets from actual agent traces
   - Learn from real usage patterns
   - Continuously improve benchmarks based on production data

4. **Synthetic Dataset Creation**
   - Generate domain-specific test cases on the fly
   - Use LLMs to create relevant evaluation scenarios
   - Adapt to emerging use cases without manual curation

**Note**: These advanced features are beyond our initial contribution but represent the natural evolution of agent evaluation. Our framework should be designed with extensibility in mind to support these future capabilities.

## Next Steps Based on Research

1. **Immediate**: Build token metric and test on existing ACP examples
2. **Week 1**: Create 20-case benchmark with tasks across 4 categories
3. **Week 2**: Implement automated eval loop with regression detection
4. **Week 3**: Add persistence and long-horizon task measurements
5. **Week 4**: Test supervisor/swarm/linear patterns on same tasks
6. **Ongoing**: Share findings with benchmarks mapped to use cases
