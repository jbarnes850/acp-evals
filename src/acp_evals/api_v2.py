"""
ACP-Evals v2 API: Professional developer tools for BeeAI/ACP ecosystem.

This module provides the next-generation API focused on simplicity
and power for professional agent builders.
"""

import asyncio
import time
from typing import Any, Optional, Union, Dict, List, Callable
from dataclasses import dataclass, field

# Import base evaluators
from .evaluators.accuracy import AccuracyEval as _BaseAccuracyEval
from .evaluators.common import EvalResult, BatchResult
from .core.validation import InputValidator

# Import ACP SDK types
try:
    from acp_sdk.models import Message, MessagePart
    HAS_ACP = True
except ImportError:
    HAS_ACP = False
    Message = None
    MessagePart = None


@dataclass
class TestOptions:
    """Progressive configuration for test() function."""
    # Basic options
    check: str = "semantic"  # "exact", "semantic", "contains", "tool_usage", "reasoning"
    rubric: Optional[str] = None
    threshold: float = 0.7
    
    # Advanced options
    judge_model: Optional[str] = None
    expected_tools: Optional[List[str]] = None
    expected_steps: Optional[List[Dict[str, str]]] = None
    
    # Professional metrics
    track_latency: bool = True
    track_tokens: bool = True
    show_details: bool = True


def _normalize_input(input_data: Union[str, Message, Dict[str, Any]]) -> str:
    """
    Normalize various input types to string for evaluation.
    
    Supports:
    - Plain strings
    - ACP Message objects
    - Dict representations of messages
    """
    if isinstance(input_data, str):
        return input_data
    
    if HAS_ACP and isinstance(input_data, Message):
        # Extract text from ACP message parts
        text_parts = []
        for part in input_data.parts:
            if part.content_type == "text/plain" and part.content:
                text_parts.append(part.content)
        return " ".join(text_parts)
    
    if isinstance(input_data, dict):
        # Handle dict representation of messages
        if "parts" in input_data:
            text_parts = []
            for part in input_data["parts"]:
                if part.get("content_type") == "text/plain" and part.get("content"):
                    text_parts.append(part["content"])
            return " ".join(text_parts)
        # Simple dict with content
        elif "content" in input_data:
            return str(input_data["content"])
    
    # Fallback to string representation
    return str(input_data)


async def test_async(
    agent: Union[str, Callable],
    input_data: Union[str, Message, Dict[str, Any]],
    expected: Union[str, Dict[str, Any]],
    options: Optional[TestOptions] = None
) -> EvalResult:
    """
    Core async test function with progressive disclosure.
    
    Args:
        agent: Agent URL, callable, or BeeAI agent instance
        input_data: Test input (string, ACP Message, or dict)
        expected: Expected output or behavior
        options: Optional test configuration
        
    Returns:
        EvalResult with score, pass/fail, and detailed feedback
        
    Examples:
        # Simple test
        result = await test_async(agent, "What's 2+2?", "4")
        
        # ACP Message test
        message = Message(parts=[
            MessagePart(content="Analyze this", content_type="text/plain"),
            MessagePart(content=image_data, content_type="image/png")
        ])
        result = await test_async(agent, message, "Identifies key elements")
        
        # Advanced options
        result = await test_async(
            agent, 
            "Plan a trip", 
            {"steps": ["research", "budget", "book"]},
            TestOptions(check="reasoning", expected_steps=[...])
        )
    """
    options = options or TestOptions()
    
    # Normalize input
    input_str = _normalize_input(input_data)
    
    # Choose evaluator based on check type
    if options.check == "exact":
        # Simple exact match - no LLM needed
        response_text = ""
        latency_ms = 0
        
        if callable(agent):
            # Handle callable agents directly
            start_time = time.time()
            if asyncio.iscoroutinefunction(agent):
                response = await agent(input_str)
            else:
                response = agent(input_str)
            response_text = str(response)
            latency_ms = (time.time() - start_time) * 1000
        else:
            # Use BaseEval for URL-based agents
            from .evaluators.common import BaseEval
            
            class ExactMatchEval(BaseEval):
                pass  # Just use inherited _run_agent
                    
            eval_obj = ExactMatchEval(agent=agent)
            result = await eval_obj._run_agent(input_str)
            response_text = result.get("response", "")
            latency_ms = result.get("latency_ms", 0)
        
        # Direct comparison
        score = 1.0 if response_text.strip() == str(expected).strip() else 0.0
        details = {
            "response": response_text,
            "expected": str(expected),
            "match": score == 1.0
        }
        
        if options.track_latency:
            details["latency_ms"] = latency_ms
            
        return EvalResult(
            name="Exact Match Test",
            passed=score >= options.threshold,
            score=score,
            details=details,
            metadata={}
        )
    
    elif options.check in ["semantic", "contains"]:
        # Use accuracy evaluator with appropriate rubric
        rubric = options.rubric or "factual"  # Use factual as default for now
        
        eval_obj = _BaseAccuracyEval(
            agent=agent,
            judge_model=options.judge_model,
            rubric=rubric,
            pass_threshold=options.threshold
        )
        
        expected_str = str(expected) if isinstance(expected, str) else str(expected.get("output", expected))
        return await eval_obj.run(input_str, expected_str)
    
    elif options.check == "tool_usage":
        # TODO: Implement tool usage evaluation
        raise NotImplementedError("Tool usage evaluation coming soon")
    
    elif options.check == "reasoning":
        # TODO: Implement reasoning evaluation
        raise NotImplementedError("Reasoning evaluation coming soon")
    
    else:
        raise ValueError(f"Unknown check type: {options.check}")


def test(
    agent: Union[str, Callable],
    input_data: Union[str, Message, Dict[str, Any]],
    expected: Union[str, Dict[str, Any]],
    options: Optional[TestOptions] = None
) -> EvalResult:
    """
    Synchronous wrapper for test_async.
    
    The primary test function that "just works" for professional developers.
    """
    try:
        # Check if we're already in an event loop
        loop = asyncio.get_running_loop()
        # If we are, create a task
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, test_async(agent, input_data, expected, options))
            return future.result()
    except RuntimeError:
        # No event loop, we can use asyncio.run
        return asyncio.run(test_async(agent, input_data, expected, options))


class evaluate:
    """Enhanced evaluation namespace with BeeAI-specific capabilities."""
    
    @staticmethod
    async def tool_usage(
        agent: Union[str, Callable],
        task: str,
        expected_tools: List[str],
        **kwargs
    ) -> EvalResult:
        """
        Evaluate if agent uses the expected tools for a task.
        
        Args:
            agent: Agent to evaluate
            task: Task description
            expected_tools: List of tool names expected to be used
            
        Returns:
            EvalResult with tool usage analysis
        """
        from .evaluators.tool_usage import ToolUsageEval
        
        eval_obj = ToolUsageEval(
            agent=agent,
            expected_tools=expected_tools,
            **kwargs
        )
        return await eval_obj.run(task)
    
    @staticmethod
    def reasoning(
        agent: Union[str, Callable],
        task: str,
        expected_steps: List[Dict[str, str]],
        **kwargs
    ) -> EvalResult:
        """
        Evaluate agent's reasoning and problem-solving approach.
        
        Args:
            agent: Agent to evaluate
            task: Complex task requiring multi-step reasoning
            expected_steps: Expected reasoning steps
            
        Returns:
            EvalResult with reasoning quality analysis
        """
        # TODO: Implement reasoning evaluation
        raise NotImplementedError("Reasoning evaluation coming soon")
    
    @staticmethod
    async def streaming(agent: Union[str, Callable], prompt: str):
        """
        Evaluate streaming responses chunk by chunk.
        
        Yields:
            Evaluation results for each chunk with coherence and relevance scores
        """
        # TODO: Implement streaming evaluation
        raise NotImplementedError("Streaming evaluation coming soon")
    
    @staticmethod
    def conversation(agent: Union[str, Callable]):
        """
        Create a stateful conversation evaluator.
        
        Returns:
            ConversationEvaluator instance for multi-turn testing
        """
        # TODO: Implement conversation evaluation
        raise NotImplementedError("Conversation evaluation coming soon")
    
    @staticmethod
    async def performance(
        agent: Union[str, Callable],
        test_inputs: Union[str, List[str]],
        num_iterations: int = 5,
        **kwargs
    ) -> EvalResult:
        """
        Evaluate agent performance (latency, memory, tokens).
        
        Args:
            agent: Agent to evaluate
            test_inputs: Input text or list of inputs
            num_iterations: Number of test iterations
            
        Returns:
            EvalResult with performance metrics
        """
        from .evaluators.performance import PerformanceEval
        
        eval_obj = PerformanceEval(
            agent=agent,
            num_iterations=num_iterations,
            **kwargs
        )
        return await eval_obj.run(test_inputs)
    
    @staticmethod
    def comprehensive(
        agent: Union[str, Callable],
        test_suite: Optional[str] = None
    ) -> BatchResult:
        """
        Run comprehensive evaluation suite on an agent.
        
        Args:
            agent: Agent to evaluate
            test_suite: Optional test suite name (e.g., "customer_support", "code_assistant")
            
        Returns:
            BatchResult with detailed performance metrics
        """
        # TODO: Implement comprehensive evaluation
        raise NotImplementedError("Comprehensive evaluation coming soon")


def discover() -> List[Dict[str, Any]]:
    """
    Discover available ACP/BeeAI agents.
    
    Returns:
        List of discovered agents with metadata
    """
    # TODO: Implement agent discovery
    # - Scan common ports (8000-8010)
    # - Check for .acp-agents config
    # - Look for bee.yaml files
    raise NotImplementedError("Agent discovery coming soon")


# Import recipes for easy access
from . import recipes

# Export public API
__all__ = [
    "test",
    "test_async",
    "evaluate",
    "discover",
    "TestOptions",
    "EvalResult",
    "BatchResult",
    "recipes"
]