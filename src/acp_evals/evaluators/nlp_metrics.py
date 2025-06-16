"""
NLP metrics evaluators for text quality assessment.

Provides standard NLP metrics like BLEU, ROUGE, METEOR for evaluation.
"""

import math
from collections import Counter

from .base import EvaluationResult, Evaluator


class BleuScoreEvaluator(Evaluator):
    """BLEU score evaluator for machine translation quality."""

    def __init__(self, n_gram: int = 4):
        """
        Initialize BLEU evaluator.

        Args:
            n_gram: Maximum n-gram size (default: 4 for BLEU-4)
        """
        self.n_gram = n_gram

    def evaluate(
        self,
        response: str,
        ground_truth: str | list[str],
        **kwargs
    ) -> EvaluationResult:
        """Calculate BLEU score."""
        # Handle multiple references
        if isinstance(ground_truth, str):
            references = [ground_truth.split()]
        else:
            references = [ref.split() for ref in ground_truth]

        hypothesis = response.split()

        # Calculate n-gram precisions
        precisions = []
        for n in range(1, self.n_gram + 1):
            matches = 0
            total = 0

            hyp_ngrams = self._get_ngrams(hypothesis, n)
            for ref in references:
                ref_ngrams = self._get_ngrams(ref, n)
                matches += sum((hyp_ngrams & ref_ngrams).values())

            total = max(len(hypothesis) - n + 1, 0)
            if total > 0:
                precisions.append(matches / total)
            else:
                precisions.append(0.0)

        # Calculate brevity penalty
        ref_len = min(len(ref) for ref in references)
        if len(hypothesis) > ref_len:
            bp = 1
        elif len(hypothesis) == 0:
            bp = 0
        else:
            bp = math.exp(1 - ref_len / len(hypothesis))

        # Calculate BLEU score
        if any(p == 0 for p in precisions):
            score = 0.0
        else:
            score = bp * math.exp(sum(math.log(p) for p in precisions) / len(precisions))

        return EvaluationResult(
            name="bleu_score",
            score=score,
            passed=score > 0.3,  # Reasonable threshold
            details={
                "precisions": precisions,
                "brevity_penalty": bp,
                "n_gram": self.n_gram
            }
        )

    def _get_ngrams(self, tokens: list[str], n: int) -> Counter:
        """Extract n-grams from token list."""
        ngrams = []
        for i in range(len(tokens) - n + 1):
            ngrams.append(tuple(tokens[i:i+n]))
        return Counter(ngrams)


class RougeScoreEvaluator(Evaluator):
    """ROUGE score evaluator for summarization quality."""

    def __init__(self, rouge_type: str = "rouge-l"):
        """
        Initialize ROUGE evaluator.

        Args:
            rouge_type: Type of ROUGE metric (rouge-1, rouge-2, rouge-l)
        """
        self.rouge_type = rouge_type.lower()

    def evaluate(
        self,
        response: str,
        ground_truth: str,
        **kwargs
    ) -> EvaluationResult:
        """Calculate ROUGE score."""
        hypothesis = response.lower().split()
        reference = ground_truth.lower().split()

        if self.rouge_type == "rouge-l":
            score = self._rouge_l(hypothesis, reference)
        elif self.rouge_type == "rouge-1":
            score = self._rouge_n(hypothesis, reference, 1)
        elif self.rouge_type == "rouge-2":
            score = self._rouge_n(hypothesis, reference, 2)
        else:
            raise ValueError(f"Unknown ROUGE type: {self.rouge_type}")

        return EvaluationResult(
            name=f"{self.rouge_type}_score",
            score=score,
            passed=score > 0.4,
            details={
                "rouge_type": self.rouge_type,
                "hypothesis_length": len(hypothesis),
                "reference_length": len(reference)
            }
        )

    def _rouge_n(self, hypothesis: list[str], reference: list[str], n: int) -> float:
        """Calculate ROUGE-N score."""
        hyp_ngrams = Counter(tuple(hypothesis[i:i+n]) for i in range(len(hypothesis)-n+1))
        ref_ngrams = Counter(tuple(reference[i:i+n]) for i in range(len(reference)-n+1))

        overlap = sum((hyp_ngrams & ref_ngrams).values())
        total = sum(ref_ngrams.values())

        if total == 0:
            return 0.0

        return overlap / total

    def _rouge_l(self, hypothesis: list[str], reference: list[str]) -> float:
        """Calculate ROUGE-L (Longest Common Subsequence) score."""
        lcs_length = self._lcs_length(hypothesis, reference)

        if len(reference) == 0:
            return 0.0

        precision = lcs_length / len(hypothesis) if len(hypothesis) > 0 else 0.0
        recall = lcs_length / len(reference)

        if precision + recall == 0:
            return 0.0

        f_score = 2 * precision * recall / (precision + recall)
        return f_score

    def _lcs_length(self, X: list[str], Y: list[str]) -> int:
        """Find length of longest common subsequence."""
        m, n = len(X), len(Y)
        L = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            for j in range(n + 1):
                if i == 0 or j == 0:
                    L[i][j] = 0
                elif X[i-1] == Y[j-1]:
                    L[i][j] = L[i-1][j-1] + 1
                else:
                    L[i][j] = max(L[i-1][j], L[i][j-1])

        return L[m][n]


class MeteorScoreEvaluator(Evaluator):
    """METEOR score evaluator with basic synonym matching."""

    def __init__(self):
        """Initialize METEOR evaluator."""
        # Simple synonym sets for demonstration
        self.synonyms = {
            "good": {"great", "excellent", "fine"},
            "bad": {"poor", "terrible", "awful"},
            "big": {"large", "huge", "enormous"},
            "small": {"tiny", "little", "mini"}
        }

    def evaluate(
        self,
        response: str,
        ground_truth: str,
        **kwargs
    ) -> EvaluationResult:
        """Calculate METEOR score."""
        hypothesis = response.lower().split()
        reference = ground_truth.lower().split()

        # Exact matches
        exact_matches = sum(1 for h, r in zip(hypothesis, reference) if h == r)

        # Synonym matches (simplified)
        synonym_matches = 0
        for h in hypothesis:
            for r in reference:
                if h != r and self._are_synonyms(h, r):
                    synonym_matches += 1

        total_matches = exact_matches + synonym_matches * 0.8  # Weight synonyms less

        precision = total_matches / len(hypothesis) if len(hypothesis) > 0 else 0.0
        recall = total_matches / len(reference) if len(reference) > 0 else 0.0

        if precision + recall == 0:
            score = 0.0
        else:
            # METEOR formula with penalty for fragmentation
            fmean = (10 * precision * recall) / (recall + 9 * precision)

            # Simplified fragmentation penalty
            chunks = self._count_chunks(hypothesis, reference)
            penalty = 0.5 * (chunks / total_matches) if total_matches > 0 else 0

            score = fmean * (1 - penalty)

        return EvaluationResult(
            name="meteor_score",
            score=score,
            passed=score > 0.35,
            details={
                "exact_matches": exact_matches,
                "synonym_matches": synonym_matches,
                "precision": precision,
                "recall": recall
            }
        )

    def _are_synonyms(self, word1: str, word2: str) -> bool:
        """Check if two words are synonyms."""
        for syn_set in self.synonyms.values():
            if word1 in syn_set and word2 in syn_set:
                return True
        return False

    def _count_chunks(self, hypothesis: list[str], reference: list[str]) -> int:
        """Count matching chunks (simplified)."""
        # This is a simplified chunk counting
        chunks = 1
        prev_match = False

        for h in hypothesis:
            curr_match = h in reference
            if curr_match and not prev_match:
                chunks += 1
            prev_match = curr_match

        return chunks


class GleuScoreEvaluator(Evaluator):
    """GLEU (Google-BLEU) score evaluator."""

    def __init__(self, n_gram: int = 4):
        """Initialize GLEU evaluator."""
        self.n_gram = n_gram

    def evaluate(
        self,
        response: str,
        ground_truth: str,
        **kwargs
    ) -> EvaluationResult:
        """Calculate GLEU score (simplified version)."""
        hypothesis = response.split()
        reference = ground_truth.split()

        # Calculate n-gram precisions with recall consideration
        scores = []

        for n in range(1, min(self.n_gram + 1, len(hypothesis) + 1)):
            hyp_ngrams = self._get_ngrams(hypothesis, n)
            ref_ngrams = self._get_ngrams(reference, n)

            matches = sum((hyp_ngrams & ref_ngrams).values())

            # GLEU considers both precision and recall
            precision = matches / len(hyp_ngrams) if len(hyp_ngrams) > 0 else 0.0
            recall = matches / len(ref_ngrams) if len(ref_ngrams) > 0 else 0.0

            if precision + recall > 0:
                f1 = 2 * precision * recall / (precision + recall)
                scores.append(f1)
            else:
                scores.append(0.0)

        # Average F1 scores
        score = sum(scores) / len(scores) if scores else 0.0

        return EvaluationResult(
            name="gleu_score",
            score=score,
            passed=score > 0.3,
            details={
                "n_gram_scores": scores,
                "n_gram": self.n_gram
            }
        )

    def _get_ngrams(self, tokens: list[str], n: int) -> Counter:
        """Extract n-grams from token list."""
        ngrams = []
        for i in range(len(tokens) - n + 1):
            ngrams.append(tuple(tokens[i:i+n]))
        return Counter(ngrams)


class F1ScoreEvaluator(Evaluator):
    """F1 score evaluator for classification tasks."""

    def evaluate(
        self,
        response: str,
        ground_truth: str,
        **kwargs
    ) -> EvaluationResult:
        """Calculate F1 score based on token overlap."""
        # Tokenize and normalize
        pred_tokens = set(response.lower().split())
        true_tokens = set(ground_truth.lower().split())

        # Calculate precision and recall
        if len(pred_tokens) == 0:
            precision = 0.0
        else:
            precision = len(pred_tokens & true_tokens) / len(pred_tokens)

        if len(true_tokens) == 0:
            recall = 0.0
        else:
            recall = len(pred_tokens & true_tokens) / len(true_tokens)

        # Calculate F1
        if precision + recall == 0:
            f1_score = 0.0
        else:
            f1_score = 2 * precision * recall / (precision + recall)

        return EvaluationResult(
            name="f1_score",
            score=f1_score,
            passed=f1_score > 0.5,
            details={
                "precision": precision,
                "recall": recall,
                "predicted_tokens": len(pred_tokens),
                "true_tokens": len(true_tokens),
                "overlap": len(pred_tokens & true_tokens)
            }
        )
