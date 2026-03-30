"""
AI-powered CV Rewrite Engine for job-specific optimization
"""

import os
from typing import Dict, List, Optional, Tuple
import openai
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
import re


class CVRewriteEngine:
    """AI-powered CV rewriting and optimization engine"""

    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.7, model="gpt-4")  # Use GPT-4 for better rewriting
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200,
            length_function=len
        )

    def rewrite_cv(self, cv_data: Dict, jd_data: Dict,
                   optimization_level: str = "moderate") -> Dict:
        """
        Rewrite CV to better match job description

        Args:
            cv_data: Parsed CV data
            jd_data: Parsed job description data
            optimization_level: "conservative", "moderate", "aggressive"

        Returns:
            Dict with rewritten CV content and optimization details
        """
        # Convert structured data to text for processing
        cv_text = self._cv_data_to_text(cv_data)
        jd_text = self._jd_data_to_text(jd_data)

        # Get optimization strategy based on level
        strategy = self._get_optimization_strategy(optimization_level)

        prompt = f"""
        You are an expert CV optimization specialist. Rewrite this CV to better match the target job description.

        OPTIMIZATION STRATEGY: {strategy}

        TARGET JOB: {jd_data.get('job_title', 'Unknown Position')}
        COMPANY: {jd_data.get('company', 'Unknown Company')}

        REQUIRED SKILLS: {', '.join(jd_data.get('requirements', {}).get('skills', []))}
        KEY RESPONSIBILITIES: {', '.join(jd_data.get('responsibilities', []))}

        ORIGINAL CV:
        {cv_text}

        INSTRUCTIONS:
        1. Optimize the professional summary to highlight relevant experience and skills
        2. Reorder and rephrase work experience to emphasize relevant achievements
        3. Highlight transferable skills that match job requirements
        4. Use industry-specific keywords from the job description
        5. Quantify achievements where possible
        6. Maintain truthfulness - don't fabricate experience
        7. Keep the CV concise and professional

        Return the rewritten CV in a structured format with sections clearly marked.
        """

        try:
            rewritten_cv_text = self.llm.predict(prompt)

            # Parse the rewritten CV back into structured format
            rewritten_data = self._parse_rewritten_cv(rewritten_cv_text, cv_data)

            # Calculate match score improvement
            from .matching_engine import MatchingEngine
            matcher = MatchingEngine()

            original_score = matcher.compute_similarity_score(cv_text, jd_text)
            new_score = matcher.compute_similarity_score(rewritten_cv_text, jd_text)

            return {
                "original_cv": cv_data,
                "rewritten_cv": rewritten_data,
                "rewritten_text": rewritten_cv_text,
                "optimization_details": {
                    "level": optimization_level,
                    "original_score": original_score,
                    "new_score": new_score,
                    "improvement": round(new_score - original_score, 2),
                    "strategy": strategy
                },
                "recommendations": self._generate_rewrite_recommendations(cv_data, jd_data)
            }

        except Exception as e:
            print(f"CV rewriting failed: {e}")
            return {
                "error": str(e),
                "original_cv": cv_data,
                "rewritten_cv": None
            }

    def _cv_data_to_text(self, cv_data: Dict) -> str:
        """Convert structured CV data to readable text"""
        text_parts = []

        # Personal info
        personal = cv_data.get('personal_info', {})
        if personal.get('name'):
            text_parts.append(f"Name: {personal['name']}")
        if personal.get('email'):
            text_parts.append(f"Email: {personal['email']}")

        # Summary
        if cv_data.get('summary'):
            text_parts.append(f"\nPROFESSIONAL SUMMARY:\n{cv_data['summary']}")

        # Experience
        if cv_data.get('experience'):
            text_parts.append("\nWORK EXPERIENCE:")
            for exp in cv_data['experience']:
                text_parts.append(f"- {exp.get('position', '')} at {exp.get('company', '')}")
                text_parts.append(f"  {exp.get('duration', '')}")
                text_parts.append(f"  {exp.get('description', '')}")

        # Education
        if cv_data.get('education'):
            text_parts.append("\nEDUCATION:")
            for edu in cv_data['education']:
                text_parts.append(f"- {edu.get('degree', '')} from {edu.get('institution', '')} ({edu.get('year', '')})")

        # Skills
        if cv_data.get('skills'):
            text_parts.append(f"\nSKILLS: {', '.join(cv_data['skills'])}")

        return '\n'.join(text_parts)

    def _jd_data_to_text(self, jd_data: Dict) -> str:
        """Convert structured JD data to readable text"""
        text_parts = []

        if jd_data.get('job_title'):
            text_parts.append(f"Job Title: {jd_data['job_title']}")

        if jd_data.get('company'):
            text_parts.append(f"Company: {jd_data['company']}")

        if jd_data.get('requirements', {}).get('skills'):
            text_parts.append(f"Required Skills: {', '.join(jd_data['requirements']['skills'])}")

        if jd_data.get('responsibilities'):
            text_parts.append("Key Responsibilities:")
            for resp in jd_data['responsibilities']:
                text_parts.append(f"- {resp}")

        return '\n'.join(text_parts)

    def _get_optimization_strategy(self, level: str) -> str:
        """Get optimization strategy based on level"""
        strategies = {
            "conservative": """
            - Make minimal changes to preserve original voice
            - Only add relevant keywords naturally
            - Focus on reordering existing content
            - Maintain original structure and length
            """,
            "moderate": """
            - Rephrase sections to better highlight relevant experience
            - Add industry keywords strategically
            - Reorder bullet points to emphasize key achievements
            - Slightly expand on relevant experience
            """,
            "aggressive": """
            - Significantly rephrase content for maximum impact
            - Aggressively incorporate job-specific keywords
            - Restructure entire sections for better flow
            - Add quantifiable achievements where possible
            - Optimize for ATS (Applicant Tracking Systems)
            """
        }
        return strategies.get(level, strategies["moderate"])

    def _parse_rewritten_cv(self, rewritten_text: str, original_cv: Dict) -> Dict:
        """Parse rewritten CV text back into structured format"""
        # This is a simplified parser - in production, you'd use more sophisticated NLP
        sections = self._split_into_sections(rewritten_text)

        return {
            "personal_info": original_cv.get('personal_info', {}),
            "summary": sections.get('summary', ''),
            "experience": self._parse_experience_section(sections.get('experience', '')),
            "education": original_cv.get('education', []),
            "skills": self._extract_skills_from_text(sections.get('skills', '')),
            "projects": original_cv.get('projects', [])
        }

    def _split_into_sections(self, text: str) -> Dict[str, str]:
        """Split CV text into sections"""
        sections = {}
        current_section = None
        current_content = []

        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for section headers
            upper_line = line.upper()
            if 'SUMMARY' in upper_line or 'OBJECTIVE' in upper_line:
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = 'summary'
                current_content = []
            elif 'EXPERIENCE' in upper_line or 'WORK' in upper_line:
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = 'experience'
                current_content = []
            elif 'SKILLS' in upper_line:
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = 'skills'
                current_content = []
            else:
                if current_section:
                    current_content.append(line)

        if current_section:
            sections[current_section] = '\n'.join(current_content)

        return sections

    def _parse_experience_section(self, text: str) -> List[Dict]:
        """Parse experience section into structured data"""
        experiences = []
        lines = text.split('\n')

        current_exp = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if this is a job title line
            if not line.startswith('-') and not line.startswith(' ') and len(line) < 100:
                if current_exp:
                    experiences.append(current_exp)

                current_exp = {
                    "position": line,
                    "company": "",
                    "duration": "",
                    "description": ""
                }
            elif current_exp:
                if ' at ' in line or ' @ ' in line:
                    # Extract company
                    parts = re.split(r' at | @ ', line, 1)
                    if len(parts) > 1:
                        current_exp["company"] = parts[1]
                elif any(word in line.lower() for word in ['years', 'months', 'present', 'current']):
                    current_exp["duration"] = line
                else:
                    current_exp["description"] += line + ' '

        if current_exp:
            experiences.append(current_exp)

        return experiences

    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from skills section text"""
        if not text:
            return []

        # Split by common delimiters
        skills = re.split(r'[,\n•\-*]', text)
        skills = [skill.strip() for skill in skills if skill.strip()]

        return skills

    def _generate_rewrite_recommendations(self, cv_data: Dict, jd_data: Dict) -> List[str]:
        """Generate recommendations for CV improvement"""
        recommendations = []

        cv_skills = set(cv_data.get('skills', []))
        jd_skills = set(jd_data.get('requirements', {}).get('skills', []))

        missing_skills = jd_skills - cv_skills
        if missing_skills:
            recommendations.append(f"Consider adding or highlighting these missing skills: {', '.join(missing_skills)}")

        # Check experience level
        jd_exp = jd_data.get('requirements', {}).get('experience_years', '')
        if jd_exp and jd_exp.isdigit():
            required_years = int(jd_exp)
            # This would need more sophisticated experience parsing
            recommendations.append(f"Job requires {required_years}+ years of experience - ensure your experience section reflects this level")

        # Check for quantifiable achievements
        has_quantifiable = any('increased' in str(exp).lower() or '%' in str(exp) or '$' in str(exp)
                             for exp in cv_data.get('experience', []))
        if not has_quantifiable:
            recommendations.append("Add quantifiable achievements (percentages, numbers, metrics) to make your experience more impactful")

        return recommendations

    def optimize_cv_section(self, section_name: str, section_content: str,
                          jd_keywords: List[str]) -> str:
        """
        Optimize a specific CV section with job-specific keywords
        """
        prompt = f"""
        Optimize this CV section to incorporate relevant keywords from the job description.

        SECTION: {section_name}
        ORIGINAL CONTENT:
        {section_content}

        KEYWORDS TO INCORPORATE: {', '.join(jd_keywords)}

        INSTRUCTIONS:
        - Naturally incorporate the keywords where relevant
        - Maintain professional tone and truthfulness
        - Improve clarity and impact
        - Keep similar length

        Return only the optimized section content:
        """

        try:
            optimized = self.llm.predict(prompt)
            return optimized.strip()
        except Exception as e:
            print(f"Section optimization failed: {e}")
            return section_content

    def generate_cover_letter(self, cv_data: Dict, jd_data: Dict) -> str:
        """
        Generate a tailored cover letter based on CV and job description
        """
        prompt = f"""
        Write a professional cover letter for this candidate applying to this position.

        CANDIDATE INFO:
        Name: {cv_data.get('personal_info', {}).get('name', 'Candidate')}
        Summary: {cv_data.get('summary', '')}

        TOP SKILLS: {', '.join(cv_data.get('skills', [])[:5])}

        JOB DETAILS:
        Position: {jd_data.get('job_title', '')}
        Company: {jd_data.get('company', '')}
        Key Requirements: {', '.join(jd_data.get('requirements', {}).get('skills', [])[:3])}

        INSTRUCTIONS:
        - Keep it to 3-4 paragraphs
        - Highlight relevant experience and skills
        - Show enthusiasm for the role and company
        - Professional and concise tone
        - End with a call to action

        Write the cover letter:
        """

        try:
            cover_letter = self.llm.predict(prompt)
            return cover_letter.strip()
        except Exception as e:
            return "Error generating cover letter. Please try again."