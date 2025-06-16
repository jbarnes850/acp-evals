"""
Retrieval evaluator for ACP agents.

Evaluates the quality of information retrieval by agents,
checking relevance, completeness, and accuracy of retrieved content.
"""

from typing import Any

from ..providers.base import LLMProvider
from .base import EvaluationResult, Evaluator


class RetrievalEvaluator(Evaluator):
    """
    Evaluates the quality of information retrieval performed by agents.

    This evaluator assesses:
    - Relevance of retrieved information to the query
    - Completeness of the retrieval
    - Accuracy of the retrieved content
    - Ranking quality (if applicable)
    """

    def __init__(
        self,
        provider: LLMProvider | None = None,
        relevance_threshold: float = 0.7,
        completeness_weight: float = 0.3,
        relevance_weight: float = 0.5,
        accuracy_weight: float = 0.2
    ):
        """
        Initialize the retrieval evaluator.

        Args:
            provider: LLM provider for evaluation
            relevance_threshold: Minimum relevance score for passing
            completeness_weight: Weight for completeness in final score
            relevance_weight: Weight for relevance in final score
            accuracy_weight: Weight for accuracy in final score
        """
        self.provider = provider
        self.relevance_threshold = relevance_threshold
        self.weights = {
            "completeness": completeness_weight,
            "relevance": relevance_weight,
            "accuracy": accuracy_weight
        }

        self._evaluation_prompt = """
You are evaluating the quality of information retrieval.

Query: {query}

Retrieved Information:
{retrieved}

Expected/Reference Information (if available):
{reference}

Evaluate the retrieval quality based on:

1. Relevance (0-1): How relevant is the retrieved information to the query?
2. Completeness (0-1): Does the retrieval cover all important aspects of the query?
3. Accuracy (0-1): Is the retrieved information factually correct?
4. Missing Information: What key information is missing?
5. Irrelevant Information: What irrelevant information was included?

Format your response as:
Relevance Score: [0-1]
Completeness Score: [0-1]
Accuracy Score: [0-1]
Missing Information: [List key missing items]
Irrelevant Information: [List irrelevant items]
Overall Assessment: [Brief explanation]
"""

    @property
    def name(self) -> str:
        """Name of the evaluator."""
        return "RetrievalEvaluator"

    async def evaluate(
        self,
        task: str,
        response: str,
        reference: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> EvaluationResult:
        """
        Evaluate retrieval quality.

        Args:
            task: The retrieval query
            response: The retrieved information
            reference: Expected/reference retrieval results
            context: Additional context (e.g., 'source_documents', 'num_results')

        Returns:
            EvaluationResult with retrieval quality metrics
        """
        # Extract retrieved documents if provided in context
        retrieved_docs = []
        if context and 'source_documents' in context:
            retrieved_docs = context['source_documents']
        elif context and 'retrieved' in context:
            retrieved_docs = context['retrieved']
        else:
            # Treat response as the retrieved content
            retrieved_docs = [response]

        # Format retrieved information
        retrieved_text = self._format_retrieved_docs(retrieved_docs)

        if self.provider:
            # Use LLM for evaluation
            prompt = self._evaluation_prompt.format(
                query=task,
                retrieved=retrieved_text,
                reference=reference or "Not provided"
            )

            try:
                evaluation = await self.provider.generate(prompt)

                # Parse scores
                relevance_score = self._extract_score(evaluation, "Relevance Score:")
                completeness_score = self._extract_score(evaluation, "Completeness Score:")
                accuracy_score = self._extract_score(evaluation, "Accuracy Score:")

                # Calculate weighted score
                score = (
                    self.weights["relevance"] * relevance_score +
                    self.weights["completeness"] * completeness_score +
                    self.weights["accuracy"] * accuracy_score
                )

                # Extract additional information
                missing_info = self._extract_list(evaluation, "Missing Information:")
                irrelevant_info = self._extract_list(evaluation, "Irrelevant Information:")
                assessment = self._extract_section(evaluation, "Overall Assessment:")

                breakdown = {
                    "relevance": relevance_score,
                    "completeness": completeness_score,
                    "accuracy": accuracy_score,
                    "weighted_score": score,
                    "missing_items": len(missing_info),
                    "irrelevant_items": len(irrelevant_info)
                }

                passed = score >= self.relevance_threshold

                feedback = f"Retrieval Quality: {score:.2f}/1.0. "
                feedback += f"Relevance: {relevance_score:.2f}, "
                feedback += f"Completeness: {completeness_score:.2f}, "
                feedback += f"Accuracy: {accuracy_score:.2f}. "
                if missing_info:
                    feedback += f"Missing {len(missing_info)} key items. "
                feedback += assessment

            except Exception as e:
                score = 0.0
                passed = False
                breakdown = {"error": str(e)}
                feedback = f"Error during evaluation: {str(e)}"
        else:
            # Fallback: Simple similarity check
            score = self._simple_retrieval_check(task, retrieved_text, reference)
            passed = score >= self.relevance_threshold
            breakdown = {"similarity_score": score}
            feedback = f"Retrieval score: {score:.2f} (using similarity check)"

        return EvaluationResult(
            score=score,
            passed=passed,
            breakdown=breakdown,
            feedback=feedback,
            metadata={
                "evaluator": self.name,
                "query": task,
                "num_retrieved": len(retrieved_docs),
                "has_reference": reference is not None
            }
        )

    def _format_retrieved_docs(self, docs: list[Any]) -> str:
        """Format retrieved documents for evaluation."""
        if not docs:
            return "No documents retrieved"

        formatted = []
        for i, doc in enumerate(docs):
            if isinstance(doc, dict):
                content = doc.get('content', doc.get('text', str(doc)))
                source = doc.get('source', doc.get('url', ''))
                formatted.append(f"Document {i+1}:\n{content}\n[Source: {source}]")
            else:
                formatted.append(f"Document {i+1}:\n{str(doc)}")

        return "\n\n".join(formatted)

    def _simple_retrieval_check(self, query: str, retrieved: str, reference: str | None) -> float:
        """Simple retrieval check using keyword overlap."""
        # Extract key terms from query
        query_terms = set(query.lower().split())
        retrieved_terms = set(retrieved.lower().split())

        # Remove common words
        common_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'what', 'when',
                       'where', 'who', 'why', 'how', 'which', 'of', 'to', 'in', 'for'}
        query_terms = query_terms - common_words

        if not query_terms:
            return 0.5

        # Check query coverage in retrieved
        coverage = len(query_terms.intersection(retrieved_terms)) / len(query_terms)

        # If reference is provided, check similarity
        if reference:
            ref_terms = set(reference.lower().split()) - common_words
            similarity = len(retrieved_terms.intersection(ref_terms)) / max(len(ref_terms), 1)
            return (coverage + similarity) / 2

        return coverage

    def _extract_score(self, text: str, marker: str) -> float:
        """Extract numerical score from text."""
        import re
        pattern = marker + r"\s*([0-9.]+)"
        match = re.search(pattern, text)
        if match:
            try:
                return float(match.group(1))
            except:
                pass
        return 0.5

    def _extract_list(self, text: str, marker: str) -> list[str]:
        """Extract list items after a marker."""
        lines = text.split('\n')
        items = []
        found_marker = False

        for line in lines:
            if marker in line:
                found_marker = True
                continue
            if found_marker and line.strip():
                if line.strip().startswith('-') or line.strip().startswith('•'):
                    items.append(line.strip()[1:].strip())
                elif ':' in line and any(m in line for m in ['Score', 'Information', 'Assessment']):
                    break

        return items

    def _extract_section(self, text: str, marker: str) -> str:
        """Extract text section after marker."""
        if marker in text:
            parts = text.split(marker)
            if len(parts) > 1:
                # Get text until next section or end
                section = parts[1].strip()
                lines = section.split('\n')
                result = []
                for line in lines:
                    if line and not any(m in line for m in ['Score:', 'Information:']):
                        result.append(line)
                    else:
                        break
                return ' '.join(result).strip()
        return ""
