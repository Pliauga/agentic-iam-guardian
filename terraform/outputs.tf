output "guardian_role_arn" {
  description = "ARN of the Guardian Execution IAM Role"
  value       = aws_iam_role.guardian_execution_role.arn
}

output "public_reports_bucket" {
  description = "Name of the public reports bucket"
  value       = aws_s3_bucket.public_reports.id
}

output "confidential_finance_bucket" {
  description = "Name of the confidential finance bucket"
  value       = aws_s3_bucket.confidential_finance.id
}

output "customer_records_table" {
  description = "Name of the customer records DynamoDB table"
  value       = aws_dynamodb_table.customer_records.name
}

output "kms_key_arn" {
  description = "ARN of the main KMS encryption key"
  value       = aws_kms_key.main.arn
}
