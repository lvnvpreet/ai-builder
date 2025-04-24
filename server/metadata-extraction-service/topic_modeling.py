# server/metadata-extraction-service/topic_modeling.py
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
from gensim import corpora
from gensim.models import LdaMulticore, CoherenceModel
import numpy as np
from typing import List, Dict, Any, Tuple
import logging

# Download required NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

logger = logging.getLogger(__name__)

class TopicModeler:
    """Topic modeling using LDA, NMF, and other techniques."""
    
    def __init__(self, n_topics: int = 5, method: str = "lda"):
        self.n_topics = n_topics
        self.method = method
        self.model = None
        self.vectorizer = None
        self.stop_words = set(stopwords.words('english'))
        
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for topic modeling."""
        # Tokenize
        tokens = word_tokenize(text.lower())
        
        # Remove stopwords and short tokens
        tokens = [token for token in tokens if token not in self.stop_words and len(token) > 3]
        
        return ' '.join(tokens)
    
    def fit_transform(self, texts: List[str]) -> Tuple[Any, Any]:
        """Fit topic model and transform texts."""
        # Preprocess texts
        processed_texts = [self.preprocess_text(text) for text in texts]
        
        if self.method == "lda":
            return self._fit_transform_lda(processed_texts)
        elif self.method == "nmf":
            return self._fit_transform_nmf(processed_texts)
        elif self.method == "gensim":
            return self._fit_transform_gensim(processed_texts)
        else:
            raise ValueError(f"Unknown method: {self.method}")
    
    def _fit_transform_lda(self, texts: List[str]) -> Tuple[Any, Any]:
        """LDA using scikit-learn."""
        self.vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=1000)
        doc_term_matrix = self.vectorizer.fit_transform(texts)
        
        self.model = LatentDirichletAllocation(
            n_components=self.n_topics,
            random_state=42,
            learning_method='batch'
        )
        
        topic_distributions = self.model.fit_transform(doc_term_matrix)
        return self.model, topic_distributions
    
    def _fit_transform_nmf(self, texts: List[str]) -> Tuple[Any, Any]:
        """Non-negative Matrix Factorization."""
        self.vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, max_features=1000)
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        
        self.model = NMF(
            n_components=self.n_topics,
            random_state=42,
            init='nndsvd'
        )
        
        topic_distributions = self.model.fit_transform(tfidf_matrix)
        return self.model, topic_distributions
    
    def _fit_transform_gensim(self, texts: List[str]) -> Tuple[Any, Any]:
        """LDA using Gensim for better topic quality."""
        # Tokenize and create dictionary
        tokenized_texts = [text.split() for text in texts]
        dictionary = corpora.Dictionary(tokenized_texts)
        
        # Filter extremes
        dictionary.filter_extremes(no_below=2, no_above=0.9)
        
        # Create corpus
        corpus = [dictionary.doc2bow(text) for text in tokenized_texts]
        
        # Train LDA model
        self.model = LdaMulticore(
            corpus=corpus,
            id2word=dictionary,
            num_topics=self.n_topics,
            random_state=42,
            passes=10,
            workers=4
        )
        
        # Get topic distributions
        topic_distributions = []
        for bow in corpus:
            topic_dist = self.model.get_document_topics(bow, minimum_probability=0.0)
            topic_distributions.append([prob for _, prob in topic_dist])
        
        return self.model, np.array(topic_distributions)
    
    def get_topics(self, n_words: int = 10) -> List[Dict[str, Any]]:
        """Get topics with top words."""
        if self.model is None:
            raise ValueError("Model not fitted yet")
        
        topics = []
        
        if self.method == "gensim":
            for idx in range(self.n_topics):
                topic_words = self.model.show_topic(idx, topn=n_words)
                topics.append({
                    "id": idx,
                    "words": [word for word, _ in topic_words],
                    "weights": [float(weight) for _, weight in topic_words]
                })
        else:
            feature_names = self.vectorizer.get_feature_names_out()
            for idx, topic in enumerate(self.model.components_):
                top_indices = topic.argsort()[:-n_words-1:-1]
                top_words = [feature_names[i] for i in top_indices]
                top_weights = [float(topic[i]) for i in top_indices]
                
                topics.append({
                    "id": idx,
                    "words": top_words,
                    "weights": top_weights
                })
        
        return topics
    
    def get_document_topics(self, text: str) -> List[Dict[str, Any]]:
        """Get topic distribution for a new document."""
        if self.model is None:
            raise ValueError("Model not fitted yet")
        
        processed_text = self.preprocess_text(text)
        
        if self.method == "gensim":
            # For Gensim LDA
            bow = self.model.id2word.doc2bow(processed_text.split())
            topic_distribution = self.model.get_document_topics(bow, minimum_probability=0.0)
            
            topics = []
            for topic_id, prob in topic_distribution:
                topics.append({
                    "topic_id": topic_id,
                    "probability": float(prob),
                    "top_words": [word for word, _ in self.model.show_topic(topic_id, topn=5)]
                })
        else:
            # For scikit-learn LDA/NMF
            if self.method == "lda":
                vec = self.vectorizer.transform([processed_text])
                topic_distribution = self.model.transform(vec)[0]
            else:  # NMF
                vec = self.vectorizer.transform([processed_text])
                topic_distribution = self.model.transform(vec)[0]
            
            topics = []
            feature_names = self.vectorizer.get_feature_names_out()
            
            for topic_id, prob in enumerate(topic_distribution):
                if prob > 0.01:  # Only include topics with >1% probability
                    top_indices = self.model.components_[topic_id].argsort()[:-6:-1]
                    top_words = [feature_names[i] for i in top_indices]
                    
                    topics.append({
                        "topic_id": topic_id,
                        "probability": float(prob),
                        "top_words": top_words
                    })
        
        return sorted(topics, key=lambda x: x["probability"], reverse=True)
    
    def evaluate_coherence(self, texts: List[str]) -> Dict[str, float]:
        """Evaluate topic coherence (only for Gensim models)."""
        if self.method != "gensim":
            return {"coherence": None, "message": "Coherence only available for Gensim models"}
        
        tokenized_texts = [self.preprocess_text(text).split() for text in texts]
        
        coherence_model = CoherenceModel(
            model=self.model,
            texts=tokenized_texts,
            dictionary=self.model.id2word,
            coherence='c_v'
        )
        
        coherence_score = coherence_model.get_coherence()
        
        return {
            "coherence": coherence_score,
            "interpretation": "Higher is better (typical range: 0.3-0.7)"
        }