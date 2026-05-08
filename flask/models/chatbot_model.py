import os
import pickle
import random

import pandas as pd
import torch
import torch.nn.functional as F
from flask import current_app

from ai.architecture import MiniMedicalLLM
from ai.tokenizer    import MalagasyTokenizer
from ai.retriever    import HybridRetriever    # ← v5 : BM25 + TF-IDF
from config          import Config


# ════════════════════════════════════════════════════════════════
#  load_chatbot — appelé depuis create_app() dans app.py
#  Remplace l'ancien fichier load_chatbot.py
# ════════════════════════════════════════════════════════════════

def load_chatbot(app):
    """
    Charge les fichiers depuis model_files/ et stocke dans app.chatbot.

    Fichiers nécessaires en v5 :
      ✅ model.pt
      ✅ tokenizer.pkl
      ✅ dataset.csv
      ❌ tfidf_vectorizer.pkl  (supprimé — HybridRetriever le reconstruit)
    """
    model_dir = Config.MODEL_DIR

    torch.set_num_threads(Config.TORCH_THREADS)
    torch.set_grad_enabled(False)

    # ── Tokenizer ────────────────────────────────────────────────
    with open(os.path.join(model_dir, "tokenizer.pkl"), "rb") as f:
        tok_data = pickle.load(f)

    tokenizer            = MalagasyTokenizer()
    tokenizer.word2idx   = tok_data["word2idx"]
    tokenizer.idx2word   = tok_data["idx2word"]
    tokenizer.vocab_size = tok_data.get("vocab_size", 8000)

    # ── Dataset ──────────────────────────────────────────────────
    df = pd.read_csv(
        os.path.join(model_dir, "dataset.csv"),
        encoding="utf-8-sig",       # v5 : latin-1 pour caractères malgaches
        index_col=False,
        on_bad_lines="skip",
    )
    for col in ["texte", "medicament1", "medicament2", "astuce", "categorie"]:
        if col not in df.columns:
            df[col] = ""
    df[["texte", "medicament1", "medicament2", "astuce"]] = (
        df[["texte", "medicament1", "medicament2", "astuce"]].fillna("")
    )
    if "cat_base" not in df.columns:
        df["cat_base"] = (
            df["categorie"]
            .str.replace(r"\s*\(olona antitra\)", "", regex=True)
            .str.lower()
            .str.strip()
        )
    df["cat_base"] = df["cat_base"].fillna("Inconnu").str.lower().str.strip()

    # ── Retriever hybride BM25 + TF-IDF (nouveauté v5) ──────────
    # Reconstruit au démarrage (~1s), plus besoin de tfidf_vectorizer.pkl
    retriever = HybridRetriever(df, tokenizer, bm25_weight=0.6)

    # ── Modèle PyTorch ───────────────────────────────────────────
    ckpt = torch.load(
        os.path.join(model_dir, "model.pt"),
        map_location=torch.device("cpu"),
    )
    idx2category = ckpt["idx2category"]
    num_classes  = ckpt["num_classes"]
    cfg          = ckpt.get("config", {})

    # Paramètres v5 (plus petits que v4)
    d_model    = cfg.get("d_model",      128)   # v4 : 256
    num_heads  = cfg.get("num_heads",      4)   # v4 : 8
    num_layers = cfg.get("num_layers",     3)   # v4 : 4
    d_ff       = cfg.get("d_ff",         256)   # v4 : 512
    max_len    = cfg.get("max_input_len",  96)  # v4 : 128

    model = MiniMedicalLLM(
        vocab_size  = tokenizer.actual_vocab_size,
        num_classes = num_classes,
        d_model     = d_model,
        num_heads   = num_heads,
        num_layers  = num_layers,
        d_ff        = d_ff,
        max_seq_len = max_len,
        dropout     = 0.0,
    )
    missing, unexpected = model.load_state_dict(ckpt["model_state_dict"], strict=False)
    if missing:
        print(f"[v5] Clés absentes ignorées ({len(missing)}) : {missing[:3]} ...")
    if unexpected:
        print(f"[v5] Clés inattendues ignorées ({len(unexpected)}) : {unexpected[:3]} ...")

    model.eval()

    # ── Stockage dans app ─────────────────────────────────────────
    app.chatbot = {
        "model"        : model,
        "tokenizer"    : tokenizer,
        "retriever"    : retriever,
        "idx2category" : idx2category,
        "max_input_len": max_len,
    }

    print(
        f"[v5] Modèle chargé | classes={num_classes} "
        f"| vocab={tokenizer.actual_vocab_size} "
        f"| d_model={d_model} | params={model.count_parameters():,}"
    )


# ════════════════════════════════════════════════════════════════
#  Constantes
# ════════════════════════════════════════════════════════════════

CATEGORY_ICONS = {
    "aretin-doha"            : "🧠",
    "areti-maso"             : "👁️",
    "areti-nify"             : "🦷",
    "areti-koditra"          : "🩺",
    "aretin-kibo"            : "🫃",
    "aretim-po"              : "❤️",
    "aretin-aty"             : "🟡",
    "aretin-tsinay"          : "🦠",
    "aretin-tratra"          : "🫁",
    "aretin-tongotra"        : "🦶",
    "aretin-tanana"          : "✋",
    "aretin-tsakafo"         : "🤢",
    "diabeta"                : "💉",
    "fiakaran-ny-tosi-dra"   : "💊",
    "tazomoka"               : "🦟",
    "tazo"                   : "🌡️",
    "kohaka"                 : "😮",
    "aretin-pivalanana"      : "🚿",
    "fanaintainan-damosina"  : "🔩",
    "marenina"               : "👂",
    "aretin-kozatra"         : "🤧",
    "aretin-tsaina"          : "🧘",
    "fiakaran-ny-kolesterola": "🩸",
    "aretin-urinaire"        : "💧",
    "aretin-nosy"            : "💫",
    "aretin-tenda"           : "🗣️",
    "aretin-orona"           : "👃",
}

CATEGORY_LABELS_FR = {
    "aretin-doha"            : "Maux de tete",
    "areti-maso"             : "Yeux",
    "areti-nify"             : "Dents",
    "areti-koditra"          : "Peau",
    "aretin-kibo"            : "Ventre",
    "aretim-po"              : "Coeur",
    "aretin-aty"             : "Foie",
    "aretin-tsinay"          : "Intestins",
    "aretin-tratra"          : "Poumons",
    "aretin-tongotra"        : "Jambes / pieds",
    "aretin-tanana"          : "Mains / bras",
    "aretin-tsakafo"         : "Nausees",
    "diabeta"                : "Diabete",
    "fiakaran-ny-tosi-dra"   : "Hypertension",
    "tazomoka"               : "Paludisme",
    "tazo"                   : "Fievre",
    "kohaka"                 : "Toux",
    "aretin-pivalanana"      : "Diarrhee",
    "fanaintainan-damosina"  : "Douleurs dorsales",
    "marenina"               : "Oreilles",
    "aretin-kozatra"         : "Allergies",
    "aretin-tsaina"          : "Sante mentale",
    "fiakaran-ny-kolesterola": "Cholesterol",
    "aretin-urinaire"        : "Urinaire",
    "aretin-nosy"            : "Vertiges",
    "aretin-tenda"           : "Gorge",
    "aretin-orona"           : "Nez",
}

SALUTATIONS = {
    "salama"           : "Salama! Miarahaba. Inona no azoko anampiana anao?",
    "manao ahoana"     : "Manao ahoana! Azoko atao ny manampy anao ara-pahasalamana.",
    "manahoana"        : "Manahoana! Mikarakara ny fahasalamanao aho. Inona no tenanao?",
    "mbola tsara"      : "Mbola tsara! Inona no azoko anampiana anao androany?",
    "veloma"           : "Veloma! Mirary fahasalamana ho anao aho.",
    "misaotra"         : "Misaotra betsaka! Faly aho fa nanampy anao. Veloma!",
    "misaotra betsaka" : "Misaotra betsaka! Veloma ary tandremo ny fahasalamanao!",
    "help"             : (
        "Torohevitra fampiasana:\n"
        "- Soraty ny soritr-aretinao amin-ny Malagasy\n"
        "- Ohatra: Marary ny lohako na Misy tazo aho"
    ),
    "inona no azonao"  : "Azoko atao ny milaza fanafody sy torohevitra ara-pahasalamana.",
}

# Symptômes graves v5 — liste étendue et plus précise
SYMPTOMES_GRAVES = [
    "very hevitra", "tsy mitsahatra", "ra mivoaka",
    "fivalozana", "tsy afaka miaina", "mafy be loatra",
    "sempotra mafy", "mangorakoraka",
    "tazo 39", "tazo 40",        # ← plus précis qu'en v4 ("tazo" seul)
    "lavo tampoka", "kivy be",
    "mangirifirifa mafy", "tsimokamokan",
    "tsy mahatsapa", "very ny hevitra",
]

REGLES_METIER = {
    "loha"    : (
        "Torohevitra misy aretina eo amin'ny loha:\n"
        "• Misotroa Paracétamol 500mg (3x/andro)\n"
        "• Miala sasatra, misotroa rano betsaka (2L/andro)\n"
        "• Aza mijery efijery ela loatra\n"
        "• Raha tsy miova ao anatin'ny 48 ora: dokotera"
    ),
    "kibo"    : (
        "Torohevitra misy aretin-kibo:\n"
        "• Mihinana sakafo malefaka sy mora an-tsaina\n"
        "• Misotroa rano mafana misy sira kely\n"
        "• Raha misy ra na tsy miova: dokotera"
    ),
    "nify"    : (
        "Torohevitra misy aretin-nify:\n"
        "• Miborosy nify roa andro isan'andro\n"
        "• Misotroa Ibuprofène 400mg raha mafy\n"
        "• Mankanesa any amin'ny dokiteran-nify haingana"
    ),
    "tazo"    : (
        "Torohevitra misy tazo:\n"
        "• Misotroa Paracétamol 500mg isaky ny 6 ora\n"
        "• Misotroa rano betsaka (3L/andro)\n"
        "• Raha mihoatra ny 38.5°C mandritra ny 2 andro: dokotera"
    ),
    "maso"    : (
        "Torohevitra misy areti-maso:\n"
        "• Aza mikasika ny maso amin'ny tanan-doto\n"
        "• Sasao ny maso amin'ny rano madio\n"
        "• Raha misy fahitana menarana: dokotera haingana"
    ),
    "tratra"  : (
        "Torohevitra misy aretin-tratra:\n"
        "• Miala sasatra, misotroa rano mafana misy tantely\n"
        "• Raha misy fahasahiranana amin'ny aina: dokotera HAINGANA"
    ),
    "tongotra": (
        "Torohevitra misy aretin-tongotra:\n"
        "• Mitsahara ary asio ranomandry raha mivonto\n"
        "• Mampiasa gel anti-inflammatoire\n"
        "• Raha fotsy avokoa ny tongotra: dokotera haingana"
    ),
    "koditra" : (
        "Torohevitra misy areti-koditra:\n"
        "• Mampiasa crème hydratante raha maina\n"
        "• Misotroa Cétirizine raha misy hasirotro\n"
        "• Raha miitatra na mafy: dokotera"
    ),
}

OOD_CONF_THRESH = 0.15
OOD_SIM_THRESH  = 0.01
FALLBACK_THRESH = 0.40

OOD_RESPONSES = [
    "Miala tsiny fa tsy ao anatin'ny sehatry ny fitsaboana izany. Mba lazao ny soritr'aretinao.",
    "Tsy misy fandikana ara-pahasalamana amin'izany. Inona no soritr'aretina misy anao?",
    "Azoko fa ilaina ny fanampiana. Fa ny sehatry ny fitsaboana ihany no fantatro.",
]


# ════════════════════════════════════════════════════════════════
#  Fonctions utilitaires
# ════════════════════════════════════════════════════════════════

def detect_salutation(texte: str):
    t = texte.lower().strip()
    for key, response in SALUTATIONS.items():
        if t == key or t.startswith(key) or key in t:
            return response
    return None


def check_symptome_grave(texte: str):
    t        = texte.lower()
    detected = [s for s in SYMPTOMES_GRAVES if s in t]
    if detected:
        return (
            "SORITR-ARETINA MAFY VOAMARIKA!\n"
            f"Hitako : {', '.join(detected[:3])}\n"
            "=> MANDEHANA ANY AMIN-NY DOKOTERA NA HOPITALY HAINGANA!"
        )
    return None


def get_fallback_rule(texte: str, tokenizer):
    t = tokenizer.clean_text(texte)
    for keyword, conseil in REGLES_METIER.items():
        if keyword in t:
            return conseil
    return None


def get_confidence_indicator(confidence: float) -> str:
    if confidence >= 65: return "green"    # v4 : 70
    if confidence >= 40: return "yellow"
    return "red"


def _clean_val(v) -> str:
    """Nettoie les valeurs NaN du dataset."""
    return "" if (v is None or str(v).strip().lower() == "nan") else str(v).strip()


# ════════════════════════════════════════════════════════════════
#  predict_symptome — fonction principale appelée par les routes
# ════════════════════════════════════════════════════════════════

@torch.no_grad()
def predict_symptome(texte: str) -> dict:
    """
    Retourne la réponse médicale complète (v5).

    Changements vs v4 :
    - Retriever hybride BM25+TF-IDF via HybridRetriever
    - expand_query sur le texte avant retrieval
    - Suppression de model.generate() (plus de TextGeneratorHead)
    - Seuils OOD affinés (0.20 / 0.08)
    - Symptômes graves liste étendue et plus précise
    - Nettoyage NaN automatique
    """
    chatbot       = current_app.chatbot
    model         = chatbot["model"]
    tokenizer     = chatbot["tokenizer"]
    retriever     = chatbot["retriever"]
    idx2category  = chatbot["idx2category"]
    max_input_len = chatbot["max_input_len"]

    # 1. Alerte symptômes graves
    alerte = check_symptome_grave(texte)

    # 2. Encodage
    ids = torch.tensor(
        [tokenizer.encode(texte, max_len=max_input_len)]
    )

    # 3. Classification
    out        = model(ids)
    probs      = F.softmax(out["class_logits"], dim=-1)[0]
    top_idx    = int(probs.argmax())
    category   = idx2category.get(top_idx, "Inconnu")
    confidence = float(probs[top_idx])

    # 4. Indicateur confiance
    indicator = get_confidence_indicator(confidence * 100)

    # 5. Top-3
    top3 = [
        {
            "categorie": idx2category.get(i, "?"),
            "icon"     : CATEGORY_ICONS.get(idx2category.get(i, ""), ""),
            "score"    : round(p * 100, 1),
        }
        for i, p in sorted(enumerate(probs.tolist()), key=lambda x: -x[1])[:3]
    ]

    # 6. Retrieval hybride BM25+TF-IDF
    # Si confiance faible → on ignore la catégorie pour élargir la recherche
    retrieval_cat       = category if confidence >= FALLBACK_THRESH else None
    best_row, sim_score = retriever.retrieve(texte, category=retrieval_cat)

    # 7. Détection hors-domaine
    if confidence < OOD_CONF_THRESH and sim_score < OOD_SIM_THRESH:
        return {
            "texte"      : texte,
            "categorie"  : "hors_domaine",
            "label_fr"   : "Hors domaine",
            "icon"       : "❓",
            "confidence" : round(confidence * 100, 1),
            "indicator"  : "red",
            "tfidf_sim"  : round(sim_score, 3),
            "medicament1": "",
            "medicament2": "",
            "astuce"     : "",
            "generated"  : "",
            "top3"       : top3,
            "alerte"     : alerte,
            "fallback"   : random.choice(OOD_RESPONSES),
            "ood"        : True,
        }

    # 8. Fallback règles métier si confiance faible
    fallback = None
    if confidence * 100 < FALLBACK_THRESH * 100:
        fallback = get_fallback_rule(texte, tokenizer)

    return {
        "texte"      : texte,
        "categorie"  : category,
        "label_fr"   : CATEGORY_LABELS_FR.get(category, category),
        "icon"       : CATEGORY_ICONS.get(category, "🏥"),
        "confidence" : round(confidence * 100, 1),
        "indicator"  : indicator,
        "tfidf_sim"  : round(sim_score, 3),
        "medicament1": _clean_val(best_row["medicament1"]),
        "medicament2": _clean_val(best_row["medicament2"]),
        "astuce"     : _clean_val(best_row["astuce"]),
        "generated"  : "",           # supprimé en v5
        "top3"       : top3,
        "alerte"     : alerte,
        "fallback"   : fallback,
        "ood"        : False,
    }


def get_all_categories() -> list:
    chatbot      = current_app.chatbot
    idx2category = chatbot["idx2category"]
    return [
        {
            "id"      : k,
            "label_fr": CATEGORY_LABELS_FR.get(k, k),
            "icon"    : CATEGORY_ICONS.get(k, ""),
        }
        for k in sorted(set(idx2category.values()))
    ]