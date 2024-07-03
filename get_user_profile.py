import os
import json
import boto3
from botocore.exceptions import ClientError


dynamodb = boto3.resource('dynamodb')
users_table_name = os.environ['USERS_TABLE_NAME']
users_table = dynamodb.Table(users_table_name)

def get_user_profile(event, context):
    try:
        # Extract user's email from query parameters
        email = event['queryStringParameters']['email']
        
        # Fetch user profile from DynamoDB
        response = users_table.get_item(
            Key={'Email': email}
        )
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'User profile not found'})
            }

        user_profile = response['Item']
        
        return {
            'statusCode': 200,
            'body': json.dumps(user_profile)
        }

    except ClientError as e:
        print(f"ClientError: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)})
        }
