"""
AI-Powered Recruitment Platform - Agentic CV-JD Matching Suite
"""

__version__ = "1.0.0"
__author__ = "AI Recruitment Team"

from .document_parser import CVParser, JDParser, WebScraper
from .matching_engine import MatchingEngine
from .cv_rewrite_engine import CVRewriteEngine
from .agent_system import (
    AgentRole, RecruitmentAgent, ScreeningAgent, MatchingAgent,
    AnalysisAgent, RewriteAgent, IngestionAgent, CoordinatorAgent
)