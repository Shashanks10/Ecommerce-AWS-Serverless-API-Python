import os
import json
import boto3
from botocore.exceptions import ClientError


dynamodb = boto3.resource('dynamodb')

# Table names
cart_table_name = os.environ['CART_TABLE_NAME']
users_table_name = os.environ['USERS_TABLE_NAME']
products_table_name = os.environ['PRODUCTS_TABLE_NAME']

# Tables
cart_table = dynamodb.Table(cart_table_name)
users_table = dynamodb.Table(users_table_name)
products_table = dynamodb.Table(products_table_name)

def remove_from_cart(event, context):
    try:
        print("Event:", event)  # Debug log

        # Parse request body
        if 'body' in event and event['body']:
            body = json.loads(event['body'])
            print("Parsed body:", body)  # Debug log
            user_id = body.get('UserId')
            product_id = body.get('ProductId')
        else:
            print("No body found in the request")  # Debug log
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing request body'})
            }

        # Basic validation
        if not user_id or not product_id:
            print("Missing required fields: UserId or ProductId")  # Debug log
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required fields'})
            }

        # Validate user ID
        user_response = users_table.get_item(Key={'Email': user_id})
        if 'Item' not in user_response:
            print("Invalid user ID")  # Debug log
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid user ID'})
            }

        # Validate product ID
        product_response = products_table.get_item(Key={'ProductId': product_id})
        if 'Item' not in product_response:
            print("Item not available")  # Debug log
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Item not available'})
            }

        # Remove item from cart
        try:
            response = cart_table.delete_item(
                Key={
                    'UserId': user_id,
                    'ProductId': product_id
                }
            )
            print("DeleteItem response:", response)  # Debug log

            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Product removed from cart successfully'})
            }

        except ClientError as e:
            print(f"ClientError: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Internal server error', 'details': str(e)})
            }

    except Exception as e:
        print(f"Exception: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)})
        }
