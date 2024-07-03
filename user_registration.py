import os
import json
import boto3
from botocore.exceptions import ClientError
import hashlib
import uuid
import re

dynamodb = boto3.resource('dynamodb')
table_name = os.environ['USERS_TABLE_NAME']
table = dynamodb.Table(table_name)

def register(event, context):
    try:
        # Parse request body
        body = json.loads(event['body'])
        name = body.get('Name')
        email = body.get('Email')
        password = body.get('Password')
        shipping_address = body.get('Shipping Address')

        # Basic validation
        if not all([name, email, password, shipping_address]):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required fields'})
            }

        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid email format'})
            }

        if len(password) > 10:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Password exceeds maximum length of 10 characters'})
            }

        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        response = table.get_item(Key={'Email': email})
        if 'Item' in response:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Email already exists'})
            }

        scan_response = table.scan(
            FilterExpression='#name = :name',
            ExpressionAttributeNames={'#name': 'Name'},
            ExpressionAttributeValues={':name': name}
        )
        if scan_response['Count'] > 0:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Name already exists'})
            }

        scan_response = table.scan(
            FilterExpression='#password = :password',
            ExpressionAttributeNames={'#password': 'Password'},
            ExpressionAttributeValues={':password': hashed_password}
        )
        if scan_response['Count'] > 0:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Password already used'})
            }

        # Generate a unique user ID
        user_id = str(uuid.uuid4())

        table.put_item(
            Item={
                'UserID': user_id,
                'Email': email,
                'Name': name,
                'Password': hashed_password,
                'ShippingAddress': shipping_address
            }
        )

        return {
            'statusCode': 201,
            'body': json.dumps({'message': 'User registered successfully', 'user_id': user_id})
        }

    except ClientError as e:
        print(f"ClientError: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)})
        }