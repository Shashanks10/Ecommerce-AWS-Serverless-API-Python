# Serverless-Ecommerce-API-Python
An E-Commerce Api on AWS serverless using serverless framework
Here's a summary of all the APIs you've worked on, including their purposes and key features:
----------------------------------------------------------------------------------------------------------------------------
Register User API

Purpose: Register a new user by storing their details in DynamoDB.
HTTP Method: POST
Endpoint: /register
Request Body:json

{
  "Name": "string",
  "Email": "string",
  "Password": "string",
  "Shipping Address": "string"
}

Features:
Validates required fields.
Hashes the password.
Checks for duplicate names and emails.
Enforces password uniqueness and a maximum length of 10 characters.
Returns a success message or an error if validation fails.

------------------------------------------------------------------------------------------------------------------------------

Search Products API

Purpose: Search for products based on various criteria.
HTTP Method: GET
Endpoint: /search-products
Query Parameters:
Keywords: Search term for product name or description.
Category: Category of the product.
Subcategory: Subcategory of the product.
MinPrice: Minimum price of the product.
MaxPrice: Maximum price of the product.
Features:
Filters products based on the search criteria.
Returns a list of matching products or a message if no products are found.

--------------------------------------------------------------------------------------------------------
Add to Cart API
Purpose: Add a product to a user's cart.

HTTP Method: POST
Endpoint: /add-to-cart
Request Body: json

{
  "UserId": "string",
  "ProductId": "string"
}
Features:
Validates required fields.
Check's if the user ID exists in the USERS_TABLE_NAME.
Check's if the product ID exists in the PRODUCTS_TABLE_NAME.
Adds the product to the user's cart or increments the quantity if it already exists.
Returns a success message or an error if validation fails.

-----------------------------------------------------------------------------------------------------

Remove from Cart API
Purpose: Remove a product from a user's cart.

HTTP Method: POST
Endpoint: /remove-from-cart
Request Body:json

{
  "UserId": "string",
  "ProductId": "string"
}

Features:
Validates required fields.
Checks if the user ID exists in the USERS_TABLE_NAME.
Removes the specified product from the user's cart.
Returns a success message or an error if validation fails.

---------------------------------------------------------------------------------------------------------

Checkout API
Purpose: Process a user's cart and create an order.

HTTP Method: POST
Endpoint: /checkout
Request Body:json

{
  "UserId": "string",
  "ShippingAddress": "string",
  "PaymentMethod": "string",
  "CartItems": [{"ProductId": "string","Quantity": int}]
}
Features:
Validates required fields.
Checks if the user ID exists in the USERS_TABLE_NAME.
Checks if each product ID in the cart exists in the PRODUCTS_TABLE_NAME.
Validates the payment method.
Calculates the order total and creates a new order in the ORDERS_TABLE_NAME.
Clears the user's cart after checkout.
Returns a success message with the order ID or an error if validation fails.

-------------------------------------------------------------------------------------------------------------
Get Order History API

Purpose: Retrieve a user's order history.
HTTP Method: GET
Endpoint: /order-history
Query Parameters:
UserID: The user's ID.

Features:
Validates required fields.
Checks if the user ID exists in the USERS_TABLE_NAME.
Queries the ORDERS_TABLE_NAME for orders associated with the user ID.
Returns the user's order history or an error if validation fails.
Common Features Across APIs
Error Handling: Each API has robust error handling to manage client and server errors.
Validation: All APIs perform necessary validation to ensure that required fields are provided and correctly formatted.
Logging: APIs include logging for debugging and monitoring purposes.
CORS: All APIs include CORS headers to allow cross-origin requests from permitted domains.
These APIs collectively form a comprehensive system for user registration, product searching, cart management, order processing, and retrieving order histories, ensuring a seamless user experience.
