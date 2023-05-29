# %%
import evaluate
import re
import sqlite3
import sys

bleu = evaluate.load("bleu")
rouge = evaluate.load('rouge')

checkpoint_name = sys.argv[1]

#sede
# inp_file_path = "/workspace/DATA1/rahul/text2SQL/sede/experiments/booksql_experiment3/error_analysis.sql"
# Total test size:  1210
# Final bleu_score:  0.5077970801685224
# Final rouge_score:  0.7762963395503069
# Exact Match Accuracy:  0.18512396694214875
# "partial_match_f1": 0.7917974655927642
# "partial_match_em": 0.38602292768959434
# Exact Match: 224/1210
# Total exec SQL query: 1079/1210
# Total non-exec SQL query: 131/1210
# Exec_Accuracy:  0.7275254865616312

#resdsql
inp_file_path = f"eval_results/test/predictions/{checkpoint_name}_sql.txt"
# Total test size:  1336
# Final bleu_score:  0.5074160039403908
# Final rouge_score:  0.7309949979841709
# Exact Match: 55/1336
# Exact Match Accuracy:  0.04116766467065868
# Total exec SQL query: 1297/1336
# Total non-exec SQL query: 39/1336
# Exec_Accuracy:  0.7625289128758674
exact_match=0
count=0
print(inp_file_path)

def get_exec_match_acc(gold, pred):
    assert len(gold)==len(pred)
    count=0
    for g, p in zip(gold, pred):
        gold = str(g).replace("'", '"')
        pred = str(p).replace("'", '"')
        if gold==pred:
            count+=1
    return count

with open(inp_file_path) as f:
    lines = f.readlines()
    
    gold_score, pred_score=[], []
    for line in lines:
        line=line.split()
        if len(line)>0 and line[0] in ['Gold:', 'Pred:']:
            
    #for i in range(len(line)):
        #if re.search("^Gold:\t.*",line[i]):
            #gold = line[i].split(":\t",maxsplit = 1)[1]

            #if re.search("^Pred:\t.*",line[i+1]):
            #    pred = line[i+1].split(":\t",maxsplit = 1)[1]
            count+=1

            if line[0]=='Pred:': pred_score.append(" ".join(line[1:]))
            else: gold_score.append([" ".join(line[1:])])
            #bleu_score  = bleu.compute(predictions=[pred], references=[[gold]])
            #rouge_score = rouge.compute(predictions=[pred], references=[[gold]])

            #gold = str(line).replace("'", '"')
            #pred = str(line).replace("'", '"')
            #if gold==pred: exact_match+=1
            #if count%100==0:
            #    print("i: ", count)
            #    print()

            # print("pred: ", str(pred).replace("'", '"'))
            # print("gold: ", str(gold).replace("'", '"'))
        #     if count==5: break
        # if count==5: break
            # print("bleu_score: ", bleu_score['bleu'])
            # print("rouge_score: ", rouge_score['rougeL'])
            # print()
            # print(rouge_score)
            
    gold_score1 = [item[0] for item in gold_score]
    exact_match = get_exec_match_acc(gold_score1, pred_score)

    bleu_score  = bleu.compute(predictions=pred_score, references=gold_score)
    rouge_score  = rouge.compute(predictions=pred_score, references=gold_score)

    print("Total test size: ", len(gold_score))
    print("Final bleu_score: ", bleu_score['bleu'])
    print("Final rouge_score: ", rouge_score['rougeL'])
    print("Exact Match: {}/{}".format(exact_match, len(gold_score)))
    print("Exact Match Accuracy: ", exact_match/len(gold_score))


# %% [markdown]
# Total test size:  1000
# Final bleu_score:  0.6979045536010703
# Final rouge_score:  0.7387873891017711
# Exact Match: 235/1000
# Exact Match Accuracy:  0.235

# %%


# %%
# pip install evaluate

# %%


# %%
import pandas

# %%
# pip install rouge_score

# %%
def get_exec_results(cur, scores):
    i=0
    out={}
    non_exec={}
    for s in scores:
        try:
            cur.execute(str(s).replace('"', "'"))
            res = cur.fetchone()
            out[i]=res
        except Exception as err:
            non_exec[i]=err
        i+=1
    return out, non_exec

def get_scores(gold_dict, pred_dict):
    exec_count, non_exec_count=0, 0
    for k, res in pred_dict.items():
        if k in gold_dict:
            if res==None or None in res: continue
            if res==gold_dict[k]:
                exec_count+=1
                # print("res: ", res)
            else: non_exec_count+=1
                
    return exec_count, non_exec_count

# %%
#connecting to DB
import sqlite3
# Create a SQL connection to our SQLite database
con = sqlite3.connect("data/booksql/database/accounting/accounting.sqlite")
cur = con.cursor()

gold_score1 = [item[0] for item in gold_score]
print("Getting Gold results")
gout_res_dict, gnon_exec_err_dict = get_exec_results(cur, gold_score1)
print("Getting Pred results")
pout_res_dict, pnon_exec_err_dict = get_exec_results(cur, pred_score)


print("Total exec SQL query: {}/{}".format(len(pout_res_dict), len(pred_score)))
print("Total non-exec SQL query: {}/{}".format(len(pnon_exec_err_dict), len(pred_score)))

exec_acc_count, non_exec_count  = get_scores(gout_res_dict, pout_res_dict)
print("Exec_Accuracy: ", exec_acc_count/len(pout_res_dict))

con.close()

