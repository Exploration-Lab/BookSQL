#!/bin/bash

#requirement:
#./data/spider
#./BART-large

# data/spider -> data/spider_schema_linking_tag
# python step1_schema_linking.py --dataset=spider

# data/spider_schema_linking_tag -> dataset_post/spider_sl
# python step2_serialization.py

###training
python train.py --dataset_path /data/unified_parser_text_to_sql/dataset_post/accounting_sl/bin  --exp_name booksql_mbart_sl_v2  --models_path ./models  --total_num_update 1000  --max_tokens 1024 --finetune /data/unified_parser_text_to_sql/models/spider_sl/model.pt
###evaluate
python3 step3_evaluate.py --dataset_path /data/unified_parser_text_to_sql/dataset_post/accounting_sl --constrain