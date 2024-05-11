import pandas as pd
import numpy as np

from itertools import permutations, product as iter_prod
import random
import datetime
from datetime import date, timedelta

# from faker import Faker


def alter_created_and_due_date(org_df, no_of_example=-1):
    print("Updating Created Date")
    new_df=pd.DataFrame(columns=org_df.columns)
    # c=0
    fake=Faker()
    for b_id in org_df['business Id'].unique():
        print("b_id: ", b_id)
        c=0
        df=org_df.copy()
        df=df[df['business Id']==b_id]
        id_list = df['Transaction ID'].unique()
        random.shuffle(id_list)
        for id in id_list:
            temp_df = df[df['Transaction ID']==id]
            ## same across all rows for one transaction id
    #         print(temp_df['Created date'].tolist()[0].date())
            cur_transaction_date = fake.date_between(start_date='-30y', end_date='now') #temp_df['Transaction date'].tolist()[0].date()
            new_transaction_date = cur_transaction_date + timedelta(days=random.randint(10, 365))
            new_due_date = new_transaction_date + timedelta(days=random.randint(10, 365))
            temp_df['Transaction date'] = [cur_transaction_date]*len(temp_df)
            temp_df['Created date'] = [new_transaction_date]*len(temp_df)
            temp_df['Due date'] = [new_due_date]*len(temp_df)
            new_df = pd.concat([new_df, temp_df], ignore_index=True)
    #         print("cur_created_date: ", cur_transaction_date)
    #         print("random no: ", get_random_no_of_days)
    #         print("new_created_date: ", new_transaction_date)
            c+=len(temp_df)
            if no_of_example!=-1 and c>=no_of_example: 
                break
                # return new_df
    return new_df

def alter_transaction_type(master_txn_df, transaction_type_list):
    print("Updating Transaction type")
    new_df=pd.DataFrame(columns=master_txn_df.columns)
    org_df=master_txn_df.copy()
    for b_id in org_df['business Id'].unique():
        print("b_id: ", b_id)
        df=org_df[org_df['business Id']==b_id]
        id_list = df['Transaction ID'].unique()
        for id in id_list:
            temp_df = df[df['Transaction ID']==id]
            temp_df['Transaction type'] = random.choice(transaction_type_list)
            new_df = pd.concat([new_df, temp_df], ignore_index=True)
    return new_df

# new_df = pd.read_csv("generated_data/Master_txn_table.csv")
# no_of_example = 30000
# new_df = alter_created_and_due_date(new_df, no_of_example)
# new_df

df = pd.read_excel('data/dataset_details.xlsx', sheet_name='Master Txn Tables')
transaction_type_list = df['Transaction type'].unique()
print(transaction_type_list)

df = pd.read_csv('generated_data/Master_txn_table.csv')
new_df = alter_transaction_type(df, transaction_type_list)

new_df.to_csv('generated_data/new_Master_txn_table1.csv')