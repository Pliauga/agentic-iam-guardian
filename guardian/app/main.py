from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

from .policy_engine import policy_engine
from .broker import sts_broker
from .audit import audit_ledger

app = FastAPI(
    title="Agentic IAM Guardian",
    description="Just-In-Time (JIT) Dynamic Identity Broker and Policy Firewall for Autonomous AI Agents",
    version="1.0.0"
)

class LeaseRequest(BaseModel):
    agent_id: str = Field(..., example="agent-alpha-01", description="Unique ID of the AI agent")
    task_id: str = Field(..., example="task-backup-992", description="Unique ID of the specific task execution")
    agent_role: str = Field(default="devops-agent", example="devops-agent", description="Declared role of the agent")
    intent_description: str = Field(..., example="Upload daily report to S3", description="Human/Agent natural language intent")
    action: str = Field(..., example="s3:PutObject", description="Target AWS IAM action verb")
    resource_arn: str = Field(..., example="arn:aws:s3:::enterprise-public-reports-bucket/reports/q3.txt", description="Target resource ARN")
    requested_duration_seconds: int = Field(default=300, le=3600, ge=60, description="Requested session lifetime in seconds")

class LeaseResponse(BaseModel):
    status: str
    decision: str
    reason: str
    credentials: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None

@app.get("/health")
def health_check():
    return {
        "status": "HEALTHY",
        "service": "Agentic IAM Guardian",
        "zero_trust_enforcement": "ACTIVE"
    }

@app.post("/lease", response_model=LeaseResponse)
def request_credential_lease(req: LeaseRequest):
    """
    Evaluates an AI agent's requested action against guardrail policies.
    If valid, dynamically synthesizes an inline down-scoped AWS STS session policy.
    """
    # 1. Policy Evaluation
    is_allowed, reason = policy_engine.evaluate(
        agent_role=req.agent_role,
        action=req.action,
        resource=req.resource_arn,
        duration_seconds=req.requested_duration_seconds
    )

    if not is_allowed:
        # Record Violation in Audit Ledger
        audit_ledger.record_event(
            agent_id=req.agent_id,
            task_id=req.task_id,
            intent=req.intent_description,
            action=req.action,
            resource=req.resource_arn,
            decision="BLOCKED",
            reason=reason
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "status": "ACCESS_DENIED",
                "decision": "BLOCKED",
                "reason": reason,
                "agent_id": req.agent_id,
                "task_id": req.task_id
            }
        )

    # 2. Dynamic STS Session Policy Synthesis
    try:
        creds = sts_broker.issue_ephemeral_credentials(
            agent_id=req.agent_id,
            task_id=req.task_id,
            agent_role=req.agent_role,
            action=req.action,
            resource=req.resource_arn,
            duration_seconds=req.requested_duration_seconds
        )
        session_id = creds["session_name"]

        # Record Approved Lease in Audit Ledger
        audit_ledger.record_event(
            agent_id=req.agent_id,
            task_id=req.task_id,
            intent=req.intent_description,
            action=req.action,
            resource=req.resource_arn,
            decision="ALLOWED",
            reason=reason,
            session_id=session_id,
            duration_seconds=req.requested_duration_seconds
        )

        return LeaseResponse(
            status="SUCCESS",
            decision="ALLOWED",
            reason=reason,
            credentials=creds,
            session_id=session_id
        )

    except Exception as e:
        audit_ledger.record_event(
            agent_id=req.agent_id,
            task_id=req.task_id,
            intent=req.intent_description,
            action=req.action,
            resource=req.resource_arn,
            decision="ERROR",
            reason=f"Broker synthesis failure: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to issue STS credentials: {str(e)}"
        )

@app.get("/audit")
def get_audit_logs(limit: int = 50):
    """Returns the latest audit ledger records."""
    return {
        "total_records": len(audit_ledger.records),
        "violations_count": len(audit_ledger.get_violations()),
        "records": audit_ledger.get_all(limit)
    }

@app.get("/audit/violations")
def get_audit_violations():
    """Returns all blocked security violations and prompt-injection attempts."""
    violations = audit_ledger.get_violations()
    return {
        "violations_count": len(violations),
        "violations": violations
    }
