import json
import os
import boto3
import logging
from boto3.dynamodb.conditions import Attr
from decimal import Decimal

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table_name = os.environ['PRODUCTS_TABLE_NAME']
table = dynamodb.Table(table_name)

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def search_products(event, context):
    logger.info("Received event: %s", json.dumps(event))

    query_params = event.get('queryStringParameters') or {}
    
    keywords = query_params.get('Keywords', '')
    category = query_params.get('Category')
    subcategory = query_params.get('Subcategory')
    min_price = query_params.get('MinPrice')
    max_price = query_params.get('MaxPrice')
    
    logger.info("Search parameters - Keywords: %s, Category: %s, Subcategory: %s, MinPrice: %s, MaxPrice: %s", 
                keywords, category, subcategory, min_price, max_price)
    
    filter_expression = Attr('Name').contains(keywords) | Attr('Description').contains(keywords)
    
    if category:
        filter_expression &= Attr('Category').eq(category)
    if subcategory:
        filter_expression &= Attr('Subcategory').eq(subcategory)
    if min_price:
        filter_expression &= Attr('Price').gte(float(min_price))
    if max_price:
        filter_expression &= Attr('Price').lte(float(max_price))
        
    
    response = table.scan(FilterExpression=filter_expression)
    products = response.get('Items', [])
    
    if products:
        message = "Yes, the product is available"
    else:
        message = "Not available right now, sorry"
    
    logger.info("Search results: %s", json.dumps(products, default=decimal_default))
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': message})
    }
