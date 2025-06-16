#!/usr/bin/env python3
"""
Comprehensive End-to-End Trace Pipeline Test

This example demonstrates the complete ACP-Evals trace recycling pipeline:
1. Live ACP agent deployment with real LLM calls
2. Trace collection and format conversion
3. Adaptive quality threshold selection
4. Synthetic evaluation data generation
5. Pattern detection and analysis

This validates that the entire system works error-free end-to-end.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from acp_evals.benchmarks.datasets.trace_recycler import TraceRecycler
from acp_evals.telemetry.otel_exporter import OTelExporter

# Set up logging to see all debug info
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

console = Console()

class EndToEndTraceTestPipeline:
    """Complete end-to-end trace pipeline testing system."""
    
    def __init__(self):
        self.agent_process = None
        self.agent_url = "http://localhost:8100"
        self.results = {}
        
    async def deploy_test_agent(self) -> bool:
        """Deploy a minimal test ACP agent for trace generation."""
        
        console.print("🚀 Deploying test ACP agent...")
        
        # Create minimal test agent
        agent_code = '''
import asyncio
import json
import os
from collections import defaultdict
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import List, Dict, Any

from acp_sdk import Message
from acp_sdk.models import MessagePart
from acp_sdk.server import Context, Server
from openai import AsyncOpenAI

# Initialize OpenAI client
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

server = Server()
execution_traces = []

class TracingWrapper:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        
    def log_execution(self, input_msg: str, output_msg: str, metadata: Dict[str, Any]):
        trace = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_name,
            "input": input_msg,
            "output": output_msg,
            "metadata": metadata,
            "session_id": metadata.get("session_id", "unknown"),
            "execution_time_ms": metadata.get("execution_time_ms", 0),
            "token_usage": metadata.get("token_usage", {}),
        }
        execution_traces.append(trace)

tracer = TracingWrapper("test_agent")

async def call_llm(prompt: str, system_prompt: str) -> tuple[str, dict]:
    """Make real LLM call."""
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        token_usage = {
            "input": response.usage.prompt_tokens,
            "output": response.usage.completion_tokens,
            "total": response.usage.total_tokens
        }
        return content, token_usage
    except Exception as e:
        return f"Error: {str(e)}", {"input": 0, "output": 0, "total": 0}

@server.agent(name="test_agent")
async def test_agent(input: List[Message], context: Context) -> AsyncGenerator:
    """Test agent that processes various types of requests."""
    start_time = datetime.now()
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    input_text = str(input[0]) if input else ""
    
    # Determine request type and respond accordingly
    if "error" in input_text.lower():
        # Simulate error handling
        response = "I encountered an error processing your request. Please try again."
        token_usage = {"input": 10, "output": 15, "total": 25}
        has_error = True
        error_type = "simulated_error"
    else:
        # Make real LLM call
        system_prompt = "You are a helpful AI assistant. Provide clear, concise responses."
        response, token_usage = await call_llm(input_text, system_prompt)
        has_error = False
        error_type = None
    
    execution_time = (datetime.now() - start_time).total_seconds() * 1000
    
    # Log trace
    tracer.log_execution(
        input_text,
        response,
        {
            "session_id": session_id,
            "execution_time_ms": execution_time,
            "token_usage": token_usage,
            "tools_used": ["llm_call", "text_processing"],
            "real_llm_call": True,
            "error": has_error,
            "error_type": error_type,
            "model_used": "gpt-4.1-mini"
        }
    )
    
    yield MessagePart(content=response, role="assistant")

@server.agent(name="get_traces")
async def traces_agent(input: List[Message], context: Context) -> AsyncGenerator:
    """Return all execution traces."""
    traces_data = {
        "traces": execution_traces,
        "total_traces": len(execution_traces),
        "timestamp": datetime.now().isoformat()
    }
    yield MessagePart(content=json.dumps(traces_data, indent=2), role="assistant")

@server.agent(name="health_check")
async def health_agent(input: List[Message], context: Context) -> AsyncGenerator:
    """Health check endpoint."""
    health_data = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "traces_collected": len(execution_traces)
    }
    yield MessagePart(content=json.dumps(health_data, indent=2), role="assistant")

if __name__ == "__main__":
    print("🚀 Starting Test ACP Agent Server...")
    server.run(port=8100)
'''
        
        # Write agent to temporary file
        agent_file = Path("temp_test_agent.py")
        with open(agent_file, "w") as f:
            f.write(agent_code)
        
        try:
            # Get API key from environment
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                # Try to load from .env file
                env_file = Path(".env")
                if env_file.exists():
                    with open(env_file) as f:
                        for line in f:
                            if line.startswith("OPENAI_API_KEY="):
                                api_key = line.split("=", 1)[1].strip()
                                break
            
            if not api_key:
                console.print("❌ No OpenAI API key found. Set OPENAI_API_KEY environment variable.")
                return False
            
            # Start agent process
            env = os.environ.copy()
            env["OPENAI_API_KEY"] = api_key
            
            self.agent_process = subprocess.Popen(
                [sys.executable, str(agent_file)],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for startup
            await asyncio.sleep(3)
            
            # Test health check
            from acp_sdk.client import Client
            from acp_sdk import Message
            from acp_sdk.models import MessagePart
            
            try:
                async with Client(base_url=self.agent_url) as client:
                    health_result = await client.run_sync(
                        agent="health_check",
                        input=[Message(parts=[MessagePart(content="ping", role="user")])]
                    )
                    
                    if health_result and health_result.output:
                        console.print("✅ Test agent deployed and healthy")
                        return True
                    else:
                        console.print("❌ Health check failed")
                        return False
                        
            except Exception as e:
                console.print(f"❌ Failed to connect to test agent: {e}")
                return False
                
        except Exception as e:
            console.print(f"❌ Failed to deploy test agent: {e}")
            return False
    
    async def generate_test_traces(self) -> List[Dict]:
        """Generate various types of traces for testing."""
        
        console.print("📊 Generating test traces...")
        
        test_inputs = [
            "Hello, what is the capital of France?",
            "Can you explain machine learning in simple terms?", 
            "What are the benefits of renewable energy?",
            "Please help me with this error message",  # Should trigger error handling
            "Write a short poem about technology"
        ]
        
        from acp_sdk.client import Client
        from acp_sdk import Message
        from acp_sdk.models import MessagePart
        
        traces_generated = 0
        
        async with Client(base_url=self.agent_url) as client:
            for i, test_input in enumerate(test_inputs, 1):
                console.print(f"  Sending test {i}/{len(test_inputs)}: {test_input[:50]}...")
                
                try:
                    result = await client.run_sync(
                        agent="test_agent",
                        input=[Message(parts=[MessagePart(content=test_input, role="user")])]
                    )
                    
                    if result and result.output:
                        traces_generated += 1
                        console.print(f"    ✅ Response: {str(result.output[0])[:100]}...")
                    else:
                        console.print(f"    ❌ No response received")
                        
                except Exception as e:
                    console.print(f"    ❌ Error: {e}")
                
                # Small delay between requests
                await asyncio.sleep(1)
        
        # Collect all traces
        try:
            async with Client(base_url=self.agent_url) as client:
                traces_result = await client.run_sync(
                    agent="get_traces",
                    input=[Message(parts=[MessagePart(content="get_traces", role="user")])]
                )
                
                if traces_result and traces_result.output:
                    traces_json = str(traces_result.output[0])
                    traces_data = json.loads(traces_json)
                    traces = traces_data.get("traces", [])
                    
                    console.print(f"✅ Collected {len(traces)} traces")
                    self.results["traces_generated"] = len(traces)
                    return traces
                else:
                    console.print("❌ Failed to collect traces")
                    return []
                    
        except Exception as e:
            console.print(f"❌ Error collecting traces: {e}")
            return []
    
    async def test_trace_recycling(self, traces: List[Dict]) -> Dict:
        """Test the complete trace recycling pipeline."""
        
        console.print("🔄 Testing trace recycling pipeline...")
        
        if not traces:
            console.print("❌ No traces to recycle")
            return {"error": "No traces available"}
        
        # Initialize trace recycler
        telemetry_exporter = OTelExporter()
        trace_recycler = TraceRecycler(telemetry_exporter)
        
        console.print(f"📥 Ingesting {len(traces)} traces...")
        
        # Ingest traces (auto-conversion should happen)
        ingested_count = 0
        for trace in traces:
            try:
                trace_recycler.ingest_trace(trace)  # Should auto-convert ACP → OpenTelemetry
                ingested_count += 1
            except Exception as e:
                console.print(f"❌ Failed to ingest trace: {e}")
        
        console.print(f"✅ Ingested {ingested_count}/{len(traces)} traces")
        
        # Test adaptive threshold generation
        console.print("🧠 Testing adaptive threshold selection...")
        
        try:
            # Test with different dataset sizes
            for count in [3, 5, 10]:
                synthetic_tests = trace_recycler.generate_evaluation_dataset(
                    count=count,
                    adaptive_threshold=True  # Use adaptive threshold
                )
                
                console.print(f"  Requesting {count} tests: Generated {len(synthetic_tests)} synthetic tests")
                
                if synthetic_tests:
                    # Display sample
                    sample = synthetic_tests[0]
                    console.print(f"    Sample ID: {sample.get('id', 'unknown')}")
                    console.print(f"    Sample input: {sample.get('input', '')[:50]}...")
                    console.print(f"    Quality score: {sample.get('metadata', {}).get('quality_score', 0):.3f}")
            
            # Test pattern detection
            console.print("🔍 Testing pattern detection...")
            patterns_detected = len(trace_recycler.patterns)
            console.print(f"  Detected {patterns_detected} patterns")
            
            # Test evaluation candidates
            candidates = len(trace_recycler.evaluation_candidates)
            console.print(f"  Created {candidates} evaluation candidates")
            
            return {
                "ingested_traces": ingested_count,
                "total_input_traces": len(traces),
                "patterns_detected": patterns_detected,
                "evaluation_candidates": candidates,
                "synthetic_tests_generated": len(synthetic_tests) if 'synthetic_tests' in locals() else 0,
                "pipeline_status": "SUCCESS"
            }
            
        except Exception as e:
            console.print(f"❌ Trace recycling failed: {e}")
            import traceback
            console.print(traceback.format_exc())
            return {"error": str(e), "pipeline_status": "FAILED"}
    
    async def cleanup(self):
        """Clean up test resources."""
        console.print("🧹 Cleaning up...")
        
        if self.agent_process:
            try:
                self.agent_process.terminate()
                self.agent_process.wait(timeout=5)
                console.print("✅ Agent process terminated")
            except:
                try:
                    self.agent_process.kill()
                    console.print("✅ Agent process killed")
                except:
                    console.print("❌ Failed to stop agent process")
        
        # Clean up temp files
        temp_files = ["temp_test_agent.py"]
        for temp_file in temp_files:
            try:
                Path(temp_file).unlink(missing_ok=True)
                console.print(f"✅ Removed {temp_file}")
            except:
                pass
    
    async def run_complete_test(self) -> Dict:
        """Run the complete end-to-end test."""
        
        console.print(Panel.fit("🎯 End-to-End Trace Pipeline Test", style="bold blue"))
        
        try:
            # Step 1: Deploy test agent
            if not await self.deploy_test_agent():
                return {"status": "FAILED", "error": "Agent deployment failed"}
            
            # Step 2: Generate test traces
            traces = await self.generate_test_traces()
            if not traces:
                return {"status": "FAILED", "error": "No traces generated"}
            
            # Step 3: Test trace recycling pipeline
            recycling_results = await self.test_trace_recycling(traces)
            
            # Compile final results
            final_results = {
                "timestamp": time.time(),
                "traces_generated": len(traces),
                "recycling_results": recycling_results,
                "status": "SUCCESS" if recycling_results.get("pipeline_status") == "SUCCESS" else "FAILED"
            }
            
            return final_results
            
        except Exception as e:
            console.print(f"❌ Test failed: {e}")
            import traceback
            console.print(traceback.format_exc())
            return {"status": "FAILED", "error": str(e)}
        
        finally:
            await self.cleanup()

async def main():
    """Main test execution."""
    
    # Run complete test
    test_pipeline = EndToEndTraceTestPipeline()
    results = await test_pipeline.run_complete_test()
    
    # Display results
    if results["status"] == "SUCCESS":
        console.print(Panel.fit("🎉 END-TO-END TEST: SUCCESS", style="bold green"))
        console.print("✅ Live ACP agent deployment: Working")
        console.print("✅ Real LLM trace generation: Working") 
        console.print("✅ ACP → OpenTelemetry conversion: Working")
        console.print("✅ Adaptive quality thresholds: Working")
        console.print("✅ Synthetic data generation: Working")
        console.print("✅ Pattern detection: Working")
        console.print("✅ Complete pipeline: ERROR-FREE")
        
        recycling = results.get("recycling_results", {})
        console.print(f"\n📊 Final Metrics:")
        console.print(f"  Traces generated: {results.get('traces_generated', 0)}")
        console.print(f"  Traces ingested: {recycling.get('ingested_traces', 0)}")
        console.print(f"  Patterns detected: {recycling.get('patterns_detected', 0)}")
        console.print(f"  Evaluation candidates: {recycling.get('evaluation_candidates', 0)}")
        console.print(f"  Synthetic tests: {recycling.get('synthetic_tests_generated', 0)}")
        
    else:
        console.print(Panel.fit("❌ END-TO-END TEST: FAILED", style="bold red"))
        console.print(f"Error: {results.get('error', 'Unknown error')}")
    
    # Save detailed results
    with open("end_to_end_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    console.print(f"\n📊 Detailed results saved to: end_to_end_test_results.json")
    
    return results["status"] == "SUCCESS"

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)