import os
import json
import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')

cart_table_name = os.environ['CART_TABLE_NAME']
users_table_name = os.environ['USERS_TABLE_NAME']
products_table_name = os.environ['PRODUCTS_TABLE_NAME']

cart_table = dynamodb.Table(cart_table_name)
users_table = dynamodb.Table(users_table_name)
products_table = dynamodb.Table(products_table_name)

def add_to_cart(event, context):
    try:
        # Parse request body
        body = json.loads(event['body'])
        user_id = body.get('UserId')
        product_id = body.get('ProductId')
        
        if not user_id or not product_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required fields'})
            }
        
        # Validate user
        user_response = users_table.get_item(Key={'Email': user_id})
        if 'Item' not in user_response:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid user ID'})
            }
        
        product_response = products_table.get_item(Key={'ProductId': product_id})
        if 'Item' not in product_response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Product not available'})
            }
        
        # Add item to the cart
        cart_table.update_item(
            Key={
                'UserId': user_id,
                'ProductId': product_id
            },
            UpdateExpression="set Quantity = if_not_exists(Quantity, :start) + :inc",
            ExpressionAttributeValues={
                ':start': 0,
                ':inc': 1
            },
            ReturnValues="UPDATED_NEW"
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Product added to cart successfully'})
        }
    
    except ClientError as e:
        print(f"ClientError: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)})
        }