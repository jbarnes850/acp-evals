"""
Trace recycling system to convert telemetry data into evaluation datasets.

Implements continuous learning by transforming production traces into
evaluation data, enabling regression detection and performance monitoring.
"""

import hashlib
import json
import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

try:
    from acp_evals.telemetry.otel_exporter import OTelExporter
except ImportError:
    OTelExporter = None

logger = logging.getLogger(__name__)


@dataclass
class TracePattern:
    """Represents a recurring pattern in traces."""
    pattern_id: str
    pattern_type: str  # success, failure, performance_issue, error_pattern
    frequency: int
    first_seen: datetime
    last_seen: datetime
    example_traces: list[str]
    characteristics: dict[str, Any]


@dataclass
class EvaluationCandidate:
    """A trace that can be converted to an evaluation test case."""
    trace_id: str
    timestamp: datetime
    input_data: str
    expected_output: str | None
    actual_output: str
    tools_used: list[str]
    error_occurred: bool
    error_type: str | None
    performance_metrics: dict[str, float]
    metadata: dict[str, Any]
    quality_score: float = 0.0


class TraceRecycler:
    """Convert production traces into evaluation datasets."""

    def __init__(
        self,
        telemetry_exporter: OTelExporter | None = None,
        retention_days: int = 30,
        min_pattern_frequency: int = 3
    ):
        """
        Initialize trace recycler.

        Args:
            telemetry_exporter: OpenTelemetry exporter for reading traces
            retention_days: How long to keep traces
            min_pattern_frequency: Minimum occurrences to identify a pattern
        """
        self.telemetry_exporter = telemetry_exporter
        self.retention_days = retention_days
        self.min_pattern_frequency = min_pattern_frequency

        # Storage for traces and patterns
        self.trace_buffer: list[dict[str, Any]] = []
        self.patterns: dict[str, TracePattern] = {}
        self.evaluation_candidates: list[EvaluationCandidate] = []

        # Pattern detection
        self.pattern_signatures: dict[str, list[str]] = defaultdict(list)

    def ingest_trace(self, trace: dict[str, Any]) -> None:
        """
        Ingest a new trace from production.

        Args:
            trace: OpenTelemetry trace data
        """
        # Extract relevant information
        trace_id = trace.get("trace_id", "")
        spans = trace.get("spans", [])

        # Analyze trace for patterns
        pattern_sig = self._compute_pattern_signature(spans)
        self.pattern_signatures[pattern_sig].append(trace_id)

        # Check if this creates a new pattern
        if len(self.pattern_signatures[pattern_sig]) >= self.min_pattern_frequency:
            self._create_pattern(pattern_sig, self.pattern_signatures[pattern_sig])

        # Extract evaluation candidate
        candidate = self._extract_evaluation_candidate(trace)
        if candidate:
            self.evaluation_candidates.append(candidate)

        # Add to buffer
        self.trace_buffer.append(trace)

        # Clean old traces
        self._cleanup_old_traces()

    def _compute_pattern_signature(self, spans: list[dict[str, Any]]) -> str:
        """Compute a signature for pattern matching."""
        # Extract key characteristics
        operations = []
        for span in spans:
            op_type = span.get("attributes", {}).get("operation.type", "")
            status = span.get("status", {}).get("status_code", "")
            operations.append(f"{op_type}:{status}")

        # Create hash of operation sequence
        pattern_str = "|".join(operations)
        return hashlib.md5(pattern_str.encode()).hexdigest()[:8]

    def _create_pattern(self, signature: str, trace_ids: list[str]) -> None:
        """Create a new pattern from recurring traces."""
        if signature in self.patterns:
            # Update existing pattern
            pattern = self.patterns[signature]
            pattern.frequency = len(trace_ids)
            pattern.last_seen = datetime.now()
            pattern.example_traces = trace_ids[-5:]  # Keep last 5 examples
        else:
            # Create new pattern
            pattern = TracePattern(
                pattern_id=f"pattern_{signature}",
                pattern_type=self._classify_pattern(trace_ids),
                frequency=len(trace_ids),
                first_seen=datetime.now(),
                last_seen=datetime.now(),
                example_traces=trace_ids[-5:],
                characteristics=self._extract_pattern_characteristics(trace_ids)
            )
            self.patterns[signature] = pattern
            logger.info(f"New pattern detected: {pattern.pattern_id}")

    def _classify_pattern(self, trace_ids: list[str]) -> str:
        """Classify the type of pattern."""
        # Analyze traces to determine pattern type
        error_count = 0
        slow_count = 0

        for trace_id in trace_ids:
            trace = self._get_trace_by_id(trace_id)
            if not trace:
                continue

            # Check for errors
            if any(span.get("status", {}).get("status_code") == "ERROR"
                   for span in trace.get("spans", [])):
                error_count += 1

            # Check for slow operations
            duration = self._calculate_trace_duration(trace)
            if duration > 1000:  # > 1 second
                slow_count += 1

        if error_count > len(trace_ids) * 0.5:
            return "error_pattern"
        elif slow_count > len(trace_ids) * 0.5:
            return "performance_issue"
        else:
            return "success"

    def _extract_pattern_characteristics(self, trace_ids: list[str]) -> dict[str, Any]:
        """Extract common characteristics from pattern traces."""
        characteristics = {
            "common_operations": [],
            "avg_duration_ms": 0,
            "error_types": [],
            "tools_used": set()
        }

        durations = []
        operations = defaultdict(int)

        for trace_id in trace_ids:
            trace = self._get_trace_by_id(trace_id)
            if not trace:
                continue

            # Collect operations
            for span in trace.get("spans", []):
                op = span.get("attributes", {}).get("operation.type", "")
                operations[op] += 1

                # Collect tools
                tool = span.get("attributes", {}).get("tool.name")
                if tool:
                    characteristics["tools_used"].add(tool)

            # Collect duration
            duration = self._calculate_trace_duration(trace)
            durations.append(duration)

        # Summarize
        characteristics["common_operations"] = [
            op for op, count in operations.items()
            if count > len(trace_ids) * 0.5
        ]
        characteristics["avg_duration_ms"] = sum(durations) / len(durations) if durations else 0
        characteristics["tools_used"] = list(characteristics["tools_used"])

        return characteristics

    def _extract_evaluation_candidate(self, trace: dict[str, Any]) -> EvaluationCandidate | None:
        """Extract an evaluation candidate from a trace."""
        spans = trace.get("spans", [])
        if not spans:
            return None

        # Find input and output
        input_data = None
        output_data = None
        tools_used = []
        error_info = None

        for span in spans:
            attrs = span.get("attributes", {})

            # Extract input (usually in first span)
            if attrs.get("input.value") and not input_data:
                input_data = attrs["input.value"]

            # Extract output (usually in last span)
            if attrs.get("output.value"):
                output_data = attrs["output.value"]

            # Track tools
            if attrs.get("tool.name"):
                tools_used.append(attrs["tool.name"])

            # Check for errors
            if span.get("status", {}).get("status_code") == "ERROR":
                error_info = {
                    "occurred": True,
                    "type": attrs.get("error.type", "unknown"),
                    "message": attrs.get("error.message", "")
                }

        if not input_data:
            return None

        # Calculate performance metrics
        perf_metrics = {
            "duration_ms": self._calculate_trace_duration(trace),
            "span_count": len(spans),
            "tool_calls": len(tools_used)
        }

        # Create candidate
        return EvaluationCandidate(
            trace_id=trace.get("trace_id", ""),
            timestamp=datetime.fromisoformat(trace.get("timestamp", datetime.now().isoformat())),
            input_data=input_data,
            expected_output=None,  # Will be set during curation
            actual_output=output_data or "",
            tools_used=tools_used,
            error_occurred=bool(error_info),
            error_type=error_info["type"] if error_info else None,
            performance_metrics=perf_metrics,
            metadata={
                "source": "production_trace",
                "pattern_id": self._compute_pattern_signature(spans)
            }
        )

    def generate_evaluation_dataset(
        self,
        count: int = 100,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
        min_quality_score: float = 0.7
    ) -> list[dict[str, Any]]:
        """
        Generate evaluation dataset from recycled traces.

        Args:
            count: Number of test cases to generate
            include_patterns: Pattern types to include
            exclude_patterns: Pattern types to exclude
            min_quality_score: Minimum quality score for candidates

        Returns:
            List of evaluation test cases
        """
        # Score and filter candidates
        scored_candidates = []
        for candidate in self.evaluation_candidates:
            score = self._score_candidate(candidate)
            candidate.quality_score = score

            if score >= min_quality_score:
                pattern_type = self._get_pattern_type(candidate.metadata.get("pattern_id", ""))

                if include_patterns and pattern_type not in include_patterns:
                    continue
                if exclude_patterns and pattern_type in exclude_patterns:
                    continue

                scored_candidates.append(candidate)

        # Sort by quality and diversity
        scored_candidates.sort(key=lambda c: c.quality_score, reverse=True)

        # Select diverse set
        selected = self._select_diverse_candidates(scored_candidates, count)

        # Convert to evaluation format
        dataset = []
        for candidate in selected:
            test_case = {
                "id": f"recycled_{candidate.trace_id}",
                "input": candidate.input_data,
                "expected": candidate.expected_output or candidate.actual_output,
                "metadata": {
                    "source": "trace_recycling",
                    "timestamp": candidate.timestamp.isoformat(),
                    "tools_used": candidate.tools_used,
                    "performance_baseline": candidate.performance_metrics,
                    "quality_score": candidate.quality_score,
                    "pattern_type": self._get_pattern_type(candidate.metadata.get("pattern_id", ""))
                }
            }

            # Add error cases for regression testing
            if candidate.error_occurred:
                test_case["expected_behavior"] = "handle_error_gracefully"
                test_case["error_type"] = candidate.error_type

            dataset.append(test_case)

        return dataset

    def _score_candidate(self, candidate: EvaluationCandidate) -> float:
        """Score a candidate based on its value for evaluation."""
        score = 0.0

        # Factors that increase score
        if candidate.tools_used:
            score += 0.2  # Tool usage is valuable

        if candidate.error_occurred:
            score += 0.3  # Error cases are important

        if len(candidate.input_data) > 50:
            score += 0.1  # Non-trivial input

        # Performance outliers are interesting
        avg_duration = 500  # ms
        if abs(candidate.performance_metrics["duration_ms"] - avg_duration) > 1000:
            score += 0.2

        # Recent traces are more relevant
        age_days = (datetime.now() - candidate.timestamp).days
        if age_days < 7:
            score += 0.2

        return min(score, 1.0)

    def _select_diverse_candidates(
        self,
        candidates: list[EvaluationCandidate],
        count: int
    ) -> list[EvaluationCandidate]:
        """Select diverse set of candidates."""
        selected = []
        pattern_counts = defaultdict(int)
        tool_counts = defaultdict(int)

        for candidate in candidates:
            if len(selected) >= count:
                break

            # Check diversity criteria
            pattern_id = candidate.metadata.get("pattern_id", "")

            # Limit same pattern
            if pattern_counts[pattern_id] >= count // 10:
                continue

            # Ensure tool diversity
            for tool in candidate.tools_used:
                if tool_counts[tool] >= count // 5:
                    continue

            selected.append(candidate)
            pattern_counts[pattern_id] += 1
            for tool in candidate.tools_used:
                tool_counts[tool] += 1

        return selected

    def detect_regressions(
        self,
        baseline_traces: list[dict[str, Any]],
        current_traces: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Detect performance or behavior regressions.

        Args:
            baseline_traces: Historical traces (good behavior)
            current_traces: Recent traces to check

        Returns:
            List of detected regressions
        """
        regressions = []

        # Group by pattern
        baseline_patterns = self._group_by_pattern(baseline_traces)
        current_patterns = self._group_by_pattern(current_traces)

        for pattern_id, current_group in current_patterns.items():
            baseline_group = baseline_patterns.get(pattern_id, [])

            if not baseline_group:
                continue  # New pattern, not a regression

            # Compare performance
            baseline_perf = self._calculate_group_performance(baseline_group)
            current_perf = self._calculate_group_performance(current_group)

            # Check for performance regression
            if current_perf["avg_duration"] > baseline_perf["avg_duration"] * 1.5:
                regressions.append({
                    "type": "performance_regression",
                    "pattern_id": pattern_id,
                    "baseline_duration_ms": baseline_perf["avg_duration"],
                    "current_duration_ms": current_perf["avg_duration"],
                    "degradation_factor": current_perf["avg_duration"] / baseline_perf["avg_duration"],
                    "affected_traces": [t.get("trace_id") for t in current_group]
                })

            # Check for error rate regression
            if current_perf["error_rate"] > baseline_perf["error_rate"] + 0.1:
                regressions.append({
                    "type": "error_rate_regression",
                    "pattern_id": pattern_id,
                    "baseline_error_rate": baseline_perf["error_rate"],
                    "current_error_rate": current_perf["error_rate"],
                    "increase": current_perf["error_rate"] - baseline_perf["error_rate"],
                    "affected_traces": [t.get("trace_id") for t in current_group]
                })

        return regressions

    def _group_by_pattern(self, traces: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        """Group traces by pattern signature."""
        groups = defaultdict(list)
        for trace in traces:
            pattern_sig = self._compute_pattern_signature(trace.get("spans", []))
            groups[pattern_sig].append(trace)
        return groups

    def _calculate_group_performance(self, traces: list[dict[str, Any]]) -> dict[str, float]:
        """Calculate performance metrics for a group of traces."""
        durations = []
        error_count = 0

        for trace in traces:
            durations.append(self._calculate_trace_duration(trace))

            # Check for errors
            if any(span.get("status", {}).get("status_code") == "ERROR"
                   for span in trace.get("spans", [])):
                error_count += 1

        return {
            "avg_duration": sum(durations) / len(durations) if durations else 0,
            "error_rate": error_count / len(traces) if traces else 0
        }

    def _calculate_trace_duration(self, trace: dict[str, Any]) -> float:
        """Calculate total duration of a trace in milliseconds."""
        spans = trace.get("spans", [])
        if not spans:
            return 0

        # Find earliest start and latest end
        start_times = []
        end_times = []

        for span in spans:
            start = span.get("start_time")
            end = span.get("end_time")
            if start:
                start_times.append(datetime.fromisoformat(start))
            if end:
                end_times.append(datetime.fromisoformat(end))

        if not start_times or not end_times:
            return 0

        duration = (max(end_times) - min(start_times)).total_seconds() * 1000
        return duration

    def _get_trace_by_id(self, trace_id: str) -> dict[str, Any] | None:
        """Get trace by ID from buffer."""
        for trace in self.trace_buffer:
            if trace.get("trace_id") == trace_id:
                return trace
        return None

    def _get_pattern_type(self, pattern_id: str) -> str:
        """Get pattern type by ID."""
        for pattern in self.patterns.values():
            if pattern.pattern_id == f"pattern_{pattern_id}":
                return pattern.pattern_type
        return "unknown"

    def _cleanup_old_traces(self) -> None:
        """Remove traces older than retention period."""
        cutoff = datetime.now() - timedelta(days=self.retention_days)

        self.trace_buffer = [
            trace for trace in self.trace_buffer
            if datetime.fromisoformat(trace.get("timestamp", datetime.now().isoformat())) > cutoff
        ]

        self.evaluation_candidates = [
            candidate for candidate in self.evaluation_candidates
            if candidate.timestamp > cutoff
        ]

    def export_patterns(self, output_path: str) -> None:
        """Export discovered patterns for analysis."""
        patterns_data = []

        for pattern in self.patterns.values():
            patterns_data.append({
                "pattern_id": pattern.pattern_id,
                "type": pattern.pattern_type,
                "frequency": pattern.frequency,
                "first_seen": pattern.first_seen.isoformat(),
                "last_seen": pattern.last_seen.isoformat(),
                "characteristics": pattern.characteristics,
                "example_traces": pattern.example_traces[:3]  # Limit examples
            })

        with open(output_path, "w") as f:
            json.dump({
                "patterns": patterns_data,
                "total_patterns": len(patterns_data),
                "export_time": datetime.now().isoformat()
            }, f, indent=2)

        logger.info(f"Exported {len(patterns_data)} patterns to {output_path}")

    def ingest_traces_from_file(self, file_path: str) -> int:
        """
        Ingest traces from a JSON file.

        Args:
            file_path: Path to JSON file containing traces

        Returns:
            Number of traces ingested
        """
        try:
            with open(file_path) as f:
                data = json.load(f)

            # Support both single trace and array of traces
            traces = data if isinstance(data, list) else [data]

            count = 0
            for trace in traces:
                if isinstance(trace, dict) and ('trace_id' in trace or 'spans' in trace):
                    self.ingest_trace(trace)
                    count += 1

            logger.info(f"Ingested {count} traces from {file_path}")
            return count

        except Exception as e:
            logger.error(f"Error ingesting traces from file: {e}")
            return 0

    def generate_sample_traces(self, count: int = 10) -> list[dict[str, Any]]:
        """
        Generate sample traces for testing.

        Args:
            count: Number of sample traces to generate

        Returns:
            List of sample traces
        """
        import random
        import uuid

        traces = []

        # Define sample patterns
        patterns = [
            # Successful API call pattern
            {
                "type": "api_call",
                "operations": ["http.request", "auth.validate", "db.query", "http.response"],
                "error_rate": 0.1
            },
            # Tool usage pattern
            {
                "type": "tool_usage",
                "operations": ["agent.input", "tool.search", "tool.parse", "agent.output"],
                "error_rate": 0.2
            },
            # Multi-step reasoning pattern
            {
                "type": "reasoning",
                "operations": ["agent.input", "llm.generate", "memory.store", "llm.generate", "agent.output"],
                "error_rate": 0.15
            },
            # Error recovery pattern
            {
                "type": "error_recovery",
                "operations": ["agent.input", "tool.call", "error.catch", "retry.attempt", "agent.output"],
                "error_rate": 0.5
            }
        ]

        for i in range(count):
            pattern = random.choice(patterns)
            trace_id = str(uuid.uuid4())
            timestamp = datetime.now() - timedelta(hours=random.randint(0, 72))

            # Build spans
            spans = []
            start_time = timestamp

            for j, op in enumerate(pattern["operations"]):
                duration_ms = random.randint(10, 500) if "llm" in op else random.randint(1, 100)
                end_time = start_time + timedelta(milliseconds=duration_ms)

                # Determine if this span should error
                has_error = random.random() < pattern["error_rate"] and j == len(pattern["operations"]) - 2

                span = {
                    "span_id": f"{trace_id}-{j}",
                    "name": op,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "attributes": {
                        "operation.type": op,
                        "span.kind": "internal"
                    },
                    "status": {
                        "status_code": "ERROR" if has_error else "OK"
                    }
                }

                # Add operation-specific attributes
                if j == 0:  # First span has input
                    span["attributes"]["input.value"] = f"Sample input for {pattern['type']} task"

                if j == len(pattern["operations"]) - 1:  # Last span has output
                    if has_error:
                        span["attributes"]["error.type"] = "ProcessingError"
                        span["attributes"]["error.message"] = "Simulated error"
                    else:
                        span["attributes"]["output.value"] = f"Result of {pattern['type']} operation"

                if "tool" in op:
                    span["attributes"]["tool.name"] = random.choice(["search", "calculator", "code_executor"])

                spans.append(span)
                start_time = end_time

            trace = {
                "trace_id": trace_id,
                "timestamp": timestamp.isoformat(),
                "service": "acp-agent",
                "spans": spans,
                "metadata": {
                    "pattern_type": pattern["type"],
                    "agent_version": "1.0.0",
                    "environment": "production"
                }
            }

            traces.append(trace)

        return traces
