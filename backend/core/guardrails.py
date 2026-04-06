import logging
import re
from typing import Tuple

logger = logging.getLogger(__name__)

class InputGuardrail:
    def __init__(self):
        # Common prompt injection heuristics
        self.injection_patterns = [
            r"ignore previous instructions",
            r"ignore all previous instructions",
            r"ignore the above instructions",
            r"disregard previous instructions",
            r"system prompt",
            r"you are now",
            r"from now on you will",
            r"jailbreak",
            r"bypass instructions",
            r"forget what you were told",
            r"forget previous instructions"
        ]
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.injection_patterns]
        logger.info("InputGuardrail initialized successfully.")

    def detect_injection(self, text: str) -> Tuple[bool, str]:
        """
        Scans input text for potential prompt injection patterns.
        Returns a boolean (True if injection detected, False otherwise)
        and an explanatory message.
        """
        if not text:
            return False, ""

        for pattern in self.compiled_patterns:
            if pattern.search(text):
                logger.warning(f"Prompt injection detected! Pattern matched: {pattern.pattern}")
                return True, "Potential prompt injection detected. Request blocked for security reasons."

        return False, ""

# Singleton instance
guardrail = InputGuardrail()
