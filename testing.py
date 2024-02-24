import json
import regex as re
from TurkishStemmer import TurkishStemmer
from trBPE.core import visualise_tokens
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

def turkish_word_splitter(word: str):
    possessive_suffixes = ['ım', 'im', 'ın', 'in', 'ı', 'i', 'um', 'üm', 'un', 'ün', 'uz', 'ünüz', 'larım', 'lerim', 'larım', 'lerim', 'larımız', 'lerimiz', 'ları', 'leri', 'lar', 'ler']
    plural_suffixes = ['ler', 'lar']
    case_suffixes = ['da', 'de', 'ta', 'te', 'dan', 'den', 'tan', 'ten', 'a', 'e', 'ı', 'i', 'u', 'ü', 'yi', 'yı', 'yu', 'yü']
    tense_markers = ['yor', 'acak', 'ecek', 'dı', 'di', 'du', 'dü']
    other_suffixes = ['dır', 'dir', 'ki']

    suffix_order = [*other_suffixes, *tense_markers, *case_suffixes, *plural_suffixes, *possessive_suffixes]

    root = word
    suffixes = []

    stop = 0
    while len(root) > 0 and stop < len(suffix_order):
        for suffix in suffix_order:
            if root.endswith(suffix):
                root = root[:-len(suffix)]
                suffixes.append(suffix)
                #print(root, suffixes, stop)
                stop = 0
                break
            stop += 1
            #suffixes.append(suffix)
    return list(reversed(suffixes + [root]))

def turkish_split(text: str):
    """
    split the text into words using vocab.txt similar to the way the tokenizer does;
    - turkish is aggulutinative by nature, so agglutinated pieces begin with `##` in tokenizer
    This is usuallay done with regex. However, I am bad at it so I did it this way
    """
    with open("vocab.txt", "r") as f:
        vocabs = f.read().splitlines()
    words = []
    # split the text into words
    pattern = r"""[^\r\n\p{L}\p{N}]?+\p{L}+|\p{N}{1,3}| ?[^\s\p{L}\p{N}]++[\r\n]*|\s*[\r\n]|\s+(?!\S)|\s+"""
    _pattern = re.compile(pattern)
    regex_split = lambda x: re.findall(_pattern, x)
    for word in regex_split(text):
        # check if the word is in the vocabs
        if word.strip() in vocabs or word in vocabs:
            words.append(word)
        else:
            # if not, split the word into subwords
            for subword in turkish_word_splitter(word):
                # check if the subword is in the vocabs
                if subword.strip() in vocabs:
                    words.append(subword)
                elif "##" + subword.strip() in vocabs:
                    words.append(subword)
                else:
                    # if not, split the subword into characters
                    for char in regex_split(subword):
                        # check if the character is in the vocabs
                        if char in vocabs:
                            words.append(char)
                        else:

                            # if not, split the character into characters
                            # # Split text into characters and combine consecutive spaces
                            # I don't know why this is necessary, but that's what seems to be different with GPT-4 tokenizer
                            characters = [char[0]]
                            for i in range(1, len(char)):
                                if char[i] == ' ' and char[i - 1] == ' ':
                                    characters[-1] += char[i]
                                    continue
                                characters.append(char[i])

                            words.extend(characters)

    return words

def _visualize(word):
    return visualise_tokens(list(c.encode('utf-8') for c in word))

if __name__ == "__main__":
    print("turkish language split")
    word = "okuldakilerden"
    print("Turkish word splitter for", word, turkish_word_splitter(word), turkish_word_splitter("evlerimizden"))
    _visualize(turkish_word_splitter(word))
    _visualize(turkish_word_splitter("sokaklarda"))
    print("-"*8, "TURKISH WORD TOKENS", "-"*8)
    with open("tr_sample.txt", "r") as f:
        w = f.read()
        print(w)
        print("-"*27)

        words = turkish_split(w)
        print(words)
        print("-"*27)

        _visualize(words)
        print("-"*27)

        x_words = turkish_word_splitter(w)
        print(x_words)
        print("-"*27)

        _visualize(x_words)
        print("-"*27)

    words = turkish_split("merhaba dünyadaki insanlar! okuldakilerden biri olmak istiyorum.")
    _visualize(words)
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

