import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class TFIDFRetriever:
    def __init__(self, df: pd.DataFrame, tokenizer, vectorizer=None):
        self.df        = df.reset_index(drop=True)
        self.tokenizer = tokenizer
        corpus         = [tokenizer.clean_text(str(t)) for t in df["texte"].tolist()]

        if vectorizer is not None:
            self.vectorizer   = vectorizer
            self.tfidf_matrix = vectorizer.transform(corpus)
        else:
            self.vectorizer   = TfidfVectorizer(
                analyzer="word", min_df=1,
                sublinear_tf=True, ngram_range=(1, 2)
            )
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def retrieve(self, query: str, category: str = None):
        q_clean  = self.tokenizer.clean_text(query)
        q_vec    = self.vectorizer.transform([q_clean])
        sims     = cosine_similarity(q_vec, self.tfidf_matrix).flatten()

        if category:
            cat_mask = (self.df["cat_base"] == category).values
            if cat_mask.sum() > 0:
                sims_cat             = sims.copy()
                sims_cat[~cat_mask] *= 0.4
                best_idx = int(np.argmax(sims_cat))
            else:
                best_idx = int(np.argmax(sims))
        else:
            best_idx = int(np.argmax(sims))

        return self.df.iloc[best_idx], float(sims[best_idx])
