<div align="center">
  <h2>trBPE</h2>
</div>

The current landscape of LLMs predominantly caters to the English language. This bias can be attributed to two primary factors: extensive training on English datasets and the efficacy of token embedding. Notably, GPT4's token embedding stands out as one of the most advanced in recent times. Its superiority lies in its ability to contextualize tokens based on syllabic divisions, enhancing comprehension and generation capabilities.

However, for foreign languages, especially Turkish, this advantage diminishes due to the inherent randomness in tokenization. Consequently, there is a pressing need to address this limitation, prompting the creation of this repository. Our goal is to develop a BPE tokenizer specifically tailored to Turkish, leveraging datasets rich in Turkish language content.

An Attempt of replicating this [paper](https://www.cmpe.boun.edu.tr/~gungort/theses/A%20Comprehensive%20Analysis%20of%20Subword%20Tokenizers%20for%20Morphologically%20Rich%20Languages.pdf) 
 for BPE tokenizers, while making a few exceptions 
1. all non-agglutinative pieces with with a space and agglutinatve pieces are not preceded by `#`
2. case insensitive

Why not wordpiece? 
---
Well, apparently the Wordpiece implementation is similar to Huggingface/tokenizer. So no need to. 
Also, we believe splitting it only based on grammatical structure on trained piece limits the capture of grammatically wrong structure. 
Thus, leading to either not splitting word at all or split it on character level. Grammatical sound pieces, are preintitialized as mergeable ranks.
<!-- ![affine](./assets/tokens.png)

![colored](./assets/colored_tokens.png) -->

