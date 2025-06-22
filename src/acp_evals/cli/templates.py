"""Templates for the init command."""

TEMPLATES = {
    "simple": """#!/usr/bin/env python3
\"\"\"
Simple evaluation example for {agent_name}.

This template shows how to evaluate a basic agent.
\"\"\"

import asyncio
from acp_evals import AccuracyEval

# Your agent (can be URL, callable, or agent instance)
AGENT = "{agent_url}"

async def evaluate_agent():
    \"\"\"Run a simple accuracy evaluation.\"\"\"

    # Create evaluator
    eval = AccuracyEval(
        agent=AGENT,
        rubric="factual"  # or "research_quality", "code_quality"
    )

    # Single evaluation
    result = await eval.run(
        input="What is the capital of France?",
        expected="Paris",
        print_results=True
    )

    print(f"\\nScore: {{result.score}}")
    print(f"Passed: {{result.passed}}")
    print(f"Cost: ${{result.cost:.4f}}")

    # Batch evaluation
    test_cases = [
        {{"input": "What is 2+2?", "expected": "4"}},
        {{"input": "Name the largest planet", "expected": "Jupiter"}},
        {{"input": "What language is this code written in?", "expected": "Python"}}
    ]

    batch_results = await eval.run_batch(
        test_cases=test_cases,
        print_results=True
    )

    print(f"\\nBatch Results:")
    print(f"Pass rate: {{batch_results.pass_rate:.1f}}%")
    print(f"Average score: {{batch_results.avg_score:.2f}}")

if __name__ == "__main__":
    asyncio.run(evaluate_agent())
""",
    "comprehensive": """#!/usr/bin/env python3
\"\"\"
Comprehensive evaluation suite for {agent_name}.

Tests accuracy, performance, and reliability.
\"\"\"

import asyncio
from acp_evals import AccuracyEval, PerformanceEval, ReliabilityEval

# Your agent
AGENT = "{agent_url}"

async def run_comprehensive_evaluation():
    \"\"\"Run all three evaluation types.\"\"\"

    print("=== Comprehensive Agent Evaluation ===\\n")

    # 1. Accuracy Evaluation
    print("1. Testing Accuracy...")
    accuracy = AccuracyEval(
        agent=AGENT,
        rubric="factual",
        pass_threshold=0.8
    )

    accuracy_result = await accuracy.run(
        input="Explain the theory of relativity in simple terms",
        expected="A scientific theory about space, time, and gravity by Einstein",
        print_results=True
    )

    # 2. Performance Evaluation
    print("\\n2. Testing Performance...")
    performance = PerformanceEval(
        agent=AGENT,
        num_iterations=5,
        warmup_runs=1
    )

    perf_result = await performance.run(
        input_text="What is the meaning of life?",
        expected=None  # Performance doesn't need expected output
    )

    print(f"Average latency: {{perf_result.details.get('avg_latency_ms', 0):.0f}}ms")
    print(f"Throughput: {{perf_result.details.get('throughput_rps', 0):.2f}} req/s")

    # 3. Reliability Evaluation
    print("\\n3. Testing Reliability...")
    reliability = ReliabilityEval(
        agent=AGENT,
        tool_definitions=["search", "calculate", "summarize"]
    )

    reliability_result = await reliability.run(
        input="Search for information about Mars and calculate its distance from Earth",
        expected_tools=["search", "calculate"]
    )

    print(f"Reliability score: {{reliability_result.score:.2f}}")
    print(f"Tool coverage: {{reliability_result.details.get('tool_coverage', 0):.0%}}")

    # Summary
    print("\\n=== Evaluation Summary ===")
    print(f"Accuracy: {{accuracy_result.score:.2f}} ({'PASS' if accuracy_result.passed else 'FAIL'}})")
    print(f"Performance: {{perf_result.score:.2f}} ({'PASS' if perf_result.passed else 'FAIL'}})")
    print(f"Reliability: {{reliability_result.score:.2f}} ({'PASS' if reliability_result.passed else 'FAIL'}})")

    overall = (accuracy_result.score + perf_result.score + reliability_result.score) / 3
    print(f"\\nOverall Score: {{overall:.2f}}")

    # Cost tracking
    total_cost = (
        accuracy_result.metadata.get('cost', 0) +
        perf_result.metadata.get('cost', 0) +
        reliability_result.metadata.get('cost', 0)
    )
    print(f"Total Cost: ${{total_cost:.4f}}")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_evaluation())
""",
    "research": """#!/usr/bin/env python3
\"\"\"
Research quality evaluation for {agent_name}.

Tests complex reasoning and research capabilities.
\"\"\"

import asyncio
from acp_evals import AccuracyEval

AGENT = "{agent_url}"

# Research-focused test cases
RESEARCH_TASKS = [
    {{
        "input": "Compare and contrast supervised vs unsupervised learning",
        "expected": "Explanation covering labeled data, training approaches, and use cases"
    }},
    {{
        "input": "What are the main challenges in quantum computing?",
        "expected": "Discussion of decoherence, error rates, and scalability"
    }},
    {{
        "input": "Analyze the environmental impact of large language models",
        "expected": "Analysis of energy consumption, carbon footprint, and mitigation strategies"
    }}
]

async def evaluate_research_quality():
    \"\"\"Evaluate agent's research and analysis capabilities.\"\"\"

    print("=== Research Quality Evaluation ===\\n")

    # Use research quality rubric
    eval = AccuracyEval(
        agent=AGENT,
        rubric="research_quality",
        judge_model="gpt-4",  # Use best model for judging
        pass_threshold=0.7
    )

    # Test individual research tasks
    for i, task in enumerate(RESEARCH_TASKS, 1):
        print(f"\\nTask {{i}}: {{task['input'][:50]}}...")

        result = await eval.run(
            input=task["input"],
            expected=task["expected"],
            print_results=False
        )

        print(f"Score: {{result.score:.2f}}")
        print(f"Key strengths: {{result.details.get('strengths', 'N/A')}}")
        print(f"Areas for improvement: {{result.details.get('improvements', 'N/A')}}")

    # Batch evaluation for overall assessment
    print("\\n=== Overall Research Performance ===")
    batch_results = await eval.run_batch(
        test_cases=RESEARCH_TASKS,
        parallel=True,
        print_results=True
    )

    # Detailed analysis
    print(f"\\nDetailed Scoring:")
    print(f"- Accuracy: {{batch_results.score_breakdown.get('accuracy', 0):.2f}}")
    print(f"- Completeness: {{batch_results.score_breakdown.get('completeness', 0):.2f}}")
    print(f"- Reasoning: {{batch_results.score_breakdown.get('reasoning', 0):.2f}}")
    print(f"- Clarity: {{batch_results.score_breakdown.get('clarity', 0):.2f}}")

    # Recommendations
    if batch_results.avg_score < 0.6:
        print("\\nRecommendation: Agent needs improvement in research tasks")
    elif batch_results.avg_score < 0.8:
        print("\\nRecommendation: Agent shows good research capabilities")
    else:
        print("\\nRecommendation: Agent demonstrates excellent research skills")

if __name__ == "__main__":
    asyncio.run(evaluate_research_quality())
""",
    "tool": """#!/usr/bin/env python3
\"\"\"
Tool usage evaluation for {agent_name}.

Tests how well the agent uses available tools.
\"\"\"

import asyncio
from acp_evals import ReliabilityEval

AGENT = "{agent_url}"

# Define available tools
AVAILABLE_TOOLS = [
    "search",      # Web search
    "calculate",   # Mathematical calculations
    "code",        # Code execution
    "database",    # Database queries
    "api_call",    # External API calls
]

# Test scenarios requiring specific tools
TOOL_SCENARIOS = [
    {{
        "input": "Search for the current Bitcoin price and calculate the value of 0.5 BTC",
        "expected_tools": ["search", "calculate"],
        "description": "Multi-tool task"
    }},
    {{
        "input": "Write and execute a Python function to find prime numbers up to 100",
        "expected_tools": ["code"],
        "description": "Code execution"
    }},
    {{
        "input": "Query the user database for active users in the last 30 days",
        "expected_tools": ["database"],
        "description": "Database operation"
    }},
    {{
        "input": "Get weather data from OpenWeatherMap API for New York",
        "expected_tools": ["api_call"],
        "description": "External API usage"
    }}
]

async def evaluate_tool_usage():
    \"\"\"Evaluate how well the agent uses tools.\"\"\"

    print("=== Tool Usage Evaluation ===\\n")
    print(f"Available tools: {{', '.join(AVAILABLE_TOOLS)}}\\n")

    # Create reliability evaluator
    eval = ReliabilityEval(
        agent=AGENT,
        tool_definitions=AVAILABLE_TOOLS
    )

    # Test each scenario
    results = []
    for scenario in TOOL_SCENARIOS:
        print(f"\\nTesting: {{scenario['description']}}")
        print(f"Task: {{scenario['input'][:60]}}...")
        print(f"Expected tools: {{', '.join(scenario['expected_tools'])}}")

        result = await eval.run(
            input=scenario["input"],
            expected_tools=scenario["expected_tools"],
            test_error_handling=True
        )

        results.append(result)

        # Display results
        tools_used = result.details.get("tools_used", [])
        print(f"Tools used: {{', '.join(tools_used) if tools_used else 'None'}}")
        print(f"Coverage: {{result.details.get('tool_coverage', 0):.0%}}")
        print(f"Score: {{result.score:.2f}}")

        # Check for issues
        if unexpected := result.details.get("unexpected_tools", []):
            print(f"⚠️  Unexpected tools used: {{', '.join(unexpected)}}")

    # Overall assessment
    print("\\n=== Tool Usage Summary ===")
    avg_score = sum(r.score for r in results) / len(results)
    print(f"Average score: {{avg_score:.2f}}")

    # Tool usage statistics
    all_tools_used = set()
    for r in results:
        all_tools_used.update(r.details.get("tools_used", []))

    print(f"\\nUnique tools used: {{len(all_tools_used)}}/{{len(AVAILABLE_TOOLS)}}")
    print(f"Tools utilized: {{', '.join(sorted(all_tools_used))}}")

    unused_tools = set(AVAILABLE_TOOLS) - all_tools_used
    if unused_tools:
        print(f"Unused tools: {{', '.join(sorted(unused_tools))}}")

    # Error handling
    error_handling_passed = all(
        r.details.get("error_handling", {{}}).get("passed", True)
        for r in results
    )
    print(f"\\nError handling: {{'PASS' if error_handling_passed else 'FAIL'}}")

if __name__ == "__main__":
    asyncio.run(evaluate_tool_usage())
""",
    "acp-agent": """#!/usr/bin/env python3
\"\"\"
ACP agent evaluation example.

Shows how to evaluate agents running on the ACP protocol.
\"\"\"

import asyncio
from acp_evals import AccuracyEval, PerformanceEval

# ACP Agent URL - replace with your agent
AGENT_URL = "{agent_url}"

async def evaluate_acp_agent():
    \"\"\"Evaluate a real ACP agent.\"\"\"

    # Option 1: Direct URL evaluation
    print("=== Direct ACP Agent Evaluation ===")
    eval = AccuracyEval(
        agent=AGENT_URL,
        rubric="factual"
    )

    result = await eval.run(
        input="What are the key features of the ACP protocol?",
        expected="The Agent Communication Protocol (ACP) enables seamless agent-to-agent communication",
        print_results=True
    )

    # Option 2: Batch evaluation with real scenarios
    print("\\n=== Batch Evaluation ===")
    acp_test_cases = [
        {{
            "input": "What is ACP?",
            "expected": "Agent Communication Protocol"
        }},
        {{
            "input": "How do agents communicate in ACP?",
            "expected": "Through standardized message formats and endpoints"
        }},
        {{
            "input": "What are the benefits of using ACP?",
            "expected": "Interoperability, standardization, and scalability"
        }}
    ]

    batch_results = await eval.run_batch(
        test_cases=acp_test_cases,
        parallel=True,
        print_results=True
    )

    print(f"\\nBatch evaluation complete!")
    print(f"Pass rate: {{batch_results.pass_rate:.1f}}%")
    print(f"Average score: {{batch_results.avg_score:.2f}}")

if __name__ == "__main__":
    # Run the evaluation
    asyncio.run(evaluate_acp_agent())
""",
}
