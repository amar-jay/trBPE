<div align="center">
  <h2>trBPE</h2>
</div>

The current landscape of Large Language Models (LLMs) predominantly caters to the English language. This bias can be attributed to two primary factors: extensive training on English datasets and the efficacy of token embedding. Notably, the token embedding of GPT-4 stands out as one of the most advanced in recent times. Its superiority lies in its ability to contextualize tokens based on syllabic divisions, thereby enhancing comprehension and generation capabilities.

However, for foreign languages, especially Turkish, this advantage diminishes due to the inherent randomness in tokenization. Consequently, there is a pressing need to address this limitation, which prompted the creation of this repository. Our goal is to develop a Byte Pair Encoding (BPE) tokenizer specifically tailored to Turkish, leveraging datasets rich in Turkish language content.

<div align="center">
  <h3>This is aimed to be used by KomRade in the competition...</h3>
    <h5>Still in dev tho</h5>
</div>


In attempting to replicate the methods outlined in the [paper](https://www.cmpe.boun.edu.tr/~gungort/theses/A%20Comprehensive%20Analysis%20of%20Subword%20Tokenizers%20for%20Morphologically%20Rich%20Languages.pdf), with a few exceptions:

1. All non-agglutinative pieces are preceded by a space, and agglutinative pieces are not `#` prefixed.
2. The tokenization process is case-insensitive.

Why not WordPiece?
---
Apparently, the WordPiece implementation is similar to Huggingface/tokenizer, so there is no need to reinvent the wheel. Additionally, we believe that solely splitting tokens based on grammatical structure, as done in trained WordPiece models, limits the capture of grammatically incorrect structures. This may lead to either not splitting words at all or splitting them on a character level. Grammatically sound pieces are preinitialized as mergeable ranks.

<!-- ![affine](./assets/tokens.png)

![colored](./assets/colored_tokens.png) -->

