from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, Dict, List
import os
import tempfile
import json
from datetime import datetime

# Import recruitment modules
from recruitment.document_parser import CVParser, JDParser
from recruitment.matching_engine import MatchingEngine
from recruitment.cv_rewrite_engine import CVRewriteEngine
from recruitment.agent_system import CoordinatorAgent

app = FastAPI(title="AI-Powered Recruitment Platform", version="1.0.0")

# Initialize components
cv_parser = CVParser()
jd_parser = JDParser()
matching_engine = MatchingEngine()
cv_rewrite_engine = CVRewriteEngine()
coordinator_agent = CoordinatorAgent()

# Pydantic models
class CVUploadResponse(BaseModel):
    success: bool
    cv_data: Dict
    message: str

class JDUploadResponse(BaseModel):
    success: bool
    jd_data: Dict
    message: str

class MatchRequest(BaseModel):
    cv_id: str
    jd_id: str

class MatchResponse(BaseModel):
    match_score: float
    analysis: Dict
    swot_analysis: Dict
    gap_analysis: Dict
    recommendations: List[str]

class RewriteRequest(BaseModel):
    cv_data: Dict
    jd_data: Dict
    optimization_level: Optional[str] = "moderate"

class RewriteResponse(BaseModel):
    original_cv: Dict
    rewritten_cv: Dict
    rewritten_text: str
    optimization_details: Dict
    recommendations: List[str]

# In-memory storage (in production, use database)
cv_storage = {}
jd_storage = {}
match_results = {}

@app.get("/")
def home():
    return {
        "message": "AI-Powered Recruitment Platform 🚀",
        "version": "1.0.0",
        "endpoints": [
            "/upload-cv", "/upload-jd", "/match-cv-jd",
            "/rewrite-cv", "/analytics", "/health"
        ]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/upload-cv", response_model=CVUploadResponse)
async def upload_cv(
    file: UploadFile = File(...),
    source_type: str = Form("file")
):
    """Upload and parse CV document"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Parse CV
        cv_data = cv_parser.parse_cv(temp_file_path)

        # Generate CV ID
        cv_id = f"cv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Store CV data
        cv_storage[cv_id] = {
            "data": cv_data,
            "filename": file.filename,
            "upload_time": datetime.now().isoformat()
        }

        # Clean up temp file
        os.unlink(temp_file_path)

        return CVUploadResponse(
            success=True,
            cv_data=cv_data,
            message=f"CV uploaded and parsed successfully. ID: {cv_id}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CV upload failed: {str(e)}")

@app.post("/upload-jd", response_model=JDUploadResponse)
async def upload_jd(
    source: str = Form(...),
    source_type: str = Form("file"),  # file, url, text
    file: Optional[UploadFile] = File(None)
):
    """Upload and parse job description"""
    try:
        if source_type == "file" and file:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            jd_data = jd_parser.parse_jd(temp_file_path, source_type)
            os.unlink(temp_file_path)
        else:
            # Handle URL or text input
            jd_data = jd_parser.parse_jd(source, source_type)

        # Generate JD ID
        jd_id = f"jd_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Store JD data
        jd_storage[jd_id] = {
            "data": jd_data,
            "source": source,
            "source_type": source_type,
            "upload_time": datetime.now().isoformat()
        }

        return JDUploadResponse(
            success=True,
            jd_data=jd_data,
            message=f"Job description processed successfully. ID: {jd_id}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JD upload failed: {str(e)}")

@app.post("/match-cv-jd", response_model=MatchResponse)
def match_cv_jd(request: MatchRequest):
    """Perform CV-JD matching with analysis"""
    try:
        # Retrieve stored data
        cv_data = cv_storage.get(request.cv_id)
        jd_data = jd_storage.get(request.jd_id)

        if not cv_data or not jd_data:
            raise HTTPException(status_code=404, detail="CV or JD not found")

        cv_content = cv_data["data"]
        jd_content = jd_data["data"]

        # Perform matching analysis
        analysis = matching_engine.detailed_matching_analysis(cv_content, jd_content)
        swot = matching_engine.swot_analysis(cv_content, jd_content)
        gap = matching_engine.gap_analysis(cv_content, jd_content)

        # Compute similarity score
        cv_text = json.dumps(cv_content)
        jd_text = json.dumps(jd_content)
        match_score = matching_engine.compute_similarity_score(cv_text, jd_text)

        # Store results
        match_id = f"match_{request.cv_id}_{request.jd_id}"
        match_results[match_id] = {
            "cv_id": request.cv_id,
            "jd_id": request.jd_id,
            "match_score": match_score,
            "analysis": analysis,
            "swot": swot,
            "gap": gap,
            "timestamp": datetime.now().isoformat()
        }

        return MatchResponse(
            match_score=match_score,
            analysis=analysis,
            swot_analysis=swot,
            gap_analysis=gap,
            recommendations=analysis.get("recommendations", [])
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Matching failed: {str(e)}")

@app.post("/rewrite-cv", response_model=RewriteResponse)
def rewrite_cv(request: RewriteRequest):
    """AI-powered CV rewriting for job optimization"""
    try:
        result = cv_rewrite_engine.rewrite_cv(
            request.cv_data,
            request.jd_data,
            request.optimization_level
        )

        return RewriteResponse(**result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CV rewrite failed: {str(e)}")

@app.get("/analytics")
def get_analytics():
    """Get recruitment analytics"""
    try:
        total_cvs = len(cv_storage)
        total_jds = len(jd_storage)
        total_matches = len(match_results)

        # Calculate average match scores
        if match_results:
            scores = [result["match_score"] for result in match_results.values()]
            avg_score = sum(scores) / len(scores)
            max_score = max(scores)
            min_score = min(scores)
        else:
            avg_score = max_score = min_score = 0

        return {
            "total_cvs": total_cvs,
            "total_jds": total_jds,
            "total_matches": total_matches,
            "average_match_score": round(avg_score, 2),
            "highest_match_score": round(max_score, 2),
            "lowest_match_score": round(min_score, 2),
            "recent_matches": list(match_results.keys())[-5:] if match_results else []
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics retrieval failed: {str(e)}")

@app.post("/full-workflow")
def run_full_workflow(
    cv_file: UploadFile = File(...),
    jd_file: UploadFile = File(...),
    optimize_cv: bool = Form(False),
    optimization_level: str = Form("moderate")
):
    """Run complete recruitment workflow"""
    try:
        # Upload and parse CV
        cv_response = await upload_cv(cv_file, "file")
        cv_id = cv_response.message.split("ID: ")[1]

        # Upload and parse JD
        jd_response = await upload_jd(
            source=jd_file.filename,
            source_type="file",
            file=jd_file
        )
        jd_id = jd_response.message.split("ID: ")[1]

        # Perform matching
        match_request = MatchRequest(cv_id=cv_id, jd_id=jd_id)
        match_response = match_cv_jd(match_request)

        result = {
            "cv_id": cv_id,
            "jd_id": jd_id,
            "matching": match_response.dict(),
            "workflow_completed": True
        }

        # Optional CV optimization
        if optimize_cv:
            rewrite_request = RewriteRequest(
                cv_data=cv_response.cv_data,
                jd_data=jd_response.jd_data,
                optimization_level=optimization_level
            )
            rewrite_response = rewrite_cv(rewrite_request)
            result["cv_optimization"] = rewrite_response.dict()

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow failed: {str(e)}")

@app.get("/stored-data")
def get_stored_data():
    """Get overview of stored CVs and JDs (for debugging)"""
    return {
        "cvs": {k: {"filename": v["filename"], "upload_time": v["upload_time"]}
                for k, v in cv_storage.items()},
        "jds": {k: {"source": v["source"], "upload_time": v["upload_time"]}
                for k, v in jd_storage.items()},
        "matches": list(match_results.keys())
    }

# Legacy evaluation endpoints (keeping for compatibility)
from mcq_evaluator import evaluate_mcq, evaluate_short_answer, evaluate_code

class ShortAnswerPayload(BaseModel):
    student_answer: str
    model_answer: str

class CodeEvaluationPayload(BaseModel):
    student_code: str
    test_input: str = ""
    expected_output: str = ""
    timeout_seconds: int = 5

@app.get("/evaluate")
def evaluate():
    result = evaluate_mcq("C:/Users/Acer/OneDrive/Desktop/AI-EVALUATION-ENGINE/Data/sample_mcq.csv")
    return result

@app.post("/evaluate_short")
def evaluate_short(payload: ShortAnswerPayload):
    if not payload.student_answer or not payload.model_answer:
        raise HTTPException(status_code=400, detail="Both student_answer and model_answer are required")

    result = evaluate_short_answer(payload.student_answer, payload.model_answer)
    return result

@app.post("/evaluate_code")
def evaluate_code_endpoint(payload: CodeEvaluationPayload):
    if not payload.student_code.strip():
        raise HTTPException(status_code=400, detail="student_code is required")

    result = evaluate_code(
        payload.student_code,
        test_input=payload.test_input,
        expected_output=payload.expected_output,
        timeout_seconds=payload.timeout_seconds
    )
    return result


@app.get("/evaluate_code")
def evaluate_code_get(student_code: str, test_input: str = "", expected_output: str = "", timeout_seconds: int = 5):
    if not student_code.strip():
        raise HTTPException(status_code=400, detail="student_code is required")

    result = evaluate_code(
        student_code,
        test_input=test_input,
        expected_output=expected_output,
        timeout_seconds=timeout_seconds
    )
    return result