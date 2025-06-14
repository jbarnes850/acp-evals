# New Features Summary

This document summarizes the new features added to ACP Evals for feature parity with Azure AI Evaluation SDK.

## 1. Gold Standard Datasets ✅

**Location**: `src/acp_evals/benchmarks/datasets/gold_standard_datasets.py`

Production-ready evaluation tasks with multi-step scenarios:
- 7 comprehensive agent tasks covering debugging, research, code generation
- Expected tool usage sequences and trace patterns
- Failure mode tracking
- Export functionality for evaluation format

**Key Features**:
- `GOLD_STANDARD_TASKS`: Complete task library
- `get_multi_step_tasks()`: Filter multi-step scenarios
- `get_tool_using_tasks()`: Tasks requiring specific tools
- `export_for_evaluation()`: Convert to evaluation format

## 2. Adversarial Testing Framework ✅

**Location**: `src/acp_evals/benchmarks/datasets/adversarial_datasets.py`

Real-world adversarial test scenarios:
- 18 adversarial tests across 7 categories
- 2 multi-turn adversarial conversations
- 2 attack chain scenarios
- Severity levels: low, medium, high, critical

**Categories**:
- Prompt injection
- Jailbreak attempts
- Harmful content generation
- Data extraction attacks
- Indirect attacks
- Edge cases
- Encoding attacks

## 3. External Dataset Loader ✅

**Location**: `src/acp_evals/benchmarks/datasets/dataset_loader.py`

Load standard benchmarks from HuggingFace:
- TRAIL (trace-based evaluation)
- GAIA, SWE-Bench, MMLU, HumanEval
- GSM8K, TruthfulQA, HellaSwag
- Agent-specific benchmarks

**Note**: Requires `requests` library and HuggingFace authentication for some datasets.

## 4. Trace Recycling System ✅

**Location**: `src/acp_evals/benchmarks/datasets/trace_recycler.py`

Convert production telemetry into evaluation datasets:
- Pattern detection from recurring traces
- Quality scoring for evaluation candidates
- Regression detection capabilities
- Sample trace generation for testing

**Key Methods**:
- `ingest_trace()`: Process production traces
- `generate_evaluation_dataset()`: Create test cases
- `detect_regressions()`: Compare baseline vs current
- `generate_sample_traces()`: Testing support

## 5. New Evaluators ✅

### GroundednessEvaluator
**Location**: `src/acp_evals/evaluators/groundedness.py`

Evaluates if responses are grounded in provided context:
- LLM-based evaluation with fallback to keyword matching
- Identifies ungrounded claims and contradictions
- Configurable provider support

### RetrievalEvaluator
**Location**: `src/acp_evals/evaluators/retrieval.py`

Assesses information retrieval quality:
- Relevance, completeness, and accuracy metrics
- Weighted scoring system
- Support for multiple retrieved documents

### DocumentRetrievalEvaluator
**Location**: `src/acp_evals/evaluators/document_retrieval.py`

Standard IR metrics for document retrieval:
- Precision@k and Recall@k
- Mean Average Precision (MAP)
- Normalized Discounted Cumulative Gain (NDCG)
- Mean Reciprocal Rank (MRR)

## 6. Enhanced Simulator ✅

**Location**: `src/acp_evals/simulator.py`

Added adversarial scenario generation:
- `generate_adversarial_suite()`: Create comprehensive test suites
- `_get_adversarial_templates()`: Adversarial test templates
- Integration with adversarial datasets
- Mixed scenario generation (normal + adversarial)

## 7. Continuous Evaluation Pipeline ✅

**Location**: `src/acp_evals/continuous_evaluation.py`

Automated evaluation with regression detection:
- Periodic evaluation cycles
- Baseline comparison and updates
- Regression alerting system
- Integration with trace recycling

**Key Classes**:
- `ContinuousEvaluationPipeline`: Main orchestrator
- `EvaluationRun`: Individual evaluation results
- `RegressionAlert`: Detected regressions

## Usage Examples

### Gold Standard Evaluation
```python
from acp_evals.benchmarks.datasets import GOLD_STANDARD_TASKS, get_multi_step_tasks

# Get multi-step tasks
tasks = get_multi_step_tasks()
for task in tasks:
    print(f"{task.task_id}: {task.description}")
    print(f"Expected tools: {task.expected_tools}")
```

### Adversarial Testing
```python
from acp_evals.benchmarks.datasets import create_test_suite, AdversarialCategory

# Create adversarial suite
suite = create_test_suite(
    categories=[AdversarialCategory.PROMPT_INJECTION],
    min_severity="medium"
)
```

### Trace Recycling
```python
from acp_evals.benchmarks.datasets import TraceRecycler

recycler = TraceRecycler()
recycler.ingest_traces_from_file("production_traces.json")
dataset = recycler.generate_evaluation_dataset(count=50)
```

### Continuous Evaluation
```python
from acp_evals import ContinuousEvaluationPipeline

pipeline = ContinuousEvaluationPipeline(agent=my_agent)
await pipeline.run_evaluation_cycle()
```

## Documentation

- [Trace Recycling Guide](trace-recycling.md) - Detailed trace recycling documentation
- [Architecture Overview](architecture.md) - System architecture
- Main README - Getting started guide

## Dependencies

Some features require additional dependencies:
- `requests`: For dataset loader
- `opentelemetry-*`: For telemetry export
- Provider-specific packages for LLM evaluation

Install with: `pip install -e ".[all-providers]"`