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

# Enhanced safe data access functions
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

# PDF Generation functions
def generate_job_completion_pdf(request_data, invoice_data=None):
    """Generate PDF report for job completion and invoice"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center alignment
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
    
    # Sidebar
    with st.sidebar:
        st.title(f"Welcome, {user['username']}")
        st.write(f"**Role:** {role.replace('_', ' ').title()}")
        if user['vendor_type']:
            st.write(f"**Vendor Type:** {user['vendor_type']}")
        
        st.markdown("---")
        
        # Navigation based on user role
        if role == 'facility_user':
            menu_options = ["Dashboard", "Create Request", "My Requests"]
        elif role == 'facility_manager':
            menu_options = ["Dashboard", "Manage Requests", "Vendor Management", "Reports", "Job & Invoice Reports"]
        else:  # vendor
            menu_options = ["Dashboard", "Assigned Jobs", "Completed Jobs", "Vendor Registration", "Invoice Creation"]
        
        selected_menu = st.radio("Navigation", menu_options)
        
        st.markdown("---")
        if st.button("Logout"):
            st.session_state.user = None
            st.rerun()
    
    # Main content
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
    else:  # vendor
        show_vendor_dashboard()

def show_user_dashboard():
    user_requests = get_user_requests(st.session_state.user['username'])
    
    # Stats
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
    
    # Recent requests
    st.subheader("Recent Requests")
    if user_requests:
        # Create safe display data
        display_data = []
        for req in user_requests[:10]:  # Show only first 10
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

def show_manager_dashboard():
    all_requests = get_all_requests()
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Requests", len(all_requests))
    
    with col2:
        pending_count = len([r for r in all_requests if safe_get(r, 'status') == 'Pending'])
        st.metric("Pending", pending_count)
    
    with col3:
        assigned_count = len([r for r in all_requests if safe_get(r, 'status') == 'Assigned'])
        st.metric("Assigned", assigned_count)
    
    with col4:
        completed_count = len([r for r in all_requests if safe_get(r, 'status') == 'Completed'])
        st.metric("Completed", completed_count)
    
    st.markdown("---")
    
    # Charts
    if all_requests:
        col1, col2 = st.columns(2)
        
        with col1:
            # Status distribution
            status_counts = {}
            for req in all_requests:
                status = safe_str(safe_get(req, 'status'), 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            if status_counts:
                fig = px.pie(values=list(status_counts.values()), names=list(status_counts.keys()), 
                            title="Request Status Distribution")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Facility type distribution
            facility_counts = {}
            for req in all_requests:
                facility_type = safe_str(safe_get(req, 'facility_type'), 'Unknown')
                facility_counts[facility_type] = facility_counts.get(facility_type, 0) + 1
            
            if facility_counts:
                fig = px.bar(x=list(facility_counts.values()), y=list(facility_counts.keys()), 
                            title="Requests by Facility Type", orientation='h')
                st.plotly_chart(fig, use_container_width=True)
    
    # Recent requests
    st.subheader("Recent Requests")
    if all_requests:
        # Create safe display data
        display_data = []
        for req in all_requests[:10]:
            display_data.append({
                'id': safe_get(req, 'id'),
                'title': safe_str(safe_get(req, 'title'), 'N/A'),
                'location': safe_str(safe_get(req, 'location'), 'Common Area'),
                'facility_type': safe_str(safe_get(req, 'facility_type'), 'N/A'),
                'priority': safe_str(safe_get(req, 'priority'), 'N/A'),
                'status': safe_str(safe_get(req, 'status'), 'N/A'),
                'created_by': safe_str(safe_get(req, 'created_by'), 'N/A'),
                'created_date': safe_str(safe_get(req, 'created_date'), 'N/A')
            })
        
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No maintenance requests found")

def show_vendor_dashboard():
    vendor_requests = get_vendor_requests(st.session_state.user['username'])
    
    # Stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        assigned_count = len([r for r in vendor_requests if safe_get(r, 'status') == 'Assigned'])
        st.metric("Assigned Jobs", assigned_count)
    
    with col2:
        completed_count = len([r for r in vendor_requests if safe_get(r, 'status') == 'Completed'])
        st.metric("Completed Jobs", completed_count)
    
    with col3:
        st.metric("Total Jobs", len(vendor_requests))
    
    st.markdown("---")
    
    # Assigned jobs
    st.subheader("Currently Assigned Jobs")
    assigned_jobs = [r for r in vendor_requests if safe_get(r, 'status') == 'Assigned']
    
    if assigned_jobs:
        display_data = []
        for job in assigned_jobs:
            display_data.append({
                'id': safe_get(job, 'id'),
                'title': safe_str(safe_get(job, 'title'), 'N/A'),
                'location': safe_str(safe_get(job, 'location'), 'Common Area'),
                'facility_type': safe_str(safe_get(job, 'facility_type'), 'N/A'),
                'priority': safe_str(safe_get(job, 'priority'), 'N/A'),
                'created_date': safe_str(safe_get(job, 'created_date'), 'N/A')
            })
        
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No currently assigned jobs")

def show_create_request():
    st.title("📝 Create Maintenance Request")
    
    with st.form("create_request_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Request Title")
            location = st.selectbox(
                "Location",
                ["Water Treatment Plant", "Finance", "HR", "Admin", "Common Area", "Production", "Warehouse", "Office Building", "Laboratory"]
            )
            facility_type = st.selectbox(
                "Facility Type",
                ["HVAC (Cooling Systems)", "Generator Maintenance", "Fixture and Fittings", 
                 "Building Maintenance", "HSE", "Space Management"]
            )
        
        with col2:
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        
        description = st.text_area("Description of the Request", height=100, 
                                 placeholder="Please provide detailed description of the maintenance request...")
        
        submitted = st.form_submit_button("Submit Request")
        
        if submitted:
            if not all([title, description, location, facility_type, priority]):
                st.error("Please fill in all fields")
            else:
                success = execute_update(
                    'INSERT INTO maintenance_requests (title, description, location, facility_type, priority, created_by) VALUES (?, ?, ?, ?, ?, ?)',
                    (title, description, location, facility_type, priority, st.session_state.user['username'])
                )
                if success:
                    st.success("Maintenance request created successfully!")
                else:
                    st.error("Failed to create request")

def show_my_requests():
    st.title("📋 My Maintenance Requests")
    
    user_requests = get_user_requests(st.session_state.user['username'])
    
    if not user_requests:
        st.info("No maintenance requests found")
        return
    
    # Create safe display data
    display_data = []
    for req in user_requests:
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
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        status_options = ["All"] + list(df['status'].unique())
        status_filter = st.selectbox("Filter by Status", status_options)
    with col2:
        priority_options = ["All"] + list(df['priority'].unique())
        priority_filter = st.selectbox("Filter by Priority", priority_options)
    with col3:
        facility_options = ["All"] + list(df['facility_type'].unique())
        facility_filter = st.selectbox("Filter by Facility Type", facility_options)
    with col4:
        location_options = ["All"] + list(df['location'].unique())
        location_filter = st.selectbox("Filter by Location", location_options)
    
    # Apply filters
    filtered_df = df
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    if priority_filter != "All":
        filtered_df = filtered_df[filtered_df['priority'] == priority_filter]
    if facility_filter != "All":
        filtered_df = filtered_df[filtered_df['facility_type'] == facility_filter]
    if location_filter != "All":
        filtered_df = filtered_df[filtered_df['location'] == location_filter]
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Request details
    st.subheader("Request Details")
    selected_id = st.selectbox("Select Request to View Details", [""] + [str(safe_get(req, 'id')) for req in user_requests])
    
    if selected_id:
        request = next((r for r in user_requests if str(safe_get(r, 'id')) == selected_id), None)
        if request:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Basic Information**")
                st.write(f"**Title:** {safe_str(safe_get(request, 'title'), 'N/A')}")
                st.write(f"**Description:** {safe_str(safe_get(request, 'description'), 'N/A')}")
                st.write(f"**Location:** {safe_str(safe_get(request, 'location'), 'Common Area')}")
                st.write(f"**Facility Type:** {safe_str(safe_get(request, 'facility_type'), 'N/A')}")
                st.write(f"**Priority:** {safe_str(safe_get(request, 'priority'), 'N/A')}")
                st.write(f"**Status:** {safe_str(safe_get(request, 'status'), 'N/A')}")
            
            with col2:
                st.write("**Additional Information**")
                st.write(f"**Created Date:** {safe_str(safe_get(request, 'created_date'), 'N/A')}")
                if safe_get(request, 'assigned_vendor'):
                    st.write(f"**Assigned Vendor:** {safe_str(safe_get(request, 'assigned_vendor'))}")
                if safe_get(request, 'completion_notes'):
                    st.write(f"**Completion Notes:** {safe_str(safe_get(request, 'completion_notes'))}")
                if safe_get(request, 'job_breakdown'):
                    st.write(f"**Job Breakdown:** {safe_str(safe_get(request, 'job_breakdown'))}")
                if safe_get(request, 'invoice_amount'):
                    st.write(f"**Invoice Amount:** ${safe_float(safe_get(request, 'invoice_amount')):.2f}")
                    st.write(f"**Invoice Number:** {safe_str(safe_get(request, 'invoice_number'), 'N/A')}")
            
            # Approval button for completed requests
            if (safe_get(request, 'status') == 'Completed' and 
                not safe_get(request, 'requesting_dept_approval') and
                safe_get(request, 'created_by') == st.session_state.user['username']):
                
                if st.button("Approve (Department)"):
                    if execute_update(
                        'UPDATE maintenance_requests SET requesting_dept_approval = 1 WHERE id = ?',
                        (safe_get(request, 'id'),)
                    ):
                        st.success("Department approval granted!")
                        st.rerun()

# ... (other functions like show_manage_requests, show_vendor_management, show_reports remain similar with safe functions)

def show_assigned_jobs():
    st.title("🔧 Assigned Jobs")
    
    vendor_requests = get_vendor_requests(st.session_state.user['username'])
    assigned_jobs = [r for r in vendor_requests if safe_get(r, 'status') == 'Assigned']
    
    if not assigned_jobs:
        st.info("No assigned jobs found")
        return
    
    st.subheader(f"You have {len(assigned_jobs)} assigned job(s)")
    
    for job in assigned_jobs:
        with st.expander(f"Job #{safe_get(job, 'id')}: {safe_str(safe_get(job, 'title'), 'N/A')} - {safe_str(safe_get(job, 'priority'), 'N/A')} Priority"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Location:** {safe_str(safe_get(job, 'location'), 'Common Area')}")
                st.write(f"**Facility Type:** {safe_str(safe_get(job, 'facility_type'), 'N/A')}")
                st.write(f"**Description:** {safe_str(safe_get(job, 'description'), 'N/A')}")
                st.write(f"**Created By:** {safe_str(safe_get(job, 'created_by'), 'N/A')}")
                st.write(f"**Created Date:** {safe_str(safe_get(job, 'created_date'), 'N/A')}")
            
            with col2:
                st.subheader("Complete Job")
                with st.form(f"complete_job_{safe_get(job, 'id')}"):
                    completion_notes = st.text_area("Completion Notes")
                    job_breakdown = st.text_area("Breakdown of Job Done", height=100, 
                                               placeholder="Provide detailed breakdown of work completed...")
                    completion_date = st.date_input("Date Completed")
                    invoice_amount = st.number_input("Invoice Amount ($)", min_value=0.0, step=0.01)
                    invoice_number = st.text_input("Invoice Number")
                    
                    if st.form_submit_button("Submit Completion"):
                        if not all([completion_notes, job_breakdown, invoice_amount, invoice_number]):
                            st.error("Please fill in all fields")
                        else:
                            if execute_update(
                                '''UPDATE maintenance_requests SET status = ?, completion_notes = ?, job_breakdown = ?, 
                                completed_date = ?, invoice_amount = ?, invoice_number = ? WHERE id = ?''',
                                ('Completed', completion_notes, job_breakdown, completion_date.strftime('%Y-%m-%d'), 
                                 invoice_amount, invoice_number, safe_get(job, 'id'))
                            ):
                                st.success("Job completed successfully! Waiting for approvals.")
                                st.rerun()

def show_completed_jobs():
    st.title("✅ Completed Jobs")
    
    vendor_requests = get_vendor_requests(st.session_state.user['username'])
    completed_jobs = [r for r in vendor_requests if safe_get(r, 'status') in ['Completed', 'Approved']]
    
    if not completed_jobs:
        st.info("No completed jobs found")
        return
    
    st.subheader(f"You have completed {len(completed_jobs)} job(s)")
    
    display_data = []
    for job in completed_jobs:
        display_data.append({
            'id': safe_get(job, 'id'),
            'title': safe_str(safe_get(job, 'title'), 'N/A'),
            'location': safe_str(safe_get(job, 'location'), 'Common Area'),
            'facility_type': safe_str(safe_get(job, 'facility_type'), 'N/A'),
            'invoice_amount': safe_float(safe_get(job, 'invoice_amount')),
            'invoice_number': safe_str(safe_get(job, 'invoice_number'), 'N/A'),
            'status': safe_str(safe_get(job, 'status'), 'N/A'),
            'completed_date': safe_str(safe_get(job, 'completed_date'), 'N/A')
        })
    
    df = pd.DataFrame(display_data)
    st.dataframe(df, use_container_width=True)
    
    # Job details
    st.subheader("Job Details")
    selected_id = st.selectbox("Select Job to View Details", [""] + [str(safe_get(job, 'id')) for job in completed_jobs])
    
    if selected_id:
        job = next((j for j in completed_jobs if str(safe_get(j, 'id')) == selected_id), None)
        if job:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Job Information**")
                st.write(f"**Title:** {safe_str(safe_get(job, 'title'), 'N/A')}")
                st.write(f"**Description:** {safe_str(safe_get(job, 'description'), 'N/A')}")
                st.write(f"**Location:** {safe_str(safe_get(job, 'location'), 'Common Area')}")
                st.write(f"**Facility Type:** {safe_str(safe_get(job, 'facility_type'), 'N/A')}")
                st.write(f"**Job Breakdown:** {safe_str(safe_get(job, 'job_breakdown'), 'Not provided')}")
                st.write(f"**Completion Notes:** {safe_str(safe_get(job, 'completion_notes'), 'Not provided')}")
            
            with col2:
                st.write("**Financial & Status**")
                st.write(f"**Invoice Amount:** ${safe_float(safe_get(job, 'invoice_amount')):.2f}")
                st.write(f"**Invoice Number:** {safe_str(safe_get(job, 'invoice_number'), 'N/A')}")
                st.write(f"**Status:** {safe_str(safe_get(job, 'status'), 'N/A')}")
                st.write(f"**Completed Date:** {safe_str(safe_get(job, 'completed_date'), 'N/A')}")
                st.write(f"**Department Approval:** {'✅ Approved' if safe_get(job, 'requesting_dept_approval') else '❌ Pending'}")
                st.write(f"**Manager Approval:** {'✅ Approved' if safe_get(job, 'facilities_manager_approval') else '❌ Pending'}")

def show_vendor_registration():
    st.title("🏢 Vendor Registration")
    
    # Check if vendor is already registered
    existing_vendor = execute_query(
        'SELECT * FROM vendors WHERE username = ?',
        (st.session_state.user['username'],)
    )
    
    if existing_vendor:
        st.success("✅ You are already registered as a vendor!")
        vendor = existing_vendor[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Company Information**")
            st.write(f"**Company Name:** {safe_str(safe_get(vendor, 'company_name'), 'N/A')}")
            st.write(f"**Contact Person:** {safe_str(safe_get(vendor, 'contact_person'), 'N/A')}")
            st.write(f"**Email:** {safe_str(safe_get(vendor, 'email'), 'N/A')}")
            st.write(f"**Phone:** {safe_str(safe_get(vendor, 'phone'), 'N/A')}")
            st.write(f"**Vendor Type:** {safe_str(safe_get(vendor, 'vendor_type'), 'N/A')}")
            annual_turnover = safe_get(vendor, 'annual_turnover')
            if annual_turnover:
                st.write(f"**Annual Turnover:** ${safe_float(annual_turnover):,.2f}")
            else:
                st.write("**Annual Turnover:** Not specified")
            tax_id = safe_get(vendor, 'tax_identification_number')
            st.write(f"**Tax ID:** {safe_str(tax_id)}" if tax_id else "**Tax ID:** Not specified")
            rc_number = safe_get(vendor, 'rc_number')
            st.write(f"**RC Number:** {safe_str(rc_number)}" if rc_number else "**RC Number:** Not specified")
        
        with col2:
            st.write("**Services & Details**")
            st.write(f"**Services Offered:** {safe_str(safe_get(vendor, 'services_offered'), 'N/A')}")
            key_staff = safe_get(vendor, 'key_management_staff')
            st.write(f"**Key Management Staff:** {safe_str(key_staff)}" if key_staff else "**Key Management Staff:** Not specified")
            account_details = safe_get(vendor, 'account_details')
            st.write(f"**Account Details:** {safe_str(account_details)}" if account_details else "**Account Details:** Not specified")
            st.write(f"**Certification:** {safe_str(safe_get(vendor, 'certification'), 'Not specified')}")
            st.write(f"**Address:** {safe_str(safe_get(vendor, 'address'), 'N/A')}")
            st.write(f"**Registration Date:** {safe_str(safe_get(vendor, 'registration_date'), 'N/A')}")
        
        return
    
    # Registration form
    st.info("Please complete your vendor registration details below:")
    
    with st.form("vendor_registration"):
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company Name *")
            contact_person = st.text_input("Contact Person *")
            email = st.text_input("Email *")
            phone = st.text_input("Phone *")
            vendor_type = st.text_input("Vendor Type", value=st.session_state.user['vendor_type'], disabled=True)
            annual_turnover = st.number_input("Annual Turnover ($)", min_value=0.0, step=1000.0, format="%.2f")
            tax_identification_number = st.text_input("Tax Identification Number")
            rc_number = st.text_input("RC Number")
        
        with col2:
            services_offered = st.text_area("Services Offered *", height=100)
            key_management_staff = st.text_area("Key Management Staff", height=80, 
                                              placeholder="List key management staff and their positions...")
            account_details = st.text_area("Account Details", height=80, 
                                         placeholder="Bank name, account number, routing number...")
            certification = st.text_input("Certification (Optional)")
            address = st.text_area("Address *", height=80)
        
        st.subheader("Attachments")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            certificate_incorporation = st.file_uploader("Certificate of Incorporation", type=['pdf', 'doc', 'docx'])
        with col2:
            tax_clearance_certificate = st.file_uploader("Tax Clearance Certificate", type=['pdf', 'doc', 'docx'])
        with col3:
            audited_financial_statement = st.file_uploader("Audited Financial Statement (Optional)", type=['pdf', 'doc', 'docx'])
        
        submitted = st.form_submit_button("Register Vendor")
        
        if submitted:
            if not all([company_name, contact_person, email, phone, services_offered, address]):
                st.error("Please fill in all required fields (*)")
            else:
                # Convert file uploads to binary data
                cert_inc_data = certificate_incorporation.read() if certificate_incorporation else None
                tax_clear_data = tax_clearance_certificate.read() if tax_clearance_certificate else None
                audited_fin_data = audited_financial_statement.read() if audited_financial_statement else None
                
                success = execute_update(
                    '''INSERT INTO vendors (company_name, contact_person, email, phone, vendor_type, services_offered, 
                    annual_turnover, tax_identification_number, rc_number, key_management_staff, account_details, 
                    certification, address, username, certificate_incorporation, tax_clearance_certificate, audited_financial_statement) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (company_name, contact_person, email, phone, st.session_state.user['vendor_type'], services_offered,
                     annual_turnover, tax_identification_number, rc_number, key_management_staff, account_details,
                     certification, address, st.session_state.user['username'], cert_inc_data, tax_clear_data, audited_fin_data)
                )
                if success:
                    st.success("Vendor registration completed successfully!")
                    st.rerun()
                else:
                    st.error("Failed to complete registration")

def show_invoice_creation():
    st.title("🧾 Invoice Creation")
    
    # Get vendor's completed jobs that don't have invoices yet
    vendor_jobs = execute_query('''
        SELECT mr.* 
        FROM maintenance_requests mr
        LEFT JOIN invoices i ON mr.id = i.request_id
        WHERE mr.assigned_vendor = ? AND mr.status = 'Completed' AND i.id IS NULL
        ORDER BY mr.completed_date DESC
    ''', (st.session_state.user['username'],))
    
    if not vendor_jobs:
        st.info("No jobs available for invoicing")
        return
    
    st.subheader("Select Job for Invoice Creation")
    job_options = {f"#{safe_get(job, 'id')}: {safe_str(safe_get(job, 'title'), 'N/A')} - {safe_str(safe_get(job, 'location'), 'Common Area')}": safe_get(job, 'id') for job in vendor_jobs}
    selected_job_key = st.selectbox("Choose a completed job", list(job_options.keys()))
    selected_job_id = job_options[selected_job_key]
    
    selected_job = next((job for job in vendor_jobs if safe_get(job, 'id') == selected_job_id), None)
    
    if selected_job:
        st.write(f"**Job Details:** {safe_str(safe_get(selected_job, 'title'), 'N/A')}")
        st.write(f"**Location:** {safe_str(safe_get(selected_job, 'location'), 'Common Area')}")
        st.write(f"**Description:** {safe_str(safe_get(selected_job, 'description'), 'N/A')}")
        
        st.markdown("---")
        st.subheader("Invoice Details")
        
        with st.form("invoice_creation_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                invoice_number = st.text_input("Invoice Number *")
                invoice_date = st.date_input("Invoice Date *")
                details_of_work = st.text_area("Details of Work Done *", height=100,
                                             value=safe_str(safe_get(selected_job, 'job_breakdown'), ''))
                quantity = st.number_input("Quantity *", min_value=1, value=1)
            
            with col2:
                unit_cost = st.number_input("Unit Cost ($) *", min_value=0.0, step=0.01, format="%.2f")
                labour_charge = st.number_input("Labour/Installation/Service Charge ($)", min_value=0.0, step=0.01, format="%.2f")
                vat_applicable = st.checkbox("Apply VAT (7.5%)")
            
            # Calculate amounts
            amount = quantity * unit_cost
            subtotal = amount + labour_charge
            vat_amount = subtotal * 0.075 if vat_applicable else 0
            total_amount = subtotal + vat_amount
            
            # Display calculations
            st.markdown("---")
            st.subheader("Invoice Summary")
            
            calc_col1, calc_col2, calc_col3 = st.columns(3)
            with calc_col1:
                st.metric("Amount", f"${amount:.2f}")
            with calc_col2:
                st.metric("Labour Charge", f"${labour_charge:.2f}")
            with calc_col3:
                st.metric("VAT Amount", f"${vat_amount:.2f}")
            
            st.metric("**Total Amount**", f"**${total_amount:.2f}**")
            
            submitted = st.form_submit_button("Create Invoice")
            
            if submitted:
                if not all([invoice_number, details_of_work]):
                    st.error("Please fill in all required fields (*)")
                else:
                    # Check if invoice number already exists
                    existing_invoice = execute_query('SELECT * FROM invoices WHERE invoice_number = ?', (invoice_number,))
                    if existing_invoice:
                        st.error("Invoice number already exists. Please use a different invoice number.")
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
                            st.success("Invoice created successfully!")
                        else:
                            st.error("Failed to create invoice")

def show_job_invoice_reports():
    st.title("📋 Job & Invoice Reports")
    
    # Get all completed and approved jobs with their invoices
    completed_jobs = execute_query('''
        SELECT mr.*, i.invoice_number, i.invoice_date, i.total_amount as invoice_total, i.status as invoice_status
        FROM maintenance_requests mr
        LEFT JOIN invoices i ON mr.id = i.request_id
        WHERE mr.status IN ('Completed', 'Approved')
        ORDER BY mr.completed_date DESC
    ''')
    
    if not completed_jobs:
        st.info("No completed jobs with invoices found")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_options = ["All"] + list(set(safe_str(safe_get(job, 'status')) for job in completed_jobs))
        status_filter = st.selectbox("Filter by Job Status", status_options)
    with col2:
        location_options = ["All"] + list(set(safe_str(safe_get(job, 'location'), 'Common Area') for job in completed_jobs))
        location_filter = st.selectbox("Filter by Location", location_options)
    with col3:
        has_invoice_filter = st.selectbox("Filter by Invoice", ["All", "With Invoice", "Without Invoice"])
    
    # Apply filters
    filtered_jobs = completed_jobs
    if status_filter != "All":
        filtered_jobs = [job for job in filtered_jobs if safe_str(safe_get(job, 'status')) == status_filter]
    if location_filter != "All":
        filtered_jobs = [job for job in filtered_jobs if safe_str(safe_get(job, 'location'), 'Common Area') == location_filter]
    if has_invoice_filter == "With Invoice":
        filtered_jobs = [job for job in filtered_jobs if safe_get(job, 'invoice_number') is not None]
    elif has_invoice_filter == "Without Invoice":
        filtered_jobs = [job for job in filtered_jobs if safe_get(job, 'invoice_number') is None]
    
    st.subheader(f"Found {len(filtered_jobs)} job(s)")
    
    # Display jobs
    for job in filtered_jobs:
        with st.expander(f"Job #{safe_get(job, 'id')}: {safe_str(safe_get(job, 'title'), 'N/A')} - {safe_str(safe_get(job, 'location'), 'Common Area')} - {safe_str(safe_get(job, 'status'), 'N/A')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Job Information**")
                st.write(f"**Title:** {safe_str(safe_get(job, 'title'), 'N/A')}")
                st.write(f"**Location:** {safe_str(safe_get(job, 'location'), 'Common Area')}")
                st.write(f"**Facility Type:** {safe_str(safe_get(job, 'facility_type'), 'N/A')}")
                st.write(f"**Priority:** {safe_str(safe_get(job, 'priority'), 'N/A')}")
                st.write(f"**Status:** {safe_str(safe_get(job, 'status'), 'N/A')}")
                st.write(f"**Created By:** {safe_str(safe_get(job, 'created_by'), 'N/A')}")
                st.write(f"**Assigned Vendor:** {safe_str(safe_get(job, 'assigned_vendor'), 'Not assigned')}")
                if safe_get(job, 'job_breakdown'):
                    st.write(f"**Job Breakdown:** {safe_str(safe_get(job, 'job_breakdown'))}")
            
            with col2:
                st.write("**Invoice Information**")
                if safe_get(job, 'invoice_number'):
                    st.write(f"**Invoice Number:** {safe_str(safe_get(job, 'invoice_number'))}")
                    st.write(f"**Invoice Date:** {safe_str(safe_get(job, 'invoice_date'))}")
                    st.write(f"**Invoice Amount:** ${safe_float(safe_get(job, 'invoice_total')):.2f}")
                    st.write(f"**Invoice Status:** {safe_str(safe_get(job, 'invoice_status'), 'N/A')}")
                    
                    # Get detailed invoice information
                    invoice_details = execute_query(
                        'SELECT * FROM invoices WHERE invoice_number = ?', 
                        (safe_get(job, 'invoice_number'),)
                    )
                    if invoice_details:
                        invoice = invoice_details[0]
                        st.write("**Invoice Details:**")
                        st.write(f"Details of Work: {safe_str(safe_get(invoice, 'details_of_work'), 'N/A')}")
                        st.write(f"Quantity: {safe_str(safe_get(invoice, 'quantity'), '0')}")
                        st.write(f"Unit Cost: ${safe_float(safe_get(invoice, 'unit_cost')):.2f}")
                        st.write(f"Amount: ${safe_float(safe_get(invoice, 'amount')):.2f}")
                        st.write(f"Labour Charge: ${safe_float(safe_get(invoice, 'labour_charge')):.2f}")
                        st.write(f"VAT Applied: {'Yes' if safe_get(invoice, 'vat_applicable') else 'No'}")
                        st.write(f"VAT Amount: ${safe_float(safe_get(invoice, 'vat_amount')):.2f}")
                        st.write(f"Total Amount: ${safe_float(safe_get(invoice, 'total_amount')):.2f}")
                else:
                    st.write("**No invoice created yet**")
                
                st.write("**Approval Status**")
                st.write(f"**Department Approval:** {'✅ Approved' if safe_get(job, 'requesting_dept_approval') else '❌ Pending'}")
                st.write(f"**Manager Approval:** {'✅ Approved' if safe_get(job, 'facilities_manager_approval') else '❌ Pending'}")
            
            # Generate PDF report
            if safe_get(job, 'invoice_number'):
                invoice_details = execute_query(
                    'SELECT * FROM invoices WHERE invoice_number = ?', 
                    (safe_get(job, 'invoice_number'),)
                )
                if invoice_details:
                    if st.button(f"Generate PDF Report for Job #{safe_get(job, 'id')}"):
                        pdf_buffer = generate_job_completion_pdf(job, invoice_details[0])
                        st.download_button(
                            label="Download PDF Report",
                            data=pdf_buffer.getvalue(),
                            file_name=f"job_report_{safe_get(job, 'id')}_{safe_get(job, 'invoice_number')}.pdf",
                            mime="application/pdf"
                        )

if __name__ == "__main__":
    main()
