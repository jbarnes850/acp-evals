"""
Multi-agent patterns for evaluation.
"""

from acp_evals.patterns.base import AgentPattern
from acp_evals.patterns.linear import LinearPattern
from acp_evals.patterns.supervisor import SupervisorPattern
from acp_evals.patterns.swarm import SwarmPattern

__all__ = ["AgentPattern", "LinearPattern", "SupervisorPattern", "SwarmPattern"]