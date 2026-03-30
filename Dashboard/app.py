import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os
from typing import Dict, List

# Page configuration
st.set_page_config(
    page_title="AI Recruitment Platform",
    page_icon="🎯",
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
    .success-card {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 0.5rem 0;
    }
    .warning-card {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
        margin: 0.5rem 0;
    }
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .match-score {
        font-size: 2rem;
        font-weight: bold;
        color: #28a745;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Backend API base URL
API_BASE = "http://localhost:8000"

# Sidebar
st.sidebar.title("🎯 AI Recruitment Platform")

# Navigation
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "CV Upload", "JD Upload", "CV-JD Matching", "CV Optimization", "Analytics"]
)

# Helper functions
def call_api(endpoint: str, method: str = "GET", data: Dict = None, files: Dict = None):
    """Call backend API"""
    try:
        url = f"{API_BASE}{endpoint}"
        if method == "GET":
            response = requests.get(url, params=data)
        elif method == "POST":
            if files:
                response = requests.post(url, data=data, files=files)
            else:
                response = requests.post(url, json=data)
        else:
            st.error(f"Unsupported method: {method}")
            return None

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API call failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"API connection failed: {e}")
        return None

def display_match_analysis(analysis: Dict):
    """Display detailed match analysis"""
    st.subheader("📊 Match Analysis")

    # Overall score
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Match Score", f"{analysis.get('overall_score', 0)}%")
    with col2:
        st.metric("Skill Matches", len(analysis.get('skill_matches', [])))
    with col3:
        st.metric("Skill Gaps", len(analysis.get('skill_gaps', [])))

    # Skill analysis
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("✅ Matching Skills")
        skills = analysis.get('skill_matches', [])
        if skills:
            for skill in skills:
                st.write(f"• {skill}")
        else:
            st.write("No matching skills identified")

    with col2:
        st.subheader("❌ Skill Gaps")
        gaps = analysis.get('skill_gaps', [])
        if gaps:
            for gap in gaps:
                st.write(f"• {gap}")
        else:
            st.write("No skill gaps identified")

    # Recommendations
    st.subheader("💡 Recommendations")
    recommendations = analysis.get('recommendations', [])
    if recommendations:
        for rec in recommendations:
            st.write(f"• {rec}")
    else:
        st.write("No specific recommendations available")

def display_swot_analysis(swot: Dict):
    """Display SWOT analysis"""
    st.subheader("🎯 SWOT Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💪 Strengths")
        strengths = swot.get('strengths', [])
        if strengths:
            for strength in strengths:
                st.write(f"• {strength}")
        else:
            st.write("No strengths identified")

        st.subheader("🚀 Opportunities")
        opportunities = swot.get('opportunities', [])
        if opportunities:
            for opp in opportunities:
                st.write(f"• {opp}")
        else:
            st.write("No opportunities identified")

    with col2:
        st.subheader("⚠️ Weaknesses")
        weaknesses = swot.get('weaknesses', [])
        if weaknesses:
            for weakness in weaknesses:
                st.write(f"• {weakness}")
        else:
            st.write("No weaknesses identified")

        st.subheader("⚡ Threats")
        threats = swot.get('threats', [])
        if threats:
            for threat in threats:
                st.write(f"• {threat}")
        else:
            st.write("No threats identified")

def display_gap_analysis(gaps: Dict):
    """Display gap analysis"""
    st.subheader("🔍 Gap Analysis")

    gap_types = ['skill_gaps', 'experience_gaps', 'knowledge_gaps', 'certification_gaps']

    for gap_type in gap_types:
        gap_list = gaps.get(gap_type, [])
        if gap_list:
            title = gap_type.replace('_', ' ').title()
            st.subheader(f"📋 {title}")
            for gap in gap_list:
                st.write(f"• {gap}")

    # Development plan
    dev_plan = gaps.get('development_plan', [])
    if dev_plan:
        st.subheader("📈 Development Recommendations")
        for plan in dev_plan:
            st.write(f"• {plan}")

# Main content based on selected page
if page == "Dashboard":
    st.markdown('<h1 class="main-header">AI-Powered Recruitment Platform</h1>', unsafe_allow_html=True)

    st.markdown("""
    ## 🎯 Welcome to the Agentic CV-JD Matching Suite

    This platform revolutionizes recruitment workflows through:

    - 🤖 **Multi-role AI Agents**: Automated CV screening and analysis
    - 📄 **Smart Document Processing**: Multi-format CV and JD ingestion
    - 🎯 **Intelligent Matching**: Semantic similarity and gap analysis
    - ✍️ **CV Optimization**: AI-powered resume rewriting
    - 📊 **Advanced Analytics**: Real-time recruitment insights

    ### 🚀 Quick Start
    1. Upload candidate CVs and job descriptions
    2. Run automated matching analysis
    3. Get AI-powered insights and recommendations
    4. Optimize CVs for better matches
    """)

    # Platform stats
    st.subheader("📈 Platform Overview")
    analytics = call_api("/analytics")
    if analytics:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total CVs", analytics.get('total_cvs', 0))
        with col2:
            st.metric("Total JDs", analytics.get('total_jds', 0))
        with col3:
            st.metric("Matches Performed", analytics.get('total_matches', 0))
        with col4:
            st.metric("Avg Match Score", f"{analytics.get('average_match_score', 0)}%")

elif page == "CV Upload":
    st.header("📄 CV Upload & Parsing")

    uploaded_file = st.file_uploader("Upload CV (PDF, DOCX, TXT)", type=['pdf', 'docx', 'txt'])

    if uploaded_file is not None:
        if st.button("Process CV"):
            with st.spinner("Processing CV..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                result = call_api("/upload-cv", "POST", files=files)

                if result and result.get('success'):
                    st.success("CV processed successfully!")

                    # Display parsed data
                    cv_data = result['cv_data']

                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("👤 Personal Information")
                        personal = cv_data.get('personal_info', {})
                        st.write(f"**Name:** {personal.get('name', 'Not found')}")
                        st.write(f"**Email:** {personal.get('email', 'Not found')}")
                        st.write(f"**Phone:** {personal.get('phone', 'Not found')}")

                    with col2:
                        st.subheader("💼 Professional Summary")
                        summary = cv_data.get('summary', 'Not available')
                        st.write(summary[:300] + "..." if len(summary) > 300 else summary)

                    # Skills
                    st.subheader("🛠️ Skills Identified")
                    skills = cv_data.get('skills', [])
                    if skills:
                        st.write(", ".join(skills))
                    else:
                        st.warning("No skills automatically identified")

                    # Experience
                    st.subheader("💼 Work Experience")
                    experience = cv_data.get('experience', [])
                    if experience:
                        for exp in experience[:3]:  # Show first 3
                            st.write(f"**{exp.get('position', '')}** at {exp.get('company', '')}")
                            st.write(f"*{exp.get('duration', '')}*")
                            st.write(exp.get('description', '')[:200] + "..." if len(exp.get('description', '')) > 200 else exp.get('description', ''))
                            st.write("---")
                    else:
                        st.warning("No experience information found")

elif page == "JD Upload":
    st.header("📋 Job Description Upload")

    # JD input options
    input_method = st.radio("Input Method", ["File Upload", "URL", "Text Input"])

    jd_data = None
    source_type = "file"

    if input_method == "File Upload":
        uploaded_file = st.file_uploader("Upload JD (PDF, DOCX, TXT)", type=['pdf', 'docx', 'txt'])
        if uploaded_file:
            jd_data = uploaded_file
            source_type = "file"

    elif input_method == "URL":
        url = st.text_input("Job Description URL")
        if url:
            jd_data = url
            source_type = "url"

    elif input_method == "Text Input":
        text = st.text_area("Paste Job Description", height=200)
        if text:
            jd_data = text
            source_type = "text"

    if jd_data and st.button("Process Job Description"):
        with st.spinner("Processing job description..."):
            if source_type == "file":
                files = {"file": (jd_data.name, jd_data.getvalue(), jd_data.type)}
                data = {"source": jd_data.name, "source_type": source_type}
                result = call_api("/upload-jd", "POST", data=data, files=files)
            else:
                data = {"source": jd_data, "source_type": source_type}
                result = call_api("/upload-jd", "POST", data=data)

            if result and result.get('success'):
                st.success("Job description processed successfully!")

                # Display parsed data
                jd_info = result['jd_data']

                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("💼 Job Details")
                    st.write(f"**Title:** {jd_info.get('job_title', 'Not found')}")
                    st.write(f"**Company:** {jd_info.get('company', 'Not found')}")
                    st.write(f"**Location:** {jd_info.get('location', 'Not found')}")

                with col2:
                    st.subheader("💰 Requirements")
                    req = jd_info.get('requirements', {})
                    st.write(f"**Experience:** {req.get('experience_years', 'Not specified')}")
                    st.write(f"**Education:** {req.get('education', 'Not specified')}")

                # Required skills
                st.subheader("🛠️ Required Skills")
                skills = req.get('skills', [])
                if skills:
                    st.write(", ".join(skills))
                else:
                    st.warning("No skills specified")

                # Responsibilities
                st.subheader("📋 Key Responsibilities")
                responsibilities = jd_info.get('responsibilities', [])
                if responsibilities:
                    for resp in responsibilities[:5]:  # Show first 5
                        st.write(f"• {resp}")
                else:
                    st.warning("No responsibilities listed")

elif page == "CV-JD Matching":
    st.header("🎯 CV-JD Matching & Analysis")

    # Get stored data for selection
    stored_data = call_api("/stored-data")
    if stored_data:
        cv_options = list(stored_data.get('cvs', {}).keys())
        jd_options = list(stored_data.get('jds', {}).keys())

        if cv_options and jd_options:
            col1, col2 = st.columns(2)

            with col1:
                selected_cv = st.selectbox("Select CV", cv_options,
                                         format_func=lambda x: stored_data['cvs'][x]['filename'])

            with col2:
                selected_jd = st.selectbox("Select Job Description", jd_options,
                                         format_func=lambda x: f"JD: {stored_data['jds'][x]['source'][:50]}...")

            if st.button("🔍 Perform Matching Analysis"):
                with st.spinner("Analyzing match..."):
                    match_request = {
                        "cv_id": selected_cv,
                        "jd_id": selected_jd
                    }

                    result = call_api("/match-cv-jd", "POST", match_request)

                    if result:
                        # Display match score prominently
                        st.markdown('<div class="match-score">', unsafe_allow_html=True)
                        st.subheader(f"Match Score: {result['match_score']}%")
                        st.markdown('</div>', unsafe_allow_html=True)

                        # Detailed analysis tabs
                        tab1, tab2, tab3 = st.tabs(["📊 Match Analysis", "🎯 SWOT Analysis", "🔍 Gap Analysis"])

                        with tab1:
                            display_match_analysis(result['analysis'])

                        with tab2:
                            display_swot_analysis(result['swot_analysis'])

                        with tab3:
                            display_gap_analysis(result['gap_analysis'])

                        # Recommendations summary
                        st.subheader("💡 Key Insights")
                        recommendations = result.get('recommendations', [])
                        if recommendations:
                            for rec in recommendations[:3]:  # Show top 3
                                st.info(rec)
        else:
            st.warning("Please upload CVs and job descriptions first")
    else:
        st.error("Unable to retrieve stored data")

elif page == "CV Optimization":
    st.header("✍️ AI-Powered CV Optimization")

    # Get stored data
    stored_data = call_api("/stored-data")
    if stored_data:
        cv_options = list(stored_data.get('cvs', {}).keys())
        jd_options = list(stored_data.get('jds', {}).keys())

        if cv_options and jd_options:
            col1, col2, col3 = st.columns(3)

            with col1:
                selected_cv = st.selectbox("Select CV to Optimize", cv_options,
                                         format_func=lambda x: stored_data['cvs'][x]['filename'])

            with col2:
                selected_jd = st.selectbox("Target Job Description", jd_options,
                                         format_func=lambda x: f"JD: {stored_data['jds'][x]['source'][:30]}...")

            with col3:
                optimization_level = st.selectbox("Optimization Level",
                                                ["conservative", "moderate", "aggressive"],
                                                index=1,
                                                help="Conservative: Minimal changes, Moderate: Balanced optimization, Aggressive: Maximum impact")

            if st.button("🚀 Optimize CV"):
                with st.spinner("AI is rewriting your CV..."):
                    # Get CV and JD data
                    cv_data = stored_data['cvs'][selected_cv]
                    jd_data = stored_data['jds'][selected_jd]

                    rewrite_request = {
                        "cv_data": cv_data['data'],
                        "jd_data": jd_data['data'],
                        "optimization_level": optimization_level
                    }

                    result = call_api("/rewrite-cv", "POST", rewrite_request)

                    if result:
                        st.success("CV optimization complete!")

                        # Display results
                        opt_details = result['optimization_details']

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Original Score", f"{opt_details['original_score']}%")
                        with col2:
                            st.metric("New Score", f"{opt_details['new_score']}%")
                        with col3:
                            st.metric("Improvement", f"{opt_details['improvement']:+.1f}%")

                        # Show rewritten CV
                        st.subheader("📝 Optimized CV")
                        st.text_area("Rewritten Content", result['rewritten_text'], height=300)

                        # Recommendations
                        st.subheader("💡 Optimization Recommendations")
                        for rec in result.get('recommendations', []):
                            st.write(f"• {rec}")

                        # Download option
                        st.download_button(
                            label="📥 Download Optimized CV",
                            data=result['rewritten_text'],
                            file_name=f"optimized_cv_{selected_cv}.txt",
                            mime="text/plain"
                        )
        else:
            st.warning("Please upload CVs and job descriptions first")
    else:
        st.error("Unable to retrieve stored data")

elif page == "Analytics":
    st.header("📊 Recruitment Analytics")

    analytics = call_api("/analytics")
    if analytics:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total CVs Processed", analytics.get('total_cvs', 0))
        with col2:
            st.metric("Total Job Descriptions", analytics.get('total_jds', 0))
        with col3:
            st.metric("Matching Operations", analytics.get('total_matches', 0))
        with col4:
            st.metric("Average Match Score", f"{analytics.get('average_match_score', 0)}%")

        # Match score distribution (mock data for now)
        st.subheader("📈 Match Score Distribution")
        if analytics.get('total_matches', 0) > 0:
            # Create sample distribution based on available data
            scores = [analytics.get('average_match_score', 50)] * 10  # Mock distribution
            fig = px.histogram(scores, nbins=10, title="Match Score Distribution")
            st.plotly_chart(fig)
        else:
            st.info("No match data available yet")

        # Recent activity
        st.subheader("🕒 Recent Activity")
        recent_matches = analytics.get('recent_matches', [])
        if recent_matches:
            for match_id in recent_matches[-5:]:  # Show last 5
                st.write(f"• Match operation: {match_id}")
        else:
            st.write("No recent activity")

    else:
        st.error("Unable to retrieve analytics data")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔗 API Status")
health = call_api("/health")
if health:
    st.sidebar.success("✅ Backend Connected")
else:
    st.sidebar.error("❌ Backend Disconnected")

st.sidebar.markdown("### 📚 About")
st.sidebar.info("""
AI-Powered Recruitment Platform
- Multi-format document processing
- AI-driven matching & analysis
- CV optimization engine
- Real-time analytics
""")
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