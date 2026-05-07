import re
import unicodedata


class MalagasyTokenizer:
    SPECIAL_TOKENS    = {"<PAD>": 0, "<UNK>": 1, "<SOS>": 2, "<EOS>": 3, "<SEP>": 4}
    POSSESSIVE_SUFFIXES = [
        "-ko", "-nao", "-ny", "-ntsika", "-nareo", "-reo", "-dre", "-dreo"
    ]

    def __init__(self, vocab_size: int = 15000):
        self.vocab_size = vocab_size
        self.word2idx   = dict(self.SPECIAL_TOKENS)
        self.idx2word   = {v: k for k, v in self.SPECIAL_TOKENS.items()}

    @staticmethod
    def _normalize_unicode(text: str) -> str:
        nfkd = unicodedata.normalize("NFKD", text)
        return "".join(c for c in nfkd if not unicodedata.combining(c))

    def clean_text(self, text) -> str:
        if not isinstance(text, str) or not text.strip():
            return ""
        text = text.lower()
        text = self._normalize_unicode(text)
        for suf in self.POSSESSIVE_SUFFIXES:
            text = text.replace(suf, "")
        text = re.sub(r"[^\w\s'\-:\/]", "", text)
        return re.sub(r"\s+", " ", text).strip()

    def tokenize(self, text) -> list:
        return [t for t in self.clean_text(text).split() if len(t) > 1]

    def encode(self, text, max_len=128, add_sos=True, add_eos=True) -> list:
        tokens = self.tokenize(text)
        ids    = [self.word2idx.get(t, self.SPECIAL_TOKENS["<UNK>"]) for t in tokens]
        if add_sos: ids = [self.SPECIAL_TOKENS["<SOS>"]] + ids
        if add_eos: ids = ids + [self.SPECIAL_TOKENS["<EOS>"]]
        ids = ids[:max_len]
        ids = ids + [self.SPECIAL_TOKENS["<PAD>"]] * (max_len - len(ids))
        return ids

    def decode(self, ids, skip_special=True) -> str:
        special = set(self.SPECIAL_TOKENS.values()) if skip_special else set()
        return " ".join(
            self.idx2word.get(i, "<UNK>") for i in ids if i not in special
        )

    @property
    def actual_vocab_size(self): return len(self.word2idx)
    @property
    def pad_id(self):  return 0
    @property
    def sos_id(self):  return 2
    @property
    def eos_id(self):  return 3
