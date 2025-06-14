# Contributing to ACP Evals

Thank you for your interest in contributing to ACP Evals! This guide will help you get started.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and constructive in all interactions.

## How to Contribute

### Reporting Issues

1. Check if the issue already exists
2. Include a clear description of the problem
3. Provide steps to reproduce
4. Include relevant code snippets or error messages
5. Specify your environment (OS, Python version, etc.)

### Suggesting Features

1. Open a discussion first to gauge interest
2. Describe the use case and benefits
3. Consider implementation complexity
4. Be open to feedback and alternative approaches

### Contributing Code

#### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/i-am-bee/acp-evals
cd acp-evals

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
cd python
pip install -e ".[dev]"
```

#### Development Workflow

1. **Fork the repository** on GitHub
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following our coding standards
4. **Write/update tests** for your changes
5. **Run tests**:
   ```bash
   pytest
   ```
6. **Run linting**:
   ```bash
   ruff check .
   ruff format .
   ```
7. **Commit your changes**:
   ```bash
   git commit -m "feat: add new metric for X"
   ```
8. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
9. **Create a Pull Request** on GitHub

#### Commit Message Convention

We follow conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `chore:` Maintenance tasks

Examples:
```
feat: add response time percentile metrics
fix: correct token counting for multi-part messages
docs: update benchmark creation guide
```

### Areas for Contribution

#### High Priority

1. **New Benchmarks**
   - Domain-specific benchmarks (legal, medical, finance)
   - Multi-language support benchmarks
   - Tool-use evaluation benchmarks
   - Long-context benchmarks

2. **Additional Metrics**
   - Semantic similarity metrics
   - Factuality checking
   - Bias detection
   - Safety metrics

3. **Framework Enhancements**
   - Real-time evaluation dashboard
   - Parallel benchmark execution
   - Result visualization tools
   - CI/CD integration plugins

#### Good First Issues

- Add more distractor contexts to `core_tasks.py`
- Implement additional cost models for new LLMs
- Add examples for specific use cases
- Improve error messages and logging
- Add type hints where missing

### Code Standards

#### Python Style

- Follow PEP 8
- Use type hints for all public APIs
- Maximum line length: 100 characters
- Use descriptive variable names
- Add docstrings to all public functions/classes

Example:
```python
from typing import List, Optional
from acp_evals.base import Metric, MetricResult

class CustomMetric(Metric):
    """
    Brief description of what this metric measures.
    
    Longer description explaining when and why to use this metric,
    including any important considerations.
    
    Args:
        param1: Description of parameter
        param2: Optional parameter description
        
    Example:
        >>> metric = CustomMetric(param1="value")
        >>> result = await metric.calculate(run, events)
    """
    
    def __init__(self, param1: str, param2: Optional[int] = None):
        self.param1 = param1
        self.param2 = param2 or 10
```

#### Testing Requirements

- Write tests for all new features
- Maintain or improve code coverage
- Use `pytest` for testing
- Mock external dependencies
- Test both success and failure cases

Example test:
```python
import pytest
from acp_evals.metrics import TokenUsageMetric

@pytest.mark.asyncio
async def test_token_usage_calculation():
    metric = TokenUsageMetric(model="gpt-4.1")
    
    # Create mock run and events
    mock_run = ...
    mock_events = [...]
    
    result = await metric.calculate(mock_run, mock_events)
    
    assert result.name == "token_usage"
    assert result.value > 0
    assert "cost_usd" in result.breakdown
```

### Documentation

- Update relevant documentation for any changes
- Include docstrings for new code
- Add examples for new features
- Update README if adding major features

### Review Process

1. All PRs require at least one review
2. CI checks must pass
3. No decrease in test coverage
4. Documentation must be updated
5. Commits should be atomic and well-described

### Getting Help

- Check existing documentation
- Look at similar code in the repository
- Ask questions in GitHub Discussions
- Join our Discord community
- Tag maintainers for complex issues

## Recognition

Contributors will be:
- Listed in the project README
- Mentioned in release notes
- Given credit in relevant documentation

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

Thank you for helping make ACP Evals better! 🚀