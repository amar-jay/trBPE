import re
from typing import Dict

MAX_NUM_THREADS = 4


class CoreBPE:
    """
    Core BPE tokenizer
    """
    def __init__(self, encoder: Dict[bytes, Rank], special_tokens_encoder: Dict[str, Rank], pattern: str):
        self.encoder = encoder
        self.special_tokens_encoder = special_tokens_encoder
        self.decoder = {v: k for k, v in encoder.items()}
        self.special_tokens_decoder = {v: k.encode() for k, v in special_tokens_encoder.items()}
        self.regex_tls = [re.compile(pattern) for _ in range(MAX_NUM_THREADS)]
        self.special_regex_tls = [re.compile('|'.join(map(re.escape, special_tokens_encoder.keys()))) for _ in range(MAX_NUM_THREADS)]
        self.sorted_token_bytes = sorted(encoder.keys())
        #self.vocab = self._build_vocab() 

    def _build_vocab(self):
        return NotImplementedError

    def save(self, prefix):
        """
        Saves two files: file_prefix.vocab and file_prefix.model
        This is inspired (but not equivalent to!) sentencepiece's model saving:
            - model file is the critical one, intended for load()
            - vocab file is just a pretty printed version for human inspection only
        """
        model_file = prefix + ".model"
        vocab_file = prefix + ".vocab"
        with open(model_file, "w") as f:
            f.write("")

