import logging
import warnings
import re
from typing import Dict, Tuple

from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

logger = logging.getLogger(__name__)

class ReversiblePIIMasker:
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

        # Add custom banking recognizers if needed
        # e.g. generic bank account pattern
        bank_account_pattern = Pattern(
            name="bank_account_pattern",
            regex=r"\b[0-9]{8,12}\b", # simplified for demo
            score=0.5
        )
        bank_recognizer = PatternRecognizer(
            supported_entity="BANK_ACCOUNT",
            patterns=[bank_account_pattern],
            context=["account", "acc", "bank"]
        )
        self.analyzer.registry.add_recognizer(bank_recognizer)

    def mask_text(self, text: str) -> Tuple[str, Dict[str, str]]:
        if not text:
            return text, {}

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

        for res in results:
            entity_type = res.entity_type
            counter[entity_type] = counter.get(entity_type, 0) + 1
            placeholder = f"<{entity_type}_{counter[entity_type]}>"

            original_value = text[res.start:res.end]

            # Save mapping (placeholder -> original)
            mapping[placeholder] = original_value

            # Replace in text
            masked_text = masked_text[:res.start] + placeholder + masked_text[res.end:]

        return masked_text, mapping

    def unmask_text(self, text: str, mapping: Dict[str, str]) -> str:
        unmasked_text = text
        for placeholder, original_value in mapping.items():
            unmasked_text = unmasked_text.replace(placeholder, original_value)
        return unmasked_text

if __name__ == "__main__":
    masker = ReversiblePIIMasker()
    text_to_mask = "My name is John Doe and my account is 123456789. Also my email is john.doe@example.com."
    masked, mapping = masker.mask_text(text_to_mask)
    print(f"Masked: {masked}")
    print(f"Mapping: {mapping}")

    unmasked = masker.unmask_text(masked, mapping)
    print(f"Unmasked: {unmasked}")
