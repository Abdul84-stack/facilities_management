import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.units import inch
import base64
from PIL import Image as PILImage
import numpy as np

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
        font-size: 2.5rem !important;
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
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.5);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f1f5f9 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
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
        padding: 12px;
        border-radius: 8px;
        margin: 20px 0;
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
# DATABASE SETUP WITH ENHANCED SCHEMA
# =============================================
def init_database():
    conn = sqlite3.connect('facilities_management.db')
    cursor = conn.cursor()
    
    # Users table
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
    
    # Maintenance requests table with all columns
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS maintenance_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT NOT NULL,
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
            requesting_dept_approval BOOLEAN DEFAULT 0,
            facilities_manager_approval BOOLEAN DEFAULT 0
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
            username TEXT NOT NULL,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            certificate_incorporation BLOB,
            tax_clearance_certificate BLOB,
            audited_financial_statement BLOB
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
            vat_applicable BOOLEAN DEFAULT 0,
            vat_amount REAL DEFAULT 0,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (request_id) REFERENCES maintenance_requests (id)
        )
    ''')
    
    # Check and add missing columns to existing tables
    def add_column_if_not_exists(table, column, column_type):
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        if column not in columns:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")
    
    # Add missing columns to maintenance_requests
    add_column_if_not_exists('maintenance_requests', 'location', 'TEXT DEFAULT "Common Area"')
    add_column_if_not_exists('maintenance_requests', 'job_breakdown', 'TEXT')
    
    # Add missing columns to vendors
    vendor_columns = [
        ('annual_turnover', 'REAL'),
        ('tax_identification_number', 'TEXT'),
        ('rc_number', 'TEXT'),
        ('key_management_staff', 'TEXT'),
        ('account_details', 'TEXT'),
        ('certificate_incorporation', 'BLOB'),
        ('tax_clearance_certificate', 'BLOB'),
        ('audited_financial_statement', 'BLOB')
    ]
    
    for column, column_type in vendor_columns:
        add_column_if_not_exists('vendors', column, column_type)
    
    # Insert sample data
    sample_users = [
        ('facility_user', '0123456', 'facility_user', None),
        ('facility_manager', '0123456', 'facility_manager', None),
        ('hvac_vendor', '0123456', 'vendor', 'HVAC'),
        ('generator_vendor', '0123456', 'vendor', 'Generator'),
        ('fixture_vendor', '0123456', 'vendor', 'Fixture and Fittings'),
        ('building_vendor', '0123456', 'vendor', 'Building Maintenance'),
        ('hse_vendor', '0123456', 'vendor', 'HSE'),
        ('space_vendor', '0123456', 'vendor', 'Space Management')
    ]
    
    for username, password, role, vendor_type in sample_users:
        try:
            cursor.execute(
                'INSERT OR IGNORE INTO users (username, password_hash, role, vendor_type) VALUES (?, ?, ?, ?)',
                (username, password, role, vendor_type)
            )
        except sqlite3.IntegrityError:
            pass
    
    # Sample vendor registrations
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
                INSERT OR IGNORE INTO vendors 
                (username, company_name, contact_person, email, phone, vendor_type, services_offered, 
                 annual_turnover, tax_identification_number, rc_number, key_management_staff, 
                 account_details, certification, address) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', vendor_data)
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()

# Initialize database
init_database()

# =============================================
# DATABASE FUNCTIONS
# =============================================
def get_connection():
    return sqlite3.connect('facilities_management.db', detect_types=sqlite3.PARSE_DECLTYPES)

def execute_query(query, params=()):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results

def execute_update(query, params=()):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

# =============================================
# SAFE DATA ACCESS FUNCTIONS
# =============================================
def safe_get(data, key, default=None):
    """Safely get value from dictionary with fallback"""
    if not data:
        return default
    return data.get(key, default)

def safe_float(value, default=0.0):
    """Safely convert value to float with fallback"""
    try:
        if value is None:
            return default
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_str(value, default="N/A"):
    """Safely convert value to string with fallback"""
    if value is None:
        return default
    return str(value)

def safe_int(value, default=0):
    """Safely convert value to integer with fallback"""
    try:
        if value is None:
            return default
        return int(value)
    except (ValueError, TypeError):
        return default

def format_ngn(amount):
    """Format amount as NGN currency"""
    return f"₦{safe_float(amount):,.2f}"

# =============================================
# ENHANCED PDF GENERATION WITH BETTER UI
# =============================================
def generate_job_invoice_pdf(request_data, invoice_data=None):
    """Generate enhanced PDF report for job completion and invoice"""
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
    
    # Header with logo and title
    header_data = [
        ["A-Z FACILITIES MANAGEMENT PRO APP™", "", "JOB & INVOICE REPORT"],
        ["", "", f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"],
        ["", "", "Currency: NGN (₦)"]
    ]
    
    header_table = Table(header_data, colWidths=[200, 100, 200])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f1f5f9')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('SPAN', (0, 0), (1, 0)),
    ]))
    story.append(header_table)
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
        ["Status:", safe_str(safe_get(request_data, 'status'))],
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
    
    # Approval Status
    story.append(Paragraph("APPROVAL STATUS", subtitle_style))
    approval_data = [
        ["Approval Type", "Status", "Date"],
        ["Department Approval", 
         "✅ APPROVED" if safe_get(request_data, 'requesting_dept_approval') else "⏳ PENDING",
         safe_str(safe_get(request_data, 'completed_date'), '-')],
        ["Facilities Manager Approval", 
         "✅ APPROVED" if safe_get(request_data, 'facilities_manager_approval') else "⏳ PENDING",
         safe_str(safe_get(request_data, 'completed_date'), '-')]
    ]
    
    approval_table = Table(approval_data, colWidths=[200, 150, 150])
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
    
    # Footer
    story.append(Spacer(1, 30))
    footer = Paragraph(
        f"© 2025 A-Z Facilities Management Pro APP™. Developed by Abdulahi Ibrahim. "
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
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
# ENHANCED DASHBOARD COMPONENTS
# =============================================
def create_metric_card(title, value, icon="📊", change=None):
    """Create a beautiful metric card"""
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f"<div style='font-size: 2.5rem;'>{icon}</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<h3 style='margin: 0;'>{title}</h3>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='margin: 0; color: #1e3a8a;'>{value}</h1>", unsafe_allow_html=True)
        if change:
            color = "green" if change >= 0 else "red"
            arrow = "↑" if change >= 0 else "↓"
            st.markdown(f"<p style='margin: 0; color: {color};'>{arrow} {abs(change)}%</p>", unsafe_allow_html=True)

def show_enhanced_login():
    """Enhanced login page with beautiful UI"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
        st.markdown("<h1 class='app-title'>🏢 A-Z Facilities Management Pro APP™</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6b7280;'>Professional Facilities Management Solution</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #1e3a8a;'>🔐 Login to Your Account</h3>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                login_button = st.form_submit_button("🚀 Login", use_container_width=True)
            with col2:
                if st.form_submit_button("🔄 Reset", type="secondary", use_container_width=True):
                    st.rerun()
            
            if login_button:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state.user = user
                        st.success("Login successful! Redirecting...")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Sample credentials
        with st.expander("📋 Sample Credentials"):
            st.code("""
            👥 Users:
            • Facility User: facility_user / 0123456
            • Facility Manager: facility_manager / 0123456
            
            🏢 Vendors:
            • HVAC Solutions Inc.: hvac_vendor / 0123456
            • Generator Pros Ltd.: generator_vendor / 0123456
            • Fixture Masters Co.: fixture_vendor / 0123456
            • Building Care Services: building_vendor / 0123456
            """)
        
        st.markdown("---")
        st.markdown("<p style='text-align: center; color: #6b7280;'>© 2025 A-Z Facilities Management Pro APP™. Developed by Abdulahi Ibrahim.</p>", unsafe_allow_html=True)

# =============================================
# MAIN APPLICATION FUNCTIONS (ENHANCED)
# =============================================
def show_main_app():
    user = st.session_state.user
    role = user['role']
    
    # Enhanced sidebar
    with st.sidebar:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color: #1e3a8a;'>👋 Welcome, {user['username']}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p><strong>Role:</strong> {role.replace('_', ' ').title()}</p>", unsafe_allow_html=True)
        if user['vendor_type']:
            st.markdown(f"<p><strong>Vendor Type:</strong> {user['vendor_type']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p><strong>Currency:</strong> <span class='ngn'>NGN (₦)</span></p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-header'>Navigation</div>", unsafe_allow_html=True)
        
        # Navigation based on user role
        if role == 'facility_user':
            menu_options = ["📊 Dashboard", "📝 Create Request", "📋 My Requests"]
        elif role == 'facility_manager':
            menu_options = ["📊 Dashboard", "🛠️ Manage Requests", "👥 Vendor Management", 
                          "📈 Reports & Analytics", "📄 Job & Invoice Reports"]
        else:  # vendor
            menu_options = ["📊 Dashboard", "🔧 Assigned Jobs", "✅ Completed Jobs", 
                          "🏢 Vendor Registration", "🧾 Invoice Creation", "📄 My Reports"]
        
        selected_menu = st.radio("", menu_options, label_visibility="collapsed")
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()
    
    # Main content routing
    menu_map = {
        "📊 Dashboard": show_dashboard,
        "📝 Create Request": show_create_request,
        "📋 My Requests": show_my_requests,
        "🛠️ Manage Requests": show_manage_requests,
        "👥 Vendor Management": show_vendor_management,
        "📈 Reports & Analytics": show_reports,
        "🔧 Assigned Jobs": show_assigned_jobs,
        "✅ Completed Jobs": show_completed_jobs,
        "🏢 Vendor Registration": show_vendor_registration,
        "🧾 Invoice Creation": show_invoice_creation,
        "📄 Job & Invoice Reports": show_job_invoice_reports,
        "📄 My Reports": show_vendor_reports
    }
    
    if selected_menu in menu_map:
        menu_map[selected_menu]()

def show_dashboard():
    st.markdown("<h1 class='app-title'>📊 Dashboard Overview</h1>", unsafe_allow_html=True)
    
    user = st.session_state.user
    role = user['role']
    
    if role == 'facility_user':
        show_user_dashboard()
    elif role == 'facility_manager':
        show_manager_dashboard()
    else:  # vendor
        show_vendor_dashboard()

def show_user_dashboard():
    user_requests = execute_query(
        'SELECT * FROM maintenance_requests WHERE created_by = ? ORDER BY created_date DESC',
        (st.session_state.user['username'],)
    )
    
    # Stats in metric cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Total Requests", len(user_requests), "📋")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        pending_count = len([r for r in user_requests if safe_get(r, 'status') == 'Pending'])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Pending", pending_count, "⏳")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        completed_count = len([r for r in user_requests if safe_get(r, 'status') == 'Completed'])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Completed", completed_count, "✅")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        approved_count = len([r for r in user_requests if safe_get(r, 'status') == 'Approved'])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Approved", approved_count, "👍")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent requests in a beautiful table
    st.markdown("<div class='section-header'>📋 Recent Requests</div>", unsafe_allow_html=True)
    
    if user_requests:
        display_data = []
        for req in user_requests[:10]:
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
            
            display_data.append({
                'ID': safe_get(req, 'id'),
                'Title': safe_str(safe_get(req, 'title')),
                'Location': safe_str(safe_get(req, 'location'), 'Common Area'),
                'Priority': f"<span style='color:{priority_color}; font-weight:bold;'>{priority}</span>",
                'Status': f"{status_icon} {status}",
                'Created': safe_str(safe_get(req, 'created_date'))[:10]
            })
        
        df = pd.DataFrame(display_data)
        st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.info("📭 No maintenance requests found")

def show_manager_dashboard():
    all_requests = execute_query('SELECT * FROM maintenance_requests ORDER BY created_date DESC')
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Total Requests", len(all_requests), "📊")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        pending_count = len([r for r in all_requests if safe_get(r, 'status') == 'Pending'])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Pending", pending_count, "⏳")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        assigned_count = len([r for r in all_requests if safe_get(r, 'status') == 'Assigned'])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Assigned", assigned_count, "👷")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        completed_count = len([r for r in all_requests if safe_get(r, 'status') == 'Completed'])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Completed", completed_count, "✅")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts in columns
    if all_requests:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h4>📈 Status Distribution</h4>", unsafe_allow_html=True)
            status_counts = {}
            for req in all_requests:
                status = safe_str(safe_get(req, 'status'), 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            if status_counts:
                fig = px.pie(values=list(status_counts.values()), names=list(status_counts.keys()),
                            color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h4>📊 Priority Distribution</h4>", unsafe_allow_html=True)
            priority_counts = {}
            for req in all_requests:
                priority = safe_str(safe_get(req, 'priority'), 'Unknown')
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            if priority_counts:
                fig = px.bar(x=list(priority_counts.keys()), y=list(priority_counts.values()),
                            labels={'x': 'Priority', 'y': 'Count'},
                            color=list(priority_counts.keys()),
                            color_discrete_map={'Low': '#10b981', 'Medium': '#f59e0b', 
                                              'High': '#ef4444', 'Critical': '#dc2626'})
                st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

def show_vendor_dashboard():
    vendor_requests = execute_query(
        'SELECT * FROM maintenance_requests WHERE assigned_vendor = ? ORDER BY created_date DESC',
        (st.session_state.user['username'],)
    )
    
    # Stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        assigned_count = len([r for r in vendor_requests if safe_get(r, 'status') == 'Assigned'])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Assigned Jobs", assigned_count, "🔧")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        completed_count = len([r for r in vendor_requests if safe_get(r, 'status') == 'Completed'])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Completed Jobs", completed_count, "✅")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        total_invoice_amount = sum([safe_float(r.get('invoice_amount', 0)) for r in vendor_requests])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Total Revenue", format_ngn(total_invoice_amount), "💰")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Assigned jobs
    st.markdown("<div class='section-header'>🔧 Currently Assigned Jobs</div>", unsafe_allow_html=True)
    assigned_jobs = [r for r in vendor_requests if safe_get(r, 'status') == 'Assigned']
    
    if assigned_jobs:
        for job in assigned_jobs:
            with st.expander(f"Job #{safe_get(job, 'id')}: {safe_str(safe_get(job, 'title'))}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Location:** {safe_str(safe_get(job, 'location'), 'Common Area')}")
                    st.write(f"**Priority:** {safe_str(safe_get(job, 'priority'))}")
                    st.write(f"**Created:** {safe_str(safe_get(job, 'created_date'))}")
                with col2:
                    st.write(f"**Description:** {safe_str(safe_get(job, 'description'))}")
    else:
        st.info("🎉 No currently assigned jobs")

def show_job_invoice_reports():
    """FIXED: Job & Invoice Reports section with corrected SQL"""
    st.markdown("<h1 class='app-title'>📄 Job & Invoice Reports</h1>", unsafe_allow_html=True)
    
    # CORRECTED SQL QUERY - using proper table aliases and only existing columns
    completed_jobs = execute_query('''
        SELECT mr.*, i.invoice_number, i.invoice_date, i.total_amount, i.status as invoice_status
        FROM maintenance_requests mr
        LEFT JOIN invoices i ON mr.id = i.request_id
        WHERE mr.status IN ('Completed', 'Approved')
        ORDER BY mr.completed_date DESC
    ''')
    
    if not completed_jobs:
        st.info("📭 No completed jobs with invoices found")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_options = ["All"] + sorted(list(set(safe_str(safe_get(job, 'status')) for job in completed_jobs)))
        status_filter = st.selectbox("Filter by Job Status", status_options)
    with col2:
        location_options = ["All"] + sorted(list(set(safe_str(safe_get(job, 'location'), 'Common Area') for job in completed_jobs)))
        location_filter = st.selectbox("Filter by Location", location_options)
    with col3:
        invoice_options = ["All", "With Invoice", "Without Invoice"]
        invoice_filter = st.selectbox("Filter by Invoice Status", invoice_options)
    
    # Apply filters
    filtered_jobs = completed_jobs
    if status_filter != "All":
        filtered_jobs = [job for job in filtered_jobs if safe_str(safe_get(job, 'status')) == status_filter]
    if location_filter != "All":
        filtered_jobs = [job for job in filtered_jobs if safe_str(safe_get(job, 'location'), 'Common Area') == location_filter]
    if invoice_filter == "With Invoice":
        filtered_jobs = [job for job in filtered_jobs if safe_get(job, 'invoice_number') is not None]
    elif invoice_filter == "Without Invoice":
        filtered_jobs = [job for job in filtered_jobs if safe_get(job, 'invoice_number') is None]
    
    st.markdown(f"<div class='card'><h4>Found {len(filtered_jobs)} job(s)</h4></div>", unsafe_allow_html=True)
    
    # Enhanced job display with PDF download
    for job in filtered_jobs:
        job_id = safe_get(job, 'id')
        job_title = safe_str(safe_get(job, 'title'))
        location = safe_str(safe_get(job, 'location'), 'Common Area')
        status = safe_str(safe_get(job, 'status'))
        
        with st.expander(f"📋 Job #{job_id}: {job_title} | 📍 {location} | 🏷️ {status}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📝 Job Details")
                st.write(f"**Title:** {job_title}")
                st.write(f"**Location:** {location}")
                st.write(f"**Facility Type:** {safe_str(safe_get(job, 'facility_type'))}")
                st.write(f"**Priority:** {safe_str(safe_get(job, 'priority'))}")
                st.write(f"**Status:** {status}")
                st.write(f"**Created By:** {safe_str(safe_get(job, 'created_by'))}")
                st.write(f"**Assigned Vendor:** {safe_str(safe_get(job, 'assigned_vendor'), 'Not assigned')}")
                
                if safe_get(job, 'job_breakdown'):
                    with st.expander("View Job Breakdown"):
                        st.write(safe_str(safe_get(job, 'job_breakdown')))
            
            with col2:
                st.markdown("### 🧾 Invoice Details")
                invoice_number = safe_get(job, 'invoice_number')
                
                if invoice_number:
                    st.success(f"**Invoice Number:** {invoice_number}")
                    st.write(f"**Invoice Date:** {safe_str(safe_get(job, 'invoice_date'))}")
                    st.write(f"**Invoice Amount:** {format_ngn(safe_get(job, 'total_amount'))}")
                    st.write(f"**Invoice Status:** {safe_str(safe_get(job, 'invoice_status'), 'N/A')}")
                    
                    # Get detailed invoice information
                    invoice_details = execute_query(
                        'SELECT * FROM invoices WHERE invoice_number = ?', 
                        (invoice_number,)
                    )
                    
                    if invoice_details:
                        invoice = invoice_details[0]
                        with st.expander("📊 View Detailed Invoice"):
                            st.write(f"**Details of Work:** {safe_str(safe_get(invoice, 'details_of_work'))}")
                            st.write(f"**Quantity:** {safe_str(safe_get(invoice, 'quantity'))}")
                            st.write(f"**Unit Cost:** {format_ngn(safe_get(invoice, 'unit_cost'))}")
                            st.write(f"**Amount:** {format_ngn(safe_get(invoice, 'amount'))}")
                            st.write(f"**Labour Charge:** {format_ngn(safe_get(invoice, 'labour_charge'))}")
                            st.write(f"**VAT Applied:** {'✅ Yes (7.5%)' if safe_get(invoice, 'vat_applicable') else '❌ No'}")
                            st.write(f"**VAT Amount:** {format_ngn(safe_get(invoice, 'vat_amount'))}")
                            st.write(f"**Total Amount:** {format_ngn(safe_get(invoice, 'total_amount'))}")
                else:
                    st.warning("No invoice created yet")
                
                st.markdown("### ✅ Approval Status")
                col_a, col_b = st.columns(2)
                with col_a:
                    dept_approval = safe_get(job, 'requesting_dept_approval')
                    st.write(f"**Department:** {'✅ Approved' if dept_approval else '⏳ Pending'}")
                with col_b:
                    manager_approval = safe_get(job, 'facilities_manager_approval')
                    st.write(f"**Manager:** {'✅ Approved' if manager_approval else '⏳ Pending'}")
            
            # PDF Generation Button
            if invoice_number and invoice_details:
                st.markdown("---")
                col1, col2, col3 = st.columns([2, 1, 1])
                with col2:
                    if st.button(f"📄 Generate PDF Report", key=f"pdf_{job_id}", use_container_width=True):
                        with st.spinner("Generating PDF report..."):
                            pdf_buffer = generate_job_invoice_pdf(job, invoice_details[0])
                            st.success("PDF generated successfully!")
                            
                            # Download button
                            st.download_button(
                                label="⬇️ Download PDF Report",
                                data=pdf_buffer.getvalue(),
                                file_name=f"Job_Report_{job_id}_{invoice_number}.pdf",
                                mime="application/pdf",
                                key=f"download_{job_id}"
                            )
                with col3:
                    # Quick preview button
                    if st.button("👁️ Preview PDF", key=f"preview_{job_id}", use_container_width=True):
                        pdf_buffer = generate_job_invoice_pdf(job, invoice_details[0])
                        base64_pdf = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
                        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
                        st.markdown(pdf_display, unsafe_allow_html=True)

# =============================================
# ADDITIONAL ENHANCED FUNCTIONS
# =============================================
def show_vendor_reports():
    """Vendor-specific reports"""
    st.markdown("<h1 class='app-title'>📊 My Vendor Reports</h1>", unsafe_allow_html=True)
    
    vendor_username = st.session_state.user['username']
    
    # Get vendor jobs
    vendor_jobs = execute_query(
        'SELECT * FROM maintenance_requests WHERE assigned_vendor = ? ORDER BY completed_date DESC',
        (vendor_username,)
    )
    
    if not vendor_jobs:
        st.info("📭 No jobs found for your vendor account")
        return
    
    # Stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_jobs = len(vendor_jobs)
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Total Jobs", total_jobs, "📋")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        completed_jobs = len([j for j in vendor_jobs if safe_get(j, 'status') == 'Completed'])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Completed", completed_jobs, "✅")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        total_revenue = sum([safe_float(j.get('invoice_amount', 0)) for j in vendor_jobs])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Total Revenue", format_ngn(total_revenue), "💰")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Charts
    if vendor_jobs:
        col1, col2 = st.columns(2)
        
        with col1:
            # Monthly revenue chart
            monthly_data = {}
            for job in vendor_jobs:
                if safe_get(job, 'completed_date'):
                    month = safe_str(safe_get(job, 'completed_date'))[:7]
                    amount = safe_float(safe_get(job, 'invoice_amount', 0))
                    monthly_data[month] = monthly_data.get(month, 0) + amount
            
            if monthly_data:
                df_monthly = pd.DataFrame({
                    'Month': list(monthly_data.keys()),
                    'Revenue': list(monthly_data.values())
                })
                fig = px.line(df_monthly, x='Month', y='Revenue', 
                            title="Monthly Revenue Trend (NGN)", markers=True)
                st.plotly_chart(fig, use_container_width=True)

# =============================================
# MAIN APPLICATION
# =============================================
def main():
    # Initialize session state
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    # Show appropriate page
    if st.session_state.user is None:
        show_enhanced_login()
    else:
        show_main_app()

# Note: You need to add the other functions (show_create_request, show_my_requests, etc.)
# with the same enhanced UI patterns. For brevity, I've focused on the critical fixes
# and main enhancements. The other functions should follow the same pattern.

if __name__ == "__main__":
    main()
