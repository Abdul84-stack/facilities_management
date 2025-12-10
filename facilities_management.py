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
    hourly_counts = df['start_time'].value_counts().sort_index().resetindex()
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

def show_ppm_schedules():
    st.markdown("### 📋 PPM Schedules Overview")
    
    # Status filter buttons
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("All", use_container_width=True):
            st.session_state.ppm_filter = "All"
    with col2:
        if st.button("Not Due", use_container_width=True):
            st.session_state.ppm_filter = "Not Due"
    with col3:
        if st.button("Prepare", use_container_width=True):
            st.session_state.ppm_filter = "Prepare"
    with col4:
        if st.button("Due", use_container_width=True):
            st.session_state.ppm_filter = "Due"
    with col5:
        if st.button("Completed", use_container_width=True):
            st.session_state.ppm_filter = "Completed"
    
    # Get filter from session state
    ppm_filter = st.session_state.get('ppm_filter', 'All')
    
    # Build query based on filter
    query = "SELECT * FROM ppm_schedules"
    params = []
    
    if ppm_filter != "All":
        query += " WHERE status = ?"
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
                        st.session_state.assigning_schedule_id = schedule['id']
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
                    
                    # PDF Download for completed PPM - MOVED OUTSIDE THE FORM
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
    
    # Get all PPM schedules
    schedules = execute_query("SELECT * FROM ppm_schedules")
    
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
    df['next_maintenance_date'] = pd.to_datetime(df['next_maintenance_date'])
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
            
            # Approval buttons - MOVED OUTSIDE OF ANY FORM
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
# GENERATOR RECORDS - FACILITY USER
# =============================================
def show_generator_records_facility_user():
    st.markdown("<h1 class='app-title'>🔌 Generator Daily Records</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📝 New Record", "📋 View Records", "📊 Analytics"])
    
    with tab1:
        show_new_generator_record()
    
    with tab2:
        show_generator_records()
    
    with tab3:
        show_generator_analytics()

def show_new_generator_record():
    st.markdown("### 📝 New Generator Record")
    
    with st.form("generator_record_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            record_date = st.date_input("Record Date *", value=datetime.now())
            generator_type = st.selectbox(
                "Generator Type *",
                ["Standby Generator", "Prime Generator", "Portable Generator", "Other"]
            )
            opening_hours = st.number_input("Opening Hours Reading *", 
                                           min_value=0.0, value=0.0, step=0.1, format="%.1f")
            closing_hours = st.number_input("Closing Hours Reading *", 
                                           min_value=0.0, value=0.0, step=0.1, format="%.1f")
        
        with col2:
            opening_inventory = st.number_input("Opening Inventory (Liters) *", 
                                               min_value=0.0, value=0.0, step=0.1, format="%.1f")
            purchase_liters = st.number_input("Purchase/Delivery (Liters)", 
                                             min_value=0.0, value=0.0, step=0.1, format="%.1f")
            closing_inventory = st.number_input("Closing Inventory (Liters) *", 
                                               min_value=0.0, value=0.0, step=0.1, format="%.1f")
        
        recorded_by = st.text_input("Recorded By *", value=st.session_state.user['username'])
        notes = st.text_area("Notes", placeholder="Any observations, issues, or maintenance notes...")
        
        submitted = st.form_submit_button("💾 Save Record", use_container_width=True)
        
        if submitted:
            # Calculate derived values
            net_hours = float(closing_hours) - float(opening_hours)
            net_diesel_consumed = (float(opening_inventory) + float(purchase_liters)) - float(closing_inventory)
            
            if not all([generator_type, recorded_by]):
                st.error("❌ Please fill in all required fields (*)")
            elif float(closing_hours) < float(opening_hours):
                st.error("❌ Closing hours must be greater than opening hours")
            elif net_diesel_consumed < 0:
                st.error("❌ Diesel consumption cannot be negative. Check your inventory figures.")
            else:
                try:
                    # Direct database connection approach
                    conn = get_connection()
                    cursor = conn.cursor()
                    
                    # Check table structure
                    cursor.execute("PRAGMA table_info(generator_records)")
                    columns = cursor.fetchall()
                    st.info(f"Table columns: {columns}")
                    
                    # Insert the record
                    cursor.execute(
                        '''INSERT INTO generator_records 
                        (record_date, generator_type, opening_hours, closing_hours, net_hours,
                         opening_inventory_liters, purchase_liters, closing_inventory_liters,
                         net_diesel_consumed, recorded_by, notes) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (
                            record_date.strftime('%Y-%m-%d'),
                            str(generator_type),
                            float(opening_hours),
                            float(closing_hours),
                            float(net_hours),
                            float(opening_inventory),
                            float(purchase_liters),
                            float(closing_inventory),
                            float(net_diesel_consumed),
                            str(recorded_by),
                            str(notes) if notes else ""
                        )
                    )
                    
                    conn.commit()
                    conn.close()
                    
                    st.success("✅ Generator record saved successfully!")
                    
                    # Show summary
                    st.markdown("#### 📊 Record Summary")
                    summary_col1, summary_col2 = st.columns(2)
                    with summary_col1:
                        st.write(f"**Net Hours Run:** {net_hours:.1f} hours")
                        st.write(f"**Net Diesel Consumed:** {net_diesel_consumed:.1f} liters")
                    with summary_col2:
                        if net_hours > 0:
                            consumption_rate = net_diesel_consumed / net_hours
                            st.write(f"**Consumption Rate:** {consumption_rate:.2f} liters/hour")
                        st.write(f"**Recorded By:** {recorded_by}")
                    
                    # Clear form by rerunning
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Database error: {str(e)}")
                    
                    # Try to create table if it doesn't exist
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()
                        
                        # Recreate the table with correct structure
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
                        
                        conn.commit()
                        conn.close()
                        
                        st.success("✅ Table structure verified/created. Please try saving again.")
                        
                    except Exception as create_error:
                        st.error(f"❌ Could not create table: {create_error}")

def show_generator_records():
    st.markdown("### 📋 Generator Records History")
    
    # Date range filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", 
                                   value=datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now())
    
    # Generator type filter
    generator_types = execute_query("SELECT DISTINCT generator_type FROM generator_records")
    generator_type_list = ["All"] + [g['generator_type'] for g in generator_types if g['generator_type']]
    
    selected_type = st.selectbox("Filter by Generator Type", generator_type_list)
    
    # Build query
    query = '''
        SELECT * FROM generator_records 
        WHERE record_date BETWEEN ? AND ?
    '''
    params = [start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
    
    if selected_type != "All":
        query += " AND generator_type = ?"
        params.append(selected_type)
    
    query += " ORDER BY record_date DESC"
    
    records = execute_query(query, tuple(params))
    
    if records:
        # Convert to DataFrame for display
        df_data = []
        total_hours = 0
        total_diesel = 0
        
        for record in records:
            net_hours = safe_float(record.get('net_hours'), 0)
            net_diesel = safe_float(record.get('net_diesel_consumed'), 0)
            
            df_data.append({
                "Date": record.get('record_date', ''),
                "Generator Type": record.get('generator_type', ''),
                "Opening Hours": f"{safe_float(record.get('opening_hours'), 0):.1f}",
                "Closing Hours": f"{safe_float(record.get('closing_hours'), 0):.1f}",
                "Net Hours": f"{net_hours:.1f}",
                "Opening Inventory": f"{safe_float(record.get('opening_inventory_liters'), 0):.1f}L",
                "Closing Inventory": f"{safe_float(record.get('closing_inventory_liters'), 0):.1f}L",
                "Net Diesel": f"{net_diesel:.1f}L",
                "Recorded By": record.get('recorded_by', '')
            })
            
            total_hours += net_hours
            total_diesel += net_diesel
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Summary statistics
        st.markdown("#### 📊 Summary Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Records", len(records))
        with col2:
            st.metric("Total Hours Run", f"{total_hours:.1f}")
        with col3:
            st.metric("Total Diesel Used", f"{total_diesel:.1f}L")
        with col4:
            if total_hours > 0:
                avg_consumption = total_diesel / total_hours
                st.metric("Avg Consumption", f"{avg_consumption:.2f}L/hr")
            else:
                st.metric("Avg Consumption", "N/A")
        
        # Export option
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export as CSV",
            data=csv,
            file_name=f"generator_records_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("📭 No generator records found for the selected period")

def show_generator_analytics():
    st.markdown("### 📊 Generator Analytics")
    
    # Get data for the last 90 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    records = execute_query('''
        SELECT * FROM generator_records 
        WHERE record_date BETWEEN ? AND ?
        ORDER BY record_date
    ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
    
    if not records:
        st.info("📭 No generator data available for analytics")
        return
    
    df = pd.DataFrame(records)
    df['record_date'] = pd.to_datetime(df['record_date'])
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_hours = df['net_hours'].sum()
        create_metric_card("Total Hours", f"{total_hours:.0f}", "⏱️")
    
    with col2:
        total_diesel = df['net_diesel_consumed'].sum()
        create_metric_card("Total Diesel", f"{total_diesel:.0f}L", "⛽")
    
    with col3:
        avg_daily_hours = total_hours / len(df['record_date'].unique()) if len(df['record_date'].unique()) > 0 else 0
        create_metric_card("Avg Daily Hours", f"{avg_daily_hours:.1f}", "📈")
    
    with col4:
        if total_hours > 0:
            avg_consumption = total_diesel / total_hours
            create_metric_card("Avg Consumption", f"{avg_consumption:.2f}L/hr", "⚡")
        else:
            create_metric_card("Avg Consumption", "N/A", "⚡")
    
    st.divider()
    
    # Daily hours trend
    st.markdown("#### 📈 Daily Running Hours Trend")
    daily_data = df.groupby('record_date').agg({
        'net_hours': 'sum',
        'net_diesel_consumed': 'sum'
    }).reset_index()
    
    fig1 = px.line(daily_data, x='record_date', y='net_hours',
                   title="Daily Generator Running Hours",
                   labels={'net_hours': 'Hours', 'record_date': 'Date'})
    st.plotly_chart(fig1, use_container_width=True)
    
    # Consumption analysis
    st.markdown("#### ⛽ Diesel Consumption Analysis")
    
    if total_hours > 0:
        # Calculate consumption rate
        daily_data['consumption_rate'] = daily_data['net_diesel_consumed'] / daily_data['net_hours']
        
        fig2 = px.scatter(daily_data, x='net_hours', y='net_diesel_consumed',
                         title="Hours vs Diesel Consumption",
                         labels={'net_hours': 'Running Hours', 'net_diesel_consumed': 'Diesel (L)'},
                         trendline="ols")
        st.plotly_chart(fig2, use_container_width=True)
        
        # Show correlation
        correlation = daily_data['net_hours'].corr(daily_data['net_diesel_consumed'])
        st.write(f"**Correlation between hours and diesel consumption:** {correlation:.3f}")
    
    # Monthly summary
    st.markdown("#### 📅 Monthly Summary")
    df['month'] = df['record_date'].dt.strftime('%Y-%m')
    monthly_data = df.groupby('month').agg({
        'net_hours': 'sum',
        'net_diesel_consumed': 'sum'
    }).reset_index()
    
    fig3 = px.bar(monthly_data, x='month', y=['net_hours', 'net_diesel_consumed'],
                  title="Monthly Hours and Diesel Usage",
                  barmode='group',
                  labels={'value': 'Amount', 'variable': 'Metric'})
    st.plotly_chart(fig3, use_container_width=True)

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
                
                # Show PDF download for completed jobs - MOVED OUTSIDE THE FORM
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
    
    # IMPORTANT FIX: Moved download button OUTSIDE the form
    # The form will only contain input fields and the submit button
    
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
                            # Show download button AFTER successful submission (outside form)
                            st.markdown("---")
                            st.markdown("### 📄 Invoice PDF Download")
                            pdf_buffer = create_invoice_pdf(invoice_id)
                            if pdf_buffer:
                                st.download_button(
                                    label="📥 Download Invoice PDF",
                                    data=pdf_buffer,
                                    file_name=f"invoice_{invoice_number}.pdf",
                                    mime="application/pdf",
                                    key=f"invoice_download_{invoice_id}"
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
                
                # Update status - MOVED OUTSIDE ANY FORM
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
                
                # Show PDF download for completed PPM - MOVED OUTSIDE ANY FORM
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
    
    # FIXED: Safe date parsing
    if not df_invoices.empty and 'invoice_date' in df_invoices.columns:
        try:
            # Try to parse dates with error handling
            df_invoices['invoice_date'] = pd.to_datetime(df_invoices['invoice_date'], errors='coerce')
            # Fill NaT with today's date
            df_invoices['invoice_date'] = df_invoices['invoice_date'].fillna(pd.Timestamp.now())
        except Exception as e:
            st.warning(f"⚠️ Could not parse some invoice dates: {e}")
            df_invoices['invoice_date'] = pd.Timestamp.now()
    
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
        if not df_invoices.empty and 'total_amount' in df_invoices.columns:
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
                # Filter out rows with invalid dates
                completed_df = completed_df.dropna(subset=['created_date', 'completed_date'])
                if not completed_df.empty:
                    completed_df['completion_time'] = (completed_df['completed_date'] - completed_df['created_date']).dt.days
                    avg_time = completed_df['completion_time'].mean()
                    create_metric_card("Avg Time", f"{avg_time:.1f} days", "⏱️")
                else:
                    create_metric_card("Avg Time", "N/A", "⏱️")
            except Exception as e:
                create_metric_card("Avg Time", "N/A", "⏱️")
        else:
            create_metric_card("Avg Time", "N/A", "⏱️")
    
    st.divider()
    
    # Monthly job completion trend
    st.markdown("#### 📈 Monthly Performance")
    
    if not df_jobs.empty and 'created_date' in df_jobs.columns:
        try:
            df_jobs['created_date'] = pd.to_datetime(df_jobs['created_date'], errors='coerce')
            # Filter out rows with invalid dates
            df_jobs_clean = df_jobs.dropna(subset=['created_date'])
            if not df_jobs_clean.empty:
                df_jobs_clean['month'] = df_jobs_clean['created_date'].dt.strftime('%Y-%m')
                
                monthly_stats = df_jobs_clean.groupby('month').agg({
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
            else:
                st.info("📭 No valid date data available for monthly analysis")
        except Exception as e:
            st.warning(f"⚠️ Could not generate monthly chart: {e}")
    
    # Revenue trend if invoices exist
    if not df_invoices.empty and 'invoice_date' in df_invoices.columns and 'total_amount' in df_invoices.columns:
        st.markdown("#### 💰 Revenue Trend")
        
        try:
            # Filter out rows with invalid dates
            df_invoices_clean = df_invoices.dropna(subset=['invoice_date'])
            if not df_invoices_clean.empty:
                df_invoices_clean['month'] = df_invoices_clean['invoice_date'].dt.strftime('%Y-%m')
                
                monthly_revenue = df_invoices_clean.groupby('month')['total_amount'].sum().reset_index()
                
                fig2 = px.line(monthly_revenue, x='month', y='total_amount',
                               title="Monthly Revenue",
                               markers=True,
                               labels={'total_amount': 'Revenue (₦)', 'month': 'Month'})
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("📭 No valid invoice date data available for revenue analysis")
        except Exception as e:
            st.warning(f"⚠️ Could not generate revenue chart: {e}")

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
# FACILITY MANAGER DASHBOARD - ENHANCED
# =============================================
def show_facility_manager_dashboard():
    st.markdown("<h1 class='app-title'>👨‍💼 Facility Manager Dashboard</h1>", unsafe_allow_html=True)
    
    # Comprehensive metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Get statistics
    total_requests = execute_query('SELECT COUNT(*) as count FROM maintenance_requests')
    total_count = total_requests[0]['count'] if total_requests else 0
    
    pending_requests = execute_query("SELECT COUNT(*) as count FROM maintenance_requests WHERE status = 'Pending'")
    pending_count = pending_requests[0]['count'] if pending_requests else 0
    
    completed_requests = execute_query("SELECT COUNT(*) as count FROM maintenance_requests WHERE status = 'Completed'")
    completed_count = completed_requests[0]['count'] if completed_requests else 0
    
    approved_requests = execute_query("SELECT COUNT(*) as count FROM maintenance_requests WHERE status = 'Approved'")
    approved_count = approved_requests[0]['count'] if approved_requests else 0
    
    with col1:
        create_metric_card("Total Requests", total_count, "📋")
    with col2:
        create_metric_card("Pending", pending_count, "⏳")
    with col3:
        create_metric_card("Completed", completed_count, "✅")
    with col4:
        create_metric_card("Approved", approved_count, "🏆")
    
    st.divider()
    
    # Advanced tabs for manager
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Dashboard", "✅ Approvals", "👥 Vendor Management", "📅 PPM Overview", 
        "🔌 Generator Records", "🛡️ HSE Overview", "🏢 Space Management"
    ])
    
    with tab1:
        show_manager_dashboard()
    
    with tab2:
        show_manager_approvals()
    
    with tab3:
        show_vendor_management()
    
    with tab4:
        show_manager_ppm_overview()
    
    with tab5:
        show_manager_generator_records()
    
    with tab6:
        show_manager_hse_overview()
    
    with tab7:
        show_manager_space_management()

def show_manager_dashboard():
    st.markdown("### 📊 Comprehensive Analytics Dashboard")
    
    # Get all data
    requests = execute_query('SELECT * FROM maintenance_requests')
    ppm_schedules = execute_query('SELECT * FROM ppm_schedules')
    generator_records = execute_query('SELECT * FROM generator_records')
    
    if not requests:
        st.info("📭 No data available for dashboard")
        return
    
    # Convert to DataFrames
    df_requests = pd.DataFrame(requests)
    df_ppm = pd.DataFrame(ppm_schedules) if ppm_schedules else pd.DataFrame()
    df_generator = pd.DataFrame(generator_records) if generator_records else pd.DataFrame()
    
    # Request analysis
    st.markdown("#### 📈 Request Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Status distribution
        status_counts = df_requests['status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        
        fig1 = px.pie(status_counts, values='Count', names='Status',
                      title="Request Status Distribution",
                      hole=0.3)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Priority distribution
        priority_counts = df_requests['priority'].value_counts().reset_index()
        priority_counts.columns = ['Priority', 'Count']
        
        fig2 = px.bar(priority_counts, x='Priority', y='Count',
                      title="Requests by Priority",
                      color='Priority',
                      color_discrete_sequence=px.colors.sequential.Reds)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Monthly trend
    st.markdown("#### 📅 Monthly Request Trend")
    
    if 'created_date' in df_requests.columns:
        df_requests['created_date'] = pd.to_datetime(df_requests['created_date'])
        df_requests['month'] = df_requests['created_date'].dt.strftime('%Y-%m')
        
        monthly_requests = df_requests.groupby('month').size().reset_index(name='Count')
        
        fig3 = px.line(monthly_requests, x='month', y='Count',
                       title="Monthly Request Volume",
                       markers=True)
        st.plotly_chart(fig3, use_container_width=True)
    
    # Vendor performance if PPM data exists
    if not df_ppm.empty:
        st.markdown("#### 👷 Vendor Performance (PPM)")
        
        vendor_performance = df_ppm.groupby('assigned_vendor').agg({
            'id': 'count',
            'status': lambda x: (x == 'Completed').sum()
        }).reset_index()
        
        vendor_performance.columns = ['Vendor', 'Total Assignments', 'Completed']
        vendor_performance['Completion Rate'] = (vendor_performance['Completed'] / vendor_performance['Total Assignments'] * 100).round(1)
        
        fig4 = px.bar(vendor_performance, x='Vendor', y='Completion Rate',
                      title="Vendor PPM Completion Rate",
                      color='Completion Rate',
                      color_continuous_scale='viridis')
        st.plotly_chart(fig4, use_container_width=True)
    
    # Generator efficiency if data exists
    if not df_generator.empty and 'net_hours' in df_generator.columns and 'net_diesel_consumed' in df_generator.columns:
        st.markdown("#### ⚡ Generator Efficiency Analysis")
        
        # Calculate efficiency
        df_generator['efficiency'] = df_generator['net_hours'] / df_generator['net_diesel_consumed'] if df_generator['net_diesel_consumed'].sum() > 0 else 0
        
        fig5 = px.scatter(df_generator, x='net_hours', y='net_diesel_consumed',
                         title="Generator Hours vs Diesel Consumption",
                         trendline="ols")
        st.plotly_chart(fig5, use_container_width=True)

def show_manager_approvals():
    st.markdown("### ✅ Approval Queue")
    
    tab1, tab2 = st.tabs(["📋 Maintenance Requests", "📅 PPM Schedules"])
    
    with tab1:
        show_maintenance_request_approvals()
    
    with tab2:
        show_ppm_manager_approvals()

def show_maintenance_request_approvals():
    """Manager approval for maintenance requests"""
    # Get requests awaiting manager approval
    approval_requests = get_requests_for_manager_approval()
    
    if approval_requests:
        for request in approval_requests:
            with st.expander(f"📋 {request['title']} - {request['created_by']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Location:** {request['location']}")
                    st.write(f"**Facility Type:** {request['facility_type']}")
                    st.write(f"**Priority:** {request['priority']}")
                    st.write(f"**Assigned Vendor:** {request['assigned_vendor']}")
                
                with col2:
                    st.write(f"**Created Date:** {request['created_date']}")
                    st.write(f"**Completed Date:** {request['completed_date']}")
                    st.write(f"**Department Approved:** {request['department_approval_date']}")
                
                st.write(f"**Description:** {request['description']}")
                
                if request['completion_notes']:
                    st.write(f"**Completion Notes:** {request['completion_notes']}")
                
                if request['job_breakdown']:
                    st.write(f"**Job Breakdown:** {request['job_breakdown']}")
                
                # Invoice information if available
                invoice = execute_query(
                    'SELECT * FROM invoices WHERE request_id = ?',
                    (request['id'],)
                )
                
                if invoice:
                    st.markdown("#### 💰 Invoice Details")
                    inv = invoice[0]
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Material Cost", format_ngn(inv['amount']))
                    with col2:
                        st.metric("Labour Charges", format_ngn(inv['labour_charge']))
                    with col3:
                        st.metric("VAT", format_ngn(inv['vat_amount']))
                    with col4:
                        st.metric("Total", format_ngn(inv['total_amount']))
                
                # PDF Download - MOVED OUTSIDE ANY FORM
                pdf_buffer = create_maintenance_pdf_report(request['id'])
                if pdf_buffer:
                    st.download_button(
                        label="📥 Download Job Report",
                        data=pdf_buffer,
                        file_name=f"job_report_{request['id']}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        key=f"manager_pdf_{request['id']}"
                    )
                
                # Approval buttons - MOVED OUTSIDE ANY FORM
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✅ Approve", key=f"manager_approve_{request['id']}", 
                               use_container_width=True):
                        success = execute_update(
                            '''UPDATE maintenance_requests 
                            SET facilities_manager_approval = 1, 
                                status = 'Approved',
                                manager_approval_date = ?
                            WHERE id = ?''',
                            (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), request['id'])
                        )
                        
                        if success and invoice:
                            # Update invoice status
                            execute_update(
                                "UPDATE invoices SET status = 'Approved' WHERE request_id = ?",
                                (request['id'],)
                            )
                        
                        st.success("✅ Request approved successfully!")
                        st.rerun()
                
                with col2:
                    if st.button("❌ Reject", key=f"manager_reject_{request['id']}", 
                               use_container_width=True, type="secondary"):
                        reject_reason = st.text_input(
                            "Rejection Reason", 
                            key=f"manager_reject_reason_{request['id']}",
                            placeholder="Please provide reason for rejection..."
                        )
                        
                        if reject_reason:
                            success = execute_update(
                                '''UPDATE maintenance_requests 
                                SET facilities_manager_approval = 0, 
                                    status = 'Rejected',
                                    completion_notes = ?
                                WHERE id = ?''',
                                (f"Rejected by Manager: {reject_reason}", request['id'])
                            )
                            st.success("✅ Request rejected")
                            st.rerun()
    else:
        st.info("📭 No requests awaiting manager approval")

def show_ppm_manager_approvals():
    """Manager approval for PPM schedules"""
    # Get PPM schedules that need manager approval
    ppm_schedules = get_ppm_for_manager_approval()
    
    if not ppm_schedules:
        st.info("📭 No PPM schedules awaiting manager approval")
        return
    
    for schedule in ppm_schedules:
        with st.expander(f"📋 {schedule['schedule_name']} - Completed: {schedule['actual_completion_date']}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Facility:** {schedule['facility_category']}")
                st.write(f"**Sub-Category:** {schedule['sub_category']}")
                st.write(f"**Frequency:** {schedule['frequency']}")
                st.write(f"**Assigned Vendor:** {schedule['assigned_vendor']}")
            
            with col2:
                st.write(f"**Estimated Cost:** {format_ngn(schedule['estimated_cost'])}")
                st.write(f"**Actual Cost:** {format_ngn(schedule['actual_cost']) if schedule['actual_cost'] else 'N/A'}")
                st.write(f"**Completed Date:** {schedule['actual_completion_date']}")
                st.write(f"**User Approved:** {'Yes' if schedule['user_approved'] else 'No'}")
            
            st.write(f"**Description:** {schedule['description']}")
            
            if schedule['notes']:
                st.write(f"**Notes:** {schedule['notes']}")
            
            # Get assignment details
            assignment = execute_query(
                'SELECT * FROM ppm_assignments WHERE schedule_id = ?',
                (schedule['id'],)
            )
            
            if assignment:
                assignment = assignment[0]
                st.write(f"**Completion Notes:** {assignment['completion_notes']}")
            
            # PDF Download - MOVED OUTSIDE ANY FORM
            pdf_buffer = create_ppm_pdf_report(schedule['id'])
            if pdf_buffer:
                st.download_button(
                    label="📥 Download PPM Report",
                    data=pdf_buffer,
                    file_name=f"ppm_report_{schedule['id']}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    key=f"manager_ppm_pdf_{schedule['id']}"
                )
            
            # Approval buttons - MOVED OUTSIDE ANY FORM
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Final Approve PPM", key=f"manager_approve_ppm_{schedule['id']}", 
                           use_container_width=True):
                    execute_update(
                        "UPDATE ppm_schedules SET manager_approved = 1 WHERE id = ?",
                        (schedule['id'],)
                    )
                    st.success("✅ PPM finally approved!")
                    st.rerun()
            
            with col2:
                if st.button("❌ Request Changes", key=f"manager_reject_ppm_{schedule['id']}", 
                           use_container_width=True, type="secondary"):
                    changes_reason = st.text_input(
                        "Required Changes",
                        key=f"ppm_changes_{schedule['id']}",
                        placeholder="What changes are required?"
                    )
                    if changes_reason:
                        execute_update(
                            '''UPDATE ppm_schedules SET status = 'WIP' WHERE id = ?''',
                            (schedule['id'],)
                        )
                        st.success("✅ Changes requested")
                        st.rerun()

def show_vendor_management():
    st.markdown("### 👥 Vendor Management")
    
    # Get all vendors
    vendors = execute_query('SELECT * FROM vendors ORDER BY company_name')
    
    if vendors:
        # Vendor metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_vendors = len(vendors)
        active_vendors = execute_query(
            "SELECT COUNT(DISTINCT assigned_vendor) as count FROM maintenance_requests WHERE assigned_vendor IS NOT NULL"
        )
        active_count = active_vendors[0]['count'] if active_vendors else 0
        
        with col1:
            create_metric_card("Total Vendors", total_vendors, "🏢")
        with col2:
            create_metric_card("Active Vendors", active_count, "👷")
        with col3:
            vendor_types = len(set(v['vendor_type'] for v in vendors))
            create_metric_card("Vendor Types", vendor_types, "📊")
        with col4:
            # Calculate average rating (placeholder)
            create_metric_card("Avg Rating", "4.2/5", "⭐")
        
        # Vendor list
        st.markdown("#### 📋 Vendor List")
        for vendor in vendors:
            with st.expander(f"{vendor['company_name']} - {vendor['vendor_type']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Contact:** {vendor['contact_person']}")
                    st.write(f"**Email:** {vendor['email']}")
                    st.write(f"**Phone:** {vendor['phone']}")
                    st.write(f"**TIN:** {vendor['tax_identification_number']}")
                
                with col2:
                    st.write(f"**RC Number:** {vendor['rc_number']}")
                    st.write(f"**Annual Turnover:** {format_ngn(vendor['annual_turnover'])}")
                    st.write(f"**Username:** {vendor['username']}")
                    st.write(f"**Registered:** {vendor['registration_date']}")
                
                st.write(f"**Services:** {vendor['services_offered']}")
                st.write(f"**Address:** {vendor['address']}")
                
                # Performance stats
                st.markdown("##### 📊 Performance Statistics")
                
                # Get vendor performance data
                assigned_jobs = execute_query(
                    'SELECT COUNT(*) as count FROM maintenance_requests WHERE assigned_vendor = ?',
                    (vendor['username'],)
                )
                assigned_count = assigned_jobs[0]['count'] if assigned_jobs else 0
                
                completed_jobs = execute_query(
                    'SELECT COUNT(*) as count FROM maintenance_requests WHERE assigned_vendor = ? AND status = ?',
                    (vendor['username'], 'Completed')
                )
                completed_count = completed_jobs[0]['count'] if completed_jobs else 0
                
                total_invoices = execute_query(
                    'SELECT SUM(total_amount) as total FROM invoices WHERE vendor_username = ? AND status = ?',
                    (vendor['username'], 'Approved')
                )
                total_amount = total_invoices[0]['total'] if total_invoices and total_invoices[0]['total'] else 0
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Assigned Jobs", assigned_count)
                with col2:
                    completion_rate = (completed_count / assigned_count * 100) if assigned_count > 0 else 0
                    st.metric("Completion Rate", f"{completion_rate:.1f}%")
                with col3:
                    st.metric("Total Revenue", format_ngn(total_amount))
                
                # Action buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📧 Contact Vendor", key=f"contact_{vendor['id']}"):
                        st.info(f"Email: {vendor['email']} | Phone: {vendor['phone']}")
                with col2:
                    if st.button("📋 View Jobs", key=f"jobs_{vendor['id']}"):
                        vendor_jobs = execute_query(
                            'SELECT * FROM maintenance_requests WHERE assigned_vendor = ? ORDER BY created_date DESC',
                            (vendor['username'],)
                        )
                        
                        if vendor_jobs:
                            st.markdown("##### 📋 Recent Jobs")
                            for job in vendor_jobs[:5]:  # Show last 5 jobs
                                st.write(f"- {job['title']} ({job['status']}) - {job['created_date']}")
    
    else:
        st.info("📭 No vendors found")
    
    # Add new vendor section
    st.markdown("---")
    st.markdown("#### ➕ Register New Vendor")
    
    with st.form("new_vendor_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_company = st.text_input("Company Name *")
            new_contact = st.text_input("Contact Person *")
            new_email = st.text_input("Email *")
            new_phone = st.text_input("Phone *")
            new_vendor_type = st.selectbox(
                "Vendor Type *",
                ["HVAC", "Generator", "Fixture and Fittings", "Building Maintenance", 
                 "Plumbing", "Electrical", "Cleaning", "HSE", "Space Management"]
            )
        
        with col2:
            new_turnover = st.number_input("Annual Turnover (₦)", min_value=0.0, value=0.0, step=10000.0)
            new_tin = st.text_input("Tax Identification Number")
            new_rc = st.text_input("RC Number")
            new_username = st.text_input("Username *", placeholder="Vendor login username")
            new_password = st.text_input("Temporary Password *", type="password", value="0123456")
        
        new_services = st.text_area("Services Offered *", height=80)
        new_address = st.text_area("Address *", height=80)
        new_certification = st.text_area("Certifications", height=60)
        
        submitted = st.form_submit_button("➕ Register Vendor", use_container_width=True)
        
        if submitted:
            if not all([new_company, new_contact, new_email, new_phone, new_vendor_type, 
                       new_username, new_password, new_services, new_address]):
                st.error("❌ Please fill in all required fields (*)")
            else:
                # Check if username exists
                existing_user = execute_query(
                    'SELECT * FROM users WHERE username = ?',
                    (new_username,)
                )
                
                if existing_user:
                    st.error("❌ Username already exists")
                else:
                    # Create user account
                    user_success = execute_update(
                        'INSERT INTO users (username, password_hash, role, vendor_type) VALUES (?, ?, ?, ?)',
                        (new_username, new_password, 'vendor', new_vendor_type)
                    )
                    
                    if user_success:
                        # Create vendor record
                        vendor_success = execute_update(
                            '''INSERT INTO vendors 
                            (username, company_name, contact_person, email, phone, 
                             vendor_type, services_offered, annual_turnover, 
                             tax_identification_number, rc_number, address, certification) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            (new_username, new_company, new_contact, new_email, new_phone,
                             new_vendor_type, new_services, new_turnover, new_tin,
                             new_rc, new_address, new_certification)
                        )
                        
                        if vendor_success:
                            st.success("✅ Vendor registered successfully!")
                            st.info(f"**Login Credentials:** Username: {new_username} | Password: {new_password}")
                            st.rerun()
                        else:
                            st.error("❌ Failed to create vendor record")
                    else:
                        st.error("❌ Failed to create user account")

def show_manager_ppm_overview():
    st.markdown("### 📅 PPM Overview & Management")
    
    # Get all PPM schedules
    schedules = execute_query('SELECT * FROM ppm_schedules ORDER BY next_maintenance_date')
    
    if schedules:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_ppm = len(schedules)
        due_ppm = len([s for s in schedules if s['status'] == 'Due'])
        prepare_ppm = len([s for s in schedules if s['status'] == 'Prepare'])
        completed_ppm = len([s for s in schedules if s['status'] == 'Completed'])
        
        with col1:
            create_metric_card("Total PPM", total_ppm, "📅")
        with col2:
            create_metric_card("Due Now", due_ppm, "⚠️")
        with col3:
            create_metric_card("To Prepare", prepare_ppm, "📋")
        with col4:
            create_metric_card("Completed", completed_ppm, "✅")
        
        # Filter options
        st.markdown("#### 🔍 Filter PPM Schedules")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            facility_filter = st.selectbox(
                "Facility Category",
                ["All"] + sorted(list(set(s['facility_category'] for s in schedules if s['facility_category'])))
            )
        
        with col2:
            status_filter = st.selectbox(
                "Status",
                ["All", "Not Due", "Prepare", "Due", "WIP", "Completed", "Approved"]
            )
        
        with col3:
            vendor_filter = st.selectbox(
                "Assigned Vendor",
                ["All"] + sorted(list(set(s['assigned_vendor'] for s in schedules if s['assigned_vendor'])))
            )
        
        # Apply filters
        filtered_schedules = schedules
        
        if facility_filter != "All":
            filtered_schedules = [s for s in filtered_schedules if s['facility_category'] == facility_filter]
        
        if status_filter != "All":
            filtered_schedules = [s for s in filtered_schedules if s['status'] == status_filter]
        
        if vendor_filter != "All":
            filtered_schedules = [s for s in filtered_schedules if s['assigned_vendor'] == vendor_filter]
        
        # Display filtered schedules
        st.markdown(f"#### 📋 PPM Schedules ({len(filtered_schedules)} found)")
        
        for schedule in filtered_schedules:
            status_colors = {
                "Not Due": "status-not-due",
                "Prepare": "status-prepare", 
                "Due": "status-due",
                "WIP": "status-wip",
                "Completed": "status-completed",
                "Approved": "status-approved"
            }
            
            status_class = status_colors.get(schedule['status'], "")
            
            with st.expander(f"{schedule['schedule_name']} - {schedule['next_maintenance_date']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Facility:** {schedule['facility_category']}")
                    st.write(f"**Sub-Category:** {schedule['sub_category']}")
                    st.write(f"**Frequency:** {schedule['frequency']}")
                    st.write(f"**Created By:** {schedule['created_by']}")
                
                with col2:
                    st.write(f"**Status:** <span class='{status_class}'>{schedule['status']}</span>", unsafe_allow_html=True)
                    st.write(f"**Assigned Vendor:** {schedule['assigned_vendor'] or 'Not assigned'}")
                    st.write(f"**Next Due:** {schedule['next_maintenance_date']}")
                    if schedule['estimated_cost']:
                        st.write(f"**Est. Cost:** {format_ngn(schedule['estimated_cost'])}")
                
                st.write(f"**Description:** {schedule['description']}")
                
                # Management actions - MOVED OUTSIDE ANY FORM
                if schedule['status'] in ['Prepare', 'Due'] and not schedule['assigned_vendor']:
                    st.markdown("---")
                    st.markdown("##### 👷 Assign to Vendor")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        vendors = execute_query(
                            'SELECT * FROM vendors WHERE vendor_type = ? OR vendor_type LIKE ?',
                            (schedule['facility_category'], f'%{schedule['facility_category']}%')
                        )
                        
                        vendor_options = ["Select vendor..."] + [f"{v['company_name']} ({v['username']})" for v in vendors]
                        selected_vendor = st.selectbox("Choose Vendor", vendor_options, key=f"vendor_select_{schedule['id']}")
                    
                    with col2:
                        due_date = st.date_input("Due Date", 
                                                value=datetime.strptime(schedule['next_maintenance_date'], '%Y-%m-%d'),
                                                key=f"due_date_{schedule['id']}")
                    
                    if st.button("✅ Assign", key=f"assign_{schedule['id']}"):
                        if selected_vendor != "Select vendor...":
                            vendor_username = selected_vendor.split('(')[-1].strip(')')
                            
                            # Update PPM schedule
                            execute_update(
                                '''UPDATE ppm_schedules 
                                SET assigned_vendor = ?, status = 'WIP' 
                                WHERE id = ?''',
                                (vendor_username, schedule['id'])
                            )
                            
                            # Create assignment record
                            execute_update(
                                '''INSERT INTO ppm_assignments 
                                (schedule_id, vendor_username, assigned_date, due_date, assigned_by) 
                                VALUES (?, ?, ?, ?, ?)''',
                                (schedule['id'], vendor_username, 
                                 datetime.now().strftime('%Y-%m-%d'),
                                 due_date.strftime('%Y-%m-%d'),
                                 st.session_state.user['username'])
                            )
                            
                            st.success("✅ PPM assigned to vendor successfully!")
                            st.rerun()
                
                # PDF Download for completed PPM - MOVED OUTSIDE ANY FORM
                if schedule['status'] == 'Completed':
                    pdf_buffer = create_ppm_pdf_report(schedule['id'])
                    if pdf_buffer:
                        st.download_button(
                            label="📥 Download PPM Report",
                            data=pdf_buffer,
                            file_name=f"ppm_report_{schedule['id']}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            key=f"manager_ppm_pdf_dl_{schedule['id']}"
                        )
    else:
        st.info("📭 No PPM schedules found")

def show_manager_generator_records():
    st.markdown("### 🔌 Generator Records Overview")
    
    # Date range filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", 
                                   value=datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now())
    
    # Get generator records
    records = execute_query('''
        SELECT * FROM generator_records 
        WHERE record_date BETWEEN ? AND ?
        ORDER BY record_date DESC
    ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
    
    if records:
        # Summary statistics
        total_hours = sum(safe_float(r.get('net_hours'), 0) for r in records)
        total_diesel = sum(safe_float(r.get('net_diesel_consumed'), 0) for r in records)
        avg_consumption = total_diesel / total_hours if total_hours > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            create_metric_card("Total Records", len(records), "📋")
        with col2:
            create_metric_card("Total Hours", f"{total_hours:.1f}", "⏱️")
        with col3:
            create_metric_card("Total Diesel", f"{total_diesel:.1f}L", "⛽")
        with col4:
            create_metric_card("Avg Rate", f"{avg_consumption:.2f}L/hr", "⚡")
        
        # Display records
        st.markdown("#### 📋 Recent Records")
        
        df_data = []
        for record in records[:10]:  # Show last 10 records
            net_hours = safe_float(record.get('net_hours'), 0)
            net_diesel = safe_float(record.get('net_diesel_consumed'), 0)
            
            df_data.append({
                "Date": record.get('record_date', ''),
                "Generator Type": record.get('generator_type', ''),
                "Hours Run": f"{net_hours:.1f}",
                "Diesel Used": f"{net_diesel:.1f}L",
                "Rate": f"{net_diesel / net_hours:.2f}L/hr" if net_hours > 0 else "N/A",
                "Recorded By": record.get('recorded_by', '')
            })
        
        if df_data:
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Export option
        all_data = []
        for record in records:
            all_data.append({
                "Date": record.get('record_date', ''),
                "Generator Type": record.get('generator_type', ''),
                "Opening Hours": safe_float(record.get('opening_hours'), 0),
                "Closing Hours": safe_float(record.get('closing_hours'), 0),
                "Net Hours": safe_float(record.get('net_hours'), 0),
                "Opening Inventory (L)": safe_float(record.get('opening_inventory_liters'), 0),
                "Purchase (L)": safe_float(record.get('purchase_liters'), 0),
                "Closing Inventory (L)": safe_float(record.get('closing_inventory_liters'), 0),
                "Net Diesel (L)": safe_float(record.get('net_diesel_consumed'), 0),
                "Recorded By": record.get('recorded_by', ''),
                "Notes": record.get('notes', '')
            })
        
        df_all = pd.DataFrame(all_data)
        csv = df_all.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 Export All Records (CSV)",
            data=csv,
            file_name=f"generator_records_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("📭 No generator records found for the selected period")

def show_manager_hse_overview():
    st.markdown("### 🛡️ HSE Management Overview")
    
    # Get HSE data
    schedules = execute_query('SELECT * FROM hse_schedules ORDER BY next_due_date')
    incidents = execute_query('SELECT * FROM hse_incidents ORDER BY incident_date DESC')
    inspections = execute_query('SELECT * FROM hse_inspections ORDER BY inspection_date DESC')
    
    # HSE Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_metric_card("HSE Schedules", len(schedules), "📅")
    with col2:
        create_metric_card("Incidents", len(incidents), "⚠️")
    with col3:
        open_incidents = len([i for i in incidents if i['status'] == 'Open'])
        create_metric_card("Open Incidents", open_incidents, "🔴")
    with col4:
        create_metric_card("Inspections", len(inspections), "🔍")
    
    # Tabs for different HSE aspects
    tab1, tab2, tab3 = st.tabs(["📅 Schedules", "⚠️ Incidents", "🔍 Inspections"])
    
    with tab1:
        if schedules:
            for schedule in schedules[:10]:  # Show first 10
                with st.expander(f"{schedule['schedule_type']} - Due: {schedule['next_due_date']}"):
                    st.write(f"**Frequency:** {schedule['frequency']}")
                    st.write(f"**Responsible:** {schedule['responsible_person'] or 'Not assigned'}")
                    st.write(f"**Status:** {schedule['status']}")
                    st.write(f"**Description:** {schedule['description']}")
        else:
            st.info("📭 No HSE schedules found")
    
    with tab2:
        if incidents:
            # Incident severity breakdown
            severity_counts = {}
            for incident in incidents:
                severity = incident['severity']
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Display severity summary
            st.markdown("##### 🎯 Incident Severity Breakdown")
            cols = st.columns(len(severity_counts))
            for idx, (severity, count) in enumerate(severity_counts.items()):
                with cols[idx]:
                    create_metric_card(severity, count, "⚠️")
            
            # Recent incidents
            st.markdown("##### 📋 Recent Incidents")
            for incident in incidents[:5]:
                severity_icon = {
                    "Low": "🟢",
                    "Medium": "🟡",
                    "High": "🟠", 
                    "Critical": "🔴"
                }.get(incident['severity'], "⚪")
                
                st.write(f"{severity_icon} **{incident['incident_type']}** - {incident['incident_date']}")
                st.write(f"Location: {incident['location']} | Status: {incident['status']}")
                st.write(f"Reported by: {incident['reported_by']}")
                st.divider()
        else:
            st.info("📭 No incident reports found")
    
    with tab3:
        if inspections:
            for inspection in inspections[:5]:  # Show first 5
                with st.expander(f"{inspection['inspection_type']} - {inspection['inspection_date']}"):
                    st.write(f"**Inspector:** {inspection['inspector_name']}")
                    st.write(f"**Area:** {inspection['area_inspected']}")
                    st.write(f"**Status:** {inspection['status']}")
                    st.write(f"**Findings:** {inspection['findings'][:200]}..." if len(inspection['findings']) > 200 else f"**Findings:** {inspection['findings']}")
        else:
            st.info("📭 No inspection reports found")

def show_manager_space_management():
    st.markdown("### 🏢 Space Management Overview")
    
    # Get booking data
    bookings = execute_query('''
        SELECT * FROM room_bookings 
        ORDER BY booking_date DESC, start_time
    ''')
    
    if bookings:
        # Space metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_bookings = len(bookings)
        today = datetime.now().strftime('%Y-%m-%d')
        today_bookings = len([b for b in bookings if b['booking_date'] == today])
        unique_rooms = len(set(b['room_name'] for b in bookings))
        avg_attendees = sum(b['attendees_count'] or 0 for b in bookings) / total_bookings if total_bookings > 0 else 0
        
        with col1:
            create_metric_card("Total Bookings", total_bookings, "📅")
        with col2:
            create_metric_card("Today's Bookings", today_bookings, "📋")
        with col3:
            create_metric_card("Rooms Used", unique_rooms, "🏢")
        with col4:
            create_metric_card("Avg Attendees", f"{avg_attendees:.0f}", "👥")
        
        # Room utilization
        st.markdown("#### 📊 Room Utilization")
        
        # Group by room
        room_stats = {}
        for booking in bookings:
            room = booking['room_name']
            if room not in room_stats:
                room_stats[room] = {
                    'bookings': 0,
                    'attendees': 0,
                    'types': set()
                }
            room_stats[room]['bookings'] += 1
            room_stats[room]['attendees'] += (booking['attendees_count'] or 0)
            room_stats[room]['types'].add(booking['room_type'])
        
        # Display room statistics
        room_data = []
        for room, stats in room_stats.items():
            room_data.append({
                'Room': room,
                'Bookings': stats['bookings'],
                'Avg Attendees': stats['attendees'] / stats['bookings'] if stats['bookings'] > 0 else 0,
                'Room Types': ', '.join(stats['types'])
            })
        
        if room_data:
            df_rooms = pd.DataFrame(room_data)
            st.dataframe(df_rooms, use_container_width=True, hide_index=True)
        
        # Upcoming bookings
        st.markdown("#### 📅 Upcoming Bookings (Next 7 Days)")
        
        upcoming_date = datetime.now() + timedelta(days=7)
        upcoming_bookings = [b for b in bookings 
                           if b['booking_date'] >= today 
                           and b['booking_date'] <= upcoming_date.strftime('%Y-%m-%d')
                           and b['status'] == 'Confirmed']
        
        if upcoming_bookings:
            for booking in sorted(upcoming_bookings, key=lambda x: (x['booking_date'], x['start_time']))[:10]:
                st.write(f"**{booking['room_name']}** - {booking['booking_date']} {booking['start_time']}-{booking['end_time']}")
                st.write(f"Booked by: {booking['booked_by']} | Attendees: {booking['attendees_count']}")
                st.write(f"Purpose: {booking['purpose'][:100]}..." if len(booking['purpose']) > 100 else f"Purpose: {booking['purpose']}")
                st.divider()
        else:
            st.info("📭 No upcoming bookings in the next 7 days")
    else:
        st.info("📭 No booking data available")

# =============================================
# FACILITY USER DASHBOARD - ENHANCED
# =============================================
def show_facility_user_dashboard():
    st.markdown("<h1 class='app-title'>👤 Facility User Dashboard</h1>", unsafe_allow_html=True)
    
    user_info = st.session_state.user
    username = user_info['username']
    
    # User-specific metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Get user statistics
    user_requests = get_user_requests(username)
    pending_requests = [r for r in user_requests if r['status'] == 'Pending']
    completed_requests = [r for r in user_requests if r['status'] == 'Completed']
    approved_requests = [r for r in user_requests if r['status'] == 'Approved']
    
    with col1:
        create_metric_card("My Requests", len(user_requests), "📋")
    with col2:
        create_metric_card("Pending", len(pending_requests), "⏳")
    with col3:
        create_metric_card("Completed", len(completed_requests), "✅")
    with col4:
        create_metric_card("Approved", len(approved_requests), "🏆")
    
    # Enhanced tabs for facility user
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🏠 Dashboard", "➕ New Request", "📋 My Requests", "📅 PPM", "🔌 Generator", 
        "🛡️ HSE", "🏢 Space Management"
    ])
    
    with tab1:
        show_user_dashboard(username, user_requests)
    
    with tab2:
        show_new_request(username)
    
    with tab3:
        show_user_requests_view(username)
    
    with tab4:
        show_ppm_management_facility_user()
    
    with tab5:
        show_generator_records_facility_user()
    
    with tab6:
        show_hse_management_facility_user()
    
    with tab7:
        show_space_management_facility_user()

def show_user_dashboard(username, user_requests):
    st.markdown("### 📊 My Dashboard")
    
    if user_requests:
        # Convert to DataFrame for analysis
        df = pd.DataFrame(user_requests)
        
        # Priority breakdown
        st.markdown("#### 🎯 Request Priority Distribution")
        priority_counts = df['priority'].value_counts().reset_index()
        priority_counts.columns = ['Priority', 'Count']
        
        fig1 = px.pie(priority_counts, values='Count', names='Priority',
                      title="My Requests by Priority",
                      hole=0.3)
        st.plotly_chart(fig1, use_container_width=True)
        
        # Status timeline
        st.markdown("#### 📈 Request Status Timeline")
        
        if 'created_date' in df.columns:
            df['created_date'] = pd.to_datetime(df['created_date'])
            df['month'] = df['created_date'].dt.strftime('%Y-%m')
            
            monthly_stats = df.groupby('month').agg({
                'id': 'count',
                'status': lambda x: (x == 'Completed').sum()
            }).reset_index()
            
            monthly_stats.columns = ['Month', 'Total', 'Completed']
            
            fig2 = px.bar(monthly_stats, x='Month', y=['Total', 'Completed'],
                          title="Monthly Request Activity",
                          barmode='group',
                          labels={'value': 'Number of Requests'})
            st.plotly_chart(fig2, use_container_width=True)
        
        # Recent activity
        st.markdown("#### 📋 Recent Activity")
        recent_requests = sorted(user_requests, key=lambda x: x.get('created_date', ''), reverse=True)[:5]
        
        for request in recent_requests:
            status_icon = {
                'Pending': '🟡',
                'Assigned': '🔵', 
                'Completed': '🟢',
                'Approved': '✅',
                'Rejected': '🔴'
            }.get(request['status'], '⚪')
            
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.write(f"{status_icon} **{request['title']}**")
                st.write(f"Priority: {request['priority']} | Status: {request['status']}")
            with col2:
                st.write(request.get('created_date', '')[:10])
            
            st.divider()
    else:
        st.info("📭 You haven't created any maintenance requests yet.")
        st.markdown("""
        ### 🚀 Getting Started
        
        1. **Create a new request** using the "➕ New Request" tab
        2. **Track PPM schedules** in the "📅 PPM" tab  
        3. **Record generator usage** in the "🔌 Generator" tab
        4. **Manage HSE activities** in the "🛡️ HSE" tab
        5. **Book meeting rooms** in the "🏢 Space Management" tab
        
        ### 📞 Need Help?
        - Contact your facility manager for urgent issues
        - Check the knowledge base for common solutions
        - Report system issues to IT support
        """)

def show_new_request(username):
    st.markdown("### ➕ Create New Maintenance Request")
    
    with st.form("new_request_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Title *", placeholder="Brief description of the issue")
            location = st.text_input("Location *", placeholder="Building, floor, room number")
            facility_type = st.selectbox(
                "Facility Type *",
                ["HVAC", "Electrical", "Plumbing", "Generator", "Fixture and Fittings", 
                 "Building Structure", "Cleaning", "Security", "Other"]
            )
        
        with col2:
            priority = st.selectbox(
                "Priority *",
                ["Low", "Medium", "High", "Critical"],
                help="Critical: Immediate attention required, High: Within 24 hours, Medium: Within 3 days, Low: Within 7 days"
            )
            assigned_vendor = st.selectbox(
                "Preferred Vendor (Optional)",
                ["", "hvac_vendor", "generator_vendor", "electrical_vendor", 
                 "plumbing_vendor", "building_vendor", "cleaning_vendor"]
            )
        
        description = st.text_area(
            "Description *", 
            height=150,
            placeholder="Please provide detailed description of the issue, including:\n• What is not working?\n• When did it start?\n• Any error messages?\n• Photos if available"
        )
        
        job_breakdown = st.text_area(
            "Suggested Job Breakdown (Optional)",
            height=100,
            placeholder="If you know what needs to be done, provide details here..."
        )
        
        submitted = st.form_submit_button("📤 Submit Request", use_container_width=True)
        
        if submitted:
            if not all([title, location, facility_type, priority, description]):
                st.error("❌ Please fill in all required fields (*)")
            else:
                success = execute_update(
                    '''INSERT INTO maintenance_requests 
                    (title, description, location, facility_type, priority, 
                     created_by, assigned_vendor, job_breakdown) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (title, description, location, facility_type, priority,
                     username, assigned_vendor if assigned_vendor else None, job_breakdown)
                )
                
                if success:
                    st.success("✅ Maintenance request submitted successfully!")
                    
                    # Show next steps
                    st.markdown("""
                    ### 📋 Next Steps:
                    
                    1. **Request Received** - Your request has been logged
                    2. **Assignment** - Facility manager will assign to a vendor
                    3. **Job Execution** - Vendor will complete the work
                    4. **Completion** - Vendor marks job as completed
                    5. **Approval** - You'll be notified to approve the work
                    6. **Payment** - Invoice processing after approval
                    
                    You can track the progress in the "📋 My Requests" tab.
                    """)
                    
                    st.rerun()
                else:
                    st.error("❌ Failed to submit request")

def show_user_requests_view(username):
    st.markdown("### 📋 My Maintenance Requests")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Pending", "Assigned", "Completed", "Approved", "Rejected"]
        )
    
    with col2:
        priority_filter = st.selectbox(
            "Filter by Priority",
            ["All", "Critical", "High", "Medium", "Low"]
        )
    
    with col3:
        sort_order = st.selectbox(
            "Sort by",
            ["Newest First", "Oldest First", "Priority", "Status"]
        )
    
    # Get user requests
    user_requests = get_user_requests(username)
    
    # Apply filters
    filtered_requests = user_requests
    
    if status_filter != "All":
        filtered_requests = [r for r in filtered_requests if r['status'] == status_filter]
    
    if priority_filter != "All":
        filtered_requests = [r for r in filtered_requests if r['priority'] == priority_filter]
    
    # Apply sorting
    if sort_order == "Newest First":
        filtered_requests.sort(key=lambda x: x.get('created_date', ''), reverse=True)
    elif sort_order == "Oldest First":
        filtered_requests.sort(key=lambda x: x.get('created_date', ''))
    elif sort_order == "Priority":
        priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        filtered_requests.sort(key=lambda x: priority_order.get(x.get('priority', 'Low'), 3))
    elif sort_order == "Status":
        status_order = {"Pending": 0, "Assigned": 1, "Completed": 2, "Approved": 3, "Rejected": 4}
        filtered_requests.sort(key=lambda x: status_order.get(x.get('status', 'Pending'), 5))
    
    if filtered_requests:
        for request in filtered_requests:
            # Determine status color
            status_colors = {
                'Pending': '🟡',
                'Assigned': '🔵',
                'Completed': '🟢',
                'Approved': '✅',
                'Rejected': '🔴'
            }
            
            status_icon = status_colors.get(request['status'], '⚪')
            
            with st.expander(f"{status_icon} {request['title']} - {request['created_date'][:10]}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Location:** {request['location']}")
                    st.write(f"**Facility Type:** {request['facility_type']}")
                    st.write(f"**Priority:** {request['priority']}")
                    st.write(f"**Status:** {request['status']}")
                
                with col2:
                    st.write(f"**Created Date:** {request['created_date']}")
                    st.write(f"**Assigned Vendor:** {request['assigned_vendor'] or 'Not assigned'}")
                    if request['completed_date']:
                        st.write(f"**Completed Date:** {request['completed_date']}")
                    if request['invoice_amount']:
                        st.write(f"**Invoice Amount:** {format_ngn(request['invoice_amount'])}")
                
                st.write(f"**Description:** {request['description']}")
                
                if request['job_breakdown']:
                    st.write(f"**Job Breakdown:** {request['job_breakdown']}")
                
                if request['completion_notes']:
                    st.write(f"**Completion Notes:** {request['completion_notes']}")
                
                # Show workflow status
                show_workflow_status(request)
                
                # PDF Download for completed/approved jobs - MOVED OUTSIDE ANY FORM
                if request['status'] in ['Completed', 'Approved']:
                    pdf_buffer = create_maintenance_pdf_report(request['id'])
                    if pdf_buffer:
                        st.download_button(
                            label="📥 Download Job Report",
                            data=pdf_buffer,
                            file_name=f"job_report_{request['id']}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            key=f"user_pdf_{request['id']}"
                        )
                
                # Actions based on status - MOVED OUTSIDE ANY FORM
                if request['status'] == 'Completed' and not request['requesting_dept_approval']:
                    st.markdown("---")
                    st.markdown("#### ✅ Department Approval Required")
                    
                    if st.button("✅ Approve Completion", key=f"dept_approve_{request['id']}", use_container_width=True):
                        success = execute_update(
                            '''UPDATE maintenance_requests 
                            SET requesting_dept_approval = 1,
                                department_approval_date = ?
                            WHERE id = ?''',
                            (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), request['id'])
                        )
                        
                        if success:
                            st.success("✅ Department approval submitted!")
                            st.rerun()
                    
                    if st.button("❌ Request Revision", key=f"dept_reject_{request['id']}", use_container_width=True, type="secondary"):
                        revision_reason = st.text_input(
                            "Revision Reason", 
                            key=f"revision_reason_{request['id']}",
                            placeholder="What needs to be revised?"
                        )
                        
                        if revision_reason:
                            execute_update(
                                '''UPDATE maintenance_requests 
                                SET status = 'Assigned',
                                    completion_notes = ?
                                WHERE id = ?''',
                                (f"Revision requested: {revision_reason}", request['id'])
                            )
                            st.success("✅ Revision requested from vendor")
                            st.rerun()
    else:
        st.info("📭 No requests found with the selected filters")

# =============================================
# AUTHENTICATION & MAIN APP FLOW
# =============================================
def login():
    st.markdown("<h1 class='app-title'>🏢 A-Z Facilities Management Pro APP™</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container():
            st.markdown("### 🔐 Login")
            
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                login_button = st.button("Login", use_container_width=True)
            with col2:
                if st.button("Clear", use_container_width=True, type="secondary"):
                    st.rerun()
            
            if login_button:
                if not username or not password:
                    st.error("❌ Please enter both username and password")
                else:
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state.user = user
                        st.session_state.logged_in = True
                        st.success(f"✅ Welcome, {user['username']}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
            
            st.markdown("---")
            st.markdown("""
            ### 🆕 Demo Accounts
            
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

def authenticate_user(username, password):
    users = execute_query(
        'SELECT * FROM users WHERE username = ? AND password_hash = ?',
        (username, password)
    )
    
    if users:
        return users[0]
    return None

def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

def main():
    # Initialize session state variables
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'ppm_filter' not in st.session_state:
        st.session_state.ppm_filter = 'All'
    if 'selected_job_for_invoice' not in st.session_state:
        st.session_state.selected_job_for_invoice = None
    if 'assigning_schedule_id' not in st.session_state:
        st.session_state.assigning_schedule_id = None
    
    # Check if user is logged in
    if not st.session_state.logged_in:
        login()
        return
    
    # Sidebar with user info and navigation
    with st.sidebar:
        st.markdown(f"""
        <div style='text-align: center; padding: 10px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 10px; color: white; margin-bottom: 20px;'>
            <h3 style='margin: 0;'>👤 {st.session_state.user['username']}</h3>
            <p style='margin: 5px 0; opacity: 0.9;'>{st.session_state.user['role'].replace('_', ' ').title()}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation based on user role
        user_role = st.session_state.user['role']
        
        if user_role == 'facility_user':
            menu_options = [
                "🏠 Dashboard",
                "➕ New Request", 
                "📋 My Requests",
                "📅 PPM Management",
                "🔌 Generator Records",
                "🛡️ HSE Management",
                "🏢 Space Management",
                "🔓 Logout"
            ]
        elif user_role == 'facility_manager':
            menu_options = [
                "🏠 Dashboard",
                "✅ Approvals",
                "👥 Vendor Management", 
                "📅 PPM Overview",
                "🔌 Generator Records",
                "🛡️ HSE Overview",
                "🏢 Space Management",
                "🔓 Logout"
            ]
        elif user_role == 'vendor':
            menu_options = [
                "🏠 Dashboard",
                "📋 Assigned Jobs",
                "📤 Submit Invoice",
                "💼 PPM Assignments",
                "📊 Performance",
                "📝 Update Profile",
                "🔓 Logout"
            ]
        else:
            menu_options = ["🔓 Logout"]
        
        selected_option = st.sidebar.selectbox("Navigation", menu_options)
        
        # Logout button at bottom
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            logout()
    
    # Main content based on selection
    if selected_option == "🔓 Logout":
        logout()
    
    elif selected_option == "🏠 Dashboard":
        if user_role == 'facility_user':
            show_facility_user_dashboard()
        elif user_role == 'facility_manager':
            show_facility_manager_dashboard()
        elif user_role == 'vendor':
            show_vendor_dashboard()
    
    elif selected_option == "➕ New Request" and user_role == 'facility_user':
        show_new_request(st.session_state.user['username'])
    
    elif selected_option == "📋 My Requests" and user_role == 'facility_user':
        show_user_requests_view(st.session_state.user['username'])
    
    elif selected_option == "📅 PPM Management" and user_role == 'facility_user':
        show_ppm_management_facility_user()
    
    elif selected_option == "🔌 Generator Records" and user_role == 'facility_user':
        show_generator_records_facility_user()
    
    elif selected_option == "🛡️ HSE Management" and user_role == 'facility_user':
        show_hse_management_facility_user()
    
    elif selected_option == "🏢 Space Management" and user_role == 'facility_user':
        show_space_management_facility_user()
    
    elif selected_option == "✅ Approvals" and user_role == 'facility_manager':
        show_manager_approvals()
    
    elif selected_option == "👥 Vendor Management" and user_role == 'facility_manager':
        show_vendor_management()
    
    elif selected_option == "📅 PPM Overview" and user_role == 'facility_manager':
        show_manager_ppm_overview()
    
    elif selected_option == "🔌 Generator Records" and user_role == 'facility_manager':
        show_manager_generator_records()
    
    elif selected_option == "🛡️ HSE Overview" and user_role == 'facility_manager':
        show_manager_hse_overview()
    
    elif selected_option == "🏢 Space Management" and user_role == 'facility_manager':
        show_manager_space_management()
    
    elif selected_option == "📋 Assigned Jobs" and user_role == 'vendor':
        show_vendor_assigned_jobs(st.session_state.user['username'])
    
    elif selected_option == "📤 Submit Invoice" and user_role == 'vendor':
        show_vendor_invoice_submission(st.session_state.user['username'])
    
    elif selected_option == "💼 PPM Assignments" and user_role == 'vendor':
        show_vendor_ppm_assignments(st.session_state.user['username'])
    
    elif selected_option == "📊 Performance" and user_role == 'vendor':
        show_vendor_performance(st.session_state.user['username'])
    
    elif selected_option == "📝 Update Profile" and user_role == 'vendor':
        vendor_details = execute_query(
            'SELECT * FROM vendors WHERE username = ?',
            (st.session_state.user['username'],)
        )
        if vendor_details:
            show_vendor_profile_update(vendor_details[0], st.session_state.user['username'])

# =============================================
# RUN THE APPLICATION
# =============================================
if __name__ == "__main__":
    main()

