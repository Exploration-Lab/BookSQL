import os
import json
import torch
import argparse
import torch.optim as optim
import transformers

from tqdm import tqdm
from tokenizers import AddedToken

from torch.utils.tensorboard import SummaryWriter
from torch.utils.data import DataLoader
from transformers import T5TokenizerFast, T5ForConditionalGeneration
from transformers.optimization import Adafactor
from transformers.trainer_utils import set_seed
from utils.spider_metric.evaluator import EvaluateTool
from utils.load_dataset import Text2SQLDataset
from utils.text2sql_decoding_utils import decode_sqls, decode_natsqls

def parse_option():
    parser = argparse.ArgumentParser("command line arguments for fine-tuning pre-trained language model.")
    
    parser.add_argument('--batch_size', type = int, default = 8,
                        help = 'input batch size.')
    parser.add_argument('--gradient_descent_step', type = int, default = 4,
                        help = 'perform gradient descent per "gradient_descent_step" steps.')
    parser.add_argument('--device', type = str, default = "0gpustat",
                        help = 'the id of used GPU device.')
    parser.add_argument('--learning_rate',type = float, default = 3e-5,
                        help = 'learning rate.')
    parser.add_argument('--epochs', type = int, default = 128,
                        help = 'training epochs.')
    parser.add_argument('--seed', type = int, default = 42,
                        help = 'random seed.')
    parser.add_argument('--save_path', type = str, default = "models/text2sql",
                        help = 'save path of best fine-tuned text2sql model.')
    parser.add_argument('--tensorboard_save_path', type = str, default = "tensorboard_log/text2sql",
                        help = 'save path of tensorboard log.')
    parser.add_argument('--model_name_or_path', type = str, default = "t5-3b",
                        help = 
                        '''
                        pre-trained model name. 
                        options: 
                            t5-base, https://huggingface.co/t5-base;
                            t5-large, https://huggingface.co/t5-large;
                            t5-3b, https://huggingface.co/t5-3b;
                        ''')
    parser.add_argument('--use_adafactor', action='store_true',
                        help = 'whether to use adafactor optimizer.')
    parser.add_argument('--mode', type = str, default = "train",
                        help='trian, eval or test.')
    parser.add_argument('--train_filepath', type = str, default = "data/preprocessed_data/resdsql_train_spider.json",
                        help = 'file path of test2sql training set.')
    parser.add_argument('--dev_filepath', type = str, default = "data/preprocessed_data/resdsql_dev.json",
                        help = 'file path of test2sql dev set.')
    parser.add_argument('--original_dev_filepath', type = str, default = "data/spider/dev.json",
                        help = 'file path of the original dev set (for registing evaluator).')
    parser.add_argument('--db_path', type = str, default = "database",
                        help = 'file path of database.')
    parser.add_argument('--tables_for_natsql', type = str, default = "NatSQL/NatSQLv1_6/tables_for_natsql.json",
                        help = 'file path of tables_for_natsql.json.')
    parser.add_argument('--num_beams', type = int, default = 8,
                        help = 'beam size in model.generate() function.')
    parser.add_argument('--num_return_sequences', type = int, default = 8,
                        help = 'the number of returned sequences in model.generate() function (num_return_sequences <= num_beams).')
    parser.add_argument("--target_type", type = str, default = "sql",
                help = "sql or natsql.")
    
    opt = parser.parse_args()

    return opt

def _train(opt):
    set_seed(opt.seed)
    print(opt)

    if opt.tensorboard_save_path is not None:
        writer = SummaryWriter(opt.tensorboard_save_path)
    else:
        writer = None

    os.environ["CUDA_VISIBLE_DEVICES"] = opt.device

    text2sql_tokenizer = T5TokenizerFast.from_pretrained(
        opt.model_name_or_path,
        add_prefix_space = True
    )
    
    if isinstance(text2sql_tokenizer, T5TokenizerFast):
        text2sql_tokenizer.add_tokens([AddedToken(" <="), AddedToken(" <")])
    
    train_dataset = Text2SQLDataset(
        dir_ = opt.train_filepath,
        mode = "train"
    )

    train_dataloder = DataLoader(
        train_dataset, 
        batch_size = opt.batch_size, 
        shuffle = True,
        collate_fn = lambda x: x,
        drop_last = True
    )

    print("initializing text2sql model.")
    # initialize model
    model = T5ForConditionalGeneration.from_pretrained(opt.model_name_or_path)
    model.resize_token_embeddings(len(text2sql_tokenizer))
    if torch.cuda.is_available():
        model = model.cuda()
    
    print("finished.")

    # warm up steps (10% training step)
    num_warmup_steps = int(0.1*opt.epochs*len(train_dataset)/opt.batch_size)
    # total training steps
    num_training_steps = int(opt.epochs*len(train_dataset)/opt.batch_size)
    # save checkpoint for each 1.42857 epochs (about 1.42857*7000=10000 examples for Spider's training set)
    num_checkpoint_steps = int(1.42857 * len(train_dataset)/opt.batch_size)

    early_stop=0
    patience=16

    if opt.use_adafactor:
        print("Let's use Adafactor!")
        optimizer = Adafactor(
            model.parameters(), 
            lr=opt.learning_rate, 
            scale_parameter=False, 
            relative_step=False, 
            clip_threshold = 1.0,
            warmup_init=False
        )
    else:
        print("Let's use AdamW!")
        optimizer = optim.AdamW(
            model.parameters(), 
            lr = opt.learning_rate
        )

    scheduler = transformers.get_cosine_schedule_with_warmup(
        optimizer, 
        num_warmup_steps = num_warmup_steps,
        num_training_steps = num_training_steps
    )

    model.train()
    train_step = 0
    best_val_exec_acc=0.0
    best_val_exact_match=0.0 
    best_epoch=0
    for epoch in range(opt.epochs):
        print(f"This is epoch {epoch+1}.")
        train_loss=0
        for batch in train_dataloder:
            train_step += 1
            
            batch_inputs = [data[0] for data in batch]
            batch_sqls = [data[1] for data in batch]
            batch_db_ids = [data[2] for data in batch] # unused
            batch_tc_original = [data[3] for data in batch] # unused
            
            # if epoch == 0:
            #     # for batch_id in range(len(batch_inputs)):
            #         print(batch_inputs[batch_id])
            #         print(batch_sqls[batch_id])
            #         print("----------------------")

            tokenized_inputs = text2sql_tokenizer(
                batch_inputs, 
                padding = "max_length",
                return_tensors = "pt",
                max_length = 512,
                truncation = True
            )
            
            with text2sql_tokenizer.as_target_tokenizer():
                tokenized_outputs = text2sql_tokenizer(
                    batch_sqls, 
                    padding = "max_length", 
                    return_tensors = 'pt',
                    max_length = 256,
                    truncation = True
                )
            
            encoder_input_ids = tokenized_inputs["input_ids"]
            encoder_input_attention_mask = tokenized_inputs["attention_mask"]

            decoder_labels = tokenized_outputs["input_ids"]
            decoder_labels[decoder_labels == text2sql_tokenizer.pad_token_id] = -100
            decoder_attention_mask = tokenized_outputs["attention_mask"]

            if torch.cuda.is_available():
                encoder_input_ids = encoder_input_ids.cuda()
                encoder_input_attention_mask = encoder_input_attention_mask.cuda()
                decoder_labels = decoder_labels.cuda()
                decoder_attention_mask = decoder_attention_mask.cuda()
            
            model_outputs = model(
                input_ids = encoder_input_ids,
                attention_mask = encoder_input_attention_mask,
                labels = decoder_labels,
                decoder_attention_mask = decoder_attention_mask,
                return_dict = True
            )
            
            loss = model_outputs["loss"]
            train_loss += loss.item()
            loss.backward()

            if scheduler is not None:
                scheduler.step()

            if writer is not None:
                # record training loss (tensorboard)
                writer.add_scalar('train loss', loss.item(), train_step)
                # print("Train loss: ", loss.item())
                
                # record learning rate (tensorboard)
                writer.add_scalar('train lr', optimizer.state_dict()['param_groups'][0]['lr'], train_step)

            if train_step % opt.gradient_descent_step == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                optimizer.zero_grad()

            
            
            if train_step % num_checkpoint_steps == 0 and epoch >= 6:
                print(f"At {train_step} training step, save a checkpoint.")
                os.makedirs(opt.save_path, exist_ok = True)
                model.save_pretrained(save_directory = opt.save_path + "/checkpoint-{}".format(train_step))
                text2sql_tokenizer.save_pretrained(save_directory = opt.save_path + "/checkpoint-{}".format(train_step))
        
        print("Train Loss: ", train_loss/len(train_dataloder))
        #Validation
        exact_match, exec_acc, total_errs = _validate(opt, model, text2sql_tokenizer)
        
        if exec_acc > best_val_exec_acc:
            best_epoch=epoch
            best_val_exec_acc=exec_acc
            best_val_exact_match=exact_match
            os.makedirs(opt.save_path, exist_ok = True)
            model.save_pretrained(save_directory = opt.save_path + "/epoch-{}".format(epoch))
            text2sql_tokenizer.save_pretrained(save_directory = opt.save_path + "/epoch-{}".format(epoch))
            #Appending non-executable error in one files
            with open("logs/non_execu_error.err", "w") as outfile:
                outfile.write("\n".join(total_errs))
            early_stop=0
        else:
            early_stop+=1
        print(f"Best Epoch {best_epoch}, \n Best Exec Acc so far: {best_val_exec_acc} \n Best Exact Match so far: {best_val_exact_match}")
        if early_stop==patience:
            print(f"Early stopping at epoch {epoch} ---------")
            break
    

def _validate(opt, model, tokenizer):
    set_seed(opt.seed)
    print(opt)

    import time
    start_time = time.time()
    
    os.environ["CUDA_VISIBLE_DEVICES"] = opt.device
    
    if opt.target_type == "natsql":
        tables = json.load(open(opt.tables_for_natsql,'r'))
        table_dict = dict()
        for t in tables:
            table_dict[t["db_id"]] = t
    
    dev_dataset = Text2SQLDataset(
        dir_ = opt.dev_filepath,
        mode = opt.mode
    )

    dev_dataloder = DataLoader(
        dev_dataset, 
        batch_size = opt.batch_size, 
        shuffle = False,
        collate_fn = lambda x: x,
        drop_last = False
    )

    if torch.cuda.is_available():
        model = model.cuda()

    model.eval()
    predict_sqls = []
    total_errs=[]
    total_executable_count, total_non_executable_count=0, 0
    for batch in tqdm(dev_dataloder): #since mode is train here so 4 value will be returned, modify train return type according to val type
        batch_inputs = [data[0] for data in batch] #check utils.load_dataset
        batch_db_ids = [data[2] for data in batch]
        batch_tc_original = [data[3] for data in batch]
        tokenized_inputs = tokenizer(
            batch_inputs, 
            return_tensors="pt",
            padding = "max_length",
            max_length = 512,
            truncation = True
        )
        
        encoder_input_ids = tokenized_inputs["input_ids"]
        encoder_input_attention_mask = tokenized_inputs["attention_mask"]
        if torch.cuda.is_available():
            encoder_input_ids = encoder_input_ids.cuda()
            encoder_input_attention_mask = encoder_input_attention_mask.cuda()

        with torch.no_grad():
            model_outputs = model.generate(
                input_ids = encoder_input_ids,
                attention_mask = encoder_input_attention_mask,
                max_length = 256,
                decoder_start_token_id = model.config.decoder_start_token_id,
                num_beams = opt.num_beams,
                num_return_sequences = opt.num_return_sequences
            )

            model_outputs = model_outputs.view(len(batch_inputs), opt.num_return_sequences, model_outputs.shape[1])
            if opt.target_type == "sql":
                predict_sql, (executable_count, non_executable_count), total_err= decode_sqls(
                    opt.db_path, 
                    model_outputs, 
                    batch_db_ids, 
                    batch_inputs, 
                    tokenizer, 
                    batch_tc_original
                )
                predict_sqls+=predict_sql
                total_errs+=total_err
                total_executable_count+=executable_count 
                total_non_executable_count+=non_executable_count
            elif opt.target_type == "natsql":
                predict_sqls += decode_natsqls(
                    opt.db_path, 
                    model_outputs, 
                    batch_db_ids, 
                    batch_inputs, 
                    tokenizer, 
                    batch_tc_original, 
                    table_dict
                )
            else:
                raise ValueError()
    
    end_time = time.time()
    print("Text-to-SQL validation spends {}s.".format(end_time-start_time))
    print("Total Executable: ", total_executable_count)
    print("Total Non-Executable: ", total_non_executable_count)

    # initialize evaluator
    evaluator = EvaluateTool()
    evaluator.register_golds(opt.original_dev_filepath, opt.db_path)
    metric_result = evaluator.evaluate(predict_sqls)
    print('exact_match score: {}'.format(metric_result["exact_match"]))
    print('exec score: {}'.format(metric_result["exec"]))

    return metric_result["exact_match"], metric_result["exec"], total_errs

def _test(opt, ckpt_name):
    set_seed(opt.seed)
    print(opt)

    import time
    start_time = time.time()
    
    os.environ["CUDA_VISIBLE_DEVICES"] = opt.device
    
    if opt.target_type == "natsql":
        tables = json.load(open(opt.tables_for_natsql,'r'))
        table_dict = dict()
        for t in tables:
            table_dict[t["db_id"]] = t

    # initialize tokenizer
    tokenizer = T5TokenizerFast.from_pretrained(
        opt.save_path,
        add_prefix_space = True
    )
    
    if isinstance(tokenizer, T5TokenizerFast):
        tokenizer.add_tokens([AddedToken(" <="), AddedToken(" <")])
    
    dev_dataset = Text2SQLDataset(
        dir_ = opt.dev_filepath,
        mode = opt.mode
    )

    dev_dataloder = DataLoader(
        dev_dataset, 
        batch_size = opt.batch_size, 
        shuffle = False,
        collate_fn = lambda x: x,
        drop_last = False
    )

    # initialize model
    model = T5ForConditionalGeneration.from_pretrained(opt.save_path)
    if torch.cuda.is_available():
        model = model.cuda()

    model.eval()
    predict_sqls = []
    total_errs=[]
    total_executable_count, total_non_executable_count=0, 0
    for batch in tqdm(dev_dataloder):
        batch_inputs = [data[0] for data in batch]
        batch_db_ids = [data[1] for data in batch]
        batch_tc_original = [data[2] for data in batch]

        tokenized_inputs = tokenizer(
            batch_inputs, 
            return_tensors="pt",
            padding = "max_length",
            max_length = 512,
            truncation = True
        )
        
        encoder_input_ids = tokenized_inputs["input_ids"]
        encoder_input_attention_mask = tokenized_inputs["attention_mask"]
        if torch.cuda.is_available():
            encoder_input_ids = encoder_input_ids.cuda()
            encoder_input_attention_mask = encoder_input_attention_mask.cuda()

        with torch.no_grad():
            model_outputs = model.generate(
                input_ids = encoder_input_ids,
                attention_mask = encoder_input_attention_mask,
                max_length = 256,
                decoder_start_token_id = model.config.decoder_start_token_id,
                num_beams = opt.num_beams,
                num_return_sequences = opt.num_return_sequences
            )

            model_outputs = model_outputs.view(len(batch_inputs), opt.num_return_sequences, model_outputs.shape[1])
            if opt.target_type == "sql":
                predict_sql, (executable_count, non_executable_count), total_err = decode_sqls(
                    opt.db_path, 
                    model_outputs, 
                    batch_db_ids, 
                    batch_inputs, 
                    tokenizer, 
                    batch_tc_original
                )
                predict_sqls+=predict_sql
                total_errs+=total_err
                total_executable_count+=executable_count 
                total_non_executable_count+=non_executable_count
            elif opt.target_type == "natsql":
                predict_sqls += decode_natsqls(
                    opt.db_path, 
                    model_outputs, 
                    batch_db_ids, 
                    batch_inputs, 
                    tokenizer, 
                    batch_tc_original, 
                    table_dict
                )
            else:
                raise ValueError()

    # print("org path: ", opt.original_dev_filepath)
    with open(opt.original_dev_filepath, "r") as read_file:
        gold_json = json.load(read_file)
    gold_sqls=[]
    for gg in gold_json:
        # gold_sqls.append({'question': gg['question'], 'query': gg['query'], 'level': gg['Levels']})
        gold_sqls.append({'question': gg['question'], 'query': gg['query']})

    assert len(gold_sqls) == len(predict_sqls)

    print("Checkpoint: ", ckpt_name)
    print("Total Executable: ", total_executable_count)
    print("Total Non-Executable: ", total_non_executable_count)

    #Writing error
    with open( "eval_results/test/errors/" + f"{ckpt_name}_sql.err", "w", encoding = 'utf-8') as f:
        for line in total_errs:
            f.write(line+"\n")

    # save results
    with open( "eval_results/test/predictions/" + f"{ckpt_name}_sql.txt", "w", encoding = 'utf-8') as f:
        for gold, pred in zip(gold_sqls, predict_sqls):
            f.write("ques:\t"+gold['question'] + "\n")
            # f.write("Level:\t"+gold['level'] + "\n")
            f.write("Gold:\t"+gold['query'] + "\n")
            f.write("Pred:\t"+pred + "\n")
            f.write("\n")
    
    end_time = time.time()
    print("Text-to-SQL inference spends {}s.".format(end_time-start_time))
    
    if opt.mode == "eval":
        # initialize evaluator
        evaluator = EvaluateTool()
        evaluator.register_golds(opt.original_dev_filepath, opt.db_path)
        spider_metric_result = evaluator.evaluate(predict_sqls)
        print('exact_match score: {}'.format(spider_metric_result["exact_match"]))
        print('exec score: {}'.format(spider_metric_result["exec"]))
    
        return spider_metric_result["exact_match"], spider_metric_result["exec"]
    
if __name__ == "__main__":
    opt = parse_option()
    if opt.mode in ["train"]:
        _train(opt)
    elif opt.mode in ["eval", "test"]:
        _test(opt)