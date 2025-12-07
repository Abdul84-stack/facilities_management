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
    
    /* Status badges */
    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .status-pending { background-color: #fef3c7; color: #92400e; }
    .status-assigned { background-color: #dbeafe; color: #1e40af; }
    .status-completed { background-color: #dcfce7; color: #166534; }
    .status-approved { background-color: #f0f9ff; color: #0c4a6e; }
    
    /* Form styling */
    .stTextInput > div > div > input {
        border-radius: 8px !important;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 8px !important;
    }
    
    .stSelectbox > div > div > select {
        border-radius: 8px !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0px 0px !important;
        padding: 10px 20px !important;
    }
    
    /* Workflow steps */
    .workflow-step {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
        padding: 10px;
        border-radius: 8px;
        background-color: #f8fafc;
    }
    
    .step-number {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background-color: #3b82f6;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 10px;
        font-weight: bold;
    }
    
    .step-active {
        background-color: #dbeafe;
        border-left: 4px solid #3b82f6;
    }
    
    .step-completed {
        background-color: #dcfce7;
        border-left: 4px solid #10b981;
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
                password_hash TEXT NOT NULL,
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
                ('space_vendor', '0123456', 'vendor', 'Space Management')
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
        print("Database initialized successfully")
        
    except Exception as e:
        print(f"Database initialization error: {e}")
        try:
            if os.path.exists('facilities_management.db'):
                os.remove('facilities_management.db')
            print("Old database removed, please restart the app")
        except:
            pass

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
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f"<div style='font-size: 2.5rem;'>{icon}</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<h3 style='margin: 0;'>{title}</h3>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='margin: 0; color: #1e3a8a;'>{value}</h1>", unsafe_allow_html=True)

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
        step_class = "step-completed" if step["completed"] else "step-active" if step["active"] else ""
        
        st.markdown(f'''
        <div class="workflow-step {step_class}">
            <div class="step-number">{step["number"]}</div>
            <div>
                <strong>{step["title"]}</strong>
                {f'<br><small>Date: {safe_str(step["date"])}</small>' if step["date"] else ''}
            </div>
        </div>
        ''', unsafe_allow_html=True)

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
# ENHANCED PDF GENERATION
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
# NEW: DEPARTMENT APPROVAL PAGE FOR FACILITY USER
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
# NEW: FINAL APPROVAL PAGE FOR FACILITY MANAGER
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
# MAIN APPLICATION FUNCTIONS (UPDATED)
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
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Total", len(user_requests), "📋")
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
# UPDATED MANAGE REQUESTS FOR FACILITY MANAGER
# =============================================
def show_manage_requests():
    st.markdown("<h1 class='app-title'>🛠️ Manage Maintenance Requests</h1>", unsafe_allow_html=True)
    
    all_requests = get_all_requests()
    
    if not all_requests:
        st.info("📭 No maintenance requests found")
        return
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Total", len(all_requests), "📊")
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
                    
                    # Get vendors
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

# =============================================
# VENDOR FUNCTIONS - COMPLETELY UPDATED
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
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        details_of_work = st.text_input("Work Description *", placeholder="Description of work")
                        quantity = st.number_input("Quantity *", min_value=1, value=1)
                    with col2:
                        unit_cost = st.number_input("Unit Cost (₦) *", min_value=0.0, value=0.0, step=100.0)
                        labour_charge = st.number_input("Labour/Service Charge (₦)", min_value=0.0, value=0.0, step=100.0)
                    with col3:
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
# VENDOR REGISTRATION
# =============================================
def show_vendor_registration():
    """Vendor registration page"""
    st.markdown("<h1 class='app-title'>🏢 Vendor Registration</h1>", unsafe_allow_html=True)
    
    # Check if vendor is already registered
    vendor_username = st.session_state.user['username']
    existing_vendor = execute_query('SELECT * FROM vendors WHERE username = ?', (vendor_username,))
    
    if existing_vendor:
        st.info("✅ You are already registered as a vendor.")
        
        vendor = existing_vendor[0]
        with st.expander("View Your Registration Details", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Company Name:** {safe_str(safe_get(vendor, 'company_name'))}")
                st.write(f"**Contact Person:** {safe_str(safe_get(vendor, 'contact_person'))}")
                st.write(f"**Email:** {safe_str(safe_get(vendor, 'email'))}")
                st.write(f"**Phone:** {safe_str(safe_get(vendor, 'phone'))}")
                st.write(f"**Vendor Type:** {safe_str(safe_get(vendor, 'vendor_type'))}")
                st.write(f"**Registration Date:** {safe_str(safe_get(vendor, 'registration_date'))}")
            
            with col2:
                st.write(f"**Services Offered:** {safe_str(safe_get(vendor, 'services_offered'))}")
                st.write(f"**Annual Turnover:** {format_ngn(safe_get(vendor, 'annual_turnover'))}")
                st.write(f"**Tax ID:** {safe_str(safe_get(vendor, 'tax_identification_number'))}")
                st.write(f"**RC Number:** {safe_str(safe_get(vendor, 'rc_number'))}")
                st.write(f"**Address:** {safe_str(safe_get(vendor, 'address'))}")
        
        return
    
    # Registration form for new vendors
    st.info("📋 Please complete your vendor registration form below")
    
    with st.form("vendor_registration_form"):
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company Name *", placeholder="Enter your company name")
            contact_person = st.text_input("Contact Person *", placeholder="Full name of contact person")
            email = st.text_input("Email Address *", placeholder="company@example.com")
            phone = st.text_input("Phone Number *", placeholder="123-456-7890")
            vendor_type = st.selectbox(
                "Vendor Type *",
                ["HVAC", "Generator", "Fixture and Fittings", "Building Maintenance", 
                 "HSE", "Space Management", "Electrical", "Plumbing", "Other"]
            )
        
        with col2:
            services_offered = st.text_area("Services Offered *", height=80, 
                                          placeholder="Describe the services you offer")
            annual_turnover = st.number_input("Annual Turnover (₦)", min_value=0.0, 
                                            value=0.0, step=10000.0)
            tax_id = st.text_input("Tax Identification Number")
            rc_number = st.text_input("RC/Business Registration Number")
            address = st.text_area("Company Address *", height=60, 
                                 placeholder="Full physical address")
        
        # Additional fields
        st.markdown("### Additional Information")
        col3, col4 = st.columns(2)
        
        with col3:
            key_management_staff = st.text_area("Key Management Staff", height=60,
                                              placeholder="Names and positions of key staff")
            account_details = st.text_area("Bank Account Details", height=60,
                                         placeholder="Bank name and account number")
        
        with col4:
            certification = st.text_area("Certifications/Licenses", height=60,
                                       placeholder="Any professional certifications")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        submitted = st.form_submit_button("📋 Register as Vendor", use_container_width=True)
        
        if submitted:
            if not all([company_name, contact_person, email, phone, vendor_type, 
                       services_offered, address]):
                st.error("❌ Please fill in all required fields (*)")
            else:
                success = execute_update(
                    '''INSERT INTO vendors 
                    (username, company_name, contact_person, email, phone, vendor_type, 
                     services_offered, annual_turnover, tax_identification_number, 
                     rc_number, key_management_staff, account_details, certification, address) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (vendor_username, company_name, contact_person, email, phone, vendor_type,
                     services_offered, annual_turnover, tax_id, rc_number,
                     key_management_staff, account_details, certification, address)
                )
                if success:
                    st.success("✅ Vendor registration successful! You can now receive job assignments.")
                    st.rerun()
                else:
                    st.error("❌ Failed to register vendor")

# =============================================
# INVOICE CREATION (FOR VENDORS)
# =============================================
def show_invoice_creation():
    """Invoice creation page for vendors"""
    st.markdown("<h1 class='app-title'>🧾 Invoice Creation</h1>", unsafe_allow_html=True)
    
    vendor_username = st.session_state.user['username']
    
    # Get completed jobs without invoices
    completed_jobs = execute_query('''
        SELECT * FROM maintenance_requests 
        WHERE assigned_vendor = ? 
        AND status = 'Completed' 
        AND invoice_number IS NULL
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
                        value=safe_str(safe_get(job, 'job_breakdown'), ""),
                        placeholder="Description of work performed"
                    )
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        quantity = st.number_input("Quantity *", min_value=1, value=1, key=f"qty_{safe_get(job, 'id')}")
                        unit_cost = st.number_input("Unit Cost (₦) *", min_value=0.0, value=0.0, step=100.0, 
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

# =============================================
# VENDOR REPORTS
# =============================================
def show_vendor_reports():
    """Vendor reports page"""
    st.markdown("<h1 class='app-title'>📊 My Vendor Reports</h1>", unsafe_allow_html=True)
    
    vendor_username = st.session_state.user['username']
    
    # Get vendor stats
    vendor_jobs = get_vendor_requests(vendor_username)
    vendor_invoices = execute_query(
        'SELECT * FROM invoices WHERE vendor_username = ? ORDER BY invoice_date DESC',
        (vendor_username,)
    )
    
    # Stats cards
    col1, col2, col3, col4 = st.columns(4)
    
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
        approved_jobs = len([j for j in vendor_jobs if safe_get(j, 'status') == 'Approved'])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Approved", approved_jobs, "👍")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        total_invoices = len(vendor_invoices)
        total_revenue = sum([safe_float(inv['total_amount']) for inv in vendor_invoices])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Total Revenue", format_ngn(total_revenue), "💰")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2 = st.tabs(["Job Analytics", "Invoice History"])
    
    with tab1:
        if vendor_jobs:
            # Create job status chart
            status_counts = {}
            for job in vendor_jobs:
                status = safe_get(job, 'status')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            if status_counts:
                df_status = pd.DataFrame({
                    'Status': list(status_counts.keys()),
                    'Count': list(status_counts.values())
                })
                
                fig = px.pie(df_status, values='Count', names='Status', 
                           title="Job Status Distribution",
                           color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig, use_container_width=True)
            
            # Monthly trend
            try:
                monthly_data = []
                for job in vendor_jobs:
                    if safe_get(job, 'completed_date'):
                        month = datetime.strptime(safe_get(job, 'completed_date'), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m')
                        monthly_data.append(month)
                
                if monthly_data:
                    month_counts = pd.Series(monthly_data).value_counts().sort_index()
                    df_monthly = pd.DataFrame({
                        'Month': month_counts.index,
                        'Jobs Completed': month_counts.values
                    })
                    
                    fig2 = px.bar(df_monthly, x='Month', y='Jobs Completed',
                                 title="Monthly Jobs Completed Trend",
                                 color='Jobs Completed')
                    st.plotly_chart(fig2, use_container_width=True)
            except:
                pass
        else:
            st.info("📭 No job data available for analytics")
    
    with tab2:
        if vendor_invoices:
            # Display invoices table
            invoice_data = []
            for inv in vendor_invoices:
                invoice_data.append({
                    'Invoice #': safe_str(safe_get(inv, 'invoice_number')),
                    'Date': safe_str(safe_get(inv, 'invoice_date')),
                    'Details': safe_str(safe_get(inv, 'details_of_work')),
                    'Amount': format_ngn(safe_get(inv, 'total_amount')),
                    'Status': safe_str(safe_get(inv, 'status'))
                })
            
            df_invoices = pd.DataFrame(invoice_data)
            st.dataframe(df_invoices, use_container_width=True, hide_index=True)
            
            # Download invoices as CSV
            csv = df_invoices.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Invoices as CSV",
                data=csv,
                file_name=f"vendor_invoices_{vendor_username}.csv",
                mime="text/csv"
            )
        else:
            st.info("📭 No invoices found")

# =============================================
# VENDOR MANAGEMENT (FOR FACILITY MANAGER)
# =============================================
def show_vendor_management():
    """Vendor management page for facility manager"""
    st.markdown("<h1 class='app-title'>👥 Vendor Management</h1>", unsafe_allow_html=True)
    
    # Get all vendors
    vendors = execute_query('SELECT * FROM vendors ORDER BY company_name')
    
    if not vendors:
        st.info("📭 No vendors registered yet")
        return
    
    st.markdown(f"<div class='card'><h4>🏢 {len(vendors)} Registered Vendor(s)</h4></div>", unsafe_allow_html=True)
    
    # Vendor stats
    col1, col2, col3 = st.columns(3)
    with col1:
        vendor_types = set([v['vendor_type'] for v in vendors])
        st.metric("Vendor Types", len(vendor_types))
    with col2:
        active_vendors = len([v for v in vendors])
        st.metric("Total Vendors", active_vendors)
    with col3:
        # Get vendor performance (jobs completed)
        vendor_performance = []
        for vendor in vendors:
            jobs = execute_query(
                'SELECT COUNT(*) as count FROM maintenance_requests WHERE assigned_vendor = ? AND status = "Approved"',
                (vendor['username'],)
            )
            vendor_performance.append(jobs[0]['count'] if jobs else 0)
        avg_jobs = sum(vendor_performance) / len(vendor_performance) if vendor_performance else 0
        st.metric("Avg Jobs Completed", f"{avg_jobs:.1f}")
    
    st.markdown("---")
    
    # Display vendors with expandable details
    for vendor in vendors:
        with st.expander(f"🏢 {safe_str(safe_get(vendor, 'company_name'))} - {safe_str(safe_get(vendor, 'vendor_type'))}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Company Information")
                st.write(f"**Company:** {safe_str(safe_get(vendor, 'company_name'))}")
                st.write(f"**Contact:** {safe_str(safe_get(vendor, 'contact_person'))}")
                st.write(f"**Email:** {safe_str(safe_get(vendor, 'email'))}")
                st.write(f"**Phone:** {safe_str(safe_get(vendor, 'phone'))}")
                st.write(f"**Vendor Type:** {safe_str(safe_get(vendor, 'vendor_type'))}")
                st.write(f"**Services:** {safe_str(safe_get(vendor, 'services_offered'))}")
                st.write(f"**Address:** {safe_str(safe_get(vendor, 'address'))}")
                st.write(f"**Registered:** {safe_str(safe_get(vendor, 'registration_date'))}")
            
            with col2:
                st.markdown("### Business Details")
                st.write(f"**Annual Turnover:** {format_ngn(safe_get(vendor, 'annual_turnover'))}")
                st.write(f"**Tax ID:** {safe_str(safe_get(vendor, 'tax_identification_number'))}")
                st.write(f"**RC Number:** {safe_str(safe_get(vendor, 'rc_number'))}")
                
                if safe_get(vendor, 'certification'):
                    st.write(f"**Certifications:** {safe_str(safe_get(vendor, 'certification'))}")
                
                # Get vendor performance stats
                vendor_username = safe_get(vendor, 'username')
                vendor_jobs = execute_query(
                    'SELECT status, COUNT(*) as count FROM maintenance_requests WHERE assigned_vendor = ? GROUP BY status',
                    (vendor_username,)
                )
                
                if vendor_jobs:
                    st.markdown("### 📊 Performance Stats")
                    for job_stat in vendor_jobs:
                        status = safe_str(safe_get(job_stat, 'status'))
                        count = safe_int(safe_get(job_stat, 'count'))
                        st.write(f"**{status} Jobs:** {count}")
                
                # Action buttons
                st.markdown("### ⚙️ Actions")
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("View Jobs", key=f"view_jobs_{vendor_username}"):
                        st.session_state.selected_vendor = vendor_username
                        st.rerun()
                with col_b:
                    if st.button("Remove Vendor", key=f"remove_{vendor_username}", type="secondary"):
                        if execute_update('DELETE FROM vendors WHERE username = ?', (vendor_username,)):
                            st.success("✅ Vendor removed successfully")
                            st.rerun()

# =============================================
# REPORTS & ANALYTICS
# =============================================
def show_reports():
    """Comprehensive reports and analytics"""
    st.markdown("<h1 class='app-title'>📈 Reports & Analytics</h1>", unsafe_allow_html=True)
    
    # Get all data
    all_requests = get_all_requests()
    all_vendors = execute_query('SELECT * FROM vendors')
    all_invoices = execute_query('SELECT * FROM invoices')
    
    if not all_requests:
        st.info("📭 No data available for reports")
        return
    
    # Overall stats
    st.markdown("<div class='section-header'>📊 Overall Statistics</div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_requests = len(all_requests)
        st.metric("Total Requests", total_requests)
    
    with col2:
        pending_requests = len([r for r in all_requests if safe_get(r, 'status') == 'Pending'])
        st.metric("Pending Requests", pending_requests)
    
    with col3:
        completed_requests = len([r for r in all_requests if safe_get(r, 'status') == 'Completed'])
        st.metric("Completed Jobs", completed_requests)
    
    with col4:
        approved_requests = len([r for r in all_requests if safe_get(r, 'status') == 'Approved'])
        st.metric("Approved Jobs", approved_requests)
    
    st.markdown("---")
    
    # Tabs for different reports
    tab1, tab2, tab3, tab4 = st.tabs(["📅 Time Analysis", "🏢 Facility Analysis", "💰 Financial Reports", "📋 Detailed View"])
    
    with tab1:
        # Monthly trend analysis
        st.markdown("### 📅 Monthly Request Trend")
        try:
            monthly_data = {}
            for req in all_requests:
                if safe_get(req, 'created_date'):
                    month = datetime.strptime(safe_get(req, 'created_date'), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m')
                    monthly_data[month] = monthly_data.get(month, 0) + 1
            
            if monthly_data:
                df_monthly = pd.DataFrame({
                    'Month': list(monthly_data.keys()),
                    'Requests': list(monthly_data.values())
                }).sort_values('Month')
                
                fig = px.line(df_monthly, x='Month', y='Requests', 
                            title="Monthly Maintenance Requests",
                            markers=True)
                st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("No time-based data available")
    
    with tab2:
        # Facility type analysis
        st.markdown("### 🏢 Facility Type Distribution")
        facility_counts = {}
        for req in all_requests:
            facility = safe_get(req, 'facility_type')
            facility_counts[facility] = facility_counts.get(facility, 0) + 1
        
        if facility_counts:
            df_facility = pd.DataFrame({
                'Facility Type': list(facility_counts.keys()),
                'Count': list(facility_counts.values())
            })
            
            fig = px.bar(df_facility, x='Facility Type', y='Count',
                       title="Requests by Facility Type",
                       color='Count')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Financial reports
        st.markdown("### 💰 Financial Summary")
        
        if all_invoices:
            # Total revenue
            total_revenue = sum([safe_float(inv['total_amount']) for inv in all_invoices])
            avg_invoice = total_revenue / len(all_invoices) if all_invoices else 0
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Total Revenue", format_ngn(total_revenue))
            with col_b:
                st.metric("Average Invoice", format_ngn(avg_invoice))
            
            # Revenue by vendor
            vendor_revenue = {}
            for inv in all_invoices:
                vendor = safe_get(inv, 'vendor_username')
                amount = safe_float(inv['total_amount'])
                vendor_revenue[vendor] = vendor_revenue.get(vendor, 0) + amount
            
            if vendor_revenue:
                df_vendor_rev = pd.DataFrame({
                    'Vendor': list(vendor_revenue.keys()),
                    'Revenue': list(vendor_revenue.values())
                }).sort_values('Revenue', ascending=False)
                
                fig = px.bar(df_vendor_rev.head(10), x='Vendor', y='Revenue',
                           title="Top 10 Vendors by Revenue",
                           color='Revenue')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No invoice data available")
    
    with tab4:
        # Detailed data view
        st.markdown("### 📋 Detailed Data View")
        
        # Create detailed dataframe
        detailed_data = []
        for req in all_requests:
            detailed_data.append({
                'ID': safe_get(req, 'id'),
                'Title': safe_str(safe_get(req, 'title')),
                'Facility Type': safe_str(safe_get(req, 'facility_type')),
                'Priority': safe_str(safe_get(req, 'priority')),
                'Status': safe_str(safe_get(req, 'status')),
                'Created By': safe_str(safe_get(req, 'created_by')),
                'Created Date': safe_str(safe_get(req, 'created_date')),
                'Assigned Vendor': safe_str(safe_get(req, 'assigned_vendor')),
                'Invoice Amount': format_ngn(safe_get(req, 'invoice_amount'))
            })
        
        df_detailed = pd.DataFrame(detailed_data)
        st.dataframe(df_detailed, use_container_width=True)
        
        # Download options
        csv = df_detailed.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name="facilities_management_report.csv",
            mime="text/csv"
        )

# =============================================
# JOB & INVOICE REPORTS
# =============================================
def show_job_invoice_reports():
    """Job and invoice reports"""
    st.markdown("<h1 class='app-title'>📄 Job & Invoice Reports</h1>", unsafe_allow_html=True)
    
    # Get all jobs with invoices
    jobs_with_invoices = execute_query('''
        SELECT mr.*, i.invoice_date, i.total_amount, i.status as invoice_status
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
    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox("Filter by Job Status", ["All", "Completed", "Approved"], key="job_status_filter")
    with col2:
        invoice_filter = st.selectbox("Filter by Invoice Status", ["All", "Paid", "Pending"], key="invoice_status_filter")
    
    # Apply filters
    filtered_jobs = jobs_with_invoices
    if status_filter != "All":
        filtered_jobs = [j for j in filtered_jobs if safe_get(j, 'status') == status_filter]
    if invoice_filter != "All":
        filtered_jobs = [j for j in filtered_jobs if safe_get(j, 'invoice_status') == invoice_filter]
    
    # Display filtered jobs
    for job in filtered_jobs:
        with st.expander(f"📄 Job #{safe_get(job, 'id')}: {safe_str(safe_get(job, 'title'))} - Invoice: {safe_str(safe_get(job, 'invoice_number'))}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📝 Job Details")
                st.write(f"**Title:** {safe_str(safe_get(job, 'title'))}")
                st.write(f"**Description:** {safe_str(safe_get(job, 'description'))}")
                st.write(f"**Facility Type:** {safe_str(safe_get(job, 'facility_type'))}")
                st.write(f"**Priority:** {safe_str(safe_get(job, 'priority'))}")
                st.write(f"**Status:** {safe_str(safe_get(job, 'status'))}")
                st.write(f"**Created By:** {safe_str(safe_get(job, 'created_by'))}")
                st.write(f"**Completed Date:** {safe_str(safe_get(job, 'completed_date'))}")
            
            with col2:
                st.markdown("### 🧾 Invoice Details")
                st.write(f"**Invoice Number:** {safe_str(safe_get(job, 'invoice_number'))}")
                st.write(f"**Invoice Date:** {safe_str(safe_get(job, 'invoice_date'))}")
                st.write(f"**Total Amount:** {format_ngn(safe_get(job, 'total_amount'))}")
                st.write(f"**Invoice Status:** {safe_str(safe_get(job, 'invoice_status'))}")
                
                # Get detailed invoice
                invoice_details = execute_query(
                    'SELECT * FROM invoices WHERE invoice_number = ?', 
                    (safe_get(job, 'invoice_number'),)
                )
                
                if invoice_details:
                    invoice = invoice_details[0]
                    with st.expander("View Full Invoice Details"):
                        st.write(f"**Details of Work:** {safe_str(safe_get(invoice, 'details_of_work'))}")
                        st.write(f"**Quantity:** {safe_str(safe_get(invoice, 'quantity'))}")
                        st.write(f"**Unit Cost:** {format_ngn(safe_get(invoice, 'unit_cost'))}")
                        st.write(f"**Amount:** {format_ngn(safe_get(invoice, 'amount'))}")
                        st.write(f"**Labour Charge:** {format_ngn(safe_get(invoice, 'labour_charge'))}")
                        st.write(f"**VAT Amount:** {format_ngn(safe_get(invoice, 'vat_amount'))}")
                        st.write(f"**Total:** {format_ngn(safe_get(invoice, 'total_amount'))}")
                
                # Generate PDF button
                if safe_get(job, 'facilities_manager_approval'):
                    pdf_buffer = generate_final_report_pdf(job, invoice_details[0] if invoice_details else None)
                    
                    st.download_button(
                        label="📄 Download Invoice Report",
                        data=pdf_buffer.getvalue(),
                        file_name=f"Invoice_Report_Job_{safe_get(job, 'id')}.pdf",
                        mime="application/pdf",
                        key=f"invoice_report_{safe_get(job, 'id')}",
                        use_container_width=True
                    )

# =============================================
# DASHBOARD FUNCTIONS (UPDATED WITH APPROVAL STATS)
# =============================================
def show_user_dashboard():
    st.markdown("<h1 class='app-title'>📊 Dashboard Overview</h1>", unsafe_allow_html=True)
    
    user_requests = get_user_requests(st.session_state.user['username'])
    
    # Stats including approval stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Total", len(user_requests), "📋")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        pending_approval = len([r for r in user_requests if safe_get(r, 'status') == 'Completed' and not safe_get(r, 'requesting_dept_approval')])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Awaiting My Approval", pending_approval, "✅")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        approved_jobs = len([r for r in user_requests if safe_get(r, 'status') == 'Approved'])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Fully Approved", approved_jobs, "👍")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        pending_jobs = len([r for r in user_requests if safe_get(r, 'status') == 'Pending'])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Pending", pending_jobs, "⏳")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("<div class='section-header'>🚀 Quick Actions</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📝 Create New Request", use_container_width=True):
            # Show the create request form directly
            show_create_request()
            return
    
    with col2:
        pending_approvals = get_requests_for_user_approval(st.session_state.user['username'])
        if pending_approvals:
            if st.button(f"✅ Approve Jobs ({len(pending_approvals)})", use_container_width=True, type="primary"):
                # Show department approval directly
                show_department_approval()
                return
    
    with col3:
        if st.button("📋 View My Requests", use_container_width=True):
            # Show my requests directly
            show_my_requests()
            return

def show_manager_dashboard():
    st.markdown("<h1 class='app-title'>📊 Dashboard Overview</h1>", unsafe_allow_html=True)
    
    all_requests = get_all_requests()
    
    # Stats including approval stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Total", len(all_requests), "📊")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        pending_final = len(get_requests_for_manager_approval())
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Awaiting Final Approval", pending_final, "✅")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        assigned_count = len([r for r in all_requests if safe_get(r, 'status') == 'Assigned'])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Assigned", assigned_count, "👷")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        approved_count = len([r for r in all_requests if safe_get(r, 'status') == 'Approved'])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Fully Approved", approved_count, "👍")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("<div class='section-header'>🚀 Quick Actions</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🛠️ Manage Requests", use_container_width=True):
            show_manage_requests()
            return
    
    with col2:
        pending_final_approvals = get_requests_for_manager_approval()
        if pending_final_approvals:
            if st.button(f"✅ Final Approval ({len(pending_final_approvals)})", use_container_width=True, type="primary"):
                show_final_approval()
                return
    
    with col3:
        if st.button("👥 Vendor Management", use_container_width=True):
            show_vendor_management()
            return

def show_vendor_dashboard():
    st.markdown("<h1 class='app-title'>📊 Dashboard Overview</h1>", unsafe_allow_html=True)
    
    vendor_requests = get_vendor_requests(st.session_state.user['username'])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        assigned_count = len([r for r in vendor_requests if safe_get(r, 'status') == 'Assigned'])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Assigned Jobs", assigned_count, "🔧")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        completed_count = len([r for r in vendor_requests if safe_get(r, 'status') == 'Completed'])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Completed", completed_count, "✅")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        approved_count = len([r for r in vendor_requests if safe_get(r, 'status') == 'Approved'])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Approved", approved_count, "👍")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        # Calculate total revenue from completed jobs
        total_revenue = sum([safe_float(r['invoice_amount']) for r in vendor_requests if r['invoice_amount']])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Total Revenue", format_ngn(total_revenue), "💰")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("<div class='section-header'>🚀 Quick Actions</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        assigned_jobs = len([r for r in vendor_requests if safe_get(r, 'status') == 'Assigned'])
        if assigned_jobs > 0:
            if st.button(f"🔧 Work on Jobs ({assigned_jobs})", use_container_width=True, type="primary"):
                show_assigned_jobs()
                return
    
    with col2:
        if st.button("🏢 Vendor Registration", use_container_width=True):
            show_vendor_registration()
            return
    
    with col3:
        if st.button("📊 My Reports", use_container_width=True):
            show_vendor_reports()
            return

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

# =============================================
# MAIN APPLICATION ROUTING (UPDATED)
# =============================================
def show_main_app():
    user = st.session_state.user
    role = user['role']
    
    with st.sidebar:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color: #1e3a8a;'>👋 Welcome, {user['username']}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p><strong>Role:</strong> {role.replace('_', ' ').title()}</p>", unsafe_allow_html=True)
        if user['vendor_type']:
            st.markdown(f"<p><strong>Vendor Type:</strong> {user['vendor_type']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p><strong>Currency:</strong> <span class='ngn'>NGN (₦)</span></p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-header'>📱 Navigation</div>", unsafe_allow_html=True)
        
        # Navigation based on user role
        if role == 'facility_user':
            menu_options = ["📊 Dashboard", "📝 Create Request", "📋 My Requests", "✅ Department Approval"]
        elif role == 'facility_manager':
            menu_options = ["📊 Dashboard", "🛠️ Manage Requests", "✅ Final Approval", "👥 Vendor Management", 
                          "📈 Reports & Analytics", "📄 Job & Invoice Reports"]
        else:  # vendor
            menu_options = ["📊 Dashboard", "🔧 Assigned Jobs", "✅ Completed Jobs", 
                          "🏢 Vendor Registration", "🧾 Invoice Creation", "📊 My Reports"]
        
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
        "📊 My Reports": show_vendor_reports
    }
    
    if selected_menu in menu_map:
        menu_map[selected_menu]()
    else:
        st.error("Page not found")

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
