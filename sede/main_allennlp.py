import sys
import os
import shutil

from allennlp.commands import main
os.environ['WANDB_API_KEY'] = "79fa6ac86245ac0aeb170f02225dceb8088b2213"

# if os.path.exists("experiments/booksql_experiment"):
#     shutil.rmtree("experiments/booksql_experiment")

sys.path.append("src")

if __name__ == "__main__":
    main()
