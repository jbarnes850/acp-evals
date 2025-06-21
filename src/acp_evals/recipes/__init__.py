"""
BeeAI evaluation recipes for common agent patterns.

Pre-configured test suites that provide immediate value for developers
building agents in the BeeAI/ACP ecosystem.
"""

from .customer_support import CustomerSupportRecipes
from .code_assistant import CodeAssistantRecipes
from .research import ResearchAgentRecipes
from .multi_agent import MultiAgentRecipes

# Create convenience namespaces
customer_support = CustomerSupportRecipes()
code_assistant = CodeAssistantRecipes()
research = ResearchAgentRecipes()
multi_agent = MultiAgentRecipes()

__all__ = [
    "customer_support",
    "code_assistant", 
    "research",
    "multi_agent",
    "CustomerSupportRecipes",
    "CodeAssistantRecipes",
    "ResearchAgentRecipes",
    "MultiAgentRecipes"
]