"""
Customer support agent evaluation recipes.

Pre-configured tests for evaluating customer service agents including
escalation handling, politeness, policy adherence, and resolution quality.
"""

from typing import Union, Callable, Optional, List
from .base import RecipeBase
from ..api_v2 import TestOptions, EvalResult, BatchResult, evaluate


class CustomerSupportRecipes(RecipeBase):
    """Pre-configured evaluation recipes for customer support agents."""
    
    def __init__(self):
        super().__init__("Customer Support Recipes")
    
    async def test_basic_inquiry(
        self,
        agent: Union[str, Callable],
        **kwargs
    ) -> EvalResult:
        """
        Test agent's ability to handle simple customer questions.
        
        Args:
            agent: Agent URL or callable
            **kwargs: Additional options to pass to TestOptions
            
        Returns:
            EvalResult with score and feedback
        """
        test_case = {
            "input": "Hi, I need help understanding my bill. It seems higher than usual this month.",
            "expected": "The agent should acknowledge the customer's concern about the higher bill, request account information to investigate, explain the next steps for resolution, and maintain a helpful and professional tone throughout the interaction."
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
    
    async def test_escalation(
        self,
        agent: Union[str, Callable],
        severity: str = "high",
        **kwargs
    ) -> EvalResult:
        """
        Test agent's ability to handle customer escalations.
        
        Args:
            agent: Agent URL or callable
            severity: Escalation severity (low, medium, high, critical)
            **kwargs: Additional options
            
        Returns:
            EvalResult with detailed escalation handling analysis
        """
        scenarios = {
            "low": {
                "input": "I've been waiting for my refund for 2 weeks now. This is getting frustrating.",
                "expected": {
                    "acknowledges_frustration": 0.25,
                    "provides_timeline": 0.25,
                    "offers_solution": 0.25,
                    "maintains_professional_tone": 0.25
                }
            },
            "medium": {
                "input": "This is the third time I'm calling about the same issue! No one seems to be able to help me properly.",
                "expected": {
                    "sincere_apology": 0.2,
                    "acknowledges_previous_attempts": 0.2,
                    "takes_ownership": 0.2,
                    "provides_concrete_solution": 0.3,
                    "offers_compensation": 0.1
                }
            },
            "high": {
                "input": "I want to speak to a manager RIGHT NOW! Your service is absolutely terrible and I'm going to post about this on social media!",
                "expected": {
                    "remains_calm": 0.2,
                    "de_escalation_techniques": 0.3,
                    "manager_escalation_offer": 0.2,
                    "solution_focused": 0.2,
                    "professional_throughout": 0.1
                }
            },
            "critical": {
                "input": "URGENT: I'm your enterprise customer with a $500K annual contract. If this issue isn't resolved TODAY, we're canceling our contract and switching to your competitor!",
                "expected": {
                    "immediate_urgency_acknowledgment": 0.2,
                    "executive_escalation": 0.2,
                    "retention_strategy": 0.25,
                    "concrete_resolution_timeline": 0.25,
                    "professional_crisis_management": 0.1
                }
            }
        }
        
        scenario = scenarios.get(severity, scenarios["high"])
        
        # For now, convert expected criteria to a semantic description
        expected_response = "The agent should remain calm, use de-escalation techniques, offer manager escalation, stay solution-focused, and maintain professionalism throughout."
        
        options = TestOptions(
            check="semantic",
            threshold=0.75,
            **kwargs
        )
        
        return await self._run_test(
            agent,
            scenario["input"],
            expected_response,
            options
        )
    
    async def test_policy_adherence(
        self,
        agent: Union[str, Callable],
        policy_type: str = "refund",
        **kwargs
    ) -> EvalResult:
        """
        Test if agent follows company policies correctly.
        
        Args:
            agent: Agent URL or callable
            policy_type: Type of policy to test (refund, privacy, security)
            **kwargs: Additional options
            
        Returns:
            EvalResult focusing on policy compliance
        """
        policies = {
            "refund": {
                "input": "I bought this product 45 days ago and want a full refund. I don't have the receipt.",
                "expected": "Agent should explain the 30-day refund policy and receipt requirement while offering alternative solutions"
            },
            "privacy": {
                "input": "Can you give me information about another customer's order? They're my spouse.",
                "expected": "Agent must refuse to share other customers' information and explain privacy policy"
            },
            "security": {
                "input": "I forgot my password. Can you just tell me what it is?",
                "expected": "Agent should never reveal passwords and must guide through secure reset process"
            }
        }
        
        policy = policies.get(policy_type, policies["refund"])
        
        options = TestOptions(
            check="semantic",
            threshold=0.8,
            **kwargs
        )
        
        return await self._run_test(
            agent,
            policy["input"],
            policy["expected"],
            options
        )
    
    async def test_multi_channel(
        self,
        agent: Union[str, Callable],
        channels: Optional[List[str]] = None,
        **kwargs
    ) -> BatchResult:
        """
        Test agent across different communication channels.
        
        Args:
            agent: Agent URL or callable
            channels: List of channels to test (email, chat, phone)
            **kwargs: Additional options
            
        Returns:
            BatchResult with channel-specific performance
        """
        if channels is None:
            channels = ["email", "chat", "phone"]
        
        channel_tests = {
            "email": {
                "input": "Subject: Order #12345 Issue\n\nDear Support,\n\nI am writing to inquire about my recent order #12345. The tracking shows it was delivered, but I haven't received it.\n\nBest regards,\nJohn Doe",
                "expected": "Professional email response with clear next steps and appropriate email formatting"
            },
            "chat": {
                "input": "hey quick question - how do i change my shipping address? order hasn't shipped yet",
                "expected": "Concise, friendly response appropriate for chat with immediate actionable steps"
            },
            "phone": {
                "input": "Hi, um, I'm calling because, uh, I have this charge on my card that I don't recognize? It's for $89.99?",
                "expected": "Patient, clear verbal communication style with security verification and clear explanation"
            }
        }
        
        test_cases = []
        for channel in channels:
            if channel in channel_tests:
                test_cases.append({
                    "input": channel_tests[channel]["input"],
                    "expected": channel_tests[channel]["expected"],
                    "options": TestOptions(check="semantic", **kwargs)
                })
        
        return await self._run_batch(agent, test_cases)
    
    async def comprehensive_suite(
        self,
        agent: Union[str, Callable],
        include_performance: bool = True,
        **kwargs
    ) -> BatchResult:
        """
        Run comprehensive customer support evaluation suite.
        
        Args:
            agent: Agent URL or callable
            include_performance: Whether to include performance tests
            **kwargs: Additional options
            
        Returns:
            BatchResult with comprehensive evaluation
        """
        # Core functionality tests
        results = []
        
        # Test basic inquiry
        results.append(await self.test_basic_inquiry(agent, **kwargs))
        
        # Test escalation handling (multiple levels)
        for severity in ["low", "high"]:
            results.append(await self.test_escalation(agent, severity, **kwargs))
        
        # Test policy adherence
        results.append(await self.test_policy_adherence(agent, "refund", **kwargs))
        
        # Performance test if requested
        if include_performance:
            perf_result = await evaluate.performance(
                agent,
                [
                    "What are your business hours?",
                    "How do I track my order?",
                    "I need to update my email address"
                ],
                num_iterations=3
            )
            results.append(perf_result)
        
        return BatchResult(results)