variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "ap-southeast-2"
}

variable "project_name" {
  description = "Project name used for naming AWS resources"
  type        = string
  default     = "aws-cost-guardian"
}

variable "slack_webhook_url" {
  description = "Slack Incoming Webhook URL for notifications"
  type        = string
  sensitive   = true
}
