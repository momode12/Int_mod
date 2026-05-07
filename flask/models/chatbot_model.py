import os
import pickle

import pandas as pd
import torch

from ai.architecture import MiniMedicalLLM
from ai.tokenizer    import MalagasyTokenizer
from ai.retriever    import TFIDFRetriever
from config          import Config


def load_chatbot(app):
    """
    Charge les 4 fichiers depuis model_files/ et stocke dans app.chatbot.
    Meme principe que app.db pour MongoDB.
    """
    model_dir = Config.MODEL_DIR

    torch.set_num_threads(Config.TORCH_THREADS)
    torch.set_grad_enabled(False)

    # Tokenizer
    with open(os.path.join(model_dir, "tokenizer.pkl"), "rb") as f:
        tok_data = pickle.load(f)

    tokenizer            = MalagasyTokenizer()
    tokenizer.word2idx   = tok_data["word2idx"]
    tokenizer.idx2word   = tok_data["idx2word"]
    tokenizer.vocab_size = tok_data.get("vocab_size", 15000)

    # Dataset
    df = pd.read_csv(
        os.path.join(model_dir, "dataset.csv"),
        encoding="utf-8", index_col=False
    )
    for col in ["texte", "medicament1", "medicament2", "astuce"]:
        if col not in df.columns:
            df[col] = ""
    df[["texte", "medicament1", "medicament2", "astuce"]] = (
        df[["texte", "medicament1", "medicament2", "astuce"]].fillna("")
    )
    if "cat_base" not in df.columns:
        df["cat_base"] = (
            df["categorie"]
            .str.replace(r"\s*\(olona antitra\)", "", regex=True)
            .str.strip()
        )
    df["cat_base"] = df["cat_base"].fillna("Inconnu")

    # TF-IDF
    with open(os.path.join(model_dir, "tfidf_vectorizer.pkl"), "rb") as f:
        vectorizer = pickle.load(f)

    retriever = TFIDFRetriever(df, tokenizer, vectorizer)

    # Modele PyTorch
    ckpt = torch.load(
        os.path.join(model_dir, "model.pt"),
        map_location=torch.device("cpu")
    )
    idx2category = ckpt["idx2category"]
    num_classes  = ckpt["num_classes"]
    cfg          = ckpt.get("config", {})
    max_len      = max(cfg.get("max_input_len", 128), cfg.get("max_target_len", 128))

    model = MiniMedicalLLM(
        vocab_size  = tokenizer.actual_vocab_size,
        num_classes = num_classes,
        d_model     = cfg.get("d_model",   256),
        num_heads   = cfg.get("num_heads",   8),
        num_layers  = cfg.get("num_layers",  4),
        d_ff        = cfg.get("d_ff",       512),
        max_seq_len = max_len,
        dropout     = 0.0,
    )
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()

    # Stockage dans app (meme principe que app.db)
    app.chatbot = {
        "model"        : model,
        "tokenizer"    : tokenizer,
        "retriever"    : retriever,
        "idx2category" : idx2category,
        "max_input_len": cfg.get("max_input_len", 128),
    }

    print(f"Modele IA charge | classes={num_classes} | vocab={tokenizer.actual_vocab_size}")
