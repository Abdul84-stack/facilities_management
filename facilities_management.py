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
        
        # Users table - SIMPLIFIED
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
        
        # Maintenance requests table - SIMPLIFIED
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
                facilities_manager_approval INTEGER DEFAULT 0
            )
        ''')
        
        # Vendors table - SIMPLIFIED
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
        
        # Invoices table - SIMPLIFIED
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
        # Try to delete and recreate database
        try:
            if os.path.exists('facilities_management.db'):
                os.remove('facilities_management.db')
            print("Old database removed, please restart the app")
        except:
            pass

# Initialize database
init_database()

# =============================================
# DATABASE FUNCTIONS - SIMPLIFIED
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
# HELPER FUNCTIONS
# =============================================
def get_user_requests(username):
    """Get user requests"""
    return execute_query(
        'SELECT * FROM maintenance_requests WHERE created_by = ? ORDER BY created_date DESC',
        (username,)
    )

def get_all_requests():
    """Get all requests"""
    return execute_query('SELECT * FROM maintenance_requests ORDER BY created_date DESC')

def get_vendor_requests(vendor_username):
    """Get vendor requests"""
    return execute_query(
        'SELECT * FROM maintenance_requests WHERE assigned_vendor = ? ORDER BY created_date DESC',
        (vendor_username,)
    )

def create_metric_card(title, value, icon="📊"):
    """Create a beautiful metric card"""
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f"<div style='font-size: 2.5rem;'>{icon}</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<h3 style='margin: 0;'>{title}</h3>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='margin: 0; color: #1e3a8a;'>{value}</h1>", unsafe_allow_html=True)

# =============================================
# ENHANCED PDF GENERATION
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
    story.append(Paragraph("A-Z FACILITIES MANAGEMENT PRO APP™", title_style))
    story.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
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
        ["Approval Type", "Status"],
        ["Department Approval", 
         "✅ APPROVED" if safe_get(request_data, 'requesting_dept_approval') else "⏳ PENDING"],
        ["Facilities Manager Approval", 
         "✅ APPROVED" if safe_get(request_data, 'facilities_manager_approval') else "⏳ PENDING"]
    ]
    
    approval_table = Table(approval_data, colWidths=[200, 300])
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
# ENHANCED LOGIN PAGE
# =============================================
def show_enhanced_login():
    """Enhanced login page with beautiful UI"""
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
            with col2:
                reset_button = st.form_submit_button("🔄 Reset", type="secondary", use_container_width=True)
            
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
# MAIN APPLICATION FUNCTIONS
# =============================================
def show_create_request():
    """Create maintenance request"""
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
    """Show user's maintenance requests"""
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
    
    # Display requests
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
                    st.write(f"**Completion Notes:** {safe_str(safe_get(req, 'completion_notes'))}")
                if safe_get(req, 'invoice_amount'):
                    st.write(f"**Invoice Amount:** {format_ngn(safe_get(req, 'invoice_amount'))}")

def show_manage_requests():
    """Manage all requests (for facility manager)"""
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
                
                elif status == 'Completed':
                    st.subheader("Approval Actions")
                    
                    if safe_get(req, 'requesting_dept_approval'):
                        st.success("✅ Department approval received")
                        
                        if not safe_get(req, 'facilities_manager_approval'):
                            if st.button("Approve as Facilities Manager", key=f"approve_{safe_get(req, 'id')}"):
                                if execute_update(
                                    'UPDATE maintenance_requests SET status = ?, facilities_manager_approval = ? WHERE id = ?',
                                    ('Approved', 1, safe_get(req, 'id'))
                                ):
                                    st.success("✅ Facilities manager approval granted!")
                                    st.rerun()
                        else:
                            st.success("✅ Facilities manager approval granted")
                    else:
                        st.info("⏳ Waiting for department approval")
                
                # Display vendor and completion details
                if safe_get(req, 'assigned_vendor'):
                    vendor_info = execute_query(
                        'SELECT company_name FROM vendors WHERE username = ?',
                        (safe_get(req, 'assigned_vendor'),)
                    )
                    vendor_name = vendor_info[0]['company_name'] if vendor_info else safe_get(req, 'assigned_vendor')
                    st.write(f"**Assigned Vendor:** {vendor_name}")
                
                if safe_get(req, 'completion_notes'):
                    st.write(f"**Completion Notes:** {safe_str(safe_get(req, 'completion_notes'))}")
                
                if safe_get(req, 'job_breakdown'):
                    st.write(f"**Job Breakdown:** {safe_str(safe_get(req, 'job_breakdown'))}")
                
                if safe_get(req, 'completed_date'):
                    st.write(f"**Completed Date:** {safe_str(safe_get(req, 'completed_date'))}")
                
                if safe_get(req, 'invoice_amount'):
                    st.write(f"**Invoice Amount:** {format_ngn(safe_get(req, 'invoice_amount'))}")

def show_vendor_management():
    """Vendor management for facility manager"""
    st.markdown("<h1 class='app-title'>👥 Vendor Management</h1>", unsafe_allow_html=True)
    
    vendors = execute_query('SELECT * FROM vendors ORDER BY company_name')
    
    if not vendors:
        st.info("🏢 No vendors registered yet")
        return
    
    st.markdown(f"<div class='card'><h4>📊 Registered Vendors: {len(vendors)}</h4></div>", unsafe_allow_html=True)
    
    # Display vendors
    for vendor in vendors:
        with st.expander(f"🏢 {safe_str(safe_get(vendor, 'company_name'))} - {safe_str(safe_get(vendor, 'vendor_type'))}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Company Information**")
                st.write(f"**Company:** {safe_str(safe_get(vendor, 'company_name'))}")
                st.write(f"**Contact:** {safe_str(safe_get(vendor, 'contact_person'))}")
                st.write(f"**Email:** {safe_str(safe_get(vendor, 'email'))}")
                st.write(f"**Phone:** {safe_str(safe_get(vendor, 'phone'))}")
                st.write(f"**Type:** {safe_str(safe_get(vendor, 'vendor_type'))}")
                
                turnover = safe_get(vendor, 'annual_turnover')
                if turnover:
                    st.write(f"**Annual Turnover:** {format_ngn(turnover)}")
                
                tax_id = safe_get(vendor, 'tax_identification_number')
                if tax_id:
                    st.write(f"**Tax ID:** {tax_id}")
            
            with col2:
                st.markdown("**Services & Details**")
                st.write(f"**Services:** {safe_str(safe_get(vendor, 'services_offered'))}")
                
                key_staff = safe_get(vendor, 'key_management_staff')
                if key_staff:
                    st.write(f"**Key Staff:** {key_staff}")
                
                account_details = safe_get(vendor, 'account_details')
                if account_details:
                    st.write(f"**Account:** {account_details}")
                
                st.write(f"**Certification:** {safe_str(safe_get(vendor, 'certification'), 'Not specified')}")
                st.write(f"**Address:** {safe_str(safe_get(vendor, 'address'))}")
                st.write(f"**Registered:** {safe_str(safe_get(vendor, 'registration_date'))}")

def show_reports():
    """Reports and analytics"""
    st.markdown("<h1 class='app-title'>📈 Reports & Analytics</h1>", unsafe_allow_html=True)
    
    all_requests = get_all_requests()
    
    if not all_requests:
        st.info("📊 No data available for reports")
        return
    
    # Summary stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Total Requests", len(all_requests), "📊")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        completed = len([r for r in all_requests if safe_get(r, 'status') == 'Completed'])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Completed", completed, "✅")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        pending = len([r for r in all_requests if safe_get(r, 'status') == 'Pending'])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Pending", pending, "⏳")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        total_amount = sum([safe_float(r.get('invoice_amount', 0)) for r in all_requests])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Total Value", format_ngn(total_amount), "💰")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h4>📊 Status Distribution</h4>", unsafe_allow_html=True)
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
        st.markdown("<h4>📈 Priority Distribution</h4>", unsafe_allow_html=True)
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

def show_assigned_jobs():
    """Show vendor's assigned jobs"""
    st.markdown("<h1 class='app-title'>🔧 Assigned Jobs</h1>", unsafe_allow_html=True)
    
    vendor_requests = get_vendor_requests(st.session_state.user['username'])
    assigned_jobs = [r for r in vendor_requests if safe_get(r, 'status') == 'Assigned']
    
    if not assigned_jobs:
        st.info("🎉 No assigned jobs found")
        return
    
    st.markdown(f"<div class='card'><h4>📋 You have {len(assigned_jobs)} assigned job(s)</h4></div>", unsafe_allow_html=True)
    
    for job in assigned_jobs:
        with st.expander(f"🔧 Job #{safe_get(job, 'id')}: {safe_str(safe_get(job, 'title'))}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Location:** {safe_str(safe_get(job, 'location'), 'Common Area')}")
                st.write(f"**Facility Type:** {safe_str(safe_get(job, 'facility_type'))}")
                st.write(f"**Priority:** {safe_str(safe_get(job, 'priority'))}")
                st.write(f"**Created By:** {safe_str(safe_get(job, 'created_by'))}")
                st.write(f"**Created Date:** {safe_str(safe_get(job, 'created_date'))}")
                st.write(f"**Description:** {safe_str(safe_get(job, 'description'))}")
            
            with col2:
                st.markdown("### 📝 Complete Job")
                with st.form(f"complete_job_{safe_get(job, 'id')}"):
                    completion_notes = st.text_area("Completion Notes *", 
                                                   placeholder="Describe what work was completed...")
                    job_breakdown = st.text_area("Breakdown of Job Done *", height=100,
                                               placeholder="Provide detailed breakdown of work completed...")
                    completion_date = st.date_input("Date Completed *")
                    invoice_amount = st.number_input("Invoice Amount (₦) *", min_value=0.0, step=1000.0, format="%.2f")
                    invoice_number = st.text_input("Invoice Number *", 
                                                  placeholder="e.g., INV-2023-001")
                    
                    submitted = st.form_submit_button("✅ Submit Completion", use_container_width=True)
                    
                    if submitted:
                        if not all([completion_notes, job_breakdown, invoice_amount, invoice_number]):
                            st.error("❌ Please fill in all required fields (*)")
                        else:
                            if execute_update(
                                '''UPDATE maintenance_requests SET status = ?, completion_notes = ?, job_breakdown = ?, 
                                completed_date = ?, invoice_amount = ?, invoice_number = ? WHERE id = ?''',
                                ('Completed', completion_notes, job_breakdown, completion_date.strftime('%Y-%m-%d'), 
                                 invoice_amount, invoice_number, safe_get(job, 'id'))
                            ):
                                st.success("✅ Job completed successfully! Waiting for approvals.")
                                st.rerun()

def show_completed_jobs():
    """Show vendor's completed jobs"""
    st.markdown("<h1 class='app-title'>✅ Completed Jobs</h1>", unsafe_allow_html=True)
    
    vendor_requests = get_vendor_requests(st.session_state.user['username'])
    completed_jobs = [r for r in vendor_requests if safe_get(r, 'status') in ['Completed', 'Approved']]
    
    if not completed_jobs:
        st.info("📭 No completed jobs found")
        return
    
    # Stats
    col1, col2 = st.columns(2)
    with col1:
        total = len(completed_jobs)
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Completed Jobs", total, "✅")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        total_revenue = sum([safe_float(j.get('invoice_amount', 0)) for j in completed_jobs])
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        create_metric_card("Total Revenue", format_ngn(total_revenue), "💰")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Display jobs
    for job in completed_jobs:
        status = safe_get(job, 'status')
        status_icon = '✅' if status == 'Completed' else '👍'
        
        with st.expander(f"{status_icon} Job #{safe_get(job, 'id')}: {safe_str(safe_get(job, 'title'))}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Title:** {safe_str(safe_get(job, 'title'))}")
                st.write(f"**Location:** {safe_str(safe_get(job, 'location'), 'Common Area')}")
                st.write(f"**Facility Type:** {safe_str(safe_get(job, 'facility_type'))}")
                st.write(f"**Job Breakdown:** {safe_str(safe_get(job, 'job_breakdown'), 'Not provided')}")
                st.write(f"**Completion Notes:** {safe_str(safe_get(job, 'completion_notes'), 'Not provided')}")
            
            with col2:
                st.write(f"**Invoice Amount:** {format_ngn(safe_get(job, 'invoice_amount'))}")
                st.write(f"**Invoice Number:** {safe_str(safe_get(job, 'invoice_number'), 'N/A')}")
                st.write(f"**Status:** {status}")
                st.write(f"**Completed Date:** {safe_str(safe_get(job, 'completed_date'), 'N/A')}")
                st.write(f"**Department Approval:** {'✅ Approved' if safe_get(job, 'requesting_dept_approval') else '⏳ Pending'}")
                st.write(f"**Manager Approval:** {'✅ Approved' if safe_get(job, 'facilities_manager_approval') else '⏳ Pending'}")

def show_vendor_registration():
    """Vendor registration"""
    st.markdown("<h1 class='app-title'>🏢 Vendor Registration</h1>", unsafe_allow_html=True)
    
    # Check if already registered
    existing_vendor = execute_query(
        'SELECT * FROM vendors WHERE username = ?',
        (st.session_state.user['username'],)
    )
    
    if existing_vendor:
        st.success("✅ You are already registered as a vendor!")
        vendor = existing_vendor[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Company Information**")
            st.write(f"**Company:** {safe_str(safe_get(vendor, 'company_name'))}")
            st.write(f"**Contact:** {safe_str(safe_get(vendor, 'contact_person'))}")
            st.write(f"**Email:** {safe_str(safe_get(vendor, 'email'))}")
            st.write(f"**Phone:** {safe_str(safe_get(vendor, 'phone'))}")
            st.write(f"**Type:** {safe_str(safe_get(vendor, 'vendor_type'))}")
            
            turnover = safe_get(vendor, 'annual_turnover')
            if turnover:
                st.write(f"**Annual Turnover:** {format_ngn(turnover)}")
            
            tax_id = safe_get(vendor, 'tax_identification_number')
            if tax_id:
                st.write(f"**Tax ID:** {tax_id}")
        
        with col2:
            st.markdown("**Services & Details**")
            st.write(f"**Services:** {safe_str(safe_get(vendor, 'services_offered'))}")
            
            key_staff = safe_get(vendor, 'key_management_staff')
            if key_staff:
                st.write(f"**Key Staff:** {key_staff}")
            
            account_details = safe_get(vendor, 'account_details')
            if account_details:
                st.write(f"**Account:** {account_details}")
            
            st.write(f"**Certification:** {safe_str(safe_get(vendor, 'certification'), 'Not specified')}")
            st.write(f"**Address:** {safe_str(safe_get(vendor, 'address'))}")
            st.write(f"**Registered:** {safe_str(safe_get(vendor, 'registration_date'))}")
        
        return
    
    # Registration form
    st.info("📝 Please complete your vendor registration details below:")
    
    with st.form("vendor_registration"):
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company Name *", placeholder="Your company name")
            contact_person = st.text_input("Contact Person *", placeholder="Full name")
            email = st.text_input("Email *", placeholder="company@example.com")
            phone = st.text_input("Phone *", placeholder="+234 XXX XXX XXXX")
            vendor_type = st.text_input("Vendor Type", value=st.session_state.user['vendor_type'], disabled=True)
            annual_turnover = st.number_input("Annual Turnover (₦)", min_value=0.0, step=100000.0, format="%.2f")
            tax_identification_number = st.text_input("Tax ID Number", placeholder="TIN-XXXXXXXXX")
            rc_number = st.text_input("RC Number", placeholder="RC-XXXXXXXX")
        
        with col2:
            services_offered = st.text_area("Services Offered *", height=100,
                                          placeholder="List all services your company provides...")
            key_management_staff = st.text_area("Key Management Staff", height=80,
                                              placeholder="CEO: John Doe\nCTO: Jane Smith...")
            account_details = st.text_area("Account Details", height=80,
                                         placeholder="Bank: XYZ Bank\nAccount: 1234567890\nSort Code: 123456")
            certification = st.text_input("Certification", placeholder="e.g., ISO 9001:2015")
            address = st.text_area("Address *", height=80,
                                 placeholder="Full company address...")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        submitted = st.form_submit_button("🚀 Register Vendor", use_container_width=True)
        
        if submitted:
            if not all([company_name, contact_person, email, phone, services_offered, address]):
                st.error("❌ Please fill in all required fields (*)")
            else:
                success = execute_update(
                    '''INSERT INTO vendors (company_name, contact_person, email, phone, vendor_type, services_offered, 
                    annual_turnover, tax_identification_number, rc_number, key_management_staff, account_details, 
                    certification, address, username) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (company_name, contact_person, email, phone, st.session_state.user['vendor_type'], services_offered,
                     annual_turnover, tax_identification_number, rc_number, key_management_staff, account_details,
                     certification, address, st.session_state.user['username'])
                )
                if success:
                    st.success("✅ Vendor registration completed successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to complete registration")

def show_invoice_creation():
    """Create invoices for completed jobs"""
    st.markdown("<h1 class='app-title'>🧾 Invoice Creation</h1>", unsafe_allow_html=True)
    
    # Get vendor's completed jobs without invoices
    vendor_jobs = execute_query('''
        SELECT mr.* 
        FROM maintenance_requests mr
        LEFT JOIN invoices i ON mr.id = i.request_id
        WHERE mr.assigned_vendor = ? AND mr.status = 'Completed' AND i.id IS NULL
        ORDER BY mr.completed_date DESC
    ''', (st.session_state.user['username'],))
    
    if not vendor_jobs:
        st.info("📭 No jobs available for invoicing")
        return
    
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h4>📋 Select Job for Invoice Creation</h4>", unsafe_allow_html=True)
    
    job_options = {f"#{safe_get(job, 'id')}: {safe_str(safe_get(job, 'title'))} - {safe_str(safe_get(job, 'location'), 'Common Area')}": safe_get(job, 'id') 
                   for job in vendor_jobs}
    
    selected_job_key = st.selectbox("Choose a completed job", list(job_options.keys()))
    selected_job_id = job_options[selected_job_key]
    
    selected_job = next((job for job in vendor_jobs if safe_get(job, 'id') == selected_job_id), None)
    
    if selected_job:
        st.write(f"**Job:** {safe_str(safe_get(selected_job, 'title'))}")
        st.write(f"**Location:** {safe_str(safe_get(selected_job, 'location'), 'Common Area')}")
        st.write(f"**Description:** {safe_str(safe_get(selected_job, 'description'))}")
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Invoice form
        with st.form("invoice_form"):
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<h4>📄 Invoice Details</h4>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                invoice_number = st.text_input("Invoice Number *", placeholder="INV-YYYY-XXXX")
                invoice_date = st.date_input("Invoice Date *")
                details_of_work = st.text_area("Details of Work *", height=100,
                                             value=safe_str(safe_get(selected_job, 'job_breakdown'), ''))
                quantity = st.number_input("Quantity *", min_value=1, value=1)
            
            with col2:
                unit_cost = st.number_input("Unit Cost (₦) *", min_value=0.0, step=1000.0, format="%.2f")
                labour_charge = st.number_input("Labour/Service Charge (₦)", min_value=0.0, step=1000.0, format="%.2f")
                vat_applicable = st.checkbox("Apply VAT (7.5%)")
            
            # Calculate amounts
            amount = quantity * unit_cost
            subtotal = amount + labour_charge
            vat_amount = subtotal * 0.075 if vat_applicable else 0
            total_amount = subtotal + vat_amount
            
            # Display calculations
            st.markdown("---")
            st.markdown("<h4>💰 Invoice Summary</h4>", unsafe_allow_html=True)
            
            calc_col1, calc_col2, calc_col3 = st.columns(3)
            with calc_col1:
                st.metric("Amount", format_ngn(amount))
            with calc_col2:
                st.metric("Labour Charge", format_ngn(labour_charge))
            with calc_col3:
                st.metric("VAT Amount", format_ngn(vat_amount))
            
            st.markdown(f"<h3 style='color: #1e3a8a; text-align: center;'>Total Amount: {format_ngn(total_amount)}</h3>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            submitted = st.form_submit_button("📤 Create Invoice", use_container_width=True)
            
            if submitted:
                if not all([invoice_number, details_of_work]):
                    st.error("❌ Please fill in all required fields (*)")
                else:
                    # Check if invoice number exists
                    existing = execute_query('SELECT * FROM invoices WHERE invoice_number = ?', (invoice_number,))
                    if existing:
                        st.error("❌ Invoice number already exists")
                    else:
                        success = execute_update(
                            '''INSERT INTO invoices (invoice_number, request_id, vendor_username, invoice_date, 
                            details_of_work, quantity, unit_cost, amount, labour_charge, vat_applicable, vat_amount, total_amount) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            (invoice_number, selected_job_id, st.session_state.user['username'], 
                             invoice_date.strftime('%Y-%m-%d'), details_of_work, quantity, unit_cost, 
                             amount, labour_charge, vat_applicable, vat_amount, total_amount)
                        )
                        if success:
                            st.success("✅ Invoice created successfully!")
                        else:
                            st.error("❌ Failed to create invoice")

def show_job_invoice_reports():
    """Job & Invoice Reports with PDF download"""
    st.markdown("<h1 class='app-title'>📄 Job & Invoice Reports</h1>", unsafe_allow_html=True)
    
    # Get completed jobs with invoices
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
    col1, col2 = st.columns(2)
    with col1:
        status_options = ["All"] + sorted(list(set(safe_str(safe_get(job, 'status')) for job in completed_jobs if safe_get(job, 'status'))))
        status_filter = st.selectbox("Filter by Job Status", status_options)
    with col2:
        invoice_options = ["All", "With Invoice", "Without Invoice"]
        invoice_filter = st.selectbox("Filter by Invoice Status", invoice_options)
    
    # Apply filters
    filtered_jobs = completed_jobs
    if status_filter != "All":
        filtered_jobs = [job for job in filtered_jobs if safe_str(safe_get(job, 'status')) == status_filter]
    if invoice_filter == "With Invoice":
        filtered_jobs = [job for job in filtered_jobs if safe_get(job, 'invoice_number') is not None]
    elif invoice_filter == "Without Invoice":
        filtered_jobs = [job for job in filtered_jobs if safe_get(job, 'invoice_number') is None]
    
    st.markdown(f"<div class='card'><h4>📊 Found {len(filtered_jobs)} job(s)</h4></div>", unsafe_allow_html=True)
    
    # Display jobs with PDF download
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
                    
                    # Get detailed invoice
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
            
            # PDF Generation
            if invoice_number and invoice_details:
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"📄 Generate PDF Report", key=f"pdf_{job_id}", use_container_width=True):
                        with st.spinner("Generating PDF..."):
                            pdf_buffer = generate_job_invoice_pdf(job, invoice_details[0])
                            st.success("✅ PDF generated!")
                            
                            # Download button
                            st.download_button(
                                label="⬇️ Download PDF Report",
                                data=pdf_buffer.getvalue(),
                                file_name=f"Job_Report_{job_id}_{invoice_number}.pdf",
                                mime="application/pdf",
                                key=f"download_{job_id}"
                            )
                with col2:
                    # Preview
                    if st.button("👁️ Preview PDF", key=f"preview_{job_id}", use_container_width=True):
                        pdf_buffer = generate_job_invoice_pdf(job, invoice_details[0])
                        base64_pdf = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
                        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
                        st.markdown(pdf_display, unsafe_allow_html=True)

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

# =============================================
# DASHBOARD FUNCTIONS
# =============================================
def show_user_dashboard():
    """User dashboard"""
    user_requests = get_user_requests(st.session_state.user['username'])
    
    # Stats
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
    
    # Recent requests
    st.markdown("<div class='section-header'>📋 Recent Requests</div>", unsafe_allow_html=True)
    
    if user_requests:
        display_data = []
        for req in user_requests[:5]:
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
                'Created': safe_str(safe_get(req, 'created_date'))[:10] if safe_get(req, 'created_date') else 'N/A'
            })
        
        df = pd.DataFrame(display_data)
        st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.info("📭 No maintenance requests found")

def show_manager_dashboard():
    """Manager dashboard"""
    all_requests = get_all_requests()
    
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

def show_vendor_dashboard():
    """Vendor dashboard"""
    vendor_requests = get_vendor_requests(st.session_state.user['username'])
    
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

def show_dashboard():
    """Main dashboard router"""
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
# MAIN APPLICATION ROUTING
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
        
        st.markdown("<div class='section-header'>📱 Navigation</div>", unsafe_allow_html=True)
        
        # Navigation based on user role
        if role == 'facility_user':
            menu_options = ["📊 Dashboard", "📝 Create Request", "📋 My Requests"]
        elif role == 'facility_manager':
            menu_options = ["📊 Dashboard", "🛠️ Manage Requests", "👥 Vendor Management", 
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
        "🛠️ Manage Requests": show_manage_requests,
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

def main():
    # Initialize session state
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    # Show appropriate page
    if st.session_state.user is None:
        show_enhanced_login()
    else:
        show_main_app()

if __name__ == "__main__":
    main()
