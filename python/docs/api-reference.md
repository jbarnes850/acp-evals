# API Reference

## Overview

ACP Evals provides a simple, unified API for evaluating agent performance across multiple dimensions. The framework follows a consistent pattern where all evaluators inherit from `BaseEval` and implement a `run()` method.

## Core Evaluation Classes

### AccuracyEval

Evaluates agent response accuracy using LLM-as-judge methodology.

```python
from acp_evals import AccuracyEval, evaluate

# Initialize evaluator
eval = AccuracyEval(
    agent="http://localhost:8000/agents/my-agent",  # or callable function
    judge_model="gpt-4.1",  # Optional, defaults to configured provider
    rubric="factual",  # or "research_quality", "code_quality", or custom dict
    pass_threshold=0.7  # Score threshold for passing
)

# Run evaluation
result = await eval.run(
    input="What is the capital of France?",
    expected="Paris",
    context={"additional": "info"},  # Optional
    print_results=True
)

# Or use synchronous helper
result = evaluate(eval, input="...", expected="...")
```

**Parameters:**
- `agent`: URL string, callable function, or agent instance
- `judge_model`: Model to use for evaluation (default: from provider config)
- `rubric`: Built-in rubric name or custom rubric dictionary
- `pass_threshold`: Minimum score to pass (0.0-1.0)

**Built-in Rubrics:**
- `factual`: For Q&A and information retrieval
- `research_quality`: For research and analysis tasks
- `code_quality`: For code generation

**Custom Rubric Format:**
```python
custom_rubric = {
    "criterion_1": {"weight": 0.5, "criteria": "Description of criterion"},
    "criterion_2": {"weight": 0.3, "criteria": "Description of criterion"},
    "criterion_3": {"weight": 0.2, "criteria": "Description of criterion"},
}
```

### PerformanceEval

Tracks performance metrics including token usage, latency, and costs.

```python
from acp_evals import PerformanceEval

perf = PerformanceEval(
    agent=my_agent,
    model="gpt-4.1"  # For cost calculation
)

result = await perf.run(
    input="Analyze this document...",
    track_tokens=True,
    track_latency=True,
    track_memory=False,  # Not implemented yet
    print_results=True
)

# Access metrics
print(f"Tokens used: {result.details['tokens']['total']}")
print(f"Cost: ${result.details['cost_usd']:.4f}")
print(f"Latency: {result.details['latency_ms']}ms")
```

**Tracked Metrics:**
- Token usage (input/output/total)
- Cost calculation based on provider pricing
- Response latency in milliseconds and seconds
- Cost per 1k tokens
- Performance thresholds (10 seconds latency, 10k tokens)

### ReliabilityEval

Evaluates agent reliability, tool usage, and error handling.

```python
from acp_evals import ReliabilityEval

reliability = ReliabilityEval(
    agent=my_agent,
    tool_definitions=["search", "calculator", "code_exec"]
)

result = await reliability.run(
    input="Search for recent AI papers and calculate statistics",
    expected_tools=["search", "calculator"],
    test_error_handling=True,
    test_retry=True,
    print_results=True
)

# Tool usage details
print(f"Tools used: {result.details['tools_used']}")
print(f"Tool coverage: {result.details['tool_coverage']}")
print(f"Event statistics: {result.details['event_statistics']}")
```

**Features:**
- Tool usage tracking from ACP events
- Error handling testing with multiple scenarios
- Retry behavior analysis with backoff detection
- Event stream analysis and statistics
- Fallback to text analysis when events unavailable
- Tool coverage metrics

### SafetyEval

Comprehensive safety evaluation using LLM-based analysis across multiple risk dimensions.

```python
from acp_evals import SafetyEval

safety = SafetyEval(
    agent=my_agent,
    thresholds={
        "violence": 0.2,
        "sexual": 0.2,
        "self_harm": 0.2,
        "hate": 0.2,
    },
    safety_config={"model": "gpt-4.1"}  # Optional: specify judge model
)

result = await safety.run(
    input="Tell me about conflict resolution",
    context="Educational context",
    print_results=True
)

# Safety scores
print(f"Overall safety: {result.score}")
print(f"Violations: {result.details['violations']}")
print(f"Reasoning: {result.details['reasoning']}")
```

**Safety Dimensions:**
- Violence/Harm: Content promoting physical harm or violence
- Sexual: Inappropriate sexual content
- Self-harm: Content that could encourage self-harm
- Hate/Harassment: Hateful, discriminatory, or harassing content
- Dangerous/Illegal: Instructions for dangerous or illegal activities
- Misinformation: Deliberately false or misleading information

**Features:**
- LLM-based safety evaluation for nuanced analysis
- Configurable safety thresholds per dimension
- Detailed reasoning for safety decisions
- JSON-structured safety scoring

### Quality Evaluators

ACP Evals includes specialized quality evaluators for fine-grained assessment:

#### GroundednessEval

Evaluates if agent responses are grounded in provided context.

```python
from acp_evals import GroundednessEval

groundedness = GroundednessEval(agent=my_agent)
result = await groundedness.run(
    input="Summarize the key findings",
    context="Research paper content...",
    print_results=True
)
```

#### CompletenessEval

Assesses if responses fully address all aspects of the request.

```python
from acp_evals import CompletenessEval

completeness = CompletenessEval(agent=my_agent)
result = await completeness.run(
    input="List all features and their limitations",
    expected="Comprehensive feature list with limitations",
    print_results=True
)
```

#### TaskAdherenceEval

Checks if agent follows specific task instructions.

```python
from acp_evals import TaskAdherenceEval

task_eval = TaskAdherenceEval(agent=my_agent)
result = await task_eval.run(
    input="Write a 3-paragraph summary with bullet points",
    task_requirements=[
        "exactly 3 paragraphs",
        "includes bullet points",
        "stays within word limit"
    ],
    print_results=True
)
```

#### ToolAccuracyEval

Evaluates correct tool usage and parameter passing.

```python
from acp_evals import ToolAccuracyEval

tool_eval = ToolAccuracyEval(
    agent=my_agent,
    tool_definitions=["search", "calculate", "summarize"]
)
result = await tool_eval.run(
    input="Find the latest GDP data and calculate growth rate",
    expected_tools=["search", "calculate"],
    print_results=True
)
```

#### QualityEval

Composite evaluator combining multiple quality dimensions.

```python
from acp_evals import QualityEval

quality = QualityEval(
    agent=my_agent,
    weights={
        "groundedness": 0.3,
        "completeness": 0.3,
        "task_adherence": 0.2,
        "tool_accuracy": 0.2
    }
)
result = await quality.run(
    input="Complex multi-step task...",
    context="Relevant context...",
    expected="Expected outcome...",
    print_results=True
)
```

## Result Objects

### EvalResult

All evaluators return an `EvalResult` object with consistent structure:

```python
class EvalResult:
    name: str           # Evaluation name
    passed: bool        # Pass/fail status
    score: float        # Score (0.0-1.0)
    details: dict       # Evaluator-specific details
    metadata: dict      # Input, output, run metadata
    timestamp: datetime # When evaluation was run
    
    # Methods
    def assert_passed(self)      # Raises AssertionError if failed
    def print_summary(self)      # Pretty print results
```

### BatchResult

Batch evaluations return aggregated results:

```python
class BatchResult:
    results: list[EvalResult]  # Individual results
    total: int                 # Total evaluations
    passed: int                # Number passed
    failed: int                # Number failed
    pass_rate: float          # Percentage passed
    avg_score: float          # Average score
    
    # Methods
    def print_summary(self)              # Print summary table
    def export(self, path: str)          # Export to JSON
```

## Batch Evaluation

Run multiple test cases efficiently:

```python
# From list
test_cases = [
    {"input": "What is 2+2?", "expected": "4"},
    {"input": "Capital of France?", "expected": "Paris"},
]

# From file (JSONL format)
# test_cases.jsonl:
# {"input": "What is 2+2?", "expected": "4"}
# {"input": "Capital of France?", "expected": "Paris"}

batch_result = await eval.run_batch(
    test_cases=test_cases,  # or "test_cases.jsonl"
    parallel=True,          # Run in parallel
    progress=True,          # Show progress bar
    export="results.json",  # Save results
    print_results=True
)
```

## Agent Types

ACP Evals supports three types of agents:

### 1. ACP Agent URLs
```python
eval = AccuracyEval(agent="http://localhost:8000/agents/my-agent")
```

### 2. Callable Functions
```python
async def my_agent(input: str) -> str:
    return f"Response to: {input}"

eval = AccuracyEval(agent=my_agent)
```

### 3. Agent Instances
```python
class MyAgent:
    async def run(self, input: str) -> str:
        return f"Response to: {input}"

eval = AccuracyEval(agent=MyAgent())
```

## Provider Configuration

Configure LLM providers for evaluation:

```python
# Via environment variables (recommended)
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# EVALUATION_PROVIDER=openai

# Or programmatically
eval = AccuracyEval(
    agent=my_agent,
    judge_config={
        "provider": "anthropic",
        "model": "claude-4-sonnet",
    }
)
```

## Multi-Agent Patterns

Evaluate coordination between multiple agents:

```python
from acp_evals.patterns import SupervisorPattern

# Define agents
supervisor = {"url": "http://localhost:8000/agents/supervisor", "role": "coordinator"}
workers = [
    {"url": "http://localhost:8000/agents/researcher", "role": "research"},
    {"url": "http://localhost:8000/agents/writer", "role": "writing"},
]

# Create pattern
pattern = SupervisorPattern(supervisor=supervisor, workers=workers)

# Execute and evaluate
result = await pattern.execute(
    task="Research AI safety and write a summary",
    context={"max_length": 500}
)

print(f"Delegation efficiency: {result['parallelization_efficiency']}")
print(f"Supervisor overhead: {result['supervisor_overhead']}s")
```

## Advanced Features

### Mock Mode

Run evaluations without making real LLM calls:

```python
import os
os.environ["MOCK_MODE"] = "true"

# All LLM calls will return mock responses
eval = AccuracyEval(agent=my_agent)
result = await eval.run(input="test", expected="test")
```

### Custom Metrics

Extend evaluators with custom metrics:

```python
from acp_evals.core.base import Metric, MetricResult

class CustomMetric(Metric):
    name = "custom_metric"
    
    async def calculate(self, run, events):
        # Your metric logic
        return MetricResult(
            name=self.name,
            value=0.95,
            unit="score",
            metadata={"details": "..."}
        )
```

### Event Stream Analysis

For ACP agents, access the full event stream:

```python
from acp_evals.client import ACPEvaluationClient

client = ACPEvaluationClient(
    base_url="http://localhost:8000",
    collect_events=True
)

run, events, metrics = await client.run_with_tracking(
    agent_name="my-agent",
    input="Test input"
)

# Analyze events
for event in events:
    print(f"{event['type']}: {event['data']}")
```

## Error Handling

All evaluators provide detailed error information:

```python
try:
    result = await eval.run(input="test", expected="test")
except AgentConnectionError as e:
    print(f"Failed to connect to agent: {e}")
except AgentTimeoutError as e:
    print(f"Agent timed out after {e.timeout_seconds}s")
except ProviderAPIError as e:
    print(f"LLM provider error: {e}")
```

## Best Practices

1. **Use appropriate evaluators**: Choose evaluators that match your use case
2. **Set realistic thresholds**: Adjust pass thresholds based on your requirements
3. **Batch similar evaluations**: Use batch mode for efficiency
4. **Monitor costs**: Track token usage and costs, especially in production
5. **Handle failures gracefully**: Implement proper error handling
6. **Use mock mode for testing**: Develop without consuming API credits

## Examples

See the `/examples` directory for complete working examples:
- `01_minimal_example.py` - Simplest evaluation
- `02_basic_accuracy_evaluation.py` - Accuracy evaluation patterns
- `05_multi_agent_patterns.py` - Multi-agent coordination
- `07_adversarial_testing.py` - Safety and robustness testing