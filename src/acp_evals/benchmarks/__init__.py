"""
Benchmarks for evaluating ACP agents.

This package provides various benchmarks to test agent capabilities
across different dimensions, including gold standard datasets, adversarial
testing, and trace-based evaluation.
"""

from acp_evals.benchmarks.context_scaling import ContextScalingBenchmark
from acp_evals.benchmarks.datasets.adversarial_datasets import (
    ADVERSARIAL_CONVERSATIONS,
    ADVERSARIAL_TESTS,
    ATTACK_CHAINS,
    AdversarialCategory,
    AdversarialTest,
    create_test_suite,
    get_high_frequency_tests,
    get_tests_by_severity,
)
from acp_evals.benchmarks.datasets.adversarial_datasets import (
    get_tests_by_category as get_adversarial_by_category,
)
from acp_evals.benchmarks.datasets.dataset_loader import (
    DATASET_REGISTRY,
    DatasetInfo,
    DatasetLoader,
)

# Import dataset modules
from acp_evals.benchmarks.datasets.gold_standard_datasets import (
    GOLD_STANDARD_TASKS,
    AgentTask,
    get_multi_step_tasks,
    get_tasks_by_category,
    get_tasks_by_difficulty,
    get_tool_using_tasks,
)
from acp_evals.benchmarks.datasets.trace_recycler import (
    EvaluationCandidate,
    TracePattern,
    TraceRecycler,
)
from acp_evals.benchmarks.multi_agent import HandoffQualityBenchmark, PatternComparisonBenchmark

__all__ = [
    # Benchmark classes
    "ContextScalingBenchmark",
    "HandoffQualityBenchmark",
    "PatternComparisonBenchmark",

    # Gold standard datasets
    "GOLD_STANDARD_TASKS",
    "AgentTask",
    "get_tasks_by_category",
    "get_tasks_by_difficulty",
    "get_multi_step_tasks",
    "get_tool_using_tasks",

    # Adversarial datasets
    "ADVERSARIAL_TESTS",
    "ADVERSARIAL_CONVERSATIONS",
    "ATTACK_CHAINS",
    "AdversarialTest",
    "AdversarialCategory",
    "get_adversarial_by_category",
    "get_tests_by_severity",
    "get_high_frequency_tests",
    "create_test_suite",

    # Dataset loader
    "DatasetLoader",
    "DatasetInfo",
    "DATASET_REGISTRY",

    # Trace recycling
    "TraceRecycler",
    "TracePattern",
    "EvaluationCandidate",
]
