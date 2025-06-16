#!/usr/bin/env python3
"""
Real ACP agent evaluation example.

Shows how to evaluate agents running on the ACP protocol.
"""

import asyncio
from acp_evals import AccuracyEval, PerformanceEval
from acp_evals.client import ACPEvaluationClient

# ACP Agent URL - replace with your agent
AGENT_URL = "http://localhost:8000/agents/my-agent"

async def evaluate_acp_agent():
    """Evaluate a real ACP agent."""
    
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
    print("\n=== ACP Client Evaluation ===")
    client = ACPEvaluationClient(base_url="http://localhost:8000")
    
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
        
        print(f"\nRun ID: {{run.id}}")
        print(f"Events collected: {{len(events)}}")
        print(f"Metrics: {{metrics}}")
    
    # Option 3: Batch evaluation with real scenarios
    print("\n=== Batch Evaluation ===")
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
    
    print(f"\nBatch evaluation complete!")
    print(f"Pass rate: {{batch_results.pass_rate:.1f}}%")
    print(f"Average score: {{batch_results.avg_score:.2f}}")

if __name__ == "__main__":
    # Run the evaluation
    asyncio.run(evaluate_acp_agent())
