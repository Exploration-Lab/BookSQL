import pandas as pd
import evaluate as nlp_evaluate
import re
import sqlite3
import random
from tqdm import tqdm
import sys
import numpy as np
import json

from get_exact_and_f1_score.ext_services.jsql_parser import JSQLParser
from get_exact_and_f1_score.metrics.partial_match_eval.evaluate import evaluate

_jsql_parser = JSQLParser.create()

random.seed(10001)

bleu = nlp_evaluate.load("bleu")
rouge = nlp_evaluate.load('rouge')

sqlite_path = "data/testing/updated_accounting_for_testing.sqlite"
target = "experiments/test_predictions.sql"
source = "data/test.jsonl"


def get_data(source, target):
    count,gcount=0,0
    gold_ids=[]
    gold_sql, pred_sql, questions=[],[],[]
    levels = []
    with open(source) as src:
        src_lines = src.readlines()
        for s_line in tqdm(src_lines):
            s_line=json.loads(s_line)
            ques = s_line["Title"]
            g_sql = s_line["QueryBody"].lower()
            _id = int(s_line["QuerySetId"])
            level = s_line['Levels']
            gold_ids.append(_id)
            gold_sql.append(g_sql)
            questions.append(ques)
            levels.append(level)
            gcount+=1

    pred_ids, _pred_sql=[],[]
    with open(target) as tgt:
        tgt_lines = tgt.readlines()
        for t_line in tqdm(tgt_lines):
            t_line=t_line.split()
            _id = int(t_line[0])
            p_sql = " ".join(t_line[1:])
            _pred_sql.append(p_sql)
            pred_ids.append(_id)

    for i,_id in enumerate(gold_ids):
        if _id in pred_ids:
            idx = pred_ids.index(_id)
            pred_sql.append(_pred_sql[idx])
        else:
            pred_sql.append("")
        count+=1

    assert len(gold_sql)==len(pred_sql)==len(questions)

    return gold_sql, pred_sql, questions, levels



def replace_current_date_and_now(_sql, _date):
    _sql = _sql.replace('current_date', "\'"+_date+"\'")
    _sql = _sql.replace(', now', ", \'"+_date+"\'")
    return _sql

def remove_gold_Non_exec(data,df1, sqlite_path):

    con = sqlite3.connect(sqlite_path)
    cur = con.cursor()

    out, non_exec=[], []
    new_df = df1.copy()
    new_df.loc[:, 'Exec/Non-Exec'] = 0
    for i,s in tqdm(enumerate(data)):
        _sql = str(s).replace('"', "'").lower()
        _sql = replace_current_date_and_now(_sql, '2022-06-01')
        _sql = replace_percent_symbol_y(_sql)
        try:
            cur.execute(_sql)
            res = cur.fetchall()
            out.append(i)
        except:
            non_exec.append(i)
            # print("_sql: ", _sql)

    new_df.loc[out, 'Exec/Non-Exec'] = 1
    con.close()
    return out, non_exec, new_df

def remove_data_from_index(data, ind_list):
    new_data=[]
    for i in ind_list:
        new_data.append(data[i])
    return new_data

def get_exec_match_acc(gold, pred):
    assert len(gold)==len(pred)
    count=0
    goldd = [re.sub(' +', ' ', str(g).replace("'", '"').lower()) for g in gold]
    predd = [re.sub(' +', ' ', str(p).replace("'", '"').lower()) for p in pred]

    goldd = _jsql_parser.translate_batch(goldd)
    predd = _jsql_parser.translate_batch(predd)
    pcm_f1_scores = evaluate(goldd, predd)
    pcm_em_scores = evaluate(goldd, predd, exact_match=True)

    _pcm_f1_scores, _pcm_em_scores=[], []
    for f1, em in zip(pcm_f1_scores, pcm_em_scores):
        if type(f1)==float and type(em)==float: 
            _pcm_f1_scores.append(f1)
            _pcm_em_scores.append(em)

    assert len(_pcm_f1_scores) == len(_pcm_em_scores)
    
    jsql_error_count=0 ####JSQLError
    for i, score in enumerate(pcm_f1_scores):
        if type(score)==str:
            jsql_error_count+=1

    print("JSQLError in sql: ", jsql_error_count)

    return sum(_pcm_em_scores) / len(_pcm_em_scores), sum(_pcm_f1_scores) / len(_pcm_f1_scores)


def replace_percent_symbol_y(_sql):
    _sql = _sql.replace('%y', "%Y")
    return _sql


def get_exec_results(sqlite_path, scores, df, flag, gold_sql_map_res={}):

    con = sqlite3.connect(sqlite_path)
    cur = con.cursor()

    i,j,count=0,0,0
    out,non_exec={},{}
    new_df = df.copy()
    responses=[]
    for s in tqdm(scores):
        _sql = str(s).replace('"', "'").lower()
        _sql = replace_current_date_and_now(_sql, '2022-06-01')
        _sql = replace_percent_symbol_y(_sql)
        try:
            cur.execute(_sql)
            res = cur.fetchall()
            out[i] = str(res)
        except Exception as err:
            non_exec[i]=err

        i+=1

    # if flag=='g': return out, non_exec, gold_sql_map_res
    if flag=='g': 
        new_df.loc[list(out.keys()), 'GOLD_res'] = list(out.values())
    # assert len(gold_sql_map_res)==count
    if flag=='p':
        new_df.loc[list(out.keys()), 'PRED_res'] = list(out.values())
    if flag=='d':
        new_df.loc[list(out.keys()), 'DEBUG_res'] = list(out.values())

    con.close()
    return out, non_exec, new_df

def get_scores(gold_dict, pred_dict):
    exec_count, non_exec_count=0, 0
    none_count=0
    correct_sql, incorrect_sql = [], []
    for k, res in pred_dict.items():
        if k in gold_dict:
            # print("pred_res: ", res)
            # print("gold_res: ", gold_dict[k])
            # print()
            if gold_dict[k]==str(None) or str(None) in gold_dict[k]: 
                none_count+=1
                continue
            if res==gold_dict[k]: #or ((res==None or None in res) and round(res[0], 2) == round(gold_dict[k][0], 2)):
                exec_count+=1
                correct_sql.append(k)
            else: 
                non_exec_count+=1
                incorrect_sql.append(k)
                
    return exec_count, non_exec_count, none_count, correct_sql, incorrect_sql

def get_total_gold_none_count(gold_dict):
    none_count, ok_count=0, 0
    for k, res in gold_dict.items():
        if res==str(None) or str(None) in res: 
            none_count+=1
        else: ok_count+=1
    return ok_count, none_count

gold_sql, pred_sql, questions, levels = get_data(source, target)

df = pd.DataFrame({'NLQ':questions, 'GOLD SQL':gold_sql, 'PREDICTED SQL':pred_sql, 'LEVELS':levels})
print(df.head())

test_size = len(df)
print("Total Data size: ", test_size)

pred_score = df['PREDICTED SQL'].str.lower().values
# debug_score = df['DEBUGGED SQL'].str.lower().values
gold_score1 = df['GOLD SQL'].str.lower().values


print("Checking non-exec Gold sql query")
gold_exec, gold_not_exec, new_df = remove_gold_Non_exec(gold_score1, df, sqlite_path)
print("GOLD Total exec SQL query: {}/{}".format(len(gold_exec), test_size))
print("GOLD Total non-exec SQL query: {}/{}".format(len(gold_not_exec), test_size))


prev_non_exec_df = new_df[new_df['Exec/Non-Exec'] == 0]
new_df = new_df[new_df['Exec/Non-Exec']==1]

prev_non_exec_df.reset_index(inplace=True)
new_df.reset_index(inplace=True)

#Removing Non-exec sql from data
print(f"Removing {len(gold_not_exec)} non-exec sql query from all Gold/Pred/Debug")
gold_score1 = remove_data_from_index(gold_score1, gold_exec)
pred_score = remove_data_from_index(pred_score, gold_exec)
# debug_score = remove_data_from_index(debug_score, gold_exec)
gold_score = [[x] for x in gold_score1]

assert len(gold_score) == len(pred_score) #== len(debug_score)

pred_bleu_score  = bleu.compute(predictions=pred_score, references=gold_score)
pred_rouge_score  = rouge.compute(predictions=pred_score, references=gold_score)
pred_exact_match, pred_partial_f1_score = get_exec_match_acc(gold_score1, pred_score)

# debug_bleu_score  = bleu.compute(predictions=debug_score, references=gold_score)
# debug_rouge_score  = rouge.compute(predictions=debug_score, references=gold_score)
# debug_exact_match = get_exec_match_acc(gold_score1, debug_score)


print("PREDICTED_vs_GOLD Final bleu_score: ", pred_bleu_score['bleu'])
print("PREDICTED_vs_GOLD Final rouge_score: ", pred_rouge_score['rougeL'])
# print("PREDICTED_vs_GOLD Exact Match: {}/{}".format(pred_exact_match, len(gold_score)))
# print("PREDICTED_vs_GOLD Exact Match Accuracy: ", pred_exact_match/len(gold_score))
print("PREDICTED_vs_GOLD Exact Match Accuracy: ", pred_exact_match)
print("PREDICTED_vs_GOLD Partial CM F1 score: ", pred_partial_f1_score)
print()
# print("DEBUGGED_vs_GOLD Final bleu_score: ", debug_bleu_score['bleu'])
# print("DEBUGGED_vs_GOLD Final rouge_score: ", debug_rouge_score['rougeL'])
# print("DEBUGGED_vs_GOLD Exact Match: {}/{}".format(debug_exact_match, len(gold_score)))
# print("DEBUGGED_vs_GOLD Exact Match Accuracy: ", debug_exact_match/len(gold_score))

new_df.loc[:, 'GOLD_res'] = str(None)
new_df.loc[:, 'PRED_res'] = str(None)
# new_df.loc[:, 'DEBUG_res'] = str(None)

print("Getting Gold results")
# gout_res_dict, gnon_exec_err_dict, gold_sql_map_res = get_exec_results(cur, gold_score1, 'g')
gout_res_dict, gnon_exec_err_dict, new_df = get_exec_results(sqlite_path, gold_score1, new_df, 'g')

total_gold_ok_count, total_gold_none_count = get_total_gold_none_count(gout_res_dict)
print("Total Gold None count: ", total_gold_none_count)

print("Getting Pred results")
pout_res_dict, pnon_exec_err_dict, new_df = get_exec_results(sqlite_path, pred_score, new_df, 'p')
# print("Getting Debug results")
# dout_res_dict, dnon_exec_err_dict = get_exec_results(cur, debug_score, 'd')

print("GOLD Total exec SQL query: {}/{}".format(len(gold_exec), test_size))
print("GOLD Total non-exec SQL query: {}/{}".format(len(gold_not_exec), test_size))
print()
print("PRED Total exec SQL query: {}/{}".format(len(pout_res_dict), len(pred_score)))
print("PRED Total non-exec SQL query: {}/{}".format(len(pnon_exec_err_dict), len(pred_score)))
print()
# print("DEBUG Total exec SQL query: {}/{}".format(len(dout_res_dict), len(debug_score)))
# print("DEBUG Total non-exec SQL query: {}/{}".format(len(dnon_exec_err_dict), len(debug_score)))
# print()
pred_correct_exec_acc_count, pred_incorrect_exec_acc_count, pred_none_count, pred_correct_sql, pred_incorrect_sql  = get_scores(gout_res_dict, pout_res_dict)
# debug_correct_exec_acc_count, debug_incorrect_exec_acc_count, debug_none_count, debug_correct_sql, debug_incorrect_sql   = get_scores(gout_res_dict, dout_res_dict)
# print("PRED_vs_GOLD None_count: ", total_gold_none_count)
print("PRED_vs_GOLD Correct_Exec_count without None: ", pred_correct_exec_acc_count)
print("PRED_vs_GOLD Incorrect_Exec_count without None: ", pred_incorrect_exec_acc_count)
print("PRED_vs_GOLD Exec_Accuracy: ", pred_correct_exec_acc_count/total_gold_ok_count)
print()
# print("DEBUG_vs_GOLD None_count: ", total_gold_none_count)
# print("DEBUG_vs_GOLD Correct_Exec_count without None: ", debug_correct_exec_acc_count)
# print("DEBUG_vs_GOLD Incorrect_Exec_count without None: ", debug_incorrect_exec_acc_count)
# print("DEBUG_vs_GOLD Exec_Accuracy: ", debug_correct_exec_acc_count/total_gold_ok_count)

# con.close()

# ddf1 = df[df['Exec/Non_Exec on database'] == 1]
# ddf0 = df[df['Exec/Non_Exec on database'] == 0]

# ddf1.reset_index(inplace=True)
# ddf0.reset_index(inplace=True)

# ddf1.loc[pred_correct_sql, 'PRED_vs_GOLD'] = 1
# ddf1.loc[pred_incorrect_sql, 'PRED_vs_GOLD'] = 0
# ddf0['PRED_vs_GOLD'] = None

# # ddf1.loc[debug_correct_sql, 'DEBUG_vs_GOLD'] = 1
# # ddf1.loc[debug_incorrect_sql, 'DEBUG_vs_GOLD'] = 0
# # ddf0['DEBUG_vs_GOLD'] = None

# ddf = pd.concat([ddf1, ddf0], ignore_index=True)

new_df.loc[:, 'PRED_vs_GOLD'] = 0
new_df.loc[pred_correct_sql, 'PRED_vs_GOLD'] = 1
if len(prev_non_exec_df)>0:
    prev_non_exec_df.loc[:, 'PRED_vs_GOLD'] = None
    prev_non_exec_df.loc[:, 'PRED_res']=None

    new_df = pd.concat([new_df, prev_non_exec_df], ignore_index=True).reset_index()
new_df.to_csv("experiments/test_predictions_results.csv")