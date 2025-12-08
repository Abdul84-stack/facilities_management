import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime
import io
import os

# =============================================
# CUSTOM CSS FOR ENHANCED UI/UX
# =============================================
def inject_custom_css():
    st.markdown("""
    <style>
    .app-title {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        text-align: center;
        padding: 10px;
        margin-bottom: 20px;
    }
    
    .card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        border-left: 5px solid #3b82f6;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# =============================================
# PAGE CONFIGURATION
# =============================================
st.set_page_config(
    page_title="A-Z Facilities Management Pro APP™",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS
inject_custom_css()

# =============================================
# DEBUG MODE
# =============================================
DEBUG_MODE = True  # Set to False in production

# =============================================
# DATABASE SETUP - SIMPLIFIED VERSION
# =============================================
def init_database():
    try:
        conn = sqlite3.connect('facilities_management.db', check_same_thread=False)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                vendor_type TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Maintenance requests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS maintenance_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                location TEXT,
                facility_type TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT DEFAULT 'Pending',
                created_by TEXT NOT NULL,
                assigned_vendor TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_date TIMESTAMP,
                completion_notes TEXT,
                job_breakdown TEXT,
                invoice_amount REAL,
                invoice_number TEXT,
                requesting_dept_approval INTEGER DEFAULT 0,
                facilities_manager_approval INTEGER DEFAULT 0,
                department_approval_date TIMESTAMP,
                manager_approval_date TIMESTAMP
            )
        ''')
        
        # Insert sample users if table is empty
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            sample_users = [
                ('facility_user', '0123456', 'facility_user', None),
                ('facility_manager', '0123456', 'facility_manager', None),
                ('hvac_vendor', '0123456', 'vendor', 'HVAC'),
                ('generator_vendor', '0123456', 'vendor', 'Generator'),
                ('fixture_vendor', '0123456', 'vendor', 'Fixture and Fittings'),
                ('building_vendor', '0123456', 'vendor', 'Building Maintenance'),
            ]
            
            for username, password, role, vendor_type in sample_users:
                try:
                    cursor.execute(
                        'INSERT INTO users (username, password, role, vendor_type) VALUES (?, ?, ?, ?)',
                        (username, password, role, vendor_type)
                    )
                except Exception as e:
                    if DEBUG_MODE:
                        print(f"Error inserting user {username}: {e}")
        
        conn.commit()
        conn.close()
        if DEBUG_MODE:
            print("✅ Database initialized successfully")
        
    except Exception as e:
        print(f"❌ Database initialization error: {e}")

# Initialize database
init_database()

# =============================================
# DATABASE FUNCTIONS
# =============================================
def get_connection():
    return sqlite3.connect('facilities_management.db', check_same_thread=False)

def execute_query(query, params=()):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        columns = [column[0] for column in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            result = {}
            for i, column in enumerate(columns):
                result[column] = row[i]
            results.append(result)
        
        conn.close()
        return results
    except Exception as e:
        if DEBUG_MODE:
            print(f"❌ Query error: {e}")
        return []

def execute_update(query, params=()):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        if DEBUG_MODE:
            print(f"❌ Update error: {e}")
        return False

# =============================================
# FIXED AUTHENTICATION FUNCTION
# =============================================
def authenticate_user(username, password):
    """Check if username and password match"""
    if DEBUG_MODE:
        print(f"🔐 Attempting login for: username='{username}', password='{password}'")
    
    try:
        # First, let's see what users exist in the database
        all_users = execute_query('SELECT username, password, role FROM users')
        if DEBUG_MODE:
            print(f"📊 Total users in database: {len(all_users)}")
            for user in all_users:
                print(f"   User: {user}")
        
        # Get the specific user
        users = execute_query('SELECT * FROM users WHERE username = ?', (username,))
        
        if DEBUG_MODE:
            print(f"🔍 Found {len(users)} user(s) with username '{username}'")
        
        if users and len(users) > 0:
            user = users[0]
            stored_password = str(user.get('password', ''))
            input_password = str(password)
            
            if DEBUG_MODE:
                print(f"📝 Stored password: '{stored_password}'")
                print(f"📝 Input password: '{input_password}'")
                print(f"📝 Password match: {stored_password == input_password}")
            
            # Check if password matches
            if stored_password == input_password:
                if DEBUG_MODE:
                    print(f"✅ Authentication successful for {username}")
                return user
            else:
                if DEBUG_MODE:
                    print(f"❌ Password mismatch for {username}")
        else:
            if DEBUG_MODE:
                print(f"❌ No user found with username '{username}'")
        
        return None
        
    except Exception as e:
        if DEBUG_MODE:
            print(f"💥 Authentication error: {e}")
        return None

# =============================================
# SIMPLE LOGIN PAGE WITH DEBUG
# =============================================
def show_enhanced_login():
    st.markdown("<h1 class='app-title'>🏢 A-Z Facilities Management Pro APP™</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6b7280;'>Professional Facilities Management Solution</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #1e3a8a; text-align: center;'>🔐 Login to Your Account</h3>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="Enter your username", value="facility_user")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", value="0123456")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                login_button = st.form_submit_button("🚀 Login", use_container_width=True)
            
            if login_button:
                if not username or not password:
                    st.error("❌ Please enter both username and password")
                else:
                    with st.spinner("Authenticating..."):
                        user = authenticate_user(username, password)
                        if user:
                            st.session_state.user = user
                            st.success("✅ Login successful! Redirecting...")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # DEBUG: Check database button
        if DEBUG_MODE:
            with st.expander("🔧 Debug Tools", expanded=False):
                if st.button("Check Database Users"):
                    users = execute_query('SELECT username, password, role FROM users ORDER BY username')
                    if users:
                        st.write(f"Found {len(users)} user(s):")
                        for user in users:
                            st.write(f"- **{user['username']}**: password='{user['password']}', role={user['role']}")
                    else:
                        st.warning("No users found in database")
                
                if st.button("Reset Database"):
                    if os.path.exists('facilities_management.db'):
                        os.remove('facilities_management.db')
                        st.success("Database reset. Please refresh the page.")
                        st.stop()
        
        # Sample credentials
        with st.expander("📋 Sample Credentials", expanded=True):
            st.markdown("""
            **👥 Users:**
            - Facility User: `facility_user` / `0123456`
            - Facility Manager: `facility_manager` / `0123456`
            
            **🏢 Vendors:**
            - HVAC Solutions Inc.: `hvac_vendor` / `0123456`
            - Generator Pros Ltd.: `generator_vendor` / `0123456`
            - Fixture Masters Co.: `fixture_vendor` / `0123456`
            - Building Care Services: `building_vendor` / `0123456`
            """)
        
        st.markdown("---")
        st.markdown("<p style='text-align: center; color: #6b7280;'>© 2025 A-Z Facilities Management Pro APP™. Developed by Abdulahi Ibrahim.</p>", unsafe_allow_html=True)

# =============================================
# SAFE DATA ACCESS FUNCTIONS
# =============================================
def safe_get(data, key, default=None):
    if not data:
        return default
    return data.get(key, default)

def safe_str(value, default="N/A"):
    if value is None:
        return default
    return str(value)

# =============================================
# DASHBOARD FUNCTIONS
# =============================================
def show_user_dashboard():
    st.markdown("<h1 class='app-title'>📊 Dashboard Overview</h1>", unsafe_allow_html=True)
    st.success(f"Welcome, {st.session_state.user['username']}! You are logged in as a Facility User.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 📝 Create Request")
        st.write("Create a new maintenance request")
        if st.button("Create New", use_container_width=True):
            st.session_state.show_create = True
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 📋 My Requests")
        st.write("View your maintenance requests")
        if st.button("View Requests", use_container_width=True):
            st.session_state.show_requests = True
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### ✅ Approvals")
        st.write("Approve completed jobs")
        if st.button("Review Approvals", use_container_width=True):
            st.session_state.show_approvals = True
        st.markdown("</div>", unsafe_allow_html=True)

def show_manager_dashboard():
    st.markdown("<h1 class='app-title'>📊 Dashboard Overview</h1>", unsafe_allow_html=True)
    st.success(f"Welcome, {st.session_state.user['username']}! You are logged in as a Facility Manager.")

def show_vendor_dashboard():
    st.markdown("<h1 class='app-title'>📊 Dashboard Overview</h1>", unsafe_allow_html=True)
    st.success(f"Welcome, {st.session_state.user['username']}! You are logged in as a Vendor.")

# =============================================
# CREATE REQUEST FUNCTION
# =============================================
def show_create_request():
    st.markdown("<h1 class='app-title'>📝 Create Maintenance Request</h1>", unsafe_allow_html=True)
    
    with st.form("create_request_form"):
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Request Title *", placeholder="Brief title of the maintenance request", value="AC Repair")
            location = st.selectbox(
                "Location *",
                ["Water Treatment Plant", "Finance", "HR", "Admin", "Common Area", 
                 "Production", "Warehouse", "Office Building", "Laboratory", "Parking Lot"],
                index=3
            )
            facility_type = st.selectbox(
                "Facility Type *",
                ["HVAC (Cooling Systems)", "Generator Maintenance", "Fixture and Fittings", 
                 "Building Maintenance", "HSE", "Space Management", "Electrical", "Plumbing"],
                index=0
            )
        
        with col2:
            priority = st.selectbox("Priority *", ["Low", "Medium", "High", "Critical"], index=1)
        
        description = st.text_area(
            "Description *", 
            height=100,
            placeholder="Please provide detailed description of the maintenance request...",
            value="AC unit in Admin office not cooling properly. Needs inspection and repair."
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            submitted = st.form_submit_button("📤 Submit Request", use_container_width=True)
        with col2:
            if st.form_submit_button("← Back to Dashboard", type="secondary", use_container_width=True):
                st.session_state.show_create = False
                st.rerun()
        
        if submitted:
            if not all([title, description, location, facility_type, priority]):
                st.error("❌ Please fill in all required fields (*)")
            else:
                success = execute_update(
                    'INSERT INTO maintenance_requests (title, description, location, facility_type, priority, created_by) VALUES (?, ?, ?, ?, ?, ?)',
                    (title, description, location, facility_type, priority, st.session_state.user['username'])
                )
                if success:
                    st.success("✅ Maintenance request created successfully!")
                    # Clear the form
                    st.rerun()
                else:
                    st.error("❌ Failed to create request")

# =============================================
# MY REQUESTS FUNCTION
# =============================================
def show_my_requests():
    st.markdown("<h1 class='app-title'>📋 My Maintenance Requests</h1>", unsafe_allow_html=True)
    
    # Get user's requests
    requests = execute_query(
        'SELECT * FROM maintenance_requests WHERE created_by = ? ORDER BY created_date DESC',
        (st.session_state.user['username'],)
    )
    
    if st.button("← Back to Dashboard", type="secondary"):
        st.session_state.show_requests = False
        st.rerun()
    
    if not requests:
        st.info("📭 No maintenance requests found")
        return
    
    st.write(f"Found {len(requests)} request(s)")
    
    for req in requests:
        with st.expander(f"📋 Request #{safe_get(req, 'id')}: {safe_str(safe_get(req, 'title'))}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Title:** {safe_str(safe_get(req, 'title'))}")
                st.write(f"**Description:** {safe_str(safe_get(req, 'description'))}")
                st.write(f"**Location:** {safe_str(safe_get(req, 'location'), 'Common Area')}")
                st.write(f"**Facility Type:** {safe_str(safe_get(req, 'facility_type'))}")
            
            with col2:
                st.write(f"**Priority:** {safe_str(safe_get(req, 'priority'))}")
                st.write(f"**Status:** {safe_str(safe_get(req, 'status'))}")
                st.write(f"**Created Date:** {safe_str(safe_get(req, 'created_date'))}")
                if safe_get(req, 'assigned_vendor'):
                    st.write(f"**Assigned Vendor:** {safe_str(safe_get(req, 'assigned_vendor'))}")

# =============================================
# DEPARTMENT APPROVAL FUNCTION
# =============================================
def show_department_approval():
    st.markdown("<h1 class='app-title'>✅ Department Approval</h1>", unsafe_allow_html=True)
    
    if st.button("← Back to Dashboard", type="secondary"):
        st.session_state.show_approvals = False
        st.rerun()
    
    # Get requests that need department approval
    pending_approvals = execute_query('''
        SELECT * FROM maintenance_requests 
        WHERE created_by = ? 
        AND status = 'Completed' 
        AND requesting_dept_approval = 0
        ORDER BY completed_date DESC
    ''', (st.session_state.user['username'],))
    
    if not pending_approvals:
        st.info("🎉 No jobs pending your department approval")
        return
    
    st.write(f"Found {len(pending_approvals)} job(s) awaiting your approval")
    
    for req in pending_approvals:
        with st.expander(f"🔄 Job #{safe_get(req, 'id')}: {safe_str(safe_get(req, 'title'))}"):
            st.write(f"**Title:** {safe_str(safe_get(req, 'title'))}")
            st.write(f"**Description:** {safe_str(safe_get(req, 'description'))}")
            st.write(f"**Completed Date:** {safe_str(safe_get(req, 'completed_date'))}")
            
            if st.button(f"Approve Job #{safe_get(req, 'id')}", key=f"approve_{safe_get(req, 'id')}"):
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if execute_update(
                    '''UPDATE maintenance_requests 
                    SET requesting_dept_approval = 1, 
                        department_approval_date = ?
                    WHERE id = ?''',
                    (current_time, safe_get(req, 'id'))
                ):
                    st.success(f"✅ Job #{safe_get(req, 'id')} approved!")
                    st.rerun()

# =============================================
# MAIN APPLICATION ROUTING
# =============================================
def show_main_app():
    user = st.session_state.user
    role = user['role']
    
    with st.sidebar:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color: #1e3a8a;'>👋 Welcome, {user['username']}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p><strong>Role:</strong> {role.replace('_', ' ').title()}</p>", unsafe_allow_html=True)
        if DEBUG_MODE:
            st.markdown(f"<p><small>User ID: {user.get('id', 'N/A')}</small></p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        if role == 'facility_user':
            menu_options = ["📊 Dashboard", "📝 Create Request", "📋 My Requests", "✅ Department Approval"]
        elif role == 'facility_manager':
            menu_options = ["📊 Dashboard", "🛠️ Manage Requests", "✅ Final Approval"]
        else:  # vendor
            menu_options = ["📊 Dashboard", "🔧 Assigned Jobs", "✅ Completed Jobs"]
        
        selected_menu = st.radio("Navigation", menu_options, label_visibility="collapsed")
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()
    
    # Check for direct page requests
    if 'show_create' in st.session_state and st.session_state.show_create:
        show_create_request()
    elif 'show_requests' in st.session_state and st.session_state.show_requests:
        show_my_requests()
    elif 'show_approvals' in st.session_state and st.session_state.show_approvals:
        show_department_approval()
    else:
        # Regular menu navigation
        if selected_menu == "📊 Dashboard":
            if role == 'facility_user':
                show_user_dashboard()
            elif role == 'facility_manager':
                show_manager_dashboard()
            else:
                show_vendor_dashboard()
        elif selected_menu == "📝 Create Request":
            show_create_request()
        elif selected_menu == "📋 My Requests":
            show_my_requests()
        elif selected_menu == "✅ Department Approval":
            show_department_approval()
        elif selected_menu == "🛠️ Manage Requests":
            st.info("Manage Requests page - Under development")
        elif selected_menu == "✅ Final Approval":
            st.info("Final Approval page - Under development")
        elif selected_menu == "🔧 Assigned Jobs":
            st.info("Assigned Jobs page - Under development")
        elif selected_menu == "✅ Completed Jobs":
            st.info("Completed Jobs page - Under development")

# =============================================
# MAIN FUNCTION
# =============================================
def main():
    # Initialize session state
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'show_create' not in st.session_state:
        st.session_state.show_create = False
    if 'show_requests' not in st.session_state:
        st.session_state.show_requests = False
    if 'show_approvals' not in st.session_state:
        st.session_state.show_approvals = False
    
    if st.session_state.user is None:
        show_enhanced_login()
    else:
        show_main_app()

if __name__ == "__main__":
    main()
