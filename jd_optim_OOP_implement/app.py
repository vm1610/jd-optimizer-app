import streamlit as st
import os
import datetime
import uuid
import time
import json
from pathlib import Path

# Import components
from config import set_page_config, custom_css
from utils.file_utils import save_enhanced_jd
from utils.job_search import JobSearchUtility
from models.job_description_analyzer import JobDescriptionAnalyzer
from models.job_description_agent import JobDescriptionAgent
from jdoptim_logger import JDOptimLogger
from state_manager import StateManager

# Import UI components
from ui.common import render_header, render_role_selector, render_role_specific_tabs, display_section_header, auto_save_session
from ui.jd_optimization import render_jd_optimization_page
from ui.candidate_ranking import render_candidate_ranking_page
from ui.interview_prep import render_interview_prep_page
from ui.client_feedback import render_client_feedback_page
from ui.jd_creation import render_jd_creation_page

# Import the session sidebar component
from session_sidebar import render_session_sidebar, render_sidebar_toggle

def init_session_state():
    """Initialize global session state manager"""
    if 'state_manager' not in st.session_state:
        # Create state manager with built-in defaults
        st.session_state.state_manager = StateManager()
        state_manager = st.session_state.state_manager
        
        # Initialize essential global state
        state_manager.set('session_id', str(uuid.uuid4()))
        state_manager.set('role', 'Recruiter')  # Default role
        state_manager.set('active_tab', "JD Optimization")  # Default tab
        
        # Initialize empty containers for job descriptions
        state_manager.set('jd_repository', {
            'original': None,           # Original JD content
            'source_name': None,        # Name/source of JD
            'unique_id': None,          # Unique ID for caching
            'enhanced_versions': [],    # List of enhanced versions 
            'selected_version_idx': 0,  # User-selected version
            'final_version': None,      # Final enhanced version
        })
        
        # Initialize feedback repository
        state_manager.set('feedback_repository', {
            'history': [],              # All feedback items
            'current_feedback': '',     # Current feedback text
            'current_type': 'General Feedback'  # Current feedback type
        })
        
        # Initialize analytics repository
        state_manager.set('analytics_repository', {
            'original_scores': None,
            'version_scores': {},
            'final_scores': None
        })
        
        # Initialize resume repository
        state_manager.set('resume_repository', {
            'pools': [],
            'ranked_candidates': [],
            'analysis_results': None
        })
        
        # Register notification bus
        state_manager.set('notifications', [])
        
        # Initialize job search utility
        state_manager.set('job_search_utility', JobSearchUtility())
        state_manager.set('job_search_initialized', False)
        
        # Auto-save tracking
        state_manager.set('last_autosave_time', time.time())
        state_manager.set('significant_change', False)
        
        # Sidebar state
        state_manager.set('sidebar_visible', False)

def get_or_create_logger():
    """Get existing logger from session state or create a new one with proper integration"""
    state_manager = st.session_state.state_manager
    
    # First check if we have a logger in session state
    if 'logger' in st.session_state:
        logger = st.session_state.logger
        
        # Ensure logger has latest role
        if logger.username != state_manager.get('role'):
            logger.username = state_manager.get('role')
            logger.current_state["username"] = state_manager.get('role')
            logger._save_state()
            
        return logger
    
    # Try to load existing session by ID
    session_id = state_manager.get('session_id')
    try:
        logger = JDOptimLogger.load_session(session_id)
        if logger:
            # Update role if it changed
            if logger.username != state_manager.get('role'):
                logger.username = state_manager.get('role')
                logger.current_state["username"] = state_manager.get('role')
                logger._save_state()
            
            st.session_state.logger = logger
            return logger
    except Exception as e:
        print(f"Failed to load existing session: {e}")
    
    # Create a new logger with the current role
    logger = JDOptimLogger(username=state_manager.get('role'))
    
    # Update session ID in state manager
    state_manager.set('session_id', logger.session_id)
    st.session_state.logger = logger
    
    return logger

def check_for_autosave(state_manager):
    """
    Check if it's time to auto-save based on time elapsed or significant changes
    
    Args:
        state_manager: The state manager instance
    """
    # Get current time and last save time
    current_time = time.time()
    last_save_time = state_manager.get('last_autosave_time', 0)
    significant_change = state_manager.get('significant_change', False)
    
    # Auto-save conditions:
    # 1. Time-based: If it's been more than 2 minutes since the last save
    # 2. Change-based: If there's been a significant change flagged
    
    time_threshold = 2 * 60  # 2 minutes in seconds
    time_based_save = (current_time - last_save_time) > time_threshold
    
    if time_based_save or significant_change:
        # Only save if we have a job description
        jd_repository = state_manager.get('jd_repository', {})
        if jd_repository.get('original'):
            # Get JD name for context
            jd_name = jd_repository.get('source_name', 'Unnamed JD')
            
            # Auto-save the session
            auto_save_session(state_manager, f"Auto: {jd_name}")
            
            # Reset tracking flags
            state_manager.set('last_autosave_time', current_time)
            state_manager.set('significant_change', False)
            
            # Manage session history to keep only the last 10
            prune_session_history(10)
            
            return True
            
    return False

def prune_session_history(max_sessions=10):
    """
    Keep only the most recent sessions up to max_sessions
    
    Args:
        max_sessions (int): Maximum number of sessions to keep
    """
    try:
        # Create history directory if it doesn't exist
        history_dir = "jd_optim_history"
        os.makedirs(history_dir, exist_ok=True)
        
        # Get all session files
        session_files = []
        for filename in os.listdir(history_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(history_dir, filename)
                try:
                    # Get file stats
                    file_stat = os.stat(filepath)
                    # Add to list with creation time
                    session_files.append({
                        'filepath': filepath,
                        'filename': filename,
                        'mtime': file_stat.st_mtime
                    })
                except Exception as e:
                    print(f"Error checking file {filename}: {e}")
        
        # Sort by modification time (newest first)
        session_files.sort(key=lambda x: x['mtime'], reverse=True)
        
        # If we have more than max_sessions, delete the oldest ones
        if len(session_files) > max_sessions:
            for file_info in session_files[max_sessions:]:
                try:
                    os.remove(file_info['filepath'])
                    print(f"Pruned old session file: {file_info['filename']}")
                except Exception as e:
                    print(f"Error removing file {file_info['filename']}: {e}")
    except Exception as e:
        print(f"Error pruning session history: {e}")

def main():
    """Main function with improved integration between app components and role-based access"""
    # Configure the Streamlit page
    set_page_config()

    # Apply custom CSS
    st.markdown(custom_css, unsafe_allow_html=True)

    # Initialize session state
    init_session_state()
    
    # Get state manager and logger
    state_manager = st.session_state.state_manager
    logger = get_or_create_logger()

    # Handle auto-save check (invisible to user)
    check_for_autosave(state_manager)

    # Important: Handle sidebar toggle from URL params or session state
    if 'sidebar_toggle' in st.experimental_get_query_params():
        st.session_state.sidebar_visible = not st.session_state.get('sidebar_visible', False)
        # Clear query params
        st.experimental_set_query_params()
        
    # Add direct sidebar toggle button in a fixed position
    st.markdown("""
    <style>
    .sidebar-toggle-button {
        position: fixed;
        top: 70px;
        left: 10px;
        background-color: #3182CE;
        color: white;
        border: none;
        border-radius: 4px;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        cursor: pointer;
        z-index: 1000;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .sidebar-toggle-button:hover {
        background-color: #4299E1;
    }
    </style>
    
    <button 
        class="sidebar-toggle-button" 
        onclick="toggleSidebar()" 
        title="Show/Hide Session History">☰</button>
    
    <script>
    function toggleSidebar() {
        // Set URL parameter to trigger sidebar toggle on refresh
        const url = new URL(window.location);
        url.searchParams.set('sidebar_toggle', 'true');
        window.history.pushState({}, '', url);
        // Force a reload to apply the change
        window.location.reload();
    }
    </script>
    """, unsafe_allow_html=True)

    # If sidebar is visible, render it
    if st.session_state.get('sidebar_visible', False):
        render_session_sidebar()

    # Render header with logo and title
    render_header()
    
    # Render role selector (updates state manager)
    render_role_selector(state_manager)
    
    # Get current role
    current_role = state_manager.get('role')
    
    # Role-specific tab configuration
    if current_role == "Employee":
        # Employee only sees Interview Prep
        tabs = ["Interview Prep"]
        state_manager.set('active_tab', "Interview Prep")
    else:
        # Both Recruiters and Hiring Managers see all tabs including JD Creation
        tabs = ["JD Creation", "JD Optimization", "Candidate Ranking", "Feedback Loop", "Interview Prep"]
        
        # Default to JD Creation if coming from another role or if current tab is not in available tabs
        if state_manager.get('active_tab') not in tabs:
            state_manager.set('active_tab', "JD Creation")
    
    # Render tabs based on role
    render_role_specific_tabs(state_manager, tabs)
    
    # Initialize the analyzer and agent as shared services
    analyzer = JobDescriptionAnalyzer()
    agent = JobDescriptionAgent(model_id="anthropic.claude-3-haiku-20240307-v1:0")
    
    # Create service container for shared resources
    services = {
        'logger': logger,
        'analyzer': analyzer,
        'agent': agent,
        'state_manager': state_manager
    }
    
    # Check for notifications from other tabs
    process_notifications(state_manager)
    
    # Render the appropriate page based on active tab
    active_tab = state_manager.get('active_tab')
    
    if active_tab == "JD Creation":
        render_jd_creation_page(services)
    elif active_tab == "JD Optimization":
        render_jd_optimization_page(services)
    elif active_tab == "Candidate Ranking":
        render_candidate_ranking_page(services)
    elif active_tab == "Feedback Loop":
        render_client_feedback_page(services)
    elif active_tab == "Interview Prep":
        render_interview_prep_page()
    
    # Show notification if loaded from history
    if state_manager.get('loaded_from_history'):
        loaded_session_name = state_manager.get('loaded_session_name', 'Unknown Session')
        st.success(f"⏱️ Session restored: {loaded_session_name}")
        
        # Flag a significant change when loading from history
        state_manager.set('significant_change', True)
        
        # Reset the flag to prevent showing again on next render
        state_manager.set('loaded_from_history', False)
    
    # Footer with company info
    st.markdown("---")
    footer_col1, footer_col2 = st.columns([4, 1])
    
    with footer_col1:
        st.caption("JD Agent | Made by Apexon")
    
    with footer_col2:
        st.caption(f"v2.1 - {datetime.datetime.now().strftime('%Y')}")

def process_notifications(state_manager):
    """Process any pending notifications between tabs"""
    notifications = state_manager.get('notifications', [])
    
    if notifications:
        # Process each notification
        for notification in notifications:
            notify_type = notification.get('type')
            
            if notify_type == 'jd_selected':
                # Job description was selected in another tab
                st.success(f"Using job description: {notification.get('source_name')}")
                # Flag for auto-save
                state_manager.set('significant_change', True)
            
            elif notify_type == 'feedback_added':
                # Feedback was added in another tab
                st.info(f"New feedback added in {notification.get('origin')} tab")
                # Flag for auto-save
                state_manager.set('significant_change', True)
            
            elif notify_type == 'version_enhanced':
                # Job description was enhanced in another tab
                st.success(f"Job description enhanced in {notification.get('origin')} tab")
                # Flag for auto-save
                state_manager.set('significant_change', True)
                
            elif notify_type == 'session_loaded':
                # Session was loaded from history
                st.success(f"Session restored: {notification.get('session_name')}")
        
        # Clear notifications after processing
        state_manager.set('notifications', [])

if __name__ == "__main__":
    main()