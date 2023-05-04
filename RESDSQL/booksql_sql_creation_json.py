from nltk import word_tokenize, tokenize
import numpy as np
import pandas as pd
import json

def f1(df):
    res = []
    df = df.dropna()
    for i in df.values:
        i=list(i)
        d1 = {'db_id':"accounting"}
        
        d1["query"] = i[2]
        d1["query_toks"] = word_tokenize(i[2])
        d1["query_toks_no_value"] = word_tokenize(i[2].lower())
        
        d1["question"] = i[1]
        d1["question_toks"] = word_tokenize(i[1])    
        d1['Levels'] = i[3]
        res.append(d1)
        
    return res


for fold in range(3):

    # df = pd.read_csv(f'data/booksql/sql_pairs/sql_pairs_fold_id{fold}.csv')
    df = pd.read_csv(f'data/booksql/folds/test_fold/sql_pairs_fold_id{fold}.csv')

    train = df[df['split']=='train']
    test = df[df['split']=='test']
    dev = df[df['split']=='dev']
    train_json = f1(train)
    test_json = f1(test)
    dev_json = f1(dev)

    # with open(f"data/booksql/folds/fold{fold}/train.json","w") as op_file:
    #     json.dump(train_json,op_file,indent=4)
        
    with open(f"data/booksql/folds/test_fold/fold{fold}/test.json","w") as op_file:
        json.dump(test_json,op_file,indent=4)
        
    # with open(f"data/booksql/folds/fold{fold}/dev.json","w") as op_file:
    #     json.dump(dev_json,op_file,indent=4)