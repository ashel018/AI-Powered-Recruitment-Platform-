from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mcq_evaluator import evaluate_mcq, evaluate_short_answer, evaluate_code

app = FastAPI()

class ShortAnswerPayload(BaseModel):
    student_answer: str
    model_answer: str

class CodeEvaluationPayload(BaseModel):
    student_code: str
    test_input: str = ""
    expected_output: str = ""
    timeout_seconds: int = 5

@app.get("/")
def home():
    return {"message": "AI Evaluation Engine Running 🚀"}

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


@app.get("/evaluate_short")
def evaluate_short_get(student_answer: str, model_answer: str):
    if not student_answer.strip() or not model_answer.strip():
        raise HTTPException(status_code=400, detail="Both student_answer and model_answer are required")

    result = evaluate_short_answer(student_answer, model_answer)
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