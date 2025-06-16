"""
Classification metrics for binary evaluators.

Implements precision, recall, F1, and Cohen's kappa for evaluating
LLM-as-judge performance.
"""

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass
class ClassificationMetrics:
    """
    Classification metrics for binary evaluation results.

    Attributes:
        precision: True positives / (True positives + False positives)
        recall: True positives / (True positives + False negatives)
        f1_score: Harmonic mean of precision and recall
        cohen_kappa: Agreement corrected for chance
        accuracy: Overall accuracy
        confusion_matrix: 2x2 confusion matrix
    """

    precision: float
    recall: float
    f1_score: float
    cohen_kappa: float
    accuracy: float
    confusion_matrix: dict[str, dict[str, int]]

    def __str__(self) -> str:
        """Format metrics as readable string."""
        return (
            f"Precision: {self.precision:.3f}\n"
            f"Recall: {self.recall:.3f}\n"
            f"F1 Score: {self.f1_score:.3f}\n"
            f"Cohen's κ: {self.cohen_kappa:.3f}\n"
            f"Accuracy: {self.accuracy:.3f}"
        )


class BinaryClassificationCalculator:
    """
    Calculator for binary classification metrics.

    Designed for evaluating LLM-evaluator performance against
    ground truth labels. Supports both string and boolean labels.
    """

    def __init__(
        self, positive_labels: set[str] | None = None, negative_labels: set[str] | None = None
    ):
        """
        Initialize calculator.

        Args:
            positive_labels: Labels considered positive (default: {"pass", "true", "1"})
            negative_labels: Labels considered negative (default: {"fail", "false", "0"})
        """
        self.positive_labels = positive_labels or {
            "pass",
            "true",
            "yes",
            "1",
            "accurate",
            "safe",
            "relevant",
        }
        self.negative_labels = negative_labels or {
            "fail",
            "false",
            "no",
            "0",
            "inaccurate",
            "unsafe",
            "irrelevant",
        }

    def _normalize_label(self, label: str | bool | int) -> bool:
        """Convert various label formats to boolean."""
        if isinstance(label, bool):
            return label
        if isinstance(label, int):
            return bool(label)

        label_str = str(label).lower().strip()
        if label_str in self.positive_labels:
            return True
        elif label_str in self.negative_labels:
            return False
        else:
            raise ValueError(
                f"Unknown label: {label}. Expected one of {self.positive_labels} or {self.negative_labels}"
            )

    def calculate_metrics(
        self, predictions: Sequence[str | bool], ground_truth: Sequence[str | bool]
    ) -> ClassificationMetrics:
        """
        Calculate classification metrics.

        Args:
            predictions: Predicted labels from evaluator
            ground_truth: True labels

        Returns:
            ClassificationMetrics object

        Raises:
            ValueError: If lengths don't match or labels are invalid
        """
        if len(predictions) != len(ground_truth):
            raise ValueError(
                f"Length mismatch: {len(predictions)} predictions vs {len(ground_truth)} ground truth"
            )

        # Normalize labels
        pred_binary = [self._normalize_label(p) for p in predictions]
        true_binary = [self._normalize_label(t) for t in ground_truth]

        # Calculate confusion matrix
        tp = sum(p and t for p, t in zip(pred_binary, true_binary))
        tn = sum(not p and not t for p, t in zip(pred_binary, true_binary))
        fp = sum(p and not t for p, t in zip(pred_binary, true_binary))
        fn = sum(not p and t for p, t in zip(pred_binary, true_binary))

        # Calculate metrics
        total = len(predictions)
        accuracy = (tp + tn) / total if total > 0 else 0.0

        # Precision: of all positive predictions, how many were correct?
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0

        # Recall: of all actual positives, how many did we find?
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

        # F1: harmonic mean of precision and recall
        f1_score = (
            2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        )

        # Cohen's kappa: agreement corrected for chance
        cohen_kappa = self._calculate_cohen_kappa(tp, tn, fp, fn, total)

        confusion_matrix = {
            "actual_positive": {"predicted_positive": tp, "predicted_negative": fn},
            "actual_negative": {"predicted_positive": fp, "predicted_negative": tn},
        }

        return ClassificationMetrics(
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            cohen_kappa=cohen_kappa,
            accuracy=accuracy,
            confusion_matrix=confusion_matrix,
        )

    def _calculate_cohen_kappa(self, tp: int, tn: int, fp: int, fn: int, total: int) -> float:
        """
        Calculate Cohen's kappa coefficient.

        Cohen's kappa measures agreement while accounting for chance agreement.
        It's more conservative than raw accuracy and recommended in the research.

        κ = (p_o - p_e) / (1 - p_e)
        where p_o is observed agreement and p_e is expected agreement by chance
        """
        if total == 0:
            return 0.0

        # Observed agreement
        p_o = (tp + tn) / total

        # Expected agreement by chance
        # Marginal probabilities
        actual_positive = (tp + fn) / total
        actual_negative = (fp + tn) / total
        predicted_positive = (tp + fp) / total
        predicted_negative = (tn + fn) / total

        # Expected agreement
        p_e = (actual_positive * predicted_positive) + (actual_negative * predicted_negative)

        # Cohen's kappa
        if p_e == 1.0:
            return 1.0 if p_o == 1.0 else 0.0

        kappa = (p_o - p_e) / (1 - p_e)
        return kappa


class MultiClassMetricsCalculator:
    """
    Calculator for multi-class classification metrics.

    Useful when evaluating multiple binary evaluators or
    multi-class safety categories.
    """

    def calculate_metrics(
        self, predictions: Sequence[str], ground_truth: Sequence[str], average: str = "macro"
    ) -> dict[str, float]:
        """
        Calculate multi-class metrics.

        Args:
            predictions: Predicted labels
            ground_truth: True labels
            average: Averaging method ("macro", "micro", "weighted")

        Returns:
            Dictionary of metrics
        """
        if len(predictions) != len(ground_truth):
            raise ValueError("Length mismatch between predictions and ground truth")

        # Get unique classes
        classes = sorted(set(predictions) | set(ground_truth))

        # Calculate per-class metrics
        class_metrics = {}
        for cls in classes:
            # Binary classification for this class (one-vs-rest)
            binary_pred = [p == cls for p in predictions]
            binary_true = [t == cls for t in ground_truth]

            tp = sum(p and t for p, t in zip(binary_pred, binary_true))
            fp = sum(p and not t for p, t in zip(binary_pred, binary_true))
            fn = sum(not p and t for p, t in zip(binary_pred, binary_true))

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (
                2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            )

            class_metrics[cls] = {
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
                "support": sum(t == cls for t in ground_truth),
            }

        # Average metrics
        if average == "macro":
            # Simple average across classes
            avg_precision = sum(m["precision"] for m in class_metrics.values()) / len(classes)
            avg_recall = sum(m["recall"] for m in class_metrics.values()) / len(classes)
            avg_f1 = sum(m["f1_score"] for m in class_metrics.values()) / len(classes)
        elif average == "weighted":
            # Weighted by class frequency
            total_support = sum(m["support"] for m in class_metrics.values())
            avg_precision = (
                sum(m["precision"] * m["support"] for m in class_metrics.values()) / total_support
            )
            avg_recall = (
                sum(m["recall"] * m["support"] for m in class_metrics.values()) / total_support
            )
            avg_f1 = (
                sum(m["f1_score"] * m["support"] for m in class_metrics.values()) / total_support
            )
        else:  # micro
            # Calculate globally
            all_tp = sum(
                sum(p == cls and t == cls for p, t in zip(predictions, ground_truth))
                for cls in classes
            )
            all_fp = sum(
                sum(p == cls and t != cls for p, t in zip(predictions, ground_truth))
                for cls in classes
            )
            all_fn = sum(
                sum(p != cls and t == cls for p, t in zip(predictions, ground_truth))
                for cls in classes
            )

            avg_precision = all_tp / (all_tp + all_fp) if (all_tp + all_fp) > 0 else 0.0
            avg_recall = all_tp / (all_tp + all_fn) if (all_tp + all_fn) > 0 else 0.0
            avg_f1 = (
                2 * (avg_precision * avg_recall) / (avg_precision + avg_recall)
                if (avg_precision + avg_recall) > 0
                else 0.0
            )

        # Overall accuracy
        accuracy = sum(p == t for p, t in zip(predictions, ground_truth)) / len(predictions)

        return {
            "accuracy": accuracy,
            "precision": avg_precision,
            "recall": avg_recall,
            "f1_score": avg_f1,
            "per_class": class_metrics,
        }


def evaluate_evaluator_performance(
    evaluator_results: list[tuple[bool, bool]], metric_focus: str = "recall"
) -> tuple[ClassificationMetrics, str]:
    """
    Evaluate an LLM-evaluator's performance and provide recommendations.

    Args:
        evaluator_results: List of (predicted, actual) boolean pairs
        metric_focus: Which metric to optimize for ("recall", "precision", "balanced")

    Returns:
        Tuple of (metrics, recommendation_text)
    """
    predictions, ground_truth = zip(*evaluator_results)

    calculator = BinaryClassificationCalculator()
    metrics = calculator.calculate_metrics(predictions, ground_truth)

    # Generate recommendations based on metrics and research
    recommendations = []

    # Based on research findings about Cohen's kappa
    if metrics.cohen_kappa < 0.4:
        recommendations.append(
            "Low Cohen's κ (<0.4) indicates poor agreement with ground truth. "
            "Consider switching to a stronger model (GPT-4, Claude-3) or refining criteria."
        )
    elif metrics.cohen_kappa < 0.6:
        recommendations.append(
            "Moderate Cohen's κ (0.4-0.6) suggests room for improvement. "
            "Try adding Chain-of-Thought prompting or more specific criteria."
        )

    # Task-specific recommendations
    if metric_focus == "recall" and metrics.recall < 0.7:
        recommendations.append(
            "Low recall for defect detection. Consider:\n"
            "- Lowering decision thresholds\n"
            "- Adding specific examples of defects to criteria\n"
            "- Using multiple evaluators (Panel of LLMs approach)"
        )
    elif metric_focus == "precision" and metrics.precision < 0.8:
        recommendations.append(
            "Low precision may cause alert fatigue. Consider:\n"
            "- Raising decision thresholds\n"
            "- Adding 'don't overthink' instructions (research-backed)\n"
            "- Clarifying what constitutes acceptable vs unacceptable"
        )

    # General performance
    if metrics.f1_score < 0.5:
        recommendations.append(
            "Overall performance is below production standards. "
            "Consider using a finetuned classifier for this specific task."
        )

    recommendation_text = (
        "\n\n".join(recommendations)
        if recommendations
        else "Performance is within acceptable ranges."
    )

    return metrics, recommendation_text
