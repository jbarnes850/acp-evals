"""
Command-line interface for ACP-Evals.
"""

from acp_evals.cli.check import check_providers
from acp_evals.cli.main import cli, main

__all__ = [
    "cli",
    "main",
    "check_providers",
]
