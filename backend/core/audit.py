import logging
import json
import uuid
from datetime import datetime
from typing import Any, Dict

# Create a dedicated logger for audits
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

# We can output audit logs to a file for compliance
audit_handler = logging.FileHandler("audit.log")
audit_formatter = logging.Formatter('%(message)s') # Just output the JSON
audit_handler.setFormatter(audit_formatter)
audit_logger.addHandler(audit_handler)

class AuditLogger:
    @staticmethod
    def log_event(event_type: str, session_id: str, data: Dict[str, Any]):
        """
        Logs a structured JSON audit event.
        Ensure that `data` does NOT contain unmasked PII.
        """
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": event_type,
            "session_id": session_id,
            "data": data
        }
        # Log as a single JSON line
        audit_logger.info(json.dumps(event))

# Singleton/Utility
audit = AuditLogger()
