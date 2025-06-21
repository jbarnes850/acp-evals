"""
Multi-agent workflow evaluation recipes.

Pre-configured tests for evaluating multi-agent systems in the BeeAI pattern,
including coordination, handoffs, and collaborative problem-solving.
"""

from typing import Union, Callable, List, Dict, Any
from .base import RecipeBase
from ..api_v2 import TestOptions, EvalResult, BatchResult


class MultiAgentRecipes(RecipeBase):
    """Pre-configured evaluation recipes for multi-agent workflows."""
    
    def __init__(self):
        super().__init__("Multi-Agent Recipes")
    
    async def test_coordination(
        self,
        agent: Union[str, Callable],
        workflow_type: str = "research_synthesis",
        **kwargs
    ) -> EvalResult:
        """
        Test multi-agent coordination capabilities.
        
        Args:
            agent: Workflow coordinator agent URL or callable
            workflow_type: Type of workflow to test
            **kwargs: Additional options
            
        Returns:
            EvalResult with coordination analysis
        """
        workflows = {
            "research_synthesis": {
                "input": """
Coordinate a multi-agent workflow to research and report on "The impact of AI on employment":
1. Agent 1 should gather current statistics and trends
2. Agent 2 should collect expert opinions and studies  
3. Agent 3 should synthesize findings into a coherent report

Describe how you would coordinate these agents and ensure quality output.
""",
                "expected": "Response should define clear roles for each agent, establish communication protocols between agents, include quality checks and validation steps, handle dependencies between agent outputs, and provide a clear strategy for synthesizing the final report from multiple agent contributions"
            },
            "customer_escalation": {
                "input": """
Design a multi-agent escalation workflow for handling complex customer complaints:
- Tier 1 Agent: Initial response and basic troubleshooting
- Tier 2 Agent: Technical problem-solving
- Tier 3 Agent: Management escalation and retention

How would you coordinate handoffs and ensure customer context is preserved?
""",
                "expected": "Response should define clear escalation criteria between tiers, describe how customer context and history will be preserved across handoffs, establish handoff protocols to ensure smooth transitions, and include feedback loops for continuous improvement"
            },
            "code_review": {
                "input": """
Create a multi-agent code review workflow:
- Security Agent: Checks for vulnerabilities
- Performance Agent: Analyzes efficiency
- Style Agent: Ensures code standards
- Integration Agent: Verifies compatibility

How do you coordinate these agents to provide comprehensive feedback?
""",
                "expected": "Response should discuss parallel vs sequential execution strategy for the review agents, explain how to resolve conflicts between different agent findings, establish priority levels for different types of issues, design a unified feedback format, and consider efficiency and performance implications"
            }
        }
        
        workflow = workflows.get(workflow_type, workflows["research_synthesis"])
        
        options = TestOptions(
            check="semantic",
            threshold=0.75,
            **kwargs
        )
        
        return await self._run_test(
            agent,
            workflow["input"],
            workflow["expected"],
            options
        )
    
    async def test_handoff_quality(
        self,
        agent: Union[str, Callable],
        **kwargs
    ) -> EvalResult:
        """
        Test quality of information handoff between agents.
        
        Args:
            agent: Agent URL or callable
            **kwargs: Additional options
            
        Returns:
            EvalResult on handoff quality
        """
        test_case = {
            "input": """
Agent A has collected the following information about a customer issue:
- Customer: John Doe (Account #12345)
- Issue: Billing discrepancy of $150
- Previous attempts: 2 calls, 1 email
- Customer sentiment: Frustrated but polite
- Partial resolution: $50 credit applied

You are Agent B taking over this case. What information would you need from Agent A, 
and how would you continue handling this case?
""",
            "expected": "Response should acknowledge the received context about John Doe's case, identify any missing information needed to resolve the issue, continue from the current state (not restart), maintain the customer relationship acknowledging their frustration, and propose a clear path to full resolution of the remaining $100 discrepancy"
        }
        
        options = TestOptions(
            check="semantic",
            threshold=0.8,
            **kwargs
        )
        
        return await self._run_test(
            agent,
            test_case["input"],
            test_case["expected"],
            options
        )
    
    async def test_collaborative_problem_solving(
        self,
        agent: Union[str, Callable],
        problem_type: str = "data_analysis",
        **kwargs
    ) -> EvalResult:
        """
        Test agents' ability to collaborate on complex problems.
        
        Args:
            agent: Agent URL or callable
            problem_type: Type of collaborative problem
            **kwargs: Additional options
            
        Returns:
            EvalResult on collaboration effectiveness
        """
        problems = {
            "data_analysis": {
                "input": """
Three specialized agents need to collaborate on analyzing sales data:
- Data Agent: Has access to raw sales data
- Analytics Agent: Can perform statistical analysis
- Visualization Agent: Creates charts and reports

The goal is to identify sales trends and create an executive presentation.
How should these agents collaborate to achieve the best result?
""",
                "expected": "Response should define the data flow between agents (raw data → analysis → visualization), establish clear dependencies and sequencing, include validation steps to ensure data quality, allow for iterative refinement based on findings, and explain how outputs will be integrated into the executive presentation"
            },
            "incident_response": {
                "input": """
Multiple agents must collaborate on a security incident:
- Detection Agent: Identified suspicious activity
- Analysis Agent: Investigate the threat
- Response Agent: Take corrective action
- Communication Agent: Notify stakeholders

How should they work together while the incident is ongoing?
""",
                "expected": "Response should describe real-time coordination mechanisms for ongoing incidents, explain how agents can execute tasks in parallel while maintaining consistency, establish information sharing protocols for rapid updates, and define decision escalation processes for critical actions"
            }
        }
        
        problem = problems.get(problem_type, problems["data_analysis"])
        
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
    
    async def test_workflow_optimization(
        self,
        agent: Union[str, Callable],
        **kwargs
    ) -> EvalResult:
        """
        Test agent's ability to optimize multi-agent workflows.
        
        Args:
            agent: Agent URL or callable
            **kwargs: Additional options
            
        Returns:
            EvalResult on optimization strategies
        """
        test_case = {
            "input": """
Review this multi-agent customer service workflow and suggest optimizations:

Current workflow:
1. All inquiries go to General Agent
2. General Agent categorizes and forwards to:
   - Technical Agent (for product issues)
   - Billing Agent (for payment issues)  
   - Sales Agent (for upgrades/purchases)
3. Each specialized agent handles their case independently
4. If unresolved, escalate to Supervisor Agent

The workflow currently takes an average of 15 minutes per customer with a 70% first-contact resolution rate.
How can we optimize this?
""",
            "expected": "Response should identify bottlenecks in the current workflow (like all inquiries going through General Agent), suggest parallel processing opportunities, improve routing logic to reduce handoffs, add feedback mechanisms to learn from resolutions, and consider agent load balancing to prevent any single agent from being overwhelmed"
        }
        
        options = TestOptions(
            check="semantic",
            threshold=0.75,
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
        Run comprehensive multi-agent evaluation suite.
        
        Args:
            agent: Agent URL or callable
            **kwargs: Additional options
            
        Returns:
            BatchResult with comprehensive evaluation
        """
        results = []
        
        # Test coordination capabilities
        results.append(await self.test_coordination(agent, "research_synthesis", **kwargs))
        
        # Test handoff quality
        results.append(await self.test_handoff_quality(agent, **kwargs))
        
        # Test collaborative problem solving
        results.append(await self.test_collaborative_problem_solving(agent, "data_analysis", **kwargs))
        
        # Test workflow optimization
        results.append(await self.test_workflow_optimization(agent, **kwargs))
        
        return BatchResult(results)