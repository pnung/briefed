import nltk
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx

nltk.download('punkt')

class TextRankSummarizer:
    def __init__(self, compression_ratio=0.2):
        self.compression_ratio = compression_ratio
        
    def summarize(self, text):
        sentences = sent_tokenize(text)
        vectorizer = TfidfVectorizer()
        sentence_vectors = vectorizer.fit_transform(sentences)
        similarity_matrix = cosine_similarity(sentence_vectors)
        
        nx_graph = nx.from_numpy_array(similarity_matrix)
        scores = nx.pagerank(nx_graph)
        
        ranked_sentences = sorted(
            ((scores[i], s) for i, s in enumerate(sentences)),
            reverse=True
        )
        top_n = max(1, int(len(sentences) * self.compression_ratio))
        return ' '.join(s[1] for s in ranked_sentences[:top_n])