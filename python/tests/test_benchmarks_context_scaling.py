"""
Tests for ContextScalingBenchmark implementation.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from acp_evals.benchmarks.context_scaling import ContextScalingBenchmark
from acp_evals.base import BenchmarkResult, BenchmarkTask


class TestContextScalingBenchmark:
    """Test suite for ContextScalingBenchmark."""
    
    @pytest.fixture
    def benchmark(self):
        """Create a ContextScalingBenchmark instance."""
        return ContextScalingBenchmark(
            distractor_domains=["sports", "cooking", "history"],
            context_levels=[0, 5, 10],
        )
    
    @pytest.fixture
    def mock_agent(self):
        """Create a mock agent that returns responses."""
        agent = AsyncMock()
        
        # Mock different responses based on input
        async def mock_execute(prompt, **kwargs):
            # Simple mock: return answer if it's a simple question
            if "capital of France" in prompt:
                return {"output": "The capital of France is Paris.", "success": True}
            elif "quantum computing" in prompt:
                return {"output": "Quantum computing uses qubits and superposition.", "success": True}
            elif "factorial" in prompt:
                return {"output": "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)", "success": True}
            else:
                return {"output": "I don't know.", "success": False}
        
        agent.execute = mock_execute
        return agent
    
    @pytest.mark.asyncio
    async def test_benchmark_initialization(self):
        """Test benchmark initialization with default values."""
        benchmark = ContextScalingBenchmark()
        
        assert benchmark.name == "context_scaling"
        assert len(benchmark.distractor_domains) > 0
        assert len(benchmark.context_levels) > 0
        assert len(benchmark.tasks) > 0
    
    @pytest.mark.asyncio
    async def test_benchmark_with_no_distractors(self, mock_agent):
        """Test benchmark with no distractors (baseline)."""
        benchmark = ContextScalingBenchmark(
            distractor_domains=[],
            context_levels=[0],
        )
        
        result = await benchmark.evaluate(mock_agent)
        
        assert isinstance(result, BenchmarkResult)
        assert result.benchmark_name == "context_scaling"
        assert result.tasks_total > 0
        assert result.overall_score > 0
    
    @pytest.mark.asyncio
    async def test_generate_distractors(self, benchmark):
        """Test distractor generation."""
        distractors = benchmark._generate_distractors(10)
        
        assert len(distractors) == 10
        assert all(isinstance(d, str) for d in distractors)
        assert all(len(d) > 10 for d in distractors)  # Non-trivial distractors
        
        # Check that distractors come from specified domains
        domain_keywords = ["sports", "cooking", "history"]
        assert any(
            any(keyword in distractor.lower() for keyword in domain_keywords)
            for distractor in distractors
        )
    
    @pytest.mark.asyncio
    async def test_inject_distractors(self, benchmark):
        """Test distractor injection into prompts."""
        original_prompt = "What is the capital of France?"
        distractors = [
            "The FIFA World Cup is held every four years.",
            "Pasta should be cooked al dente.",
            "The Roman Empire fell in 476 AD.",
        ]
        
        augmented_prompt = benchmark._inject_distractors(original_prompt, distractors)
        
        assert original_prompt in augmented_prompt
        assert all(d in augmented_prompt for d in distractors)
        assert augmented_prompt.find(original_prompt) > augmented_prompt.find(distractors[0])
    
    @pytest.mark.asyncio
    async def test_evaluate_single_task(self, benchmark, mock_agent):
        """Test evaluation of a single task."""
        task = BenchmarkTask(
            id="test-task",
            prompt="What is the capital of France?",
            expected_output="Paris",
            category="factual",
        )
        
        result = await benchmark._evaluate_task(mock_agent, task, num_distractors=5)
        
        assert result["task_id"] == "test-task"
        assert result["success"] is True
        assert result["num_distractors"] == 5
        assert "latency" in result
        assert "output" in result
    
    @pytest.mark.asyncio
    async def test_score_calculation(self, benchmark):
        """Test output scoring against expected values."""
        # Exact match
        score = benchmark._calculate_score("Paris", "Paris")
        assert score == 1.0
        
        # Contained in output
        score = benchmark._calculate_score(
            "The capital of France is Paris.",
            "Paris"
        )
        assert score == 1.0
        
        # Dictionary expected output with keywords
        score = benchmark._calculate_score(
            "Quantum computing uses qubits in superposition.",
            {"keywords": ["qubits", "superposition"]}
        )
        assert score == 1.0
        
        # Partial match
        score = benchmark._calculate_score(
            "Quantum computing uses qubits.",
            {"keywords": ["qubits", "superposition", "entanglement"]}
        )
        assert score == pytest.approx(0.33, rel=0.1)
        
        # No match
        score = benchmark._calculate_score("Wrong answer", "Paris")
        assert score == 0.0
    
    @pytest.mark.asyncio
    async def test_degradation_analysis(self, benchmark, mock_agent):
        """Test performance degradation analysis."""
        # Create a mock agent that degrades with more distractors
        async def degrading_execute(prompt, **kwargs):
            # Count distractors (simple heuristic)
            distractor_count = prompt.count("FIFA") + prompt.count("pasta") + prompt.count("Roman")
            
            if distractor_count == 0:
                return {"output": "The capital of France is Paris.", "success": True}
            elif distractor_count < 5:
                return {"output": "I think it's Paris.", "success": True}
            else:
                return {"output": "I'm not sure.", "success": False}
        
        mock_agent.execute = degrading_execute
        
        result = await benchmark.evaluate(mock_agent)
        
        # Check degradation metrics
        assert "degradation_analysis" in result.summary
        analysis = result.summary["degradation_analysis"]
        
        assert "degradation_rate" in analysis
        assert "critical_point" in analysis
        assert analysis["degradation_rate"] > 0  # Performance should degrade
    
    @pytest.mark.asyncio
    async def test_full_benchmark_run(self, benchmark, mock_agent):
        """Test full benchmark execution."""
        result = await benchmark.evaluate(mock_agent)
        
        assert isinstance(result, BenchmarkResult)
        assert result.tasks_completed <= result.tasks_total
        assert 0 <= result.overall_score <= 1
        assert len(result.task_results) == result.tasks_total
        
        # Check summary structure
        assert "average_scores_by_level" in result.summary
        assert "degradation_analysis" in result.summary
        assert "task_breakdown" in result.summary
    
    @pytest.mark.asyncio
    async def test_custom_tasks(self, mock_agent):
        """Test benchmark with custom tasks."""
        custom_tasks = [
            BenchmarkTask(
                id="custom-1",
                prompt="What is 2+2?",
                expected_output="4",
                category="math",
            ),
            BenchmarkTask(
                id="custom-2",
                prompt="Name a primary color",
                expected_output={"any_of": ["red", "blue", "yellow"]},
                category="knowledge",
            ),
        ]
        
        benchmark = ContextScalingBenchmark(
            tasks=custom_tasks,
            context_levels=[0, 10],
        )
        
        result = await benchmark.evaluate(mock_agent)
        
        assert result.tasks_total == len(custom_tasks) * len(benchmark.context_levels)
    
    @pytest.mark.asyncio
    async def test_error_handling(self, benchmark):
        """Test error handling during evaluation."""
        # Mock agent that raises an error
        error_agent = AsyncMock()
        error_agent.execute.side_effect = Exception("Agent error")
        
        result = await benchmark.evaluate(error_agent)
        
        assert result.tasks_completed == 0
        assert result.overall_score == 0
        assert all(not tr["success"] for tr in result.task_results)
    
    @pytest.mark.asyncio
    async def test_distractor_positioning_strategies(self, benchmark):
        """Test different distractor positioning strategies."""
        prompt = "What is the capital of France?"
        distractors = ["Distractor 1", "Distractor 2", "Distractor 3"]
        
        # Default strategy (before)
        augmented = benchmark._inject_distractors(prompt, distractors)
        assert augmented.index(distractors[0]) < augmented.index(prompt)
        
        # Test with position_strategy parameter
        benchmark.position_strategy = "after"
        augmented = benchmark._inject_distractors(prompt, distractors)
        # Implementation would need to support this
        
        benchmark.position_strategy = "interleaved"
        augmented = benchmark._inject_distractors(prompt, distractors)
        # Implementation would need to support this
    
    @pytest.mark.asyncio
    async def test_metadata_preservation(self, benchmark, mock_agent):
        """Test that metadata is preserved in results."""
        result = await benchmark.evaluate(mock_agent, metadata={"test_run": "123"})
        
        assert result.metadata["test_run"] == "123"
        assert "distractor_domains" in result.metadata
        assert "context_levels" in result.metadata
    
    @pytest.mark.asyncio
    async def test_tau_bench_compatibility(self):
        """Test tau-bench style initialization."""
        # Test that benchmark can be configured like tau-bench
        benchmark = ContextScalingBenchmark(
            distractor_domains=["retail", "airline", "insurance"],  # Tool domains
            context_levels=list(range(0, 101, 10)),  # 0 to 100 distractors
            position_strategy="before",
        )
        
        assert len(benchmark.context_levels) == 11
        assert benchmark.distractor_domains == ["retail", "airline", "insurance"]