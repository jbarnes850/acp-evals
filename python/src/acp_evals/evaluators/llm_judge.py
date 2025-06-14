"""
LLM-as-Judge evaluator based on Anthropic research.

Uses a single LLM call with structured rubric for consistent evaluation.
"""

import json
from typing import Any, Dict, Optional, List
from acp_sdk.client import Client
from acp_sdk import Message, MessagePart

from acp_evals.evaluators.base import Evaluator, EvaluationResult


class LLMJudge(Evaluator):
    """
    Automated evaluation using LLM with structured rubrics.
    
    Based on Anthropic's findings that single LLM calls with
    comprehensive rubrics are more consistent than multiple calls.
    """
    
    DEFAULT_RUBRIC = {
        "factual_accuracy": {
            "weight": 0.3,
            "criteria": "Does the response accurately answer the question with correct information?"
        },
        "completeness": {
            "weight": 0.25,
            "criteria": "Does the response address all aspects of the task or question?"
        },
        "clarity": {
            "weight": 0.2,
            "criteria": "Is the response clear, well-structured, and easy to understand?"
        },
        "relevance": {
            "weight": 0.15,
            "criteria": "Does the response stay focused on the task without unnecessary information?"
        },
        "efficiency": {
            "weight": 0.1,
            "criteria": "Is the response appropriately concise while remaining complete?"
        }
    }
    
    def __init__(
        self,
        judge_url: str = "http://localhost:8000",
        judge_agent: str = "default",
        rubric: Optional[Dict[str, Dict[str, Any]]] = None,
        pass_threshold: float = 0.7,
    ):
        """
        Initialize LLM Judge.
        
        Args:
            judge_url: URL of the ACP server running the judge agent
            judge_agent: Name of the agent to use as judge
            rubric: Custom evaluation rubric (uses default if None)
            pass_threshold: Minimum score to pass (0.0 to 1.0)
        """
        self.judge_url = judge_url
        self.judge_agent = judge_agent
        self.rubric = rubric or self.DEFAULT_RUBRIC
        self.pass_threshold = pass_threshold
        self.client = Client(base_url=judge_url)
    
    @property
    def name(self) -> str:
        return "llm_judge"
    
    def _build_evaluation_prompt(
        self,
        task: str,
        response: str,
        reference: Optional[str] = None,
    ) -> str:
        """Build the evaluation prompt for the judge LLM."""
        rubric_text = ""
        for criterion, details in self.rubric.items():
            rubric_text += f"\n- {criterion} (weight: {details['weight']}): {details['criteria']}"
        
        prompt = f"""You are an expert evaluator assessing an AI agent's response quality.

Task given to the agent:
{task}

Agent's response:
{response}

{f"Reference answer for comparison:\n{reference}\n" if reference else ""}

Evaluation rubric:{rubric_text}

Instructions:
1. Evaluate the response on each criterion, providing a score from 0.0 to 1.0
2. Calculate the weighted overall score
3. Provide brief, constructive feedback
4. Return your evaluation as a JSON object with this structure:
{{
    "scores": {{
        "criterion_name": score,
        ...
    }},
    "overall_score": weighted_score,
    "passed": true/false (based on >= {self.pass_threshold}),
    "feedback": "Brief explanation of strengths and areas for improvement"
}}

Important: Return ONLY the JSON object, no other text."""
        
        return prompt
    
    async def evaluate(
        self,
        task: str,
        response: str,
        reference: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> EvaluationResult:
        """
        Evaluate an agent response using LLM judge.
        
        Args:
            task: The task/prompt given to the agent
            response: The agent's response
            reference: Optional reference answer
            context: Optional additional context
            
        Returns:
            EvaluationResult with score and breakdown
        """
        # Build evaluation prompt
        eval_prompt = self._build_evaluation_prompt(task, response, reference)
        
        # Create message for judge
        message = Message(
            parts=[MessagePart(content=eval_prompt, content_type="text/plain")]
        )
        
        try:
            # Get evaluation from judge LLM
            run = await self.client.run_sync(
                agent=self.judge_agent,
                input=[message]
            )
            
            # Extract response
            if run.output and run.output[0].parts:
                judge_response = run.output[0].parts[0].content
                
                # Parse JSON response
                try:
                    evaluation = json.loads(judge_response)
                except json.JSONDecodeError:
                    # Try to extract JSON from response
                    import re
                    json_match = re.search(r'\{.*\}', judge_response, re.DOTALL)
                    if json_match:
                        evaluation = json.loads(json_match.group())
                    else:
                        raise ValueError("Could not parse judge response as JSON")
                
                # Create result
                return EvaluationResult(
                    score=evaluation["overall_score"],
                    passed=evaluation["passed"],
                    breakdown=evaluation["scores"],
                    feedback=evaluation["feedback"],
                    metadata={
                        "judge_agent": self.judge_agent,
                        "rubric": self.rubric,
                        "task_length": len(task),
                        "response_length": len(response),
                        "has_reference": reference is not None,
                    }
                )
                
            else:
                # No response from judge
                return EvaluationResult(
                    score=0.0,
                    passed=False,
                    breakdown={},
                    feedback="Judge agent did not provide a response",
                    metadata={"error": "no_response"}
                )
                
        except Exception as e:
            # Handle evaluation errors
            return EvaluationResult(
                score=0.0,
                passed=False,
                breakdown={},
                feedback=f"Evaluation failed: {str(e)}",
                metadata={"error": str(e), "error_type": type(e).__name__}
            )
    
    async def batch_evaluate(
        self,
        evaluations: List[Dict[str, Any]],
        max_concurrent: int = 5,
    ) -> List[EvaluationResult]:
        """
        Evaluate multiple responses in batch.
        
        Args:
            evaluations: List of dicts with 'task', 'response', 'reference' keys
            max_concurrent: Maximum concurrent evaluations
            
        Returns:
            List of EvaluationResults
        """
        import asyncio
        
        results = []
        
        # Process in batches to avoid overwhelming the judge
        for i in range(0, len(evaluations), max_concurrent):
            batch = evaluations[i:i + max_concurrent]
            
            # Create evaluation tasks
            tasks = [
                self.evaluate(
                    task=eval_data["task"],
                    response=eval_data["response"],
                    reference=eval_data.get("reference"),
                    context=eval_data.get("context"),
                )
                for eval_data in batch
            ]
            
            # Run batch concurrently
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
        
        return results