import random
import re
from collections import defaultdict

def generate_text_blob(num_sentences=5, num_paragraphs=1):
    # Training corpus — replace with more text for variety
    corpus = """
    The wind whispered through the silent trees as shadows stretched across the path.
    Beyond the hills, the sky burned with the orange glow of a fading sun.
    A river wound lazily through the valley, carrying with it the scent of distant rain.
    In the quiet village, windows glimmered with the warmth of candlelight.
    Somewhere in the distance, a lone bell tolled, slow and heavy.
    Time seemed to pause, holding its breath for something unseen.
    """
    
    # Tokenize corpus
    words = re.findall(r"\b\w+\b|[.!?]", corpus)
    
    # Build Markov chain
    chain = defaultdict(list)
    for i in range(len(words) - 2):
        key = (words[i], words[i+1])
        chain[key].append(words[i+2])
    
    def generate_sentence():
        start = random.choice([k for k in chain.keys() if k[0][0].isupper()])
        w1, w2 = start
        sentence = [w1, w2]
        
        while True:
            next_word = random.choice(chain[(w1, w2)])
            sentence.append(next_word)
            if next_word in ".!?":
                break
            w1, w2 = w2, next_word
            if len(sentence) > random.randint(8, 20):
                sentence.append(".")
                break
        
        return " ".join(sentence).replace(" .", ".").replace(" !", "!").replace(" ?", "?")
    
    paragraphs = []
    for _ in range(num_paragraphs):
        sentences = [generate_sentence() for _ in range(num_sentences)]
        paragraphs.append(" ".join(sentences))
    
    return "\n\n".join(paragraphs)


def main():
    print(generate_text_blob)

if __name__ == "__main__":
    main()