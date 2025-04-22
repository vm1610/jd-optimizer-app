import streamlit as st
import datetime
import json
import os
from streamlit.components.v1 import html

def render_session_sidebar():
    """
    Renders a collapsible sidebar with session history functionality.
    
    This sidebar allows users to:
    1. View their session history
    2. Restore previous sessions
    3. Auto-saves sessions without user prompting
    """
    
    # Check if state manager exists
    if 'state_manager' not in st.session_state:
        st.error("Session state manager not initialized.")
        return
    
    state_manager = st.session_state.state_manager
    
    # Create history directory if it doesn't exist
    history_dir = "jd_optim_history"
    os.makedirs(history_dir, exist_ok=True)
    
    # Get current role and session ID
    current_role = state_manager.get('role', 'Anonymous')
    current_session_id = state_manager.get('session_id', '')
    
    # Load session history
    session_history = load_session_history()
    
    # Add save/restore options
    with st.sidebar:
        # Add a nice header with close button
        st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h1 style="margin: 0; padding: 0; color: #4299E1;">Session History</h1>
            <button onclick="hideSidebar()" style="background: none; border: none; font-size: 24px; cursor: pointer; color: #A0AEC0;">×</button>
        </div>
        <script>
        function hideSidebar() {
            // Set URL parameter to trigger sidebar toggle on refresh
            const url = new URL(window.location);
            url.searchParams.set('sidebar_toggle', 'true');
            window.history.pushState({}, '', url);
            // Force a reload to apply the change
            window.location.reload();
        }
        </script>
        """, unsafe_allow_html=True)
        
        # Display the current user and mode
        st.caption(f"Current User: {current_role}")
        
        # Add a divider
        st.markdown('<hr style="margin: 15px 0;">', unsafe_allow_html=True)
        
        # Display session history
        st.subheader("📚 Recent Sessions")
        
        # Add a subtitle explaining auto-save
        st.markdown("""
        <div style="background-color: #2D3748; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #4299E1;">
            <p style="margin-top: 0; color: #E2E8F0;">Your sessions are automatically saved. Last 10 sessions are kept.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Filter and sort options
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Sort options
            sort_option = st.selectbox(
                "Sort By",
                ["Most Recent", "Oldest First", "Alphabetical"],
                key="history_sort"
            )
        
        with col2:
            # Show/hide auto-saves toggle
            show_autosaves = st.checkbox("Show Auto-Saves", value=True, key="show_autosaves")
        
        # Optional search by name
        search_term = st.text_input("Search", placeholder="Filter by job name", key="history_search")
        
        # Apply filters and sorting
        filtered_history = filter_session_history(session_history, search_term, [], show_autosaves)
        sorted_history = sort_session_history(filtered_history, sort_option)
        
        # Add a divider before the session list
        st.markdown('<hr style="margin: 20px 0 15px 0;">', unsafe_allow_html=True)
        
        # Display history items
        if not sorted_history:
            st.info("No saved sessions found")
        else:
            st.write(f"Found {len(sorted_history)} sessions")
            
            # Main history list
            for idx, session in enumerate(sorted_history):
                # Format the session card with improved styling
                render_session_card(session, idx, state_manager)

def render_session_card(session, idx, state_manager):
    """Render a single session card with improved styling"""
    # Get formatted timestamp
    timestamp_display = format_timestamp(session.get('timestamp', ''))
    
    # Determine if it's an auto-save
    is_autosave = "Auto" in session.get('name', '') or "Auto-Save" in session.get('tags', [])
    
    # Get JD info
    jd_name = session.get('jd_info', {}).get('source_name', 'No JD')
    
    # Get active tab
    active_tab = session.get('active_tab', 'Unknown')
    
    # Get tags
    tags = session.get('tags', [])
    
    # Create a clean session card with modern styling
    st.markdown(f"""
    <div style="background-color: {'#2C3E50' if is_autosave else '#2D3748'}; 
               padding: 15px; border-radius: 8px; margin-bottom: 15px; 
               border-left: 4px solid {'#2C5282' if is_autosave else '#4299E1'}">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <div style="font-weight: bold; font-size: 1.1rem; color: #E2E8F0;">
                {session.get('name', 'Untitled Session')}
            </div>
            <div style="font-size: 0.8rem; color: #A0AEC0;">
                {timestamp_display}
            </div>
        </div>
        <div style="font-size: 0.9rem; color: #CBD5E0; margin-top: 5px;">
            <strong>JD:</strong> {jd_name}
        </div>
        <div style="font-size: 0.9rem; color: #CBD5E0; margin-top: 3px;">
            <strong>Tab:</strong> {active_tab}
        </div>
        <div style="display: flex; flex-wrap: wrap; gap: 5px; margin-top: 10px; margin-bottom: 10px;">
            {' '.join([f'<span style="background-color: #4A5568; color: #E2E8F0; font-size: 0.7rem; padding: 2px 8px; border-radius: 12px;">{tag}</span>' for tag in tags])}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Restore", key=f"restore_{idx}", use_container_width=True):
            restore_success = restore_session(session.get('filename'), state_manager)
            if restore_success:
                st.success(f"Restored session: {session.get('name')}")
                # Force a rerun to apply changes
                st.rerun()
            else:
                st.error("Failed to restore session")
    
    with col2:
        if st.button("Delete", key=f"delete_{idx}", use_container_width=True):
            delete_session(session.get('filename'))
            st.warning(f"Deleted session: {session.get('name')}")
            # Force a rerun to update list
            st.rerun()

def restore_session(filename, state_manager):
    """Restore a session from a file"""
    history_dir = "jd_optim_history"
    filepath = os.path.join(history_dir, filename)
    
    if not os.path.exists(filepath):
        return False
    
    try:
        with open(filepath, 'r') as f:
            session_data = json.load(f)
        
        # Extract the state export
        state_export = session_data.get('state_export', '{}')
        
        # Import state into state manager
        if state_manager.import_state(state_export):
            # Set the active tab
            active_tab = session_data.get('active_tab')
            if active_tab:
                state_manager.set('active_tab', active_tab)
            
            # Mark this session as loaded
            state_manager.set('loaded_from_history', True)
            state_manager.set('loaded_from_filename', filename)
            state_manager.set('loaded_session_name', session_data.get('name', 'Unnamed Session'))
            
            # Add notification
            state_manager.add_notification({
                'type': 'session_loaded',
                'session_name': session_data.get('name', 'Unnamed Session'),
                'timestamp': datetime.datetime.now().isoformat()
            })
            
            # Flag significant change for auto-save
            state_manager.set('significant_change', True)
            
            return True
    except Exception as e:
        print(f"Error restoring session: {e}")
    
    return False

def delete_session(filename):
    """Delete a session file"""
    history_dir = "jd_optim_history"
    filepath = os.path.join(history_dir, filename)
    
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    
    return False

def load_session_history():
    """Load all available session history"""
    history_dir = "jd_optim_history"
    os.makedirs(history_dir, exist_ok=True)
    
    history = []
    
    for filename in os.listdir(history_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(history_dir, filename)
            
            try:
                with open(filepath, 'r') as f:
                    session_data = json.load(f)
                
                # Add filename to session data for reference
                if 'filename' not in session_data:
                    session_data['filename'] = filename
                
                history.append(session_data)
            except Exception as e:
                print(f"Error loading session file {filename}: {e}")
    
    return history

def filter_session_history(history, search_term, tag_filter, show_autosaves=True):
    """Filter session history by search term and tags"""
    filtered_history = history
    
    # Apply auto-save filter if not showing auto-saves
    if not show_autosaves:
        filtered_history = [
            session for session in filtered_history
            if not ("Auto" in session.get('name', '') or "Auto-Save" in session.get('tags', []))
        ]
    
    # Apply search term filter
    if search_term:
        search_term = search_term.lower()
        filtered_history = [
            session for session in filtered_history
            if search_term in session.get('name', '').lower() or
               search_term in session.get('jd_info', {}).get('source_name', '').lower() or
               any(search_term in tag.lower() for tag in session.get('tags', []))
        ]
    
    # Apply tag filter
    if tag_filter:
        filtered_history = [
            session for session in filtered_history
            if all(tag in session.get('tags', []) for tag in tag_filter)
        ]
    
    return filtered_history

def sort_session_history(history, sort_option):
    """Sort session history based on sort option"""
    if sort_option == "Most Recent":
        return sorted(history, key=lambda x: x.get('timestamp', ''), reverse=True)
    elif sort_option == "Oldest First":
        return sorted(history, key=lambda x: x.get('timestamp', ''))
    elif sort_option == "Alphabetical":
        return sorted(history, key=lambda x: x.get('name', '').lower())
    
    return history

def format_timestamp(timestamp):
    """Format timestamp for display"""
    try:
        dt = datetime.datetime.fromisoformat(timestamp)
        return dt.strftime("%b %d, %Y • %I:%M %p")
    except:
        return timestamp

def render_sidebar_toggle():
    """Render a sidebar toggle button"""
    toggle_html = """
    <style>
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
    .sidebar-toggle:hover {
        background-color: #4299E1;
    }
    </style>
    <button class="sidebar-toggle" onclick="toggleSidebar()">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 18H21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M3 12H21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <path d="M3 6H21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
    </button>
    <script>
    function toggleSidebar() {
        // Set URL parameter to trigger sidebar toggle
        const url = new URL(window.location);
        url.searchParams.set('sidebar_toggle', 'true');
        window.history.pushState({}, '', url);
        // Force a reload to apply the change
        window.location.reload();
    }
    </script>
    """
    html(toggle_html)