output "lambda_function_name" {
  description = "Name of the deployed Lambda function"
  value       = aws_lambda_function.cost_guardian.function_name
}

output "lambda_function_arn" {
  description = "ARN of the deployed Lambda function"
  value       = aws_lambda_function.cost_guardian.arn
}

output "eventbridge_rule_arn" {
  description = "ARN of the EventBridge scheduled rule"
  value       = aws_cloudwatch_event_rule.weekly_trigger.arn
}