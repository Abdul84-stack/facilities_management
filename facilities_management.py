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
                    st.rerun()
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
                    st.rerun()
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
                    st.rerun()
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
            room_name = st.text_input("Room Name *", placeholder="e.g., Conference Room A")
            room_type = st.selectbox(
                "Room Type *",
                ["Conference Room", "Meeting Room", "Training Room", "Auditorium", 
                 "Board Room", "Interview Room", "Other"]
            )
            booking_date = st.date_input("Booking Date *", value=datetime.now())
        
        with col2:
            start_time = st.time_input("Start Time *", value=datetime.now().time())
            end_time = st.time_input("End Time *", value=(datetime.now() + timedelta(hours=1)).time())
            attendees_count = st.number_input("Number of Attendees", min_value=1, value=5)
        
        booked_by = st.text_input("Booked By *", value=st.session_state.user['username'])
        purpose = st.text_area("Purpose *", placeholder="Purpose of the booking...")
        notes = st.text_area("Additional Notes", placeholder="Any special requirements...")
        
        submitted = st.form_submit_button("✅ Book Room", use_container_width=True)
        
        if submitted:
            # Validation
            if not all([room_name, room_type, booked_by, purpose]):
                st.error("❌ Please fill in all required fields (*)")
            elif end_time <= start_time:
                st.error("❌ End time must be after start time")
            else:
                # Check for booking conflicts
                conflicting_bookings = execute_query('''
                    SELECT * FROM room_bookings 
                    WHERE room_name = ? 
                    AND booking_date = ?
                    AND ((start_time < ? AND end_time > ?) OR (start_time < ? AND end_time > ?))
                    AND status != 'Cancelled'
                ''', (room_name, booking_date.strftime('%Y-%m-%d'), 
                      start_time.strftime('%H:%M'), end_time.strftime('%H:%M'),
                      end_time.strftime('%H:%M'), start_time.strftime('%H:%M')))
                
                if conflicting_bookings:
                    st.error("❌ Room already booked for this time slot")
                else:
                    success = execute_update(
                        '''INSERT INTO room_bookings 
                        (room_name, room_type, booking_date, start_time, end_time,
                         booked_by, purpose, attendees_count, notes) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (room_name, room_type, booking_date.strftime('%Y-%m-%d'),
                         start_time.strftime('%H:%M'), end_time.strftime('%H:%M'),
                         booked_by, purpose, attendees_count, notes)
                    )
                    if success:
                        st.success("✅ Room booked successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to book room")
    
    # Display today's bookings
    st.markdown("### 📋 Today's Bookings")
    today = datetime.now().strftime('%Y-%m-%d')
    today_bookings = execute_query('''
        SELECT * FROM room_bookings 
        WHERE booking_date = ? 
        AND status != 'Cancelled'
        ORDER BY start_time
    ''', (today,))
    
    if today_bookings:
        for booking in today_bookings:
            col1, col2, col3 = st.columns([0.6, 0.3, 0.1])
            with col1:
                st.write(f"**{booking['room_name']}** ({booking['room_type']})")
                st.write(f"⏰ {booking['start_time']} - {booking['end_time']}")
            with col2:
                st.write(f"👤 {booking['booked_by']}")
                st.write(f"👥 {booking['attendees_count']} people")
            with col3:
                if st.button("❌", key=f"cancel_{booking['id']}", help="Cancel booking"):
                    execute_update(
                        "UPDATE room_bookings SET status = 'Cancelled' WHERE id = ?",
                        (booking['id'],)
                    )
                    st.success("✅ Booking cancelled")
                    st.rerun()
            
            st.write(f"**Purpose:** {booking['purpose']}")
            st.divider()
    else:
        st.info("📭 No bookings for today")

def show_room_bookings_overview():
    st.markdown("### 👀 All Room Bookings")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        view_option = st.selectbox(
            "View",
            ["All", "Today", "This Week", "This Month", "Upcoming", "Past"]
        )
    with col2:
        room_filter = st.text_input("Filter by Room Name", "")
    with col3:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Confirmed", "Cancelled", "Completed"]
        )
    
    # Date range filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=7))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now() + timedelta(days=30))
    
    # Build query based on filters
    query = '''
        SELECT * FROM room_bookings 
        WHERE booking_date BETWEEN ? AND ?
    '''
    params = [start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
    
    if room_filter:
        query += " AND room_name LIKE ?"
        params.append(f"%{room_filter}%")
    
    if status_filter != "All":
        query += " AND status = ?"
        params.append(status_filter)
    
    if view_option == "Today":
        query += " AND booking_date = ?"
        params.append(datetime.now().strftime('%Y-%m-%d'))
    elif view_option == "This Week":
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        query += " AND booking_date BETWEEN ? AND ?"
        params.extend([week_start.strftime('%Y-%m-%d'), week_end.strftime('%Y-%m-%d')])
    elif view_option == "This Month":
        today = datetime.now()
        month_start = today.replace(day=1)
        next_month = today.replace(day=28) + timedelta(days=4)
        month_end = next_month - timedelta(days=next_month.day)
        query += " AND booking_date BETWEEN ? AND ?"
        params.extend([month_start.strftime('%Y-%m-%d'), month_end.strftime('%Y-%m-%d')])
    elif view_option == "Upcoming":
        query += " AND booking_date >= ? AND status = 'Confirmed'"
        params.append(datetime.now().strftime('%Y-%m-%d'))
    elif view_option == "Past":
        query += " AND booking_date < ?"
        params.append(datetime.now().strftime('%Y-%m-%d'))
    
    query += " ORDER BY booking_date DESC, start_time"
    
    bookings = execute_query(query, tuple(params))
    
    if bookings:
        # Convert to DataFrame for display
        df_data = []
        for booking in bookings:
            df_data.append({
                "Room": booking['room_name'],
                "Type": booking['room_type'],
                "Date": booking['booking_date'],
                "Time": f"{booking['start_time']} - {booking['end_time']}",
                "Booked By": booking['booked_by'],
                "Attendees": booking['attendees_count'],
                "Status": booking['status'],
                "Purpose": booking['purpose'][:50] + "..." if len(booking['purpose']) > 50 else booking['purpose']
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Export option
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export as CSV",
            data=csv,
            file_name=f"room_bookings_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("📭 No bookings found with the selected filters")

def show_space_analytics():
    st.markdown("### 📊 Space Utilization Analytics")
    
    # Get booking data for the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    bookings_data = execute_query('''
        SELECT * FROM room_bookings 
        WHERE booking_date BETWEEN ? AND ?
        AND status != 'Cancelled'
    ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
    
    if not bookings_data:
        st.info("📭 No booking data available for analytics")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(bookings_data)
    
    # Analytics metrics
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
        utilization_rate = (len(df) / 30) * 10  # Simplified utilization metric
        create_metric_card("Utilization", f"{utilization_rate:.1f}%", "📈")
    
    st.divider()
    
    # Room usage chart
    st.markdown("#### 🏢 Room Usage Frequency")
    room_counts = df['room_name'].value_counts().reset_index()
    room_counts.columns = ['Room', 'Bookings']
    
    fig1 = px.bar(room_counts, x='Room', y='Bookings', 
                  title="Number of Bookings per Room (Last 30 Days)",
                  color='Bookings', color_continuous_scale='blues')
    st.plotly_chart(fig1, use_container_width=True)
    
    # Daily bookings trend
    st.markdown("#### 📈 Daily Bookings Trend")
    df['booking_date'] = pd.to_datetime(df['booking_date'])
    daily_counts = df.groupby('booking_date').size().reset_index(name='Bookings')
    
    fig2 = px.line(daily_counts, x='booking_date', y='Bookings',
                   title="Daily Bookings Trend",
                   markers=True)
    fig2.update_layout(xaxis_title="Date", yaxis_title="Number of Bookings")
    st.plotly_chart(fig2, use_container_width=True)
    
    # Room type distribution
    st.markdown("#### 📊 Room Type Distribution")
    room_type_counts = df['room_type'].value_counts().reset_index()
    room_type_counts.columns = ['Room Type', 'Count']
    
    fig3 = px.pie(room_type_counts, values='Count', names='Room Type',
                  title="Bookings by Room Type",
                  hole=0.3)
    st.plotly_chart(fig3, use_container_width=True)
    
    # Peak hours analysis
    st.markdown("#### ⏰ Peak Booking Hours")
    df['start_time'] = pd.to_datetime(df['start_time']).dt.hour
    hourly_counts = df['start_time'].value_counts().sort_index().reset_index()
    hourly_counts.columns = ['Hour', 'Bookings']
    
    fig4 = px.bar(hourly_counts, x='Hour', y='Bookings',
                  title="Bookings by Hour of Day",
                  labels={'Hour': 'Hour of Day (24h)'})
    st.plotly_chart(fig4, use_container_width=True)

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
            # Clear modal state
            if 'show_vendor_modal' in st.session_state:
                st.session_state.show_vendor_modal = False
            if 'assigning_schedule_id' in st.session_state:
                st.session_state.assigning_schedule_id = None
            st.rerun()
    
    with col2:
        if st.button("❌ Cancel", use_container_width=True, type="secondary"):
            # Clear modal state
            if 'show_vendor_modal' in st.session_state:
                st.session_state.show_vendor_modal = False
            if 'assigning_schedule_id' in st.session_state:
                st.session_state.assigning_schedule_id = None
                def show_ppm_schedules():
    """Display and manage PPM schedules"""
    st.markdown("### 📋 PPM Schedules")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Not Due", "Due Soon", "WIP", "Completed", "Overdue"]
        )
    with col2:
        category_filter = st.selectbox(
            "Filter by Category",
            ["All", "Electrical", "HVAC", "Plumbing", "Generator", "Building", "Cleaning", "Security"]
        )
    with col3:
        frequency_filter = st.selectbox(
            "Filter by Frequency",
            ["All", "Daily", "Weekly", "Monthly", "Quarterly", "Bi-annual", "Annual"]
        )
    
    # Build query
    query = '''SELECT * FROM ppm_schedules WHERE created_by = ?'''
    params = [st.session_state.user['username']]
    
    if status_filter != "All":
        if status_filter == "Due Soon":
            # Get schedules due in the next 7 days
            query += " AND status IN ('Not Due', 'Prepare') AND next_maintenance_date BETWEEN date('now') AND date('now', '+7 days')"
        elif status_filter == "Overdue":
            query += " AND status = 'Due' AND next_maintenance_date < date('now')"
        else:
            query += " AND status = ?"
            params.append(status_filter)
    
    if category_filter != "All":
        query += " AND facility_category = ?"
        params.append(category_filter)
    
    if frequency_filter != "All":
        query += " AND frequency = ?"
        params.append(frequency_filter)
    
    query += " ORDER BY next_maintenance_date"
    
    schedules = execute_query(query, tuple(params))
    
    if schedules:
        for schedule in schedules:
            with st.expander(f"{schedule['schedule_name']} - {schedule['status']} - Due: {schedule['next_maintenance_date']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Category:** {schedule['facility_category']}")
                    st.write(f"**Sub-Category:** {schedule['sub_category']}")
                    st.write(f"**Frequency:** {schedule['frequency']}")
                    
                    # Status badge with color
                    status = schedule['status']
                    status_colors = {
                        'Not Due': '🟢',
                        'Prepare': '🟡',
                        'Due': '🟠',
                        'WIP': '🔵',
                        'Completed': '🟣',
                        'Overdue': '🔴'
                    }
                    st.write(f"**Status:** {status_colors.get(status, '⚪')} {status}")
                    
                    if schedule['assigned_vendor']:
                        st.write(f"**Assigned Vendor:** {schedule['assigned_vendor']}")
                
                with col2:
                    if schedule['estimated_duration_hours']:
                        st.write(f"**Est. Duration:** {schedule['estimated_duration_hours']} hours")
                    if schedule['estimated_cost']:
                        st.write(f"**Est. Cost:** {format_ngn(schedule['estimated_cost'])}")
                    
                    if schedule['actual_completion_date']:
                        st.write(f"**Completed On:** {schedule['actual_completion_date']}")
                    if schedule['actual_cost']:
                        st.write(f"**Actual Cost:** {format_ngn(schedule['actual_cost'])}")
                
                st.write(f"**Description:**")
                st.info(schedule['description'])
                
                if schedule['notes']:
                    st.write(f"**Notes:**")
                    st.warning(schedule['notes'])
                
                # Action buttons
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if schedule['status'] in ['Not Due', 'Prepare'] and not schedule['assigned_vendor']:
                        if st.button("👷 Assign Vendor", key=f"assign_{schedule['id']}", use_container_width=True):
                            st.session_state.show_vendor_modal = True
                            st.session_state.assigning_schedule_id = schedule['id']
                            st.rerun()
                
                with col2:
                    if schedule['status'] == 'WIP' and schedule['assigned_vendor']:
                        if st.button("✅ Mark Complete", key=f"complete_{schedule['id']}", use_container_width=True):
                            st.session_state.completing_schedule_id = schedule['id']
                            st.rerun()
                
                with col3:
                    if st.button("📝 Edit", key=f"edit_{schedule['id']}", use_container_width=True, type="secondary"):
                        st.session_state.editing_schedule_id = schedule['id']
                        st.rerun()
                
                with col4:
                    if st.button("🗑️ Delete", key=f"delete_{schedule['id']}", use_container_width=True, type="secondary"):
                        execute_update("DELETE FROM ppm_schedules WHERE id = ?", (schedule['id'],))
                        st.success("✅ Schedule deleted!")
                        st.rerun()
    else:
        st.info("📭 No PPM schedules found")
    
    # Handle vendor assignment modal
    if st.session_state.get('show_vendor_modal') and st.session_state.get('assigning_schedule_id'):
        schedule_id = st.session_state.assigning_schedule_id
        schedule = execute_query('SELECT * FROM ppm_schedules WHERE id = ?', (schedule_id,))
        if schedule:
            schedule = schedule[0]
            show_assign_vendor_modal(schedule_id, schedule['facility_category'])
    
    # Handle schedule completion
    if st.session_state.get('completing_schedule_id'):
        schedule_id = st.session_state.completing_schedule_id
        show_complete_ppm_modal(schedule_id)

def show_complete_ppm_modal(schedule_id):
    """Modal for completing PPM schedule"""
    st.markdown("---")
    st.markdown("### ✅ Complete PPM Schedule")
    
    with st.form(f"complete_ppm_{schedule_id}"):
        actual_completion_date = st.date_input("Completion Date", value=datetime.now())
        actual_cost = st.number_input("Actual Cost (₦)", min_value=0.0, step=1000.0)
        completion_notes = st.text_area("Completion Notes", placeholder="Details of work completed...")
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("✅ Complete PPM", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True, type="secondary")
        
        if submit:
            if not completion_notes:
                st.error("❌ Please provide completion notes")
            else:
                # Update schedule
                execute_update('''
                    UPDATE ppm_schedules 
                    SET status = 'Completed',
                        actual_completion_date = ?,
                        actual_cost = ?,
                        notes = COALESCE(notes || '\n\nCompletion: ' || ?, ?)
                    WHERE id = ?
                ''', (
                    actual_completion_date.strftime('%Y-%m-%d'),
                    actual_cost,
                    completion_notes,
                    completion_notes,
                    schedule_id
                ))
                
                # Update assignment
                execute_update('''
                    UPDATE ppm_assignments 
                    SET status = 'Completed',
                        completed_date = ?,
                        completion_notes = ?
                    WHERE schedule_id = ? AND status = 'Assigned'
                ''', (
                    actual_completion_date.strftime('%Y-%m-%d'),
                    completion_notes,
                    schedule_id
                ))
                
                st.success("✅ PPM marked as completed!")
                st.session_state.completing_schedule_id = None
                st.rerun()
        
        if cancel:
            st.session_state.completing_schedule_id = None
            st.rerun()

def show_new_ppm_schedule():
    """Form to create new PPM schedule"""
    st.markdown("### ➕ Create New PPM Schedule")
    
    with st.form("new_ppm_schedule"):
        col1, col2 = st.columns(2)
        
        with col1:
            schedule_name = st.text_input("Schedule Name *", placeholder="e.g., Monthly HVAC Maintenance")
            facility_category = st.selectbox(
                "Facility Category *",
                ["Electrical", "HVAC", "Plumbing", "Generator", "Building", "Cleaning", "Security", "Fire Safety", "Other"]
            )
            sub_category = st.text_input("Sub-Category *", placeholder="e.g., AC Units, Chillers, etc.")
        
        with col2:
            frequency = st.selectbox(
                "Frequency *",
                ["Daily", "Weekly", "Monthly", "Quarterly", "Bi-annual", "Annual"]
            )
            next_maintenance_date = st.date_input("Next Maintenance Date *", 
                                                  value=datetime.now() + timedelta(days=30))
        
        # Additional fields
        col1, col2 = st.columns(2)
        with col1:
            estimated_duration_hours = st.number_input("Estimated Duration (hours)", min_value=0, value=2)
        with col2:
            estimated_cost = st.number_input("Estimated Cost (₦)", min_value=0.0, value=0.0)
        
        description = st.text_area("Description *", 
                                   placeholder="Detailed description of maintenance activities...")
        notes = st.text_area("Notes", 
                             placeholder="Any special instructions or requirements...")
        
        submitted = st.form_submit_button("✅ Create PPM Schedule", use_container_width=True)
        
        if submitted:
            if not all([schedule_name, facility_category, sub_category, frequency, description]):
                st.error("❌ Please fill in all required fields (*)")
            else:
                success = execute_update('''
                    INSERT INTO ppm_schedules 
                    (schedule_name, facility_category, sub_category, frequency, 
                     next_maintenance_date, description, notes, estimated_duration_hours,
                     estimated_cost, created_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    schedule_name, facility_category, sub_category, frequency,
                    next_maintenance_date.strftime('%Y-%m-%d'), description, notes,
                    estimated_duration_hours, estimated_cost,
                    st.session_state.user['username']
                ))
                
                if success:
                    st.success("✅ PPM schedule created successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to create schedule")

def show_ppm_analytics():
    """Display PPM analytics and reports"""
    st.markdown("### 📊 PPM Analytics")
    
    # Get all PPM schedules for this user
    schedules = execute_query(
        'SELECT * FROM ppm_schedules WHERE created_by = ?',
        (st.session_state.user['username'],)
    )
    
    if not schedules:
        st.info("📭 No PPM data available for analytics")
        return
    
    df = pd.DataFrame(schedules)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_ppm = len(df)
        create_metric_card("Total PPM", total_ppm, "📋")
    
    with col2:
        completed = df[df['status'] == 'Completed'].shape[0]
        completion_rate = (completed / total_ppm * 100) if total_ppm > 0 else 0
        create_metric_card("Completion Rate", f"{completion_rate:.1f}%", "✅")
    
    with col3:
        overdue = df[df['status'] == 'Overdue'].shape[0]
        create_metric_card("Overdue", overdue, "⚠️")
    
    with col4:
        total_estimated_cost = df['estimated_cost'].sum()
        create_metric_card("Est. Budget", format_ngn(total_estimated_cost), "💰")
    
    st.divider()
    
    # Status distribution
    st.markdown("#### 📊 PPM Status Distribution")
    status_counts = df['status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    
    fig1 = px.pie(status_counts, values='Count', names='Status',
                  title="PPM Schedules by Status",
                  hole=0.3)
    st.plotly_chart(fig1, use_container_width=True)
    
    # Category distribution
    st.markdown("#### 🏢 PPM by Facility Category")
    category_counts = df['facility_category'].value_counts().reset_index()
    category_counts.columns = ['Category', 'Count']
    
    fig2 = px.bar(category_counts, x='Category', y='Count',
                  title="PPM Schedules by Category",
                  color='Count', color_continuous_scale='blues')
    st.plotly_chart(fig2, use_container_width=True)
    
    # Monthly schedule
    st.markdown("#### 📅 Monthly PPM Schedule")
    
    # Get current month's schedules
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    month_schedules = []
    for schedule in schedules:
        try:
            due_date = datetime.strptime(schedule['next_maintenance_date'], '%Y-%m-%d')
            if due_date.month == current_month and due_date.year == current_year:
                month_schedules.append({
                    'Date': schedule['next_maintenance_date'],
                    'Schedule': schedule['schedule_name'],
                    'Category': schedule['facility_category'],
                    'Status': schedule['status'],
                    'Vendor': schedule['assigned_vendor'] or 'Not assigned'
                })
        except:
            continue
    
    if month_schedules:
        month_df = pd.DataFrame(month_schedules)
        month_df = month_df.sort_values('Date')
        
        fig3 = px.timeline(month_df, x_start='Date', x_end='Date', y='Schedule',
                           color='Status', title=f"PPM Schedule for {calendar.month_name[current_month]} {current_year}",
                           hover_data=['Category', 'Vendor'])
        fig3.update_yaxes(autorange="reversed")
        st.plotly_chart(fig3, use_container_width=True)
        
        # Display as table
        st.dataframe(month_df, use_container_width=True, hide_index=True)
    else:
        st.info(f"📭 No PPM schedules for {calendar.month_name[current_month]}")
    
    # Download report
    st.divider()
    st.markdown("#### 📥 Download Reports")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Export PPM Data as CSV", use_container_width=True):
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"ppm_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📋 Generate PPM Summary Report", use_container_width=True):
            # Create a summary report
            summary = {
                'Total PPM Schedules': [total_ppm],
                'Completed': [completed],
                'Pending': [total_ppm - completed],
                'Overdue': [overdue],
                'Total Estimated Budget': [format_ngn(total_estimated_cost)],
                'Report Date': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
            }
            summary_df = pd.DataFrame(summary)
            st.dataframe(summary_df, use_container_width=True, hide_index=True)

def show_ppm_approvals_facility_user():
    """Show PPM schedules that need user approval"""
    st.markdown("### ✅ PPM Approvals")
    st.markdown("Review and approve completed PPM schedules")
    
    ppm_for_approval = get_ppm_for_user_approval(st.session_state.user['username'])
    
    if not ppm_for_approval:
        st.success("🎉 No PPM schedules pending your approval!")
        return
    
    for ppm in ppm_for_approval:
        with st.expander(f"{ppm['schedule_name']} - Completed: {ppm['actual_completion_date']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Category:** {ppm['facility_category']}")
                st.write(f"**Sub-Category:** {ppm['sub_category']}")
                st.write(f"**Completed By:** {ppm['assigned_vendor'] or 'N/A'}")
                st.write(f"**Actual Cost:** {format_ngn(ppm['actual_cost']) if ppm['actual_cost'] else 'N/A'}")
            
            with col2:
                st.write(f"**Frequency:** {ppm['frequency']}")
                st.write(f"**Completion Date:** {ppm['actual_completion_date']}")
                st.write(f"**Next Due:** {ppm['next_maintenance_date']}")
            
            # Get completion notes from assignment
            assignment = execute_query(
                'SELECT * FROM ppm_assignments WHERE schedule_id = ?',
                (ppm['id'],)
            )
            if assignment:
                st.write(f"**Completion Notes:**")
                st.info(assignment[0].get('completion_notes', 'No notes provided'))
            
            # Approval buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✅ Approve", key=f"approve_ppm_{ppm['id']}", 
                           use_container_width=True, type="primary"):
                    execute_update(
                        'UPDATE ppm_schedules SET user_approved = 1 WHERE id = ?',
                        (ppm['id'],)
                    )
                    st.success("✅ PPM approved! Sent to manager for final approval.")
                    st.rerun()
            
            with col2:
                if st.button(f"❌ Reject", key=f"reject_ppm_{ppm['id']}", 
                           use_container_width=True, type="secondary"):
                    execute_update(
                        '''UPDATE ppm_schedules 
                        SET status = 'WIP', 
                            notes = COALESCE(notes || '\n\nRejected by user: ' || datetime('now'), 'Rejected by user')
                        WHERE id = ?''',
                        (ppm['id'],)
                    )
                    st.success("✅ PPM rejected and sent back to vendor.")
                    st.rerun()

# =============================================
# GENERATOR MANAGEMENT - FACILITY USER
# =============================================
def show_generator_management_facility_user():
    st.markdown("<h1 class='app-title'>⚡ Generator Management</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📝 Daily Records", "📊 Consumption Analysis", "⚠️ Maintenance Alerts"])
    
    with tab1:
        show_daily_generator_records()
    
    with tab2:
        show_generator_consumption_analysis()
    
    with tab3:
        show_generator_maintenance_alerts()

def show_daily_generator_records():
    """Record daily generator readings"""
    st.markdown("### 📝 Daily Generator Readings")
    
    with st.form("generator_record_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            record_date = st.date_input("Record Date *", value=datetime.now())
            generator_type = st.selectbox(
                "Generator Type *",
                ["Standby", "Prime", "Portable", "Other"]
            )
            opening_hours = st.number_input("Opening Hours Reading *", min_value=0.0, step=0.1)
            closing_hours = st.number_input("Closing Hours Reading *", min_value=0.0, step=0.1)
        
        with col2:
            opening_inventory = st.number_input("Opening Inventory (Liters) *", min_value=0.0, step=10.0)
            purchase_liters = st.number_input("Purchase/Delivery (Liters)", min_value=0.0, step=10.0)
            closing_inventory = st.number_input("Closing Inventory (Liters) *", min_value=0.0, step=10.0)
        
        notes = st.text_area("Notes", placeholder="Any observations or issues...")
        
        submitted = st.form_submit_button("💾 Save Daily Record", use_container_width=True)
        
        if submitted:
            # Validate inputs
            if closing_hours < opening_hours:
                st.error("❌ Closing hours cannot be less than opening hours")
                return
            
            if closing_inventory > (opening_inventory + purchase_liters):
                st.error("❌ Closing inventory cannot be more than opening + purchase")
                return
            
            # Calculate net values
            net_hours = closing_hours - opening_hours
            net_diesel_consumed = (opening_inventory + purchase_liters) - closing_inventory
            
            success = execute_update('''
                INSERT INTO generator_records 
                (record_date, generator_type, opening_hours, closing_hours, net_hours,
                 opening_inventory_liters, purchase_liters, closing_inventory_liters,
                 net_diesel_consumed, recorded_by, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record_date.strftime('%Y-%m-%d'), generator_type,
                opening_hours, closing_hours, net_hours,
                opening_inventory, purchase_liters, closing_inventory,
                net_diesel_consumed, st.session_state.user['username'], notes
            ))
            
            if success:
                st.success("✅ Daily generator record saved successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to save record")
    
    # Display recent records
    st.markdown("### 📋 Recent Records")
    records = execute_query('''
        SELECT * FROM generator_records 
        ORDER BY record_date DESC 
        LIMIT 10
    ''')
    
    if records:
        for record in records:
            with st.expander(f"{record['record_date']} - {record['generator_type']} - Hours: {record['net_hours']:.1f}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Opening Hours:** {record['opening_hours']}")
                    st.write(f"**Closing Hours:** {record['closing_hours']}")
                    st.write(f"**Net Hours:** {record['net_hours']}")
                
                with col2:
                    st.write(f"**Diesel Consumed:** {record['net_diesel_consumed']} liters")
                    st.write(f"**Recorded By:** {record['recorded_by']}")
                    if record['notes']:
                        st.write(f"**Notes:** {record['notes']}")
    else:
        st.info("📭 No generator records found")

def show_generator_consumption_analysis():
    """Analyze generator consumption patterns"""
    st.markdown("### 📊 Generator Consumption Analysis")
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now())
    
    # Get data for the period
    records = execute_query('''
        SELECT * FROM generator_records 
        WHERE record_date BETWEEN ? AND ?
        ORDER BY record_date
    ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
    
    if not records:
        st.info("📭 No generator data available for the selected period")
        return
    
    df = pd.DataFrame(records)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_hours = df['net_hours'].sum()
        create_metric_card("Total Hours", f"{total_hours:.1f}", "⏱️")
    
    with col2:
        total_diesel = df['net_diesel_consumed'].sum()
        create_metric_card("Diesel Used", f"{total_diesel:.0f}L", "⛽")
    
    with col3:
        avg_hours_per_day = df['net_hours'].mean()
        create_metric_card("Avg Hours/Day", f"{avg_hours_per_day:.1f}", "📅")
    
    with col4:
        efficiency = total_diesel / total_hours if total_hours > 0 else 0
        create_metric_card("Efficiency", f"{efficiency:.2f}L/hour", "📈")
    
    st.divider()
    
    # Consumption trend
    st.markdown("#### 📈 Daily Consumption Trend")
    
    # Ensure record_date is datetime
    df['record_date'] = pd.to_datetime(df['record_date'])
    
    # Create daily summary
    daily_summary = df.groupby('record_date').agg({
        'net_hours': 'sum',
        'net_diesel_consumed': 'sum'
    }).reset_index()
    
    # Plot
    fig1 = px.line(daily_summary, x='record_date', y=['net_hours', 'net_diesel_consumed'],
                   title="Daily Generator Hours and Diesel Consumption",
                   labels={'value': 'Amount', 'variable': 'Metric'},
                   height=400)
    st.plotly_chart(fig1, use_container_width=True)
    
    # Efficiency analysis
    st.markdown("#### 📊 Efficiency Analysis")
    daily_summary['efficiency'] = daily_summary['net_diesel_consumed'] / daily_summary['net_hours']
    
    fig2 = px.scatter(daily_summary, x='record_date', y='efficiency',
                      title="Daily Efficiency (Liters per Hour)",
                      trendline="ols",
                      labels={'efficiency': 'Liters per Hour'})
    st.plotly_chart(fig2, use_container_width=True)
    
    # Generator type breakdown
    st.markdown("#### ⚡ Generator Type Breakdown")
    type_summary = df.groupby('generator_type').agg({
        'net_hours': 'sum',
        'net_diesel_consumed': 'sum'
    }).reset_index()
    type_summary['efficiency'] = type_summary['net_diesel_consumed'] / type_summary['net_hours']
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig3 = px.pie(type_summary, values='net_hours', names='generator_type',
                      title="Hours by Generator Type")
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        fig4 = px.bar(type_summary, x='generator_type', y='efficiency',
                      title="Efficiency by Generator Type",
                      labels={'efficiency': 'Liters per Hour'})
        st.plotly_chart(fig4, use_container_width=True)

def show_generator_maintenance_alerts():
    """Show generator maintenance alerts and schedule"""
    st.markdown("### ⚠️ Generator Maintenance Alerts")
    
    # Maintenance schedule
    st.markdown("#### 📅 Maintenance Schedule")
    
    maintenance_tasks = [
        {"task": "Oil Change", "frequency": "Every 250 hours", "last_done": None, "next_due": None},
        {"task": "Oil Filter Change", "frequency": "Every 500 hours", "last_done": None, "next_due": None},
        {"task": "Fuel Filter Change", "frequency": "Every 500 hours", "last_done": None, "next_due": None},
        {"task": "Air Filter Change", "frequency": "Every 1000 hours", "last_done": None, "next_due": None},
        {"task": "Coolant Change", "frequency": "Every 1000 hours", "last_done": None, "next_due": None},
        {"task": "Belt Inspection", "frequency": "Every 250 hours", "last_done": None, "next_due": None},
        {"task": "General Inspection", "frequency": "Daily", "last_done": None, "next_due": None},
    ]
    
    # Calculate total hours from records
    total_hours_query = execute_query('SELECT SUM(net_hours) as total_hours FROM generator_records')
    total_hours = total_hours_query[0]['total_hours'] if total_hours_query and total_hours_query[0]['total_hours'] else 0
    
    # Update tasks with calculated due dates
    for task in maintenance_tasks:
        if "Every" in task["frequency"]:
            hours = int(task["frequency"].split()[1])
            cycles = total_hours // hours
            task["last_done"] = f"{cycles * hours} hours ago"
            task["next_due"] = f"In {(cycles + 1) * hours - total_hours:.0f} hours"
    
    # Display as table
    df = pd.DataFrame(maintenance_tasks)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Alerts based on total hours
    st.markdown("#### 🔔 Maintenance Alerts")
    
    if total_hours >= 250 and total_hours < 500:
        st.warning("⚠️ **Oil Change Due** - Generator has reached 250 hours")
    elif total_hours >= 500 and total_hours < 1000:
        st.warning("⚠️ **Oil & Filter Change Due** - Generator has reached 500 hours")
    elif total_hours >= 1000:
        st.error("🚨 **Major Service Due** - Generator has reached 1000 hours")
    else:
        st.success("✅ All maintenance is up to date")
    
    # Manual maintenance log
    st.divider()
    st.markdown("#### 📝 Log Maintenance Activity")
    
    with st.form("maintenance_log_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            maintenance_date = st.date_input("Maintenance Date", value=datetime.now())
            maintenance_type = st.selectbox(
                "Maintenance Type",
                ["Oil Change", "Filter Change", "General Service", "Repair", "Inspection"]
            )
        
        with col2:
            generator_hours = st.number_input("Generator Hours at Service", min_value=0.0, value=total_hours)
            cost = st.number_input("Cost (₦)", min_value=0.0, step=1000.0)
        
        description = st.text_area("Description", placeholder="Details of maintenance performed...")
        parts_replaced = st.text_input("Parts Replaced", placeholder="List parts replaced, if any...")
        
        if st.form_submit_button("📋 Log Maintenance", use_container_width=True):
            st.success("✅ Maintenance logged successfully!")
            # Here you would save to a maintenance_logs table

# =============================================
# MAIN DASHBOARD - FACILITY USER
# =============================================
def show_facility_user_dashboard():
    """Main dashboard for facility users"""
    st.markdown("<h1 class='dashboard-title'>🏢 Facility User Dashboard</h1>", unsafe_allow_html=True)
    
    # Quick stats
    user_requests = get_user_requests(st.session_state.user['username'])
    pending_requests = [r for r in user_requests if r['status'] == 'Pending']
    completed_requests = [r for r in user_requests if r['status'] == 'Completed']
    approved_requests = [r for r in user_requests if r['status'] == 'Approved']
    
    # PPM stats
    ppm_schedules = execute_query(
        'SELECT * FROM ppm_schedules WHERE created_by = ?',
        (st.session_state.user['username'],)
    )
    ppm_due_soon = [p for p in ppm_schedules if p['status'] in ['Prepare', 'Due']]
    ppm_completed = [p for p in ppm_schedules if p['status'] == 'Completed']
    
    # Generator stats
    today = datetime.now().strftime('%Y-%m-%d')
    today_generator = execute_query(
        'SELECT * FROM generator_records WHERE record_date = ?',
        (today,)
    )
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_metric_card("Active Requests", len(pending_requests), "📋")
    
    with col2:
        create_metric_card("PPM Due Soon", len(ppm_due_soon), "📅")
    
    with col3:
        create_metric_card("Today's Generator", 
                          "Recorded" if today_generator else "Pending", 
                          "⚡")
    
    with col4:
        create_metric_card("Room Bookings", 
                          "Check Calendar", 
                          "🏢")
    
    st.divider()
    
    # Navigation
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📝 New Request", use_container_width=True):
            st.session_state.current_page = "maintenance_request"
            st.rerun()
    
    with col2:
        if st.button("📅 PPM Schedule", use_container_width=True):
            st.session_state.current_page = "ppm_management"
            st.rerun()
    
    with col3:
        if st.button("⚡ Generator Log", use_container_width=True):
            st.session_state.current_page = "generator_management"
            st.rerun()
    
    with col4:
        if st.button("🏢 Book Room", use_container_width=True):
            st.session_state.current_page = "space_management"
            st.rerun()
    
    st.divider()
    
    # Recent activity
    st.markdown("### 📋 Recent Maintenance Requests")
    
    if user_requests:
        # Show last 5 requests
        recent_requests = user_requests[:5]
        for request in recent_requests:
            status_color = {
                'Pending': '🟡',
                'Assigned': '🔵',
                'Completed': '🟣',
                'Approved': '🟢'
            }.get(request['status'], '⚪')
            
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.write(f"**{request['title']}**")
                st.write(f"{status_color} {request['status']} | 📍 {request['location']} | 🏢 {request['facility_type']}")
            with col2:
                if st.button("View", key=f"view_{request['id']}"):
                    st.session_state.viewing_request_id = request['id']
                    st.rerun()
            st.divider()
    else:
        st.info("📭 No maintenance requests yet. Create your first request!")
    
    # Upcoming PPM
    st.markdown("### 📅 Upcoming PPM")
    
    if ppm_schedules:
        # Get schedules due in next 7 days
        upcoming_ppm = []
        for ppm in ppm_schedules:
            try:
                due_date = datetime.strptime(ppm['next_maintenance_date'], '%Y-%m-%d')
                days_until = (due_date - datetime.now()).days
                if 0 <= days_until <= 7:
                    upcoming_ppm.append((ppm, days_until))
            except:
                continue
        
        if upcoming_ppm:
            for ppm, days in sorted(upcoming_ppm, key=lambda x: x[1]):
                urgency = "🔴" if days == 0 else "🟠" if days <= 2 else "🟡"
                st.write(f"{urgency} **{ppm['schedule_name']}** - Due in {days} days")
                st.write(f"   📍 {ppm['facility_category']} | 👷 {ppm['assigned_vendor'] or 'Not assigned'}")
        else:
            st.info("🎉 No PPM due in the next 7 days")
    else:
        st.info("📭 No PPM schedules created yet")

# =============================================
# MAINTENANCE REQUEST - FACILITY USER
# =============================================
def show_maintenance_request():
    """Maintenance request creation and management"""
    st.markdown("<h1 class='app-title'>🛠️ Maintenance Request</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["➕ New Request", "📋 My Requests"])
    
    with tab1:
        show_new_maintenance_request()
    
    with tab2:
        show_my_requests()

def show_new_maintenance_request():
    """Form to create new maintenance request"""
    st.markdown("### ➕ Create New Maintenance Request")
    
    with st.form("maintenance_request_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Title *", placeholder="Brief description of the issue")
            location = st.text_input("Location *", placeholder="Where is the issue?")
            facility_type = st.selectbox(
                "Facility Type *",
                ["Electrical", "HVAC", "Plumbing", "Generator", "Building", "Cleaning", "Security", "Other"]
            )
        
        with col2:
            priority = st.selectbox(
                "Priority *",
                ["Low", "Medium", "High", "Critical"]
            )
            # Vendor assignment will be done by manager
        
        description = st.text_area("Description *", 
                                  height=150,
                                  placeholder="Please provide detailed description of the issue...")
        
        submitted = st.form_submit_button("📤 Submit Request", use_container_width=True)
        
        if submitted:
            if not all([title, location, facility_type, priority, description]):
                st.error("❌ Please fill in all required fields (*)")
            else:
                success = execute_update('''
                    INSERT INTO maintenance_requests 
                    (title, description, location, facility_type, priority, created_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (title, description, location, facility_type, priority, 
                     st.session_state.user['username']))
                
                if success:
                    st.success("✅ Maintenance request submitted successfully!")
                    
                    # Show next steps
                    st.info("""
                    **Next Steps:**
                    1. Your request will be reviewed by the facility manager
                    2. A vendor will be assigned based on the facility type
                    3. You'll be notified when work begins
                    4. You can track progress in "My Requests"
                    """)
                    
                    # Option to create another request
                    if st.button("➕ Create Another Request", use_container_width=True):
                        st.rerun()
                else:
                    st.error("❌ Failed to submit request")

def show_my_requests():
    """Display user's maintenance requests"""
    st.markdown("### 📋 My Maintenance Requests")
    
    requests = get_user_requests(st.session_state.user['username'])
    
    if not requests:
        st.info("📭 You haven't created any maintenance requests yet.")
        return
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Pending", "Assigned", "Completed", "Approved"]
        )
    with col2:
        priority_filter = st.selectbox(
            "Filter by Priority",
            ["All", "Low", "Medium", "High", "Critical"]
        )
    
    # Apply filters
    filtered_requests = requests
    if status_filter != "All":
        filtered_requests = [r for r in filtered_requests if r['status'] == status_filter]
    if priority_filter != "All":
        filtered_requests = [r for r in filtered_requests if r['priority'] == priority_filter]
    
    # Display requests
    for request in filtered_requests:
        with st.expander(f"{request['title']} - {request['status']} - Priority: {request['priority']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Location:** {request['location']}")
                st.write(f"**Facility Type:** {request['facility_type']}")
                st.write(f"**Created:** {request['created_date']}")
                
                # Status with color
                status = request['status']
                status_colors = {
                    'Pending': '🟡',
                    'Assigned': '🔵',
                    'Completed': '🟣',
                    'Approved': '🟢'
                }
                st.write(f"**Status:** {status_colors.get(status, '⚪')} {status}")
                
                if request['assigned_vendor']:
                    st.write(f"**Assigned Vendor:** {request['assigned_vendor']}")
            
            with col2:
                st.write(f"**Priority:** {request['priority']}")
                if request['completed_date']:
                    st.write(f"**Completed:** {request['completed_date']}")
                if request['completion_notes']:
                    st.write(f"**Completion Notes:** {request['completion_notes']}")
                
                # Show workflow status
                show_workflow_status(request)
            
            st.write(f"**Description:**")
            st.info(request['description'])
            
            # Action buttons based on status
            if request['status'] == 'Completed' and not request['requesting_dept_approval']:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Approve Completion", key=f"user_approve_{request['id']}", use_container_width=True):
                        execute_update('''
                            UPDATE maintenance_requests 
                            SET requesting_dept_approval = 1,
                                department_approval_date = datetime('now')
                            WHERE id = ?
                        ''', (request['id'],))
                        st.success("✅ Approved! Sent to manager for final approval.")
                        st.rerun()
                with col2:
                    if st.button("❌ Request Changes", key=f"user_reject_{request['id']}", 
                               use_container_width=True, type="secondary"):
                        # Here you could add a modal for feedback
                        execute_update('''
                            UPDATE maintenance_requests 
                            SET status = 'Assigned',
                                completion_notes = COALESCE(completion_notes || '\n\nRejected by user: ' || datetime('now'), 'Rejected by user')
                            WHERE id = ?
                        ''', (request['id'],))
                        st.success("✅ Sent back to vendor for changes.")
                        st.rerun()
            
            # PDF report for completed/approved requests
            if request['status'] in ['Completed', 'Approved']:
                st.divider()
                st.markdown("#### 📄 Reports")
                
                pdf_buffer = create_maintenance_pdf_report(request['id'])
                if pdf_buffer:
                    pdf_link = get_pdf_download_link(pdf_buffer, f"Maintenance_Report_{request['id']}.pdf")
                    st.markdown(pdf_link, unsafe_allow_html=True)

# =============================================
# FACILITY MANAGER FUNCTIONS
# =============================================
def show_facility_manager_dashboard():
    """Dashboard for facility manager"""
    st.markdown("<h1 class='dashboard-title'>👨‍💼 Facility Manager Dashboard</h1>", unsafe_allow_html=True)
    
    # Get all data for metrics
    all_requests = get_all_requests()
    all_ppm = execute_query('SELECT * FROM ppm_schedules')
    all_invoices = execute_query('SELECT * FROM invoices')
    all_vendors = execute_query('SELECT * FROM vendors')
    
    # Calculate metrics
    pending_requests = [r for r in all_requests if r['status'] == 'Pending']
    active_requests = [r for r in all_requests if r['status'] == 'Assigned']
    completed_requests = [r for r in all_requests if r['status'] == 'Completed']
    ppm_due = [p for p in all_ppm if p['status'] in ['Due', 'Prepare']]
    pending_invoices = [i for i in all_invoices if i['status'] == 'Pending']
    
    # Calculate financial metrics
    total_invoice_amount = sum(i['total_amount'] for i in all_invoices if i['status'] == 'Approved')
    pending_invoice_amount = sum(i['total_amount'] for i in pending_invoices)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_metric_card("Pending Requests", len(pending_requests), "📋")
    
    with col2:
        create_metric_card("PPM Due", len(ppm_due), "📅")
    
    with col3:
        create_metric_card("Pending Invoices", f"₦{pending_invoice_amount:,.0f}", "💰")
    
    with col4:
        create_metric_card("Active Vendors", len(all_vendors), "👷")
    
    st.divider()
    
    # Quick actions
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("👀 Review Requests", use_container_width=True):
            st.session_state.current_page = "manager_requests"
            st.rerun()
    
    with col2:
        if st.button("✅ Approve Jobs", use_container_width=True):
            st.session_state.current_page = "manager_approvals"
            st.rerun()
    
    with col3:
        if st.button("💰 Invoice Approval", use_container_width=True):
            st.session_state.current_page = "invoice_management"
            st.rerun()
    
    with col4:
        if st.button("👷 Vendor Mgmt", use_container_width=True):
            st.session_state.current_page = "vendor_management"
            st.rerun()
    
    st.divider()
    
    # Recent activity in two columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Recent Requests")
        if all_requests[:5]:
            for request in all_requests[:5]:
                status_color = {
                    'Pending': '🟡',
                    'Assigned': '🔵',
                    'Completed': '🟣',
                    'Approved': '🟢'
                }.get(request['status'], '⚪')
                
                st.write(f"{status_color} **{request['title']}**")
                st.write(f"   👤 {request['created_by']} | 📍 {request['location']}")
        else:
            st.info("📭 No recent requests")
    
    with col2:
        st.markdown("### 📅 Upcoming PPM")
        if all_ppm:
            # Get PPM due in next 3 days
            upcoming = []
            for ppm in all_ppm:
                try:
                    due_date = datetime.strptime(ppm['next_maintenance_date'], '%Y-%m-%d')
                    days_until = (due_date - datetime.now()).days
                    if 0 <= days_until <= 3:
                        upcoming.append((ppm, days_until))
                except:
                    continue
            
            if upcoming:
                for ppm, days in sorted(upcoming, key=lambda x: x[1]):
                    urgency = "🔴" if days == 0 else "🟠"
                    st.write(f"{urgency} **{ppm['schedule_name']}**")
                    st.write(f"   🏢 {ppm['facility_category']} | 👷 {ppm['assigned_vendor'] or 'Unassigned'}")
            else:
                st.info("🎉 No PPM due in next 3 days")
        else:
            st.info("📭 No PPM schedules")

def show_manager_requests():
    """Manager view of all maintenance requests"""
    st.markdown("<h1 class='app-title'>📋 All Maintenance Requests</h1>", unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox(
            "Status",
            ["All", "Pending", "Assigned", "Completed", "Approved"]
        )
    with col2:
        priority_filter = st.selectbox(
            "Priority",
            ["All", "Low", "Medium", "High", "Critical"]
        )
    with col3:
        facility_filter = st.selectbox(
            "Facility Type",
            ["All", "Electrical", "HVAC", "Plumbing", "Generator", "Building", "Cleaning", "Security", "Other"]
        )
    
    # Get all requests
    all_requests = get_all_requests()
    
    # Apply filters
    filtered_requests = all_requests
    if status_filter != "All":
        filtered_requests = [r for r in filtered_requests if r['status'] == status_filter]
    if priority_filter != "All":
        filtered_requests = [r for r in filtered_requests if r['priority'] == priority_filter]
    if facility_filter != "All":
        filtered_requests = [r for r in filtered_requests if r['facility_type'] == facility_filter]
    
    # Display requests
    for request in filtered_requests:
        with st.expander(f"{request['title']} - Status: {request['status']} - Priority: {request['priority']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Created By:** {request['created_by']}")
                st.write(f"**Location:** {request['location']}")
                st.write(f"**Facility Type:** {request['facility_type']}")
                st.write(f"**Created Date:** {request['created_date']}")
            
            with col2:
                st.write(f"**Assigned Vendor:** {request['assigned_vendor'] or 'Not assigned'}")
                st.write(f"**Completed Date:** {request['completed_date'] or 'Not completed'}")
                st.write(f"**Approval Status:**")
                st.write(f"  - Department: {'✅' if request['requesting_dept_approval'] else '❌'}")
                st.write(f"  - Manager: {'✅' if request['facilities_manager_approval'] else '❌'}")
            
            st.write(f"**Description:**")
            st.info(request['description'])
            
            if request['completion_notes']:
                st.write(f"**Completion Notes:**")
                st.success(request['completion_notes'])
            
            # Manager actions based on status
            if request['status'] == 'Pending':
                st.markdown("#### 👷 Assign to Vendor")
                vendors = execute_query(
                    'SELECT * FROM vendors WHERE vendor_type = ? OR vendor_type LIKE ?',
                    (request['facility_type'], f'%{request['facility_type']}%')
                )
                
                if vendors:
                    vendor_options = {f"{v['company_name']} ({v['username']})": v['username'] for v in vendors}
                    selected_vendor = st.selectbox("Select Vendor", list(vendor_options.keys()), 
                                                  key=f"vendor_select_{request['id']}")
                    
                    if st.button("✅ Assign Vendor", key=f"assign_{request['id']}"):
                        vendor_username = vendor_options[selected_vendor]
                        execute_update(
                            'UPDATE maintenance_requests SET status = "Assigned", assigned_vendor = ? WHERE id = ?',
                            (vendor_username, request['id'])
                        )
                        st.success(f"✅ Assigned to {selected_vendor}")
                        st.rerun()
                else:
                    st.warning("No vendors available for this facility type")
            
            elif request['status'] == 'Completed' and request['requesting_dept_approval'] and not request['facilities_manager_approval']:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Approve & Close", key=f"manager_approve_{request['id']}", 
                               use_container_width=True):
                        execute_update('''
                            UPDATE maintenance_requests 
                            SET facilities_manager_approval = 1,
                                manager_approval_date = datetime('now'),
                                status = 'Approved'
                            WHERE id = ?
                        ''', (request['id'],))
                        st.success("✅ Job approved and closed!")
                        st.rerun()
                with col2:
                    if st.button("❌ Send Back", key=f"manager_reject_{request['id']}", 
                               use_container_width=True, type="secondary"):
                        execute_update('''
                            UPDATE maintenance_requests 
                            SET status = 'Assigned',
                                requesting_dept_approval = 0
                            WHERE id = ?
                        ''', (request['id'],))
                        st.success("✅ Sent back for rework")
                        st.rerun()
            
            # View PDF report
            if request['status'] in ['Completed', 'Approved']:
                st.divider()
                pdf_buffer = create_maintenance_pdf_report(request['id'])
                if pdf_buffer:
                    pdf_link = get_pdf_download_link(pdf_buffer, f"Report_{request['id']}.pdf")
                    st.markdown(pdf_link, unsafe_allow_html=True)

# =============================================
# VENDOR FUNCTIONS
# =============================================
def show_vendor_dashboard():
    """Dashboard for vendors"""
    st.markdown("<h1 class='dashboard-title'>👷 Vendor Dashboard</h1>", unsafe_allow_html=True)
    
    # Get vendor's jobs
    vendor_jobs = get_vendor_requests(st.session_state.user['username'])
    active_jobs = [j for j in vendor_jobs if j['status'] == 'Assigned']
    completed_jobs = [j for j in vendor_jobs if j['status'] == 'Completed']
    approved_jobs = [j for j in vendor_jobs if j['status'] == 'Approved']
    
    # Get PPM assignments
    ppm_assignments = execute_query(
        'SELECT * FROM ppm_assignments WHERE vendor_username = ?',
        (st.session_state.user['username'],)
    )
    active_ppm = [p for p in ppm_assignments if p['status'] == 'Assigned']
    completed_ppm = [p for p in ppm_assignments if p['status'] == 'Completed']
    
    # Get pending invoices
    pending_invoices = execute_query(
        'SELECT * FROM invoices WHERE vendor_username = ? AND status = "Pending"',
        (st.session_state.user['username'],)
    )
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_metric_card("Active Jobs", len(active_jobs), "🛠️")
    
    with col2:
        create_metric_card("PPM Due", len(active_ppm), "📅")
    
    with col3:
        create_metric_card("Pending Invoices", len(pending_invoices), "💰")
    
    with col4:
        total_completed = len(completed_jobs) + len(completed_ppm)
        create_metric_card("Completed", total_completed, "✅")
    
    st.divider()
    
    # Quick actions
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📋 View Jobs", use_container_width=True):
            st.session_state.current_page = "vendor_jobs"
            st.rerun()
    
    with col2:
        if st.button("📅 PPM Tasks", use_container_width=True):
            st.session_state.current_page = "vendor_ppm"
            st.rerun()
    
    with col3:
        if st.button("💰 Create Invoice", use_container_width=True):
            st.session_state.current_page = "vendor_invoice"
            st.rerun()
    
    with col4:
        if st.button("📊 My Performance", use_container_width=True):
            st.session_state.current_page = "vendor_performance"
            st.rerun()
    
    st.divider()
    
    # Active jobs
    st.markdown("### 🛠️ Active Jobs")
    if active_jobs:
        for job in active_jobs[:3]:
            with st.container():
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    st.write(f"**{job['title']}**")
                    st.write(f"📍 {job['location']} | 🏢 {job['facility_type']}")
                    st.write(f"📅 Created: {job['created_date']}")
                with col2:
                    if st.button("Complete", key=f"complete_{job['id']}"):
                        st.session_state.completing_job_id = job['id']
                        st.rerun()
                st.divider()
    else:
        st.info("📭 No active jobs")
    
    # Active PPM
    st.markdown("### 📅 Active PPM")
    if active_ppm:
        for assignment in active_ppm[:3]:
            schedule = execute_query(
                'SELECT * FROM ppm_schedules WHERE id = ?',
                (assignment['schedule_id'],)
            )
            if schedule:
                schedule = schedule[0]
                st.write(f"**{schedule['schedule_name']}**")
                st.write(f"🏢 {schedule['facility_category']} | 📅 Due: {assignment['due_date']}")
                if st.button("Complete PPM", key=f"complete_ppm_{assignment['id']}"):
                    st.session_state.completing_ppm_assignment_id = assignment['id']
                    st.rerun()
                st.divider()
    else:
        st.info("📭 No active PPM assignments")

def show_vendor_jobs():
    """Vendor view of assigned jobs"""
    st.markdown("<h1 class='app-title'>🛠️ My Jobs</h1>", unsafe_allow_html=True)
    
    vendor_jobs = get_vendor_requests(st.session_state.user['username'])
    
    if not vendor_jobs:
        st.info("📭 No jobs assigned to you yet.")
        return
    
    # Filter tabs
    tab1, tab2, tab3 = st.tabs(["Active", "Completed", "All"])
    
    with tab1:
        active_jobs = [j for j in vendor_jobs if j['status'] == 'Assigned']
        show_jobs_list(active_jobs, "Active")
    
    with tab2:
        completed_jobs = [j for j in vendor_jobs if j['status'] == 'Completed']
        show_jobs_list(completed_jobs, "Completed")
    
    with tab3:
        show_jobs_list(vendor_jobs, "All")
    
    # Handle job completion
    if st.session_state.get('completing_job_id'):
        show_complete_job_modal(st.session_state.completing_job_id)

def show_jobs_list(jobs, title):
    """Display list of jobs"""
    st.markdown(f"### {title} Jobs ({len(jobs)})")
    
    for job in jobs:
        with st.expander(f"{job['title']} - Priority: {job['priority']} - Status: {job['status']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Created By:** {job['created_by']}")
                st.write(f"**Location:** {job['location']}")
                st.write(f"**Facility Type:** {job['facility_type']}")
                st.write(f"**Created:** {job['created_date']}")
            
            with col2:
                st.write(f"**Priority:** {job['priority']}")
                if job['completed_date']:
                    st.write(f"**Completed:** {job['completed_date']}")
                if job['completion_notes']:
                    st.write(f"**Completion Notes:** {job['completion_notes']}")
            
            st.write(f"**Description:**")
            st.info(job['description'])
            
            # Action buttons
            if job['status'] == 'Assigned':
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Mark as Complete", key=f"complete_{job['id']}", 
                               use_container_width=True):
                        st.session_state.completing_job_id = job['id']
                        st.rerun()
                
                with col2:
                    if st.button("📝 Add Job Breakdown", key=f"breakdown_{job['id']}", 
                               use_container_width=True, type="secondary"):
                        st.session_state.adding_breakdown_job_id = job['id']
                        st.rerun()

def show_complete_job_modal(job_id):
    """Modal for completing a job"""
    st.markdown("---")
    st.markdown("### ✅ Complete Job")
    
    job = execute_query('SELECT * FROM maintenance_requests WHERE id = ?', (job_id,))
    if not job:
        st.error("Job not found")
        return
    
    job = job[0]
    
    with st.form(f"complete_job_{job_id}"):
        completion_notes = st.text_area(
            "Completion Notes *",
            height=150,
            placeholder="Describe what work was completed..."
        )
        
        job_breakdown = st.text_area(
            "Job Breakdown",
            height=100,
            placeholder="Breakdown of work done (optional)...",
            value=job.get('job_breakdown', '')
        )
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("✅ Mark as Complete", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True, type="secondary")
        
        if submit:
            if not completion_notes:
                st.error("❌ Please provide completion notes")
            else:
                # Update job status
                execute_update('''
                    UPDATE maintenance_requests 
                    SET status = 'Completed',
                        completed_date = datetime('now'),
                        completion_notes = ?,
                        job_breakdown = ?
                    WHERE id = ?
                ''', (completion_notes, job_breakdown, job_id))
                
                st.success("✅ Job marked as complete! Waiting for user approval.")
                st.session_state.completing_job_id = None
                st.rerun()
        
        if cancel:
            st.session_state.completing_job_id = None
            st.rerun()

# =============================================
# AUTHENTICATION & SESSION MANAGEMENT
# =============================================
def authenticate_user(username, password):
    """Authenticate user"""
    try:
        user = execute_query('SELECT * FROM users WHERE username = ?', (username,))
        if not user:
            return None
        
        user = user[0]
        # Simple password check (in production, use proper hashing)
        if user['password_hash'] == password:
            return user
        return None
    except Exception as e:
        print(f"Authentication error: {e}")
        return None

def logout():
    """Clear session state"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def show_login():
    """Login page"""
    st.markdown("<h1 class='app-title'>🔐 A-Z Facilities Management Pro APP™</h1>", unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                st.markdown("### Login to Your Account")
                
                username = st.text_input("👤 Username", placeholder="Enter your username")
                password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
                
                col1, col2 = st.columns(2)
                with col1:
                    login_button = st.form_submit_button("🚀 Login", use_container_width=True)
                with col2:
                    if st.form_submit_button("🔄 Reset", use_container_width=True, type="secondary"):
                        st.rerun()
                
                if login_button:
                    if not username or not password:
                        st.error("❌ Please enter both username and password")
                    else:
                        user = authenticate_user(username, password)
                        if user:
                            st.session_state.authenticated = True
                            st.session_state.user = user
                            st.success(f"✅ Welcome back, {user['username']}!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password")
            
            # Demo credentials
            st.markdown("---")
            st.markdown("""
            ### 👥 Demo Credentials
            
            **Facility User:**
            - Username: `facility_user`
            - Password: `0123456`
            
            **Facility Manager:**
            - Username: `facility_manager`
            - Password: `0123456`
            
            **Vendor (HVAC):**
            - Username: `hvac_vendor`
            - Password: `0123456`
            """)

# =============================================
# MAIN APPLICATION LOGIC
# =============================================
def main():
    """Main application logic"""
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard"
    
    # Show login if not authenticated
    if not st.session_state.authenticated:
        show_login()
        return
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"""
        <div style='text-align: center; padding: 10px;'>
            <h3>👤 {st.session_state.user['username']}</h3>
            <p><strong>Role:</strong> {st.session_state.user['role'].replace('_', ' ').title()}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Navigation based on role
        user_role = st.session_state.user['role']
        
        if user_role == 'facility_user':
            st.markdown("### 📊 Navigation")
            if st.button("🏠 Dashboard", use_container_width=True):
                st.session_state.current_page = "dashboard"
                st.rerun()
            
            if st.button("🛠️ Maintenance Request", use_container_width=True):
                st.session_state.current_page = "maintenance_request"
                st.rerun()
            
            if st.button("📅 PPM Management", use_container_width=True):
                st.session_state.current_page = "ppm_management"
                st.rerun()
            
            if st.button("⚡ Generator Management", use_container_width=True):
                st.session_state.current_page = "generator_management"
                st.rerun()
            
            if st.button("🏢 Space Management", use_container_width=True):
                st.session_state.current_page = "space_management"
                st.rerun()
            
            if st.button("🛡️ HSE Management", use_container_width=True):
                st.session_state.current_page = "hse_management"
                st.rerun()
            
        elif user_role == 'facility_manager':
            st.markdown("### 📊 Navigation")
            if st.button("🏠 Dashboard", use_container_width=True):
                st.session_state.current_page = "dashboard"
                st.rerun()
            
            if st.button("📋 All Requests", use_container_width=True):
                st.session_state.current_page = "manager_requests"
                st.rerun()
            
            if st.button("✅ Approve Jobs", use_container_width=True):
                st.session_state.current_page = "manager_approvals"
                st.rerun()
            
            if st.button("💰 Invoice Management", use_container_width=True):
                st.session_state.current_page = "invoice_management"
                st.rerun()
            
            if st.button("👷 Vendor Management", use_container_width=True):
                st.session_state.current_page = "vendor_management"
                st.rerun()
            
            if st.button("📊 Reports & Analytics", use_container_width=True):
                st.session_state.current_page = "reports_analytics"
                st.rerun()
        
        elif user_role == 'vendor':
            st.markdown("### 📊 Navigation")
            if st.button("🏠 Dashboard", use_container_width=True):
                st.session_state.current_page = "dashboard"
                st.rerun()
            
            if st.button("🛠️ My Jobs", use_container_width=True):
                st.session_state.current_page = "vendor_jobs"
                st.rerun()
            
            if st.button("📅 My PPM", use_container_width=True):
                st.session_state.current_page = "vendor_ppm"
                st.rerun()
            
            if st.button("💰 Create Invoice", use_container_width=True):
                st.session_state.current_page = "vendor_invoice"
                st.rerun()
            
            if st.button("📊 Performance", use_container_width=True):
                st.session_state.current_page = "vendor_performance"
                st.rerun()
        
        st.divider()
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            logout()
    
    # Main content area
    try:
        user_role = st.session_state.user['role']
        
        # Facility User Pages
        if user_role == 'facility_user':
            if st.session_state.current_page == "dashboard":
                show_facility_user_dashboard()
            elif st.session_state.current_page == "maintenance_request":
                show_maintenance_request()
            elif st.session_state.current_page == "ppm_management":
                show_ppm_management_facility_user()
            elif st.session_state.current_page == "generator_management":
                show_generator_management_facility_user()
            elif st.session_state.current_page == "space_management":
                show_space_management_facility_user()
            elif st.session_state.current_page == "hse_management":
                show_hse_management_facility_user()
        
        # Facility Manager Pages
        elif user_role == 'facility_manager':
            if st.session_state.current_page == "dashboard":
                show_facility_manager_dashboard()
            elif st.session_state.current_page == "manager_requests":
                show_manager_requests()
            elif st.session_state.current_page == "manager_approvals":
                show_facility_manager_approvals()
            elif st.session_state.current_page == "invoice_management":
                show_invoice_management()
            elif st.session_state.current_page == "vendor_management":
                show_vendor_management()
            elif st.session_state.current_page == "reports_analytics":
                show_reports_analytics()
        
        # Vendor Pages
        elif user_role == 'vendor':
            if st.session_state.current_page == "dashboard":
                show_vendor_dashboard()
            elif st.session_state.current_page == "vendor_jobs":
                show_vendor_jobs()
            elif st.session_state.current_page == "vendor_ppm":
                show_vendor_ppm()
            elif st.session_state.current_page == "vendor_invoice":
                show_vendor_invoice()
            elif st.session_state.current_page == "vendor_performance":
                show_vendor_performance()
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please try refreshing the page or contact support.")

# =============================================
# RUN THE APPLICATION
# =============================================
if __name__ == "__main__":
    main()
