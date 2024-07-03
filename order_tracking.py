import os
import json
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
orders_table_name = os.environ['ORDERS_TABLE_NAME']
orders_table = dynamodb.Table(orders_table_name)

def convert_decimal_to_float(data):
    if isinstance(data, Decimal):
        return float(data)
    elif isinstance(data, dict):
        return {key: convert_decimal_to_float(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_decimal_to_float(item) for item in data]
    return data

def track_order(event, context):
    try:
        # Extract Order ID from path parameters
        order_id = event['pathParameters']['orderID']
        
        # Fetch order details from DynamoDB
        response = orders_table.get_item(
            Key={'OrderId': order_id}
        )
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Order not found'})
            }

        order = response['Item']

        # Convert Decimal types to float
        order = convert_decimal_to_float(order)
        
        return {
            'statusCode': 200,
            'body': json.dumps(order)
        }

    except ClientError as e:
        print(f"ClientError: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)})
        }