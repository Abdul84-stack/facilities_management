import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime
import base64
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import tempfile
import os

# Page configuration with enhanced UI
st.set_page_config(
    page_title="Facilities Management System",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "### Facilities Management System v2.0\nDeveloped by Abdulahi Ibrahim\n© 2024 All Rights Reserved"
    }
)

# Custom CSS for enhanced UI
st.markdown("""
    <style>
    /* Main styling */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Login page styling */
    .login-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        color: white;
    }
    
    .login-title {
        text-align: center;
        font-size: 2.5em;
        margin-bottom: 30px;
        color: white;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #4CAF50, #2E7D32);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 16px;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    
    /* Form styling */
    .stTextInput > div > div > input,
    .stTextInput > div > div > input:focus {
        background-color: rgba(255,255,255,0.9);
        border: 2px solid #ddd;
        border-radius: 8px;
        padding: 12px;
        font-size: 16px;
    }
    
    .stSelectbox > div > div > div,
    .stTextArea > div > div > textarea {
        background-color: rgba(255,255,255,0.9);
        border: 2px solid #ddd;
        border-radius: 8px;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(90deg, #1a237e, #283593);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Card styling */
    .card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* Currency styling */
    .currency-naira {
        color: #4CAF50;
        font-weight: bold;
        font-size: 1.1em;
    }
    
    /* Footer styling */
    .footer {
        position: fixed;
        bottom: 0;
        width: 100%;
        background: linear-gradient(90deg, #1a237e, #283593);
        color: white;
        text-align: center;
        padding: 10px;
        font-size: 12px;
        z-index: 1000;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2c3e50, #34495e);
        color: white;
    }
    
    /* Metric card styling */
    .stMetric {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Custom separator */
    .separator {
        height: 4px;
        background: linear-gradient(90deg, #4CAF50, #2196F3);
        border-radius: 2px;
        margin: 20px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Database setup with schema migration
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
    
    # Check if maintenance_requests table has location column
    cursor.execute("PRAGMA table_info(maintenance_requests)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'maintenance_requests' not in [table[0] for table in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
        # Create maintenance_requests table with new location field
        cursor.execute('''
            CREATE TABLE maintenance_requests (
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
    elif 'location' not in columns:
        # Add location column to existing table
        cursor.execute('ALTER TABLE maintenance_requests ADD COLUMN location TEXT DEFAULT "Common Area"')
    
    if 'job_breakdown' not in columns:
        cursor.execute('ALTER TABLE maintenance_requests ADD COLUMN job_breakdown TEXT')
    
    # Check if vendors table has new columns
    cursor.execute("PRAGMA table_info(vendors)")
    vendor_columns = [column[1] for column in cursor.fetchall()]
    
    if 'vendors' not in [table[0] for table in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
        # Create vendors table with new fields
        cursor.execute('''
            CREATE TABLE vendors (
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
    else:
        # Add new columns to existing vendors table
        new_vendor_columns = [
            'annual_turnover', 'tax_identification_number', 'rc_number', 
            'key_management_staff', 'account_details', 'certificate_incorporation',
            'tax_clearance_certificate', 'audited_financial_statement'
        ]
        for column in new_vendor_columns:
            if column not in vendor_columns:
                if column in ['annual_turnover']:
                    cursor.execute(f'ALTER TABLE vendors ADD COLUMN {column} REAL')
                elif column in ['certificate_incorporation', 'tax_clearance_certificate', 'audited_financial_statement']:
                    cursor.execute(f'ALTER TABLE vendors ADD COLUMN {column} BLOB')
                else:
                    cursor.execute(f'ALTER TABLE vendors ADD COLUMN {column} TEXT')
    
    # Invoices table - UPDATED CURRENCY TO NAIRA
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
            currency TEXT DEFAULT '₦',
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (request_id) REFERENCES maintenance_requests (id)
        )
    ''')
    
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
    
    # Also create sample vendor registrations with Naira amounts
    sample_vendors = [
        ('hvac_vendor', 'HVAC Solutions Inc.', 'John HVAC', 'hvac@example.com', '123-456-7890', 'HVAC', 
         'HVAC installation, maintenance and repair services', 50000000.00, 'TIN123456', 'RC789012',
         'John Smith (CEO), Jane Doe (Operations Manager)', 'Bank: Zenith Bank, Acc: 1234567890', 
         'HVAC Certified', '123 HVAC Street, Lagos'),
        ('generator_vendor', 'Generator Pros Ltd.', 'Mike Generator', 'generator@example.com', '123-456-7891', 'Generator',
         'Generator installation and maintenance', 30000000.00, 'TIN123457', 'RC789013',
         'Mike Johnson (Director)', 'Bank: First Bank, Acc: 9876543210', 
         'Generator Specialist', '456 Power Ave, Abuja'),
        ('fixture_vendor', 'Fixture Masters Co.', 'Sarah Fixtures', 'fixtures@example.com', '123-456-7892', 'Fixture and Fittings',
         'Fixture installation and repairs', 25000000.00, 'TIN123458', 'RC789014',
         'Sarah Wilson (Owner)', 'Bank: GTBank, Acc: 4561237890', 
         'Fixture Expert', '789 Fixture Road, Port Harcourt'),
        ('building_vendor', 'Building Care Services', 'David Builder', 'building@example.com', '123-456-7893', 'Building Maintenance',
         'General building maintenance and repairs', 40000000.00, 'TIN123459', 'RC789015',
         'David Brown (Manager)', 'Bank: Access Bank, Acc: 7894561230', 
         'Building Maintenance Certified', '321 Builders Lane, Kano')
    ]
    
    for username, company_name, contact_person, email, phone, vendor_type, services_offered, annual_turnover, tax_id, rc_number, key_staff, account_details, certification, address in sample_vendors:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO vendors 
                (username, company_name, contact_person, email, phone, vendor_type, services_offered, 
                 annual_turnover, tax_identification_number, rc_number, key_management_staff, 
                 account_details, certification, address) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, company_name, contact_person, email, phone, vendor_type, services_offered,
                  annual_turnover, tax_id, rc_number, key_staff, account_details, certification, address))
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()

# Initialize database
init_database()

# Database functions with safe column access
def get_connection():
    return sqlite3.connect('facilities_management.db')

def execute_query(query, params=()):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = [dict(row) for row in cursor.fetchall()]
    conn.commit()
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

# Enhanced safe data access functions with Naira formatting
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

def format_naira(amount, decimal_places=2):
    """Format amount as Naira currency"""
    try:
        amount = safe_float(amount, 0)
        if amount >= 1000000:
            return f"₦{amount/1000000:.{decimal_places}f}M"
        elif amount >= 1000:
            return f"₦{amount/1000:.{decimal_places}f}K"
        else:
            return f"₦{amount:.{decimal_places}f}"
    except:
        return f"₦0.00"

def get_user_requests(username):
    """Get user requests with safe column access"""
    return execute_query(
        'SELECT * FROM maintenance_requests WHERE created_by = ? ORDER BY created_date DESC',
        (username,)
    )

def get_all_requests():
    """Get all requests with safe column access"""
    return execute_query('SELECT * FROM maintenance_requests ORDER BY created_date DESC')

def get_vendor_requests(vendor_username):
    """Get vendor requests with safe column access"""
    return execute_query(
        'SELECT * FROM maintenance_requests WHERE assigned_vendor = ? ORDER BY created_date DESC',
        (vendor_username,)
    )

# Authentication
def authenticate_user(username, password):
    user = execute_query('SELECT * FROM users WHERE username = ? AND password_hash = ?', (username, password))
    return user[0] if user else None

# PDF Generation functions with Naira currency
def generate_job_completion_pdf(request_data, invoice_data=None):
    """Generate PDF report for job completion and invoice"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom title with trademark and developer info
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        alignment=1,
        textColor=colors.HexColor('#1a237e')
    )
    
    # Header with copyright and trademark
    header_text = "FACILITIES MANAGEMENT SYSTEM™<br/>" + \
                 "Job Completion and Invoice Report<br/>" + \
                 "<font size=10>© 2024 All Rights Reserved | Developed by Abdulahi Ibrahim</font>"
    story.append(Paragraph(header_text, title_style))
    story.append(Spacer(1, 20))
    
    # Job Information
    story.append(Paragraph("JOB INFORMATION", styles['Heading2']))
    job_info_data = [
        ["Request ID:", safe_str(safe_get(request_data, 'id'), 'N/A')],
        ["Title:", safe_str(safe_get(request_data, 'title'), 'N/A')],
        ["Description:", safe_str(safe_get(request_data, 'description'), 'N/A')],
        ["Location:", safe_str(safe_get(request_data, 'location'), 'Common Area')],
        ["Facility Type:", safe_str(safe_get(request_data, 'facility_type'), 'N/A')],
        ["Priority:", safe_str(safe_get(request_data, 'priority'), 'N/A')],
        ["Status:", safe_str(safe_get(request_data, 'status'), 'N/A')],
        ["Created By:", safe_str(safe_get(request_data, 'created_by'), 'N/A')],
        ["Assigned Vendor:", safe_str(safe_get(request_data, 'assigned_vendor'), 'Not assigned')],
        ["Created Date:", safe_str(safe_get(request_data, 'created_date'), 'N/A')],
        ["Completed Date:", safe_str(safe_get(request_data, 'completed_date'), 'N/A')]
    ]
    
    job_table = Table(job_info_data, colWidths=[150, 300])
    job_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(job_table)
    story.append(Spacer(1, 20))
    
    # Job Breakdown
    if safe_get(request_data, 'job_breakdown'):
        story.append(Paragraph("JOB BREAKDOWN", styles['Heading2']))
        story.append(Paragraph(safe_str(safe_get(request_data, 'job_breakdown')), styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Completion Notes
    if safe_get(request_data, 'completion_notes'):
        story.append(Paragraph("COMPLETION NOTES", styles['Heading2']))
        story.append(Paragraph(safe_str(safe_get(request_data, 'completion_notes')), styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Invoice Information with Naira currency
    if invoice_data:
        story.append(Paragraph("INVOICE DETAILS", styles['Heading2']))
        invoice_info = [
            ["Invoice Number:", safe_str(safe_get(invoice_data, 'invoice_number'), 'N/A')],
            ["Invoice Date:", safe_str(safe_get(invoice_data, 'invoice_date'), 'N/A')],
            ["Details of Work:", safe_str(safe_get(invoice_data, 'details_of_work'), 'N/A')],
            ["Quantity:", safe_str(safe_get(invoice_data, 'quantity'), '0')],
            ["Unit Cost:", format_naira(safe_get(invoice_data, 'unit_cost'))],
            ["Amount:", format_naira(safe_get(invoice_data, 'amount'))],
            ["Labour/Service Charge:", format_naira(safe_get(invoice_data, 'labour_charge'))],
            ["VAT Applicable:", "Yes" if safe_get(invoice_data, 'vat_applicable') else "No"],
            ["VAT Amount:", format_naira(safe_get(invoice_data, 'vat_amount'))],
            ["Total Amount:", format_naira(safe_get(invoice_data, 'total_amount'))]
        ]
        
        invoice_table = Table(invoice_info, colWidths=[150, 300])
        invoice_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#283593')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(invoice_table)
    
    # Approval Status
    story.append(Spacer(1, 20))
    story.append(Paragraph("APPROVAL STATUS", styles['Heading2']))
    approval_data = [
        ["Department Approval:", "✅ APPROVED" if safe_get(request_data, 'requesting_dept_approval') else "⏳ PENDING"],
        ["Facilities Manager Approval:", "✅ APPROVED" if safe_get(request_data, 'facilities_manager_approval') else "⏳ PENDING"]
    ]
    
    approval_table = Table(approval_data, colWidths=[150, 300])
    approval_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
        ('BACKGROUND', (1, 0), (1, -1), colors.lightgreen),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(approval_table)
    
    # Footer with copyright
    story.append(Spacer(1, 30))
    footer_text = "© 2024 Facilities Management System™. All rights reserved.<br/>" + \
                  "Developed by Abdulahi Ibrahim<br/>" + \
                  "<font size=8>This is an official document generated by the Facilities Management System</font>"
    story.append(Paragraph(footer_text, ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        alignment=1,
        textColor=colors.grey
    )))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Main application
def main():
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    if st.session_state.user is None:
        show_login()
    else:
        show_main_app()

def show_login():
    # Beautiful login page with enhanced UI
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Login container with gradient background
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # App title with trademark
        st.markdown('<h1 class="login-title">🏢 FACILITIES MANAGEMENT SYSTEM™</h1>', unsafe_allow_html=True)
        st.markdown('<h3 style="text-align: center; color: rgba(255,255,255,0.9);">Secure Login Portal</h3>', unsafe_allow_html=True)
        
        # Separator
        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
        
        # Login form
        with st.form("login_form"):
            st.markdown('<h3 style="color: white;">🔐 User Login</h3>', unsafe_allow_html=True)
            
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
            
            login_col1, login_col2, login_col3 = st.columns([1, 2, 1])
            with login_col2:
                login_button = st.form_submit_button("🚀 Login", use_container_width=True)
            
            if login_button:
                if username and password:
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state.user = user
                        st.success("Login successful! Redirecting...")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.warning("⚠️ Please enter both username and password")
        
        # Separator
        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
        
        # Sample credentials card
        st.markdown('<div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin-top: 20px;">', unsafe_allow_html=True)
        st.markdown('<h4 style="color: white;">📋 Sample Credentials</h4>', unsafe_allow_html=True)
        
        credentials = """
        👥 **Facility User:** 
        • Username: facility_user
        • Password: 0123456
        
        👨‍💼 **Facility Manager:** 
        • Username: facility_manager
        • Password: 0123456
        
        🏢 **Vendors:**
        • HVAC Solutions: hvac_vendor / 0123456
        • Generator Pros: generator_vendor / 0123456
        • Fixture Masters: fixture_vendor / 0123456
        • Building Care: building_vendor / 0123456
        """
        st.code(credentials, language=None)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Footer with copyright and developer info
        st.markdown("""
            <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.2);">
                <p style="color: rgba(255,255,255,0.8); font-size: 12px;">
                    © 2024 Facilities Management System™ | Developed by Abdulahi Ibrahim<br>
                    All trademarks and copyrights belong to their respective owners
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Add custom footer
    st.markdown("""
        <div class="footer">
            FACILITIES MANAGEMENT SYSTEM™ © 2024 | Currency: Nigerian Naira (₦) | Developed by Abdulahi Ibrahim
        </div>
    """, unsafe_allow_html=True)

def show_main_app():
    user = st.session_state.user
    role = user['role']
    
    # Custom header with trademark
    st.markdown(f"""
        <div class="header-container">
            <h1 style="margin: 0; display: flex; align-items: center; gap: 10px;">
                🏢 FACILITIES MANAGEMENT SYSTEM™
                <span style="font-size: 14px; background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 10px;">
                    v2.0
                </span>
            </h1>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">
                Welcome, <strong>{user['username']}</strong> | Role: {role.replace('_', ' ').title()} | 
                Currency: Nigerian Naira (₦) | © 2024 Developed by Abdulahi Ibrahim
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; padding: 10px; background: linear-gradient(45deg, #4CAF50, #2E7D32); 
                     border-radius: 10px; margin-bottom: 20px;">
                <h3 style="color: white; margin: 0;">👋 Welcome</h3>
                <p style="color: white; margin: 5px 0;">{}</p>
            </div>
        """.format(user['username']), unsafe_allow_html=True)
        
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                <p style="margin: 0;"><strong>Role:</strong> {role.replace('_', ' ').title()}</p>
                {f'<p style="margin: 0;"><strong>Vendor Type:</strong> {user["vendor_type"]}</p>' if user['vendor_type'] else ''}
                <p style="margin: 0;"><strong>Currency:</strong> Nigerian Naira (₦)</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
        
        # Navigation based on user role
        if role == 'facility_user':
            menu_options = ["📊 Dashboard", "📝 Create Request", "📋 My Requests"]
        elif role == 'facility_manager':
            menu_options = ["📊 Dashboard", "🛠️ Manage Requests", "👥 Vendor Management", 
                          "📈 Reports", "📋 Job & Invoice Reports"]
        else:  # vendor
            menu_options = ["📊 Dashboard", "🔧 Assigned Jobs", "✅ Completed Jobs", 
                          "🏢 Vendor Registration", "🧾 Invoice Creation"]
        
        selected_menu = st.radio("🗺️ Navigation", menu_options, label_visibility="collapsed")
        
        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()
        
        # Copyright info in sidebar
        st.markdown("""
            <div style="position: absolute; bottom: 20px; left: 0; right: 0; padding: 10px; 
                     text-align: center; font-size: 10px; color: rgba(255,255,255,0.6);">
                <hr style="margin: 10px 0;">
                © 2024 FMS™<br>
                Developed by Abdulahi Ibrahim<br>
                All Rights Reserved
            </div>
        """, unsafe_allow_html=True)
    
    # Main content routing
    menu_map = {
        "📊 Dashboard": "show_dashboard",
        "📝 Create Request": "show_create_request",
        "📋 My Requests": "show_my_requests",
        "🛠️ Manage Requests": "show_manage_requests",
        "👥 Vendor Management": "show_vendor_management",
        "📈 Reports": "show_reports",
        "📋 Job & Invoice Reports": "show_job_invoice_reports",
        "🔧 Assigned Jobs": "show_assigned_jobs",
        "✅ Completed Jobs": "show_completed_jobs",
        "🏢 Vendor Registration": "show_vendor_registration",
        "🧾 Invoice Creation": "show_invoice_creation"
    }
    
    if selected_menu in menu_map:
        globals()[menu_map[selected_menu]]()
    else:
        show_dashboard()

def show_dashboard():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("📊 Dashboard Overview")
    st.markdown('</div>', unsafe_allow_html=True)
    
    user = st.session_state.user
    role = user['role']
    
    if role == 'facility_user':
        show_user_dashboard()
    elif role == 'facility_manager':
        show_manager_dashboard()
    else:  # vendor
        show_vendor_dashboard()

def show_user_dashboard():
    user_requests = get_user_requests(st.session_state.user['username'])
    
    # Stats cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="stMetric">', unsafe_allow_html=True)
        st.metric("📊 Total Requests", len(user_requests))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stMetric">', unsafe_allow_html=True)
        pending_count = len([r for r in user_requests if safe_get(r, 'status') == 'Pending'])
        st.metric("⏳ Pending", pending_count, delta=f"{pending_count} pending" if pending_count > 0 else "All clear")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="stMetric">', unsafe_allow_html=True)
        completed_count = len([r for r in user_requests if safe_get(r, 'status') == 'Completed'])
        st.metric("✅ Completed", completed_count)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # Recent requests
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📋 Recent Requests")
    if user_requests:
        display_data = []
        for req in user_requests[:10]:
            display_data.append({
                'ID': safe_get(req, 'id'),
                'Title': safe_str(safe_get(req, 'title'), 'N/A'),
                'Location': safe_str(safe_get(req, 'location'), 'Common Area'),
                'Facility': safe_str(safe_get(req, 'facility_type'), 'N/A'),
                'Priority': safe_str(safe_get(req, 'priority'), 'N/A'),
                'Status': safe_str(safe_get(req, 'status'), 'N/A'),
                'Created': safe_str(safe_get(req, 'created_date'), 'N/A')[:10]
            })
        
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("📭 No maintenance requests found")
    st.markdown('</div>', unsafe_allow_html=True)

def show_manager_dashboard():
    all_requests = get_all_requests()
    
    # Stats cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="stMetric">', unsafe_allow_html=True)
        st.metric("📊 Total Requests", len(all_requests))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stMetric">', unsafe_allow_html=True)
        pending_count = len([r for r in all_requests if safe_get(r, 'status') == 'Pending'])
        st.metric("⏳ Pending", pending_count)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="stMetric">', unsafe_allow_html=True)
        assigned_count = len([r for r in all_requests if safe_get(r, 'status') == 'Assigned'])
        st.metric("👷 Assigned", assigned_count)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="stMetric">', unsafe_allow_html=True)
        completed_count = len([r for r in all_requests if safe_get(r, 'status') == 'Completed'])
        st.metric("✅ Completed", completed_count)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # Charts
    if all_requests:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            status_counts = {}
            for req in all_requests:
                status = safe_str(safe_get(req, 'status'), 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            if status_counts:
                fig = px.pie(values=list(status_counts.values()), names=list(status_counts.keys()), 
                            title="📈 Request Status Distribution", color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            facility_counts = {}
            for req in all_requests:
                facility_type = safe_str(safe_get(req, 'facility_type'), 'Unknown')
                facility_counts[facility_type] = facility_counts.get(facility_type, 0) + 1
            
            if facility_counts:
                fig = px.bar(x=list(facility_counts.values()), y=list(facility_counts.keys()), 
                            title="🏢 Requests by Facility Type", orientation='h',
                            color=list(facility_counts.values()),
                            color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Recent requests
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📋 Recent Requests")
    if all_requests:
        display_data = []
        for req in all_requests[:10]:
            display_data.append({
                'ID': safe_get(req, 'id'),
                'Title': safe_str(safe_get(req, 'title'), 'N/A'),
                'Location': safe_str(safe_get(req, 'location'), 'Common Area'),
                'Facility': safe_str(safe_get(req, 'facility_type'), 'N/A'),
                'Priority': safe_str(safe_get(req, 'priority'), 'N/A'),
                'Status': safe_str(safe_get(req, 'status'), 'N/A'),
                'Created By': safe_str(safe_get(req, 'created_by'), 'N/A'),
                'Created': safe_str(safe_get(req, 'created_date'), 'N/A')[:10]
            })
        
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("📭 No maintenance requests found")
    st.markdown('</div>', unsafe_allow_html=True)

def show_vendor_dashboard():
    vendor_requests = get_vendor_requests(st.session_state.user['username'])
    
    # Stats cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="stMetric">', unsafe_allow_html=True)
        assigned_count = len([r for r in vendor_requests if safe_get(r, 'status') == 'Assigned'])
        st.metric("🔧 Assigned Jobs", assigned_count)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="stMetric">', unsafe_allow_html=True)
        completed_count = len([r for r in vendor_requests if safe_get(r, 'status') == 'Completed'])
        st.metric("✅ Completed Jobs", completed_count)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="stMetric">', unsafe_allow_html=True)
        st.metric("📊 Total Jobs", len(vendor_requests))
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # Assigned jobs
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔧 Currently Assigned Jobs")
    assigned_jobs = [r for r in vendor_requests if safe_get(r, 'status') == 'Assigned']
    
    if assigned_jobs:
        display_data = []
        for job in assigned_jobs:
            display_data.append({
                'ID': safe_get(job, 'id'),
                'Title': safe_str(safe_get(job, 'title'), 'N/A'),
                'Location': safe_str(safe_get(job, 'location'), 'Common Area'),
                'Facility': safe_str(safe_get(job, 'facility_type'), 'N/A'),
                'Priority': safe_str(safe_get(job, 'priority'), 'N/A'),
                'Created': safe_str(safe_get(job, 'created_date'), 'N/A')[:10]
            })
        
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.success("🎉 All jobs are completed! No currently assigned jobs.")
    st.markdown('</div>', unsafe_allow_html=True)

# [Rest of the functions remain the same but with Naira formatting updates]
# Note: I'll show the key changes to the remaining functions...

def show_create_request():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("📝 Create Maintenance Request")
    st.markdown('</div>', unsafe_allow_html=True)
    
    with st.form("create_request_form"):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("📌 Request Title", placeholder="Enter request title")
            location = st.selectbox(
                "📍 Location",
                ["Water Treatment Plant", "Finance", "HR", "Admin", "Common Area", 
                 "Production", "Warehouse", "Office Building", "Laboratory"]
            )
            facility_type = st.selectbox(
                "🏢 Facility Type",
                ["HVAC (Cooling Systems)", "Generator Maintenance", "Fixture and Fittings", 
                 "Building Maintenance", "HSE", "Space Management"]
            )
        
        with col2:
            priority = st.selectbox("🚨 Priority", ["Low", "Medium", "High", "Critical"])
        
        description = st.text_area("📄 Description of the Request", height=100, 
                                 placeholder="Please provide detailed description of the maintenance request...")
        st.markdown('</div>', unsafe_allow_html=True)
        
        submitted = st.form_submit_button("🚀 Submit Request", use_container_width=True)
        
        if submitted:
            if not all([title, description, location, facility_type, priority]):
                st.error("⚠️ Please fill in all fields")
            else:
                success = execute_update(
                    'INSERT INTO maintenance_requests (title, description, location, facility_type, priority, created_by) VALUES (?, ?, ?, ?, ?, ?)',
                    (title, description, location, facility_type, priority, st.session_state.user['username'])
                )
                if success:
                    st.success("✅ Maintenance request created successfully!")
                else:
                    st.error("❌ Failed to create request")

# [Continue updating other functions with similar UI enhancements and Naira formatting...]

# In show_my_requests() and other functions, update currency displays:
# Replace: f"${safe_float(safe_get(request, 'invoice_amount')):.2f}"
# With: format_naira(safe_get(request, 'invoice_amount'))

# In show_invoice_creation():
def show_invoice_creation():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🧾 Invoice Creation")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Get vendor's completed jobs that don't have invoices yet
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
    
    st.subheader("📋 Select Job for Invoice Creation")
    job_options = {f"#{safe_get(job, 'id')}: {safe_str(safe_get(job, 'title'), 'N/A')} - {safe_str(safe_get(job, 'location'), 'Common Area')}": safe_get(job, 'id') for job in vendor_jobs}
    selected_job_key = st.selectbox("Choose a completed job", list(job_options.keys()))
    selected_job_id = job_options[selected_job_key]
    
    selected_job = next((job for job in vendor_jobs if safe_get(job, 'id') == selected_job_id), None)
    
    if selected_job:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write(f"**📌 Job Details:** {safe_str(safe_get(selected_job, 'title'), 'N/A')}")
        st.write(f"**📍 Location:** {safe_str(safe_get(selected_job, 'location'), 'Common Area')}")
        st.write(f"**📄 Description:** {safe_str(safe_get(selected_job, 'description'), 'N/A')}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
        st.subheader("💰 Invoice Details")
        
        with st.form("invoice_creation_form"):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            
            with col1:
                invoice_number = st.text_input("🔢 Invoice Number *")
                invoice_date = st.date_input("📅 Invoice Date *")
                details_of_work = st.text_area("🔧 Details of Work Done *", height=100,
                                             value=safe_str(safe_get(selected_job, 'job_breakdown'), ''))
                quantity = st.number_input("📦 Quantity *", min_value=1, value=1)
            
            with col2:
                # CHANGED FROM USD TO NAIRA
                unit_cost = st.number_input("💵 Unit Cost (₦) *", min_value=0.0, step=0.01, format="%.2f")
                labour_charge = st.number_input("👷 Labour/Service Charge (₦)", min_value=0.0, step=0.01, format="%.2f")
                vat_applicable = st.checkbox("🏛️ Apply VAT (7.5%)")
            
            # Calculate amounts
            amount = quantity * unit_cost
            subtotal = amount + labour_charge
            vat_amount = subtotal * 0.075 if vat_applicable else 0
            total_amount = subtotal + vat_amount
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Display calculations
            st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
            st.subheader("🧮 Invoice Summary")
            
            calc_col1, calc_col2, calc_col3, calc_col4 = st.columns(4)
            with calc_col1:
                st.markdown(f'<div class="stMetric"><h4>Amount</h4><h3 class="currency-naira">{format_naira(amount)}</h3></div>', unsafe_allow_html=True)
            with calc_col2:
                st.markdown(f'<div class="stMetric"><h4>Labour Charge</h4><h3 class="currency-naira">{format_naira(labour_charge)}</h3></div>', unsafe_allow_html=True)
            with calc_col3:
                st.markdown(f'<div class="stMetric"><h4>VAT Amount</h4><h3 class="currency-naira">{format_naira(vat_amount)}</h3></div>', unsafe_allow_html=True)
            with calc_col4:
                st.markdown(f'<div class="stMetric"><h4>Total Amount</h4><h3 class="currency-naira">{format_naira(total_amount)}</h3></div>', unsafe_allow_html=True)
            
            submitted = st.form_submit_button("📄 Create Invoice", use_container_width=True)
            
            if submitted:
                if not all([invoice_number, details_of_work]):
                    st.error("⚠️ Please fill in all required fields (*)")
                else:
                    existing_invoice = execute_query('SELECT * FROM invoices WHERE invoice_number = ?', (invoice_number,))
                    if existing_invoice:
                        st.error("❌ Invoice number already exists. Please use a different invoice number.")
                    else:
                        success = execute_update(
                            '''INSERT INTO invoices (invoice_number, request_id, vendor_username, invoice_date, 
                            details_of_work, quantity, unit_cost, amount, labour_charge, vat_applicable, vat_amount, total_amount, currency) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            (invoice_number, selected_job_id, st.session_state.user['username'], 
                             invoice_date.strftime('%Y-%m-%d'), details_of_work, quantity, unit_cost, 
                             amount, labour_charge, vat_applicable, vat_amount, total_amount, '₦')
                        )
                        if success:
                            st.success("✅ Invoice created successfully!")
                        else:
                            st.error("❌ Failed to create invoice")

# [Update all other financial displays similarly...]

if __name__ == "__main__":
    main()
