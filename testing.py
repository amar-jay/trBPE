from tiktoken._educational import train_simple_encoding
import sentencepiece


def load_dataset():
    with open("dataset.txt", "r") as f:
        return f.read()

if __name__ == "__main__":
    print("-"*8, "TESTING TIKTOKEN", "-"*8)
    tik = train_simple_encoding()
    print(">>>", tik.encode(load_dataset()))

    print("-"*8, "TESTING SENTENCEPIECE", "-"*8)
    sp  = sentencepiece
