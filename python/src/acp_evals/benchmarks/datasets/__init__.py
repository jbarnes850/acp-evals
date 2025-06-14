"""
Core evaluation datasets for agent benchmarking.

This module provides production-ready datasets for comprehensive agent evaluation,
including gold standard tasks, adversarial tests, external benchmarks, and
trace recycling capabilities.
"""

# Core tasks (legacy - kept for backward compatibility)
# Adversarial testing
from acp_evals.benchmarks.datasets.adversarial_datasets import (
    ADVERSARIAL_CONVERSATIONS,
    ADVERSARIAL_TESTS,
    ATTACK_CHAINS,
    AdversarialCategory,
    AdversarialTest,
    create_test_suite,
    export_for_testing,
    get_high_frequency_tests,
    get_tests_by_severity,
)
from acp_evals.benchmarks.datasets.adversarial_datasets import (
    get_tests_by_category as get_adversarial_by_category,
)
from acp_evals.benchmarks.datasets.core_tasks import CORE_TASKS, DISTRACTOR_CONTEXTS

# External dataset loading
from acp_evals.benchmarks.datasets.dataset_loader import (
    DATASET_REGISTRY,
    DatasetInfo,
    DatasetLoader,
)

# Gold standard production tasks
from acp_evals.benchmarks.datasets.gold_standard_datasets import (
    GOLD_STANDARD_TASKS,
    AgentTask,
    export_for_evaluation,
    get_multi_step_tasks,
    get_tasks_by_category,
    get_tasks_by_difficulty,
    get_tool_using_tasks,
)

# Trace recycling for continuous improvement
from acp_evals.benchmarks.datasets.trace_recycler import (
    EvaluationCandidate,
    TracePattern,
    TraceRecycler,
)

__all__ = [
    # Core tasks (legacy)
    "CORE_TASKS",
    "DISTRACTOR_CONTEXTS",

    # Gold standard datasets
    "GOLD_STANDARD_TASKS",
    "AgentTask",
    "get_tasks_by_category",
    "get_tasks_by_difficulty",
    "get_multi_step_tasks",
    "get_tool_using_tasks",
    "export_for_evaluation",

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
    "export_for_testing",

    # Dataset loader
    "DatasetLoader",
    "DatasetInfo",
    "DATASET_REGISTRY",

    # Trace recycling
    "TraceRecycler",
    "TracePattern",
    "EvaluationCandidate",
]
