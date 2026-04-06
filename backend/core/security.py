import logging
import warnings
import re
from typing import Dict, Tuple

from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_anonymizer import AnonymizerEngine

import os

# Suppress annoying Pydantic warnings from Presidio internals
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
warnings.filterwarnings("ignore", message='Field "model_name" has conflict')
warnings.filterwarnings("ignore", message='Field "model_to_presidio_entity_mapping" has conflict')

logger = logging.getLogger(__name__)

class ReversiblePIIMasker:
    def __init__(self):
        try:
            self.analyzer = AnalyzerEngine()
            self.anonymizer = AnonymizerEngine()

            # Custom banking recognizers
            bank_account_pattern = Pattern(
                name="bank_account_pattern",
                regex=r"\b[0-9]{8,12}\b", # Simplified for demo purposes
                score=0.5
            )
            bank_recognizer = PatternRecognizer(
                supported_entity="BANK_ACCOUNT",
                patterns=[bank_account_pattern],
                context=["account", "acc", "bank"]
            )
            self.analyzer.registry.add_recognizer(bank_recognizer)

            logger.info("Presidio Reversible PII Masking Service initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Presidio: {e}")
            raise

    def mask_text(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Detects and masks PII in the given text, returning the masked text and a mapping for unmasking.
        """
        if not text:
            return text, {}

        try:
            # Analyze text for PII
            results = self.analyzer.analyze(
                text=text,
                language='en',
                entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "US_SSN", "CREDIT_CARD", "BANK_ACCOUNT"]
            )

            # Sort results by start index in descending order to replace from back to front
            results = sorted(results, key=lambda x: x.start, reverse=True)

            masked_text = text
            mapping = {}
            counter = {}

            import uuid

            for res in results:
                entity_type = res.entity_type
                # Use a UUID to avoid mapping collisions across multiple masking calls in the same session
                unique_id = str(uuid.uuid4())[:8]
                placeholder = f"<{entity_type}_{unique_id}>"

                original_value = text[res.start:res.end]

                # Save mapping (placeholder -> original)
                mapping[placeholder] = original_value

                # Replace in text
                masked_text = masked_text[:res.start] + placeholder + masked_text[res.end:]

            return masked_text, mapping

        except Exception as e:
            logger.error(f"Error during PII masking: {e}")
            return "<Error during PII masking: content hidden for safety>", {}

    def unmask_text(self, text: str, mapping: Dict[str, str]) -> str:
        """
        Replaces placeholders with original PII using the provided mapping.
        """
        if not text or not mapping:
            return text

        unmasked_text = text
        for placeholder, original_value in mapping.items():
            unmasked_text = unmasked_text.replace(placeholder, original_value)

        return unmasked_text

# Singleton instance
pii_masker = ReversiblePIIMasker()
