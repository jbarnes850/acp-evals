"""Input validation utilities for ACP Evals."""

from typing import Any
from urllib.parse import urlparse

from .exceptions import InvalidEvaluationInputError, format_validation_error


class InputValidator:
    """Validates evaluation inputs."""

    @staticmethod
    def validate_agent_input(agent: str | Any) -> None:
        """
        Validate agent input (URL, callable, or instance).

        Args:
            agent: Agent to validate

        Raises:
            InvalidEvaluationInputError: If agent is invalid
        """
        if isinstance(agent, str):
            # Allow different string formats
            if agent.startswith(("http://", "https://")):
                # Validate URL format
                try:
                    parsed = urlparse(agent)
                    if not parsed.scheme or not parsed.netloc:
                        raise InvalidEvaluationInputError(
                            "agent",
                            f"Invalid URL format: {agent}. Expected format: http://host:port/agents/name",
                        )

                    # Check for /agents/ path for strict ACP URLs
                    if "/agents/" not in agent:
                        raise InvalidEvaluationInputError(
                            "agent", f"Agent URL must contain '/agents/' path. Got: {agent}"
                        )

                except Exception as e:
                    raise InvalidEvaluationInputError("agent", f"Invalid agent URL: {str(e)}")
            else:
                # Allow file paths, function references, or other string identifiers
                # These will be handled by the agent factory
                if not agent.strip():
                    raise InvalidEvaluationInputError("agent", "Agent identifier cannot be empty")

        elif callable(agent):
            # Callable is valid
            pass

        elif hasattr(agent, "run"):
            # Instance with run method is valid
            pass

        else:
            raise InvalidEvaluationInputError(
                "agent",
                f"Agent must be a URL string, callable, or instance with 'run' method. Got: {type(agent)}",
            )

    @staticmethod
    def validate_test_input(test_input: str) -> None:
        """
        Validate test input string.

        Args:
            test_input: Input to validate

        Raises:
            InvalidEvaluationInputError: If input is invalid
        """
        if not isinstance(test_input, str):
            raise InvalidEvaluationInputError(
                "input", f"Test input must be a string. Got: {type(test_input)}"
            )

        if not test_input.strip():
            raise InvalidEvaluationInputError("input", "Test input cannot be empty")

        # Check for reasonable length
        if len(test_input) > 100000:
            raise InvalidEvaluationInputError(
                "input",
                f"Test input too long ({len(test_input)} chars). Maximum: 100,000 characters",
            )

    @staticmethod
    def validate_expected_output(expected: str | dict[str, Any]) -> None:
        """
        Validate expected output.

        Args:
            expected: Expected output to validate

        Raises:
            InvalidEvaluationInputError: If expected output is invalid
        """
        if isinstance(expected, str):
            if not expected.strip():
                raise InvalidEvaluationInputError("expected", "Expected output cannot be empty")

        elif isinstance(expected, dict):
            if not expected:
                raise InvalidEvaluationInputError(
                    "expected", "Expected output dict cannot be empty"
                )

        else:
            raise InvalidEvaluationInputError(
                "expected", f"Expected output must be string or dict. Got: {type(expected)}"
            )

    @staticmethod
    def validate_rubric(rubric: dict[str, dict[str, Any]]) -> None:
        """
        Validate evaluation rubric.

        Args:
            rubric: Rubric to validate

        Raises:
            InvalidEvaluationInputError: If rubric is invalid
        """
        if not isinstance(rubric, dict):
            raise InvalidEvaluationInputError(
                "rubric", f"Rubric must be a dictionary. Got: {type(rubric)}"
            )

        if not rubric:
            raise InvalidEvaluationInputError("rubric", "Rubric cannot be empty")

        errors = {}
        total_weight = 0.0

        for criterion, config in rubric.items():
            if not isinstance(config, dict):
                errors[criterion] = "Criterion config must be a dict"
                continue

            # Check required fields
            if "weight" not in config:
                errors[criterion] = "Missing 'weight' field"
                continue

            if "criteria" not in config:
                errors[criterion] = "Missing 'criteria' field"
                continue

            # Validate weight
            try:
                weight = float(config["weight"])
                if weight < 0 or weight > 1:
                    errors[criterion] = f"Weight must be between 0 and 1. Got: {weight}"
                else:
                    total_weight += weight
            except (TypeError, ValueError):
                errors[criterion] = f"Weight must be a number. Got: {config['weight']}"

            # Validate criteria
            if not isinstance(config["criteria"], str) or not config["criteria"].strip():
                errors[criterion] = "Criteria must be a non-empty string"

        # Check total weight
        if abs(total_weight - 1.0) > 0.01:  # Allow small floating point errors
            errors["_total_weight"] = f"Total weight must equal 1.0. Got: {total_weight:.3f}"

        if errors:
            raise InvalidEvaluationInputError("rubric", format_validation_error(errors))

    @staticmethod
    def validate_threshold(threshold: float, name: str = "threshold") -> None:
        """
        Validate a threshold value.

        Args:
            threshold: Threshold to validate
            name: Name of threshold for error messages

        Raises:
            InvalidEvaluationInputError: If threshold is invalid
        """
        try:
            threshold = float(threshold)
        except (TypeError, ValueError):
            raise InvalidEvaluationInputError(name, f"Must be a number. Got: {type(threshold)}")

        if threshold < 0 or threshold > 1:
            raise InvalidEvaluationInputError(name, f"Must be between 0 and 1. Got: {threshold}")

    @staticmethod
    def validate_test_cases(test_cases: list[dict[str, Any]]) -> None:
        """
        Validate a list of test cases.

        Args:
            test_cases: Test cases to validate

        Raises:
            InvalidEvaluationInputError: If test cases are invalid
        """
        if not isinstance(test_cases, list):
            raise InvalidEvaluationInputError(
                "test_cases", f"Must be a list. Got: {type(test_cases)}"
            )

        if not test_cases:
            raise InvalidEvaluationInputError("test_cases", "Test cases list cannot be empty")

        errors = {}

        for i, test_case in enumerate(test_cases):
            case_errors = []

            if not isinstance(test_case, dict):
                case_errors.append(f"Test case must be a dict. Got: {type(test_case)}")
                continue

            # Check required fields
            if "input" not in test_case:
                case_errors.append("Missing 'input' field")
            else:
                try:
                    InputValidator.validate_test_input(test_case["input"])
                except InvalidEvaluationInputError as e:
                    case_errors.append(f"Invalid input: {e.args[0]}")

            # Check for expected or expected_output
            if "expected" not in test_case and "expected_output" not in test_case:
                case_errors.append("Missing 'expected' or 'expected_output' field")
            else:
                expected_field = "expected" if "expected" in test_case else "expected_output"
                try:
                    InputValidator.validate_expected_output(test_case[expected_field])
                except InvalidEvaluationInputError as e:
                    case_errors.append(f"Invalid {expected_field}: {e.args[0]}")

            if case_errors:
                errors[f"test_case_{i}"] = "; ".join(case_errors)

        if errors:
            raise InvalidEvaluationInputError("test_cases", format_validation_error(errors))
