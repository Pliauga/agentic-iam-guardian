# ---------------------------------------------------------------------------------------------------------------------
# DYNAMODB: CUSTOMER RECORDS (High Value Target)
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_dynamodb_table" "customer_records" {
  name           = "CustomerRecordsTable"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "CustomerId"

  attribute {
    name = "CustomerId"
    type = "S"
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.main.arn
  }

  tags = {
    DataClassification = "Restricted-PII"
  }
}

resource "aws_dynamodb_table_item" "sample_customer" {
  table_name = aws_dynamodb_table.customer_records.name
  hash_key   = aws_dynamodb_table.customer_records.hash_key

  item = jsonencode({
    CustomerId = { S = "CUST-9901" }
    Name       = { S = "Jane Doe" }
    Email      = { S = "jane.doe@example.com" }
    Balance    = { N = "150000" }
  })
}
