import json
import regex as re
from TurkishStemmer import TurkishStemmer
from trBPE.core import visualise_tokens, turkish_word_splitter, turkish_split
import base64
import os


# https://github.com/openai/tiktoken/blob/1b9faf2779855124f05174adf1383e53689ed94b/tiktoken/load.py#L143
def load_tiktoken_bpe(
    tiktoken_bpe_file: str
) -> list[str]:
    # NB: do not add caching to this function
    with open(tiktoken_bpe_file, "rb") as f:
        contents = f.read()

    res = []
    lines = [line.split() for line in contents.splitlines() if line]
    print("lines count", len(lines))
    unable_to_decode = 0
    
    for token, _ in lines:
        try:
            v = base64.b64decode(token).decode("utf-8")
            res.append(v)
        except:
            unable_to_decode += 1

    print("unable to decode", unable_to_decode)
    return res


def load_cached_tiktoken_bpe(
    tiktoken_bpe_file: str,cache_file: str 
) -> list[str]:
    # NB: do not add caching to this function
    if os.path.exists(cache_file):

        encoding = []
        with open(cache_file, "rb") as f:
            for line in f.read().splitlines():
                encoding.append(line)
        return list(map(lambda x: x.decode("utf-8"), encoding))


    encoding = load_tiktoken_bpe(tiktoken_bpe_file)
    with open(cache_file, "w+") as f:
        for line in encoding:
            f.write(line + "\n")
    return encoding

def regex_split(text:str):
    """""
    GPT-4 tokenizer (cl100k_base) regex split
    """
    pattern = r"""'(?i:[sdmt]|ll|ve|re)|[^\r\n\p{L}\p{N}]?+\p{L}+|\p{N}{1,3}| ?[^\s\p{L}\p{N}]++[\r\n]*|\s*[\r\n]|\s+(?!\S)|\s+"""
    _pattern = re.compile(pattern)
    return re.findall(_pattern, text)

splitter = TurkishStemmer()
def turkish_stemmer_split(text: str):
    """
    split the text into words based on the Turkish Stemmer library
    NOTE: doesn't work as expected, apparently it just derives the root of the word
    """
    splitter.stem(text)
    return splitter.__dict__


def _visualize(word):
    return visualise_tokens(list(c.encode('utf-8') for c in word))

if __name__ == "__main__":
    print("turkish language split")

    _visualize(turkish_word_splitter("onlarındakilerden"))
    _visualize(turkish_word_splitter("sokaklarda"))
    print("-"*21, "TURKISH WORD TOKENS", "-"*21)
    with open("tr_sample.txt", "r") as f:
        w = f.read()
        print(w)
        print("-"*63)

        words = turkish_split(w)
        print(words)
        print("-"*63)

        _visualize(words)
        print("-"*63)
    #visualise_tokens(words)
    #    print(turkish_split("merhaba dünyadaki insanlar! okuldakilerden biri olmak istiyorum."))

    """
    print("regex split sample text")
    with open("sample.txt", "r") as f:
        text = f.read()
        print(regex_split(text))
    print("loading tiktoken_bpe")
    bpe = load_cached_tiktoken_bpe("base.tiktoken", "base.bpe")
    print(bpe[-100:])
    print("saving file")
    """

