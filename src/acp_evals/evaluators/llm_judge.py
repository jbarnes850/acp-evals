"""LLM Judge for evaluating agent outputs."""

from typing import Optional, Dict, Any
import asyncio
from dataclasses import dataclass

from ..providers.base import LLMProvider
from ..providers.factory import ProviderFactory


@dataclass
class JudgeResult:
    """Result from LLM judge evaluation."""
    score: float
    feedback: str
    passed: bool
    breakdown: Optional[Dict[str, float]] = None


class LLMJudge:
    """Simple LLM-based judge for evaluating outputs."""
    
    def __init__(
        self,
        provider: Optional[LLMProvider] = None,
        rubric: Optional[Dict[str, Any]] = None,
        pass_threshold: float = 0.7,
        model: Optional[str] = None,
        judge_url: Optional[str] = None,
        judge_agent: Optional[str] = None,
        **kwargs
    ):
        """Initialize with optional provider and configuration."""
        self.provider = provider or ProviderFactory.create()
        self.rubric = rubric or {}
        self.pass_threshold = pass_threshold
        self.model = model
        self.judge_url = judge_url
        self.judge_agent = judge_agent
    
    async def evaluate(
        self,
        task: str = None,
        prompt: str = None,
        response: str = None,
        reference: str = None,
        expected: str = None,
        rubric: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> JudgeResult:
        """Evaluate response against expected output."""
        # Use task or prompt for the input
        input_text = task or prompt or ""
        
        # Use reference if expected not provided
        check_against = reference or expected or ""
        
        # Build evaluation prompt
        eval_prompt = f"""
You are an expert evaluator. Please evaluate the following response based on the expected output.

Input: {input_text}
Response: {response}
Expected: {check_against}

Please score the response from 0.0 to 1.0 based on how well it matches the expected output.
Consider:
- Factual accuracy
- Completeness
- Relevance

Respond with:
- Score: [0.0-1.0]
- Feedback: [Brief explanation]
"""
        
        try:
            # Use the LLM provider to evaluate
            result = await self.provider.ainvoke(eval_prompt)
            
            # Parse the response
            lines = result.strip().split('\n')
            score = 0.0
            feedback = ""
            
            for line in lines:
                if line.startswith("Score:"):
                    try:
                        score = float(line.split(":")[-1].strip())
                    except:
                        score = 0.5
                elif line.startswith("Feedback:"):
                    feedback = line.split(":", 1)[-1].strip()
            
            # If we couldn't parse, fall back to simple check
            if score == 0.0 and not feedback:
                score = 1.0 if check_against.lower() in response.lower() else 0.0
                feedback = f"Response {'contains' if score > 0 else 'does not contain'} expected content"
                
        except Exception as e:
            # Fallback to simple evaluation
            score = 1.0 if check_against.lower() in response.lower() else 0.0
            feedback = f"Response {'contains' if score > 0 else 'does not contain'} expected content (fallback evaluation)"
        
        passed = score >= self.pass_threshold
        
        return JudgeResult(
            score=score,
            passed=passed,
            feedback=feedback,
            breakdown={"similarity": score}
        )
    
    async def compare(
        self,
        prompt: str,
        response1: str,
        response2: str,
        criteria: Optional[str] = None
    ) -> Dict[str, Any]:
        """Compare two responses."""
        # Simple similarity check
        similarity = 1.0 if response1.lower() == response2.lower() else 0.5
        
        return {
            "similarity": similarity,
            "feedback": f"Responses are {'identical' if similarity == 1.0 else 'different'}",
            "preferred": None  # No preference in simple implementation
        }