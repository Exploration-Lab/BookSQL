
import pandas as pd
import time
import openai
import os
import sys


schema_prompt = ''' Database schema:
Table master_txn_table, columns = [*, Transaction_ID, Transaction_DATE, Transaction_TYPE, Amount, CreatedDATE, CreatedUSER, Account, AR_paid, AP_paid, Due_DATE, Open_balance, \
                            Customers, Vendor, Product_Service, Quantity, Rate, Credit, Debit, payment_method, Misc]
Table chart_of_accounts, columns = [*, Account_name, Account_type]
Table customers, columns = [*, customer_name, customer_full_name, Billing_address, Billing_city, Billing_state, Billing_ZIP_code, Shipping_address, Shipping_city, Shipping_state, Shipping_ZIP_code, Balance]
Table employees, columns = [*, Employee_name, Employee_ID, Hire_date, Billing_rate, Deleted]
Table products, columns = [*, Product_Service, Product_Service_type]
Table vendors, columns = [*, Vendor_name, Billing_address, Billing_city, Billing_state, Billing_ZIP_code, Balance]
Table payment_method, columns = [*, Payment_method, Credit_card]
Foreign_keys = [master_txn_table.Account = chart_of_accounts.Account_name, master_txn_table.Customers = customers.customer_name, master_txn_table.Vendor = vendors.Vendor_name, master_txn_table.Product_Service = products.Product_Service, master_txn_table.payment_method = payment_method.payment_method]
'''



DATASET = "./fold0/train.json"

df = pd.read_json(DATASET)

examples = []

for index, row in df.iterrows():
    if index % 10 != 0:
        continue
    examples.append({'input': row['question'], 'output': row['query']})



from langchain import FewShotPromptTemplate, PromptTemplate
from langchain.chains.sql_database.prompt import _sqlite_prompt #, PROMPT_SUFFIX
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.prompts.example_selector.semantic_similarity import SemanticSimilarityExampleSelector
from langchain.vectorstores import Chroma


from langchain.prompts.example_selector import MaxMarginalRelevanceExampleSelector
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import FewShotPromptTemplate, PromptTemplate

example_prompt = PromptTemplate(
    input_variables=["input", "output"],
    template="Input: {input}\nOutput: {output}",
)
MaxMarginalRelevanceExampleSelector
# examples = [
#     {"input": "How much open credit does customer Ronald Bailey have?", "output": "select sum(open_balance) from ( select distinct transaction_id, open_balance from master_txn_table where customers = 'Ronald Bailey')"},
#     {"input": "What are my transactions Last 7 days?", "output": "select distinct transaction_id, amount from master_txn_table where transaction_date BETWEEN date( current_date, '-7 days') AND date( current_date)"},
#     {"input": "How many Traveller accomodation did we sell to Ethan Walker today?", "output": "select sum(quantity) from master_txn_table where customers = 'Ethan Walker' and product_service = 'Traveller accomodation' and trasaction_type in ('invoice','sales receipt') and transaction_date BETWEEN date(current_date) AND date(current_date)"},
#     {"input": "How many invoices are still oustanding for Tony Arellano as of in q1 this year?", "output": "select count(distinct transaction_id) from master_txn_table where customers = 'Tony Arellano' and transaction_type = 'invoice' and open_balance >0 and transaction_date BETWEEN date(current_date, 'start of year') AND date(current_date, 'start of year', '+3 month', '-1 day') "},
    
# ]

example_selector = MaxMarginalRelevanceExampleSelector.from_examples(
    examples, 
    HuggingFaceEmbeddings(model_name="all-mpnet-base-v2-table"), 
    Chroma, 
    k=10
)
similar_prompt = FewShotPromptTemplate(
    # We provide an ExampleSelector instead of examples.
    example_selector=example_selector,
    example_prompt=example_prompt,
    prefix= schema_prompt + "\nFollowing are the example of questions and corresponding SQL queries.",
    suffix="Translate following question to SQL query. \n Input: {question}\nOutput: SELECT ", 
    input_variables=["question"],
)

print(similar_prompt.format(question="How much open credit does customer Ronald Bailey have?"))



DATASET_SCHEMA = "./booksql/booksqltables.json"
DATASET = "./booksql/test.json"
OUTPUT_DF = "predicted_booksql_gpt4_dynamic_few_shot_3_mod_200.csv"


val_df = pd.read_json(DATASET)
print(f"Number of data samples {val_df.shape[0]}")
CODEX = []

for index, row in val_df.iterrows():
    if (index % 200 != 3):
       continue
    
    print(f"index is {index}")
    print(row['query'])
    print(row['question'])

    SQL = None
    s = 10
    while SQL is None:
        try:
            print('generating SQL')
            prompt = similar_prompt.format(question=row['question'])
            #print('prompt=', prompt)
            SQL = GPT4_generation(prompt)
        except Exception as e:
            print(str(e))
            time.sleep(s)
            s = s + 10
            pass

    SQL = "SELECT " + SQL
    print(SQL)
    CODEX.append([row['question'], SQL, row['query']])
    #break
df = pd.DataFrame(CODEX, columns=['NLQ', 'PREDICTED SQL', 'GOLD SQL'])
df.to_csv(OUTPUT_DF, index=False)

