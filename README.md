# AI-Powered Recruitment Platform 🚀

An intelligent agentic CV-JD matching suite that revolutionizes recruitment workflows through AI-powered screening, matching, and profile optimization.

## 🌟 Features

### 🤖 Agentic CV Screening Platform
- Multi-role AI agents for comprehensive CV evaluation
- LLM-powered CV-to-JD ranked matching with similarity scores
- Automated SWOT analysis (Strengths, Weaknesses, Opportunities, Threats)
- GAP analysis identifying skill mismatches and development areas

### ✍️ AI-Driven CV Rewrite Engine
- Intelligent CV rewriting targeting specific job descriptions
- Real-time match score tracking during optimization
- Prompt engineering for personalized profile enhancement
- Multi-format CV parsing and processing

### 📄 Multi-Format Ingestion Pipeline
- Job description ingestion from:
  - Web links (URL scraping)
  - Document files (PDF, DOCX, TXT)
  - LinkedIn job posts
  - AI-assisted form input
- Candidate profile parsing from multiple formats
- Automated data extraction and structuring

### 📊 Advanced Analytics Dashboard
- Real-time matching analytics
- Candidate ranking and filtering
- Skill gap visualization
- Recruitment workflow optimization insights

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit
- **AI/ML**: LangChain, OpenAI GPT, Sentence Transformers
- **Document Processing**: PyPDF2, python-docx, BeautifulSoup
- **Vector Database**: ChromaDB / FAISS
- **Data Processing**: Pandas, NumPy
- **Charts**: Plotly

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key
- pip

### Installation

1. **Clone/Update the repository**
   ```bash
   cd ai-evaluation-engine
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

4. **Run the application**
   ```bash
   # Backend
   cd backend
   uvicorn main:app --reload

   # Dashboard (in new terminal)
   cd Dashboard
   streamlit run app.py
   ```

## 📋 API Endpoints

- `POST /upload-cv` - Upload and parse candidate CV
- `POST /upload-jd` - Upload and parse job description
- `POST /match-cv-jd` - Perform CV-JD matching with analysis
- `POST /rewrite-cv` - AI-powered CV rewriting
- `GET /analytics` - Get matching analytics

## 🤖 Agent Architecture

The platform uses multiple specialized AI agents:

1. **Screening Agent**: Initial CV qualification
2. **Matching Agent**: Semantic similarity analysis
3. **Analysis Agent**: SWOT and GAP analysis
4. **Rewrite Agent**: CV optimization and enhancement
5. **Ingestion Agent**: Multi-format data processing
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

## 📊 Sample Data Format

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

## 🎯 Usage Examples

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

## 🔒 Security Features

- **Code Execution**: Sandboxed in temporary directories with timeout
- **Input Validation**: All API inputs validated
- **Error Handling**: Graceful error responses
- **Rate Limiting**: Built-in FastAPI rate limiting

## 📈 Dashboard Features

- **Overview Tab**: Performance metrics and charts
- **Concept Analysis**: Topic-wise performance breakdown
- **Question Details**: Individual question review with filtering
- **Short Answer AI**: Real-time AI evaluation
- **Code Evaluator**: Code execution and scoring
- **Batch CSV**: Upload and evaluate multiple answers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ for educational assessment automation
- Inspired by the need for fair and efficient evaluation systems

## 📞 Support

For questions or issues, please open an issue on GitHub or contact the maintainers.

---

**Made with ❤️ using FastAPI, Streamlit, and Python**