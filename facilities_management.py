import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
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
import calendar

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
    
    /* Status colors for PPM */
    .status-due { background-color: #fee2e2; color: #dc2626; }
    .status-not-due { background-color: #d1fae5; color: #059669; }
    .status-prepare { background-color: #fef3c7; color: #d97706; }
    .status-wip { background-color: #dbeafe; color: #2563eb; }
    .status-completed { background-color: #dcfce7; color: #16a34a; }
    
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
    
    /* Workflow steps */
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
    
    /* Generator status indicator */
    .generator-status {
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 0.8rem;
    }
    
    .generator-normal { background-color: #d1fae5; color: #065f46; }
    .generator-warning { background-color: #fef3c7; color: #92400e; }
    .generator-maintenance { background-color: #fee2e2; color: #991b1b; }
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
# DATABASE SETUP - ENHANCED WITH NEW TABLES
# =============================================
def init_database():
    try:
        conn = sqlite3.connect('facilities_management.db', check_same_thread=False)
        cursor = conn.cursor()
        
        # Existing tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                vendor_type TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
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
                username TEXT NOT NULL,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
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
        
        # NEW TABLES FOR ADDED REQUIREMENTS
        
        # Planned Preventive Maintenance (PPM) Schedules
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ppm_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_name TEXT NOT NULL,
                facility_category TEXT NOT NULL,
                sub_category TEXT NOT NULL,
                frequency TEXT NOT NULL,
                next_maintenance_date DATE NOT NULL,
                status TEXT DEFAULT 'Not Due',
                assigned_vendor TEXT,
                created_by TEXT NOT NULL,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT,
                notes TEXT,
                estimated_duration_hours INTEGER,
                estimated_cost REAL,
                actual_completion_date DATE,
                actual_cost REAL
            )
        ''')
        
        # Generator Daily Records
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS generator_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_date DATE NOT NULL,
                generator_type TEXT NOT NULL,
                opening_hours REAL NOT NULL,
                closing_hours REAL NOT NULL,
                net_hours REAL GENERATED ALWAYS AS (closing_hours - opening_hours) STORED,
                opening_inventory_liters REAL NOT NULL,
                purchase_liters REAL DEFAULT 0,
                closing_inventory_liters REAL NOT NULL,
                net_diesel_consumed REAL GENERATED ALWAYS AS (opening_inventory_liters + purchase_liters - closing_inventory_liters) STORED,
                recorded_by TEXT NOT NULL,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        ''')
        
        # HSE Management
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hse_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_type TEXT NOT NULL,
                description TEXT NOT NULL,
                frequency TEXT NOT NULL,
                next_due_date DATE NOT NULL,
                status TEXT DEFAULT 'Not Due',
                responsible_person TEXT,
                created_by TEXT NOT NULL,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hse_incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_date DATE NOT NULL,
                incident_type TEXT NOT NULL,
                description TEXT NOT NULL,
                location TEXT NOT NULL,
                severity TEXT NOT NULL,
                reported_by TEXT NOT NULL,
                status TEXT DEFAULT 'Open',
                action_taken TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hse_inspections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inspection_date DATE NOT NULL,
                inspection_type TEXT NOT NULL,
                inspector_name TEXT NOT NULL,
                area_inspected TEXT NOT NULL,
                findings TEXT,
                recommendations TEXT,
                status TEXT DEFAULT 'Completed',
                created_by TEXT NOT NULL,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Space Management - Room Booking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS room_bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_name TEXT NOT NULL,
                room_type TEXT NOT NULL,
                booking_date DATE NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                booked_by TEXT NOT NULL,
                purpose TEXT NOT NULL,
                attendees_count INTEGER,
                status TEXT DEFAULT 'Confirmed',
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        ''')
        
        # PPM Assignments to Vendors
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ppm_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_id INTEGER NOT NULL,
                vendor_username TEXT NOT NULL,
                assigned_date DATE NOT NULL,
                due_date DATE NOT NULL,
                status TEXT DEFAULT 'Assigned',
                assigned_by TEXT NOT NULL,
                completed_date DATE,
                completion_notes TEXT,
                invoice_number TEXT,
                FOREIGN KEY (schedule_id) REFERENCES ppm_schedules(id)
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
                ('hse_vendor', '0123456', 'vendor', 'HSE'),
                ('space_vendor', '0123456', 'vendor', 'Space Management'),
                ('plumbing_vendor', '0123456', 'vendor', 'Plumbing'),
                ('electrical_vendor', '0123456', 'vendor', 'Electrical'),
                ('cleaning_vendor', '0123456', 'vendor', 'Cleaning')
            ]
            
            for username, password, role, vendor_type in sample_users:
                try:
                    cursor.execute(
                        'INSERT INTO users (username, password_hash, role, vendor_type) VALUES (?, ?, ?, ?)',
                        (username, password, role, vendor_type)
                    )
                except:
                    pass
        
        # Insert sample vendors if table is empty
        cursor.execute('SELECT COUNT(*) FROM vendors')
        vendor_count = cursor.fetchone()[0]
        
        if vendor_count == 0:
            sample_vendors = [
                ('hvac_vendor', 'HVAC Solutions Inc.', 'John HVAC', 'hvac@example.com', '123-456-7890', 'HVAC', 
                 'HVAC installation, maintenance and repair services', 500000.00, 'TIN123456', 'RC789012',
                 'John Smith (CEO), Jane Doe (Operations Manager)', 'Bank: ABC Bank, Acc: 123456789', 
                 'HVAC Certified', '123 HVAC Street, City, State'),
                ('generator_vendor', 'Generator Pros Ltd.', 'Mike Generator', 'generator@example.com', '123-456-7891', 'Generator',
                 'Generator installation and maintenance', 300000.00, 'TIN123457', 'RC789013',
                 'Mike Johnson (Director)', 'Bank: XYZ Bank, Acc: 987654321', 
                 'Generator Specialist', '456 Power Ave, City, State'),
                ('fixture_vendor', 'Fixture Masters Co.', 'Sarah Fixtures', 'fixtures@example.com', '123-456-7892', 'Fixture and Fittings',
                 'Fixture installation and repairs', 250000.00, 'TIN123458', 'RC789014',
                 'Sarah Wilson (Owner)', 'Bank: DEF Bank, Acc: 456123789', 
                 'Fixture Expert', '789 Fixture Road, City, State'),
                ('building_vendor', 'Building Care Services', 'David Builder', 'building@example.com', '123-456-7893', 'Building Maintenance',
                 'General building maintenance and repairs', 400000.00, 'TIN123459', 'RC789015',
                 'David Brown (Manager)', 'Bank: GHI Bank, Acc: 789456123', 
                 'Building Maintenance Certified', '321 Builders Lane, City, State')
            ]
            
            for vendor_data in sample_vendors:
                try:
                    cursor.execute('''
                        INSERT INTO vendors 
                        (username, company_name, contact_person, email, phone, vendor_type, services_offered, 
                         annual_turnover, tax_identification_number, rc_number, key_management_staff, 
                         account_details, certification, address) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', vendor_data)
                except:
                    pass
        
        conn.commit()
        conn.close()
        print("Database initialized successfully with new tables")
        
    except Exception as e:
        print(f"Database initialization error: {e}")

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

def safe_bool(value, default=False):
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
    return execute_query('''
        SELECT * FROM maintenance_requests 
        WHERE created_by = ? 
        AND status = 'Completed' 
        AND requesting_dept_approval = 0
        ORDER BY completed_date DESC
    ''', (username,))

def get_requests_for_manager_approval():
    return execute_query('''
        SELECT * FROM maintenance_requests 
        WHERE status = 'Completed' 
        AND requesting_dept_approval = 1
        AND facilities_manager_approval = 0
        ORDER BY department_approval_date DESC
    ''')

def create_metric_card(title, value, icon="📊"):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon">{icon}</div>
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def show_workflow_status(request):
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

# =============================================
# NEW FUNCTIONS FOR ADDED REQUIREMENTS
# =============================================

# =============================================
# PLANNED PREVENTIVE MAINTENANCE (PPM) - FACILITY USER
# =============================================
def show_ppm_facility_user():
    st.markdown("<h1 class='app-title'>🔧 Planned Preventive Maintenance</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📅 Add New Schedule", "📋 Schedule Overview", "📊 Reports & Analytics"])
    
    with tab1:
        show_add_ppm_schedule()
    
    with tab2:
        show_ppm_schedule_overview()
    
    with tab3:
        show_ppm_analytics()

def show_add_ppm_schedule():
    st.markdown("### 📅 Add New Preventive Maintenance Schedule")
    
    with st.form("add_ppm_schedule_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            schedule_name = st.text_input("Schedule Name *", placeholder="e.g., Monthly Generator Check")
            facility_category = st.selectbox(
                "Facility Category *",
                ["HVAC", "Generator Maintenance", "Fixture and Fittings", "Building Maintenance"]
            )
            
            # Dynamic sub-categories based on category
            sub_categories = {
                "HVAC": ["Airconditioners"],
                "Generator Maintenance": ["Generator 150kva", "Generator 250kva"],
                "Fixture and Fittings": ["Printers", "Copiers", "Office Chairs"],
                "Building Maintenance": [
                    "Painting of Building", "Water Treatment Plant", "Plumbing Maintenance",
                    "Electrical Maintenance", "Access Control Doors", "Fire Extinguishers",
                    "CCTV Cameras", "Fumigation", "Daily Cleaning of Offices",
                    "Horticulture Maintenance", "Fountain Maintenance"
                ]
            }
            
            sub_category = st.selectbox(
                "Sub-Category *",
                sub_categories.get(facility_category, [])
            )
        
        with col2:
            frequency = st.selectbox(
                "Frequency *",
                ["Daily", "Weekly", "Monthly", "Every 200 hours", "Quarterly", "Bi-annual", "Annual"]
            )
            
            next_maintenance_date = st.date_input("Next Maintenance Date *")
            
            status = st.selectbox(
                "Status *",
                ["Due", "Not Due", "Prepare for Maintenance", "Work In Progress", "Completed"]
            )
        
        description = st.text_area("Description", placeholder="Enter schedule description...")
        estimated_duration = st.number_input("Estimated Duration (hours)", min_value=1, value=2)
        estimated_cost = st.number_input("Estimated Cost (₦)", min_value=0.0, value=0.0, step=1000.0)
        
        submitted = st.form_submit_button("➕ Add Schedule", use_container_width=True)
        
        if submitted:
            if not all([schedule_name, facility_category, sub_category, frequency]):
                st.error("❌ Please fill in all required fields (*)")
            else:
                success = execute_update(
                    '''INSERT INTO ppm_schedules 
                    (schedule_name, facility_category, sub_category, frequency, 
                     next_maintenance_date, status, created_by, description,
                     estimated_duration_hours, estimated_cost) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (schedule_name, facility_category, sub_category, frequency,
                     next_maintenance_date.strftime('%Y-%m-%d'), status, 
                     st.session_state.user['username'], description,
                     estimated_duration, estimated_cost)
                )
                if success:
                    st.success("✅ Preventive maintenance schedule added successfully!")
                else:
                    st.error("❌ Failed to add schedule")

def show_ppm_schedule_overview():
    st.markdown("### 📋 Preventive Maintenance Schedules Overview")
    
    # Get all PPM schedules
    schedules = execute_query('SELECT * FROM ppm_schedules ORDER BY next_maintenance_date')
    
    if not schedules:
        st.info("📭 No preventive maintenance schedules found")
        return
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        category_filter = st.selectbox(
            "Filter by Category",
            ["All"] + list(set([s['facility_category'] for s in schedules]))
        )
    with col2:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Due", "Not Due", "Prepare for Maintenance", "Work In Progress", "Completed"]
        )
    with col3:
        search_term = st.text_input("Search by name", "")
    
    # Apply filters
    filtered_schedules = schedules
    
    if category_filter != "All":
        filtered_schedules = [s for s in filtered_schedules if s['facility_category'] == category_filter]
    
    if status_filter != "All":
        filtered_schedules = [s for s in filtered_schedules if s['status'] == status_filter]
    
    if search_term:
        filtered_schedules = [s for s in filtered_schedules if search_term.lower() in s['schedule_name'].lower()]
    
    st.markdown(f"<div class='card'><h4>📋 {len(filtered_schedules)} Schedule(s) Found</h4></div>", unsafe_allow_html=True)
    
    # Display schedules
    for schedule in filtered_schedules:
        status = schedule['status']
        status_color = {
            "Due": "status-due",
            "Not Due": "status-not-due",
            "Prepare for Maintenance": "status-prepare",
            "Work In Progress": "status-wip",
            "Completed": "status-completed"
        }.get(status, "")
        
        with st.expander(f"{schedule['schedule_name']} - <span class='{status_color}'>{status}</span>", unsafe_allow_html=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Category:** {schedule['facility_category']}")
                st.write(f"**Sub-Category:** {schedule['sub_category']}")
                st.write(f"**Frequency:** {schedule['frequency']}")
                st.write(f"**Next Maintenance:** {schedule['next_maintenance_date']}")
                st.write(f"**Created By:** {schedule['created_by']}")
            
            with col2:
                st.write(f"**Estimated Duration:** {schedule['estimated_duration_hours']} hours")
                st.write(f"**Estimated Cost:** {format_ngn(schedule['estimated_cost'])}")
                if schedule['assigned_vendor']:
                    vendor_info = execute_query(
                        'SELECT company_name FROM vendors WHERE username = ?',
                        (schedule['assigned_vendor'],)
                    )
                    vendor_name = vendor_info[0]['company_name'] if vendor_info else schedule['assigned_vendor']
                    st.write(f"**Assigned Vendor:** {vendor_name}")
                if schedule['actual_completion_date']:
                    st.write(f"**Completed On:** {schedule['actual_completion_date']}")
                    st.write(f"**Actual Cost:** {format_ngn(schedule['actual_cost'])}")
            
            if schedule['description']:
                st.write(f"**Description:** {schedule['description']}")
            
            if schedule['notes']:
                st.write(f"**Notes:**")
                st.info(schedule['notes'])
            
            # Action buttons for facility user
            if st.session_state.user['role'] == 'facility_user':
                if schedule['status'] in ['Completed', 'Work In Progress']:
                    st.markdown("---")
                    st.markdown("### ✅ Approval Action")
                    
                    if schedule['status'] == 'Completed' and schedule['assigned_vendor']:
                        if st.button(f"Approve Work Completion", key=f"approve_ppm_{schedule['id']}", use_container_width=True):
                            # Update approval status
                            if execute_update(
                                "UPDATE ppm_schedules SET status = 'Approved' WHERE id = ?",
                                (schedule['id'],)
                            ):
                                st.success("✅ Work approved successfully!")
                                st.rerun()

def show_ppm_analytics():
    st.markdown("### 📊 Preventive Maintenance Analytics")
    
    # Get all PPM data
    schedules = execute_query('SELECT * FROM ppm_schedules')
    
    if not schedules:
        st.info("📭 No data available for analytics")
        return
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(schedules)
    
    # Overall statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_metric_card("Total Schedules", len(df), "📋")
    
    with col2:
        due_count = len(df[df['status'] == 'Due'])
        create_metric_card("Due Now", due_count, "⚠️")
    
    with col3:
        completed_count = len(df[df['status'] == 'Completed'])
        create_metric_card("Completed", completed_count, "✅")
    
    with col4:
        total_estimated_cost = df['estimated_cost'].sum()
        create_metric_card("Estimated Cost", format_ngn(total_estimated_cost), "💰")
    
    st.markdown("---")
    
    # Status distribution chart
    st.markdown("### 📈 Status Distribution")
    status_counts = df['status'].value_counts()
    
    if not status_counts.empty:
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Maintenance Status Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Category analysis
    st.markdown("### 🏗️ Category Analysis")
    category_counts = df['facility_category'].value_counts()
    
    if not category_counts.empty:
        fig2 = px.bar(
            x=category_counts.index,
            y=category_counts.values,
            title="Maintenance by Category",
            labels={'x': 'Category', 'y': 'Count'}
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Upcoming maintenance
    st.markdown("### 📅 Upcoming Maintenance (Next 30 Days)")
    upcoming = df[df['status'] != 'Completed'].copy()
    upcoming['days_until'] = pd.to_datetime(upcoming['next_maintenance_date']) - pd.Timestamp.now()
    upcoming = upcoming[upcoming['days_until'].dt.days <= 30]
    
    if not upcoming.empty:
        st.dataframe(
            upcoming[['schedule_name', 'facility_category', 'next_maintenance_date', 'status']],
            use_container_width=True
        )
    else:
        st.info("🎉 No upcoming maintenance in the next 30 days")

# =============================================
# GENERATOR RECORDS - FACILITY USER
# =============================================
def show_generator_records_facility_user():
    st.markdown("<h1 class='app-title'>⚡ Generator Records</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📝 Daily Records", "📋 Report Overview", "📊 Reports & Analytics"])
    
    with tab1:
        show_generator_daily_records()
    
    with tab2:
        show_generator_report_overview()
    
    with tab3:
        show_generator_analytics()

def show_generator_daily_records():
    st.markdown("### 📝 Daily Generator Records")
    
    with st.form("generator_daily_record_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            record_date = st.date_input("Record Date *", value=datetime.now())
            generator_type = st.selectbox(
                "Generator Type *",
                ["150kva Generator set", "250kva Generator set"]
            )
            opening_hours = st.number_input("Opening Hours *", min_value=0.0, max_value=24.0, value=0.0, step=0.5)
            closing_hours = st.number_input("Closing Hours *", min_value=opening_hours, max_value=24.0, value=8.0, step=0.5)
        
        with col2:
            opening_inventory = st.number_input("Opening Inventory of Diesel (liters) *", min_value=0.0, value=500.0, step=10.0)
            purchase_liters = st.number_input("Purchase (liters)", min_value=0.0, value=0.0, step=10.0)
            closing_inventory = st.number_input("Closing Inventory of Diesel (liters) *", min_value=0.0, value=450.0, step=10.0)
        
        notes = st.text_area("Notes", placeholder="Any additional notes...")
        
        submitted = st.form_submit_button("💾 Save Daily Record", use_container_width=True)
        
        if submitted:
            if closing_hours <= opening_hours:
                st.error("❌ Closing hours must be greater than opening hours")
            elif closing_inventory > (opening_inventory + purchase_liters):
                st.error("❌ Closing inventory cannot be greater than opening inventory + purchase")
            else:
                # Calculate net hours and diesel consumed (these are generated columns in DB)
                net_hours = closing_hours - opening_hours
                net_diesel = opening_inventory + purchase_liters - closing_inventory
                
                # Check if record already exists for this date and generator
                existing = execute_query(
                    'SELECT * FROM generator_records WHERE record_date = ? AND generator_type = ?',
                    (record_date.strftime('%Y-%m-%d'), generator_type)
                )
                
                if existing:
                    st.warning("⚠️ Record already exists for this date and generator. Updating existing record.")
                    success = execute_update(
                        '''UPDATE generator_records 
                        SET opening_hours = ?, closing_hours = ?,
                            opening_inventory_liters = ?, purchase_liters = ?,
                            closing_inventory_liters = ?, notes = ?
                        WHERE record_date = ? AND generator_type = ?''',
                        (opening_hours, closing_hours, opening_inventory, purchase_liters,
                         closing_inventory, notes, record_date.strftime('%Y-%m-%d'), generator_type)
                    )
                else:
                    success = execute_update(
                        '''INSERT INTO generator_records 
                        (record_date, generator_type, opening_hours, closing_hours,
                         opening_inventory_liters, purchase_liters, closing_inventory_liters,
                         recorded_by, notes) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (record_date.strftime('%Y-%m-%d'), generator_type, opening_hours, closing_hours,
                         opening_inventory, purchase_liters, closing_inventory,
                         st.session_state.user['username'], notes)
                    )
                
                if success:
                    # Check if generator needs maintenance (150 hours threshold)
                    if net_hours > 0:
                        # Get total hours for this generator
                        total_hours_result = execute_query(
                            '''SELECT SUM(net_hours) as total_hours 
                            FROM generator_records 
                            WHERE generator_type = ?''',
                            (generator_type,)
                        )
                        
                        total_hours = total_hours_result[0]['total_hours'] if total_hours_result else 0
                        
                        if total_hours >= 150:
                            # Find PPM schedule for this generator
                            generator_schedule_name = f"{generator_type} Maintenance"
                            ppm_schedules = execute_query(
                                '''SELECT * FROM ppm_schedules 
                                WHERE schedule_name LIKE ? AND status NOT IN ('Completed', 'Approved')''',
                                (f'%{generator_type}%',)
                            )
                            
                            if ppm_schedules:
                                for schedule in ppm_schedules:
                                    execute_update(
                                        '''UPDATE ppm_schedules 
                                        SET status = 'Prepare for Maintenance',
                                            notes = CONCAT(COALESCE(notes, ''), '\nGenerator reached ', ?, ' hours on ', ?)
                                        WHERE id = ?''',
                                        (total_hours, datetime.now().strftime('%Y-%m-%d'), schedule['id'])
                                    )
                                st.info(f"⚠️ {generator_type} has reached {total_hours:.1f} hours. Maintenance schedule updated to 'Prepare for Maintenance'")
                            else:
                                # Create new maintenance schedule
                                execute_update(
                                    '''INSERT INTO ppm_schedules 
                                    (schedule_name, facility_category, sub_category, frequency,
                                     next_maintenance_date, status, created_by, description)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                                    (generator_schedule_name, 'Generator Maintenance', generator_type,
                                     'Every 200 hours', datetime.now().strftime('%Y-%m-%d'),
                                     'Prepare for Maintenance', st.session_state.user['username'],
                                     f'Generator has reached {total_hours:.1f} hours. Requires maintenance.')
                                )
                                st.info(f"⚠️ {generator_type} has reached {total_hours:.1f} hours. New maintenance schedule created.")
                    
                    st.success("✅ Daily generator record saved successfully!")
                else:
                    st.error("❌ Failed to save record")

def show_generator_report_overview():
    st.markdown("### 📋 Generator Records Overview")
    
    # Get all generator records
    records = execute_query('''
        SELECT * FROM generator_records 
        ORDER BY record_date DESC, generator_type
    ''')
    
    if not records:
        st.info("📭 No generator records found")
        return
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        generator_filter = st.selectbox(
            "Filter by Generator Type",
            ["All"] + list(set([r['generator_type'] for r in records]))
        )
    with col2:
        date_range = st.date_input(
            "Date Range",
            [datetime.now() - timedelta(days=30), datetime.now()]
        )
    
    # Apply filters
    filtered_records = records
    
    if generator_filter != "All":
        filtered_records = [r for r in filtered_records if r['generator_type'] == generator_filter]
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_records = [
            r for r in filtered_records 
            if start_date <= datetime.strptime(r['record_date'], '%Y-%m-%d').date() <= end_date
        ]
    
    st.markdown(f"<div class='card'><h4>📋 {len(filtered_records)} Record(s) Found</h4></div>", unsafe_allow_html=True)
    
    # Display as dataframe
    df = pd.DataFrame(filtered_records)
    
    # Calculate totals
    if not df.empty:
        total_hours = df['net_hours'].sum()
        total_diesel = df['net_diesel_consumed'].sum()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Generator Hours", f"{total_hours:.1f}")
        with col2:
            st.metric("Total Diesel Consumed", f"{total_diesel:.1f} liters")
        
        st.markdown("---")
    
    st.dataframe(
        df[['record_date', 'generator_type', 'opening_hours', 'closing_hours', 
            'net_hours', 'opening_inventory_liters', 'purchase_liters',
            'closing_inventory_liters', 'net_diesel_consumed', 'recorded_by']],
        use_container_width=True
    )
    
    # Export option
    if st.button("📤 Export to CSV", use_container_width=True):
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"generator_records_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

def show_generator_analytics():
    st.markdown("### 📊 Generator Analytics")
    
    # Get all generator records
    records = execute_query('SELECT * FROM generator_records')
    
    if not records:
        st.info("📭 No data available for analytics")
        return
    
    df = pd.DataFrame(records)
    df['record_date'] = pd.to_datetime(df['record_date'])
    
    # Overall statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_hours = df['net_hours'].sum()
        create_metric_card("Total Hours", f"{total_hours:.1f}", "⏱️")
    
    with col2:
        total_diesel = df['net_diesel_consumed'].sum()
        create_metric_card("Total Diesel", f"{total_diesel:.1f}L", "⛽")
    
    with col3:
        avg_hours_per_day = df.groupby('record_date')['net_hours'].sum().mean()
        create_metric_card("Avg Daily Hours", f"{avg_hours_per_day:.1f}", "📅")
    
    with col4:
        diesel_per_hour = total_diesel / total_hours if total_hours > 0 else 0
        create_metric_card("Diesel/Hour", f"{diesel_per_hour:.2f}L", "📊")
    
    st.markdown("---")
    
    # Generator comparison
    st.markdown("### ⚡ Generator Performance Comparison")
    
    if 'generator_type' in df.columns:
        generator_stats = df.groupby('generator_type').agg({
            'net_hours': 'sum',
            'net_diesel_consumed': 'sum'
        }).reset_index()
        
        generator_stats['efficiency'] = generator_stats['net_diesel_consumed'] / generator_stats['net_hours']
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = px.bar(
                generator_stats,
                x='generator_type',
                y='net_hours',
                title="Total Hours by Generator",
                labels={'net_hours': 'Total Hours', 'generator_type': 'Generator Type'}
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = px.bar(
                generator_stats,
                x='generator_type',
                y='efficiency',
                title="Diesel Efficiency (Liters per Hour)",
                labels={'efficiency': 'Liters per Hour', 'generator_type': 'Generator Type'}
            )
            st.plotly_chart(fig2, use_container_width=True)
    
    # Time series analysis
    st.markdown("### 📈 Daily Consumption Trend")
    
    daily_stats = df.groupby('record_date').agg({
        'net_hours': 'sum',
        'net_diesel_consumed': 'sum'
    }).reset_index()
    
    fig3 = px.line(
        daily_stats,
        x='record_date',
        y=['net_hours', 'net_diesel_consumed'],
        title="Daily Generator Usage",
        labels={'value': 'Amount', 'record_date': 'Date', 'variable': 'Metric'},
        height=400
    )
    st.plotly_chart(fig3, use_container_width=True)

# =============================================
# HSE MANAGEMENT - FACILITY USER
# =============================================
def show_hse_management_facility_user():
    st.markdown("<h1 class='app-title'>🛡️ HSE Management</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📅 HSE Schedule", "⚠️ Incident Reports", "🔍 New Inspection"])
    
    with tab1:
        show_hse_schedule()
    
    with tab2:
        show_incident_reports()
    
    with tab3:
        show_new_inspection()

def show_hse_schedule():
    st.markdown("### 📅 HSE Schedule Management")
    
    with st.form("hse_schedule_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            schedule_type = st.selectbox(
                "Schedule Type *",
                ["Safety Audit", "Fire Drill", "First Aid Training", "Equipment Inspection", 
                 "Environmental Check", "Health Screening", "Emergency Response Drill"]
            )
            frequency = st.selectbox(
                "Frequency *",
                ["Daily", "Weekly", "Monthly", "Quarterly", "Bi-annual", "Annual"]
            )
        
        with col2:
            next_due_date = st.date_input("Next Due Date *")
            responsible_person = st.text_input("Responsible Person")
        
        description = st.text_area("Description *", placeholder="Describe the HSE activity...")
        
        submitted = st.form_submit_button("➕ Add HSE Schedule", use_container_width=True)
        
        if submitted:
            if not all([schedule_type, frequency, description]):
                st.error("❌ Please fill in all required fields (*)")
            else:
                success = execute_update(
                    '''INSERT INTO hse_schedules 
                    (schedule_type, description, frequency, next_due_date, 
                     responsible_person, created_by) 
                    VALUES (?, ?, ?, ?, ?, ?)''',
                    (schedule_type, description, frequency, next_due_date.strftime('%Y-%m-%d'),
                     responsible_person, st.session_state.user['username'])
                )
                if success:
                    st.success("✅ HSE schedule added successfully!")
                else:
                    st.error("❌ Failed to add schedule")
    
    # Display existing schedules
    st.markdown("### 📋 Existing HSE Schedules")
    schedules = execute_query('SELECT * FROM hse_schedules ORDER BY next_due_date')
    
    if schedules:
        for schedule in schedules:
            with st.expander(f"{schedule['schedule_type']} - Due: {schedule['next_due_date']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Frequency:** {schedule['frequency']}")
                    st.write(f"**Responsible:** {schedule['responsible_person'] or 'Not assigned'}")
                    st.write(f"**Status:** {schedule['status']}")
                with col2:
                    st.write(f"**Created By:** {schedule['created_by']}")
                    st.write(f"**Created Date:** {schedule['created_date']}")
                
                st.write(f"**Description:** {schedule['description']}")
                
                # Update status
                if st.button(f"Mark as Completed", key=f"complete_hse_{schedule['id']}"):
                    execute_update(
                        "UPDATE hse_schedules SET status = 'Completed' WHERE id = ?",
                        (schedule['id'],)
                    )
                    st.success("✅ Schedule marked as completed!")
                    st.rerun()
    else:
        st.info("📭 No HSE schedules found")

def show_incident_reports():
    st.markdown("### ⚠️ Incident Reports")
    
    with st.form("incident_report_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            incident_date = st.date_input("Incident Date *", value=datetime.now())
            incident_type = st.selectbox(
                "Incident Type *",
                ["Near Miss", "First Aid Case", "Medical Treatment Case", "Lost Time Injury",
                 "Property Damage", "Fire", "Spill/Release", "Security Breach", "Other"]
            )
            location = st.text_input("Location *", placeholder="Where did it happen?")
        
        with col2:
            severity = st.selectbox(
                "Severity *",
                ["Low", "Medium", "High", "Critical"]
            )
            reported_by = st.text_input("Reported By *", value=st.session_state.user['username'])
        
        description = st.text_area("Description *", height=150, placeholder="Describe the incident in detail...")
        action_taken = st.text_area("Immediate Action Taken", height=100, placeholder="What immediate actions were taken?")
        
        submitted = st.form_submit_button("📤 Submit Incident Report", use_container_width=True)
        
        if submitted:
            if not all([incident_type, location, description]):
                st.error("❌ Please fill in all required fields (*)")
            else:
                success = execute_update(
                    '''INSERT INTO hse_incidents 
                    (incident_date, incident_type, description, location, 
                     severity, reported_by, action_taken) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (incident_date.strftime('%Y-%m-%d'), incident_type, description, location,
                     severity, reported_by, action_taken)
                )
                if success:
                    st.success("✅ Incident report submitted successfully!")
                else:
                    st.error("❌ Failed to submit report")
    
    # Display existing incidents
    st.markdown("### 📋 Recent Incident Reports")
    incidents = execute_query('SELECT * FROM hse_incidents ORDER BY incident_date DESC LIMIT 10')
    
    if incidents:
        for incident in incidents:
            severity_color = {
                "Low": "🟢",
                "Medium": "🟡", 
                "High": "🟠",
                "Critical": "🔴"
            }.get(incident['severity'], "⚪")
            
            with st.expander(f"{severity_color} {incident['incident_type']} - {incident['incident_date']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Location:** {incident['location']}")
                    st.write(f"**Severity:** {incident['severity']}")
                    st.write(f"**Reported By:** {incident['reported_by']}")
                with col2:
                    st.write(f"**Status:** {incident['status']}")
                    st.write(f"**Reported On:** {incident['created_date']}")
                
                st.write(f"**Description:**")
                st.info(incident['description'])
                
                if incident['action_taken']:
                    st.write(f"**Action Taken:**")
                    st.success(incident['action_taken'])
    else:
        st.info("📭 No incident reports found")

def show_new_inspection():
    st.markdown("### 🔍 New HSE Inspection")
    
    with st.form("hse_inspection_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            inspection_date = st.date_input("Inspection Date *", value=datetime.now())
            inspection_type = st.selectbox(
                "Inspection Type *",
                ["Safety", "Health", "Environmental", "Fire Safety", "Equipment", "General"]
            )
            inspector_name = st.text_input("Inspector Name *", value=st.session_state.user['username'])
        
        with col2:
            area_inspected = st.text_input("Area Inspected *", placeholder="e.g., Production Floor, Office Building")
            status = st.selectbox(
                "Status",
                ["Completed", "In Progress", "Scheduled"]
            )
        
        findings = st.text_area("Findings *", height=150, placeholder="Document all findings...")
        recommendations = st.text_area("Recommendations", height=150, placeholder="Recommendations for improvement...")
        
        submitted = st.form_submit_button("📝 Submit Inspection Report", use_container_width=True)
        
        if submitted:
            if not all([inspection_type, inspector_name, area_inspected, findings]):
                st.error("❌ Please fill in all required fields (*)")
            else:
                success = execute_update(
                    '''INSERT INTO hse_inspections 
                    (inspection_date, inspection_type, inspector_name, area_inspected,
                     findings, recommendations, status, created_by) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (inspection_date.strftime('%Y-%m-%d'), inspection_type, inspector_name, area_inspected,
                     findings, recommendations, status, st.session_state.user['username'])
                )
                if success:
                    st.success("✅ Inspection report submitted successfully!")
                else:
                    st.error("❌ Failed to submit report")

# =============================================
# SPACE MANAGEMENT - FACILITY USER
# =============================================
def show_space_management_facility_user():
    st.markdown("<h1 class='app-title'>🏢 Space Management</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📅 Room Booking", "👀 Room Bookings Overview", "📊 Analytics"])
    
    with tab1:
        show_room_booking()
    
    with tab2:
        show_room_bookings_overview()
    
    with tab3:
        show_space_analytics()

def show_room_booking():
    st.markdown("### 📅 Book a Room")
    
    with st.form("room_booking_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            room_name = st.selectbox(
                "Room Name *",
                ["Conference Room A", "Conference Room B", "Training Room", "Executive Boardroom",
                 "Meeting Room 1", "Meeting Room 2", "Auditorium", "Cafeteria", "Open Space"]
            )
            
            room_type = st.selectbox(
                "Room Type *",
                ["Conference", "Meeting", "Training", "Boardroom", "Event", "Other"]
            )
            
            booking_date = st.date_input("Booking Date *", value=datetime.now())
        
        with col2:
            start_time = st.time_input("Start Time *", value=datetime.now().replace(hour=9, minute=0, second=0))
            end_time = st.time_input("End Time *", value=datetime.now().replace(hour=10, minute=0, second=0))
            attendees_count = st.number_input("Number of Attendees", min_value=1, value=5)
        
        purpose = st.text_input("Purpose *", placeholder="e.g., Team Meeting, Client Presentation, Training Session")
        booked_by = st.text_input("Booked By *", value=st.session_state.user['username'])
        notes = st.text_area("Additional Notes", placeholder="Any special requirements...")
        
        submitted = st.form_submit_button("📅 Book Room", use_container_width=True)
        
        if submitted:
            # Check for time conflicts
            conflicting_bookings = execute_query('''
                SELECT * FROM room_bookings 
                WHERE room_name = ? AND booking_date = ?
                AND (
                    (start_time <= ? AND end_time >= ?) OR
                    (start_time <= ? AND end_time >= ?) OR
                    (start_time >= ? AND end_time <= ?)
                )
            ''', (
                room_name, booking_date.strftime('%Y-%m-%d'),
                start_time, start_time,
                end_time, end_time,
                start_time, end_time
            ))
            
            if conflicting_bookings:
                st.error("❌ Time conflict! This room is already booked during the selected time.")
            else:
                success = execute_update(
                    '''INSERT INTO room_bookings 
                    (room_name, room_type, booking_date, start_time, end_time,
                     booked_by, purpose, attendees_count, notes) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (room_name, room_type, booking_date.strftime('%Y-%m-%d'), 
                     start_time.strftime('%H:%M:%S'), end_time.strftime('%H:%M:%S'),
                     booked_by, purpose, attendees_count, notes)
                )
                if success:
                    st.success("✅ Room booked successfully!")
                else:
                    st.error("❌ Failed to book room")

def show_room_bookings_overview():
    st.markdown("### 👀 Room Bookings Overview")
    
    # Get all bookings
    bookings = execute_query('''
        SELECT * FROM room_bookings 
        WHERE booking_date >= DATE('now', '-30 days')
        ORDER BY booking_date, start_time
    ''')
    
    if not bookings:
        st.info("📭 No room bookings found")
        return
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        room_filter = st.selectbox(
            "Filter by Room",
            ["All"] + list(set([b['room_name'] for b in bookings]))
        )
    with col2:
        date_filter = st.date_input(
            "Filter by Date",
            value=datetime.now()
        )
    
    # Apply filters
    filtered_bookings = bookings
    
    if room_filter != "All":
        filtered_bookings = [b for b in filtered_bookings if b['room_name'] == room_filter]
    
    filtered_bookings = [
        b for b in filtered_bookings 
        if datetime.strptime(b['booking_date'], '%Y-%m-%d').date() == date_filter
    ]
    
    st.markdown(f"<div class='card'><h4>📋 {len(filtered_bookings)} Booking(s) for {date_filter.strftime('%B %d, %Y')}</h4></div>", unsafe_allow_html=True)
    
    # Display bookings
    for booking in filtered_bookings:
        with st.expander(f"{booking['room_name']} - {booking['start_time']} to {booking['end_time']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Room Type:** {booking['room_type']}")
                st.write(f"**Date:** {booking['booking_date']}")
                st.write(f"**Time:** {booking['start_time']} - {booking['end_time']}")
            with col2:
                st.write(f"**Booked By:** {booking['booked_by']}")
                st.write(f"**Attendees:** {booking['attendees_count']}")
                st.write(f"**Status:** {booking['status']}")
            
            st.write(f"**Purpose:** {booking['purpose']}")
            
            if booking['notes']:
                st.write(f"**Notes:** {booking['notes']}")
            
            # Cancel booking option
            if st.button(f"Cancel Booking", key=f"cancel_{booking['id']}"):
                execute_update(
                    "UPDATE room_bookings SET status = 'Cancelled' WHERE id = ?",
                    (booking['id'],)
                )
                st.success("✅ Booking cancelled!")
                st.rerun()

def show_space_analytics():
    st.markdown("### 📊 Space Utilization Analytics")
    
    # Get booking data
    bookings = execute_query('SELECT * FROM room_bookings WHERE booking_date >= DATE("now", "-90 days")')
    
    if not bookings:
        st.info("📭 No booking data available for analytics")
        return
    
    df = pd.DataFrame(bookings)
    df['booking_date'] = pd.to_datetime(df['booking_date'])
    df['duration_hours'] = pd.to_timedelta(df['end_time']) - pd.to_timedelta(df['start_time'])
    df['duration_hours'] = df['duration_hours'].dt.total_seconds() / 3600
    
    # Overall statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_bookings = len(df)
        create_metric_card("Total Bookings", total_bookings, "📅")
    
    with col2:
        unique_rooms = df['room_name'].nunique()
        create_metric_card("Rooms Used", unique_rooms, "🏢")
    
    with col3:
        avg_attendees = df['attendees_count'].mean()
        create_metric_card("Avg Attendees", f"{avg_attendees:.0f}", "👥")
    
    with col4:
        total_hours = df['duration_hours'].sum()
        create_metric_card("Total Hours", f"{total_hours:.1f}", "⏱️")
    
    st.markdown("---")
    
    # Room utilization
    st.markdown("### 🏢 Room Utilization")
    
    room_utilization = df.groupby('room_name').agg({
        'id': 'count',
        'duration_hours': 'sum',
        'attendees_count': 'sum'
    }).rename(columns={'id': 'booking_count'}).reset_index()
    
    if not room_utilization.empty:
        fig1 = px.bar(
            room_utilization,
            x='room_name',
            y='booking_count',
            title="Number of Bookings per Room",
            labels={'room_name': 'Room', 'booking_count': 'Number of Bookings'}
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    # Booking trend over time
    st.markdown("### 📈 Booking Trend")
    
    daily_bookings = df.groupby('booking_date').size().reset_index(name='count')
    
    if not daily_bookings.empty:
        fig2 = px.line(
            daily_bookings,
            x='booking_date',
            y='count',
            title="Daily Bookings Trend",
            labels={'booking_date': 'Date', 'count': 'Number of Bookings'}
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Purpose analysis
    st.markdown("### 🎯 Booking Purposes")
    
    purpose_counts = df['purpose'].value_counts().head(10)
    
    if not purpose_counts.empty:
        fig3 = px.pie(
            values=purpose_counts.values,
            names=purpose_counts.index,
            title="Top 10 Booking Purposes"
        )
        st.plotly_chart(fig3, use_container_width=True)

# =============================================
# PLANNED PREVENTIVE MAINTENANCE - FACILITY MANAGER
# =============================================
def show_ppm_facility_manager():
    st.markdown("<h1 class='app-title'>🔧 Planned Preventive Maintenance (Manager)</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📅 Add New Schedule", "📋 Schedule Overview", "📊 Reports & Analytics"])
    
    with tab1:
        show_add_ppm_schedule()  # Same as user but with additional manager features
    
    with tab2:
        show_ppm_manager_overview()
    
    with tab3:
        show_ppm_analytics()

def show_ppm_manager_overview():
    st.markdown("### 📋 PPM Management Dashboard")
    
    # Get all PPM schedules
    schedules = execute_query('SELECT * FROM ppm_schedules ORDER BY next_maintenance_date')
    
    if not schedules:
        st.info("📭 No preventive maintenance schedules found")
        return
    
    # Manager actions: Assign to vendors
    st.markdown("### 👥 Assign Schedules to Vendors")
    
    for schedule in schedules:
        if schedule['status'] in ['Due', 'Prepare for Maintenance'] and not schedule['assigned_vendor']:
            with st.expander(f"🔄 {schedule['schedule_name']} - Needs Assignment"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Category:** {schedule['facility_category']}")
                    st.write(f"**Sub-Category:** {schedule['sub_category']}")
                    st.write(f"**Next Due:** {schedule['next_maintenance_date']}")
                    st.write(f"**Status:** {schedule['status']}")
                
                with col2:
                    # Get appropriate vendors
                    vendor_type_map = {
                        "HVAC": "HVAC",
                        "Generator Maintenance": "Generator",
                        "Fixture and Fittings": "Fixture and Fittings",
                        "Building Maintenance": "Building Maintenance"
                    }
                    
                    vendor_type = vendor_type_map.get(schedule['facility_category'], schedule['facility_category'])
                    vendors = execute_query(
                        'SELECT * FROM vendors WHERE vendor_type = ?',
                        (vendor_type,)
                    )
                    
                    if vendors:
                        vendor_options = {v['company_name']: v['username'] for v in vendors}
                        selected_vendor = st.selectbox(
                            "Select Vendor",
                            options=list(vendor_options.keys()),
                            key=f"vendor_select_{schedule['id']}"
                        )
                        
                        if st.button(f"Assign to {selected_vendor}", key=f"assign_{schedule['id']}"):
                            # Update schedule with vendor assignment
                            execute_update(
                                '''UPDATE ppm_schedules 
                                SET assigned_vendor = ?, status = 'Work In Progress'
                                WHERE id = ?''',
                                (vendor_options[selected_vendor], schedule['id'])
                            )
                            
                            # Create assignment record
                            execute_update(
                                '''INSERT INTO ppm_assignments 
                                (schedule_id, vendor_username, assigned_date, due_date, assigned_by)
                                VALUES (?, ?, ?, ?, ?)''',
                                (schedule['id'], vendor_options[selected_vendor],
                                 datetime.now().strftime('%Y-%m-%d'),
                                 schedule['next_maintenance_date'],
                                 st.session_state.user['username'])
                            )
                            
                            st.success(f"✅ Schedule assigned to {selected_vendor}!")
                            st.rerun()
                    else:
                        st.warning(f"No vendors available for {vendor_type}")

# =============================================
# FINAL APPROVAL OF ALL WORKS - FACILITY MANAGER
# =============================================
def show_final_approval_all_works():
    st.markdown("<h1 class='app-title'>✅ Final Approval - All Works</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 PPM Works", "🛠️ Reactive Works"])
    
    with tab1:
        show_ppm_final_approval()
    
    with tab2:
        show_reactive_final_approval()

def show_ppm_final_approval():
    st.markdown("### 📋 PPM Works Awaiting Final Approval")
    
    # Get PPM assignments completed by vendors
    completed_ppm = execute_query('''
        SELECT pa.*, ps.schedule_name, ps.facility_category, ps.sub_category,
               ps.estimated_cost, ps.actual_cost, v.company_name as vendor_name
        FROM ppm_assignments pa
        JOIN ppm_schedules ps ON pa.schedule_id = ps.id
        LEFT JOIN vendors v ON pa.vendor_username = v.username
        WHERE pa.status = 'Completed'
        ORDER BY pa.completed_date DESC
    ''')
    
    if not completed_ppm:
        st.info("🎉 No PPM works awaiting final approval")
        return
    
    for assignment in completed_ppm:
        with st.expander(f"🔄 {assignment['schedule_name']} - {assignment['vendor_name']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Schedule:** {assignment['schedule_name']}")
                st.write(f"**Category:** {assignment['facility_category']}")
                st.write(f"**Sub-Category:** {assignment['sub_category']}")
                st.write(f"**Assigned Date:** {assignment['assigned_date']}")
                st.write(f"**Completed Date:** {assignment['completed_date']}")
            
            with col2:
                st.write(f"**Vendor:** {assignment['vendor_name']}")
                st.write(f"**Estimated Cost:** {format_ngn(assignment['estimated_cost'])}")
                st.write(f"**Actual Cost:** {format_ngn(assignment['actual_cost'])}")
            
            if assignment['completion_notes']:
                st.write(f"**Completion Notes:**")
                st.info(assignment['completion_notes'])
            
            # Approval action
            st.markdown("---")
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button(f"✅ Approve Work", key=f"approve_ppm_{assignment['id']}", use_container_width=True):
                    execute_update(
                        "UPDATE ppm_assignments SET status = 'Approved' WHERE id = ?",
                        (assignment['id'],)
                    )
                    execute_update(
                        "UPDATE ppm_schedules SET status = 'Approved' WHERE id = ?",
                        (assignment['schedule_id'],)
                    )
                    st.success("✅ PPM work approved!")
                    st.rerun()
            
            with col_b:
                if st.button(f"❌ Request Changes", key=f"reject_ppm_{assignment['id']}", use_container_width=True):
                    st.text_input("Reason for rejection/changes:", key=f"reject_reason_{assignment['id']}")
                    if st.button("Submit", key=f"submit_reject_{assignment['id']}"):
                        execute_update(
                            "UPDATE ppm_assignments SET status = 'Changes Requested' WHERE id = ?",
                            (assignment['id'],)
                        )
                        st.warning("⚠️ Changes requested from vendor")
                        st.rerun()

def show_reactive_final_approval():
    show_final_approval()  # Use existing final approval function

# =============================================
# VENDORS PAGE - ASSIGNED PPM WORK & COMPLETION
# =============================================
def show_vendor_ppm_work():
    st.markdown("<h1 class='app-title'>🔧 Assigned PPM Work</h1>", unsafe_allow_html=True)
    
    vendor_username = st.session_state.user['username']
    
    # Get assigned PPM work
    assigned_ppm = execute_query('''
        SELECT pa.*, ps.schedule_name, ps.facility_category, ps.sub_category,
               ps.description, ps.estimated_duration_hours, ps.estimated_cost,
               ps.next_maintenance_date as due_date
        FROM ppm_assignments pa
        JOIN ppm_schedules ps ON pa.schedule_id = ps.id
        WHERE pa.vendor_username = ? AND pa.status = 'Assigned'
        ORDER BY pa.due_date
    ''', (vendor_username,))
    
    if not assigned_ppm:
        st.info("🎉 No PPM work assigned to you at the moment")
        return
    
    st.markdown(f"<div class='card'><h4>🔧 {len(assigned_ppm)} PPM Job(s) Assigned to You</h4></div>", unsafe_allow_html=True)
    
    for assignment in assigned_ppm:
        with st.expander(f"🛠️ {assignment['schedule_name']} - Due: {assignment['due_date']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Category:** {assignment['facility_category']}")
                st.write(f"**Sub-Category:** {assignment['sub_category']}")
                st.write(f"**Due Date:** {assignment['due_date']}")
                st.write(f"**Assigned Date:** {assignment['assigned_date']}")
                st.write(f"**Est. Duration:** {assignment['estimated_duration_hours']} hours")
                st.write(f"**Est. Cost:** {format_ngn(assignment['estimated_cost'])}")
            
            with col2:
                if assignment['description']:
                    st.write(f"**Description:** {assignment['description']}")
            
            # Completion form
            st.markdown("---")
            st.markdown("### ✅ Complete PPM Work")
            
            with st.form(key=f"complete_ppm_{assignment['id']}"):
                completion_notes = st.text_area(
                    "Completion Notes *",
                    height=100,
                    placeholder="Describe work performed, observations, recommendations..."
                )
                
                actual_cost = st.number_input(
                    "Actual Cost (₦) *",
                    min_value=0.0,
                    value=float(assignment['estimated_cost']),
                    step=1000.0
                )
                
                invoice_number = st.text_input(
                    "Invoice Number",
                    placeholder="Enter your invoice number (if applicable)"
                )
                
                submitted = st.form_submit_button("✅ Mark as Completed", use_container_width=True)
                
                if submitted:
                    if not completion_notes:
                        st.error("❌ Please provide completion notes")
                    else:
                        # Update assignment
                        execute_update(
                            '''UPDATE ppm_assignments 
                            SET status = 'Completed',
                                completed_date = ?,
                                completion_notes = ?,
                                invoice_number = ?
                            WHERE id = ?''',
                            (datetime.now().strftime('%Y-%m-%d'), completion_notes,
                             invoice_number if invoice_number else None, assignment['id'])
                        )
                        
                        # Update schedule
                        execute_update(
                            '''UPDATE ppm_schedules 
                            SET status = 'Completed',
                                actual_completion_date = ?,
                                actual_cost = ?
                            WHERE id = ?''',
                            (datetime.now().strftime('%Y-%m-%d'), actual_cost,
                             assignment['schedule_id'])
                        )
                        
                        st.success("✅ PPM work marked as completed! Awaiting manager approval.")
                        st.rerun()

# =============================================
# AUTHENTICATION
# =============================================
def authenticate_user(username, password):
    user = execute_query('SELECT * FROM users WHERE username = ? AND password_hash = ?', (username, password))
    return user[0] if user else None

# =============================================
# ENHANCED LOGIN PAGE
# =============================================
def show_enhanced_login():
    st.markdown("<h1 class='app-title'>🏢 A-Z Facilities Management Pro APP™</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6b7280;'>Professional Facilities Management Solution</p>", unsafe_allow_html=True)
    
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
# MAIN APPLICATION ROUTING WITH NEW PAGES
# =============================================
def show_main_app():
    user = st.session_state.user
    role = user['role']
    
    with st.sidebar:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color: #1e3a8a; font-size: 1.1rem;'>👋 Welcome, {user['username']}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size: 0.9rem;'><strong>Role:</strong> {role.replace('_', ' ').title()}</p>", unsafe_allow_html=True)
        if user['vendor_type']:
            st.markdown(f"<p style='font-size: 0.9rem;'><strong>Vendor Type:</strong> {user['vendor_type']}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-header'>📱 Navigation</div>", unsafe_allow_html=True)
        
        # Navigation based on user role with new pages
        if role == 'facility_user':
            menu_options = [
                "📊 Dashboard", "📝 Create Request", "📋 My Requests", "✅ Department Approval",
                "🔧 PPM", "⚡ Generator Records", "🛡️ HSE Management", "🏢 Space Management",
                "📈 Reports & Analytics", "📄 Job & Invoice Reports"
            ]
        elif role == 'facility_manager':
            menu_options = [
                "📊 Dashboard", "🛠️ Manage Requests", "✅ Final Approval", "✅ Final Approval All Works",
                "🔧 PPM Manager", "👥 Vendor Management", "📈 Reports & Analytics", "📄 Job & Invoice Reports"
            ]
        else:  # vendor
            menu_options = [
                "📊 Dashboard", "🔧 Assigned Jobs", "✅ Completed Jobs", "🔧 Vendor PPM Work",
                "🏢 Vendor Registration", "🧾 Invoice Creation", "📊 My Reports"
            ]
        
        selected_menu = st.radio("", menu_options, label_visibility="collapsed")
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()
    
    # Main content routing with new pages
    menu_map = {
        # Existing pages
        "📊 Dashboard": show_dashboard,
        "📝 Create Request": show_create_request,
        "📋 My Requests": show_my_requests,
        "✅ Department Approval": show_department_approval,
        "🛠️ Manage Requests": show_manage_requests,
        "✅ Final Approval": show_final_approval,
        "👥 Vendor Management": show_vendor_management,
        "📈 Reports & Analytics": show_reports,
        "🔧 Assigned Jobs": show_assigned_jobs,
        "✅ Completed Jobs": show_completed_jobs,
        "🏢 Vendor Registration": show_vendor_registration,
        "🧾 Invoice Creation": show_invoice_creation,
        "📄 Job & Invoice Reports": show_job_invoice_reports,
        "📊 My Reports": show_vendor_reports,
        
        # New pages
        "🔧 PPM": show_ppm_facility_user,
        "⚡ Generator Records": show_generator_records_facility_user,
        "🛡️ HSE Management": show_hse_management_facility_user,
        "🏢 Space Management": show_space_management_facility_user,
        "🔧 PPM Manager": show_ppm_facility_manager,
        "✅ Final Approval All Works": show_final_approval_all_works,
        "🔧 Vendor PPM Work": show_vendor_ppm_work
    }
    
    if selected_menu in menu_map:
        menu_map[selected_menu]()
    else:
        st.error("Page not found")

# =============================================
# EXISTING FUNCTIONS (keeping them as is)
# =============================================

def show_department_approval():
    """Page for facility user to approve completed jobs from vendors"""
    st.markdown("<h1 class='app-title'>✅ Department Approval</h1>", unsafe_allow_html=True)
    
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
                
                if safe_get(req, 'invoice_number'):
                    st.markdown("### 🧾 Invoice Details")
                    st.write(f"**Invoice Number:** {safe_str(safe_get(req, 'invoice_number'))}")
                    st.write(f"**Invoice Amount:** {format_ngn(safe_get(req, 'invoice_amount'))}")
            
            show_workflow_status(req)
            
            st.markdown("---")
            st.markdown("### ✅ Department Approval Action")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(f"Approve Job Completion", key=f"dept_approve_{safe_get(req, 'id')}", 
                           use_container_width=True, type="primary"):
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

def show_final_approval():
    """Page for facility manager to give final approval"""
    st.markdown("<h1 class='app-title'>✅ Final Manager Approval</h1>", unsafe_allow_html=True)
    
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
                
                if safe_get(req, 'assigned_vendor'):
                    vendor_info = execute_query(
                        'SELECT company_name FROM vendors WHERE username = ?',
                        (safe_get(req, 'assigned_vendor'),)
                    )
                    vendor_name = vendor_info[0]['company_name'] if vendor_info else safe_get(req, 'assigned_vendor')
                    st.write(f"**Vendor:** {vendor_name}")
            
            with col2:
                if safe_get(req, 'job_breakdown'):
                    st.write(f"**Job Breakdown:**")
                    st.info(safe_str(safe_get(req, 'job_breakdown')))
                
                if safe_get(req, 'invoice_number'):
                    st.markdown("### 🧾 Invoice Summary")
                    st.write(f"**Invoice Number:** {safe_str(safe_get(req, 'invoice_number'))}")
                    st.write(f"**Invoice Amount:** {format_ngn(safe_get(req, 'invoice_amount'))}")
            
            show_workflow_status(req)
            
            st.markdown("---")
            st.markdown("### ✅ Final Approval & Report Generation")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(f"✓ Grant Final Approval", key=f"final_approve_{safe_get(req, 'id')}", 
                           use_container_width=True, type="primary"):
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
    st.markdown("<h1 class='app-title'>📋 My Maintenance Requests</h1>", unsafe_allow_html=True)
    
    user_requests = get_user_requests(st.session_state.user['username'])
    
    if not user_requests:
        st.info("📭 No maintenance requests found")
        return
    
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
                
                if safe_get(req, 'invoice_amount'):
                    st.write(f"**Invoice Amount:** {format_ngn(safe_get(req, 'invoice_amount'))}")

def show_manage_requests():
    st.markdown("<h1 class='app-title'>🛠️ Manage Maintenance Requests</h1>", unsafe_allow_html=True)
    
    all_requests = get_all_requests()
    
    if not all_requests:
        st.info("📭 No maintenance requests found")
        return
    
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
    
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Assigned", "Completed", "Approved"])
    with col2:
        priority_filter = st.selectbox("Filter by Priority", ["All", "Low", "Medium", "High", "Critical"])
    
    filtered_requests = all_requests
    if status_filter != "All":
        filtered_requests = [r for r in filtered_requests if safe_get(r, 'status') == status_filter]
    if priority_filter != "All":
        filtered_requests = [r for r in filtered_requests if safe_get(r, 'priority') == priority_filter]
    
    st.markdown(f"<div class='card'><h4>📋 Showing {len(filtered_requests)} request(s)</h4></div>", unsafe_allow_html=True)
    
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
                show_workflow_status(req)
                
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
                    
                    vendors = execute_query('''
                        SELECT v.* FROM vendors v 
                        WHERE v.vendor_type = ?
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
                        st.warning(f"No vendors found for {facility_type}")

def show_assigned_jobs():
    st.markdown("<h1 class='app-title'>🔧 Assigned Jobs</h1>", unsafe_allow_html=True)
    
    vendor_username = st.session_state.user['username']
    assigned_jobs = get_vendor_requests(vendor_username)
    
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
                    
                    amount = quantity * unit_cost
                    vat_amount = (amount + labour_charge) * 0.075 if vat_applicable else 0.0
                    total_amount = amount + labour_charge + vat_amount
                    
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
                            invoice_number = f"INV-{safe_get(job, 'id')}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            
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
    st.markdown("<h1 class='app-title'>✅ Completed Jobs</h1>", unsafe_allow_html=True)
    
    vendor_username = st.session_state.user['username']
    completed_jobs = get_vendor_requests(vendor_username)
    
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

def show_invoice_creation():
    st.markdown("<h1 class='app-title'>🧾 Invoice Creation</h1>", unsafe_allow_html=True)
    
    vendor_username = st.session_state.user['username']
    
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
                    
                    amount = quantity * unit_cost
                    vat_amount = (amount + labour_charge) * 0.075 if vat_applicable else 0.0
                    total_amount = amount + labour_charge + vat_amount
                    
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
                            invoice_number = f"INV-{safe_get(job, 'id')}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                            
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

def show_dashboard():
    user = st.session_state.user
    role = user['role']
    
    if role == 'facility_user':
        show_user_dashboard()
    elif role == 'facility_manager':
        show_manager_dashboard()
    else:
        show_vendor_dashboard()

def show_user_dashboard():
    st.markdown("<h1 class='dashboard-title'>📊 Dashboard Overview</h1>", unsafe_allow_html=True)
    
    user_requests = get_user_requests(st.session_state.user['username'])
    
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
    
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Create New Request", use_container_width=True, key="create_new_dash"):
            show_create_request()
    
    with col2:
        pending_approvals = get_requests_for_user_approval(st.session_state.user['username'])
        if pending_approvals:
            if st.button(f"✅ Approve Jobs ({len(pending_approvals)})", use_container_width=True, type="primary", key="approve_jobs_dash"):
                show_department_approval()
    
    with col3:
        if st.button("📋 View My Requests", use_container_width=True, key="view_requests_dash"):
            show_my_requests()

def show_manager_dashboard():
    st.markdown("<h1 class='dashboard-title'>📊 Dashboard Overview</h1>", unsafe_allow_html=True)
    
    all_requests = get_all_requests()
    
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
    
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🛠️ Manage Requests", use_container_width=True, key="manage_req_dash"):
            show_manage_requests()
    
    with col2:
        pending_final_approvals = get_requests_for_manager_approval()
        if pending_final_approvals:
            if st.button(f"✅ Final Approval ({len(pending_final_approvals)})", use_container_width=True, type="primary", key="final_approve_dash"):
                show_final_approval()
    
    with col3:
        if st.button("👥 Vendor Management", use_container_width=True, key="vendor_mgmt_dash"):
            show_vendor_management()

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
        total_revenue = sum([safe_float(r['invoice_amount']) for r in vendor_requests if r['invoice_amount']])
        create_metric_card("Total Revenue", format_ngn(total_revenue), "💰")
    
    st.markdown("---")
    
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        assigned_jobs = len([r for r in vendor_requests if safe_get(r, 'status') == 'Assigned'])
        if assigned_jobs > 0:
            if st.button(f"🔧 Work on Jobs ({assigned_jobs})", use_container_width=True, type="primary", key="work_jobs_dash"):
                show_assigned_jobs()
    
    with col2:
        vendor_username = st.session_state.user['username']
        jobs_needing_invoice = execute_query('''
            SELECT COUNT(*) as count FROM maintenance_requests 
            WHERE assigned_vendor = ? 
            AND status = 'Completed' 
            AND (invoice_number IS NULL OR invoice_number = '')
        ''', (vendor_username,))
        
        invoice_count = jobs_needing_invoice[0]['count'] if jobs_needing_invoice else 0
        if invoice_count > 0:
            if st.button(f"🧾 Create Invoices ({invoice_count})", use_container_width=True, key="create_inv_dash"):
                show_invoice_creation()
    
    with col3:
        if st.button("📊 My Reports", use_container_width=True, key="my_reports_dash"):
            show_vendor_reports()

def show_vendor_registration():
    st.markdown("<h1 class='app-title'>🏢 Vendor Registration</h1>", unsafe_allow_html=True)
    
    vendor_username = st.session_state.user['username']
    existing_vendor = execute_query('SELECT * FROM vendors WHERE username = ?', (vendor_username,))
    
    if existing_vendor:
        st.info("✅ You are already registered as a vendor.")
        return
    
    st.info("📋 Please complete your vendor registration")
    
    with st.form("vendor_reg_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company Name *")
            contact_person = st.text_input("Contact Person *")
            email = st.text_input("Email *")
            phone = st.text_input("Phone *")
        
        with col2:
            vendor_type = st.selectbox("Vendor Type *", ["HVAC", "Generator", "Building Maintenance", "Electrical", "Plumbing", "Other"])
            address = st.text_area("Address *")
        
        submitted = st.form_submit_button("Register Vendor")
        if submitted:
            if execute_update(
                '''INSERT INTO vendors (username, company_name, contact_person, email, phone, vendor_type, services_offered, address) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (vendor_username, company_name, contact_person, email, phone, vendor_type, "Various services", address)
            ):
                st.success("✅ Vendor registered successfully!")
                st.rerun()

def show_vendor_management():
    st.markdown("<h1 class='app-title'>👥 Vendor Management</h1>", unsafe_allow_html=True)
    
    vendors = execute_query('SELECT * FROM vendors ORDER BY company_name')
    
    if not vendors:
        st.info("📭 No vendors registered")
        return
    
    st.markdown(f"<div class='card'><h4>🏢 {len(vendors)} Registered Vendor(s)</h4></div>", unsafe_allow_html=True)
    
    for vendor in vendors:
        with st.expander(f"🏢 {safe_str(safe_get(vendor, 'company_name'))}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Contact:** {safe_str(safe_get(vendor, 'contact_person'))}")
                st.write(f"**Email:** {safe_str(safe_get(vendor, 'email'))}")
                st.write(f"**Phone:** {safe_str(safe_get(vendor, 'phone'))}")
                st.write(f"**Type:** {safe_str(safe_get(vendor, 'vendor_type'))}")
            with col2:
                st.write(f"**Address:** {safe_str(safe_get(vendor, 'address'))}")
                st.write(f"**Registered:** {safe_str(safe_get(vendor, 'registration_date'))}")

def show_reports():
    st.markdown("<h1 class='app-title'>📈 Reports & Analytics</h1>", unsafe_allow_html=True)
    
    all_requests = get_all_requests()
    
    if not all_requests:
        st.info("📭 No data available for reports")
        return
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Requests", len(all_requests))
    with col2:
        completed = len([r for r in all_requests if r['status'] == 'Completed'])
        st.metric("Completed", completed)
    with col3:
        approved = len([r for r in all_requests if r['status'] == 'Approved'])
        st.metric("Approved", approved)
    
    status_counts = {}
    for req in all_requests:
        status = req['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    if status_counts:
        df = pd.DataFrame({
            'Status': list(status_counts.keys()),
            'Count': list(status_counts.values())
        })
        st.dataframe(df, use_container_width=True)

def show_vendor_reports():
    st.markdown("<h1 class='app-title'>📊 My Vendor Reports</h1>", unsafe_allow_html=True)
    
    vendor_username = st.session_state.user['username']
    vendor_jobs = get_vendor_requests(vendor_username)
    
    if not vendor_jobs:
        st.info("📭 No job data available")
        return
    
    col1, col2, col3 = st.columns(3)
    with col1:
        assigned = len([j for j in vendor_jobs if j['status'] == 'Assigned'])
        st.metric("Assigned", assigned)
    with col2:
        completed = len([j for j in vendor_jobs if j['status'] == 'Completed'])
        st.metric("Completed", completed)
    with col3:
        approved = len([j for j in vendor_jobs if j['status'] == 'Approved'])
        st.metric("Approved", approved)
    
    total_revenue = sum([safe_float(j['invoice_amount']) for j in vendor_jobs if j['invoice_amount']])
    st.metric("Total Revenue", format_ngn(total_revenue))

def show_job_invoice_reports():
    st.markdown("<h1 class='app-title'>📄 Job & Invoice Reports</h1>", unsafe_allow_html=True)
    
    jobs_with_invoices = execute_query('''
        SELECT mr.*, i.*
        FROM maintenance_requests mr
        LEFT JOIN invoices i ON mr.id = i.request_id
        WHERE mr.invoice_number IS NOT NULL
        ORDER BY mr.completed_date DESC
    ''')
    
    if not jobs_with_invoices:
        st.info("📭 No jobs with invoices found")
        return
    
    st.markdown(f"<div class='card'><h4>🧾 {len(jobs_with_invoices)} Job(s) with Invoices</h4></div>", unsafe_allow_html=True)

# =============================================
# PDF Generation Functions (keeping as is)
# =============================================

def generate_final_report_pdf(request_data, invoice_data=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    story = []
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=30,
        alignment=1,
        fontName='Helvetica-Bold'
    )
    
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
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_invoice_pdf(invoice_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph("INVOICE", styles['Heading1']))
    story.append(Spacer(1, 20))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_job_summary_pdf(job_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph("JOB SUMMARY REPORT", styles['Heading1']))
    story.append(Spacer(1, 20))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_monthly_summary_report(jobs):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph(f"MONTHLY SUMMARY REPORT - {datetime.now().strftime('%B %Y')}", styles['Heading1']))
    story.append(Spacer(1, 20))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# =============================================
# MAIN FUNCTION
# =============================================
def main():
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    if st.session_state.user is None:
        show_enhanced_login()
    else:
        show_main_app()

if __name__ == "__main__":
    main()
