### BookSQL Description


It'll generate BookSQL Data - accounting database (accounting.sqlite), train.json & val.json

* accounting.sqlite
    1. master_txn_table - It is the main table which consists of all the transactions record that happened in the businesses.
    2. chart_of_accounts - It consists of all the accounts names and their types of all the businesses.
    3. products_service - It consists of all the products/services and their types used by businesses.
    4. customers - It consists the record of all the customers and their details like name, billing and shipping address, etc which are associated with the businesses.
    5. vendors - It consists the record of all the vendors and their details like name, billing and shipping address, etc which are associated with the businesses.
    6. payment_method - It consists of the payment methods used by the businesses.
    7. employees - It consists of the details of employees such as name, employee ID, hire date, etc working in particular business.

* train.json
    Training Examples - 70828
* val.json
    Validation Examples - 7605
* README.md

Format of train/val/test.json
    Ex - 
    {
        "Query":"What was the first invoice for Matthew James?",
        "SQL":"select transaction_id from master_txn_table where customers = \"Matthew James\" and transaction_type = 'invoice' order by transaction_date limit 1",
        "Levels":"medium",
        "split":"test"
    }

    Query - Natural language query of users
    SQL - GOLD SQL
    Levels - All queries are divided into 3 levels based on the complexity of the SQL. 
    split - test/traiin/val



### BookSQL Creation

We used dummy accounting databases - Master Txn Tables for reference and generated 27 Business accouting databases.

Business details can be found in table - Industry Details

1. database_creation.py - It'll create database accouting.sqlite that contains all 7 tables mentioned above.
2. gen_data.ipynb - It'll generate all 7 tables for different businesses.
3. query_on_db.py - will run query on database and give output.

