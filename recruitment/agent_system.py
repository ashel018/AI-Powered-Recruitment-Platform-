"""
Agentic System for Recruitment Platform
Multi-role AI agents coordinating CV screening and matching workflows
"""

import os
from typing import Dict, List, Optional, Any
from enum import Enum
import openai
from langchain_openai import ChatOpenAI
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.prompts import StringPromptTemplate
from langchain.chains import LLMChain
from langchain.schema import AgentAction, AgentFinish
from langchain.tools import BaseTool
import re

from .document_parser import CVParser, JDParser
from .matching_engine import MatchingEngine
from .cv_rewrite_engine import CVRewriteEngine


class AgentRole(Enum):
    SCREENING = "screening_agent"
    MATCHING = "matching_agent"
    ANALYSIS = "analysis_agent"
    REWRITE = "rewrite_agent"
    INGESTION = "ingestion_agent"
    COORDINATOR = "coordinator_agent"


class RecruitmentAgent:
    """Base class for recruitment AI agents"""

    def __init__(self, role: AgentRole, llm: ChatOpenAI = None):
        self.role = role
        self.llm = llm or ChatOpenAI(temperature=0.3, model="gpt-3.5-turbo")
        self.tools = []
        self.setup_tools()

    def setup_tools(self):
        """Setup tools specific to the agent role"""
        pass

    def execute_task(self, task: str, context: Dict = None) -> Dict:
        """Execute a task with the agent's capabilities"""
        raise NotImplementedError("Subclasses must implement execute_task")


class ScreeningAgent(RecruitmentAgent):
    """Agent responsible for initial CV screening and qualification"""

    def __init__(self):
        super().__init__(AgentRole.SCREENING)
        self.cv_parser = CVParser()
        self.matching_engine = MatchingEngine()

    def setup_tools(self):
        self.tools = [
            Tool(
                name="ParseCV",
                description="Parse and extract structured data from CV documents",
                func=self._parse_cv_tool
            ),
            Tool(
                name="InitialScreening",
                description="Perform initial screening based on basic qualifications",
                func=self._initial_screening_tool
            ),
            Tool(
                name="QualificationCheck",
                description="Check if candidate meets minimum qualifications",
                func=self._qualification_check_tool
            )
        ]

    def execute_task(self, task: str, context: Dict = None) -> Dict:
        """Execute screening task"""
        cv_path = context.get('cv_path')
        jd_data = context.get('jd_data')

        if not cv_path or not jd_data:
            return {"error": "Missing CV path or job data"}

        # Parse CV
        cv_data = self.cv_parser.parse_cv(cv_path)

        # Perform initial screening
        screening_result = self._perform_screening(cv_data, jd_data)

        return {
            "cv_data": cv_data,
            "screening_result": screening_result,
            "qualified": screening_result.get("qualified", False),
            "screening_criteria": screening_result.get("criteria", [])
        }

    def _perform_screening(self, cv_data: Dict, jd_data: Dict) -> Dict:
        """Perform initial screening analysis"""
        prompt = f"""
        Perform initial screening of this candidate for the job position.

        Evaluate based on:
        1. Experience level match
        2. Education requirements
        3. Basic skill alignment
        4. Location preferences (if specified)
        5. Overall qualification status

        CV Data:
        {cv_data}

        Job Requirements:
        {jd_data}

        Return as JSON:
        {{
            "qualified": true/false,
            "confidence_score": 0-100,
            "criteria": [
                {{"criterion": "Experience", "met": true/false, "notes": "..."}},
                ...
            ],
            "recommendations": []
        }}
        """

        try:
            response = self.llm.predict(prompt)
            import json
            result = json.loads(response)
            return result
        except Exception as e:
            return {
                "qualified": True,  # Default to qualified if analysis fails
                "confidence_score": 50,
                "criteria": [{"criterion": "Analysis failed", "met": None, "notes": str(e)}],
                "recommendations": ["Manual review recommended"]
            }

    def _parse_cv_tool(self, cv_path: str) -> str:
        """Tool for parsing CV"""
        try:
            cv_data = self.cv_parser.parse_cv(cv_path)
            return f"CV parsed successfully: {cv_data.get('personal_info', {}).get('name', 'Unknown')}"
        except Exception as e:
            return f"CV parsing failed: {e}"

    def _initial_screening_tool(self, cv_data: str, jd_data: str) -> str:
        """Tool for initial screening"""
        try:
            import json
            cv = json.loads(cv_data)
            jd = json.loads(jd_data)
            result = self._perform_screening(cv, jd)
            return f"Screening complete: Qualified={result['qualified']}"
        except Exception as e:
            return f"Screening failed: {e}"

    def _qualification_check_tool(self, cv_data: str, criteria: str) -> str:
        """Tool for checking specific qualifications"""
        return f"Qualification check for {criteria}: Analysis would be performed here"


class MatchingAgent(RecruitmentAgent):
    """Agent responsible for detailed CV-JD matching"""

    def __init__(self):
        super().__init__(AgentRole.MATCHING)
        self.matching_engine = MatchingEngine()

    def setup_tools(self):
        self.tools = [
            Tool(
                name="ComputeSimilarity",
                description="Compute semantic similarity between CV and JD",
                func=self._similarity_tool
            ),
            Tool(
                name="DetailedAnalysis",
                description="Perform detailed matching analysis",
                func=self._detailed_analysis_tool
            ),
            Tool(
                name="RankCandidates",
                description="Rank multiple candidates for a job",
                func=self._ranking_tool
            )
        ]

    def execute_task(self, task: str, context: Dict = None) -> Dict:
        """Execute matching task"""
        cv_data = context.get('cv_data')
        jd_data = context.get('jd_data')

        if not cv_data or not jd_data:
            return {"error": "Missing CV or JD data"}

        # Perform detailed matching
        analysis = self.matching_engine.detailed_matching_analysis(cv_data, jd_data)

        # Compute similarity score
        cv_text = self._dict_to_text(cv_data)
        jd_text = self._dict_to_text(jd_data)
        similarity_score = self.matching_engine.compute_similarity_score(cv_text, jd_text)

        return {
            "similarity_score": similarity_score,
            "detailed_analysis": analysis,
            "skill_matches": analysis.get("skill_matches", []),
            "skill_gaps": analysis.get("skill_gaps", []),
            "recommendations": analysis.get("recommendations", [])
        }

    def _dict_to_text(self, data: Dict) -> str:
        """Convert dict to text for similarity computation"""
        return str(data)

    def _similarity_tool(self, cv_text: str, jd_text: str) -> str:
        """Tool for computing similarity"""
        score = self.matching_engine.compute_similarity_score(cv_text, jd_text)
        return f"Similarity score: {score}%"

    def _detailed_analysis_tool(self, cv_data: str, jd_data: str) -> str:
        """Tool for detailed analysis"""
        try:
            import json
            cv = json.loads(cv_data)
            jd = json.loads(jd_data)
            analysis = self.matching_engine.detailed_matching_analysis(cv, jd)
            return f"Detailed analysis complete: Score {analysis.get('overall_score', 0)}%"
        except Exception as e:
            return f"Analysis failed: {e}"

    def _ranking_tool(self, candidates_data: str, jd_data: str) -> str:
        """Tool for ranking candidates"""
        try:
            import json
            candidates = json.loads(candidates_data)
            jd = json.loads(jd_data)
            ranked = self.matching_engine.rank_candidates(candidates, jd)
            return f"Ranking complete: Top candidate score {ranked[0]['match_score'] if ranked else 0}%"
        except Exception as e:
            return f"Ranking failed: {e}"


class AnalysisAgent(RecruitmentAgent):
    """Agent responsible for SWOT and GAP analysis"""

    def __init__(self):
        super().__init__(AgentRole.ANALYSIS)
        self.matching_engine = MatchingEngine()

    def setup_tools(self):
        self.tools = [
            Tool(
                name="SWOTAnalysis",
                description="Perform SWOT analysis for candidate-job match",
                func=self._swot_tool
            ),
            Tool(
                name="GapAnalysis",
                description="Identify skill and experience gaps",
                func=self._gap_tool
            ),
            Tool(
                name="GenerateInsights",
                description="Generate recruitment insights and recommendations",
                func=self._insights_tool
            )
        ]

    def execute_task(self, task: str, context: Dict = None) -> Dict:
        """Execute analysis task"""
        cv_data = context.get('cv_data')
        jd_data = context.get('jd_data')

        if not cv_data or not jd_data:
            return {"error": "Missing CV or JD data"}

        # Perform SWOT analysis
        swot = self.matching_engine.swot_analysis(cv_data, jd_data)

        # Perform gap analysis
        gaps = self.matching_engine.gap_analysis(cv_data, jd_data)

        return {
            "swot_analysis": swot,
            "gap_analysis": gaps,
            "insights": self._generate_insights(swot, gaps)
        }

    def _generate_insights(self, swot: Dict, gaps: Dict) -> List[str]:
        """Generate actionable insights from analysis"""
        insights = []

        # SWOT-based insights
        strengths = swot.get('strengths', [])
        weaknesses = swot.get('weaknesses', [])
        opportunities = swot.get('opportunities', [])
        threats = swot.get('threats', [])

        if strengths:
            insights.append(f"Leverage strengths: {', '.join(strengths[:3])}")

        if weaknesses:
            insights.append(f"Address weaknesses: {', '.join(weaknesses[:3])}")

        if opportunities:
            insights.append(f"Capitalize on opportunities: {', '.join(opportunities[:3])}")

        # Gap-based insights
        skill_gaps = gaps.get('skill_gaps', [])
        if skill_gaps:
            insights.append(f"Bridge skill gaps: {', '.join(skill_gaps[:3])}")

        return insights

    def _swot_tool(self, cv_data: str, jd_data: str) -> str:
        """Tool for SWOT analysis"""
        try:
            import json
            cv = json.loads(cv_data)
            jd = json.loads(jd_data)
            swot = self.matching_engine.swot_analysis(cv, jd)
            return f"SWOT analysis complete: {len(swot.get('strengths', []))} strengths identified"
        except Exception as e:
            return f"SWOT analysis failed: {e}"

    def _gap_tool(self, cv_data: str, jd_data: str) -> str:
        """Tool for gap analysis"""
        try:
            import json
            cv = json.loads(cv_data)
            jd = json.loads(jd_data)
            gaps = self.matching_engine.gap_analysis(cv, jd)
            return f"Gap analysis complete: {len(gaps.get('skill_gaps', []))} skill gaps identified"
        except Exception as e:
            return f"Gap analysis failed: {e}"

    def _insights_tool(self, swot_data: str, gap_data: str) -> str:
        """Tool for generating insights"""
        try:
            import json
            swot = json.loads(swot_data)
            gaps = json.loads(gap_data)
            insights = self._generate_insights(swot, gaps)
            return f"Insights generated: {len(insights)} recommendations"
        except Exception as e:
            return f"Insights generation failed: {e}"


class RewriteAgent(RecruitmentAgent):
    """Agent responsible for CV rewriting and optimization"""

    def __init__(self):
        super().__init__(AgentRole.REWRITE)
        self.rewrite_engine = CVRewriteEngine()

    def setup_tools(self):
        self.tools = [
            Tool(
                name="RewriteCV",
                description="Rewrite CV to match job description",
                func=self._rewrite_tool
            ),
            Tool(
                name="OptimizeSection",
                description="Optimize specific CV section",
                func=self._optimize_section_tool
            ),
            Tool(
                name="GenerateCoverLetter",
                description="Generate tailored cover letter",
                func=self._cover_letter_tool
            )
        ]

    def execute_task(self, task: str, context: Dict = None) -> Dict:
        """Execute rewrite task"""
        cv_data = context.get('cv_data')
        jd_data = context.get('jd_data')
        optimization_level = context.get('optimization_level', 'moderate')

        if not cv_data or not jd_data:
            return {"error": "Missing CV or JD data"}

        # Rewrite CV
        rewrite_result = self.rewrite_engine.rewrite_cv(
            cv_data, jd_data, optimization_level
        )

        return rewrite_result

    def _rewrite_tool(self, cv_data: str, jd_data: str, level: str = "moderate") -> str:
        """Tool for CV rewriting"""
        try:
            import json
            cv = json.loads(cv_data)
            jd = json.loads(jd_data)
            result = self.rewrite_engine.rewrite_cv(cv, jd, level)
            improvement = result.get('optimization_details', {}).get('improvement', 0)
            return f"CV rewritten: {improvement}% improvement in match score"
        except Exception as e:
            return f"CV rewrite failed: {e}"

    def _optimize_section_tool(self, section_name: str, content: str, keywords: str) -> str:
        """Tool for section optimization"""
        try:
            keyword_list = keywords.split(',')
            optimized = self.rewrite_engine.optimize_cv_section(
                section_name, content, keyword_list
            )
            return f"Section '{section_name}' optimized with keywords"
        except Exception as e:
            return f"Section optimization failed: {e}"

    def _cover_letter_tool(self, cv_data: str, jd_data: str) -> str:
        """Tool for cover letter generation"""
        try:
            import json
            cv = json.loads(cv_data)
            jd = json.loads(jd_data)
            cover_letter = self.rewrite_engine.generate_cover_letter(cv, jd)
            return f"Cover letter generated: {len(cover_letter)} characters"
        except Exception as e:
            return f"Cover letter generation failed: {e}"


class IngestionAgent(RecruitmentAgent):
    """Agent responsible for multi-format data ingestion"""

    def __init__(self):
        super().__init__(AgentRole.INGESTION)
        self.cv_parser = CVParser()
        self.jd_parser = JDParser()

    def setup_tools(self):
        self.tools = [
            Tool(
                name="ParseDocument",
                description="Parse CV or JD from various formats",
                func=self._parse_document_tool
            ),
            Tool(
                name="ScrapeJobDescription",
                description="Scrape JD from web URL",
                func=self._scrape_jd_tool
            ),
            Tool(
                name="ValidateData",
                description="Validate parsed document data",
                func=self._validate_data_tool
            )
        ]

    def execute_task(self, task: str, context: Dict = None) -> Dict:
        """Execute ingestion task"""
        source = context.get('source')
        source_type = context.get('source_type', 'file')
        doc_type = context.get('doc_type', 'cv')  # 'cv' or 'jd'

        if not source:
            return {"error": "No source provided"}

        try:
            if doc_type == 'cv':
                if source_type == 'file':
                    parsed_data = self.cv_parser.parse_cv(source)
                else:
                    return {"error": "CVs must be file-based"}
            else:  # jd
                parsed_data = self.jd_parser.parse_jd(source, source_type)

            return {
                "parsed_data": parsed_data,
                "doc_type": doc_type,
                "source_type": source_type,
                "validation": self._validate_parsed_data(parsed_data, doc_type)
            }

        except Exception as e:
            return {"error": f"Ingestion failed: {e}"}

    def _validate_parsed_data(self, data: Dict, doc_type: str) -> Dict:
        """Validate parsed document data"""
        validation = {
            "is_valid": True,
            "issues": [],
            "completeness_score": 0
        }

        if doc_type == 'cv':
            required_fields = ['personal_info', 'experience', 'skills']
            total_fields = len(required_fields)
            present_fields = sum(1 for field in required_fields if data.get(field))

            validation["completeness_score"] = (present_fields / total_fields) * 100

            if not data.get('personal_info', {}).get('name'):
                validation["issues"].append("Missing candidate name")

            if not data.get('experience'):
                validation["issues"].append("No work experience found")

        else:  # jd
            if not data.get('job_title'):
                validation["issues"].append("Missing job title")

            if not data.get('requirements', {}).get('skills'):
                validation["issues"].append("No skills requirements found")

        if validation["issues"]:
            validation["is_valid"] = False

        return validation

    def _parse_document_tool(self, source: str, source_type: str, doc_type: str) -> str:
        """Tool for document parsing"""
        try:
            if doc_type == 'cv':
                data = self.cv_parser.parse_cv(source)
            else:
                data = self.jd_parser.parse_jd(source, source_type)
            return f"Document parsed: {doc_type.upper()} with {len(data)} fields"
        except Exception as e:
            return f"Parsing failed: {e}"

    def _scrape_jd_tool(self, url: str) -> str:
        """Tool for JD scraping"""
        try:
            data = self.jd_parser.parse_jd(url, 'url')
            return f"JD scraped from {url}: {data.get('job_title', 'Unknown position')}"
        except Exception as e:
            return f"Scraping failed: {e}"

    def _validate_data_tool(self, data: str, doc_type: str) -> str:
        """Tool for data validation"""
        try:
            import json
            parsed = json.loads(data)
            validation = self._validate_parsed_data(parsed, doc_type)
            return f"Validation complete: {validation['completeness_score']}% complete"
        except Exception as e:
            return f"Validation failed: {e}"


class CoordinatorAgent(RecruitmentAgent):
    """Master agent that coordinates all other agents"""

    def __init__(self):
        super().__init__(AgentRole.COORDINATOR)
        self.agents = {
            AgentRole.SCREENING: ScreeningAgent(),
            AgentRole.MATCHING: MatchingAgent(),
            AgentRole.ANALYSIS: AnalysisAgent(),
            AgentRole.REWRITE: RewriteAgent(),
            AgentRole.INGESTION: IngestionAgent()
        }

    def setup_tools(self):
        # Coordinator has access to all agent tools
        for agent in self.agents.values():
            self.tools.extend(agent.tools)

    def execute_task(self, task: str, context: Dict = None) -> Dict:
        """Execute coordinated recruitment workflow"""
        workflow_type = context.get('workflow', 'full_analysis')

        if workflow_type == 'full_analysis':
            return self._full_analysis_workflow(context)
        elif workflow_type == 'quick_screen':
            return self._quick_screen_workflow(context)
        elif workflow_type == 'cv_optimization':
            return self._cv_optimization_workflow(context)
        else:
            return {"error": f"Unknown workflow: {workflow_type}"}

    def _full_analysis_workflow(self, context: Dict) -> Dict:
        """Complete recruitment analysis workflow"""
        results = {}

        # Step 1: Ingest documents
        ingestion_agent = self.agents[AgentRole.INGESTION]
        cv_result = ingestion_agent.execute_task("parse_cv", {
            "source": context.get("cv_path"),
            "source_type": "file",
            "doc_type": "cv"
        })
        jd_result = ingestion_agent.execute_task("parse_jd", {
            "source": context.get("jd_path"),
            "source_type": "file",
            "doc_type": "jd"
        })

        results["ingestion"] = {
            "cv": cv_result,
            "jd": jd_result
        }

        if cv_result.get("error") or jd_result.get("error"):
            return {"error": "Document ingestion failed", "details": results}

        # Step 2: Screening
        screening_agent = self.agents[AgentRole.SCREENING]
        screening_result = screening_agent.execute_task("screen", {
            "cv_data": cv_result["parsed_data"],
            "jd_data": jd_result["parsed_data"]
        })

        results["screening"] = screening_result

        # Step 3: Detailed matching
        matching_agent = self.agents[AgentRole.MATCHING]
        matching_result = matching_agent.execute_task("match", {
            "cv_data": cv_result["parsed_data"],
            "jd_data": jd_result["parsed_data"]
        })

        results["matching"] = matching_result

        # Step 4: Analysis
        analysis_agent = self.agents[AgentRole.ANALYSIS]
        analysis_result = analysis_agent.execute_task("analyze", {
            "cv_data": cv_result["parsed_data"],
            "jd_data": jd_result["parsed_data"]
        })

        results["analysis"] = analysis_result

        # Step 5: CV optimization (optional)
        if context.get("optimize_cv", False):
            rewrite_agent = self.agents[AgentRole.REWRITE]
            rewrite_result = rewrite_agent.execute_task("rewrite", {
                "cv_data": cv_result["parsed_data"],
                "jd_data": jd_result["parsed_data"],
                "optimization_level": context.get("optimization_level", "moderate")
            })

            results["rewrite"] = rewrite_result

        return results

    def _quick_screen_workflow(self, context: Dict) -> Dict:
        """Quick screening workflow"""
        ingestion_agent = self.agents[AgentRole.INGESTION]
        screening_agent = self.agents[AgentRole.SCREENING]

        # Ingest and screen
        cv_result = ingestion_agent.execute_task("parse_cv", {
            "source": context.get("cv_path"),
            "source_type": "file",
            "doc_type": "cv"
        })

        jd_result = ingestion_agent.execute_task("parse_jd", {
            "source": context.get("jd_path"),
            "source_type": "file",
            "doc_type": "jd"
        })

        screening_result = screening_agent.execute_task("screen", {
            "cv_data": cv_result.get("parsed_data"),
            "jd_data": jd_result.get("parsed_data")
        })

        return {
            "cv_parsed": cv_result,
            "jd_parsed": jd_result,
            "screening": screening_result
        }

    def _cv_optimization_workflow(self, context: Dict) -> Dict:
        """CV optimization workflow"""
        ingestion_agent = self.agents[AgentRole.INGESTION]
        rewrite_agent = self.agents[AgentRole.REWRITE]

        # Ingest documents
        cv_result = ingestion_agent.execute_task("parse_cv", {
            "source": context.get("cv_path"),
            "source_type": "file",
            "doc_type": "cv"
        })

        jd_result = ingestion_agent.execute_task("parse_jd", {
            "source": context.get("jd_path"),
            "source_type": "file",
            "doc_type": "jd"
        })

        # Optimize CV
        rewrite_result = rewrite_agent.execute_task("rewrite", {
            "cv_data": cv_result.get("parsed_data"),
            "jd_data": jd_result.get("parsed_data"),
            "optimization_level": context.get("optimization_level", "moderate")
        })

        return {
            "original_cv": cv_result,
            "jd": jd_result,
            "optimized_cv": rewrite_result
        }