from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.normalizers import NFKC, Sequence
from tokenizers.pre_tokenizers import ByteLevel
from tokenizers.decoders import ByteLevel as ByteLevelDecoder
from transformers import GPT2TokenizerFast

# # 构建分词器 GPT2 基于 BPE 算法实现
# tokenizer = Tokenizer(BPE(unk_token="<unk>"))
# tokenizer.normalizer = Sequence([NFKC()])
# tokenizer.pre_tokenizer = ByteLevel()
# tokenizer.decoder = ByteLevelDecoder()

# special_tokens = ["<s>","<pad>","</s>","<unk>","<mask>"]
# trainer = BpeTrainer(vocab_size=50000, show_progress=True, inital_alphabet=ByteLevel.alphabet(), special_tokens=special_tokens)
# # 创建 text 文件夹，并把 sanguoyanyi.txt 下载，放到目录里
# files = ["text/sanguoyanyi.txt"]
# # 开始训练了
# tokenizer.train(files, trainer)
# # 把训练的分词通过GPT2保存起来，以方便后续使用
# newtokenizer = GPT2TokenizerFast(tokenizer_object=tokenizer)
# newtokenizer.save_pretrained("./sanguo")


# from transformers import GPT2Config, GPT2LMHeadModel, GPT2Tokenizer
# # 加载分词器
# tokenizer = GPT2Tokenizer.from_pretrained("./sanguo")
# tokenizer.add_special_tokens({
#   "eos_token": "</s>",
#   "bos_token": "<s>",
#   "unk_token": "<unk>",
#   "pad_token": "<pad>",
#   "mask_token": "<mask>"
# })
# # 配置GPT2模型参数
# config = GPT2Config(
#   vocab_size=tokenizer.vocab_size,
#   bos_token_id=tokenizer.bos_token_id,
#   eos_token_id=tokenizer.eos_token_id
# )
# # 创建模型
# model = GPT2LMHeadModel(config)
# # 训练数据我们用按行分割
# from transformers import LineByLineTextDataset
# dataset = LineByLineTextDataset(
#     tokenizer=tokenizer,
#     file_path="./text/sanguoyanyi.txt",
#     block_size=32,
#   # 如果训练时你的显存不够
#   # 可以适当调小 block_size
# )
# from transformers import DataCollatorForLanguageModeling
# data_collator = DataCollatorForLanguageModeling(
#     tokenizer=tokenizer, mlm=False, mlm_probability=0.15
# )

# from transformers import Trainer, TrainingArguments
# # 配置训练参数
# training_args = TrainingArguments(
#     output_dir="./output",
#     overwrite_output_dir=True,
#     num_train_epochs=20,
#     per_gpu_train_batch_size=16,
#     save_steps=2000,
#     save_total_limit=2,
# )
# trainer = Trainer(
#     model=model,
#     args=training_args,
#     data_collator=data_collator,
#     train_dataset=dataset,
# )
# trainer.train()
# # 保存模型
# model.save_pretrained('./sanguo')

from transformers import pipeline, set_seed
generator = pipeline('text-generation', model='./sanguo')
set_seed(42)
txt = generator("吕布", max_length=10)
print(txt)