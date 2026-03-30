# AI Evaluation Engine 

A comprehensive AI-powered evaluation system for educational assessments, featuring multiple-choice questions (MCQ), short answer evaluation, and code execution testing.

##  Features

###  MCQ Evaluation
- Automated grading of multiple-choice questions
- Performance analytics by concept/topic
- Individual question analysis
- Accuracy metrics and insights

###  AI Short Answer Evaluation
- Semantic similarity analysis
- Automated scoring (0-100)
- Intelligent feedback generation
- Key term detection and suggestions

###  Code Execution Evaluator
- Safe Python code execution in sandboxed environment
- Output comparison with expected results
- Timeout protection and error handling
- Similarity-based scoring

###  Interactive Dashboard
- Real-time performance metrics
- Concept-wise analysis charts
- Batch CSV upload and evaluation
- Professional UI with Streamlit

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit
- **Data Processing**: Pandas
- **Charts**: Plotly
- **AI/ML**: difflib (semantic similarity)

##  Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-evaluation-engine.git
   cd ai-evaluation-engine
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the backend server**
   ```bash
   cd backend
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

4. **Start the dashboard (in a new terminal)**
   ```bash
   cd ../Dashboard
   streamlit run app.py
   ```

5. **Open your browser**
   - Dashboard: `http://localhost:8501`
   - API Docs: `http://127.0.0.1:8000/docs`

## 📁 Project Structure

```
ai-evaluation-engine/
├── backend/
│   ├── main.py              # FastAPI server and endpoints
│   └── mcq_evaluator.py     # Core evaluation logic
├── Dashboard/
│   └── app.py               # Streamlit dashboard
├── Data/
│   └── sample_mcq.csv       # Sample MCQ data
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔧 API Endpoints

### MCQ Evaluation
- `GET /evaluate` - Evaluate MCQ data from CSV

### Short Answer Evaluation
- `POST /evaluate_short` - Evaluate short answer
- `GET /evaluate_short` - Browser-friendly short answer evaluation

### Code Evaluation
- `POST /evaluate_code` - Evaluate Python code execution
- `GET /evaluate_code` - Browser-friendly code evaluation

##  Sample Data Format

### MCQ CSV Format
```csv
student_id	question	correct_answer	student_answer	concept
1	What is 2+2?	4	4	Math Basics
2	Capital of India?	Delhi	Mumbai	Geography
```

### Short Answer Evaluation
```json
{
  "student_answer": "Water is H2O.",
  "model_answer": "Water has chemical formula H2O."
}
```

### Code Evaluation
```json
{
  "student_code": "print(int(input())*2)",
  "test_input": "3",
  "expected_output": "6",
  "timeout_seconds": 5
}
```

##  Usage Examples

### Evaluate Short Answer
```bash
curl -X POST http://127.0.0.1:8000/evaluate_short \
  -H "Content-Type: application/json" \
  -d '{"student_answer":"Water is H2O","model_answer":"Water has chemical formula H2O"}'
```

### Evaluate Code
```bash
curl -X POST http://127.0.0.1:8000/evaluate_code \
  -H "Content-Type: application/json" \
  -d '{"student_code":"print(int(input())*2)","test_input":"3","expected_output":"6"}'
```

##  Security Features

- **Code Execution**: Sandboxed in temporary directories with timeout
- **Input Validation**: All API inputs validated
- **Error Handling**: Graceful error responses
- **Rate Limiting**: Built-in FastAPI rate limiting

##  Dashboard Features

- **Overview Tab**: Performance metrics and charts
- **Concept Analysis**: Topic-wise performance breakdown
- **Question Details**: Individual question review with filtering
- **Short Answer AI**: Real-time AI evaluation
- **Code Evaluator**: Code execution and scoring
- **Batch CSV**: Upload and evaluate multiple answers

##  Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
