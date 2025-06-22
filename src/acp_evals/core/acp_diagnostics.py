"""
ACP/BeeAI-aware diagnostics and error messages.

Provides helpful, context-aware error messages for developers
working in the BeeAI/ACP ecosystem.
"""

import re
from typing import Any, Optional


def format_agent_connection_error(
    url: str, error: Exception, expected_name: str | None = None
) -> str:
    """
    Format connection errors with ACP/BeeAI-specific troubleshooting.

    Args:
        url: The agent URL that failed
        error: The underlying exception
        expected_name: Expected agent name if known

    Returns:
        Formatted error message with troubleshooting steps
    """
    # Parse URL to extract useful info
    match = re.match(r"(https?://)?([^:/]+):?(\d+)?(/agents/)?(.+)?", url)
    if match:
        protocol, host, port, path, agent_name = match.groups()
        port = port or "8000"
        agent_name = agent_name or expected_name or "your-agent"
    else:
        host, port, agent_name = "localhost", "8000", "your-agent"

    # Build troubleshooting message
    message = f"""
Could not connect to agent at {url}

Troubleshooting Steps:

1. Check if your agent is running:
   • For ACP agents:
     curl http://{host}:{port}/agents

   • For BeeAI agents:
     bee agent:dev
     bee agent:list

2. Verify the agent URL format:
   • ACP format: http://{host}:{port}/agents/{agent_name}
   • Make sure the agent name matches exactly

3. Check agent configuration:
   • For BeeAI: Check bee.yaml
     name: {agent_name}
     port: {port}

   • For ACP: Check your server.agent() decorator
     @server.agent(name="{agent_name}")

4. View agent logs:
   • BeeAI: bee agent:logs
   • ACP: Check server output

5. Test connectivity:
   curl -X POST http://{host}:{port}/runs \\
     -H "Content-Type: application/json" \\
     -d '{{"agent_name": "{agent_name}", "input": [{{"parts": [{{"content": "test"}}]}}]}}'

Technical details: {str(error)}
"""
    return message.strip()


def format_evaluation_error(error: Exception, context: dict[str, Any]) -> str:
    """
    Format evaluation errors with context-aware suggestions.

    Args:
        error: The evaluation error
        context: Context about the evaluation (agent type, input, etc.)

    Returns:
        Formatted error with suggestions
    """
    error_type = type(error).__name__

    if "timeout" in str(error).lower():
        return f"""
Evaluation Timeout

The agent took too long to respond. This could mean:

1. Complex processing:
   • Your agent might be doing expensive operations
   • Consider implementing streaming responses
   • Add progress indicators in your agent

2. Network issues:
   • Check network connectivity
   • Ensure agent is running locally for faster response

3. Configuration:
   • Increase timeout in TestOptions:
     TestOptions(timeout=30.0)  # 30 seconds

Technical details: {str(error)}
"""

    elif "json" in str(error).lower():
        return f"""
Invalid Agent Response Format

The agent returned a response that couldn't be parsed.

Common causes:
1. Agent returning plain text instead of ACP Message format
2. Malformed JSON in response
3. Binary data not properly encoded

To fix:
• For ACP agents, ensure you return Message objects:
  return Message(parts=[MessagePart(content="response", content_type="text/plain")])

• For BeeAI agents, check your response formatting

Technical details: {str(error)}
"""

    else:
        return f"""
Evaluation Error: {error_type}

{str(error)}

Debug suggestions:
1. Enable verbose mode to see full agent interaction
2. Test agent directly with curl to verify it's working
3. Check agent logs for errors
4. Ensure LLM provider is configured correctly
"""


def suggest_agent_improvements(result: Any, agent_type: str | None = None) -> str:
    """
    Provide actionable suggestions based on evaluation results.

    Args:
        result: The evaluation result
        agent_type: Type of agent (e.g., "customer_support", "code_assistant")

    Returns:
        Formatted suggestions for improvement
    """
    suggestions = []

    if result.score < 0.5:
        suggestions.append("• Core functionality needs work - ensure agent understands basic tasks")
        suggestions.append("• Consider adding more examples to your agent's prompt")

    elif result.score < 0.8:
        suggestions.append("• Good foundation - focus on edge cases and error handling")
        suggestions.append("• Add validation for unexpected inputs")

    if hasattr(result, "details"):
        details = result.details

        # Check for specific issues
        if details.get("latency_ms", 0) > 2000:
            suggestions.append("• Response time is slow (>2s) - consider caching or optimization")

        if "hallucination" in details.get("feedback", "").lower():
            suggestions.append("• Agent may be hallucinating - add grounding with tools or context")

    # Agent-type specific suggestions
    if agent_type == "customer_support":
        suggestions.append("• Ensure polite, helpful tone in all responses")
        suggestions.append("• Add fallback to human support for complex issues")

    elif agent_type == "code_assistant":
        suggestions.append("• Validate generated code syntax")
        suggestions.append("• Include error handling in code examples")

    if suggestions:
        return "\nSuggestions for improvement:\n" + "\n".join(suggestions)
    else:
        return "\n✓ Your agent is performing well! Consider:\n• Adding more test cases\n• Testing edge cases\n• Monitoring production performance"


# Export public API
__all__ = ["format_agent_connection_error", "format_evaluation_error", "suggest_agent_improvements"]
