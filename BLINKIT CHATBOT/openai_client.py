import os
from openai import OpenAI
import json

token = os.getenv("GITHUB_TOKEN")
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o"

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

def generate_sql(user_query):
    
    messages = [
        {
            "role": "system",
            "content": """

      You are an SQL Query Generator for a SQL Server database. Your task is to convert natural language requests into optimized SQL queries while following these rules:

        1. Only return the SQL query as plain text without any description, comments, code blocks, or extra characters.
        2. No use of Markdown or enclosing query in ```sql or ``` blocks.
        3. Generate the query in a single line or properly formatted with minimal whitespace.
        4. Ensure the query uses valid SQL syntax that can be executed directly in SQL Server.
        5.Dont use any /n in the code.

        Use correct table names, column names, and relationships.
        Optimize queries by selecting only necessary columns and avoiding unnecessary joins.
        Apply filters (WHERE, GROUP BY, ORDER BY) where applicable.
        Ensure queries run efficiently and return accurate results.
        If a request is unclear, ask clarifying questions instead of making assumptions.
        Database Schema with Relationships & Column Descriptions
        Each table has Primary Keys (PK), Foreign Keys (FK), and column descriptions for better understanding. Some tables are standalone and do not have relationships with others.

        1. [dbo].[blinkit_orders]
        Primary Key: [order_id]
        Foreign Keys:
        [customer_id] → [dbo].[blinkit_customers].[customer_id]
        [delivery_partner_id] → [dbo].[blinkit_delivery_performance].[delivery_partner_id]
        Columns:
        [order_id] - Unique order ID
        [customer_id] - ID of the customer placing the order
        [order_date] - Date of order placement
        [promised_delivery_time] - Estimated delivery time
        [actual_delivery_time] - Actual time of delivery
        [delivery_status] - Status (Delivered, Pending, etc.)
        [order_total] - Total order amount
        [payment_method] - Mode of payment (Credit Card, UPI, etc.)
        [delivery_partner_id] - ID of delivery personnel
        [store_id] - ID of the store fulfilling the order
        2. [dbo].[blinkit_customers]
        Primary Key: [customer_id]
        Columns:
        [customer_id] - Unique customer ID
        [customer_name] - Customer’s full name
        [email] - Email address
        [phone] - Contact number
        [address] - Complete address
        [area] - Area or locality
        [pincode] - Postal code
        [registration_date] - Date of registration
        [customer_segment] - Customer category (e.g., Frequent, New)
        [total_orders] - Number of orders placed
        [avg_order_value] - Average spending per order
        3. [dbo].[blinkit_order_items]
        Primary Key: [order_id], [product_id]
        Foreign Keys:
        [order_id] → [dbo].[blinkit_orders].[order_id]
        [product_id] → [dbo].[blinkit_products].[product_id]
        Columns:
        [order_id] - Related order ID
        [product_id] - Related product ID
        [quantity] - Number of units ordered
        [unit_price] - Price per unit
        [total_price] - Total cost of the item
        4. [dbo].[blinkit_products]
        Primary Key: [product_id]
        Columns:
        [product_id] - Unique product ID
        [product_name] - Name of the product
        [category] - Product category (e.g., Dairy, Snacks)
        [brand] - Brand of the product
        [price] - Selling price
        [mrp] - Maximum retail price
        [margin_percentage] - Profit margin percentage
        [shelf_life_days] - Product shelf life in days
        [min_stock_level] - Minimum stock required
        [max_stock_level] - Maximum stock level
        5. [dbo].[blinkit_customer_feedback]
        Primary Key: [feedback_id]
        Foreign Keys:
        [order_id] → [dbo].[blinkit_orders].[order_id]
        [customer_id] → [dbo].[blinkit_customers].[customer_id]
        Columns:
        [feedback_id] - Unique feedback ID
        [order_id] - Order related to the feedback
        [customer_id] - Customer providing the feedback
        [rating] - Star rating (1-5)
        [feedback_text] - Textual feedback
        [feedback_category] - Type of feedback (e.g., Delivery, Product)
        [sentiment] - Sentiment (Positive, Neutral, Negative)
        [feedback_date] - Date of feedback submission
        [numeric_rating] - Numeric rating value
        Standalone Tables (No Direct Relationships)
        6. [dbo].[blinkit_grocery_data]
        Primary Key: [Item_Identifier]
        Columns:
        [Item_Identifier] - Unique item identifier
        [Item_Fat_Content] - Fat content of the product
        [Item_Type] - Type of grocery item
        [Outlet_Establishment_Year] - Year the outlet was established
        [Outlet_Identifier] - Store ID
        [Outlet_Location_Type] - Store location type
        [Outlet_Size] - Store size category
        [Outlet_Type] - Type of outlet (e.g., Supermarket, Grocery Store)
        [Item_Visibility] - How visible the item is in-store
        [Item_Weight] - Weight of the item
        [Sales] - Sales revenue for the item
        [Rating] - Customer rating for the item
        7. [dbo].[blinkit_inventory]
        Primary Key: [product_id], [date]
        Columns:
        [product_id] - Product in inventory
        [date] - Stock update date
        [stock_received] - Quantity received
        [damaged_stock] - Damaged quantity
        8. [dbo].[blinkit_marketing_performance]
        Primary Key: [campaign_id]
        Columns:
        [campaign_id] - Unique campaign ID
        [campaign_name] - Name of the marketing campaign
        [date] - Campaign date
        [target_audience] - Target group
        [channel] - Advertisement channel (e.g., Facebook, Google)
        [impressions] - Ad views count
        [clicks] - Number of clicks received
        [conversions] - Number of successful purchases
        [spend] - Total amount spent
        [revenue_generated] - Revenue earned
        [roas] - Return on Ad Spend
""",        
            },
            {
                "role": "user",
                "content": user_query
            },
        ]

    completion = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.7,  
        max_tokens=500,   
        top_p=1.0,
    )

    sql_query = completion.choices[0].message.content
    return sql_query

def generate_user_response(result):
    if not result:
        return "No relevant data found."

    result_str = json.dumps(result, indent=2)

    messages = [
        {
            "role": "system",
            "content": """
                You are an AI assistant that converts SQL query results into **clear, human-readable summaries**.

                **Your Task:**
                - 🚫 **DO NOT return raw JSON or list data directly.**
                - ✅ **Summarize insights clearly and naturally.**
                - ✅ **Explain patterns, trends, or key takeaways.**
                - ✅ **Use a professional but friendly tone.**

                **Example SQL JSON Result:**
                ```json
                [
                    {"product_name": "Laptop", "total_quantity_sold": 500},
                    {"product_name": "Smartphone", "total_quantity_sold": 450}
                ]
                ```

                **Correct Human-Like Summary:**
                "Laptops were the top-selling item with 500 units sold, followed closely by smartphones with 450 units."

                **❌ Incorrect Response:**
                ```json
                [
                    {"product_name": "Laptop", "total_quantity_sold": 500},
                    {"product_name": "Smartphone", "total_quantity_sold": 450}
                ]
                ```

                **Do NOT return JSON. Only generate a natural summary.**
            """        
        },
        {
            "role": "user",
            "content": f"""Here is a SQL query result:\n\n{result_str}\n\n
            Please summarize this **in a natural way**, providing key insights, without returning JSON."""
        },
    ]

    completion = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.5,
        max_tokens=1000,
        top_p=1.0,
    )

    response = completion.choices[0].message.content
    print("\n🔹 **Generated Human Response:**\n", response)

    return response


