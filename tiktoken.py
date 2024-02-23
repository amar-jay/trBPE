import json
import regex as re
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

if __name__ == "__main__":
    print("regex split sample text")
    with open("sample.txt", "r") as f:
        text = f.read()
        print(regex_split(text))

    """
    print("loading tiktoken_bpe")
    bpe = load_cached_tiktoken_bpe("base.tiktoken", "base.bpe")
    print(bpe[-100:])
    print("saving file")
    """
