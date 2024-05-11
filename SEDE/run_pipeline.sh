set -e

echo "Training"
python main_allennlp.py train configs/t5_text2sql_booksql.jsonnet -s experiments/booksql_experiment --include-package src

echo "Evaluation"
python main_allennlp.py evaluate experiments/booksql_experiment booksql/test.jsonl --output-file experiments/booksql_experiment/test_predictions.sql --cuda-device 0 --batch-size 10 --include-package src

echo "Inference"
python main_allennlp.py predict experiments/booksql_experiment booksql/test.jsonl --output-file experiments/booksql_experiment/val_predictions.sql --use-dataset-reader --predictor seq2seq2 --cuda-device 0 --batch-size 10 --include-package src