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
# DATABASE FUNCTIONS - MOVED TO TOP
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
# PASSWORD HASHING FUNCTIONS
# =============================================
def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    return stored_password == hashlib.sha256(provided_password.encode()).hexdigest()

def generate_password(length=8):
    """Generate a random password"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(characters) for _ in range(length))

# =============================================
# DATABASE SETUP - ENHANCED VERSION
# =============================================
def init_database():
    try:
        conn = sqlite3.connect('facilities_management.db', check_same_thread=False)
        cursor = conn.cursor()
        
        # Users table - UPDATED with status field
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                vendor_type TEXT,
                status TEXT DEFAULT 'pending', -- pending, approved, rejected
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
        
        # Vendors table - UPDATED with status field
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
                status TEXT DEFAULT 'pending', -- pending, approved, rejected
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
        try:
            if os.path.exists('facilities_management.db'):
                os.remove('facilities_management.db')
            print("Old database removed, please restart the app")
        except:
            pass

# =============================================
# ENSURE DEFAULT ACCOUNTS FUNCTION - FIXED VERSION
# =============================================
def ensure_vendor_records():
    """Ensure vendor records exist for vendor accounts"""
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
            print(f"Created vendor record for {company_name}")

def ensure_default_accounts():
    """Ensure default accounts exist with correct passwords"""
    default_accounts = [
        ('facility_manager', 'manager123', 'facility_manager', 'System Manager'),
        ('facility_user', 'user123', 'facility_user', 'Sample User'),
        ('hvac_vendor', 'vendor123', 'vendor', 'HVAC Vendor', 'HVAC'),
        ('generator_vendor', 'vendor123', 'vendor', 'Generator Vendor', 'Generator'),
        ('fixture_vendor', 'vendor123', 'vendor', 'Fixture Vendor', 'Fixture and Fittings'),
        ('building_vendor', 'vendor123', 'vendor', 'Building Vendor', 'Building Maintenance'),
    ]
    
    # First check if database has any users
    existing_users = execute_query("SELECT COUNT(*) as count FROM users")
    user_count = existing_users[0]['count'] if existing_users else 0
    
    if user_count > 0:
        print(f"Database already has {user_count} users, skipping default account creation")
        return
    
    print("Creating default accounts...")
    
    for account in default_accounts:
        if len(account) == 4:  # User account
            username, password, role, full_name = account
            vendor_type = None
        else:  # Vendor account
            username, password, role, full_name, vendor_type = account
        
        # Check if user exists
        existing = execute_query("SELECT * FROM users WHERE username = ?", (username,))
        
        if not existing:
            # Create new user
            password_hash = hash_password(password)
            success = execute_update(
                '''INSERT INTO users (username, password_hash, role, status, full_name, vendor_type, approved_by) 
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (username, password_hash, role, 'approved', full_name, vendor_type, 'system')
            )
            if success:
                print(f"✅ Created user: {username} (Role: {role})")
            else:
                print(f"❌ Failed to create user: {username}")
        else:
            print(f"⚠️ User {username} already exists")
    
    # Also ensure vendor records exist
    ensure_vendor_records()

# Initialize database and create default accounts
init_database()
ensure_default_accounts()

# =============================================
# AUTHENTICATION & USER MANAGEMENT FUNCTIONS
# =============================================
def authenticate_user(username, password):
    """Authenticate user with username and password"""
    print(f"Attempting to authenticate user: {username}")
    
    # First, check if user exists and is approved
    user = execute_query('SELECT * FROM users WHERE username = ? AND status = ?', (username, 'approved'))
    
    if not user:
        print(f"❌ No approved user found with username: {username}")
        # Check if user exists but not approved
        pending_user = execute_query('SELECT * FROM users WHERE username = ?', (username,))
        if pending_user:
            print(f"⚠️ User {username} exists but status is: {pending_user[0].get('status')}")
        return None
    
    user_data = user[0]
    print(f"Found user: {user_data['username']}, Role: {user_data['role']}")
    
    # Verify password
    provided_hash = hash_password(password)
    stored_hash = user_data['password_hash']
    
    print(f"Stored hash: {stored_hash[:10]}...")
    print(f"Provided hash: {provided_hash[:10]}...")
    
    if stored_hash == provided_hash:
        print(f"✅ Password verified for user: {username}")
        return user_data
    else:
        print(f"❌ Password verification failed for user: {username}")
        return None

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
    """Show the workflow status for a request - FIXED to avoid HTML display issues"""
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
# ENHANCED LOGIN PAGE WITH REGISTRATION OPTIONS
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
                            st.success("✅ Login successful! Redirecting...")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        show_user_registration_form()
    
    with tab3:
        show_vendor_registration_form()
    
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #6b7280;'>© 2025 A-Z Facilities Management Pro APP™. Developed by Abdulahi Ibrahim.</p>", unsafe_allow_html=True)

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
# ENHANCED PDF GENERATION FUNCTIONS
# =============================================
def generate_final_report_pdf(request_data, invoice_data=None):
    """Generate final approved PDF report"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=30,
        alignment=1,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#3b82f6'),
        spaceAfter=15,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'NormalCustom',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    # Header
    story.append(Paragraph("A-Z FACILITIES MANAGEMENT PRO APP™", title_style))
    story.append(Paragraph("FINAL APPROVED JOB REPORT", ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#10b981'),
        spaceAfter=20,
        alignment=1,
        fontName='Helvetica-Bold'
    )))
    story.append(Paragraph(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    story.append(Paragraph("Currency: NGN (₦)", normal_style))
    story.append(Spacer(1, 20))
    
    # Job Information
    story.append(Paragraph("JOB INFORMATION", subtitle_style))
    
    job_info_data = [
        ["Request ID:", safe_str(safe_get(request_data, 'id'))],
        ["Title:", safe_str(safe_get(request_data, 'title'))],
        ["Description:", safe_str(safe_get(request_data, 'description'))],
        ["Location:", safe_str(safe_get(request_data, 'location'), 'Common Area')],
        ["Facility Type:", safe_str(safe_get(request_data, 'facility_type'))],
        ["Priority:", safe_str(safe_get(request_data, 'priority'))],
        ["Created By:", safe_str(safe_get(request_data, 'created_by'))],
        ["Assigned Vendor:", safe_str(safe_get(request_data, 'assigned_vendor'), 'Not assigned')],
        ["Created Date:", safe_str(safe_get(request_data, 'created_date'))],
        ["Completed Date:", safe_str(safe_get(request_data, 'completed_date'), 'Not completed')]
    ]
    
    job_table = Table(job_info_data, colWidths=[150, 300])
    job_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(job_table)
    story.append(Spacer(1, 15))
    
    # Job Breakdown
    if safe_get(request_data, 'job_breakdown'):
        story.append(Paragraph("JOB BREAKDOWN DETAILS", subtitle_style))
        story.append(Paragraph(safe_str(safe_get(request_data, 'job_breakdown')), normal_style))
        story.append(Spacer(1, 15))
    
    # Completion Notes
    if safe_get(request_data, 'completion_notes'):
        story.append(Paragraph("COMPLETION NOTES", subtitle_style))
        story.append(Paragraph(safe_str(safe_get(request_data, 'completion_notes')), normal_style))
        story.append(Spacer(1, 15))
    
    # Invoice Information
    if invoice_data:
        story.append(Paragraph("INVOICE DETAILS", subtitle_style))
        
        invoice_info = [
            ["Invoice Number:", safe_str(safe_get(invoice_data, 'invoice_number'))],
            ["Invoice Date:", safe_str(safe_get(invoice_data, 'invoice_date'))],
            ["Details of Work:", safe_str(safe_get(invoice_data, 'details_of_work'))],
            ["Quantity:", safe_str(safe_get(invoice_data, 'quantity'), '1')],
            ["Unit Cost:", format_ngn(safe_get(invoice_data, 'unit_cost'))],
            ["Amount:", format_ngn(safe_get(invoice_data, 'amount'))],
            ["Labour/Service Charge:", format_ngn(safe_get(invoice_data, 'labour_charge'))],
            ["VAT Applicable:", "Yes (7.5%)" if safe_get(invoice_data, 'vat_applicable') else "No"],
            ["VAT Amount:", format_ngn(safe_get(invoice_data, 'vat_amount'))],
            ["Total Amount:", format_ngn(safe_get(invoice_data, 'total_amount'))]
        ]
        
        invoice_table = Table(invoice_info, colWidths=[150, 300])
        invoice_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#10b981')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f0fdf4')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(invoice_table)
        story.append(Spacer(1, 15))
    
    # Approval Status with Dates
    story.append(Paragraph("APPROVAL HISTORY", subtitle_style))
    approval_data = [
        ["Approval Type", "Status", "Approved By", "Date"],
        ["Department Approval", 
         "✅ APPROVED" if safe_get(request_data, 'requesting_dept_approval') else "❌ PENDING",
         safe_str(safe_get(request_data, 'created_by'), 'N/A'),
         safe_str(safe_get(request_data, 'department_approval_date'), '-')],
        ["Facilities Manager Approval", 
         "✅ APPROVED" if safe_get(request_data, 'facilities_manager_approval') else "❌ PENDING",
         "Facility Manager",
         safe_str(safe_get(request_data, 'manager_approval_date'), '-')]
    ]
    
    approval_table = Table(approval_data, colWidths=[150, 100, 120, 130])
    approval_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(approval_table)
    
    # Final Approval Stamp
    if safe_get(request_data, 'facilities_manager_approval'):
        story.append(Spacer(1, 30))
        story.append(Paragraph("""
        <para alignment="center">
        <font color="#10b981" size="14"><b>✓ FINALLY APPROVED</b></font><br/>
        <font size="10">This job has been fully approved and completed.</font>
        </para>
        """, ParagraphStyle('Stamp', parent=styles['Normal'], alignment=1)))
    
    # Footer
    story.append(Spacer(1, 40))
    footer = Paragraph(
        f"© 2025 A-Z Facilities Management Pro APP™. Developed by Abdulahi Ibrahim. "
        f"Final Report Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.gray, alignment=1)
    )
    story.append(footer)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

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
    
    pending_vendors = get_pending_vendors()
    
    if not pending_vendors:
        st.info("🎉 No pending vendor approvals")
        return
    
    st.markdown(f"<div class='card'><h4>⏳ {len(pending_vendors)} Vendor(s) Pending Approval</h4></div>", unsafe_allow_html=True)
    
    for vendor in pending_vendors:
        with st.expander(f"🏢 {safe_str(safe_get(vendor, 'company_name'))} - {safe_str(safe_get(vendor, 'contact_person'))}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Company Name:** {safe_str(safe_get(vendor, 'company_name'))}")
                st.write(f"**Contact Person:** {safe_str(safe_get(vendor, 'contact_person'))}")
                st.write(f"**Email:** {safe_str(safe_get(vendor, 'email'))}")
                st.write(f"**Phone:** {safe_str(safe_get(vendor, 'phone'))}")
                st.write(f"**Vendor Type:** {safe_str(safe_get(vendor, 'vendor_type'))}")
                st.write(f"**Services Offered:** {safe_str(safe_get(vendor, 'services_offered'))}")
                st.write(f"**Address:** {safe_str(safe_get(vendor, 'address'))}")
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
                        # Approve vendor and associated user
                        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        # Update vendor
                        vendor_success = execute_update(
                            '''UPDATE vendors 
                            SET status = 'approved', 
                                approved_by = ?,
                                approval_date = ?
                            WHERE id = ?''',
                            (st.session_state.user['username'], current_time, safe_get(vendor, 'id'))
                        )
                        
                        # Update user account
                        user_success = execute_update(
                            '''UPDATE users 
                            SET status = 'approved', 
                                approved_by = ?,
                                approval_date = ?
                            WHERE username = ?''',
                            (st.session_state.user['username'], current_time, safe_get(vendor, 'username'))
                        )
                        
                        if vendor_success and user_success:
                            st.success(f"✅ Vendor {safe_get(vendor, 'company_name')} approved successfully!")
                            st.rerun()
                
                with col_b:
                    if st.button(f"Reject Vendor", key=f"reject_vendor_{safe_get(vendor, 'id')}", 
                               use_container_width=True, type="secondary"):
                        # Reject vendor and associated user
                        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        # Update vendor
                        vendor_success = execute_update(
                            '''UPDATE vendors 
                            SET status = 'rejected', 
                                approved_by = ?,
                                approval_date = ?
                            WHERE id = ?''',
                            (st.session_state.user['username'], current_time, safe_get(vendor, 'id'))
                        )
                        
                        # Update user account
                        user_success = execute_update(
                            '''UPDATE users 
                            SET status = 'rejected', 
                                approved_by = ?,
                                approval_date = ?
                            WHERE username = ?''',
                            (st.session_state.user['username'], current_time, safe_get(vendor, 'username'))
                        )
                        
                        if vendor_success and user_success:
                            st.warning(f"❌ Vendor {safe_get(vendor, 'company_name')} rejected.")
                            st.rerun()

def show_user_directory():
    """Show all approved users"""
    st.markdown("### 📋 User Directory")
    
    # Get all approved users
    users = execute_query('''
        SELECT * FROM users 
        WHERE status = 'approved'
        ORDER BY role, full_name
    ''')
    
    if not users:
        st.info("📭 No approved users found")
        return
    
    st.markdown(f"<div class='card'><h4>👥 {len(users)} Approved User(s)</h4></div>", unsafe_allow_html=True)
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        role_filter = st.selectbox("Filter by Role", ["All", "Facility Manager", "Facility User", "Vendor"])
    with col2:
        search_term = st.text_input("Search by name or username", "")
    
    # Apply filters
    filtered_users = users
    if role_filter != "All":
        role_map = {
            "Facility Manager": "facility_manager",
            "Facility User": "facility_user",
            "Vendor": "vendor"
        }
        filtered_users = [u for u in filtered_users if u.get('role') == role_map.get(role_filter)]
    
    if search_term:
        filtered_users = [u for u in filtered_users 
                         if search_term.lower() in safe_str(u.get('full_name', '')).lower() 
                         or search_term.lower() in safe_str(u.get('username', '')).lower()]
    
    # Display users
    for user in filtered_users:
        role = safe_get(user, 'role')
        role_icon = {
            'facility_manager': '👑',
            'facility_user': '👤',
            'vendor': '🏢'
        }.get(role, '👤')
        
        with st.expander(f"{role_icon} {safe_str(safe_get(user, 'full_name'))} ({safe_str(safe_get(user, 'username'))})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Username:** {safe_str(safe_get(user, 'username'))}")
                st.write(f"**Full Name:** {safe_str(safe_get(user, 'full_name'))}")
                st.write(f"**Email:** {safe_str(safe_get(user, 'email'))}")
                st.write(f"**Phone:** {safe_str(safe_get(user, 'phone'))}")
                st.write(f"**Role:** {role.replace('_', ' ').title()}")
                
                if role == 'facility_user':
                    st.write(f"**Department:** {safe_str(safe_get(user, 'department'))}")
                elif role == 'vendor':
                    st.write(f"**Vendor Type:** {safe_str(safe_get(user, 'vendor_type'))}")
            
            with col2:
                st.write(f"**Account Status:** Approved")
                st.write(f"**Approved By:** {safe_str(safe_get(user, 'approved_by'), 'System')}")
                st.write(f"**Approval Date:** {safe_str(safe_get(user, 'approval_date'))}")
                st.write(f"**Created Date:** {safe_str(safe_get(user, 'created_date'))}")
                
                # Action buttons
                if st.session_state.user['role'] == 'facility_manager':
                    st.markdown("### ⚙️ Account Actions")
                    
                    if st.button(f"Reset Password", key=f"reset_pass_{safe_get(user, 'id')}", 
                               use_container_width=True):
                        # Generate new password
                        new_password = generate_password()
                        new_password_hash = hash_password(new_password)
                        
                        if execute_update(
                            'UPDATE users SET password_hash = ? WHERE id = ?',
                            (new_password_hash, safe_get(user, 'id'))
                        ):
                            st.success(f"✅ Password reset for {safe_get(user, 'username')}")
                            st.info(f"**New Password:** `{new_password}`")
                            st.warning("⚠️ Please share this password securely with the user.")

# =============================================
# MAIN APPLICATION FUNCTIONS
# =============================================
def show_create_request():
    st.markdown("<h1 class='app-title'>📝 Create Maintenance Request</h1>", unsafe_allow_html=True)
    
    with st.form("create_request_form"):
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Request Title *", placeholder="Brief title of the maintenance request")
            location = st.selectbox(
                "Location *",
                ["Water Treatment Plant", "Finance", "HR", "Admin", "Common Area", 
                 "Production", "Warehouse", "Office Building", "Laboratory", "Parking Lot"]
            )
            facility_type = st.selectbox(
                "Facility Type *",
                ["HVAC (Cooling Systems)", "Generator Maintenance", "Fixture and Fittings", 
                 "Building Maintenance", "HSE", "Space Management", "Electrical", "Plumbing"]
            )
        
        with col2:
            priority = st.selectbox("Priority *", ["Low", "Medium", "High", "Critical"])
        
        description = st.text_area(
            "Description *", 
            height=100,
            placeholder="Please provide detailed description of the maintenance request..."
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        submitted = st.form_submit_button("📤 Submit Request", use_container_width=True)
        
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
                else:
                    st.error("❌ Failed to create request")

def show_my_requests():
    """Enhanced version of show_my_requests with better UI and approval workflow"""
    st.markdown("<h1 class='app-title'>📋 My Maintenance Requests</h1>", unsafe_allow_html=True)
    
    user_requests = get_user_requests(st.session_state.user['username'])
    
    if not user_requests:
        st.info("📭 No maintenance requests found")
        return
    
    # Stats with cleaner display
    st.markdown("### 📊 Request Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_metric_card("Total", len(user_requests), "📋")
    
    with col2:
        pending_count = len([r for r in user_requests if safe_get(r, 'status') == 'Pending'])
        create_metric_card("Pending", pending_count, "⏳")
    
    with col3:
        completed_count = len([r for r in user_requests if safe_get(r, 'status') == 'Completed'])
        create_metric_card("Completed", completed_count, "✅")
    
    with col4:
        approved_count = len([r for r in user_requests if safe_get(r, 'status') == 'Approved'])
        create_metric_card("Approved", approved_count, "👍")
    
    st.markdown("---")
    
    # Display all requests
    for req in user_requests:
        status = safe_get(req, 'status')
        status_icon = {
            'Pending': '⏳',
            'Assigned': '👷',
            'Completed': '✅',
            'Approved': '👍'
        }.get(status, '📋')
        
        priority = safe_get(req, 'priority')
        priority_color = {
            'Low': '#10b981',
            'Medium': '#f59e0b',
            'High': '#ef4444',
            'Critical': '#dc2626'
        }.get(priority, '#6b7280')
        
        with st.expander(f"{status_icon} Request #{safe_get(req, 'id')}: {safe_str(safe_get(req, 'title'))}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Location:** {safe_str(safe_get(req, 'location'), 'Common Area')}")
                st.write(f"**Facility Type:** {safe_str(safe_get(req, 'facility_type'))}")
                st.write(f"**Priority:** <span style='color:{priority_color}; font-weight:bold;'>{priority}</span>", unsafe_allow_html=True)
                st.write(f"**Status:** {status_icon} {status}")
                st.write(f"**Created Date:** {safe_str(safe_get(req, 'created_date'))}")
                
                # Show workflow status
                if status in ['Completed', 'Approved']:
                    st.markdown("---")
                    st.markdown("### 📋 Approval Status")
                    st.write(f"**Department Approval:** {'✅ Approved' if safe_get(req, 'requesting_dept_approval') else '⏳ Pending'}")
                    st.write(f"**Manager Approval:** {'✅ Approved' if safe_get(req, 'facilities_manager_approval') else '⏳ Pending'}")
            
            with col2:
                st.write(f"**Description:** {safe_str(safe_get(req, 'description'))}")
                if safe_get(req, 'assigned_vendor'):
                    vendor_info = execute_query(
                        'SELECT company_name FROM vendors WHERE username = ?',
                        (safe_get(req, 'assigned_vendor'),)
                    )
                    vendor_name = vendor_info[0]['company_name'] if vendor_info else safe_get(req, 'assigned_vendor')
                    st.write(f"**Assigned Vendor:** {vendor_name}")
                
                if safe_get(req, 'completion_notes'):
                    st.write(f"**Completion Notes:**")
                    st.info(safe_str(safe_get(req, 'completion_notes')))
                
                if safe_get(req, 'job_breakdown'):
                    with st.expander("View Job Breakdown"):
                        st.write(safe_str(safe_get(req, 'job_breakdown')))
                
                if safe_get(req, 'invoice_amount'):
                    st.write(f"**Invoice Amount:** {format_ngn(safe_get(req, 'invoice_amount'))}")
                    st.write(f"**Invoice Number:** {safe_str(safe_get(req, 'invoice_number'), 'N/A')}")
                    
                    # Get detailed invoice
                    invoice_details = execute_query(
                        'SELECT * FROM invoices WHERE invoice_number = ?', 
                        (safe_get(req, 'invoice_number'),)
                    )
                    
                    if invoice_details:
                        invoice = invoice_details[0]
                        with st.expander("View Invoice Details"):
                            st.write(f"**Details:** {safe_str(safe_get(invoice, 'details_of_work'))}")
                            st.write(f"**Quantity:** {safe_str(safe_get(invoice, 'quantity'))}")
                            st.write(f"**Unit Cost:** {format_ngn(safe_get(invoice, 'unit_cost'))}")
                            st.write(f"**Total:** {format_ngn(safe_get(invoice, 'total_amount'))}")
                
                # ✅ IMPORTANT: Department Approval Button for Completed Jobs
                if (status == 'Completed' and 
                    not safe_get(req, 'requesting_dept_approval') and
                    safe_get(req, 'created_by') == st.session_state.user['username']):
                    
                    st.markdown("---")
                    st.markdown("### ✅ Department Approval Required")
                    
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        if st.button(f"Approve Job Completion", 
                                   key=f"dept_approve_myreq_{safe_get(req, 'id')}", 
                                   use_container_width=True,
                                   type="primary"):
                            # Update department approval
                            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            if execute_update(
                                '''UPDATE maintenance_requests 
                                SET requesting_dept_approval = 1, 
                                    department_approval_date = ?
                                WHERE id = ?''',
                                (current_time, safe_get(req, 'id'))
                            ):
                                st.success("✅ Department approval granted! Sent to facility manager for final approval.")
                                st.rerun()
                    
                    with col_b:
                        if st.button("Request Changes", 
                                   key=f"dept_reject_myreq_{safe_get(req, 'id')}", 
                                   use_container_width=True,
                                   type="secondary"):
                            st.warning("Changes requested from vendor")
                            # In a real app, you would add a notes field and send back to vendor
                
                # ✅ Show download button for fully approved jobs
                elif (status == 'Approved' and 
                      safe_get(req, 'requesting_dept_approval') and 
                      safe_get(req, 'facilities_manager_approval')):
                    
                    st.markdown("---")
                    st.markdown("### 📄 Final Report Available")
                    
                    # Get invoice for PDF
                    invoice_details = execute_query(
                        'SELECT * FROM invoices WHERE request_id = ?', 
                        (safe_get(req, 'id'),)
                    )
                    
                    if invoice_details:
                        invoice = invoice_details[0]
                        pdf_buffer = generate_final_report_pdf(req, invoice)
                        
                        st.download_button(
                            label="📄 Download Final Approved Report",
                            data=pdf_buffer.getvalue(),
                            file_name=f"Final_Approved_Report_Job_{safe_get(req, 'id')}.pdf",
                            mime="application/pdf",
                            key=f"user_final_download_{safe_get(req, 'id')}",
                            use_container_width=True
                        )

# =============================================
# DEPARTMENT APPROVAL PAGE FOR FACILITY USER
# =============================================
def show_department_approval():
    """Page for facility user to approve completed jobs from vendors"""
    st.markdown("<h1 class='app-title'>✅ Department Approval</h1>", unsafe_allow_html=True)
    
    # Get requests that need department approval (created by this user)
    pending_approvals = get_requests_for_user_approval(st.session_state.user['username'])
    
    if not pending_approvals:
        st.info("🎉 No jobs pending your department approval")
        return
    
    st.markdown(f"<div class='card'><h4>📋 {len(pending_approvals)} Job(s) Awaiting Your Approval</h4></div>", unsafe_allow_html=True)
    
    for req in pending_approvals:
        with st.expander(f"🔄 Job #{safe_get(req, 'id')}: {safe_str(safe_get(req, 'title'))}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📝 Job Details")
                st.write(f"**Title:** {safe_str(safe_get(req, 'title'))}")
                st.write(f"**Description:** {safe_str(safe_get(req, 'description'))}")
                st.write(f"**Location:** {safe_str(safe_get(req, 'location'), 'Common Area')}")
                st.write(f"**Facility Type:** {safe_str(safe_get(req, 'facility_type'))}")
                st.write(f"**Priority:** {safe_str(safe_get(req, 'priority'))}")
                st.write(f"**Status:** {safe_str(safe_get(req, 'status'))}")
                st.write(f"**Completed Date:** {safe_str(safe_get(req, 'completed_date'))}")
                
                # Show assigned vendor details
                if safe_get(req, 'assigned_vendor'):
                    vendor_info = execute_query(
                        'SELECT company_name FROM vendors WHERE username = ?',
                        (safe_get(req, 'assigned_vendor'),)
                    )
                    vendor_name = vendor_info[0]['company_name'] if vendor_info else safe_get(req, 'assigned_vendor')
                    st.write(f"**Vendor:** {vendor_name}")
            
            with col2:
                st.markdown("### 🛠️ Work Completed")
                if safe_get(req, 'job_breakdown'):
                    st.write(f"**Job Breakdown:**")
                    st.info(safe_str(safe_get(req, 'job_breakdown')))
                
                if safe_get(req, 'completion_notes'):
                    st.write(f"**Completion Notes:**")
                    st.info(safe_str(safe_get(req, 'completion_notes')))
                
                # Show invoice details if available
                if safe_get(req, 'invoice_number'):
                    st.markdown("### 🧾 Invoice Details")
                    st.write(f"**Invoice Number:** {safe_str(safe_get(req, 'invoice_number'))}")
                    st.write(f"**Invoice Amount:** {format_ngn(safe_get(req, 'invoice_amount'))}")
                    
                    # Get detailed invoice
                    invoice_details = execute_query(
                        'SELECT * FROM invoices WHERE invoice_number = ?', 
                        (safe_get(req, 'invoice_number'),)
                    )
                    
                    if invoice_details:
                        invoice = invoice_details[0]
                        with st.expander("View Invoice Details"):
                            st.write(f"**Details:** {safe_str(safe_get(invoice, 'details_of_work'))}")
                            st.write(f"**Quantity:** {safe_str(safe_get(invoice, 'quantity'))}")
                            st.write(f"**Unit Cost:** {format_ngn(safe_get(invoice, 'unit_cost'))}")
                            st.write(f"**Total:** {format_ngn(safe_get(invoice, 'total_amount'))}")
            
            # Show workflow status
            show_workflow_status(req)
            
            # Approval buttons
            st.markdown("---")
            st.markdown("### ✅ Department Approval Action")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(f"Approve Job Completion", key=f"dept_approve_{safe_get(req, 'id')}", 
                           use_container_width=True, type="primary"):
                    # Update department approval
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    if execute_update(
                        '''UPDATE maintenance_requests 
                        SET requesting_dept_approval = 1, 
                            department_approval_date = ?
                        WHERE id = ?''',
                        (current_time, safe_get(req, 'id'))
                    ):
                        st.success("✅ Department approval granted! Sent to facility manager for final approval.")
                        st.rerun()
            
            with col3:
                if st.button("Request Changes", key=f"dept_reject_{safe_get(req, 'id')}", 
                           use_container_width=True, type="secondary"):
                    st.warning("Changes requested from vendor")
                    # In a real app, you would add a notes field and send back to vendor

# =============================================
# FINAL APPROVAL PAGE FOR FACILITY MANAGER
# =============================================
def show_final_approval():
    """Page for facility manager to give final approval"""
    st.markdown("<h1 class='app-title'>✅ Final Manager Approval</h1>", unsafe_allow_html=True)
    
    # Get requests that need final manager approval
    pending_final_approvals = get_requests_for_manager_approval()
    
    if not pending_final_approvals:
        st.info("🎉 No jobs pending final approval")
        return
    
    st.markdown(f"<div class='card'><h4>📋 {len(pending_final_approvals)} Job(s) Awaiting Final Approval</h4></div>", unsafe_allow_html=True)
    
    for req in pending_final_approvals:
        with st.expander(f"📄 Job #{safe_get(req, 'id')}: {safe_str(safe_get(req, 'title'))} - Department Approved: {safe_str(safe_get(req, 'department_approval_date'))}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📝 Job Details")
                st.write(f"**Title:** {safe_str(safe_get(req, 'title'))}")
                st.write(f"**Created By:** {safe_str(safe_get(req, 'created_by'))}")
                st.write(f"**Location:** {safe_str(safe_get(req, 'location'), 'Common Area')}")
                st.write(f"**Facility Type:** {safe_str(safe_get(req, 'facility_type'))}")
                st.write(f"**Completed Date:** {safe_str(safe_get(req, 'completed_date'))}")
                st.write(f"**Department Approved:** {safe_str(safe_get(req, 'department_approval_date'))}")
                
                # Show vendor details
                if safe_get(req, 'assigned_vendor'):
                    vendor_info = execute_query(
                        'SELECT company_name FROM vendors WHERE username = ?',
                        (safe_get(req, 'assigned_vendor'),)
                    )
                    vendor_name = vendor_info[0]['company_name'] if vendor_info else safe_get(req, 'assigned_vendor')
                    st.write(f"**Vendor:** {vendor_name}")
            
            with col2:
                st.markdown("### 🛠️ Work Summary")
                if safe_get(req, 'job_breakdown'):
                    st.write(f"**Job Breakdown:**")
                    st.info(safe_str(safe_get(req, 'job_breakdown')))
                
                # Show invoice details
                if safe_get(req, 'invoice_number'):
                    st.markdown("### 🧾 Invoice Summary")
                    st.write(f"**Invoice Number:** {safe_str(safe_get(req, 'invoice_number'))}")
                    st.write(f"**Invoice Amount:** {format_ngn(safe_get(req, 'invoice_amount'))}")
                    
                    # Get detailed invoice
                    invoice_details = execute_query(
                        'SELECT * FROM invoices WHERE invoice_number = ?', 
                        (safe_get(req, 'invoice_number'),)
                    )
                    
                    if invoice_details:
                        invoice = invoice_details[0]
                        st.write(f"**Total Amount:** {format_ngn(safe_get(invoice, 'total_amount'))}")
                        st.write(f"**VAT Applied:** {'Yes' if safe_get(invoice, 'vat_applicable') else 'No'}")
            
            # Show complete workflow
            show_workflow_status(req)
            
            # Final approval section with PDF generation
            st.markdown("---")
            st.markdown("### ✅ Final Approval & Report Generation")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(f"✓ Grant Final Approval", key=f"final_approve_{safe_get(req, 'id')}", 
                           use_container_width=True, type="primary"):
                    # Update final approval
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    if execute_update(
                        '''UPDATE maintenance_requests 
                        SET facilities_manager_approval = 1, 
                            manager_approval_date = ?,
                            status = 'Approved'
                        WHERE id = ?''',
                        (current_time, safe_get(req, 'id'))
                    ):
                        st.success("✅ Final approval granted! Job is now fully approved.")
                        st.rerun()
            
            with col2:
                # Get invoice details for PDF
                invoice_details = execute_query(
                    'SELECT * FROM invoices WHERE request_id = ?', 
                    (safe_get(req, 'id'),)
                )
                
                if invoice_details:
                    invoice = invoice_details[0]
                    
                    # Generate and offer PDF download
                    pdf_buffer = generate_final_report_pdf(req, invoice)
                    
                    st.download_button(
                        label="📄 Download Final Report",
                        data=pdf_buffer.getvalue(),
                        file_name=f"Final_Approved_Report_Job_{safe_get(req, 'id')}.pdf",
                        mime="application/pdf",
                        key=f"download_{safe_get(req, 'id')}",
                        use_container_width=True
                    )
                else:
                    st.warning("No invoice found for this job")

# =============================================
# MANAGE REQUESTS FOR FACILITY MANAGER
# =============================================
def show_manage_requests():
    st.markdown("<h1 class='app-title'>🛠️ Manage Maintenance Requests</h1>", unsafe_allow_html=True)
    
    all_requests = get_all_requests()
    
    if not all_requests:
        st.info("📭 No maintenance requests found")
        return
    
    # Stats
    st.markdown("### 📊 Request Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_metric_card("Total", len(all_requests), "📊")
    
    with col2:
        pending_count = len([r for r in all_requests if safe_get(r, 'status') == 'Pending'])
        create_metric_card("Pending", pending_count, "⏳")
    
    with col3:
        assigned_count = len([r for r in all_requests if safe_get(r, 'status') == 'Assigned'])
        create_metric_card("Assigned", assigned_count, "👷")
    
    with col4:
        completed_count = len([r for r in all_requests if safe_get(r, 'status') == 'Completed'])
        create_metric_card("Completed", completed_count, "✅")
    
    st.markdown("---")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Assigned", "Completed", "Approved"])
    with col2:
        priority_filter = st.selectbox("Filter by Priority", ["All", "Low", "Medium", "High", "Critical"])
    
    # Apply filters
    filtered_requests = all_requests
    if status_filter != "All":
        filtered_requests = [r for r in filtered_requests if safe_get(r, 'status') == status_filter]
    if priority_filter != "All":
        filtered_requests = [r for r in filtered_requests if safe_get(r, 'priority') == priority_filter]
    
    st.markdown(f"<div class='card'><h4>📋 Showing {len(filtered_requests)} request(s)</h4></div>", unsafe_allow_html=True)
    
    # Display filtered requests
    for req in filtered_requests:
        status = safe_get(req, 'status')
        status_icon = {
            'Pending': '⏳',
            'Assigned': '👷',
            'Completed': '✅',
            'Approved': '👍'
        }.get(status, '📋')
        
        with st.expander(f"{status_icon} Request #{safe_get(req, 'id')}: {safe_str(safe_get(req, 'title'))}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Title:** {safe_str(safe_get(req, 'title'))}")
                st.write(f"**Description:** {safe_str(safe_get(req, 'description'))}")
                st.write(f"**Location:** {safe_str(safe_get(req, 'location'), 'Common Area')}")
                st.write(f"**Facility Type:** {safe_str(safe_get(req, 'facility_type'))}")
                st.write(f"**Priority:** {safe_str(safe_get(req, 'priority'))}")
                st.write(f"**Status:** {status}")
                st.write(f"**Created By:** {safe_str(safe_get(req, 'created_by'))}")
                st.write(f"**Created Date:** {safe_str(safe_get(req, 'created_date'))}")
            
            with col2:
                # Show workflow status
                show_workflow_status(req)
                
                # Management actions based on status
                if status == 'Pending':
                    st.subheader("Assign to Vendor")
                    
                    facility_type = safe_str(safe_get(req, 'facility_type'))
                    facility_to_vendor_map = {
                        "HVAC (Cooling Systems)": "HVAC",
                        "Generator Maintenance": "Generator",
                        "Fixture and Fittings": "Fixture and Fittings",
                        "Building Maintenance": "Building Maintenance",
                        "HSE": "HSE",
                        "Space Management": "Space Management"
                    }
                    
                    vendor_type = facility_to_vendor_map.get(facility_type, facility_type)
                    
                    # Get approved vendors
                    vendors = execute_query('''
                        SELECT v.* FROM vendors v 
                        WHERE v.vendor_type = ? AND v.status = 'approved'
                    ''', (vendor_type,))
                    
                    if vendors:
                        vendor_options = {f"{v['company_name']}": v['username'] for v in vendors}
                        selected_vendor_key = st.selectbox(
                            "Select Vendor",
                            options=list(vendor_options.keys()),
                            key=f"vendor_{safe_get(req, 'id')}"
                        )
                        
                        if selected_vendor_key and st.button(f"Assign to {selected_vendor_key}", key=f"assign_{safe_get(req, 'id')}"):
                            if execute_update(
                                'UPDATE maintenance_requests SET status = ?, assigned_vendor = ? WHERE id = ?',
                                ('Assigned', vendor_options[selected_vendor_key], safe_get(req, 'id'))
                            ):
                                st.success(f"✅ Request assigned to {selected_vendor_key}!")
                                st.rerun()
                    else:
                        st.warning(f"No approved vendors found for {facility_type}")

# =============================================
# VENDOR FUNCTIONS
# =============================================
def show_assigned_jobs():
    """Show assigned jobs to vendor with completion form"""
    st.markdown("<h1 class='app-title'>🔧 Assigned Jobs</h1>", unsafe_allow_html=True)
    
    vendor_username = st.session_state.user['username']
    assigned_jobs = get_vendor_requests(vendor_username)
    
    # Filter only assigned jobs
    assigned_jobs = [job for job in assigned_jobs if safe_get(job, 'status') == 'Assigned']
    
    if not assigned_jobs:
        st.info("🎉 No jobs assigned to you at the moment")
        return
    
    st.markdown(f"<div class='card'><h4>🔧 {len(assigned_jobs)} Job(s) Assigned to You</h4></div>", unsafe_allow_html=True)
    
    for job in assigned_jobs:
        with st.expander(f"🛠️ Job #{safe_get(job, 'id')}: {safe_str(safe_get(job, 'title'))}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📝 Job Details")
                st.write(f"**Title:** {safe_str(safe_get(job, 'title'))}")
                st.write(f"**Description:** {safe_str(safe_get(job, 'description'))}")
                st.write(f"**Location:** {safe_str(safe_get(job, 'location'), 'Common Area')}")
                st.write(f"**Facility Type:** {safe_str(safe_get(job, 'facility_type'))}")
                st.write(f"**Priority:** {safe_str(safe_get(job, 'priority'))}")
                st.write(f"**Created By:** {safe_str(safe_get(job, 'created_by'))}")
                st.write(f"**Created Date:** {safe_str(safe_get(job, 'created_date'))}")
            
            with col2:
                st.markdown("### 📋 Complete Job Form")
                
                with st.form(key=f"complete_job_{safe_get(job, 'id')}"):
                    job_breakdown = st.text_area(
                        "Job Breakdown/Details *",
                        height=100,
                        placeholder="Describe the work performed, materials used, hours spent, etc."
                    )
                    
                    completion_notes = st.text_area(
                        "Completion Notes",
                        height=80,
                        placeholder="Any additional notes about the job completion"
                    )
                    
                    # Invoice details section
                    st.markdown("### 🧾 Invoice Details")
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        details_of_work = st.text_input("Work Description *", 
                                                       value=safe_str(safe_get(job, 'description')),
                                                       placeholder="Description of work")
                        quantity = st.number_input("Quantity *", min_value=1, value=1)
                    with col_b:
                        unit_cost = st.number_input("Unit Cost (₦) *", min_value=0.0, value=1000.0, step=100.0)
                        labour_charge = st.number_input("Labour/Service Charge (₦)", min_value=0.0, value=0.0, step=100.0)
                    with col_c:
                        vat_applicable = st.checkbox("Apply 7.5% VAT", value=True)
                    
                    # Calculate amounts
                    amount = quantity * unit_cost
                    vat_amount = (amount + labour_charge) * 0.075 if vat_applicable else 0.0
                    total_amount = amount + labour_charge + vat_amount
                    
                    # Display calculated amounts
                    st.markdown("### 💰 Amount Summary")
                    st.write(f"**Amount:** ₦{amount:,.2f}")
                    st.write(f"**Labour Charge:** ₦{labour_charge:,.2f}")
                    st.write(f"**VAT ({'7.5%' if vat_applicable else '0%'}):** ₦{vat_amount:,.2f}")
                    st.write(f"**Total Amount:** ₦{total_amount:,.2f}")
                    
                    submitted = st.form_submit_button("✅ Mark Job as Completed", use_container_width=True)
                    
                    if submitted:
                        if not job_breakdown or not details_of_work:
                            st.error("❌ Please fill in all required fields (*)")
                        else:
                            # Generate invoice number
                            invoice_number = f"INV-{safe_get(job, 'id')}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                            
                            # Update job status and add completion details
                            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            
                            # First update the job
                            job_update_success = execute_update(
                                '''UPDATE maintenance_requests 
                                SET status = 'Completed',
                                    completion_notes = ?,
                                    job_breakdown = ?,
                                    completed_date = ?,
                                    invoice_amount = ?,
                                    invoice_number = ?
                                WHERE id = ?''',
                                (completion_notes, job_breakdown, current_time, total_amount, invoice_number, safe_get(job, 'id'))
                            )
                            
                            # Then create invoice
                            if job_update_success:
                                invoice_success = execute_update(
                                    '''INSERT INTO invoices 
                                    (invoice_number, request_id, vendor_username, details_of_work, 
                                     quantity, unit_cost, amount, labour_charge, vat_applicable, 
                                     vat_amount, total_amount) 
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                    (invoice_number, safe_get(job, 'id'), vendor_username, details_of_work,
                                     quantity, unit_cost, amount, labour_charge, 1 if vat_applicable else 0,
                                     vat_amount, total_amount)
                                )
                                
                                if invoice_success:
                                    st.success("✅ Job marked as completed! Invoice created. Waiting for department approval.")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to create invoice")

def show_completed_jobs():
    """Show completed jobs by vendor"""
    st.markdown("<h1 class='app-title'>✅ Completed Jobs</h1>", unsafe_allow_html=True)
    
    vendor_username = st.session_state.user['username']
    completed_jobs = get_vendor_requests(vendor_username)
    
    # Filter only completed jobs
    completed_jobs = [job for job in completed_jobs if safe_get(job, 'status') in ['Completed', 'Approved']]
    
    if not completed_jobs:
        st.info("📭 No completed jobs yet")
        return
    
    st.markdown(f"<div class='card'><h4>✅ {len(completed_jobs)} Job(s) Completed</h4></div>", unsafe_allow_html=True)
    
    for job in completed_jobs:
        status = safe_get(job, 'status')
        status_icon = '✅' if status == 'Completed' else '👍' if status == 'Approved' else '📋'
        
        with st.expander(f"{status_icon} Job #{safe_get(job, 'id')}: {safe_str(safe_get(job, 'title'))}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Title:** {safe_str(safe_get(job, 'title'))}")
                st.write(f"**Location:** {safe_str(safe_get(job, 'location'), 'Common Area')}")
                st.write(f"**Facility Type:** {safe_str(safe_get(job, 'facility_type'))}")
                st.write(f"**Status:** {status}")
                st.write(f"**Completed Date:** {safe_str(safe_get(job, 'completed_date'))}")
                
                # Show approval status
                if status in ['Completed', 'Approved']:
                    st.write(f"**Department Approval:** {'✅ Approved' if safe_get(job, 'requesting_dept_approval') else '⏳ Pending'}")
                    st.write(f"**Manager Approval:** {'✅ Approved' if safe_get(job, 'facilities_manager_approval') else '⏳ Pending'}")
            
            with col2:
                if safe_get(job, 'job_breakdown'):
                    st.write(f"**Job Breakdown:**")
                    st.info(safe_str(safe_get(job, 'job_breakdown')))
                
                if safe_get(job, 'completion_notes'):
                    st.write(f"**Completion Notes:**")
                    st.info(safe_str(safe_get(job, 'completion_notes')))
                
                if safe_get(job, 'invoice_amount'):
                    st.write(f"**Invoice Amount:** {format_ngn(safe_get(job, 'invoice_amount'))}")
                    st.write(f"**Invoice Number:** {safe_str(safe_get(job, 'invoice_number'), 'N/A')}")

# =============================================
# INVOICE CREATION (FOR VENDORS)
# =============================================
def show_invoice_creation():
    """Invoice creation page for vendors - FIXED to show jobs without invoices"""
    st.markdown("<h1 class='app-title'>🧾 Invoice Creation</h1>", unsafe_allow_html=True)
    
    vendor_username = st.session_state.user['username']
    
    # Get completed jobs without invoices
    completed_jobs = execute_query('''
        SELECT * FROM maintenance_requests 
        WHERE assigned_vendor = ? 
        AND status = 'Completed' 
        AND (invoice_number IS NULL OR invoice_number = '')
        ORDER BY completed_date DESC
    ''', (vendor_username,))
    
    if not completed_jobs:
        st.info("🎉 All your completed jobs already have invoices.")
        return
    
    st.markdown(f"<div class='card'><h4>📋 {len(completed_jobs)} Job(s) Need Invoice</h4></div>", unsafe_allow_html=True)
    
    for job in completed_jobs:
        with st.expander(f"🧾 Create Invoice for Job #{safe_get(job, 'id')}: {safe_str(safe_get(job, 'title'))}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📝 Job Details")
                st.write(f"**Title:** {safe_str(safe_get(job, 'title'))}")
                st.write(f"**Description:** {safe_str(safe_get(job, 'description'))}")
                st.write(f"**Location:** {safe_str(safe_get(job, 'location'), 'Common Area')}")
                st.write(f"**Completed Date:** {safe_str(safe_get(job, 'completed_date'))}")
                
                if safe_get(job, 'job_breakdown'):
                    st.write(f"**Job Breakdown:**")
                    st.info(safe_str(safe_get(job, 'job_breakdown')))
            
            with col2:
                st.markdown("### 🧾 Invoice Details")
                
                with st.form(key=f"invoice_form_{safe_get(job, 'id')}"):
                    details_of_work = st.text_input(
                        "Details of Work *",
                        value=safe_str(safe_get(job, 'job_breakdown'), safe_str(safe_get(job, 'description'))),
                        placeholder="Description of work performed"
                    )
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        quantity = st.number_input("Quantity *", min_value=1, value=1, key=f"qty_{safe_get(job, 'id')}")
                        unit_cost = st.number_input("Unit Cost (₦) *", min_value=0.0, value=1000.0, step=100.0, 
                                                  key=f"unit_{safe_get(job, 'id')}")
                    with col_b:
                        labour_charge = st.number_input("Labour/Service Charge (₦)", min_value=0.0, value=0.0, 
                                                      step=100.0, key=f"labour_{safe_get(job, 'id')}")
                        vat_applicable = st.checkbox("Apply 7.5% VAT", value=True, key=f"vat_{safe_get(job, 'id')}")
                    
                    # Calculate amounts
                    amount = quantity * unit_cost
                    vat_amount = (amount + labour_charge) * 0.075 if vat_applicable else 0.0
                    total_amount = amount + labour_charge + vat_amount
                    
                    # Display summary
                    st.markdown("### 💰 Amount Summary")
                    st.write(f"**Amount:** {format_ngn(amount)}")
                    st.write(f"**Labour Charge:** {format_ngn(labour_charge)}")
                    st.write(f"**VAT ({'7.5%' if vat_applicable else '0%'}):** {format_ngn(vat_amount)}")
                    st.write(f"**Total Amount:** {format_ngn(total_amount)}")
                    
                    submitted = st.form_submit_button("📤 Create Invoice", use_container_width=True)
                    
                    if submitted:
                        if not details_of_work:
                            st.error("❌ Please enter details of work")
                        else:
                            # Generate invoice number
                            invoice_number = f"INV-{safe_get(job, 'id')}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                            
                            # Create invoice
                            invoice_success = execute_update(
                                '''INSERT INTO invoices 
                                (invoice_number, request_id, vendor_username, details_of_work, 
                                 quantity, unit_cost, amount, labour_charge, vat_applicable, 
                                 vat_amount, total_amount) 
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                (invoice_number, safe_get(job, 'id'), vendor_username, details_of_work,
                                 quantity, unit_cost, amount, labour_charge, 1 if vat_applicable else 0,
                                 vat_amount, total_amount)
                            )
                            
                            # Update job with invoice info
                            if invoice_success:
                                job_update_success = execute_update(
                                    '''UPDATE maintenance_requests 
                                    SET invoice_amount = ?, invoice_number = ?
                                    WHERE id = ?''',
                                    (total_amount, invoice_number, safe_get(job, 'id'))
                                )
                                
                                if job_update_success:
                                    st.success(f"✅ Invoice {invoice_number} created successfully!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to update job with invoice info")
                            else:
                                st.error("❌ Failed to create invoice")

# =============================================
# DASHBOARD FUNCTIONS - FIXED UI/UX
# =============================================
def show_user_dashboard():
    st.markdown("<h1 class='dashboard-title'>📊 Dashboard Overview</h1>", unsafe_allow_html=True)
    
    user_requests = get_user_requests(st.session_state.user['username'])
    
    # Stats including approval stats - Cleaner display
    st.markdown("### 📊 Your Request Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_metric_card("Total", len(user_requests), "📋")
    
    with col2:
        pending_approval = len([r for r in user_requests if safe_get(r, 'status') == 'Completed' and not safe_get(r, 'requesting_dept_approval')])
        create_metric_card("Awaiting Approval", pending_approval, "✅")
    
    with col3:
        approved_jobs = len([r for r in user_requests if safe_get(r, 'status') == 'Approved'])
        create_metric_card("Fully Approved", approved_jobs, "👍")
    
    with col4:
        pending_jobs = len([r for r in user_requests if safe_get(r, 'status') == 'Pending'])
        create_metric_card("Pending", pending_jobs, "⏳")
    
    st.markdown("---")
    
    # Quick actions - Cleaner layout
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Create New Request", use_container_width=True, key="create_new_dash"):
            st.session_state.page = "create_request"
            st.rerun()
    
    with col2:
        pending_approvals = get_requests_for_user_approval(st.session_state.user['username'])
        if pending_approvals:
            if st.button(f"✅ Approve Jobs ({len(pending_approvals)})", use_container_width=True, type="primary", key="approve_jobs_dash"):
                st.session_state.page = "department_approval"
                st.rerun()
    
    with col3:
        if st.button("📋 View My Requests", use_container_width=True, key="view_requests_dash"):
            st.session_state.page = "my_requests"
            st.rerun()

def show_manager_dashboard():
    st.markdown("<h1 class='dashboard-title'>📊 Dashboard Overview</h1>", unsafe_allow_html=True)
    
    all_requests = get_all_requests()
    
    # Stats including approval stats
    st.markdown("### 📊 System Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_metric_card("Total Requests", len(all_requests), "📊")
    
    with col2:
        pending_final = len(get_requests_for_manager_approval())
        create_metric_card("Awaiting Final Approval", pending_final, "✅")
    
    with col3:
        assigned_count = len([r for r in all_requests if safe_get(r, 'status') == 'Assigned'])
        create_metric_card("Assigned", assigned_count, "👷")
    
    with col4:
        approved_count = len([r for r in all_requests if safe_get(r, 'status') == 'Approved'])
        create_metric_card("Fully Approved", approved_count, "👍")
    
    st.markdown("---")
    
    # User management stats
    st.markdown("### 👥 User Management")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        pending_users = len(get_pending_users())
        create_metric_card("Pending Users", pending_users, "👤")
    
    with col2:
        pending_vendors = len(get_pending_vendors())
        create_metric_card("Pending Vendors", pending_vendors, "🏢")
    
    with col3:
        approved_users = len(execute_query("SELECT * FROM users WHERE status = 'approved'"))
        create_metric_card("Approved Users", approved_users, "✅")
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🛠️ Manage Requests", use_container_width=True, key="manage_req_dash"):
            st.session_state.page = "manage_requests"
            st.rerun()
    
    with col2:
        pending_final_approvals = get_requests_for_manager_approval()
        if pending_final_approvals:
            if st.button(f"✅ Final Approval ({len(pending_final_approvals)})", use_container_width=True, type="primary", key="final_approve_dash"):
                st.session_state.page = "final_approval"
                st.rerun()
    
    with col3:
        if st.button("👥 Manage Users", use_container_width=True, key="manage_users_dash"):
            st.session_state.page = "manage_users"
            st.rerun()

def show_vendor_dashboard():
    st.markdown("<h1 class='dashboard-title'>📊 Dashboard Overview</h1>", unsafe_allow_html=True)
    
    vendor_requests = get_vendor_requests(st.session_state.user['username'])
    
    st.markdown("### 📊 Your Job Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        assigned_count = len([r for r in vendor_requests if safe_get(r, 'status') == 'Assigned'])
        create_metric_card("Assigned Jobs", assigned_count, "🔧")
    
    with col2:
        completed_count = len([r for r in vendor_requests if safe_get(r, 'status') == 'Completed'])
        create_metric_card("Completed", completed_count, "✅")
    
    with col3:
        approved_count = len([r for r in vendor_requests if safe_get(r, 'status') == 'Approved'])
        create_metric_card("Approved", approved_count, "👍")
    
    with col4:
        # Calculate total revenue from completed jobs
        total_revenue = sum([safe_float(r['invoice_amount']) for r in vendor_requests if r['invoice_amount']])
        create_metric_card("Total Revenue", format_ngn(total_revenue), "💰")
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        assigned_jobs = len([r for r in vendor_requests if safe_get(r, 'status') == 'Assigned'])
        if assigned_jobs > 0:
            if st.button(f"🔧 Work on Jobs ({assigned_jobs})", use_container_width=True, key="work_jobs_dash"):
                st.session_state.page = "assigned_jobs"
                st.rerun()
        else:
            st.info("📭 No assigned jobs")
    
    with col2:
        completed_jobs = len([r for r in vendor_requests if safe_get(r, 'status') in ['Completed', 'Approved']])
        if completed_jobs > 0:
            if st.button(f"✅ View Completed ({completed_jobs})", use_container_width=True, key="view_completed_dash"):
                st.session_state.page = "completed_jobs"
                st.rerun()
    
    with col3:
        # Check if there are jobs needing invoices
        jobs_needing_invoices = execute_query('''
            SELECT COUNT(*) as count FROM maintenance_requests 
            WHERE assigned_vendor = ? 
            AND status = 'Completed' 
            AND (invoice_number IS NULL OR invoice_number = '')
        ''', (st.session_state.user['username'],))
        
        invoice_count = jobs_needing_invoices[0]['count'] if jobs_needing_invoices else 0
        if invoice_count > 0:
            if st.button(f"🧾 Create Invoices ({invoice_count})", use_container_width=True, type="primary", key="create_invoice_dash"):
                st.session_state.page = "invoice_creation"
                st.rerun()

# =============================================
# ENHANCED SIDEBAR NAVIGATION
# =============================================
def show_sidebar_navigation():
    """Show sidebar navigation based on user role"""
    with st.sidebar:
        st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
        st.markdown("<h3>🏢 Facilities Pro</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #6b7280; font-size: 0.8rem;'>Professional Management Solution</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # User info
        if 'user' in st.session_state:
            user = st.session_state.user
            role_display = user['role'].replace('_', ' ').title()
            st.markdown(f"**👤 Welcome, {user['full_name']}**")
            st.markdown(f"<small style='color: #6b7280;'>{role_display}</small>", unsafe_allow_html=True)
            st.markdown("---")
        
        # Navigation based on role
        if 'user' in st.session_state:
            user_role = st.session_state.user['role']
            
            if user_role == 'facility_manager':
                # Manager Navigation
                st.markdown("### 📊 Dashboard")
                if st.sidebar.button("📊 Dashboard", key="manager_dash", use_container_width=True):
                    st.session_state.page = "dashboard"
                    st.rerun()
                
                st.markdown("### 🛠️ Request Management")
                if st.sidebar.button("🛠️ Manage Requests", key="manage_req", use_container_width=True):
                    st.session_state.page = "manage_requests"
                    st.rerun()
                
                if st.sidebar.button("✅ Final Approval", key="final_approval", use_container_width=True):
                    st.session_state.page = "final_approval"
                    st.rerun()
                
                st.markdown("### 👥 User Management")
                if st.sidebar.button("👥 Manage Users", key="manage_users", use_container_width=True):
                    st.session_state.page = "manage_users"
                    st.rerun()
            
            elif user_role == 'facility_user':
                # Facility User Navigation
                st.markdown("### 📊 Dashboard")
                if st.sidebar.button("📊 Dashboard", key="user_dash", use_container_width=True):
                    st.session_state.page = "dashboard"
                    st.rerun()
                
                st.markdown("### 📝 Requests")
                if st.sidebar.button("📝 Create Request", key="create_req", use_container_width=True):
                    st.session_state.page = "create_request"
                    st.rerun()
                
                if st.sidebar.button("📋 My Requests", key="my_req", use_container_width=True):
                    st.session_state.page = "my_requests"
                    st.rerun()
                
                if st.sidebar.button("✅ Department Approval", key="dept_approval", use_container_width=True):
                    st.session_state.page = "department_approval"
                    st.rerun()
            
            elif user_role == 'vendor':
                # Vendor Navigation
                st.markdown("### 📊 Dashboard")
                if st.sidebar.button("📊 Dashboard", key="vendor_dash", use_container_width=True):
                    st.session_state.page = "dashboard"
                    st.rerun()
                
                st.markdown("### 🔧 Job Management")
                if st.sidebar.button("🔧 Assigned Jobs", key="assigned_jobs", use_container_width=True):
                    st.session_state.page = "assigned_jobs"
                    st.rerun()
                
                if st.sidebar.button("✅ Completed Jobs", key="completed_jobs", use_container_width=True):
                    st.session_state.page = "completed_jobs"
                    st.rerun()
                
                if st.sidebar.button("🧾 Create Invoice", key="create_invoice", use_container_width=True):
                    st.session_state.page = "invoice_creation"
                    st.rerun()
        
        st.markdown("---")
        
        # Logout button
        if st.sidebar.button("🚪 Logout", use_container_width=True, type="secondary"):
            if 'user' in st.session_state:
                del st.session_state.user
            if 'page' in st.session_state:
                del st.session_state.page
            st.rerun()
        
        st.markdown("---")
        st.markdown("<div style='text-align: center; color: #6b7280; font-size: 0.7rem;'>© 2025 A-Z Facilities Management Pro APP™<br>Developed by Abdulahi Ibrahim</div>", unsafe_allow_html=True)

# =============================================
# MAIN APPLICATION ROUTING
# =============================================
def main():
    # Initialize session state
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'page' not in st.session_state:
        st.session_state.page = None
    
    # Show login page if not authenticated
    if not st.session_state.user:
        show_enhanced_login()
        return
    
    # Show sidebar navigation
    show_sidebar_navigation()
    
    # Page routing based on session state
    if st.session_state.page == "dashboard":
        if st.session_state.user['role'] == 'facility_manager':
            show_manager_dashboard()
        elif st.session_state.user['role'] == 'facility_user':
            show_user_dashboard()
        elif st.session_state.user['role'] == 'vendor':
            show_vendor_dashboard()
    
    elif st.session_state.page == "create_request":
        show_create_request()
    
    elif st.session_state.page == "my_requests":
        show_my_requests()
    
    elif st.session_state.page == "manage_requests":
        show_manage_requests()
    
    elif st.session_state.page == "assigned_jobs":
        show_assigned_jobs()
    
    elif st.session_state.page == "completed_jobs":
        show_completed_jobs()
    
    elif st.session_state.page == "invoice_creation":
        show_invoice_creation()
    
    elif st.session_state.page == "manage_users":
        show_manage_users()
    
    elif st.session_state.page == "department_approval":
        show_department_approval()
    
    elif st.session_state.page == "final_approval":
        show_final_approval()
    
    else:
        # Default to dashboard
        if st.session_state.user['role'] == 'facility_manager':
            show_manager_dashboard()
        elif st.session_state.user['role'] == 'facility_user':
            show_user_dashboard()
        elif st.session_state.user['role'] == 'vendor':
            show_vendor_dashboard()

# =============================================
# RUN THE APPLICATION
# =============================================
if __name__ == "__main__":
    main()
