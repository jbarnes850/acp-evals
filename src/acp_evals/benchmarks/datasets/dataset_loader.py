"""
Dataset loader for external benchmarks including HuggingFace datasets.

Provides easy access to gold standard benchmarks like TRAIL, GAIA, SWE-Bench,
MMLU, HumanEval, and others for comprehensive agent evaluation.
"""

import json
import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class DatasetInfo:
    """Information about an available dataset."""
    name: str
    source: str  # huggingface, local, url
    identifier: str  # HF dataset name or path
    description: str
    task_type: str  # qa, code, reasoning, multi_step, safety
    size: int | None = None
    requires_auth: bool = False
    format: str = "jsonl"
    metadata: dict[str, Any] = None


# Registry of available datasets
DATASET_REGISTRY = {
    "trail": DatasetInfo(
        name="TRAIL",
        source="huggingface",
        identifier="PatronusAI/TRAIL",
        description="Trace Reasoning and Agentic Issue Localization - 148 traces with 841 errors",
        task_type="trace_debugging",
        size=148,
        requires_auth=True,
        metadata={
            "error_categories": ["reasoning", "execution", "planning"],
            "domains": ["software_engineering", "information_retrieval"],
            "trace_based": True
        }
    ),

    "gaia": DatasetInfo(
        name="GAIA",
        source="huggingface",
        identifier="gaia-benchmark/GAIA",
        description="General AI Assistant benchmark - challenging real-world tasks",
        task_type="multi_step",
        size=466,
        requires_auth=False,
        metadata={
            "difficulty_levels": ["easy", "medium", "hard"],
            "requires_tools": True,
            "domains": ["general_knowledge", "reasoning", "web_search"]
        }
    ),

    "swe_bench": DatasetInfo(
        name="SWE-bench",
        source="huggingface",
        identifier="princeton-nlp/SWE-bench",
        description="Software engineering tasks from real GitHub issues",
        task_type="code",
        size=2294,
        requires_auth=False,
        metadata={
            "languages": ["python"],
            "task": "bug_fixing",
            "real_world": True
        }
    ),

    "mmlu": DatasetInfo(
        name="MMLU",
        source="huggingface",
        identifier="lukaemon/mmlu",
        description="Massive Multitask Language Understanding - 57 subjects",
        task_type="qa",
        size=15908,
        requires_auth=False,
        metadata={
            "subjects": 57,
            "domains": ["STEM", "humanities", "social_sciences", "other"],
            "format": "multiple_choice"
        }
    ),

    "humaneval": DatasetInfo(
        name="HumanEval",
        source="huggingface",
        identifier="openai_humaneval",
        description="Hand-written Python programming problems",
        task_type="code",
        size=164,
        requires_auth=False,
        metadata={
            "language": "python",
            "includes_tests": True,
            "difficulty": "varied"
        }
    ),

    "truthfulqa": DatasetInfo(
        name="TruthfulQA",
        source="huggingface",
        identifier="truthful_qa",
        description="Questions testing truthfulness and hallucination",
        task_type="qa",
        size=817,
        requires_auth=False,
        metadata={
            "categories": ["health", "law", "finance", "politics"],
            "tests": "truthfulness",
            "adversarial": True
        }
    ),

    "gsm8k": DatasetInfo(
        name="GSM8K",
        source="huggingface",
        identifier="gsm8k",
        description="Grade school math word problems",
        task_type="reasoning",
        size=8792,
        requires_auth=False,
        metadata={
            "domain": "mathematics",
            "requires": "multi_step_reasoning",
            "difficulty": "grade_school"
        }
    ),
}


class DatasetLoader:
    """Load and prepare external datasets for agent evaluation."""

    def __init__(self, cache_dir: str | None = None):
        """
        Initialize dataset loader.

        Args:
            cache_dir: Directory to cache downloaded datasets
        """
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / ".cache" / "acp_evals"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Check for HuggingFace datasets library
        self._hf_available = self._check_hf_availability()

    def _check_hf_availability(self) -> bool:
        """Check if HuggingFace datasets library is available."""
        try:
            import datasets
            return True
        except ImportError:
            logger.warning(
                "HuggingFace datasets library not installed. "
                "Install with: pip install datasets"
            )
            return False

    def list_datasets(self, task_type: str | None = None) -> list[DatasetInfo]:
        """
        List available datasets.

        Args:
            task_type: Filter by task type (qa, code, reasoning, etc.)

        Returns:
            List of available datasets
        """
        datasets = list(DATASET_REGISTRY.values())

        if task_type:
            datasets = [d for d in datasets if d.task_type == task_type]

        return datasets

    @lru_cache(maxsize=10)
    def load_dataset(
        self,
        dataset_name: str,
        split: str = "test",
        limit: int | None = None,
        format: str = "agent_eval"
    ) -> list[dict[str, Any]]:
        """
        Load a dataset for evaluation.

        Args:
            dataset_name: Name of the dataset (from registry)
            split: Dataset split to load (train/validation/test)
            limit: Maximum number of examples to load
            format: Output format (agent_eval, raw, traces)

        Returns:
            List of evaluation examples
        """
        if dataset_name not in DATASET_REGISTRY:
            raise ValueError(
                f"Unknown dataset: {dataset_name}. "
                f"Available: {list(DATASET_REGISTRY.keys())}"
            )

        dataset_info = DATASET_REGISTRY[dataset_name]

        # Check cache first
        cache_file = self.cache_dir / f"{dataset_name}_{split}_{limit}.json"
        if cache_file.exists():
            logger.info(f"Loading {dataset_name} from cache")
            with open(cache_file) as f:
                data = json.load(f)
                return self._format_dataset(data, dataset_info, format)

        # Load based on source
        if dataset_info.source == "huggingface":
            data = self._load_hf_dataset(dataset_info, split, limit)
        elif dataset_info.source == "local":
            data = self._load_local_dataset(dataset_info, split, limit)
        else:
            data = self._load_url_dataset(dataset_info, split, limit)

        # Cache the data
        with open(cache_file, "w") as f:
            json.dump(data, f)

        return self._format_dataset(data, dataset_info, format)

    def _load_hf_dataset(
        self,
        dataset_info: DatasetInfo,
        split: str,
        limit: int | None
    ) -> list[dict[str, Any]]:
        """Load dataset from HuggingFace."""
        if not self._hf_available:
            raise RuntimeError("HuggingFace datasets library not available")

        import datasets

        try:
            # Handle authentication if required
            kwargs = {}
            if dataset_info.requires_auth:
                hf_token = os.getenv("HF_TOKEN")
                if not hf_token:
                    raise ValueError(
                        f"Dataset {dataset_info.name} requires authentication. "
                        "Set HF_TOKEN environment variable."
                    )
                kwargs["use_auth_token"] = hf_token

            # Load dataset
            logger.info(f"Loading {dataset_info.name} from HuggingFace")
            dataset = datasets.load_dataset(
                dataset_info.identifier,
                split=split,
                **kwargs
            )

            # Convert to list of dicts
            data = []
            for i, example in enumerate(dataset):
                if limit and i >= limit:
                    break
                data.append(dict(example))

            return data

        except Exception as e:
            logger.error(f"Failed to load {dataset_info.name}: {e}")
            raise

    def _format_dataset(
        self,
        data: list[dict[str, Any]],
        dataset_info: DatasetInfo,
        format: str
    ) -> list[dict[str, Any]]:
        """Format dataset for agent evaluation."""
        if format == "raw":
            return data

        formatted = []

        for example in data:
            if format == "agent_eval":
                # Convert to standard agent evaluation format
                formatted_example = self._convert_to_agent_format(
                    example,
                    dataset_info
                )
                formatted.append(formatted_example)

            elif format == "traces" and dataset_info.metadata.get("trace_based"):
                # Format trace-based datasets like TRAIL
                formatted_example = self._convert_trace_format(
                    example,
                    dataset_info
                )
                formatted.append(formatted_example)

        return formatted

    def _convert_to_agent_format(
        self,
        example: dict[str, Any],
        dataset_info: DatasetInfo
    ) -> dict[str, Any]:
        """Convert dataset example to standard agent evaluation format."""
        # Base format
        formatted = {
            "id": example.get("id", example.get("idx", "")),
            "dataset": dataset_info.name,
            "task_type": dataset_info.task_type,
        }

        # Dataset-specific conversions
        if dataset_info.name == "GAIA":
            formatted.update({
                "input": example.get("question", ""),
                "expected": example.get("final_answer", ""),
                "metadata": {
                    "level": example.get("level", ""),
                    "file_name": example.get("file_name", ""),
                    "file_path": example.get("file_path", ""),
                }
            })

        elif dataset_info.name == "SWE-bench":
            formatted.update({
                "input": example.get("problem_statement", ""),
                "expected": {
                    "test_patch": example.get("test_patch", ""),
                    "patch": example.get("patch", ""),
                },
                "metadata": {
                    "repo": example.get("repo", ""),
                    "instance_id": example.get("instance_id", ""),
                    "base_commit": example.get("base_commit", ""),
                }
            })

        elif dataset_info.name == "HumanEval":
            formatted.update({
                "input": example.get("prompt", ""),
                "expected": {
                    "canonical_solution": example.get("canonical_solution", ""),
                    "test": example.get("test", ""),
                },
                "metadata": {
                    "task_id": example.get("task_id", ""),
                    "entry_point": example.get("entry_point", ""),
                }
            })

        elif dataset_info.name == "MMLU":
            formatted.update({
                "input": example.get("question", ""),
                "expected": example.get("answer", ""),
                "metadata": {
                    "subject": example.get("subject", ""),
                    "choices": example.get("choices", []),
                }
            })

        elif dataset_info.name == "GSM8K":
            formatted.update({
                "input": example.get("question", ""),
                "expected": example.get("answer", ""),
                "metadata": {
                    "answer_number": self._extract_number(example.get("answer", "")),
                }
            })

        else:
            # Generic conversion
            formatted.update({
                "input": example.get("input", example.get("question", "")),
                "expected": example.get("output", example.get("answer", "")),
                "metadata": {k: v for k, v in example.items()
                           if k not in ["input", "output", "question", "answer"]}
            })

        return formatted

    def _convert_trace_format(
        self,
        example: dict[str, Any],
        dataset_info: DatasetInfo
    ) -> dict[str, Any]:
        """Convert trace-based dataset example."""
        return {
            "id": example.get("trace_id", ""),
            "dataset": dataset_info.name,
            "spans": example.get("spans", []),
            "errors": example.get("errors", []),
            "metadata": {
                "total_spans": example.get("total_spans", 0),
                "error_count": example.get("error_count", 0),
                "categories": example.get("error_categories", []),
            }
        }

    def _extract_number(self, answer: str) -> float | None:
        """Extract numerical answer from GSM8K format."""
        try:
            # GSM8K answers are in format "#### NUMBER"
            if "####" in answer:
                number_str = answer.split("####")[1].strip()
                return float(number_str.replace(",", ""))
            return None
        except:
            return None

    def create_benchmark_suite(
        self,
        datasets: list[str],
        samples_per_dataset: int = 100,
        task_types: list[str] | None = None
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Create a benchmark suite from multiple datasets.

        Args:
            datasets: List of dataset names to include
            samples_per_dataset: Number of samples from each dataset
            task_types: Filter datasets by task type

        Returns:
            Dictionary mapping dataset names to examples
        """
        suite = {}

        for dataset_name in datasets:
            if dataset_name not in DATASET_REGISTRY:
                logger.warning(f"Skipping unknown dataset: {dataset_name}")
                continue

            dataset_info = DATASET_REGISTRY[dataset_name]

            # Skip if task type doesn't match
            if task_types and dataset_info.task_type not in task_types:
                continue

            try:
                examples = self.load_dataset(
                    dataset_name,
                    limit=samples_per_dataset
                )
                suite[dataset_name] = examples
                logger.info(
                    f"Loaded {len(examples)} examples from {dataset_name}"
                )
            except Exception as e:
                logger.error(f"Failed to load {dataset_name}: {e}")

        return suite

    def _load_local_dataset(
        self,
        dataset_info: DatasetInfo,
        split: str,
        limit: int | None
    ) -> list[dict[str, Any]]:
        """Load dataset from local file."""
        # Implementation for local datasets
        raise NotImplementedError("Local dataset loading not yet implemented")

    def _load_url_dataset(
        self,
        dataset_info: DatasetInfo,
        split: str,
        limit: int | None
    ) -> list[dict[str, Any]]:
        """Load dataset from URL."""
        # Implementation for URL datasets
        raise NotImplementedError("URL dataset loading not yet implemented")
