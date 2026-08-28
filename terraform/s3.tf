# ---------------------------------------------------------------------------------------------------------------------
# S3 BUCKET 1: PUBLIC / REGULAR REPORTS (Permitted for general AI agents)
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_s3_bucket" "public_reports" {
  bucket = "enterprise-public-reports-bucket"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "public_reports_sse" {
  bucket = aws_s3_bucket.public_reports.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.main.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_object" "sample_report" {
  bucket  = aws_s3_bucket.public_reports.id
  key     = "reports/q3_summary.txt"
  content = "Q3 Enterprise Operational Report: All systems nominal. Growth target at 14%."
}

# ---------------------------------------------------------------------------------------------------------------------
# S3 BUCKET 2: CONFIDENTIAL FINANCE DATA (Restricted - Denied for standard AI agents)
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_s3_bucket" "confidential_finance" {
  bucket = "enterprise-confidential-finance-bucket"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "confidential_finance_sse" {
  bucket = aws_s3_bucket.confidential_finance.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.main.arn
      sse_algorithm     = "aws:kms"
    }
  }
}

resource "aws_s3_object" "sensitive_ledger" {
  bucket  = aws_s3_bucket.confidential_finance.id
  key     = "finance/unreleased_earnings_2027.json"
  content = jsonencode({
    secret_revenue = "$450,000,000"
    insider_notes  = "Confidential merger data - strict authorization required"
  })
}
