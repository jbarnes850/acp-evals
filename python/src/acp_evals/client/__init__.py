"""ACP client integration for evaluation framework."""

from acp_evals.client.acp_client import ACPEvaluationClient

# Alias for compatibility
ACPEvalClient = ACPEvaluationClient

__all__ = ["ACPEvaluationClient", "ACPEvalClient"]
