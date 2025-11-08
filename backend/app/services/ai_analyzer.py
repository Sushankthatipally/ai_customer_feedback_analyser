"""
AI/ML Service for Sentiment Analysis, Emotion Detection, and Text Analysis
"""

import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    pipeline
)
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import Dict, List, Tuple
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """Main AI/ML analyzer for feedback"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        # Initialize models
        self._init_sentiment_model()
        self._init_emotion_model()
        self._init_embedding_model()
        
    def _init_sentiment_model(self):
        """Initialize sentiment analysis model"""
        try:
            self.sentiment_tokenizer = AutoTokenizer.from_pretrained(settings.SENTIMENT_MODEL)
            self.sentiment_model = AutoModelForSequenceClassification.from_pretrained(
                settings.SENTIMENT_MODEL
            ).to(self.device)
            logger.info("Sentiment model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading sentiment model: {e}")
            # Fallback to simpler model
            self.sentiment_pipeline = pipeline("sentiment-analysis", device=0 if self.device == "cuda" else -1)
    
    def _init_emotion_model(self):
        """Initialize emotion detection model"""
        try:
            self.emotion_pipeline = pipeline(
                "text-classification",
                model=settings.EMOTION_MODEL,
                top_k=None,
                device=0 if self.device == "cuda" else -1
            )
            logger.info("Emotion model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading emotion model: {e}")
            self.emotion_pipeline = None
    
    def _init_embedding_model(self):
        """Initialize embedding model for similarity search"""
        try:
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            self.embedding_model = None
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text
        Returns: {"label": "positive/negative/neutral", "score": 0-1}
        """
        try:
            inputs = self.sentiment_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.sentiment_model(**inputs)
            
            scores = torch.nn.functional.softmax(outputs.logits, dim=-1)
            scores = scores.cpu().numpy()[0]
            
            # Map to sentiment labels
            labels = ["negative", "neutral", "positive"]
            sentiment_idx = np.argmax(scores)
            
            return {
                "label": labels[sentiment_idx],
                "score": float(scores[sentiment_idx]),
                "negative": float(scores[0]),
                "neutral": float(scores[1]),
                "positive": float(scores[2]),
                "compound_score": float(scores[2] - scores[0])  # -1 to 1
            }
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {"label": "neutral", "score": 0.5, "compound_score": 0.0}
    
    def detect_emotion(self, text: str) -> Dict[str, float]:
        """
        Detect emotions in text
        Returns: Dictionary of emotion scores
        """
        if not self.emotion_pipeline:
            return {}
        
        try:
            results = self.emotion_pipeline(text[:512])[0]  # Truncate long text
            emotion_scores = {item['label']: item['score'] for item in results}
            
            # Get dominant emotion
            dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])
            
            return {
                "dominant": dominant_emotion[0],
                "scores": emotion_scores
            }
        except Exception as e:
            logger.error(f"Emotion detection error: {e}")
            return {"dominant": "neutral", "scores": {}}
    
    def calculate_urgency(self, text: str, sentiment: Dict) -> Tuple[int, str]:
        """
        Calculate urgency score (1-10) based on keywords and sentiment
        Returns: (score, level)
        """
        text_lower = text.lower()
        
        # Urgency keywords with weights
        critical_keywords = ["urgent", "critical", "emergency", "immediately", "asap", "broken", "down", "not working"]
        high_keywords = ["important", "soon", "problem", "issue", "bug", "error", "frustrated"]
        medium_keywords = ["please", "need", "help", "confused", "unclear"]
        
        score = 5  # Base score
        
        # Check keywords
        if any(keyword in text_lower for keyword in critical_keywords):
            score += 3
        elif any(keyword in text_lower for keyword in high_keywords):
            score += 2
        elif any(keyword in text_lower for keyword in medium_keywords):
            score += 1
        
        # Adjust based on sentiment
        if sentiment.get("label") == "negative":
            score += 1
        
        # Check for exclamation marks (indicates urgency)
        exclamation_count = text.count("!")
        score += min(exclamation_count, 2)
        
        # Clamp score between 1-10
        score = max(1, min(10, score))
        
        # Determine level
        if score >= settings.URGENCY_HIGH_THRESHOLD:
            level = "high" if score < 9 else "critical"
        elif score >= settings.URGENCY_MEDIUM_THRESHOLD:
            level = "medium"
        else:
            level = "low"
        
        return score, level
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate vector embedding for text"""
        if not self.embedding_model:
            return []
        
        try:
            embedding = self.embedding_model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            return []
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Extract important keywords from text"""
        # Simple keyword extraction (can be enhanced with RAKE, YAKE, etc.)
        import re
        from collections import Counter
        
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
        
        # Extract words
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        words = [w for w in words if w not in stop_words]
        
        # Count and get top keywords
        counter = Counter(words)
        keywords = [word for word, count in counter.most_common(top_n)]
        
        return keywords
    
    def detect_feature_request(self, text: str) -> bool:
        """Detect if feedback is a feature request"""
        feature_indicators = [
            "would be great", "please add", "wish you had", "feature request",
            "could you add", "suggestion", "enhance", "improve", "add support",
            "would love to see", "missing", "lack of", "needs", "want"
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in feature_indicators)
    
    def detect_bug_report(self, text: str) -> bool:
        """Detect if feedback is a bug report"""
        bug_indicators = [
            "bug", "error", "broken", "not working", "doesn't work", "crash",
            "issue", "problem", "glitch", "malfunction", "incorrect", "wrong"
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in bug_indicators)
    
    def detect_competitors(self, text: str) -> List[str]:
        """Detect competitor mentions"""
        # Common competitor names (can be customized per industry)
        competitors = [
            "salesforce", "hubspot", "zendesk", "intercom", "freshdesk",
            "pipedrive", "zoho", "microsoft dynamics", "oracle", "sap"
        ]
        
        text_lower = text.lower()
        mentioned = [comp for comp in competitors if comp in text_lower]
        
        return mentioned
    
    def calculate_priority_score(self, 
                                 sentiment_score: float,
                                 urgency_score: int,
                                 is_feature_request: bool,
                                 is_bug_report: bool) -> float:
        """
        Calculate overall priority score (0-100)
        """
        # Weighted priority calculation
        priority = 0
        
        # Urgency contributes most (40%)
        priority += (urgency_score / 10) * 40
        
        # Negative sentiment increases priority (30%)
        if sentiment_score < 0:
            priority += abs(sentiment_score) * 30
        
        # Bug reports get high priority (20%)
        if is_bug_report:
            priority += 20
        
        # Feature requests get moderate priority (10%)
        if is_feature_request:
            priority += 10
        
        return min(100, priority)
    
    def analyze_feedback(self, text: str) -> Dict:
        """
        Comprehensive feedback analysis
        Returns all analysis results
        """
        # Sentiment analysis
        sentiment = self.analyze_sentiment(text)
        
        # Emotion detection
        emotion = self.detect_emotion(text)
        
        # Urgency calculation
        urgency_score, urgency_level = self.calculate_urgency(text, sentiment)
        
        # Embedding generation
        embedding = self.generate_embedding(text)
        
        # Keyword extraction
        keywords = self.extract_keywords(text)
        
        # Feature/bug detection
        is_feature_request = self.detect_feature_request(text)
        is_bug_report = self.detect_bug_report(text)
        
        # Competitor detection
        competitors = self.detect_competitors(text)
        
        # Priority calculation
        priority_score = self.calculate_priority_score(
            sentiment.get("compound_score", 0),
            urgency_score,
            is_feature_request,
            is_bug_report
        )
        
        return {
            "sentiment": sentiment.get("label"),
            "sentiment_score": sentiment.get("compound_score"),
            "sentiment_details": sentiment,
            "emotion": emotion.get("dominant", "neutral"),
            "emotion_scores": emotion.get("scores", {}),
            "urgency_score": urgency_score,
            "urgency_level": urgency_level,
            "keywords": keywords,
            "embedding": embedding,
            "is_feature_request": is_feature_request,
            "is_bug_report": is_bug_report,
            "competitor_mentions": competitors,
            "priority_score": priority_score
        }


# Singleton instance
_ai_analyzer = None

def get_ai_analyzer() -> AIAnalyzer:
    """Get or create AI analyzer instance"""
    global _ai_analyzer
    if _ai_analyzer is None:
        _ai_analyzer = AIAnalyzer()
    return _ai_analyzer
