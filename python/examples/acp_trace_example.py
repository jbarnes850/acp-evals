#!/usr/bin/env python3
"""
Example of ACP agent JSON responses and trace conversion.

This shows realistic ACP agent responses including tool usage,
and how they convert to traces for evaluation recycling.
"""

import json
import uuid
from datetime import datetime, timedelta


def create_acp_response_with_tools():
    """
    Create a realistic ACP agent response that includes tool usage.
    
    This represents an agent that:
    1. Receives a query about weather
    2. Uses a weather tool
    3. Returns the result
    """
    run_id = str(uuid.uuid4())
    start_time = datetime.now()
    
    # ACP Response with tool usage events
    response = {
        "agent_name": "weather-assistant",
        "run_id": run_id,
        "status": "completed",
        "output": [
            # Initial thinking
            {
                "role": "agent/weather-assistant",
                "parts": [{
                    "content_type": "text/plain",
                    "content": "I'll check the current weather in San Francisco for you."
                }],
                "created_at": start_time.isoformat(),
                "completed_at": (start_time + timedelta(milliseconds=100)).isoformat()
            },
            # Tool usage indication (following ACP events pattern)
            {
                "role": "agent/weather-assistant",
                "parts": [{
                    "content_type": "application/json",
                    "content": json.dumps({
                        "tool": "weather_api",
                        "parameters": {"location": "San Francisco, CA"},
                        "status": "calling"
                    })
                }],
                "created_at": (start_time + timedelta(milliseconds=100)).isoformat(),
                "completed_at": (start_time + timedelta(milliseconds=500)).isoformat()
            },
            # Tool result
            {
                "role": "agent/weather-assistant", 
                "parts": [{
                    "content_type": "application/json",
                    "content": json.dumps({
                        "tool": "weather_api",
                        "result": {
                            "temperature": 68,
                            "conditions": "Partly cloudy",
                            "humidity": 65
                        },
                        "status": "completed"
                    })
                }],
                "created_at": (start_time + timedelta(milliseconds=500)).isoformat(),
                "completed_at": (start_time + timedelta(milliseconds=600)).isoformat()
            },
            # Final response
            {
                "role": "agent/weather-assistant",
                "parts": [{
                    "content_type": "text/plain", 
                    "content": "The current weather in San Francisco is 68°F with partly cloudy skies and 65% humidity."
                }],
                "created_at": (start_time + timedelta(milliseconds=600)).isoformat(),
                "completed_at": (start_time + timedelta(milliseconds=700)).isoformat()
            }
        ],
        "created_at": start_time.isoformat(),
        "finished_at": (start_time + timedelta(milliseconds=700)).isoformat()
    }
    
    return response


def create_acp_error_response():
    """Create an ACP response showing error handling."""
    run_id = str(uuid.uuid4())
    start_time = datetime.now()
    
    return {
        "agent_name": "data-processor",
        "run_id": run_id,
        "status": "failed",
        "output": [
            {
                "role": "agent/data-processor",
                "parts": [{
                    "content_type": "text/plain",
                    "content": "I'll process your data file."
                }],
                "created_at": start_time.isoformat()
            }
        ],
        "error": {
            "code": "invalid_input",
            "message": "The provided file format is not supported. Please use CSV or JSON."
        },
        "created_at": start_time.isoformat(),
        "finished_at": (start_time + timedelta(milliseconds=200)).isoformat()
    }


def convert_to_opentelemetry_trace(acp_response, input_query):
    """
    Convert ACP response to OpenTelemetry trace format.
    
    This creates spans for:
    - Input processing
    - Tool calls (if any)
    - Output generation
    - Error handling (if failed)
    """
    trace_id = str(uuid.uuid4())
    spans = []
    
    # Parse timestamps
    start_time = datetime.fromisoformat(acp_response["created_at"])
    end_time = datetime.fromisoformat(acp_response["finished_at"])
    
    # Input span
    span_id = 0
    spans.append({
        "span_id": f"{trace_id}-{span_id}",
        "name": "agent.input",
        "start_time": start_time.isoformat(),
        "end_time": (start_time + timedelta(milliseconds=10)).isoformat(),
        "attributes": {
            "operation.type": "agent.input",
            "input.value": input_query,
            "agent.name": acp_response["agent_name"],
            "run.id": acp_response["run_id"]
        },
        "status": {"status_code": "OK"}
    })
    span_id += 1
    
    # Process output messages
    for i, message in enumerate(acp_response["output"]):
        for part in message["parts"]:
            span_start = datetime.fromisoformat(message.get("created_at", start_time.isoformat()))
            span_end = datetime.fromisoformat(message.get("completed_at", span_start.isoformat()))
            
            # Check if this is a tool call
            if part["content_type"] == "application/json":
                try:
                    content = json.loads(part["content"])
                    if "tool" in content:
                        spans.append({
                            "span_id": f"{trace_id}-{span_id}",
                            "name": f"tool.{content['tool']}",
                            "start_time": span_start.isoformat(),
                            "end_time": span_end.isoformat(),
                            "attributes": {
                                "operation.type": "tool.call",
                                "tool.name": content["tool"],
                                "tool.parameters": json.dumps(content.get("parameters", {})),
                                "tool.status": content.get("status", "unknown")
                            },
                            "status": {"status_code": "OK"}
                        })
                        span_id += 1
                except:
                    pass
    
    # Output span
    final_output = ""
    if acp_response["output"]:
        last_message = acp_response["output"][-1]
        if last_message["parts"]:
            final_output = last_message["parts"][0].get("content", "")
    
    spans.append({
        "span_id": f"{trace_id}-{span_id}",
        "name": "agent.output",
        "start_time": (end_time - timedelta(milliseconds=10)).isoformat(),
        "end_time": end_time.isoformat(),
        "attributes": {
            "operation.type": "agent.output",
            "output.value": final_output,
            "agent.name": acp_response["agent_name"],
            "status": acp_response["status"]
        },
        "status": {
            "status_code": "ERROR" if acp_response["status"] == "failed" else "OK"
        }
    })
    
    # Add error span if failed
    if acp_response.get("error"):
        spans.append({
            "span_id": f"{trace_id}-{span_id + 1}",
            "name": "agent.error",
            "start_time": end_time.isoformat(),
            "end_time": end_time.isoformat(),
            "attributes": {
                "operation.type": "error",
                "error.type": acp_response["error"]["code"],
                "error.message": acp_response["error"]["message"]
            },
            "status": {"status_code": "ERROR"}
        })
    
    return {
        "trace_id": trace_id,
        "timestamp": start_time.isoformat(),
        "service": f"acp-agent-{acp_response['agent_name']}",
        "spans": spans,
        "metadata": {
            "agent_name": acp_response["agent_name"],
            "run_id": acp_response["run_id"],
            "status": acp_response["status"],
            "tool_count": len([s for s in spans if "tool." in s["name"]])
        }
    }


def main():
    print("="*60)
    print("ACP AGENT JSON RESPONSE EXAMPLES")
    print("="*60)
    
    # Example 1: Response with tool usage
    print("\n1. ACP Response with Tool Usage:")
    print("-" * 40)
    
    tool_response = create_acp_response_with_tools()
    print(json.dumps(tool_response, indent=2)[:800] + "...\n")
    
    # Convert to trace
    trace = convert_to_opentelemetry_trace(
        tool_response,
        "What's the weather in San Francisco?"
    )
    
    print("Converted to OpenTelemetry trace:")
    print(f"- Trace ID: {trace['trace_id']}")
    print(f"- Service: {trace['service']}")
    print(f"- Spans: {len(trace['spans'])}")
    print(f"- Tool calls: {trace['metadata']['tool_count']}")
    
    print("\nSpan breakdown:")
    for span in trace['spans']:
        print(f"  - {span['name']}: {span['attributes']['operation.type']}")
    
    # Example 2: Error response
    print("\n\n2. ACP Error Response:")
    print("-" * 40)
    
    error_response = create_acp_error_response()
    print(json.dumps(error_response, indent=2))
    
    # Convert to trace
    error_trace = convert_to_opentelemetry_trace(
        error_response,
        "Process this data file: invalid.xyz"
    )
    
    print("\nConverted to OpenTelemetry trace:")
    print(f"- Status: {error_trace['metadata']['status']}")
    print(f"- Error captured in spans: {any('error' in s['name'] for s in error_trace['spans'])}")
    
    # Example 3: Trace recycling benefits
    print("\n\n3. Benefits for Trace Recycling:")
    print("-" * 40)
    print("✅ Captures complete agent workflow including tool usage")
    print("✅ Records timing information for performance analysis")
    print("✅ Preserves error scenarios for regression testing")
    print("✅ Identifies patterns in agent behavior")
    print("✅ Enables creation of realistic test cases from production")
    
    # Save example traces
    examples = {
        "tool_usage_trace": trace,
        "error_trace": error_trace
    }
    
    with open("acp_trace_examples.json", "w") as f:
        json.dump(examples, f, indent=2)
    
    print("\n📁 Saved example traces to acp_trace_examples.json")


if __name__ == "__main__":
    main()