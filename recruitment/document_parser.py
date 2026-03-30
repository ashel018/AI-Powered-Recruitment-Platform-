"""
Document Parsers for CV and Job Description Processing
"""

import os
import re
from typing import Dict, List, Optional, Tuple
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import PyPDF2
from docx import Document
import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI


class DocumentParser:
    """Base class for document parsing"""

    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )

    def extract_text(self, file_path: str) -> str:
        """Extract text from various file formats"""
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == '.pdf':
            return self._extract_pdf_text(file_path)
        elif file_extension in ['.docx', '.doc']:
            return self._extract_docx_text(file_path)
        elif file_extension == '.txt':
            return self._extract_txt_text(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF files"""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text

    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX files"""
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

    def _extract_txt_text(self, file_path: str) -> str:
        """Extract text from TXT files"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()


class WebScraper:
    """Web scraping for job descriptions"""

    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")

    def scrape_job_description(self, url: str) -> str:
        """Scrape job description from URL"""
        try:
            # Try with requests first (faster)
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()

            # Try to find job description content
            jd_content = self._extract_jd_content(soup)
            return jd_content

        except Exception as e:
            print(f"Requests scraping failed, trying Selenium: {e}")
            return self._scrape_with_selenium(url)

    def _scrape_with_selenium(self, url: str) -> str:
        """Fallback scraping with Selenium"""
        driver = webdriver.Chrome(
            ChromeDriverManager().install(),
            options=self.chrome_options
        )

        try:
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            return self._extract_jd_content(soup)
        finally:
            driver.quit()

    def _extract_jd_content(self, soup: BeautifulSoup) -> str:
        """Extract job description content from HTML"""
        # Common selectors for job descriptions
        selectors = [
            '.job-description',
            '.job-detail',
            '.description',
            '[data-testid="job-description"]',
            '.jobsearch-JobMetadataHeader-item',
            '.jobs-description',
            'div[data-jobsdb-job-description]'
        ]

        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)

        # Fallback: get all paragraph text
        paragraphs = soup.find_all('p')
        content = ' '.join([p.get_text(strip=True) for p in paragraphs])

        if len(content) < 100:  # If too short, get more content
            content = soup.get_text(strip=True)

        return content


class CVParser(DocumentParser):
    """Specialized parser for CV/resume documents"""

    def __init__(self):
        super().__init__()
        self.llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")

    def parse_cv(self, file_path: str) -> Dict:
        """Parse CV and extract structured information"""
        raw_text = self.extract_text(file_path)

        # Use LLM to extract structured data
        prompt = f"""
        Extract the following information from this CV/resume text. Return as JSON:

        {{
            "personal_info": {{
                "name": "",
                "email": "",
                "phone": "",
                "location": "",
                "linkedin": "",
                "github": ""
            }},
            "summary": "",
            "experience": [
                {{
                    "company": "",
                    "position": "",
                    "duration": "",
                    "description": ""
                }}
            ],
            "education": [
                {{
                    "institution": "",
                    "degree": "",
                    "year": ""
                }}
            ],
            "skills": [],
            "certifications": [],
            "projects": [
                {{
                    "name": "",
                    "description": "",
                    "technologies": []
                }}
            ]
        }}

        CV Text:
        {raw_text[:4000]}  # Limit text length
        """

        try:
            response = self.llm.predict(prompt)
            # Parse JSON response
            import json
            parsed_data = json.loads(response)
            return parsed_data
        except Exception as e:
            print(f"LLM parsing failed: {e}")
            return self._fallback_parse(raw_text)

    def _fallback_parse(self, text: str) -> Dict:
        """Fallback parsing using regex patterns"""
        return {
            "personal_info": self._extract_personal_info(text),
            "summary": self._extract_summary(text),
            "experience": self._extract_experience(text),
            "education": self._extract_education(text),
            "skills": self._extract_skills(text),
            "certifications": [],
            "projects": []
        }

    def _extract_personal_info(self, text: str) -> Dict:
        """Extract personal information using regex"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'

        email = re.search(email_pattern, text)
        phone = re.search(phone_pattern, text)

        return {
            "name": "",  # Would need more sophisticated NLP
            "email": email.group(0) if email else "",
            "phone": phone.group(0) if phone else "",
            "location": "",
            "linkedin": "",
            "github": ""
        }

    def _extract_summary(self, text: str) -> str:
        """Extract professional summary"""
        # Look for common summary keywords
        summary_keywords = ['summary', 'objective', 'profile', 'about']
        lines = text.split('\n')

        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in summary_keywords):
                # Get next few lines as summary
                start = i + 1
                summary_lines = []
                for j in range(start, min(start + 5, len(lines))):
                    if lines[j].strip():
                        summary_lines.append(lines[j].strip())
                    else:
                        break
                return ' '.join(summary_lines)

        return ""

    def _extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience"""
        # Simple pattern matching for experience section
        experience = []
        lines = text.split('\n')

        exp_start = -1
        for i, line in enumerate(lines):
            if 'experience' in line.lower() or 'work history' in line.lower():
                exp_start = i + 1
                break

        if exp_start > 0:
            # Extract next few relevant lines
            for i in range(exp_start, min(exp_start + 20, len(lines))):
                line = lines[i].strip()
                if line and len(line) > 10:  # Filter out short/irrelevant lines
                    experience.append({
                        "company": "",
                        "position": line,
                        "duration": "",
                        "description": ""
                    })

        return experience

    def _extract_education(self, text: str) -> List[Dict]:
        """Extract education information"""
        education = []
        lines = text.split('\n')

        edu_start = -1
        for i, line in enumerate(lines):
            if 'education' in line.lower():
                edu_start = i + 1
                break

        if edu_start > 0:
            for i in range(edu_start, min(edu_start + 10, len(lines))):
                line = lines[i].strip()
                if line and len(line) > 5:
                    education.append({
                        "institution": line,
                        "degree": "",
                        "year": ""
                    })

        return education

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills using keyword matching"""
        common_skills = [
            'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go',
            'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring',
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git',
            'machine learning', 'ai', 'data science', 'tensorflow', 'pytorch'
        ]

        found_skills = []
        text_lower = text.lower()

        for skill in common_skills:
            if skill in text_lower:
                found_skills.append(skill.title())

        return found_skills


class JDParser(DocumentParser):
    """Specialized parser for Job Descriptions"""

    def __init__(self):
        super().__init__()
        self.llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
        self.web_scraper = WebScraper()

    def parse_jd(self, source: str, source_type: str = 'file') -> Dict:
        """
        Parse job description from various sources
        source_type: 'file', 'url', 'text'
        """
        if source_type == 'file':
            raw_text = self.extract_text(source)
        elif source_type == 'url':
            raw_text = self.web_scraper.scrape_job_description(source)
        elif source_type == 'text':
            raw_text = source
        else:
            raise ValueError(f"Unsupported source type: {source_type}")

        return self._parse_jd_text(raw_text)

    def _parse_jd_text(self, text: str) -> Dict:
        """Parse JD text using LLM"""
        prompt = f"""
        Extract the following information from this job description. Return as JSON:

        {{
            "job_title": "",
            "company": "",
            "location": "",
            "employment_type": "",
            "salary_range": "",
            "requirements": {{
                "experience_years": "",
                "education": "",
                "skills": [],
                "certifications": []
            }},
            "responsibilities": [],
            "benefits": [],
            "company_description": "",
            "application_deadline": ""
        }}

        Job Description Text:
        {text[:4000]}
        """

        try:
            response = self.llm.predict(prompt)
            import json
            parsed_data = json.loads(response)
            return parsed_data
        except Exception as e:
            print(f"LLM parsing failed: {e}")
            return self._fallback_jd_parse(text)

    def _fallback_jd_parse(self, text: str) -> Dict:
        """Fallback JD parsing"""
        return {
            "job_title": self._extract_job_title(text),
            "company": "",
            "location": "",
            "employment_type": "",
            "salary_range": "",
            "requirements": {
                "experience_years": "",
                "education": "",
                "skills": self._extract_jd_skills(text),
                "certifications": []
            },
            "responsibilities": self._extract_responsibilities(text),
            "benefits": [],
            "company_description": "",
            "application_deadline": ""
        }

    def _extract_job_title(self, text: str) -> str:
        """Extract job title from JD"""
        lines = text.split('\n')
        for line in lines[:5]:  # Check first few lines
            line = line.strip()
            if line and len(line) < 100 and not any(word in line.lower() for word in ['company', 'location', 'salary']):
                return line
        return "Unknown Position"

    def _extract_jd_skills(self, text: str) -> List[str]:
        """Extract required skills from JD"""
        # Similar to CV skills extraction but focused on requirements
        common_skills = [
            'python', 'java', 'javascript', 'leadership', 'communication',
            'project management', 'agile', 'scrum', 'aws', 'cloud'
        ]

        found_skills = []
        text_lower = text.lower()

        for skill in common_skills:
            if skill in text_lower:
                found_skills.append(skill.title())

        return found_skills

    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract job responsibilities"""
        responsibilities = []
        lines = text.split('\n')

        resp_start = -1
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in ['responsibilities', 'duties', 'role']):
                resp_start = i + 1
                break

        if resp_start > 0:
            for i in range(resp_start, min(resp_start + 15, len(lines))):
                line = lines[i].strip()
                if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                    responsibilities.append(line[1:].strip())

        return responsibilities