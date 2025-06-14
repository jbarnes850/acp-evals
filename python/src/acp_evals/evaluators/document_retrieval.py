"""
Document retrieval evaluator for ACP agents.

Evaluates the quality of document retrieval and ranking,
with focus on precision, recall, and ranking metrics.
"""

import math
from dataclasses import dataclass
from typing import Any

from ..providers.base import LLMProvider
from .base import EvaluationResult, Evaluator


@dataclass
class RetrievedDocument:
    """Represents a retrieved document."""
    doc_id: str
    content: str
    score: float
    metadata: dict[str, Any] | None = None


class DocumentRetrievalEvaluator(Evaluator):
    """
    Evaluates document retrieval quality using standard IR metrics.

    This evaluator computes:
    - Precision and Recall
    - F1 Score
    - Mean Average Precision (MAP)
    - Normalized Discounted Cumulative Gain (NDCG)
    - Mean Reciprocal Rank (MRR)
    """

    def __init__(
        self,
        provider: LLMProvider | None = None,
        k_values: list[int] = None,
        relevance_threshold: float = 0.7
    ):
        """
        Initialize the document retrieval evaluator.

        Args:
            provider: LLM provider for relevance assessment
            k_values: List of k values for P@k and R@k metrics (default: [1, 3, 5, 10])
            relevance_threshold: Threshold for binary relevance judgment
        """
        self.provider = provider
        self.k_values = k_values or [1, 3, 5, 10]
        self.relevance_threshold = relevance_threshold

        self._relevance_prompt = """
Assess the relevance of a document to a query.

Query: {query}

Document:
{document}

Rate the relevance on a scale of 0-3:
- 0: Not relevant
- 1: Marginally relevant
- 2: Relevant
- 3: Highly relevant

Also provide a binary judgment (relevant/not relevant) based on whether the document helps answer the query.

Format:
Relevance Score: [0-3]
Binary Relevance: [Yes/No]
Explanation: [Brief explanation]
"""

    @property
    def name(self) -> str:
        """Name of the evaluator."""
        return "DocumentRetrievalEvaluator"

    async def evaluate(
        self,
        task: str,
        response: str,
        reference: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> EvaluationResult:
        """
        Evaluate document retrieval quality.

        Args:
            task: The search query
            response: Not used directly (documents should be in context)
            reference: Ground truth relevant document IDs (comma-separated)
            context: Must contain 'retrieved_documents' with list of documents

        Returns:
            EvaluationResult with IR metrics
        """
        if not context or 'retrieved_documents' not in context:
            return EvaluationResult(
                score=0.0,
                passed=False,
                breakdown={"error": "No retrieved documents provided"},
                feedback="Document retrieval evaluation requires 'retrieved_documents' in context",
                metadata={"evaluator": self.name}
            )

        # Parse retrieved documents
        retrieved_docs = self._parse_documents(context['retrieved_documents'])

        # Get ground truth if provided
        relevant_ids = set()
        if reference:
            relevant_ids = set(doc_id.strip() for doc_id in reference.split(','))

        # Assess relevance for each document
        relevance_scores = await self._assess_relevance(task, retrieved_docs)

        # Compute metrics
        metrics = self._compute_metrics(retrieved_docs, relevance_scores, relevant_ids)

        # Overall score (weighted combination of metrics)
        score = self._compute_overall_score(metrics)
        passed = score >= 0.7

        # Format feedback
        feedback = self._format_feedback(metrics, len(retrieved_docs))

        return EvaluationResult(
            score=score,
            passed=passed,
            breakdown=metrics,
            feedback=feedback,
            metadata={
                "evaluator": self.name,
                "query": task,
                "num_retrieved": len(retrieved_docs),
                "num_relevant": len(relevant_ids),
                "k_values": self.k_values
            }
        )

    def _parse_documents(self, docs: list[Any]) -> list[RetrievedDocument]:
        """Parse documents into standard format."""
        parsed = []

        for i, doc in enumerate(docs):
            if isinstance(doc, dict):
                doc_id = doc.get('id', doc.get('doc_id', f'doc_{i}'))
                content = doc.get('content', doc.get('text', str(doc)))
                score = doc.get('score', doc.get('relevance', 1.0))
                metadata = doc.get('metadata', {})
            else:
                doc_id = f'doc_{i}'
                content = str(doc)
                score = 1.0
                metadata = {}

            parsed.append(RetrievedDocument(
                doc_id=doc_id,
                content=content,
                score=float(score),
                metadata=metadata
            ))

        # Sort by score (descending)
        parsed.sort(key=lambda d: d.score, reverse=True)
        return parsed

    async def _assess_relevance(
        self,
        query: str,
        documents: list[RetrievedDocument]
    ) -> dict[str, tuple[float, bool]]:
        """Assess relevance of each document to the query."""
        relevance_scores = {}

        if self.provider:
            # Use LLM for relevance assessment
            for doc in documents:
                prompt = self._relevance_prompt.format(
                    query=query,
                    document=doc.content[:1000]  # Limit content length
                )

                try:
                    assessment = await self.provider.generate(prompt)
                    score = self._extract_relevance_score(assessment)
                    is_relevant = self._extract_binary_relevance(assessment)
                    relevance_scores[doc.doc_id] = (score, is_relevant)
                except:
                    # Default to retrieval score
                    relevance_scores[doc.doc_id] = (
                        doc.score * 3,  # Scale to 0-3
                        doc.score >= self.relevance_threshold
                    )
        else:
            # Use retrieval scores directly
            for doc in documents:
                relevance_scores[doc.doc_id] = (
                    doc.score * 3,  # Scale to 0-3
                    doc.score >= self.relevance_threshold
                )

        return relevance_scores

    def _compute_metrics(
        self,
        documents: list[RetrievedDocument],
        relevance_scores: dict[str, tuple[float, bool]],
        ground_truth: set[str]
    ) -> dict[str, float]:
        """Compute standard IR metrics."""
        metrics = {}

        # Get relevance info for retrieved docs
        retrieved_relevant = []
        relevance_grades = []

        for i, doc in enumerate(documents):
            grade, is_relevant = relevance_scores.get(doc.doc_id, (0, False))
            relevance_grades.append(grade)

            if ground_truth:
                # Use ground truth
                is_relevant = doc.doc_id in ground_truth

            retrieved_relevant.append(is_relevant)

        # Precision and Recall at k
        for k in self.k_values:
            if k <= len(documents):
                relevant_at_k = sum(retrieved_relevant[:k])
                metrics[f'P@{k}'] = relevant_at_k / k

                if ground_truth:
                    metrics[f'R@{k}'] = relevant_at_k / max(len(ground_truth), 1)

        # F1 Score
        if ground_truth and len(documents) > 0:
            total_retrieved_relevant = sum(retrieved_relevant)
            precision = total_retrieved_relevant / len(documents)
            recall = total_retrieved_relevant / len(ground_truth)

            if precision + recall > 0:
                metrics['F1'] = 2 * precision * recall / (precision + recall)
            else:
                metrics['F1'] = 0.0

        # Mean Average Precision (MAP)
        metrics['MAP'] = self._compute_map(retrieved_relevant)

        # Normalized Discounted Cumulative Gain (NDCG)
        for k in self.k_values:
            if k <= len(documents):
                metrics[f'NDCG@{k}'] = self._compute_ndcg(relevance_grades[:k])

        # Mean Reciprocal Rank (MRR)
        metrics['MRR'] = self._compute_mrr(retrieved_relevant)

        return metrics

    def _compute_map(self, relevant_list: list[bool]) -> float:
        """Compute Mean Average Precision."""
        if not relevant_list or not any(relevant_list):
            return 0.0

        num_relevant = 0
        precision_sum = 0.0

        for i, is_relevant in enumerate(relevant_list):
            if is_relevant:
                num_relevant += 1
                precision_sum += num_relevant / (i + 1)

        return precision_sum / max(sum(relevant_list), 1)

    def _compute_ndcg(self, relevance_grades: list[float]) -> float:
        """Compute Normalized Discounted Cumulative Gain."""
        if not relevance_grades:
            return 0.0

        # Compute DCG
        dcg = relevance_grades[0]
        for i in range(1, len(relevance_grades)):
            dcg += relevance_grades[i] / math.log2(i + 1)

        # Compute ideal DCG
        ideal_grades = sorted(relevance_grades, reverse=True)
        idcg = ideal_grades[0]
        for i in range(1, len(ideal_grades)):
            idcg += ideal_grades[i] / math.log2(i + 1)

        return dcg / idcg if idcg > 0 else 0.0

    def _compute_mrr(self, relevant_list: list[bool]) -> float:
        """Compute Mean Reciprocal Rank."""
        for i, is_relevant in enumerate(relevant_list):
            if is_relevant:
                return 1.0 / (i + 1)
        return 0.0

    def _compute_overall_score(self, metrics: dict[str, float]) -> float:
        """Compute weighted overall score."""
        # Focus on key metrics
        key_metrics = []

        if 'MAP' in metrics:
            key_metrics.append(metrics['MAP'])

        if 'NDCG@5' in metrics:
            key_metrics.append(metrics['NDCG@5'])
        elif 'NDCG@3' in metrics:
            key_metrics.append(metrics['NDCG@3'])

        if 'MRR' in metrics:
            key_metrics.append(metrics['MRR'])

        if 'P@5' in metrics:
            key_metrics.append(metrics['P@5'])

        return sum(key_metrics) / len(key_metrics) if key_metrics else 0.0

    def _format_feedback(self, metrics: dict[str, float], num_docs: int) -> str:
        """Format metrics into readable feedback."""
        feedback = f"Retrieved {num_docs} documents. "

        # Report key metrics
        if 'MAP' in metrics:
            feedback += f"MAP: {metrics['MAP']:.3f}, "

        if 'MRR' in metrics:
            feedback += f"MRR: {metrics['MRR']:.3f}, "

        # Report precision at different k
        p_scores = []
        for k in [1, 3, 5]:
            if f'P@{k}' in metrics:
                p_scores.append(f"P@{k}={metrics[f'P@{k}']:.2f}")

        if p_scores:
            feedback += f"Precision: {', '.join(p_scores)}. "

        # Add NDCG if available
        if 'NDCG@5' in metrics:
            feedback += f"NDCG@5: {metrics['NDCG@5']:.3f}."

        return feedback.strip()

    def _extract_relevance_score(self, text: str) -> float:
        """Extract relevance score from assessment."""
        import re
        pattern = r"Relevance Score:\s*([0-3])"
        match = re.search(pattern, text)
        if match:
            try:
                return float(match.group(1))
            except:
                pass
        return 0.0

    def _extract_binary_relevance(self, text: str) -> bool:
        """Extract binary relevance from assessment."""
        import re
        pattern = r"Binary Relevance:\s*(Yes|No)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).lower() == 'yes'
        return False
