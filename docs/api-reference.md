# API Reference

## Overview

ACP Evals provides a simplified API for evaluating agent performance across three core dimensions: accuracy, performance, and reliability. All evaluators follow a consistent pattern with `run()` and `run_batch()` methods.

## Core Classes

### AccuracyEval

Evaluates agent response accuracy using LLM-as-judge methodology.

```python
from acp_evals import AccuracyEval

eval = AccuracyEval(
    agent="http://localhost:8000/agent",
    rubric="factual",
    judge_model="gpt-4o",
    pass_threshold=0.7
)
```

#### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `agent` | `Union[str, Callable, Any]` | Required | Agent URL, callable function, or agent instance |
| `rubric` | `Union[str, Dict[str, Dict[str, Any]]]` | `"factual"` | Built-in rubric name or custom rubric dictionary |
| `judge_model` | `Optional[str]` | `None` | Model to use for evaluation |
| `pass_threshold` | `float` | `0.7` | Minimum score to pass (0.0-1.0) |

#### Built-in Rubrics

- **`"factual"`**: For Q&A and information retrieval
  - accuracy (50%): Is the information factually correct?
  - completeness (30%): Does the response cover all key points?
  - relevance (20%): Is the response relevant to the question?

- **`"research_quality"`**: For research and analysis tasks
  - depth (30%): Does the response show deep understanding?
  - sources (20%): Are claims properly sourced?
  - analysis (30%): Is the analysis thorough and insightful?
  - clarity (20%): Is the response clear and well-structured?

- **`"code_quality"`**: For code generation
  - correctness (40%): Is the code correct and bug-free?
  - efficiency (20%): Is the code efficient?
  - readability (20%): Is the code readable and well-documented?
  - best_practices (20%): Does it follow best practices?

#### Methods

##### `async run(input, expected, context=None, print_results=False) -> EvalResult`

Run a single evaluation.

**Parameters:**
- `input` (str): Input to send to agent
- `expected` (Union[str, Dict[str, Any]]): Expected output or criteria
- `context` (Optional[Dict[str, Any]]): Additional context for evaluation
- `print_results` (bool): Whether to print results to console

**Returns:** `EvalResult` object

##### `async run_batch(test_cases, parallel=True, progress=True, export=None, print_results=True) -> BatchResult`

Run multiple evaluations.

**Parameters:**
- `test_cases` (Union[List[Dict[str, Any]], str, Path]): List of test cases or path to JSONL file
- `parallel` (bool): Run tests in parallel
- `progress` (bool): Show progress bar
- `export` (Optional[str]): Path to export results
- `print_results` (bool): Print summary

**Returns:** `BatchResult` object

### PerformanceEval

Evaluates agent performance metrics including latency and resource usage.

```python
from acp_evals import PerformanceEval

eval = PerformanceEval(
    agent="http://localhost:8000/agent",
    num_iterations=5,
    track_memory=False,
    warmup_runs=1
)
```

#### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `agent` | `Union[str, Callable, Any]` | Required | Agent URL, callable function, or agent instance |
| `num_iterations` | `int` | `5` | Number of test iterations |
| `track_memory` | `bool` | `False` | Whether to track memory usage |
| `warmup_runs` | `int` | `1` | Number of warmup runs before measurement |

#### Methods

##### `async run(input_text, expected=None) -> EvalResult`

Run performance evaluation.

**Parameters:**
- `input_text` (Union[str, List[str]]): Input text or list of inputs for varied testing
- `expected` (Optional[str]): Optional expected output (not used for scoring)

**Returns:** `EvalResult` object with performance metrics

**Metrics Tracked:**
- Latency statistics (mean, median, std dev, min, max, p95)
- Memory usage (if enabled)
- Token metrics (if available from agent)
- Performance score based on latency thresholds

### ReliabilityEval

Evaluates agent reliability, tool usage, and error handling.

```python
from acp_evals import ReliabilityEval

eval = ReliabilityEval(
    agent="http://localhost:8000/agent",
    tool_definitions=["search", "summarize"]
)
```

#### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `agent` | `Union[str, Callable, Any]` | Required | Agent URL, callable function, or agent instance |
| `tool_definitions` | `Optional[List[str]]` | `None` | List of available tool names |

#### Methods

##### `async run(input, expected_tools=None, test_error_handling=False, test_retry=False, print_results=False) -> EvalResult`

Run reliability evaluation.

**Parameters:**
- `input` (str): Input to send to agent
- `expected_tools` (Optional[List[str]]): Tools expected to be used
- `test_error_handling` (bool): Test error handling capabilities
- `test_retry` (bool): Test retry behavior
- `print_results` (bool): Whether to print results

**Returns:** `EvalResult` object with reliability metrics

**Features:**
- Tool usage tracking from ACP events
- Error handling testing with multiple scenarios
- Retry behavior analysis with backoff detection
- Event stream analysis and statistics
- Fallback to text analysis when events unavailable

## Result Objects

### EvalResult

All evaluators return an `EvalResult` object with the following structure:

```python
class EvalResult:
    name: str              # Evaluation name
    passed: bool           # Pass/fail status
    score: float          # Score (0.0-1.0)
    details: Dict[str, Any]   # Evaluator-specific details
    metadata: Dict[str, Any]  # Input, output, run metadata
    timestamp: datetime    # When evaluation was run
```

#### Methods

- `assert_passed()`: Raises AssertionError if evaluation failed
- `print_summary()`: Pretty print results to console

### BatchResult

Batch evaluations return a `BatchResult` object:

```python
class BatchResult:
    results: List[EvalResult]  # Individual results
    total: int                 # Total evaluations
    passed: int               # Number passed
    failed: int               # Number failed
    pass_rate: float         # Percentage passed
    avg_score: float         # Average score
```

#### Methods

- `print_summary()`: Print summary table
- `export(path: str)`: Export results to JSON file

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

## Test Case Format

Test cases for batch evaluation can be provided as:

### List of Dictionaries
```python
test_cases = [
    {"input": "What is 2+2?", "expected": "4"},
    {"input": "Capital of France?", "expected": "Paris", "context": {"type": "geography"}},
]
```

### JSONL File
```jsonl
{"input": "What is 2+2?", "expected": "4"}
{"input": "Capital of France?", "expected": "Paris", "context": {"type": "geography"}}
```

### JSON File
```json
[
    {"input": "What is 2+2?", "expected": "4"},
    {"input": "Capital of France?", "expected": "Paris", "context": {"type": "geography"}}
]
```

## Example Usage

### Basic Accuracy Evaluation
```python
from acp_evals import AccuracyEval

# Create evaluator
eval = AccuracyEval("http://localhost:8000/agents/my-agent")

# Run single evaluation
result = await eval.run(
    input="What is the capital of France?",
    expected="Paris",
    print_results=True
)

# Check if passed
result.assert_passed()
```

### Performance Testing
```python
from acp_evals import PerformanceEval

# Create evaluator with custom settings
eval = PerformanceEval(
    agent="http://localhost:8000/agents/my-agent",
    num_iterations=10,
    warmup_runs=2
)

# Run performance test
result = await eval.run("Process this text quickly")

# Access metrics
print(f"Mean latency: {result.details['latency']['mean_ms']}ms")
print(f"P95 latency: {result.details['latency']['p95_ms']}ms")
```

### Reliability Testing with Tools
```python
from acp_evals import ReliabilityEval

# Create evaluator with tool definitions
eval = ReliabilityEval(
    agent="http://localhost:8000/agents/my-agent",
    tool_definitions=["search", "calculate", "summarize"]
)

# Run reliability test
result = await eval.run(
    input="Search for recent AI papers and calculate statistics",
    expected_tools=["search", "calculate"],
    test_error_handling=True,
    print_results=True
)

# Check tool coverage
print(f"Tool coverage: {result.details['tool_coverage']}")
```

### Batch Evaluation
```python
from acp_evals import AccuracyEval

# Create evaluator
eval = AccuracyEval("http://localhost:8000/agents/my-agent")

# Run batch evaluation from file
batch_result = await eval.run_batch(
    test_cases="test_cases.jsonl",
    parallel=True,
    export="results.json",
    print_results=True
)

# Access results
print(f"Pass rate: {batch_result.pass_rate}%")
print(f"Average score: {batch_result.avg_score}")
```