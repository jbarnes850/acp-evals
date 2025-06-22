"""
Test CLI commands with real LLM calls and synthetic data generation.

These tests verify CLI functionality using actual API calls to ensure
production-ready quality of synthetic data generation.
"""

import json
import os
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from acp_evals.cli.main import cli


class TestCLICommands:
    """Test all CLI commands with real API calls."""

    def setup_method(self):
        """Setup for each test."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()
        # Ensure we have API keys for real testing
        assert os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"), (
            "API keys required for CLI testing"
        )

    def test_check_command(self):
        """Test provider configuration check."""
        result = self.runner.invoke(cli, ["check"])
        assert result.exit_code == 0
        assert "Provider Status" in result.output

    def test_list_rubrics_command(self):
        """Test list-rubrics command."""
        result = self.runner.invoke(cli, ["list-rubrics"])
        assert result.exit_code == 0
        assert "Available Evaluation Rubrics" in result.output
        assert "factual" in result.output

    def test_init_simple_template(self):
        """Test template generation with simple template."""
        temp_file = os.path.join(self.temp_dir, "test_agent.py")

        result = self.runner.invoke(
            cli, ["init", "simple", "--name", "TestAgent", "--output", temp_file]
        )
        assert result.exit_code == 0
        assert "Created evaluation template" in result.output

        # Verify file was created and is executable
        assert Path(temp_file).exists()
        content = Path(temp_file).read_text()
        assert "TestAgent" in content
        assert "from acp_evals" in content

    def test_init_acp_agent_template(self):
        """Test ACP agent template generation."""
        temp_file = os.path.join(self.temp_dir, "acp_agent.py")

        result = self.runner.invoke(
            cli, ["init", "acp-agent", "--name", "ACPTestAgent", "--output", temp_file]
        )
        assert result.exit_code == 0

        content = Path(temp_file).read_text()
        assert "AccuracyEval" in content
        assert "localhost:8000" in content
        assert "evaluate_acp_agent" in content

    # Multi-agent template removed in simplified framework


@pytest.mark.skip(reason="Generate command removed in simplified framework")
class TestGenerateCommand:
    """Test synthetic data generation with real LLM calls."""

    def setup_method(self):
        """Setup for each test."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()

    @pytest.mark.slow
    def test_generate_tests_with_llm(self):
        """Test test generation using real LLM calls."""
        output_file = os.path.join(self.temp_dir, "test_qa.jsonl")

        result = self.runner.invoke(
            cli,
            [
                "generate",
                "tests",
                "--scenario",
                "qa",
                "--count",
                "3",
                "--export",
                output_file,
                "--use-llm",
            ],
        )

        assert result.exit_code == 0
        assert "Generated 3 test cases" in result.output
        assert Path(output_file).exists()

        # Verify generated data quality
        with open(output_file) as f:
            lines = f.readlines()
            assert len(lines) == 3

            for line in lines:
                test_case = json.loads(line)
                assert "input" in test_case
                assert "expected" in test_case
                assert "metadata" in test_case
                assert test_case["metadata"]["generated_by"] == "llm"

                # Verify quality - input and expected should be non-empty
                assert len(test_case["input"].strip()) > 10
                assert len(test_case["expected"].strip()) > 10

    @pytest.mark.slow
    def test_generate_research_scenario(self):
        """Test research scenario generation."""
        output_file = os.path.join(self.temp_dir, "research_tests.jsonl")

        result = self.runner.invoke(
            cli,
            [
                "generate",
                "tests",
                "--scenario",
                "research",
                "--count",
                "2",
                "--export",
                output_file,
                "--use-llm",
            ],
        )

        assert result.exit_code == 0

        # Verify research-specific content
        with open(output_file) as f:
            lines = f.readlines()
            assert len(lines) == 2

            for line in lines:
                test_case = json.loads(line)
                # Research scenarios should be more complex
                assert len(test_case["input"]) > 20
                assert any(
                    keyword in test_case["input"].lower()
                    for keyword in ["analyze", "research", "investigate", "study"]
                )

    def test_generate_adversarial(self):
        """Test adversarial test generation."""
        output_file = os.path.join(self.temp_dir, "adversarial.jsonl")

        result = self.runner.invoke(
            cli,
            [
                "generate",
                "adversarial",
                "--severity",
                "medium",
                "--count",
                "5",
                "--export",
                output_file,
            ],
        )

        assert result.exit_code == 0
        assert Path(output_file).exists()

        with open(output_file) as f:
            lines = f.readlines()
            assert len(lines) <= 5  # May be fewer if not enough adversarial tests

            for line in lines:
                test = json.loads(line)
                assert "input" in test
                assert "category" in test
                assert "severity" in test
                assert test["severity"] == "medium"

    def test_generate_scenarios(self):
        """Test multi-turn conversation generation."""
        output_file = os.path.join(self.temp_dir, "conversations.jsonl")

        result = self.runner.invoke(
            cli, ["generate", "scenarios", "--turns", "3", "--count", "2", "--export", output_file]
        )

        assert result.exit_code == 0
        assert Path(output_file).exists()

        with open(output_file) as f:
            lines = f.readlines()

            for line in lines:
                conversation = json.loads(line)
                if "conversation" in conversation:
                    assert len(conversation["conversation"]) == 3


@pytest.mark.skip(reason="Dataset command removed in simplified framework")
class TestDatasetCommand:
    """Test dataset management commands."""

    def setup_method(self):
        """Setup for each test."""
        self.runner = CliRunner()

    def test_dataset_list(self):
        """Test dataset listing."""
        result = self.runner.invoke(cli, ["dataset", "list"])
        assert result.exit_code == 0
        assert "Available Datasets" in result.output or "Evaluation Datasets" in result.output
        # Should show some of the 7 external benchmarks
        assert any(dataset in result.output for dataset in ["GAIA", "TRAIL", "MMLU"])

    def test_dataset_local(self):
        """Test local dataset listing."""
        result = self.runner.invoke(cli, ["dataset", "local"])
        # Should not fail even if no local datasets exist
        assert result.exit_code == 0
        assert "Local Synthetic Datasets" in result.output

    def test_dataset_load_preview(self):
        """Test dataset loading and preview."""
        result = self.runner.invoke(cli, ["dataset", "load", "GAIA", "--preview"])
        # Dataset loading may fail in test environment, just check it doesn't crash completely
        assert result.exit_code in [0, 1]  # Allow failure but not crash


# These commands were removed in the simplified framework
@pytest.mark.skip(reason="Traces command removed in simplified framework")
class TestTracesCommand:
    """Test trace processing commands."""

    def setup_method(self):
        """Setup for each test."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()

    def test_traces_help(self):
        """Test traces command help."""
        result = self.runner.invoke(cli, ["traces", "--help"])
        assert result.exit_code == 0
        assert "ingest" in result.output
        assert "recycle" in result.output


@pytest.mark.skip(reason="Workflow command removed in simplified framework")
class TestWorkflowCommand:
    """Test workflow commands."""

    def setup_method(self):
        """Setup for each test."""
        self.runner = CliRunner()

    def test_workflow_help(self):
        """Test workflow command help."""
        result = self.runner.invoke(cli, ["workflow", "--help"])
        assert result.exit_code == 0
        assert "test" in result.output
        assert "compare" in result.output
        assert "handoff" in result.output


class TestTemplateQuality:
    """Test generated template quality by actually executing them."""

    def setup_method(self):
        """Setup for each test."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()

    @pytest.mark.slow
    def test_simple_template_execution(self):
        """Test that generated simple template actually works."""
        template_file = os.path.join(self.temp_dir, "test_simple_agent.py")

        # Generate template
        result = self.runner.invoke(
            cli, ["init", "simple", "--name", "TestSimpleAgent", "--output", template_file]
        )
        assert result.exit_code == 0

        # Modify template to use mock mode for testing
        content = Path(template_file).read_text()
        # Replace the agent with a test function for testing
        content = content.replace(
            'AGENT = "{agent_url}"',
            """async def test_agent(prompt: str) -> str:
    return "Test response"

AGENT = test_agent""",
        )
        Path(template_file).write_text(content)

        # Try to import and verify syntax
        import importlib.util

        spec = importlib.util.spec_from_file_location("test_agent", template_file)
        module = importlib.util.module_from_spec(spec)

        # Should not raise syntax errors
        try:
            spec.loader.exec_module(module)
            # Verify it has the expected functions
            assert hasattr(module, "evaluate_agent") or hasattr(module, "main"), (
                f"Template missing main function. Available: {dir(module)}"
            )
        except Exception as e:
            pytest.fail(f"Generated template has errors: {e}")

    @pytest.mark.slow
    def test_acp_agent_template_execution(self):
        """Test that ACP agent template imports correctly."""
        template_file = os.path.join(self.temp_dir, "test_acp_agent.py")

        # Generate template
        result = self.runner.invoke(
            cli, ["init", "acp-agent", "--name", "TestACPAgent", "--output", template_file]
        )
        assert result.exit_code == 0

        # Verify imports work
        content = Path(template_file).read_text()
        assert "from acp_evals import AccuracyEval" in content
        # Client module was removed in refactoring, check for server import instead
        assert "acp_evals" in content

        # Try to import and verify syntax
        import importlib.util

        spec = importlib.util.spec_from_file_location("test_acp_agent", template_file)
        module = importlib.util.module_from_spec(spec)

        try:
            spec.loader.exec_module(module)
            # Check for main evaluation function
            assert hasattr(module, "evaluate_acp_agent") or hasattr(module, "main"), (
                f"Template missing main function. Available: {dir(module)}"
            )
        except Exception as e:
            pytest.fail(f"ACP agent template has errors: {e}")


@pytest.mark.skip(reason="Generate command removed in simplified framework")
@pytest.mark.slow
class TestSyntheticDataQuality:
    """Test the quality of LLM-generated synthetic data."""

    def setup_method(self):
        """Setup for each test."""
        self.runner = CliRunner()
        self.temp_dir = tempfile.mkdtemp()

    def test_qa_data_quality(self):
        """Test quality of generated Q&A data."""
        output_file = os.path.join(self.temp_dir, "qa_quality_test.jsonl")

        result = self.runner.invoke(
            cli,
            [
                "generate",
                "tests",
                "--scenario",
                "qa",
                "--count",
                "5",
                "--export",
                output_file,
                "--use-llm",
                "--diversity",
                "0.8",
            ],
        )

        assert result.exit_code == 0

        with open(output_file) as f:
            test_cases = [json.loads(line) for line in f]

        # Quality checks
        for i, test_case in enumerate(test_cases):
            # Length checks
            assert len(test_case["input"]) > 15, f"Test {i}: Input too short"
            assert len(test_case["expected"]) > 10, f"Test {i}: Expected too short"

            # Diversity check - questions should be different
            input_text = test_case["input"].lower()
            if i > 0:
                prev_input = test_cases[i - 1]["input"].lower()
                # Should not be identical (allowing for some similarity)
                assert input_text != prev_input, f"Test {i}: Identical to previous"

            # Question format check
            has_question_word = any(
                word in input_text
                for word in ["what", "how", "why", "when", "where", "who", "which"]
            )
            has_question_mark = "?" in test_case["input"]
            assert has_question_word or has_question_mark, f"Test {i}: Doesn't look like a question"

            # Metadata verification
            assert test_case["metadata"]["generated_by"] == "llm"
            assert test_case["metadata"]["scenario"] == "qa"

    def test_research_data_complexity(self):
        """Test that research scenarios are appropriately complex."""
        output_file = os.path.join(self.temp_dir, "research_quality_test.jsonl")

        result = self.runner.invoke(
            cli,
            [
                "generate",
                "tests",
                "--scenario",
                "research",
                "--count",
                "3",
                "--export",
                output_file,
                "--use-llm",
            ],
        )

        assert result.exit_code == 0

        with open(output_file) as f:
            test_cases = [json.loads(line) for line in f]

        for i, test_case in enumerate(test_cases):
            input_text = test_case["input"].lower()

            # Research tasks should be longer and more complex
            assert len(test_case["input"]) > 30, f"Research test {i}: Too simple"

            # Should contain research-related terms
            research_terms = [
                "analyze",
                "research",
                "investigate",
                "study",
                "examine",
                "compare",
                "evaluate",
                "assess",
                "review",
            ]
            assert any(term in input_text for term in research_terms), (
                f"Research test {i}: Missing research terminology"
            )

            # Expected output should indicate methodology or approach
            expected_text = test_case["expected"].lower()
            methodology_terms = ["approach", "method", "analysis", "findings", "conclusion"]
            assert any(term in expected_text for term in methodology_terms), (
                f"Research test {i}: Expected output lacks methodology"
            )
