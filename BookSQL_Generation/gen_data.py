#!/usr/bin/env python
# coding: utf-8

# In[56]:


import pandas as pd
import numpy as np

from itertools import permutations, product as iter_prod
import random
import datetime
from datetime import date, timedelta

from faker import Faker


# In[57]:


# pip install faker


# In[58]:


pd.options.mode.chained_assignment = None  # default='warn'


# In[59]:


df = pd.read_excel('data/dataset_details.xlsx', sheet_name='Master Txn Tables')
chart_of_accounts = pd.read_excel('data/dataset_details.xlsx', sheet_name='chart of accounts')
# vendor_df = pd.read_csv('data/vendor-payments-purchase-order-summary-1.csv') ## This is for getting different vendor names only
vendor_details_df = pd.read_excel('data/dataset_details.xlsx', sheet_name='Vendors')
customer_details_df = pd.read_excel('data/dataset_details.xlsx', sheet_name='Customers')
employees_details_df = pd.read_excel('data/dataset_details.xlsx', sheet_name='Employees')
prod_service_df = pd.read_excel('data/dataset_details.xlsx', sheet_name='Product_Service')
other_business_account_acc_names_and_prod = pd.read_csv('data/Industry_Details.csv')
payment_method = pd.read_excel('data/dataset_details.xlsx', sheet_name='Payment Method')
df.head(10)


transaction_type_list = df['Transaction type'].unique()
# In[60]:


other_business_account_acc_names_and_prod.head()
# employees_details_df.head()


# In[61]:


df.columns


# In[62]:


np.unique(df['Transaction type'])


# In[63]:


np.unique(df['Account'])


# In[64]:


df['Transaction ID'] = df['Transaction ID'].astype(int)


# In[65]:


df.head()


# In[66]:


df.columns


# In[67]:


def get_vendor_names(list_size):
    vendor_lists=[Faker().name() for _ in range(list_size)]
    return vendor_lists
    # return vendor_df['Vendor'].unique().tolist()
def get_customer_names(list_size):
    customer_lists=[Faker().name() for _ in range(list_size)]
    return customer_lists
def get_employees_names(list_size):
    employees_lists=[Faker().name() for _ in range(list_size)]
    return employees_lists


# In[68]:


# vendor_lists = get_vendor_names(100000)
# print("Total Vendor names: ", len(vendor_lists))
# employees_lists = get_employees_names(100000)
# print("Total Employee names: ", len(employees_lists))
# customer_lists = get_customer_names(100000) #100k customer names are being generated
# print("Total Customer names: ", len(customer_lists))


# In[69]:


import pickle
# with open('generated_data/vendor_names', 'wb') as fp:
#     pickle.dump(vendor_lists, fp)

# with open('generated_data/customer_names', 'wb') as fp:
#     pickle.dump(customer_lists, fp)

# with open('generated_data/employees_names', 'wb') as fp:
#     pickle.dump(employees_lists, fp)

with open ('generated_data/vendor_names', 'rb') as fp:
    vendor_lists = pickle.load(fp)

with open ('generated_data/customer_names', 'rb') as fp:
    customer_lists = pickle.load(fp)
    
with open ('generated_data/employees_names', 'rb') as fp:
    employees_lists = pickle.load(fp)
print("Total Vendor names: ", len(vendor_lists))
print("Total Customer names: ", len(customer_lists))
print("Total Employees names: ", len(employees_lists))


# ### For different business, following are possible account names 

# In[70]:


def get_other_business_details(org_df):
    df=org_df.copy()
    uniq_industry = df['Industry'].unique().tolist()
    


# In[71]:


#Current choice - that helps to modify the Master Txn table with other business
# Business specific account names are-
business_specific_acc_names = ['Cost of Goods Sold','Fountains and Garden Lighting','Fountain and Garden Lighting',
                               'Inventory Asset','Landscaping Services',
                               'Opening Balance Equity','Pest Control Services','Plants and Soil',
                               'Sales of Product Income','Sprinklers and Drip Systems']
                               # 'Permits','Decks and Patios','Maintenance and Repair',
                               # 'Job Materials','Equipment Rental',
                               # 'Labor','Installation',
                               # 'Computer Repairs']

# dict={"industry":{"business 1" : [account_names], "business 2":[] ...}}
'''
other_business=[['Artificial corundum','Sandpaper','Polishing and grinding wheels',
                'Textile-backed abrasive product', 'Grains and Powders',
                'Nonmetallic abrasive product','Buffing and polishing wheels',
                'Metal abrasives'],
                ['Pens','Lead and colored Pencils','Markers','Paint and Paintbrushes',
                'Canvas Boards','Crayons and Watercolors','Office Supplies',
                'Carbon Paper','Stencil Paper','Inked Ribbon'],
                ['Natural and Synthetic Perfumes',
                'Shaving creams and aftershave products','Haircare products',
                'Face and body creams','Beauty creams and lotion','Sunscreen products',
                'Cosmetics','Bath Salts and Talcum Powders',
                'Deodorants and Depilatory products',
                'Nail care preparations and nail polishes','Toilet cream or lotions'],
                ['Automotive bodywork','Automotive painting',
                'Automotive upholstery shop operation','Automotive interior repair',
                'Antique and classic automotive restoration',
                'Truck trailer body shop operation','Truck trailer paint and body repair',
                'Van conversion','Automotive glass shop operation',
                'Automotive glass tinting'],
                ['Repairing automotive engines',
                'Automotive repairs','Repairing trucks',
                'Repairing automotive exhaust systems',
                'Repairing mufflers','Repairing automotive transmissions',
                'Repairing automotive brakes','Performing automotive electric repairs',
                'Performing automotive wheel alignments','Repairing automotive radiators']]
'''


# In[72]:


#chart_of_accounts['Account name'].index(business_specific_acc_names)
#chart_of_accounts['Account name'].tolist()


# In[73]:


def get_diff_business_acc_names(master_txn_df, chart_of_accounts, business_specific_acc_names, other_business_df):
    new_df = pd.DataFrame(columns=chart_of_accounts.columns)
    new_master_txn_df = pd.DataFrame(columns=master_txn_df.columns) #master_txn_df.copy()
    other_business_list=other_business_df['Industry'].unique()
    txn_id_max=max(master_txn_df['Transaction ID'].tolist())+1
    for b_id in range(len(other_business_list)):
        #Chart of accounts
        df = chart_of_accounts.copy()
        b_df = other_business_df[other_business_df['Industry'] == other_business_list[b_id]]
        b_spec_names = df['Account name'].tolist()
        df['Account name']=df['Account name'].replace(business_specific_acc_names, b_df['Account Name'].tolist())
        df['Account Full Name']=df['Account name']
        b_spec_idx =[]
        for i, b_spec in enumerate(b_spec_names):
            if b_spec in business_specific_acc_names:
                b_spec_idx.append(i)
        df.loc[b_spec_idx, 'Account type'] = ['Income']*len(b_spec_idx)
        df['Business Id']=b_id+2 #1 is already there so start with 2 
        new_df = pd.concat([new_df, df], ignore_index=True)
        
        #Master Txn Table
        m_txn_df = master_txn_df.copy()
        b_df = other_business_df[other_business_df['Industry'] == other_business_list[b_id]]
        b_prod_names = b_df['Product_Service'].tolist()
        b_spec_names = m_txn_df['Account'].tolist()
        m_txn_df['Account']=m_txn_df['Account'].replace(business_specific_acc_names, b_df['Account Name'].tolist())
        b_spec_idx, ob_prod_names =[], [] #ob_names-other business product names
        for i, b_spec in enumerate(b_spec_names):
            if b_spec in business_specific_acc_names:
                b_spec_idx.append(i)
                ob_prod_names.append(b_prod_names[business_specific_acc_names.index(b_spec)])
                
        m_txn_df.loc[b_spec_idx,'Product_Service'] = ob_prod_names
        
        m_txn_df['business Id']=b_id+2 #1 is already there so start with 2 
        m_txn_df['Transaction ID']+=txn_id_max
        txn_id_max+=1
        new_master_txn_df = pd.concat([new_master_txn_df, m_txn_df], ignore_index=True)
    new_df = new_df[['Business Id', 'Account name', 'Account Full Name', 'Account type']]
    return new_df, new_master_txn_df
        
other_business_chart_of_accounts, new_master_txn_df = get_diff_business_acc_names(df, chart_of_accounts, business_specific_acc_names, other_business_account_acc_names_and_prod) 


# In[74]:


new_master_txn_df[new_master_txn_df['Product_Service']!='--']['Product_Service']


# In[75]:


new_master_txn_df[['Account', 'Product_Service']].head(20)


# In[76]:


other_business_chart_of_accounts
#new_master_txn_df


# In[77]:


def get_diff_acc_names_w_same_acc_type(chart_of_accounts):
    new_df=pd.DataFrame(columns=chart_of_accounts.columns)
    business_id=chart_of_accounts['Business Id'].unique()
    print(business_id)
    business_acc_names_dict={}
    for b_id in business_id:
        df = chart_of_accounts.copy()
        df = df[df['Business Id']==b_id]
        acc_type = df['Account type'].unique()
        same_acc_type_diff_names={}
        for a_type in acc_type:
            temp_df = df[df['Account type']==a_type]
            if len(temp_df)>1:
                get_acc_names = temp_df['Account name'].tolist()
                same_acc_type_diff_names.update({name:[] for name in get_acc_names})
                pairwise_names = [(a, b) for idx, a in enumerate(get_acc_names) for b in get_acc_names[idx + 1:]]
                for names in pairwise_names:
                    if names[0] in same_acc_type_diff_names:
                        same_acc_type_diff_names[names[0]].append(names[1])
                    else: same_acc_type_diff_names[names[0]] = names[1]
                    if names[1] in same_acc_type_diff_names:
                        same_acc_type_diff_names[names[1]].append(names[0])
                    else: same_acc_type_diff_names[names[1]] = names[0]
        business_acc_names_dict[b_id]=same_acc_type_diff_names
#     print(same_acc_type_diff_names)
    return business_acc_names_dict


# In[78]:


same_acc_type_diff_names_dict = get_diff_acc_names_w_same_acc_type(other_business_chart_of_accounts)
same_acc_type_diff_names_dict


# In[79]:


def alter_account_names(df, no_of_example=-1):
    new_df=pd.DataFrame(columns=df.columns)
    c=0
    id_list = df['Transaction ID'].unique()
    random.shuffle(id_list)
#     print(id_list)
    for id in id_list:
        temp_df = df[df['Transaction ID']==id]
#         print(len(temp_df))
        account_names = temp_df['Account'].tolist()
#         print(account_names)
        acc_name_dict={}
        i=0
        for acc_name in set(account_names):
            acc_name_dict[acc_name]=i
            i+=1
        account_names_idx = [acc_name_dict[name] for name in account_names]
        #generate all unique permutations of different account names
        all_perm = set(permutations(list(account_names_idx)))
        all_perm = list(all_perm)
#         print(all_perm)
        original_perm = tuple(account_names_idx)
#         print(original_perm)
        #remove the original data to avoid duplication
        all_perm.remove(original_perm)
#         print(all_perm)
        for perm in all_perm:
            account_names_as_per_perm = [account_names[acc_idx] for acc_idx in perm]
            #print(account_names_as_per_perm)
            temp_df['Account'] = account_names_as_per_perm
            new_df = pd.concat([new_df, temp_df], ignore_index=True)
            c+=len(perm)
            if no_of_example!=-1 and c>=no_of_example: 
                return new_df
    return new_df


# In[80]:


def alter_account_names_w_same_account_type(org_df, same_acc_type_diff_names_dict, no_of_example=-1):
    print("Getting more account names with same account types")
    new_df=pd.DataFrame(columns=org_df.columns)
    # c=0
    txn_id_max=max(org_df['Transaction ID'].tolist())+1
    acc_names_map_to_prod_dict={k: v for k, v in zip(org_df['Account'].tolist(), org_df['Product_Service'].tolist())} 
    for b_id in org_df['business Id'].unique():
        print("Business Id: ", b_id)
        c=0
        df=org_df.copy()
        df = df[df['business Id']==b_id]
        id_list = df['Transaction ID'].unique()
        for id in id_list:
            # print("id: ", id)
            temp_df = df[df['Transaction ID']==id]  

            acc_list = temp_df['Account'] #.unique()
            get_rep_acc_names_list = []
            for acc_name in acc_list:
                if acc_name not in same_acc_type_diff_names_dict[b_id]: 
                    get_rep_acc_names_list.append([acc_name])
                else: get_rep_acc_names_list.append(same_acc_type_diff_names_dict[b_id][acc_name])
            
            get_differ_perm_acc_names=[]
            for x in iter_prod(*get_rep_acc_names_list):
                if len(set(x))==len(x):
                    get_differ_perm_acc_names.append(list(x))
            
            #Consider 20% perm only
#             get_differ_perm_acc_names = get_differ_perm_acc_names[:int(0.1*len(get_differ_perm_acc_names))]
            
#             print("Actual acc_names: ", acc_list)
#             print("get_differ_perm_acc_names: ", get_differ_perm_acc_names)
#             print()
#             c+=1
#             if c==10: return new_df
#         return new_df
            flag=0
            random.shuffle(get_differ_perm_acc_names)
            for acc_name_list in get_differ_perm_acc_names:
                if len(acc_list)!=len(acc_name_list):
                    print(acc_list)
                    print(acc_name_list)
                assert len(acc_list) == len(acc_name_list)
                temp_df['Account']=acc_name_list
                temp_df['Transaction ID'] = txn_id_max+1
                temp_df['Product_Service'] = temp_df['Account'].apply(lambda x: acc_names_map_to_prod_dict[x] if x in acc_names_map_to_prod_dict else '--')
                txn_id_max += 1
                new_df = pd.concat([new_df, temp_df], ignore_index=True)
                c+=len(temp_df)
                if no_of_example!=-1 and c>=no_of_example: 
                    flag=1
                    break
                    # return new_df
            if flag==1:
                break
#             for acc_name in acc_list:
#                 if acc_name not in same_acc_type_diff_names_dict[b_id]: continue
#                 temp_df = temp_df[temp_df['Account']==acc_name]
#                 for diff_acc_name in same_acc_type_diff_names_dict[b_id][acc_name]:
#                     temp_df['Account']=diff_acc_name
#                     txn_id_list = np.arange(txn_id_max, txn_id_max+len(temp_df))
#                     temp_df['Transaction ID'] = txn_id_list
#                     txn_id_max = txn_id_list[-1]+1

    return new_df


# In[81]:


# acc_names_map_to_prod_dict={'Accounts Payable (A/P)':'Sod', 'Miscellaneous':'Misc'}
# temp_df = df[df['Transaction ID'] == 1]
# temp_df
# temp_df['Product_Service'] = temp_df['Account'].apply(lambda x: acc_names_map_to_prod_dict[x])
# temp_df[temp_df.columns[:20]]


# In[82]:


def alter_created_and_due_date(org_df, no_of_example=-1):
    print("Updating Created Date")
    new_df=pd.DataFrame(columns=org_df.columns)
    # c=0
    fake=Faker()
    for b_id in org_df['business Id'].unique():
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

# In[83]:


# def alter_ar_ap_paid(df, no_of_examples=-1):
#     #don't generate same examples if it is unpaid then change into paid and also update open balance to some value
#     #A/P is non-zero that means vendor names should get updated with any vendor names
#     #A/R is non-zero then customer names should get udpated
#     #If the A/P is Unpaid, open_balance>0 and becuase of double accounting update, debit from account_type='any service name' and credit to the account_type="Account Payable"
#     #If we modify A/R & A/P then Open balance, Quantity, Rate, credit and debit will get changed.
#     new_df=pd.DataFrame(columns=df.columns)
#     id_list = df['Transaction ID'].unique()
#     random.shuffle(id_list)
#     c=0
#     status = ['Paid', 'Unpaid']
#     AR_AP_col = ['A/R paid', 'A/P paid']
#     for id in id_list:
#         temp_df = df[df['Transaction ID']==id]
#         status_rnd_idx = random.randint(0, 1)
#         AR_AP_rnd_idx = random.randint(0, 1)
#         print("status_rnd_idx: ", status_rnd_idx)
#         print("AR_AP_rnd_idx: ", AR_AP_rnd_idx)
#         #get random index between status and AR and AP 
#         temp_df[AR_AP_col[AR_AP_rnd_idx]] = status[status_rnd_idx]
#         #remove the other column to null string because only one can be filled in one row
#         temp_df[AR_AP_col[AR_AP_rnd_idx^1]] = ['']*len(temp_df)
#         new_df = pd.concat([new_df, temp_df], ignore_index=True)
#         c+=len(temp_df)
#         if no_of_example!=-1 and c>=no_of_example: 
#             return new_df
#     return new_df


# In[84]:


def alter_user_name(org_df, customer_lists, no_of_example=-1):
    print("Updating User Name")
    new_df=pd.DataFrame(columns=org_df.columns)
    c=0
    cidx=0
    for b_id in org_df['business Id'].unique():
        c=0
        df=org_df.copy()
        df=df[df['business Id']==b_id]
        id_list = df['Transaction ID'].unique()
        random.shuffle(id_list)
#         fake = Faker()
        for id in id_list:
            temp_df = df[df['Transaction ID']==id]
            if(temp_df['Customer name'].tolist()[0]=='--'): temp_df=temp_df
            else: temp_df['Customer name'] = customer_lists[cidx] #fake.name()
            cidx+=1
            if cidx>= len(customer_lists):
                cidx=0
            new_df = pd.concat([new_df, temp_df], ignore_index=True)
            c+=len(temp_df)
            if no_of_example!=-1 and c>=no_of_example: 
                break
                # return new_df
    return new_df


# In[85]:


def alter_vendor_names(org_df, vendor_lists, no_of_example=-1):
    print("Updating Vendor Names")
    new_df=pd.DataFrame(columns=org_df.columns)
    c,i=0,0
    for b_id in org_df['business Id'].unique():
        c,i=0,0
        df=org_df.copy()
        df=df[df['business Id']==b_id]
        id_list = df['Transaction ID'].unique()
        random.shuffle(id_list)
        random.shuffle(vendor_lists)
#         fake = Faker()
        for id in id_list:
            temp_df = df[df['Transaction ID']==id]
            if temp_df['Vendor name'].values[0] =='--': temp_df=temp_df
            else: temp_df['Vendor name'] = vendor_lists[i]
            new_df = pd.concat([new_df, temp_df], ignore_index=True)
            i+=1
            if i>= len(vendor_lists):
                i=0
            c+=len(temp_df)
            if no_of_example!=-1 and c>=no_of_example: 
                break
                # return new_df
    return new_df


# In[86]:


print(random.uniform(15.5, 80.5))


# In[87]:


np.random.uniform(5, 35, size=11)


# In[88]:


#This will alter Open balance, Quantity, Rate, Credit and Debit column
def alter_credit_debit(master_txn_df):
    print("Updating Rate, Credit & Quantity")
    org_df=master_txn_df.copy()
    for b_id in org_df['business Id'].unique():
        df=org_df[org_df['business Id']==b_id]
        id_list = df['Transaction ID'].unique()
        for id in id_list:
            temp_df = df[df['Transaction ID']==id]
            if(len(temp_df)==2):
                credit_df = temp_df[temp_df['Credit']!='--']
                debit_df = temp_df[temp_df['Debit']!='--']
                credit_list = credit_df['Credit'].tolist()
                debit_list = debit_df['Debit'].tolist()
                if credit_list[0]==debit_list[0]:
                    random_val = credit_list[0] + round(random.uniform(1, credit_list[0]), 2)
                    debit_idx = debit_df.index[0]
                    org_df.loc[debit_idx, ['Debit']] = [random_val]
                    credit_idx = credit_df.index[0]
                    org_df.loc[credit_idx, ['Credit']] = [random_val]
            else:
                not_all_pos_quan_rate_debit = temp_df.loc[(temp_df['Quantity']=='--') &
                                                     (temp_df['Rate']=='--') &
                                                     (temp_df['Debit']!='--')]
                all_pos_quan_rate_cred = temp_df.loc[(temp_df['Quantity']!='--') &
                                                     (temp_df['Rate']!='--') &
                                                     (temp_df['Credit']!='--')]
                if len(all_pos_quan_rate_cred)==0 or len(not_all_pos_quan_rate_debit)==0:
                    continue
                all_pos_quan_rate_cred_idx = all_pos_quan_rate_cred.index
                not_all_pos_quan_rate_debit_idx = not_all_pos_quan_rate_debit.index
                random_quantity = np.random.randint(1, 100, size=len(all_pos_quan_rate_cred))
                random_rate = [round(x, 2) for x in 
                                               np.random.uniform(1, 500, size=len(all_pos_quan_rate_cred))]
                random_credit = [x*y for (x, y) in zip(random_quantity, random_rate)]
                
                credit_sum = sum(all_pos_quan_rate_cred['Credit'].tolist())
                debit_sum = sum(not_all_pos_quan_rate_debit['Debit'].tolist())
                new_debit_sum = debit_sum - credit_sum + sum(random_credit) #because there are some rows where  quantity, rate is not null 
                                                                            #and credit is null 
                org_df.loc[all_pos_quan_rate_cred_idx, ['Quantity']] = random_quantity
                org_df.loc[all_pos_quan_rate_cred_idx, ['Rate']] = random_rate
                org_df.loc[all_pos_quan_rate_cred_idx, ['Credit']] = random_credit
                org_df.loc[not_all_pos_quan_rate_debit_idx[0], ['Debit']] = new_debit_sum
    return org_df


# In[89]:


def alter_amount_open_balance(master_txn_df):
    print("Updating Open Balance")
    new_df=pd.DataFrame(columns=master_txn_df.columns)
    org_df=master_txn_df.copy()
    for b_id in org_df['business Id'].unique():
        df=org_df[org_df['business Id']==b_id]
        id_list = df['Transaction ID'].unique()
        for id in id_list:
            temp_df = df[df['Transaction ID']==id]
            credit_sum = round(temp_df[temp_df['Credit']!='--']['Credit'].sum(), 2)
            debit_sum = round(temp_df[temp_df['Debit']!='--']['Debit'].sum(), 2)
            if credit_sum!=debit_sum:
                print(temp_df)
                print("credit_sum: ", credit_sum)
                print("debit_sum: ", debit_sum)
            assert credit_sum == debit_sum
            temp_df['Amount'] = credit_sum
            temp_df['Open balance'] = round(random.uniform(1, credit_sum),2)
    #         print("Amount",  df['Amount'])
    #         print("Open Balance: ", df['Open balance'])
            new_df = pd.concat([new_df, temp_df], ignore_index=True)
        
    return new_df


# In[90]:


def alter_created_user(master_txn_df):
    print("Updating Created User")
    new_df=pd.DataFrame(columns=master_txn_df.columns)
    org_df=master_txn_df.copy()
    for b_id in org_df['business Id'].unique():
        df=org_df[org_df['business Id']==b_id]
        df['Created user'] = Faker().name()
        new_df = pd.concat([new_df, df], ignore_index=True)
    return new_df


# In[91]:


def alter_payment_method(master_txn_df, payment_method_df):
    print("Updating Payment Method")
    new_df=pd.DataFrame(columns=master_txn_df.columns)
    org_df=master_txn_df.copy()
    payment_method_list = payment_method_df['Payment method'].tolist()
    for b_id in org_df['business Id'].unique():
        df=org_df[org_df['business Id']==b_id]
        id_list = df['Transaction ID'].unique()
        for id in id_list:
            temp_df = df[df['Transaction ID']==id]
            if temp_df['payment method'].tolist()[0] in payment_method_list:
                temp_df['payment method'] = random.choice(payment_method_list)
            new_df = pd.concat([new_df, temp_df], ignore_index=True)
    return new_df


def alter_transaction_type(master_txn_df, transaction_type_list):
    print("Updating Transaction type")
    new_df=pd.DataFrame(columns=master_txn_df.columns)
    org_df=master_txn_df.copy()
    for b_id in org_df['business Id'].unique():
        df=org_df[org_df['business Id']==b_id]
        id_list = df['Transaction ID'].unique()
        for id in id_list:
            temp_df = df[df['Transaction ID']==id]
            temp_df['Transaction type'] = random.choice(transaction_type_list)
            new_df = pd.concat([new_df, temp_df], ignore_index=True)
    return new_df

# In[92]:


# no_of_example=-1
no_of_example=25000 #no_of_txn from each business
# new_df = alter_account_names(df, no_of_example)
new_master_txn_df1 = alter_credit_debit(new_master_txn_df)
new_df = alter_account_names_w_same_account_type(new_master_txn_df1, same_acc_type_diff_names_dict, no_of_example)
new_df = alter_created_and_due_date(new_df, no_of_example)
new_df = alter_user_name(new_df, customer_lists, no_of_example)
new_df = alter_vendor_names(new_df, vendor_lists, no_of_example)
new_df = alter_created_user(new_df)
new_df = alter_payment_method(new_df, payment_method)
new_df = alter_transaction_type(new_df, transaction_type_list)
final_df = alter_amount_open_balance(new_df)
print(len(final_df))
final_df


# In[ ]:


final_df['payment method'].unique()


# In[ ]:


def get_vendor_tables(vendor_df, vendor_lists, no_of_example=-1):
    col_names = list(vendor_df.columns)
    examples=[]
    business_id=2
    fake = Faker()
    c=0
    for vendor in vendor_lists:
        vendor_name = vendor
        address = fake.address()
        address = address.split('\n')
        billing_address = address[0]
        address = address[-1].split(' ')
        if len(address)>=4:
            billing_city = " ".join(address[:2]).replace(',', '')
        else: billing_city = address[0].replace(',', '')
        billing_state = address[-2]
        billing_zipcode = address[-1]
        temp_df = {col_names[0]:business_id, 
                   col_names[1]:vendor_name,
                   col_names[2]:billing_address, 
                   col_names[3]:billing_city,
                   col_names[4]:billing_state, 
                   col_names[5]:billing_zipcode,
                   col_names[6]:"--"}
        examples.append(temp_df)
        c+=1
        if c%100==0: business_id+=1 
        if no_of_example!=-1 and c>=no_of_example: 
            break
    new_df = pd.DataFrame.from_dict(examples)
    return new_df

def get_customer_tables(customer_df, customer_lists, no_of_example=100):
    col_names = list(customer_df.columns)
    examples=[]
    business_id=2
    fake = Faker()
    c=0
    while c<no_of_example:
        customer_name = customer_lists[c] #fake.name()
        address = fake.address()
        address = address.split('\n')
        billing_address = address[0]
        address = address[-1].split(' ')
        if len(address)>=4:
            billing_city = " ".join(address[:2]).replace(',', '')
        else: billing_city = address[0].replace(',', '')
        billing_state = address[-2]
        billing_zipcode = address[-1]
        
        address = fake.address()
        address = address.split('\n')
        shipping_address = address[0]
        address = address[-1].split(' ')
        if len(address)>=4:
            shipping_city = " ".join(address[:2]).replace(',', '')
        else: shipping_city = address[0].replace(',', '')
        shipping_state = address[-2]
        shipping_zipcode = address[-1]
        temp_df = {col_names[0]:business_id, 
                   col_names[1]:customer_name,
                   col_names[2]:customer_name,
                   col_names[3]:billing_address, 
                   col_names[4]:billing_city,
                   col_names[5]:billing_state, 
                   col_names[6]:billing_zipcode,
                   col_names[7]:shipping_address, 
                   col_names[8]:shipping_city,
                   col_names[9]:shipping_state, 
                   col_names[10]:shipping_zipcode,
                   col_names[11]:"--"}
        examples.append(temp_df)
        c+=1
        if c== len(customer_lists):
            break
        if c%100==0: business_id+=1 
    new_df = pd.DataFrame.from_dict(examples)
    return new_df

def get_employees_table(employees_df, employees_lists, no_of_example=100):
    col_names = list(employees_df.columns)
    examples=[]
    business_id=1
    c=0
    for emp in employees_lists:
        emp_name = emp
        emp_id = str(emp[:3].upper()) + str(np.random.randint(100,999))
        hire_date = datetime.date(random.randint(1990,2023), random.randint(1,12),random.randint(1,28)).strftime("%m/%d/%Y")
        billing_rate = '--'
        deleted = 'Yes' if random.randint(0,1) else 'No'
        temp_df = {col_names[0]:business_id, 
                   col_names[1]:emp_name,
                   col_names[2]:emp_id,
                   col_names[3]:hire_date, 
                   col_names[4]:billing_rate,
                   col_names[5]:deleted
                  }
        examples.append(temp_df)
        c+=1
        if c%100==0: business_id+=1 
        if no_of_example!=-1 and c>=no_of_example: 
            break;
    new_df = pd.DataFrame.from_dict(examples)
    return new_df

def get_product_service_table(prod_service_df, other_business_df):
    new_df=pd.DataFrame(columns=prod_service_df.columns)
    org_df=other_business_df.copy()
    for b_id, b_name in enumerate(org_df['Industry'].unique()):
        df=pd.DataFrame(columns=prod_service_df.columns)
        df['Product_Service']=org_df[org_df['Industry']==b_name]['Product_Service']
        df['Product_Service_Type'] = org_df[org_df['Industry']==b_name]['Product_Service_Type']
        df['Business Id'] = b_id+2
        new_df = pd.concat([new_df, df], ignore_index=True)
    new_df = new_df[['Business Id', 'Product_Service', 'Product_Service_Type']]
    return new_df

def get_payment_method_table(master_txn_df, payment_method_df):
    df = master_txn_df.copy()
    business_id_list = df['business Id'].unique()
    new_df=pd.DataFrame(columns=payment_method_df.columns)
    for b_id in business_id_list:
        temp_df=pd.DataFrame(columns=payment_method_df.columns)
        temp_df['Business Id'] = [b_id]*len(payment_method_df)
        c = list(zip(payment_method_df['Payment method'], payment_method_df['Credit card']))
        random.shuffle(c)
        method, card = zip(*c)
        temp_df['Payment method'] = method
        temp_df['Credit card'] = card
        new_df = pd.concat([new_df, temp_df], ignore_index=True)
    return new_df


# In[ ]:


random.randint(0,1)


# In[ ]:


new_vendor_df = get_vendor_tables(vendor_details_df, vendor_lists)
new_customer_df = get_customer_tables(customer_details_df, customer_lists, 10000)
new_employees_df = get_employees_table(employees_details_df, employees_lists, 10000)
new_product_service_df = get_product_service_table(prod_service_df, other_business_account_acc_names_and_prod)
new_payment_method = get_payment_method_table(new_master_txn_df, payment_method)
new_customer_df


# In[ ]:





# In[ ]:


final_df.to_csv('generated_data/Master_txn_table.csv')
new_vendor_df.to_csv('generated_data/vendor_table.csv')
new_customer_df.to_csv('generated_data/customer_table.csv')
new_employees_df.to_csv('generated_data/employee_table.csv')
new_product_service_df.to_csv('generated_data/product_service_table.csv')
other_business_chart_of_accounts.to_csv('generated_data/chart_of_account_OB.csv')
new_payment_method.to_csv('generated_data/payment_method.csv')


# In[ ]:




