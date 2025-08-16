import csv
import random
import re
from collections import defaultdict
import os
import json
import time
from uuid import uuid4

config = {
	"RESULT_AUTHOR": "",
	"RESULT_DIRECTORY": "./results",
	"RESULT_FILE": "result.csv",
	"RESULT_ENTRIES": [
		"author",
		"file_path",
		"start_timestamp",
		"end_timestamp",
		"language_proficiency"
	],
	"LANGUAGE_PROFICIENCY": 0.5,
	"DATA_DIRECTORY": "./data",
	"CORPUS_FILE": "./corpus/large.txt",
	"CHAIN_ORDER": 3,
	"MIN_SENTENCE_LEN": 8,
	"MAX_SENTENCE_LEN": 30,
	"RUN_CONFIGURATIONS": [],
	"NUM_SENTENCES": 5,
	"NUM_PARAGRAPHS": 2,
	"PARAGRAPH_SENTENCE_VARIATION": 2
}

def load_config(json_file):
    global config
    with open(json_file, "r", encoding="utf-8") as f:
        json_config = json.load(f)

    for key in config.keys():
        if key in json_config:
            config[key] = json_config[key]

def load_corpus(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def build_markov_chain(corpus, order):
    words = re.findall(r"\b\w+\b|[.!?]", corpus)
    chain = defaultdict(list)
    
    for i in range(len(words) - order):
        key = tuple(words[i:i+order])
        chain[key].append(words[i+order])
    
    return chain, words

def generate_sentence(chain, words, order):
    starts = [k for k in chain.keys() if k[0][0].isupper()]
    wlist = list(random.choice(starts))
    sentence = wlist[:]
    
    while True:
        key = tuple(sentence[-order:])
        if key not in chain:
            break
        next_word = random.choice(chain[key])
        sentence.append(next_word)
        
        if next_word in ".!?":
            break
        if len(sentence) > random.randint(config["MIN_SENTENCE_LEN"], config["MAX_SENTENCE_LEN"]):
            sentence.append(".")
            break
    
    return " ".join(sentence).replace(" .", ".").replace(" !", "!").replace(" ?", "?")

def generate_text_blob(
    num_sentences,
    num_paragraphs,
    corpus_file
):
    corpus = load_corpus(corpus_file)
    chain, words = build_markov_chain(corpus, config["CHAIN_ORDER"])
    
    paragraphs = []
    for _ in range(num_paragraphs):
        # Randomize sentence count per paragraph
        sentence_count = max(1, num_sentences + random.randint(-config["PARAGRAPH_SENTENCE_VARIATION"], config["PARAGRAPH_SENTENCE_VARIATION"]))
        sentences = [generate_sentence(chain, words, config["CHAIN_ORDER"]) for _ in range(sentence_count)]
        paragraphs.append(" ".join(sentences))
    
    return "\n\n".join(paragraphs)

def write_text_blob(blob):
    file_name = f"{uuid4()}.txt"
    file_path = os.path.join(config["DATA_DIRECTORY"], file_name)
    with open(file_path, "w") as f:
        f.write(blob)

    return (file_path, file_name)

def write_result_line(file_path, start, end):
    with open(os.path.join(config["RESULT_DIRECTORY"], config["RESULT_FILE"]), "a") as f:
        writer = csv.writer(f)
        writer.writerow([config["RESULT_AUTHOR"], file_path, start, end, config["LANGUAGE_PROFICIENCY"]])

def ensure_folder_structure():
    if not os.path.exists(config["DATA_DIRECTORY"]):
        os.makedirs(config["DATA_DIRECTORY"])

    if not os.path.exists(config["RESULT_DIRECTORY"]):
        os.makedirs(config["RESULT_DIRECTORY"])

    if not os.path.exists(os.path.join(config["RESULT_DIRECTORY"], config["RESULT_FILE"])):
        with open(os.path.join(config["RESULT_DIRECTORY"], config["RESULT_FILE"]), "w") as f:
            writer = csv.writer(f)
            writer.writerow(config["RESULT_ENTRIES"])


def main():
    first_run = True
    config_index = 0

    print(f"There are {len(config["RUN_CONFIGURATIONS"])} runs configured.")
    print(f"After the first batch of configured runs, you can choose to quit or continue after each run.\n")

    while True:
        current_config = config["RUN_CONFIGURATIONS"][config_index] if len(config["RUN_CONFIGURATIONS"]) > 0 else {}

        blob = generate_text_blob(
            current_config.get("SENTENCES", config["NUM_SENTENCES"]),
            current_config.get("PARAGRAPHS", config["NUM_PARAGRAPHS"]),
            current_config.get("CORPUS", config["CORPUS_FILE"])
        )

        print("You'll be prompted with one or multiple paragraphs of randomly generated text. When you're done reading, press the enter key")
        input("Press enter when you're ready\n")
        print("\n\n\n")

        start = time.time() * 1000
        print(blob)
        input("\n\n\n")
        end = time.time() * 1000
        start = start // 1
        end = end // 1

        file_path, file_name = write_text_blob(blob)
        write_result_line(file_path, start, end)

        config_index = (config_index + 1) % len(config["RUN_CONFIGURATIONS"]) if len(config["RUN_CONFIGURATIONS"]) > 0 else 0
        if first_run and config_index == 0:
            first_run = False

        if not first_run and input("Continue? [Y]es/[N]o ").lower() == "n":
            break


# ===== Example usage =====
if __name__ == "__main__":
    load_config("./config.json")
    ensure_folder_structure()
    main()