import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, date
import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from io import BytesIO
import random
import string

# Page configuration
st.set_page_config(
    page_title="Facilities Management System",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .login-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        color: white;
        max-width: 600px;
        margin: 0 auto;
    }
    .login-title {
        text-align: center;
        font-size: 2.5em;
        margin-bottom: 30px;
        color: white;
        font-weight: bold;
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
    .header-container {
        background: linear-gradient(90deg, #1a237e, #283593);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    .card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .separator {
        height: 4px;
        background: linear-gradient(90deg, #4CAF50, #2196F3);
        border-radius: 2px;
        margin: 20px 0;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    .alert-danger {
        background-color: #F8D7DA;
        border-left: 4px solid #DC3545;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
    .alert-success {
        background-color: #D4EDDA;
        border-left: 4px solid #28A745;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# ========== DATABASE SETUP ==========
def get_db_path():
    """Get the correct database path for local vs Streamlit Cloud"""
    if 'STREAMLIT_SHARING' in os.environ:
        return '/tmp/facilities_management.db'
    else:
        return 'facilities_management.db'

def get_connection():
    """Get database connection with correct path"""
    db_path = get_db_path()
    return sqlite3.connect(db_path)

def init_database():
    """Initialize database with tables and minimal sample data"""
    conn = get_connection()
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
            location TEXT NOT NULL DEFAULT "Common Area",
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
            username TEXT NOT NULL UNIQUE,
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
            vat_applicable BOOLEAN DEFAULT 0,
            vat_amount REAL DEFAULT 0,
            total_amount REAL NOT NULL,
            currency TEXT DEFAULT '₦',
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (request_id) REFERENCES maintenance_requests (id)
        )
    ''')
    
    # Preventive maintenance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS preventive_maintenance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipment_name TEXT NOT NULL,
            equipment_type TEXT NOT NULL,
            location TEXT NOT NULL,
            maintenance_type TEXT NOT NULL,
            frequency TEXT NOT NULL,
            last_maintenance_date DATE,
            next_maintenance_date DATE NOT NULL,
            status TEXT DEFAULT 'Upcoming',
            assigned_to TEXT,
            notes TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Generator records table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS generator_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_date DATE NOT NULL,
            generator_name TEXT NOT NULL,
            opening_hours REAL NOT NULL,
            closing_hours REAL NOT NULL,
            opening_diesel_level REAL NOT NULL,
            closing_diesel_level REAL NOT NULL,
            recorded_by TEXT NOT NULL,
            notes TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Space bookings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS space_bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_name TEXT NOT NULL,
            room_type TEXT NOT NULL,
            booking_date DATE NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            purpose TEXT NOT NULL,
            booked_by TEXT NOT NULL,
            department TEXT NOT NULL,
            attendees_count INTEGER,
            status TEXT DEFAULT 'Confirmed',
            catering_required BOOLEAN DEFAULT 0,
            special_requirements TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # HSE schedule table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hse_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inspection_type TEXT NOT NULL,
            area TEXT NOT NULL,
            frequency TEXT NOT NULL,
            last_inspection_date DATE,
            next_inspection_date DATE NOT NULL,
            assigned_to TEXT NOT NULL,
            status TEXT DEFAULT 'Upcoming',
            compliance_level TEXT DEFAULT 'Compliant',
            findings TEXT,
            corrective_actions TEXT,
            follow_up_date DATE,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # HSE incidents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hse_incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_date DATE NOT NULL,
            incident_time TEXT NOT NULL,
            location TEXT NOT NULL,
            incident_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            description TEXT NOT NULL,
            reported_by TEXT NOT NULL,
            affected_persons TEXT,
            immediate_actions TEXT,
            investigation_status TEXT DEFAULT 'Open',
            corrective_measures TEXT,
            status TEXT DEFAULT 'Open',
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Check and insert sample users if needed
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        sample_users = [
            ('facility_user', '0123456', 'facility_user', None),
            ('facility_manager', '0123456', 'facility_manager', None),
            ('hvac_vendor', '0123456', 'vendor', 'HVAC'),
            ('generator_vendor', '0123456', 'vendor', 'Generator'),
            ('fixture_vendor', '0123456', 'vendor', 'Fixture and Fittings'),
            ('building_vendor', '0123456', 'vendor', 'Building Maintenance'),
            ('hse_vendor', '0123456', 'vendor', 'HSE'),
            ('space_vendor', '0123456', 'vendor', 'Space Management'),
            ('hse_officer', '0123456', 'hse_officer', None),
            ('space_manager', '0123456', 'space_manager', None)
        ]
        for username, password, role, vendor_type in sample_users:
            cursor.execute(
                'INSERT INTO users (username, password_hash, role, vendor_type) VALUES (?, ?, ?, ?)',
                (username, password, role, vendor_type)
            )
    
    # Check and insert sample vendors if needed
    cursor.execute('SELECT COUNT(*) FROM vendors')
    if cursor.fetchone()[0] == 0:
        sample_vendors = [
            ('hvac_vendor', 'HVAC Solutions Inc.', 'John HVAC', 'hvac@example.com', '123-456-7890', 'HVAC', 
             'HVAC installation, maintenance and repair services', 50000000.00, 'TIN123456', 'RC789012',
             'John Smith (CEO), Jane Doe (Operations Manager)', 'Bank: Zenith Bank, Acc: 1234567890', 
             'HVAC Certified', '123 HVAC Street, Lagos'),
            ('generator_vendor', 'Generator Pros Ltd.', 'Mike Generator', 'generator@example.com', '123-456-7891', 'Generator',
             'Generator installation and maintenance', 30000000.00, 'TIN123457', 'RC789013',
             'Mike Johnson (Director)', 'Bank: First Bank, Acc: 9876543210', 
             'Generator Specialist', '456 Power Ave, Abuja'),
        ]
        for vendor_data in sample_vendors:
            cursor.execute('''
                INSERT INTO vendors 
                (username, company_name, contact_person, email, phone, vendor_type, services_offered, 
                 annual_turnover, tax_identification_number, rc_number, key_management_staff, 
                 account_details, certification, address) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', vendor_data)
    
    # Insert minimal preventive maintenance data (5 records)
    cursor.execute('SELECT COUNT(*) FROM preventive_maintenance')
    if cursor.fetchone()[0] == 0:
        today = datetime.now().date()
        sample_maintenance = [
            ('Main HVAC System', 'HVAC', 'Main Building', 'Routine Check', 'Monthly', 
             (today - timedelta(days=15)), (today + timedelta(days=15)), 'HVAC Team', 'Regular check'),
            ('Fire Extinguishers', 'Fire Safety', 'All Floors', 'Inspection', 'Biannual',
             (today - timedelta(days=60)), (today + timedelta(days=120)), 'Safety Officer', 'Fire safety'),
            ('Smoke Detectors', 'Fire Safety', 'All Floors', 'Testing', 'Quarterly',
             (today - timedelta(days=45)), (today + timedelta(days=45)), 'Maintenance Team', 'System test'),
            ('Generator Set #1', 'Generator', 'Generator Room', 'Service', '200 hours',
             (today - timedelta(days=10)), (today + timedelta(days=10)), 'Generator Team', 'Regular service'),
            ('Pest Control', 'General', 'Entire Facility', 'Fumigation', 'Quarterly',
             (today - timedelta(days=30)), (today + timedelta(days=60)), 'Pest Control Vendor', 'Fumigation')
        ]
        for data in sample_maintenance:
            cursor.execute('''
                INSERT INTO preventive_maintenance 
                (equipment_name, equipment_type, location, maintenance_type, frequency, 
                 last_maintenance_date, next_maintenance_date, assigned_to, notes) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', data)
    
    # Insert minimal generator records (3 records)
    cursor.execute('SELECT COUNT(*) FROM generator_records')
    if cursor.fetchone()[0] == 0:
        today = datetime.now().date()
        for i in range(3):
            record_date = today - timedelta(days=i)
            cursor.execute('''
                INSERT INTO generator_records 
                (record_date, generator_name, opening_hours, closing_hours, 
                 opening_diesel_level, closing_diesel_level, recorded_by, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (record_date, 'Generator #1', 1000 + i*8, 1008 + i*8, 500 - i*50, 450 - i*50, 'facility_user', f'Day {i+1}'))
    
    # Insert minimal space bookings (2 records)
    cursor.execute('SELECT COUNT(*) FROM space_bookings')
    if cursor.fetchone()[0] == 0:
        today = datetime.now().date()
        sample_bookings = [
            ('Conference Room A', 'Conference', today, '09:00', '12:00', 
             'Management Meeting', 'facility_manager', 'Management', 10, 'Confirmed', 0, None),
            ('Meeting Room B', 'Meeting', today + timedelta(days=1), '14:00', '16:00', 
             'Team Brainstorming', 'facility_user', 'Operations', 6, 'Confirmed', 0, None)
        ]
        for booking in sample_bookings:
            cursor.execute('''
                INSERT INTO space_bookings 
                (room_name, room_type, booking_date, start_time, end_time, purpose, 
                 booked_by, department, attendees_count, status, catering_required, special_requirements)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', booking)
    
    # Insert minimal HSE schedule (3 records)
    cursor.execute('SELECT COUNT(*) FROM hse_schedule')
    if cursor.fetchone()[0] == 0:
        today = datetime.now().date()
        sample_hse_schedule = [
            ('Fire Safety Inspection', 'All Buildings', 'Quarterly', 
             today - timedelta(days=45), today + timedelta(days=45), 'hse_officer', 'Compliant', None, None, None),
            ('First Aid Kit Check', 'All Floors', 'Monthly',
             today - timedelta(days=20), today + timedelta(days=10), 'hse_officer', 'Non-Compliant', 'Missing bandages', 'Restock', today + timedelta(days=7)),
            ('Emergency Exit Inspection', 'Main Building', 'Monthly',
             today - timedelta(days=15), today + timedelta(days=15), 'hse_officer', 'Compliant', None, None, None)
        ]
        for inspection in sample_hse_schedule:
            cursor.execute('''
                INSERT INTO hse_schedule 
                (inspection_type, area, frequency, last_inspection_date, next_inspection_date,
                 assigned_to, compliance_level, findings, corrective_actions, follow_up_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', inspection)
    
    conn.commit()
    conn.close()

# Database helper functions
def execute_query(query, params=()):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        st.error(f"Query error: {e}")
        results = []
    finally:
        conn.close()
    return results

def execute_update(query, params=()):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Database update error: {e}")
        return False
    finally:
        conn.close()

def safe_get(data, key, default=None):
    if not data or not isinstance(data, dict):
        return default
    return data.get(key, default)

def format_naira(amount):
    try:
        return f"₦{float(amount):,.2f}"
    except:
        return "₦0.00"

# Authentication function
def authenticate_user(username, password):
    users = execute_query('SELECT * FROM users WHERE username = ? AND password_hash = ?', (username, password))
    return users[0] if users else None

# ========== LOGIN PAGE ==========
def show_login():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="login-title">🏢 FACILITIES MANAGEMENT SYSTEM™</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align: center; color: rgba(255,255,255,0.9);">Secure Login Portal</h3>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("👤 Username", placeholder="Enter your username")
        password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
        
        if st.form_submit_button("🚀 Login", use_container_width=True):
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
    
    st.markdown("""
        <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin-top: 30px;">
            <h4 style="color: white;">📋 Sample Credentials</h4>
            <div style="color: white; font-size: 14px;">
                <p><strong>👥 Facility User:</strong> facility_user / 0123456</p>
                <p><strong>👨‍💼 Facility Manager:</strong> facility_manager / 0123456</p>
                <p><strong>🚨 HSE Officer:</strong> hse_officer / 0123456</p>
                <p><strong>🏢 Space Manager:</strong> space_manager / 0123456</p>
                <p><strong>🏢 Vendor (HVAC):</strong> hvac_vendor / 0123456</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ========== WORKFLOW FUNCTIONS ==========

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

# ========== CORE WORKFLOW PAGES ==========

def show_create_request():
    """Facility user creates a maintenance request"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("📝 Create Maintenance Request")
    st.markdown('</div>', unsafe_allow_html=True)
    
    with st.form("create_request_form"):
        title = st.text_input("Request Title", placeholder="Enter request title")
        location = st.selectbox("Location", ["Main Building", "Admin Block", "Production Area", "Warehouse"])
        facility_type = st.selectbox("Facility Type", ["HVAC", "Generator", "Electrical", "Plumbing", "Building"])
        priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        description = st.text_area("Description", placeholder="Describe the issue...")
        
        if st.form_submit_button("Submit Request"):
            if title and description:
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
    """Facility user views their requests"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("📋 My Maintenance Requests")
    st.markdown('</div>', unsafe_allow_html=True)
    
    requests = get_user_requests(st.session_state.user['username'])
    
    if not requests:
        st.info("📭 No maintenance requests found")
        return
    
    for req in requests:
        with st.expander(f"Request #{req['id']}: {req['title']} - {req['status']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Title:** {req['title']}")
                st.write(f"**Location:** {req['location']}")
                st.write(f"**Priority:** {req['priority']}")
                st.write(f"**Status:** {req['status']}")
            with col2:
                st.write(f"**Created:** {req['created_date']}")
                if req['assigned_vendor']:
                    st.write(f"**Assigned Vendor:** {req['assigned_vendor']}")
                if req['completion_notes']:
                    st.write(f"**Completion Notes:** {req['completion_notes']}")
            
            # Department approval for completed jobs
            if req['status'] == 'Completed' and not req['requesting_dept_approval']:
                if st.button(f"✅ Approve (Department)", key=f"dept_approve_{req['id']}"):
                    if execute_update(
                        'UPDATE maintenance_requests SET requesting_dept_approval = 1 WHERE id = ?',
                        (req['id'],)
                    ):
                        st.success("✅ Department approval granted!")
                        st.rerun()

def show_manage_requests():
    """Facility manager manages all requests"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🛠️ Manage Maintenance Requests")
    st.markdown('</div>', unsafe_allow_html=True)
    
    requests = get_all_requests()
    
    if not requests:
        st.info("📭 No maintenance requests found")
        return
    
    for req in requests:
        with st.expander(f"Request #{req['id']}: {req['title']} - {req['status']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Title:** {req['title']}")
                st.write(f"**Description:** {req['description']}")
                st.write(f"**Created By:** {req['created_by']}")
                st.write(f"**Priority:** {req['priority']}")
                st.write(f"**Status:** {req['status']}")
            
            with col2:
                # Assign to vendor for pending requests
                if req['status'] == 'Pending':
                    st.subheader("Assign to Vendor")
                    vendors = execute_query('SELECT * FROM vendors WHERE vendor_type LIKE ?', 
                                          (f"%{req['facility_type']}%",))
                    if vendors:
                        vendor_options = {v['company_name']: v['username'] for v in vendors}
                        selected_vendor = st.selectbox("Select Vendor", list(vendor_options.keys()), 
                                                     key=f"vendor_select_{req['id']}")
                        if st.button(f"Assign to {selected_vendor}", key=f"assign_{req['id']}"):
                            vendor_username = vendor_options[selected_vendor]
                            if execute_update(
                                'UPDATE maintenance_requests SET status = ?, assigned_vendor = ? WHERE id = ?',
                                ('Assigned', vendor_username, req['id'])
                            ):
                                st.success(f"✅ Request assigned to {selected_vendor}!")
                                st.rerun()
                    else:
                        st.warning("No vendors available for this facility type")
                
                # Manager approval for completed requests with department approval
                elif req['status'] == 'Completed' and req['requesting_dept_approval'] and not req['facilities_manager_approval']:
                    st.subheader("Manager Approval")
                    if st.button(f"✅ Approve as Manager", key=f"manager_approve_{req['id']}"):
                        if execute_update(
                            'UPDATE maintenance_requests SET status = ?, facilities_manager_approval = 1 WHERE id = ?',
                            ('Approved', req['id'])
                        ):
                            st.success("✅ Manager approval granted!")
                            st.rerun()

def show_assigned_jobs():
    """Vendor views and completes assigned jobs"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🔧 Assigned Jobs")
    st.markdown('</div>', unsafe_allow_html=True)
    
    jobs = get_vendor_requests(st.session_state.user['username'])
    assigned_jobs = [j for j in jobs if j['status'] == 'Assigned']
    
    if not assigned_jobs:
        st.success("🎉 No assigned jobs found")
        return
    
    for job in assigned_jobs:
        with st.expander(f"Job #{job['id']}: {job['title']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Title:** {job['title']}")
                st.write(f"**Description:** {job['description']}")
                st.write(f"**Location:** {job['location']}")
                st.write(f"**Priority:** {job['priority']}")
            
            with col2:
                st.subheader("Complete Job")
                with st.form(f"complete_job_{job['id']}"):
                    completion_notes = st.text_area("Completion Notes")
                    job_breakdown = st.text_area("Work Performed")
                    invoice_amount = st.number_input("Invoice Amount (₦)", min_value=0.0, step=0.01)
                    invoice_number = st.text_input("Invoice Number")
                    
                    if st.form_submit_button("✅ Submit Completion"):
                        if completion_notes and job_breakdown and invoice_amount and invoice_number:
                            success = execute_update(
                                '''UPDATE maintenance_requests SET 
                                status = ?, completion_notes = ?, job_breakdown = ?, 
                                completed_date = CURRENT_TIMESTAMP, invoice_amount = ?, invoice_number = ?
                                WHERE id = ?''',
                                ('Completed', completion_notes, job_breakdown, invoice_amount, invoice_number, job['id'])
                            )
                            if success:
                                st.success("✅ Job marked as completed!")
                                st.rerun()

def show_vendor_registration():
    """Facility manager registers new vendors"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🏢 Vendor Registration")
    st.markdown('</div>', unsafe_allow_html=True)
    
    with st.form("vendor_registration"):
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company Name *")
            contact_person = st.text_input("Contact Person *")
            email = st.text_input("Email *")
            phone = st.text_input("Phone *")
            vendor_type = st.selectbox("Vendor Type *", ["HVAC", "Generator", "Electrical", "Plumbing", "Building"])
        
        with col2:
            services_offered = st.text_area("Services Offered *")
            address = st.text_area("Address *")
            # Generate username and password
            vendor_username = company_name.lower().replace(' ', '_') + "_vendor"
            vendor_password = '0123456'
            
            st.markdown(f"""
                <div class="card">
                    <h4>Generated Login Details</h4>
                    <p><strong>Username:</strong> {vendor_username}</p>
                    <p><strong>Password:</strong> {vendor_password}</p>
                </div>
            """, unsafe_allow_html=True)
        
        if st.form_submit_button("Register Vendor"):
            if all([company_name, contact_person, email, phone, vendor_type, services_offered, address]):
                # Create user account for vendor
                user_success = execute_update(
                    'INSERT INTO users (username, password_hash, role, vendor_type) VALUES (?, ?, ?, ?)',
                    (vendor_username, vendor_password, 'vendor', vendor_type)
                )
                
                if user_success:
                    # Create vendor record
                    vendor_success = execute_update(
                        '''INSERT INTO vendors 
                        (username, company_name, contact_person, email, phone, vendor_type, 
                         services_offered, address) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                        (vendor_username, company_name, contact_person, email, phone, 
                         vendor_type, services_offered, address)
                    )
                    
                    if vendor_success:
                        st.success("✅ Vendor registered successfully!")
                        st.success(f"**Login details sent to vendor:**")
                        st.success(f"Username: `{vendor_username}`")
                        st.success(f"Password: `{vendor_password}`")
                        st.rerun()
                    else:
                        st.error("❌ Failed to create vendor record")
                else:
                    st.error("❌ Failed to create user account")

# ========== NEW FEATURE PAGES (REDUCED DATA) ==========

def show_preventive_maintenance():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("📅 Preventive Maintenance")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display only 5 records
    records = execute_query('SELECT * FROM preventive_maintenance LIMIT 5')
    
    if records:
        df = pd.DataFrame(records)
        st.dataframe(df[['equipment_name', 'equipment_type', 'location', 'next_maintenance_date', 'status']], 
                    use_container_width=True)
    else:
        st.info("No preventive maintenance records found")

def show_space_management():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🏢 Space Management")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display only 2 bookings
    bookings = execute_query('SELECT * FROM space_bookings LIMIT 2')
    
    if bookings:
        for booking in bookings:
            with st.expander(f"{booking['room_name']} - {booking['booking_date']}"):
                st.write(f"**Purpose:** {booking['purpose']}")
                st.write(f"**Booked By:** {booking['booked_by']}")
                st.write(f"**Time:** {booking['start_time']} to {booking['end_time']}")
                st.write(f"**Status:** {booking['status']}")
    else:
        st.info("No room bookings found")

def show_generator_diesel_records():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("⛽ Generator Records")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display only 3 records
    records = execute_query('SELECT * FROM generator_records LIMIT 3')
    
    if records:
        df = pd.DataFrame(records)
        st.dataframe(df[['record_date', 'generator_name', 'opening_hours', 'closing_hours', 'recorded_by']], 
                    use_container_width=True)
    else:
        st.info("No generator records found")

def show_hse_management():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🚨 HSE Management")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display only 3 records
    records = execute_query('SELECT * FROM hse_schedule LIMIT 3')
    
    if records:
        df = pd.DataFrame(records)
        st.dataframe(df[['inspection_type', 'area', 'next_inspection_date', 'status', 'compliance_level']], 
                    use_container_width=True)
    else:
        st.info("No HSE records found")

# ========== DASHBOARD ==========

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
    elif role == 'vendor':
        show_vendor_dashboard()
    else:
        st.info(f"Welcome {role}!")

def show_user_dashboard():
    st.subheader("👤 Facility User Dashboard")
    
    # Quick actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📝 Create Request", use_container_width=True):
            st.session_state.navigation_menu = "Create Request"
            st.rerun()
    with col2:
        if st.button("📋 My Requests", use_container_width=True):
            st.session_state.navigation_menu = "My Requests"
            st.rerun()
    with col3:
        if st.button("🏢 Book Room", use_container_width=True):
            st.session_state.navigation_menu = "Space Management"
            st.rerun()
    
    # Stats
    requests = get_user_requests(st.session_state.user['username'])
    st.metric("Total Requests", len(requests))
    st.metric("Pending Requests", len([r for r in requests if r['status'] == 'Pending']))

def show_manager_dashboard():
    st.subheader("👨‍💼 Facility Manager Dashboard")
    
    # Quick actions
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🛠️ Manage Requests", use_container_width=True):
            st.session_state.navigation_menu = "Manage Requests"
            st.rerun()
    with col2:
        if st.button("🏢 Vendor Registration", use_container_width=True):
            st.session_state.navigation_menu = "Vendor Registration"
            st.rerun()
    with col3:
        if st.button("📅 Maintenance", use_container_width=True):
            st.session_state.navigation_menu = "Preventive Maintenance"
            st.rerun()
    with col4:
        if st.button("🚨 HSE", use_container_width=True):
            st.session_state.navigation_menu = "HSE Management"
            st.rerun()
    
    # Stats
    requests = get_all_requests()
    st.metric("Total Requests", len(requests))
    st.metric("Pending Assignment", len([r for r in requests if r['status'] == 'Pending']))
    st.metric("Awaiting Approval", len([r for r in requests if r['status'] == 'Completed' and not r['facilities_manager_approval']]))

def show_vendor_dashboard():
    st.subheader("🏢 Vendor Dashboard")
    
    # Quick actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔧 Assigned Jobs", use_container_width=True):
            st.session_state.navigation_menu = "Assigned Jobs"
            st.rerun()
    with col2:
        if st.button("⛽ Generator Records", use_container_width=True):
            st.session_state.navigation_menu = "Generator Records"
            st.rerun()
    
    # Stats
    jobs = get_vendor_requests(st.session_state.user['username'])
    st.metric("Assigned Jobs", len([j for j in jobs if j['status'] == 'Assigned']))
    st.metric("Completed Jobs", len([j for j in jobs if j['status'] == 'Completed']))

# ========== MAIN APP ==========

def show_main_app():
    user = st.session_state.user
    
    st.markdown(f"""
        <div class="header-container">
            <h1 style="margin: 0;">🏢 FACILITIES MANAGEMENT SYSTEM™</h1>
            <p style="margin: 5px 0 0 0;">
                Welcome, <strong>{user['username']}</strong> | Role: {user['role'].replace('_', ' ').title()}
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown(f"""
            <div style="text-align: center; padding: 10px; background: linear-gradient(45deg, #4CAF50, #2E7D32); 
                     border-radius: 10px; margin-bottom: 20px;">
                <h3 style="color: white; margin: 0;">👋 Welcome</h3>
                <p style="color: white; margin: 5px 0;">{user['username']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Navigation based on role
        if user['role'] == 'facility_user':
            menu_options = ["Dashboard", "Create Request", "My Requests", 
                          "Space Management", "Generator Records", "HSE Management"]
        elif user['role'] == 'facility_manager':
            menu_options = ["Dashboard", "Manage Requests", "Vendor Registration", 
                          "Preventive Maintenance", "Space Management", "Generator Records", "HSE Management"]
        elif user['role'] == 'vendor':
            menu_options = ["Dashboard", "Assigned Jobs", "Generator Records"]
        else:
            menu_options = ["Dashboard"]
        
        # Initialize navigation menu
        if 'navigation_menu' not in st.session_state:
            st.session_state.navigation_menu = "Dashboard"
        
        selected = st.radio("Navigation", menu_options, 
                          index=menu_options.index(st.session_state.navigation_menu) 
                          if st.session_state.navigation_menu in menu_options else 0)
        
        # Update session state
        if selected != st.session_state.navigation_menu:
            st.session_state.navigation_menu = selected
            st.rerun()
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            del st.session_state.user
            if 'navigation_menu' in st.session_state:
                del st.session_state.navigation_menu
            st.rerun()
    
    # Route to selected page
    menu = st.session_state.navigation_menu
    
    if menu == "Dashboard":
        show_dashboard()
    elif menu == "Create Request":
        show_create_request()
    elif menu == "My Requests":
        show_my_requests()
    elif menu == "Manage Requests":
        show_manage_requests()
    elif menu == "Vendor Registration":
        show_vendor_registration()
    elif menu == "Assigned Jobs":
        show_assigned_jobs()
    elif menu == "Preventive Maintenance":
        show_preventive_maintenance()
    elif menu == "Space Management":
        show_space_management()
    elif menu == "Generator Records":
        show_generator_diesel_records()
    elif menu == "HSE Management":
        show_hse_management()

# ========== MAIN FUNCTION ==========

def main():
    # Initialize database
    init_database()
    
    # Check if user is logged in
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    if st.session_state.user is None:
        show_login()
    else:
        show_main_app()

if __name__ == "__main__":
    main()
