import csv
import random
import re
from collections import defaultdict
import os
import json

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
	"NUM_SENTENCES": 5,
	"NUM_PARAGRAPHS": 1,
	"PARAGRAPH_SENTENCE_VARIATION": 2
}

def load_config(json_file):
    global config
    with open(json_file, "r", encoding="utf-8") as f:
        json_config = json.load(f)

    for key in config.keys():
        if key in json_config:
            config[key] = json_config[key]
    
    print(config)

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
    num_paragraphs
):
    corpus = load_corpus(config["CORPUS_FILE"])
    chain, words = build_markov_chain(corpus, config["CHAIN_ORDER"])
    
    paragraphs = []
    for _ in range(num_paragraphs):
        # Randomize sentence count per paragraph
        sentence_count = max(1, num_sentences + random.randint(-config["PARAGRAPH_SENTENCE_VARIATION"], config["PARAGRAPH_SENTENCE_VARIATION"]))
        sentences = [generate_sentence(chain, words, config["CHAIN_ORDER"]) for _ in range(sentence_count)]
        paragraphs.append(" ".join(sentences))
    
    return "\n\n".join(paragraphs)

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

# ===== Example usage =====
if __name__ == "__main__":
    load_config("./config.json")
    ensure_folder_structure()
    print(generate_text_blob(config["NUM_SENTENCES"], config["NUM_PARAGRAPHS"]))