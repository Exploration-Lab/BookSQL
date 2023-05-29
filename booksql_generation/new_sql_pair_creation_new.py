# %%
import numpy as np
import pandas as pd
import re
import random
from nltk.stem import WordNetLemmatizer
from sklearn.model_selection import train_test_split
from datetime import date, timedelta, datetime
from tqdm import tqdm
lemmatizer = WordNetLemmatizer()

# %%
df = pd.read_csv("data/dataset details new.xlsx - sample questions.csv")

df = df[:183]
df.tail()

# %%
df.columns

# %%
uniq_temp=set([])
for ques in df['question']:
    attributes = re.findall(r'\[.*?\]', str(ques))
    # if len(attributes)>=3:
        # print(ques) 
        # print(df[df['question']==ques]['sql'].values)
        # print()
    for attr in attributes:
        uniq_temp.add(attr)
uniq_temp

# %%
df.rename(columns = {'question':'Query Pattern','sql':'Sql pattern'}, inplace = True)

# %%
master_txn_table = pd.read_csv("generated_data/Master_txn_table.csv")
customers = pd.read_csv("generated_data/customer_table.csv")
customer_master_merge = pd.merge(customers,master_txn_table,on = "Customer name")

products = vendors = accounts = master_txn_table.copy()
employee = pd.read_csv("generated_data/employee_table.csv")
date_ranges = pd.read_csv("data/dataset details.xlsx - sample date ranges.csv")
date_ranges["sql"] = date_ranges["sql"].replace(r"\n","",regex=True)

ignore_keys = ["sample", "test", "quickbooks", "unknown", "my company", "customer", "cash", "sale", "deposit", ".", "payroll", "anonymous"]

# %%
master_txn_table.columns

# %%
master_txn_table_columns = ['business Id', 'Transaction ID', 'Transaction date', 'Transaction type',
       'Amount', 'Created date', 'Created user', 'Account', 'A/R paid',
       'A/P paid', 'Due date', 'Open balance', 'PO status', 'Estimate status',
       'Customer name', 'Vendor name', 'Product_Service', 'Quantity', 'Rate',
       'Credit', 'Debit', 'Sale', 'Purchase', 'Billable', 'Invoiced',
       'Cleared', 'payment method', 'Misc (Business specific fields)']

# %%
print("customers shape: ", customers.shape)
print("products shape: ", products.shape)
print("vendors shape: ", vendors.shape)
print("accounts shape: ", accounts.shape)
print("employee shape: ", employee.shape)
print("date_ranges shape: ", date_ranges.shape)


# %%
def clean_names(df, var):
    flag = df[var].apply(lambda x: sum([y in x for y in ignore_keys]))
    df = df[flag == 0].reset_index(drop = True)
    return df

# %%
def stem_tokens(x):
    return " ".join([lemmatizer.lemmatize(y) for y in x.lower().split(" ")])

# %%
def get_variants(x):
    return np.array([x])
    # variants = [x.lower()]
    # variants.append(stem_tokens(x))
    # if "&" in x:
    #     x0 = x.split("&")[0].strip().lower()
    #     x1 = x.split("&")[1].strip().lower()
    #     variants.append(x0)
    #     variants.append(stem_tokens(x0))
    #     variants.append(x1)
    #     variants.append(stem_tokens(x1))
    # if "|" in x:
    #     x0 = x.split("|")[0].strip().lower()
    #     x1 = x.split("|")[1].strip().lower()
    #     variants.append(x0)
    #     variants.append(stem_tokens(x0))
    #     variants.append(x1)
    #     variants.append(stem_tokens(x1))
    # variants = np.unique(variants)
    # return variants

# %%
def choose_random_attribute(filter_by_attribute):
    return random.sample(filter_by_attribute[random.sample(sorted(filter_by_attribute), 1)[0]].tolist(), 1)[0]

# %%
customers = clean_names(customers, "Customer name")
products = clean_names(products, "Product_Service")
vendors = clean_names(vendors, "Vendor name")
accounts = clean_names(accounts, "Account")
employee = clean_names(employee, "Employee name")

# %%
customers["Variants"] = customers["Customer name"].apply(lambda x: get_variants(x))
products["Variants"] = products["Product_Service"].apply(lambda x: get_variants(x))
vendors["Variants"] = vendors["Vendor name"].apply(lambda x: get_variants(x))
accounts["Variants"] = accounts["Account"].apply(lambda x: get_variants(x))
employee["Variants"] = employee["Employee name"].apply(lambda x: get_variants(x))
print("completed")

# %%
# K = 50

aggregation_entity = ["total", "average", "mean", "max", "min", "first", "last", "highest", "lowest"]

intents = ["sales", "expense", "invoice", "bill", "account payable", "account receivable"]   #txn_type,

date_filter_entity = date_ranges["sample date ranges in questions"].tolist()
date_sql_entity = dict(zip(date_ranges["sample date ranges in questions"], date_ranges["sql"]))

filter_by_city = list(customer_master_merge['Billing city'].unique())

filter_by_invoice_number = list(master_txn_table['Transaction ID'].unique())

filter_by_paymentmethod = list(master_txn_table["payment method"].unique())

filter_by_number = [i for i in range(1,11)]
filter_by_percentage = [i for i in range(1,101)]

filter_by_customer = customers.set_index("Customer name").to_dict()["Variants"]

filter_by_product = products.set_index("Product_Service").to_dict()["Variants"]

filter_by_vendor = vendors.set_index("Vendor name").to_dict()["Variants"]          #salesperson_name

filter_by_account = accounts.set_index("Account").to_dict()["Variants"]

filter_by_employee = employee.set_index("Employee name").to_dict()["Variants"]

group_by_entity = ["account", "vendor", "customers", "product_service"]



del filter_by_product['--']
del filter_by_vendor['--']

# %%
# filter_by_product["--"]

# %%
# filter_by_paymentmethod,filter_by_product,filter_by_vendor

# %%


# %%
# attributes_list = df["Query Pattern"].apply(lambda x:  re.findall(r'\[.*?\]', str(x) ))
# attributes_list = attributes_list.apply(lambda x: [y.replace("[", "").replace("]", "") for y in x])
# attributes_list = [x for y in attributes_list for x in y]
# pd.Series(attributes_list).value_counts()

# %%
attributes_dict = {
    "date_filter": date_filter_entity,
    "customer_name": filter_by_customer,
    "vendor_name": filter_by_vendor,
    "product_name": filter_by_product,
    "aggregation_entity": aggregation_entity,
    "account_name": filter_by_account,
    "employee_name": filter_by_employee,
    "groupby_entity": group_by_entity,
    #
    # "txn_type": intents,
    "transaction_type":intents,
#     "salesperson_name": filter_by_vendor

    "city": filter_by_city,
    "invoice_number": filter_by_invoice_number,
    "number": filter_by_number,
    "percentage": filter_by_percentage,
    "payment_method" : filter_by_paymentmethod,
}

# %%
def choose_random_attribute(attribute_dict):
    return random.sample(attribute_dict[random.sample(sorted(attribute_dict), 1)[0]].tolist(), 1)[0]

# %%
def get_aggregation(query):
    if any(word in query for word in ["average", "mean"]):
        return "avg"
    elif any(word in query for word in ["max", "last", "highest"]):
        return "max"
    elif any(word in query for word in ["min", "first", "lowest"]):
        return "min"
    else:
        return "sum"

# %%
def f1(query_pattern,d_word,is_sql=0):
    attributes = re.findall(r'\[.*?\]', str(query_pattern))
    
    # print("att: ",attributes)  #ex - ['[customer_name]', '[date_filter]']
    # print("word: ",d_word)
    
#     assert len(attributes) == len(word)

#     print("asdasdasdas      ",d_word)
#     print("its attr : " , attributes)
#     print()
#     return ""
    
    

    for a in attributes:
        
        a_cleaned = re.sub(r"[\[\]]", "", a)

        new_word = d_word[0][a_cleaned]

        if is_sql == 1 and a_cleaned == "aggregation_entity" :
            new_word = get_aggregation(new_word)
        
        elif is_sql == 1 and a_cleaned == "date_filter":                          #"entity" above dict
            new_word = date_sql_entity[new_word]
            a = '"' + a + '"'
        elif is_sql == 1 and a_cleaned == "number":                          #"entity" above dict
            new_word = filter_by_number[new_word-1]
            a = '"' + a + '"'
        elif is_sql == 1 and a_cleaned == "percentage":                          #"entity" above dict
            new_word = filter_by_percentage[new_word-1]
            a = '"' + a + '"'
        elif is_sql == 1 and a_cleaned == "invoice_number":                          #"entity" above dict
            a = '"' + a + '"'
            # print("a: ", a) #a: "[date_filter]"
            # print("new_word: ", new_word) #new_word:  BETWEEN date(current_date, 'start of year','+3 month') AND date(current_date, 'start of year', '+6 month', '-1 day')
            # print("query_pattern: ", query_pattern) #query_pattern:  select distinct transaction_id, amount from master_txn_table where transaction_date "[date_filter]"
            # print("qq: ", query_pattern.replace(a, new_word)) # qq:  select distinct transaction_id, amount from master_txn_table where transaction_date BETWEEN date(current_date, 'start of year','+3 month') AND date(current_date, 'start of year', '+6 month', '-1 day')
            
            # print("new word: ",new_word)
            # print("new_word: ", d_word[0])
            # # exit()
            # new_word = new_word.values

        # print("new_word: ", new_word) #ex- new_word:  Christopher Hart

        query_pattern = query_pattern.replace(a, str(new_word))
        # try:
        #     query_pattern = query_pattern.replace(a, str(new_word))
        # except:
        #     print(f"query_pattern : {query_pattern}")
        #     print(f"num : {new_word} and attr : {a}")
        #     pass
            
        
#     for a,w in zip(attributes,word) :
#         a_cleaned = re.sub(r"[\[\]]", "", a)
#         query_pattern = query_pattern.replace(a, d_word[a])
# #     print("$$$$",query_pattern)
    # print("query_pattern: ", query_pattern) #ex - query pattern is both sql and question 
                        #ex - query_pattern:  How much money does customer Christopher Hart still owe? 
                        # query_pattern: select sum(open_balance) from ( select distinct transaction_id, open_balance from master_txn_table where customers = "Christopher Hart" )
    return query_pattern

# %%
# re.sub(r"[\[\]]", "", 'klsd "[date_filter]"')
re.findall(r'\[.*?\]', "jklsdnjd '[date_filter]'")

# %%
h = {"a":10, "b":11 , "c":12}


a,b = list(h.items())[1]
b

# %%
master_txn_table.head()

# %% [markdown]
# 

# %%
master_txn_table_subset = master_txn_table.copy()

# %%
def select_third_col_value(attr_mapp , third_col, flag_txntype,txn_val):
    #attr_mapp : {"col_name" : "col_value"}
    global master_txn_table_subset
    name_dict = {"account_name": "Account" , "customer_name":"Customer name","vendor_name":"Vendor name","product_name":"Product_Service"}
    first_col,first_val = list(attr_mapp.items())[0]
    second_col,second_val = list(attr_mapp.items())[1]

    #changing filters in column names
    if first_col in name_dict.keys(): first_col = name_dict[first_col]
    if second_col in name_dict.keys(): second_col = name_dict[second_col]
    if third_col in name_dict.keys(): third_col = name_dict[third_col]

    #making a subset of dataframe
    if flag_txntype == 0:
        master_txn_table_subset = master_txn_table_subset.loc[(master_txn_table_subset[first_col].str.lower() == first_val.lower()) & 
                                    (master_txn_table_subset[second_col].str.lower() == second_val.lower()) ]
    else:
        master_txn_table_subset = master_txn_table_subset.loc[(master_txn_table_subset[first_col].str.lower() == first_val.lower()) & 
                                    (master_txn_table_subset[second_col].str.lower() == second_val.lower()) & 
                                    (master_txn_table_subset["Transaction type"].str.lower() == txn_val)]
        

    val = list(master_txn_table_subset[third_col].values)
    return random.sample(val,1)[0]


# %%
def select_first_based_on_txn_type(a_cleaned, txn_val):
    global master_txn_table_subset
    name_dict = {"account_name": "Account" , "customer_name":"Customer name","vendor_name":"Vendor name","product_name":"Product_Service"}
    if a_cleaned in name_dict.keys(): a_cleaned = name_dict[a_cleaned]

    master_txn_table_subset = master_txn_table_subset.loc[master_txn_table_subset["Transaction type"].str.lower() == str(txn_val).lower()]
    a = ""
    try:
        val = list(master_txn_table_subset[a_cleaned].values)
        a = random.sample(val,1)[0]
    except:
        print("val :" ,val)
    
    # return random.sample(val,1)[0]
    return a

# %%
s = 'select distinct transaction_id from master_txn_table where transaction_type = "bill" and customers = "[customer_name]" and product_service = "[product_name]" and transaction_date "[date_filter]"'

s = s.split(" ")
i = s.index("transaction_type")

s[i],s[i+1],s[i+2][1:-1] 


# %%

def select_second_col_value(first_value,first_col,second_col, flag_txntype,txn_val):
    global master_txn_table_subset
    name_dict = {"account_name": "Account" , "customer_name":"Customer name","vendor_name":"Vendor name","product_name":"Product_Service"}
    
    #changing filters in column names
    if first_col in name_dict.keys(): first_col = name_dict[first_col]
    if second_col in name_dict.keys(): second_col = name_dict[second_col]

    #making a subset of dataframe
    if flag_txntype == 0:
        master_txn_table_subset = master_txn_table_subset.loc[master_txn_table_subset[first_col].str.lower() == first_value.lower()]    
    else:

        master_txn_table_subset = master_txn_table_subset.loc[(master_txn_table_subset[first_col].str.lower() == first_value.lower()) 
                                      & (master_txn_table_subset["Transaction type"].str.lower() == txn_val)]    
    # print("subset shape : ",subset.shape)
    # print("col : {} value : {}".format(first_col,first_value))

    val = list(master_txn_table_subset[second_col].values)
    
    return random.sample(val,1)[0]


# def replace_attributes(query_pattern):
def replace_attributes(query_pattern,sql_pattern):
    global master_txn_table_subset
    master_txn_table_subset =  master_txn_table.copy()
    temp = []        # list of templae:value pairs for each sqlquestion
    d = {}           #values for both templates
    attributes = re.findall(r'\[.*?\]', str(query_pattern))

    # print("attr : ",attributes) # ['[customer_name]', '[date_filter]']

    ls1 = sql_pattern.split(" ")
    try:
        ind = ls1.index("transaction_type")
        if(ind != -1 and ls1[ind+1] == "="):
            ind +=2
    except:
        ind = -1
  
    flag_txntype = 0
    txn_val = ""
    if ind != -1 and ls1[ind][1:-1] in ["payment","invoice","bill","purchase order"]:
        flag_txntype = 1
        txn_val = ls1[ind][1:-1]
    
    count  = 0

    # print("query pattern : " , query_pattern)
    # print("sql pattern : ",sql_pattern)
    
    for a in attributes:
        a_cleaned = re.sub(r"[\[\]]", "", a)
        
        # print("a_cleaned attr : " , a_cleaned)
        # print("dict : " , d)


        if type(attributes_dict[a_cleaned]) == list:
            
            # for first template and for a_cleaned of second template also and if first template was among these then for second template we take directly randomly
            if count == 0 or a_cleaned in ("aggregation_entity","groupby_entity","date_filter","number","payment_method","city","invoice_number","percentage") or (len(d) > 0 and list(d.keys())[0] in ("aggregation_entity","groupby_entity","date_filter","number","invoice_number","percentage")):
                if flag_txntype == 0 or a_cleaned in ("aggregation_entity","groupby_entity","date_filter","number","payment_method","city","invoice_number","percentage") or (len(d) > 0 and list(d.keys())[0] in ("aggregation_entity","groupby_entity","date_filter","number","invoice_number","percentage")):
                    select_attribute = random.sample(attributes_dict[a_cleaned], 1)[0]
                else:
                    select_attribute = select_first_based_on_txn_type(a_cleaned, txn_val)

            elif count == 1:
                select_attribute = select_second_col_value(list(d.values())[0] ,list(d.keys())[0] , a_cleaned , flag_txntype,txn_val)
            else:
                select_attribute = select_third_col_value(d , a_cleaned, flag_txntype,txn_val)
            
        else:

            if count == 0 or a_cleaned in ("aggregation_entity","groupby_entity","date_filter","number","payment_method","city","invoice_number","percentage") or (len(d) > 0 and list(d.keys())[0] in ("aggregation_entity","groupby_entity","date_filter","number","invoice_number","percentage")):
                # select_attribute = choose_random_attribute(attributes_dict[a_cleaned])
                if flag_txntype==0 or a_cleaned in ("aggregation_entity","groupby_entity","date_filter","number","payment_method","city","invoice_number","percentage") or (len(d) > 0 and list(d.keys())[0] in ("aggregation_entity","groupby_entity","date_filter","number","invoice_number","percentage")):
                    select_attribute = choose_random_attribute(attributes_dict[a_cleaned])
                else:
                    # print("here : 1")
                    select_attribute = select_first_based_on_txn_type(a_cleaned, txn_val)
            elif count == 1:
                # print("here : 4")
                select_attribute = select_second_col_value(list(d.values())[0] ,list(d.keys())[0] , a_cleaned , flag_txntype,txn_val)
            else:
                # print("here : 5")
                select_attribute = select_third_col_value(d , a_cleaned, flag_txntype,txn_val)

            # we need to add ("percentage","invoice_number","city") if we add more templates of type double template per query
            # print("a_cleaned attr : " , a_cleaned)
            # print("select_attribute: ", select_attribute)
            # print("*********")

#         query_pattern = query_pattern.replace(a, select_attribute)
#         temp.append(select_attribute)
        
        d[a_cleaned]  =  select_attribute

        count +=1
    
    temp.append(d)
    # print("temp : " , temp)
    # print("*****")
    # print()
    # print()
    return temp

# %%
df.head()

# %%
master_txn_table.columns

# %%
def adding_rows(dict_attr, transaction_type_val, ar_unpaid, account_type_val):

    sample = master_txn_table.copy()
    name_dict = {"account_name": "Account" , "customer_name":"Customer name","vendor_name":"Vendor name","product_name":"Product_Service", "invoice_number":"Transaction ID"}

    sample = master_txn_table.loc[master_txn_table["Transaction ID"] ==  random.choice(master_txn_table["Transaction ID"].unique())]

    for col,val in dict_attr.items():
        if col in name_dict.keys(): 
            col = name_dict[col]
            sample.loc[:, col] = val

        if col == "date_filter":
            cur_transaction_date = datetime.strptime(date_ranges[date_ranges['sample date ranges in questions']==val]['Fixed Date'].values[0], '%Y-%m-%d').date()
            new_created_date = cur_transaction_date + timedelta(days=random.randint(10, 365))
            new_due_date = new_created_date + timedelta(days=random.randint(10, 365))
            sample.loc[:, 'Transaction date'] = [str(cur_transaction_date)]*len(sample)
            sample.loc[:, 'Created date'] = [str(new_created_date)]*len(sample)
            sample.loc[:, 'Due date'] = [str(new_due_date)]*len(sample)
            # print(sample)

    if len(transaction_type_val)>0:
        # print("transaction_type_val: ", transaction_type_val)
        sample.loc[:, 'Transaction type'] = transaction_type_val

    if ar_unpaid==1:
        sample.loc[:, 'A/R paid'] = 'unpaid'
    
    if len(account_type_val)>0:
        sample.loc[:, 'Account'] = account_type_val
    
    
    # sample.loc[:,"Transaction ID"] = max(master_txn_table["Transaction ID"]) + int(random.choice(range(1,10)))
    return sample


# %%
new_df = pd.DataFrame(columns=master_txn_table_columns)


def get_transaction_value(sql):
    transaction_type_values=''
    transaction_type_match = re.search(r"transaction_type\s*=\s*['\"](.*?)['\"]", sql)
    if transaction_type_match:
        transaction_type_values = transaction_type_match.group(1)
        # print(f"Transaction Type: {transaction_type}")

    transaction_type_in_match = re.search(r"transaction_type\s+in\s*\(\s*(.*?)\s*\)", sql)
    if transaction_type_in_match:
        transaction_type_values = re.findall(r"['\"](.*?)['\"]", transaction_type_in_match.group(1))[0]
        # print(f"Transaction Type Values: {', '.join(transaction_type_values)}")
        # print(transaction_type_values)
    
    return transaction_type_values

def get_account_types(sql):
    account_type_values=""
    account_type_match = re.search(r'account_type\s+in\s*\(\s*(.*?)\s*\)', sql)
    if account_type_match:
        account_type_values = re.findall(r"['\"](.*?)['\"]", account_type_match.group(1))[0]
    return account_type_values

def simulate_questions(n,df_1):
    # df_sample = df[~df["Query Pattern"].apply(lambda x: "salesperson_name" in x)].reset_index(drop=True)
    df_sample = df_1.copy()
    global new_df
    
    df_simulated = df_sample.loc[random.choices(range(len(df_sample)), k=n)].reset_index(drop=True)
    # df_simulated = df_sample.loc[np.arange(len(df_sample))].reset_index(drop=True)
    
#     df_simulated["Query"] = df_simulated["Query Pattern"].apply(lambda x: replace_attributes(x))
    
#     df_simulated["Sql pattern new"] = df_simulated["Sql pattern"].apply(lambda x: replace_attributes(str(x)))
#     df_simulated.loc[df_simulated["Aggregation"].isna(), "Aggregation"] = df_simulated[df_simulated["Aggregation"].isna()]["Query"].apply(lambda x: get_aggregation(x))
    
    ls1 = df_simulated.apply(lambda x: replace_attributes(x['Query Pattern'], x['Sql pattern']), axis=1).to_list()
    # print(ls1)
    
    # print(ls1)
    df_simulated["Query"] = np.nan
    df_simulated["Sql pattern new"] = np.nan
    

    for i in range(len(ls1)):
        
        # print("asdasdas  ",i,ls1[i])
        # print(df_simulated.loc[i].to_list())
        # print()

        df_simulated.loc[[i],["Query"] ] = f1(df_simulated.iloc[i]["Query Pattern"],ls1[i])
        df_simulated.loc[[i],["Sql pattern new"] ] = f1(df_simulated.iloc[i]["Sql pattern"],ls1[i],is_sql=1)

        # print(df_simulated.values)


        _sql = df_simulated.iloc[i]["Sql pattern"].lower().replace('"',"'")
        transaction_val, account_type_val='', ''
        ar_unpaid=0
        if 'transaction_type' in df_simulated.iloc[i]["Sql pattern"]:
            # print("transaction sql: ", df_simulated.iloc[i]["Sql pattern"].replace('"',"'"))
            transaction_val = get_transaction_value(_sql)

        if "ar_paid = 'unpaid'" in _sql:
            ar_unpaid=1
        
        if "account_type" in _sql:
            account_type_val = get_account_types(_sql)


        #adding new rows to master txn table
        sample = adding_rows(ls1[i][0], transaction_val, ar_unpaid, account_type_val)
        sample = sample[master_txn_table_columns]
        new_df =  pd.concat([new_df,sample], ignore_index=True)

        # if 'percentage' in ls1[i][0].keys() or 'number' in ls1[i][0].keys():
        #     print("asdasdas  ",i,ls1[i])
        #     print(df_simulated.loc[[i], ["Query"] ].values)
        #     print(df_simulated.loc[[i], ["Sql pattern new"] ].values)
        #     print()

    
    print("len(new_df): ", len(new_df))
    
    return df_simulated

# %% [markdown]
# ***generated master_txn_table had 810059rows before adding new rows.**

# %%
# temp_df = pd.DataFrame([df.iloc[26,:]], columns = df.columns).reset_index()


# t_df = simulate_questions(1,temp_df)
# t_df.values

# %%
master_txn_table.shape     

# %%
# df_simulated = simulate_questions(10000,df)

for fold_id in range(1):
    print("Fold id: ", fold_id)
    df = pd.read_csv(f"generated_data/template_basis_split/fold_{fold_id}.csv")
    final_df=pd.DataFrame(columns=['Query','Sql pattern new', 'Levels', 'split'])                                   #100k => 10^5
    total_samples = 10**5
    for c_type, n_sample in tqdm(zip(['easy', 'medium', 'hard'], [int(0.1 * total_samples) , int(0.45 * total_samples), int(0.45 * total_samples)])):
        # df = df.loc[df["split"] == s_type]
        df_1 = df.loc[df['Levels'] == c_type]
        df_1.reset_index(inplace=True)
        df_simulated = simulate_questions(n_sample, df_1)
        df_simulated["Sql pattern"] = df_simulated["Sql pattern"].replace(r"\n","",regex=True)
        df_simulated["Sql pattern new"] = df_simulated["Sql pattern new"].replace(r"\n","",regex=True)
        new_df1 = df_simulated[['Query','Sql pattern new', 'Levels', 'split']]
        final_df = pd.concat([final_df, new_df1], ignore_index=True)
    final_df.to_csv(f"generated_data/testing/temp_sql_pairs_fold_id{fold_id}.csv")
print("Completed")

# %%
# print(new_df.head())
new_df = new_df[master_txn_table_columns]
master_txn_table1 = master_txn_table[master_txn_table_columns]

# %%
master_txn_table1 =  pd.concat([master_txn_table1,new_df], ignore_index=True)
master_txn_table1.to_csv("generated_data/new_Master_txn_table.csv")

# %%
print("Creating database now")
import os
os.system('python database_creation.py')


# %%
temp = []

#connecting to DB
import sqlite3
import re
import pandas as pd
from tqdm import tqdm

# Create a SQL connection to our SQLite database
# con = sqlite3.connect("generated_data/accounting/accounting.sqlite")
con = sqlite3.connect("generated_data/testing/accounting_for_testing.sqlite")
final_df = pd.read_csv("generated_data/testing/temp_sql_pairs_fold_id0.csv")
# final_df = df_simulated

cur = con.cursor()

# The result of a "cursor.execute" can be iterated over by row
# for row in cur.execute('SELECT * FROM species;'):
#     print(row)
results=[]
j=0
for i in tqdm(final_df["Sql pattern new"].to_list()):
    # print(j)
    # print(i)
    # print()
    i = re.sub(r'\bcurrent_date\b', "'2022-06-01'", i)
    i = re.sub(r'\bnow\b', "'2022-06-01'", i)
    i = str(i).lower().replace('"', "'")
    i = i.replace("%y", "%Y")
    try:
        cur.execute(i)
        res = cur.fetchone()
        # if res is None or None in res:
        #     print(i, res)
        #     exit()
        results.append({(j,i):res})
    except:
        temp.append([j,i])
        print(i)
        # exit()
        # print(j)
        # print(i)
        # print()
    
    j+=1

# Be sure to close the connection
con.close()


# %%
temp

# %%
len(temp), len(results)

# %%
# con = sqlite3.connect("generated_data/testing/accounting_for_testing.sqlite")

# cur = con.cursor()
# cur.execute("select * from master_txn_table where customers = 'kristen allen' group by product_service having count(distinct strftime('%m', transaction_date)) >= 0")
# res = cur.fetchone()
# print(res)

# %%
# s="select transaction_date from (select distinct transaction_id, transaction_date from master_txn_table where customers='david mccormick' and transaction_type = \'invoice\')"
import re
s="select date(transaction_date, \'start of month\'), sum(debit) from master_txn_table  as t1 join chart_of_accounts as t2 on t1.account = t2.account_name wherecurrent_date vendor = 'david allen' and account_type in (\'expense\',\'other expense\') group by date(transaction_date, current_date, \'start of month\')"
s=s.replace('"',"'")
re.sub(r'\bcurrent_date\b', "'2022-06-01'", s)
# s

# %%
master_txn_table1.columns

# %%
none_count=0
for r in results:
    if None in r.values():
        print(list(r.keys())[0][0])
        print(list(r.keys())[0][1])
        print()
        none_count+=1
print("none_count: ", none_count)

# %%

for i in temp:
    # if i[0]< 141:
    #     continue
    print(i[0], end = ' ')
    print(i[1])

# %%
# final_df.iloc[189].to_list()

# %%
len(temp)

# %%



