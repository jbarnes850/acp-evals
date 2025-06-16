"""
Handoff quality metric for multi-agent systems.

Based on Cognition's research on context sharing and decision preservation.
"""

import re
from typing import Any

from acp_sdk import Event, Run

from acp_evals.core.base import Metric, MetricResult


class HandoffQualityMetric(Metric):
    """
    Measures information preservation and quality across agent handoffs.

    Key aspects measured:
    - Context preservation: Are key facts maintained?
    - Decision preservation: Are decisions respected?
    - Information loss: What gets dropped?
    - Noise accumulation: What gets added unnecessarily?
    """

    def __init__(
        self,
        track_decisions: bool = True,
        track_constraints: bool = True,
        track_entities: bool = True,
    ):
        """
        Initialize handoff quality metric.

        Args:
            track_decisions: Track decision preservation
            track_constraints: Track constraint preservation
            track_entities: Track entity/name preservation
        """
        self.track_decisions = track_decisions
        self.track_constraints = track_constraints
        self.track_entities = track_entities

    @property
    def name(self) -> str:
        return "handoff_quality"

    @property
    def description(self) -> str:
        return "Measures information preservation across agent handoffs"

    async def calculate(self, run: Run, events: list[Event]) -> MetricResult:
        """
        Calculate handoff quality metrics.

        Args:
            run: The evaluation run
            events: List of events from the run

        Returns:
            MetricResult with handoff quality analysis
        """
        # Extract handoff sequences from events
        handoffs = self._extract_handoffs(events)

        if not handoffs:
            return MetricResult(
                name=self.name,
                value=1.0,  # No handoffs = no loss
                unit="score",
                breakdown={"handoff_count": 0},
                metadata={"message": "No handoffs detected"},
            )

        # Analyze each handoff
        handoff_scores = []
        total_information_loss = 0
        total_noise_added = 0
        decision_conflicts = 0

        for i, handoff in enumerate(handoffs):
            analysis = self._analyze_handoff(
                handoff["source_content"],
                handoff["target_content"],
                handoff["original_context"],
            )

            handoff_scores.append(analysis["preservation_score"])
            total_information_loss += analysis["information_loss"]
            total_noise_added += analysis["noise_added"]
            decision_conflicts += analysis["decision_conflicts"]

        # Calculate overall metrics
        avg_preservation = sum(handoff_scores) / len(handoff_scores)
        degradation_rate = 1.0 - handoff_scores[-1] if handoff_scores else 0.0

        # Exponential degradation factor (how quickly info degrades)
        if len(handoff_scores) > 1:
            degradation_factor = self._calculate_degradation_factor(handoff_scores)
        else:
            degradation_factor = 0.0

        return MetricResult(
            name=self.name,
            value=avg_preservation,
            unit="score",
            breakdown={
                "handoff_count": len(handoffs),
                "average_preservation": avg_preservation,
                "final_preservation": handoff_scores[-1] if handoff_scores else 1.0,
                "total_degradation": degradation_rate,
                "degradation_factor": degradation_factor,
                "information_loss_bytes": total_information_loss,
                "noise_added_bytes": total_noise_added,
                "decision_conflicts": decision_conflicts,
                "preservation_by_handoff": handoff_scores,
            },
            metadata={
                "track_settings": {
                    "decisions": self.track_decisions,
                    "constraints": self.track_constraints,
                    "entities": self.track_entities,
                },
            },
        )

    def _extract_handoffs(self, events: list[Event]) -> list[dict[str, Any]]:
        """Extract handoff sequences from events."""
        handoffs = []
        current_agent = None
        previous_content = None
        original_context = None

        for event in events:
            if event.type == "message.created" and hasattr(event, "agent_id"):
                # Check if this is a handoff (agent change)
                if current_agent and event.agent_id != current_agent:
                    # Extract content from message
                    current_content = self._extract_message_content(event)

                    if previous_content and current_content:
                        handoffs.append({
                            "source_agent": current_agent,
                            "target_agent": event.agent_id,
                            "source_content": previous_content,
                            "target_content": current_content,
                            "original_context": original_context or previous_content,
                            "timestamp": event.timestamp,
                        })

                # Update tracking
                current_agent = event.agent_id
                previous_content = self._extract_message_content(event)

                # Set original context from first agent
                if original_context is None:
                    original_context = previous_content

        return handoffs

    def _extract_message_content(self, event: Event) -> str | None:
        """Extract content from a message event."""
        try:
            if hasattr(event, "message") and event.message:
                if hasattr(event.message, "parts"):
                    parts = []
                    for part in event.message.parts:
                        if hasattr(part, "content"):
                            parts.append(part.content)
                    return "\n".join(parts)
                elif hasattr(event.message, "content"):
                    return event.message.content
        except:
            pass
        return None

    def _analyze_handoff(
        self,
        source_content: str,
        target_content: str,
        original_context: str,
    ) -> dict[str, Any]:
        """Analyze a single handoff for information preservation."""
        analysis = {
            "preservation_score": 1.0,
            "information_loss": 0,
            "noise_added": 0,
            "decision_conflicts": 0,
            "preserved_elements": {},
            "lost_elements": {},
        }

        # Extract key elements from source
        source_elements = self._extract_key_elements(source_content)
        target_elements = self._extract_key_elements(target_content)
        self._extract_key_elements(original_context)

        # Track preservation of different element types
        preservation_scores = []

        # Check constraint preservation
        if self.track_constraints:
            constraint_score = self._check_element_preservation(
                source_elements["constraints"],
                target_elements["constraints"],
                "constraints",
                analysis,
            )
            preservation_scores.append(constraint_score)

        # Check decision preservation
        if self.track_decisions:
            decision_score = self._check_element_preservation(
                source_elements["decisions"],
                target_elements["decisions"],
                "decisions",
                analysis,
            )
            preservation_scores.append(decision_score)

            # Check for conflicting decisions
            conflicts = self._find_decision_conflicts(
                source_elements["decisions"],
                target_elements["decisions"],
            )
            analysis["decision_conflicts"] = len(conflicts)

        # Check entity preservation
        if self.track_entities:
            entity_score = self._check_element_preservation(
                source_elements["entities"],
                target_elements["entities"],
                "entities",
                analysis,
            )
            preservation_scores.append(entity_score)

        # Calculate information metrics
        source_length = len(source_content)
        target_length = len(target_content)

        # Information loss (content that disappeared)
        if target_length < source_length:
            analysis["information_loss"] = source_length - target_length

        # Noise added (unnecessary expansion)
        if target_length > source_length * 1.5:  # 50% expansion threshold
            analysis["noise_added"] = target_length - source_length

        # Overall preservation score
        if preservation_scores:
            analysis["preservation_score"] = sum(preservation_scores) / len(preservation_scores)

        return analysis

    def _extract_key_elements(self, content: str) -> dict[str, set[str]]:
        """Extract key elements from content."""
        elements = {
            "constraints": set(),
            "decisions": set(),
            "entities": set(),
        }

        if not content:
            return elements

        content_lower = content.lower()

        # Extract constraints (budget, deadline, requirements)
        constraint_patterns = [
            r"budget[:\s]+\$?[\d,]+",
            r"deadline[:\s]+[\w\s,]+",
            r"must\s+[\w\s]+",
            r"require[s]?\s+[\w\s]+",
            r"constraint[:\s]+[\w\s]+",
            r"limit[:\s]+[\w\s]+",
        ]

        for pattern in constraint_patterns:
            matches = re.findall(pattern, content_lower)
            elements["constraints"].update(matches)

        # Extract decisions (use X, implement Y, choose Z)
        decision_patterns = [
            r"use\s+[\w\s]+",
            r"implement\s+[\w\s]+",
            r"choose\s+[\w\s]+",
            r"select[ed]?\s+[\w\s]+",
            r"decid[ed]?\s+[\w\s]+",
            r"will\s+[\w\s]+",
        ]

        for pattern in decision_patterns:
            matches = re.findall(pattern, content_lower)
            elements["decisions"].update(matches)

        # Extract entities (proper nouns, specific names)
        # Simple approach: capitalized words that aren't sentence starts
        words = content.split()
        for i, word in enumerate(words):
            if (
                word[0].isupper() and
                i > 0 and
                not words[i-1].endswith(".") and
                len(word) > 2
            ):
                elements["entities"].add(word.strip(".,;:"))

        return elements

    def _check_element_preservation(
        self,
        source_elements: set[str],
        target_elements: set[str],
        element_type: str,
        analysis: dict[str, Any],
    ) -> float:
        """Check preservation of specific element type."""
        if not source_elements:
            return 1.0

        preserved = source_elements & target_elements
        lost = source_elements - target_elements

        preservation_rate = len(preserved) / len(source_elements)

        analysis["preserved_elements"][element_type] = list(preserved)
        analysis["lost_elements"][element_type] = list(lost)

        return preservation_rate

    def _find_decision_conflicts(
        self,
        source_decisions: set[str],
        target_decisions: set[str],
    ) -> list[tuple[str, str]]:
        """Find conflicting decisions between source and target."""
        conflicts = []

        # Look for contradictory patterns
        for source_dec in source_decisions:
            for target_dec in target_decisions:
                # Check if decisions contradict (simplified)
                if self._decisions_conflict(source_dec, target_dec):
                    conflicts.append((source_dec, target_dec))

        return conflicts

    def _decisions_conflict(self, decision1: str, decision2: str) -> bool:
        """Check if two decisions conflict (simplified)."""
        # Extract action and object
        words1 = decision1.split()
        words2 = decision2.split()

        if len(words1) < 2 or len(words2) < 2:
            return False

        action1, object1 = words1[0], " ".join(words1[1:])
        action2, object2 = words2[0], " ".join(words2[1:])

        # Check for contradictory actions on same object
        contradictory_actions = {
            "use": {"avoid", "skip", "remove"},
            "implement": {"skip", "defer", "cancel"},
            "enable": {"disable", "deactivate"},
        }

        for action, contradictions in contradictory_actions.items():
            if action1 == action and action2 in contradictions:
                # Check if they refer to similar objects
                if any(word in object2 for word in object1.split()):
                    return True

        return False

    def _calculate_degradation_factor(self, scores: list[float]) -> float:
        """Calculate exponential degradation factor."""
        if len(scores) < 2:
            return 0.0

        # Fit exponential decay: score = e^(-λ * handoff_number)
        # Simplified: calculate average decay rate
        decay_rates = []
        for i in range(1, len(scores)):
            if scores[i-1] > 0:
                decay_rate = -1 * (scores[i] - scores[i-1]) / scores[i-1]
                decay_rates.append(decay_rate)

        return sum(decay_rates) / len(decay_rates) if decay_rates else 0.0
