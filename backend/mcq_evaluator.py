import pandas as pd

def evaluate_mcq(file_path):
    df = pd.read_csv(file_path, sep='\t')

    # Check correctness
    df["is_correct"] = df["correct_answer"] == df["student_answer"]

    # Total score
    total_questions = len(df)
    score = df["is_correct"].sum()
    accuracy = score / total_questions

    # Concept-wise performance
    concept_analysis = df.groupby("concept")["is_correct"].mean()

    # Individual question results
    questions_data = []
    for _, row in df.iterrows():
        questions_data.append({
            "student_id": int(row["student_id"]),
            "question": row["question"],
            "correct_answer": row["correct_answer"],
            "student_answer": row["student_answer"],
            "concept": row["concept"],
            "is_correct": bool(row["is_correct"])
        })

    return {
        "total_questions": total_questions,
        "score": int(score),
        "accuracy": round(float(accuracy), 2),
        "concept_analysis": concept_analysis.to_dict(),
        "questions": questions_data
    }


def _normalize_text(text):
    import re
    text = str(text).strip().lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def evaluate_short_answer(student_answer, model_answer):
    from difflib import SequenceMatcher

    student_norm = _normalize_text(student_answer)
    model_norm = _normalize_text(model_answer)

    if len(student_norm) == 0 or len(model_norm) == 0:
        return {
            "score": 0,
            "accuracy": 0.0,
            "feedback": "Student or model answer is empty, please provide valid text.",
            "similarity": 0.0
        }

    ratio = SequenceMatcher(a=student_norm, b=model_norm).ratio()
    score_percent = int(round(ratio * 100))

    notes = []

    student_words = set(student_norm.split())
    model_words = set(model_norm.split())

    missing_words = model_words - student_words
    extra_words = student_words - model_words

    if missing_words:
        short = sorted(list(missing_words))[:6]
        notes.append(f"Consider adding key terms: {', '.join(short)}")
    if extra_words and len(extra_words) > 10:
        notes.append("Your answer contains several unrelated words; try focusing on the main points.")

    if ratio > 0.90:
        feedback = "Excellent answer! Very close to the model answer."
    elif ratio > 0.75:
        feedback = "Good answer; mostly correct but can improve with a couple of details."
    elif ratio > 0.50:
        feedback = "Fair answer; key points are missing or phrasing differs significantly."
    else:
        feedback = "Needs improvement; your answer misses core points from the model answer."

    if notes:
        feedback = f"{feedback} " + " ".join(notes)

    return {
        "score": score_percent,
        "accuracy": round(ratio, 2),
        "feedback": feedback,
        "similarity": round(ratio, 4),
        "student_answer": student_answer,
        "model_answer": model_answer
    }


def evaluate_code(student_code, test_input='', expected_output='', timeout_seconds=5):
    import os, tempfile, subprocess, textwrap
    from difflib import SequenceMatcher

    if not student_code.strip():
        return {
            "score": 0,
            "feedback": "No code submitted.",
            "actual_output": "",
            "expected_output": expected_output,
            "error": "student_code_empty",
            "details": "Student code cannot be empty."
        }

    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, 'student_solution.py')

        # Score only Python for now
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(textwrap.dedent(student_code))

        try:
            proc = subprocess.run(
                ["python", file_path],
                input=test_input.encode('utf-8'),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout_seconds,
                check=False
            )

            actual_output = proc.stdout.decode('utf-8').strip()
            stderr_output = proc.stderr.decode('utf-8').strip()

            if proc.returncode != 0:
                return {
                    "score": 0,
                    "feedback": "Code execution failed with error.",
                    "actual_output": actual_output,
                    "expected_output": expected_output,
                    "error": "runtime_error",
                    "details": stderr_output
                }

            expected_clean = expected_output.strip()
            actual_clean = actual_output.strip()

            if expected_clean == '':
                similarity = 1.0 if actual_clean == '' else 0.0
            else:
                similarity = SequenceMatcher(a=actual_clean, b=expected_clean).ratio()

            score_percent = int(round(similarity * 100))

            if similarity == 1.0:
                feedback = "Great job! Output is exactly correct."
            elif similarity >= 0.8:
                feedback = "Almost correct; output is close to expected. Check formatting/spacing."
            elif similarity >= 0.5:
                feedback = "Partially correct; output differs significantly. Review logic and edge cases."
            else:
                feedback = "Incorrect output; needs debugging against expected result."

            return {
                "score": score_percent,
                "feedback": feedback,
                "actual_output": actual_clean,
                "expected_output": expected_clean,
                "similarity": round(similarity, 4),
                "error": None,
                "stderr": stderr_output
            }

        except subprocess.TimeoutExpired:
            return {
                "score": 0,
                "feedback": "Code execution timed out. Optimize your solution and avoid infinite loops.",
                "actual_output": "",
                "expected_output": expected_output,
                "error": "timeout",
                "details": f"Execution exceeded {timeout_seconds} seconds."
            }
        except Exception as ex:
            return {
                "score": 0,
                "feedback": "Error while evaluating code.",
                "actual_output": "",
                "expected_output": expected_output,
                "error": "internal_error",
                "details": str(ex)
            }
