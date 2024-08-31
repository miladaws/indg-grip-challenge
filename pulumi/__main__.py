import pulumi
from pulumi_aws import iam, lambda_, sqs
import os

# Get the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Create an SQS queue
queue = sqs.Queue("indg-grip-sqs-queue")

# Create an IAM role for the Lambda function
lambda_role = iam.Role("indg-grip-lambda-role",
    assume_role_policy="""{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Action": "sts:AssumeRole",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Effect": "Allow",
                "Sid": ""
            }
        ]
    }"""
)

# Attach policies to the IAM role
lambda_role_policy = iam.RolePolicy("indg-grip-lambda-role-policy",
    role=lambda_role.id,
    policy="""{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "sqs:SendMessage"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "arn:aws:logs:*:*:*"
            }
        ]
    }"""
)

# Create the Lambda function
lambda_func = lambda_.Function("indg-grip-sqs-lambda",
    code=pulumi.AssetArchive({
        '.': pulumi.FileArchive(os.path.join(project_root, 'lambda', 'lambda_function.zip'))
    }),
    handler="lambda_function.lambda_handler",
    role=lambda_role.arn,
    runtime="python3.8",
    environment={
        "variables": {
            "SQS_QUEUE_URL": queue.url
        }
    }
)

# Export the queue URL and Lambda function name
pulumi.export('queue_url', queue.url)
pulumi.export('lambda_function_name', lambda_func.name)