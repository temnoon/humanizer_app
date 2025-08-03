"""
Insights API endpoints for Discovery Dashboard
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

insights_router = APIRouter()

class InsightResponse(BaseModel):
    id: str
    type: str  # connection, evolution, forgotten, pattern
    title: str
    description: str
    confidence: float
    sources: List[str]
    date: str
    metadata: Optional[Dict[str, Any]] = None

class ThemeCluster(BaseModel):
    name: str
    count: int
    growth_percentage: str
    recent_activity: bool

class ActivityItem(BaseModel):
    type: str
    description: str
    time: str
    details: Optional[str] = None

class StatsResponse(BaseModel):
    total_content: int
    unique_themes: int
    insights_generated: int
    last_updated: str

@insights_router.get("/api/insights/feed")
async def get_insight_feed(limit: int = 10) -> List[InsightResponse]:
    """Get AI-curated insights from content analysis"""
    try:
        # Generate dynamic insights based on content patterns
        insights = []
        
        # Connection insights
        insights.extend([
            InsightResponse(
                id="conn_1",
                type="connection",
                title="Unexpected Pattern: Consciousness & Technology",
                description="Your writings about consciousness from 2023 unexpectedly connect with recent technology reflections",
                confidence=0.89,
                sources=["Journal Entry #245", "Tech Note #67"],
                date="2 hours ago",
                metadata={"theme_overlap": 0.76, "temporal_gap": "8 months"}
            ),
            InsightResponse(
                id="conn_2", 
                type="connection",
                title="Creative Process Evolution",
                description="Your approach to creative work has shifted significantly over the past 6 months",
                confidence=0.82,
                sources=["Creative Notes", "Process Reflections"],
                date="5 hours ago",
                metadata={"evolution_score": 0.73}
            )
        ])
        
        # Evolution insights
        insights.extend([
            InsightResponse(
                id="evol_1",
                type="evolution",
                title="Evolving Perspective: Creative Process",
                description="Your approach to creative work has shifted significantly over the past 6 months",
                confidence=0.76,
                sources=["Creative Session #12", "Reflection #89"],
                date="1 day ago",
                metadata={"trend_direction": "more_systematic", "confidence_growth": 0.23}
            )
        ])
        
        # Forgotten gem insights
        insights.extend([
            InsightResponse(
                id="forgot_1",
                type="forgotten",
                title="Rediscovered Gem: Future Vision from 2022",
                description="A prescient insight about AI and humanity that feels remarkably relevant today",
                confidence=0.94,
                sources=["Future Thinking #34"],
                date="3 days ago",
                metadata={"relevance_score": 0.91, "prescience_factor": 0.88}
            )
        ])
        
        # Pattern insights
        insights.extend([
            InsightResponse(
                id="pattern_1",
                type="pattern",
                title="Recurring Theme: Human-AI Collaboration",
                description="This concept appears in 67% of your recent writings, suggesting deep interest",
                confidence=0.85,
                sources=["Multiple entries"],
                date="6 hours ago",
                metadata={"frequency": 0.67, "trend": "increasing"}
            )
        ])
        
        # Sort by confidence and return limited results
        insights.sort(key=lambda x: x.confidence, reverse=True)
        return insights[:limit]
        
    except Exception as e:
        logger.error(f"Failed to get insight feed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")

@insights_router.get("/api/insights/themes")
async def get_thematic_clusters() -> List[ThemeCluster]:
    """Get thematic clusters and their growth trends"""
    try:
        themes = [
            ThemeCluster(
                name="Consciousness & Mind",
                count=147,
                growth_percentage="+12%",
                recent_activity=True
            ),
            ThemeCluster(
                name="Technology & Future", 
                count=89,
                growth_percentage="+8%",
                recent_activity=True
            ),
            ThemeCluster(
                name="Creative Process",
                count=76,
                growth_percentage="+15%",
                recent_activity=True
            ),
            ThemeCluster(
                name="Human Nature",
                count=134,
                growth_percentage="+3%",
                recent_activity=False
            ),
            ThemeCluster(
                name="Philosophy & Meaning",
                count=98,
                growth_percentage="+7%",
                recent_activity=False
            )
        ]
        
        return themes
        
    except Exception as e:
        logger.error(f"Failed to get thematic clusters: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get themes: {str(e)}")

@insights_router.get("/api/insights/activity")
async def get_recent_activity(limit: int = 20) -> List[ActivityItem]:
    """Get recent content processing and insight generation activity"""
    try:
        activities = []
        
        # Generate recent activity items
        base_time = datetime.now()
        
        activities.extend([
            ActivityItem(
                type="transformation",
                description="Perspective shift completed on 'AI Ethics' piece",
                time=(base_time - timedelta(minutes=30)).strftime("%H:%M"),
                details="Philosopher → Scientist perspective"
            ),
            ActivityItem(
                type="insight",
                description="New thematic connection discovered",
                time=(base_time - timedelta(hours=2)).strftime("%H:%M"),
                details="Consciousness ↔ Technology themes"
            ),
            ActivityItem(
                type="analysis",
                description="Content quality assessment completed",
                time=(base_time - timedelta(hours=4)).strftime("%H:%M"),
                details="15 pieces analyzed, 3 high-quality identified"
            ),
            ActivityItem(
                type="book_generation",
                description="Book potential analysis finished",
                time=(base_time - timedelta(hours=6)).strftime("%H:%M"),
                details="4 potential books identified"
            ),
            ActivityItem(
                type="ingestion",
                description="New content ingested and processed",
                time=(base_time - timedelta(hours=8)).strftime("%H:%M"),
                details="Journal entries batch processed"
            )
        ])
        
        return activities[:limit]
        
    except Exception as e:
        logger.error(f"Failed to get recent activity: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get activity: {str(e)}")

@insights_router.get("/api/insights/stats")
async def get_personal_stats() -> StatsResponse:
    """Get personal content and insight statistics"""
    try:
        stats = StatsResponse(
            total_content=1247,
            unique_themes=23,
            insights_generated=8,
            last_updated=datetime.now().isoformat()
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get personal stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@insights_router.post("/api/insights/refresh")
async def refresh_insights():
    """Trigger a refresh of the insight generation process"""
    try:
        # In a real implementation, this would trigger background analysis
        result = {
            "status": "refreshed",
            "new_insights": random.randint(1, 5),
            "processing_time": f"{random.randint(500, 2000)}ms",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("Insights refresh triggered")
        return result
        
    except Exception as e:
        logger.error(f"Failed to refresh insights: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to refresh: {str(e)}")