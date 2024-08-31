import json
import os
import boto3

# Create an SQS client using Boto3
sqs = boto3.client('sqs')

# Retrieve the SQS queue URL from environment variables
SQS_QUEUE_URL = os.environ['SQS_QUEUE_URL']

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])

        # Extract 'reply_to' and 'inputs' from the parsed body
        reply_to = body['reply_to']
        inputs = body['inputs']
        
        # Check if the 'inputs' contains a 'type' key with the value 'name'
        if 'type' in inputs and inputs['type'] == 'name':
            payload = {
                "set": {
                    "name": inputs['value']
                }
            }
        else:
            # Return a 400 error response if the input type is invalid
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid input type'})
            }
        
        # Send the payload to the SQS queue
        response = sqs.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps(payload)
        )
        
        # Return a 200 response with the SQS message ID
        return {
            'statusCode': 200,
            'body': json.dumps({'message_id': response['MessageId']})
        }
        
    except KeyError as e:
        # Return a 400 error response if a required field is missing
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Missing required field: {str(e)}'})
        }
    except Exception as e:
        # Return a 500 error response for any other exceptions
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }