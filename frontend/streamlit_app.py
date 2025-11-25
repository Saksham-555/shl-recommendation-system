"""
Streamlit Frontend for SHL Assessment Recommendation System
Matches your FastAPI backend structure
"""

import streamlit as st
import requests
import pandas as pd

# Configuration
st.set_page_config(
    page_title="SHL Assessment Recommender",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🎯 SHL Assessment Recommendation System")
st.markdown("### AI-Powered Recommendations from 377+ Individual Test Solutions")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API URL input
    api_base_url = st.text_input(
        "API Base URL",
        value="http://localhost:8000",
        help="Enter your API base URL (without /recommend)"
    )
    
    # Check API health
    try:
        health_response = requests.get(f"{api_base_url}/health", timeout=5)
        if health_response.status_code == 200:
            health_data = health_response.json()
            st.success("✅ API Connected")
            st.json({
                "Status": health_data.get("status", "unknown"),
                "Gemini AI": health_data.get("gemini_ai", "unknown"),
                "Vector DB": health_data.get("vector_db", "unknown")
            })
        else:
            st.error("❌ API Not Responding")
    except:
        st.warning("⚠️ API Not Connected")
        st.code(f"Make sure API is running at:\n{api_base_url}")
    
    st.markdown("---")
    
    # Settings
    use_ai_insights = st.checkbox(
        "Enable AI Insights (Gemini)", 
        value=True,
        help="Generate AI-powered insights using Gemini"
    )
    
    num_recommendations = st.slider(
        "Max Recommendations", 
        min_value=5, 
        max_value=10, 
        value=10
    )
    
    st.markdown("---")
    st.markdown("### 📖 Example Queries")
    
    example_queries = [
        "Java developer who collaborates with business teams",
        "Python and SQL skills, mid-level, under 60 minutes",
        "Cognitive and personality tests for analyst role",
        "Sales position for new graduates, 30 min assessment"
    ]
    
    for i, example in enumerate(example_queries, 1):
        if st.button(f"💡 Example {i}", key=f"example_{i}"):
            st.session_state.query = example
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.info("""
    **Data Source:** SHL Product Catalog
    
    **Category:** Individual Test Solutions only
    
    **Total Assessments:** 377
    
    **Technology:** RAG + Gemini AI
    """)

# Main content
st.subheader("🔍 Enter Your Query")

# Initialize session state
if 'query' not in st.session_state:
    st.session_state.query = ""

# Query input
query = st.text_area(
    "Job Description or Query:",
    value=st.session_state.query,
    height=150,
    placeholder="Example: Looking for a mid-level Python developer who can work with SQL databases and collaborate with cross-functional teams...",
    help="Enter a job description, natural language query, or paste a JD URL"
)

# Buttons
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    search_button = st.button("🚀 Get Recommendations", type="primary")

with col2:
    clear_button = st.button("🗑️ Clear")

with col3:
    st.write("")  # Spacer

if clear_button:
    st.session_state.query = ""
    st.rerun()

# Process query
if search_button:
    if not query.strip():
        st.warning("⚠️ Please enter a query or job description")
    else:
        with st.spinner("🤖 Analyzing requirements and finding best assessments..."):
            try:
                # Call your API
                response = requests.post(
                    f"{api_base_url}/recommend",
                    json={
                        "text": query,
                        "use_ai": use_ai_insights
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    recommendations = data.get("recommendations", [])
                    total_found = data.get("total_found", len(recommendations))
                    returned = data.get("returned", len(recommendations))
                    
                    if recommendations:
                        # Success metrics
                        st.success(f"✅ Found {total_found} matching assessments, showing top {min(num_recommendations, returned)}")
                        
                        # Stats
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Matches", total_found)
                        with col2:
                            st.metric("Showing", min(num_recommendations, len(recommendations)))
                        with col3:
                            avg_score = sum(r.get('relevance_score', 0) for r in recommendations[:num_recommendations]) / min(num_recommendations, len(recommendations))
                            st.metric("Avg Match Score", f"{avg_score*100:.1f}%")
                        
                        st.markdown("---")
                        
                        # Display recommendations
                        for i, rec in enumerate(recommendations[:num_recommendations], 1):
                            with st.expander(
                                f"#{i} - {rec['name']} ({rec.get('relevance_score', 0)*100:.0f}% Match)", 
                                expanded=(i <= 3)
                            ):
                                # Header with score
                                col_title, col_score = st.columns([4, 1])
                                with col_title:
                                    st.markdown(f"### {rec['name']}")
                                with col_score:
                                    score = rec.get('relevance_score', 0)
                                    st.progress(score)
                                    st.caption(f"{score*100:.1f}% Match")
                                
                                # Details grid
                                col1, col2, col3, col4 = st.columns(4)
                                
                                with col1:
                                    st.markdown("**⏱️ Duration**")
                                    st.write(rec.get('duration', 'Not specified'))
                                
                                with col2:
                                    st.markdown("**👤 Job Level**")
                                    st.write(rec.get('job_level', 'Not specified'))
                                
                                with col3:
                                    st.markdown("**📋 Test Type**")
                                    st.write(rec.get('test_type', 'Not specified'))
                                
                                with col4:
                                    st.markdown("**🌐 Remote**")
                                    st.write(rec.get('remote_testing', 'Not specified'))
                                
                                # Description
                                st.markdown("**📝 Description:**")
                                st.write(rec.get('description', 'No description available'))
                                
                                # AI Insights
                                if use_ai_insights and rec.get('ai_insights'):
                                    st.markdown("**🤖 AI-Generated Insights:**")
                                    with st.container():
                                        st.info(rec['ai_insights'])
                                
                                # Languages
                                if rec.get('languages') and rec['languages'] != 'Not specified':
                                    st.markdown("**🌍 Available Languages:**")
                                    st.write(rec['languages'])
                                
                                # Link
                                st.markdown(f"**🔗 [View Full Assessment Details]({rec['url']})**")
                        
                        # Export section
                        st.markdown("---")
                        st.subheader("📥 Export Results")
                        
                        # Prepare DataFrame
                        export_data = []
                        for rec in recommendations[:num_recommendations]:
                            export_data.append({
                                'Assessment Name': rec['name'],
                                'URL': rec['url'],
                                'Match Score': f"{rec.get('relevance_score', 0)*100:.1f}%",
                                'Duration': rec.get('duration', 'N/A'),
                                'Job Level': rec.get('job_level', 'N/A'),
                                'Test Type': rec.get('test_type', 'N/A'),
                                'Remote Testing': rec.get('remote_testing', 'N/A'),
                                'Description': rec.get('description', '')[:200] + '...'
                            })
                        
                        df = pd.DataFrame(export_data)
                        
                        # Display table
                        st.dataframe(df, use_container_width=True)
                        
                        # Download button
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Results as CSV",
                            data=csv,
                            file_name="shl_recommendations.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    else:
                        st.warning("😕 No assessments found. Try rephrasing your query or using different keywords.")
                
                elif response.status_code == 500:
                    st.error("❌ Server Error")
                    error_detail = response.json().get('detail', 'Unknown error')
                    st.code(error_detail)
                    if 'Vector database not initialized' in error_detail:
                        st.info("💡 Run `python app/rag.py` to initialize the vector database")
                else:
                    st.error(f"❌ API Error: {response.status_code}")
                    st.code(response.text)
            
            except requests.exceptions.ConnectionError:
                st.error(f"❌ Could not connect to API at {api_base_url}")
                st.info("""
                **Troubleshooting:**
                1. Make sure API is running: `uvicorn app.api_fixed:app --reload`
                2. Check if URL is correct
                3. Verify firewall settings
                """)
            
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. The API might be processing...")
            
            except Exception as e:
                st.error(f"❌ Unexpected Error: {str(e)}")
                st.code(str(e))

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p><strong>SHL Assessment Recommendation System</strong></p>
        <p>Built with Streamlit | Powered by RAG + Gemini AI | Data from SHL Product Catalog</p>
        <p>📊 377 Individual Test Solutions | 🎯 Semantic Search | 🤖 AI-Enhanced Insights</p>
    </div>
""", unsafe_allow_html=True)
