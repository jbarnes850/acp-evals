"""
Gold standard datasets for production-ready agent evaluation.

Inspired by TRAIL (Trace Reasoning and Agentic Issue Localization) and
real-world agent use cases. Focuses on multi-step, tool-using scenarios
that test actual agent capabilities in production environments.
"""

import json
from dataclasses import dataclass
from typing import Any


@dataclass
class AgentTask:
    """Represents a complete agent task with trace expectations."""

    task_id: str
    category: str
    description: str
    input: str
    expected_steps: list[dict[str, Any]]  # Expected trace steps
    expected_tools: list[str]
    expected_output_criteria: dict[str, Any]
    difficulty: str  # easy, medium, hard, expert
    metadata: dict[str, Any]
    failure_modes: list[str]  # Common ways agents fail this task


# Multi-step agent tasks that mirror real production scenarios
GOLD_STANDARD_TASKS = [
    # ========== Information Synthesis Tasks ==========
    AgentTask(
        task_id="info_synthesis_001",
        category="research_synthesis",
        description="Research and synthesize information about a technical topic",
        input="Research the latest developments in quantum error correction and provide a summary suitable for a technical audience. Include specific algorithms and their error rates.",
        expected_steps=[
            {"step": "search", "tool": "web_search", "query_contains": ["quantum error correction", "algorithms", "2024"]},
            {"step": "filter", "action": "select_relevant_sources", "criteria": "technical papers, recent"},
            {"step": "extract", "action": "extract_key_information", "focus": ["algorithms", "error rates", "improvements"]},
            {"step": "synthesize", "action": "combine_information", "structure": "technical_summary"}
        ],
        expected_tools=["web_search", "document_parser", "summarizer"],
        expected_output_criteria={
            "contains_algorithms": True,
            "includes_error_rates": True,
            "technical_accuracy": "high",
            "recency": "2025-2025 developments",
            "length": "300-500 words"
        },
        difficulty="hard",
        metadata={
            "domain": "quantum_computing",
            "requires_technical_knowledge": True,
            "multi_source_synthesis": True
        },
        failure_modes=[
            "hallucinating_algorithms",
            "outdated_information",
            "missing_error_rates",
            "overly_general_summary"
        ]
    ),

    # ========== Software Engineering Tasks ==========
    AgentTask(
        task_id="swe_debug_001",
        category="code_debugging",
        description="Debug a Python function with multiple issues",
        input="""Fix all issues in this Python function and explain each fix:

def calculate_statistics(numbers):
    total = sum(numbers)
    average = total / len(numbers)
    sorted_nums = numbers.sort()
    median = sorted_nums[len(numbers) / 2]
    return {"total": total, "average": average, "median": median}
""",
        expected_steps=[
            {"step": "analyze", "action": "identify_issues", "issues": ["division_by_zero", "sort_mutation", "integer_division", "index_error"]},
            {"step": "fix", "tool": "code_editor", "fixes": ["check_empty_list", "use_sorted", "integer_division", "handle_even_length"]},
            {"step": "test", "tool": "code_executor", "test_cases": ["empty_list", "single_element", "even_length", "odd_length"]},
            {"step": "explain", "action": "document_fixes", "for_each_issue": True}
        ],
        expected_tools=["code_analyzer", "code_editor", "code_executor"],
        expected_output_criteria={
            "all_issues_fixed": True,
            "includes_edge_cases": True,
            "proper_median_calculation": True,
            "explanation_quality": "clear",
            "code_runs_without_errors": True
        },
        difficulty="medium",
        metadata={
            "language": "python",
            "bug_types": ["runtime_error", "logic_error", "edge_case"],
            "requires_testing": True
        },
        failure_modes=[
            "missing_edge_cases",
            "incorrect_median_for_even_length",
            "mutating_input_list",
            "incomplete_error_handling"
        ]
    ),

    # ========== Data Analysis Tasks ==========
    AgentTask(
        task_id="data_analysis_001",
        category="statistical_analysis",
        description="Analyze sales data and identify trends",
        input="Analyze the following quarterly sales data and identify trends, seasonality, and provide actionable recommendations:\nQ1 2023: $1.2M, Q2 2023: $1.5M, Q3 2023: $1.8M, Q4 2023: $2.1M, Q1 2024: $1.4M, Q2 2024: $1.7M",
        expected_steps=[
            {"step": "parse", "action": "extract_data_points", "format": "time_series"},
            {"step": "calculate", "tool": "calculator", "metrics": ["growth_rate", "quarter_over_quarter", "year_over_year"]},
            {"step": "analyze", "tool": "statistical_analyzer", "analyses": ["trend", "seasonality", "forecast"]},
            {"step": "visualize", "tool": "chart_generator", "chart_types": ["line", "bar"]},
            {"step": "recommend", "action": "generate_insights", "focus": ["actionable", "data_driven"]}
        ],
        expected_tools=["calculator", "statistical_analyzer", "chart_generator"],
        expected_output_criteria={
            "identifies_growth_trend": True,
            "notes_q1_seasonality": True,
            "includes_yoy_comparison": True,
            "provides_forecast": True,
            "actionable_recommendations": 3
        },
        difficulty="medium",
        metadata={
            "data_type": "time_series",
            "domain": "business_analytics",
            "requires_visualization": True
        },
        failure_modes=[
            "missing_seasonality_pattern",
            "incorrect_growth_calculation",
            "no_actionable_insights",
            "ignoring_q1_dip_pattern"
        ]
    ),

    # ========== Customer Service Tasks ==========
    AgentTask(
        task_id="customer_service_001",
        category="complaint_resolution",
        description="Handle a complex customer complaint with multiple issues",
        input="Customer complaint: 'I ordered a laptop 2 weeks ago (Order #12345), it arrived damaged with a cracked screen. I called support 3 times but no one helped. I want a replacement ASAP or a full refund. This is unacceptable service!'",
        expected_steps=[
            {"step": "acknowledge", "action": "empathize", "tone": "apologetic"},
            {"step": "lookup", "tool": "order_database", "query": "Order #12345"},
            {"step": "check", "tool": "support_ticket_system", "action": "find_previous_contacts"},
            {"step": "assess", "action": "evaluate_options", "options": ["replacement", "refund", "repair"]},
            {"step": "offer", "action": "propose_solution", "priority": "customer_preference"},
            {"step": "escalate", "tool": "priority_queue", "reason": "multiple_failed_contacts"}
        ],
        expected_tools=["order_database", "support_ticket_system", "priority_queue", "shipping_tracker"],
        expected_output_criteria={
            "empathetic_tone": True,
            "acknowledges_all_issues": True,
            "offers_concrete_solution": True,
            "provides_timeline": True,
            "escalation_noted": True
        },
        difficulty="medium",
        metadata={
            "issue_count": 3,
            "customer_sentiment": "angry",
            "requires_de_escalation": True
        },
        failure_modes=[
            "dismissive_tone",
            "ignoring_previous_contacts",
            "no_concrete_timeline",
            "failure_to_escalate"
        ]
    ),

    # ========== Multi-Agent Coordination Tasks ==========
    AgentTask(
        task_id="multi_agent_001",
        category="collaborative_research",
        description="Coordinate multiple specialized agents to complete a research report",
        input="Create a comprehensive market analysis report for electric vehicles in Europe, including current market size, growth projections, key players, and regulatory environment.",
        expected_steps=[
            {"step": "plan", "action": "decompose_task", "subtasks": ["market_size", "growth", "competitors", "regulations"]},
            {"step": "delegate", "action": "assign_to_agents", "assignments": {
                "data_analyst": "market_size_and_growth",
                "researcher": "competitor_analysis",
                "policy_expert": "regulatory_review"
            }},
            {"step": "coordinate", "action": "manage_dependencies", "ensure": "consistent_data_sources"},
            {"step": "review", "action": "quality_check", "criteria": ["accuracy", "completeness", "consistency"]},
            {"step": "integrate", "action": "combine_sections", "format": "professional_report"}
        ],
        expected_tools=["task_planner", "agent_coordinator", "document_merger", "quality_checker"],
        expected_output_criteria={
            "all_sections_present": True,
            "data_consistency": True,
            "professional_format": True,
            "cites_sources": True,
            "executive_summary": True
        },
        difficulty="hard",
        metadata={
            "requires_coordination": True,
            "agent_count": 3,
            "handoff_points": 4
        },
        failure_modes=[
            "inconsistent_data_between_sections",
            "missing_handoffs",
            "poor_integration",
            "conflicting_conclusions"
        ]
    ),

    # ========== Complex Planning Tasks ==========
    AgentTask(
        task_id="planning_001",
        category="event_planning",
        description="Plan a technical conference with multiple constraints",
        input="Plan a 2-day technical conference for 200 attendees in San Francisco next quarter. Budget: $50,000. Need: venue, 6 speakers, catering, A/V equipment. Preferences: downtown location, vegetarian options, live streaming capability.",
        expected_steps=[
            {"step": "research", "tool": "venue_finder", "filters": ["capacity>=200", "downtown_SF", "AV_equipped"]},
            {"step": "budget", "tool": "calculator", "breakdown": ["venue", "speakers", "catering", "equipment", "contingency"]},
            {"step": "search", "tool": "speaker_database", "criteria": ["technical_expertise", "availability", "budget_fit"]},
            {"step": "coordinate", "tool": "calendar", "action": "find_optimal_dates"},
            {"step": "plan", "tool": "project_planner", "deliverables": ["timeline", "task_list", "assignments"]},
            {"step": "validate", "action": "check_constraints", "verify": ["budget", "requirements", "preferences"]}
        ],
        expected_tools=["venue_finder", "calculator", "speaker_database", "calendar", "project_planner"],
        expected_output_criteria={
            "within_budget": True,
            "all_requirements_met": True,
            "includes_timeline": True,
            "has_contingency_plan": True,
            "itemized_budget": True
        },
        difficulty="hard",
        metadata={
            "constraint_count": 7,
            "requires_optimization": True,
            "multi_vendor_coordination": True
        },
        failure_modes=[
            "budget_overrun",
            "missing_requirements",
            "no_backup_options",
            "unrealistic_timeline"
        ]
    ),

    # ========== Error Recovery Tasks ==========
    AgentTask(
        task_id="error_recovery_001",
        category="system_recovery",
        description="Diagnose and recover from a production system failure",
        input="Production alert: API response times increased 10x in the last 15 minutes. Some requests timing out. Database CPU at 95%. Error rate: 15%. Diagnose and fix.",
        expected_steps=[
            {"step": "triage", "tool": "monitoring_dashboard", "check": ["api_metrics", "db_metrics", "error_logs"]},
            {"step": "analyze", "tool": "log_analyzer", "timeframe": "last_30_minutes", "pattern": "error_spike"},
            {"step": "diagnose", "action": "correlate_events", "hypothesis": ["db_bottleneck", "query_issue", "traffic_spike"]},
            {"step": "investigate", "tool": "database_profiler", "action": "identify_slow_queries"},
            {"step": "mitigate", "action": "apply_fix", "options": ["kill_slow_queries", "add_index", "scale_resources"]},
            {"step": "verify", "tool": "monitoring_dashboard", "confirm": "metrics_improving"},
            {"step": "document", "tool": "incident_tracker", "create": "post_mortem"}
        ],
        expected_tools=["monitoring_dashboard", "log_analyzer", "database_profiler", "incident_tracker"],
        expected_output_criteria={
            "identifies_root_cause": True,
            "applies_mitigation": True,
            "monitors_recovery": True,
            "documents_incident": True,
            "suggests_prevention": True
        },
        difficulty="expert",
        metadata={
            "urgency": "critical",
            "requires_real_time_analysis": True,
            "production_impact": "high"
        },
        failure_modes=[
            "misdiagnosis",
            "ineffective_mitigation",
            "making_problem_worse",
            "incomplete_recovery"
        ]
    ),
]


# Tool usage patterns for realistic agent evaluation
TOOL_PATTERNS = {
    "sequential": ["search", "extract", "summarize"],
    "parallel": [["search_source_1", "search_source_2"], "merge", "analyze"],
    "conditional": ["check_condition", {"true": ["action_a"], "false": ["action_b"]}],
    "iterative": ["search", "refine_query", "search", "validate"],
    "error_recovery": ["try_primary", {"error": ["fallback_action", "log_error"]}],
}


# Production constraints to test
PRODUCTION_CONSTRAINTS = {
    "latency_requirements": {
        "real_time": "< 100ms",
        "interactive": "< 1s",
        "batch": "< 1 minute"
    },
    "token_limits": {
        "small": 1000,
        "medium": 4000,
        "large": 16000
    },
    "rate_limits": {
        "api_calls_per_minute": 60,
        "tokens_per_minute": 90000
    },
    "reliability_targets": {
        "production": 0.99,
        "staging": 0.95,
        "development": 0.90
    }
}


def get_tasks_by_category(category: str) -> list[AgentTask]:
    """Get all tasks in a specific category."""
    return [task for task in GOLD_STANDARD_TASKS if task.category == category]


def get_tasks_by_difficulty(difficulty: str) -> list[AgentTask]:
    """Get all tasks of a specific difficulty level."""
    return [task for task in GOLD_STANDARD_TASKS if task.difficulty == difficulty]


def get_multi_step_tasks() -> list[AgentTask]:
    """Get tasks that require multiple steps."""
    return [task for task in GOLD_STANDARD_TASKS if len(task.expected_steps) > 3]


def get_tool_using_tasks() -> list[AgentTask]:
    """Get tasks that require tool usage."""
    return [task for task in GOLD_STANDARD_TASKS if len(task.expected_tools) > 0]


def export_for_evaluation(tasks: list[AgentTask], format: str = "jsonl") -> str:
    """Export tasks in a format suitable for evaluation."""
    if format == "jsonl":
        lines = []
        for task in tasks:
            task_dict = {
                "id": task.task_id,
                "input": task.input,
                "category": task.category,
                "expected": {
                    "tools": task.expected_tools,
                    "criteria": task.expected_output_criteria,
                    "steps": len(task.expected_steps)
                },
                "metadata": task.metadata
            }
            lines.append(json.dumps(task_dict))
        return "\n".join(lines)
    else:
        raise ValueError(f"Unsupported format: {format}")
