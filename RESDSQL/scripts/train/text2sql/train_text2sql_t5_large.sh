# set -e

# # train text2sql-t5-large model
# python -u text2sql.py \
#     --batch_size 16 \
#     --gradient_descent_step 2 \
#     --device "0" \
#     --learning_rate 5e-5 \
#     --epochs 128 \
#     --seed 42 \
#     --save_path "./models/text2sql-t5-large" \
#     --tensorboard_save_path "./tensorboard_log/text2sql-t5-large" \
#     --model_name_or_path "t5-large" \
#     --use_adafactor \
#     --mode train \
#     --train_filepath "./data/preprocessed_data/resdsql_train_spider.json"

# # select the best text2sql-t5-large ckpt
# python -u evaluate_text2sql_ckpts.py \
#     --batch_size 12 \
#     --device "0" \
#     --seed 42 \
#     --save_path "./models/text2sql-t5-large" \
#     --eval_results_path "./eval_results/text2sql-t5-large" \
#     --mode eval \
#     --dev_filepath "./data/preprocessed_data/resdsql_dev.json" \
#     --original_dev_filepath "./data/spider/dev.json" \
#     --db_path "./database" \
#     --num_beams 8 \
#     --num_return_sequences 8 \
#     --target_type "sql"


#"models/text2sql-t5-large/checkpoint-30576" \
set -e
fold_id=0
# train text2sql-t5-large model
# python -u text2sql.py \
#     --batch_size 4 \
#     --gradient_descent_step 2 \
#     --device "2" \
#     --learning_rate 5e-5\
#     --epochs 50 \
#     --seed 42 \
#     --save_path "models/unisar-based-booksql-t5-large" \
#     --tensorboard_save_path "tensorboard_log/booksql-t5-base" \
#     --model_name_or_path "t5-large" \
#     --use_adafactor \
#     --mode train \
#     --train_filepath "data/booksql/folds/fold$fold_id/unisar_based_ip_data/resdsql_train_booksql.json" \
#     --dev_filepath "data/booksql/folds/fold$fold_id/unisar_based_ip_data/resdsql_dev.json" \
#     --original_dev_filepath "data/booksql/folds/fold$fold_id/unisar_based_ip_data/dev.json" \
#     --db_path "data/booksql/database" \
#     --num_beams 8 \
#     --num_return_sequences 8 \
#     --target_type "sql"
    
# # select the best text2sql-t5-large ckpt
# python -u evaluate_text2sql_ckpts.py \
#     --batch_size 4 \
#     --device "2" \
#     --seed 42 \
#     --save_path "models/unisar-based-booksql-t5-large" \
#     --eval_results_path "eval_results/booksql-t5-large/unisar-based" \
#     --mode eval \
#     --dev_filepath "data/booksql/folds/fold$fold_id/unisar_based_ip_data/resdsql_test.json" \
#     --original_dev_filepath "data/booksql/folds/fold$fold_id/unisar_based_ip_data/test.json" \
#     --db_path "data/booksql/database" \
#     --num_beams 8 \
#     --num_return_sequences 8 \
#     --target_type "sql"

# select the best text2sql-t5-large ckpt
python -u evaluate_text2sql_ckpts.py \
    --batch_size 2 \
    --device "3" \
    --seed 42 \
    --save_path "models/unisar-based-booksql-t5-large" \
    --best_checkpoint_name "epoch-3" \
    --eval_results_path "eval_results/booksql-t5-large/unisar-based" \
    --mode eval \
    --dev_filepath "data/booksql/folds/fold$fold_id/unisar_based_ip_data/resdsql_test.json" \
    --original_dev_filepath "data/booksql/folds/fold$fold_id/unisar_based_ip_data/test.json" \
    --db_path "data/booksql/database" \
    --num_beams 8 \
    --num_return_sequences 8 \
    --target_type "sql"