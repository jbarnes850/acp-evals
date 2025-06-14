"""
Domain-specific benchmark templates.
"""

from acp_evals.benchmarks.domains.base import DomainBenchmark
from acp_evals.benchmarks.domains.customer_service import CustomerServiceBenchmark
from acp_evals.benchmarks.domains.code_generation import CodeGenerationBenchmark
from acp_evals.benchmarks.domains.financial_analysis import FinancialAnalysisBenchmark

__all__ = [
    "DomainBenchmark",
    "CustomerServiceBenchmark",
    "CodeGenerationBenchmark",
    "FinancialAnalysisBenchmark",
]