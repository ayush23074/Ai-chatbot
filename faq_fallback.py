# faq_fallback.py
# Simple TF-IDF based FAQ retriever to answer common questions


import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


nltk.download('punkt', quiet=True)


class FAQFallback:
    def __init__(self, faqs: dict):
        # faqs: {"question": "answer"}
        self.questions = list(faqs.keys())
        self.answers = [faqs[q] for q in self.questions]
        self.vectorizer = TfidfVectorizer().fit(self.questions)
        self.q_vecs = self.vectorizer.transform(self.questions)


    def query(self, text: str, threshold: float = 0.45) -> str:
        v = self.vectorizer.transform([text])
        sims = cosine_similarity(v, self.q_vecs)[0]
        idx = sims.argmax()
        if sims[idx] >= threshold:
            return self.answers[idx]
        return ""