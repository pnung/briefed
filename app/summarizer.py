import nltk
from nltk.tokenize import sent_tokenize
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Optional
from .logger import logger

class TextRankSummarizer:
    def __init__(self, compression_ratio: float = 0.3):
        self.compression_ratio = compression_ratio
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)

    def summarize(self, text: str) -> Optional[str]:
        if not text or not isinstance(text, str):
            return None
            
        try:
            sentences = sent_tokenize(text)
            if len(sentences) < 2:
                return text
                
            vectorizer = TfidfVectorizer(stop_words='english')
            sentence_vectors = vectorizer.fit_transform(sentences)
            similarity_matrix = cosine_similarity(sentence_vectors)
            
            nx_graph = nx.from_numpy_array(similarity_matrix)
            scores = nx.pagerank(nx_graph)
            
            ranked_sentences = sorted(
                ((scores[i], s) for i, s in enumerate(sentences)),
                reverse=True
            )
            
            num_sentences = max(1, int(len(sentences) * self.compression_ratio))
            return ' '.join([ranked_sentences[i][1] for i in range(num_sentences)])
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return None