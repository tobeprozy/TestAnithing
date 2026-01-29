"""Instruction-tuning"""
import itertools
import jsonlines

from datasets import load_dataset
from pprint import pprint

# from llama import BasicModelRunner
from lamini import Lamini
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


instruction_tuned_dataset = load_dataset("tatsu-lab/alpaca", split="train", streaming=True)

m = 5
print("Instruction-tuned dataset:")
top_m = list(itertools.islice(instruction_tuned_dataset, m))
for j in top_m:
  print(j)


"""Two prompt templates"""
prompt_template_with_input = """
Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Input:
{input}

### Response:
"""

prompt_template_without_input = """
Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Response:
"""


"""Hydrate prompts (add data to prompts)"""
processed_data = []
for j in top_m:
  if not j["input"]:
    processed_prompt = prompt_template_without_input.format(instruction=j["instruction"])
  else:
    processed_prompt = prompt_template_with_input.format(instruction=j["instruction"], input=j["input"])

  processed_data.append({"input": processed_prompt, "output": j["output"]})

pprint(processed_data[0])


"""Save data to jsonl"""
with jsonlines.open(f'alpaca_processed.jsonl', 'w') as writer:
    writer.write_all(processed_data)


"""Compare non-instruction-tuned vs. instruction-tuned models"""
dataset_path_hf = "lamini/alpaca"
dataset_hf = load_dataset(dataset_path_hf)
print(dataset_hf)

# non_instruct_model = Lamini("meta-llama/Llama-2-7b-hf")
# non_instruct_output = non_instruct_model.generate("Tell me how to train my dog to sit")
# print("Not instruction-tuned output (Llama 2 Base):", non_instruct_output)

# instruct_model = Lamini("meta-llama/Llama-2-7b-chat-hf")
# instruct_output = instruct_model.generate("Tell me how to train my dog to sit")
# print("Instruction-tuned output (Llama 2): ", instruct_output)

# chatgpt = Lamini("chat-gpt")
# instruct_output_chatgpt = chatgpt.generate("Tell me how to train my dog to sit")
# print("Instruction-tuned output (ChatGPT): ", instruct_output_chatgpt)


"""Try smaller models"""
tokenizer = AutoTokenizer.from_pretrained("EleutherAI/pythia-70m")
model = AutoModelForCausalLM.from_pretrained("EleutherAI/pythia-70m")

def inference(text, model, tokenizer, max_input_tokens=1000, max_output_tokens=100):
  # Tokenize
  input_ids = tokenizer.encode(
          text,
          return_tensors="pt",
          truncation=True,
          max_length=max_input_tokens)

  # Generate
  device = model.device
  generated_tokens_with_prompt = model.generate(
    input_ids=input_ids.to(device),
    max_length=max_output_tokens)

  # Decode
  generated_text_with_prompt = tokenizer.batch_decode(generated_tokens_with_prompt, skip_special_tokens=True)

  # Strip the prompt
  generated_text_answer = generated_text_with_prompt[0][len(text):]

  return generated_text_answer

finetuning_dataset_path = "lamini/lamini_docs"
finetuning_dataset = load_dataset(finetuning_dataset_path)
print(finetuning_dataset)

test_sample = finetuning_dataset["test"][0]
print(test_sample)

print(inference(test_sample["question"], model, tokenizer))


"""Compare to finetuned small model"""
instruction_model = AutoModelForCausalLM.from_pretrained("lamini/lamini_docs_finetuned")

print(inference(test_sample["question"], instruction_model, tokenizer))