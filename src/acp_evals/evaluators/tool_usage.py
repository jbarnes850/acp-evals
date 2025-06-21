"""
Tool usage evaluator for BeeAI/ACP agents.

This evaluator checks if agents make expected tool calls,
competing directly with Agno's ReliabilityEval.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass

from ..evaluators.common import BaseEval, EvalResult
from ..core.exceptions import AgentConnectionError
from acp_sdk.client import Client
from acp_sdk.models import Message, MessagePart


@dataclass
class ToolCall:
    """Represents a tool call made by an agent."""
    name: str
    arguments: Dict[str, Any]
    timestamp: float
    result: Optional[Any] = None


class ToolUsageEval(BaseEval):
    """
    Evaluates if an agent makes expected tool calls.
    
    This is ACP-Evals' answer to Agno's ReliabilityEval,
    designed specifically for the BeeAI/ACP ecosystem.
    """
    
    def __init__(
        self,
        agent: Union[str, Any],
        expected_tools: List[str],
        check_order: bool = False,
        check_arguments: Optional[Dict[str, Dict[str, Any]]] = None,
        allow_extra_tools: bool = True,
        name: str = "Tool Usage Evaluation"
    ):
        """
        Initialize tool usage evaluator.
        
        Args:
            agent: Agent URL or instance
            expected_tools: List of tool names expected to be called
            check_order: Whether to enforce tool call order
            check_arguments: Expected arguments for specific tools
            allow_extra_tools: Whether to allow additional tool calls
            name: Name of the evaluation
        """
        super().__init__(agent, name)
        self.expected_tools = expected_tools
        self.check_order = check_order
        self.check_arguments = check_arguments or {}
        self.allow_extra_tools = allow_extra_tools
    
    async def run(
        self,
        input_text: str,
        max_steps: int = 10,
        timeout: float = 30.0
    ) -> EvalResult:
        """
        Run the evaluation and check tool usage.
        
        Args:
            input_text: Input prompt for the agent
            max_steps: Maximum number of agent steps
            timeout: Timeout in seconds
            
        Returns:
            EvalResult with tool usage analysis
        """
        start_time = time.time()
        tool_calls: List[ToolCall] = []
        
        try:
            if isinstance(self.agent, str):
                # For URL-based agents, we need to capture tool calls
                # This requires enhanced ACP client support
                tool_calls = await self._run_with_tool_tracking(
                    input_text, max_steps, timeout
                )
            else:
                # For function-based agents, we need a different approach
                # This would require the agent to expose tool call history
                raise NotImplementedError(
                    "Tool usage evaluation for non-URL agents requires "
                    "agents to expose their tool call history"
                )
            
            # Analyze tool usage
            result = self._analyze_tool_usage(tool_calls)
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            result.details["latency_ms"] = latency_ms
            
            return result
            
        except Exception as e:
            return EvalResult(
                name=self.name,
                passed=False,
                score=0.0,
                details={
                    "error": str(e),
                    "error_type": type(e).__name__
                },
                metadata={}
            )
    
    async def _run_with_tool_tracking(
        self,
        input_text: str,
        max_steps: int,
        timeout: float
    ) -> List[ToolCall]:
        """
        Run agent and track tool calls.
        
        Note: This is a placeholder implementation.
        Real implementation would require enhanced ACP client
        that can stream and capture tool calls.
        """
        # TODO: Implement actual tool call tracking
        # This would require:
        # 1. Enhanced ACP client with streaming support
        # 2. Tool call event capture
        # 3. Real-time monitoring of agent execution
        
        # For now, return mock data to demonstrate the API
        raise NotImplementedError(
            "Tool call tracking requires enhanced ACP client support. "
            "This feature is coming soon!"
        )
    
    def _analyze_tool_usage(self, tool_calls: List[ToolCall]) -> EvalResult:
        """Analyze tool calls against expectations."""
        called_tools = [tc.name for tc in tool_calls]
        
        # Check if all expected tools were called
        missing_tools = set(self.expected_tools) - set(called_tools)
        extra_tools = set(called_tools) - set(self.expected_tools)
        
        # Calculate score
        score = 1.0
        feedback = []
        
        if missing_tools:
            score -= 0.3 * len(missing_tools)
            feedback.append(f"Missing expected tools: {', '.join(missing_tools)}")
        
        if extra_tools and not self.allow_extra_tools:
            score -= 0.2 * len(extra_tools)
            feedback.append(f"Unexpected tool calls: {', '.join(extra_tools)}")
        
        if self.check_order:
            # Check if tools were called in expected order
            expected_order = []
            actual_order = []
            
            for tool in self.expected_tools:
                if tool in called_tools:
                    expected_order.append(tool)
                    actual_order.append(called_tools[called_tools.index(tool)])
            
            if expected_order != actual_order:
                score -= 0.2
                feedback.append("Tools called in wrong order")
        
        # Check arguments if specified
        if self.check_arguments:
            for tc in tool_calls:
                if tc.name in self.check_arguments:
                    expected_args = self.check_arguments[tc.name]
                    for arg, expected_value in expected_args.items():
                        if tc.arguments.get(arg) != expected_value:
                            score -= 0.1
                            feedback.append(
                                f"Tool '{tc.name}' called with wrong argument "
                                f"'{arg}': expected {expected_value}, "
                                f"got {tc.arguments.get(arg)}"
                            )
        
        # Ensure score stays in [0, 1]
        score = max(0.0, min(1.0, score))
        
        return EvalResult(
            name=self.name,
            passed=score >= 0.7,  # Default threshold
            score=score,
            details={
                "expected_tools": self.expected_tools,
                "called_tools": called_tools,
                "missing_tools": list(missing_tools),
                "extra_tools": list(extra_tools),
                "tool_count": len(tool_calls),
                "feedback": "\n".join(feedback) if feedback else "All expected tools called correctly"
            },
            metadata={
                "check_order": self.check_order,
                "allow_extra_tools": self.allow_extra_tools
            }
        )


class ReliabilityEval(ToolUsageEval):
    """
    Alias for ToolUsageEval to match Agno's naming.
    
    This makes migration from Agno easier while maintaining
    our BeeAI/ACP-specific implementation.
    """
    pass