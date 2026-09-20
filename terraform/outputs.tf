output "rds_endpoint" {
  description = "Connection endpoint for the CloudGuard PostgreSQL database"
  value       = aws_db_instance.postgres.endpoint
}

output "security_audit_role_arn" {
  description = "IAM Role ARN for target accounts to delegate read-only audit access"
  value       = aws_iam_role.security_audit_role.arn
}

output "vpc_id" {
  description = "VPC ID where database and services reside"
  value       = aws_vpc.main.id
}
