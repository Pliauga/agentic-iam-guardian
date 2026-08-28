import datetime
import logging
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AgenticGuardian")

class AuditLog:
    """In-memory telemetry ledger recording all agent intents, authorizations, and policy violations."""
    def __init__(self):
        self.records: List[Dict[str, Any]] = []

    def record_event(
        self,
        agent_id: str,
        task_id: str,
        intent: str,
        action: str,
        resource: str,
        decision: str,
        reason: str,
        session_id: Optional[str] = None,
        duration_seconds: Optional[int] = None
    ) -> Dict[str, Any]:
        event = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "agent_id": agent_id,
            "task_id": task_id,
            "intent": intent,
            "requested_action": action,
            "requested_resource": resource,
            "decision": decision,  # "ALLOWED" or "BLOCKED"
            "reason": reason,
            "session_id": session_id,
            "ttl_seconds": duration_seconds
        }
        self.records.append(event)
        
        if decision == "ALLOWED":
            logger.info(f"🛡️ [APPROVED] Agent={agent_id} | Task={task_id} | Action={action} on {resource}")
        else:
            logger.warning(f"🚨 [BLOCKED] Agent={agent_id} | Task={task_id} | Action={action} on {resource} | Reason={reason}")
            
        return event

    def get_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        return list(reversed(self.records))[:limit]

    def get_violations(self) -> List[Dict[str, Any]]:
        return [r for r in self.records if r["decision"] == "BLOCKED"]

audit_ledger = AuditLog()
