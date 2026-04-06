import logging
import warnings
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

import os

# Suppress annoying Pydantic warnings from Presidio internals
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
warnings.filterwarnings("ignore", message='Field "model_name" has conflict')
warnings.filterwarnings("ignore", message='Field "model_to_presidio_entity_mapping" has conflict')

logger = logging.getLogger(__name__)

class PIIMaskingService:
    def __init__(self):
        try:
            self.analyzer = AnalyzerEngine()
            self.anonymizer = AnonymizerEngine()
            logger.info("Presidio PII Masking Service initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Presidio: {e}")
            raise

    def mask_text(self, text: str) -> str:
        """
        Detects and masks PII in the given text.
        """
        if not text:
            return text

        try:
            # Analyze text for PII
            # By default it looks for EMAIL_ADDRESS, PERSON, PHONE_NUMBER, US_SSN, etc.
            results = self.analyzer.analyze(
                text=text,
                entities=None, # None means all default entities
                language='en'
            )

            # Anonymize the findings
            anonymized_result = self.anonymizer.anonymize(
                text=text,
                analyzer_results=results
            )
            return anonymized_result.text
        except Exception as e:
            logger.error(f"Error during PII masking: {e}")
            # In case of error, fail safe by returning a redacted string or the original text?
            # Industry standard: fail safe, redact everything or return generic error.
            # But to not break the app completely, we will log it and return the original text
            # or a safe string. Let's return a safe string.
            return "<Error during PII masking: content hidden for safety>"

# Singleton instance
pii_masker = PIIMaskingService()
