variable "aws_region" {
  description = "AWS region for CloudGuard deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment name (e.g. production, staging)"
  type        = string
  default     = "production"
}

variable "db_username" {
  description = "PostgreSQL administrator username"
  type        = string
  default     = "cloudguard_admin"
}

variable "db_password" {
  description = "PostgreSQL administrator password"
  type        = string
  sensitive   = true
  default     = "ChangeMeStrongPassword123!"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "cloudguard"
}
