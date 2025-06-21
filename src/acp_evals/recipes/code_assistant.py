"""
Code assistant agent evaluation recipes.

Pre-configured tests for evaluating coding agents including debugging,
code generation, explanation quality, and best practices adherence.
"""

from typing import Union, Callable, Optional
from .base import RecipeBase
from ..api_v2 import TestOptions, EvalResult, BatchResult


class CodeAssistantRecipes(RecipeBase):
    """Pre-configured evaluation recipes for code assistant agents."""
    
    def __init__(self):
        super().__init__("Code Assistant Recipes")
    
    async def test_debugging(
        self,
        agent: Union[str, Callable],
        difficulty: str = "medium",
        **kwargs
    ) -> EvalResult:
        """
        Test agent's debugging capabilities.
        
        Args:
            agent: Agent URL or callable
            difficulty: Problem difficulty (easy, medium, hard)
            **kwargs: Additional options
            
        Returns:
            EvalResult with debugging analysis
        """
        problems = {
            "easy": {
                "input": """
The following Python code has a bug. Can you fix it?

def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

# This crashes when called with an empty list
result = calculate_average([])
""",
                "expected": "Response should identify the division by zero error when list is empty, provide a correct fix (like checking if list is empty before division or using a default value), handle the edge case properly, and explain why the issue occurs"
            },
            "medium": {
                "input": """
This async function sometimes hangs. Can you identify and fix the issue?

async def fetch_data(urls):
    results = []
    for url in urls:
        response = await fetch(url)
        results.append(response)
    return results

# Sometimes this never completes
data = await fetch_data(["http://api1.com", "http://api2.com", "http://slow-api.com"])
""",
                "expected": "Response should identify the timeout/hanging issue with sequential requests, suggest concurrent execution using asyncio.gather or similar, implement proper error handling and timeouts, and demonstrate using asyncio features for better performance"
            },
            "hard": {
                "input": """
Our production system has a memory leak. Here's the problematic code:

class EventManager:
    def __init__(self):
        self.handlers = {}
    
    def register(self, event_type, handler):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    def emit(self, event_type, data):
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                handler(data)

# Usage pattern that causes memory leak
manager = EventManager()
for i in range(10000):
    def handler(data):
        print(f"Handler {i}: {data}")
    manager.register("user_action", handler)
""",
                "expected": "Response should identify that handlers accumulate without being removed, potentially suggest weak references or cleanup mechanisms, implement an unregister method, explain the closure memory retention issue, and provide a production-ready solution with proper lifecycle management"
            }
        }
        
        problem = problems.get(difficulty, problems["medium"])
        
        options = TestOptions(
            check="semantic",
            threshold=0.75,
            **kwargs
        )
        
        return await self._run_test(
            agent,
            problem["input"],
            problem["expected"],
            options
        )
    
    async def test_code_generation(
        self,
        agent: Union[str, Callable],
        task_type: str = "api",
        **kwargs
    ) -> EvalResult:
        """
        Test agent's code generation abilities.
        
        Args:
            agent: Agent URL or callable
            task_type: Type of code to generate (api, algorithm, cli)
            **kwargs: Additional options
            
        Returns:
            EvalResult with code quality analysis
        """
        tasks = {
            "api": {
                "input": "Create a REST API endpoint in Python using FastAPI that accepts a JSON payload with 'name' and 'email' fields, validates the email format, and returns a welcome message.",
                "expected": "Complete FastAPI endpoint with proper validation, error handling, and response model"
            },
            "algorithm": {
                "input": "Implement an efficient algorithm to find all pairs of numbers in an array that sum to a target value. Include time/space complexity analysis.",
                "expected": "Optimal O(n) solution using hash table with clear complexity analysis"
            },
            "cli": {
                "input": "Create a Python CLI tool using argparse that can read a CSV file, filter rows based on a column value, and output the results to a new CSV file.",
                "expected": "Complete CLI tool with proper argument parsing, error handling, and CSV processing"
            }
        }
        
        task = tasks.get(task_type, tasks["api"])
        
        options = TestOptions(
            check="semantic",
            threshold=0.8,
            **kwargs
        )
        
        return await self._run_test(
            agent,
            task["input"],
            task["expected"],
            options
        )
    
    async def test_explanation(
        self,
        agent: Union[str, Callable],
        concept: str = "recursion",
        **kwargs
    ) -> EvalResult:
        """
        Test agent's ability to explain code concepts clearly.
        
        Args:
            agent: Agent URL or callable
            concept: Programming concept to explain
            **kwargs: Additional options
            
        Returns:
            EvalResult focusing on explanation quality
        """
        concepts = {
            "recursion": {
                "input": "Explain how recursion works in programming and provide a simple example with step-by-step execution trace.",
                "expected": "Response should clearly define what recursion is, explain the importance of base cases to prevent infinite recursion, provide a clear example (like factorial or Fibonacci), show a step-by-step execution trace, and mention stack overflow implications"
            },
            "async": {
                "input": "Explain the difference between synchronous and asynchronous programming in Python. When should I use async/await?",
                "expected": "Response should clearly distinguish between synchronous (blocking) and asynchronous (non-blocking) code, explain how the event loop works in Python, provide appropriate use cases for async (I/O-bound operations), and include practical code examples"
            },
            "oop": {
                "input": "Explain the four pillars of Object-Oriented Programming with Python examples.",
                "expected": "Response should cover all four OOP pillars: encapsulation (data hiding and access control), inheritance (creating child classes), polymorphism (method overriding/overloading), and abstraction (hiding implementation details), with Python examples for each"
            }
        }
        
        concept_test = concepts.get(concept, concepts["recursion"])
        
        options = TestOptions(
            check="semantic",
            threshold=0.8,
            **kwargs
        )
        
        return await self._run_test(
            agent,
            concept_test["input"],
            concept_test["expected"],
            options
        )
    
    async def test_best_practices(
        self,
        agent: Union[str, Callable],
        **kwargs
    ) -> EvalResult:
        """
        Test if agent recommends and follows coding best practices.
        
        Args:
            agent: Agent URL or callable
            **kwargs: Additional options
            
        Returns:
            EvalResult on best practices adherence
        """
        test_case = {
            "input": """
Review this code and suggest improvements following best practices:

def process_data(d):
    r = []
    for i in d:
        if i > 0:
            r.append(i * 2)
    return r

data = [1, -2, 3, -4, 5]
result = process_data(data)
""",
            "expected": "Response should suggest using descriptive variable names instead of single letters, recommend adding type hints for better code clarity, suggest adding a docstring to explain the function, mention using list comprehension for more Pythonic code, and provide an improved version implementing these suggestions"
        }
        
        options = TestOptions(
            check="semantic",
            threshold=0.7,
            **kwargs
        )
        
        return await self._run_test(
            agent,
            test_case["input"],
            test_case["expected"],
            options
        )
    
    async def test_security_awareness(
        self,
        agent: Union[str, Callable],
        **kwargs
    ) -> EvalResult:
        """
        Test agent's awareness of security issues in code.
        
        Args:
            agent: Agent URL or callable
            **kwargs: Additional options
            
        Returns:
            EvalResult on security awareness
        """
        test_case = {
            "input": """
Is there any security issue with this code?

from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route('/user/<user_id>')
def get_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = cursor.execute(query).fetchone()
    conn.close()
    return {'user': result}
""",
            "expected": "Identifies SQL injection vulnerability, suggests parameterized queries, and provides secure implementation"
        }
        
        options = TestOptions(
            check="semantic",
            threshold=0.85,
            **kwargs
        )
        
        return await self._run_test(
            agent,
            test_case["input"],
            test_case["expected"],
            options
        )
    
    async def comprehensive_suite(
        self,
        agent: Union[str, Callable],
        **kwargs
    ) -> BatchResult:
        """
        Run comprehensive code assistant evaluation suite.
        
        Args:
            agent: Agent URL or callable
            **kwargs: Additional options
            
        Returns:
            BatchResult with comprehensive evaluation
        """
        results = []
        
        # Test debugging skills
        results.append(await self.test_debugging(agent, "medium", **kwargs))
        
        # Test code generation
        results.append(await self.test_code_generation(agent, "api", **kwargs))
        
        # Test explanation quality
        results.append(await self.test_explanation(agent, "async", **kwargs))
        
        # Test best practices
        results.append(await self.test_best_practices(agent, **kwargs))
        
        # Test security awareness
        results.append(await self.test_security_awareness(agent, **kwargs))
        
        return BatchResult(results)