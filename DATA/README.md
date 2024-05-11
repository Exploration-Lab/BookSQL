# BookSQL (A Large Scale Text-to-SQL Dataset for Accounting Domain)

The dataset can be obtained by filling this google [form](#). After filling this form, you will get access to the dataset link in a week. Please note that data is free to use for academic research and but not for commercial usage. 


## BookSQL dataset statistics

Comparison of benchmark datasets with  BookSQL, \#Size, \#DB, \#D, and \#T/DB represent the numbers of query-SQL pairs, databases, domains, and the averaged number of tables per domain, respectively. The “-” in the \#D column indicates an unknown number of domains. Last 3 columns indicate the query types. Yelp dataset is based on Yelp website, IMDB is based on movie domain and Advising dataset is based on the University Course domain

**Dataset** | **\#Size** | **#DB** | **#D** | **#T/DB** | **Domain** | **ORDER BY** | **GROUP BY** | **NESTED**
|------|-----|-----|-----|-----|-----|-----|-----|-----|
Spider | 10,181 | 200 | 138 | 5.1 | Cross | 1335 | 1491 | 844
WikiSQL | 80,654 | 26,521 | - | 1 | Cross | 0 | 0 | 0 
Advising | 3,898 | 208 | 1 | 10 | Single  | 15 | 9 | 22
BIRD | 12,751 | 95 | 37 | 7.3 | Cross | 2576 | 881 | 0 
IMDB | 131 | 1 | 1 | 16 | Single  | 10 | 6 | 1
Yelp | 128 | 1 | 1 | 7 | Single  | 18 | 21 | 0
**BookSQL** | **100k** | **1** | **1** | **7** | **Single** | **17,529** | **11,508** | **4,456**
