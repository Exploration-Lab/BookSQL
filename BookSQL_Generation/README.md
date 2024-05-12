### BookSQL Description

This will generate BookSQL Data - accounting database (accounting.sqlite), train.json, val.json and test.json

* accounting.sqlite
    1. Master_txn_table - It is the main table which consists of all the transactions record that happened in the businesses.
    2. Chart_of_accounts - It consists of all the accounts names and their types of all the businesses.
    3. Products_service - It consists of all the products/services and their types used by businesses.
    4. Customers - It consists the record of all the customers and their details like name, billing and shipping address, etc which are associated with the businesses.
    5. Vendors - It consists the record of all the vendors and their details like name, billing and shipping address, etc which are associated with the businesses.
    6. Payment_method - It consists of the payment methods used by the businesses.
    7. Employees - It consists of the details of employees such as name, employee ID, hire date, etc working in particular business.

* train.json
    Training Examples - 70828
* val.json
    Validation Examples - 7605
* test.json
    Testing Samples - 21567

Format of train/val/test.json:
```
    {
        "Query":"What was the first invoice for Matthew James?",
        "SQL":"select transaction_id from master_txn_table where customers = \"Matthew James\" and transaction_type = 'invoice' order by transaction_date limit 1",
        "Levels":"medium",
        "split":"test"
    }
```

    Query - Natural language query of users
    SQL - GOLD SQL
    Levels - All queries are divided into 3 levels based on the complexity of the SQL. 
    split - test/traiin/val

NOTE: We are not releasing the Gold SQL queries for the test set as we are maintaining a leaderboard where a user can upload the predictions of their model and evaluate. 

### BookSQL Creation

BookSQL dataset consists of 100k questions in natural language and their corresponding SQL on multiple tables, covering 27 different businesses. We involved financial experts in the query creation process.
In order to be as exhaustive as possible, with the help of experts, we arrived at a list of 183 unique natural language questions that customers typically ask when interacting with accounting databases. The financial experts helped us on a pro bono basis since the creation of Text-to-SQL system for the accounting domain would help them and their customers.

Business details can be found in table - Industry Details

1. database_creation.py - It'll create database accouting.sqlite that contains all 7 tables mentioned above.
2. gen_data.ipynb - It'll generate all 7 tables for different businesses.
3. query_on_db.py - will run query on database and give output.

