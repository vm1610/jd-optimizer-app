import streamlit as st

def set_page_config():
    """Configure the Streamlit page settings"""
    st.set_page_config(
        page_title="JD Agent",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

# Base custom CSS from the original app
base_custom_css = """
<style>
    /* Base Text and Background Colors */
    .main .block-container {
        color: #FFFFFF;
        background-color: #1A202C;
    }
    
    /* Headers */
    .main-header {
        font-size: 26px;
        font-weight: bold;
        margin-bottom: 15px;
        color: #f5f5dc;
    }
    
    .section-header {
        font-size: 22px;
        font-weight: bold;
        margin-top: 25px;
        margin-bottom: 10px;
        color: #f5f5dc;
        padding: 5px 0;
        border-bottom: 2px solid #4299E1;
    }
    
    .subsection-header {
        font-size: 18px;
        font-weight: bold;
        margin-top: 15px;
        margin-bottom: 5px;
        color: #f5f5dc;
    }
    
    /* Message Boxes */
    .highlight-box {
        background-color: #2D3748;
        border-left: 4px solid #4299E1;
        padding: 12px;
        margin: 12px 0;
        border-radius: 4px;
        color: #FFFFFF;
    }
    
    .success-box {
        background-color: #1C4532;
        border-left: 4px solid #38A169;
        padding: 12px;
        margin: 12px 0;
        border-radius: 4px;
        color: #FFFFFF;
    }
    
    .warning-box {
        background-color: #744210;
        border-left: 4px solid #ED8936;
        padding: 12px;
        margin: 12px 0;
        border-radius: 4px;
        color: #FFFFFF;
    }
    
    /* Content Cards */
    .tab-header {
        font-weight: bold;
        color: #FFFFFF;
    }
    
    .metric-card {
        background-color: #2D3748;
        border-radius: 5px;
        padding: 12px;
        margin: 8px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        color: #FFFFFF;
        border: 1px solid #4A5568;
    }
    
    /* Category Boxes */
    .category-high {
        background-color: #1C4532;
        border-left: 3px solid #38A169;
        padding: 12px;
        margin: 8px 0;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        color: #FFFFFF;
    }
    
    .category-medium {
        background-color: #744210;
        border-left: 3px solid #ED8936;
        padding: 12px;
        margin: 8px 0;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        color: #FFFFFF;
    }
    
    .category-low {
        background-color: #742A2A;
        border-left: 3px solid #F56565;
        padding: 12px;
        margin: 8px 0;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
        color: #FFFFFF;
    }
    
    /* Input Fields and Selectors */
    .stTextInput > div > div > input {
        color: #FFFFFF;
        border: 1px solid #4A5568;
        background-color: #2D3748;
    }
    
    .stSelectbox > div > div > div {
        color: #FFFFFF;
        border: 1px solid #4A5568;
        background-color: #2D3748;
    }
    
    .stTextArea > div > div > textarea {
        color: #FFFFFF;
        border: 1px solid #4A5568;
        background-color: #2D3748;
        font-family: monospace;
    }
    
    /* Buttons */
    .stButton > button {
        font-weight: 600;
        border-radius: 4px;
        background-color: #3182CE;
        color: white;
    }
    
    .stButton > button[kind="secondary"] {
        background-color: #2D3748;
        color: #FFFFFF;
        border: 1px solid #4299E1;
    }
    
    /* Drag and drop styles */
    .drag-container {
        padding: 15px;
        border: 2px dashed #4A5568;
        border-radius: 5px;
        margin-bottom: 12px;
        background-color: #2D3748;
    }
    
    .drag-item {
        padding: 12px;
        background-color: #1A202C;
        border: 1px solid #4A5568;
        border-radius: 5px;
        margin-bottom: 8px;
        cursor: grab;
        color: #FFFFFF;
    }
    
    .drag-item:hover {
        background-color: #2D3748;
        border-color: #63B3ED;
    }
    
    /* Feedback Box */
    .client-feedback-box {
        background-color: #2D3748;
        border-left: 4px solid #4299E1;
        padding: 15px;
        margin: 12px 0;
        border-radius: 4px;
        color: #FFFFFF;
    }
    
    /* Tab Styling */
    button[data-baseweb="tab"] {
        background-color: #2D3748;
        color: #FFFFFF;
        border-bottom: 2px solid #4299E1;
        font-weight: 500;
    }
    
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #4A5568;
        color: #FFFFFF;
        border-bottom: 2px solid #63B3ED;
        font-weight: 600;
    }
    
    /* Better contrast for DataFrames and tables */
    .stDataFrame {
        color: #FFFFFF;
    }
    
    .stDataFrame [data-testid="stTable"] {
        background-color: #2D3748;
        border: 1px solid #4A5568;
    }
    
    .stDataFrame th {
        background-color: #4A5568;
        color: #FFFFFF;
        font-weight: 600;
    }
    
    .stDataFrame td {
        color: #FFFFFF;
        border-bottom: 1px solid #4A5568;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #FFFFFF;
        background-color: #2D3748;
        border-radius: 4px;
    }
    
    .streamlit-expanderContent {
        background-color: #1A202C;
        border: 1px solid #4A5568;
        border-top: none;
        border-radius: 0 0 4px 4px;
        padding: 10px;
        color: #FFFFFF;
    }
    
    /* Text Area Improvements - Final Enhanced Version and Read-only areas */
    .stTextArea > div > div > textarea {
        background-color: #2D3748;
        color: #FFFFFF !important;
        border: 1px solid #4A5568;
        font-family: monospace;
    }
    
    /* Specifically target disabled/read-only text areas */
    .stTextArea > div > div > textarea:disabled,
    .stTextArea > div > div > textarea[readonly] {
        background-color: #2D3748 !important;
        color: #FFFFFF !important;
        opacity: 1 !important; /* Prevent dimming on disabled elements */
        -webkit-text-fill-color: #FFFFFF !important; /* Safari fix */
        font-weight: 500 !important; /* Make slightly bolder */
    }
    
    /* Add more contrast to radio buttons and checkboxes */
    .stRadio > div {
        color: #FFFFF;
    }
    
    .stCheckbox > div > label {
        color: #FFFFFF;
    }
    
    /* Make tabs more visible */
    div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] button {
        background-color: #2D3748;
        color: #f5f5dc;
    }
    
    div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] button:hover {
        background-color: #4A5568;
    }

    /* Additional style for better contrast of text inputs */
    input, textarea, .stLinkButton, .stMarkdown, p, ol, ul, dl {
        color:#f5f5dc !important;
    }

    /* Additional styles for alert messages */
    .stAlert > div {
        color: #f5f5dc;
    }

    /* Ensure headers are clearly visible */
    h1, h2, h3, h4, h5, h6 {
        color:#f5f5dc !important;
    }

    /* Focus on enhancing the final enhanced version block and all read-only text areas */
    [data-testid="stTextArea"] textarea {
        color: #FFFFFF !important;
        font-size: 1rem !important;
    }

    /* Cross-platform fixes for text visibility */
    [data-testid="stTextArea"] textarea:disabled,
    [data-testid="stTextArea"] textarea[readonly],
    textarea.st-ce,
    textarea.st-dk {
        background-color: #2D3748 !important;
        color: #e0e0e0 !important;
        opacity: 1 !important;
        -webkit-text-fill-color: #FFFFFF !important; /* Fix for Safari/Mac */
        -moz-osx-font-smoothing: grayscale !important; /* Improves text rendering on Mac */
        -webkit-font-smoothing: antialiased !important; /* Improves text rendering on Mac */
        text-shadow: 0 0 0 #FFFFFF !important; /* Alternative rendering fix */
    }
</style>
"""

# Add session history sidebar styling
sidebar_css = """
<style>
    /* Session History Sidebar Styles */
    .sidebar-toggle {
        position: fixed;
        top: 80px;
        left: 0;
        background-color: #3182CE;
        color: white;
        border: none;
        border-radius: 0 4px 4px 0;
        padding: 8px;
        cursor: pointer;
        z-index: 1000;
    }
    
    /* Session cards */
    .session-history-card {
        background-color: #2D3748;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 4px solid #4299E1;
        transition: all 0.2s ease;
    }
    
    .session-history-card:hover {
        background-color: #3A4963;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .session-title {
        font-weight: bold;
        font-size: 1.1rem;
        color: #f5f5dc;
        margin-bottom: 5px;
    }
    
    .session-timestamp {
        font-size: 0.8rem;
        color: #A0AEC0;
    }
    
    .session-jd {
        font-size: 0.9rem;
        color: #E2E8F0;
        margin-top: 8px;
    }
    
    .session-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
        margin-top: 10px;
    }
    
    .session-tag {
        background-color: #4A5568;
        color: #E2E8F0;
        font-size: 0.7rem;
        padding: 2px 8px;
        border-radius: 12px;
    }
    
    /* Buttons in sidebar */
    .sidebar-button {
        background-color: #3182CE;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 12px;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.2s ease;
        width: 100%;
        margin-bottom: 10px;
        text-align: center;
    }
    
    .sidebar-button:hover {
        background-color: #4299E1;
    }
    
    .sidebar-button.danger {
        background-color: #742A2A;
    }
    
    .sidebar-button.danger:hover {
        background-color: #E53E3E;
    }
    
    /* Add extra padding to the Streamlit sidebar */
    [data-testid="stSidebar"] {
        background-color: #1A202C;
        padding: 2rem 1rem;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdown"] h1,
    [data-testid="stSidebar"] [data-testid="stMarkdown"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdown"] h3 {
        color: #f5f5dc !important;
    }
    
    /* Save form in sidebar */
    .save-session-form {
        background-color: #2D3748;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    
    .save-session-form h3 {
        margin-top: 0;
        margin-bottom: 10px;
        font-size: 1.2rem;
    }
    
    /* Session history list */
    .history-list {
        margin-top: 20px;
    }
    
    .history-divider {
        height: 1px;
        background-color: #4A5568;
        margin: 15px 0;
    }
    
    /* Empty state */
    .empty-history {
        text-align: center;
        padding: 30px 0;
        color: #A0AEC0;
    }
</style>
"""

# Combine all CSS
custom_css = base_custom_css + sidebar_css

# AWS API credentials - using direct values or Streamlit secrets as fallback
AWS_CREDENTIALS = {
    "access_key": st.secrets["aws"]["access_key"] if "aws" in st.secrets else "",
    "secret_key": st.secrets["aws"]["secret_key"] if "aws" in st.secrets else "",
    "region": st.secrets["aws"]["region"] if "aws" in st.secrets else "us-east-1"
}