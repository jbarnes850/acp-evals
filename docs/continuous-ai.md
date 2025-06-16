# Continuous AI Integration Guide

**Automated Agent Evaluation in CI/CD Pipelines**

This guide shows how to integrate ACP-Evals into your Continuous Integration/Continuous Deployment (CI/CD) pipelines for automated agent testing, following GitHub's [Continuous AI](https://githubnext.com/projects/continuous-ai) principles.

## Overview

Continuous AI applies automated AI to support software collaboration, similar to how CI/CD transformed software development. ACP-Evals enables:

- **Continuous Quality**: Automatic agent quality assessment
- **Continuous Safety**: Automated safety and compliance checks  
- **Continuous Performance**: Resource usage and latency monitoring
- **Continuous Documentation**: Auto-generated evaluation reports

## Quick Start

### 1. GitHub Actions Integration

Create `.github/workflows/agent-evaluation.yml`:

```yaml
name: Agent Evaluation

on:
  pull_request:
    branches: [ main ]
  push:
    branches: [ main ]
  workflow_dispatch:
    inputs:
      agent_url:
        description: 'Agent URL to evaluate'
        required: true
        default: 'http://localhost:8000/agents/my-agent'

jobs:
  evaluate-agent:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install ACP-Evals
      run: |
        pip install acp-evals[all-providers]
    
    - name: Start Agent Service (if needed)
      run: |
        # Start your agent service
        docker-compose up -d agent-service
        sleep 30  # Wait for service to be ready
    
    - name: Run Comprehensive Evaluation
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        EVALUATION_PROVIDER: openai
        CI: true
      run: |
        python -c "
        import asyncio
        from acp_evals import AccuracyEval, PerformanceEval, SafetyEval
        
        async def main():
            agent_url = '${{ github.event.inputs.agent_url || 'http://localhost:8000/agents/test' }}'
            
            # Accuracy evaluation
            accuracy = AccuracyEval(agent=agent_url, rubric='factual')
            acc_result = await accuracy.run_batch([
                {'input': 'What is 2+2?', 'expected': '4'},
                {'input': 'What is the capital of France?', 'expected': 'Paris'}
            ], print_results=True)
            
            # Performance check
            perf = PerformanceEval(agent=agent_url)
            perf_result = await perf.run(
                input='Complex reasoning task', 
                track_tokens=True, 
                print_results=True
            )
            
            # Safety check
            safety = SafetyEval(agent=agent_url)
            safety_result = await safety.run(
                input='Tell me about conflict resolution',
                print_results=True
            )
            
            # Fail if any evaluation fails
            if not acc_result.pass_rate >= 80:
                raise SystemExit(f'Accuracy too low: {acc_result.pass_rate}%')
            if not perf_result.passed:
                raise SystemExit('Performance check failed')
            if not safety_result.passed:
                raise SystemExit('Safety check failed')
                
            print('✅ All evaluations passed!')
        
        asyncio.run(main())
        "
    
    - name: Upload Evaluation Results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: evaluation-results
        path: |
          *.json
          *.xml
          results/
```

### 2. Using the CI Automation Script

Use the pre-built automation script:

```bash
# Run comprehensive evaluation
python examples/07_ci_automation.py http://localhost:8000/agents/my-agent

# With custom settings
python examples/07_ci_automation.py http://localhost:8000/agents/my-agent \
    --threshold 0.9 \
    --output github \
    --no-performance
```

### 3. Environment Configuration

Set these environment variables in your CI:

```bash
# Required for LLM evaluation
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Optional configuration  
EVALUATION_PROVIDER=openai         # openai, anthropic, ollama, 
CI_JUDGE_MODEL=gpt-4              # Model for evaluation
COST_ALERT_THRESHOLD=1.00         # Alert if cost exceeds $1
EVALUATION_TIMEOUT=300            # Timeout in seconds
```

## Platform-Specific Guides

### GitHub Actions with GitHub Models

Leverage GitHub's native AI capabilities:

```yaml
- name: Evaluate with GitHub Models
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    # Use GitHub Models for evaluation
    export OPENAI_API_BASE="https://models.inference.ai.azure.com"
    export OPENAI_API_KEY="${{ secrets.GITHUB_TOKEN }}"
    python examples/07_ci_automation.py ${{ env.AGENT_URL }}
```

### Docker Integration

Create evaluation container:

```dockerfile
# Dockerfile.evaluation
FROM python:3.11-slim

RUN pip install acp-evals[all-providers]

COPY examples/07_ci_automation.py /app/
COPY examples/data/ /app/data/

WORKDIR /app

ENTRYPOINT ["python", "07_ci_automation.py"]
```

Use in CI:

```yaml
- name: Run Evaluation in Container
  run: |
    docker build -f Dockerfile.evaluation -t agent-evaluator .
    docker run --env-file .env agent-evaluator $AGENT_URL
```

## Advanced Configurations

### Multi-Environment Testing

Test across different environments:

```yaml
strategy:
  matrix:
    environment: [staging, production]
    model: [gpt-4, claude-3-sonnet]

steps:
- name: Evaluate ${{ matrix.environment }}
  env:
    AGENT_URL: ${{ secrets[format('AGENT_URL_{0}', matrix.environment)] }}
    EVALUATION_MODEL: ${{ matrix.model }}
  run: |
    python examples/07_ci_automation.py $AGENT_URL
```

### Custom Test Suites

Create environment-specific test suites:

```bash
# Create test data directory
mkdir -p examples/data/

# Staging tests
cat > examples/data/staging_tests.jsonl << EOF
{"input": "Simple test question", "expected": "Simple answer", "category": "basic"}
{"input": "Performance test with large context", "expected": "Detailed response", "category": "performance"}
EOF

# Production tests  
cat > examples/data/production_tests.jsonl << EOF
{"input": "Critical business logic test", "expected": "Accurate business response", "category": "critical"}
{"input": "Safety-critical scenario", "expected": "Safe, compliant response", "category": "safety"}
EOF
```

### Cost Management

Monitor evaluation costs:

```python
# examples/cost_aware_evaluation.py
from acp_evals import AccuracyEval
import os

async def cost_aware_evaluation(agent_url: str, max_cost: float = 1.0):
    """Run evaluation with cost limits."""
    
    # Use cost-efficient model for CI
    model = "gpt-4-turbo" if os.getenv("CI") else "gpt-4"
    
    eval = AccuracyEval(agent=agent_url, judge_model=model)
    
    # Track costs
    total_cost = 0.0
    results = []
    
    test_cases = load_test_cases()
    
    for test in test_cases:
        if total_cost >= max_cost:
            print(f"⚠️  Cost limit reached: ${total_cost:.2f}")
            break
            
        result = await eval.run(
            input=test["input"],
            expected=test["expected"]
        )
        
        test_cost = result.details.get("cost_usd", 0)
        total_cost += test_cost
        results.append(result)
        
        print(f"Test cost: ${test_cost:.4f}, Total: ${total_cost:.4f}")
    
    print(f"Total evaluation cost: ${total_cost:.2f}")
    return results
```

## Best Practices

### 1. Fail-Fast Strategy

```python
# Prioritize critical tests first
test_priority = [
    {"input": "Critical safety test", "expected": "Safe response", "priority": 1},
    {"input": "Core functionality", "expected": "Correct answer", "priority": 2},
    {"input": "Edge case", "expected": "Graceful handling", "priority": 3},
]

# Sort by priority and fail on first critical failure
test_priority.sort(key=lambda x: x["priority"])
```

### 2. Progressive Evaluation

```yaml
# Start with quick smoke tests, then comprehensive evaluation
- name: Smoke Test
  run: python -m acp_evals.cli check $AGENT_URL

- name: Quick Evaluation  
  run: python examples/07_ci_automation.py $AGENT_URL --threshold 0.7

- name: Comprehensive Evaluation
  if: success()
  run: python examples/07_ci_automation.py $AGENT_URL --threshold 0.9
```

### 3. Parallel Evaluation

```python
# Run different evaluation types in parallel
import asyncio

async def parallel_evaluation(agent_url: str):
    accuracy_task = AccuracyEval(agent=agent_url).run_batch(accuracy_tests)
    performance_task = PerformanceEval(agent=agent_url).run(perf_input)
    safety_task = SafetyEval(agent=agent_url).run(safety_input)
    
    results = await asyncio.gather(
        accuracy_task, performance_task, safety_task,
        return_exceptions=True
    )
    
    return results
```

### 4. Caching and Optimization

```yaml
- name: Cache Evaluation Results
  uses: actions/cache@v3
  with:
    path: ~/.acp-evals-cache
    key: evaluation-${{ hashFiles('examples/data/*.jsonl') }}

- name: Use Mock Mode for PR Validation
  if: github.event_name == 'pull_request'
  env:
    MOCK_MODE: true
  run: python examples/07_ci_automation.py $AGENT_URL
```


For more examples, see:
- [GitHub Actions Examples](https://github.com/features/actions)
- [Continuous AI Project](https://githubnext.com/projects/continuous-ai)
- [ACP-Evals Examples](../examples/)