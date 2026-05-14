from __future__ import annotations

import math
import os
import pickle
import random
import re
import unicodedata
from collections import Counter
from pathlib import Path

import numpy as np

try:
    import pandas as pd
    from rank_bm25 import BM25Okapi
    from sklearn.metrics.pairwise import cosine_similarity
    _DEPS_OK = True
except ImportError:
    _DEPS_OK = False

NOMS_CAT = {
    'areti-maso': 'areti-maso',
    'aretim-po': 'aretim-po',
    'aretin-doha': 'aretin-doha',
    'aretin-kibo': 'aretin-kibo',
    'aretin-pivalanana': 'aretin-pivalanana',
    'aretin-tanana': 'aretin-tanana',
    'aretin-tenda': 'aretin-tenda',
    'aretin-tongotra': 'aretin-tongotra',
    'aretin-tratra': 'aretin-tratra',
    'aretin-tsaina': 'aretin-tsaina',
    'aretin-urinaire': 'aretin-urinaire',
    'diabeta': 'diabeta',
    'fiakaran-ny-tosi-dra': 'fiakaran-ny-tosi-dra',
    'kohaka': 'kohaka',
    'tazo': 'tazo',
    'tazomoka': 'tazomoka',
}

ICONES = {
    'areti-maso': '👁',
    'aretim-po': '❤️',
    'aretin-doha': '🧠',
    'aretin-kibo': '🤢',
    'aretin-pivalanana': '🚽',
    'aretin-tanana': '🤲',
    'aretin-tenda': '🗯',
    'aretin-tongotra': '🦶',
    'aretin-tratra': '🫀',
    'aretin-tsaina': '🧘',
    'aretin-urinaire': '💧',
    'diabeta': '💉',
    'fiakaran-ny-tosi-dra': '🩸',
    'kohaka': '😮',
    'tazo': '🌡',
    'tazomoka': '🦟',
}

SALUTATIONS = {
    'salama': (
        " Salama! Tongasoa eto amin'ny Chatbot Médical Malagasy!\n"
        " Lazao amiko ny soritr'aretinao amin'ny teny malagasy.\n"
        " Ohatra: 'Marary ny lohako' na 'Voan'ny tazo aho'."
    ),
    'manao ahoana': " Manao ahoana! Lazao amiko ny soritr'aretinao mba ahafahako manampy anao.",
    'manahoana':    " Manahoana! Inona no azoko anampiana anao?",
    'mbola tsara':  " Mbola tsara eh! Inona no azoko anampiana anao momban'ny fahasalamanao?",
    'veloma':       " Veloma! Mirary fahasalamana ho anao aho. Mitandrema amin'ny lafiny rehetra!",
    'misaotra':     " Misaotra betsaka! Faly hatrany aho manampy anao.",
    'misaotra betsaka': " Misaotra betsaka! Veloma ary tandremo ny fahasalamanao!",
    'eny':          " Tsara! Azonao atao ny milaza fanazavana fanampiny.",
    'tsia':         " Azo atao. Inona no mba hanampiako anao?",
    '/ampio': (
        " Torohevitra fampiasana:\n"
        " • Soraty ny soritr'aretinao amin'ny teny malagasy\n"
        " • Ohatra: 'Marary ny lohako', 'Voan'ny tazo aho'\n"
    ),
}

MSG_LANGUE = (
    " Azafady, resaho amin'ny malagasy ny momba ny fahasalamanao sy ny aretina mahazo anao."
)

MSGS_GIB = [
    "Tsy azonko izany teny izany. Mba soraty ny soritr'aretinao amin'ny malagasy.",
    "Miala tsiny, fa tsy mahalala izany voambolana izany aho. Lazao amin'ny malagasy azafady.",
    "Tsy mahafantatra izany aho. Inona ny soritr'aretina mahazo anao? Soraty amin'ny malagasy.",
]

MSGS_HORS = [
    "Miala tsiny fa tsy ao anatin'ny sehatry ny fitsaboana izany. Inona no soritr-aretina misy anao?",
    "Tsy misy fandikana ara-pahasalamana amin'izany. Lazao ny soritr'aretinao mba hanampiako.",
]

SYMPTOMES_GRAVES = [
    'mangorakoraka tampoka', 'very hevitra', 'lavo tampoka',
    'tsy afaka miaina', 'tazo 40', 'ra mivoaka be',
    'te hamono tena', 'tsy te-ho velona', 'tsy mahatsiaro tena', 'convulsion',
    'aita ny aina', 'infarctus', 'very ny hevitra', 'paralysie',
]

MSG_URGENCE = (
    " SORITR-ARETINA MAFY! MANDEHANA ANY AMIN-NY HOPITALY HAINGANA! \n"
    "Ity soritr-aretina ity dia mahafaty haingana aza miandry ela intsony, mandehana hopitaly izao!"
)

VOYELLES = set('aeiouàâäéèêëîïôùûü')

CONF_MED = 0.35
CONF_LOW = 0.18
SIM_LOW  = 0.12

MOTS_MG_CORE = {
    'aho', 'izaho', 'ianao', 'izy', 'ny', 'misy', 'tsy', 'efa', 'mbola',
    'marary', 'manaintaina', 'mafana', 'tazo', 'kohaka', 'mandrevo',
    'loha', 'kibo', 'maso', 'tenda', 'tratra', 'tongotra', 'tanana',
    'vatana', 'fo', 'nify', 'dokotera', 'fanafody', 'aretina',
    'tazomoka', 'diabeta', 'salama', 'veloma', 'misaotra',
}

MOTS_FR_CORE = {
    'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles',
    'bonjour', 'bonsoir', 'merci', 'oui', 'non', 'est', 'suis',
    'avoir', 'faire', 'aller', 'mal', 'douleur', 'médecin', 'maladie',
}

MOTS_EN_CORE = {
    'i', 'you', 'he', 'she', 'we', 'they', 'is', 'are', 'have', 'has',
    'hello', 'hi', 'yes', 'no', 'pain', 'sick', 'doctor', 'fever',
    'headache', 'medicine', 'help', 'feel', 'need',
}

MOTS_HORS_CORE = {
    'fiara', 'moto', 'bus', 'taxi', 'vola', 'ariary', 'lalao',
    'football', 'cinema', 'facebook', 'internet', 'wifi', 'solosaina',
    'sekoly', 'oniversite', 'politika', 'fifidianana',
}


class MalagasyTokenizer:
    SYNONYMES = {
        'marary':   ['manaintaina', 'mangirifiry', 'fanaintainana'],
        'loha':     ['lohako', 'lohany'],
        'kibo':     ['kibony', 'kiboko'],
        'maso':     ['masoko', 'masony'],
        'tratra':   ['tratrako'],
        'tenda':    ['tendako', 'tendany', 'marary tenda'],
        'tongotra': ['tongotro', 'lohalika', 'ratsan-tongotra'],
        'tanana':   ['tananako', 'ankihibe', 'ratsan-tanana'],
        'tazo':     ['manavy', 'mafana', 'mamay'],
        'tazomoka': ['tazo avy amin ny kaikitry ny moka'],
        'kohaka':   ['mikohaka'],
        'pipi':     ['mamany', 'mipipi'],
        'foko':     ['fo'],
        'diabeta':  ['fiakaran ny siramamy', 'fidinan ny siramamy'],
        'tsindry':  ['tosi-dra', 'hypertension'],
        'saiko':    ['saina', 'kivy'],
        'mandrevo': ['mivalanana', 'mivalan-tay'],
        'nify':     ['nifiko', 'nifinao'],
    }

    def clean(self, text: str) -> str:
        if not isinstance(text, str):
            return ''
        t = text.lower()
        t = unicodedata.normalize('NFKD', t)
        t = ''.join(c for c in t if not unicodedata.combining(c))
        t = t.replace("'", "'").replace('`', "'")
        t = re.sub(r"[^\w\s'\-]", ' ', t)
        return re.sub(r'\s+', ' ', t).strip()

    def tokenize(self, text: str) -> list[str]:
        tokens = []
        for t in self.clean(text).split():
            if len(t) > 1:
                tokens.append(t)
                if '-' in t:
                    tokens.extend([p for p in t.split('-') if len(p) > 1])
        return tokens

    def expand(self, text: str) -> str:
        tokens = self.tokenize(text)
        extra = []
        for tok in tokens:
            for key, syns in self.SYNONYMES.items():
                if tok == key or tok in syns:
                    extra.extend([s for s in [key] + syns if s != tok])
        return ' '.join(tokens + extra)

    def for_tfidf(self, text: str) -> str:
        return self.clean(self.expand(text))

class HybridRetriever:
    def __init__(self, df, tok: MalagasyTokenizer, tfidf_vec):
        self.df   = df.reset_index(drop=True)
        self.tok  = tok
        corpus_tok = [tok.tokenize(str(t)) for t in df['texte']]
        self.bm25 = BM25Okapi(corpus_tok)
        self.vec  = tfidf_vec
        self.mat  = self.vec.transform(
            [tok.clean(str(t)) for t in df['texte']]
        )

    def get(self, query: str, category: str | None = None):
        qc     = self.tok.clean(self.tok.expand(query))
        bm25_s = np.array(self.bm25.get_scores(qc.split()))
        mx     = bm25_s.max()
        if mx > 0:
            bm25_s /= mx
        cos_s = cosine_similarity(self.vec.transform([qc]), self.mat).flatten()
        score = 0.45 * bm25_s + 0.55 * cos_s

        if category:
            mask = (self.df['cat_base'] == category).values
            if mask.sum() > 0:
                s2         = score.copy()
                s2[~mask] *= 0.25
                idx        = int(s2.argmax())
            else:
                idx = int(score.argmax())
        else:
            idx = int(score.argmax())

        return self.df.iloc[idx], float(score[idx])

def _vowel_ratio(word: str) -> float:
    if not word:
        return 0.0
    return sum(1 for c in word if c in VOYELLES) / len(word)

def _max_cons_run(word: str) -> int:
    run = mx = 0
    for c in word:
        if c.isalpha() and c not in VOYELLES:
            run += 1
            mx   = max(mx, run)
        else:
            run  = 0
    return mx

def _entropy(word: str) -> float:
    if not word:
        return 0.0
    c = Counter(word)
    l = len(word)
    return -sum((v / l) * math.log2(v / l) for v in c.values())

def _is_gib_word(w: str) -> bool:
    w = w.lower()
    if len(w) < 4:
        return False
    vr = _vowel_ratio(w)
    cr = _max_cons_run(w)
    if vr == 0.0 and len(w) >= 2:
        return True
    if vr < 0.30 and cr >= 2:
        return True
    if _entropy(w) > 3.2 and len(w) > 2:
        return True
    if cr >= 2:
        return True
    return False

def is_gibberish(text: str) -> bool:
    words = re.findall(r'[a-zA-Z]{4,}', text.lower())
    if not words:
        return False
    n_gib = sum(1 for w in words if _is_gib_word(w))
    return n_gib / len(words) > 0.50

def detect_language(text: str) -> str | None:
    if re.search(r'[\u0400-\u04FF\u0600-\u06FF\u4E00-\u9FFF\u3040-\u30FF]', text):
        return 'autre'
    words = set(re.findall(r'[a-zA-Z]+', text.lower()))
    if not words:
        return None
    if words & MOTS_MG_CORE:
        return None
    total   = max(len(words), 1)
    hits_fr = len(words & MOTS_FR_CORE)
    hits_en = len(words & MOTS_EN_CORE)
    if hits_fr / total > 0.25:
        return 'francais'
    if hits_en / total > 0.25:
        return 'anglais'
    if total >= 3 and not (words & MOTS_MG_CORE):
        return 'autre'
    return None

def is_hors_domaine(text: str) -> bool:
    words = set(text.lower().split())
    if words & MOTS_HORS_CORE:
        return True
    if len(words) > 2 and not (words & MOTS_MG_CORE):
        return True
    return False

def detect_salutation(text: str) -> str | None:
    t = text.lower().strip()
    if t in SALUTATIONS:
        return SALUTATIONS[t]
    for key in sorted(SALUTATIONS, key=len, reverse=True):
        if len(key) > 3 and (t == key or t.startswith(key) or key in t):
            return SALUTATIONS[key]
    return None

def check_grave(text: str) -> str | None:
    t = text.lower()
    return MSG_URGENCE if any(s in t for s in SYMPTOMES_GRAVES) else None

def build_response(category: str, med1: str, med2: str, astuce: str) -> str:
    def ok(v):
        v = str(v).strip()
        return v if v and v.lower() not in ('nan', 'none', '') else ''

    m1  = ok(med1)
    m2  = ok(med2)
    a   = ok(astuce)
    nom = NOMS_CAT.get(category, category)

    parties = []
    if m1:
        parties.append(f"Raha {nom} no mahazo anao dia mila mihinana ny fanafody {m1}.")
    else:
        parties.append(f"Raha {nom} no mahazo anao, tsara raha mandehana dokotera.")
    if m2:
        parties.append(f"Raha tsy sitrana, dia andramo indray ity fanafody ity {m2}.")
    if a:
        parties.append(f"Ary ity ny torohevitra kely omeko anao: {a}.")
    parties.append("Ka raha tena tsy mijanona ny aretina, mitsangana mandehana dokotera.")
    return ' '.join(parties)

def _indicator(conf: float) -> str:
    if conf >= CONF_MED:
        return "green"
    if conf >= CONF_LOW:
        return "yellow"
    return "red"

class ChatService:

    _instance: "ChatService | None" = None

    def __init__(self):
        self._ready    = False
        self._pipeline = None
        self._le       = None
        self._retriever: HybridRetriever | None = None
        self._tok      = MalagasyTokenizer()
        self._idx2cat: dict[int, str] = {}

        model_dir = os.getenv("CHATBOT_MODEL_DIR", "")
        if not model_dir:
            print("CHATBOT_MODEL_DIR non défini mode fallback")
            return

        path = Path(model_dir)
        required = ["pipeline.pkl", "encoder.pkl",
                    "retriever_tfidf.pkl", "dataset_clean.csv"]
        missing = [f for f in required if not (path / f).exists()]
        if missing:
            print(f"Attention artefacts manquants {missing} — mode fallback")
            return

        if not _DEPS_OK:
            print("Attention dépendances ML manquantes (pandas/rank_bm25) — mode fallback")
            return

        try:
            with open(path / "pipeline.pkl",        "rb") as f:
                self._pipeline = pickle.load(f)
            with open(path / "encoder.pkl",         "rb") as f:
                self._le       = pickle.load(f)
            with open(path / "retriever_tfidf.pkl", "rb") as f:
                tfidf_vec = pickle.load(f)

            df = pd.read_csv(path / "dataset_clean.csv", encoding="utf-8")
            for col in ["texte", "medicament1", "medicament2", "astuce", "cat_base"]:
                if col not in df.columns:
                    df[col] = ""
                df[col] = df[col].fillna("")
            df = df.drop_duplicates(subset=["texte"]).reset_index(drop=True)

            self._retriever = HybridRetriever(df, self._tok, tfidf_vec)
            self._idx2cat   = {i: c for i, c in enumerate(self._le.classes_)}
            self._ready     = True
            print(f"ChatService prêt — {len(df)} docs, {len(self._le.classes_)} classes")

        except Exception as exc:
            print(f"Erreur chargement modèle: {exc} — mode fallback")

    @classmethod
    def get(cls) -> "ChatService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def chat(self, user_input: str, session_last_cat: str | None = None) -> dict:

        ui = (user_input or "").strip()

        if not ui:
            return self._special("empty", "Mba soraty zavatra...")
        if len(ui) < 5:
            return self._special("too_short", "Mba omeo fanazavana fanampiny.")

        sal = detect_salutation(ui)
        if sal:
            return {"type": "salutation", "response": sal}

        if is_gibberish(ui):
            return self._special("gibberish", random.choice(MSGS_GIB), ood=True)

        lang = detect_language(ui)
        if lang:
            return self._special("langue", MSG_LANGUE, ood=True)

        if is_hors_domaine(ui):
            return self._special("hors_domaine", random.choice(MSGS_HORS), ood=True)

        alerte = check_grave(ui)

        if not self._ready:
            fb = (alerte + "\n\n" if alerte else "") + random.choice(MSGS_HORS)
            return self._special("fallback", fb, alerte=alerte, ood=True)

        proc  = self._tok.for_tfidf(ui)
        probs = self._pipeline.predict_proba([proc])[0]
        idx   = int(probs.argmax())
        cat   = self._idx2cat[idx]
        conf  = float(probs[idx])

        if (conf < CONF_MED
                and session_last_cat
                and session_last_cat not in ("gibberish", "hors_domaine", "langue")):
            cat  = session_last_cat
            conf = max(conf, CONF_MED)

        top_idx = probs.argsort()[-3:][::-1]
        top3    = [
            {"categorie": self._idx2cat[i],
             "icon":      ICONES.get(self._idx2cat[i], "🏥"),
             "score":     round(float(probs[i]), 3)}
            for i in top_idx
        ]

        row, sim = self._retriever.get(ui, category=cat)

        if conf < CONF_LOW and sim < SIM_LOW and not alerte:
            return self._special("hors_domaine", random.choice(MSGS_HORS), ood=True)

        m1    = str(row.get("medicament1", "")).strip()
        m2    = str(row.get("medicament2", "")).strip()
        astuce = str(row.get("astuce", "")).strip()
        for v in (m1, m2, astuce):
            if v.lower() in ("nan", "none"):
                v = ""

        generated = build_response(cat, m1, m2, astuce)
        icon      = ICONES.get(cat, "🏥")
        label_fr  = NOMS_CAT.get(cat, cat)
        indicator = _indicator(conf)

        return {
            "type":        "medical",
            "categorie":   cat,
            "label_fr":    label_fr,
            "icon":        icon,
            "confidence":  round(conf * 100, 1),
            "indicator":   indicator,
            "tfidf_sim":   round(sim, 4),
            "medicament1": m1 or None,
            "medicament2": m2 or None,
            "astuce":      astuce or None,
            "generated":   (alerte + "\n\n" + generated) if alerte else generated,
            "top3":        top3,
            "alerte":      alerte,
            "fallback":    None,
            "ood":         False,
        }

    @staticmethod
    def _special(
        type_: str,
        generated: str,
        *,
        alerte: str | None = None,
        fallback: str | None = None,
        ood: bool = False,
    ) -> dict:
        return {
            "type":        type_,
            "categorie":   None,
            "label_fr":    None,
            "icon":        None,
            "confidence":  None,
            "indicator":   None,
            "tfidf_sim":   None,
            "medicament1": None,
            "medicament2": None,
            "astuce":      None,
            "generated":   generated,
            "top3":        [],
            "alerte":      alerte,
            "fallback":    fallback,
            "ood":         ood,
        }