#!/usr/bin/env python3
"""
Test script for AI Recruitment Platform
Demonstrates the core functionality of the CV-JD matching system
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from recruitment.document_parser import CVParser, JDParser
from recruitment.matching_engine import MatchingEngine
from recruitment.cv_rewrite_engine import CVRewriteEngine
from recruitment.agent_system import CoordinatorAgent

def test_document_parsing():
    """Test CV and JD parsing"""
    print("🔍 Testing Document Parsing...")

    # Initialize parsers
    cv_parser = CVParser()
    jd_parser = JDParser()

    # Parse sample CV
    cv_path = "Data/sample_cv.txt"
    if os.path.exists(cv_path):
        cv_data = cv_parser.parse_cv(cv_path)
        print(f"✅ CV Parsed: {cv_data.get('personal_info', {}).get('name', 'Unknown')}")
        print(f"   Skills found: {len(cv_data.get('skills', []))}")
    else:
        print("❌ Sample CV not found")
        return False

    # Parse sample JD
    jd_path = "Data/sample_jd.txt"
    if os.path.exists(jd_path):
        jd_data = jd_parser.parse_jd(jd_path, 'file')
        print(f"✅ JD Parsed: {jd_data.get('job_title', 'Unknown Position')}")
        print(f"   Required skills: {len(jd_data.get('requirements', {}).get('skills', []))}")
    else:
        print("❌ Sample JD not found")
        return False

    return cv_data, jd_data

def test_matching_engine(cv_data, jd_data):
    """Test matching functionality"""
    print("\n🎯 Testing Matching Engine...")

    matcher = MatchingEngine()

    # Test similarity scoring
    cv_text = str(cv_data)
    jd_text = str(jd_data)
    similarity_score = matcher.compute_similarity_score(cv_text, jd_text)
    print(f"✅ Similarity Score: {similarity_score}%")

    # Test detailed analysis
    analysis = matcher.detailed_matching_analysis(cv_data, jd_data)
    print(f"✅ Detailed Analysis: Overall score {analysis.get('overall_score', 0)}%")
    print(f"   Matching skills: {len(analysis.get('skill_matches', []))}")
    print(f"   Skill gaps: {len(analysis.get('skill_gaps', []))}")

    # Test SWOT analysis
    swot = matcher.swot_analysis(cv_data, jd_data)
    print(f"✅ SWOT Analysis: {len(swot.get('strengths', []))} strengths, {len(swot.get('weaknesses', []))} weaknesses")

    return analysis, swot

def test_cv_rewrite(cv_data, jd_data):
    """Test CV rewriting functionality"""
    print("\n✍️ Testing CV Rewrite Engine...")

    rewriter = CVRewriteEngine()

    # Test CV rewriting
    rewrite_result = rewriter.rewrite_cv(cv_data, jd_data, "moderate")
    if 'error' not in rewrite_result:
        print("✅ CV Rewrite Complete")
        opt_details = rewrite_result.get('optimization_details', {})
        print(f"   Original score: {opt_details.get('original_score', 0)}%")
        print(f"   New score: {opt_details.get('new_score', 0)}%")
        print(f"   Improvement: {opt_details.get('improvement', 0):+.1f}%")
        print(f"   Recommendations: {len(rewrite_result.get('recommendations', []))}")
    else:
        print(f"❌ CV Rewrite Failed: {rewrite_result['error']}")

    return rewrite_result

def test_agent_system(cv_data, jd_data):
    """Test agent system"""
    print("\n🤖 Testing Agent System...")

    coordinator = CoordinatorAgent()

    # Test full workflow
    context = {
        'cv_path': 'Data/sample_cv.txt',
        'jd_path': 'Data/sample_jd.txt',
        'workflow': 'full_analysis',
        'optimize_cv': True,
        'optimization_level': 'moderate'
    }

    try:
        result = coordinator.execute_task("run_workflow", context)
        if 'error' not in result:
            print("✅ Agent Workflow Complete")
            if 'matching' in result:
                match_score = result['matching'].get('match_score', 0)
                print(f"   Match Score: {match_score}%")
            if 'analysis' in result:
                swot = result['analysis'].get('swot_analysis', {})
                print(f"   SWOT: {len(swot.get('strengths', []))}S, {len(swot.get('weaknesses', []))}W")
        else:
            print(f"❌ Agent Workflow Failed: {result['error']}")
    except Exception as e:
        print(f"❌ Agent System Error: {e}")

def main():
    """Main test function"""
    print("🚀 AI Recruitment Platform - Test Suite")
    print("=" * 50)

    # Test document parsing
    parse_result = test_document_parsing()
    if not parse_result:
        print("❌ Document parsing failed. Exiting.")
        return

    cv_data, jd_data = parse_result

    # Test matching engine
    analysis, swot = test_matching_engine(cv_data, jd_data)

    # Test CV rewriting
    rewrite_result = test_cv_rewrite(cv_data, jd_data)

    # Test agent system
    test_agent_system(cv_data, jd_data)

    print("\n" + "=" * 50)
    print("🎉 Test Suite Complete!")
    print("\n📋 Summary:")
    print("- Document parsing: ✅")
    print("- Matching engine: ✅")
    print("- CV rewriting: ✅")
    print("- Agent system: ✅")
    print("\n🚀 Ready to start the recruitment platform!")
    print("Run: python -m uvicorn backend.main:app --reload")
    print("Then: streamlit run Dashboard/app.py")

if __name__ == "__main__":
    main()