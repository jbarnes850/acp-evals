"""
Performance Evaluation Example

This example demonstrates how to evaluate agent performance metrics like
latency, throughput, and resource usage. Shows real-time performance monitoring.

Run:
    python performance_eval.py
"""

import asyncio
import time

from acp_evals import EvalResult, PerformanceEval


# Mock data processing agent for demonstration
async def data_processing_agent(prompt: str) -> str:
    """Agent that processes data with varying complexity."""
    # Simulate realistic processing times based on task complexity
    if "simple" in prompt:
        await asyncio.sleep(0.1)  # 100ms for simple tasks
        return "Processed simple data successfully"
    elif "complex" in prompt:
        await asyncio.sleep(0.5)  # 500ms for complex tasks
        return "Processed complex data with multiple transformations"
    elif "heavy" in prompt:
        await asyncio.sleep(1.0)  # 1s for heavy tasks
        return "Processed heavy dataset with intensive computation"
    else:
        await asyncio.sleep(0.2)  # 200ms default
        return "Processed data successfully"


async def main():
    """Run performance evaluations."""
    print("\n⚡ Running Performance Evaluation Example\n")
    print("This example evaluates agent performance under different workloads.")
    print("Watch the real-time performance metrics!\n")

    # Create evaluator (in production, use your agent URL)
    evaluator = PerformanceEval(data_processing_agent)

    # Define test workloads
    test_prompts = [
        # Simple tasks - should be fast
        "Process simple JSON data",
        "Parse simple CSV file",
        "Simple data transformation",
        # Complex tasks - moderate latency acceptable
        "Process complex nested JSON",
        "Complex data aggregation",
        # Heavy tasks - higher latency expected
        "Process heavy dataset",
        "Heavy computational task",
        # Mixed workload
        "Standard data processing",
        "Quick validation check",
        "Regular data update",
    ]

    # Run performance tests
    latencies = []
    start_time = time.time()

    print("📊 Running performance tests...\n")

    for i, prompt in enumerate(test_prompts):
        print(f"Test {i + 1}/{len(test_prompts)}: {prompt}")
        result = await evaluator.run(prompt)

        # Extract latency from details
        latency_ms = result.details.get("latency", {}).get("mean_ms", 0)
        latencies.append(latency_ms)

        # Show performance bar
        bar_length = int(latency_ms / 50)  # 50ms per character
        bar = "█" * min(bar_length, 20)  # Cap at 20 chars
        print(f"   Latency: {latency_ms:>6.0f}ms {bar}")

        # Check for token info in metadata
        if result.metadata and "tokens" in result.metadata:
            tokens = result.metadata["tokens"]
            if isinstance(tokens, dict) and "total" in tokens:
                print(f"   Tokens:  {tokens['total']:>6d}")

    # Calculate metrics
    total_time = time.time() - start_time
    throughput = len(test_prompts) / total_time
    avg_latency = sum(latencies) / len(latencies)

    # Sort for percentiles
    sorted_latencies = sorted(latencies)
    p95_index = int(len(sorted_latencies) * 0.95)
    p99_index = int(len(sorted_latencies) * 0.99)
    p95_latency = sorted_latencies[min(p95_index, len(sorted_latencies) - 1)]
    p99_latency = sorted_latencies[min(p99_index, len(sorted_latencies) - 1)]

    # Performance Summary
    print("\n📊 Performance Summary:")
    print(f"   Total Tests:     {len(test_prompts)}")
    print(f"   Total Time:      {total_time:.1f}s")
    print(f"   Throughput:      {throughput:.1f} req/s")
    print(f"   Average Latency: {avg_latency:.0f}ms")
    print(f"   Min Latency:     {min(latencies):.0f}ms")
    print(f"   Max Latency:     {max(latencies):.0f}ms")
    print(f"   P95 Latency:     {p95_latency:.0f}ms")
    print(f"   P99 Latency:     {p99_latency:.0f}ms")

    # Latency distribution
    print("\n📈 Latency Distribution:")
    buckets = {"0-200ms": 0, "200-500ms": 0, "500-1000ms": 0, "1000ms+": 0}
    for latency in latencies:
        if latency <= 200:
            buckets["0-200ms"] += 1
        elif latency <= 500:
            buckets["200-500ms"] += 1
        elif latency <= 1000:
            buckets["500-1000ms"] += 1
        else:
            buckets["1000ms+"] += 1

    for bucket, count in buckets.items():
        bar = "█" * count
        print(f"   {bucket:>10}: {bar} ({count})")


if __name__ == "__main__":
    asyncio.run(main())
