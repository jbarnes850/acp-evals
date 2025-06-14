# Trace Recycling

The trace recycling system converts production telemetry data into evaluation datasets, enabling continuous improvement and regression detection for ACP agents.

## Overview

Trace recycling transforms OpenTelemetry traces from production into:
- Evaluation test cases
- Pattern detection for common workflows
- Regression detection baselines
- Performance benchmarks

This creates a feedback loop where production behavior continuously improves your evaluation suite.

## Architecture

```
Production Agent → OpenTelemetry → TraceRecycler → Evaluation Dataset
                                         ↓
                                  Pattern Detection
                                         ↓
                                  Regression Tests
```

## Key Components

### TraceRecycler

The main class that ingests traces and produces evaluation candidates.

```python
from acp_evals.benchmarks.datasets import TraceRecycler

# Initialize recycler
recycler = TraceRecycler(
    retention_days=30,           # Keep traces for 30 days
    min_pattern_frequency=3      # Need 3+ occurrences for pattern
)
```

### TracePattern

Represents recurring patterns in agent behavior:
- **Success patterns**: Common successful workflows
- **Error patterns**: Recurring failure modes
- **Performance patterns**: Slow operations needing optimization

### EvaluationCandidate

A production trace converted into a test case with:
- Input/output pairs
- Tool usage sequences
- Performance baselines
- Error scenarios

## Usage Examples

### Basic Trace Ingestion

```python
# Ingest individual traces
trace = {
    "trace_id": "abc-123",
    "timestamp": "2024-01-15T10:30:00Z",
    "spans": [
        {
            "name": "agent.input",
            "attributes": {
                "input.value": "Analyze this dataset",
                "operation.type": "agent.input"
            }
        },
        {
            "name": "tool.search",
            "attributes": {
                "tool.name": "data_analyzer",
                "operation.type": "tool.search"
            }
        }
    ]
}

recycler.ingest_trace(trace)
```

### Batch Ingestion from File

```python
# Ingest traces from JSON file
count = recycler.ingest_traces_from_file("production_traces.json")
print(f"Ingested {count} traces")
```

### Generate Evaluation Dataset

```python
# Create evaluation dataset from recycled traces
dataset = recycler.generate_evaluation_dataset(
    count=100,                    # Generate 100 test cases
    min_quality_score=0.8,        # High quality traces only
    include_patterns=["success", "error_recovery"]
)

# Use in evaluation
for test_case in dataset:
    result = await evaluator.run(
        input=test_case["input"],
        expected=test_case["expected"]
    )
```

### Pattern Analysis

```python
# Export discovered patterns
recycler.export_patterns("patterns_analysis.json")

# Patterns include:
# - Common operation sequences
# - Average performance metrics
# - Error rates and types
# - Tool usage patterns
```

### Regression Detection

```python
# Compare baseline vs current traces
regressions = recycler.detect_regressions(
    baseline_traces=last_week_traces,
    current_traces=today_traces
)

for regression in regressions:
    if regression["type"] == "performance_regression":
        print(f"Performance degraded by {regression['degradation_factor']:.1%}")
    elif regression["type"] == "error_rate_regression":
        print(f"Error rate increased by {regression['increase']:.1%}")
```

## Pattern Detection

The system automatically identifies patterns based on:

1. **Operation Sequences**: Common workflows (e.g., search → analyze → respond)
2. **Error Patterns**: Recurring failures that need handling
3. **Performance Characteristics**: Slow operations or resource-intensive patterns
4. **Tool Usage**: Which tools are used together

### Pattern Types

- **Success Patterns**: Ideal workflows to replicate
- **Failure Patterns**: Common errors to test against
- **Performance Issues**: Operations needing optimization
- **Recovery Patterns**: How agents recover from errors

## Quality Scoring

Traces are scored for evaluation value based on:

```python
def score_candidate(candidate):
    score = 0.0
    
    # Tool usage is valuable for testing
    if candidate.tools_used:
        score += 0.2
    
    # Error cases are important
    if candidate.error_occurred:
        score += 0.3
    
    # Complex inputs are better
    if len(candidate.input_data) > 50:
        score += 0.1
    
    # Performance outliers
    if is_outlier(candidate.performance_metrics):
        score += 0.2
    
    # Recent traces are more relevant
    if candidate.age_days < 7:
        score += 0.2
    
    return min(score, 1.0)
```

## Integration with Continuous Evaluation

The trace recycler integrates with the continuous evaluation pipeline:

```python
from acp_evals import ContinuousEvaluationPipeline

pipeline = ContinuousEvaluationPipeline(
    agent=my_agent,
    telemetry_exporter=otel_exporter
)

# Recycled traces are automatically included
await pipeline.run_evaluation_cycle(
    include_recycled=True  # Use production traces
)
```

## Best Practices

### 1. Privacy and Security
- **Sanitize sensitive data** before recycling
- **Hash or anonymize** user information
- **Filter out** credentials and API keys

### 2. Trace Selection
- Focus on **edge cases** and **error scenarios**
- Prioritize **recent traces** over old ones
- Balance **diversity** in your dataset

### 3. Pattern Management
- Review patterns regularly
- Update baselines monthly
- Archive old patterns

### 4. Performance Optimization
- Set appropriate retention periods
- Use sampling for high-volume services
- Export patterns for offline analysis

## Testing with Sample Data

For development and testing, generate sample traces:

```python
# Generate sample traces
sample_traces = recycler.generate_sample_traces(count=50)

# Save to file
import json
with open("sample_traces.json", "w") as f:
    json.dump(sample_traces, f, indent=2)

# Ingest and test
recycler.ingest_traces_from_file("sample_traces.json")
dataset = recycler.generate_evaluation_dataset(count=10)
```

## Configuration Options

### Environment Variables

```bash
# Trace retention
TRACE_RETENTION_DAYS=30

# Pattern detection
MIN_PATTERN_FREQUENCY=3

# Quality thresholds
MIN_QUALITY_SCORE=0.7
```

### Advanced Configuration

```python
recycler = TraceRecycler(
    telemetry_exporter=otel_exporter,  # Optional: for direct OTEL integration
    retention_days=60,                  # Longer retention
    min_pattern_frequency=5             # Stricter pattern detection
)
```

## Troubleshooting

### No Patterns Detected
- Ensure minimum frequency threshold isn't too high
- Check that traces have consistent operation sequences
- Verify span attributes are properly set

### Low Quality Scores
- Review scoring criteria
- Ensure traces include sufficient context
- Check for missing input/output data

### Memory Issues
- Reduce retention period
- Implement trace sampling
- Export and archive old patterns

## Future Enhancements

Planned improvements include:
- Machine learning for pattern detection
- Automatic test case generation
- Cross-agent pattern comparison
- Real-time regression alerts