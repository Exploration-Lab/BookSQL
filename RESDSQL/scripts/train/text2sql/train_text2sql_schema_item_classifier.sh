set -e

# train schema item classifier
# python -u schema_item_classifier.py \
#     --batch_size 16 \
#     --gradient_descent_step 2 \
#     --device "0" \
#     --learning_rate 1e-5 \
#     --gamma 2.0 \
#     --alpha 0.75 \
#     --epochs 128 \
#     --patience 16 \
#     --seed 42 \
#     --save_path "./models/text2sql_schema_item_classifier" \
#     --tensorboard_save_path "./tensorboard_log/text2sql_schema_item_classifier" \
#     --train_filepath "./data/preprocessed_data/preprocessed_train_spider.json" \
#     --dev_filepath "./data/preprocessed_data/preprocessed_dev.json" \
#     --model_name_or_path "roberta-large" \
#     --use_contents \
#     --add_fk_info \
#     --mode "train"

python -u schema_item_classifier.py \
    --batch_size 8 \
    --gradient_descent_step 2 \
    --device "0,1,2,3" \
    --learning_rate 1e-5 \
    --gamma 2.0 \
    --alpha 0.75 \
    --epochs 50 \
    --patience 5 \
    --seed 42 \
    --save_path "models/text2sql_schema_item_classifier_booksql" \
    --tensorboard_save_path "tensorboard_log/text2sql_schema_item_classifier_booksql" \
    --train_filepath "data/booksql/folds/fold0/preprocessed_data/preprocessed_train_booksql.json" \
    --dev_filepath "data/booksql/folds/fold0/preprocessed_data/preprocessed_dev.json" \
    --model_name_or_path "roberta-large" \
    --use_contents \
    --add_fk_info \
    --mode "train" > "logs/cross-encoder.log"