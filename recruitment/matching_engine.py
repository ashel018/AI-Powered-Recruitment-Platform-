"""
CV-JD Matching Engine with AI-powered similarity analysis
"""

import os
import numpy as np
from typing import Dict, List, Tuple, Optional
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import openai
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import chromadb
from chromadb.config import Settings


class MatchingEngine:
    """AI-powered CV-JD matching engine"""

    def __init__(self):
        # Initialize sentence transformer for embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Initialize ChromaDB for vector storage
        self.chroma_client = chromadb.PersistentClient(
            path="./recruitment/vector_db"
        )

        # Initialize LLM for advanced analysis
        self.llm = ChatOpenAI(temperature=0.1, model="gpt-3.5-turbo")

        # Create collections for CVs and JDs
        try:
            self.cv_collection = self.chroma_client.get_or_create_collection(
                name="cv_embeddings",
                metadata={"description": "CV document embeddings"}
            )
            self.jd_collection = self.chroma_client.get_or_create_collection(
                name="jd_embeddings",
                metadata={"description": "Job description embeddings"}
            )
        except Exception as e:
            print(f"Error creating collections: {e}")

    def compute_similarity_score(self, cv_text: str, jd_text: str) -> float:
        """
        Compute semantic similarity between CV and JD
        Returns score between 0-100
        """
        try:
            # Generate embeddings
            cv_embedding = self.embedding_model.encode([cv_text])[0]
            jd_embedding = self.embedding_model.encode([jd_text])[0]

            # Compute cosine similarity
            similarity = cosine_similarity(
                cv_embedding.reshape(1, -1),
                jd_embedding.reshape(1, -1)
            )[0][0]

            # Convert to 0-100 scale
            score = float(similarity * 100)
            return round(score, 2)

        except Exception as e:
            print(f"Error computing similarity: {e}")
            return 0.0

    def detailed_matching_analysis(self, cv_data: Dict, jd_data: Dict) -> Dict:
        """
        Perform detailed matching analysis with skill mapping and gap analysis
        """
        prompt = f"""
        Analyze the match between this candidate CV and job description.
        Provide a detailed analysis including:

        1. Overall match score (0-100)
        2. Key matching skills
        3. Missing required skills
        4. Experience match assessment
        5. Education match assessment
        6. Recommendations for improvement

        CV Data:
        {cv_data}

        Job Description Data:
        {jd_data}

        Return your analysis as a JSON object with the following structure:
        {{
            "overall_score": 0,
            "skill_matches": [],
            "skill_gaps": [],
            "experience_match": "",
            "education_match": "",
            "recommendations": [],
            "strengths": [],
            "weaknesses": []
        }}
        """

        try:
            response = self.llm.predict(prompt)
            import json
            analysis = json.loads(response)
            return analysis
        except Exception as e:
            print(f"LLM analysis failed: {e}")
            return self._fallback_analysis(cv_data, jd_data)

    def _fallback_analysis(self, cv_data: Dict, jd_data: Dict) -> Dict:
        """Fallback analysis using rule-based matching"""
        cv_skills = set(cv_data.get('skills', []))
        jd_skills = set(jd_data.get('requirements', {}).get('skills', []))

        matching_skills = cv_skills.intersection(jd_skills)
        missing_skills = jd_skills - cv_skills

        # Simple scoring based on skill match
        if jd_skills:
            skill_score = (len(matching_skills) / len(jd_skills)) * 100
        else:
            skill_score = 50  # Default if no skills specified

        return {
            "overall_score": round(skill_score, 2),
            "skill_matches": list(matching_skills),
            "skill_gaps": list(missing_skills),
            "experience_match": "Analysis requires LLM",
            "education_match": "Analysis requires LLM",
            "recommendations": ["Consider using AI analysis for detailed insights"],
            "strengths": list(matching_skills),
            "weaknesses": list(missing_skills)
        }

    def swot_analysis(self, cv_data: Dict, jd_data: Dict) -> Dict:
        """
        Perform SWOT analysis for the candidate-job match
        """
        prompt = f"""
        Perform a SWOT analysis for this candidate applying to this job position.

        SWOT Analysis Framework:
        - Strengths: What advantages does the candidate have for this role?
        - Weaknesses: What gaps or weaknesses does the candidate have?
        - Opportunities: What opportunities exist for the candidate in this role?
        - Threats: What potential challenges or risks does the candidate face?

        CV Data:
        {cv_data}

        Job Description Data:
        {jd_data}

        Return as JSON:
        {{
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
            "threats": []
        }}
        """

        try:
            response = self.llm.predict(prompt)
            import json
            swot = json.loads(response)
            return swot
        except Exception as e:
            return {
                "strengths": ["Matching skills identified"],
                "weaknesses": ["Detailed analysis requires LLM"],
                "opportunities": ["Potential for skill development"],
                "threats": ["Competition from other candidates"]
            }

    def gap_analysis(self, cv_data: Dict, jd_data: Dict) -> Dict:
        """
        Perform gap analysis identifying skill and experience gaps
        """
        prompt = f"""
        Perform a gap analysis between the candidate's profile and job requirements.

        Identify:
        1. Skill gaps (required skills the candidate lacks)
        2. Experience gaps (years or type of experience missing)
        3. Knowledge gaps (specific knowledge areas missing)
        4. Certification gaps (required certifications missing)
        5. Development recommendations (how to bridge the gaps)

        CV Data:
        {cv_data}

        Job Description Data:
        {jd_data}

        Return as JSON:
        {{
            "skill_gaps": [],
            "experience_gaps": [],
            "knowledge_gaps": [],
            "certification_gaps": [],
            "development_plan": []
        }}
        """

        try:
            response = self.llm.predict(prompt)
            import json
            gaps = json.loads(response)
            return gaps
        except Exception as e:
            return {
                "skill_gaps": ["Analysis requires LLM"],
                "experience_gaps": ["Analysis requires LLM"],
                "knowledge_gaps": ["Analysis requires LLM"],
                "certification_gaps": ["Analysis requires LLM"],
                "development_plan": ["Consider AI-powered gap analysis"]
            }

    def rank_candidates(self, candidates: List[Dict], jd_data: Dict) -> List[Dict]:
        """
        Rank candidates based on their match scores for a job description
        """
        ranked_candidates = []

        for candidate in candidates:
            # Get detailed analysis
            analysis = self.detailed_matching_analysis(candidate, jd_data)

            candidate_with_score = {
                **candidate,
                "match_score": analysis.get("overall_score", 0),
                "analysis": analysis
            }

            ranked_candidates.append(candidate_with_score)

        # Sort by match score (descending)
        ranked_candidates.sort(key=lambda x: x["match_score"], reverse=True)

        return ranked_candidates

    def store_cv_embedding(self, cv_id: str, cv_text: str, metadata: Dict = None):
        """Store CV embedding in vector database"""
        try:
            embedding = self.embedding_model.encode([cv_text])[0]
            embedding_list = embedding.tolist()

            self.cv_collection.add(
                embeddings=[embedding_list],
                documents=[cv_text],
                ids=[cv_id],
                metadatas=[metadata or {}]
            )
        except Exception as e:
            print(f"Error storing CV embedding: {e}")

    def store_jd_embedding(self, jd_id: str, jd_text: str, metadata: Dict = None):
        """Store JD embedding in vector database"""
        try:
            embedding = self.embedding_model.encode([jd_text])[0]
            embedding_list = embedding.tolist()

            self.jd_collection.add(
                embeddings=[embedding_list],
                documents=[jd_text],
                ids=[jd_id],
                metadatas=[metadata or {}]
            )
        except Exception as e:
            print(f"Error storing JD embedding: {e}")

    def find_similar_cvs(self, jd_text: str, top_k: int = 5) -> List[Dict]:
        """Find most similar CVs for a job description"""
        try:
            query_embedding = self.embedding_model.encode([jd_text])[0]
            query_embedding_list = query_embedding.tolist()

            results = self.cv_collection.query(
                query_embeddings=[query_embedding_list],
                n_results=top_k
            )

            similar_cvs = []
            for i, doc_id in enumerate(results['ids'][0]):
                similar_cvs.append({
                    "cv_id": doc_id,
                    "similarity_score": round(results['distances'][0][i] * 100, 2),
                    "metadata": results['metadatas'][0][i]
                })

            return similar_cvs

        except Exception as e:
            print(f"Error finding similar CVs: {e}")
            return []

    def find_similar_jds(self, cv_text: str, top_k: int = 5) -> List[Dict]:
        """Find most similar job descriptions for a CV"""
        try:
            query_embedding = self.embedding_model.encode([cv_text])[0]
            query_embedding_list = query_embedding.tolist()

            results = self.jd_collection.query(
                query_embeddings=[query_embedding_list],
                n_results=top_k
            )

            similar_jds = []
            for i, doc_id in enumerate(results['ids'][0]):
                similar_jds.append({
                    "jd_id": doc_id,
                    "similarity_score": round(results['distances'][0][i] * 100, 2),
                    "metadata": results['metadatas'][0][i]
                })

            return similar_jds

        except Exception as e:
            print(f"Error finding similar JDs: {e}")
            return []