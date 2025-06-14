# General
Ensure code maintainability and extendability.

# Security
Solutions should be secure by default, keeping in mind OWASP Top 10 security guidelines.
Never put credentials such as API keys and secrets in code. Instead, use environment variables or, in the case of AWS deployments, use the AWS Parameter Store and Secrets Manager.

# Code repositories & libraries
Use permissive licensed code where possible. Avoid AGPL and SSPL licensed code.

# AWS
## Credentials
Unless otherwise stated, assume AWS credentials are configured locally in `~/.aws/credentials` and `~/.aws/config`, or that the code runs on AWS compute with appropriate role permissions.
