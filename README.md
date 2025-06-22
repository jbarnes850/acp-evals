# ACP Evals

**Production-grade evaluation framework for ACP agents with LLM-powered assessment**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org)
[![ACP Compatible](https://img.shields.io/badge/ACP-Compatible-green.svg)](https://agentcommunicationprotocol.dev)
[![Apache License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

<a href="./docs">Documentation</a> • 
<a href="./examples">Examples</a> • 
<a href="#quick-start">Quick Start</a> • 
<a href="./CONTRIBUTING.md">Contributing</a>

---

## Test Your Agent in 3 Lines

```python
from acp_evals import AccuracyEval

result = await AccuracyEval("http://localhost:8001/agents/my-agent").run(
    input="What is 2+2?", 
    expected="4"
)
print(f"Score: {result.score}")  # Score: 1.00
```

ACP Evals provides three evaluators for testing AI agents with real LLM-powered assessment using GPT-4, Claude, or Ollama.

## Evaluators

### AccuracyEval
LLM-powered evaluation of response quality against expected outputs:
```python
eval = AccuracyEval(agent_url, rubric="factual")
result = await eval.run(input="What is the capital of France?", expected="Paris")
```

### PerformanceEval
Measure response latency and resource efficiency:
```python
eval = PerformanceEval(agent_url, track_tokens=True)
result = await eval.run(input="Generate a haiku")
```

### ReliabilityEval
Assess consistency and tool usage patterns:
```python
eval = ReliabilityEval(agent_url)
result = await eval.run(input="Search and calculate", expected_tools=["search", "calculator"])
```

## Features

- **Complete LLM Transparency**: Full input/expected/actual output comparison with detailed LLM judge reasoning
- **Professional CLI Display**: Rich terminal output with visual score bars, comprehensive panels, and structured feedback
- **No Text Truncation**: See complete agent responses and evaluation details for informed decision-making
- **Detailed Score Breakdown**: Individual criterion scores with 3-decimal precision (e.g., 1.000 vs 0.847)
- **Performance Context**: Response time analysis with user experience impact assessment
- **Multiple Evaluation Types**: Accuracy (LLM-as-judge), Performance (latency/efficiency), Reliability (tool usage)
- **Flexible Input**: ACP agents, Python functions, or file references
- **Multiple Rubrics**: factual, research_quality, code_quality evaluation criteria
- **Export Results**: JSON output for CI/CD integration

## Prerequisites

- Python 3.11 or newer
- LLM API key (OpenAI, Anthropic, or local Ollama)
- Agent to evaluate (ACP-compatible or Python function)

## Installation

### From PyPI

```bash
pip install acp-evals
```

### From Source

```bash
git clone https://github.com/jbarnes850/acp-evals.git
cd acp-evals
pip install -e .
```

## Quick Start

### 1. Configure Provider

```bash
# Create configuration file
echo "OPENAI_API_KEY=your-key-here" > .env

# Verify setup
acp-evals check
```

Expected output:
```
ACP Evals Provider Configuration Check

Found .env file at: /path/to/.env
                      Provider Status                       
╭───────────┬────────────┬────────────────────────┬────────╮
│ Provider  │ Configured │ Model                  │ Status │
├───────────┼────────────┼────────────────────────┼────────┤
│ Openai    │ Yes        │ gpt-4.1                │ —      │
│ Anthropic │ Yes        │ claude-sonnet-4-20250514│ —      │
│ Ollama    │ Yes        │ qwen3:8b               │ —      │
╰───────────┴────────────┴────────────────────────┴────────╯

All providers configured!
Run 'acp-evals check --test-connection' to verify connectivity
```

### 2. Evaluate with CLI

```bash
# Accuracy evaluation
acp-evals run accuracy my_agent.py:agent_function -i "What is 2+2?" -e "4"

# Performance evaluation  
acp-evals run performance my_agent.py:agent_function -i "Complex task" --track-latency

# Reliability evaluation
acp-evals run reliability my_agent.py:agent_function -i "Use tools" --expected-tools search
```

## CLI Command Examples

### Accuracy Evaluation

```bash
acp-evals run accuracy agent.py:my_agent -i "What is 2+2?" -e "4"
```

Output:
```
Running Accuracy Evaluation
Agent: test_agent.py:smart_agent
Input: What is the capital of France?

⠙ Complete!
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                          Accuracy Evaluation Result                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

                               Evaluation Context                               
                                                                                
   Agent: test_agent.py:smart_agent                                             
   Input: What is the capital of France?                                        
                                                                                
                                                                                

╭───────────────────────────── Evaluation Scores ──────────────────────────────╮
│                                                                              │
│  Accuracy Score                                                              │
│  ████████████████████ 1.000 (100.0%)                                         │
│                                                                              │
│    Similarity    ████████████████████ 1.000                                  │
│    Response Speed ████████████████████ 1.000                                 │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯

╭────────────────────── Complete LLM Evaluation Analysis ──────────────────────╮
│                                                                              │
│  Input:                                                                      │
│  What is the capital of France?                                              │
│                                                                              │
│  Expected Output:                                                            │
│  Paris                                                                       │
│                                                                              │
│  Actual LLM Output:                                                          │
│  Paris is the capital of France. It has been the political and cultural      │
│  center of France for over a thousand years.                                 │
│                                                                              │
│  Overall Score (factual rubric):                                             │
│  ████████████████████ 1.000                                                  │
│                                                                              │
│  Score Breakdown:                                                            │
│    Similarity: ███████████████ 1.000                                         │
│                                                                              │
│  LLM Judge Reasoning:                                                        │
│  The response is factually accurate, directly answers the question with      │
│  "Paris," and provides relevant additional information. It fully matches     │
│  the expected output.                                                        │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯

╭──────────────────────────── Performance Analysis ────────────────────────────╮
│                                                                              │
│  Response Time Analysis:                                                     │
│  Time: 0.4ms - Excellent - Sub-200ms response                                │
│  Impact: Real-time user experience                                           │
│                                                                              │
│  Detailed Performance:                                                       │
│                                                                              │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯

╔════════════════════════════════ Final Result ════════════════════════════════╗
║  PASSED                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### Performance Evaluation

```bash
acp-evals run performance test_agent.py:smart_agent -i "Tell me about Jupiter" --track-latency
```

Output:
```
Running Performance Evaluation
Agent: test_agent.py:smart_agent
Input: Tell me about Jupiter

╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                        Performance Evaluation Result                         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

                               Evaluation Context                               
                                                                                
   Agent: test_agent.py:smart_agent                                             
   Input: Tell me about Jupiter                                                 
                                                                                
                                                                                

╭───────────────────────────── Evaluation Scores ──────────────────────────────╮
│                                                                              │
│  Performance Score                                                           │
│  ████████████████████ 1.000 (100.0%)                                         │
│                                                                              │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯

╔════════════════════════════════ Final Result ════════════════════════════════╗
║  PASSED                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### Code Quality Evaluation

```bash
acp-evals run accuracy test_agent.py:smart_agent -i "Write a Python function to check if a number is prime" -e "A function that correctly identifies prime numbers" --rubric code_quality
```

Output:
```
Running Accuracy Evaluation
Agent: test_agent.py:smart_agent
Input: Write a Python function to check if a number is prime

⠸ Complete!
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                          Accuracy Evaluation Result                          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

                               Evaluation Context                               
                                                                                
   Agent: test_agent.py:smart_agent                                             
   Input: Write a Python function to check if a number is prime                 
                                                                                
                                                                                

╭───────────────────────────── Evaluation Scores ──────────────────────────────╮
│                                                                              │
│  Accuracy Score                                                              │
│  ████████████████████ 1.000 (100.0%)                                         │
│                                                                              │
│    Similarity    ████████████████████ 1.000                                  │
│    Response Speed ████████████████████ 1.000                                 │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯

╭────────────────────── Complete LLM Evaluation Analysis ──────────────────────╮
│                                                                              │
│  Input:                                                                      │
│  Write a Python function to check if a number is prime                       │
│                                                                              │
│  Expected Output:                                                            │
│  A function that correctly identifies prime numbers                          │
│                                                                              │
│  Actual LLM Output:                                                          │
│  def is_prime(n):                                                            │
│      if n < 2:                                                               │
│          return False                                                        │
│      for i in range(2, int(n**0.5) + 1):                                     │
│          if n % i == 0:                                                      │
│              return False                                                    │
│      return True                                                             │
│                                                                              │
│  Overall Score (factual rubric):                                             │
│  ████████████████████ 1.000                                                  │
│                                                                              │
│  Score Breakdown:                                                            │
│    Similarity: ███████████████ 1.000                                         │
│                                                                              │
│  LLM Judge Reasoning:                                                        │
│  The response provides a correct, complete, and efficient implementation of  │
│  a function to check if a number is prime. It accurately handles edge cases  │
│  (numbers less than 2) and uses an optimal loop up to the square root of n.  │
│  The function is relevant and fully meets the expected output.               │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯

╭──────────────────────────── Performance Analysis ────────────────────────────╮
│                                                                              │
│  Response Time Analysis:                                                     │
│  Time: 0.1ms - Excellent - Sub-200ms response                                │
│  Impact: Real-time user experience                                           │
│                                                                              │
│  Detailed Performance:                                                       │
│                                                                              │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯

╔════════════════════════════════ Final Result ════════════════════════════════╗
║  PASSED                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

### Batch Test Results

```bash
acp-evals test test_agent.py:smart_agent --quick
```

Output:
```
ACP Agent Testing
Agent: test_agent.py:smart_agent
Test Suite: quick

Using provider: openai

⠼ Complete!
⠴ Complete!
⠏ Complete!
⠏ Quick tests complete
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                            ACP Evaluation Report                             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

╭─────────────────────────────── Score Summary ────────────────────────────────╮
│                                                                              │
│  Overall Score: ██████░░░░░░░░░░░░░░ 33%                                     │
│                                                                              │
│  Overall         ██████░░░░░░░░░░░░░░ 33%                                    │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯

╭──────────────────────────────── Test Results ────────────────────────────────╮
│                                                                              │
│  Test Details (1 passed, 2 failed)                                           │
│                                                                              │
│  ├── ✓ Basic Q&A → Score: 1.00                                               │
│  ├── ✗ Simple Math → Score: 0.00                                             │
│  └── ✗ Factual Knowledge → Score: 0.00                                       │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯

  Evaluation Metrics   
╭─────────────┬───────╮
│ Metric      │ Value │
├─────────────┼───────┤
│ Total Tests │ 3     │
│ Passed      │ 1     │
│ Failed      │ 2     │
│ Pass Rate   │ 33.3% │
│ Suite Name  │ Quick │
╰─────────────┴───────╯

Test failed: Pass rate 33.3% below threshold 60.0%
```

### Multi-Dimensional Evaluation

The `comprehensive` command runs all three evaluators and displays unified results with full LLM visibility:

```bash
acp-evals comprehensive agent.py:my_agent -i "Explain machine learning" -e "ML enables computers to learn from data" --show-details
```

**Dashboard View:**
```
Running Agent Evaluation
Agent: agent.py:my_agent
Input: Explain machine learning

╔════════════════════ AGENT EVALUATION DASHBOARD ═════════════════════╗
║                                                                      ║
║  Agent: agent.py:my_agent                                            ║
║                                                                      ║
║  Evaluation Breakdown:                                               ║
║                                                                      ║
║  Accuracy                                                            ║
║  ████████████████████ 1.000 (100.0%)                                 ║
║                                                                      ║
║    Similarity       ████████████████████ 1.000                       ║
║    Response Speed   ████████████████████ 1.000                       ║
║  Performance                                                         ║
║  ████████████████████ 1.000 (100.0%)                                 ║
║                                                                      ║
║    Response Time    ████████████████████ 1.000                       ║
║    Memory Usage     ████████████████████ 1.000                       ║
║  Reliability                                                         ║
║  ░░░░░░░░░░░░░░░░░░░░ 0.000 (0.0%)                                   ║
║                                                                      ║
║    Error Handling   ████████████████████ 1.000                       ║
║                                                                      ║
║  Overall Assessment:                                                 ║
║  ████████████████░░░░░░░░░ 0.667 (66.7%)                             ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

**LLM Evaluation Analysis (with --show-details):**
```
ACCURACY ANALYSIS:

╭──────────────────────── LLM EVALUATION ANALYSIS ────────────────────────╮
│                                                                          │
│   EVALUATION METHODOLOGY:                                                │
│   Rubric: FACTUAL                                                        │
│   Judge Model: GPT-4 (LLM-as-Judge)                                      │
│   Evaluation Type: Semantic similarity and quality assessment            │
│                                                                          │
│   USER INPUT:                                                            │
│   Explain machine learning and its core approaches                       │
│                                                                          │
│   ↑ Input provided to agent under evaluation                             │
│                                                                          │
│   EXPECTED OUTPUT:                                                       │
│   Machine learning enables computers to learn from data using            │
│   supervised, unsupervised, and reinforcement learning methods           │
│                                                                          │
│   ↑ Target response for this evaluation                                  │
│                                                                          │
│   AGENT OUTPUT:                                                          │
│   Machine Learning (ML) is a subset of artificial intelligence that      │
│   enables computers to learn and make decisions from data without being  │
│   explicitly programmed for every task. The three primary approaches     │
│   are: (1) Supervised Learning - where algorithms learn from labeled     │
│   training data to make predictions on new data, (2) Unsupervised        │
│   Learning - where algorithms find hidden patterns in data without       │
│   labeled examples, and (3) Reinforcement Learning - where agents learn  │
│   optimal actions through trial and error with reward feedback.          │
│   Applications include recommendation systems, image recognition,         │
│   natural language processing, autonomous vehicles, and predictive       │
│   analytics.                                                             │
│                                                                          │
│   ↑ Response generated by agent                                          │
│                                                                          │
│   LLM JUDGE PROCESS:                                                     │
│   1. Input Analysis: Analyzed user input for context and requirements    │
│   2. Response Comparison: Compared agent output against expected output  │
│   3. Quality Assessment: Evaluated response using factual criteria       │
│   4. Score Calculation: Assigned numerical scores based on rubric        │
│                                                                          │
│   EVALUATION USAGE:                                                      │
│   Total Tokens: 1,247 (Input: 823, Output: 424)                         │
│   Estimated Cost: $0.0186                                                │
│                                                                          │
│   FINAL SCORE (FACTUAL RUBRIC):                                          │
│   ██████████████████████████████ 1.000 (100%)                           │
│                                                                          │
│   SCORE BREAKDOWN:                                                       │
│   Individual criterion scores:                                           │
│     Similarity     : █████████████████████████ 1.000                    │
│     Completeness   : █████████████████████████ 1.000                    │
│     Relevance      : █████████████████████████ 1.000                    │
│                                                                          │
│   LLM JUDGE REASONING:                                                   │
│   Explanation of scoring decisions:                                      │
│                                                                          │
│   The response is factually accurate, clearly explains what machine      │
│   learning is, and describes the three core approaches (supervised,      │
│   unsupervised, and reinforcement learning) as expected. It also         │
│   provides relevant examples and applications, adding value without      │
│   deviating from the core topic. The response demonstrates good          │
│   understanding and exceeds the minimum requirements while maintaining   │
│   accuracy.                                                              │
│                                                                          │
│   ↑ How the LLM judge arrived at the scores above                        │
│                                                                          │
╰──────────────────────────────────────────────────────────────────────────╯

PERFORMANCE ANALYSIS:

╭─────────────────────── Performance Analysis ───────────────────────╮
│                                                                     │
│  Response Time Analysis:                                            │
│  Time: 2.1ms - Excellent - Sub-200ms response                      │
│  Impact: Real-time user experience                                 │
│                                                                     │
│  Memory Usage Analysis:                                             │
│  Usage: 15.2MB - Efficient                                         │
│  Assessment: Optimal resource utilization                          │
│                                                                     │
│  Token Efficiency:                                                  │
│  Input/Output Ratio: 1.8x - Balanced verbosity                     │
│  Assessment: Appropriate detail level                              │
│                                                                     │
╰─────────────────────────────────────────────────────────────────────╯

RELIABILITY ANALYSIS:

╭─────────────────── Reliability Analysis ──────────────────╮
│                                                            │
│  Reliability Metrics:                                      │
│  Consistency: ████████████████████ 1.000 - Excellent      │
│  Error Rate: 0.0% - Excellent                             │
│  Tool Coverage: N/A (No tools expected)                    │
│                                                            │
│  Execution Analysis:                                       │
│  Total Events: 1                                          │
│    • function_call: 1 (100.0%)                            │
│    • error_handling: 0 (0.0%)                             │
│                                                            │
│  Assessment: Agent executed without errors                │
│                                                            │
╰────────────────────────────────────────────────────────────╯

╔═════════════════════ FINAL ASSESSMENT ══════════════════════╗
║  SOME EVALUATIONS FAILED                                    ║
╚══════════════════════════════════════════════════════════════╝
```

**Key Features:**
- **Unified Dashboard**: All three evaluation dimensions with visual score bars in one view
- **Complete LLM Transparency**: Full input/expected/actual output comparison without truncation
- **LLM Judge Methodology**: Clear 4-step evaluation process with complete reasoning trace
- **Performance Context**: Response time analysis with user experience impact assessment
- **Reliability Metrics**: Tool usage patterns, error rates, and execution statistics
- **Visual Score Bars**: Immediate feedback on performance across all dimensions with expanded width
- **Executive Summary**: Combined assessment with clear pass/fail status

**Professional Design Principles:**
- **Zero Text Truncation**: See complete agent responses (500+ characters) for informed decision-making
- **Clear Information Hierarchy**: Primary scores prominent, sub-scores indented, methodology explicit
- **Expanded Display Width**: 120-character width for optimal readability on professional terminals
- **Complete Audit Trail**: Full LLM evaluation reasoning with step-by-step process explanation
- **Contextual Analysis**: Performance metrics interpreted with real-world impact assessments
- **No Emoji Clutter**: Clean, professional interface designed for enterprise software engineers

### Available Rubrics

```bash
acp-evals list-rubrics
```

Shows factual, research_quality, and code_quality rubrics with detailed criteria.

## Programmatic Usage

### Single Evaluation

```python
import asyncio
from acp_evals import AccuracyEval

async def main():
    eval = AccuracyEval("http://localhost:8001/agents/my-agent", rubric="factual")
    
    result = await eval.run(
        input="What is the capital of France?",
        expected="Paris",
        print_results=True
    )
    
    print(f"Score: {result.score}")
    print(f"Passed: {result.passed}")
    print(f"Feedback: {result.details['feedback']}")

asyncio.run(main())
```

### Batch Evaluation

```python
async def batch_test():
    eval = AccuracyEval("http://localhost:8001/agents/my-agent")
    
    test_cases = [
        {"input": "What is 2+2?", "expected": "4"},
        {"input": "Capital of France?", "expected": "Paris"},
        {"input": "Largest planet?", "expected": "Jupiter"}
    ]
    
    results = await eval.run_batch(test_cases, print_results=True)
    print(f"Pass rate: {results.pass_rate}%")
    print(f"Average score: {results.avg_score}")
```

## Agent Input Formats

ACP Evals supports multiple agent input formats:

```bash
# ACP URL
acp-evals run accuracy http://localhost:8001/agents/my-agent -i "test" -e "result"

# Python file with function
acp-evals run accuracy agent.py:function_name -i "test" -e "result"

# Python module
acp-evals run accuracy mymodule.agent_function -i "test" -e "result"
```

## Understanding Results

### Scores
- **1.000** - Perfect response quality (shown with 3-decimal precision)
- **0.700+** - Good quality (default pass threshold)
- **<0.700** - Needs improvement

### Complete LLM Evaluation Display
All accuracy evaluations show:
- **Full Input**: Complete question or prompt without truncation
- **Full Expected Output**: Complete expected response without truncation  
- **Full Actual LLM Output**: Complete agent response without truncation
- **Score Breakdown**: Individual criterion scores (accuracy, completeness, relevance, etc.)
- **Complete LLM Judge Reasoning**: Full explanation of why the score was assigned
- **Performance Analysis**: Response time with user experience context

No simple text matching - all evaluations use real LLM assessment with complete transparency.

## CLI Commands

```bash
# Configuration
acp-evals check                    # Verify provider setup
acp-evals list-rubrics            # Show evaluation criteria

# Discovery
acp-evals discover                # Find ACP agents
acp-evals quick-start            # Interactive setup wizard

# Evaluation
acp-evals run accuracy <agent> -i <input> -e <expected> [--rubric <rubric>]
acp-evals run performance <agent> -i <input> [--track-tokens] [--track-latency]
acp-evals run reliability <agent> -i <input> [--expected-tools <tool1> <tool2>]

# Comprehensive Evaluation (NEW)
acp-evals comprehensive <agent> -i <input> -e <expected> [--show-details]

# Testing
acp-evals test <agent>           # Quick comprehensive test
acp-evals init <template>        # Generate evaluation template
```

## Common Issues

**"No providers configured"**
```bash
echo "OPENAI_API_KEY=your-key" > .env
acp-evals check
```

**"Failed to connect to agent"**
```bash
# Check agent is running
curl http://localhost:8001/agents

# Test with Python function instead
acp-evals run accuracy my_agent.py:my_function -i "test" -e "result"
```

**"LLM evaluation failed"**
Ensure valid API key and network connectivity. No fallbacks to simple text matching.

## Examples

The [examples](./examples) directory contains:
- BeeAI ACP server integration
- Custom evaluation scripts
- Python function agents

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for development guidelines.

## License

Apache 2.0 - see [LICENSE](./LICENSE)