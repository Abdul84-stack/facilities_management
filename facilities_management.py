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
    .status-approved { background-color: #bbf7d0; color: #166534; }
    
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
    
    /* Fix for workflow step dates */
    .step-date {
        font-size: 0.8rem;
        color: #666;
        margin-top: 2px;
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
    
    /* PDF download button styling */
    .pdf-download-btn {
        background: linear-gradient(90deg, #dc2626 0%, #ef4444 100%) !important;
        color: white !important;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 5px;
        cursor: pointer;
    }
    
    .pdf-download-btn:hover {
        background: linear-gradient(90deg, #b91c1c 0%, #dc2626 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(220, 38, 38, 0.5);
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
                actual_cost REAL,
                ppm_approved INTEGER DEFAULT 0
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
                net_hours REAL,
                opening_inventory_liters REAL NOT NULL,
                purchase_liters REAL DEFAULT 0,
                closing_inventory_liters REAL NOT NULL,
                net_diesel_consumed REAL,
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
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
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
                    st.rerun()
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
            ["All", "Due", "Not Due", "Prepare for Maintenance", "Work In Progress", "Completed", "Approved"]
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
            "Completed": "status-completed",
            "Approved": "status-approved"
        }.get(status, "")
        
        with st.expander(f"{schedule['schedule_name']} - {status}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Category:** {schedule['facility_category']}")
                st.write(f"**Sub-Category:** {schedule['sub_category']}")
                st.write(f"**Frequency:** {schedule['frequency']}")
                st.write(f"**Next Maintenance:** {schedule['next_maintenance_date']}")
                st.write(f"**Created By:** {schedule['created_by']}")
                st.write(f"**Status:** {status}")
            
            with col2:
                st.write(f"**Estimated Duration:** {schedule['estimated_duration_hours']} hours")
                st.write(f"**Estimated Cost:** {format_ngn(schedule['estimated_cost'])}")
                if schedule.get('assigned_vendor'):
                    vendor_info = execute_query(
                        'SELECT company_name FROM vendors WHERE username = ?',
                        (schedule['assigned_vendor'],)
                    )
                    vendor_name = vendor_info[0]['company_name'] if vendor_info else schedule['assigned_vendor']
                    st.write(f"**Assigned Vendor:** {vendor_name}")
                if schedule.get('actual_completion_date'):
                    st.write(f"**Completed On:** {schedule['actual_completion_date']}")
                    st.write(f"**Actual Cost:** {format_ngn(schedule['actual_cost'])}")
            
            if schedule.get('description'):
                st.write(f"**Description:** {schedule['description']}")
            
            if schedule.get('notes'):
                st.write(f"**Notes:**")
                st.info(schedule['notes'])
            
            # Action buttons for facility user - FIXED APPROVAL WORKFLOW
            if st.session_state.user['role'] == 'facility_user':
                if schedule.get('status') == 'Completed':
                    st.markdown("---")
                    st.markdown("### ✅ Approval Action")
                    
                    ppm_approved = schedule.get('ppm_approved', 0)
                    if ppm_approved == 0:
                        if st.button(f"Approve PPM Work", key=f"approve_ppm_{schedule['id']}", use_container_width=True, type="primary"):
                            # Update approval status
                            if execute_update(
                                "UPDATE ppm_schedules SET ppm_approved = 1, status = 'Approved' WHERE id = ?",
                                (schedule['id'],)
                            ):
                                st.success("✅ PPM work approved successfully!")
                                st.rerun()
                    else:
                        st.success("✅ Already approved")

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
    if 'status' in df.columns:
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
    if 'facility_category' in df.columns:
        category_counts = df['facility_category'].value_counts()
        
        if not category_counts.empty:
            fig2 = px.bar(
                x=category_counts.index,
                y=category_counts.values,
                title="Maintenance by Category",
                labels={'x': 'Category', 'y': 'Count'}
            )
            st.plotly_chart(fig2, use_container_width=True)

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
            
            # Calculate default closing hours
            default_closing = opening_hours + 8.0
            if default_closing > 24.0:
                default_closing = 24.0
            
            closing_hours = st.number_input(
                "Closing Hours *", 
                min_value=opening_hours + 0.1,
                max_value=24.0, 
                value=default_closing, 
                step=0.5
            )
        
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
                # Calculate net hours and diesel consumed
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
                        SET opening_hours = ?, closing_hours = ?, net_hours = ?,
                            opening_inventory_liters = ?, purchase_liters = ?,
                            closing_inventory_liters = ?, net_diesel_consumed = ?, notes = ?
                        WHERE record_date = ? AND generator_type = ?''',
                        (opening_hours, closing_hours, net_hours, 
                         opening_inventory, purchase_liters,
                         closing_inventory, net_diesel, notes, 
                         record_date.strftime('%Y-%m-%d'), generator_type)
                    )
                else:
                    success = execute_update(
                        '''INSERT INTO generator_records 
                        (record_date, generator_type, opening_hours, closing_hours, net_hours,
                         opening_inventory_liters, purchase_liters, closing_inventory_liters,
                         net_diesel_consumed, recorded_by, notes) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (record_date.strftime('%Y-%m-%d'), generator_type, opening_hours, closing_hours, net_hours,
                         opening_inventory, purchase_liters, closing_inventory, net_diesel,
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
                        
                        total_hours = total_hours_result[0]['total_hours'] if total_hours_result and total_hours_result[0]['total_hours'] else 0
                        
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
                                            notes = COALESCE(notes, '') || '\nGenerator reached ' || ? || ' hours on ' || ?
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
                    st.rerun()
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
            [datetime.now() - timedelta(days=30), datetime.now()],
            key="date_range_gen"
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
        total_hours = df['net_hours'].sum() if 'net_hours' in df.columns else 0
        total_diesel = df['net_diesel_consumed'].sum() if 'net_diesel_consumed' in df.columns else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Generator Hours", f"{total_hours:.1f}")
        with col2:
            st.metric("Total Diesel Consumed", f"{total_diesel:.1f} liters")
        
        st.markdown("---")
    
    if not df.empty:
        display_cols = ['record_date', 'generator_type', 'opening_hours', 'closing_hours', 'net_hours']
        display_cols.extend(['opening_inventory_liters', 'purchase_liters', 'closing_inventory_liters', 'net_diesel_consumed'])
        display_cols.append('recorded_by')
        
        # Filter only existing columns
        existing_cols = [col for col in display_cols if col in df.columns]
        st.dataframe(
            df[existing_cols],
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
    
    # Overall statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_hours = df['net_hours'].sum() if 'net_hours' in df.columns else 0
        create_metric_card("Total Hours", f"{total_hours:.1f}", "⏱️")
    
    with col2:
        total_diesel = df['net_diesel_consumed'].sum() if 'net_diesel_consumed' in df.columns else 0
        create_metric_card("Total Diesel", f"{total_diesel:.1f}L", "⛽")
    
    with col3:
        if 'record_date' in df.columns and 'net_hours' in df.columns:
            df['record_date'] = pd.to_datetime(df['record_date'])
            avg_hours_per_day = df.groupby('record_date')['net_hours'].sum().mean()
            create_metric_card("Avg Daily Hours", f"{avg_hours_per_day:.1f}", "📅")
        else:
            create_metric_card("Avg Daily Hours", "0.0", "📅")
    
    with col4:
        diesel_per_hour = total_diesel / total_hours if total_hours > 0 else 0
        create_metric_card("Diesel/Hour", f"{diesel_per_hour:.2f}L", "📊")
    
    st.markdown("---")
    
    # Generator comparison
    st.markdown("### ⚡ Generator Performance Comparison")
    
    if 'generator_type' in df.columns and 'net_hours' in df.columns and 'net_diesel_consumed' in df.columns:
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

# =============================================
# ENHANCED JOB & INVOICE REPORTS WITH BEAUTIFUL PDF
# =============================================
def show_job_invoice_reports():
    st.markdown("<h1 class='app-title'>📄 Job & Invoice Reports</h1>", unsafe_allow_html=True)
    
    # Get all jobs with invoices
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
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox(
            "Filter by Approval Status", 
            ["All", "Fully Approved", "Pending Approval", "Department Approved"]
        )
    with col2:
        vendor_filter = st.selectbox(
            "Filter by Vendor",
            ["All"] + list(set([j.get('assigned_vendor', '') for j in jobs_with_invoices if j.get('assigned_vendor')]))
        )
    with col3:
        month_filter = st.selectbox(
            "Filter by Month",
            ["All", "Current Month", "Last Month", "Last 3 Months"]
        )
    
    # Apply filters
    filtered_jobs = jobs_with_invoices
    
    if status_filter == "Fully Approved":
        filtered_jobs = [j for j in filtered_jobs if j.get('facilities_manager_approval') == 1]
    elif status_filter == "Pending Approval":
        filtered_jobs = [j for j in filtered_jobs if j.get('facilities_manager_approval') != 1]
    elif status_filter == "Department Approved":
        filtered_jobs = [j for j in filtered_jobs if j.get('requesting_dept_approval') == 1 and j.get('facilities_manager_approval') != 1]
    
    if vendor_filter != "All":
        filtered_jobs = [j for j in filtered_jobs if j.get('assigned_vendor') == vendor_filter]
    
    if month_filter != "All":
        current_date = datetime.now()
        if month_filter == "Current Month":
            filtered_jobs = [j for j in filtered_jobs 
                           if j.get('completed_date') 
                           and datetime.strptime(j['completed_date'][:10], '%Y-%m-%d').month == current_date.month]
        elif month_filter == "Last Month":
            last_month = current_date.month - 1 if current_date.month > 1 else 12
            filtered_jobs = [j for j in filtered_jobs 
                           if j.get('completed_date') 
                           and datetime.strptime(j['completed_date'][:10], '%Y-%m-%d').month == last_month]
    
    st.markdown(f"<div class='card'><h4>📋 Showing {len(filtered_jobs)} Filtered Job(s)</h4></div>", unsafe_allow_html=True)
    
    # Summary statistics
    st.markdown("### 📊 Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_amount = sum([j.get('total_amount', 0) for j in filtered_jobs])
        create_metric_card("Total Value", format_ngn(total_amount), "💰")
    
    with col2:
        approved_count = len([j for j in filtered_jobs if j.get('facilities_manager_approval') == 1])
        create_metric_card("Approved", approved_count, "✅")
    
    with col3:
        pending_count = len([j for j in filtered_jobs if j.get('facilities_manager_approval') != 1])
        create_metric_card("Pending", pending_count, "⏳")
    
    with col4:
        vat_total = sum([j.get('vat_amount', 0) for j in filtered_jobs])
        create_metric_card("Total VAT", format_ngn(vat_total), "🧾")
    
    st.markdown("---")
    
    # Display jobs with PDF download options
    for job in filtered_jobs:
        status = job.get('status', 'N/A')
        approval_status = "✅ Fully Approved" if job.get('facilities_manager_approval') == 1 else \
                         "🟡 Department Approved" if job.get('requesting_dept_approval') == 1 else \
                         "⏳ Pending Approval"
        
        with st.expander(f"{approval_status} - Job #{job.get('id')}: {job.get('title')} - Amount: {format_ngn(job.get('total_amount', 0))}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📝 Job Details")
                st.write(f"**Job ID:** {job.get('id')}")
                st.write(f"**Title:** {job.get('title')}")
                st.write(f"**Description:** {job.get('description')}")
                st.write(f"**Location:** {job.get('location', 'Common Area')}")
                st.write(f"**Facility Type:** {job.get('facility_type')}")
                st.write(f"**Priority:** {job.get('priority')}")
                st.write(f"**Created By:** {job.get('created_by')}")
                st.write(f"**Created Date:** {job.get('created_date')}")
                st.write(f"**Completed Date:** {job.get('completed_date', 'N/A')}")
                st.write(f"**Status:** {status}")
                
                if job.get('assigned_vendor'):
                    vendor_info = execute_query(
                        'SELECT company_name FROM vendors WHERE username = ?',
                        (job.get('assigned_vendor'),)
                    )
                    vendor_name = vendor_info[0]['company_name'] if vendor_info else job.get('assigned_vendor')
                    st.write(f"**Assigned Vendor:** {vendor_name}")
            
            with col2:
                st.markdown("### 🧾 Invoice Details")
                st.write(f"**Invoice Number:** {job.get('invoice_number', 'N/A')}")
                st.write(f"**Invoice Date:** {job.get('invoice_date', 'N/A')}")
                st.write(f"**Details of Work:** {job.get('details_of_work', 'N/A')}")
                st.write(f"**Quantity:** {job.get('quantity', 1)}")
                st.write(f"**Unit Cost:** {format_ngn(job.get('unit_cost', 0))}")
                st.write(f"**Amount:** {format_ngn(job.get('amount', 0))}")
                st.write(f"**Labour/Service Charge:** {format_ngn(job.get('labour_charge', 0))}")
                st.write(f"**VAT Applicable:** {'Yes (7.5%)' if job.get('vat_applicable') else 'No'}")
                st.write(f"**VAT Amount:** {format_ngn(job.get('vat_amount', 0))}")
                st.write(f"**Total Amount:** {format_ngn(job.get('total_amount', 0))}")
                st.write(f"**Invoice Status:** {job.get('status', 'N/A')}")
                
                st.markdown("### ✅ Approval Status")
                st.write(f"**Department Approval:** {'✅ Approved' if job.get('requesting_dept_approval') else '❌ Pending'}")
                st.write(f"**Department Approval Date:** {job.get('department_approval_date', 'N/A')}")
                st.write(f"**Manager Approval:** {'✅ Approved' if job.get('facilities_manager_approval') else '❌ Pending'}")
                st.write(f"**Manager Approval Date:** {job.get('manager_approval_date', 'N/A')}")
            
            # PDF Download Section
            st.markdown("---")
            st.markdown("### 📄 Download Reports")
            
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                # Generate and download detailed report
                pdf_buffer = generate_enhanced_final_report_pdf(job)
                
                st.download_button(
                    label="📥 Download Final Report",
                    data=pdf_buffer.getvalue(),
                    file_name=f"Final_Report_Job_{job.get('id')}_{job.get('invoice_number')}.pdf",
                    mime="application/pdf",
                    key=f"final_report_{job.get('id')}",
                    use_container_width=True,
                    type="primary"
                )
            
            with col_b:
                # Generate invoice-only PDF
                invoice_pdf = generate_enhanced_invoice_pdf(job)
                st.download_button(
                    label="🧾 Download Invoice",
                    data=invoice_pdf.getvalue(),
                    file_name=f"Invoice_{job.get('invoice_number')}.pdf",
                    mime="application/pdf",
                    key=f"invoice_only_{job.get('id')}",
                    use_container_width=True
                )
            
            with col_c:
                # Generate job summary PDF
                job_summary_pdf = generate_enhanced_job_summary_pdf(job)
                st.download_button(
                    label="📋 Download Job Summary",
                    data=job_summary_pdf.getvalue(),
                    file_name=f"Job_Summary_{job.get('id')}.pdf",
                    mime="application/pdf",
                    key=f"job_summary_{job.get('id')}",
                    use_container_width=True
                )
            
            # Financial Summary
            st.markdown("---")
            st.markdown("### 💰 Financial Summary")
            
            col_x, col_y, col_z = st.columns(3)
            with col_x:
                st.metric("Total Amount", format_ngn(job.get('total_amount', 0)))
            with col_y:
                vat_percent = 7.5 if job.get('vat_applicable') else 0
                st.metric("VAT", f"{vat_percent}%")
            with col_z:
                net_amount = job.get('total_amount', 0) - job.get('vat_amount', 0)
                st.metric("Net Amount", format_ngn(net_amount))
    
    # Bulk download options for manager
    if st.session_state.user['role'] == 'facility_manager':
        st.markdown("---")
        st.markdown("### 📦 Bulk Report Generation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Generate All Approved Reports (ZIP)", use_container_width=True):
                approved_jobs = [j for j in filtered_jobs if j.get('facilities_manager_approval') == 1]
                
                if approved_jobs:
                    # Create a ZIP file with all PDFs
                    import zipfile
                    zip_buffer = io.BytesIO()
                    
                    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                        for job in approved_jobs:
                            pdf_buffer = generate_enhanced_final_report_pdf(job)
                            file_name = f"Approved_Job_{job.get('id')}_{job.get('invoice_number')}.pdf"
                            zip_file.writestr(file_name, pdf_buffer.getvalue())
                    
                    zip_buffer.seek(0)
                    
                    st.download_button(
                        label="📦 Download All Approved Reports (ZIP)",
                        data=zip_buffer.getvalue(),
                        file_name="All_Approved_Job_Reports.zip",
                        mime="application/zip",
                        key="bulk_download",
                        use_container_width=True
                    )
                else:
                    st.warning("No fully approved jobs to download")
        
        with col2:
            if st.button("📊 Generate Monthly Summary Report", use_container_width=True):
                # Generate monthly summary report
                monthly_summary_pdf = generate_enhanced_monthly_summary_report(filtered_jobs)
                
                st.download_button(
                    label="📈 Download Monthly Summary",
                    data=monthly_summary_pdf.getvalue(),
                    file_name=f"Monthly_Summary_{datetime.now().strftime('%Y_%m')}.pdf",
                    mime="application/pdf",
                    key="monthly_summary",
                    use_container_width=True
                )

# =============================================
# ENHANCED PDF GENERATION WITH BEAUTIFUL UI/UX
# =============================================
def generate_enhanced_final_report_pdf(request_data, invoice_data=None):
    """Generate enhanced final approved PDF report with beautiful design"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles with beautiful design
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=20,
        alignment=1,
        fontName='Helvetica-Bold',
        underline=True
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#3b82f6'),
        spaceAfter=12,
        spaceBefore=15,
        fontName='Helvetica-Bold',
        borderPadding=5,
        borderColor=colors.HexColor('#3b82f6'),
        borderWidth=1
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#4b5563'),
        spaceAfter=8,
        alignment=1,
        fontName='Helvetica'
    )
    
    # Header with logo and company info
    story.append(Paragraph("A-Z FACILITIES MANAGEMENT PRO APP™", title_style))
    story.append(Paragraph("FINAL APPROVED JOB REPORT", ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#10b981'),
        spaceAfter=15,
        alignment=1,
        fontName='Helvetica-Bold'
    )))
    
    # Report details
    story.append(Paragraph(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", header_style))
    story.append(Paragraph("Currency: NGN (₦)", header_style))
    story.append(Spacer(1, 25))
    
    # Job Information Section
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
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
    ]))
    story.append(job_table)
    story.append(Spacer(1, 20))
    
    # Invoice Information Section
    story.append(Paragraph("INVOICE DETAILS", subtitle_style))
    
    if invoice_data or request_data.get('invoice_number'):
        invoice_data_to_use = invoice_data if invoice_data else request_data
        invoice_info = [
            ["Invoice Number:", safe_str(safe_get(invoice_data_to_use, 'invoice_number'))],
            ["Invoice Date:", safe_str(safe_get(invoice_data_to_use, 'invoice_date'))],
            ["Details of Work:", safe_str(safe_get(invoice_data_to_use, 'details_of_work'))],
            ["Quantity:", safe_str(safe_get(invoice_data_to_use, 'quantity'), '1')],
            ["Unit Cost:", format_ngn(safe_get(invoice_data_to_use, 'unit_cost'))],
            ["Amount:", format_ngn(safe_get(invoice_data_to_use, 'amount'))],
            ["Labour/Service Charge:", format_ngn(safe_get(invoice_data_to_use, 'labour_charge'))],
            ["VAT Applicable:", "Yes (7.5%)" if safe_get(invoice_data_to_use, 'vat_applicable') else "No"],
            ["VAT Amount:", format_ngn(safe_get(invoice_data_to_use, 'vat_amount'))],
            ["Total Amount:", format_ngn(safe_get(invoice_data_to_use, 'total_amount'))]
        ]
        
        invoice_table = Table(invoice_info, colWidths=[150, 300])
        invoice_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#10b981')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f0fdf4')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1fae5')),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(invoice_table)
        story.append(Spacer(1, 20))
    
    # Approval Status Section
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
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
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
    
    # Footer with watermark
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

def generate_enhanced_invoice_pdf(invoice_data):
    """Generate beautiful invoice-only PDF"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title with gradient effect simulation
    story.append(Paragraph("INVOICE", ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=20,
        alignment=1,
        fontName='Helvetica-Bold',
        underline=True
    )))
    
    # Company info
    story.append(Paragraph("A-Z Facilities Management Pro APP™", styles['Normal']))
    story.append(Paragraph("Professional Facilities Management Solution", ParagraphStyle(
        'CompanySub',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.gray,
        alignment=1,
        spaceAfter=15
    )))
    
    # Invoice details table
    invoice_info = [
        ["Invoice Number:", invoice_data.get('invoice_number', 'N/A')],
        ["Invoice Date:", invoice_data.get('invoice_date', 'N/A')],
        ["Job ID:", invoice_data.get('id', 'N/A')],
        ["Job Title:", invoice_data.get('title', 'N/A')],
        ["Vendor:", invoice_data.get('assigned_vendor', 'N/A')],
    ]
    
    invoice_table = Table(invoice_info, colWidths=[150, 300])
    invoice_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(invoice_table)
    story.append(Spacer(1, 20))
    
    # Amount details table
    amount_data = [
        ["Description", "Quantity", "Unit Price", "Amount"],
        [invoice_data.get('details_of_work', 'Work performed'), 
         invoice_data.get('quantity', 1), 
         format_ngn(invoice_data.get('unit_cost', 0)), 
         format_ngn(invoice_data.get('amount', 0))],
        ["Labour/Service Charge", "", "", format_ngn(invoice_data.get('labour_charge', 0))],
        ["Subtotal", "", "", format_ngn(invoice_data.get('amount', 0) + invoice_data.get('labour_charge', 0))],
        ["VAT (7.5%)" if invoice_data.get('vat_applicable') else "VAT", "", "", format_ngn(invoice_data.get('vat_amount', 0))],
        ["TOTAL", "", "", format_ngn(invoice_data.get('total_amount', 0))]
    ]
    
    amount_table = Table(amount_data, colWidths=[250, 60, 80, 80])
    amount_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(amount_table)
    
    # Payment terms
    story.append(Spacer(1, 20))
    story.append(Paragraph("Payment Terms:", ParagraphStyle(
        'TermsTitle',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#4b5563'),
        spaceAfter=5
    )))
    story.append(Paragraph("Net 30 days from invoice date. Please make payment to the account details provided by the vendor.", 
                         ParagraphStyle('Terms', parent=styles['Normal'], fontSize=10)))
    
    # Footer
    story.append(Spacer(1, 30))
    footer_text = f"Invoice Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Page 1 of 1"
    story.append(Paragraph(footer_text, ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.gray,
        alignment=1
    )))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_enhanced_job_summary_pdf(job_data):
    """Generate beautiful job summary PDF"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph("JOB SUMMARY REPORT", ParagraphStyle(
        'JobSummaryTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=15,
        alignment=1,
        fontName='Helvetica-Bold'
    )))
    
    story.append(Spacer(1, 10))
    
    # Job details in a nice table
    job_info = [
        ["Job ID:", job_data.get('id', 'N/A')],
        ["Title:", job_data.get('title', 'N/A')],
        ["Description:", job_data.get('description', 'N/A')],
        ["Location:", job_data.get('location', 'Common Area')],
        ["Facility Type:", job_data.get('facility_type', 'N/A')],
        ["Priority:", job_data.get('priority', 'N/A')],
        ["Status:", job_data.get('status', 'N/A')],
        ["Created By:", job_data.get('created_by', 'N/A')],
        ["Created Date:", job_data.get('created_date', 'N/A')],
        ["Completed Date:", job_data.get('completed_date', 'N/A')],
        ["Assigned Vendor:", job_data.get('assigned_vendor', 'N/A')],
    ]
    
    job_table = Table(job_info, colWidths=[150, 300])
    job_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#10b981')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f0fdf4')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1fae5')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
    ]))
    story.append(job_table)
    
    # Add approval status if available
    if job_data.get('requesting_dept_approval') or job_data.get('facilities_manager_approval'):
        story.append(Spacer(1, 20))
        story.append(Paragraph("APPROVAL STATUS", ParagraphStyle(
            'ApprovalTitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#3b82f6'),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )))
        
        approval_info = [
            ["Department Approval:", "✅ Approved" if job_data.get('requesting_dept_approval') else "❌ Pending"],
            ["Manager Approval:", "✅ Approved" if job_data.get('facilities_manager_approval') else "❌ Pending"],
            ["Invoice Status:", job_data.get('status', 'N/A')]
        ]
        
        approval_table = Table(approval_info, colWidths=[150, 300])
        approval_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#dbeafe')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#93c5fd')),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(approval_table)
    
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                         ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, textColor=colors.gray, alignment=1)))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_enhanced_monthly_summary_report(jobs):
    """Generate enhanced monthly summary report"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    story.append(Paragraph(f"MONTHLY SUMMARY REPORT - {datetime.now().strftime('%B %Y')}", ParagraphStyle(
        'MonthlyTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=15,
        alignment=1,
        fontName='Helvetica-Bold'
    )))
    story.append(Spacer(1, 15))
    
    # Summary statistics
    total_jobs = len(jobs)
    approved_jobs = len([j for j in jobs if j.get('facilities_manager_approval') == 1])
    total_amount = sum([safe_float(j.get('total_amount', 0)) for j in jobs])
    vat_total = sum([safe_float(j.get('vat_amount', 0)) for j in jobs])
    
    summary_data = [
        ["Total Jobs", str(total_jobs)],
        ["Fully Approved Jobs", str(approved_jobs)],
        ["Total Invoice Amount", format_ngn(total_amount)],
        ["Total VAT", format_ngn(vat_total)],
        ["Net Amount", format_ngn(total_amount - vat_total)],
    ]
    
    summary_table = Table(summary_data, colWidths=[200, 200])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#f0fdf4')),
        ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#fef3c7')),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Job list table
    if jobs:
        story.append(Paragraph("JOB DETAILS", ParagraphStyle(
            'JobListTitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#3b82f6'),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )))
        
        job_list_data = [["Job ID", "Title", "Vendor", "Amount", "Status"]]
        
        for job in jobs[:20]:  # Limit to first 20 jobs for readability
            status = "Approved" if job.get('facilities_manager_approval') == 1 else "Pending"
            vendor = job.get('assigned_vendor', 'N/A')
            if vendor != 'N/A':
                vendor_info = execute_query('SELECT company_name FROM vendors WHERE username = ?', (vendor,))
                vendor = vendor_info[0]['company_name'] if vendor_info else vendor
            
            job_list_data.append([
                job.get('id'),
                job.get('title', 'N/A')[:30] + "..." if len(job.get('title', '')) > 30 else job.get('title', 'N/A'),
                vendor[:20] + "..." if len(vendor) > 20 else vendor,
                format_ngn(job.get('total_amount', 0)),
                status
            ])
        
        job_list_table = Table(job_list_data, colWidths=[60, 150, 100, 100, 80])
        job_list_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(job_list_table)
        
        if len(jobs) > 20:
            story.append(Paragraph(f"... and {len(jobs) - 20} more jobs", 
                                 ParagraphStyle('MoreJobs', parent=styles['Normal'], fontSize=10, textColor=colors.gray)))
    
    # Footer
    story.append(Spacer(1, 30))
    footer = Paragraph(
        f"© 2025 A-Z Facilities Management Pro APP™ | Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.gray, alignment=1)
    )
    story.append(footer)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

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
# MAIN APPLICATION ROUTING
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
        
        # Navigation based on user role
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
    
    # Main content routing
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
                    st.rerun()
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
        total_revenue = sum([safe_float(r.get('invoice_amount', 0)) for r in vendor_requests if r])
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
    
    total_revenue = sum([safe_float(j.get('invoice_amount', 0)) for j in vendor_jobs])
    st.metric("Total Revenue", format_ngn(total_revenue))

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
