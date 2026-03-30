import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AI Evaluation Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .correct-answer {
        color: #28a745;
        font-weight: bold;
    }
    .wrong-answer {
        color: #dc3545;
        font-weight: bold;
    }
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🎯 AI Evaluation Engine")
st.sidebar.markdown("---")

# Refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 Dashboard Features")
st.sidebar.markdown("- Overall Performance Metrics")
st.sidebar.markdown("- Concept-wise Analysis")
st.sidebar.markdown("- Individual Question Review")
st.sidebar.markdown("- Interactive Charts")

# Main title
st.markdown('<h1 class="main-header">📊 AI Evaluation Dashboard</h1>', unsafe_allow_html=True)

# Function to fetch data from backend with local CSV fallback
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_evaluation_data():
    try:
        response = requests.get("http://127.0.0.1:8000/evaluate", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Backend returned status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.warning(f"Failed to connect to backend: {str(e)}")
        st.info("💡 Backend not running on port 8000; falling back to local data source.")

        # Local fallback path
        try:
            local_df = pd.read_csv("../Data/sample_mcq.csv", sep="\t")
            local_df["is_correct"] = local_df["correct_answer"] == local_df["student_answer"]
            total_q = len(local_df)
            score = int(local_df["is_correct"].sum())
            accuracy = round(float(score / total_q), 2) if total_q > 0 else 0.0
            concept_analysis = local_df.groupby("concept")["is_correct"].mean().to_dict()
            questions = local_df.to_dict(orient="records")
            return {
                "total_questions": total_q,
                "score": score,
                "accuracy": accuracy,
                "concept_analysis": concept_analysis,
                "questions": questions
            }
        except Exception as local_err:
            st.error(f"Local fallback failed: {local_err}")
            return None

# Fetch data
data = get_evaluation_data()

if data:
    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Overview", "📚 Concept Analysis", "❓ Question Details", "🧠 Short Answer AI", "💻 Code Evaluator", "🗃️ Batch CSV"])

    with tab1:
        st.header("Overall Performance")

        # Metrics in columns
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>Total Questions</h3>
                <h2 style="color: #1f77b4;">{}</h2>
            </div>
            """.format(data['total_questions']), unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>Correct Answers</h3>
                <h2 style="color: #28a745;">{}</h2>
            </div>
            """.format(data['score']), unsafe_allow_html=True)

        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3>Wrong Answers</h3>
                <h2 style="color: #dc3545;">{}</h2>
            </div>
            """.format(data['total_questions'] - data['score']), unsafe_allow_html=True)

        with col4:
            accuracy_percentage = data['accuracy'] * 100
            st.markdown("""
            <div class="metric-card">
                <h3>Accuracy</h3>
                <h2 style="color: #ff7f0e;">{:.1f}%</h2>
            </div>
            """.format(accuracy_percentage), unsafe_allow_html=True)

        # Progress bar
        st.markdown("### Accuracy Progress")
        st.progress(data['accuracy'])
        st.markdown(f"**{accuracy_percentage:.1f}%** of questions answered correctly")

        # Pie chart for correct/wrong
        fig_pie = go.Figure(data=[go.Pie(
            labels=['Correct', 'Incorrect'],
            values=[data['score'], data['total_questions'] - data['score']],
            marker_colors=['#28a745', '#dc3545'],
            textinfo='label+percent',
            title="Answer Distribution"
        )])
        fig_pie.update_layout(showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    with tab2:
        st.header("Concept-wise Analysis")

        if data['concept_analysis']:
            # Convert to DataFrame for better display
            concept_df = pd.DataFrame({
                'Concept': list(data['concept_analysis'].keys()),
                'Accuracy': [v * 100 for v in data['concept_analysis'].values()]
            })

            # Bar chart
            fig_bar = px.bar(
                concept_df,
                x='Concept',
                y='Accuracy',
                title='Accuracy by Concept',
                color='Accuracy',
                color_continuous_scale='RdYlGn'
            )
            fig_bar.update_layout(yaxis_title="Accuracy (%)")
            st.plotly_chart(fig_bar, use_container_width=True)

            # Table
            st.markdown("### Detailed Concept Performance")
            st.dataframe(
                concept_df.style.format({'Accuracy': '{:.1f}%'}),
                use_container_width=True
            )

            # Best and worst performing concepts
            best_concept = concept_df.loc[concept_df['Accuracy'].idxmax()]
            worst_concept = concept_df.loc[concept_df['Accuracy'].idxmin()]

            col1, col2 = st.columns(2)
            with col1:
                st.success(f"🏆 Best Performance: {best_concept['Concept']} ({best_concept['Accuracy']:.1f}%)")
            with col2:
                st.error(f"📉 Needs Improvement: {worst_concept['Concept']} ({worst_concept['Accuracy']:.1f}%)")
        else:
            st.info("No concept data available")

    with tab3:
        st.header("Individual Question Analysis")

        if data['questions']:
            # Convert to DataFrame
            questions_df = pd.DataFrame(data['questions'])

            # Filters
            col1, col2 = st.columns(2)
            with col1:
                concept_filter = st.multiselect(
                    "Filter by Concept",
                    options=sorted(questions_df['concept'].unique()),
                    default=sorted(questions_df['concept'].unique())
                )
            with col2:
                status_filter = st.multiselect(
                    "Filter by Status",
                    options=['Correct', 'Incorrect'],
                    default=['Correct', 'Incorrect']
                )

            # Apply filters
            filtered_df = questions_df[questions_df['concept'].isin(concept_filter)]

            if 'Correct' in status_filter and 'Incorrect' not in status_filter:
                filtered_df = filtered_df[filtered_df['is_correct'] == True]
            elif 'Incorrect' in status_filter and 'Correct' not in status_filter:
                filtered_df = filtered_df[filtered_df['is_correct'] == False]

            # Display questions
            st.markdown(f"### Showing {len(filtered_df)} questions")

            for idx, row in filtered_df.iterrows():
                with st.expander(f"Question {row['student_id']}: {row['question'][:50]}..."):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**Question:**")
                        st.write(row['question'])

                        st.markdown("**Concept:**")
                        st.write(row['concept'])

                    with col2:
                        st.markdown("**Correct Answer:**")
                        st.markdown(f"<span class='correct-answer'>{row['correct_answer']}</span>", unsafe_allow_html=True)

                        st.markdown("**Student Answer:**")
                        if row['is_correct']:
                            st.markdown(f"<span class='correct-answer'>✓ {row['student_answer']}</span>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<span class='wrong-answer'>✗ {row['student_answer']}</span>", unsafe_allow_html=True)

                        st.markdown("**Status:**")
                        if row['is_correct']:
                            st.success("Correct")
                        else:
                            st.error("Incorrect")

                    if not row['is_correct']:
                        st.info("💡 The student provided an incorrect answer.")

            # Summary statistics for filtered data
            st.markdown("---")
            st.markdown("### Filtered Results Summary")

            correct_count = filtered_df['is_correct'].sum()
            total_filtered = len(filtered_df)

            if total_filtered > 0:
                filtered_accuracy = (correct_count / total_filtered) * 100

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Questions Shown", total_filtered)
                with col2:
                    st.metric("Correct", correct_count)
                with col3:
                    st.metric("Accuracy", f"{filtered_accuracy:.1f}%")
        else:
            st.info("No question data available")

    with tab4:
        st.header("AI Short Answer Evaluation")
        st.write("Enter model answer and student answer to get automated score and feedback.")

        with st.form(key='short_answer_form'):
            model_answer = st.text_area("Model Answer", height=130)
            student_answer = st.text_area("Student Answer", height=130)
            submitted = st.form_submit_button("Evaluate Short Answer")

        if submitted:
            if not model_answer.strip() or not student_answer.strip():
                st.error("Both model answer and student answer are required.")
            else:
                payload = {
                    "model_answer": model_answer,
                    "student_answer": student_answer
                }
                try:
                    response = requests.post("http://127.0.0.1:8000/evaluate_short", json=payload, timeout=10)
                    if response.status_code == 200:
                        result = response.json()
                        st.metric("Short Answer Score", f"{result['score']} / 100")
                        st.metric("Similarity", f"{result['similarity'] * 100:.1f}%")
                        st.markdown(f"**Feedback:** {result['feedback']}")

                        st.markdown("### Details")
                        st.write("**Model Answer**")
                        st.write(result['model_answer'])
                        st.write("**Student Answer**")
                        st.write(result['student_answer'])

                    else:
                        st.error(f"Evaluation server returned status {response.status_code}: {response.text}")
                except requests.exceptions.RequestException as err:
                    st.error(f"Failed to connect to evaluation server: {err}")

    with tab5:
        st.header("Code Output Evaluator")
        st.write("Submit student Python code with input and expected output for scoring.")

        with st.form(key='code_eval_form'):
            student_code = st.text_area("Student Code", height=220, help="Write Python code; it will be executed safely in a temporary environment.")
            test_input = st.text_area("Test Input", height=100, help="Input passed to the code on stdin.")
            expected_output = st.text_area("Expected Output", height=100, help="Expected stdout after execution.")
            timeout_seconds = st.number_input("Timeout (seconds)", min_value=1, max_value=30, value=5)
            code_submit = st.form_submit_button("Evaluate Code")

        if code_submit:
            if not student_code.strip():
                st.error("Student code is required for code evaluation.")
            else:
                payload = {
                    "student_code": student_code,
                    "test_input": test_input,
                    "expected_output": expected_output,
                    "timeout_seconds": int(timeout_seconds)
                }
                try:
                    response = requests.post("http://127.0.0.1:8000/evaluate_code", json=payload, timeout=20)
                    if response.status_code == 200:
                        r = response.json()
                        st.metric("Code Evaluation Score", f"{r.get('score', 0)} / 100")
                        st.metric("Output Similarity", f"{r.get('similarity', 0) * 100:.1f}%")
                        st.markdown(f"**Feedback:** {r.get('feedback', 'No feedback')} ")
                        if r.get('error'):
                            st.warning(f"Error: {r.get('error')} - {r.get('details', '')}")
                        st.markdown("### Result Details")
                        st.write(f"**Expected Output:** {r.get('expected_output', '')}")
                        st.write(f"**Actual Output:** {r.get('actual_output', '')}")
                        if r.get('stderr'):
                            st.write("**STDERR:**")
                            st.code(r.get('stderr'), language='bash')
                    else:
                        st.error(f"Evaluator returned {response.status_code}: {response.text}")
                except requests.exceptions.RequestException as err:
                    st.error(f"Failed to connect to evaluation server: {err}")

    with tab6:
        st.header("Batch CSV Upload")
        st.write("Upload CSV with student answers and model answers to get batch AI evaluation.")
        st.markdown("**Expected columns:** student_id, question, model_answer, student_answer, concept (optional)**")

        uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

        if uploaded_file is not None:
            try:
                batch_df = pd.read_csv(uploaded_file)

                required_cols = {"student_id", "question", "model_answer", "student_answer"}
                if not required_cols.issubset(batch_df.columns):
                    st.error(f"CSV must include columns: {', '.join(required_cols)}")
                else:
                    results = []
                    for _, row in batch_df.iterrows():
                        payload = {
                            "student_answer": str(row.get("student_answer", "")),
                            "model_answer": str(row.get("model_answer", ""))
                        }
                        r = requests.post("http://127.0.0.1:8000/evaluate_short", json=payload, timeout=10)
                        if r.status_code == 200:
                            rep = r.json()
                            results.append({
                                "student_id": row.get("student_id"),
                                "question": row.get("question"),
                                "model_answer": row.get("model_answer"),
                                "student_answer": row.get("student_answer"),
                                "score": rep.get("score"),
                                "similarity": rep.get("similarity"),
                                "feedback": rep.get("feedback")
                            })
                        else:
                            results.append({
                                "student_id": row.get("student_id"),
                                "question": row.get("question"),
                                "model_answer": row.get("model_answer"),
                                "student_answer": row.get("student_answer"),
                                "score": 0,
                                "similarity": 0,
                                "feedback": f"API error: {r.status_code}"
                            })

                    batch_results_df = pd.DataFrame(results)
                    st.markdown("### Batch Evaluation Results")
                    st.dataframe(batch_results_df)

                    csv = batch_results_df.to_csv(index=False).encode("utf-8")
                    st.download_button("Download results CSV", data=csv, file_name="batch_evaluation_results.csv", mime="text/csv")

            except Exception as e:
                st.error(f"Failed to process upload: {e}")

else:
    st.error("❌ Unable to load evaluation data")
    st.info("Please ensure the backend server is running and accessible.")

# Footer
st.markdown("---")
st.markdown(f"📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.markdown("Built with ❤️ using Streamlit & FastAPI")