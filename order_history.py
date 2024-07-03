import os
import json
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal
import time


# Custom JSON Encoder to handle Decimal serialization
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            if o % 1 == 0:
                return int(o)
            else:
                return float(o)
        return super(DecimalEncoder, self).default(o)

dynamodb = boto3.resource('dynamodb')

# Table names
orders_table_name = os.environ['ORDERS_TABLE_NAME']
users_table_name = os.environ['USERS_TABLE_NAME']

# Tables
orders_table = dynamodb.Table(orders_table_name)
users_table = dynamodb.Table(users_table_name)

def get_order_history(event, context):
    try:
        # Get the user ID from the query string parameters
        user_id = event['queryStringParameters']['UserID']

        # Basic validation
        if not user_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required fields'})
            }

        # Validate user ID
        user_response = users_table.get_item(Key={'Email': user_id})
        if 'Item' not in user_response:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid UserId'})
            }

        # Retry logic for querying the GSI
        retries = 5
        while retries > 0:
            try:
                response = orders_table.query(
                    IndexName='UserId-index',
                    KeyConditionExpression=boto3.dynamodb.conditions.Key('UserId').eq(user_id)
                )
                orders = response.get('Items', [])

                # Serialize Decimal types using custom JSON encoder
                serialized_orders = json.dumps(orders, cls=DecimalEncoder)

                return {
                    'statusCode': 200,
                    'body': serialized_orders
                }
            except ClientError as e:
                if e.response['Error']['Code'] == 'ValidationException' and 'Cannot read from backfilling global secondary index' in e.response['Error']['Message']:
                    time.sleep(5)
                    retries -= 1
                else:
                    raise e

        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error', 'details': 'GSI is still backfilling'})
        }

    except ClientError as e:
        print(f"ClientError: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)})
        }