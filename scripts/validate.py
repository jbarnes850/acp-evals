#!/usr/bin/env python3
"""
Validation script for ACP Evals implementation.

This script verifies that the implementation matches the proposal
and includes all required features.
"""

import sys
import importlib
import inspect
from typing import Dict, List, Tuple
from pathlib import Path


class ImplementationValidator:
    """Validates the ACP Evals implementation against requirements."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.successes: List[str] = []
    
    def validate_all(self):
        """Run all validation checks."""
        print("🔍 Validating ACP Evals Implementation...\n")
        
        # Check module structure
        self.validate_module_structure()
        
        # Check base classes
        self.validate_base_classes()
        
        # Check metrics implementation
        self.validate_metrics()
        
        # Check benchmarks
        self.validate_benchmarks()
        
        # Check evaluators
        self.validate_evaluators()
        
        # Check patterns
        self.validate_patterns()
        
        # Check integration components
        self.validate_integration()
        
        # Report results
        self.report_results()
    
    def validate_module_structure(self):
        """Validate the module structure matches the proposal."""
        print("📁 Checking module structure...")
        
        required_modules = [
            "acp_evals",
            "acp_evals.base",
            "acp_evals.metrics",
            "acp_evals.metrics.token_usage",
            "acp_evals.metrics.context",
            "acp_evals.metrics.cost",
            "acp_evals.metrics.handoff_quality",
            "acp_evals.benchmarks",
            "acp_evals.benchmarks.context_scaling",
            "acp_evals.benchmarks.multi_agent",
            "acp_evals.evaluators",
            "acp_evals.evaluators.llm_judge",
            "acp_evals.patterns",
            "acp_evals.patterns.linear",
            "acp_evals.patterns.supervisor",
            "acp_evals.patterns.swarm",
            "acp_evals.client",
            "acp_evals.telemetry",
        ]
        
        for module_name in required_modules:
            try:
                importlib.import_module(module_name)
                self.successes.append(f"✓ Module {module_name} found")
            except ImportError as e:
                self.errors.append(f"✗ Missing module: {module_name} - {e}")
    
    def validate_base_classes(self):
        """Validate base classes are properly implemented."""
        print("\n🏗️  Checking base classes...")
        
        try:
            from acp_evals.core.base import (
                Metric, MetricResult,
                Benchmark, BenchmarkResult, BenchmarkTask,
                Evaluator, EvaluatorResult
            )
            
            # Check Metric abstract class
            if not inspect.isabstract(Metric):
                self.warnings.append("⚠️  Metric should be abstract")
            
            # Check required methods
            metric_methods = ["calculate", "name", "description"]
            for method in metric_methods:
                if not hasattr(Metric, method):
                    self.errors.append(f"✗ Metric missing method: {method}")
                else:
                    self.successes.append(f"✓ Metric.{method} found")
            
            # Check MetricResult dataclass
            metric_result_fields = ["name", "value", "unit", "breakdown", "metadata"]
            for field in metric_result_fields:
                if not hasattr(MetricResult, field):
                    self.errors.append(f"✗ MetricResult missing field: {field}")
                else:
                    self.successes.append(f"✓ MetricResult.{field} found")
            
        except ImportError as e:
            self.errors.append(f"✗ Failed to import base classes: {e}")
    
    def validate_metrics(self):
        """Validate metric implementations."""
        print("\n📊 Checking metrics...")
        
        metrics_to_check = [
            ("token_usage", "TokenUsageMetric", ["track_context_usage"]),
            ("context", "ContextMetric", ["window_size"]),
            ("cost", "CostMetric", ["pricing_model"]),
            ("handoff_quality", "HandoffQualityMetric", ["track_decisions", "track_constraints"]),
        ]
        
        for module_name, class_name, expected_attrs in metrics_to_check:
            try:
                module = importlib.import_module(f"acp_evals.metrics.{module_name}")
                cls = getattr(module, class_name)
                
                # Check it inherits from Metric
                from acp_evals.core.base import Metric
                if not issubclass(cls, Metric):
                    self.errors.append(f"✗ {class_name} doesn't inherit from Metric")
                else:
                    self.successes.append(f"✓ {class_name} properly inherits from Metric")
                
                # Check expected attributes
                instance = cls()
                for attr in expected_attrs:
                    if not hasattr(instance, attr):
                        self.warnings.append(f"⚠️  {class_name} missing attribute: {attr}")
                
            except Exception as e:
                self.errors.append(f"✗ Error checking {class_name}: {e}")
    
    def validate_benchmarks(self):
        """Validate benchmark implementations."""
        print("\n🎯 Checking benchmarks...")
        
        # Check ContextScalingBenchmark
        try:
            from acp_evals.benchmarks.context_scaling import ContextScalingBenchmark
            
            benchmark = ContextScalingBenchmark()
            
            # Check required attributes
            required_attrs = ["distractor_domains", "context_levels", "tasks"]
            for attr in required_attrs:
                if not hasattr(benchmark, attr):
                    self.errors.append(f"✗ ContextScalingBenchmark missing: {attr}")
                else:
                    self.successes.append(f"✓ ContextScalingBenchmark.{attr} found")
            
            # Check tau-bench compatibility
            if hasattr(benchmark, "_generate_distractors"):
                self.successes.append("✓ Distractor generation implemented")
            else:
                self.warnings.append("⚠️  Missing distractor generation")
            
        except Exception as e:
            self.errors.append(f"✗ Error checking ContextScalingBenchmark: {e}")
        
        # Check multi-agent benchmarks
        try:
            from acp_evals.benchmarks.multi_agent import (
                PatternComparisonBenchmark,
                HandoffQualityBenchmark
            )
            
            self.successes.append("✓ Multi-agent benchmarks found")
            
        except Exception as e:
            self.errors.append(f"✗ Error checking multi-agent benchmarks: {e}")
    
    def validate_evaluators(self):
        """Validate evaluator implementations."""
        print("\n⚖️  Checking evaluators...")
        
        try:
            from acp_evals.evaluators.llm_judge import LLMJudge
            
            judge = LLMJudge()
            
            # Check default rubric
            if hasattr(judge, "DEFAULT_RUBRIC"):
                rubric = judge.DEFAULT_RUBRIC
                expected_criteria = ["factual_accuracy", "completeness", "clarity", "relevance", "efficiency"]
                
                for criterion in expected_criteria:
                    if criterion not in rubric:
                        self.warnings.append(f"⚠️  Missing rubric criterion: {criterion}")
                    else:
                        self.successes.append(f"✓ Rubric includes {criterion}")
                
                # Check weights sum to 1.0
                total_weight = sum(c["weight"] for c in rubric.values())
                if abs(total_weight - 1.0) > 0.01:
                    self.errors.append(f"✗ Rubric weights sum to {total_weight}, not 1.0")
                else:
                    self.successes.append("✓ Rubric weights properly normalized")
            
        except Exception as e:
            self.errors.append(f"✗ Error checking LLMJudge: {e}")
    
    def validate_patterns(self):
        """Validate multi-agent patterns."""
        print("\n🔀 Checking multi-agent patterns...")
        
        patterns_to_check = ["LinearPattern", "SupervisorPattern", "SwarmPattern"]
        
        for pattern_name in patterns_to_check:
            try:
                if pattern_name == "LinearPattern":
                    from acp_evals.patterns.linear import LinearPattern as Pattern
                elif pattern_name == "SupervisorPattern":
                    from acp_evals.patterns.supervisor import SupervisorPattern as Pattern
                else:
                    from acp_evals.patterns.swarm import SwarmPattern as Pattern
                
                # Check execute method
                if hasattr(Pattern, "execute"):
                    self.successes.append(f"✓ {pattern_name}.execute found")
                else:
                    self.errors.append(f"✗ {pattern_name} missing execute method")
                
            except Exception as e:
                self.errors.append(f"✗ Error checking {pattern_name}: {e}")
    
    def validate_integration(self):
        """Validate integration components."""
        print("\n🔌 Checking integration components...")
        
        # Check OpenTelemetry integration
        try:
            from acp_evals.telemetry.otel_exporter import OTelExporter
            
            exporter = OTelExporter()
            required_methods = ["export_run", "export_benchmark", "shutdown"]
            
            for method in required_methods:
                if hasattr(exporter, method):
                    self.successes.append(f"✓ OTelExporter.{method} found")
                else:
                    self.errors.append(f"✗ OTelExporter missing: {method}")
            
        except Exception as e:
            self.errors.append(f"✗ Error checking OTelExporter: {e}")
        
        # Check ACP client
        try:
            from acp_evals.client.acp_client import ACPEvalClient
            
            # Check for evaluation methods
            if hasattr(ACPEvalClient, "evaluate_agent"):
                self.successes.append("✓ ACPEvalClient.evaluate_agent found")
            else:
                self.errors.append("✗ ACPEvalClient missing evaluate_agent")
            
        except Exception as e:
            self.errors.append(f"✗ Error checking ACPEvalClient: {e}")
    
    def check_research_alignment(self):
        """Check alignment with research insights."""
        print("\n📚 Checking research alignment...")
        
        # Token-first metrics (Anthropic)
        try:
            from acp_evals.metrics.token_usage import TokenUsageMetric
            metric = TokenUsageMetric()
            
            # Should track efficiency
            if hasattr(metric, "calculate"):
                self.successes.append("✓ Token-first metrics implemented")
            
        except:
            self.errors.append("✗ Missing token-first metrics")
        
        # Context preservation (Cognition)
        try:
            from acp_evals.metrics.handoff_quality import HandoffQualityMetric
            self.successes.append("✓ Context preservation metrics implemented")
        except:
            self.errors.append("✗ Missing context preservation metrics")
        
        # Architecture patterns (LangChain)
        try:
            from acp_evals.patterns import LinearPattern, SupervisorPattern, SwarmPattern
            self.successes.append("✓ Multiple architecture patterns implemented")
        except:
            self.errors.append("✗ Missing architecture patterns")
    
    def report_results(self):
        """Report validation results."""
        print("\n" + "="*60)
        print("📋 VALIDATION SUMMARY")
        print("="*60)
        
        print(f"\n✅ Successes: {len(self.successes)}")
        if self.successes and len(self.successes) <= 20:
            for success in self.successes[:5]:
                print(f"   {success}")
            if len(self.successes) > 5:
                print(f"   ... and {len(self.successes) - 5} more")
        
        print(f"\n⚠️  Warnings: {len(self.warnings)}")
        for warning in self.warnings:
            print(f"   {warning}")
        
        print(f"\n❌ Errors: {len(self.errors)}")
        for error in self.errors:
            print(f"   {error}")
        
        print("\n" + "="*60)
        
        if not self.errors:
            print("✅ Implementation validated successfully!")
            return 0
        else:
            print("❌ Validation failed with errors.")
            return 1


def main():
    """Run validation."""
    # Add src to path
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    
    validator = ImplementationValidator()
    validator.validate_all()
    validator.check_research_alignment()
    
    return validator.report_results()


if __name__ == "__main__":
    sys.exit(main())