set -e

fold_id=0

#Sample
# data_folder_name=sample
# batch_size=1
# epochs=2

# #Original
data_folder_name=fold$fold_id
batch_size=16
epochs=128

echo "preprocess train_booksql dataset for Cross Encoder"
python preprocessing.py \
    --mode "train" \
    --table_path "data/booksql/booksqltables.json" \
    --input_dataset_path "data/booksql/folds/$data_folder_name/train.json" \
    --output_dataset_path "data/booksql/folds/$data_folder_name/preprocessed_data/preprocessed_train_booksql.json" \
    --db_path "data/booksql/database" \
    --target_type "sql" > logs/preprocessing_train.log

echo "preprocess dev dataset for Cross Encoder"
python preprocessing.py \
    --mode "eval" \
    --table_path "data/booksql/booksqltables.json" \
    --input_dataset_path "data/booksql/folds/$data_folder_name/dev.json" \
    --output_dataset_path "data/booksql/folds/$data_folder_name/preprocessed_data/preprocessed_dev.json" \
    --db_path "data/booksql/database"\
    --target_type "sql" > logs/preprocessing_dev.log

echo "preprocess test dataset for Cross Encoder"
python preprocessing.py \
    --mode "eval" \
    --table_path "data/booksql/booksqltables.json" \
    --input_dataset_path "data/booksql/folds/test_fold/$data_folder_name/test.json" \
    --output_dataset_path "data/booksql/folds/test_fold/$data_folder_name/preprocessed_data/preprocessed_test.json" \
    --db_path "data/booksql/database" \
    --target_type "sql" > logs/preprocessing_test.log

echo "train schema item classifier"
python -u schema_item_classifier.py \
    --batch_size $batch_size \
    --gradient_descent_step 2 \
    --device "0" \
    --learning_rate 1e-5 \
    --gamma 2.0 \
    --alpha 0.75 \
    --epochs $epochs \
    --patience 16 \
    --seed 42 \
    --save_path "models/text2sql_schema_item_classifier_booksql" \
    --tensorboard_save_path "tensorboard_log/text2sql_schema_item_classifier_booksql" \
    --train_filepath "data/booksql/folds/$data_folder_name/preprocessed_data/preprocessed_train_booksql.json" \
    --dev_filepath "data/booksql/folds/$data_folder_name/preprocessed_data/preprocessed_dev.json" \
    --model_name_or_path "roberta-large" \
    --use_contents \
    --add_fk_info \
    --mode "train" > "logs/cross-encoder.log"


echo "generate text2sql training dataset with noise_rate 0.2"
python text2sql_data_generator.py \
    --input_dataset_path "data/booksql/folds/$data_folder_name/preprocessed_data/preprocessed_train_booksql.json" \
    --output_dataset_path "data/booksql/folds/$data_folder_name/preprocessed_data/resdsql_train_booksql.json" \
    --topk_table_num 4 \
    --topk_column_num 8 \
    --mode "train" \
    --noise_rate 0.2 \
    --use_contents \
    --add_fk_info \
    --output_skeleton \
    --target_type "sql" > logs/generate_text2sql_train.log

echo "predict probability for each schema item in the eval set"
python schema_item_classifier.py \
    --batch_size $batch_size \
    --device "0" \
    --seed 42 \
    --save_path "models/text2sql_schema_item_classifier_booksql" \
    --dev_filepath "data/booksql/folds/$data_folder_name/preprocessed_data/preprocessed_dev.json" \
    --output_filepath "data/booksql/folds/$data_folder_name/preprocessed_data/dev_with_probs.json" \
    --use_contents \
    --add_fk_info \
    --mode "eval" > logs/predict_probability_train.log

echo "generate text2sql development dataset"
python text2sql_data_generator.py \
    --input_dataset_path "data/booksql/folds/$data_folder_name/preprocessed_data/dev_with_probs.json" \
    --output_dataset_path "data/booksql/folds/$data_folder_name/preprocessed_data/resdsql_dev.json" \
    --topk_table_num 4 \
    --topk_column_num 8 \
    --mode "eval" \
    --use_contents \
    --add_fk_info \
    --output_skeleton \
    --target_type "sql" > logs/generate_text2sql_dev.log
 
echo "predict probability for each schema item in the test set"
python schema_item_classifier.py \
    --batch_size $batch_size \
    --device "0" \
    --seed 42 \
    --save_path "models/text2sql_schema_item_classifier_booksql" \
    --dev_filepath "data/booksql/folds/test_fold/$data_folder_name/preprocessed_data/preprocessed_test.json" \
    --output_filepath "data/booksql/folds/test_fold/$data_folder_name/preprocessed_data/test_with_probs.json" \
    --use_contents \
    --add_fk_info \
    --mode "eval" > logs/predict_probability_test.log

echo "generate text2sql test dataset"
python text2sql_data_generator.py \
    --input_dataset_path "data/booksql/folds/test_fold/$data_folder_name/preprocessed_data/test_with_probs.json" \
    --output_dataset_path "data/booksql/folds/test_fold/$data_folder_name/preprocessed_data/resdsql_test.json" \
    --topk_table_num 4 \
    --topk_column_num 8 \
    --mode "eval" \
    --use_contents \
    --add_fk_info \
    --output_skeleton \
    --target_type "sql" > logs/generate_text2sql_test.log

echo "train text2sql-t5-large model"
python -u text2sql.py \
    --batch_size $batch_size \
    --gradient_descent_step 2 \
    --device "0" \
    --learning_rate 5e-5\
    --epochs $epochs \
    --seed 42 \
    --save_path "models/booksql-t5-large" \
    --tensorboard_save_path "tensorboard_log/booksql-t5-large" \
    --model_name_or_path "t5-large" \
    --use_adafactor \
    --mode train \
    --train_filepath "data/booksql/folds/$data_folder_name/preprocessed_data/resdsql_train_booksql.json" \
    --dev_filepath "data/booksql/folds/$data_folder_name/preprocessed_data/resdsql_dev.json" \
    --original_dev_filepath "data/booksql/folds/$data_folder_name/dev.json" \
    --db_path "data/booksql/database" \
    --num_beams 8 \
    --num_return_sequences 8 \
    --target_type "sql" > logs/train.log
    
# echo "Evaluating on test sets"
# python -u evaluate_text2sql_ckpts.py \
#     --batch_size $batch_size \
#     --device "0" \
#     --seed 42 \
#     --save_path "models/booksql-t5-large" \
#     --eval_results_path "eval_results/booksql-t5-large" \
#     --mode eval \
#     --dev_filepath "data/booksql/folds/test_fold/$data_folder_name/preprocessed_data/resdsql_test.json" \
#     --original_dev_filepath "data/booksql/folds/test_fold/$data_folder_name/test.json" \
#     --db_path "data/booksql/database" \
#     --num_beams 8 \
#     --num_return_sequences 8 \
#     --target_type "sql" > logs/eval.log


# best_checkpoint_name="checkpoint-20"

# echo "select the best text2sql-t5-large ckpt"
# python -u evaluate_text2sql_ckpts.py \
#     --batch_size $batch_size \
#     --device "0" \
#     --seed 42 \
#     --save_path "models/booksql-t5-large" \
#     --best_checkpoint_name $best_checkpoint_name \
#     --eval_results_path "eval_results/booksql-t5-large" \
#     --mode eval \
#     --dev_filepath "data/booksql/folds/test_fold/$data_folder_name/preprocessed_data/resdsql_test.json" \
#     --original_dev_filepath "data/booksql/folds/test_fold/$data_folder_name/test.json" \
#     --db_path "data/booksql/database" \
#     --num_beams 8 \
#     --num_return_sequences 8 \
#     --target_type "sql" > logs/best_chkpt_eval.log

# echo "Get Execution and Exact Match Accuracy"
# python -u query_on_db.py $best_checkpoint_name > logs/Exec_and_Exact_match_score.log