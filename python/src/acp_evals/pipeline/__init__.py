"""
Evaluation orchestration for ACP-Evals.

Quality evaluators, simulator, and continuous evaluation pipeline.
"""

from acp_evals.pipeline.continuous import (
    ContinuousEvaluationPipeline,
    EvaluationRun,
    RegressionAlert,
    start_continuous_evaluation,
)
from acp_evals.evaluators.quality.quality import (
    CompletenessEval,
    GroundednessEval,
    QualityEval,
    TaskAdherenceEval,
    ToolAccuracyEval,
)
from acp_evals.pipeline.simulator import (
    Simulator,
    simulate,
)

__all__ = [
    # Quality evaluators
    "GroundednessEval",
    "CompletenessEval",
    "TaskAdherenceEval",
    "ToolAccuracyEval",
    "QualityEval",

    # Simulator
    "Simulator",
    "simulate",

    # Continuous evaluation
    "ContinuousEvaluationPipeline",
    "start_continuous_evaluation",
    "EvaluationRun",
    "RegressionAlert",
]
