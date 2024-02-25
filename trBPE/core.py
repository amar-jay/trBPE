import regex as re


def turkish_word_splitter(word: str):
    """
    Splits word into root and other suffixes based on context 
    """
    # Define lists of Turkish suffixes categorized by type
    possessive_suffixes = ['ım', 'im', 'ın', 'in', 'ı', 'i', 'um', 'üm', 'un', 'ün', 'uz', 'ünüz', 'larım', 'lerim', 'larım', 'lerim', 'larımız', 'lerimiz', 'ları', 'leri', 'lar', 'ler']
    plural_suffixes = ['ların', 'lerin', 'ler', 'lar']
    case_suffixes = ['da', 'de', 'ta', 'te', 'dan', 'den', 'tan', 'ten', 'a', 'e', 'ı', 'i', 'u', 'ü', 'yi', 'yı', 'yu', 'yü']
    tense_markers = ['yor', 'acak', 'ecek', 'dı', 'di', 'du', 'dü']
    other_suffixes = ['dır', 'dir', 'ki']

    suffix_order = [*other_suffixes, *tense_markers, *case_suffixes, *plural_suffixes, *possessive_suffixes]

    root = word
    suffixes = []

    stop = 0
    # Iterate until the root is not empty or all possible suffixes have been checked
    while len(root) > 0 and stop < len(suffix_order):

        for suffix in suffix_order:
            if root.endswith(suffix):
                root = root[:-len(suffix)]  # Remove the suffix from the root and add it to the suffixes list
                suffixes.append(suffix)
                stop = 0
                break

            stop += 1

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


def visualise_tokens(token_values: list[bytes]) -> None:
    """
        Meant for debugging. It prints tokens based on colors
        @param token_values list of token bytes
    """

    background = [f"\u001b[48;5;{i}m" for i in [167, 179, 185, 77, 80, 68, 134]]
    # If token boundaries do not occur at unicode character boundaries, it's unclear how best to
    # visualise the token. Here, we'll just use the unicode replacement character to represent some
    # fraction of a character.
    # https://github.com/openai/tiktoken/blob/main/tiktoken/_educational.py#L147
    unicode_token_values = [x.decode("utf-8", errors="replace") for x in token_values]

    running_length = 0
    last_color = None
    for token in unicode_token_values:
        color = background[running_length % len(background)]
        if color == last_color:
            color = background[(running_length + 1) % len(background)]
            assert color != last_color
        last_color = color
        running_length += len(token)
        print(color + token, end="")
    print("\u001b[0m")
