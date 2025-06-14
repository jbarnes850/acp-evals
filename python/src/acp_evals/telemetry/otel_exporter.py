"""
OpenTelemetry exporter for ACP evaluation metrics.

Integrates with ACP's built-in OpenTelemetry support to export
evaluation metrics as spans and metrics.
"""

import os
from typing import Any

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from acp_evals.core.base import BenchmarkResult, MetricResult


class OTelExporter:
    """
    Export evaluation metrics to OpenTelemetry backend.

    Supports both Jaeger and Phoenix (AI-focused) backends that ACP uses.
    """

    def __init__(
        self,
        service_name: str = "acp-evals",
        endpoint: str | None = None,
        resource_attributes: dict[str, Any] | None = None,
    ):
        """
        Initialize OpenTelemetry exporter.

        Args:
            service_name: Name of the service in traces
            endpoint: OTLP endpoint (defaults to OTEL_EXPORTER_OTLP_ENDPOINT env var)
            resource_attributes: Additional resource attributes
        """
        self.service_name = service_name
        self.endpoint = endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")

        # Create resource
        attributes = {
            "service.name": service_name,
            "service.version": "0.1.0",
            "framework": "acp-evals",
        }
        if resource_attributes:
            attributes.update(resource_attributes)

        self.resource = Resource.create(attributes=attributes)

        # Initialize tracer
        self._setup_tracer()

        # Initialize metrics
        self._setup_metrics()

    def _setup_tracer(self):
        """Set up OpenTelemetry tracer."""
        # Create tracer provider
        provider = TracerProvider(resource=self.resource)

        # Add OTLP exporter
        otlp_exporter = OTLPSpanExporter(
            endpoint=f"{self.endpoint}/v1/traces",
        )
        processor = BatchSpanProcessor(otlp_exporter)
        provider.add_span_processor(processor)

        # Set global tracer provider
        trace.set_tracer_provider(provider)

        # Get tracer
        self.tracer = trace.get_tracer(self.service_name)

    def _setup_metrics(self):
        """Set up OpenTelemetry metrics."""
        # Create metrics exporter
        otlp_exporter = OTLPMetricExporter(
            endpoint=f"{self.endpoint}/v1/metrics",
        )

        # Create meter provider with periodic exporter
        reader = PeriodicExportingMetricReader(
            exporter=otlp_exporter,
            export_interval_millis=10000,  # Export every 10 seconds
        )

        provider = MeterProvider(
            resource=self.resource,
            metric_readers=[reader],
        )

        # Set global meter provider
        metrics.set_meter_provider(provider)

        # Get meter
        self.meter = metrics.get_meter(self.service_name)

        # Create metric instruments
        self._create_instruments()

    def _create_instruments(self):
        """Create OpenTelemetry metric instruments."""
        # Token usage metrics
        self.token_counter = self.meter.create_counter(
            "acp.agent.tokens.total",
            unit="tokens",
            description="Total tokens used by agent",
        )

        self.token_cost_counter = self.meter.create_counter(
            "acp.agent.cost.total",
            unit="USD",
            description="Total cost of agent operations",
        )

        # Latency metrics
        self.latency_histogram = self.meter.create_histogram(
            "acp.agent.latency",
            unit="s",
            description="Agent response latency",
        )

        # Quality metrics
        self.quality_gauge = self.meter.create_gauge(
            "acp.agent.quality.score",
            description="Agent output quality score (0-1)",
        )

        # Benchmark metrics
        self.benchmark_score_gauge = self.meter.create_gauge(
            "acp.benchmark.score",
            description="Benchmark overall score",
        )

        # Context efficiency metrics
        self.context_efficiency_gauge = self.meter.create_gauge(
            "acp.agent.context.efficiency",
            description="Context window utilization efficiency",
        )

    def export_metric_result(
        self,
        metric: MetricResult,
        agent_name: str,
        run_id: str | None = None,
        additional_attributes: dict[str, Any] | None = None,
    ):
        """
        Export a metric result to OpenTelemetry.

        Args:
            metric: Metric result to export
            agent_name: Name of the agent
            run_id: Optional run ID
            additional_attributes: Additional span/metric attributes
        """
        # Base attributes
        attributes = {
            "agent.name": agent_name,
            "metric.name": metric.name,
        }
        if run_id:
            attributes["run.id"] = run_id
        if additional_attributes:
            attributes.update(additional_attributes)

        # Create span for the metric calculation
        with self.tracer.start_as_current_span(
            f"metric.{metric.name}",
            attributes=attributes,
        ) as span:
            # Add metric value
            span.set_attribute("metric.value", metric.value)
            span.set_attribute("metric.unit", metric.unit)

            # Add breakdown attributes
            if metric.breakdown:
                for key, value in metric.breakdown.items():
                    if isinstance(value, int | float | str | bool):
                        span.set_attribute(f"metric.breakdown.{key}", value)

            # Export specific metrics based on type
            if metric.name == "token_usage":
                self._export_token_metrics(metric, attributes)
            elif metric.name == "latency":
                self._export_latency_metrics(metric, attributes)
            elif metric.name == "quality":
                self._export_quality_metrics(metric, attributes)
            elif metric.name == "context_efficiency":
                self._export_context_metrics(metric, attributes)

    def _export_token_metrics(self, metric: MetricResult, attributes: dict[str, Any]):
        """Export token usage metrics."""
        breakdown = metric.breakdown or {}

        # Total tokens
        self.token_counter.add(
            metric.value,
            attributes=attributes,
        )

        # Token breakdown
        if "input_tokens" in breakdown:
            self.token_counter.add(
                breakdown["input_tokens"],
                attributes={**attributes, "token.type": "input"},
            )

        if "output_tokens" in breakdown:
            self.token_counter.add(
                breakdown["output_tokens"],
                attributes={**attributes, "token.type": "output"},
            )

        if "tool_tokens" in breakdown:
            self.token_counter.add(
                breakdown["tool_tokens"],
                attributes={**attributes, "token.type": "tool"},
            )

        # Cost
        if "cost_usd" in breakdown:
            self.token_cost_counter.add(
                breakdown["cost_usd"],
                attributes=attributes,
            )

    def _export_latency_metrics(self, metric: MetricResult, attributes: dict[str, Any]):
        """Export latency metrics."""
        self.latency_histogram.record(
            metric.value,
            attributes=attributes,
        )

    def _export_quality_metrics(self, metric: MetricResult, attributes: dict[str, Any]):
        """Export quality metrics."""
        self.quality_gauge.set(
            metric.value,
            attributes=attributes,
        )

    def _export_context_metrics(self, metric: MetricResult, attributes: dict[str, Any]):
        """Export context efficiency metrics."""
        self.context_efficiency_gauge.set(
            metric.value,
            attributes=attributes,
        )

        # Export context window percentage if available
        breakdown = metric.breakdown or {}
        if "context_percentage" in breakdown:
            self.meter.create_gauge(
                "acp.agent.context.percentage",
                description="Percentage of context window used",
            ).set(
                breakdown["context_percentage"],
                attributes=attributes,
            )

    def export_benchmark_result(
        self,
        result: BenchmarkResult,
        additional_attributes: dict[str, Any] | None = None,
    ):
        """
        Export benchmark results to OpenTelemetry.

        Args:
            result: Benchmark result to export
            additional_attributes: Additional span attributes
        """
        # Base attributes
        attributes = {
            "benchmark.name": result.benchmark_name,
            "agent.name": result.agent_name,
            "benchmark.tasks.total": result.tasks_total,
            "benchmark.tasks.completed": result.tasks_completed,
        }
        if additional_attributes:
            attributes.update(additional_attributes)

        # Create span for benchmark execution
        with self.tracer.start_as_current_span(
            f"benchmark.{result.benchmark_name}",
            attributes=attributes,
        ) as span:
            # Export overall score
            self.benchmark_score_gauge.set(
                result.overall_score,
                attributes=attributes,
            )

            # Add summary attributes
            if result.summary:
                for key, value in result.summary.items():
                    if isinstance(value, int | float | str | bool):
                        span.set_attribute(f"benchmark.summary.{key}", value)

            # Export individual metrics
            for metric_name, metric_result in result.metrics.items():
                self.export_metric_result(
                    metric_result,
                    agent_name=result.agent_name,
                    additional_attributes={
                        "benchmark.name": result.benchmark_name,
                    }
                )

    def create_evaluation_span(
        self,
        name: str,
        attributes: dict[str, Any] | None = None,
    ):
        """
        Create a span for an evaluation operation.

        Args:
            name: Span name
            attributes: Span attributes

        Returns:
            Span context manager
        """
        return self.tracer.start_as_current_span(name, attributes=attributes)


def setup_telemetry(
    service_name: str = "acp-evals",
    endpoint: str | None = None,
    resource_attributes: dict[str, Any] | None = None,
) -> OTelExporter:
    """
    Set up OpenTelemetry for ACP Evals.

    Args:
        service_name: Name of the service
        endpoint: OTLP endpoint
        resource_attributes: Additional resource attributes

    Returns:
        Configured OTelExporter instance
    """
    return OTelExporter(
        service_name=service_name,
        endpoint=endpoint,
        resource_attributes=resource_attributes,
    )
