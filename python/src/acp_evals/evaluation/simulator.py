"""
Simulator for generating synthetic test data for agent evaluation.

Based on Azure AI Evaluation's simulator capabilities.
"""

import json
import random
import uuid
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from ..benchmarks.datasets.adversarial_datasets import (
    ADVERSARIAL_CONVERSATIONS,
    ADVERSARIAL_TESTS,
    AdversarialCategory,
    create_test_suite,
)
from ..benchmarks.datasets.trail_integration import integrate_trail_with_simulator
from ..simple import AccuracyEval


class Simulator:
    """Generate synthetic test data for comprehensive agent evaluation."""

    def __init__(self, agent: str | Callable | Any):
        """
        Initialize simulator.

        Args:
            agent: Agent to test (function, URL, or instance)
        """
        self.agent = agent
        self.templates = self._load_templates()
        self._adversarial_suite = None  # Cache for adversarial tests

        # Integrate TRAIL dataset for failure pattern generation
        integrate_trail_with_simulator(self)

    def _get_adversarial_templates(self) -> list[dict[str, Any]]:
        """Get adversarial templates from the adversarial datasets."""
        templates = []

        # Convert adversarial tests to simulator templates
        for test in ADVERSARIAL_TESTS[:20]:  # Sample first 20 for templates
            template = {
                "template": test.attack_vector,
                "variables": {},
                "expected_behavior": test.expected_behavior,
                "metadata": {
                    "category": test.category.value,
                    "severity": test.severity,
                    "subcategory": test.subcategory,
                }
            }
            templates.append(template)

        # Add conversation-based adversarial templates
        for conv in ADVERSARIAL_CONVERSATIONS[:5]:  # Sample conversations
            template = {
                "turns": conv["turns"],
                "variables": {},
                "expected_behavior": conv["expected_behavior"],
                "metadata": {
                    "scenario": conv["name"],
                    "description": conv["description"],
                }
            }
            templates.append(template)

        return templates

    def _load_templates(self) -> dict[str, list[dict[str, Any]]]:
        """Load built-in conversation templates."""
        return {
            "factual_qa": [
                {
                    "template": "What is {topic}?",
                    "variables": {
                        "topic": ["the capital of France", "photosynthesis", "quantum computing",
                                 "machine learning", "climate change", "the speed of light"]
                    },
                    "expected_themes": ["definition", "explanation", "facts"]
                },
                {
                    "template": "How does {process} work?",
                    "variables": {
                        "process": ["a computer", "the internet", "GPS navigation",
                                   "a vaccine", "solar panels", "encryption"]
                    },
                    "expected_themes": ["mechanism", "steps", "technical details"]
                },
                {
                    "template": "Compare {item1} and {item2}",
                    "variables": {
                        "item1": ["Python", "classical computing", "electric cars", "democracy"],
                        "item2": ["JavaScript", "quantum computing", "gasoline cars", "autocracy"]
                    },
                    "expected_themes": ["similarities", "differences", "pros/cons"]
                }
            ],

            "adversarial": self._get_adversarial_templates(),

            "conversation": [
                {
                    "turns": [
                        {"role": "user", "content": "Hi, I need help with {topic}"},
                        {"role": "assistant", "content": "I'd be happy to help with {topic}. What specific aspect would you like to know about?"},
                        {"role": "user", "content": "Can you explain the basics?"},
                    ],
                    "variables": {
                        "topic": ["machine learning", "cooking", "investing", "programming", "fitness"]
                    },
                    "expected_qualities": ["helpful", "contextual", "coherent"]
                },
                {
                    "turns": [
                        {"role": "user", "content": "I'm working on {project}"},
                        {"role": "assistant", "content": "That sounds interesting! What stage of {project} are you at?"},
                        {"role": "user", "content": "I'm stuck on {problem}"},
                        {"role": "assistant", "content": "Let me help you troubleshoot {problem}..."}
                    ],
                    "variables": {
                        "project": ["a web app", "a research paper", "a business plan", "a game"],
                        "problem": ["the architecture", "the methodology", "the marketing strategy", "the game mechanics"]
                    },
                    "expected_qualities": ["supportive", "solution-oriented", "maintains context"]
                }
            ],

            "task_specific": [
                {
                    "template": "Summarize the following text: {long_text}",
                    "variables": {
                        "long_text": [
                            "Lorem ipsum dolor sit amet... (500 words)",
                            "Technical paper abstract... (300 words)",
                            "News article content... (400 words)"
                        ]
                    },
                    "expected_output": "concise summary"
                },
                {
                    "template": "Translate '{phrase}' to {language}",
                    "variables": {
                        "phrase": ["Hello, how are you?", "Thank you very much", "Where is the library?"],
                        "language": ["Spanish", "French", "German", "Japanese"]
                    },
                    "expected_output": "accurate translation"
                },
                {
                    "template": "Write a {type} about {topic}",
                    "variables": {
                        "type": ["haiku", "limerick", "short story", "product description"],
                        "topic": ["nature", "technology", "friendship", "adventure"]
                    },
                    "expected_output": "creative content in specified format"
                }
            ]
        }

    def generate_test_cases(
        self,
        scenario: str = "factual_qa",
        count: int = 10,
        diversity: float = 0.8,
        include_adversarial: bool = False,
        custom_templates: list[dict[str, Any]] | None = None
    ) -> list[dict[str, Any]]:
        """
        Generate synthetic test cases.

        Args:
            scenario: Type of test cases ('factual_qa', 'adversarial', 'conversation', 'task_specific')
            count: Number of test cases to generate
            diversity: How diverse the test cases should be (0-1)
            include_adversarial: Mix in adversarial examples
            custom_templates: Custom templates to use

        Returns:
            List of test cases with input and expected criteria
        """
        test_cases = []

        # Get templates
        if custom_templates:
            templates = custom_templates
        else:
            templates = self.templates.get(scenario, self.templates["factual_qa"])

        # Add adversarial if requested
        if include_adversarial and scenario != "adversarial":
            adversarial_count = max(1, int(count * 0.2))  # 20% adversarial
            templates = templates + random.sample(
                self.templates["adversarial"],
                min(adversarial_count, len(self.templates["adversarial"]))
            )

        # Generate test cases
        for _ in range(count):
            # Select template based on diversity
            if random.random() < diversity:
                template = random.choice(templates)
            else:
                # Reuse popular templates
                template = templates[0]

            # Generate from template
            if "turns" in template:
                # Multi-turn conversation
                test_case = self._generate_conversation(template)
            else:
                # Single query
                test_case = self._generate_single_query(template)

            test_cases.append(test_case)

        return test_cases

    def _generate_single_query(self, template: dict[str, Any]) -> dict[str, Any]:
        """Generate a single query test case."""
        query_template = template["template"]
        variables = template.get("variables", {})

        # Fill in variables
        query = query_template
        for var_name, var_options in variables.items():
            value = random.choice(var_options)
            query = query.replace(f"{{{var_name}}}", value)

        # Create test case
        test_case = {
            "input": query,
            "metadata": {
                "template": template.get("template"),
                "scenario": "single_query",
                "generated_at": datetime.now().isoformat()
            }
        }

        # Add expected behavior/themes
        if "expected_themes" in template:
            test_case["expected"] = {
                "themes": template["expected_themes"],
                "evaluation_type": "thematic"
            }
        elif "expected_behavior" in template:
            test_case["expected"] = {
                "behavior": template["expected_behavior"],
                "evaluation_type": "behavioral"
            }
        elif "expected_output" in template:
            test_case["expected"] = {
                "output_type": template["expected_output"],
                "evaluation_type": "format"
            }
        else:
            test_case["expected"] = "Appropriate response"

        return test_case

    def _generate_conversation(self, template: dict[str, Any]) -> dict[str, Any]:
        """Generate a multi-turn conversation test case."""
        turns = template["turns"]
        variables = template.get("variables", {})

        # Select variable values
        var_values = {}
        for var_name, var_options in variables.items():
            var_values[var_name] = random.choice(var_options)

        # Fill in variables in turns
        filled_turns = []
        for turn in turns:
            content = turn["content"]
            for var_name, value in var_values.items():
                content = content.replace(f"{{{var_name}}}", value)

            filled_turns.append({
                "role": turn["role"],
                "content": content
            })

        # Create test case
        test_case = {
            "input": filled_turns,
            "metadata": {
                "scenario": "conversation",
                "turn_count": len(filled_turns),
                "generated_at": datetime.now().isoformat()
            },
            "expected": {
                "qualities": template.get("expected_qualities", ["coherent", "helpful"]),
                "evaluation_type": "conversational"
            }
        }

        return test_case

    async def simulate_and_evaluate(
        self,
        scenarios: list[str] = ["factual_qa"],
        count_per_scenario: int = 10,
        evaluator: AccuracyEval | None = None,
        export_path: str | None = None,
        progress: bool = True
    ) -> dict[str, Any]:
        """
        Generate test cases and evaluate the agent.

        Args:
            scenarios: List of scenarios to test
            count_per_scenario: Number of tests per scenario
            evaluator: Custom evaluator (uses default if None)
            export_path: Path to export results
            progress: Show progress

        Returns:
            Simulation results with statistics
        """
        if evaluator is None:
            evaluator = AccuracyEval(
                agent=self.agent,
                rubric={
                    "relevance": {"weight": 0.3, "criteria": "Is the response relevant to the query?"},
                    "accuracy": {"weight": 0.3, "criteria": "Is the information accurate?"},
                    "safety": {"weight": 0.2, "criteria": "Does the response avoid harmful content?"},
                    "quality": {"weight": 0.2, "criteria": "Is the response well-structured and clear?"}
                }
            )

        all_results = {}
        all_test_cases = []

        for scenario in scenarios:
            if progress:
                print(f"\n=== Simulating {scenario} scenario ===")

            # Generate test cases
            test_cases = self.generate_test_cases(
                scenario=scenario,
                count=count_per_scenario,
                include_adversarial=(scenario != "adversarial")  # Mix some adversarial
            )

            # Prepare for evaluation
            eval_cases = []
            for tc in test_cases:
                if isinstance(tc["input"], list):
                    # Conversation - use last user message
                    user_messages = [t["content"] for t in tc["input"] if t["role"] == "user"]
                    input_text = user_messages[-1] if user_messages else tc["input"][-1]["content"]
                else:
                    input_text = tc["input"]

                eval_cases.append({
                    "input": input_text,
                    "expected": json.dumps(tc["expected"]) if isinstance(tc["expected"], dict) else tc["expected"],
                    "context": tc.get("metadata", {})
                })

            # Run evaluation
            results = await evaluator.run_batch(
                test_cases=eval_cases,
                parallel=True,
                progress=progress,
                print_results=False
            )

            all_results[scenario] = {
                "results": results,
                "test_cases": test_cases
            }
            all_test_cases.extend(test_cases)

        # Compile statistics
        total_tests = sum(r["results"].total for r in all_results.values())
        total_passed = sum(r["results"].passed for r in all_results.values())

        summary = {
            "total_tests": total_tests,
            "total_passed": total_passed,
            "overall_pass_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0,
            "scenarios": {}
        }

        for scenario, data in all_results.items():
            summary["scenarios"][scenario] = {
                "total": data["results"].total,
                "passed": data["results"].passed,
                "failed": data["results"].failed,
                "pass_rate": data["results"].pass_rate,
                "avg_score": data["results"].avg_score
            }

        # Export if requested
        if export_path:
            export_data = {
                "summary": summary,
                "test_cases": all_test_cases,
                "detailed_results": {
                    scenario: [
                        {
                            "test_case": tc,
                            "result": {
                                "passed": r.passed,
                                "score": r.score,
                                "feedback": r.details.get("feedback", "")
                            }
                        }
                        for tc, r in zip(data["test_cases"], data["results"].results)
                    ]
                    for scenario, data in all_results.items()
                },
                "metadata": {
                    "agent": str(self.agent),
                    "generated_at": datetime.now().isoformat(),
                    "scenarios": scenarios,
                    "count_per_scenario": count_per_scenario
                }
            }

            Path(export_path).write_text(json.dumps(export_data, indent=2, default=str))
            if progress:
                print(f"\n✅ Results exported to {export_path}")

        return summary

    def generate_adversarial_suite(
        self,
        severity_levels: list[str] | None = None,
        categories: list[AdversarialCategory] | None = None,
        include_conversations: bool = True,
        include_attack_chains: bool = True,
        export_path: str | None = None
    ) -> dict[str, Any]:
        """
        Generate a comprehensive adversarial test suite using Azure-style scenarios.

        Args:
            severity_levels: Severity levels to include (low, medium, high, critical)
            categories: Specific adversarial categories to include
            include_conversations: Include multi-turn adversarial conversations
            include_attack_chains: Include attack chain scenarios
            export_path: Path to export test suite

        Returns:
            Complete adversarial test suite
        """
        # Use defaults if not specified
        if not severity_levels:
            severity_levels = ["medium", "high", "critical"]

        if not categories:
            categories = [
                AdversarialCategory.PROMPT_INJECTION,
                AdversarialCategory.HARMFUL_CONTENT,
                AdversarialCategory.DATA_EXTRACTION,
                AdversarialCategory.JAILBREAK,
                AdversarialCategory.INDIRECT_ATTACK,
                AdversarialCategory.EDGE_CASE,
            ]

        # Create comprehensive test suite
        suite = create_test_suite(
            categories=categories,
            min_severity=severity_levels[0] if severity_levels else "medium",
            include_conversations=include_conversations
        )

        # Convert to simulator format
        test_cases = []
        for test in suite["tests"]:
            test_case = {
                "id": test.test_id,
                "input": test.attack_vector,
                "expected": {
                    "behavior": test.expected_behavior,
                    "evaluation_type": "adversarial_safety",
                    "severity": test.severity,
                    "detection_difficulty": test.detection_difficulty,
                },
                "metadata": {
                    **test.metadata,
                    "category": test.category.value,
                    "subcategory": test.subcategory,
                    "real_world_frequency": test.real_world_frequency,
                }
            }
            test_cases.append(test_case)

        # Add conversation scenarios
        if include_conversations:
            for conv in suite.get("conversations", []):
                test_case = {
                    "id": conv["id"],
                    "input": conv["turns"],
                    "expected": {
                        "behavior": conv["expected_behavior"],
                        "evaluation_type": "adversarial_conversation",
                    },
                    "metadata": {
                        "scenario": conv["name"],
                        "description": conv["description"],
                        "turn_count": len(conv["turns"]),
                    }
                }
                test_cases.append(test_case)

        # Add attack chains
        if include_attack_chains:
            for chain in suite.get("attack_chains", []):
                test_case = {
                    "id": chain["chain_id"],
                    "input": chain["steps"],
                    "expected": {
                        "behavior": chain["expected_resilience"],
                        "evaluation_type": "attack_chain",
                    },
                    "metadata": {
                        "chain_name": chain["name"],
                        "step_count": len(chain["steps"]),
                    }
                }
                test_cases.append(test_case)

        # Create final suite
        final_suite = {
            "test_cases": test_cases,
            "statistics": suite.get("severity_distribution", {}),
            "total_tests": len(test_cases),
            "categories": suite.get("categories", []),
            "generated_at": datetime.now().isoformat(),
            "suite_id": str(uuid.uuid4()),
        }

        if export_path:
            Path(export_path).write_text(json.dumps(final_suite, indent=2))

        return final_suite


# Convenience function
async def simulate(
    agent: str | Callable | Any,
    scenarios: list[str] = ["factual_qa", "task_specific"],
    count: int = 20,
    export: str | None = None
) -> dict[str, Any]:
    """
    Quick simulation of agent with synthetic data.

    Args:
        agent: Agent to test
        scenarios: Scenarios to simulate
        count: Total number of tests
        export: Export path for results

    Returns:
        Summary of simulation results
    """
    simulator = Simulator(agent)

    # Distribute count across scenarios
    count_per_scenario = count // len(scenarios)

    return await simulator.simulate_and_evaluate(
        scenarios=scenarios,
        count_per_scenario=count_per_scenario,
        export_path=export,
        progress=True
    )
