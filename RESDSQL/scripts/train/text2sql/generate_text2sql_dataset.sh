set -e

# # generate text2sql training dataset with noise_rate 0.2
# python text2sql_data_generator.py \
#     --input_dataset_path "./data/preprocessed_data/preprocessed_train_spider.json" \
#     --output_dataset_path "./data/preprocessed_data/resdsql_train_spider.json" \
#     --topk_table_num 4 \
#     --topk_column_num 5 \
#     --mode "train" \
#     --noise_rate 0.2 \
#     --use_contents \
#     --add_fk_info \
#     --output_skeleton \
#     --target_type "sql"

# # predict probability for each schema item in the eval set
# python schema_item_classifier.py \
#     --batch_size 32 \
#     --device "0" \
#     --seed 42 \
#     --save_path "./models/text2sql_schema_item_classifier" \
#     --dev_filepath "./data/preprocessed_data/preprocessed_dev.json" \
#     --output_filepath "./data/preprocessed_data/dev_with_probs.json" \
#     --use_contents \
#     --add_fk_info \
#     --mode "eval"

# # generate text2sql development dataset
# python text2sql_data_generator.py \
#     --input_dataset_path "./data/preprocessed_data/dev_with_probs.json" \
#     --output_dataset_path "./data/preprocessed_data/resdsql_dev.json" \
#     --topk_table_num 4 \
#     --topk_column_num 5 \
#     --mode "eval" \
#     --use_contents \
#     --add_fk_info \
#     --output_skeleton \
#     --target_type "sql"


fold_id=0
# generate text2sql training dataset with noise_rate 0.2
# python text2sql_data_generator.py \
#     --input_dataset_path "data/booksql/folds/fold$fold_id/preprocessed_data/preprocessed_train_booksql.json" \
#     --output_dataset_path "data/booksql/folds/fold$fold_id/preprocessed_data/resdsql_train_booksql.json" \
#     --topk_table_num 4 \
#     --topk_column_num 8 \
#     --mode "train" \
#     --noise_rate 0.2 \
#     --use_contents \
#     --add_fk_info \
#     --output_skeleton \
#     --target_type "sql"

# predict probability for each schema item in the eval set
# python schema_item_classifier.py \
#     --batch_size 8 \
#     --device "0" \
#     --seed 42 \
#     --save_path "models/text2sql_schema_item_classifier_booksql" \
#     --dev_filepath "data/booksql/folds/fold$fold_id/preprocessed_data/preprocessed_dev.json" \
#     --output_filepath "data/booksql/folds/fold$fold_id/preprocessed_data/dev_with_probs.json" \
#     --use_contents \
#     --add_fk_info \
#     --mode "eval"

# generate text2sql development dataset
# python text2sql_data_generator.py \
#     --input_dataset_path "data/booksql/folds/fold$fold_id/preprocessed_data/dev_with_probs.json" \
#     --output_dataset_path "data/booksql/folds/fold$fold_id/preprocessed_data/resdsql_dev.json" \
#     --topk_table_num 4 \
#     --topk_column_num 8 \
#     --mode "eval" \
#     --use_contents \
#     --add_fk_info \
#     --output_skeleton \
#     --target_type "sql"

# predict probability for each schema item in the test set
python schema_item_classifier.py \
    --batch_size 8 \
    --device "0" \
    --seed 42 \
    --save_path "models/text2sql_schema_item_classifier_booksql" \
    --dev_filepath "data/booksql/folds/test_fold/fold$fold_id/preprocessed_data/preprocessed_test.json" \
    --output_filepath "data/booksql/folds/test_fold/fold$fold_id/preprocessed_data/test_with_probs.json" \
    --use_contents \
    --add_fk_info \
    --mode "eval"

# generate text2sql test dataset
python text2sql_data_generator.py \
    --input_dataset_path "data/booksql/folds/test_fold/fold$fold_id/preprocessed_data/test_with_probs.json" \
    --output_dataset_path "data/booksql/folds/test_fold/fold$fold_id/preprocessed_data/resdsql_test.json" \
    --topk_table_num 4 \
    --topk_column_num 8 \
    --mode "eval" \
    --use_contents \
    --add_fk_info \
    --output_skeleton \
    --target_type "sql"