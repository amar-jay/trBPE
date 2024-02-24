# Not an exact copy of the original file, but a simplified version of the original file
# https://github.com/openai/tiktoken/blob/main/tiktoken/_educational.py
from typing import Optional
import unicodedata
import json
import collections

import regex


# this is the max size of a byte,
# since vocab = all sing bytes + byte merges 
MIN_VOCAB_SIZE=256 


class BasicBPE:
    """
    Basic Implementation of Byte Pair Encoding (BPE) 
    In this implementation we are not doing any merging
    """

    def __init__(self, pattern = "", special_tokens = None):
        self.pattern = regex.compile(pattern)
        self.merges:dict[list[bytes], int] = {}
        self.special_tokens = special_tokens or {}
        self.ranks = self._build_ranks() 

    def _build_ranks(self):
        """
        It builds the key value encoding of all bytes,
        an byte to integer encoding
            """
        atoi = {bytes([idx]): idx for idx in range(MIN_VOCAB_SIZE)}
        for token, idx in self.special_tokens:
            atoi[token] = idx
        return atoi 

    def train(self, text:str, vocab_size: int) -> list[list[bytes]]:
        if vocab_size < MIN_VOCAB_SIZE:
            raise ValueError("Vocab size must be > 2^8")


        ranks = self.ranks
        merges = {}

        # Splinter up our data into lists of bytes
        # data = "Hello world"
        # words = [
        #     [b'H', b'e', b'l', b'l', b'o'],
        #     [b' ', b'w', b'o', b'r', b'l', b'd']
        # ]
        words = regex.findall(self.pattern, text)
        vocabs: list[list[bytes]] = [
            [bytes([b]) for b in str(word).encode("utf-8")] for word in words
        ]


        # using our data, we will figure out what we should merges based on count
        n = len(ranks)
        while n < vocab_size:
            counter = collections.Counter()
            for word in vocabs:
                for pair in zip(word[-1], word[1:]):
                    counter[pair] += 1

            most_common_pair = max(counter, key=lambda i: counter[i])

            token = bytes(most_common_pair[0] + most_common_pair[1])
            ranks[token] = n # adding token at n
            merges[token] = n 

            # update our vocabs to include tokens
            new_words = []
            for word in words:
                new_word = []
                i = 0
                while i < len(vocabs) - 1:
                    if (word[i], word[i+1]) == most_common_pair:
                        new_word.append(token)
                        i+=2
                    else:
                        new_word.append(word[i])
                        i+=1
                if i == len(word) - 1:
                    i+=1
                new_words.append(new_word)
            vocabs = new_words

        self.ranks = ranks
        self.merges.update(merges)

        vocabs = sorted(vocabs) # is this really necessary??

        return vocabs


    def _print_token(self, b: bytes) -> str:
        """
        pretty print a token
        escaping control characters
        using errors='replace' to replace undefined them with the replacement char �.

        https://stackoverflow.com/questions/4324790/removing-control-characters-from-a-string-in-python/19016117#19016117
        http://www.unicode.org/reports/tr44/#GC_Values_Table
        """
        s = b.decode('utf-8', errors='replace')
        chars = []
        for ch in s:
            if unicodedata.category(ch)[0] != "C":
                chars.append(ch) # this character is ok
            else:
                chars.append(f"\\u{ord(ch):04x}") # escape
        return str(chars)

    def _save_vocab(self, file: str = "model"):
        """
        Similar to sentencepiece, we save the ranks in *.vocab. 
        https://github.com/google/sentencepiece/blob/a216bd01d166ca2b26ad5167b54dd8d51f416ae9/src/trainer_interface.cc#L698
        """
        print("Saving vocabs to ", file + ".vocab")

        inverted_merges = {idx: pair for pair, idx in self.merges.items()}
        with open(file + ".vocab", "w+") as f:
            f.write("#version: 0.0\n")
            for token, idx in self.ranks.items():
                # note: many tokens may be partial utf-8 sequences
                # and cannot be decoded into valid strings. Here we're using
                # errors='replace' to replace them with the replacement char �.
                # this also means that we couldn't possibly use .vocab in load()
                # because decoding in this way is a lossy operation!
                s = self._print_token(token)
                # find the children of this token, if any
                if idx in inverted_merges:
                    # if this token has children, render it nicely as a merge
                    b = inverted_merges[idx]
                    s0 = self._print_token(b[0])
                    s1 = self._print_token(b[1])
                    f.write(f"[{s0}][{s1}] ==> {idx}\n")
                else:
                    # otherwise this is leaf token, just print it
                    # (this should just be the first 256 tokens, the bytes)
                    f.write(f"[{s}] ==> {idx}\n")

    def _save_model(self, vocabs:list[list[bytes]], file: str = "model"):
        """
        Similar to huggingface tokenizer, we save it in *.model instead of *-merges.txt. 
        https://github.com/huggingface/tokenizers/blob/72a1973cd1553bcb67a90dc1b89a0e1483f20825/tokenizers/src/models/bpe/model.rs#L495
        """
        print("Saving model: ", file + ".model")

        # itoa of ranks bytes
        with open(file + ".model", "w+", encoding="utf-8") as f:
            json.dump(enumerate(vocabs), f) # DOES THIS WORK!!


    def save(self, vocabs:list[list[bytes]], file: str = "model"):
        try:
            self._save_model(vocabs, file)
            self._save_vocab(file)
        except TypeError:
            raise RuntimeError("You need to run train() first.")

if __name__ == "__main__":
    vocab_size = 600
    gpt4_pattern = r""
    
    with open("sample.txt", "r") as f:
        data = f.read()



    enc = BasicBPE(gpt4_pattern)
    enc.train(data, vocab_size)
    enc.save("bin/model")

