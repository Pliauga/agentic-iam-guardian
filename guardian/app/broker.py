import os
import json
import boto3
from botocore.config import Config
from typing import Dict, Any

AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
GUARDIAN_ROLE_ARN = os.getenv("GUARDIAN_ROLE_ARN", "arn:aws:iam::000000000000:role/AgenticGuardianExecutionRole")

class STSBroker:
    def __init__(self):
        self.sts_client = boto3.client(
            "sts",
            endpoint_url=AWS_ENDPOINT_URL,
            region_name=AWS_REGION,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
            config=Config(signature_version="v4")
        )

    def synthesize_session_policy(self, action: str, resource: str) -> str:
        """
        Creates an inline down-scoped session policy granting strictly the single
        approved action on the single approved resource.
        """
        policy_dict = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [action],
                    "Resource": [resource]
                }
            ]
        }
        return json.dumps(policy_dict)

    def issue_ephemeral_credentials(
        self,
        agent_id: str,
        task_id: str,
        agent_role: str,
        action: str,
        resource: str,
        duration_seconds: int = 900
    ) -> Dict[str, Any]:
        """
        Calls AWS STS AssumeRole with the down-scoped inline session policy and session tags.
        """
        session_policy = self.synthesize_session_policy(action, resource)
        session_name = f"agt-{agent_id[:10]}-{task_id[:10]}"

        # Minimum duration in AWS STS is 900s (15 min), though LocalStack accepts smaller values
        sts_duration = max(900, duration_seconds)

        response = self.sts_client.assume_role(
            RoleArn=GUARDIAN_ROLE_ARN,
            RoleSessionName=session_name,
            Policy=session_policy,
            DurationSeconds=sts_duration,
            Tags=[
                {"Key": "AgentID", "Value": agent_id},
                {"Key": "TaskID", "Value": task_id},
                {"Key": "AgentRole", "Value": agent_role},
                {"Key": "SecurityBroker", "Value": "AgenticIAMGuardian"}
            ]
        )

        creds = response["Credentials"]
        return {
            "access_key_id": creds["AccessKeyId"],
            "secret_access_key": creds["SecretAccessKey"],
            "session_token": creds["SessionToken"],
            "expiration": creds["Expiration"].isoformat() if hasattr(creds["Expiration"], "isoformat") else str(creds["Expiration"]),
            "session_policy_applied": json.loads(session_policy),
            "session_name": session_name
        }

sts_broker = STSBroker()
