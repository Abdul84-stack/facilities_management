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

# Page configuration
st.set_page_config(
    page_title="Facilities Management System",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        cursor.execute('ALTER TABLE maintenance_requests ADD COLUMN location TEXT DEFAULT "Common Area"')
    
    if 'job_breakdown' not in columns:
        cursor.execute('ALTER TABLE maintenance_requests ADD COLUMN job_breakdown TEXT')
    
    # Check if vendors table has new columns
    cursor.execute("PRAGMA table_info(vendors)")
    vendor_columns = [column[1] for column in cursor.fetchall()]
    
    if 'vendors' not in [table[0] for table in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
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
    
    conn.commit()
    conn.close()

# Initialize database
init_database()

# Database functions
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

# Safe data access functions
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

# Authentication
def authenticate_user(username, password):
    user = execute_query('SELECT * FROM users WHERE username = ? AND password_hash = ?', (username, password))
    return user[0] if user else None

# PDF Generation
def generate_job_completion_pdf(request_data, invoice_data=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1
    )
    story.append(Paragraph("JOB COMPLETION AND INVOICE REPORT", title_style))
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
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
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
    
    if safe_get(request_data, 'job_breakdown'):
        story.append(Paragraph("JOB BREAKDOWN", styles['Heading2']))
        story.append(Paragraph(safe_str(safe_get(request_data, 'job_breakdown')), styles['Normal']))
        story.append(Spacer(1, 20))
    
    if safe_get(request_data, 'completion_notes'):
        story.append(Paragraph("COMPLETION NOTES", styles['Heading2']))
        story.append(Paragraph(safe_str(safe_get(request_data, 'completion_notes')), styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Invoice Information
    if invoice_data:
        story.append(Paragraph("INVOICE DETAILS", styles['Heading2']))
        invoice_info = [
            ["Invoice Number:", safe_str(safe_get(invoice_data, 'invoice_number'), 'N/A')],
            ["Invoice Date:", safe_str(safe_get(invoice_data, 'invoice_date'), 'N/A')],
            ["Details of Work:", safe_str(safe_get(invoice_data, 'details_of_work'), 'N/A')],
            ["Quantity:", safe_str(safe_get(invoice_data, 'quantity'), '0')],
            ["Unit Cost:", f"${safe_float(safe_get(invoice_data, 'unit_cost')):.2f}"],
            ["Amount:", f"${safe_float(safe_get(invoice_data, 'amount')):.2f}"],
            ["Labour/Service Charge:", f"${safe_float(safe_get(invoice_data, 'labour_charge')):.2f}"],
            ["VAT Applicable:", "Yes" if safe_get(invoice_data, 'vat_applicable') else "No"],
            ["VAT Amount:", f"${safe_float(safe_get(invoice_data, 'vat_amount')):.2f}"],
            ["Total Amount:", f"${safe_float(safe_get(invoice_data, 'total_amount')):.2f}"]
        ]
        
        invoice_table = Table(invoice_info, colWidths=[150, 300])
        invoice_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
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
        ["Department Approval:", "APPROVED" if safe_get(request_data, 'requesting_dept_approval') else "PENDING"],
        ["Facilities Manager Approval:", "APPROVED" if safe_get(request_data, 'facilities_manager_approval') else "PENDING"]
    ]
    
    approval_table = Table(approval_data, colWidths=[150, 300])
    approval_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(approval_table)
    
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
    st.title("🏢 Facilities Management System")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Login")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")
            
            if login_button:
                user = authenticate_user(username, password)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        st.markdown("---")
        st.subheader("Sample Credentials")
        st.code("""
Facility User: facility_user / 0123456
Facility Manager: facility_manager / 0123456
Vendors: hvac_vendor / 0123456
         generator_vendor / 0123456
         fixture_vendor / 0123456
        """)

def show_main_app():
    user = st.session_state.user
    role = user['role']
    
    with st.sidebar:
        st.title(f"Welcome, {user['username']}")
        st.write(f"**Role:** {role.replace('_', ' ').title()}")
        if user['vendor_type']:
            st.write(f"**Vendor Type:** {user['vendor_type']}")
        
        st.markdown("---")
        
        if role == 'facility_user':
            menu_options = ["Dashboard", "Create Request", "My Requests"]
        elif role == 'facility_manager':
            menu_options = ["Dashboard", "Manage Requests", "Vendor Management", "Reports", "Job & Invoice Reports"]
        else:
            menu_options = ["Dashboard", "Assigned Jobs", "Completed Jobs", "Vendor Registration", "Invoice Creation"]
        
        selected_menu = st.radio("Navigation", menu_options)
        
        st.markdown("---")
        if st.button("Logout"):
            st.session_state.user = None
            st.rerun()
    
    if selected_menu == "Dashboard":
        show_dashboard()
    elif selected_menu == "Create Request":
        show_create_request()
    elif selected_menu == "My Requests":
        show_my_requests()
    elif selected_menu == "Manage Requests":
        show_manage_requests()
    elif selected_menu == "Vendor Management":
        show_vendor_management()
    elif selected_menu == "Reports":
        show_reports()
    elif selected_menu == "Assigned Jobs":
        show_assigned_jobs()
    elif selected_menu == "Completed Jobs":
        show_completed_jobs()
    elif selected_menu == "Vendor Registration":
        show_vendor_registration()
    elif selected_menu == "Invoice Creation":
        show_invoice_creation()
    elif selected_menu == "Job & Invoice Reports":
        show_job_invoice_reports()

def show_dashboard():
    st.title("📊 Dashboard")
    user = st.session_state.user
    role = user['role']
    
    if role == 'facility_user':
        show_user_dashboard()
    elif role == 'facility_manager':
        show_manager_dashboard()
    else:
        show_vendor_dashboard()

def show_user_dashboard():
    user_requests = get_user_requests(st.session_state.user['username'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Requests", len(user_requests))
    with col2:
        pending_count = len([r for r in user_requests if safe_get(r, 'status') == 'Pending'])
        st.metric("Pending", pending_count)
    with col3:
        completed_count = len([r for r in user_requests if safe_get(r, 'status') == 'Completed'])
        st.metric("Completed", completed_count)
    
    st.markdown("---")
    st.subheader("Recent Requests")
    
    if user_requests:
        display_data = []
        for req in user_requests[:10]:
            display_data.append({
                'id': safe_get(req, 'id'),
                'title': safe_str(safe_get(req, 'title'), 'N/A'),
                'location': safe_str(safe_get(req, 'location'), 'Common Area'),
                'facility_type': safe_str(safe_get(req, 'facility_type'), 'N/A'),
                'priority': safe_str(safe_get(req, 'priority'), 'N/A'),
                'status': safe_str(safe_get(req, 'status'), 'N/A'),
                'created_date': safe_str(safe_get(req, 'created_date'), 'N/A')
            })
        
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No maintenance requests found")

# ... (Include all other functions from the previous working version)

if __name__ == "__main__":
    main()
