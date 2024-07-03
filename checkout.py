import os
import json
import boto3
from botocore.exceptions import ClientError
import uuid
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')

# Table names
orders_table_name = os.environ['ORDERS_TABLE_NAME']
cart_table_name = os.environ['CART_TABLE_NAME']
users_table_name = os.environ['USERS_TABLE_NAME']
products_table_name = os.environ['PRODUCTS_TABLE_NAME']

# Accepted payment methods
accepted_payment_methods = ['Credit Card', 'Debit Card', 'COD']

# Tables
orders_table = dynamodb.Table(orders_table_name)
cart_table = dynamodb.Table(cart_table_name)
users_table = dynamodb.Table(users_table_name)
products_table = dynamodb.Table(products_table_name)

def checkout(event, context):
    try:
        # Parse request body
        body = json.loads(event['body'])
        user_id = body.get('UserId')
        shipping_address = body.get('ShippingAddress')
        payment_method = body.get('PaymentMethod')
        cart_items = body.get('CartItems')
        
        # Basic validation
        if not user_id or not shipping_address or not payment_method or not cart_items:
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
        
        # Validate payment method
        if payment_method not in accepted_payment_methods:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid payment method'})
            }
        
        # Validate product in cart_items
        for item in cart_items:
            product_id = item.get('ProductId')
            product_response = products_table.get_item(Key={'ProductId': product_id})
            if 'Item' not in product_response:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': f'Product with ID {product_id} not available'})
                }
        
        # Calculate order total
        order_total = sum(Decimal(item['Quantity']) * get_product_price(item['ProductId']) for item in cart_items)
        
        # Create order
        order_id = str(uuid.uuid4())
        order = {
            'OrderId': order_id,
            'UserId': user_id,
            'ShippingAddress': shipping_address,
            'PaymentMethod': payment_method,
            'OrderItems': cart_items,
            'OrderTotal': order_total
        }
        
        # Save order to DynamoDB
        orders_table.put_item(Item=order)
        
        # Clear user's cart
        for item in cart_items:
            cart_table.delete_item(
                Key={
                    'UserId': user_id,
                    'ProductId': item['ProductId']
                }
            )
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Checkout successful', 'OrderId': order_id})
        }
    
    except ClientError as e:
        print(f"ClientError: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)})
        }

def get_product_price(product_id):
    return Decimal('20.0')