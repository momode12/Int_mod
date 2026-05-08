import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# rank_bm25 : ajouter dans requirements.txt → pip install rank_bm25
from rank_bm25 import BM25Okapi


class HybridRetriever:
    """
    Retriever hybride BM25 + TF-IDF (nouveauté v5).

    v4 : TF-IDF seul → mauvais recall sur mots-clés exacts
    v5 : BM25 (60%) + TF-IDF (40%) + expansion synonymes
         → meilleure précision sur symptômes spécifiques

    Paramètres
    ----------
    bm25_weight : float
        Part de BM25 dans le score hybride (défaut 0.6).
        TF-IDF prend le complément (1 - bm25_weight).
    """

    def __init__(self, df: pd.DataFrame, tokenizer, bm25_weight: float = 0.6):
        self.df           = df.reset_index(drop=True)
        self.tokenizer    = tokenizer
        self.bm25_weight  = bm25_weight
        self.tfidf_weight = 1.0 - bm25_weight

        # ── Corpus étendu avec synonymes ─────────────────────────
        corpus_expanded = [
            tokenizer.expand_query(str(t)) for t in df["texte"].tolist()
        ]

        # ── BM25 sur tokens ──────────────────────────────────────
        tokenized_corpus = [doc.split() for doc in corpus_expanded]
        self.bm25        = BM25Okapi(tokenized_corpus)

        # ── TF-IDF sur corpus étendu ─────────────────────────────
        self.vectorizer = TfidfVectorizer(
            analyzer    = "word",
            min_df      = 1,
            sublinear_tf= True,
            ngram_range = (1, 2),
            max_features= 5000,
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus_expanded)

    def _hybrid_scores(self, query: str) -> np.ndarray:
        """Calcule le score hybride BM25+TF-IDF pour une query."""
        query_expanded = self.tokenizer.expand_query(query)
        query_clean    = self.tokenizer.clean_text(query_expanded)

        # Score BM25 normalisé
        bm25_raw  = np.array(self.bm25.get_scores(query_clean.split()))
        bm25_max  = bm25_raw.max()
        bm25_norm = bm25_raw / bm25_max if bm25_max > 0 else bm25_raw

        # Score TF-IDF cosine
        q_vec       = self.vectorizer.transform([query_clean])
        tfidf_scores = cosine_similarity(q_vec, self.tfidf_matrix).flatten()

        return self.bm25_weight * bm25_norm + self.tfidf_weight * tfidf_scores

    def retrieve(self, query: str, category: str = None):
        """
        Retourne (best_row, sim_score).
        Si category fournie : booste les docs de cette catégorie (×1)
        et pénalise les autres (×0.35).
        """
        scores = self._hybrid_scores(query)

        if category:
            cat_mask = (self.df["cat_base"] == category).values
            if cat_mask.sum() > 0:
                scores_cat           = scores.copy()
                scores_cat[~cat_mask] *= 0.35
                best_idx = int(np.argmax(scores_cat))
            else:
                best_idx = int(np.argmax(scores))
        else:
            best_idx = int(np.argmax(scores))

        return self.df.iloc[best_idx], float(scores[best_idx])

    def retrieve_top_k(self, query: str, k: int = 3):
        """
        Retourne les k meilleures lignes (liste de tuples (row, score)).
        Utile pour afficher plusieurs suggestions dans React.
        """
        scores      = self._hybrid_scores(query)
        top_indices = np.argsort(scores)[::-1][:k]
        return [
            (self.df.iloc[idx], float(scores[idx]))
            for idx in top_indices
        ]


# ── Rétro-compatibilité : alias v4 → v5 ─────────────────────────
# Si d'autres fichiers importent encore TFIDFRetriever, ça ne casse pas.
class TFIDFRetriever(HybridRetriever):
    """Alias de rétro-compatibilité v4. Utiliser HybridRetriever en v5."""
    def __init__(self, df, tokenizer, vectorizer=None, **kwargs):
        # On ignore le vectorizer v4 pré-entraîné : v5 le reconstruit
        super().__init__(df, tokenizer, **kwargs)