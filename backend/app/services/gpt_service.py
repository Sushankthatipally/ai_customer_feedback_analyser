"""
OpenAI GPT Service for Advanced Insights and Summarization
"""

from openai import AsyncOpenAI
from typing import List, Dict, Optional
import json
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class GPTService:
    """Service for OpenAI GPT-based insights"""
    
    def __init__(self):
        self.enabled = bool(settings.OPENAI_API_KEY)
        if self.enabled:
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_MODEL
        else:
            self.client = None
            self.model = None
            logger.info("GPT Service disabled - no API key provided")
    
    async def generate_executive_summary(self, 
                                        feedbacks: List[Dict],
                                        stats: Dict) -> Dict:
        """
        Generate executive summary from feedback data
        """
        if not self.enabled:
            return {
                "error": "GPT features disabled",
                "message": "OpenAI API key not configured. Only local AI analysis available."
            }
        
        # Prepare data summary
        feedback_sample = [f["text"][:200] for f in feedbacks[:20]]  # Sample
        
        prompt = f"""
        As a customer insights analyst, create an executive summary based on the following data:
        
        **Period Statistics:**
        - Total Feedback: {stats.get('total_feedback', 0)}
        - Average Sentiment: {stats.get('avg_sentiment', 0):.2f}
        - Positive: {stats.get('positive_count', 0)} | Negative: {stats.get('negative_count', 0)} | Neutral: {stats.get('neutral_count', 0)}
        - Feature Requests: {stats.get('feature_requests', 0)}
        - Bug Reports: {stats.get('bug_reports', 0)}
        
        **Sample Feedback:**
        {chr(10).join(f"- {text}" for text in feedback_sample)}
        
        Provide:
        1. A concise 2-3 sentence overview
        2. Top 5 key themes/issues
        3. Top 3 feature requests
        4. Top 3 urgent issues
        5. 3-5 actionable recommendations
        
        Format as JSON with keys: overview, key_themes, top_requests, urgent_issues, recommendations
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert customer insights analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            
            # Try to parse as JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"raw_summary": content}
                
        except Exception as e:
            logger.error(f"GPT summary generation error: {e}")
            return {"error": str(e)}
    
    async def generate_action_items(self, feedbacks: List[Dict]) -> List[Dict]:
        """
        Generate prioritized action items from feedback
        """
        if not self.enabled:
            return []
        
        # Get high-priority and negative feedback
        priority_feedback = [
            f for f in feedbacks 
            if f.get("urgency_level") in ["high", "critical"] or f.get("sentiment") == "negative"
        ][:15]
        
        feedback_texts = "\n".join([f"- {f.get('text', '')[:150]}" for f in priority_feedback])
        
        prompt = f"""
        Based on this customer feedback, generate specific action items:
        
        {feedback_texts}
        
        For each action item, provide:
        - title: Brief description
        - category: bug_fix, feature, improvement, support
        - priority: high, medium, low
        - estimated_impact: number of customers affected
        - suggested_owner: product, engineering, support, sales
        
        Return as JSON array with 5-10 action items.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a product manager creating actionable tasks."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return []
                
        except Exception as e:
            logger.error(f"Action items generation error: {e}")
            return []
    
    async def categorize_feedback(self, text: str, categories: List[str]) -> Dict:
        """
        Categorize feedback using GPT
        """
        if not self.enabled:
            return {"main_category": "uncategorized", "sub_categories": [], "note": "GPT disabled"}
        
        prompt = f"""
        Categorize this customer feedback into one or more of these categories:
        {', '.join(categories)}
        
        Feedback: "{text}"
        
        Return JSON with: {{"main_category": "...", "sub_categories": [...], "confidence": 0-1}}
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a feedback classification expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            content = response.choices[0].message.content
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"main_category": "uncategorized", "sub_categories": []}
                
        except Exception as e:
            logger.error(f"Categorization error: {e}")
            return {"main_category": "uncategorized", "sub_categories": []}
    
    async def detect_churn_risk(self, customer_feedbacks: List[str]) -> Dict:
        """
        Analyze customer feedback history for churn risk
        """
        if not self.enabled:
            return {"risk_level": "unknown", "risk_score": 0, "note": "GPT features disabled"}
        
        feedback_text = "\n".join([f"- {text[:150]}" for text in customer_feedbacks[-10:]])
        
        prompt = f"""
        Analyze this customer's feedback history for churn risk:
        
        {feedback_text}
        
        Provide:
        - risk_level: low, medium, high, critical
        - risk_score: 0-100
        - key_indicators: list of warning signs
        - recommended_actions: immediate steps to take
        
        Return as JSON.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a customer success analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"risk_level": "unknown", "risk_score": 50}
                
        except Exception as e:
            logger.error(f"Churn risk analysis error: {e}")
            return {"risk_level": "unknown", "risk_score": 50}
    
    async def suggest_response(self, feedback: str, context: Dict) -> str:
        """
        Generate suggested response to customer feedback
        """
        if not self.enabled:
            return "GPT features disabled. Configure OpenAI API key for AI-generated responses."
        
        prompt = f"""
        Generate a professional, empathetic response to this customer feedback:
        
        Feedback: "{feedback}"
        
        Context:
        - Sentiment: {context.get('sentiment', 'neutral')}
        - Category: {context.get('category', 'general')}
        - Urgency: {context.get('urgency_level', 'medium')}
        
        Keep response concise (2-3 sentences), acknowledge their concern, and provide next steps if applicable.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a customer support specialist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"Response suggestion error: {e}")
            return "Thank you for your feedback. We're looking into this and will get back to you soon."


# Singleton instance
_gpt_service = None

def get_gpt_service() -> GPTService:
    """Get or create GPT service instance"""
    global _gpt_service
    if _gpt_service is None:
        _gpt_service = GPTService()
    return _gpt_service
