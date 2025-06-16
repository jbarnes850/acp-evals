"""Templates for the init command."""

TEMPLATES = {
    "simple": """#!/usr/bin/env python3
\"\"\"
Simple evaluation example for {agent_name}.

This template shows how to evaluate a basic agent.
\"\"\"

import asyncio
from acp_evals import AccuracyEval, evaluate

# Define your agent
async def {agent_function}(input_text: str) -> str:
    \"\"\"Your agent implementation.\"\"\"
    # TODO: Implement your agent logic here
    return f"Response to: {input_text}"

# Simple evaluation
def test_basic():
    result = evaluate(
        AccuracyEval(agent={agent_function}),
        input="What is 2+2?",
        expected="4",
        print_results=True
    )
    assert result.passed, f"Test failed with score {{result.score}}"

# Batch evaluation
async def test_batch():
    eval = AccuracyEval(agent={agent_function}, rubric="factual")

    test_cases = [
        {{"input": "What is 2+2?", "expected": "4"}},
        {{"input": "What is the capital of France?", "expected": "Paris"}},
        # Add more test cases
    ]

    batch_result = await eval.run_batch(
        test_cases=test_cases,
        print_results=True,
        export="results.json"
    )

    print(f"\\nPass rate: {{batch_result.pass_rate:.1f}}%")
    print(f"Average score: {{batch_result.avg_score:.2f}}")

if __name__ == "__main__":
    print("Running basic test...")
    test_basic()

    print("\\nRunning batch test...")
    asyncio.run(test_batch())
""",

    "comprehensive": """#!/usr/bin/env python3
\"\"\"
Comprehensive evaluation suite for {agent_name}.

This template includes accuracy, performance, and reliability testing.
\"\"\"

import asyncio
from acp_evals import AccuracyEval, PerformanceEval, ReliabilityEval

class {agent_class}:
    \"\"\"Your agent implementation.\"\"\"

    def __init__(self):
        # TODO: Initialize your agent
        pass

    async def run(self, input_text: str) -> str:
        \"\"\"Process input and return response.\"\"\"
        # TODO: Implement your agent logic
        return f"Response to: {input_text}"

async def evaluate_agent():
    \"\"\"Run comprehensive evaluation suite.\"\"\"
    agent = {agent_class}()

    # 1. Accuracy Evaluation
    print("=== Accuracy Evaluation ===")
    accuracy_eval = AccuracyEval(
        agent=agent,
        rubric={rubric_choice}
    )

    accuracy_result = await accuracy_eval.run(
        input="{sample_input}",
        expected="{sample_expected}",
        print_results=True
    )

    # 2. Performance Evaluation
    print("\\n=== Performance Evaluation ===")
    perf_eval = PerformanceEval(agent=agent)

    perf_result = await perf_eval.run(
        input="{sample_input}",
        track_tokens=True,
        track_latency=True,
        print_results=True
    )

    # 3. Reliability Evaluation
    print("\\n=== Reliability Evaluation ===")
    reliability_eval = ReliabilityEval(
        agent=agent,
        tool_definitions=["search", "calculate", "database"]  # Update with your tools
    )

    reliability_result = await reliability_eval.run(
        input="{sample_input}",
        expected_tools=["search"],  # Update with expected tools
        print_results=True
    )

    # 4. Batch Testing
    print("\\n=== Batch Testing ===")
    test_cases = [
        {{"input": "{sample_input}", "expected": "{sample_expected}"}},
        # Add more test cases here
    ]

    batch_result = await accuracy_eval.run_batch(
        test_cases=test_cases,
        parallel=True,
        print_results=True,
        export="evaluation_results.json"
    )

    return {{
        "accuracy": accuracy_result,
        "performance": perf_result,
        "reliability": reliability_result,
        "batch": batch_result
    }}

if __name__ == "__main__":
    results = asyncio.run(evaluate_agent())
    print("\\nEvaluation complete!")
""",

    "research": """#!/usr/bin/env python3
\"\"\"
Research agent evaluation template.

Specialized for evaluating agents that do research, analysis, and information synthesis.
\"\"\"

import asyncio
from acp_evals import AccuracyEval, PerformanceEval

class ResearchAgent:
    \"\"\"Research agent that searches and synthesizes information.\"\"\"

    async def run(self, query: str) -> str:
        \"\"\"Research a topic and return comprehensive analysis.\"\"\"
        # TODO: Implement your research logic
        # This could include:
        # - Web search
        # - Document analysis
        # - Information synthesis
        # - Source citation

        return f\"\"\"
## Research Results for: {{query}}

### Summary
[Your research summary here]

### Key Findings
1. Finding 1
2. Finding 2
3. Finding 3

### Sources
- Source 1
- Source 2
\"\"\"

async def evaluate_research_agent():
    agent = ResearchAgent()

    # Use research quality rubric
    eval = AccuracyEval(
        agent=agent,
        rubric="research_quality",
        pass_threshold=0.75
    )

    # Test cases for research evaluation
    test_cases = [
        {{
            "input": "What are the latest developments in quantum computing?",
            "expected": {{
                "topics": ["quantum supremacy", "error correction", "hardware advances"],
                "depth": "comprehensive",
                "sources": "multiple credible sources"
            }}
        }},
        {{
            "input": "Compare transformer vs RNN architectures for NLP",
            "expected": {{
                "comparison_aspects": ["performance", "training time", "context window"],
                "balanced": True,
                "technical_accuracy": "high"
            }}
        }}
    ]

    # Run evaluation
    results = await eval.run_batch(
        test_cases=test_cases,
        print_results=True,
        export="research_eval_results.json"
    )

    # Performance testing for research tasks
    perf_eval = PerformanceEval(agent=agent)

    perf_result = await perf_eval.run(
        input="Research the environmental impact of electric vehicles",
        track_latency=True,
        print_results=True
    )

    print(f"\\nResearch Quality Score: {{results.avg_score:.2f}}")
    print(f"Average Response Time: {{perf_result.details['latency_ms']:.0f}}ms")

if __name__ == "__main__":
    asyncio.run(evaluate_research_agent())
""",

    "tool": """#!/usr/bin/env python3
\"\"\"
Tool-using agent evaluation template.

For agents that use external tools like calculators, APIs, databases, etc.
\"\"\"

import asyncio
from typing import Dict, Any, List
from acp_evals import AccuracyEval, ReliabilityEval, PerformanceEval

class ToolAgent:
    \"\"\"Agent that uses various tools to complete tasks.\"\"\"

    def __init__(self):
        self.tools = {{
            "calculator": self._calculator,
            "search": self._search,
            "database": self._database,
            # Add your tools here
        }}
        self.tool_calls = []

    async def _calculator(self, expression: str) -> float:
        \"\"\"Calculator tool.\"\"\"
        # TODO: Implement calculator logic
        return eval(expression)  # Simple example - use safe parser in production

    async def _search(self, query: str) -> List[Dict[str, str]]:
        \"\"\"Search tool.\"\"\"
        # TODO: Implement search logic
        return [{{"title": "Result 1", "snippet": "..."}}]

    async def _database(self, query: str) -> List[Dict[str, Any]]:
        \"\"\"Database tool.\"\"\"
        # TODO: Implement database logic
        return []

    async def run(self, input_text: str) -> str:
        \"\"\"Process input using appropriate tools.\"\"\"
        self.tool_calls = []  # Reset for tracking

        # TODO: Implement tool selection and usage logic
        # Example:
        if "calculate" in input_text.lower():
            result = await self.tools["calculator"]("2+2")
            self.tool_calls.append(("calculator", "2+2"))
            return f"The result is {{result}}"

        return "I need to use tools to answer this."

async def evaluate_tool_agent():
    agent = ToolAgent()

    # 1. Tool Usage Reliability
    print("=== Tool Usage Evaluation ===")
    reliability_eval = ReliabilityEval(
        agent=agent,
        tool_definitions=list(agent.tools.keys())
    )

    tool_test_cases = [
        {{
            "input": "Calculate 25 * 4 + sqrt(16)",
            "expected_tools": ["calculator"],
            "expected_calls": 3
        }},
        {{
            "input": "Search for information about climate change",
            "expected_tools": ["search"],
            "expected_calls": 1
        }}
    ]

    for test in tool_test_cases:
        agent.tool_calls = []
        result = await reliability_eval.run(
            input=test["input"],
            expected_tools=test["expected_tools"],
            print_results=True
        )

        actual_tools = [call[0] for call in agent.tool_calls]
        print(f"Expected tools: {{test['expected_tools']}}")
        print(f"Actually used: {{list(set(actual_tools))}}")
        print(f"Tool calls: {{len(agent.tool_calls)}}\\n")

    # 2. Accuracy with Tools
    print("=== Accuracy Evaluation ===")
    accuracy_eval = AccuracyEval(
        agent=agent,
        rubric={{
            "correctness": {{"weight": 0.5, "criteria": "Are results correct?"}},
            "tool_usage": {{"weight": 0.3, "criteria": "Are tools used appropriately?"}},
            "efficiency": {{"weight": 0.2, "criteria": "Are tools used efficiently?"}}
        }}
    )

    accuracy_result = await accuracy_eval.run(
        input="What is 100 * 50?",
        expected="5000",
        print_results=True
    )

    print(f"\\nOverall tool agent score: {{accuracy_result.score:.2f}}")

if __name__ == "__main__":
    asyncio.run(evaluate_tool_agent())
""",

    "acp-agent": """#!/usr/bin/env python3
\"\"\"
Real ACP agent evaluation example.

Shows how to evaluate agents running on the ACP protocol.
\"\"\"

import asyncio
from acp_evals import AccuracyEval, PerformanceEval
from acp_evals.client import ACPEvaluationClient

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
    
    # Option 2: Using ACP client for advanced features
    print("\\n=== ACP Client Evaluation ===")
    client = ACPEvaluationClient(base_url="{base_url}")
    
    # Discover available agents
    agents = await client.list_agents()
    print(f"Available agents: {{[a.name for a in agents]}}")
    
    # Run with event tracking
    if agents:
        agent_name = agents[0].name
        run, events, metrics = await client.run_with_tracking(
            agent_name=agent_name,
            input="Explain how agents collaborate in ACP",
        )
        
        print(f"\\nRun ID: {{run.id}}")
        print(f"Events collected: {{len(events)}}")
        print(f"Metrics: {{metrics}}")
    
    # Option 3: Batch evaluation with real scenarios
    print("\\n=== Batch Evaluation ===")
    acp_test_cases = [
        {{
            "input": "What is ACP?",
            "expected": "Agent Communication Protocol"
        }},
        {{
            "input": "How do agents discover each other?",
            "expected": "Through the ACP discovery protocol"
        }},
        {{
            "input": "What message format does ACP use?",
            "expected": "JSON-RPC"
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

    "multi-agent": """#!/usr/bin/env python3
\"\"\"
Multi-agent coordination evaluation.

Tests how well multiple agents work together in different patterns.
\"\"\"

import asyncio
from acp_evals.patterns import LinearPattern, SupervisorPattern, SwarmPattern
from acp_evals.benchmarks import HandoffQualityBenchmark
from acp_evals.metrics import HandoffQualityMetric

# Define your agents
AGENTS = {{
    "researcher": "{researcher_url}",
    "analyst": "{analyst_url}",
    "writer": "{writer_url}"
}}

async def evaluate_linear_pattern():
    \"\"\"Test sequential agent coordination.\"\"\"
    print("=== Linear Pattern Evaluation ===")
    
    # Create linear workflow
    pattern = LinearPattern([
        AGENTS["researcher"],
        AGENTS["analyst"],
        AGENTS["writer"]
    ])
    
    # Run handoff benchmark
    benchmark = HandoffQualityBenchmark(
        pattern=pattern,
        endpoint=""  # Using direct URLs
    )
    
    result = await benchmark.evaluate_single(
        task="Research the latest developments in quantum computing and write a summary",
        expected_handoffs=[
            "researcher->analyst",
            "analyst->writer"
        ]
    )
    
    print(f"Handoff Score: {{result.score:.2f}}")
    print(f"Information Preserved: {{result.details.get('preservation_score', 0):.2f}}")
    print(f"Handoffs Completed: {{result.details.get('handoffs_completed', [])}}")

async def evaluate_supervisor_pattern():
    \"\"\"Test centralized coordination.\"\"\"
    print("\\n=== Supervisor Pattern Evaluation ===")
    
    # Supervisor coordinates workers
    pattern = SupervisorPattern(
        supervisor=AGENTS["analyst"],  # Analyst as supervisor
        workers=[AGENTS["researcher"], AGENTS["writer"]]
    )
    
    # Create custom evaluation
    from acp_evals import AccuracyEval
    
    # Test supervisor's ability to coordinate
    supervisor_eval = AccuracyEval(
        agent=pattern,  # Pattern acts as agent
        rubric={{
            "task_decomposition": {{
                "weight": 0.3,
                "criteria": "Does the supervisor break down tasks effectively?"
            }},
            "coordination": {{
                "weight": 0.4,
                "criteria": "Are workers coordinated efficiently?"
            }},
            "result_synthesis": {{
                "weight": 0.3,
                "criteria": "Is the final output well-synthesized?"
            }}
        }}
    )
    
    result = await supervisor_eval.run(
        input="Create a comprehensive report on AI safety, delegating research and writing tasks",
        expected="A well-coordinated report with research and writing properly delegated"
    )
    
    print(f"Coordination Score: {{result.score:.2f}}")
    print(f"Supervisor Effectiveness: {{result.details}}")

async def evaluate_swarm_pattern():
    \"\"\"Test distributed collaboration.\"\"\"
    print("\\n=== Swarm Pattern Evaluation ===")
    
    # All agents collaborate
    pattern = SwarmPattern(list(AGENTS.values()))
    
    # Test emergent behavior
    swarm_tasks = [
        "Collaboratively solve: What are the implications of AGI for society?",
        "Work together to design a sustainable city of the future",
        "Jointly create a business plan for a Mars colony"
    ]
    
    for task in swarm_tasks:
        result = await pattern.run(task)
        print(f"\\nTask: {{task[:50]}}...")
        print(f"Agents participated: {{result.metadata.get('agents_used', 'Unknown')}}")
        print(f"Consensus reached: {{result.metadata.get('consensus', False)}}")

async def compare_patterns():
    \"\"\"Compare different coordination patterns.\"\"\"
    print("\\n=== Pattern Comparison ===")
    
    from acp_evals.benchmarks.multi_agent import PatternComparisonBenchmark
    
    comparison = PatternComparisonBenchmark(
        agents=AGENTS,
        patterns=["linear", "supervisor", "swarm"]
    )
    
    # Run comparison on multiple tasks
    comparison_tasks = [
        "Research and analyze market trends",
        "Create a technical documentation",
        "Solve a complex problem requiring multiple perspectives"
    ]
    
    results = await comparison.run_comparison(
        tasks=comparison_tasks,
        metrics=["efficiency", "quality", "coordination"]
    )
    
    # Display comparison table
    print("\\nPattern Performance Comparison:")
    print("Pattern     | Efficiency | Quality | Coordination")
    print("----------- | ---------- | ------- | ------------")
    for pattern, scores in results.items():
        print(f"{{pattern:<11}} | {{scores['efficiency']:.2f}}      | {{scores['quality']:.2f}}   | {{scores['coordination']:.2f}}")

if __name__ == "__main__":
    # Run all pattern evaluations
    asyncio.run(evaluate_linear_pattern())
    asyncio.run(evaluate_supervisor_pattern())
    asyncio.run(evaluate_swarm_pattern())
    asyncio.run(compare_patterns())
"""
}