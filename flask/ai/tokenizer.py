import re
import unicodedata
from collections import Counter


class MalagasyTokenizer:
    SPECIAL_TOKENS = {"<PAD>": 0, "<UNK>": 1, "<SOS>": 2, "<EOS>": 3, "<SEP>": 4}
    POSSESSIVE_SUFFIXES = [
        "-ko", "-nao", "-ny", "-ntsika", "-nareo", "-reo", "-dre", "-dreo"
    ]
    # ── Synonymes malgaches médicaux (nouveauté v5) ──────────────
    SYNONYMES = {
        "aretin"  : ["aretina", "areti", "farary", "marary"],
        "marary"  : ["manaintaina", "mangirifirifa", "manjinjiritra"],
        "loha"    : ["lohako", "lohany"],
        "kibo"    : ["kibony", "kiboko"],
        "maso"    : ["masoko", "masony"],
        "tratra"  : ["tratranko", "tratray"],
        "tazo"    : ["tazona", "tazony"],
        "fanafody": ["fanafarina", "tsaboina", "tsabo"],
        "dokotera": ["mpitsabo"],
        "rano"    : ["ranovola", "ranon"],
        "sakafo"  : ["fihinana", "hanina"],
        "tenda"   : ["tendako", "tenday"],
        "tongotra": ["kitrokely", "lohalika"],
        "tanana"  : ["tanako", "rantsana"],
    }

    def __init__(self, vocab_size: int = 15000):
        self.vocab_size = vocab_size
        self.word2idx   = dict(self.SPECIAL_TOKENS)
        self.idx2word   = {v: k for k, v in self.SPECIAL_TOKENS.items()}
        self.word_freq  = Counter()

    @staticmethod
    def _normalize_unicode(text: str) -> str:
        nfkd = unicodedata.normalize("NFKD", text)
        return "".join(c for c in nfkd if not unicodedata.combining(c))

    def clean_text(self, text) -> str:
        if not isinstance(text, str) or not text.strip():
            return ""
        text = text.lower()
        text = self._normalize_unicode(text)
        # Normaliser apostrophes
        text = text.replace("\u2019", "'").replace("`", "'")
        for suf in self.POSSESSIVE_SUFFIXES:
            text = re.sub(r"(?<=\w)" + re.escape(suf) + r"\b", "", text)
        text = re.sub(r"[^\w\s'\-]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def tokenize(self, text) -> list:
        cleaned = self.clean_text(text)
        tokens  = []
        for t in cleaned.split():
            if len(t) > 1:
                tokens.append(t)
                # Décomposer mots composés avec tiret (aretin-doha → aretin + doha)
                if "-" in t:
                    parts = [p for p in t.split("-") if len(p) > 1]
                    tokens.extend(parts)
        return tokens

    def expand_query(self, text: str) -> str:
        """
        Expansion de requête avec synonymes malgaches (nouveauté v5).
        Améliore le recall du retriever BM25+TF-IDF.
        Exemple : "marary lohako" → ajoute "manaintaina loha lohany"
        """
        tokens   = self.tokenize(text)
        expanded = list(tokens)
        for token in tokens:
            for key, syns in self.SYNONYMES.items():
                if token == key or token in syns:
                    expanded.extend([s for s in [key] + syns if s != token])
        return " ".join(expanded)

    def build_vocab(self, texts: list):
        counter = Counter()
        for t in texts:
            counter.update(self.tokenize(t))
        self.word_freq = counter
        for word, _ in counter.most_common(self.vocab_size - len(self.SPECIAL_TOKENS)):
            if word not in self.word2idx:
                idx               = len(self.word2idx)
                self.word2idx[word] = idx
                self.idx2word[idx]  = word

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