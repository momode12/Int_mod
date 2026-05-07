import torch
import torch.nn.functional as F
from flask import current_app

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


def detect_salutation(texte: str):
    """Retourne une reponse si c'est une salutation, sinon None."""
    t = texte.lower().strip()
    for key, response in SALUTATIONS.items():
        if t == key or t.startswith(key) or key in t:
            return response
    return None

SYMPTOMES_GRAVES = [
    "very hevitra", "tsy mitsahatra", "ra mivoaka",
    "fivalozana", "tsy afaka miaina", "mafy be",
    "sempotra mafy", "mangorakoraka", "tazo",
    "lavo", "kivy be", "mangirifirifa be",
]


def check_symptome_grave(texte: str):
    """Retourne un message d'alerte si des symptomes graves sont detectes."""
    t        = texte.lower()
    detected = [s for s in SYMPTOMES_GRAVES if s in t]
    if detected:
        return (
            "SORITR-ARETINA MAFY VOAMARIKA!\n"
            f"Hitako : {', '.join(detected[:3])}\n"
            "=> MANDEHANA ANY AMIN-NY DOKOTERA HAINGANA!"
        )
    return None

REGLES_METIER = {
    "loha"     : "Torohevitra : Mitsahara, misotroa rano betsaka, matory 7-8 ora. Raha mitohy : dokotera.",
    "kibo"     : "Torohevitra : Mihinana sakafo malefaka, misotroa rano madio. Raha mitohy : dokotera.",
    "nify"     : "Torohevitra : Miborosy nify, misotroa fanafody fanaintainana. Mandehana dokotera nify.",
    "tazo"     : "Torohevitra : Misotroa Paracetamol, rano betsaka, mitory. Raha 39C+ : dokotera haingana.",
    "maso"     : "Torohevitra : Aza mikasika ny maso, sasana tanana. Raha mitohy : dokotera maso.",
    "tratra"   : "Torohevitra : Miala sasatra, rano mafana misy tantely. Raha sempotra mafy : dokotera.",
    "tongotra" : "Torohevitra : Mitsahara, asio ranomandry raha mivonto. Raha mafy : dokotera.",
    "koditra"  : "Torohevitra : Mampiasa creme, misotroa antihistaminique. Raha mitohy : dokotera.",
}


def get_fallback_rule(texte: str, tokenizer):
    """Retourne une regle metier generique si un mot-cle est trouve."""
    t = tokenizer.clean_text(texte)
    for keyword, conseil in REGLES_METIER.items():
        if keyword in t:
            return conseil
    return None


def get_confidence_indicator(confidence: float) -> str:
    """Retourne un indicateur visuel selon le niveau de confiance."""
    if confidence >= 70: return "green"
    if confidence >= 40: return "yellow"
    return "red"

@torch.no_grad()
def predict_symptome(texte: str) -> dict:
    """
    Retourne la reponse medicale complete.
    Utilise current_app.chatbot charge dans create_app().
    """
    chatbot       = current_app.chatbot
    model         = chatbot["model"]
    tokenizer     = chatbot["tokenizer"]
    retriever     = chatbot["retriever"]
    idx2category  = chatbot["idx2category"]
    max_input_len = chatbot["max_input_len"]

    # 1. Alerte symptomes graves
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

    # 6. TF-IDF retrieval
    best_row, sim_score = retriever.retrieve(texte, category=category)

    # 7. Generation texte
    pooled, _ = model.encoder(ids)
    generated = model.generate(pooled, tokenizer)

    # 8. Fallback regles metier si confiance faible
    fallback = None
    if confidence * 100 < 40:
        fallback = get_fallback_rule(texte, tokenizer)

    return {
        "texte"      : texte,
        "categorie"  : category,
        "label_fr"   : CATEGORY_LABELS_FR.get(category, category),
        "icon"       : CATEGORY_ICONS.get(category, ""),
        "confidence" : round(confidence * 100, 1),
        "indicator"  : indicator,
        "tfidf_sim"  : round(sim_score, 3),
        "medicament1": str(best_row["medicament1"]),
        "medicament2": str(best_row["medicament2"]),
        "astuce"     : str(best_row["astuce"]),
        "generated"  : generated,
        "top3"       : top3,
        "alerte"     : alerte,
        "fallback"   : fallback,
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
