"""
Topic Clustering Service using Embeddings
"""

import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
import logging
from collections import Counter

from app.core.config import settings

logger = logging.getLogger(__name__)


class ClusteringService:
    """Service for clustering feedback based on embeddings"""
    
    def __init__(self):
        self.min_cluster_size = settings.MIN_CLUSTER_SIZE
        self.max_clusters = settings.MAX_CLUSTERS
    
    def cluster_feedback(
        self,
        embeddings: List[List[float]],
        texts: List[str],
        n_clusters: int = None
    ) -> Dict:
        """
        Cluster feedback items based on their embeddings
        
        Args:
            embeddings: List of embedding vectors
            texts: List of feedback texts (for keywords extraction)
            n_clusters: Number of clusters (auto-determined if None)
        
        Returns:
            Dictionary with cluster assignments and metadata
        """
        if len(embeddings) < self.min_cluster_size:
            logger.warning(f"Not enough feedback for clustering ({len(embeddings)} < {self.min_cluster_size})")
            return {
                "clusters": [],
                "labels": [],
                "message": "Not enough feedback items for clustering"
            }
        
        embeddings_array = np.array(embeddings)
        
        # Auto-determine number of clusters using elbow method
        if n_clusters is None:
            n_clusters = self._find_optimal_clusters(embeddings_array)
        
        # Ensure n_clusters is within bounds
        n_clusters = min(n_clusters, len(embeddings), self.max_clusters)
        n_clusters = max(2, n_clusters)  # At least 2 clusters
        
        # Perform K-means clustering
        kmeans = KMeans(
            n_clusters=n_clusters,
            random_state=42,
            n_init=10
        )
        labels = kmeans.fit_predict(embeddings_array)
        
        # Create cluster metadata
        clusters = []
        for cluster_id in range(n_clusters):
            cluster_indices = np.where(labels == cluster_id)[0]
            cluster_texts = [texts[i] for i in cluster_indices]
            
            # Extract common keywords
            keywords = self._extract_cluster_keywords(cluster_texts)
            
            # Get representative samples (closest to centroid)
            cluster_embeddings = embeddings_array[cluster_indices]
            centroid = kmeans.cluster_centers_[cluster_id]
            distances = np.linalg.norm(cluster_embeddings - centroid, axis=1)
            closest_indices = np.argsort(distances)[:3]  # Top 3 closest
            
            representative_texts = [cluster_texts[i] for i in closest_indices]
            
            clusters.append({
                "id": int(cluster_id),
                "size": int(len(cluster_indices)),
                "keywords": keywords,
                "representative_texts": representative_texts
            })
        
        return {
            "n_clusters": int(n_clusters),
            "labels": [int(label) for label in labels],  # Convert all to Python int
            "clusters": clusters
        }
    
    def _find_optimal_clusters(self, embeddings: np.ndarray, max_k: int = None) -> int:
        """
        Use elbow method to find optimal number of clusters
        """
        if max_k is None:
            max_k = min(len(embeddings) // self.min_cluster_size, self.max_clusters)
        
        max_k = max(2, min(max_k, len(embeddings) - 1))
        
        inertias = []
        K_range = range(2, max_k + 1)
        
        for k in K_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(embeddings)
            inertias.append(kmeans.inertia_)
        
        # Find elbow using rate of change
        if len(inertias) < 2:
            return 2
        
        rates = np.diff(inertias)
        elbow_index = np.argmax(rates) + 2  # +2 because we start from 2
        
        return min(elbow_index, max_k)
    
    def _extract_cluster_keywords(self, texts: List[str], top_n: int = 5) -> List[str]:
        """
        Extract common keywords from cluster texts
        """
        import re
        
        # Common stop words
        stop_words = set([
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'you', 'your', 'yours',
            'he', 'him', 'his', 'she', 'her', 'hers', 'it', 'its', 'they', 'them',
            'what', 'which', 'who', 'when', 'where', 'why', 'how', 'a', 'an', 'the',
            'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at',
            'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through',
            'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down',
            'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then',
            'once', 'is', 'am', 'are', 'was', 'were', 'be', 'been', 'being', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could',
            'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
        ])
        
        all_words = []
        for text in texts:
            words = re.findall(r'\b[a-z]{3,}\b', text.lower())
            all_words.extend([w for w in words if w not in stop_words])
        
        # Count and get top keywords
        counter = Counter(all_words)
        keywords = [word for word, count in counter.most_common(top_n)]
        
        return keywords
    
    def find_similar_feedback(
        self,
        query_embedding: List[float],
        all_embeddings: List[List[float]],
        top_k: int = 5
    ) -> List[Tuple[int, float]]:
        """
        Find similar feedback items based on embedding similarity
        
        Returns:
            List of (index, similarity_score) tuples
        """
        query_vec = np.array(query_embedding).reshape(1, -1)
        embeddings_matrix = np.array(all_embeddings)
        
        similarities = cosine_similarity(query_vec, embeddings_matrix)[0]
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = [(int(idx), float(similarities[idx])) for idx in top_indices]
        return results


# Singleton instance
_clustering_service = None


def get_clustering_service() -> ClusteringService:
    """Get or create clustering service instance"""
    global _clustering_service
    if _clustering_service is None:
        _clustering_service = ClusteringService()
    return _clustering_service
