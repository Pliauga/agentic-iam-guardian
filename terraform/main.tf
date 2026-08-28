# ---------------------------------------------------------------------------------------------------------------------
# BASE KMS ENCRYPTION KEY
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_kms_key" "main" {
  description             = "Main encryption key for cloud resources in the Guardian architecture lab"
  deletion_window_in_days = 7
  enable_key_rotation     = true
}

resource "aws_kms_alias" "main_alias" {
  name          = "alias/guardian-main-key"
  target_key_id = aws_kms_key.main.key_id
}

# ---------------------------------------------------------------------------------------------------------------------
# GUARDIAN BROKER EXECUTION ROLE
# This role is assumed by the Guardian Broker to issue dynamically down-scoped STS session credentials for AI agents.
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_iam_role" "guardian_execution_role" {
  name = "AgenticGuardianExecutionRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "*" # In LocalStack, allows local caller / root to assume this broker role
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Broad base permissions attached to the role, which are ALWAYS constrained down at runtime
# via dynamic inline Session Policies created by the Guardian Broker during sts:AssumeRole
resource "aws_iam_role_policy" "guardian_base_policy" {
  name = "GuardianBasePermissions"
  role = aws_iam_role.guardian_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket",
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:Query",
          "kms:Decrypt",
          "kms:GenerateDataKey"
        ]
        Resource = "*"
      }
    ]
  })
}
