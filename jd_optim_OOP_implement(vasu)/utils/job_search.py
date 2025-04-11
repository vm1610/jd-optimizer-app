import pandas as pd
import os
import re
import streamlit as st

class JobSearchUtility:
    """Utility for searching job descriptions across Excel files"""
    
    def __init__(self):
        """Initialize the job search utility"""
        self.position_report_df = None
        self.job_listings_df = None
        self.is_initialized = False
        self.pattern_detected = None
    
    def load_data_files(self, position_report_path, job_listings_path):
        """
        Load job data from Excel or CSV files
        
        Args:
            position_report_path (str): Path to the position report file
            job_listings_path (str): Path to the job listings file
            
        Returns:
            bool: True if files loaded successfully, False otherwise
        """
        try:
            # Load the Excel or CSV files based on extension
            if position_report_path.endswith('.xlsx') or position_report_path.endswith('.xls'):
                try:
                    self.position_report_df = pd.read_excel(position_report_path, engine='openpyxl')
                except Exception as e:
                    st.warning(f"Error with openpyxl engine: {str(e)}. Trying alternative engine...")
                    # Fall back to xlrd engine if openpyxl fails
                    self.position_report_df = pd.read_excel(position_report_path, engine='xlrd')
            else:
                # Try different encodings for CSV
                try:
                    self.position_report_df = pd.read_csv(position_report_path)
                except UnicodeDecodeError:
                    # If UTF-8 fails, try latin-1 encoding which is more permissive
                    self.position_report_df = pd.read_csv(position_report_path, encoding='latin-1')
                
            if job_listings_path.endswith('.xlsx') or job_listings_path.endswith('.xls'):
                try:
                    self.job_listings_df = pd.read_excel(job_listings_path, engine='openpyxl')
                except Exception as e:
                    st.warning(f"Error with openpyxl engine: {str(e)}. Trying alternative engine...")
                    # Fall back to xlrd engine if openpyxl fails
                    self.job_listings_df = pd.read_excel(job_listings_path, engine='xlrd')
            else:
                # Try different encodings for CSV
                try:
                    self.job_listings_df = pd.read_csv(job_listings_path)
                except UnicodeDecodeError:
                    # If UTF-8 fails, try latin-1 encoding
                    self.job_listings_df = pd.read_csv(job_listings_path, encoding='latin-1')
            
            # Convert IDs to string for consistent matching
            if 'Parent Id' in self.position_report_df.columns:
                self.position_report_df['Parent Id'] = self.position_report_df['Parent Id'].astype(str)
            
            if 'Job Id' in self.job_listings_df.columns:
                self.job_listings_df['Job Id'] = self.job_listings_df['Job Id'].astype(str)
                
            if 'Refrence Id' in self.job_listings_df.columns:
                self.job_listings_df['Refrence Id'] = self.job_listings_df['Refrence Id'].astype(str)
            
            # Identify pattern between Job ID/Reference ID and Parent ID
            self._identify_id_pattern()
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            st.error(f"Error loading data files: {str(e)}")
            return False
    
    def _identify_id_pattern(self):
        """
        Identify patterns between Job ID/Reference ID and Parent ID
        This function analyzes how the IDs relate to each other
        """
        patterns = {
            'ats_position_id_match': False,
            'direct_match': False,
            'reference_id_match': False,
            'parent_id_format': None,
            'job_id_in_parent': False,
            'reference_id_in_parent': False
        }
        
        # Check for ATS Position ID in both datasets
        if (len(self.position_report_df) > 0 and len(self.job_listings_df) > 0):
            # Check if ATS Position ID exists in both datasets
            if 'ATS Position ID' in self.position_report_df.columns and 'ATS Position ID' in self.job_listings_df.columns:
                # Convert to string for consistent matching
                self.position_report_df['ATS Position ID'] = self.position_report_df['ATS Position ID'].astype(str)
                self.job_listings_df['ATS Position ID'] = self.job_listings_df['ATS Position ID'].astype(str)
                
                # Flag that we can use ATS Position ID for matching
                patterns['ats_position_id_match'] = True
                
        # Fallback patterns if ATS Position ID isn't available
        if not patterns['ats_position_id_match'] and 'Parent Id' in self.position_report_df.columns and 'Job Id' in self.job_listings_df.columns:
            # Sample some IDs for comparison
            parent_ids = self.position_report_df['Parent Id'].sample(min(10, len(self.position_report_df))).tolist()
            job_ids = self.job_listings_df['Job Id'].sample(min(10, len(self.job_listings_df))).tolist()
            
            # Check if Job ID directly matches Parent ID
            for job_id in job_ids:
                if job_id in parent_ids:
                    patterns['direct_match'] = True
                    break
            
            # Check if Reference ID exists and matches Parent ID
            if 'Refrence Id' in self.job_listings_df.columns:
                reference_ids = self.job_listings_df['Refrence Id'].sample(min(10, len(self.job_listings_df))).tolist()
                for ref_id in reference_ids:
                    if ref_id in parent_ids:
                        patterns['reference_id_match'] = True
                        break
            
            # Check if Parent IDs contain Job IDs
            for parent_id in parent_ids:
                for job_id in job_ids:
                    if job_id in parent_id:
                        patterns['job_id_in_parent'] = True
                        break
            
            # Check if Parent IDs contain Reference IDs
            if 'Refrence Id' in self.job_listings_df.columns:
                for parent_id in parent_ids:
                    for ref_id in reference_ids:
                        if ref_id in parent_id:
                            patterns['reference_id_in_parent'] = True
                            break
            
            # Look for common patterns in Parent IDs
            parent_id_patterns = []
            for parent_id in parent_ids:
                # Check for formats like X-Y-Z, X/Y/Z, etc.
                if '-' in parent_id:
                    parent_id_patterns.append('dash_separated')
                elif '/' in parent_id:
                    parent_id_patterns.append('slash_separated')
            
            if parent_id_patterns:
                most_common = max(set(parent_id_patterns), key=parent_id_patterns.count)
                patterns['parent_id_format'] = most_common
        
        self.pattern_detected = patterns
    
    def get_dropdown_options(self):
        """
        Get formatted options for the dropdown with status indicators
        Only includes jobs that have corresponding job descriptions
        
        Returns:
            list: List of formatted dropdown options
        """
        if not self.is_initialized:
            return []
        
        options = []
        
        for _, row in self.job_listings_df.iterrows():
            # Get the required fields, handling missing columns gracefully
            job_id = str(row.get('Job Id', '')) if 'Job Id' in row else ''
            ref_id = str(row.get('Refrence Id', '')) if 'Refrence Id' in row else ''
            job_name = str(row.get('Job Name', '')) if 'Job Name' in row else ''
            client = str(row.get('Client', '')) if 'Client' in row else ''
            
            # Check if this job has a corresponding description
            has_description = False
            
            if 'Parent Id' in self.position_report_df.columns:
                # Try match with Reference Id
                if ref_id and any(self.position_report_df['Parent Id'] == ref_id):
                    has_description = True
                # Try match with Job Id
                elif any(self.position_report_df['Parent Id'] == job_id):
                    has_description = True
                # Try contains match
                elif any(self.position_report_df['Parent Id'].str.contains(job_id, na=False)):
                    has_description = True
            
            # Check for ATS Position ID match
            if not has_description and 'ATS Position ID' in self.position_report_df.columns and 'ATS Position ID' in row:
                ats_id = str(row['ATS Position ID'])
                if any(self.position_report_df['ATS Position ID'] == ats_id):
                    has_description = True
            
            # If we can't confirm it has a description, skip this job
            if not has_description:
                continue
            
            # Get job status if available
            status_emoji = "📄 "  # Default document emoji instead of colored circles
            
            # Format the dropdown option with status indicator
            option = f"{status_emoji}RRID{job_id}_{job_name}_{client}"
            
            # Add to options list
            options.append(option)
        
        return options
    def extract_ids_from_option(self, selected_option):
        """
        Extract Job Id and other IDs from the selected dropdown option
        
        Args:
            selected_option (str): The selected dropdown option with optional status emoji
            
        Returns:
            dict: Dictionary containing extracted IDs
        """
        # Default empty values
        extracted = {
            'job_id': '',
            'job_name': '',
            'client': ''
        }
        
        # Remove any emoji prefix if present
        clean_option = re.sub(r'^[^\w]*', '', selected_option)
        
        # Extract Job ID from the format: RRID[Job Id]_[Job Name]_[Client]
        job_id_match = re.search(r"RRID([^_]+)_", clean_option)
        if job_id_match:
            extracted['job_id'] = job_id_match.group(1)
        
        # Extract job name and client
        parts = clean_option.split('_')
        if len(parts) >= 2:
            # Job name might be the second part (after removing RRID prefix)
            job_name_part = parts[1]
            extracted['job_name'] = job_name_part
        
        if len(parts) >= 3:
            # Client is the last part
            extracted['client'] = parts[2]
        
        return extracted
    
    def find_job_description(self, selected_option):
        """
        Find the job description for the selected option.
        Only returns job descriptions that are actually found in the data.
        
        Args:
            selected_option (str): The selected dropdown option
            
        Returns:
            tuple: (job_description, job_details_dict) or (None, details_dict) if no description found
        """
        if not self.is_initialized:
            return None, None
        
        # Extract IDs from the selected option
        extracted_ids = self.extract_ids_from_option(selected_option)
        job_id = extracted_ids.get('job_id', '')
        
        if not job_id:
            return None, None
        
        # Find the matching job listing
        matching_job = self.job_listings_df[self.job_listings_df['Job Id'] == job_id]
        
        if matching_job.empty:
            return None, None
        
        # Get reference ID from the matching job
        reference_id = matching_job['Refrence Id'].iloc[0] if 'Refrence Id' in matching_job.columns else None
        
        # Get job status if available
        job_status = matching_job['Job Status'].iloc[0] if 'Job Status' in matching_job.columns else 'Unknown'
        
        # Format status with colored indicator
        status_display = job_status
        if job_status:
            status_lower = str(job_status).lower()
            if 'active' in status_lower:
                status_display = "🟢 Active"
            elif 'closed' in status_lower:
                status_display = "🔴 Closed"
            elif 'hold' in status_lower:
                status_display = "🟠 On Hold"
            elif 'new' in status_lower:
                status_display = "🔵 New"
            else:
                status_display = f"⚪ {job_status}"
        
        # Get ATS Position ID if available
        ats_position_id = None
        if 'ATS Position ID' in matching_job.columns:
            ats_position_id = matching_job['ATS Position ID'].iloc[0]
        
        # Try all matching strategies
        parent_match = None
        
        # Make sure position_report_df has 'Parent Id' column before trying to match
        if 'Parent Id' not in self.position_report_df.columns:
            # Create job details with available information but NO job description
            job_details = {
                'Job Id': job_id,
                'Reference Id': reference_id,
                'Job Name': extracted_ids.get('job_name', ''),
                'Client': extracted_ids.get('client', ''),
                'Status': status_display,
                'ATS Position ID': ats_position_id or 'N/A',
                'Job Description': None  # No job description
            }
            
            return None, job_details
        
        # Strategy 1: Try match between Reference Id and Parent Id (PRIMARY STRATEGY)
        if reference_id and 'Parent Id' in self.position_report_df.columns:
            parent_match = self.position_report_df[self.position_report_df['Parent Id'] == reference_id]
        
        # Fallback strategies if Reference ID doesn't yield a match
        if parent_match is None or parent_match.empty:
            # Strategy 2: Use ATS Position ID if available in both datasets
            if ats_position_id and 'ATS Position ID' in self.position_report_df.columns:
                parent_match = self.position_report_df[self.position_report_df['ATS Position ID'] == ats_position_id]
            
            # Strategy 3: Try direct match between Job Id and Parent Id
            if (parent_match is None or parent_match.empty) and 'Parent Id' in self.position_report_df.columns:
                parent_match = self.position_report_df[self.position_report_df['Parent Id'] == job_id]
            
            # Strategy 4: Try partial match where Parent Id contains Reference Id
            if (parent_match is None or parent_match.empty) and reference_id and 'Parent Id' in self.position_report_df.columns:
                parent_match = self.position_report_df[self.position_report_df['Parent Id'].str.contains(reference_id, na=False)]
            
            # Strategy 5: Try partial match where Parent Id contains Job Id
            if (parent_match is None or parent_match.empty) and 'Parent Id' in self.position_report_df.columns:
                parent_match = self.position_report_df[self.position_report_df['Parent Id'].str.contains(job_id, na=False)]
        
        # If no match found, return None for job description but still return the details
        if parent_match is None or parent_match.empty:
            job_details = {
                'Job Id': job_id,
                'Reference Id': reference_id,
                'Job Name': extracted_ids.get('job_name', ''),
                'Client': extracted_ids.get('client', ''),
                'Status': status_display,
                'Parent Id': 'N/A',
                'ATS Position ID': ats_position_id or 'N/A',
                'Job Description': None  # No job description
            }
            
            return None, job_details
        
        # Get the job description
        job_description = None
        if 'Job Description' in parent_match.columns:
            job_description = parent_match['Job Description'].iloc[0]
        else:
            # If there's no Job Description column, try to find an alternative
            content_columns = [col for col in parent_match.columns if 'description' in col.lower()]
            if content_columns:
                job_description = parent_match[content_columns[0]].iloc[0]
        
        # Handle None or NaN job description
        if pd.isna(job_description) or job_description is None:
            job_description = None
        
        # Create a dictionary with all relevant job details
        job_details = {
            'Job Id': job_id,
            'Reference Id': reference_id,
            'Job Name': extracted_ids.get('job_name', ''),
            'Client': extracted_ids.get('client', ''),
            'Status': status_display,
            'Parent Id': parent_match['Parent Id'].iloc[0] if 'Parent Id' in parent_match.columns else 'N/A',
            'ATS Position ID': ats_position_id or 'N/A',
            'Job Description': job_description
        }
        
        return job_description, job_details


def find_data_files():
    """
    Find CSV and Excel files in the specified directories that might contain job data.
    Separates files properly between position reports and job listings based on directory.
    
    Returns:
        tuple: (position_report_candidates, job_listing_candidates)
    """
    # Define specific directories
    position_report_dir = 'jd_optim_OOP_implement(vasu)/Data/Data Set/Position Report'
    job_listing_dir = 'jd_optim_OOP_implement(vasu)/Data/Data Set/Job Listing'
    
    position_report_candidates = []
    job_listing_candidates = []
    
    # Process Position Report directory
    if os.path.exists(position_report_dir):
        for f in os.listdir(position_report_dir):
            if f.endswith(('.csv', '.xlsx', '.xls')):
                file_path = os.path.join(position_report_dir, f)
                position_report_candidates.append(file_path)
    
    # Process Job Listing directory
    if os.path.exists(job_listing_dir):
        for f in os.listdir(job_listing_dir):
            if f.endswith(('.csv', '.xlsx', '.xls')):
                file_path = os.path.join(job_listing_dir, f)
                job_listing_candidates.append(file_path)
    
    # If we still don't have any candidates, try a broader search
    if not position_report_candidates and not job_listing_candidates:
        general_data_dirs = [
            'jd_optim_OOP_implement(vasu)/Data',
            'jd_optim_OOP_implement(vasu)/Data/Data Set',
            'Data',
            'Data/Data Set'
        ]
        
        for directory in general_data_dirs:
            if not os.path.exists(directory):
                continue
                
            for f in os.listdir(directory):
                if f.endswith(('.csv', '.xlsx', '.xls')):
                    file_path = os.path.join(directory, f)
                    # Classify based on filename
                    if 'position' in f.lower() or 'report' in f.lower():
                        position_report_candidates.append(file_path)
                    elif 'job' in f.lower() or 'listing' in f.lower():
                        job_listing_candidates.append(file_path)
    
    return position_report_candidates, job_listing_candidates

def render_job_search_section(state_manager):
    """
    Render the job search section in the UI
    
    Args:
        state_manager: State manager instance
    """
    from ui.common import display_subsection_header, display_warning_message, display_success_message
    
    display_subsection_header("Job Description Search")
    
    # Get job search utility from state manager
    job_search = state_manager.get('job_search_utility')
    job_search_initialized = state_manager.get('job_search_initialized', False)
    
    # Ensure job search is properly initialized
    if not job_search:
        job_search = JobSearchUtility()
        state_manager.set('job_search_utility', job_search)
    
    # File selection section
    if not job_search.is_initialized and not job_search_initialized:
        # Find data files
        position_report_candidates, job_listing_candidates = find_data_files()
        
        if len(position_report_candidates) == 0 or len(job_listing_candidates) == 0:
            display_warning_message("No data files found. Please upload the position report and job listing files.")
            
            # Add file uploaders
            position_report_file = st.file_uploader(
                "Upload Position Report File",
                type=['csv', 'xlsx', 'xls'],
                key="position_report_upload"
            )
            
            job_listings_file = st.file_uploader(
                "Upload Job Listings File",
                type=['csv', 'xlsx', 'xls'],
                key="job_listings_upload"
            )
            
            if position_report_file and job_listings_file:
                # Save uploaded files with appropriate extensions
                position_file_ext = os.path.splitext(position_report_file.name)[1]
                job_file_ext = os.path.splitext(job_listings_file.name)[1]
                
                position_temp_path = f"position_report{position_file_ext}"
                job_temp_path = f"job_listings{job_file_ext}"
                
                with open(position_temp_path, "wb") as f:
                    f.write(position_report_file.getvalue())
                
                with open(job_temp_path, "wb") as f:
                    f.write(job_listings_file.getvalue())
                
                if st.button("Initialize Job Search", key="upload_init_btn"):
                    success = job_search.load_data_files(position_temp_path, job_temp_path)
                    if success:
                        state_manager.set('job_search_initialized', True)
                        display_success_message("Files loaded successfully!")
                        st.rerun()
            
            return False
        
        # Create two columns for file selection
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Select Position Report File**")
            position_file = st.selectbox(
                "File containing Parent Id and Job Description",
                options=position_report_candidates,
                key="position_report_file"
            )
        
        with col2:
            st.markdown("**Select Job Listings File**")
            job_file = st.selectbox(
                "File containing Job Id, Reference Id, etc.",
                options=job_listing_candidates,
                key="job_listings_file"
            )
        
        # Initialize button
        if st.button("Initialize Job Search", key="init_job_search"):
            with st.spinner("Loading job data..."):
                success = job_search.load_data_files(position_file, job_file)
                
                if success:
                    state_manager.set('job_search_initialized', True)
                    display_success_message("Job data loaded successfully!")
                    st.rerun()
                    return True
        
        return False
    
    
    # Search section (only shown after initialization)
    else:
        # Display data statistics
        st.info(f"📊 Loaded {len(job_search.job_listings_df)} job listings and {len(job_search.position_report_df)} position records")
        return True