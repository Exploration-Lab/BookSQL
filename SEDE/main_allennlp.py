import sys
import os
import shutil

from allennlp.commands import main
#add your WANDB_API_KEY
api_key = input('Give your WANDB_API_KEY or skip it')
os.environ['WANDB_API_KEY'] = api_key

# if os.path.exists("experiments/booksql_experiment"):
#     shutil.rmtree("experiments/booksql_experiment")

sys.path.append("src")

if __name__ == "__main__":
    main()
