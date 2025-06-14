#!/usr/bin/env python3
"""
Synthetic Data Generation and Storage Example

This example demonstrates how to:
1. Generate synthetic evaluation datasets from real traces
2. Save synthetic data to various formats (JSONL, JSON, CSV)
3. Organize datasets for different use cases
4. Load and use synthetic datasets for evaluation

The generated datasets can be used for:
- Continuous evaluation pipelines
- Regression testing
- Agent performance benchmarking
- Training data augmentation
"""

import asyncio
import json
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from acp_evals.benchmarks.datasets.trace_recycler import TraceRecycler
from acp_evals.telemetry.otel_exporter import OTelExporter

console = Console()

def create_sample_traces() -> list[dict]:
    """Create sample ACP agent traces for demonstration."""
    
    from datetime import datetime, timedelta
    import random
    
    sample_traces = []
    base_time = datetime.now() - timedelta(hours=2)
    
    # Sample trace patterns based on real agent interactions
    trace_templates = [
        {
            "agent": "research_agent",
            "input": "Research the latest developments in quantum computing applications",
            "output": "Based on recent research, quantum computing applications are advancing in three key areas: cryptography, optimization, and machine learning. Current breakthroughs include...",
            "tools_used": ["web_search", "paper_analysis", "data_synthesis"],
            "execution_time_ms": 15000
        },
        {
            "agent": "code_agent", 
            "input": "Write a Python function to calculate Fibonacci numbers efficiently",
            "output": "Here's an efficient Python implementation using dynamic programming:\n\n```python\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    a, b = 0, 1\n    for _ in range(2, n + 1):\n        a, b = b, a + b\n    return b\n```",
            "tools_used": ["code_generation", "optimization_analysis"],
            "execution_time_ms": 3500
        },
        {
            "agent": "analysis_agent",
            "input": "Analyze the performance metrics of our latest AI model deployment",
            "output": "Performance analysis shows: 95% accuracy on test set, 45ms average latency, 99.9% uptime. Key optimization opportunities include batch processing and model compression.",
            "tools_used": ["metrics_analysis", "performance_profiling", "report_generation"],
            "execution_time_ms": 8200
        },
        {
            "agent": "coordinator",
            "input": "Plan a multi-step research project on renewable energy trends",
            "output": "Research plan: 1) Literature review (2 weeks), 2) Data collection (3 weeks), 3) Analysis phase (2 weeks), 4) Report writing (1 week). Total timeline: 8 weeks with key milestones.",
            "tools_used": ["project_planning", "timeline_analysis", "resource_allocation"],
            "execution_time_ms": 6700
        },
        {
            "agent": "error_handler",
            "input": "Handle this system error: Connection timeout during data sync",
            "output": "Error handled: Implemented exponential backoff retry mechanism, increased timeout to 30s, added connection pooling. System recovered successfully.",
            "tools_used": ["error_analysis", "retry_logic", "system_recovery"],
            "execution_time_ms": 2100,
            "has_error": True,
            "error_type": "timeout_error"
        }
    ]
    
    # Generate multiple traces with variations
    for i, template in enumerate(trace_templates):
        for variation in range(3):  # 3 variations per template
            timestamp = base_time + timedelta(minutes=i*10 + variation*3)
            session_id = f"session_{timestamp.strftime('%Y%m%d_%H%M%S')}_{i}_{variation}"
            
            # Add some randomness to token usage
            base_tokens = random.randint(100, 1000)
            input_tokens = int(base_tokens * 0.7)
            output_tokens = int(base_tokens * 0.3)
            
            trace = {
                "timestamp": timestamp.isoformat(),
                "agent": template["agent"],
                "input": template["input"],
                "output": template["output"],
                "session_id": session_id,
                "execution_time_ms": template["execution_time_ms"] + random.randint(-500, 500),
                "token_usage": {
                    "input": input_tokens,
                    "output": output_tokens, 
                    "total": input_tokens + output_tokens
                },
                "metadata": {
                    "session_id": session_id,
                    "execution_time_ms": template["execution_time_ms"],
                    "token_usage": {
                        "input": input_tokens,
                        "output": output_tokens,
                        "total": input_tokens + output_tokens
                    },
                    "tools_used": template["tools_used"],
                    "real_llm_call": True,
                    "model_used": "gpt-4o-mini",
                    "error": template.get("has_error", False),
                    "error_type": template.get("error_type"),
                    "workflow_type": "multi_step" if len(template["tools_used"]) > 2 else "simple"
                }
            }
            
            sample_traces.append(trace)
    
    return sample_traces

async def demonstrate_synthetic_data_generation():
    """Demonstrate comprehensive synthetic data generation and storage."""
    
    console.print(Panel.fit("🎲 Synthetic Data Generation & Storage Demo", style="bold blue"))
    
    # Step 1: Create sample traces
    console.print("📊 Creating sample traces from various agent interactions...")
    sample_traces = create_sample_traces()
    console.print(f"✅ Created {len(sample_traces)} sample traces")
    
    # Display sample trace info
    trace_table = Table(title="Sample Traces Overview")
    trace_table.add_column("Agent", style="cyan")
    trace_table.add_column("Tools Used", style="green")
    trace_table.add_column("Tokens", style="yellow")
    trace_table.add_column("Time (ms)", style="red")
    
    for trace in sample_traces[:5]:  # Show first 5
        tools = ", ".join(trace["metadata"]["tools_used"][:2])  # First 2 tools
        if len(trace["metadata"]["tools_used"]) > 2:
            tools += "..."
        
        trace_table.add_row(
            trace["agent"],
            tools,
            str(trace["token_usage"]["total"]),
            str(trace["execution_time_ms"])
        )
    
    console.print(trace_table)
    
    # Step 2: Initialize trace recycler and ingest traces
    console.print("\n🔄 Initializing trace recycler...")
    telemetry_exporter = OTelExporter()
    trace_recycler = TraceRecycler(telemetry_exporter)
    
    console.print("📥 Ingesting traces (with automatic ACP → OpenTelemetry conversion)...")
    for trace in sample_traces:
        trace_recycler.ingest_trace(trace)  # Auto-conversion happens here
    
    console.print(f"✅ Ingested {len(sample_traces)} traces")
    console.print(f"📈 Detected {len(trace_recycler.patterns)} patterns")
    console.print(f"🎯 Created {len(trace_recycler.evaluation_candidates)} evaluation candidates")
    
    # Step 3: Generate and save synthetic datasets in multiple formats
    console.print("\n🎲 Generating synthetic datasets...")
    
    # Create datasets directory
    datasets_dir = Path("datasets")
    datasets_dir.mkdir(exist_ok=True)
    
    # Generate different types of datasets
    dataset_configs = [
        {
            "name": "comprehensive_dataset",
            "count": 20,
            "description": "Comprehensive dataset with all patterns",
            "format": "json"
        },
        {
            "name": "high_quality_dataset", 
            "count": 10,
            "min_quality_score": 0.4,
            "description": "High-quality subset for production testing",
            "format": "jsonl"
        },
        {
            "name": "research_focused_dataset",
            "count": 15,
            "include_patterns": ["success"],
            "description": "Research-focused scenarios only",
            "format": "csv"
        },
        {
            "name": "error_handling_dataset",
            "count": 8,
            "include_patterns": ["error_pattern"],
            "description": "Error handling and edge cases",
            "format": "json"
        }
    ]
    
    generated_datasets = {}
    
    for config in dataset_configs:
        console.print(f"\n🔹 Generating {config['name']}...")
        
        output_path = datasets_dir / f"{config['name']}.{config['format']}"
        
        # Generate and export dataset
        count = trace_recycler.export_synthetic_dataset(
            output_path=str(output_path),
            count=config["count"],
            include_patterns=config.get("include_patterns"),
            min_quality_score=config.get("min_quality_score"),
            adaptive_threshold=config.get("min_quality_score") is None,
            format=config["format"]
        )
        
        generated_datasets[config["name"]] = {
            "path": output_path,
            "count": count,
            "format": config["format"],
            "description": config["description"]
        }
        
        console.print(f"  ✅ Generated {count} synthetic tests")
        console.print(f"  💾 Saved to: {output_path}")
    
    # Step 4: Display dataset summary
    console.print("\n📊 Generated Datasets Summary:")
    
    summary_table = Table(title="Synthetic Datasets")
    summary_table.add_column("Dataset", style="cyan")
    summary_table.add_column("Format", style="green")
    summary_table.add_column("Test Cases", style="yellow")
    summary_table.add_column("File Size", style="red")
    summary_table.add_column("Description", style="white")
    
    for name, info in generated_datasets.items():
        file_size = info["path"].stat().st_size if info["path"].exists() else 0
        size_str = f"{file_size / 1024:.1f} KB" if file_size > 0 else "0 KB"
        
        summary_table.add_row(
            name,
            info["format"].upper(),
            str(info["count"]),
            size_str,
            info["description"][:40] + "..." if len(info["description"]) > 40 else info["description"]
        )
    
    console.print(summary_table)
    
    # Step 5: Demonstrate loading and using synthetic data
    console.print("\n📂 Demonstrating dataset loading...")
    
    # Load JSONL dataset
    jsonl_path = datasets_dir / "high_quality_dataset.jsonl"
    if jsonl_path.exists():
        console.print(f"📖 Loading JSONL dataset: {jsonl_path}")
        
        with open(jsonl_path) as f:
            loaded_tests = [json.loads(line) for line in f]
        
        console.print(f"  ✅ Loaded {len(loaded_tests)} test cases")
        
        if loaded_tests:
            sample_test = loaded_tests[0]
            console.print(f"  📋 Sample test case:")
            console.print(f"    ID: {sample_test.get('id', 'unknown')}")
            console.print(f"    Input: {sample_test.get('input', '')[:60]}...")
            console.print(f"    Expected: {sample_test.get('expected', '')[:60]}...")
            console.print(f"    Quality Score: {sample_test.get('metadata', {}).get('quality_score', 0):.3f}")
    
    # Step 6: Export patterns for analysis
    console.print("\n🔍 Exporting pattern analysis...")
    patterns_path = datasets_dir / "detected_patterns.json"
    trace_recycler.export_patterns(str(patterns_path))
    console.print(f"  ✅ Pattern analysis saved to: {patterns_path}")
    
    # Final summary
    console.print(Panel.fit("🎉 Synthetic Data Generation Complete!", style="bold green"))
    console.print("📁 All datasets saved to: datasets/")
    console.print("🔄 Ready for use in evaluation pipelines")
    console.print("📊 Patterns analyzed and exported")
    
    return generated_datasets

def demonstrate_dataset_usage():
    """Show how to use the generated synthetic datasets."""
    
    console.print(Panel.fit("🛠️ Using Synthetic Datasets", style="bold cyan"))
    
    datasets_dir = Path("datasets")
    
    # Example usage patterns
    usage_examples = [
        "# Load JSONL for streaming evaluation",
        "with open('datasets/high_quality_dataset.jsonl') as f:",
        "    for line in f:",
        "        test_case = json.loads(line)",
        "        result = evaluate_agent(test_case['input'], test_case['expected'])",
        "",
        "# Load JSON for batch evaluation", 
        "with open('datasets/comprehensive_dataset.json') as f:",
        "    dataset = json.load(f)",
        "    test_cases = dataset['synthetic_tests']",
        "    results = batch_evaluate(test_cases)",
        "",
        "# Load CSV for analysis",
        "import pandas as pd",
        "df = pd.read_csv('datasets/research_focused_dataset.csv')",
        "high_quality = df[df['quality_score'] > 0.5]"
    ]
    
    console.print("💡 Usage Examples:")
    for example in usage_examples:
        console.print(f"  {example}", style="dim")
    
    # Show actual files created
    if datasets_dir.exists():
        console.print(f"\n📂 Files created in {datasets_dir}:")
        for file_path in sorted(datasets_dir.glob("*")):
            size = file_path.stat().st_size / 1024
            console.print(f"  📄 {file_path.name} ({size:.1f} KB)")

async def main():
    """Main demonstration function."""
    
    try:
        # Generate synthetic datasets
        datasets = await demonstrate_synthetic_data_generation()
        
        # Show usage examples
        demonstrate_dataset_usage()
        
        console.print(f"\n✨ Success! Generated {len(datasets)} synthetic datasets")
        console.print("🚀 These datasets are now ready for use in your evaluation pipelines!")
        
        return True
        
    except Exception as e:
        console.print(f"❌ Error: {e}")
        import traceback
        console.print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)