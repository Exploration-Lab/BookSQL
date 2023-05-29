#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Import required modules
import csv
import sqlite3
import random
import pandas as pd
import numpy as np


# In[2]:


# rand_num = random.randint(0,100)
# print("Random num: ", rand_num)
# Connecting to the geeks database
# connection = sqlite3.connect(f'data/database_sqlite/master_txn{rand_num}.sqlite')

import os

try:
    os.remove('generated_data/testing/accounting_for_testing.sqlite')
except OSError:
    pass

connection = sqlite3.connect('generated_data/testing/accounting_for_testing.sqlite')

cursor = connection.cursor()

#mastertxn
create_table = '''CREATE TABLE master_txn_table(
                    id INTEGER ,
                    businessID INTEGER NOT NULL ,
                    Transaction_ID INTEGER NOT NULL,
                    Transaction_DATE DATE NOT NULL,
                    Transaction_TYPE TEXT NOT NULL,
                    Amount DOUBLE NOT NULL,
                    CreatedDATE DATE NOT NULL,
                    CreatedUSER TEXT NOT NULL,
                    Account TEXT NOT NULL,
                    AR_paid TEXT,
                    AP_paid TEXT,
                    Due_DATE DATE,
                    Open_balance DOUBLE,
                    Customers TEXT,
                    Vendor TEXT,
                    Product_Service TEXT,
                    Quantity INTEGER,
                    Rate DOUBLE,
                    Credit DOUBLE,
                    Debit DOUBLE,
                    payment_method TEXT,
                    Misc TEXT,
                    
                    FOREIGN KEY(businessID,Account) REFERENCES chart_of_accounts(businessID,Account_name),
                    FOREIGN KEY(businessID,Customers) REFERENCES customers(businessID,customer_name),
                    FOREIGN KEY(businessID,Vendor) REFERENCES vendors(businessID,Vendor_name),
                    FOREIGN KEY(businessID,Product_Service) REFERENCES products(businessID,Product_Service),
                    FOREIGN KEY(businessID) REFERENCES employees(businessID),
                    FOREIGN KEY(businessID,payment_method) REFERENCES payment_method(businessID,payment_method)
                    
                    );
                    '''


cursor.execute(create_table)

t = pd.read_csv("generated_data/new_Master_txn_table.csv")
t['id'] = np.arange(len(t))
t = t[['id', 'business Id', 'Transaction ID',
       'Transaction date', 'Transaction type', 'Amount', 'Created date',
       'Created user', 'Account', 'A/R paid', 'A/P paid', 'Due date',
       'Open balance', 'Customer name', 'Vendor name', 'Product_Service',
       'Quantity', 'Rate', 'Credit', 'Debit', 'payment method',
       'Misc (Business specific fields)']]

# t[['Amount','Open balance','Credit',"Debit"]] = t[['Amount','Open balance','Credit',"Debit"]].apply(lambda x : 0.0 if x == "--" else x.replace('$',"").replace(',','')).astype("float64")
t[['Amount','Open balance','Credit','Debit']] = t[['Amount','Open balance','Credit','Debit']].replace('--', str(0.0), regex=True)
t[['Amount','Open balance','Credit','Debit']] = t[['Amount','Open balance','Credit','Debit']].replace('[\$,]', '', regex=True)
t[['Amount','Open balance','Credit',"Debit"]] = t[['Amount','Open balance','Credit',"Debit"]].apply(pd.to_numeric) #.astype("float64")

# t['Amount'] = t['Amount'].apply(lambda x : 0.0 if x == "--" else x.replace({'$':"" , "," : ""},regex=True)).astype("float64")

t = t.apply(lambda x: x.astype(str).str.lower())

# date_list = ['2022-01-01', '2022-03-01', '2022-04-01', '2022-06-01', '2022-07-01', '2022-09-01', '2022-10-01', '2022-12-01']
# _choices = random.choices(range(len(date_list)), k=len(t))
# date_list1 = [date_list[_c] for _c in _choices]
# t['Transaction date']=date_list1


t.to_csv("test.csv",index = False)

file = open('test.csv')
contents = csv.reader(file)

next(contents,None)

insert_records = "INSERT INTO master_txn_table (id,businessID, Transaction_ID, Transaction_DATE, Transaction_TYPE, Amount, CreatedDATE, CreatedUSER, Account, AR_paid, AP_paid, Due_DATE, Open_balance, \
                            Customers, Vendor, Product_Service, Quantity, Rate, Credit, Debit,payment_method, Misc) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        
    

cursor.executemany(insert_records, contents)
print("master_txn_table completed")


#chart_of_acc
create_table = '''CREATE TABLE chart_of_accounts(
                    id INTEGER ,
                    businessID INTEGER NOT NULL,
                    Account_name TEXT NOT NULL,
                    Account_type TEXT NOT NULL,
                    PRIMARY KEY(id,businessID,Account_name)
                    );
                    '''

t = pd.read_csv("generated_data/chart_of_account.csv")
t['id'] = np.arange(len(t))
t = t[['id', 'Business Id', 'Account name', 'Account type']]
t = t.apply(lambda x: x.astype(str).str.lower())

t.to_csv("test.csv",index=False)

cursor.execute(create_table)
file = open('test.csv')
contents = csv.reader(file)
next(contents,None) 

insert_records = "INSERT INTO chart_of_accounts (id,businessID, Account_name, Account_type) VALUES(?,?,?,?)"

cursor.executemany(insert_records, contents)
print("chart_of_account completed")

#customers
create_table = '''CREATE TABLE customers(
                    id INTEGER ,
                    businessID INTEGER NOT NULL,
                    customer_name TEXT NOT NULL,
                    customer_full_name TEXT ,
                    Billing_address TEXT ,
                    Billing_city TEXT ,
                    Billing_state TEXT,
                    Billing_ZIP_code INTEGER,
                    Shipping_address TEXT ,
                    Shipping_city TEXT ,
                    Shipping_state TEXT ,
                    Shipping_ZIP_code INTEGER,
                    Balance DOUBLE ,
                    PRIMARY KEY(id,businessID,Customer_name)
                    );
                    '''
cursor.execute(create_table)

t = pd.read_csv("generated_data/customer_table.csv")
t['id'] = np.arange(len(t))
t[['Balance']] = t[['Balance']].replace('--', str(0.0), regex=True)
t[['Balance']] = t[['Balance']].replace('[\$,]', '', regex=True)
t[['Balance']] = t[['Balance']].apply(pd.to_numeric) #.astype("float64")

t.drop(columns=['Unnamed: 0'], inplace=True)
col = t.pop("id")
t.insert(0, col.name, col)
t = t.apply(lambda x: x.astype(str).str.lower())


t.to_csv("test.csv",index=False)

# print(t.columns)
file = open('test.csv')
contents = csv.reader(file)
next(contents,None) 


insert_records = "INSERT INTO customers(id,businessID, customer_name, customer_full_name, Billing_address,Billing_city,\
Billing_state,Billing_ZIP_code,Shipping_address,Shipping_city,Shipping_state,Shipping_ZIP_code,Balance) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)"

cursor.executemany(insert_records, contents)
print("customer completed")

#employees
create_table = '''CREATE TABLE employees(
                    id INTEGER  ,
                    businessID TEXT NOT NULL,
                    Employee_name TEXT NOT NULL,
                    Employee_ID TEXT,
                    Hire_date DATE,
                    Billing_rate DOUBLE,
                    Deleted TEXT,
                    PRIMARY KEY(id,businessID,Employee_name)
                    );
                    '''
t = pd.read_csv("generated_data/employee_table.csv")
t['id'] = np.arange(len(t))

t.drop(columns=['Unnamed: 0'], inplace=True)
col = t.pop("id")
t.insert(0, col.name, col)
t = t.apply(lambda x: x.astype(str).str.lower())


t.to_csv("test.csv",index=False)

cursor.execute(create_table)
file = open('test.csv')
contents = csv.reader(file)
next(contents,None) 

insert_records = "INSERT INTO employees(id,businessID,Employee_name,Employee_ID,Hire_date,Billing_rate,Deleted) VALUES(?,?,?,?,?,?,?)"
        

cursor.executemany(insert_records, contents)
print("employees completed")

#products
create_table = '''CREATE TABLE products(
                    id INTEGER  ,
                    businessID TEXT NOT NULL,
                    Product_Service TEXT NOT NULL,
                    Product_Service_type TEXT,
                    PRIMARY KEY(id,businessID,Product_Service)
                    );
                    '''

t = pd.read_csv('generated_data/product_service_table.csv')
t['id'] = np.arange(len(t))

t.drop(columns=['Unnamed: 0'], inplace=True)
col = t.pop("id")
t.insert(0, col.name, col)
t = t.apply(lambda x: x.astype(str).str.lower())

t.to_csv('test.csv',index=False)

cursor.execute(create_table)
file = open('test.csv')
contents = csv.reader(file)
next(contents,None) 


insert_records = "INSERT INTO products(id,businessID,Product_Service,Product_Service_type) VALUES(?,?,?,?)"

cursor.executemany(insert_records, contents)
print("products completed")

#vendors
create_table = '''CREATE TABLE vendors(
                    id INTEGER  ,
                    businessID TEXT NOT NULL,
                    Vendor_name TEXT NOT NULL,
                    Billing_address TEXT,
                    Billing_city TEXT,
                    Billing_state TEXT,
                    Billing_ZIP_code INTEGER,
                    Balance DOUBLE,
                    PRIMARY KEY(id,businessID,Vendor_name)
                   
                    );
                    '''
t = pd.read_csv('generated_data/vendor_table.csv')
t['id'] = np.arange(len(t))
t[['Balance']] = t[['Balance']].replace('--', str(0.0), regex=True)
t[['Balance']] = t[['Balance']].replace('[\$,]', '', regex=True)
t[['Balance']] = t[['Balance']].apply(pd.to_numeric) #.astype("float64")

t.drop(columns=['Unnamed: 0'], inplace=True)
col = t.pop("id")
t.insert(0, col.name, col)
t = t.apply(lambda x: x.astype(str).str.lower())

t.to_csv('test.csv',index=False)

cursor.execute(create_table)
file = open('test.csv')
contents = csv.reader(file)
next(contents,None) 

insert_records = "INSERT INTO vendors(id,businessID,Vendor_name,Billing_address,Billing_city,Billing_state,Billing_ZIP_code,Balance) VALUES(?,?,?,?,?,?,?,?)"

cursor.executemany(insert_records, contents)
print("vendors completed")

#payment_method
create_table = '''CREATE TABLE payment_method(
                    id INTEGER ,
                    businessID TEXT NOT NULL,
                    Payment_method TEXT ,
                    Credit_card TEXT,
                    PRIMARY KEY(id,businessID,Payment_method)
                    );
                    '''

t = pd.read_csv('generated_data/payment_method.csv')
t['id'] = np.arange(len(t))

t.drop(columns=['Unnamed: 0'], inplace=True)
col = t.pop("id")
t.insert(0, col.name, col)
t = t.apply(lambda x: x.astype(str).str.lower())

t.to_csv('test.csv',index=False)

cursor.execute(create_table)
file = open('test.csv')
contents = csv.reader(file)
next(contents,None) 

insert_records = "INSERT INTO payment_method(id,businessID,Payment_method,Credit_card) VALUES(?,?,?,?)"

cursor.executemany(insert_records, contents)
print("payment completed")

# Committing the changes
connection.commit()

# closing the database connection
connection.close()

