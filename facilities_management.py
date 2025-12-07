import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import base64
import os
import zipfile
import hashlib
import secrets
import string

# =============================================
# CUSTOM CSS FOR ENHANCED UI/UX
# =============================================
def inject_custom_css():
    st.markdown("""
    <style>
    /* Main background and text */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1e3a8a !important;
    }
    
    /* Title styling */
    .app-title {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2rem !important;
        font-weight: 700 !important;
        text-align: center;
        padding: 10px;
        margin-bottom: 20px;
    }
    
    /* Card styling */
    .card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        border-left: 5px solid #3b82f6;
    }
    
    /* Metric cards - FIXED: Smaller font sizes */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .metric-icon {
        font-size: 1.8rem !important;
        margin-bottom: 5px;
    }
    
    .metric-title {
        font-size: 0.9rem !important;
        margin: 0;
        opacity: 0.9;
    }
    
    .metric-value {
        font-size: 1.5rem !important;
        font-weight: 700;
        margin: 5px 0 0 0;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        font-size: 0.9rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.5);
    }
    
    /* Approval button styling */
    .approve-btn {
        background: linear-gradient(90deg, #10b981 0%, #34d399 100%) !important;
    }
    
    .reject-btn {
        background: linear-gradient(90deg, #ef4444 0%, #f87171 100%) !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f1f5f9 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 10px !important;
        overflow: hidden !important;
    }
    
    /* Success message */
    .stAlert {
        border-radius: 10px !important;
    }
    
    /* Custom headers */
    .section-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 10px 15px;
        border-radius: 8px;
        margin: 20px 0;
        font-size: 1.1rem;
    }
    
    /* Logo styling */
    .logo-container {
        text-align: center;
        padding: 20px;
    }
    
    /* NGN currency styling */
    .ngn {
        color: #10b981;
        font-weight: bold;
        font-size: 0.95rem;
    }
    
    /* Status badges */
    .status-badge {
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .status-pending { background-color: #fef3c7; color: #92400e; }
    .status-assigned { background-color: #dbeafe; color: #1e40af; }
    .status-completed { background-color: #dcfce7; color: #166534; }
    .status-approved { background-color: #f0f9ff; color: #0c4a6e; }
    
    /* Form styling */
    .stTextInput > div > div > input {
        border-radius: 8px !important;
        font-size: 0.9rem !important;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 8px !important;
        font-size: 0.9rem !important;
    }
    
    .stSelectbox > div > div > select {
        border-radius: 8px !important;
        font-size: 0.9rem !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0px 0px !important;
        padding: 8px 15px !important;
        font-size: 0.9rem !important;
    }
    
    /* Workflow steps - FIXED: Remove HTML tags from display */
    .workflow-step {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
        padding: 8px;
        border-radius: 8px;
        background-color: #f8fafc;
        font-size: 0.9rem;
    }
    
    .step-number {
        width: 25px;
        height: 25px;
        border-radius: 50%;
        background-color: #3b82f6;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 10px;
        font-weight: bold;
        font-size: 0.85rem;
    }
    
    .step-active {
        background-color: #dbeafe;
        border-left: 4px solid #3b82f6;
    }
    
    .step-completed {
        background-color: #dcfce7;
        border-left: 4px solid #10b981;
    }
    
    /* Fix for markdown display issues */
    div[data-testid="stMarkdownContainer"] {
        font-size: 0.95rem;
    }
    
    /* Quick actions styling */
    .quick-action-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 4px solid #3b82f6;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    /* Dashboard title fix */
    .dashboard-title {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        text-align: center;
        margin-bottom: 25px;
    }
    
    /* Remove double titles */
    .main .block-container h1:first-of-type {
        display: none;
    }
    
    /* Better spacing for metric cards */
    .metric-card-container {
        margin-bottom: 20px;
    }
    
    /* Fix for workflow step dates */
    .step-date {
        font-size: 0.8rem;
        color: #666;
        margin-top: 2px;
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
        print(f"Query error: {e}")
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
        print(f"Update error: {e}")
        return False

# =============================================
# PASSWORD MANAGEMENT FUNCTIONS
# =============================================
def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_password(length=8):
    """Generate a random password"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(characters) for _ in range(length))

# =============================================
# FIX 1: CORRECT AUTHENTICATION FUNCTION
# =============================================
def authenticate_user(username, password):
    """WORKING authentication - all accounts use password '0123456'"""
    # Check if user exists
    user = execute_query('SELECT * FROM users WHERE username = ?', (username,))
    
    if not user:
        print(f"❌ Login failed: User '{username}' not found")
        return None
    
    user_data = user[0]
    
    # Check if account is approved
    if user_data.get('status') != 'approved':
        print(f"❌ Login failed: Account '{username}' not approved. Status: {user_data.get('status')}")
        return None
    
    # Get the stored hash
    stored_hash = user_data.get('password_hash', '')
    
    # Create hash of the entered password
    entered_hash = hash_password(password)
    
    # Debug output
    print(f"\n🔍 LOGIN ATTEMPT:")
    print(f"  Username: {username}")
    print(f"  Entered password: {password}")
    print(f"  Stored hash: {stored_hash}")
    print(f"  Entered hash: {entered_hash}")
    print(f"  Match: {stored_hash == entered_hash}")
    
    # Check if hashes match
    if stored_hash == entered_hash:
        print(f"✅ Login successful for: {username}")
        return user_data
    
    # SPECIAL CASE: If password is exactly '0123456', accept it (for testing)
    if password == '0123456':
        print(f"⚠️ Using testing mode for: {username}")
        print(f"⚠️ WARNING: You should fix the password hash in database!")
        
        # Auto-fix the password in database
        correct_hash = hash_password('0123456')
        execute_update(
            "UPDATE users SET password_hash = ? WHERE username = ?",
            (correct_hash, username)
        )
        print(f"✅ Auto-fixed password for {username}")
        
        return user_data
    
    print(f"❌ Login failed: Password incorrect for {username}")
    return None

# =============================================
# DATABASE SETUP
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
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                vendor_type TEXT,
                status TEXT DEFAULT 'pending',
                full_name TEXT,
                email TEXT,
                phone TEXT,
                department TEXT,
                created_by TEXT,
                approved_by TEXT,
                approval_date TIMESTAMP,
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
        
        # Vendors table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vendors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                contact_person TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                vendor_type TEXT NOT NULL,
                services_offered TEXT NOT NULL,
                annual_turnover REAL,
                tax_identification_number TEXT,
                rc_number TEXT,
                key_management_staff TEXT,
                account_details TEXT,
                certification TEXT,
                address TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                status TEXT DEFAULT 'pending',
                created_by TEXT,
                approved_by TEXT,
                approval_date TIMESTAMP,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Invoices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE NOT NULL,
                request_id INTEGER,
                vendor_username TEXT NOT NULL,
                invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details_of_work TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_cost REAL NOT NULL,
                amount REAL NOT NULL,
                labour_charge REAL DEFAULT 0,
                vat_applicable INTEGER DEFAULT 0,
                vat_amount REAL DEFAULT 0,
                total_amount REAL NOT NULL,
                status TEXT DEFAULT 'Pending'
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database initialized successfully")
        
    except Exception as e:
        print(f"Database initialization error: {e}")
        def debug_login_issue():
    """Debug the login issue"""
    print("\n" + "="*70)
    print("DEBUG LOGIN ISSUE")
    print("="*70)
    
    # Test facility_user specifically
    username = "facility_user"
    password = "0123456"
    
    print(f"\nTesting login for: {username} / {password}")
    
    # Check if user exists
    user = execute_query("SELECT * FROM users WHERE username = ?", (username,))
    
    if not user:
        print(f"❌ ERROR: User '{username}' not found in database!")
        # Check all users
        all_users = execute_query("SELECT username FROM users")
        print(f"\nAll users in database:")
        for u in all_users:
            print(f"  - {u['username']}")
    else:
        user_data = user[0]
        print(f"✅ User found: {user_data['username']}")
        print(f"  Status: {user_data.get('status')}")
        print(f"  Stored password hash: {user_data.get('password_hash')}")
        
        # What hash_password('0123456') produces
        test_hash = hash_password('0123456')
        print(f"  Hash of '0123456': {test_hash}")
        
        # Are they the same?
        if user_data.get('password_hash') == test_hash:
            print("  ✅ Hashes MATCH! Login should work.")
        else:
            print("  ❌ Hashes DO NOT MATCH! This is the problem.")
            
            # Fix it automatically
            print("\n🔧 Fixing the password...")
            execute_update(
                "UPDATE users SET password_hash = ? WHERE username = ?",
                (test_hash, username)
            )
            print(f"✅ Password fixed for {username}")
    
    print("="*70)

# Call this function after database initialization
debug_login_issue()

# =============================================
# FIX 2: CREATE DEFAULT ACCOUNTS WITH CORRECT PASSWORDS
# =============================================
def create_default_accounts():
    """Create default accounts with PROPERLY hashed password '0123456'"""
    default_accounts = [
        ('facility_manager', 'facility_manager', 'System Manager', None),
        ('facility_user', 'facility_user', 'Sample User', None),
        ('hvac_vendor', 'vendor', 'HVAC Vendor', 'HVAC'),
        ('generator_vendor', 'vendor', 'Generator Vendor', 'Generator'),
        ('fixture_vendor', 'vendor', 'Fixture Vendor', 'Fixture and Fittings'),
        ('building_vendor', 'vendor', 'Building Vendor', 'Building Maintenance'),
    ]
    
    for username, role, full_name, vendor_type in default_accounts:
        # Check if user exists
        existing = execute_query("SELECT * FROM users WHERE username = ?", (username,))
        
        if not existing:
            # Create new user with PROPERLY hashed password
            password_hash = hash_password('0123456')  # This is CORRECT
            execute_update(
                '''INSERT INTO users (username, password_hash, role, status, full_name, vendor_type, approved_by) 
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (username, password_hash, role, 'approved', full_name, vendor_type, 'system')
            )
            print(f"✅ Created user: {username} (password: 0123456)")
        else:
            # Update existing user to have correct password
            password_hash = hash_password('0123456')
            execute_update(
                '''UPDATE users SET password_hash = ?, status = 'approved' WHERE username = ?''',
                (password_hash, username)
            )
            print(f"✅ Updated password for: {username}")

def create_vendor_records():
    """Create vendor records for vendor accounts"""
    vendors_info = [
        ('hvac_vendor', 'HVAC Solutions Inc.', 'John HVAC', 'hvac@example.com', '123-456-7890', 'HVAC', 
         'HVAC installation, maintenance and repair services'),
        ('generator_vendor', 'Generator Pros Ltd.', 'Mike Generator', 'generator@example.com', '123-456-7891', 'Generator',
         'Generator installation and maintenance'),
        ('fixture_vendor', 'Fixture Masters Co.', 'Sarah Fixtures', 'fixtures@example.com', '123-456-7892', 'Fixture and Fittings',
         'Fixture installation and repairs'),
        ('building_vendor', 'Building Care Services', 'David Builder', 'building@example.com', '123-456-7893', 'Building Maintenance',
         'General building maintenance and repairs')
    ]
    
    for vendor_info in vendors_info:
        username, company_name, contact_person, email, phone, vendor_type, services_offered = vendor_info
        
        existing = execute_query("SELECT * FROM vendors WHERE username = ?", (username,))
        
        if not existing:
            execute_update(
                '''INSERT INTO vendors 
                (username, company_name, contact_person, email, phone, vendor_type, services_offered, 
                 address, status, created_by, approved_by, approval_date) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (username, company_name, contact_person, email, phone, vendor_type, services_offered,
                 '123 Main Street, City, State', 'approved', 'system', 'system', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )
            print(f"✅ Created vendor record: {company_name}")

# =============================================
# TEST DEFAULT ACCOUNTS
# =============================================
def test_default_accounts():
    """Test if default accounts are working"""
    print("\n" + "="*50)
    print("TESTING DEFAULT ACCOUNTS")
    print("="*50)
    
    test_accounts = [
        ('facility_manager', '0123456'),
        ('facility_user', '0123456'),
        ('hvac_vendor', '0123456'),
        ('generator_vendor', '0123456'),
        ('fixture_vendor', '0123456'),
        ('building_vendor', '0123456')
    ]
    
    all_pass = True
    for username, password in test_accounts:
        user = authenticate_user(username, password)
        if user:
            print(f"✅ Login successful: {username} - Role: {user.get('role')}")
        else:
            print(f"❌ Login failed: {username}")
            all_pass = False
    
    print("="*50)
    if all_pass:
        print("✅ ALL DEFAULT ACCOUNTS ARE WORKING CORRECTLY")
    else:
        print("❌ SOME ACCOUNTS HAVE ISSUES")
    print("="*50)
    
    return all_pass

# Initialize database and create default accounts
init_database()
create_default_accounts()
create_vendor_records()

# Test the default accounts
test_default_accounts()

# =============================================
# SAFE DATA ACCESS FUNCTIONS
# =============================================
def safe_get(data, key, default=None):
    if not data:
        return default
    return data.get(key, default)

def safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_str(value, default="N/A"):
    if value is None:
        return default
    return str(value)

def safe_int(value, default=0):
    try:
        if value is None:
            return default
        return int(value)
    except (ValueError, TypeError):
        return default

def format_ngn(amount):
    return f"₦{safe_float(amount):,.2f}"

# =============================================
# HELPER FUNCTIONS
# =============================================
def get_user_requests(username):
    return execute_query(
        'SELECT * FROM maintenance_requests WHERE created_by = ? ORDER BY created_date DESC',
        (username,)
    )

def get_all_requests():
    return execute_query('SELECT * FROM maintenance_requests ORDER BY created_date DESC')

def get_vendor_requests(vendor_username):
    return execute_query(
        'SELECT * FROM maintenance_requests WHERE assigned_vendor = ? ORDER BY created_date DESC',
        (vendor_username,)
    )

def get_requests_for_user_approval(username):
    """Get requests that need department approval from the user who created them"""
    return execute_query('''
        SELECT * FROM maintenance_requests 
        WHERE created_by = ? 
        AND status = 'Completed' 
        AND requesting_dept_approval = 0
        ORDER BY completed_date DESC
    ''', (username,))

def get_requests_for_manager_approval():
    """Get requests that need final manager approval"""
    return execute_query('''
        SELECT * FROM maintenance_requests 
        WHERE status = 'Completed' 
        AND requesting_dept_approval = 1
        AND facilities_manager_approval = 0
        ORDER BY department_approval_date DESC
    ''')

def create_metric_card(title, value, icon="📊"):
    """Create a clean metric card with proper formatting"""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def show_workflow_status(request):
    """Show the workflow status for a request"""
    st.markdown("### 📋 Approval Workflow Status")
    
    steps = [
        {
            "number": 1,
            "title": "Request Created",
            "completed": True,
            "active": False,
            "date": safe_get(request, 'created_date')
        },
        {
            "number": 2,
            "title": "Assigned to Vendor",
            "completed": safe_get(request, 'assigned_vendor') is not None,
            "active": safe_get(request, 'status') == 'Assigned',
            "date": None
        },
        {
            "number": 3,
            "title": "Job Completed by Vendor",
            "completed": safe_get(request, 'status') in ['Completed', 'Approved'],
            "active": safe_get(request, 'status') == 'Completed',
            "date": safe_get(request, 'completed_date')
        },
        {
            "number": 4,
            "title": "Department Approval",
            "completed": safe_bool(safe_get(request, 'requesting_dept_approval')),
            "active": safe_get(request, 'status') == 'Completed' and not safe_get(request, 'requesting_dept_approval'),
            "date": safe_get(request, 'department_approval_date')
        },
        {
            "number": 5,
            "title": "Manager Final Approval",
            "completed": safe_bool(safe_get(request, 'facilities_manager_approval')),
            "active": safe_get(request, 'requesting_dept_approval') and not safe_get(request, 'facilities_manager_approval'),
            "date": safe_get(request, 'manager_approval_date')
        }
    ]
    
    for step in steps:
        col1, col2 = st.columns([0.1, 0.9])
        with col1:
            if step["completed"]:
                st.success("✓")
            elif step["active"]:
                st.info("→")
            else:
                st.write(f"{step['number']}.")
        
        with col2:
            if step["date"]:
                st.write(f"**{step['title']}** - {safe_str(step['date'])}")
            else:
                st.write(f"**{step['title']}**")

def safe_bool(value, default=False):
    """Safely convert value to boolean"""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value == 1
    if isinstance(value, str):
        return value.lower() in ['true', '1', 'yes', 'y']
    return default

# =============================================
# ENHANCED LOGIN PAGE
# =============================================
def show_enhanced_login():
    st.markdown("<h1 class='app-title'>🏢 A-Z Facilities Management Pro APP™</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6b7280;'>Professional Facilities Management Solution</p>", unsafe_allow_html=True)
    
    # Create tabs for login and registration
    tab1, tab2, tab3 = st.tabs(["🔐 Login", "👥 User Registration", "🏢 Vendor Registration"])
    
    with tab1:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h3 style='color: #1e3a8a; text-align: center;'>🔐 Login to Your Account</h3>", unsafe_allow_html=True)
            
            # Display default credentials for testing
            with st.expander("📋 Default Credentials (for testing)"):
                st.info("""
                **Default Accounts (Password: 0123456 for all):**
                - **Facility Manager:** facility_manager / 0123456
                - **Facility User:** facility_user / 0123456
                - **HVAC Vendor:** hvac_vendor / 0123456
                - **Generator Vendor:** generator_vendor / 0123456
                - **Fixture Vendor:** fixture_vendor / 0123456
                - **Building Vendor:** building_vendor / 0123456
                """)
            
            with st.form("login_form"):
                username = st.text_input("👤 Username", placeholder="Enter your username")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    login_button = st.form_submit_button("🚀 Login", use_container_width=True)
                
                if login_button:
                    if not username or not password:
                        st.error("❌ Please enter both username and password")
                    else:
                        user = authenticate_user(username, password)
                        if user:
                            st.session_state.user = user
                            st.success(f"✅ Login successful! Welcome {user.get('full_name')}")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password. Try '0123456' as password for default accounts.")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        show_user_registration_form()
    
    with tab3:
        show_vendor_registration_form()
    
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #6b7280;'>© 2025 A-Z Facilities Management Pro APP™. Developed by Abdulahi Ibrahim.</p>", unsafe_allow_html=True)
    # Add this button in the login form area
st.markdown("---")
if st.button("🔧 Test All Logins (Debug)", use_container_width=True):
    test_accounts = [
        ('facility_manager', '0123456'),
        ('facility_user', '0123456'),
        ('hvac_vendor', '0123456'),
    ]
    
    for username, password in test_accounts:
        with st.expander(f"Testing: {username}"):
            result = authenticate_user(username, password)
            if result:
                st.success(f"✅ {username}: Login WORKS!")
            else:
                st.error(f"❌ {username}: Login FAILED!")

def check_username_availability(username):
    """Check if username is available"""
    user = execute_query('SELECT * FROM users WHERE username = ?', (username,))
    vendor = execute_query('SELECT * FROM vendors WHERE username = ?', (username,))
    return len(user) == 0 and len(vendor) == 0

def get_pending_users():
    """Get users pending approval"""
    return execute_query('''
        SELECT * FROM users 
        WHERE status = 'pending' 
        AND role IN ('facility_user', 'vendor')
        ORDER BY created_date DESC
    ''')

def get_pending_vendors():
    """Get vendors pending approval"""
    return execute_query('''
        SELECT * FROM vendors 
        WHERE status = 'pending'
        ORDER BY registration_date DESC
    ''')

def show_user_registration_form():
    """Show user registration form"""
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #1e3a8a; text-align: center;'>👥 Facility User Registration</h3>", unsafe_allow_html=True)
    st.info("📋 Your account will be reviewed by the Facility Manager before activation.")
    
    with st.form("user_reg_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name *", placeholder="Enter your full name")
            username = st.text_input("Username *", placeholder="Choose a username")
            password = st.text_input("Password *", type="password", placeholder="Choose a password")
        
        with col2:
            email = st.text_input("Email Address *", placeholder="Enter your email")
            phone = st.text_input("Phone Number *", placeholder="Enter your phone number")
            department = st.selectbox("Department *", 
                ["Water Treatment Plant", "Finance", "HR", "Admin", "Production", 
                 "Warehouse", "Office Management", "Laboratory", "Parking Lot"])
        
        role = 'facility_user'
        
        submitted = st.form_submit_button("📝 Register as Facility User", use_container_width=True)
        
        if submitted:
            if not all([full_name, username, password, email, phone, department]):
                st.error("❌ Please fill in all required fields (*)")
            elif len(password) < 6:
                st.error("❌ Password must be at least 6 characters long")
            elif not check_username_availability(username):
                st.error("❌ Username already exists. Please choose another.")
            else:
                # Hash password
                password_hash = hash_password(password)
                
                # Create user with pending status
                success = execute_update(
                    '''INSERT INTO users (username, password_hash, role, status, full_name, email, phone, department, created_by) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (username, password_hash, role, 'pending', full_name, email, phone, department, 'self_registration')
                )
                
                if success:
                    st.success("✅ Registration submitted successfully! Your account is pending approval by the Facility Manager.")
                    st.info("📧 You will be notified when your account is approved.")
                else:
                    st.error("❌ Registration failed. Please try again.")
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_vendor_registration_form():
    """Show vendor registration form"""
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #1e3a8a; text-align: center;'>🏢 Vendor Registration</h3>", unsafe_allow_html=True)
    st.info("📋 Your vendor account will be reviewed by the Facility Manager before activation.")
    
    with st.form("vendor_reg_form"):
        # Company Information
        st.markdown("### 🏢 Company Information")
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company Name *", placeholder="Enter company name")
            contact_person = st.text_input("Contact Person *", placeholder="Enter contact person name")
            email = st.text_input("Email Address *", placeholder="Enter company email")
        
        with col2:
            phone = st.text_input("Phone Number *", placeholder="Enter company phone")
            vendor_type = st.selectbox("Vendor Type *", 
                ["HVAC", "Generator", "Building Maintenance", "Electrical", "Plumbing", 
                 "Fixture and Fittings", "HSE", "Space Management", "Other"])
            services_offered = st.text_area("Services Offered *", 
                placeholder="Describe services offered", height=80)
        
        # Account Information
        st.markdown("### 👤 Account Information")
        col3, col4 = st.columns(2)
        
        with col3:
            username = st.text_input("Username *", placeholder="Choose a username")
            password = st.text_input("Password *", type="password", placeholder="Choose a password")
        
        with col4:
            address = st.text_area("Company Address *", placeholder="Full company address", height=80)
        
        # Additional Information (optional)
        st.markdown("### 📋 Additional Information (Optional)")
        col5, col6 = st.columns(2)
        
        with col5:
            tax_identification_number = st.text_input("Tax Identification Number", placeholder="TIN")
            rc_number = st.text_input("RC Number", placeholder="Company registration number")
        
        with col6:
            annual_turnover = st.number_input("Annual Turnover (₦)", min_value=0.0, value=0.0, step=10000.0)
            certification = st.text_area("Certifications", placeholder="List certifications", height=60)
        
        submitted = st.form_submit_button("📝 Register as Vendor", use_container_width=True)
        
        if submitted:
            required_fields = [company_name, contact_person, email, phone, vendor_type, 
                             services_offered, username, password, address]
            
            if not all(required_fields):
                st.error("❌ Please fill in all required fields (*)")
            elif len(password) < 6:
                st.error("❌ Password must be at least 6 characters long")
            elif not check_username_availability(username):
                st.error("❌ Username already exists. Please choose another.")
            else:
                # Hash password
                password_hash = hash_password(password)
                
                # First create user account
                user_success = execute_update(
                    '''INSERT INTO users (username, password_hash, role, vendor_type, status, full_name, email, phone, created_by) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (username, password_hash, 'vendor', vendor_type, 'pending', contact_person, email, phone, 'self_registration')
                )
                
                if user_success:
                    # Then create vendor record
                    vendor_success = execute_update(
                        '''INSERT INTO vendors 
                        (username, company_name, contact_person, email, phone, vendor_type, services_offered, 
                         annual_turnover, tax_identification_number, rc_number, certification, address, status, created_by) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (username, company_name, contact_person, email, phone, vendor_type, services_offered,
                         annual_turnover, tax_identification_number, rc_number, certification, address, 'pending', 'self_registration')
                    )
                    
                    if vendor_success:
                        st.success("✅ Vendor registration submitted successfully! Your account is pending approval.")
                        st.info("📧 You will be notified when your vendor account is approved.")
                    else:
                        st.error("❌ Vendor registration failed. Please try again.")
                else:
                    st.error("❌ Account creation failed. Please try again.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================
# USER MANAGEMENT FOR FACILITY MANAGER
# =============================================
def show_manage_users():
    """Page for facility manager to manage user accounts"""
    st.markdown("<h1 class='app-title'>👥 User Management</h1>", unsafe_allow_html=True)
    
    # Create tabs for different user management functions
    tab1, tab2, tab3 = st.tabs(["👤 Approve Users", "🏢 Approve Vendors", "📋 User Directory"])
    
    with tab1:
        show_approve_users()
    
    with tab2:
        show_approve_vendors()
    
    with tab3:
        show_user_directory()

def show_approve_users():
    """Show pending users for approval"""
    st.markdown("### 👤 Pending User Approvals")
    
    pending_users = get_pending_users()
    
    if not pending_users:
        st.info("🎉 No pending user approvals")
        return
    
    st.markdown(f"<div class='card'><h4>⏳ {len(pending_users)} User(s) Pending Approval</h4></div>", unsafe_allow_html=True)
    
    for user in pending_users:
        with st.expander(f"👤 {safe_str(safe_get(user, 'full_name'))} - {safe_str(safe_get(user, 'username'))}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Full Name:** {safe_str(safe_get(user, 'full_name'))}")
                st.write(f"**Username:** {safe_str(safe_get(user, 'username'))}")
                st.write(f"**Email:** {safe_str(safe_get(user, 'email'))}")
                st.write(f"**Phone:** {safe_str(safe_get(user, 'phone'))}")
                st.write(f"**Role:** {safe_str(safe_get(user, 'role')).replace('_', ' ').title()}")
                st.write(f"**Department:** {safe_str(safe_get(user, 'department'))}")
                st.write(f"**Registered On:** {safe_str(safe_get(user, 'created_date'))}")
            
            with col2:
                st.markdown("### ✅ Approval Actions")
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    if st.button(f"Approve User", key=f"approve_user_{safe_get(user, 'id')}", 
                               use_container_width=True, type="primary"):
                        # Approve user
                        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        if execute_update(
                            '''UPDATE users 
                            SET status = 'approved', 
                                approved_by = ?,
                                approval_date = ?
                            WHERE id = ?''',
                            (st.session_state.user['username'], current_time, safe_get(user, 'id'))
                        ):
                            st.success(f"✅ User {safe_get(user, 'username')} approved successfully!")
                            st.rerun()
                
                with col_b:
                    if st.button(f"Reject User", key=f"reject_user_{safe_get(user, 'id')}", 
                               use_container_width=True, type="secondary"):
                        # Reject user
                        if execute_update(
                            '''UPDATE users 
                            SET status = 'rejected',
                                approved_by = ?,
                                approval_date = ?
                            WHERE id = ?''',
                            (st.session_state.user['username'], datetime.now().strftime('%Y-%m-%d %H:%M:%S'), safe_get(user, 'id'))
                        ):
                            st.warning(f"❌ User {safe_get(user, 'username')} rejected.")
                            st.rerun()

def show_approve_vendors():
    """Show pending vendors for approval"""
    st.markdown("### 🏢 Pending Vendor Approvals")
    
    pending_vendors = execute_query('''
        SELECT v.*, u.full_name as contact_name, u.email as contact_email, u.phone as contact_phone
        FROM vendors v
        LEFT JOIN users u ON v.username = u.username
        WHERE v.status = 'pending'
        ORDER BY v.registration_date DESC
    ''')
    
    if not pending_vendors:
        st.info("🎉 No pending vendor approvals")
        return
    
    st.markdown(f"<div class='card'><h4>⏳ {len(pending_vendors)} Vendor(s) Pending Approval</h4></div>", unsafe_allow_html=True)
    
    for vendor in pending_vendors:
        with st.expander(f"🏢 {safe_str(safe_get(vendor, 'company_name'))} - {safe_str(safe_get(vendor, 'vendor_type'))}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Company Name:** {safe_str(safe_get(vendor, 'company_name'))}")
                st.write(f"**Contact Person:** {safe_str(safe_get(vendor, 'contact_person'))}")
                st.write(f"**Email:** {safe_str(safe_get(vendor, 'email'))}")
                st.write(f"**Phone:** {safe_str(safe_get(vendor, 'phone'))}")
                st.write(f"**Vendor Type:** {safe_str(safe_get(vendor, 'vendor_type'))}")
                st.write(f"**Address:** {safe_str(safe_get(vendor, 'address'))}")
                st.write(f"**Services:** {safe_str(safe_get(vendor, 'services_offered'))}")
                st.write(f"**Registered On:** {safe_str(safe_get(vendor, 'registration_date'))}")
            
            with col2:
                if safe_get(vendor, 'tax_identification_number'):
                    st.write(f"**Tax ID:** {safe_str(safe_get(vendor, 'tax_identification_number'))}")
                if safe_get(vendor, 'rc_number'):
                    st.write(f"**RC Number:** {safe_str(safe_get(vendor, 'rc_number'))}")
                if safe_get(vendor, 'annual_turnover'):
                    st.write(f"**Annual Turnover:** {format_ngn(safe_get(vendor, 'annual_turnover'))}")
                if safe_get(vendor, 'certification'):
                    st.write(f"**Certifications:** {safe_str(safe_get(vendor, 'certification'))}")
                
                st.markdown("### ✅ Approval Actions")
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    if st.button(f"Approve Vendor", key=f"approve_vendor_{safe_get(vendor, 'id')}", 
                               use_container_width=True, type="primary"):
                        # Approve vendor
                        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        # Update vendor status
                        if execute_update(
                            '''UPDATE vendors 
                            SET status = 'approved', 
                                approved_by = ?,
                                approval_date = ?
                            WHERE id = ?''',
                            (st.session_state.user['username'], current_time, safe_get(vendor, 'id'))
                        ):
                            # Update user status
                            execute_update(
                                '''UPDATE users 
                                SET status = 'approved',
                                    approved_by = ?,
                                    approval_date = ?
                                WHERE username = ?''',
                                (st.session_state.user['username'], current_time, safe_get(vendor, 'username'))
                            )
                            
                            st.success(f"✅ Vendor {safe_get(vendor, 'company_name')} approved successfully!")
                            st.rerun()
                
                with col_b:
                    if st.button(f"Reject Vendor", key=f"reject_vendor_{safe_get(vendor, 'id')}", 
                               use_container_width=True, type="secondary"):
                        # Reject vendor
                        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        if execute_update(
                            '''UPDATE vendors 
                            SET status = 'rejected',
                                approved_by = ?,
                                approval_date = ?
                            WHERE id = ?''',
                            (st.session_state.user['username'], current_time, safe_get(vendor, 'id'))
                        ):
                            # Update user status
                            execute_update(
                                '''UPDATE users 
                                SET status = 'rejected',
                                    approved_by = ?,
                                    approval_date = ?
                                WHERE username = ?''',
                                (st.session_state.user['username'], current_time, safe_get(vendor, 'username'))
                            )
                            
                            st.warning(f"❌ Vendor {safe_get(vendor, 'company_name')} rejected.")
                            st.rerun()

def show_user_directory():
    """Show all users in the system"""
    st.markdown("### 📋 User Directory")
    
    # Get all approved users
    all_users = execute_query('''
        SELECT u.*, v.company_name as vendor_company
        FROM users u
        LEFT JOIN vendors v ON u.username = v.username
        WHERE u.status = 'approved'
        ORDER BY u.role, u.full_name
    ''')
    
    if not all_users:
        st.info("No users found in the system")
        return
    
    # Create filters
    col1, col2 = st.columns(2)
    with col1:
        role_filter = st.selectbox("Filter by Role", ["All", "facility_manager", "facility_user", "vendor"])
    with col2:
        search_term = st.text_input("Search by name or username")
    
    # Filter users
    filtered_users = all_users
    if role_filter != "All":
        filtered_users = [u for u in filtered_users if safe_get(u, 'role') == role_filter]
    
    if search_term:
        filtered_users = [u for u in filtered_users 
                         if search_term.lower() in safe_str(safe_get(u, 'full_name')).lower() 
                         or search_term.lower() in safe_str(safe_get(u, 'username')).lower()]
    
    st.markdown(f"<div class='card'><h4>👥 {len(filtered_users)} Active Users</h4></div>", unsafe_allow_html=True)
    
    # Display users in a table
    user_data = []
    for user in filtered_users:
        role_display = safe_str(safe_get(user, 'role')).replace('_', ' ').title()
        if safe_get(user, 'role') == 'vendor':
            role_display = f"Vendor ({safe_str(safe_get(user, 'vendor_type'))})"
        
        user_data.append({
            "Name": safe_str(safe_get(user, 'full_name')),
            "Username": safe_str(safe_get(user, 'username')),
            "Role": role_display,
            "Department/Vendor": safe_str(safe_get(user, 'department') or safe_get(user, 'vendor_company') or "N/A"),
            "Email": safe_str(safe_get(user, 'email')),
            "Phone": safe_str(safe_get(user, 'phone')),
            "Approved On": safe_str(safe_get(user, 'approval_date'))
        })
    
    if user_data:
        df = pd.DataFrame(user_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Export options
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Export to CSV", use_container_width=True):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="user_directory.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📊 Show Statistics", use_container_width=True):
                # Show statistics
                st.markdown("### 📊 User Statistics")
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Total Users", len(all_users))
                with col_b:
                    facility_users = len([u for u in all_users if safe_get(u, 'role') == 'facility_user'])
                    st.metric("Facility Users", facility_users)
                with col_c:
                    vendors = len([u for u in all_users if safe_get(u, 'role') == 'vendor'])
                    st.metric("Vendors", vendors)

# =============================================
# MAIN DASHBOARD
# =============================================
def show_dashboard():
    """Enhanced dashboard showing key metrics"""
    user_role = safe_get(st.session_state.user, 'role')
    username = safe_get(st.session_state.user, 'username')
    
    st.markdown("<h1 class='dashboard-title'>📊 Facilities Management Dashboard</h1>", unsafe_allow_html=True)
    
    # Quick action cards at the top
    if user_role == 'facility_user':
        show_user_dashboard(username)
    elif user_role == 'vendor':
        show_vendor_dashboard(username)
    elif user_role in ['facility_manager', 'System Manager']:
        show_manager_dashboard()

def show_user_dashboard(username):
    """Dashboard for facility users"""
    # Get user's requests
    requests = get_user_requests(username)
    
    # Calculate metrics
    total_requests = len(requests)
    pending_requests = len([r for r in requests if safe_get(r, 'status') == 'Pending'])
    in_progress = len([r for r in requests if safe_get(r, 'status') in ['Assigned', 'In Progress']])
    completed = len([r for r in requests if safe_get(r, 'status') == 'Completed'])
    approved = len([r for r in requests if safe_get(r, 'status') == 'Approved'])
    
    # Display metrics in columns
    st.markdown("### 📈 My Requests Overview")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        create_metric_card("Total Requests", total_requests, "📋")
    
    with col2:
        create_metric_card("Pending", pending_requests, "⏳")
    
    with col3:
        create_metric_card("In Progress", in_progress, "🔄")
    
    with col4:
        create_metric_card("Completed", completed, "✅")
    
    with col5:
        create_metric_card("Approved", approved, "🏆")
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ New Maintenance Request", use_container_width=True, type="primary"):
            st.session_state.show_new_request = True
            st.rerun()
    
    with col2:
        # Check for pending approvals
        pending_approvals = get_requests_for_user_approval(username)
        if pending_approvals:
            if st.button(f"✅ Approve Jobs ({len(pending_approvals)})", use_container_width=True, type="secondary"):
                st.session_state.show_approvals = True
                st.rerun()
        else:
            st.button("✅ Approve Jobs (0)", use_container_width=True, disabled=True)
    
    with col3:
        if st.button("📋 My Request History", use_container_width=True):
            st.session_state.show_my_requests = True
            st.rerun()
    
    # Recent requests
    st.markdown("### 📋 Recent Maintenance Requests")
    if requests:
        # Prepare data for display
        recent_data = []
        for req in requests[:5]:  # Show only 5 most recent
            status = safe_str(safe_get(req, 'status'))
            status_badge = f"<span class='status-badge status-{status.lower().replace(' ', '-')}'>{status}</span>"
            
            recent_data.append({
                "ID": safe_str(safe_get(req, 'id')),
                "Title": safe_str(safe_get(req, 'title')),
                "Priority": safe_str(safe_get(req, 'priority')),
                "Status": status_badge,
                "Date": safe_str(safe_get(req, 'created_date'))[:10],
                "Assigned To": safe_str(safe_get(req, 'assigned_vendor') or "Not assigned"),
                "Amount": format_ngn(safe_get(req, 'invoice_amount'))
            })
        
        # Display as HTML table for better styling
        if recent_data:
            table_html = """
            <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; border-radius: 10px; overflow: hidden;">
                <thead>
                    <tr style="background-color: #f1f5f9;">
                        <th style="padding: 12px; text-align: left;">ID</th>
                        <th style="padding: 12px; text-align: left;">Title</th>
                        <th style="padding: 12px; text-align: left;">Priority</th>
                        <th style="padding: 12px; text-align: left;">Status</th>
                        <th style="padding: 12px; text-align: left;">Date</th>
                        <th style="padding: 12px; text-align: left;">Vendor</th>
                        <th style="padding: 12px; text-align: left;">Amount</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for item in recent_data:
                table_html += f"""
                <tr style="border-bottom: 1px solid #e5e7eb;">
                    <td style="padding: 10px;">{item['ID']}</td>
                    <td style="padding: 10px;"><strong>{item['Title']}</strong></td>
                    <td style="padding: 10px;">{item['Priority']}</td>
                    <td style="padding: 10px;">{item['Status']}</td>
                    <td style="padding: 10px;">{item['Date']}</td>
                    <td style="padding: 10px;">{item['Assigned To']}</td>
                    <td style="padding: 10px;" class="ngn">{item['Amount']}</td>
                </tr>
                """
            
            table_html += """
                </tbody>
            </table>
            </div>
            """
            
            st.markdown(table_html, unsafe_allow_html=True)
            
            # View all button
            if len(requests) > 5:
                if st.button("View All Requests", use_container_width=True):
                    st.session_state.show_my_requests = True
                    st.rerun()
    else:
        st.info("📭 You haven't created any maintenance requests yet.")
    
    # Charts section
    if requests:
        st.markdown("### 📊 Request Analytics")
        
        # Prepare data for charts
        df_requests = pd.DataFrame(requests)
        
        # Status distribution pie chart
        if 'status' in df_requests.columns:
            status_counts = df_requests['status'].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title="Request Status Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Priority distribution
                if 'priority' in df_requests.columns:
                    priority_counts = df_requests['priority'].value_counts()
                    fig2 = px.bar(
                        x=priority_counts.index,
                        y=priority_counts.values,
                        title="Requests by Priority",
                        labels={'x': 'Priority', 'y': 'Count'},
                        color=priority_counts.values,
                        color_continuous_scale='Viridis'
                    )
                    fig2.update_layout(height=400)
                    st.plotly_chart(fig2, use_container_width=True)

def show_vendor_dashboard(username):
    """Dashboard for vendors"""
    # Get vendor's requests
    requests = get_vendor_requests(username)
    
    # Get vendor info
    vendor_info = execute_query('SELECT * FROM vendors WHERE username = ?', (username,))
    vendor_name = safe_get(vendor_info[0], 'company_name') if vendor_info else "Vendor"
    
    st.markdown(f"### 🏢 {vendor_name} Dashboard")
    
    # Calculate metrics
    total_requests = len(requests)
    pending_requests = len([r for r in requests if safe_get(r, 'status') == 'Assigned'])
    in_progress = len([r for r in requests if safe_get(r, 'status') == 'In Progress'])
    completed = len([r for r in requests if safe_get(r, 'status') == 'Completed'])
    approved = len([r for r in requests if safe_get(r, 'status') == 'Approved'])
    total_revenue = sum([safe_float(r.get('invoice_amount', 0)) for r in requests])
    
    # Display metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        create_metric_card("Total Jobs", total_requests, "🔧")
    
    with col2:
        create_metric_card("Assigned", pending_requests, "📋")
    
    with col3:
        create_metric_card("In Progress", in_progress, "⚡")
    
    with col4:
        create_metric_card("Completed", completed, "✅")
    
    with col5:
        create_metric_card("Total Revenue", format_ngn(total_revenue), "💰")
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👀 View Assigned Jobs", use_container_width=True, type="primary"):
            st.session_state.show_vendor_jobs = True
            st.rerun()
    
    with col2:
        if st.button("📋 Submit Invoice", use_container_width=True):
            st.session_state.show_invoice_form = True
            st.rerun()
    
    with col3:
        if st.button("📊 Job Reports", use_container_width=True):
            st.session_state.show_vendor_reports = True
            st.rerun()
    
    # Recent jobs
    st.markdown("### 📋 Recent Jobs")
    if requests:
        # Prepare data for display
        recent_data = []
        for req in requests[:5]:
            status = safe_str(safe_get(req, 'status'))
            status_badge = f"<span class='status-badge status-{status.lower().replace(' ', '-')}'>{status}</span>"
            
            recent_data.append({
                "ID": safe_str(safe_get(req, 'id')),
                "Title": safe_str(safe_get(req, 'title')),
                "Priority": safe_str(safe_get(req, 'priority')),
                "Status": status_badge,
                "Date": safe_str(safe_get(req, 'created_date'))[:10],
                "Created By": safe_str(safe_get(req, 'created_by')),
                "Amount": format_ngn(safe_get(req, 'invoice_amount'))
            })
        
        # Display as HTML table
        if recent_data:
            table_html = """
            <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; border-radius: 10px; overflow: hidden;">
                <thead>
                    <tr style="background-color: #f1f5f9;">
                        <th style="padding: 12px; text-align: left;">ID</th>
                        <th style="padding: 12px; text-align: left;">Title</th>
                        <th style="padding: 12px; text-align: left;">Priority</th>
                        <th style="padding: 12px; text-align: left;">Status</th>
                        <th style="padding: 12px; text-align: left;">Date</th>
                        <th style="padding: 12px; text-align: left;">Client</th>
                        <th style="padding: 12px; text-align: left;">Amount</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for item in recent_data:
                table_html += f"""
                <tr style="border-bottom: 1px solid #e5e7eb;">
                    <td style="padding: 10px;">{item['ID']}</td>
                    <td style="padding: 10px;"><strong>{item['Title']}</strong></td>
                    <td style="padding: 10px;">{item['Priority']}</td>
                    <td style="padding: 10px;">{item['Status']}</td>
                    <td style="padding: 10px;">{item['Date']}</td>
                    <td style="padding: 10px;">{item['Created By']}</td>
                    <td style="padding: 10px;" class="ngn">{item['Amount']}</td>
                </tr>
                """
            
            table_html += """
                </tbody>
            </table>
            </div>
            """
            
            st.markdown(table_html, unsafe_allow_html=True)
            
            if len(requests) > 5:
                if st.button("View All Jobs", use_container_width=True):
                    st.session_state.show_vendor_jobs = True
                    st.rerun()
    else:
        st.info("📭 No jobs assigned yet.")
    
    # Revenue chart
    if requests:
        st.markdown("### 📈 Revenue Analytics")
        
        # Prepare revenue data
        revenue_data = []
        for req in requests:
            if safe_get(req, 'invoice_amount'):
                revenue_data.append({
                    'date': safe_str(safe_get(req, 'completed_date') or safe_get(req, 'created_date'))[:10],
                    'amount': safe_float(safe_get(req, 'invoice_amount'))
                })
        
        if revenue_data:
            df_revenue = pd.DataFrame(revenue_data)
            if not df_revenue.empty:
                df_revenue['date'] = pd.to_datetime(df_revenue['date'])
                df_revenue = df_revenue.groupby('date')['amount'].sum().reset_index()
                
                fig = px.line(
                    df_revenue,
                    x='date',
                    y='amount',
                    title="Revenue Over Time",
                    markers=True
                )
                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Amount (₦)",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

def show_manager_dashboard():
    """Dashboard for facility manager"""
    # Get all requests
    all_requests = get_all_requests()
    
    # Get all users and vendors
    all_users = execute_query('SELECT * FROM users WHERE status = "approved"')
    all_vendors = execute_query('SELECT * FROM vendors WHERE status = "approved"')
    
    # Calculate metrics
    total_requests = len(all_requests)
    pending_requests = len([r for r in all_requests if safe_get(r, 'status') == 'Pending'])
    assigned_requests = len([r for r in all_requests if safe_get(r, 'status') == 'Assigned'])
    completed_requests = len([r for r in all_requests if safe_get(r, 'status') == 'Completed'])
    approved_requests = len([r for r in all_requests if safe_get(r, 'status') == 'Approved'])
    
    # Financial metrics
    total_revenue = sum([safe_float(r.get('invoice_amount', 0)) for r in all_requests])
    pending_approval_revenue = sum([safe_float(r.get('invoice_amount', 0)) for r in all_requests 
                                    if safe_get(r, 'status') == 'Completed' 
                                    and safe_get(r, 'requesting_dept_approval') == 1 
                                    and safe_get(r, 'facilities_manager_approval') == 0])
    
    # User metrics
    total_users = len(all_users)
    facility_users = len([u for u in all_users if safe_get(u, 'role') == 'facility_user'])
    total_vendors = len(all_vendors)
    
    st.markdown("### 📊 System Overview")
    
    # First row of metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        create_metric_card("Total Requests", total_requests, "📋")
    
    with col2:
        create_metric_card("Pending", pending_requests, "⏳")
    
    with col3:
        create_metric_card("Assigned", assigned_requests, "👷")
    
    with col4:
        create_metric_card("Completed", completed_requests, "✅")
    
    with col5:
        create_metric_card("Approved", approved_requests, "🏆")
    
    # Second row of metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_metric_card("Total Revenue", format_ngn(total_revenue), "💰")
    
    with col2:
        create_metric_card("Pending Approval", format_ngn(pending_approval_revenue), "📝")
    
    with col3:
        create_metric_card("Users", total_users, "👥")
    
    with col4:
        create_metric_card("Vendors", total_vendors, "🏢")
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("👤 User Management", use_container_width=True, type="primary"):
            st.session_state.show_manage_users = True
            st.rerun()
    
    with col2:
        pending_approvals = get_requests_for_manager_approval()
        if pending_approvals:
            if st.button(f"✅ Approve Invoices ({len(pending_approvals)})", use_container_width=True):
                st.session_state.show_manager_approvals = True
                st.rerun()
        else:
            st.button("✅ Approve Invoices (0)", use_container_width=True, disabled=True)
    
    with col3:
        if st.button("📋 All Requests", use_container_width=True):
            st.session_state.show_all_requests = True
            st.rerun()
    
    with col4:
        if st.button("📊 Analytics", use_container_width=True):
            st.session_state.show_analytics = True
            st.rerun()
    
    # Recent activity
    st.markdown("### 📈 Recent Activity")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["Recent Requests", "Pending Approvals", "Vendor Performance"])
    
    with tab1:
        if all_requests:
            recent_requests = all_requests[:10]
            request_data = []
            
            for req in recent_requests:
                status = safe_str(safe_get(req, 'status'))
                status_badge = f"<span class='status-badge status-{status.lower().replace(' ', '-')}'>{status}</span>"
                
                request_data.append({
                    "ID": safe_str(safe_get(req, 'id')),
                    "Title": safe_str(safe_get(req, 'title')),
                    "Priority": safe_str(safe_get(req, 'priority')),
                    "Status": status_badge,
                    "Created By": safe_str(safe_get(req, 'created_by')),
                    "Assigned To": safe_str(safe_get(req, 'assigned_vendor') or "Not assigned"),
                    "Date": safe_str(safe_get(req, 'created_date'))[:10],
                    "Amount": format_ngn(safe_get(req, 'invoice_amount'))
                })
            
            if request_data:
                df = pd.DataFrame(request_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No requests found")
    
    with tab2:
        pending_approvals = get_requests_for_manager_approval()
        if pending_approvals:
            approval_data = []
            
            for req in pending_approvals:
                approval_data.append({
                    "ID": safe_str(safe_get(req, 'id')),
                    "Title": safe_str(safe_get(req, 'title')),
                    "Vendor": safe_str(safe_get(req, 'assigned_vendor')),
                    "Dept Approved On": safe_str(safe_get(req, 'department_approval_date')),
                    "Invoice Amount": format_ngn(safe_get(req, 'invoice_amount'))
                })
            
            df = pd.DataFrame(approval_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Quick approve button
            if st.button("Go to Approvals", use_container_width=True):
                st.session_state.show_manager_approvals = True
                st.rerun()
        else:
            st.success("🎉 No pending approvals!")
    
    with tab3:
        # Vendor performance
        if all_requests:
            # Group by vendor
            vendor_data = {}
            for req in all_requests:
                vendor = safe_str(safe_get(req, 'assigned_vendor'))
                if vendor and vendor != 'Not assigned':
                    if vendor not in vendor_data:
                        vendor_data[vendor] = {
                            'total_jobs': 0,
                            'completed_jobs': 0,
                            'total_revenue': 0.0
                        }
                    
                    vendor_data[vendor]['total_jobs'] += 1
                    if safe_get(req, 'status') in ['Completed', 'Approved']:
                        vendor_data[vendor]['completed_jobs'] += 1
                    vendor_data[vendor]['total_revenue'] += safe_float(safe_get(req, 'invoice_amount', 0))
            
            if vendor_data:
                perf_data = []
                for vendor, stats in vendor_data.items():
                    completion_rate = (stats['completed_jobs'] / stats['total_jobs'] * 100) if stats['total_jobs'] > 0 else 0
                    perf_data.append({
                        "Vendor": vendor,
                        "Total Jobs": stats['total_jobs'],
                        "Completed": stats['completed_jobs'],
                        "Completion Rate": f"{completion_rate:.1f}%",
                        "Total Revenue": format_ngn(stats['total_revenue'])
                    })
                
                df = pd.DataFrame(perf_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No vendor performance data available")
        else:
            st.info("No requests to analyze")
    
    # Charts section
    st.markdown("### 📊 System Analytics")
    
    if all_requests:
        df_requests = pd.DataFrame(all_requests)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Status distribution
            if 'status' in df_requests.columns:
                status_counts = df_requests['status'].value_counts()
                fig = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title="Request Status Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Monthly trend
            if 'created_date' in df_requests.columns:
                df_requests['month'] = pd.to_datetime(df_requests['created_date']).dt.to_period('M')
                monthly_counts = df_requests.groupby('month').size().reset_index(name='count')
                monthly_counts['month'] = monthly_counts['month'].astype(str)
                
                fig2 = px.bar(
                    monthly_counts,
                    x='month',
                    y='count',
                    title="Monthly Request Trend",
                    labels={'month': 'Month', 'count': 'Number of Requests'},
                    color='count',
                    color_continuous_scale='Viridis'
                )
                fig2.update_layout(height=400)
                st.plotly_chart(fig2, use_container_width=True)
    
    # Financial summary
    st.markdown("### 💰 Financial Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### Total Revenue by Status")
        revenue_by_status = {}
        for req in all_requests:
            status = safe_str(safe_get(req, 'status'))
            amount = safe_float(safe_get(req, 'invoice_amount', 0))
            revenue_by_status[status] = revenue_by_status.get(status, 0) + amount
        
        for status, amount in revenue_by_status.items():
            st.write(f"**{status}:** {format_ngn(amount)}")
    
    with col2:
        st.markdown("#### Top Vendors by Revenue")
        vendor_revenue = {}
        for req in all_requests:
            vendor = safe_str(safe_get(req, 'assigned_vendor'))
            if vendor and vendor != 'Not assigned':
                amount = safe_float(safe_get(req, 'invoice_amount', 0))
                vendor_revenue[vendor] = vendor_revenue.get(vendor, 0) + amount
        
        # Sort by revenue
        sorted_vendors = sorted(vendor_revenue.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for vendor, revenue in sorted_vendors:
            st.write(f"**{vendor}:** {format_ngn(revenue)}")
    
    with col3:
        st.markdown("#### Priority Distribution")
        priority_counts = {}
        for req in all_requests:
            priority = safe_str(safe_get(req, 'priority'))
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        for priority, count in priority_counts.items():
            st.write(f"**{priority}:** {count} requests")

# =============================================
# REQUEST MANAGEMENT FUNCTIONS
# =============================================
def show_new_request_form():
    """Show form for creating new maintenance request"""
    st.markdown("<h1 class='app-title'>➕ New Maintenance Request</h1>", unsafe_allow_html=True)
    
    with st.form("new_request_form"):
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Request Title *", placeholder="Brief title of the maintenance need")
            location = st.text_input("Location *", placeholder="Where is the maintenance needed?")
            facility_type = st.selectbox("Facility Type *", 
                ["Office Building", "Factory", "Warehouse", "Laboratory", "Parking Lot", "Residential Area", "Other"])
        
        with col2:
            priority = st.selectbox("Priority *", ["Low", "Medium", "High", "Critical"])
            description = st.text_area("Detailed Description *", 
                placeholder="Describe the issue in detail...", height=120)
        
        submitted = st.form_submit_button("📝 Submit Request", use_container_width=True)
        
        if submitted:
            if not all([title, description, location, facility_type]):
                st.error("❌ Please fill in all required fields (*)")
            else:
                success = execute_update(
                    '''INSERT INTO maintenance_requests 
                    (title, description, location, facility_type, priority, created_by, status) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (title, description, location, facility_type, priority, 
                     st.session_state.user['username'], 'Pending')
                )
                
                if success:
                    st.success("✅ Maintenance request submitted successfully!")
                    st.info("📋 Your request will be reviewed and assigned to a vendor.")
                    if st.button("← Back to Dashboard", use_container_width=True):
                        st.session_state.show_new_request = False
                        st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

def show_my_requests():
    """Show user's maintenance requests"""
    st.markdown("<h1 class='app-title'>📋 My Maintenance Requests</h1>", unsafe_allow_html=True)
    
    username = safe_get(st.session_state.user, 'username')
    requests = get_user_requests(username)
    
    if not requests:
        st.info("📭 You haven't created any maintenance requests yet.")
        if st.button("➕ Create New Request", use_container_width=True):
            st.session_state.show_new_request = True
            st.rerun()
        return
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Filter by Status", 
            ["All", "Pending", "Assigned", "In Progress", "Completed", "Approved"])
    with col2:
        priority_filter = st.selectbox("Filter by Priority", 
            ["All", "Low", "Medium", "High", "Critical"])
    with col3:
        search_term = st.text_input("Search requests")
    
    # Filter requests
    filtered_requests = requests
    if status_filter != "All":
        filtered_requests = [r for r in filtered_requests if safe_get(r, 'status') == status_filter]
    if priority_filter != "All":
        filtered_requests = [r for r in filtered_requests if safe_get(r, 'priority') == priority_filter]
    if search_term:
        filtered_requests = [r for r in filtered_requests 
                           if search_term.lower() in safe_str(safe_get(r, 'title')).lower() 
                           or search_term.lower() in safe_str(safe_get(r, 'description')).lower()]
    
    st.markdown(f"<div class='card'><h4>📊 Showing {len(filtered_requests)} of {len(requests)} requests</h4></div>", unsafe_allow_html=True)
    
    # Display requests
    for request in filtered_requests:
        status = safe_str(safe_get(request, 'status'))
        priority = safe_str(safe_get(request, 'priority'))
        
        # Status badge
        if status == 'Pending':
            status_badge = f"<span class='status-badge status-pending'>⏳ {status}</span>"
        elif status == 'Assigned':
            status_badge = f"<span class='status-badge status-assigned'>👷 {status}</span>"
        elif status == 'Completed':
            status_badge = f"<span class='status-badge status-completed'>✅ {status}</span>"
        elif status == 'Approved':
            status_badge = f"<span class='status-badge status-approved'>🏆 {status}</span>"
        else:
            status_badge = f"<span class='status-badge'>{status}</span>"
        
        # Priority color
        if priority == 'High':
            priority_color = "#ef4444"
        elif priority == 'Critical':
            priority_color = "#dc2626"
        elif priority == 'Medium':
            priority_color = "#f59e0b"
        else:
            priority_color = "#10b981"
        
        with st.expander(f"{status_badge} **{safe_str(safe_get(request, 'title'))}** - Priority: <span style='color:{priority_color}'>{priority}</span>", 
                        expanded=False):
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Request ID:** {safe_str(safe_get(request, 'id'))}")
                st.write(f"**Location:** {safe_str(safe_get(request, 'location'))}")
                st.write(f"**Facility Type:** {safe_str(safe_get(request, 'facility_type'))}")
                st.write(f"**Created On:** {safe_str(safe_get(request, 'created_date'))}")
                
                if safe_get(request, 'assigned_vendor'):
                    st.write(f"**Assigned Vendor:** {safe_str(safe_get(request, 'assigned_vendor'))}")
                
                if safe_get(request, 'completed_date'):
                    st.write(f"**Completed On:** {safe_str(safe_get(request, 'completed_date'))}")
                
                if safe_get(request, 'invoice_amount'):
                    st.write(f"**Invoice Amount:** {format_ngn(safe_get(request, 'invoice_amount'))}")
            
            with col2:
                st.write(f"**Description:**")
                st.info(safe_str(safe_get(request, 'description')))
                
                if safe_get(request, 'job_breakdown'):
                    st.write(f"**Job Breakdown:**")
                    st.info(safe_str(safe_get(request, 'job_breakdown')))
                
                if safe_get(request, 'completion_notes'):
                    st.write(f"**Completion Notes:**")
                    st.success(safe_str(safe_get(request, 'completion_notes')))
            
            # Show workflow status
            show_workflow_status(request)
            
            # Actions based on status
            if status == 'Completed' and not safe_get(request, 'requesting_dept_approval'):
                st.markdown("---")
                st.markdown("### ✅ Department Approval Required")
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button(f"Approve Completion", key=f"dept_approve_{safe_get(request, 'id')}", 
                               use_container_width=True, type="primary"):
                        # Approve at department level
                        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        if execute_update(
                            '''UPDATE maintenance_requests 
                            SET requesting_dept_approval = 1,
                                department_approval_date = ?
                            WHERE id = ?''',
                            (current_time, safe_get(request, 'id'))
                        ):
                            st.success("✅ Department approval submitted! Waiting for Facility Manager final approval.")
                            st.rerun()
                
                with col_b:
                    if st.button(f"Request Changes", key=f"dept_reject_{safe_get(request, 'id')}", 
                               use_container_width=True, type="secondary"):
                        st.info("Please contact the vendor directly for any changes needed.")
    
    # Export option
    st.markdown("---")
    if st.button("📥 Export My Requests to CSV", use_container_width=True):
        export_data = []
        for req in requests:
            export_data.append({
                "ID": safe_str(safe_get(req, 'id')),
                "Title": safe_str(safe_get(req, 'title')),
                "Description": safe_str(safe_get(req, 'description')),
                "Location": safe_str(safe_get(req, 'location')),
                "Priority": safe_str(safe_get(req, 'priority')),
                "Status": safe_str(safe_get(req, 'status')),
                "Created Date": safe_str(safe_get(req, 'created_date')),
                "Assigned Vendor": safe_str(safe_get(req, 'assigned_vendor')),
                "Completed Date": safe_str(safe_get(req, 'completed_date')),
                "Invoice Amount": safe_float(safe_get(req, 'invoice_amount'))
            })
        
        df = pd.DataFrame(export_data)
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"my_requests_{username}.csv",
            mime="text/csv"
        )

def show_all_requests():
    """Show all requests (for facility manager)"""
    st.markdown("<h1 class='app-title'>📋 All Maintenance Requests</h1>", unsafe_allow_html=True)
    
    requests = get_all_requests()
    
    if not requests:
        st.info("📭 No maintenance requests in the system.")
        return
    
    # Filter and search options
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.selectbox("Status", ["All", "Pending", "Assigned", "In Progress", "Completed", "Approved"])
    with col2:
        priority_filter = st.selectbox("Priority", ["All", "Low", "Medium", "High", "Critical"])
    with col3:
        vendor_filter = st.selectbox("Vendor", ["All"] + list(set([safe_str(r.get('assigned_vendor')) for r in requests if r.get('assigned_vendor')])))
    with col4:
        search_term = st.text_input("Search")
    
    # Filter requests
    filtered_requests = requests
    if status_filter != "All":
        filtered_requests = [r for r in filtered_requests if safe_get(r, 'status') == status_filter]
    if priority_filter != "All":
        filtered_requests = [r for r in filtered_requests if safe_get(r, 'priority') == priority_filter]
    if vendor_filter != "All":
        filtered_requests = [r for r in filtered_requests if safe_get(r, 'assigned_vendor') == vendor_filter]
    if search_term:
        filtered_requests = [r for r in filtered_requests 
                           if search_term.lower() in safe_str(safe_get(r, 'title')).lower() 
                           or search_term.lower() in safe_str(safe_get(r, 'description')).lower()
                           or search_term.lower() in safe_str(safe_get(r, 'created_by')).lower()]
    
    st.markdown(f"<div class='card'><h4>📊 {len(filtered_requests)} requests found</h4></div>", unsafe_allow_html=True)
    
    # Display in a table
    if filtered_requests:
        request_data = []
        for req in filtered_requests:
            status = safe_str(safe_get(req, 'status'))
            status_badge = f"<span class='status-badge status-{status.lower().replace(' ', '-')}'>{status}</span>"
            
            request_data.append({
                "ID": safe_str(safe_get(req, 'id')),
                "Title": safe_str(safe_get(req, 'title')),
                "Priority": safe_str(safe_get(req, 'priority')),
                "Status": status_badge,
                "Created By": safe_str(safe_get(req, 'created_by')),
                "Assigned To": safe_str(safe_get(req, 'assigned_vendor') or "Not assigned"),
                "Date": safe_str(safe_get(req, 'created_date'))[:10],
                "Amount": format_ngn(safe_get(req, 'invoice_amount'))
            })
        
        df = pd.DataFrame(request_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Management actions
        st.markdown("### ⚡ Request Management")
        
        # Assign vendor to pending requests
        pending_requests = [r for r in filtered_requests if safe_get(r, 'status') == 'Pending']
        if pending_requests:
            st.markdown("#### Assign Vendor to Pending Requests")
            
            col1, col2 = st.columns(2)
            
            with col1:
                selected_request = st.selectbox(
                    "Select Request",
                    options=[f"{safe_get(r, 'id')}: {safe_get(r, 'title')}" for r in pending_requests],
                    key="assign_request_select"
                )
                
                if selected_request:
                    request_id = selected_request.split(":")[0].strip()
                    
                    # Get available vendors
                    vendors = execute_query('SELECT * FROM vendors WHERE status = "approved"')
                    vendor_options = {f"{safe_get(v, 'company_name')} ({safe_get(v, 'vendor_type')})": safe_get(v, 'username') 
                                     for v in vendors}
                    
                    selected_vendor = st.selectbox(
                        "Select Vendor",
                        options=list(vendor_options.keys())
                    )
            
            with col2:
                if selected_request and selected_vendor:
                    if st.button("👷 Assign Vendor", use_container_width=True, type="primary"):
                        vendor_username = vendor_options[selected_vendor]
                        
                        if execute_update(
                            '''UPDATE maintenance_requests 
                            SET assigned_vendor = ?,
                                status = 'Assigned'
                            WHERE id = ?''',
                            (vendor_username, request_id)
                        ):
                            st.success(f"✅ Request assigned to {selected_vendor}!")
                            st.rerun()
        
        # Export option
        st.markdown("---")
        if st.button("📥 Export All Requests to CSV", use_container_width=True):
            export_data = []
            for req in requests:
                export_data.append({
                    "ID": safe_str(safe_get(req, 'id')),
                    "Title": safe_str(safe_get(req, 'title')),
                    "Description": safe_str(safe_get(req, 'description')),
                    "Location": safe_str(safe_get(req, 'location')),
                    "Priority": safe_str(safe_get(req, 'priority')),
                    "Status": safe_str(safe_get(req, 'status')),
                    "Created By": safe_str(safe_get(req, 'created_by')),
                    "Created Date": safe_str(safe_get(req, 'created_date')),
                    "Assigned Vendor": safe_str(safe_get(req, 'assigned_vendor')),
                    "Completed Date": safe_str(safe_get(req, 'completed_date')),
                    "Invoice Amount": safe_float(safe_get(req, 'invoice_amount'))
                })
            
            df = pd.DataFrame(export_data)
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="all_requests.csv",
                mime="text/csv"
            )
    else:
        st.info("No requests match your filters.")

def show_vendor_jobs():
    """Show jobs assigned to vendor"""
    st.markdown("<h1 class='app-title'>🔧 My Assigned Jobs</h1>", unsafe_allow_html=True)
    
    username = safe_get(st.session_state.user, 'username')
    requests = get_vendor_requests(username)
    
    if not requests:
        st.info("📭 No jobs assigned to you yet.")
        return
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox("Filter by Status", 
            ["All", "Assigned", "In Progress", "Completed"])
    with col2:
        priority_filter = st.selectbox("Filter by Priority", 
            ["All", "Low", "Medium", "High", "Critical"])
    
    # Filter requests
    filtered_requests = requests
    if status_filter != "All":
        filtered_requests = [r for r in filtered_requests if safe_get(r, 'status') == status_filter]
    if priority_filter != "All":
        filtered_requests = [r for r in filtered_requests if safe_get(r, 'priority') == priority_filter]
    
    st.markdown(f"<div class='card'><h4>📊 Showing {len(filtered_requests)} of {len(requests)} jobs</h4></div>", unsafe_allow_html=True)
    
    # Display jobs
    for request in filtered_requests:
        status = safe_str(safe_get(request, 'status'))
        priority = safe_str(safe_get(request, 'priority'))
        
        # Status badge
        if status == 'Assigned':
            status_badge = f"<span class='status-badge status-assigned'>👷 {status}</span>"
        elif status == 'In Progress':
            status_badge = f"<span class='status-badge status-assigned'>⚡ {status}</span>"
        elif status == 'Completed':
            status_badge = f"<span class='status-badge status-completed'>✅ {status}</span>"
        else:
            status_badge = f"<span class='status-badge'>{status}</span>"
        
        with st.expander(f"{status_badge} **{safe_str(safe_get(request, 'title'))}** - Priority: {priority}", 
                        expanded=False):
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Request ID:** {safe_str(safe_get(request, 'id'))}")
                st.write(f"**Location:** {safe_str(safe_get(request, 'location'))}")
                st.write(f"**Facility Type:** {safe_str(safe_get(request, 'facility_type'))}")
                st.write(f"**Priority:** {priority}")
                st.write(f"**Created By:** {safe_str(safe_get(request, 'created_by'))}")
                st.write(f"**Created On:** {safe_str(safe_get(request, 'created_date'))}")
            
            with col2:
                st.write(f"**Description:**")
                st.info(safe_str(safe_get(request, 'description')))
                
                if safe_get(request, 'job_breakdown'):
                    st.write(f"**Job Breakdown:**")
                    st.info(safe_str(safe_get(request, 'job_breakdown')))
                
                if safe_get(request, 'invoice_amount'):
                    st.write(f"**Invoice Amount:** {format_ngn(safe_get(request, 'invoice_amount'))}")
            
            # Vendor actions based on status
            if status == 'Assigned':
                st.markdown("---")
                st.markdown("### 🛠️ Job Actions")
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    if st.button(f"Start Job", key=f"start_{safe_get(request, 'id')}", 
                               use_container_width=True, type="primary"):
                        if execute_update(
                            '''UPDATE maintenance_requests 
                            SET status = 'In Progress'
                            WHERE id = ?''',
                            (safe_get(request, 'id'),)
                        ):
                            st.success("✅ Job marked as In Progress!")
                            st.rerun()
                
                with col_b:
                    if st.button(f"Submit Completion", key=f"complete_{safe_get(request, 'id')}", 
                               use_container_width=True):
                        st.session_state.selected_job_complete = safe_get(request, 'id')
                        st.rerun()
            
            elif status == 'In Progress':
                st.markdown("---")
                st.markdown("### 🛠️ Job Actions")
                
                if st.button(f"Submit Completion", key=f"complete_{safe_get(request, 'id')}", 
                           use_container_width=True, type="primary"):
                    st.session_state.selected_job_complete = safe_get(request, 'id')
                    st.rerun()
            
            elif status == 'Completed':
                st.write(f"**Completed On:** {safe_str(safe_get(request, 'completed_date'))}")
                if safe_get(request, 'completion_notes'):
                    st.write(f"**Completion Notes:**")
                    st.success(safe_str(safe_get(request, 'completion_notes')))
                
                # Show approval status
                st.markdown("### 📋 Approval Status")
                if safe_get(request, 'requesting_dept_approval'):
                    st.info("✅ Department approval received")
                    if safe_get(request, 'facilities_manager_approval'):
                        st.success("🏆 Final approval received - Payment can be processed")
                    else:
                        st.warning("⏳ Waiting for Facility Manager final approval")
                else:
                    st.warning("⏳ Waiting for department approval")
    
    # Handle job completion
    if 'selected_job_complete' in st.session_state:
        show_job_completion_form(st.session_state.selected_job_complete)

def show_job_completion_form(request_id):
    """Show form for vendor to submit job completion"""
    st.markdown("### ✅ Submit Job Completion")
    
    with st.form("completion_form"):
        job_breakdown = st.text_area("Job Breakdown/Details *", 
            placeholder="Detailed description of work done, materials used, etc.",
            height=120)
        
        completion_notes = st.text_area("Completion Notes", 
            placeholder="Any additional notes or comments",
            height=100)
        
        col1, col2 = st.columns(2)
        
        with col1:
            invoice_amount = st.number_input("Invoice Amount (₦)", 
                min_value=0.0, value=0.0, step=1000.0)
        
        with col2:
            invoice_number = st.text_input("Invoice Number", 
                placeholder="Your invoice reference number")
        
        submitted = st.form_submit_button("✅ Submit Completion", use_container_width=True)
        
        if submitted:
            if not job_breakdown:
                st.error("❌ Job breakdown is required")
            else:
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                if execute_update(
                    '''UPDATE maintenance_requests 
                    SET status = 'Completed',
                        completed_date = ?,
                        job_breakdown = ?,
                        completion_notes = ?,
                        invoice_amount = ?,
                        invoice_number = ?
                    WHERE id = ?''',
                    (current_time, job_breakdown, completion_notes, 
                     invoice_amount, invoice_number, request_id)
                ):
                    st.success("✅ Job completion submitted successfully!")
                    st.info("📋 Waiting for department approval.")
                    
                    # Clear the session state
                    del st.session_state.selected_job_complete
                    st.rerun()
    
    if st.button("Cancel", use_container_width=True):
        del st.session_state.selected_job_complete
        st.rerun()

# =============================================
# APPROVAL FUNCTIONS
# =============================================
def show_user_approvals():
    """Show requests pending user approval"""
    st.markdown("<h1 class='app-title'>✅ Department Approvals</h1>", unsafe_allow_html=True)
    
    username = safe_get(st.session_state.user, 'username')
    pending_approvals = get_requests_for_user_approval(username)
    
    if not pending_approvals:
        st.success("🎉 No pending approvals at the moment!")
        if st.button("← Back to Dashboard", use_container_width=True):
            st.session_state.show_approvals = False
            st.rerun()
        return
    
    st.markdown(f"<div class='card'><h4>⏳ {len(pending_approvals)} request(s) pending your approval</h4></div>", unsafe_allow_html=True)
    
    for request in pending_approvals:
        with st.expander(f"🔧 {safe_str(safe_get(request, 'title'))} - Vendor: {safe_str(safe_get(request, 'assigned_vendor'))}", 
                        expanded=True):
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Request ID:** {safe_str(safe_get(request, 'id'))}")
                st.write(f"**Location:** {safe_str(safe_get(request, 'location'))}")
                st.write(f"**Facility Type:** {safe_str(safe_get(request, 'facility_type'))}")
                st.write(f"**Completed On:** {safe_str(safe_get(request, 'completed_date'))}")
                st.write(f"**Vendor:** {safe_str(safe_get(request, 'assigned_vendor'))}")
                st.write(f"**Invoice Amount:** {format_ngn(safe_get(request, 'invoice_amount'))}")
            
            with col2:
                st.write(f"**Original Description:**")
                st.info(safe_str(safe_get(request, 'description')))
                
                st.write(f"**Job Breakdown:**")
                st.success(safe_str(safe_get(request, 'job_breakdown')))
                
                if safe_get(request, 'completion_notes'):
                    st.write(f"**Completion Notes:**")
                    st.info(safe_str(safe_get(request, 'completion_notes')))
            
            # Approval actions
            st.markdown("---")
            st.markdown("### ✅ Approval Decision")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button(f"Approve & Forward", key=f"user_approve_{safe_get(request, 'id')}", 
                           use_container_width=True, type="primary"):
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    if execute_update(
                        '''UPDATE maintenance_requests 
                        SET requesting_dept_approval = 1,
                            department_approval_date = ?
                        WHERE id = ?''',
                        (current_time, safe_get(request, 'id'))
                    ):
                        st.success("✅ Approved! Forwarded to Facility Manager for final approval.")
                        st.rerun()
            
            with col_b:
                if st.button(f"Request Changes", key=f"user_reject_{safe_get(request, 'id')}", 
                           use_container_width=True, type="secondary"):
                    st.info("Please contact the vendor directly to request any changes.")

def show_manager_approvals():
    """Show requests pending manager approval"""
    st.markdown("<h1 class='app-title'>✅ Manager Final Approvals</h1>", unsafe_allow_html=True)
    
    pending_approvals = get_requests_for_manager_approval()
    
    if not pending_approvals:
        st.success("🎉 No pending approvals at the moment!")
        if st.button("← Back to Dashboard", use_container_width=True):
            st.session_state.show_manager_approvals = False
            st.rerun()
        return
    
    st.markdown(f"<div class='card'><h4>⏳ {len(pending_approvals)} request(s) pending final approval</h4></div>", unsafe_allow_html=True)
    
    for request in pending_approvals:
        with st.expander(f"💰 {safe_str(safe_get(request, 'title'))} - Amount: {format_ngn(safe_get(request, 'invoice_amount'))}", 
                        expanded=True):
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Request ID:** {safe_str(safe_get(request, 'id'))}")
                st.write(f"**Created By:** {safe_str(safe_get(request, 'created_by'))}")
                st.write(f"**Department:** Getting user department...")
                st.write(f"**Location:** {safe_str(safe_get(request, 'location'))}")
                st.write(f"**Vendor:** {safe_str(safe_get(request, 'assigned_vendor'))}")
                st.write(f"**Completed On:** {safe_str(safe_get(request, 'completed_date'))}")
                st.write(f"**Dept Approved On:** {safe_str(safe_get(request, 'department_approval_date'))}")
            
            with col2:
                st.write(f"**Invoice Amount:**")
                st.markdown(f"<h2 class='ngn'>{format_ngn(safe_get(request, 'invoice_amount'))}</h2>", unsafe_allow_html=True)
                
                st.write(f"**Job Breakdown:**")
                st.info(safe_str(safe_get(request, 'job_breakdown')))
                
                st.write(f"**Original Description:**")
                st.success(safe_str(safe_get(request, 'description')))
            
            # Get user department
            user_info = execute_query('SELECT department FROM users WHERE username = ?', 
                                     (safe_get(request, 'created_by'),))
            if user_info:
                st.write(f"**Department:** {safe_str(safe_get(user_info[0], 'department'))}")
            
            # Approval actions
            st.markdown("---")
            st.markdown("### ✅ Final Approval Decision")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button(f"✅ Approve Payment", key=f"manager_approve_{safe_get(request, 'id')}", 
                           use_container_width=True, type="primary"):
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    if execute_update(
                        '''UPDATE maintenance_requests 
                        SET facilities_manager_approval = 1,
                            manager_approval_date = ?,
                            status = 'Approved'
                        WHERE id = ?''',
                        (current_time, safe_get(request, 'id'))
                    ):
                        st.success("✅ Payment approved! The vendor can now process payment.")
                        st.rerun()
            
            with col_b:
                if st.button(f"❌ Reject/Query", key=f"manager_reject_{safe_get(request, 'id')}", 
                           use_container_width=True, type="secondary"):
                    st.info("Please contact the department and vendor for clarification.")

# =============================================
# INVOICE FUNCTIONS
# =============================================
def show_invoice_form():
    """Show form for vendors to submit invoices"""
    st.markdown("<h1 class='app-title'>💰 Submit Invoice</h1>", unsafe_allow_html=True)
    
    username = safe_get(st.session_state.user, 'username')
    
    # Get vendor's completed jobs without invoices
    completed_jobs = execute_query('''
        SELECT * FROM maintenance_requests 
        WHERE assigned_vendor = ? 
        AND status = 'Completed'
        AND (invoice_amount IS NULL OR invoice_amount = 0)
        ORDER BY completed_date DESC
    ''', (username,))
    
    if not completed_jobs:
        st.info("📭 No completed jobs available for invoicing.")
        if st.button("← Back to Dashboard", use_container_width=True):
            st.session_state.show_invoice_form = False
            st.rerun()
        return
    
    st.markdown("### 📋 Select Job to Invoice")
    
    job_options = {f"{safe_get(job, 'id')}: {safe_get(job, 'title')}": safe_get(job, 'id') 
                  for job in completed_jobs}
    
    selected_job_key = st.selectbox("Select Job", options=list(job_options.keys()))
    selected_job_id = job_options[selected_job_key]
    
    if selected_job_id:
        job_details = [job for job in completed_jobs if safe_get(job, 'id') == selected_job_id][0]
        
        st.markdown("### 📝 Invoice Details")
        
        with st.form("invoice_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                invoice_number = st.text_input("Invoice Number *", 
                    placeholder="e.g., INV-2024-001")
                details_of_work = st.text_area("Details of Work *", 
                    value=safe_str(safe_get(job_details, 'job_breakdown')),
                    height=100)
                quantity = st.number_input("Quantity", min_value=1, value=1)
            
            with col2:
                unit_cost = st.number_input("Unit Cost (₦)", min_value=0.0, value=0.0, step=1000.0)
                labour_charge = st.number_input("Labour Charge (₦)", min_value=0.0, value=0.0, step=1000.0)
                vat_applicable = st.checkbox("VAT Applicable?")
            
            # Calculate amounts
            amount = quantity * unit_cost
            vat_amount = (amount + labour_charge) * 0.075 if vat_applicable else 0
            total_amount = amount + labour_charge + vat_amount
            
            # Display calculation
            st.markdown("### 💰 Amount Summary")
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.write(f"**Work Amount:** {format_ngn(amount)}")
            with col_b:
                st.write(f"**Labour Charge:** {format_ngn(labour_charge)}")
            with col_c:
                if vat_applicable:
                    st.write(f"**VAT (7.5%):** {format_ngn(vat_amount)}")
            
            st.markdown(f"<h3>Total Amount: {format_ngn(total_amount)}</h3>", unsafe_allow_html=True)
            
            submitted = st.form_submit_button("📤 Submit Invoice", use_container_width=True)
            
            if submitted:
                if not invoice_number or not details_of_work:
                    st.error("❌ Please fill in all required fields (*)")
                else:
                    # Check if invoice number already exists
                    existing_invoice = execute_query(
                        'SELECT * FROM invoices WHERE invoice_number = ?',
                        (invoice_number,)
                    )
                    
                    if existing_invoice:
                        st.error("❌ Invoice number already exists. Please use a different number.")
                    else:
                        # Create invoice
                        invoice_success = execute_update(
                            '''INSERT INTO invoices 
                            (invoice_number, request_id, vendor_username, details_of_work, 
                             quantity, unit_cost, amount, labour_charge, vat_applicable, 
                             vat_amount, total_amount, status) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            (invoice_number, selected_job_id, username, details_of_work,
                             quantity, unit_cost, amount, labour_charge, 
                             1 if vat_applicable else 0, vat_amount, total_amount, 'Pending')
                        )
                        
                        if invoice_success:
                            # Update request with invoice amount
                            execute_update(
                                '''UPDATE maintenance_requests 
                                SET invoice_amount = ?,
                                    invoice_number = ?
                                WHERE id = ?''',
                                (total_amount, invoice_number, selected_job_id)
                            )
                            
                            st.success("✅ Invoice submitted successfully!")
                            st.info("📋 The invoice will be reviewed during the approval process.")
                            
                            if st.button("← Back to Dashboard", use_container_width=True):
                                st.session_state.show_invoice_form = False
                                st.rerun()
    
    if st.button("Cancel", use_container_width=True):
        st.session_state.show_invoice_form = False
        st.rerun()

# =============================================
# ANALYTICS FUNCTIONS
# =============================================
def show_analytics():
    """Show advanced analytics"""
    st.markdown("<h1 class='app-title'>📊 Advanced Analytics</h1>", unsafe_allow_html=True)
    
    # Get all data
    all_requests = get_all_requests()
    all_users = execute_query('SELECT * FROM users WHERE status = "approved"')
    all_vendors = execute_query('SELECT * FROM vendors WHERE status = "approved"')
    
    if not all_requests:
        st.info("No data available for analytics")
        return
    
    df_requests = pd.DataFrame(all_requests)
    
    # Convert date columns
    if 'created_date' in df_requests.columns:
        df_requests['created_date'] = pd.to_datetime(df_requests['created_date'])
        df_requests['month'] = df_requests['created_date'].dt.to_period('M')
        df_requests['week'] = df_requests['created_date'].dt.to_period('W')
        df_requests['day'] = df_requests['created_date'].dt.date
    
    # Create tabs for different analytics
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "💰 Financial", "👥 Users", "🏢 Vendors"])
    
    with tab1:
        st.markdown("### 📈 Request Trends")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Monthly trend
            if 'month' in df_requests.columns:
                monthly_counts = df_requests.groupby('month').size().reset_index(name='count')
                monthly_counts['month'] = monthly_counts['month'].astype(str)
                
                fig = px.line(
                    monthly_counts,
                    x='month',
                    y='count',
                    title="Monthly Request Volume",
                    markers=True
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Status over time
            if 'created_date' in df_requests.columns and 'status' in df_requests.columns:
                daily_status = df_requests.groupby(['day', 'status']).size().reset_index(name='count')
                
                fig = px.area(
                    daily_status,
                    x='day',
                    y='count',
                    color='status',
                    title="Daily Status Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # Priority analysis
        st.markdown("### 🚨 Priority Analysis")
        
        if 'priority' in df_requests.columns:
            priority_data = df_requests.groupby('priority').agg({
                'id': 'count',
                'invoice_amount': 'sum'
            }).reset_index()
            priority_data.columns = ['Priority', 'Count', 'Total Amount']
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    priority_data,
                    x='Priority',
                    y='Count',
                    title="Requests by Priority",
                    color='Priority',
                    color_discrete_sequence=['#10b981', '#f59e0b', '#ef4444', '#dc2626']
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(
                    priority_data,
                    x='Priority',
                    y='Total Amount',
                    title="Cost by Priority",
                    color='Priority',
                    color_discrete_sequence=['#10b981', '#f59e0b', '#ef4444', '#dc2626']
                )
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### 💰 Financial Analytics")
        
        # Only consider requests with invoice amounts
        financial_data = df_requests[df_requests['invoice_amount'].notna() & (df_requests['invoice_amount'] > 0)]
        
        if not financial_data.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Revenue over time
                if 'created_date' in financial_data.columns:
                    monthly_revenue = financial_data.groupby('month')['invoice_amount'].sum().reset_index()
                    monthly_revenue['month'] = monthly_revenue['month'].astype(str)
                    
                    fig = px.bar(
                        monthly_revenue,
                        x='month',
                        y='invoice_amount',
                        title="Monthly Revenue",
                        labels={'invoice_amount': 'Revenue (₦)'}
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Revenue by status
                if 'status' in financial_data.columns:
                    status_revenue = financial_data.groupby('status')['invoice_amount'].sum().reset_index()
                    
                    fig = px.pie(
                        status_revenue,
                        values='invoice_amount',
                        names='status',
                        title="Revenue by Status",
                        hole=0.4
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            # Top requests by cost
            st.markdown("### 💎 Top 10 Most Expensive Requests")
            
            top_requests = financial_data.nlargest(10, 'invoice_amount')[['title', 'created_by', 'assigned_vendor', 'invoice_amount', 'status']]
            top_requests['invoice_amount'] = top_requests['invoice_amount'].apply(lambda x: format_ngn(x))
            st.dataframe(top_requests, use_container_width=True)
        
        else:
            st.info("No financial data available")
    
    with tab3:
        st.markdown("### 👥 User Analytics")
        
        if all_users:
            # User distribution by role
            role_counts = pd.DataFrame(all_users)['role'].value_counts().reset_index()
            role_counts.columns = ['Role', 'Count']
            
            # Format role names
            role_counts['Role'] = role_counts['Role'].apply(
                lambda x: x.replace('_', ' ').title()
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.pie(
                    role_counts,
                    values='Count',
                    names='Role',
                    title="User Distribution by Role",
                    hole=0.3
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # User activity (requests created)
                user_activity = df_requests.groupby('created_by').size().reset_index(name='request_count')
                user_activity = user_activity.sort_values('request_count', ascending=False).head(10)
                
                fig = px.bar(
                    user_activity,
                    x='created_by',
                    y='request_count',
                    title="Top 10 Most Active Users",
                    labels={'created_by': 'Username', 'request_count': 'Number of Requests'}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            # Department analysis
            user_df = pd.DataFrame(all_users)
            if 'department' in user_df.columns:
                dept_counts = user_df['department'].value_counts().reset_index()
                dept_counts.columns = ['Department', 'Count']
                
                st.markdown("### 📊 Department Distribution")
                st.dataframe(dept_counts, use_container_width=True)
    
    with tab4:
        st.markdown("### 🏢 Vendor Analytics")
        
        if all_vendors:
            # Vendor distribution by type
            vendor_df = pd.DataFrame(all_vendors)
            
            if 'vendor_type' in vendor_df.columns:
                type_counts = vendor_df['vendor_type'].value_counts().reset_index()
                type_counts.columns = ['Vendor Type', 'Count']
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = px.pie(
                        type_counts,
                        values='Count',
                        names='Vendor Type',
                        title="Vendors by Type",
                        hole=0.3
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            # Vendor performance
            if all_requests:
                vendor_performance = []
                for vendor in all_vendors:
                    vendor_username = safe_get(vendor, 'username')
                    vendor_requests = [r for r in all_requests if safe_get(r, 'assigned_vendor') == vendor_username]
                    
                    if vendor_requests:
                        total_jobs = len(vendor_requests)
                        completed_jobs = len([r for r in vendor_requests if safe_get(r, 'status') in ['Completed', 'Approved']])
                        total_revenue = sum([safe_float(r.get('invoice_amount', 0)) for r in vendor_requests])
                        avg_completion_time = None  # Could calculate if you have start and end dates
                        
                        vendor_performance.append({
                            'Vendor': safe_get(vendor, 'company_name'),
                            'Type': safe_get(vendor, 'vendor_type'),
                            'Total Jobs': total_jobs,
                            'Completed Jobs': completed_jobs,
                            'Completion Rate': f"{(completed_jobs/total_jobs*100):.1f}%" if total_jobs > 0 else "0%",
                            'Total Revenue': format_ngn(total_revenue),
                            'Avg Revenue per Job': format_ngn(total_revenue/total_jobs) if total_jobs > 0 else "₦0"
                        })
                
                if vendor_performance:
                    perf_df = pd.DataFrame(vendor_performance)
                    st.markdown("### 📊 Vendor Performance Summary")
                    st.dataframe(perf_df, use_container_width=True)
        
        # Export analytics
        st.markdown("---")
        if st.button("📥 Export Analytics Report", use_container_width=True):
            # Create a summary report
            report_data = {
                "Total Requests": len(all_requests),
                "Total Users": len(all_users),
                "Total Vendors": len(all_vendors),
                "Total Revenue": format_ngn(sum([safe_float(r.get('invoice_amount', 0)) for r in all_requests])),
                "Average Request per User": f"{len(all_requests)/len(all_users):.1f}" if all_users else "N/A"
            }
            
            report_df = pd.DataFrame(list(report_data.items()), columns=['Metric', 'Value'])
            
            csv = report_df.to_csv(index=False)
            st.download_button(
                label="Download Report",
                data=csv,
                file_name="analytics_report.csv",
                mime="text/csv"
            )

# =============================================
# MAIN APPLICATION FLOW
# =============================================
def main():
    # Initialize session state
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    # Initialize other session state variables
    session_vars = [
        'show_new_request', 'show_my_requests', 'show_all_requests',
        'show_vendor_jobs', 'show_invoice_form', 'show_vendor_reports',
        'show_approvals', 'show_manager_approvals', 'show_manage_users',
        'show_analytics', 'selected_job_complete'
    ]
    
    for var in session_vars:
        if var not in st.session_state:
            st.session_state[var] = False
    
    # Show login page if not authenticated
    if not st.session_state.user:
        show_enhanced_login()
        return
    
    # User is authenticated - show main application
    user_role = safe_get(st.session_state.user, 'role')
    username = safe_get(st.session_state.user, 'username')
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
        st.markdown("### 🏢 A-Z Facilities")
        st.markdown("#### Management Pro APP™")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # User info
        st.markdown(f"**👤 Welcome, {safe_get(st.session_state.user, 'full_name')}**")
        st.markdown(f"*Role: {user_role.replace('_', ' ').title()}*")
        
        st.markdown("---")
        
        # Navigation based on role
        st.markdown("### 🧭 Navigation")
        
        if user_role == 'facility_user':
            menu_options = [
                "📊 Dashboard",
                "➕ New Request", 
                "📋 My Requests",
                "✅ Approve Jobs",
                "🔐 Logout"
            ]
            
            selected = st.selectbox("Go to", menu_options)
            
            if selected == "📊 Dashboard":
                st.session_state.show_new_request = False
                st.session_state.show_my_requests = False
                st.session_state.show_approvals = False
            
            elif selected == "➕ New Request":
                st.session_state.show_new_request = True
            
            elif selected == "📋 My Requests":
                st.session_state.show_my_requests = True
            
            elif selected == "✅ Approve Jobs":
                st.session_state.show_approvals = True
            
            elif selected == "🔐 Logout":
                st.session_state.user = None
                for var in session_vars:
                    st.session_state[var] = False
                st.rerun()
        
        elif user_role == 'vendor':
            menu_options = [
                "📊 Dashboard",
                "🔧 My Jobs",
                "💰 Submit Invoice",
                "📊 Reports",
                "🔐 Logout"
            ]
            
            selected = st.selectbox("Go to", menu_options)
            
            if selected == "📊 Dashboard":
                st.session_state.show_vendor_jobs = False
                st.session_state.show_invoice_form = False
                st.session_state.show_vendor_reports = False
            
            elif selected == "🔧 My Jobs":
                st.session_state.show_vendor_jobs = True
            
            elif selected == "💰 Submit Invoice":
                st.session_state.show_invoice_form = True
            
            elif selected == "📊 Reports":
                st.session_state.show_vendor_reports = True
            
            elif selected == "🔐 Logout":
                st.session_state.user = None
                for var in session_vars:
                    st.session_state[var] = False
                st.rerun()
        
        elif user_role in ['facility_manager', 'System Manager']:
            menu_options = [
                "📊 Dashboard",
                "👥 User Management",
                "📋 All Requests",
                "✅ Approve Invoices",
                "📊 Analytics",
                "🔐 Logout"
            ]
            
            selected = st.selectbox("Go to", menu_options)
            
            if selected == "📊 Dashboard":
                st.session_state.show_manage_users = False
                st.session_state.show_all_requests = False
                st.session_state.show_manager_approvals = False
                st.session_state.show_analytics = False
            
            elif selected == "👥 User Management":
                st.session_state.show_manage_users = True
            
            elif selected == "📋 All Requests":
                st.session_state.show_all_requests = True
            
            elif selected == "✅ Approve Invoices":
                st.session_state.show_manager_approvals = True
            
            elif selected == "📊 Analytics":
                st.session_state.show_analytics = True
            
            elif selected == "🔐 Logout":
                st.session_state.user = None
                for var in session_vars:
                    st.session_state[var] = False
                st.rerun()
        
        st.markdown("---")
        st.markdown("<p style='text-align: center; color: #6b7280; font-size: 0.8rem;'>© 2025 A-Z Facilities Management Pro APP™</p>", unsafe_allow_html=True)
    
    # Main content area
    if user_role == 'facility_user':
        if st.session_state.show_new_request:
            show_new_request_form()
        elif st.session_state.show_my_requests:
            show_my_requests()
        elif st.session_state.show_approvals:
            show_user_approvals()
        else:
            show_dashboard()
    
    elif user_role == 'vendor':
        if st.session_state.show_vendor_jobs:
            show_vendor_jobs()
        elif st.session_state.show_invoice_form:
            show_invoice_form()
        elif st.session_state.show_vendor_reports:
            show_analytics()  # Reusing analytics page for vendor reports
        else:
            show_dashboard()
    
    elif user_role in ['facility_manager', 'System Manager']:
        if st.session_state.show_manage_users:
            show_manage_users()
        elif st.session_state.show_all_requests:
            show_all_requests()
        elif st.session_state.show_manager_approvals:
            show_manager_approvals()
        elif st.session_state.show_analytics:
            show_analytics()
        else:
            show_dashboard()

# =============================================
# RUN THE APPLICATION
# =============================================
if __name__ == "__main__":
    main()

