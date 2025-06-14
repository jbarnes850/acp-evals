"""
Research Agent Evaluation Example.

This demonstrates how to evaluate a deep research agent that searches for information,
analyzes sources, and produces comprehensive reports.
"""

import asyncio
from typing import Dict, List
from acp_evals import AccuracyEval, PerformanceEval, ReliabilityEval, BatchResult


class MockResearchAgent:
    """Mock research agent for demonstration."""
    
    async def run(self, query: str) -> str:
        """Simulate a research agent response."""
        if "quantum error correction" in query.lower():
            return """
            ## Quantum Error Correction: Latest Breakthroughs

            ### Surface Codes (2023-2024)
            Recent advances in surface code implementations have achieved error rates below 0.1%, 
            marking a significant milestone. Google's Willow chip demonstrated logical qubit 
            performance improving exponentially with system size.

            ### Logical Qubits
            - IBM achieved 127 logical qubits with error rates suitable for shallow circuits
            - Quantinuum demonstrated 56 logical qubits with all-to-all connectivity
            - AWS Braket introduced topological qubits with inherent error protection

            ### Error Rate Improvements
            - Physical qubit error rates: 10^-3 → 10^-4 (10x improvement)
            - Logical qubit error rates: 10^-6 achieved in laboratory conditions
            - Real-time error correction: < 1μs correction cycles

            ### Sources
            1. "Suppressing quantum errors by scaling a surface code logical qubit" - Nature (2024)
            2. "Quantum error correction with silicon spin qubits" - Science (2024)
            3. "Fault-tolerant quantum computation roadmap" - arXiv:2403.12345
            """
        
        elif "transformer vs rnn" in query.lower():
            return """
            ## Transformer vs RNN Architectures for NLP

            ### Attention Mechanism
            **Transformers**: Self-attention allows direct connections between all positions, 
            enabling better long-range dependency modeling. O(n²) complexity but parallelizable.
            
            **RNNs**: Sequential processing with hidden states. O(n) complexity but must process 
            sequentially, limiting parallelization.

            ### Parallelization
            **Transformers**: Fully parallelizable during training, leading to 10-100x faster 
            training on modern GPUs. All positions processed simultaneously.
            
            **RNNs**: Sequential nature prevents parallelization. Each timestep depends on 
            previous, creating a bottleneck.

            ### Context Window
            **Transformers**: Fixed context window (typically 512-128k tokens). Recent advances 
            (FlashAttention, RoPE) enable million-token contexts.
            
            **RNNs**: Theoretically unlimited context, but suffers from vanishing gradients. 
            LSTMs/GRUs help but still limited to ~100-200 effective tokens.

            ### Performance Comparison
            - Language Modeling: Transformers achieve 20-30% lower perplexity
            - Translation: Transformers improved BLEU scores by 2-5 points
            - Training Speed: Transformers 10-100x faster on same hardware
            """
        
        else:
            return "Research query not recognized. Please provide a specific topic."


async def evaluate_research_agent():
    """Comprehensive evaluation of a research agent."""
    
    print("=== Research Agent Evaluation ===\n")
    
    # Initialize the research agent
    agent = MockResearchAgent()
    
    # 1. Accuracy Evaluation with Research Quality Rubric
    print("1. Evaluating Research Quality:")
    accuracy_eval = AccuracyEval(
        agent=agent,
        rubric="research_quality",
        pass_threshold=0.75
    )
    
    research_test_cases = [
        {
            "input": "What are the latest breakthroughs in quantum error correction?",
            "expected": {
                "required_topics": ["surface codes", "logical qubits", "error rates"],
                "min_sources": 2,
                "structure": ["introduction", "main points", "sources"],
                "depth": "comprehensive"
            },
            "context": {
                "audience": "quantum computing researchers",
                "detail_level": "technical"
            }
        },
        {
            "input": "Compare transformer vs RNN architectures for NLP",
            "expected": {
                "comparison_aspects": ["attention mechanism", "parallelization", "context window"],
                "balanced_analysis": True,
                "performance_metrics": True,
                "depth": "comprehensive"
            },
            "context": {
                "audience": "ML engineers",
                "focus": "practical differences"
            }
        },
        {
            "input": "Explain the latest advances in few-shot learning",
            "expected": "Comprehensive overview of few-shot learning techniques and recent progress",
            "context": {
                "expected_failure": True,  # Agent doesn't handle this topic
                "test_graceful_failure": True
            }
        }
    ]
    
    accuracy_results = await accuracy_eval.run_batch(
        test_cases=research_test_cases,
        parallel=True,
        print_results=True,
        export="research_accuracy_results.json"
    )
    
    # 2. Performance Evaluation
    print("\n2. Evaluating Performance:")
    perf_eval = PerformanceEval(
        agent=agent,
        model="gpt-4"
    )
    
    perf_test_cases = [
        {
            "query": "What are the latest breakthroughs in quantum error correction?",
            "max_tokens": 2000,
            "max_latency_ms": 5000
        },
        {
            "query": "Compare transformer vs RNN architectures for NLP",
            "max_tokens": 1500,
            "max_latency_ms": 5000
        }
    ]
    
    print("\nRunning performance tests...")
    for test in perf_test_cases:
        result = await perf_eval.run(
            input=test["query"],
            track_tokens=True,
            track_latency=True,
            print_results=False
        )
        
        # Check against thresholds
        passed = True
        if result.details["tokens"]["total"] > test["max_tokens"]:
            passed = False
            print(f"FAILED: Token limit exceeded: {result.details['tokens']['total']} > {test['max_tokens']}")
        else:
            print(f"PASSED: Token usage OK: {result.details['tokens']['total']} tokens")
        
        if result.details["latency_ms"] > test["max_latency_ms"]:
            passed = False
            print(f"FAILED: Latency limit exceeded: {result.details['latency_ms']:.0f}ms > {test['max_latency_ms']}ms")
        else:
            print(f"PASSED: Latency OK: {result.details['latency_ms']:.0f}ms")
        
        print(f"   Cost: ${result.details['cost_usd']:.4f}")
        print()
    
    # 3. Reliability Evaluation
    print("3. Evaluating Reliability:")
    reliability_eval = ReliabilityEval(
        agent=agent,
        tool_definitions=["search", "analyze", "summarize", "cite_sources"]
    )
    
    reliability_result = await reliability_eval.run(
        input="Research the latest developments in quantum error correction and provide citations",
        expected_tools=["search", "analyze", "cite_sources"],
        test_error_handling=True,
        print_results=True
    )
    
    # 4. Multi-aspect Summary
    print("\n=== Evaluation Summary ===")
    print(f"Research Quality: {accuracy_results.pass_rate:.1f}% pass rate")
    print(f"Average Quality Score: {accuracy_results.avg_score:.2f}/1.0")
    print(f"Performance: All tests within limits")
    print(f"Reliability: {'PASSED' if reliability_result.passed else 'FAILED'}")
    
    # 5. Export comprehensive report
    comprehensive_results = {
        "agent": "Research Agent v1.0",
        "evaluation_date": accuracy_results.results[0].timestamp.isoformat(),
        "accuracy": {
            "pass_rate": accuracy_results.pass_rate,
            "avg_score": accuracy_results.avg_score,
            "details": [r.details for r in accuracy_results.results]
        },
        "performance": {
            "avg_tokens": sum(r.details["tokens"]["total"] for r in accuracy_results.results) / len(accuracy_results.results),
            "avg_cost": sum(r.details.get("cost_usd", 0) for r in accuracy_results.results) / len(accuracy_results.results),
        },
        "reliability": {
            "passed": reliability_result.passed,
            "score": reliability_result.score,
            "details": reliability_result.details
        }
    }
    
    import json
    with open("research_agent_comprehensive_eval.json", "w") as f:
        json.dump(comprehensive_results, f, indent=2, default=str)
    
    print("\nCOMPLETE: Comprehensive evaluation report saved to research_agent_comprehensive_eval.json")


if __name__ == "__main__":
    asyncio.run(evaluate_research_agent())