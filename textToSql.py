from flask import Flask, jsonify, request
import vertexai
import random
from google.cloud import bigquery
from vertexai.language_models import TextGenerationModel, \
    CodeGenerationModel

apology_phrases = [
    "I sincerely apologize for any inconvenience caused by the unexpected interruption in our conversation.",
    "My deepest apologies for the sudden disruption in our chat. Please know that I'm here to assist you.",
    "I'm sorry for the technical hiccup earlier. Let's continue our conversation without any interruptions.",
    "Apologies for the brief interruption. I'm back and ready to help you with any questions you have.",
    "Sorry about the disruption. Let's pick up where we left off and get back on track.",
    "I regret the interruption in our chat. Let's move forward and address your queries.",
    "Please accept my apologies for the chat disruption. I'm at your service now.",
    "I apologize for any frustration caused by the interruption. How can I assist you further?",
    "My apologies for the unexpected pause in our conversation. Let's continue with our discussion.",
    "Sorry for the chat hiccup. I'm here to provide you with the information you need.",
    "I'm sorry our chat got momentarily derailed. Let's refocus on your questions.",
    "Apologies for the technical blip. Let's carry on with our conversation without any issues.",
    "Sorry for any confusion the interruption might have caused. How can I make it up to you?",
    "I regret any inconvenience caused by the disruption. Let's get back on track.",
    "Please accept my apologies for the chat interruption. Your satisfaction is my priority.",
    "I'm sorry the chat hit a bump. Let's continue smoothly from here on out.",
    "Apologies for the unexpected pause. Let's proceed with our discussion seamlessly.",
    "Sorry for the momentary disruption. Let's make our conversation productive.",
    "I apologize for any disturbance you experienced. Let's continue with our interaction.",
    "My sincerest apologies for the chat interruption. Your understanding is greatly appreciated."
]

app = Flask(__name__)

dataset_id = "folio3bigaihackathon"
PROJECT_ID = "merchant-assistant-395407"
vertexai.init(project=PROJECT_ID, location="us-central1")
client = bigquery.Client(project=PROJECT_ID)


def run_select_query(sql_statement):
    client = bigquery.Client()
    query_job = client.query(sql_statement)
    query_results = query_job.result()
    return query_results.to_dataframe()


vertexai.init(project=PROJECT_ID, location="us-central1")

TABLE_SCHEMA_STR = f'''
[SCHEMA details for table `{PROJECT_ID}.{dataset_id}.bc_customer`]:
Full table name: {PROJECT_ID}.{dataset_id}.bc_customer - Column: customer_id - Data Type: INT64 - Primary Key: False - Foreign Key: True - Description: The unique identifier for each customer.
Full table name: {PROJECT_ID}.{dataset_id}.bc_customer - Column: full_name - Data Type: STRING - Primary Key: False - Foreign Key: False - Description: The full name of the customer.
Full table name: {PROJECT_ID}.{dataset_id}.bc_customer - Column: first_name - Data Type: STRING - Primary Key: False - Foreign Key: False - Description: The first name of the customer.
Full table name: {PROJECT_ID}.{dataset_id}.bc_customer - Column: email - Data Type: STRING - Primary Key: False - Foreign Key: False - Description: The email address of the customer.
Full table name: {PROJECT_ID}.{dataset_id}.bc_customer - Column: date_created - Data Type: DATETIME - Primary Key: False - Foreign Key: False - Description: The date and time when the customer record was created.
Full table name: {PROJECT_ID}.{dataset_id}.bc_customer - Column: date_modified - Data Type: DATETIME - Primary Key: False - Foreign Key: False - Description: The date and time when the customer record was last modified.
Full table name: {PROJECT_ID}.{dataset_id}.bc_customer - Column: last_updated_datetime - Data Type: DATETIME - Primary Key: False - Foreign Key: False - Description: The date and time when the customer record was last updated.
[SCHEMA details for table `{PROJECT_ID}.{dataset_id}.bc_order`]:
Full table name: `{PROJECT_ID}.{dataset_id}.bc_order` - Column: order_id - Data Type: INTEGER - Primary Key: False - Foreign Key: True - Description: The unique identifier for the order.
Full table name: `{PROJECT_ID}.{dataset_id}.bc_order` - Column: order_status - Data Type: STRING - Primary Key: False - Foreign Key: False - Description: The textual representation of the order status.
Full table name: `{PROJECT_ID}.{dataset_id}.bc_order` - Column: order_created_date_time - Data Type: DATETIME - Primary Key: False - Foreign Key: False - Description: The date and time when the order was created.
Full table name: `{PROJECT_ID}.{dataset_id}.bc_order` - Column: date_shipped - Data Type: DATETIME - Primary Key: False - Foreign Key: False - Description: The date and time when the order was shipped.
Full table name: `{PROJECT_ID}.{dataset_id}.bc_order` - Column: customer_id - Data Type: INTEGER - Primary Key: False - Foreign Key: True - Description: The identifier for the customer who placed the order.
Full table name: `{PROJECT_ID}.{dataset_id}.bc_order` - Column: payment_status - Data Type: STRING - Primary Key: False - Foreign Key: False - Description: The status of the payment for the order.
Full table name: `{PROJECT_ID}.{dataset_id}.bc_order` - Column: total_items - Data Type: INTEGER - Primary Key: False - Foreign Key: False - Description: The total number of items in the order.
Full table name: `{PROJECT_ID}.{dataset_id}.bc_order` - Column: total_items_shipped - Data Type: INTEGER - Primary Key: False - Foreign Key: False - Description: The total number of items that have been shipped.
Full table name: `{PROJECT_ID}.{dataset_id}.bc_order` - Column: sub_total_including_tax - Data Type: NUMERIC - Primary Key: False - Foreign Key: False - Description: The subtotal of the order including taxes.
Full table name: `{PROJECT_ID}.{dataset_id}.bc_order` - Column: sub_total_tax - Data Type: NUMERIC - Primary Key: False - Foreign Key: False - Description: The tax amount included in the subtotal.
Full table name: `{PROJECT_ID}.{dataset_id}.bc_order` - Column: total_excluding_tax - Data Type: NUMERIC - Primary Key: False - Foreign Key: False - Description: The total order amount excluding taxes.
Full table name: `{PROJECT_ID}.{dataset_id}.bc_order` - Column: total_including_tax - Data Type: NUMERIC - Primary Key: False - Foreign Key: False - Description: The total order amount including taxes.
Full table name: `{PROJECT_ID}.{dataset_id}.bc_order` - Column: last_updated_datetime - Data Type: DATETIME - Primary Key: False - Foreign Key: False - Description: The date and time when the order was last updated.
[SCHEMA details for table `{PROJECT_ID}.{dataset_id}.bc_product`]:
Full table name: `{PROJECT_ID}.{dataset_id}.bc_product` - Column: product_id - Data Type: INTEGER - Primary Key: False - Foreign Key: True - Description: The unique identifier of the product. 
Full table name: `{PROJECT_ID}.{dataset_id}.bc_product` - Column: product_name - Data Type: STRING - Primary Key: False - Foreign Key: False - Description: The name of the product. 
Full table name: `{PROJECT_ID}.{dataset_id}.bc_product` - Column: product_type - Data Type: STRING - Primary Key: False - Foreign Key: False - Description: The type of the product (e.g., physical, digital). 
Full table name: `{PROJECT_ID}.{dataset_id}.bc_product` - Column: date_created - Data Type: DATETIME - Primary Key: False - Foreign Key: False - Description: The date and time when the product was created. 
Full table name: `{PROJECT_ID}.{dataset_id}.bc_product` - Column: date_modified - Data Type: DATETIME - Primary Key: False - Foreign Key: False - Description: The date and time when the product was last modified.  
Full table name: `{PROJECT_ID}.{dataset_id}.bc_product` - Column: price - Data Type: NUMERIC - Primary Key: False - Foreign Key: False - Description: The price of the product. 
Full table name: `{PROJECT_ID}.{dataset_id}.bc_product` - Column: cost_price - Data Type: NUMERIC - Primary Key: False - Foreign Key: False - Description: The cost price of the product. 
Full table name: `{PROJECT_ID}.{dataset_id}.bc_product` - Column: retail_price - Data Type: NUMERIC - Primary Key: False - Foreign Key: False - Description: The retail price of the product.  
Full table name: `{PROJECT_ID}.{dataset_id}.bc_product` - Column: last_updated_datetime - Data Type: DATETIME - Primary Key: False - Foreign Key: False - Description: The date and time when the product information was last updated.
'''

QUESTION = '[Q]: Give me last customer with date and name'

examples = [
    {
        "Question": "[Q]: List Customers Who Placed more than 5 Orders?",
        "SQL": f'''[SQL]: SELECT c.full_name, COUNT(o.order_id) AS order_count
                       FROM `{PROJECT_ID}.{dataset_id}.bc_customer` c
                       INNER JOIN `{PROJECT_ID}.{dataset_id}.bc_order` o ON c.customer_id = o.customer_id
                       GROUP BY c.full_name
                       HAVING order_count > 5
      '''
    }]


def getExamples():
    r = ''
    for example in examples[:2]:
        r = '\r\n'.join(
            [r, 'Here is an example of user question and answer SQL.', TABLE_SCHEMA_STR, example['Question'],
             example['SQL']])
    # print(r)
    return r


def getQuestion(q):
    return "\r\n".join(['Here is an example of user question and answer SQL.', TABLE_SCHEMA_STR, q])


parameters = {
    "temperature": 0.2,
    "max_output_tokens": 1024
}


def handleQuestions(q):
    prefix = '\r\n'.join([
        'You are a SQL expert. Please convert text into GoogleSQL statement. We will first give the dataset schema and then ask a question in text. You are asked to generate SQL statement.',
        getExamples(), getQuestion(q)])
    generation_model = CodeGenerationModel.from_pretrained("code-bison@001")
    response = generation_model.predict(prefix=prefix, **parameters)
    generated_sql = response.text.replace("[SQL]: ", "")
    print("Auto Generated SQL is :\r\n")
    print(generated_sql)
    return run_select_query(generated_sql)


handleQuestions(QUESTION)

def handleSqlToNLP(gQueryStatement, userInput):
    json_data = gQueryStatement.to_json(orient="records", indent=4)
    parameters = {
        "temperature": 0.2,
        "max_output_tokens": 256,
        "top_p": 0.8,
        "top_k": 40
    }
    model = TextGenerationModel.from_pretrained("text-bison@001")
    response = model.predict(
        f"""This is the user query : {userInput}
        and here is json response from my database:
        {json_data}
        Generate a description for the following in the natural language
        """,
        **parameters
    )
    print(response.text)
    return response.text


@app.route('/api/bigquery', methods=['GET'])
def hello_world():
    query = request.args.get('query')
    res = 'Please enter your query'
    if query:
        try:
            query = f'[Q]: {query}'
            googleSQLQuery = handleQuestions(query)
            res = handleSqlToNLP(googleSQLQuery, query)
        except Exception as e:
            res = random.choice(apology_phrases)

        return jsonify({"response": res})
    else:
        return jsonify({"response": res})


if __name__ == '__main__':
    app.run()
