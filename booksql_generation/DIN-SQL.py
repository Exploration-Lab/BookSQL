import pandas as pd
import time
import openai
import os
import sys



#----------------------------------------------------prompts-----------------------------------------------
schema_linking_prompt = '''Table master_txn_table, columns = [*, Transaction_ID, Transaction_DATE, Transaction_TYPE, Amount, CreatedDATE, CreatedUSER, Account, AR_paid, AP_paid, Due_DATE, Open_balance, \
                            Customers, Vendor, Product_Service, Quantity, Rate, Credit, Debit, payment_method, Misc]
Table chart_of_accounts, columns = [*, Account_name, Account_type]
Table customers, columns = [*, customer_name, customer_full_name, Billing_address, Billing_city, Billing_state, Billing_ZIP_code, Shipping_address, Shipping_city, Shipping_state, Shipping_ZIP_code, Balance]
Table employees, columns = [*, Employee_name, Employee_ID, Hire_date, Billing_rate, Deleted]
Table products, columns = [*, Product_Service, Product_Service_type]
Table vendors, columns = [*, Vendor_name, Billing_address, Billing_city, Billing_state, Billing_ZIP_code, Balance]
Table payment_method, columns = [*, Payment_method, Credit_card]
Foreign_keys = [master_txn_table.Account = chart_of_accounts.Account_name,master_txn_table.Customers = customers.customer_name,master_txn_table.Vendor = vendors.Vendor_name,master_txn_table.Product_Service = products.Product_Service,master_txn_table.payment_method = payment_method.payment_method]
Q: How much open credit does customer Felicia King have?
S: select sum(open_balance) from ( select distinct transaction_id, open_balance from master_txn_table where customers = 'Felicia King')
A: Let’s think step by step. In the question "How much open credit does customer Felicia King?", we are asked:
    "How much open credit", so we need column = [master_txn_table.open_balance]
    "open credit does customer Felicia King", so we need column = [master_txn_table.transaction_id,master_txn_table.customers]
    Based on the columns and tables, we need these Foreign_keys = [].
    Based on the tables, columns, and Foreign_keys, The set of possible cell values are = [Felicia King]. So the Schema_links are:
    Schema_links: [master_txn_table.open_balance,master_txn_table.customers,master_txn_table.transaction_id,Felicia King]

Q: Last 7 days, how much has Katie White paid us?
S: select sum(amount) from (select distinct transaction_id, amount from master_txn_table  where customers = 'Katie White' and transaction_type = 'payment' and transaction_date BETWEEN date( current_date, '-7 days') AND date( current_date)  )
A: Let’s think step by step. In the question "Last 7 days, how much has Katie White paid us?", we are asked: 
    "paid us", so we need column = [master_txn_table.transaction_type]
    "Katie White", so we need column = [master_txn_table.customers]
    "Last 7 days", so we need column = [master_txn_table.transaction_date]
    Based on the columns and tables, we need these Foreign_keys = [].
    Based on the tables, columns, and Foreign_keys, The set of possible cell values are = [Last 7 days]. So the Schema_links are:
    Schema_links: [master_txn_table.transaction_type,master_txn_table.customers,master_txn_table.transaction_date,current_date]

Q: How many Traveller accomodation did we sell to Eric Quinn Last 7 days?
S: select sum(quantity) from master_txn_table where customers = 'Eric Quinn' and product_service = 'Traveller accomodation' and transaction_type in ('invoice', 'sales receipt') and transaction_date BETWEEN date( current_date, '-7 days') AND date( current_date)
A: Let’s think step by step. In the question "How many Traveller accomodation did we sell to Eric Quinn Last 7 days?", we are asked: 
    "How many Traveller accomodation", so we need column = [master_txn_table.product_service,master_txn_table.quantity]
    "did we sell", so we need column = [master_txn_table.transaction_type]
    "Last 7 days", so we need column = [master_txn_table.transaction_date]
    Based on the columns and tables, we need these Foreign_keys = [].
    Based on the tables, columns, and Foreign_keys, The set of possible cell values are = [Eric Quinn,Last 7 days]. So the Schema_links are:
    Schema_links: [master_txn_table.quantity,master_txn_table.customers,master_txn_table.product_service,master_txn_table.trasaction_type,master_txn_table.transaction_date,current_date]

Q: Number of invoices created for Uncategorized Income in in q1 this year?
S: select count(distinct transaction_id) from master_txn_table where transaction_type = 'invoice' and instr(account,\"Uncategorized Income\") and transaction_date BETWEEN date(current_date, 'start of year') AND date(current_date, 'start of year', '+3 month', '-1 day')
A: Let’s think step by step. In the question "Number of invoices created for Uncategorized Income in in q1 this year?", we are asked: 
    "Number of invoices", so we need column = [master_txn_table.transaction_id]
    "Uncategorized Income", so we need column = [master_txn_table.account]
    "q1 this year", so we need column = [master_txn_table.transaction_date]
    Based on the columns and tables, we need these Foreign_keys = [].
    Based on the tables, columns, and Foreign_keys, The set of possible cell values are = [Uncategorized Income,invoice]. So the Schema_links are:
    Schema_links: [master_txn_table.transaction_id,master_txn_table.accounts,master_txn_table.trasaction_type,master_txn_table.transaction_date,current_date]

Q: What payment method was used to pay sales receipt #85820
S: select distinct payment_method from master_txn_table where transaction_type = 'sales receipt' and transaction_id = 85820
A: Let’s think step by step. In the question "What payment method was used to pay sales receipt #85820", we are asked: 
    "What payment method", so we need column = [master_txn_table.payment_method]
    "to pay sales", so we need column = [master_txn_table.transaction_type]
    "receipt #85820", so we need column = [master_txn_table.transaction_id]
    Based on the columns and tables, we need these Foreign_keys = [].
    Based on the tables, columns, and Foreign_keys, The set of possible cell values are = [85820]. So the Schema_links are:
    Schema_links: [master_txn_table.transaction_id,master_txn_table.trasaction_type]

Q: Since Last 12 months, how much has Catherine Deleon paid us?
S: select sum(amount) from (select distinct transaction_id, amount from master_txn_table  where customers = 'Catherine Deleon' and transaction_type = 'payment' and transaction_date BETWEEN date( current_date, \"-12 months\", \"start of month\") AND date( current_date, 'start of month', '-1 day')  )
A:  Let’s think step by step. In the question "Since Last 12 months, how much has Catherine Deleon paid us?", we are asked: 
    "how much has Catherine Deleon", so we need column = [master_txn_table.transaction_id,master_txn_table.customers]
    "paid us", so we need column = [master_txn_table.transaction_type]
    "Since Last 12 months", so we need column = [master_txn_table.transaction_date]
    Based on the columns and tables, we need these Foreign_keys = [].
    Based on the tables, columns, and Foreign_keys, The set of possible cell values are = [atherine Deleon]. So the Schema_links are:
    Schema_links: [master_txn_table.transaction_id,,master_txn_table.customers,master_txn_table.trasaction_type,master_txn_table.transaction_date,current_date]

Q: What was our total spend for Registration for tournaments and matches in yesterday
S: select sum(debit) from master_txn_table  as T1 join chart_of_accounts as T2 on T1.account = T2.account_name where instr(account,'Registration for tournaments and matches') and account_type in ('Expenses','Other Expenses') and transaction_date BETWEEN date( current_date, '-1 day') AND date( current_date, '-1 day')
A:  Let’s think step by step. In the question "What was our total spend for Registration for tournaments and matches in yesterday", we are asked: 
    "What was our total spend", so we need column = [master_txn_table.debit,master_txn_table.account,chart_of_accounts.account_type]
    "Registration for tournaments and matches", so we need column = [master_txn_table.account]
    "yesterday", so we need column = [master_txn_table.transaction_date]
    Based on the columns and tables, we need these Foreign_keys = [master_txn_table.account=chart_of_accounts.account_name].
    Based on the tables, columns, and Foreign_keys, The set of possible cell values are = [Bradley Howard]. So the Schema_links are:
    Schema_links: [master_txn_table.debit,master_txn_table.account,master_txn_table.customers,master_txn_table.transaction_date,chart_of_accounts.account_name,chart_of_accounts.account_type,current_date]

Q: What is my average revenue from Jacob Ramirez in the in q2 this year?
S: select avg(credit) from master_txn_table  as T1 join chart_of_accounts as T2 on T1.account = T2.account_name where account_type in ('Income','Other Income') and customers = 'Jacob Ramirez' and transaction_date BETWEEN date(current_date, 'start of year','+3 month') AND date(current_date, 'start of year', '+6 month', '-1 day')
A: Let’s think step by step. In the question "What is my average revenue from Jacob Ramirez in the in q2 this year?", we are asked: 
    "What is my average revenue", so we need column = [master_txn_table.credit]
    "from Jacob Ramirez", so we need column = [master_txn_table.customers]
    Based on the columns and tables, we need these Foreign_keys = [].
    Based on the tables, columns, and Foreign_keys, The set of possible cell values are = [Jacob Ramirez,master_txn_table.account=chart_of_accounts.account_name]. So the Schema_links are:
    Schema_links: [master_txn_table.credit,master_txn_table.customers,master_txn_table.transaction_type,master_txn_table.transaction_date,chart_of_accounts.account_name,chart_of_accounts.account_type,current_date]]

Q: How much money did we make This quarter to date?
S: select sum(credit) from master_txn_table  as T1 join chart_of_accounts as T2 on T1.account = T2.account_name where account_type in ('Income','Other Income') and transaction_date >= strftime('%Y-%m-%d', strftime('%Y', now) || '-' || substr('00' || (((strftime('%m', now) - 1) / 3) * 3 + 1), -2, 2) || '-01')
A: Let’s think step by step. In the question "How much money did we make This quarter to date?", we are asked: 
    "How much money", so we need column = [master_txn_table.credit,master_txn_table.account,chart_of_accounts.account_type]
    "This quarter to date", so we need column = [master_txn_table.transaction_date]
    Based on the columns and tables, we need these Foreign_keys = [].
    Based on the tables, columns, and Foreign_keys, The set of possible cell values are = []. So the Schema_links are:
    Schema_links: [master_txn_table.credit,master_txn_table.account,master_txn_table.transaction_date,chart_of_accounts.account_name,chart_of_accounts.account_type]

Q: What was our greatest expenses This fiscal year to date?
S: select account, sum(debit) from master_txn_table  as T1 join chart_of_accounts as T2 on T1.account = T2.account_name where account_type in ('Expenses','Other Expenses') and transaction_date BETWEEN date(current_date, '-3 months', 'start of year', '+3 months') AND date(current_date, '-3 months', 'start of year','+1 year', '+3 months', '-1 day')  order by sum(debit) desc limit 1
A: Let’s think step by step. In the question "What was our greatest expenses This fiscal year to date?", we are asked: 
    "What was our greatest expenses", so we need column = [master_txn_table.debit,master_txn_table.account,chart_of_accounts.account_type]
    "This fiscal year to date", so we need column = [master_txn_table.transaction_date]
    Based on the columns and tables, we need these Foreign_keys = [].
    Based on the tables, columns, and Foreign_keys, The set of possible cell values are = []. So the Schema_links are:
    Schema_links: [master_txn_table.debit,master_txn_table.account,master_txn_table.transaction_date,chart_of_accounts.account_name,chart_of_accounts.account_type,current_date]

'''
classification_prompt = '''Q: What are my transactions MTD? 
schema_links: [master_txn_table.transaction_id,master_txn_table.amount,master_txn_table.transaction_date]
A: Let’s think step by step. The SQL query for the question "What are my transactions MTD?" needs these tables = [master_txn_table], so we don't need JOIN.
Plus, it doesn't require nested queries with (INTERSECT, UNION, EXCEPT, IN, NOT IN), and we need the answer to the questions = [""].
So, we don't need JOIN and don't need nested queries, then the the SQL query can be classified as "EASY".
Label: "EASY"


Q: How many products are never sold with total value higher than 5? 
schema_links: [Product_Service.transaction_id,master_txn_table.transaction_type]
A: Let’s think step by step. The SQL query for the question "How many products are never sold with total value higher than 5?" needs these tables = [Product_Service,master_txn_table], so we need JOIN.
Plus, it requires nested queries with (INTERSECT, UNION, EXCEPT, IN, NOT IN) or inner query inside from clause, and we need the answer to the questions = ["products that are sold with total value higher than 5"].
So, we need JOIN and need nested queries, then the the SQL query can be classified as "NESTED".
Label: "NESTED"


Q: Who has the lowest money outstanding? 
schema_links: [master_txn_table.customers,master_txn_table.open_balance,master_txn_table.transaction_id,master_txn_table.customers]
A: Let’s think step by step. The SQL query for the question "Who has the lowest money outstanding?" needs these tables = [master_txn_table], so we dont need JOIN.
Plus, it requires nested queries with (INTERSECT, UNION, EXCEPT, IN, NOT IN) or inner query inside from clause, and we need the answer to the questions = ["products that are sold with total value higher than 5"].
So, we don't need JOIN and need nested queries, then the the SQL query can be classified as "NESTED".
Label: "NESTED"


Q: What is my average invoice from Patricia Mercado? 
schema_links: [master_txn_table.customers,master_txn_table.open_balance,master_txn_table.transaction_id,master_txn_table.customers]
A: Let’s think step by step. The SQL query for the question "What is my average invoice from Patricia Mercado? " needs these tables = [master_txn_table], so we dont need JOIN.
Plus, it requires nested queries with (INTERSECT, UNION, EXCEPT, IN, NOT IN) or inner query inside from clause, and we need the answer to the questions = ["Invoice from Patricia Mercado"].
So, we don't need JOIN and need nested queries, then the the SQL query can be classified as "NESTED".
Label: "NESTED"


Q:give me the list of accounts where my revenue increased by more than 10% in this month as compared to last month", 
schema_links: [master_txn_table.account,master_txn_table.credit,chart_of_accounts.account_name]
A: Let’s think step by step. The SQL query for the question "give me the list of accounts where my revenue increased by more than 10% in this month as compared to last month" needs these tables = [master_txn_table,chart_of_accounts], so we need JOIN.
Plus, it requires nested queries with (INTERSECT, UNION, EXCEPT, IN, NOT IN) or inner query inside from clause, and we need the answer to the questions = ["revenue of last month and this month"].
So, we need JOIN and need nested queries, then the the SQL query can be classified as "NESTED".
Label: "NESTED"


Q: What was our total income from Bradley Howard in yesterday?
schema_links = [master_txn_table.account = chart_of_accounts.account_name,master_txn_table.credit,master_txn_table.transaction_date,master_txn_table.account_type]
A: Let’s think step by step. The SQL query for the question "What was our total income from Bradley Howard in yesterday?" needs these tables = [master_txn_table,chart_of_accounts], so we need JOIN.
Plus, it doesn't need nested queries with (INTERSECT, UNION, EXCEPT, IN, NOT IN), and we need the answer to the questions = [""].
So, we need JOIN and don't need nested queries, then the the SQL query can be classified as "NON-NESTED".
Label: "NON-NESTED"


Q: What are my expenses for the Last 7 days?
schema_links = [master_txn_table.account = chart_of_accounts.account_name,master_txn_table.credit,master_txn_table.transaction_date,master_txn_table.account_type]
A: Let’s think step by step. The SQL query for the question "What are my expenses for the Last 7 days?" needs these tables = [master_txn_table,chart_of_accounts], so we need JOIN.
Plus, it doesn't need nested queries with (INTERSECT, UNION, EXCEPT, IN, NOT IN), and we need the answer to the questions = [""].
So, we need JOIN and don't need nested queries, then the the SQL query can be classified as "NON-NESTED".
Label: "NON-NESTED"


Q: YTD, what was our smallest expense?
schema_links = [master_txn_table.account = chart_of_accounts.account_name,master_txn_table.credit,master_txn_table.transaction_date,master_txn_table.account_type,master_txn_table.debit]
A: Let’s think step by step. The SQL query for the question "YTD, what was our smallest expense?" needs these tables = [master_txn_table,chart_of_accounts], so we need JOIN.
Plus, it doesn't need nested queries with (INTERSECT, UNION, EXCEPT, IN, NOT IN), and we need the answer to the questions = [""].
So, we need JOIN and don't need nested queries, then the the SQL query can be classified as "NON-NESTED".
Label: "NON-NESTED"

'''

easy_prompt = '''Q: "How much open credit does customer Felicia King?"
Schema_links: [master_txn_table.open_balance,master_txn_table.transaction_id,master_txn_table.customers,Felicia King]
SQL: select sum(open_balance) from ( select distinct transaction_id, open_balance from master_txn_table where customers = 'Felicia King')

Q: "What are my transactions Last fiscal year?"
Schema_links: [master_txn_table.transaction_id,master_txn_table.amount,master_txn_table.transaction_date]
SQL: select distinct transaction_id, amount from master_txn_table where transaction_date BETWEEN date(current_date, '-3 months', 'start of year','-1 years', '+3 months') AND date(current_date, '-3 months', 'start of year','-1 years', '+3 months', '+1 years', '-1 days')

Q: "How much open credit does customer Lonnie Snow?"
Schema_links: [master_txn_table.open_balance,master_txn_table.transaction_id,master_txn_table.customers,Lonnie Snow]
SQL: select sum(open_balance) from ( select distinct transaction_id, open_balance from master_txn_table where customers = 'Lonnie Snow')

Q: "What are my transactions in may last year?"
Schema_links: [master_txn_table.transaction_id,master_txn_table.amount,master_txn_table.transaction_date]
SQL: select distinct transaction_id, amount from master_txn_table where transaction_date BETWEEN date(current_date, '-1 year', 'start of year', '+4 month') AND date(current_date, '-1 year', 'start of year', '+5 month', '-1 day')

Q: "What are my transactions in aug this year?"
Schema_links: [master_txn_table.transaction_id,master_txn_table.amount,master_txn_table.transaction_date]
SQL: select distinct transaction_id, amount from master_txn_table where transaction_date BETWEEN date(current_date, 'start of year', '+7 month') AND date(current_date, 'start of year', '+8 month', '-1 day')


'''
medium_prompt = '''Q: "How many Traveller accomodation did we sell to Eric Quinn Last 7 days?"
Schema_links: [master_txn_table.quantity,master_txn_table.customers,master_txn_table.product_service,master_txn_table.transaction_type,master_txn_table.transaction_date]
A: Let’s think step by step. For creating the SQL for the given question, we need to join these tables = []. First, create an intermediate representation, then use it to construct the SQL query.
Intermediate_representation: select sum(master_txn_table.quantity) from master_txn_table where master_txn_table.customers = 'Eric Quinn' and master_txn_table.product_service = 'Traveller accomodation' and master_txn_table.trasaction_type in ('invoice','sales receipt') and master_txn_table.transaction_date BETWEEN date(current_date) AND date(current_date)
SQL: select sum(quantity) from master_txn_table where customers = \"Eric Quinn\" and product_service = \"Traveller accomodation\" and trasaction_type in ('invoice','sales receipt') and transaction_date BETWEEN date(current_date) AND date(current_date)

Q: "How many Richard Wall invoices are still outstanding?"
Schema_links: [master_txn_table.transaction_id,master_txn_table.customers,master_txn_table.open_balance,master_txn_table.transaction_type]
A: Let’s think step by step. For creating the SQL for the given question, we need to join these tables = []. First, create an intermediate representation, then use it to construct the SQL query.
Intermediate_representation: select count(distinct master_txn_table.transaction_id) from master_txn_table where master_txn_table.customers = 'Richard Wall' and master_txn_table.open_balance > 0 and master_txn_table.transaction_type = 'invoice'
SQL: select count(distinct transaction_id) from master_txn_table where customers = 'Richard Wall' and open_balance > 0 and transaction_type = 'invoice'

Q: "How many invoices are still oustanding for Tony Arellano as of in q1 this year?"
Schema_links: [master_txn_table.transaction_id,master_txn_table.customers,master_txn_table.transaction_type,master_txn_table.open_balance,master_txn_table.transaction_date]
A: Let’s think step by step. For creating the SQL for the given question, we need to join these tables = []. First, create an intermediate representation, then use it to construct the SQL query.
Intermediate_representation: select count(distinct master_txn_table.transaction_id) from master_txn_table where master_txn_table.customers = 'Tony Arellano' and master_txn_table.transaction_type = 'invoice' and master_txn_table.open_balance >0 and master_txn_table.transaction_date BETWEEN date(current_date, 'start of year') AND date(current_date, 'start of year', '+3 month', '-1 day')
SQL: select count(distinct transaction_id) from master_txn_table where customers = \"Tony Arellano\" and transaction_type = 'invoice' and open_balance >0 and transaction_date BETWEEN date(current_date, 'start of year') AND date(current_date, 'start of year', '+3 month', '-1 day')

Q: "Since Last 12 months, how many invoices have gone unpaid?"
Schema_links: [master_txn_table.transaction_id,master_txn_table.transaction_type,master_txn_table.due_date,master_txn_table.open_balance,master_txn_table.transaction_date]
A: Let’s think step by step. For creating the SQL for the given question, we need to join these tables = []. First, create an intermediate representation, then use it to construct the SQL query.
Intermediate_representation: select count(distinct master_txn_table.transaction_id) from master_txn_table where master_txn_table.transaction_type = 'invoice' and master_txn_table.due_date < current_date and master_txn_table.transaction_date BETWEEN date( current_date, '-12 months', 'start of month') AND date( current_date, 'start of month', '-1 day')  and master_txn_table.open_balance > 0
SQL: select count(distinct transaction_id) from master_txn_table where transaction_type = 'invoice' and due_date < current_date and transaction_date BETWEEN date( current_date, '-12 months', 'start of month') AND date( current_date, 'start of month', '-1 day')  and open_balance > 0

Q: "When was Colleen Cunningham first payment?"
Schema_links: [master_txn_table.transaction_date,master_txn_table.transaction_type,master_txn_table.customers,master_txn_table.transaction_date]
A: Let’s think step by step. For creating the SQL for the given question, we need to join these tables = []. First, create an intermediate representation, then use it to construct the SQL query.
Intermediate_representation: select master_txn_table.transaction_date from master_txn_table where master_txn_table.transaction_type = 'payment' and master_txn_table.customers = 'Colleen Cunningham' order by master_txn_table.transaction_date limit 1
SQL: select transaction_date from master_txn_table where transaction_type = 'payment' and customers = 'Colleen Cunningham' order by transaction_date limit 1

Q: "Have we billed Stephanie Boyd for the in This quarter?"
Schema_links: [master_txn_table.transaction_id,master_txn_table.transaction_type,master_txn_table.customers,master_txn_table.product_service,master_txn_table.transaction_date]
A: Let’s think step by step. For creating the SQL for the given question, we need to join these tables = []. First, create an intermediate representation, then use it to construct the SQL query.
Intermediate_representation: select distinct master_txn_table.transaction_id from master_txn_table where master_txn_table.transaction_type = 'bill' and master_txn_table.customers = \"Stephanie Boyd\" and master_txn_table.product_service = \"--\" and master_txn_table.transaction_date >= strftime('%Y-%m-%d', strftime('%Y', 'now', '-1 year') || '-' || substr('00' || (((strftime('%m', 'now') - 1) / 3) * 3 + 1), -2, 2) || '-01')
SQL: select distinct transaction_id from master_txn_table where transaction_type = 'bill' and customers = \"Stephanie Boyd\" and product_service = \"--\" and transaction_date >= strftime('%Y-%m-%d', strftime('%Y', 'now', '-1 year') || '-' || substr('00' || (((strftime('%m', 'now') - 1) / 3) * 3 + 1), -2, 2) || '-01')

Q: "Find out 5 customers name who most recently purchased something."
Schema_links: [master_txn_table.transaction_id,master_txn_table.customers,master_txn_table.transaction_date]
A: Let’s think step by step. For creating the SQL for the given question, we need to join these tables = []. First, create an intermediate representation, then use it to construct the SQL query.
Intermediate_representation: SELECT master_txn_table.customers FROM (select distinct master_txn_table.transaction_id, master_txn_table.customers, master_txn_table.transaction_date from master_txn_table) ORDER BY master_txn_table.transaction_date DESC LIMIT 5
SQL: SELECT customers FROM (select distinct transaction_id, customers, transaction_date from master_txn_table) ORDER BY transaction_date DESC LIMIT 5

Q: "Last month, how many Software Training did we sell to Ryan Mcdonald?"
Schema_links: [master_txn_table.quantity,master_txn_table.customers,master_txn_table.product_service,master_txn_table.trasaction_type,master_txn_table.transaction_date]
A: Let’s think step by step. For creating the SQL for the given question, we need to join these tables = []. First, create an intermediate representation, then use it to construct the SQL query.
Intermediate_representation: select sum(master_txn_table.quantity) from master_txn_table where master_txn_table.customers = \"Ryan Mcdonald\" and master_txn_table.product_service = \"Software Training\" and master_txn_table.trasaction_type in ('invoice','sales receipt') and master_txn_table.transaction_date BETWEEN date( current_date, \"start of month\", \"-1 months\") AND date( current_date, \"start of month\", \"-1 days\")
SQL: select sum(quantity) from master_txn_table where customers = 'Ryan Mcdonald' and product_service = 'Software Training' and trasaction_type in ('invoice','sales receipt') and transaction_date BETWEEN date( current_date, 'start of month', '-1 months') AND date( current_date, 'start of month', '-1 days')

Q: "Since in q3 last year, how many invoices have been late?"
Schema_links: [master_txn_table.transaction_id,master_txn_table.due_date,master_txn_table.open_balance,master_txn_table.transaction_date]
A: Let’s think step by step. For creating the SQL for the given question, we need to join these tables = []. First, create an intermediate representation, then use it to construct the SQL query.
Intermediate_representation: select count(distinct master_txn_table.transaction_id) from master_txn_table where master_txn_table.transaction_type = 'invoice' and master_txn_table.due_date < current_date and master_txn_table.transaction_date BETWEEN date(current_date, '-1 year', 'start of year', '+6 month') AND date(current_date, '-1 year', 'start of year', '+9 month', '-1 day')  and master_txn_table.open_balance > 0
SQL: select count(distinct transaction_id) from master_txn_table where transaction_type = 'invoice' and due_date < current_date and transaction_date BETWEEN date(current_date, '-1 year', 'start of year', '+6 month') AND date(current_date, '-1 year', 'start of year', '+9 month', '-1 day')  and open_balance > 0

Q: "This quarter to date, what are my accounts receivable?"
Schema_links: [master_txn_table.debit,master_txn_table.account,master_txn_table.transaction_date]
A: Let’s think step by step. For creating the SQL for the given question, we need to join these tables = []. First, create an intermediate representation, then use it to construct the SQL query.
Intermediate_representation: select sum(master_txn_table.debit) from master_txn_table where master_txn_table.account = 'accounts receivable (a/r)' and master_txn_table.transaction_date >= strftime('%Y-%m-%d', strftime('%Y', 'now', '-1 year') || '-' || substr('00' || (((strftime('%m', 'now') - 1) / 3) * 3 + 1), -2, 2) || '-01')
SQL: select sum(debit) from master_txn_table where account = 'accounts receivable (a/r)' and transaction_date >= strftime('%Y-%m-%d', strftime('%Y', 'now', '-1 year') || '-' || substr('00' || (((strftime('%m', 'now') - 1) / 3) * 3 + 1), -2, 2) || '-01')


'''
hard_prompt = '''Q: "How many products are never sold with total value higher than 5?"
Schema_links: [master_txn_table.product_service,master_txn_table.transaction_type,master_txn_table.credit,product_service.*]
A: Let's think step by step. "How many products are never sold with total value higher than 5?" can be solved by knowing the answer to the following sub-question "Show me all the products which are never sold with total credit value higher than 5?".
The SQL query for the sub-question "Show me all the products which are never sold with total credit value higher than 5?" is SELECT count(*) FROM Product_Service WHERE product_service NOT IN ( SELECT product_service FROM master_txn_table WHERE transaction_type in ('invoice','sales receipt') group by product_service  having sum(credit)  >  5)
So, the answer to the question "How many products are never sold with total value higher than 5?" is =
Intermediate_representation: SELECT count(Product_Service.*) FROM Product_Service WHERE Product_Service.product_service NOT IN ( SELECT master_txn_table.product_service FROM master_txn_table WHERE master_txn_table.transaction_type in ('invoice','sales receipt') group by master_txn_table.product_service  having sum(master_txn_table.credit)  >  5)
SQL: SELECT count(*) FROM Product_Service WHERE product_service NOT IN ( SELECT product_service FROM master_txn_table WHERE transaction_type in ('invoice','sales receipt') group by product_service  having sum(credit)  >  5)

Q: "What was our total income from Bradley Howard in yesterday?"
Schema_links: [master_txn_table.credit,master_txn_table.account,master_txn_table.customers,master_txn_table.transaction_date,chart_of_accounts.account,chart_of_accounts.account_type]
A: Let's think step by step. "What was our total income from Bradley Howard in yesterday?" can be solved by knowing the answer to the following sub-question "How much amount got credited yesterday from Bradley Howard".
The SQL query for the sub-question "How much amount got credited yesterday from Bradley Howard" is select sum(credit) from master_txn_table  as T1 join chart_of_accounts as T2 on T1.account = T2.account_name where customers = 'Bradley Howard' and transaction_date BETWEEN date( current_date, '-1 day') AND date( current_date, '-1 day')  and account_type in ('Income','Other Income')
So, the answer to the question "What was our total income from Bradley Howard in yesterday?" is =
Intermediate_representation: select sum(master_txn_table.credit) from master_txn_table  where master_txn_table.customers = 'Bradley Howard' and master_txn_table.transaction_date BETWEEN date( current_date, \"-1 day\") AND date( current_date, \"-1 day\")  and chart_of_accounts.account_type in ('Income','Other Income')
SQL: select sum(credit) from master_txn_table  as T1 join chart_of_accounts as T2 on T1.account = T2.account_name where customers = 'Bradley Howard' and transaction_date BETWEEN date( current_date, '-1 day') AND date( current_date, '-1 day')  and account_type in ('Income','Other Income')

Q: "How much money did we make This quarter to date?"
Schema_links: [master_txn_table.credit,master_txn_table.account,master_txn_table.transaction_date,chart_of_accounts.account_name,chart_of_accounts.account_type]
A: Let's think step by step. "How much money did we make This quarter to date?" can be solved by knowing the answer to the following sub-question "How much money got credited from current month quarter to current date".
The SQL query for the sub-question "How much money got credited from current month quarter to current date" is select sum(credit) from master_txn_table  as T1 join chart_of_accounts as T2 on T1.account = T2.account_name where account_type in ('Income','Other Income') and transaction_date >= strftime('%Y-%m-%d', strftime('%Y', 'now', '-1 year') || '-' || substr('00' || (((strftime('%m', 'now') - 1) / 3) * 3 + 1), -2, 2) || '-01')
So, the answer to the question "How much money did we make This quarter to date?" is =
Intermediate_representation: select sum(master_txn_table.credit) from master_txn_table where chart_of_accounts.account_type in ('Income','Other Income') and master_txn_table.transaction_date >= strftime('%Y-%m-%d', strftime('%Y', 'now', '-1 year') || '-' || substr('00' || (((strftime('%m', 'now') - 1) / 3) * 3 + 1), -2, 2) || '-01')
SQL: select sum(credit) from master_txn_table  as T1 join chart_of_accounts as T2 on T1.account = T2.account_name where account_type in ('Income','Other Income') and transaction_date >= strftime('%Y-%m-%d', strftime('%Y', 'now', '-1 year') || '-' || substr('00' || (((strftime('%m', 'now') - 1) / 3) * 3 + 1), -2, 2) || '-01')

Q: "Who has the lowest money outstanding?"
Schema_links: [master_txn_table.customers,master_txn_table.open_balance,master_txn_table.transaction_id]
A: Let's think step by step. "Who has the lowest money outstanding?" can be solved by knowing the answer to the following sub-question "Which customers has the lowest total open balance?".
The SQL query for the sub-question "Which customers has the lowest total open balance?" is select customers, sum(open_balance) from ( select distinct transaction_id, customers, open_balance from master_txn_table ) group by customers order by sum(open_balance) asc limit 1
So, the answer to the question "Who has the lowest money outstanding?" is =
Intermediate_representation: select master_txn_table.customers, sum(master_txn_table.open_balance) from ( select distinct master_txn_table.transaction_id, master_txn_table.customers, master_txn_table.open_balance from master_txn_table ) group by master_txn_table.customers order by sum(master_txn_table.open_balance) asc limit 1
SQL: select customers, sum(open_balance) from ( select distinct transaction_id, customers, open_balance from master_txn_table ) group by customers order by sum(open_balance) asc limit 1

Q: "Return the most common payment method used for transactions."
Schema_links: [master_txn_table.payment_method,master_txn_table.transaction_id]
A: Let's think step by step. "Return the most common payment method used for transactions." can be solved by knowing the answer to the following sub-question "Find which payment method is used in more number of transactions".
The SQL query for the sub-question "Find which payment method is used in more number of transactions" is SELECT payment_method FROM master_txn_table GROUP BY payment_method ORDER BY count(distinct transaction_id) DESC LIMIT 1
So, the answer to the question "Return the most common payment method used for transactions." is =
Intermediate_representation: SELECT master_txn_table.payment_method FROM master_txn_table GROUP BY master_txn_table.payment_method ORDER BY count(distinct master_txn_table.transaction_id) DESC LIMIT 1
SQL: SELECT payment_method FROM master_txn_table GROUP BY payment_method ORDER BY count(distinct transaction_id) DESC LIMIT 1

Q: "Who are my outstanding debtors or creditors?"
Schema_links: [master_txn_table.customers,master_txn_table.open_balance,master_txn_table.vendor_name]
A: Let's think step by step. "Who are my outstanding debtors or creditors?" can be solved by knowing the answer to the following sub-question "How many customers' and vendors' open balance greater than 0?".
The SQL query for the sub-question "How many customers' and vendors' open balance greater than 0?" is select distinct customers from master_txn_table where open_balance > 0 union select distinct vendor_name from master_txn_table where open_balance > 0
So, the answer to the question "Who are my outstanding debtors or creditors?" is =
Intermediate_representation: select distinct master_txn_table.customers from master_txn_table where master_txn_table.open_balance > 0 union select distinct master_txn_table.vendor_name from master_txn_table where master_txn_table.open_balance > 0
SQL: select distinct customers from master_txn_table where open_balance > 0 union select distinct vendor_name from master_txn_table where open_balance > 0

Q: "How much did we pay Michael Vaughn the Last fiscal year?"
Schema_links: [master_txn_table.debit,master_txn_table.vendor,master_txn_table.transaction_date,master_txn_table.account,chart_of_accounts.account_name,chart_of_accounts.account_type]
A: Let's think step by step. "How much did we pay Michael Vaughn the Last fiscal year?" can be solved by knowing the answer to the following sub-question "What are the amounts did we pay to Michael Vaughn in the Last fiscal year?".
The SQL query for the sub-question "What are the amounts did we pay to Michael Vaughn in the Last fiscal year?" is select sum(debit) from master_txn_table as T1 join chart_of_accounts as T2 on T1.account = T2.account_name where account_type in ('Expense', 'Other Expense') and vendor = \"Michael Vaughn\" and transaction_date BETWEEN date(current_date, '-3 months', 'start of year','-1 years', '+3 months') AND date(current_date, '-3 months', 'start of year','-1 years', '+3 months', '+1 years', '-1 days')
So, the answer to the question "How much did we pay Michael Vaughn the Last fiscal year?" is =
Intermediate_representation: select sum(master_txn_table.debit) from master_txn_table where chart_of_accounts.account_type in ('Expense', 'Other Expense') and master_txn_table.vendor = 'Michael Vaughn' and master_txn_table.transaction_date BETWEEN date(current_date, '-3 months', 'start of year','-1 years', '+3 months') AND date(current_date, '-3 months', 'start of year','-1 years', '+3 months', '+1 years', '-1 days')
SQL: select sum(debit) from master_txn_table as T1 join chart_of_accounts as T2 on T1.account = T2.account_name where account_type in ('Expense', 'Other Expense') and vendor = 'Michael Vaughn' and transaction_date BETWEEN date(current_date, '-3 months', 'start of year','-1 years', '+3 months') AND date(current_date, '-3 months', 'start of year','-1 years', '+3 months', '+1 years', '-1 days')

Q: "show me my product level revenue for this month vs last month"
Schema_links: [master_txn_type.product_service,master_txn_type.transaction_date,master_txn_type.credit,master_txn_type.account,chart_of_accounts.account_name,chart_of_accounts.account_type]
A: Let's think step by step. "show me my product level revenue for this month vs last month" can be solved by knowing the answer to the following sub-question "What are the product level revenue for this month vs product level revenue for last month".
The SQL query for the sub-question "What are the product level revenue for this month vs product level revenue for last month" is select product_service, strftime('%m', transaction_date), sum(credit) from master_txn_table  as T1 join chart_of_accounts as T2 on T1.account = T2.account_name where account_type in ('Income','Other Income') and strftime('%m', transaction_date) >= strftime('%m', current_timestamp) - 1 group by product_service, strftime('%m', transaction_date)
So, the answer to the question "show me my product level revenue for this month vs last month" is =
Intermediate_representation: select master_txn_table.product_service, strftime('%m', master_txn_table.transaction_date), sum(master_txn_table.credit) from master_txn_table where chart_of_accounts.account_type in ('Income','Other Income') and strftime('%m', master_txn_table.transaction_date) >= strftime('%m', current_timestamp) - 1 group by master_txn_table.product_service, strftime('%m', master_txn_table.transaction_date)
SQL: select product_service, strftime('%m', transaction_date), sum(credit) from master_txn_table  as T1 join chart_of_accounts as T2 on T1.account = T2.account_name where account_type in ('Income','Other Income') and strftime('%m', transaction_date) >= strftime('%m', current_timestamp) - 1 group by product_service, strftime('%m', transaction_date)

Q: "What are Crystal Price recurring product purchases over past 6 months?"
Schema_links: [master_txn_table.product_service,master_txn_table.customers,master_txn_table.transaction_date]
A: Let's think step by step. "What are Crystal Price recurring product purchases over past 6 months?" can be solved by knowing the answer to the following sub-question "What are the products purchased by customer Crystal Price in past over 6 months".
The SQL query for the sub-question "What are the products purchased by customer Crystal Price in past over 6 months" is select product_service from master_txn_table where customers = 'Crystal Price' and transaction_date BETWEEN date(current_date,'start of month','-6 month') and date(current_date,'start of month','-1 day') group by product_service having count(distinct strftime('%m', transaction_date)) = 6
So, the answer to the question "What are Crystal Price recurring product purchases over past 6 months?" is =
Intermediate_representation: select master_txn_table.product_service from master_txn_table where master_txn_table.customers = 'Crystal Price' and master_txn_table.transaction_date BETWEEN date(current_date,'start of month','-6 month') and date(current_date,'start of month','-1 day') group by master_txn_table.product_service having count(distinct strftime('%m', master_txn_table.transaction_date)) = 6
SQL: select product_service from master_txn_table where customers = 'Crystal Price' and transaction_date BETWEEN date(current_date,'start of month','-6 month') and date(current_date,'start of month','-1 day') group by product_service having count(distinct strftime('%m', transaction_date)) = 6

Q: "How much revenue came through Christine Stone in q3 last year"
Schema_links: [master_txn_table.credit,master_txn_table.account,transaction_date,master_txn_table.customers,chart_of_accounts.account_name,chart_of_accounts.account_type]
A: Let's think step by step. "How much revenue came through Christine Stone in q3 last year" can be solved by knowing the answer to the following sub-question "How much we earn from Christine Stone in q3 last year?".
The SQL query for the sub-question "How much we earn from Christine Stone in q3 last year?" is select sum(credit) from master_txn_table  as T1 join chart_of_accounts as T2 on T1.account = T2.account_name where account_type in ('Income','Other Income') and  transaction_date BETWEEN date(current_date, '-1 year', 'start of year', '+6 month') AND date(current_date, '-1 year', 'start of year', '+9 month', '-1 day')  and T1.customers = 'Christine Stone'
So, the answer to the question "How much revenue came through Christine Stone in q3 last year" is =
Intermediate_representation: select sum(master_txn_table.credit) from master_txn_table where chart_of_accounts.account_type in ('Income','Other Income') and  master_txn_table.transaction_date BETWEEN date(current_date, '-1 year', 'start of year', '+6 month') AND date(current_date, '-1 year', 'start of year', '+9 month', '-1 day')  and master_txn_table.customers = 'Christine Stone'
SQL: select sum(credit) from master_txn_table  as T1 join chart_of_accounts as T2 on T1.account = T2.account_name where account_type in ('Income','Other Income') and  transaction_date BETWEEN date(current_date, '-1 year', 'start of year', '+6 month') AND date(current_date, '-1 year', 'start of year', '+9 month', '-1 day')  and T1.customers = 'Christine Stone'
'''
#----------------------------------------------------------------------------------------------------------




def load_data(DATASET):
    return pd.read_json(DATASET)

def hard_prompt_maker(test_sample_text,database,schema_links,sub_questions):
  instruction = "# Use the intermediate representation and the schema links to generate the SQL queries for each of the questions.\n"
  fields = find_fields_MYSQL_like("college_2")
  fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like("college_2") + '\n'
  fields += find_fields_MYSQL_like(database)
  fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like(database) + '\n'
  stepping = f'''\nA: Let's think step by step. "{test_sample_text}" can be solved by knowing the answer to the following sub-question "{sub_questions}".'''
  fields += "\n"
  prompt = instruction +fields + hard_prompt + 'Q: "' + test_sample_text + '"' + '\nschema_links: ' + schema_links + stepping +'\nThe SQL query for the sub-question"'
  return prompt
def medium_prompt_maker(test_sample_text,database,schema_links):
  instruction = "# Use the the schema links and Intermediate_representation to generate the SQL queries for each of the questions.\n"
  fields = find_fields_MYSQL_like("college_2")
  fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like("college_2") + '\n'
  fields += find_fields_MYSQL_like(database)
  fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like(database) + '\n'
  fields += "\n"
  prompt = instruction +fields + medium_prompt + 'Q: "' + test_sample_text + '\nSchema_links: ' + schema_links + '\nA: Let’s think step by step.'
  return prompt
def easy_prompt_maker(test_sample_text,database,schema_links):
  instruction = "# Use the the schema links to generate the SQL queries for each of the questions.\n"
  fields = find_fields_MYSQL_like("college_2")
  fields += find_fields_MYSQL_like(database)
  fields += "\n"
  prompt = instruction +fields + easy_prompt + 'Q: "' + test_sample_text + '\nSchema_links: ' + schema_links + '\nSQL:'
  return prompt
def classification_prompt_maker(test_sample_text,database,schema_links):
  instruction = "# For the given question, classify it as EASY, NON-NESTED, or NESTED based on nested queries and JOIN.\n"
  instruction += "\nif need nested queries: predict NESTED\n"
  instruction += "elif need JOIN and don't need nested queries: predict NON-NESTED\n"
  instruction += "elif don't need JOIN and don't need nested queries: predict EASY\n\n"
  fields = find_fields_MYSQL_like("college_2")
  fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like("college_2") + '\n'
  fields += find_fields_MYSQL_like(database)
  fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like(database) + '\n'
  fields += "\n"
  prompt = instruction + fields + classification_prompt + 'Q: "' + test_sample_text + '\nschema_links: ' + schema_links + '\nA: Let’s think step by step.'
  return prompt

def schema_linking_prompt_maker(test_sample_text,database):
  instruction = "# Find the schema_links for generating SQL queries for each question based on the database schema and Foreign keys.\n"
  fields = find_fields_MYSQL_like(database)
  foreign_keys = "Foreign_keys = " + find_foreign_keys_MYSQL_like(database) + '\n'
  prompt = instruction + schema_linking_prompt + fields +foreign_keys+ 'Q: "' + test_sample_text + """"\nA: Let’s think step by step."""
  return prompt

def find_foreign_keys_MYSQL_like(db_name):
  df = spider_foreign[spider_foreign['Database name'] == db_name]
  output = "["
  for index, row in df.iterrows():
    output += row['First Table Name'] + '.' + row['First Table Foreign Key'] + " = " + row['Second Table Name'] + '.' + row['Second Table Foreign Key'] + ','
  output= output[:-1] + "]"
  return output

def find_fields_MYSQL_like(db_name):
  df = spider_schema[spider_schema['Database name'] == db_name]
  df = df.groupby(' Table Name')
  output = ""
  for name, group in df:
    output += "Table " +name+ ', columns = ['
    for index, row in group.iterrows():
      output += row[" Field Name"]+','
    output = output[:-1]
    output += "]\n"
  return output

def find_primary_keys_MYSQL_like(db_name):
  df = spider_primary[spider_primary['Database name'] == db_name]
  output = "["
  for index, row in df.iterrows():
    output += row['Table Name'] + '.' + row['Primary Key'] +','
  output = output[:-1]
  output += "]\n"
  return output
def creatiing_schema(DATASET_JSON):
    schema_df = pd.read_json(DATASET_JSON)
    schema_df = schema_df.drop(['column_names','table_names'], axis=1)
    schema = []
    f_keys = []
    p_keys = []
    for index, row in schema_df.iterrows():
        tables = row['table_names_original']
        col_names = row['column_names_original']
        col_types = row['column_types']
        foreign_keys = row['foreign_keys']
        primary_keys = row['primary_keys']
        for col, col_type in zip(col_names, col_types):
            index, col_name = col
            if index == -1:
                for table in tables:
                    schema.append([row['db_id'], table, '*', 'text'])
            else:
                schema.append([row['db_id'], tables[index], col_name, col_type])
        for primary_key in primary_keys:
            index, column = col_names[primary_key]
            p_keys.append([row['db_id'], tables[index], column])
        for foreign_key in foreign_keys:
            first, second = foreign_key
            first_index, first_column = col_names[first]
            second_index, second_column = col_names[second]
            f_keys.append([row['db_id'], tables[first_index], tables[second_index], first_column, second_column])
    spider_schema = pd.DataFrame(schema, columns=['Database name', ' Table Name', ' Field Name', ' Type'])
    spider_primary = pd.DataFrame(p_keys, columns=['Database name', 'Table Name', 'Primary Key'])
    spider_foreign = pd.DataFrame(f_keys,
                        columns=['Database name', 'First Table Name', 'Second Table Name', 'First Table Foreign Key',
                                 'Second Table Foreign Key'])
    return spider_schema,spider_primary,spider_foreign
def debuger(test_sample_text,database,sql):
  instruction = """#### For the given question, use the provided tables, columns, foreign keys, and primary keys to fix the given SQLite SQL QUERY for any issues. If there are any problems, fix them. If there are no issues, return the SQLite SQL QUERY as is.
#### Use the following instructions for fixing the SQL QUERY:
1) Use the database values that are explicitly mentioned in the question.
2) Pay attention to the columns that are used for the JOIN by using the Foreign_keys.
3) Use DESC and DISTINCT when needed.
4) Pay attention to the columns that are used for the GROUP BY statement.
5) Pay attention to the columns that are used for the SELECT statement.
6) Only change the GROUP BY clause when necessary (Avoid redundant columns in GROUP BY).
7) Use GROUP BY on one column only.

"""
  fields = find_fields_MYSQL_like(database)
  fields += "Foreign_keys = " + find_foreign_keys_MYSQL_like(database) + '\n'
  fields += "Primary_keys = " + find_primary_keys_MYSQL_like(database)
  prompt = instruction + fields+ '#### Question: ' + test_sample_text + '\n#### SQLite SQL QUERY\n' + sql +'\n#### SQLite FIXED SQL QUERY\nSELECT'
  return prompt



DATASET_SCHEMA = "./booksql/booksqltables.json"
DATASET = "./booksql/test.json"
OUTPUT_DF = "predicted_sql_booksql_gpt4_7_mod_100.csv"

spider_schema,spider_primary,spider_foreign = creatiing_schema(DATASET_SCHEMA)
val_df = load_data(DATASET)
print(f"Number of data samples {val_df.shape[0]}")
CODEX = []

for index, row in val_df.iterrows():
    if (index % 100 != 7):
       continue
    #if index < 405: continue #for testing
    print(f"index is {index}")
    print(row['query'])
    print(row['question'])
    schema_links = None
    s = 10
    while schema_links is None:
        try:
            print('generaing schema_links')
            prompt = schema_linking_prompt_maker(row['question'], row['db_id'])
            #print('prompt is = ')
            #print(prompt)
            schema_links = GPT4_generation(prompt)
            #print('response =', response)
            #print('schema link =', schema_links)
        except Exception as e:
            print(str(e))
            time.sleep(s)
            s = s + 10
            pass
    try:
        schema_links = schema_links.split("Schema_links: ")[1]
    except:
        print("Slicing error for the schema_linking module")
        schema_links = "[]"
    #print(schema_links)
    classification = None
    s = 10
    while classification is None:
        try:
            print('generaing  classification')
            classification = GPT4_generation(
                classification_prompt_maker(row['question'], row['db_id'], schema_links[1:]))
        except Exception as e:
            print(str(e))
            time.sleep(s)
            s = s + 10
            pass
    try:
        predicted_class = classification.split("Label: ")[1]
    except:
        print("Slicing error for the classification module")
        print("classification = ", classification)
        predicted_class = '"NON-NESTED"'
    #print(classification)
    if '"EASY"' in predicted_class:
        print("EASY")
        SQL = None
        s = 10
        while SQL is None:
            print("generating SQL - Easy")
            try:
                SQL = GPT4_generation(easy_prompt_maker(row['question'], row['db_id'], schema_links))
            except Exception as e:
                print(str(e))
                time.sleep(s)
                s = s + 10
                pass
    elif '"NON-NESTED"' in predicted_class:
        print("NON-NESTED")
        SQL = None
        s = 10
        while SQL is None:
            print("generating SQL - Non-Nested")
            try:
                SQL = GPT4_generation(medium_prompt_maker(row['question'], row['db_id'], schema_links))
            except Exception as e:
                print(str(e))
                time.sleep(s)
                s = s + 10
                pass
        try:
            SQL = SQL.split("SQL: ")[1]
        except:
            print("SQL slicing error")
            SQL = "SELECT"
    else:
        print('classification=',classification)
        sub_questions = classification.split('questions = ["')[1].split('"]')[0]
        print("NESTED")
        SQL = None
        s = 10
        while SQL is None:
            print("generating SQL - Nested")
            try:
                SQL = GPT4_generation(
                    hard_prompt_maker(row['question'], row['db_id'], schema_links, sub_questions))
            except Exception as e:
                print(str(e))
                time.sleep(s)
                s = s + 10
                pass
        try:
            SQL = SQL.split("SQL: ")[1]
        except:
            print("SQL slicing error")
            SQL = "SELECT"
    print(SQL)

    #debugger_prompt = debuger(row['question'], row['db_id'], SQL)

    debugged_SQL = None
    s = 10
    while debugged_SQL is None:
        try:
            print('generating debugged_SQL')
            prompt = debuger(row['question'], row['db_id'], SQL)
            #print('prompt=', prompt)
            debugged_SQL = GPT4_debug(prompt).replace("\n", " ")
        except Exception as e:
            print(str(e))
            time.sleep(s)
            s = s + 10
            pass
    if debugged_SQL is None:
        debugged_SQL = SQL
    else:
        debugged_SQL = "SELECT " + debugged_SQL
    print(debugged_SQL)
    CODEX.append([row['question'], SQL, row['query'], row['db_id'], debugged_SQL])
    #break
df = pd.DataFrame(CODEX, columns=['NLQ', 'PREDICTED SQL', 'GOLD SQL', 'DATABASE', 'DEBUGGED SQL'])
df.to_csv(OUTPUT_DF, index=False)
#results = df['PREDICTED SQL'].tolist()
#with open(OUTPUT_FILE, 'w') as f:
#    for line in results:
#        f.write(f"{line}\n")