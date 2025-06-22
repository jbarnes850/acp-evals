"""
Reliability Evaluation Example

This example demonstrates how to evaluate agent reliability through
error handling, recovery, and consistency tests. Perfect for production readiness.

Run:
    python reliability_eval.py
"""

import asyncio
import random

from acp_evals import EvalResult, ReliabilityEval


# Mock customer support agent for demonstration
class CustomerSupportAgent:
    """Agent that handles customer inquiries with error recovery."""

    def __init__(self):
        self.request_count = 0
        self.responses = {
            "return policy": "Our return policy allows returns within 30 days of purchase with receipt.",
            "shipping info": "We offer free shipping on orders over $50. Standard shipping takes 5-7 business days.",
            "contact support": "You can reach our support team at support@example.com or 1-800-EXAMPLE.",
            "business hours": "Our business hours are Monday-Friday, 9 AM to 5 PM EST.",
            "order status": "I can help you check your order status. Please provide your order number.",
        }

    async def __call__(self, prompt: str) -> str:
        """Simulate customer support with realistic error scenarios."""
        self.request_count += 1

        # Simulate various reliability scenarios
        if "error" in prompt.lower() and self.request_count % 3 == 0:
            # Simulate occasional errors (33% chance on error prompts)
            raise Exception("Temporary service error")

        elif len(prompt) == 0:
            # Handle empty input
            return "I notice you didn't enter anything. How can I help you today?"

        elif len(prompt) > 500:
            # Handle very long input
            return "Your message is quite long. Could you please summarize your main question?"

        elif not any(c.isalnum() for c in prompt):
            # Handle malformed input (no alphanumeric characters)
            return "I didn't understand that request. Could you please rephrase?"

        else:
            # Check for known topics
            prompt_lower = prompt.lower()
            for key, response in self.responses.items():
                if key in prompt_lower:
                    return response

            # Default response
            return "I'm here to help! Please tell me more about your inquiry."


async def main():
    """Run reliability evaluations."""
    print("\n🛡️  Running Reliability Evaluation Example\n")
    print("This example tests agent reliability, consistency, and error recovery.")
    print("Watch how the agent handles various failure scenarios!\n")

    # Create agent and evaluator
    agent = CustomerSupportAgent()
    evaluator = ReliabilityEval(agent)

    # Test scenarios
    test_scenarios = [
        # Normal operations
        ("What is your return policy?", "normal"),
        ("Tell me about shipping info", "normal"),
        ("How can I contact support?", "normal"),
        # Consistency test - same question 3 times
        ("What are your business hours?", "consistency"),
        ("What are your business hours?", "consistency"),
        ("What are your business hours?", "consistency"),
        # Error scenarios
        ("This might cause an error", "error"),
        ("Another error prone request", "error"),
        ("Yet another error test", "error"),
        # Edge cases
        ("", "empty"),
        ("!!@#$%^&*()", "malformed"),
        ("A" * 1000, "long_input"),
    ]

    # Track metrics
    results = []
    errors = []
    consistency_check = {}

    print("🔍 Running reliability tests...\n")

    for i, (prompt, scenario_type) in enumerate(test_scenarios):
        print(
            f"Test {i + 1}/{len(test_scenarios)} [{scenario_type}]: {prompt[:50]}{'...' if len(prompt) > 50 else ''}"
        )

        try:
            result = await evaluator.run(prompt)
            results.append(result)

            # Track consistency
            if scenario_type == "consistency":
                if prompt not in consistency_check:
                    consistency_check[prompt] = []
                # Store the score for consistency checking
                consistency_check[prompt].append(result.score)

            # Get latency from metadata if available
            result.metadata.get("latency_ms", 0)
            print(f"   ✅ Success (score: {result.score:.2f})")

        except Exception as e:
            errors.append((prompt, str(e)))
            print(f"   ❌ Error: {str(e)}")

            # Retry logic demonstration
            print("   🔄 Retrying...")
            await asyncio.sleep(0.1)
            try:
                retry_result = await evaluator.run(prompt)
                results.append(retry_result)
                print("   ✅ Retry successful!")
            except Exception as retry_e:
                print(f"   ❌ Retry failed: {str(retry_e)}")

    # Calculate reliability metrics
    total_tests = len(test_scenarios)
    successful_tests = len(results)
    failed_tests = len(errors)
    reliability_score = successful_tests / total_tests

    # Check consistency
    consistency_issues = 0
    for prompt, responses in consistency_check.items():
        unique_responses = set(responses)
        if len(unique_responses) > 1:
            consistency_issues += 1

    consistency_score = (
        1.0 - (consistency_issues / len(consistency_check)) if consistency_check else 1.0
    )

    # Summary
    print("\n📊 Reliability Metrics:")
    print(f"   Overall Reliability: {reliability_score:.1%}")
    print(f"   Consistency Score: {consistency_score:.1%}")
    print(f"   Success Rate: {successful_tests}/{total_tests}")
    print(f"   Error Rate: {failed_tests}/{total_tests}")

    # Consistency details
    if consistency_check:
        print("\n🔄 Consistency Analysis:")
        for prompt, responses in consistency_check.items():
            unique_responses = set(responses)
            if len(unique_responses) > 1:
                print(f"   ⚠️  Inconsistent: '{prompt}'")
                print(f"      Found {len(unique_responses)} different responses")
            else:
                print(f"   ✅ Consistent: '{prompt}'")

    # Error analysis
    if errors:
        print("\n⚠️  Error Analysis:")
        for prompt, error in errors:
            print(f"   Prompt: '{prompt[:50]}...'")
            print(f"   Error: {error}")


if __name__ == "__main__":
    asyncio.run(main())
