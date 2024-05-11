import evaluate
import re
import sqlite3

bleu = evaluate.load("bleu")
rouge = evaluate.load('rouge')

with open("/data/unified_parser_text_to_sql/eval/spider_eval.txt") as f:
    line = f.readlines()
    
    gold_score, pred_score=[], []
    for i in range(len(line)):
        if re.search("^gold: .*",line[i]):
            gold = line[i].split(":",maxsplit = 1)[1]

            if re.search("^pred: .*",line[i+1]):
                pred = line[i+1].split(":",maxsplit = 1)[1]

            pred_score.append(pred)
            gold_score.append([gold])
            bleu_score  = bleu.compute(predictions=[pred], references=[[gold]])
            rouge_score = rouge.compute(predictions=[pred], references=[[gold]])

            print(pred,gold)
            print("bleu_score: ", bleu_score['bleu'])
            print("rouge_score: ", rouge_score['rougeL'])
            # print(rouge_score)

    bleu_score  = bleu.compute(predictions=pred_score, references=gold_score)
    rouge_score  = rouge.compute(predictions=pred_score, references=gold_score)

    print("Final bleu_score: ", bleu_score['bleu'])
    print("Final rouge_score: ", rouge_score['rougeL'])




            