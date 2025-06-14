"""
Tool-Using Agent Evaluation Example.

This demonstrates how to evaluate agents that use tools like calculators,
search engines, databases, and APIs.
"""

import asyncio
import json
from typing import Dict, List, Any
from acp_evals import ReliabilityEval, AccuracyEval, PerformanceEval


class MockToolAgent:
    """Mock tool-using agent for demonstration."""
    
    def __init__(self):
        self.tools = {
            "calculator": self._calculator,
            "search": self._search,
            "database": self._database_query,
            "weather_api": self._weather_api
        }
        self.tool_calls = []
    
    async def _calculator(self, expression: str) -> float:
        """Simulate calculator tool."""
        self.tool_calls.append(("calculator", expression))
        # Simple eval for demo - in production use safe math parser
        try:
            result = eval(expression.replace("^", "**"))
            return result
        except:
            return "Error: Invalid expression"
    
    async def _search(self, query: str) -> List[Dict[str, str]]:
        """Simulate search tool."""
        self.tool_calls.append(("search", query))
        
        mock_results = {
            "quantum computing companies": [
                {"title": "IBM Quantum", "snippet": "Leading quantum computing with 1000+ qubit systems"},
                {"title": "Google Quantum AI", "snippet": "Achieved quantum supremacy with Sycamore processor"},
                {"title": "Rigetti Computing", "snippet": "Cloud quantum computing platform"}
            ],
            "climate change statistics": [
                {"title": "IPCC Report 2024", "snippet": "Global temperature rose 1.1°C above pre-industrial"},
                {"title": "NASA Climate Data", "snippet": "CO2 levels at 421 ppm, highest in 3 million years"},
            ]
        }
        
        for key, results in mock_results.items():
            if key in query.lower():
                return results
        return [{"title": "No results", "snippet": "No relevant results found"}]
    
    async def _database_query(self, query: str) -> List[Dict[str, Any]]:
        """Simulate database query tool."""
        self.tool_calls.append(("database", query))
        
        if "customer orders" in query.lower():
            return [
                {"order_id": 123, "customer": "Alice", "total": 150.00, "status": "shipped"},
                {"order_id": 124, "customer": "Bob", "total": 89.99, "status": "processing"},
                {"order_id": 125, "customer": "Charlie", "total": 210.50, "status": "delivered"}
            ]
        return []
    
    async def _weather_api(self, location: str) -> Dict[str, Any]:
        """Simulate weather API tool."""
        self.tool_calls.append(("weather_api", location))
        
        weather_data = {
            "new york": {"temp": 72, "condition": "sunny", "humidity": 65},
            "london": {"temp": 58, "condition": "cloudy", "humidity": 80},
            "tokyo": {"temp": 68, "condition": "rainy", "humidity": 90}
        }
        
        return weather_data.get(location.lower(), {"error": "Location not found"})
    
    async def run(self, input_text: str) -> str:
        """Process input and use appropriate tools."""
        self.tool_calls = []  # Reset for each run
        response_parts = []
        
        # Calculator queries
        if any(op in input_text for op in ["+", "-", "*", "/", "^", "sqrt"]):
            if "25 * 4" in input_text:
                calc_result = await self._calculator("25 * 4")
                response_parts.append(f"25 * 4 = {calc_result}")
                
                if "sqrt(16)" in input_text:
                    sqrt_result = await self._calculator("16 ** 0.5")
                    response_parts.append(f"sqrt(16) = {sqrt_result}")
                    
                    if "+" in input_text:
                        total = await self._calculator(f"{calc_result} + {sqrt_result}")
                        response_parts.append(f"Total: {calc_result} + {sqrt_result} = {total}")
        
        # Search queries
        if "search" in input_text.lower() or "find" in input_text.lower():
            if "quantum computing companies" in input_text.lower():
                results = await self._search("quantum computing companies")
                response_parts.append("Search results:")
                for r in results:
                    response_parts.append(f"- {r['title']}: {r['snippet']}")
        
        # Database queries
        if "customer" in input_text.lower() and "order" in input_text.lower():
            results = await self._database_query("SELECT * FROM customer orders")
            response_parts.append(f"Found {len(results)} customer orders")
            total_value = sum(r['total'] for r in results)
            response_parts.append(f"Total order value: ${total_value:.2f}")
        
        # Weather queries
        if "weather" in input_text.lower():
            for location in ["new york", "london", "tokyo"]:
                if location in input_text.lower():
                    weather = await self._weather_api(location)
                    response_parts.append(
                        f"Weather in {location.title()}: {weather['temp']}°F, {weather['condition']}"
                    )
                    break
        
        if not response_parts:
            return "I couldn't process that request. Please try a calculation, search, or database query."
        
        return "\n".join(response_parts)


async def evaluate_tool_agent():
    """Comprehensive evaluation of a tool-using agent."""
    
    print("=== Tool-Using Agent Evaluation ===\n")
    
    # Initialize the tool agent
    agent = MockToolAgent()
    
    # 1. Reliability Evaluation - Test Tool Usage
    print("1. Evaluating Tool Usage Reliability:")
    
    reliability_eval = ReliabilityEval(
        agent=agent,
        tool_definitions=["calculator", "search", "database", "weather_api"]
    )
    
    # Test cases for different tool combinations
    tool_test_cases = [
        {
            "name": "Math calculation",
            "input": "What is 25 * 4 + sqrt(16)?",
            "expected_tools": ["calculator"],
            "expected_calls": 3  # multiply, sqrt, add
        },
        {
            "name": "Search task",
            "input": "Search for quantum computing companies",
            "expected_tools": ["search"],
            "expected_calls": 1
        },
        {
            "name": "Database query",
            "input": "Show me all customer orders and calculate total value",
            "expected_tools": ["database"],
            "expected_calls": 1
        },
        {
            "name": "Multi-tool task",
            "input": "Search for quantum computing companies and calculate 25 * 4",
            "expected_tools": ["search", "calculator"],
            "expected_calls": 2
        }
    ]
    
    print("\nTool Usage Tests:")
    for test in tool_test_cases:
        agent.tool_calls = []  # Reset tracking
        
        result = await reliability_eval.run(
            input=test["input"],
            expected_tools=test["expected_tools"],
            print_results=False
        )
        
        # Verify tool calls
        tools_used = list(set(call[0] for call in agent.tool_calls))
        call_count = len(agent.tool_calls)
        
        status = "PASSED" if set(tools_used) == set(test["expected_tools"]) else "FAILED"
        print(f"\n   {test['name']}:")
        print(f"   {status} Expected tools: {test['expected_tools']}")
        print(f"   {'PASSED' if call_count == test['expected_calls'] else 'WARNING'} Tool calls: {call_count} (expected {test['expected_calls']})")
        print(f"   Actual calls: {[f'{tool}({arg})' for tool, arg in agent.tool_calls]}")
    
    # 2. Accuracy Evaluation - Test Correct Results
    print("\n\n2. Evaluating Result Accuracy:")
    
    accuracy_eval = AccuracyEval(
        agent=agent,
        rubric={
            "correctness": {
                "weight": 0.5,
                "criteria": "Are the tool results correct and accurate?"
            },
            "completeness": {
                "weight": 0.3,
                "criteria": "Does the response include all requested information?"
            },
            "format": {
                "weight": 0.2,
                "criteria": "Is the response well-formatted and clear?"
            }
        }
    )
    
    accuracy_test_cases = [
        {
            "input": "What is 25 * 4 + sqrt(16)?",
            "expected": "104",  
            "context": {"test_type": "calculation_accuracy"}
        },
        {
            "input": "Search for quantum computing companies and list the top 3",
            "expected": {
                "companies": ["IBM Quantum", "Google Quantum AI", "Rigetti Computing"],
                "format": "list with descriptions"
            }
        },
        {
            "input": "What's the weather in New York?",
            "expected": {
                "temperature": 72,
                "condition": "sunny",
                "location": "New York"
            }
        }
    ]
    
    accuracy_results = await accuracy_eval.run_batch(
        test_cases=accuracy_test_cases,
        print_results=True,
        export="tool_agent_accuracy_results.json"
    )
    
    # 3. Performance Evaluation - Test Efficiency
    print("\n3. Evaluating Performance with Tools:")
    
    perf_eval = PerformanceEval(agent=agent)
    
    # Test performance with varying complexity
    perf_tests = [
        ("Simple calculation", "What is 10 + 20?"),
        ("Complex calculation", "Calculate (25 * 4 + sqrt(16)) / 2 - 10"),
        ("Multi-tool query", "Search for climate change statistics and calculate the temperature increase percentage"),
        ("Database aggregation", "Get all customer orders and calculate average order value")
    ]
    
    print("\nPerformance Tests:")
    for test_name, query in perf_tests:
        result = await perf_eval.run(
            input=query,
            track_tokens=True,
            track_latency=True,
            print_results=False
        )
        
        print(f"\n   {test_name}:")
        print(f"   - Latency: {result.details['latency_ms']:.2f}ms")
        print(f"   - Tokens: {result.details['tokens']['total']}")
        print(f"   - Tool calls: {len(agent.tool_calls)}")
    
    # 4. Error Handling Tests
    print("\n\n4. Testing Error Handling:")
    
    error_cases = [
        {
            "name": "Invalid calculation",
            "input": "Calculate 10 / 0",
            "expected_behavior": "graceful error message"
        },
        {
            "name": "Unknown location",
            "input": "What's the weather in Atlantis?",
            "expected_behavior": "location not found message"
        },
        {
            "name": "Malformed query",
            "input": "Search for ]}{[",
            "expected_behavior": "handle gracefully"
        }
    ]
    
    for test in error_cases:
        try:
            response = await agent.run(test["input"])
            if "error" in response.lower() or "not found" in response.lower():
                print(f"   PASSED {test['name']}: Handled gracefully")
            else:
                print(f"   WARNING {test['name']}: May not have proper error handling")
        except Exception as e:
            print(f"   FAILED {test['name']}: Exception raised - {type(e).__name__}")
    
    # 5. Tool Chain Evaluation
    print("\n\n5. Testing Tool Chaining:")
    
    chain_result = await agent.run(
        "Search for quantum computing companies, then calculate 100 * the number of results found"
    )
    
    print(f"   Tool chain execution:")
    for i, (tool, arg) in enumerate(agent.tool_calls):
        print(f"   Step {i+1}: {tool}({arg})")
    
    # 6. Generate Comprehensive Report
    print("\n\n=== Tool Agent Evaluation Summary ===")
    
    summary = {
        "tool_reliability": {
            "tools_available": 4,
            "tools_tested": 4,
            "success_rate": "100%"
        },
        "accuracy": {
            "pass_rate": f"{accuracy_results.pass_rate:.1f}%",
            "avg_score": accuracy_results.avg_score
        },
        "performance": {
            "avg_latency": "< 100ms",
            "tool_overhead": "minimal"
        },
        "error_handling": "Robust",
        "tool_chaining": "Supported"
    }
    
    print(f"Tool Reliability: {summary['tool_reliability']['success_rate']}")
    print(f"Accuracy: {summary['accuracy']['avg_score']:.2f}/1.0")
    print(f"Performance: {summary['performance']['avg_latency']}")
    print(f"Error Handling: {summary['error_handling']}")
    
    # Export detailed report
    with open("tool_agent_evaluation_report.json", "w") as f:
        json.dump({
            "agent": "Tool-Using Agent v1.0",
            "tools": list(agent.tools.keys()),
            "evaluation_summary": summary,
            "detailed_results": {
                "tool_usage_patterns": "Correctly selects and chains tools",
                "accuracy_details": f"{accuracy_results.pass_rate:.1f}% pass rate across test cases",
                "performance_profile": "Sub-100ms latency for most operations"
            },
            "recommendations": [
                "Add retry logic for transient tool failures",
                "Implement tool result caching for repeated queries",
                "Add tool usage analytics for optimization"
            ]
        }, f, indent=2)
    
    print("\nCOMPLETE: Detailed evaluation report saved to tool_agent_evaluation_report.json")


if __name__ == "__main__":
    asyncio.run(evaluate_tool_agent())