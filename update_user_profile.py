import os
import json
import boto3
from botocore.exceptions import ClientError


dynamodb = boto3.resource('dynamodb')
users_table_name = os.environ['USERS_TABLE_NAME']
users_table = dynamodb.Table(users_table_name)

def update_user_profile(event, context):
    try:
        # Parse request body
        body = json.loads(event['body'])
        user_id = body.get('UserID')
        updated_name = body.get('UpdatedName')
        updated_email = body.get('UpdatedEmail')  # This can be optional
        updated_shipping_address = body.get('UpdatedShippingAddress')

        # Basic validation
        if not user_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'UserID is required'})
            }

        # Prepare update expressions and attribute values
        update_expression_parts = []
        expression_attribute_values = {}
        expression_attribute_names = {}

        if updated_name:
            update_expression_parts.append('set #name = :name')
            expression_attribute_values[':name'] = updated_name
            expression_attribute_names['#name'] = 'Name'
        if updated_email:
            update_expression_parts.append('set #email = :email')
            expression_attribute_values[':email'] = updated_email
            expression_attribute_names['#email'] = 'Email'
        if updated_shipping_address:
            update_expression_parts.append('#shipping_address = :shipping_address')
            expression_attribute_values[':shipping_address'] = updated_shipping_address
            expression_attribute_names['#shipping_address'] = 'ShippingAddress'

        # Join update expressions
        update_expression = ', '.join(update_expression_parts)

        # Construct update parameters
        update_params = {
            'Key': {'Email': user_id},
            'UpdateExpression': update_expression,
            'ExpressionAttributeValues': expression_attribute_values,
            'ExpressionAttributeNames': expression_attribute_names,
            'ReturnValues': 'ALL_NEW'  # Return updated item attributes
        }

        # Update item in DynamoDB
        response = users_table.update_item(**update_params)

        # Return updated profile
        updated_profile = response.get('Attributes', {})

        return {
            'statusCode': 200,
            'body': json.dumps(updated_profile)
        }

    except ClientError as e:
        print(f"ClientError: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error', 'details': str(e)})
        }
