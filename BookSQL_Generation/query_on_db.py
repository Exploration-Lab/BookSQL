# %%
def get_exec_results(cur, sql):
    i=0
    out={}
    non_exec={}
    for s in sql:
        try:
            cur.execute(str(s).replace('"', "'"))
            res = cur.fetchone()
            out[s]=res
        except Exception as err:
            non_exec[s]=err
        i+=1
    return out, non_exec

# %%
#connecting to DB
import sqlite3
import pandas as pd
# Create a SQL connection to our SQLite database
con = sqlite3.connect("generated_data/accounting/accounting.sqlite")
cur = con.cursor()

sql_query = pd.read_csv("generated_data/sql_pairs/sql_pairs_fold_id0.csv")
sql_query = sql_query['Sql pattern new'].tolist()

gout_res_dict, gnon_exec_err_dict = get_exec_results(cur, sql_query)

con.close()

# %%
import json
with open("generated_data/exec_sql.json", "w") as outfile:
    json.dump(gout_res_dict, outfile)
with open("generated_data/non_exec_sql.json", "w") as outfile:
    json.dump(gnon_exec_err_dict, outfile)

# %%
non_count, count=0, 0
exec_sql, non_exec_sql = [], []
for sql, res in gout_res_dict.items():
    if res==None:
        non_exec_sql.append(sql)
        non_count+=1
    elif None in res:
        non_count+=1
        non_exec_sql.append(sql)
    else: 
        count+=1
        exec_sql.append(sql)
        print(res)

# %%
count, non_count

# %%
from collections import Counter
dd = Counter(gout_res_dict.values())
dd

# %%
len(dd.keys())

# %%



