"""
Semantic evaluator designed for production-realistic evaluation of multi-step agent tasks.
"""

import json
import logging
from typing import Any, Dict

try:
    from ..providers.openai_provider import OpenAIProvider
except ImportError:
    OpenAIProvider = None
from .base import EvaluationResult, Evaluator

logger = logging.getLogger(__name__)


class SemanticEvaluator(Evaluator):
    """
    LLM-based semantic evaluator using GPT-4.1-nano for high-quality assessment.
    
    Designed to replace keyword matching with true semantic understanding,
    enabling TRAIL-level evaluation quality for production agent scenarios.
    """
    
    @property
    def name(self) -> str:
        """Evaluator name."""
        return "SemanticEvaluator"
    
    async def evaluate(self, 
                      task: str, 
                      response: str, 
                      reference: str | None = None, 
                      context: dict[str, Any] | None = None) -> EvaluationResult:
        """
        Main evaluation method required by base class.
        
        Args:
            task: Task/prompt given to agent
            response: Agent's response to evaluate
            reference: Expected response (optional, will use semantic criteria if available)
            context: Additional context including evaluation criteria
            
        Returns:
            EvaluationResult with semantic assessment
        """
        # Use context to get semantic evaluation criteria if available
        if context and "evaluation_criteria" in context:
            criteria = context["evaluation_criteria"]
            pass_threshold = context.get("pass_threshold", 0.7)
            expected_tools = context.get("expected_tools")
            expected_steps = context.get("expected_steps")
            
            return await self.evaluate_semantic(
                task=task,
                response=response,
                criteria=criteria,
                pass_threshold=pass_threshold,
                expected_tools=expected_tools,
                expected_steps=expected_steps
            )
        else:
            # Fallback to basic semantic evaluation
            basic_criteria = {
                "relevance": {"weight": 0.4, "description": "Response addresses the task appropriately"},
                "accuracy": {"weight": 0.3, "description": "Information provided is factually correct"},
                "completeness": {"weight": 0.3, "description": "Response covers all aspects of the task"}
            }
            
            return await self.evaluate_semantic(
                task=task,
                response=response,
                criteria=basic_criteria,
                pass_threshold=0.7
            )
    
    SYSTEM_PROMPT = """You are an expert evaluator for AI agent responses. Your role is to semantically assess whether agent responses meet specific criteria, going beyond keyword matching to understand true meaning and quality.

You will be given:
1. A task/prompt that was given to the agent
2. The agent's response
3. Evaluation criteria with weights and descriptions
4. Expected tools/steps (if applicable)

For each criterion, score from 0.0 to 1.0 based on how well the response meets that specific requirement. Consider:
- Semantic meaning, not just keyword presence
- Quality and depth of reasoning
- Practical applicability
- Technical accuracy
- Completeness relative to the criterion

Return your evaluation as JSON in this exact format:
{
    "scores": {
        "criterion_name": {"score": 0.0-1.0, "reasoning": "explanation"},
        ...
    },
    "overall_score": 0.0-1.0,
    "passed": true/false,
    "feedback": "Overall assessment of response quality and areas for improvement"
}

Be precise, fair, and focus on semantic understanding rather than surface-level pattern matching."""

    def __init__(self, 
                 model: str = "gpt-4.1-nano",
                 provider_config: Dict[str, Any] | None = None,
                 mock_mode: bool = False):
        """
        Initialize semantic evaluator.
        
        Args:
            model: Model to use for evaluation (default: gpt-4.1-nano)
            provider_config: Optional provider configuration
            mock_mode: Use mock responses for testing
        """
        self.model = model
        self.mock_mode = mock_mode or OpenAIProvider is None
        if not self.mock_mode:
            self.provider = OpenAIProvider(config=provider_config or {})
        else:
            self.provider = None
        
    async def evaluate_semantic(self,
                              task: str,
                              response: str, 
                              criteria: Dict[str, Dict[str, Any]],
                              pass_threshold: float = 0.7,
                              expected_tools: list[str] | None = None,
                              expected_steps: list[Dict[str, str]] | None = None) -> EvaluationResult:
        """
        Evaluate agent response using semantic understanding.
        
        Args:
            task: Original task/prompt given to agent
            response: Agent's response to evaluate
            criteria: Evaluation criteria with weights and descriptions
            pass_threshold: Minimum score to pass (default: 0.7)
            expected_tools: Expected tools agent should use (optional)
            expected_steps: Expected reasoning steps (optional)
            
        Returns:
            EvaluationResult with semantic scores and feedback
        """
        
        # Build evaluation prompt
        evaluation_prompt = self._build_evaluation_prompt(
            task, response, criteria, expected_tools, expected_steps
        )
        
        try:
            # Get evaluation from LLM or mock
            if self.mock_mode:
                llm_response = self._get_mock_evaluation(response, criteria)
            else:
                llm_response = await self.provider.generate(
                    messages=[
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user", "content": evaluation_prompt}
                    ],
                    model=self.model,
                    temperature=0.1,  # Low temperature for consistent evaluation
                    max_tokens=1000
                )
            
            # Parse evaluation result
            evaluation_data = json.loads(llm_response)
            
            # Validate response format
            if not self._validate_evaluation_format(evaluation_data):
                raise ValueError("Invalid evaluation format from LLM")
                
            # Calculate weighted score
            weighted_score = self._calculate_weighted_score(
                evaluation_data["scores"], criteria
            )
            
            return EvaluationResult(
                score=weighted_score,
                passed=weighted_score >= pass_threshold,
                feedback=evaluation_data["feedback"],
                breakdown=evaluation_data["scores"],
                metadata={
                    "evaluator": "semantic_llm",
                    "model": self.model,
                    "pass_threshold": pass_threshold,
                    "criteria_count": len(criteria)
                }
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM evaluation response: {e}")
            return EvaluationResult(
                score=0.0,
                passed=False,
                feedback=f"Evaluation failed: Invalid JSON response from LLM",
                breakdown={},
                metadata={"error": "json_parse_failure"}
            )
        except Exception as e:
            logger.error(f"Semantic evaluation failed: {e}")
            return EvaluationResult(
                score=0.0,
                passed=False,
                feedback=f"Evaluation failed: {str(e)}",
                breakdown={},
                metadata={"error": str(e)}
            )
    
    def _build_evaluation_prompt(self,
                               task: str,
                               response: str,
                               criteria: Dict[str, Dict[str, Any]],
                               expected_tools: list[str] | None,
                               expected_steps: list[Dict[str, str]] | None) -> str:
        """Build the evaluation prompt for the LLM."""
        
        prompt_parts = [
            "## TASK GIVEN TO AGENT:",
            task,
            "",
            "## AGENT'S RESPONSE:",
            response,
            "",
            "## EVALUATION CRITERIA:"
        ]
        
        for criterion_name, criterion_data in criteria.items():
            weight = criterion_data.get("weight", 0.0)
            description = criterion_data.get("description", "")
            prompt_parts.append(f"**{criterion_name}** (weight: {weight}): {description}")
        
        if expected_tools:
            prompt_parts.extend([
                "",
                "## EXPECTED TOOLS:",
                ", ".join(expected_tools)
            ])
            
        if expected_steps:
            prompt_parts.extend([
                "",
                "## EXPECTED REASONING STEPS:"
            ])
            for i, step in enumerate(expected_steps, 1):
                action = step.get("action", "")
                target = step.get("target", "")
                prompt_parts.append(f"{i}. {action}: {target}")
        
        prompt_parts.extend([
            "",
            "Evaluate the agent's response against each criterion. Focus on semantic understanding and practical quality, not keyword matching."
        ])
        
        return "\n".join(prompt_parts)
    
    def _validate_evaluation_format(self, data: Dict[str, Any]) -> bool:
        """Validate the evaluation response format."""
        required_fields = ["scores", "overall_score", "passed", "feedback"]
        
        if not all(field in data for field in required_fields):
            return False
            
        if not isinstance(data["scores"], dict):
            return False
            
        # Check score format
        for criterion_scores in data["scores"].values():
            if not isinstance(criterion_scores, dict):
                return False
            if "score" not in criterion_scores or "reasoning" not in criterion_scores:
                return False
            if not (0.0 <= criterion_scores["score"] <= 1.0):
                return False
                
        return True
    
    def _calculate_weighted_score(self,
                                scores: Dict[str, Dict[str, Any]],
                                criteria: Dict[str, Dict[str, Any]]) -> float:
        """Calculate weighted overall score."""
        total_weight = 0.0
        weighted_sum = 0.0
        
        for criterion_name, criterion_data in criteria.items():
            weight = criterion_data.get("weight", 0.0)
            if criterion_name in scores:
                score = scores[criterion_name]["score"]
                weighted_sum += score * weight
                total_weight += weight
        
        if total_weight == 0:
            return 0.0
            
        return weighted_sum / total_weight
    
    def _get_mock_evaluation(self, response: str, criteria: Dict[str, Dict[str, Any]]) -> str:
        """Generate mock evaluation for testing."""
        # Simple heuristic-based mock scoring
        response_lower = response.lower()
        response_length = len(response)
        
        mock_scores = {}
        
        for criterion_name, criterion_data in criteria.items():
            # Base score starts at 0.5
            score = 0.5
            
            # Adjust based on response characteristics
            if response_length > 200:
                score += 0.2  # Longer responses get bonus
            if response_length > 1000:
                score += 0.1  # Very detailed responses
                
            # Criterion-specific scoring
            if "accuracy" in criterion_name.lower() or "technical" in criterion_name.lower():
                if any(tech_term in response_lower for tech_term in ["api", "database", "transaction", "algorithm"]):
                    score += 0.2
                    
            if "implementation" in criterion_name.lower() or "solution" in criterion_name.lower():
                if "```" in response or "implementation" in response_lower:
                    score += 0.2
                    
            if "comparison" in criterion_name.lower() or "analysis" in criterion_name.lower():
                if any(comp_word in response_lower for comp_word in ["versus", "compared", "analysis", "better", "worse"]):
                    score += 0.2
                    
            # Cap at 1.0
            score = min(score, 1.0)
            
            mock_scores[criterion_name] = {
                "score": score,
                "reasoning": f"Mock evaluation based on response characteristics for {criterion_name}"
            }
        
        # Calculate overall score
        total_weight = sum(c.get("weight", 0.0) for c in criteria.values())
        if total_weight > 0:
            overall_score = sum(mock_scores[name]["score"] * criteria[name].get("weight", 0.0) 
                              for name in criteria.keys()) / total_weight
        else:
            overall_score = sum(mock_scores[name]["score"] for name in criteria.keys()) / len(criteria)
        
        mock_response = {
            "scores": mock_scores,
            "overall_score": overall_score,
            "passed": overall_score >= 0.7,
            "feedback": f"Mock evaluation: Response shows {'good' if overall_score > 0.7 else 'moderate'} quality with {response_length} characters"
        }
        
        return json.dumps(mock_response)


class TraceStepValidator:
    """
    Validates agent reasoning traces against expected steps and tool usage.
    
    Works with SemanticEvaluator to provide TRAIL-level trace evaluation.
    """
    
    def __init__(self, semantic_evaluator: SemanticEvaluator):
        self.evaluator = semantic_evaluator
    
    async def validate_trace_steps(self,
                                 response: str,
                                 expected_steps: list[Dict[str, str]],
                                 expected_tools: list[str]) -> Dict[str, Any]:
        """
        Validate that agent response demonstrates expected reasoning steps.
        
        Args:
            response: Agent's response to analyze
            expected_steps: Expected reasoning steps with actions and targets
            expected_tools: Expected tools to be used
            
        Returns:
            Validation results with step-by-step analysis
        """
        
        validation_criteria = {
            "demonstrates_systematic_approach": {
                "weight": 0.3,
                "description": "Shows systematic, step-by-step approach to problem solving"
            },
            "uses_appropriate_tools": {
                "weight": 0.3, 
                "description": f"Uses appropriate tools from: {', '.join(expected_tools)}"
            },
            "follows_logical_sequence": {
                "weight": 0.2,
                "description": "Follows logical sequence of reasoning steps"
            },
            "shows_verification": {
                "weight": 0.2,
                "description": "Shows verification or validation of intermediate results"
            }
        }
        
        task = f"Analyze this response for systematic reasoning approach using these expected steps: {expected_steps}"
        
        result = await self.evaluator.evaluate_semantic(
            task=task,
            response=response,
            criteria=validation_criteria,
            expected_tools=expected_tools,
            expected_steps=expected_steps,
            pass_threshold=0.6  # Lower threshold for trace validation
        )
        
        return {
            "step_validation_score": result.score,
            "follows_expected_approach": result.passed,
            "step_analysis": result.breakdown,
            "reasoning_quality": result.feedback
        }