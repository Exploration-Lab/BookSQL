# set -e

# # train text2sql-t5-base model
# python -u text2sql.py \
#     --batch_size 16 \
#     --gradient_descent_step 2 \
#     --device "0" \
#     --learning_rate 1e-4 \
#     --epochs 128 \
#     --seed 42 \
#     --save_path "./models/text2sql-t5-base" \
#     --tensorboard_save_path "./tensorboard_log/text2sql-t5-base" \
#     --model_name_or_path "t5-base" \
#     --use_adafactor \
#     --mode train \
#     --train_filepath "./data/preprocessed_data/resdsql_train_spider.json"
    
# # select the best text2sql-t5-base ckpt
# python -u evaluate_text2sql_ckpts.py \
#     --batch_size 32 \
#     --device "0" \
#     --seed 42 \
#     --save_path "./models/text2sql-t5-base" \
#     --eval_results_path "./eval_results/text2sql-t5-base" \
#     --mode eval \
#     --dev_filepath "./data/preprocessed_data/resdsql_dev.json" \
#     --original_dev_filepath "./data/spider/dev.json" \
#     --db_path "./database" \
#     --num_beams 8 \
#     --num_return_sequences 8 \
#     --target_type "sql"

set -e
fold_id=0
# train text2sql-t5-base model
# python -u text2sql.py \
#     --batch_size 8 \
#     --gradient_descent_step 2 \
#     --device "0" \
#     --learning_rate 1e-4 \
#     --epochs 50 \
#     --seed 42 \
#     --save_path "models/booksql-t5-base" \
#     --tensorboard_save_path "tensorboard_log/booksql-t5-base" \
#     --model_name_or_path "models/text2sql-t5-base/checkpoint-39312" \
#     --use_adafactor \
#     --mode train \
#     --train_filepath "data/booksql/folds/fold$fold_id/preprocessed_data/resdsql_train_booksql.json" \
#     --dev_filepath "data/booksql/folds/fold$fold_id/preprocessed_data/resdsql_dev.json" \
#     --original_dev_filepath "data/booksql/folds/fold$fold_id/dev.json" \
#     --db_path "data/booksql/database" \
#     --num_beams 8 \
#     --num_return_sequences 8 \
#     --target_type "sql"
    
# select the best text2sql-t5-base ckpt
# python -u evaluate_text2sql_ckpts.py \
#     --batch_size 8 \
#     --device "0" \
#     --seed 42 \
#     --save_path "models/booksql-t5-base" \
#     --eval_results_path "eval_results/booksql-t5-base" \
#     --mode eval \
#     --dev_filepath "data/booksql/folds/fold$fold_id/preprocessed_data/resdsql_test.json" \
#     --original_dev_filepath "data/booksql/folds/fold$fold_id/test.json" \
#     --db_path "data/booksql/database" \
#     --num_beams 8 \
#     --num_return_sequences 8 \
#     --target_type "sql"


# select the best text2sql-t5-base ckpt
python -u evaluate_text2sql_ckpts.py \
    --batch_size 8 \
    --device "0" \
    --seed 42 \
    --save_path "models/booksql-t5-base" \
    --best_checkpoint_name "checkpoint-10608" \
    --eval_results_path "eval_results/booksql-t5-base" \
    --mode eval \
    --dev_filepath "data/booksql/folds/fold$fold_id/preprocessed_data/resdsql_test.json" \
    --original_dev_filepath "data/booksql/folds/fold$fold_id/test.json" \
    --db_path "data/booksql/database" \
    --num_beams 8 \
    --num_return_sequences 8 \
    --target_type "sql"