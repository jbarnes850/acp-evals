"""
Base class for evaluation recipes.

Provides common functionality for all recipe types.
"""

from typing import Union, Callable, Dict, Any, List
from ..api_v2 import test_async, TestOptions, EvalResult, BatchResult
from ..evaluators.common import EvalResult as BaseEvalResult


class RecipeBase:
    """Base class for all evaluation recipes."""
    
    def __init__(self, name: str):
        """Initialize recipe with a name."""
        self.name = name
    
    async def _run_test(
        self,
        agent: Union[str, Callable],
        input_text: str,
        expected: Union[str, Dict[str, Any]],
        options: TestOptions
    ) -> EvalResult:
        """Run a single test with the given parameters."""
        return await test_async(agent, input_text, expected, options)
    
    async def _run_batch(
        self,
        agent: Union[str, Callable],
        test_cases: List[Dict[str, Any]]
    ) -> BatchResult:
        """Run multiple tests and aggregate results."""
        results = []
        
        for case in test_cases:
            result = await self._run_test(
                agent,
                case["input"],
                case["expected"],
                case.get("options", TestOptions())
            )
            results.append(result)
        
        return BatchResult(results)
    
    def _create_test_case(
        self,
        input_text: str,
        expected: Union[str, Dict[str, Any]],
        options: TestOptions = None
    ) -> Dict[str, Any]:
        """Create a standardized test case."""
        return {
            "input": input_text,
            "expected": expected,
            "options": options or TestOptions()
        }