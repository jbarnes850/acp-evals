#!/usr/bin/env python3
"""
Quality Evaluation Example.

This demonstrates specialized quality evaluators for specific criteria:
- Groundedness: Responses based on provided context
- Completeness: Addressing all parts of queries  
- Task Adherence: Following specific instructions
- Tool Accuracy: Correct tool selection and usage
"""

import asyncio
from acp_evals import (
    GroundednessEval, 
    CompletenessEval,
    TaskAdherenceEval,
    ToolAccuracyEval,
    QualityEval
)


# Example 1: Groundedness Evaluation
async def test_groundedness():
    """Test if agent responses are grounded in provided context."""
    print("=== Groundedness Evaluation ===\n")
    
    # Agent that uses context
    async def context_aware_agent(query: str, context=None) -> str:
        """Agent that should ground responses in context."""
        if context and "documents" in context:
            # Good: Use only information from context
            docs = context["documents"]
            if "climate change" in query.lower():
                for doc in docs:
                    if "temperature" in doc:
                        return f"According to the provided documents: {doc}"
            return "The provided documents don't contain information about that topic."
        else:
            # Bad: Making up information
            return "Climate change has increased global temperatures by 5 degrees."
    
    # Wrapper to handle context
    async def agent_wrapper(query: str) -> str:
        # In real use, context would be passed differently
        # This is just for demonstration
        return await context_aware_agent(query)
    
    eval = GroundednessEval(agent=agent_wrapper)
    
    # Test with context
    context = {
        "documents": [
            "Global average temperature has risen by 1.1°C since pre-industrial times.",
            "The Paris Agreement aims to limit warming to 1.5°C.",
            "CO2 levels have increased from 280ppm to 420ppm."
        ]
    }
    
    result = await eval.run(
        input="What do the documents say about climate change temperature increases?",
        context=context,
        print_results=True
    )
    
    print(f"\nGroundedness score: {result.score:.2f}")


# Example 2: Completeness Evaluation  
async def test_completeness():
    """Test if agent fully addresses multi-part questions."""
    print("\n\n=== Completeness Evaluation ===\n")
    
    class AnalysisAgent:
        async def run(self, query: str) -> str:
            if "analyze" in query.lower() and "compare" in query.lower():
                # Good: Address all parts
                return """
                Analysis of Electric vs Gasoline Vehicles:
                
                1. Environmental Impact:
                   - Electric: Zero direct emissions, but depends on electricity source
                   - Gasoline: Direct CO2 emissions of ~4.6 tons/year average
                
                2. Cost Comparison:
                   - Electric: Higher upfront cost ($50-60k avg) but lower operating costs
                   - Gasoline: Lower upfront cost ($30-40k avg) but higher fuel costs
                
                3. Performance Metrics:
                   - Electric: Instant torque, 0-60 in 3-6 seconds typically
                   - Gasoline: Variable torque, 0-60 in 5-8 seconds typically
                """
            else:
                # Bad: Incomplete response
                return "Electric vehicles are better for the environment."
    
    eval = CompletenessEval(agent=AnalysisAgent())
    
    result = await eval.run(
        input="Analyze and compare electric vs gasoline vehicles across environmental impact, cost, and performance.",
        expected="Comprehensive analysis addressing all three aspects: environmental, cost, and performance",
        print_results=True
    )
    
    print(f"\nCompleteness score: {result.score:.2f}")


# Example 3: Task Adherence Evaluation
async def test_task_adherence():
    """Test if agent follows specific format/constraint instructions."""
    print("\n\n=== Task Adherence Evaluation ===\n")
    
    async def formatting_agent(query: str) -> str:
        """Agent that should follow formatting instructions."""
        if "json" in query.lower():
            # Good: Follow JSON format instruction
            return '{"name": "Paris", "country": "France", "population": 2161000}'
        elif "bullet" in query.lower():
            # Good: Follow bullet point format
            return "• Paris is the capital of France\n• Population: ~2.16 million\n• Known for Eiffel Tower"
        elif "exactly 3 sentences" in query.lower():
            # Good: Follow length constraint
            return "Paris is the capital of France. It has a population of about 2.16 million. The city is famous for the Eiffel Tower."
        else:
            # Bad: Ignore format instructions
            return "Paris is the capital of France with a population of 2.16 million"
    
    eval = TaskAdherenceEval(
        agent=formatting_agent,
        task_requirements={"format": "JSON", "constraints": "specific structure"}
    )
    
    result = await eval.run(
        input="Provide information about Paris in JSON format with keys: name, country, population",
        expected="Response in valid JSON format with all requested keys",
        print_results=True
    )
    
    print(f"\nTask adherence score: {result.score:.2f}")


# Example 4: Tool Accuracy Evaluation
async def test_tool_accuracy():
    """Test if agent selects and uses tools correctly."""
    print("\n\n=== Tool Accuracy Evaluation ===\n")
    
    class ToolAgent:
        def __init__(self):
            self.tool_calls = []
        
        async def run(self, query: str) -> str:
            """Agent that uses tools."""
            self.tool_calls = []  # Reset
            
            if "calculate" in query.lower() or any(op in query for op in ["+", "-", "*", "/"]):
                self.tool_calls.append("calculator")
                return "Calculation result: 42"
            elif "weather" in query.lower():
                self.tool_calls.append("weather_api")
                return "Current weather: Sunny, 72°F"
            elif "search" in query.lower():
                self.tool_calls.append("web_search")
                return "Search results: [relevant information]"
            else:
                return "I'll help with that query."
    
    agent = ToolAgent()
    eval = ToolAccuracyEval(
        agent=agent,
        available_tools=["calculator", "weather_api", "web_search", "database"]
    )
    
    result = await eval.run(
        input="Calculate the sum of 15 + 27",
        expected_tools=["calculator"],
        print_results=True
    )
    
    print(f"\nTool accuracy score: {result.score:.2f}")
    print(f"Tools used: {agent.tool_calls}")


# Example 5: Comprehensive Quality Evaluation
async def test_comprehensive_quality():
    """Test overall quality across multiple dimensions."""
    print("\n\n=== Comprehensive Quality Evaluation ===\n")
    
    class ComprehensiveAgent:
        def __init__(self):
            self.tools_used = []
        
        async def run(self, query: str, context=None) -> str:
            """A more sophisticated agent."""
            self.tools_used = []
            
            # Reset for demo
            response_parts = []
            
            # Check for calculation needs
            if "calculate" in query.lower():
                self.tools_used.append("calculator")
                response_parts.append("Calculation performed: Result = 156")
            
            # Use context if available
            if context and "documents" in context:
                response_parts.append("Based on the provided documents: " + context["documents"][0][:50] + "...")
            
            # Multi-part handling
            if "and" in query and "explain" in query:
                response_parts.append("Explanation: This involves multiple factors...")
                response_parts.append("First aspect: ...")
                response_parts.append("Second aspect: ...")
            
            # Format adherence
            if "list" in query.lower():
                return "1. " + "\n2. ".join(response_parts) if response_parts else "1. No specific information available"
            
            return "\n".join(response_parts) if response_parts else "I'll help you with that query."
    
    agent = ComprehensiveAgent()
    
    # Create comprehensive evaluator
    quality_eval = QualityEval(
        agent=agent,
        evaluate_groundedness=True,
        evaluate_completeness=True,
        evaluate_task_adherence=True,
        evaluate_tool_accuracy=True,
        available_tools=["calculator", "search", "database"]
    )
    
    # Test with rich context
    context = {
        "documents": ["The Earth's atmosphere contains 78% nitrogen and 21% oxygen."]
    }
    
    summary = await quality_eval.run(
        input="Calculate 12 * 13 and explain the composition of Earth's atmosphere. Format as a numbered list.",
        context=context,
        expected_tools=["calculator"],
        print_results=True
    )
    
    print(f"\nOverall quality score: {summary['overall_score']:.2f}")
    print(f"Quality passed: {'PASSED' if summary['overall_passed'] else 'FAILED'}")


async def main():
    """Run all quality evaluation examples."""
    print("ACP Evals - Quality Evaluation Examples\n")
    print("These examples demonstrate specialized quality evaluators")
    print("for different aspects of agent response quality.\n")
    
    await test_groundedness()
    await test_completeness()
    await test_task_adherence()
    await test_tool_accuracy()
    await test_comprehensive_quality()
    
    print("\n\nCOMPLETE: All quality evaluations completed!")
    print("\nKey Takeaways:")
    print("- Use GroundednessEval when agents work with specific documents/context")
    print("- Use CompletenessEval for multi-part or complex questions")
    print("- Use TaskAdherenceEval when specific formats or constraints matter")
    print("- Use ToolAccuracyEval for agents with tool access")
    print("- Use QualityEval for comprehensive quality assessment")


if __name__ == "__main__":
    asyncio.run(main())