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
    
    /* Invoice table styling */
    .invoice-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
    }
    
    .invoice-table th {
        background-color: #1e3a8a;
        color: white;
        padding: 10px;
        text-align: left;
    }
    
    .invoice-table td {
        padding: 10px;
        border-bottom: 1px solid #ddd;
    }
    
    .invoice-table tr:hover {
        background-color: #f5f5f5;
    }
    
    /* Fix for tab overflow */
    .stTabs {
        overflow-x: auto;
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
                invoice_date DATE NOT NULL DEFAULT CURRENT_DATE,
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
                user_approved INTEGER DEFAULT 0,
                manager_approved INTEGER DEFAULT 0
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
        
        # Get column names
        columns = [column[0] for column in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
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
        print(f"Query: {query}")
        print(f"Params: {params}")
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
        print(f"Query: {query}")
        print(f"Params: {params}")
        return False

# =============================================
# SAFE DATA ACCESS FUNCTIONS
# =============================================
def safe_get(data, key, default=None):
    if not data or key not in data:
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

def safe_date(value, default=None):
    """Safely convert value to datetime"""
    try:
        if value is None or value == '':
            return default
        if isinstance(value, datetime):
            return value
        if isinstance(value, pd.Timestamp):
            return value.to_pydatetime()
        if isinstance(value, str):
            # Try multiple date formats
            formats = ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y', '%m/%d/%Y']
            for fmt in formats:
                try:
                    return datetime.strptime(value, fmt)
                except:
                    continue
        return default
    except:
        return default

# =============================================
# PDF REPORT GENERATION FUNCTIONS
# =============================================
def create_maintenance_pdf_report(request_id):
    """Create PDF report for maintenance job completion"""
    buffer = io.BytesIO()
    
    # Get request details
    request = execute_query('SELECT * FROM maintenance_requests WHERE id = ?', (request_id,))
    if not request:
        return None
    request = request[0]
    
    # Get invoice details if exists
    invoice = execute_query('SELECT * FROM invoices WHERE request_id = ?', (request_id,))
    
    # Create PDF
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, 
                           topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#1e3a8a')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.HexColor('#3b82f6')
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    # Story container for PDF elements
    story = []
    
    # Title
    story.append(Paragraph("MAINTENANCE JOB COMPLETION REPORT", title_style))
    story.append(Spacer(1, 20))
    
    # Job Details
    story.append(Paragraph("Job Details", heading_style))
    
    job_data = [
        ["Job ID:", str(safe_get(request, 'id', ''))],
        ["Title:", safe_str(safe_get(request, 'title', ''))],
        ["Location:", safe_str(safe_get(request, 'location', 'N/A'))],
        ["Facility Type:", safe_str(safe_get(request, 'facility_type', ''))],
        ["Priority:", safe_str(safe_get(request, 'priority', ''))],
        ["Created By:", safe_str(safe_get(request, 'created_by', ''))],
        ["Created Date:", safe_str(safe_get(request, 'created_date', ''))],
        ["Assigned Vendor:", safe_str(safe_get(request, 'assigned_vendor', 'N/A'))],
        ["Status:", safe_str(safe_get(request, 'status', ''))],
        ["Completed Date:", safe_str(safe_get(request, 'completed_date', 'N/A'))]
    ]
    
    job_table = Table(job_data, colWidths=[2*inch, 4*inch])
    job_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    
    story.append(job_table)
    story.append(Spacer(1, 20))
    
    # Description
    story.append(Paragraph("Job Description", heading_style))
    story.append(Paragraph(safe_str(safe_get(request, 'description', '')), normal_style))
    story.append(Spacer(1, 20))
    
    # Completion Notes
    if safe_get(request, 'completion_notes'):
        story.append(Paragraph("Completion Notes", heading_style))
        story.append(Paragraph(safe_str(safe_get(request, 'completion_notes', '')), normal_style))
        story.append(Spacer(1, 20))
    
    # Job Breakdown
    if safe_get(request, 'job_breakdown'):
        story.append(Paragraph("Job Breakdown", heading_style))
        story.append(Paragraph(safe_str(safe_get(request, 'job_breakdown', '')), normal_style))
        story.append(Spacer(1, 20))
    
    # Invoice Details
    if invoice:
        invoice = invoice[0]
        story.append(Paragraph("Invoice Details", heading_style))
        
        invoice_data = [
            ["Invoice Number:", safe_str(safe_get(invoice, 'invoice_number', ''))],
            ["Invoice Date:", safe_str(safe_get(invoice, 'invoice_date', ''))],
            ["Details of Work:", safe_str(safe_get(invoice, 'details_of_work', ''))],
            ["Quantity:", str(safe_int(safe_get(invoice, 'quantity', 0)))],
            ["Unit Cost:", format_ngn(safe_float(safe_get(invoice, 'unit_cost', 0)))],
            ["Material Cost:", format_ngn(safe_float(safe_get(invoice, 'amount', 0)))],
            ["Labour Charges:", format_ngn(safe_float(safe_get(invoice, 'labour_charge', 0)))],
            ["VAT Amount:", format_ngn(safe_float(safe_get(invoice, 'vat_amount', 0)))],
            ["Total Amount:", format_ngn(safe_float(safe_get(invoice, 'total_amount', 0)))],
            ["Invoice Status:", safe_str(safe_get(invoice, 'status', ''))]
        ]
        
        invoice_table = Table(invoice_data, colWidths=[2*inch, 4*inch])
        invoice_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        
        story.append(invoice_table)
        story.append(Spacer(1, 20))
    
    # Approval Status
    story.append(Paragraph("Approval Status", heading_style))
    
    approval_data = [
        ["Department Approval:", "Approved" if safe_bool(safe_get(request, 'requesting_dept_approval')) else "Pending"],
        ["Department Approval Date:", safe_str(safe_get(request, 'department_approval_date', 'N/A'))],
        ["Manager Approval:", "Approved" if safe_bool(safe_get(request, 'facilities_manager_approval')) else "Pending"],
        ["Manager Approval Date:", safe_str(safe_get(request, 'manager_approval_date', 'N/A'))]
    ]
    
    approval_table = Table(approval_data, colWidths=[2*inch, 4*inch])
    approval_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    
    story.append(approval_table)
    
    # Footer
    story.append(Spacer(1, 40))
    story.append(Paragraph(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    story.append(Paragraph("A-Z Facilities Management Pro APP™", normal_style))
    
    # Build PDF
    doc.build(story)
    
    buffer.seek(0)
    return buffer

def create_ppm_pdf_report(schedule_id):
    """Create PDF report for PPM completion"""
    buffer = io.BytesIO()
    
    # Get schedule details
    schedule = execute_query('SELECT * FROM ppm_schedules WHERE id = ?', (schedule_id,))
    if not schedule:
        return None
    schedule = schedule[0]
    
    # Get assignment details
    assignment = execute_query('SELECT * FROM ppm_assignments WHERE schedule_id = ?', (schedule_id,))
    
    # Create PDF
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#1e3a8a')
    )
    
    story = []
    
    # Title
    story.append(Paragraph("PPM COMPLETION REPORT", title_style))
    story.append(Spacer(1, 20))
    
    # Schedule Details
    story.append(Paragraph("PPM Schedule Details", styles['Heading2']))
    
    schedule_data = [
        ["Schedule ID:", str(safe_get(schedule, 'id', ''))],
        ["Schedule Name:", safe_str(safe_get(schedule, 'schedule_name', ''))],
        ["Facility Category:", safe_str(safe_get(schedule, 'facility_category', ''))],
        ["Sub-Category:", safe_str(safe_get(schedule, 'sub_category', ''))],
        ["Frequency:", safe_str(safe_get(schedule, 'frequency', ''))],
        ["Next Maintenance Date:", safe_str(safe_get(schedule, 'next_maintenance_date', ''))],
        ["Status:", safe_str(safe_get(schedule, 'status', ''))],
        ["Assigned Vendor:", safe_str(safe_get(schedule, 'assigned_vendor', 'N/A'))],
        ["Created By:", safe_str(safe_get(schedule, 'created_by', ''))],
        ["Estimated Cost:", format_ngn(safe_float(safe_get(schedule, 'estimated_cost', 0)))],
        ["Actual Completion Date:", safe_str(safe_get(schedule, 'actual_completion_date', 'N/A'))],
        ["Actual Cost:", format_ngn(safe_float(safe_get(schedule, 'actual_cost', 0))) if safe_get(schedule, 'actual_cost') else "N/A"]
    ]
    
    schedule_table = Table(schedule_data, colWidths=[2*inch, 4*inch])
    schedule_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    
    story.append(schedule_table)
    story.append(Spacer(1, 20))
    
    # Description
    story.append(Paragraph("Description", styles['Heading2']))
    story.append(Paragraph(safe_str(safe_get(schedule, 'description', '')), styles['Normal']))
    
    # Notes
    if safe_get(schedule, 'notes'):
        story.append(Spacer(1, 10))
        story.append(Paragraph("Notes", styles['Heading2']))
        story.append(Paragraph(safe_str(safe_get(schedule, 'notes', '')), styles['Normal']))
    
    # Assignment Details
    if assignment:
        assignment = assignment[0]
        story.append(Spacer(1, 20))
        story.append(Paragraph("Assignment Details", styles['Heading2']))
        
        assign_data = [
            ["Assigned To:", safe_str(safe_get(assignment, 'vendor_username', ''))],
            ["Assigned Date:", safe_str(safe_get(assignment, 'assigned_date', ''))],
            ["Due Date:", safe_str(safe_get(assignment, 'due_date', ''))],
            ["Completed Date:", safe_str(safe_get(assignment, 'completed_date', 'N/A'))],
            ["Status:", safe_str(safe_get(assignment, 'status', ''))]
        ]
        
        assign_table = Table(assign_data, colWidths=[2*inch, 4*inch])
        story.append(assign_table)
        
        if safe_get(assignment, 'completion_notes'):
            story.append(Spacer(1, 10))
            story.append(Paragraph("Completion Notes", styles['Heading2']))
            story.append(Paragraph(safe_str(safe_get(assignment, 'completion_notes', '')), styles['Normal']))
    
    # Approval Status
    story.append(Spacer(1, 20))
    story.append(Paragraph("Approval Status", styles['Heading2']))
    
    approval_data = [
        ["User Approved:", "Yes" if safe_bool(safe_get(schedule, 'user_approved')) else "No"],
        ["Manager Approved:", "Yes" if safe_bool(safe_get(schedule, 'manager_approved')) else "No"]
    ]
    
    approval_table = Table(approval_data, colWidths=[2*inch, 4*inch])
    story.append(approval_table)
    
    # Footer
    story.append(Spacer(1, 40))
    story.append(Paragraph(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Paragraph("A-Z Facilities Management Pro APP™", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def create_invoice_pdf(invoice_id):
    """Create PDF invoice"""
    buffer = io.BytesIO()
    
    # Get invoice details
    invoice = execute_query('SELECT * FROM invoices WHERE id = ?', (invoice_id,))
    if not invoice:
        return None
    invoice = invoice[0]
    
    # Get request details
    request = execute_query('SELECT * FROM maintenance_requests WHERE id = ?', (invoice['request_id'],))
    
    # Create PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Header
    story.append(Paragraph("INVOICE", styles['Title']))
    story.append(Spacer(1, 20))
    
    # Invoice Details
    story.append(Paragraph("Invoice Details", styles['Heading2']))
    
    invoice_details = [
        ["Invoice Number:", safe_str(safe_get(invoice, 'invoice_number', ''))],
        ["Invoice Date:", safe_str(safe_get(invoice, 'invoice_date', ''))],
        ["Vendor:", safe_str(safe_get(invoice, 'vendor_username', ''))],
        ["Status:", safe_str(safe_get(invoice, 'status', ''))]
    ]
    
    if request:
        request = request[0]
        invoice_details.append(["Job Title:", safe_str(safe_get(request, 'title', ''))])
        invoice_details.append(["Location:", safe_str(safe_get(request, 'location', 'N/A'))])
    
    inv_table = Table(invoice_details, colWidths=[2*inch, 4*inch])
    story.append(inv_table)
    story.append(Spacer(1, 20))
    
    # Work Details
    story.append(Paragraph("Work Details", styles['Heading2']))
    story.append(Paragraph(safe_str(safe_get(invoice, 'details_of_work', '')), styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Cost Breakdown
    story.append(Paragraph("Cost Breakdown", styles['Heading2']))
    
    amount = safe_float(safe_get(invoice, 'amount', 0))
    labour_charge = safe_float(safe_get(invoice, 'labour_charge', 0))
    vat_amount = safe_float(safe_get(invoice, 'vat_amount', 0))
    total_amount = safe_float(safe_get(invoice, 'total_amount', 0))
    
    cost_data = [
        ["Description", "Quantity", "Unit Cost", "Amount"],
        ["Materials", str(safe_int(safe_get(invoice, 'quantity', 0))), format_ngn(safe_float(safe_get(invoice, 'unit_cost', 0))), format_ngn(amount)],
        ["Labour Charges", "1", format_ngn(labour_charge), format_ngn(labour_charge)],
        ["Subtotal", "", "", format_ngn(amount + labour_charge)],
        ["VAT (7.5%)" if safe_bool(safe_get(invoice, 'vat_applicable')) else "VAT", "", "", format_ngn(vat_amount)],
        ["TOTAL", "", "", format_ngn(total_amount)]
    ]
    
    cost_table = Table(cost_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    cost_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f1f5f9')),
    ]))
    
    story.append(cost_table)
    
    # Footer
    story.append(Spacer(1, 40))
    story.append(Paragraph("Thank you for your business!", styles['Normal']))
    story.append(Paragraph("A-Z Facilities Management Pro APP™", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def get_pdf_download_link(pdf_buffer, filename):
    """Generate download link for PDF"""
    b64 = base64.b64encode(pdf_buffer.getvalue()).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="{filename}" class="pdf-download-btn">📥 Download {filename}</a>'

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

def get_ppm_for_user_approval(username):
    """Get PPM schedules created by user that need approval"""
    return execute_query('''
        SELECT * FROM ppm_schedules 
        WHERE created_by = ? 
        AND status = 'Completed' 
        AND user_approved = 0
        ORDER BY actual_completion_date DESC
    ''', (username,))

def get_requests_for_manager_approval():
    return execute_query('''
        SELECT * FROM maintenance_requests 
        WHERE status = 'Completed' 
        AND requesting_dept_approval = 1
        AND facilities_manager_approval = 0
        ORDER BY department_approval_date DESC
    ''')

def get_ppm_for_manager_approval():
    """Get PPM schedules that need manager approval"""
    return execute_query('''
        SELECT * FROM ppm_schedules 
        WHERE status = 'Completed' 
        AND user_approved = 1
        AND manager_approved = 0
        ORDER BY actual_completion_date DESC
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
# PPM MANAGEMENT - FACILITY USER
# =============================================
def show_ppm_management_facility_user():
    st.markdown("<h1 class='app-title'>📅 Planned Preventive Maintenance</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 PPM Schedules", "➕ New Schedule", "📊 PPM Analytics", "✅ PPM Approvals"])
    
    with tab1:
        show_ppm_schedules()
    
    with tab2:
        show_new_ppm_schedule()
    
    with tab3:
        show_ppm_analytics()
    
    with tab4:
        show_ppm_approvals_facility_user()

def show_ppm_schedules():
    st.markdown("### 📋 PPM Schedules Overview")
    
    # Initialize session state for PPM filter if not exists
    if 'ppm_filter' not in st.session_state:
        st.session_state.ppm_filter = "All"
    
    # Status filter buttons
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("All", use_container_width=True, type="primary" if st.session_state.ppm_filter == "All" else "secondary"):
            st.session_state.ppm_filter = "All"
            st.rerun()
    with col2:
        if st.button("Not Due", use_container_width=True, type="primary" if st.session_state.ppm_filter == "Not Due" else "secondary"):
            st.session_state.ppm_filter = "Not Due"
            st.rerun()
    with col3:
        if st.button("Prepare", use_container_width=True, type="primary" if st.session_state.ppm_filter == "Prepare" else "secondary"):
            st.session_state.ppm_filter = "Prepare"
            st.rerun()
    with col4:
        if st.button("Due", use_container_width=True, type="primary" if st.session_state.ppm_filter == "Due" else "secondary"):
            st.session_state.ppm_filter = "Due"
            st.rerun()
    with col5:
        if st.button("Completed", use_container_width=True, type="primary" if st.session_state.ppm_filter == "Completed" else "secondary"):
            st.session_state.ppm_filter = "Completed"
            st.rerun()
    
    # Get filter from session state
    ppm_filter = st.session_state.get('ppm_filter', 'All')
    
    # Build query based on filter
    query = "SELECT * FROM ppm_schedules WHERE created_by = ?"
    params = [st.session_state.user['username']]
    
    if ppm_filter != "All":
        query += " AND status = ?"
        params.append(ppm_filter)
    
    query += " ORDER BY next_maintenance_date"
    
    schedules = execute_query(query, tuple(params))
    
    if schedules:
        for schedule in schedules:
            # Determine status color
            status_colors = {
                "Not Due": "status-not-due",
                "Prepare": "status-prepare",
                "Due": "status-due",
                "Completed": "status-completed",
                "WIP": "status-wip",
                "Approved": "status-approved"
            }
            
            status_class = status_colors.get(safe_get(schedule, 'status', ''), "")
            
            with st.expander(f"{safe_get(schedule, 'schedule_name', '')} - {safe_get(schedule, 'next_maintenance_date', '')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Facility:** {safe_get(schedule, 'facility_category', '')}")
                    st.write(f"**Sub-Category:** {safe_get(schedule, 'sub_category', '')}")
                    st.write(f"**Frequency:** {safe_get(schedule, 'frequency', '')}")
                    st.write(f"**Assigned Vendor:** {safe_get(schedule, 'assigned_vendor', 'Not assigned')}")
                
                with col2:
                    st.write(f"**Status:** <span class='{status_class}'>{safe_get(schedule, 'status', '')}</span>", unsafe_allow_html=True)
                    st.write(f"**Created By:** {safe_get(schedule, 'created_by', '')}")
                    st.write(f"**Created Date:** {safe_get(schedule, 'created_date', '')}")
                    if safe_get(schedule, 'estimated_cost'):
                        st.write(f"**Est. Cost:** {format_ngn(safe_get(schedule, 'estimated_cost', 0))}")
                
                st.write(f"**Description:** {safe_get(schedule, 'description', '')}")
                
                if safe_get(schedule, 'notes'):
                    st.write(f"**Notes:** {safe_get(schedule, 'notes', '')}")
                
                # Action buttons based on status
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if safe_get(schedule, 'status') == 'Not Due' and st.button("🔄 Mark as Prepare", key=f"prep_{schedule['id']}"):
                        execute_update(
                            "UPDATE ppm_schedules SET status = 'Prepare' WHERE id = ?",
                            (schedule['id'],)
                        )
                        st.success("✅ Status updated to Prepare")
                        st.rerun()
                
                with col2:
                    if safe_get(schedule, 'status') in ['Prepare', 'Due'] and st.button("⚡ Assign to Vendor", key=f"assign_{schedule['id']}"):
                        # Show vendor selection modal
                        show_assign_vendor_modal(schedule['id'], schedule['facility_category'])
                        st.rerun()
                
                with col3:
                    if safe_get(schedule, 'status') == 'Completed' and safe_get(schedule, 'user_approved', 0) == 0:
                        if st.button("✅ Approve PPM", key=f"approve_ppm_{schedule['id']}"):
                            execute_update(
                                "UPDATE ppm_schedules SET user_approved = 1 WHERE id = ?",
                                (schedule['id'],)
                            )
                            st.success("✅ PPM approved!")
                            st.rerun()
                    
                    # PDF Download for completed PPM
                    if safe_get(schedule, 'status') == 'Completed':
                        pdf_buffer = create_ppm_pdf_report(schedule['id'])
                        if pdf_buffer:
                            st.download_button(
                                label="📥 Download PPM Report",
                                data=pdf_buffer,
                                file_name=f"ppm_report_{schedule['id']}_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf",
                                key=f"ppm_pdf_{schedule['id']}"
                            )
    else:
        st.info("📭 No PPM schedules found")

def show_assign_vendor_modal(schedule_id, facility_category):
    """Show modal for assigning vendor to PPM schedule"""
    st.markdown("---")
    st.markdown("### 👷 Assign to Vendor")
    
    # Get vendors for this facility category
    vendors = execute_query(
        'SELECT * FROM vendors WHERE vendor_type = ? OR vendor_type LIKE ?',
        (facility_category, f'%{facility_category}%')
    )
    
    if not vendors:
        st.warning(f"No vendors found for facility category: {facility_category}")
        return
    
    vendor_options = {f"{v['company_name']} ({v['username']})": v['username'] for v in vendors}
    selected_vendor_name = st.selectbox("Select Vendor", list(vendor_options.keys()))
    
    due_date = st.date_input("Due Date", value=datetime.now() + timedelta(days=7))
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Assign Vendor", use_container_width=True):
            vendor_username = vendor_options[selected_vendor_name]
            
            # Update PPM schedule
            execute_update(
                '''UPDATE ppm_schedules 
                SET assigned_vendor = ?, status = 'WIP' 
                WHERE id = ?''',
                (vendor_username, schedule_id)
            )
            
            # Create assignment record
            execute_update(
                '''INSERT INTO ppm_assignments 
                (schedule_id, vendor_username, assigned_date, due_date, assigned_by) 
                VALUES (?, ?, ?, ?, ?)''',
                (schedule_id, vendor_username, 
                 datetime.now().strftime('%Y-%m-%d'),
                 due_date.strftime('%Y-%m-%d'),
                 st.session_state.user['username'])
            )
            
            st.success("✅ PPM assigned to vendor successfully!")
            st.rerun()
    
    with col2:
        if st.button("❌ Cancel", use_container_width=True, type="secondary"):
            st.rerun()

def show_new_ppm_schedule():
    st.markdown("### ➕ Create New PPM Schedule")
    
    with st.form("new_ppm_schedule_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            schedule_name = st.text_input("Schedule Name *", placeholder="e.g., Monthly AC Maintenance")
            facility_category = st.selectbox(
                "Facility Category *",
                ["HVAC", "Electrical", "Plumbing", "Generator", "Fire Safety", 
                 "Elevator", "Building Structure", "Cleaning", "Security", "Other"]
            )
            sub_category = st.text_input("Sub-Category", placeholder="e.g., Split Units, Chillers")
            frequency = st.selectbox(
                "Frequency *",
                ["Daily", "Weekly", "Monthly", "Quarterly", "Bi-annual", "Annual", "Custom"]
            )
        
        with col2:
            next_maintenance_date = st.date_input("Next Maintenance Date *", 
                                                  value=datetime.now() + timedelta(days=30))
            estimated_duration = st.number_input("Estimated Duration (hours)", 
                                                 min_value=1, value=2)
            estimated_cost = st.number_input("Estimated Cost (₦)", 
                                            min_value=0.0, value=0.0, step=1000.0)
            assigned_vendor = st.selectbox(
                "Assign to Vendor (Optional)",
                ["", "hvac_vendor", "generator_vendor", "electrical_vendor", 
                 "plumbing_vendor", "building_vendor"]
            )
        
        description = st.text_area("Description *", 
                                  placeholder="Detailed description of maintenance activities...",
                                  height=100)
        notes = st.text_area("Additional Notes", 
                            placeholder="Special instructions, requirements...",
                            height=80)
        
        submitted = st.form_submit_button("💾 Save PPM Schedule", use_container_width=True)
        
        if submitted:
            if not all([schedule_name, facility_category, frequency, description]):
                st.error("❌ Please fill in all required fields (*)")
            else:
                success = execute_update(
                    '''INSERT INTO ppm_schedules 
                    (schedule_name, facility_category, sub_category, frequency,
                     next_maintenance_date, estimated_duration_hours, estimated_cost,
                     assigned_vendor, description, notes, created_by) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (schedule_name, facility_category, sub_category, frequency,
                     next_maintenance_date.strftime('%Y-%m-%d'), estimated_duration,
                     estimated_cost, assigned_vendor if assigned_vendor else None,
                     description, notes, st.session_state.user['username'])
                )
                if success:
                    st.success("✅ PPM schedule created successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to create schedule")

def show_ppm_analytics():
    st.markdown("### 📊 PPM Analytics Dashboard")
    
    # Get all PPM schedules for this user
    schedules = execute_query("SELECT * FROM ppm_schedules WHERE created_by = ?", 
                             (st.session_state.user['username'],))
    
    if not schedules:
        st.info("📭 No PPM data available for analytics")
        return
    
    df = pd.DataFrame(schedules)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_ppm = len(df)
        create_metric_card("Total PPMs", total_ppm, "📅")
    
    with col2:
        due_ppm = len(df[df['status'] == 'Due'])
        create_metric_card("Due Now", due_ppm, "⚠️")
    
    with col3:
        completed_ppm = len(df[df['status'] == 'Completed'])
        completion_rate = (completed_ppm / total_ppm * 100) if total_ppm > 0 else 0
        create_metric_card("Completion Rate", f"{completion_rate:.1f}%", "✅")
    
    with col4:
        total_estimated_cost = df['estimated_cost'].sum()
        create_metric_card("Total Est. Cost", format_ngn(total_estimated_cost), "💰")
    
    st.divider()
    
    # Status distribution
    st.markdown("#### 📊 PPM Status Distribution")
    status_counts = df['status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    
    fig1 = px.pie(status_counts, values='Count', names='Status',
                  title="PPM by Status",
                  color='Status',
                  color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig1, use_container_width=True)
    
    # Monthly due schedule
    st.markdown("#### 📅 Monthly Due Schedule")
    df['next_maintenance_date'] = pd.to_datetime(df['next_maintenance_date'], errors='coerce')
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    monthly_ppm = df[(df['next_maintenance_date'].dt.month == current_month) & 
                     (df['next_maintenance_date'].dt.year == current_year)]
    
    if not monthly_ppm.empty:
        monthly_summary = monthly_ppm.groupby(['facility_category', 'status']).size().unstack(fill_value=0)
        
        fig2 = px.bar(monthly_summary, 
                      title=f"PPM Due for {calendar.month_name[current_month]} {current_year}",
                      labels={'value': 'Count', 'facility_category': 'Facility Category'},
                      barmode='group')
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info(f"📭 No PPM scheduled for {calendar.month_name[current_month]} {current_year}")
    
    # Cost analysis by facility category
    st.markdown("#### 💰 Estimated Cost by Facility Category")
    cost_by_category = df.groupby('facility_category')['estimated_cost'].sum().reset_index()
    
    fig3 = px.bar(cost_by_category, x='facility_category', y='estimated_cost',
                  title="Estimated Cost Distribution",
                  labels={'estimated_cost': 'Estimated Cost (₦)', 'facility_category': 'Facility Category'})
    st.plotly_chart(fig3, use_container_width=True)

def show_ppm_approvals_facility_user():
    """Facility user approval for PPM completion"""
    st.markdown("### ✅ PPM Completion Approvals")
    
    # Get PPM schedules that need user approval
    ppm_schedules = get_ppm_for_user_approval(st.session_state.user['username'])
    
    if not ppm_schedules:
        st.info("📭 No PPM schedules awaiting your approval")
        return
    
    for schedule in ppm_schedules:
        with st.expander(f"📋 {safe_get(schedule, 'schedule_name', '')} - Completed: {safe_get(schedule, 'actual_completion_date', '')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Facility:** {safe_get(schedule, 'facility_category', '')}")
                st.write(f"**Sub-Category:** {safe_get(schedule, 'sub_category', '')}")
                st.write(f"**Frequency:** {safe_get(schedule, 'frequency', '')}")
                st.write(f"**Assigned Vendor:** {safe_get(schedule, 'assigned_vendor', '')}")
            
            with col2:
                st.write(f"**Estimated Cost:** {format_ngn(safe_get(schedule, 'estimated_cost', 0))}")
                st.write(f"**Actual Cost:** {format_ngn(safe_get(schedule, 'actual_cost', 0)) if safe_get(schedule, 'actual_cost') else 'N/A'}")
                st.write(f"**Completed Date:** {safe_get(schedule, 'actual_completion_date', '')}")
                st.write(f"**Status:** {safe_get(schedule, 'status', '')}")
            
            st.write(f"**Description:** {safe_get(schedule, 'description', '')}")
            
            if safe_get(schedule, 'notes'):
                st.write(f"**Notes:** {safe_get(schedule, 'notes', '')}")
            
            # Get assignment details
            assignment = execute_query(
                'SELECT * FROM ppm_assignments WHERE schedule_id = ?',
                (schedule['id'],)
            )
            
            if assignment:
                assignment = assignment[0]
                st.write(f"**Completion Notes:** {safe_get(assignment, 'completion_notes', '')}")
            
            # Approval buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Approve PPM", key=f"user_approve_ppm_{schedule['id']}", 
                           use_container_width=True):
                    execute_update(
                        "UPDATE ppm_schedules SET user_approved = 1 WHERE id = ?",
                        (schedule['id'],)
                    )
                    st.success("✅ PPM approved successfully!")
                    st.rerun()
            
            with col2:
                if st.button("❌ Request Revision", key=f"user_reject_ppm_{schedule['id']}", 
                           use_container_width=True, type="secondary"):
                    revision_reason = st.text_input(
                        "Revision Reason",
                        key=f"ppm_revision_{schedule['id']}",
                        placeholder="What needs to be revised?"
                    )
                    if revision_reason:
                        execute_update(
                            '''UPDATE ppm_schedules SET status = 'WIP' WHERE id = ?''',
                            (schedule['id'],)
                        )
                        execute_update(
                            '''UPDATE ppm_assignments SET status = 'In Progress', 
                            completion_notes = ? WHERE schedule_id = ?''',
                            (f"Revision requested: {revision_reason}", schedule['id'])
                        )
                        st.success("✅ Revision requested from vendor")
                        st.rerun()

# =============================================
# VENDOR DASHBOARD - ENHANCED
# =============================================
def show_vendor_dashboard():
    st.markdown("<h1 class='app-title'>👷‍♂️ Vendor Dashboard</h1>", unsafe_allow_html=True)
    
    user_info = st.session_state.user
    vendor_username = user_info['username']
    
    # Get vendor details
    vendor_details = execute_query(
        'SELECT * FROM vendors WHERE username = ?',
        (vendor_username,)
    )
    
    if vendor_details:
        vendor = vendor_details[0]
        
        # Display vendor info
        with st.expander("ℹ️ Vendor Information", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Company:** {vendor['company_name']}")
                st.write(f"**Contact:** {vendor['contact_person']}")
                st.write(f"**Email:** {vendor['email']}")
                st.write(f"**Phone:** {vendor['phone']}")
            with col2:
                st.write(f"**Vendor Type:** {vendor['vendor_type']}")
                st.write(f"**TIN:** {vendor['tax_identification_number']}")
                st.write(f"**RC Number:** {vendor['rc_number']}")
                st.write(f"**Registered:** {vendor['registration_date']}")
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        # Get statistics
        assigned_requests = execute_query(
            'SELECT COUNT(*) as count FROM maintenance_requests WHERE assigned_vendor = ?',
            (vendor_username,)
        )
        assigned_count = assigned_requests[0]['count'] if assigned_requests else 0
        
        completed_requests = execute_query(
            'SELECT COUNT(*) as count FROM maintenance_requests WHERE assigned_vendor = ? AND status = ?',
            (vendor_username, 'Completed')
        )
        completed_count = completed_requests[0]['count'] if completed_requests else 0
        
        pending_requests = execute_query(
            'SELECT COUNT(*) as count FROM maintenance_requests WHERE assigned_vendor = ? AND status = ?',
            (vendor_username, 'Assigned')
        )
        pending_count = pending_requests[0]['count'] if pending_requests else 0
        
        total_invoice_amount = execute_query(
            'SELECT SUM(total_amount) as total FROM invoices WHERE vendor_username = ? AND status = ?',
            (vendor_username, 'Approved')
        )
        total_amount = total_invoice_amount[0]['total'] if total_invoice_amount and total_invoice_amount[0]['total'] else 0
        
        with col1:
            create_metric_card("Assigned Jobs", assigned_count, "📋")
        with col2:
            create_metric_card("Completed", completed_count, "✅")
        with col3:
            create_metric_card("Pending", pending_count, "⏳")
        with col4:
            create_metric_card("Total Revenue", format_ngn(total_amount), "💰")
        
        # Tabs for different functionalities
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Assigned Jobs", "📤 Submit Invoice", "💼 PPM Assignments", "📊 Performance", "📝 Update Profile"])
        
        with tab1:
            show_vendor_assigned_jobs(vendor_username)
        
        with tab2:
            show_vendor_invoice_submission(vendor_username)
        
        with tab3:
            show_vendor_ppm_assignments(vendor_username)
        
        with tab4:
            show_vendor_performance(vendor_username)
        
        with tab5:
            show_vendor_profile_update(vendor, vendor_username)
    
    else:
        st.error("❌ Vendor details not found. Please contact administrator.")

def show_vendor_assigned_jobs(vendor_username):
    st.markdown("### 📋 Assigned Maintenance Jobs")
    
    # Get assigned jobs
    jobs = execute_query(
        'SELECT * FROM maintenance_requests WHERE assigned_vendor = ? ORDER BY created_date DESC',
        (vendor_username,)
    )
    
    if jobs:
        for job in jobs:
            status_color = {
                'Pending': '🟡',
                'Assigned': '🔵',
                'In Progress': '🟠',
                'Completed': '🟢',
                'Approved': '✅'
            }.get(job['status'], '⚪')
            
            with st.expander(f"{status_color} {job['title']} - Priority: {job['priority']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Location:** {job['location']}")
                    st.write(f"**Facility Type:** {job['facility_type']}")
                    st.write(f"**Created By:** {job['created_by']}")
                    st.write(f"**Created Date:** {job['created_date']}")
                with col2:
                    st.write(f"**Status:** {job['status']}")
                    st.write(f"**Priority:** {job['priority']}")
                    if job['completed_date']:
                        st.write(f"**Completed Date:** {job['completed_date']}")
                
                st.write(f"**Description:** {job['description']}")
                
                # Job breakdown if available
                if job['job_breakdown']:
                    st.write(f"**Job Breakdown:** {job['job_breakdown']}")
                
                # Actions based on status
                if job['status'] in ['Pending', 'Assigned', 'In Progress']:
                    st.markdown("---")
                    st.markdown("#### 🛠️ Job Actions")
                    
                    # If job is Pending, first need to accept it
                    if job['status'] == 'Pending':
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("✅ Accept Job", key=f"accept_{job['id']}", use_container_width=True):
                                success = execute_update(
                                    '''UPDATE maintenance_requests 
                                    SET status = 'Assigned' 
                                    WHERE id = ?''',
                                    (job['id'],)
                                )
                                if success:
                                    st.success("✅ Job accepted! You can now start working on it.")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to accept job")
                        
                        with col2:
                            if st.button("❌ Decline Job", key=f"decline_{job['id']}", use_container_width=True, type="secondary"):
                                decline_reason = st.text_input(
                                    "Decline Reason",
                                    key=f"decline_reason_{job['id']}",
                                    placeholder="Reason for declining..."
                                )
                                if decline_reason:
                                    success = execute_update(
                                        '''UPDATE maintenance_requests 
                                        SET status = 'Declined',
                                            completion_notes = ?
                                        WHERE id = ?''',
                                        (f"Declined by vendor: {decline_reason}", job['id'])
                                    )
                                    if success:
                                        st.success("✅ Job declined")
                                        st.rerun()
                    else:
                        # Job is already Assigned or In Progress, show update options
                        col1, col2 = st.columns(2)
                        with col1:
                            new_status = st.selectbox(
                                "Update Status",
                                ["In Progress", "Completed", "On Hold"],
                                key=f"status_{job['id']}"
                            )
                        
                        completion_notes = st.text_area(
                            "Completion Notes",
                            placeholder="Describe work done, parts used, materials, time spent, etc.",
                            key=f"notes_{job['id']}",
                            height=100
                        )
                        
                        # For Completed status, show invoice option
                        if new_status == 'Completed':
                            st.markdown("#### 📋 Job Completion Details")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                parts_used = st.text_area(
                                    "Parts Used",
                                    placeholder="List all parts used...",
                                    key=f"parts_{job['id']}",
                                    height=60
                                )
                            
                            with col2:
                                hours_worked = st.number_input(
                                    "Hours Worked",
                                    min_value=0.5,
                                    value=2.0,
                                    step=0.5,
                                    key=f"hours_{job['id']}"
                                )
                        
                        if st.button("💾 Update Job", key=f"update_{job['id']}", use_container_width=True):
                            if new_status == 'Completed' and not completion_notes:
                                st.error("❌ Please provide completion notes")
                            else:
                                update_query = '''
                                    UPDATE maintenance_requests 
                                    SET status = ?, completion_notes = ?
                                '''
                                params = [new_status, completion_notes]
                                
                                if new_status == 'Completed':
                                    update_query += ", completed_date = ?"
                                    params.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                                    
                                    # Add parts and hours to completion notes if provided
                                    if parts_used:
                                        params[-1] = f"{completion_notes}\n\nParts Used: {parts_used}\nHours Worked: {hours_worked}"
                                
                                update_query += " WHERE id = ?"
                                params.append(job['id'])
                                
                                success = execute_update(update_query, tuple(params))
                                if success:
                                    st.success("✅ Job updated successfully!")
                                    
                                    # If job is completed, show option to create invoice immediately
                                    if new_status == 'Completed':
                                        st.info("🎉 Job marked as completed! You can now submit an invoice in the '📤 Submit Invoice' tab.")
                                    
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to update job")
                
                # Show PDF download for completed jobs
                if job['status'] == 'Completed':
                    st.markdown("---")
                    st.markdown("#### 📄 Job Reports")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        pdf_buffer = create_maintenance_pdf_report(job['id'])
                        if pdf_buffer:
                            st.download_button(
                                label="📥 Download Job Report",
                                data=pdf_buffer,
                                file_name=f"job_report_{job['id']}_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf",
                                key=f"job_pdf_{job['id']}"
                            )
                    
                    with col2:
                        # Check if invoice already exists
                        existing_invoice = execute_query(
                            'SELECT * FROM invoices WHERE request_id = ?',
                            (job['id'],)
                        )
                        
                        if existing_invoice:
                            st.info("✅ Invoice already submitted")
                        else:
                            if st.button("📤 Create Invoice", key=f"create_invoice_{job['id']}", use_container_width=True):
                                st.session_state.selected_job_for_invoice = job['id']
                                st.rerun()
    else:
        st.info("📭 No jobs assigned to you yet")

def show_vendor_invoice_submission(vendor_username):
    st.markdown("### 📤 Submit Invoice")
    
    # Check if a specific job was selected for invoicing
    if 'selected_job_for_invoice' in st.session_state:
        selected_job_id = st.session_state.selected_job_for_invoice
        st.info(f"📋 Creating invoice for Job ID: {selected_job_id}")
        
        # Get job details
        job = execute_query('SELECT * FROM maintenance_requests WHERE id = ?', (selected_job_id,))
        if job:
            job = job[0]
            
            # Check if invoice already exists
            existing_invoice = execute_query(
                'SELECT * FROM invoices WHERE request_id = ?',
                (selected_job_id,)
            )
            
            if existing_invoice:
                st.warning("⚠️ An invoice already exists for this job.")
                st.session_state.selected_job_for_invoice = None
                st.rerun()
            else:
                show_invoice_form(vendor_username, selected_job_id, job)
                
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.selected_job_for_invoice = None
                    st.rerun()
        else:
            st.error("❌ Job not found")
            st.session_state.selected_job_for_invoice = None
            st.rerun()
    else:
        # Get completed jobs without invoices
        completed_jobs = execute_query('''
            SELECT * FROM maintenance_requests 
            WHERE assigned_vendor = ? 
            AND status = 'Completed'
            AND id NOT IN (SELECT request_id FROM invoices WHERE request_id IS NOT NULL)
            ORDER BY completed_date DESC
        ''', (vendor_username,))
        
        if not completed_jobs:
            st.info("📭 No completed jobs available for invoicing")
            return
        
        # Select job to invoice
        job_options = {f"{job['title']} (ID: {job['id']})": job['id'] for job in completed_jobs}
        selected_job_desc = st.selectbox("Select Job to Invoice", list(job_options.keys()))
        selected_job_id = job_options[selected_job_desc]
        
        # Get job details
        job = next((j for j in completed_jobs if j['id'] == selected_job_id), None)
        
        if job:
            show_invoice_form(vendor_username, selected_job_id, job)

def show_invoice_form(vendor_username, selected_job_id, job):
    """Show the invoice form for a specific job"""
    st.info(f"**Selected Job:** {job['title']} | **Location:** {job['location']}")
    
    with st.form("invoice_form"):
        # Generate invoice number
        invoice_number = f"INV-{vendor_username[:3].upper()}-{datetime.now().strftime('%Y%m%d')}-{selected_job_id}"
        
        col1, col2 = st.columns(2)
        with col1:
            invoice_date = st.date_input("Invoice Date", value=datetime.now())
            st.text_input("Invoice Number", value=invoice_number, disabled=True)
            st.text_input("Vendor Username", value=vendor_username, disabled=True)
            quantity = st.number_input("Quantity", min_value=1, value=1)
        
        with col2:
            unit_cost = st.number_input("Unit Cost (₦)", min_value=0.0, value=0.0, step=1000.0)
            labour_charge = st.number_input("Labour Charges (₦)", min_value=0.0, value=0.0, step=1000.0)
            vat_applicable = st.checkbox("VAT Applicable (7.5%)")
            details_of_work = st.text_area("Details of Work", value=job['description'])
        
        # Calculate amounts
        amount = quantity * unit_cost
        vat_amount = (amount + labour_charge) * 0.075 if vat_applicable else 0
        total_amount = amount + labour_charge + vat_amount
        
        # Display calculated amounts
        st.markdown("### 💰 Amount Summary")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Material Cost", format_ngn(amount))
        with col2:
            st.metric("Labour Charges", format_ngn(labour_charge))
        with col3:
            st.metric("VAT Amount", format_ngn(vat_amount))
        with col4:
            st.metric("Total Amount", format_ngn(total_amount))
        
        submitted = st.form_submit_button("📤 Submit Invoice", use_container_width=True)
        
        if submitted:
            if not details_of_work:
                st.error("❌ Please provide details of work")
            else:
                # Check if invoice number already exists
                existing_invoice = execute_query(
                    'SELECT * FROM invoices WHERE invoice_number = ?',
                    (invoice_number,)
                )
                
                if existing_invoice:
                    st.error("❌ Invoice number already exists. Please try again.")
                else:
                    success = execute_update(
                        '''INSERT INTO invoices 
                        (invoice_number, request_id, vendor_username, invoice_date,
                         details_of_work, quantity, unit_cost, amount, labour_charge,
                         vat_applicable, vat_amount, total_amount) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (invoice_number, selected_job_id, vendor_username,
                         invoice_date.strftime('%Y-%m-%d'), details_of_work,
                         quantity, unit_cost, amount, labour_charge,
                         1 if vat_applicable else 0, vat_amount, total_amount)
                    )
                    
                    if success:
                        st.success("✅ Invoice submitted successfully!")
                        
                        # Update request with invoice info
                        execute_update(
                            '''UPDATE maintenance_requests 
                            SET invoice_amount = ?, invoice_number = ? 
                            WHERE id = ?''',
                            (total_amount, invoice_number, selected_job_id)
                        )
                        
                        # Clear the selected job if it was set
                        if 'selected_job_for_invoice' in st.session_state:
                            st.session_state.selected_job_for_invoice = None
                        
                        # Get the invoice ID for PDF download
                        new_invoice = execute_query(
                            'SELECT id FROM invoices WHERE invoice_number = ?',
                            (invoice_number,)
                        )
                        
                        if new_invoice:
                            invoice_id = new_invoice[0]['id']
                            pdf_buffer = create_invoice_pdf(invoice_id)
                            if pdf_buffer:
                                st.download_button(
                                    label="📥 Download Invoice PDF",
                                    data=pdf_buffer,
                                    file_name=f"invoice_{invoice_number}.pdf",
                                    mime="application/pdf"
                                )
                        
                        st.rerun()
                    else:
                        st.error("❌ Failed to submit invoice")

def show_vendor_ppm_assignments(vendor_username):
    st.markdown("### 💼 PPM Assignments")
    
    # Get PPM assignments for this vendor
    assignments = execute_query('''
        SELECT pa.*, ps.schedule_name, ps.facility_category, ps.sub_category,
               ps.description, ps.estimated_cost, ps.estimated_duration_hours
        FROM ppm_assignments pa
        JOIN ppm_schedules ps ON pa.schedule_id = ps.id
        WHERE pa.vendor_username = ?
        ORDER BY pa.due_date
    ''', (vendor_username,))
    
    if assignments:
        # Status counts
        status_counts = {}
        for assignment in assignments:
            status = assignment['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Display status summary
        st.markdown("#### 📊 Assignment Status")
        cols = st.columns(len(status_counts))
        for idx, (status, count) in enumerate(status_counts.items()):
            with cols[idx]:
                create_metric_card(status, count, "📋")
        
        # Display assignments
        st.markdown("#### 📋 Your PPM Assignments")
        for assignment in assignments:
            with st.expander(f"{assignment['schedule_name']} - Due: {assignment['due_date']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Facility:** {assignment['facility_category']}")
                    st.write(f"**Sub-Category:** {assignment['sub_category']}")
                    st.write(f"**Assigned By:** {assignment['assigned_by']}")
                    st.write(f"**Assigned Date:** {assignment['assigned_date']}")
                with col2:
                    st.write(f"**Status:** {assignment['status']}")
                    st.write(f"**Due Date:** {assignment['due_date']}")
                    if assignment['completed_date']:
                        st.write(f"**Completed:** {assignment['completed_date']}")
                    if assignment['estimated_cost']:
                        st.write(f"**Est. Cost:** {format_ngn(assignment['estimated_cost'])}")
                
                st.write(f"**Description:** {assignment['description']}")
                
                # Update status
                if assignment['status'] in ['Assigned', 'In Progress']:
                    st.markdown("---")
                    new_status = st.selectbox(
                        "Update Status",
                        ["In Progress", "Completed"],
                        key=f"ppm_status_{assignment['id']}"
                    )
                    
                    completion_notes = st.text_area(
                        "Completion Notes",
                        placeholder="Describe work done, observations, recommendations...",
                        key=f"ppm_notes_{assignment['id']}",
                        height=100
                    )
                    
                    actual_cost = st.number_input(
                        "Actual Cost (₦)",
                        min_value=0.0,
                        value=float(assignment['estimated_cost'] or 0),
                        step=1000.0,
                        key=f"actual_cost_{assignment['id']}"
                    )
                    
                    if st.button("💾 Update Assignment", key=f"update_ppm_{assignment['id']}", use_container_width=True):
                        if new_status == 'Completed' and not completion_notes:
                            st.error("❌ Please provide completion notes")
                        else:
                            update_success = execute_update(
                                '''UPDATE ppm_assignments 
                                SET status = ?, completion_notes = ?, completed_date = ?
                                WHERE id = ?''',
                                (new_status, completion_notes,
                                 datetime.now().strftime('%Y-%m-%d') if new_status == 'Completed' else None,
                                 assignment['id'])
                            )
                            
                            if update_success:
                                # Also update the main PPM schedule
                                execute_update(
                                    '''UPDATE ppm_schedules 
                                    SET status = ?, actual_completion_date = ?, 
                                        actual_cost = ?, notes = ?
                                    WHERE id = ?''',
                                    (new_status, 
                                     datetime.now().strftime('%Y-%m-%d') if new_status == 'Completed' else None,
                                     actual_cost,
                                     completion_notes,
                                     assignment['schedule_id'])
                                )
                                
                                st.success("✅ Assignment updated successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to update assignment")
                
                # Show PDF download for completed PPM
                if assignment['status'] == 'Completed':
                    pdf_buffer = create_ppm_pdf_report(assignment['schedule_id'])
                    if pdf_buffer:
                        st.download_button(
                            label="📥 Download PPM Report",
                            data=pdf_buffer,
                            file_name=f"ppm_report_{assignment['schedule_id']}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            key=f"ppm_pdf_{assignment['id']}"
                        )
    else:
        st.info("📭 No PPM assignments found")

def show_vendor_performance(vendor_username):
    st.markdown("### 📊 Performance Analytics")
    
    # Get performance data
    jobs_data = execute_query('''
        SELECT * FROM maintenance_requests 
        WHERE assigned_vendor = ?
        ORDER BY created_date DESC
    ''', (vendor_username,))
    
    invoices_data = execute_query('''
        SELECT * FROM invoices 
        WHERE vendor_username = ?
        ORDER BY invoice_date DESC
    ''', (vendor_username,))
    
    if not jobs_data:
        st.info("📭 No performance data available")
        return
    
    df_jobs = pd.DataFrame(jobs_data)
    df_invoices = pd.DataFrame(invoices_data) if invoices_data else pd.DataFrame()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_jobs = len(df_jobs)
        create_metric_card("Total Jobs", total_jobs, "📋")
    
    with col2:
        completed_jobs = len(df_jobs[df_jobs['status'] == 'Completed'])
        completion_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
        create_metric_card("Completion Rate", f"{completion_rate:.1f}%", "✅")
    
    with col3:
        if not df_invoices.empty:
            total_revenue = df_invoices['total_amount'].sum()
            create_metric_card("Total Revenue", format_ngn(total_revenue), "💰")
        else:
            create_metric_card("Total Revenue", "₦0", "💰")
    
    with col4:
        # Calculate average completion time
        completed_df = df_jobs[df_jobs['status'] == 'Completed']
        if not completed_df.empty and 'created_date' in completed_df.columns and 'completed_date' in completed_df.columns:
            try:
                completed_df['created_date'] = pd.to_datetime(completed_df['created_date'], errors='coerce')
                completed_df['completed_date'] = pd.to_datetime(completed_df['completed_date'], errors='coerce')
                completed_df = completed_df.dropna(subset=['created_date', 'completed_date'])
                
                if not completed_df.empty:
                    completed_df['completion_time'] = (completed_df['completed_date'] - completed_df['created_date']).dt.days
                    avg_time = completed_df['completion_time'].mean()
                    create_metric_card("Avg Time", f"{avg_time:.1f} days", "⏱️")
                else:
                    create_metric_card("Avg Time", "N/A", "⏱️")
            except Exception as e:
                print(f"Error calculating completion time: {e}")
                create_metric_card("Avg Time", "N/A", "⏱️")
        else:
            create_metric_card("Avg Time", "N/A", "⏱️")
    
    st.divider()
    
    # Monthly job completion trend
    st.markdown("#### 📈 Monthly Performance")
    
    if not df_jobs.empty and 'created_date' in df_jobs.columns:
        df_jobs['created_date'] = pd.to_datetime(df_jobs['created_date'], errors='coerce')
        df_jobs = df_jobs.dropna(subset=['created_date'])
        
        if not df_jobs.empty:
            df_jobs['month'] = df_jobs['created_date'].dt.strftime('%Y-%m')
            
            monthly_stats = df_jobs.groupby('month').agg({
                'id': 'count',
                'status': lambda x: (x == 'Completed').sum()
            }).reset_index()
            
            monthly_stats.columns = ['Month', 'Total Jobs', 'Completed Jobs']
            monthly_stats['Completion Rate'] = (monthly_stats['Completed Jobs'] / monthly_stats['Total Jobs'] * 100).round(1)
            
            fig = px.bar(monthly_stats, x='Month', y=['Total Jobs', 'Completed Jobs'],
                         title="Monthly Job Assignments and Completions",
                         barmode='group',
                         labels={'value': 'Number of Jobs', 'variable': 'Metric'})
            st.plotly_chart(fig, use_container_width=True)
    
    # Revenue trend if invoices exist
    if not df_invoices.empty and 'invoice_date' in df_invoices.columns:
        st.markdown("#### 💰 Revenue Trend")
        
        df_invoices['invoice_date'] = pd.to_datetime(df_invoices['invoice_date'], errors='coerce')
        df_invoices = df_invoices.dropna(subset=['invoice_date'])
        
        if not df_invoices.empty:
            df_invoices['month'] = df_invoices['invoice_date'].dt.strftime('%Y-%m')
            
            monthly_revenue = df_invoices.groupby('month')['total_amount'].sum().reset_index()
            
            fig2 = px.line(monthly_revenue, x='month', y='total_amount',
                           title="Monthly Revenue",
                           markers=True,
                           labels={'total_amount': 'Revenue (₦)', 'month': 'Month'})
            st.plotly_chart(fig2, use_container_width=True)

def show_vendor_profile_update(vendor, vendor_username):
    st.markdown("### 📝 Update Vendor Profile")
    
    with st.form("vendor_profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company Name *", value=vendor['company_name'])
            contact_person = st.text_input("Contact Person *", value=vendor['contact_person'])
            email = st.text_input("Email *", value=vendor['email'])
            phone = st.text_input("Phone *", value=vendor['phone'])
            vendor_type = st.selectbox(
                "Vendor Type *",
                ["HVAC", "Generator", "Fixture and Fittings", "Building Maintenance", 
                 "Plumbing", "Electrical", "Cleaning", "HSE", "Space Management"],
                index=["HVAC", "Generator", "Fixture and Fittings", "Building Maintenance", 
                      "Plumbing", "Electrical", "Cleaning", "HSE", "Space Management"].index(vendor['vendor_type']) if vendor['vendor_type'] in ["HVAC", "Generator", "Fixture and Fittings", "Building Maintenance", "Plumbing", "Electrical", "Cleaning", "HSE", "Space Management"] else 0
            )
        
        with col2:
            annual_turnover = st.number_input("Annual Turnover (₦)", 
                                              value=float(vendor['annual_turnover'] or 0),
                                              step=10000.0)
            tax_id = st.text_input("Tax Identification Number", value=vendor['tax_identification_number'] or "")
            rc_number = st.text_input("RC Number", value=vendor['rc_number'] or "")
            key_staff = st.text_area("Key Management Staff", 
                                    value=vendor['key_management_staff'] or "",
                                    placeholder="Names and positions of key staff...")
        
        services_offered = st.text_area("Services Offered *", 
                                       value=vendor['services_offered'],
                                       height=100)
        account_details = st.text_area("Account Details", 
                                      value=vendor['account_details'] or "",
                                      placeholder="Bank details, account numbers...",
                                      height=80)
        certification = st.text_area("Certifications", 
                                    value=vendor['certification'] or "",
                                    placeholder="Professional certifications, licenses...",
                                    height=80)
        address = st.text_area("Address *", 
                              value=vendor['address'],
                              height=80)
        
        submitted = st.form_submit_button("💾 Update Profile", use_container_width=True)
        
        if submitted:
            if not all([company_name, contact_person, email, phone, vendor_type, services_offered, address]):
                st.error("❌ Please fill in all required fields (*)")
            else:
                success = execute_update(
                    '''UPDATE vendors 
                    SET company_name = ?, contact_person = ?, email = ?, phone = ?, 
                        vendor_type = ?, services_offered = ?, annual_turnover = ?,
                        tax_identification_number = ?, rc_number = ?, key_management_staff = ?,
                        account_details = ?, certification = ?, address = ?
                    WHERE username = ?''',
                    (company_name, contact_person, email, phone, vendor_type,
                     services_offered, annual_turnover, tax_id, rc_number,
                     key_staff, account_details, certification, address,
                     vendor_username)
                )
                
                if success:
                    st.success("✅ Profile updated successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to update profile")

# =============================================
# MAIN APP FLOW (Rest of the code remains the same)
# =============================================

# Note: The rest of the code remains unchanged. The main fixes were:
# 1. Added safe_date() function for safe datetime conversion
# 2. Fixed the invoice_date column in database to use DATE type
# 3. Added error handling for pd.to_datetime() with errors='coerce'
# 4. Fixed the "Assign to Vendor" button functionality in show_ppm_schedules()
# 5. Fixed the session state management for PPM filter

# The HSE, Space Management, Generator Records, and other functions remain as in the original code
# Only the problematic functions were modified above

# =============================================
# RUN THE APPLICATION
# =============================================
if __name__ == "__main__":
    main()
