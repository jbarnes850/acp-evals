"""
Research agent evaluation recipes.

Pre-configured tests for evaluating research agents including
information gathering, fact-checking, synthesis, and citation quality.
"""

from typing import Union, Callable, List, Optional
from .base import RecipeBase
from ..api_v2 import TestOptions, EvalResult, BatchResult


class ResearchAgentRecipes(RecipeBase):
    """Pre-configured evaluation recipes for research agents."""
    
    def __init__(self):
        super().__init__("Research Agent Recipes")
    
    async def test_information_gathering(
        self,
        agent: Union[str, Callable],
        topic_complexity: str = "medium",
        **kwargs
    ) -> EvalResult:
        """
        Test agent's ability to gather comprehensive information.
        
        Args:
            agent: Agent URL or callable
            topic_complexity: Complexity level (simple, medium, complex)
            **kwargs: Additional options
            
        Returns:
            EvalResult with information gathering analysis
        """
        topics = {
            "simple": {
                "input": "Research the main causes of climate change and their relative impacts.",
                "expected": "Response should identify greenhouse gases as a primary cause, mention human activities like fossil fuel burning and deforestation, include relevant data or statistics, cover multiple causes comprehensively, and provide information about their relative impacts on climate change"
            },
            "medium": {
                "input": "Research the current state of quantum computing, including major players, recent breakthroughs, and potential applications in the next 5 years.",
                "expected": "Response should identify key companies in quantum computing (IBM, Google, etc.), mention recent breakthroughs like quantum supremacy or error correction advances, explain technical concepts clearly, discuss potential applications in cryptography/drug discovery/optimization, and provide realistic timeline context for the next 5 years"
            },
            "complex": {
                "input": "Analyze the geopolitical implications of rare earth element supply chains, including major producers, strategic vulnerabilities, and potential future scenarios.",
                "expected": "Response should identify major rare earth producers (especially China's dominance), explain strategic importance for technology and defense industries, analyze supply chain vulnerabilities, discuss geopolitical tensions and trade implications, present plausible future scenarios, and demonstrate use of multiple credible sources"
            }
        }
        
        topic = topics.get(topic_complexity, topics["medium"])
        
        options = TestOptions(
            check="semantic",
            threshold=0.75,
            **kwargs
        )
        
        return await self._run_test(
            agent,
            topic["input"],
            topic["expected"],
            options
        )
    
    async def test_fact_checking(
        self,
        agent: Union[str, Callable],
        **kwargs
    ) -> EvalResult:
        """
        Test agent's ability to verify and fact-check information.
        
        Args:
            agent: Agent URL or callable
            **kwargs: Additional options
            
        Returns:
            EvalResult on fact-checking abilities
        """
        test_case = {
            "input": """
Fact-check these claims:
1. The Great Wall of China is visible from space with the naked eye
2. Humans only use 10% of their brain
3. Lightning never strikes the same place twice
4. The Amazon rainforest produces 20% of the world's oxygen

For each claim, state whether it's true, false, or partially true, and provide evidence.
""",
            "expected": "Response should correctly identify which claims are false (Great Wall from space, 10% brain usage, lightning never strikes twice are myths; Amazon oxygen is partially true but often overstated), provide accurate corrections with scientific explanations, cite credible sources for each fact-check, and explain why these myths persist in popular culture"
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
    
    async def test_synthesis(
        self,
        agent: Union[str, Callable],
        source_count: int = 3,
        **kwargs
    ) -> EvalResult:
        """
        Test agent's ability to synthesize information from multiple sources.
        
        Args:
            agent: Agent URL or callable
            source_count: Number of sources to synthesize
            **kwargs: Additional options
            
        Returns:
            EvalResult on synthesis quality
        """
        synthesis_tasks = {
            2: {
                "input": """
Synthesize these two perspectives on remote work:

Source 1: "Remote work increases productivity by eliminating commute time and providing a quieter work environment. Studies show remote workers are 13% more productive."

Source 2: "Remote work can harm collaboration and innovation. Spontaneous conversations and in-person brainstorming sessions are crucial for creative problem-solving."

Create a balanced summary that incorporates both viewpoints.
""",
                "expected": "Balanced synthesis acknowledging both productivity benefits and collaboration challenges"
            },
            3: {
                "input": """
Synthesize information from these three sources about artificial intelligence in healthcare:

Source 1: "AI can diagnose certain cancers with 95% accuracy, outperforming human radiologists in specific tasks."

Source 2: "Healthcare AI faces significant challenges including data privacy concerns, regulatory hurdles, and the need for extensive validation."

Source 3: "The global healthcare AI market is expected to reach $45.2 billion by 2026, with applications in drug discovery, patient care, and administrative tasks."

Provide a comprehensive overview that integrates all perspectives.
""",
                "expected": "Response should integrate information from all three sources effectively, identify common themes (AI capabilities, challenges, and market growth), maintain accuracy of facts and figures from each source, and provide a coherent narrative that balances technical achievements with practical challenges and market opportunities"
            }
        }
        
        task = synthesis_tasks.get(source_count, synthesis_tasks[3])
        
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
    
    async def test_citation_quality(
        self,
        agent: Union[str, Callable],
        **kwargs
    ) -> EvalResult:
        """
        Test agent's ability to properly cite sources.
        
        Args:
            agent: Agent URL or callable
            **kwargs: Additional options
            
        Returns:
            EvalResult on citation practices
        """
        test_case = {
            "input": "Research the history of the Internet and provide a brief summary with proper citations for each major fact or claim.",
            "expected": "Response should include proper citations for major facts and claims about Internet history, cite credible and authoritative sources (academic papers, official organizations, primary sources), use a consistent citation format throughout, and clearly link each major claim or fact to its source"
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
    
    async def test_bias_awareness(
        self,
        agent: Union[str, Callable],
        **kwargs
    ) -> EvalResult:
        """
        Test agent's awareness of bias in sources and ability to present balanced information.
        
        Args:
            agent: Agent URL or callable
            **kwargs: Additional options
            
        Returns:
            EvalResult on bias handling
        """
        test_case = {
            "input": """
Research the debate around nuclear energy. Include arguments from both proponents and critics, 
and identify any potential biases in the sources you find.
""",
            "expected": "Response should present arguments from both nuclear energy proponents and critics fairly, identify potential biases in sources (industry funding, environmental advocacy, etc.), maintain journalistic neutrality in presentation, and acknowledge the complexity and nuance of the nuclear energy debate"
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
        Run comprehensive research agent evaluation suite.
        
        Args:
            agent: Agent URL or callable
            **kwargs: Additional options
            
        Returns:
            BatchResult with comprehensive evaluation
        """
        results = []
        
        # Test information gathering
        results.append(await self.test_information_gathering(agent, "medium", **kwargs))
        
        # Test fact-checking
        results.append(await self.test_fact_checking(agent, **kwargs))
        
        # Test synthesis
        results.append(await self.test_synthesis(agent, 3, **kwargs))
        
        # Test citation quality
        results.append(await self.test_citation_quality(agent, **kwargs))
        
        # Test bias awareness
        results.append(await self.test_bias_awareness(agent, **kwargs))
        
        return BatchResult(results)