#!/usr/bin/env python3
"""
Financial Product Analysis Web Interface
Beautiful Streamlit app for analyzing financial products from URLs
"""

import streamlit as st
import json
import time
from datetime import datetime
from typing import Dict, Any
import plotly.graph_objects as go
import plotly.express as px
from urllib.parse import urlparse
import os
import sys

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from pipeline import analyzer_pipeline

# Page configuration
st.set_page_config(
    page_title="AI Finance Analyzer",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS styling for finance industry
st.markdown("""
<style>
    /* Import professional font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global font and base styling */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .subtitle {
        text-align: center;
        color: #1e40af;
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 2rem;
        line-height: 1.6;
    }
    
    .metric-container {
        background: #ffffff;
        border: 1px solid #3b82f6;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(59, 130, 246, 0.2);
        text-align: center;
        margin: 0.5rem 0;
        transition: all 0.2s ease;
    }
    
    .metric-container:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transform: translateY(-1px);
    }
    
    .metric-container h4 {
        color: #1e3a8a;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-container p {
        color: #1e3a8a;
        font-size: 1.1rem;
        font-weight: 500;
        margin: 0;
    }
    
    .success-container {
        background: #eff6ff;
        border: 1px solid #3b82f6;
        border-left: 4px solid #3b82f6;
        padding: 1.5rem;
        border-radius: 8px;
        color: #1e40af;
        margin: 1rem 0;
    }
    
    .success-container h3 {
        color: #1e40af;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .warning-container {
        background: #fff7ed;
        border: 1px solid #fb923c;
        border-left: 4px solid #fb923c;
        padding: 1.5rem;
        border-radius: 8px;
        color: #c2410c;
        margin: 1rem 0;
    }
    
    .insight-box {
        background: #eff6ff;
        border: 1px solid #60a5fa;
        border-left: 4px solid #3b82f6;
        padding: 1.2rem;
        border-radius: 8px;
        color: #1e3a8a;
        margin: 0.5rem 0;
        line-height: 1.6;
    }
    
    .negative-insight-box {
        background: #fef2f2;
        border: 1px solid #f87171;
        border-left: 4px solid #ef4444;
        padding: 1.2rem;
        border-radius: 8px;
        color: #991b1b;
        margin: 0.5rem 0;
        line-height: 1.6;
    }
    
    .sidebar-content {
        background: #1e3a8a;
        color: white;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(30, 58, 138, 0.2);
    }
    
    .sidebar-content h3 {
        color: white;
        font-weight: 600;
        margin-bottom: 1rem;
        font-size: 1.1rem;
    }
    
    .sidebar-content p {
        color: #dbeafe;
        font-size: 0.9rem;
        line-height: 1.5;
        margin-bottom: 0.5rem;
    }
    
    .sidebar-section {
        background: #fffbeb;
        border: 1px solid #fbbf24;
        padding: 1.2rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .sidebar-section h4 {
        color: #1e3a8a;
        font-weight: 600;
        margin-bottom: 0.8rem;
        font-size: 1rem;
    }
    
    .sidebar-list-item {
        color: #012970;
        font-size: 0.9rem;
        line-height: 1.5;
        margin-bottom: 0.3rem;
        padding-left: 0.5rem;
    }
    
    .feature-item {
        color: #012970;
        font-weight: 500;
        font-size: 0.9rem;
        margin-bottom: 0.3rem;
    }
    
    /* Improved button styling with brand colors */
    .stButton > button {
        background: #F8DB31 !important;
        color: #012970 !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        background: #F5D520 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(248, 219, 49, 0.4) !important;
    }
    
    /* Download button styling to match Begin Analysis button */
    .stDownloadButton > button {
        background: #F8DB31 !important;
        color: #012970 !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    
    .stDownloadButton > button:hover {
        background: #F5D520 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(248, 219, 49, 0.4) !important;
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        border: 2px solid #e2e8f0 !important;
        border-radius: 6px !important;
        font-size: 1rem !important;
        padding: 0.75rem !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: #3b82f6 !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: #eff6ff !important;
        border: 1px solid #3b82f6 !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
    }
    
    /* Remove default margins */
    .element-container {
        margin-bottom: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

def is_valid_url(url: str) -> bool:
    """Check if the URL is valid"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def create_progress_bar():
    """Create a beautiful animated progress bar"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    steps = [
        "🔍 Validating URL and extracting content...",
        "📄 Processing terms and conditions document...",
        "🔎 Identifying financial product details...",
        "📋 Conducting AI-powered terms analysis...",
                        "💬 Gathering community feedback from community discussions...",
        "🧠 Synthesizing insights and risk assessment...",
        "📊 Generating comprehensive analysis report..."
    ]
    
    for i, step in enumerate(steps):
        progress_bar.progress((i + 1) / len(steps))
        status_text.text(step)
        time.sleep(0.5)
    
    status_text.text("✅ Analysis complete!")
    return progress_bar, status_text

def display_product_info(product_info: Dict[str, Any]):
    """Display product information in a beautiful card"""
    st.markdown(f"""
    <div class="success-container">
        <h3>Product Identified</h3>
        <p><strong>Name:</strong> {product_info['name']}</p>
        <p><strong>Type:</strong> {product_info['type'].title()}</p>
        <p><strong>Company:</strong> {product_info['company']}</p>
    </div>
    """, unsafe_allow_html=True)

def display_terms_analysis(terms_analysis: Dict[str, Any]):
    """Display terms analysis in organized sections with clean Markdown rendering"""
    st.markdown("### Terms & Conditions Analysis")
    
    # Key Information
    with st.expander("📌 Key Information", expanded=True):
        # Remove duplicate "Key Points:" header and render clean Markdown
        content = terms_analysis['key_information']
        # Remove the "Key Points:" or "**Key Points:**" header if it exists
        if content.startswith('**Key Points:**'):
            content = content.replace('**Key Points:**\n', '', 1)
        elif content.startswith('Key Points:'):
            content = content.replace('Key Points:\n', '', 1)
        
        # Clean Markdown rendering without styled boxes
        st.markdown(content)
    
    # Consumer Score (if available)
    if terms_analysis.get('consumer_score'):
        with st.expander("⭐ Consumer Score"):
            content = terms_analysis['consumer_score']
            st.markdown(content)
    
    # Risks and Warnings
    with st.expander("⚠️ Risks & Important Notes", expanded=True):
        # Remove duplicate "Potential Risks:" header
        content = terms_analysis['risks']
        if content.startswith('**Potential Risks:**'):
            content = content.replace('**Potential Risks:**\n', '', 1)
        elif content.startswith('Potential Risks:'):
            content = content.replace('Potential Risks:\n', '', 1)
        
        # Ensure proper markdown formatting
        content = content.strip()
        st.markdown(content)
    
    # Financial Ramifications (if available)
    if terms_analysis.get('financial_ramifications'):
        with st.expander("💰 Financial Ramifications & Gotchas", expanded=True):
            content = terms_analysis['financial_ramifications']
            st.markdown(content)
    
    # Detailed Analysis
    with st.expander("Detailed Analysis"):
        # Remove duplicate "Details:" header
        content = terms_analysis['details']
        if content.startswith('**Details:**'):
            content = content.replace('**Details:**\n', '', 1)
        elif content.startswith('Details:'):
            content = content.replace('Details:\n', '', 1)
        
        # Ensure proper markdown formatting
        content = content.strip()
        st.markdown(content)

def display_reddit_insights(reddit_insights: Dict[str, Any]):
    """Display Reddit insights in a two-column layout with clean Markdown rendering"""
    st.markdown("### Community Insights from Community Discussions")
    
    # Only show negative feedback/concerns
    st.markdown("#### ⚠️ Community Concerns & Issues")
    if reddit_insights.get('negative'):
        content = reddit_insights['negative']
        st.markdown(content)
    else:
        st.info("No concerns found in community discussions")

def display_reddit_sources(reddit_data: list):
    """Display Reddit source URLs"""
    if reddit_data:
        st.markdown("These discussions were analyzed to provide community insights:")
        st.markdown("### 🔗 Reddit Discussion Sources")
        
        # Create a more compact list with tighter spacing
        links_html = "<div style='line-height: 1.3; margin-top: 0.5rem;'>"
        for i, thread in enumerate(reddit_data, 1):
            title = thread.get('title', 'Discussion')
            url = thread.get('url', '')
            if url:
                links_html += f"<p style='margin: 0.2rem 0; color: #012970;'>{i}. <a href='{url}' target='_blank' style='color: #2746DA; text-decoration: none;'>{title}</a></p>"
            else:
                links_html += f"<p style='margin: 0.2rem 0; color: #012970;'>{i}. {title}</p>"
        links_html += "</div>"
        
        st.markdown(links_html, unsafe_allow_html=True)


def save_results_to_json(results: Dict[str, Any], url: str):
    """Save analysis results to a JSON file"""
    os.makedirs("data/results", exist_ok=True)
    
    # Create filename based on URL and timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analysis_{timestamp}.json"
    filepath = os.path.join("data/results", filename)
    
    # Add metadata
    results["analysis_metadata"] = {
        "analyzed_url": url,
        "analysis_date": datetime.now().isoformat(),
        "analyzer_version": "1.0.0"
    }
    
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2)
    
    return filepath

def main():
    """Main Streamlit app"""
    
    # Header
    st.markdown('<h1 class="main-header">Your Personal Finance Advisor</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Unlock hidden insights and make smarter financial decisions with AI-powered analysis</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-content">
            <h3>How It Works</h3>
            <p><strong>Step 1:</strong> Enter a financial product URL</p>
            <p><strong>Step 2:</strong> AI extracts & analyzes terms and conditions</p>
            <p><strong>Step 3:</strong> Searches community discussions for insights</p>
            <p><strong>Step 4:</strong> Provides comprehensive analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="sidebar-section">
            <h4>📚 Example Products</h4>
            <ul style="margin: 0; padding-left: 1.2rem;">
                <li class="sidebar-list-item">Wells Fargo Active Cash Card</li>
                <li class="sidebar-list-item">Chase Sapphire Preferred</li>
                <li class="sidebar-list-item">Capital One Venture Rewards</li>
                <li class="sidebar-list-item">American Express Gold Card</li>
                <li class="sidebar-list-item">Discover it Cash Back</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="sidebar-section">
            <h4>⚡ Key Features</h4>
            <ul style="margin: 0; padding-left: 1.2rem; list-style: none;">
                <li class="feature-item">✓ AI-Powered Analysis</li>
                <li class="feature-item">✓ Risk Identification</li>
                <li class="feature-item">✓ Community Insights</li>
                <li class="feature-item">✓ Consumer Scoring</li>
                <li class="feature-item">✓ Professional Reports</li>
                <li class="feature-item">✓ Export Capabilities</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="sidebar-section">
            <h4>📋 Supported URLs</h4>
            <ul style="margin: 0; padding-left: 1.2rem;">
                <li class="sidebar-list-item">Terms and conditions (i.e., agreements) pages</li>
                <li class="sidebar-list-item">Product agreement documents</li>
                <li class="sidebar-list-item">Credit card disclosure pages</li>
                <li class="sidebar-list-item">Loan terms and conditions (i.e., agreements) documents</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content
    # PDF upload option
    st.markdown("### 📄 Upload Your Document")
    uploaded_file = st.file_uploader(
        "Upload a PDF file containing terms and conditions",
        type=['pdf'],
        help="Upload a PDF document with financial product terms and conditions"
    )
    
    # Add "OR" divider
    st.markdown("<div style='text-align: center; margin: 1rem 0; color: #6B7280; font-weight: 500;'>OR</div>", unsafe_allow_html=True)
    
    # URL input
    st.markdown("### 🔗 Enter URL")
    url = st.text_input(
        "Enter the URL of a financial product's terms and conditions page",
        placeholder="https://example.com/credit-card-terms-and-conditions",
        help="Paste the URL of terms & conditions, product agreement, or disclosure document"
    )
    
    # Analysis button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button(
            "Begin Analysis", 
            use_container_width=True,
            type="primary"
        )
    
    # Analysis section
    if analyze_button:
        # Check if either PDF or URL is provided
        if not uploaded_file and not url:
            st.error("❌ Please either upload a PDF file or enter a URL to analyze")
            return
        
        if url and not is_valid_url(url):
            st.error("❌ Please enter a valid URL (must include http:// or https://)")
            return
        
        # Determine input type
        input_source = uploaded_file if uploaded_file else url
        
        try:
            # Show progress
            progress_bar, status_text = create_progress_bar()
            
            # Run the analysis pipeline
            with st.spinner("Running AI analysis..."):
                results = analyzer_pipeline(input_source)
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Check for errors
            if "error" in results:
                st.error(f"❌ Analysis failed: {results['error']}")
                
                # Show debug information if available
                if st.checkbox("Show debug information"):
                    st.json(results)
                return
            
            # Display successful results with brand colors
            st.markdown(
                '<div style="background-color: #E6EFFF; border: 1px solid #2746DA; border-left: 4px solid #2746DA; padding: 1rem; border-radius: 8px; color: #012970; margin: 1rem 0;">'
                '<strong>✅ Analysis completed successfully!</strong>'
                '</div>',
                unsafe_allow_html=True
            )
            
            # Product information
            display_product_info(results['product_info'])
            
            # Terms analysis
            display_terms_analysis(results['terms_analysis'])
            
            # Reddit insights
            display_reddit_insights(results['reddit_insights'])
            

            # Display Reddit sources
            if results.get('reddit_data'):
                display_reddit_sources(results['reddit_data'])
            
            # Save results
            try:
                input_description = uploaded_file.name if uploaded_file else url
                filepath = save_results_to_json(results, input_description)
                # Download button for results (replaces the saved message)
                results_json = json.dumps(results, indent=2)
                st.download_button(
                    label="📥 Download Full Results (JSON)",
                    data=results_json,
                    file_name=f"financial_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            except Exception as e:
                st.warning(f"⚠️ Could not save results: {e}")

            
        except Exception as e:
            st.error(f"❌ An unexpected error occurred: {str(e)}")
            
            # Show detailed error in expander
            with st.expander("Show error details"):
                st.exception(e)

if __name__ == "__main__":
    main()
