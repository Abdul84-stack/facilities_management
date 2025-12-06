import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
import hashlib
import io
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import numpy as np

# ============================================================================
# CONFIGURATION & SETUP
# ============================================================================

st.set_page_config(
    page_title="A-B Facilities Management Pro™",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 1.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 8px 8px 0 0;
    }
    .priority-critical { background: #DC2626; color: white; padding: 4px 12px; border-radius: 12px; }
    .priority-high { background: #EA580C; color: white; padding: 4px 12px; border-radius: 12px; }
    .priority-medium { background: #F59E0B; color: white; padding: 4px 12px; border-radius: 12px; }
    .priority-low { background: #10B981; color: white; padding: 4px 12px; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATABASE FUNCTIONS - FIXED
# ============================================================================

def init_db():
    """Initialize SQLite database with all necessary tables"""
    conn = sqlite3.connect('ab_fms_pro.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    email TEXT,
                    role TEXT DEFAULT 'End User',
                    organization TEXT DEFAULT 'Demo Corp',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    
    # Work Requests
    c.execute('''CREATE TABLE IF NOT EXISTS work_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT UNIQUE,
                    title TEXT NOT NULL,
                    description TEXT,
                    requested_by TEXT,
                    organization TEXT,
                    location TEXT,
                    priority TEXT DEFAULT 'Medium',
                    status TEXT DEFAULT 'Submitted',
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    
    # Work Orders - FIXED: Added all necessary columns
    c.execute('''CREATE TABLE IF NOT EXISTS work_orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    work_order_id TEXT UNIQUE,
                    title TEXT NOT NULL,
                    description TEXT,
                    work_request_id INTEGER,
                    organization TEXT,
                    assigned_to TEXT,
                    assigned_vendor_id INTEGER,
                    priority TEXT DEFAULT 'Medium',
                    status TEXT DEFAULT 'Draft',
                    scheduled_start TIMESTAMP,
                    scheduled_end TIMESTAMP,
                    actual_start TIMESTAMP,
                    actual_end TIMESTAMP,
                    estimated_cost REAL DEFAULT 0,
                    actual_cost REAL DEFAULT 0,
                    completion_notes TEXT,
                    user_approval BOOLEAN DEFAULT 0,
                    user_approval_date TIMESTAMP,
                    manager_approval BOOLEAN DEFAULT 0,
                    manager_approval_date TIMESTAMP,
                    invoice_approved BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    
    # Vendors - FIXED: Added missing columns
    c.execute('''CREATE TABLE IF NOT EXISTS vendors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    vendor_id TEXT UNIQUE,
                    name TEXT NOT NULL,
                    organization TEXT,
                    contact_person TEXT,
                    email TEXT,
                    phone TEXT,
                    address TEXT,
                    vendor_type TEXT,
                    specialties TEXT,
                    is_approved BOOLEAN DEFAULT 0,
                    approval_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    
    # Preventive Maintenance
    c.execute('''CREATE TABLE IF NOT EXISTS preventive_maintenance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pm_id TEXT UNIQUE,
                    asset_id INTEGER,
                    organization TEXT,
                    frequency TEXT,
                    checklist TEXT,
                    assigned_to TEXT,
                    estimated_duration_hours REAL,
                    is_active BOOLEAN DEFAULT 1,
                    last_performed TIMESTAMP,
                    next_due_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    
    # Diesel & Generator Tracking - FIXED: Added all necessary columns
    c.execute('''CREATE TABLE IF NOT EXISTS diesel_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tracking_id TEXT UNIQUE,
                    organization TEXT,
                    date DATE,
                    generator_id TEXT,
                    opening_hours_reading REAL DEFAULT 0,
                    closing_hours_reading REAL DEFAULT 0,
                    total_hours_run REAL DEFAULT 0,
                    opening_diesel_liters REAL DEFAULT 0,
                    diesel_purchased_liters REAL DEFAULT 0,
                    diesel_consumed_liters REAL DEFAULT 0,
                    closing_diesel_liters REAL DEFAULT 0,
                    purchase_amount REAL DEFAULT 0,
                    recorded_by TEXT,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    
    # Generators - FIXED: Added all columns
    c.execute('''CREATE TABLE IF NOT EXISTS generators (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    generator_id TEXT UNIQUE,
                    name TEXT NOT NULL,
                    organization TEXT,
                    location TEXT,
                    capacity_kva REAL,
                    manufacturer TEXT,
                    model TEXT,
                    serial_number TEXT,
                    installation_date DATE,
                    last_service_date DATE,
                    next_service_date DATE,
                    total_hours_run REAL DEFAULT 0,
                    status TEXT DEFAULT 'Operational',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    
    # Vendor Invoices
    c.execute('''CREATE TABLE IF NOT EXISTS vendor_invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_id TEXT UNIQUE,
                    vendor_id INTEGER,
                    work_order_id INTEGER,
                    amount REAL,
                    invoice_date DATE,
                    due_date DATE,
                    status TEXT DEFAULT 'Pending',
                    payment_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    
    # Assets
    c.execute('''CREATE TABLE IF NOT EXISTS assets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_id TEXT UNIQUE,
                    name TEXT NOT NULL,
                    category TEXT,
                    organization TEXT,
                    location TEXT,
                    building TEXT,
                    floor TEXT,
                    room TEXT,
                    status TEXT DEFAULT 'Operational',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    
    # Insert demo data if empty
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        # Insert users
        demo_users = [
            ('admin', hashlib.sha256('admin123'.encode()).hexdigest(), 'admin@fms.com', 'Admin', 'Demo Corp'),
            ('manager', hashlib.sha256('manager123'.encode()).hexdigest(), 'manager@demo.com', 'Facility Manager', 'Demo Corp'),
            ('user', hashlib.sha256('user123'.encode()).hexdigest(), 'user@demo.com', 'End User', 'Demo Corp'),
            ('vendor', hashlib.sha256('vendor123'.encode()).hexdigest(), 'vendor@demo.com', 'Vendor', 'Demo Corp')
        ]
        
        for user in demo_users:
            c.execute("INSERT INTO users (username, password, email, role, organization) VALUES (?, ?, ?, ?, ?)", user)
        
        # Insert vendors
        demo_vendors = [
            ('VEND-001', 'QuickFix Electrical', 'Demo Corp', 'John Electric', 'vendor@demo.com', '555-0101', '123 Main St', 'Electrical', 'HVAC, Wiring, Lighting', 1, '2024-01-01'),
            ('VEND-002', 'Pro Plumbing Co', 'Demo Corp', 'Mike Plumber', 'mike@proplumbing.com', '555-0102', '456 Oak Ave', 'Plumbing', 'Pipes, Drains, Water Heaters', 1, '2024-01-01'),
        ]
        
        for vendor in demo_vendors:
            c.execute("INSERT INTO vendors (vendor_id, name, organization, contact_person, email, phone, address, vendor_type, specialties, is_approved, approval_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", vendor)
        
        # Insert generators
        demo_generators = [
            ('GEN-001', 'Main Backup Generator', 'Demo Corp', 'Basement', 500, 'Cummins', 'C500D5', 'SN12345', '2023-01-15', '2024-01-10', '2024-04-10', 1250.5),
            ('GEN-002', 'Emergency Generator', 'Demo Corp', 'Building B', 200, 'CAT', 'C200', 'SN67890', '2023-03-20', '2024-02-15', '2024-05-15', 850.2),
        ]
        
        for gen in demo_generators:
            c.execute("INSERT INTO generators (generator_id, name, organization, location, capacity_kva, manufacturer, model, serial_number, installation_date, last_service_date, next_service_date, total_hours_run) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", gen)
        
        # Insert assets
        demo_assets = [
            ('ASSET-001', 'HVAC System - Main', 'HVAC', 'Demo Corp', 'Building A', '3', '301'),
            ('ASSET-002', 'Water Heater - Kitchen', 'Plumbing', 'Demo Corp', 'Building A', '2', 'Kitchen'),
            ('ASSET-003', 'Generator - Backup', 'Electrical', 'Demo Corp', 'Basement', 'B1', 'Generator Room'),
        ]
        
        for asset in demo_assets:
            c.execute("INSERT INTO assets (asset_id, name, category, organization, building, floor, room) VALUES (?, ?, ?, ?, ?, ?, ?)", asset)
        
        # Insert preventive maintenance
        demo_pm = [
            ('PM-001', 3, 'Demo Corp', 'Monthly', 'Check oil level|Check fuel level|Test startup', 'VEND-001', 2, '2024-04-10'),
            ('PM-002', 1, 'Demo Corp', 'Quarterly', 'Clean filters|Check coolant|Inspect belts', 'VEND-001', 4, '2024-06-01'),
        ]
        
        for pm in demo_pm:
            c.execute("INSERT INTO preventive_maintenance (pm_id, asset_id, organization, frequency, checklist, assigned_to, estimated_duration_hours, next_due_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", pm)
        
        # Insert diesel tracking records
        for i in range(1, 8):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            c.execute("""
                INSERT INTO diesel_tracking 
                (tracking_id, organization, date, generator_id, opening_hours_reading, 
                 closing_hours_reading, total_hours_run, opening_diesel_liters, 
                 diesel_purchased_liters, diesel_consumed_liters, closing_diesel_liters,
                 purchase_amount, recorded_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"DTR-{i:03d}", 'Demo Corp', date, 'GEN-001',
                1200 + (i * 8), 1208 + (i * 8), 8,
                500 - (i * 50), 200 if i % 3 == 0 else 0, 100 + (i * 5),
                500 - (i * 50) + (200 if i % 3 == 0 else 0) - (100 + (i * 5)),
                (200 if i % 3 == 0 else 0) * 850, 'manager'
            ))
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect('ab_fms_pro.db', check_same_thread=False)

def query_to_dataframe(query, params=()):
    """Execute SQL query and return DataFrame"""
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def execute_query(query, params=()):
    """Execute SQL query"""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(query, params)
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash password"""
    return hashlib.sha256(password.encode()).hexdigest()

# ============================================================================
# AUTHENTICATION FUNCTIONS - FIXED
# ============================================================================

def init_session_state():
    """Initialize session state"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'organization' not in st.session_state:
        st.session_state.organization = None
    if 'vendor_id' not in st.session_state:
        st.session_state.vendor_id = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Dashboard'

def authenticate_user(username, password):
    """Authenticate user"""
    conn = get_db_connection()
    c = conn.cursor()
    
    hashed_password = hash_password(password)
    c.execute("SELECT id, username, role, organization FROM users WHERE username = ? AND password = ?", 
              (username, hashed_password))
    
    user = c.fetchone()
    
    if user:
        st.session_state.user_id = user[0]
        st.session_state.username = user[1]
        st.session_state.role = user[2]
        st.session_state.organization = user[3]
        st.session_state.authenticated = True
        
        # Get vendor ID if user is a vendor
        if user[2] == 'Vendor':
            c.execute("SELECT id FROM vendors WHERE email = ?", (username,))
            vendor = c.fetchone()
            if vendor:
                st.session_state.vendor_id = vendor[0]
        
        conn.close()
        return True
    
    conn.close()
    return False

def check_permission(required_roles):
    """Check if user has required role"""
    if isinstance(required_roles, str):
        required_roles = [required_roles]
    return st.session_state.role in required_roles

# ============================================================================
# VENDOR REGISTRATION - FIXED
# ============================================================================

def show_vendor_registration():
    """Display vendor registration form"""
    st.markdown('<h1 class="main-header">👷 Vendor Registration</h1>', unsafe_allow_html=True)
    
    with st.form("vendor_registration_form"):
        st.subheader("Complete Your Vendor Profile")
        
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company Name*", key="reg_company")
            contact_person = st.text_input("Contact Person*", value=st.session_state.username)
            email = st.text_input("Email*", value=st.session_state.username, key="reg_email")
            phone = st.text_input("Phone*", key="reg_phone")
        
        with col2:
            address = st.text_area("Address*", height=100, key="reg_address")
            vendor_type = st.selectbox("Service Type*", 
                ["Electrical", "Plumbing", "HVAC", "Cleaning", "General Maintenance", "Other"],
                key="reg_type")
            specialties = st.text_input("Specialties", placeholder="e.g., HVAC, Wiring, Plumbing", key="reg_specialties")
        
        st.markdown("**Required fields (*)**")
        
        submitted = st.form_submit_button("Submit Registration", type="primary")
        
        if submitted:
            if company_name and contact_person and email and phone and address:
                # Generate vendor ID
                org_code = st.session_state.organization[:3].upper()
                count = query_to_dataframe(
                    "SELECT COUNT(*) as count FROM vendors WHERE organization = ?",
                    (st.session_state.organization,)
                ).iloc[0]['count']
                
                vendor_id = f"VEND-{org_code}-{count+1:03d}"
                
                # Insert vendor
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("""
                    INSERT INTO vendors 
                    (vendor_id, name, organization, contact_person, email, phone, address, vendor_type, specialties)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    vendor_id, company_name, st.session_state.organization,
                    contact_person, email, phone, address, vendor_type, specialties
                ))
                
                # Get the new vendor ID
                c.execute("SELECT id FROM vendors WHERE vendor_id = ?", (vendor_id,))
                new_vendor_id = c.fetchone()[0]
                
                # Update user role if needed
                c.execute("UPDATE users SET role = 'Vendor' WHERE username = ?", (st.session_state.username,))
                
                conn.commit()
                conn.close()
                
                # Update session state
                st.session_state.vendor_id = new_vendor_id
                st.session_state.role = 'Vendor'
                
                st.success(f"✅ Vendor registration submitted! Vendor ID: **{vendor_id}**")
                st.info("Your registration is pending approval. You can now access vendor features.")
                st.balloons()
                
                # Redirect to vendor portal
                st.session_state.current_page = 'Vendor Portal'
                st.rerun()
            else:
                st.error("Please fill in all required fields (*)")

# ============================================================================
# DIESEL & GENERATOR TRACKING - FIXED
# ============================================================================

def show_diesel_tracking():
    """Display diesel and generator tracking module"""
    st.markdown('<h1 class="main-header">⛽ Diesel & Generator Tracking</h1>', unsafe_allow_html=True)
    
    organization = st.session_state.organization
    role = st.session_state.role
    
    tabs = st.tabs(["Daily Recording", "View Records", "Generator Management", "PM Alerts"])
    
    with tabs[0]:  # Daily Recording
        st.subheader("📝 Daily Diesel & Generator Recording")
        
        with st.form("diesel_tracking_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                date = st.date_input("Date*", value=datetime.now(), key="diesel_date")
                
                # Get available generators
                generators = query_to_dataframe(
                    "SELECT generator_id, name FROM generators WHERE organization = ?",
                    (organization,)
                )
                
                if not generators.empty:
                    generator_id = st.selectbox("Generator*", 
                        generators['generator_id'].tolist(),
                        format_func=lambda x: f"{x} - {generators[generators['generator_id'] == x]['name'].iloc[0]}",
                        key="diesel_generator")
                    
                    # Get last reading for this generator
                    last_reading = query_to_dataframe("""
                        SELECT closing_hours_reading, closing_diesel_liters 
                        FROM diesel_tracking 
                        WHERE generator_id = ? 
                        ORDER BY date DESC LIMIT 1
                    """, (generator_id,))
                    
                    opening_hours = st.number_input("Opening Hours Reading*", 
                        min_value=0.0, step=0.1, 
                        value=float(last_reading['closing_hours_reading'].iloc[0]) if not last_reading.empty else 0.0,
                        key="opening_hours")
                    
                    closing_hours = st.number_input("Closing Hours Reading*",
                        min_value=opening_hours, step=0.1, value=opening_hours + 8.0,
                        key="closing_hours")
                
                else:
                    st.warning("No generators found. Please add generators first.")
                    generator_id = None
            
            with col2:
                opening_diesel = st.number_input("Opening Diesel (liters)*",
                    min_value=0.0, step=0.1,
                    value=float(last_reading['closing_diesel_liters'].iloc[0]) if not last_reading.empty else 500.0,
                    key="opening_diesel")
                
                diesel_purchased = st.number_input("Diesel Purchased (liters)",
                    min_value=0.0, step=0.1, value=0.0, key="diesel_purchased")
                
                diesel_consumed = st.number_input("Diesel Consumed (liters)*",
                    min_value=0.0, step=0.1, value=100.0, key="diesel_consumed")
                
                purchase_amount = st.number_input("Purchase Amount (₦)",
                    min_value=0.0, step=100.0, value=0.0, key="purchase_amount")
            
            # Calculate values
            if generator_id:
                total_hours_run = closing_hours - opening_hours
                closing_diesel = opening_diesel + diesel_purchased - diesel_consumed
                
                st.info(f"**Calculated Values:**")
                st.info(f"Total Hours Run: **{total_hours_run:.1f} hours**")
                st.info(f"Closing Diesel: **{closing_diesel:.1f} liters**")
            
            notes = st.text_area("Notes (Optional)", height=100, key="diesel_notes")
            
            submitted = st.form_submit_button("Save Daily Record", type="primary")
            
            if submitted and generator_id:
                # Generate tracking ID
                count = query_to_dataframe(
                    "SELECT COUNT(*) as count FROM diesel_tracking WHERE organization = ?",
                    (organization,)
                ).iloc[0]['count']
                tracking_id = f"DTR-{organization[:3]}-{count+1:03d}"
                
                # Insert record
                conn = get_db_connection()
                c = conn.cursor()
                
                c.execute("""
                    INSERT INTO diesel_tracking 
                    (tracking_id, organization, date, generator_id, opening_hours_reading,
                     closing_hours_reading, total_hours_run, opening_diesel_liters,
                     diesel_purchased_liters, diesel_consumed_liters, closing_diesel_liters,
                     purchase_amount, recorded_by, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tracking_id, organization, date.strftime('%Y-%m-%d'), generator_id,
                    opening_hours, closing_hours, total_hours_run, opening_diesel,
                    diesel_purchased, diesel_consumed, closing_diesel,
                    purchase_amount, st.session_state.username, notes
                ))
                
                # Update generator total hours
                c.execute("""
                    UPDATE generators 
                    SET total_hours_run = total_hours_run + ?
                    WHERE generator_id = ?
                """, (total_hours_run, generator_id))
                
                conn.commit()
                conn.close()
                
                st.success(f"✅ Daily record saved! Tracking ID: **{tracking_id}**")
                st.balloons()
    
    with tabs[1]:  # View Records
        st.subheader("📋 Diesel Tracking Records")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            start_date = st.date_input("Start Date", 
                value=datetime.now() - timedelta(days=30),
                key="diesel_start")
        with col2:
            end_date = st.date_input("End Date", 
                value=datetime.now(),
                key="diesel_end")
        with col3:
            generators = query_to_dataframe(
                "SELECT generator_id, name FROM generators WHERE organization = ?",
                (organization,)
            )
            generator_filter = st.selectbox("Generator",
                ["All"] + generators['generator_id'].tolist(),
                key="diesel_filter")
        
        # Query records
        query = """
            SELECT dt.*, g.name as generator_name
            FROM diesel_tracking dt
            JOIN generators g ON dt.generator_id = g.generator_id
            WHERE dt.organization = ? 
            AND dt.date BETWEEN ? AND ?
        """
        params = [organization, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')]
        
        if generator_filter != "All":
            query += " AND dt.generator_id = ?"
            params.append(generator_filter)
        
        query += " ORDER BY dt.date DESC"
        
        records = query_to_dataframe(query, tuple(params))
        
        if not records.empty:
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_hours = records['total_hours_run'].sum()
                st.metric("Total Hours", f"{total_hours:.1f}")
            with col2:
                total_consumed = records['diesel_consumed_liters'].sum()
                st.metric("Diesel Consumed", f"{total_consumed:.1f} L")
            with col3:
                total_purchased = records['diesel_purchased_liters'].sum()
                st.metric("Diesel Purchased", f"{total_purchased:.1f} L")
            with col4:
                total_amount = records['purchase_amount'].sum()
                st.metric("Total Amount", f"₦{total_amount:,.0f}")
            
            # Display records
            st.subheader("Detailed Records")
            for _, record in records.iterrows():
                with st.expander(f"{record['date']} - {record['generator_name']} ({record['tracking_id']})"):
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.write("**Hours Tracking:**")
                        st.write(f"Opening: {record['opening_hours_reading']:.1f} hours")
                        st.write(f"Closing: {record['closing_hours_reading']:.1f} hours")
                        st.write(f"Total Run: {record['total_hours_run']:.1f} hours")
                    
                    with col_b:
                        st.write("**Diesel Tracking:**")
                        st.write(f"Opening: {record['opening_diesel_liters']:.1f} liters")
                        st.write(f"Purchased: {record['diesel_purchased_liters']:.1f} liters")
                        st.write(f"Consumed: {record['diesel_consumed_liters']:.1f} liters")
                        st.write(f"Closing: {record['closing_diesel_liters']:.1f} liters")
                    
                    if record['purchase_amount'] > 0:
                        st.write(f"**Purchase Amount:** ₦{record['purchase_amount']:,.0f}")
                    
                    if record['notes']:
                        st.write(f"**Notes:** {record['notes']}")
                    
                    st.write(f"**Recorded by:** {record['recorded_by']}")
        else:
            st.info("No records found for the selected period")
    
    with tabs[2]:  # Generator Management
        st.subheader("🔧 Generator Management")
        
        # List generators
        generators = query_to_dataframe(
            "SELECT * FROM generators WHERE organization = ?",
            (organization,)
        )
        
        if not generators.empty:
            for _, gen in generators.iterrows():
                with st.expander(f"{gen['generator_id']} - {gen['name']}"):
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.write(f"**Location:** {gen['location']}")
                        st.write(f"**Capacity:** {gen['capacity_kva']} kVA")
                        st.write(f"**Manufacturer:** {gen['manufacturer']} {gen['model']}")
                        st.write(f"**Serial:** {gen['serial_number']}")
                        st.write(f"**Total Hours:** {gen['total_hours_run']:.1f} hours")
                    
                    with col_b:
                        st.write(f"**Installation:** {gen['installation_date']}")
                        if gen['last_service_date']:
                            st.write(f"**Last Service:** {gen['last_service_date']}")
                        if gen['next_service_date']:
                            days_left = (datetime.strptime(gen['next_service_date'], '%Y-%m-%d').date() - datetime.now().date()).days
                            st.write(f"**Next Service:** {gen['next_service_date']} ({days_left} days)")
                        
                        if gen['status'] == 'Operational':
                            st.success("✅ Operational")
                        else:
                            st.warning(f"⚠️ {gen['status']}")
        
        # Add/Edit Generator
        with st.expander("➕ Add New Generator"):
            with st.form("add_generator_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    gen_name = st.text_input("Generator Name*", key="new_gen_name")
                    gen_id = st.text_input("Generator ID*", key="new_gen_id")
                    location = st.text_input("Location*", key="new_gen_location")
                    capacity = st.number_input("Capacity (kVA)*", 
                        min_value=1.0, value=100.0, key="new_gen_capacity")
                
                with col2:
                    manufacturer = st.text_input("Manufacturer", key="new_gen_manufacturer")
                    model = st.text_input("Model", key="new_gen_model")
                    serial_number = st.text_input("Serial Number", key="new_gen_serial")
                    installation_date = st.date_input("Installation Date", 
                        value=datetime.now(), key="new_gen_install")
                
                submitted = st.form_submit_button("Add Generator", type="primary")
                
                if submitted:
                    if gen_name and gen_id and location and capacity:
                        conn = get_db_connection()
                        c = conn.cursor()
                        c.execute("""
                            INSERT INTO generators 
                            (generator_id, name, organization, location, capacity_kva,
                             manufacturer, model, serial_number, installation_date)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            gen_id, gen_name, organization, location, capacity,
                            manufacturer, model, serial_number, installation_date.strftime('%Y-%m-%d')
                        ))
                        conn.commit()
                        conn.close()
                        
                        st.success(f"Generator {gen_id} added successfully!")
                        st.rerun()
    
    with tabs[3]:  # PM Alerts
        st.subheader("🚨 Preventive Maintenance Alerts")
        
        # Check for PM due based on hours
        generators = query_to_dataframe(
            "SELECT generator_id, name, total_hours_run FROM generators WHERE organization = ?",
            (organization,)
        )
        
        if not generators.empty:
            for _, gen in generators.iterrows():
                # Get last PM hours reading
                last_pm_hours = query_to_dataframe("""
                    SELECT closing_hours_reading 
                    FROM diesel_tracking 
                    WHERE generator_id = ? 
                    ORDER BY date DESC LIMIT 1
                """, (gen['generator_id'],))
                
                if not last_pm_hours.empty:
                    hours_since_pm = gen['total_hours_run'] - last_pm_hours.iloc[0]['closing_hours_reading']
                    
                    if hours_since_pm >= 200:
                        with st.container():
                            st.error(f"**{gen['generator_id']} - {gen['name']}**")
                            st.error(f"⚠️ **CRITICAL:** {hours_since_pm:.1f} hours since last PM (Threshold: 200 hours)")
                            
                            col_a, col_b = st.columns([3, 1])
                            with col_a:
                                if st.button(f"Schedule PM for {gen['generator_id']}", key=f"schedule_{gen['generator_id']}"):
                                    # Create PM work request
                                    conn = get_db_connection()
                                    c = conn.cursor()
                                    
                                    # Get next request ID
                                    count = query_to_dataframe(
                                        "SELECT COUNT(*) as count FROM work_requests WHERE organization = ?",
                                        (organization,)
                                    ).iloc[0]['count']
                                    request_id = f"WR-{organization[:3]}-{count+1:04d}"
                                    
                                    c.execute("""
                                        INSERT INTO work_requests 
                                        (request_id, title, description, requested_by, organization,
                                         location, priority, status, category)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                    """, (
                                        request_id,
                                        f"Preventive Maintenance - {gen['name']}",
                                        f"Generator has run {hours_since_pm:.1f} hours since last PM. Scheduled maintenance required.",
                                        st.session_state.username,
                                        organization,
                                        "Generator Room",
                                        "High",
                                        "Submitted",
                                        "Electrical"
                                    ))
                                    conn.commit()
                                    conn.close()
                                    
                                    st.success(f"PM work request created: {request_id}")
                                    st.rerun()
                            
                            st.markdown("---")
                    elif hours_since_pm >= 160:
                        st.warning(f"**{gen['generator_id']} - {gen['name']}**: {hours_since_pm:.1f} hours since last PM (80% of threshold)")
                    else:
                        st.success(f"**{gen['generator_id']} - {gen['name']}**: {hours_since_pm:.1f} hours since last PM")
                else:
                    st.info(f"**{gen['generator_id']} - {gen['name']}**: No PM records found")
        else:
            st.info("No generators found")

# ============================================================================
# PREVENTIVE MAINTENANCE - FIXED
# ============================================================================

def show_preventive_maintenance():
    """Display preventive maintenance module"""
    st.markdown('<h1 class="main-header">🔧 Preventive Maintenance</h1>', unsafe_allow_html=True)
    
    organization = st.session_state.organization
    
    tabs = st.tabs(["PM Schedule", "Create PM", "Maintenance History", "Due Soon"])
    
    with tabs[0]:  # PM Schedule
        st.subheader("📅 Preventive Maintenance Schedule")
        
        # Get PM schedule with asset names
        pm_schedule = query_to_dataframe("""
            SELECT pm.pm_id, a.name as asset_name, pm.frequency, pm.next_due_date,
                   pm.assigned_to, pm.is_active, pm.estimated_duration_hours
            FROM preventive_maintenance pm
            LEFT JOIN assets a ON pm.asset_id = a.id
            WHERE pm.organization = ?
            ORDER BY pm.next_due_date
        """, (organization,))
        
        if not pm_schedule.empty:
            for _, pm in pm_schedule.iterrows():
                with st.container():
                    col_a, col_b, col_c = st.columns([3, 2, 1])
                    
                    with col_a:
                        st.write(f"**{pm['pm_id']}**")
                        st.write(f"**Asset:** {pm['asset_name']}")
                        st.caption(f"Frequency: {pm['frequency']}")
                    
                    with col_b:
                        if pm['next_due_date']:
                            due_date = datetime.strptime(pm['next_due_date'], '%Y-%m-%d').date()
                            days_diff = (due_date - datetime.now().date()).days
                            
                            st.write(f"**Due Date:** {pm['next_due_date']}")
                            st.write(f"**Days Until Due:** {days_diff}")
                    
                    with col_c:
                        if pm['is_active']:
                            if days_diff < 0:
                                st.error("⚠️ Overdue")
                            elif days_diff <= 7:
                                st.warning("🔔 Due Soon")
                            else:
                                st.success("✅ Scheduled")
                        else:
                            st.info("⏸️ Inactive")
                    
                    st.markdown("---")
        else:
            st.info("No preventive maintenance scheduled")
    
    with tabs[1]:  # Create PM
        st.subheader("➕ Create Preventive Maintenance Schedule")
        
        with st.form("create_pm_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Get assets
                assets = query_to_dataframe(
                    "SELECT id, asset_id, name FROM assets WHERE organization = ?",
                    (organization,)
                )
                
                if not assets.empty:
                    asset_options = {f"{row['asset_id']} - {row['name']}": row['id'] for _, row in assets.iterrows()}
                    asset_display = list(asset_options.keys())
                    
                    selected_asset = st.selectbox("Select Asset*", asset_display, key="pm_asset")
                    asset_id = asset_options[selected_asset]
                else:
                    st.warning("No assets found. Please add assets first.")
                    asset_id = None
                
                frequency = st.selectbox("Frequency*",
                    ["Daily", "Weekly", "Monthly", "Quarterly", "Semi-Annual", "Annual"],
                    key="pm_frequency")
            
            with col2:
                # Get vendors
                vendors = query_to_dataframe(
                    "SELECT vendor_id, name FROM vendors WHERE organization = ? AND is_approved = 1",
                    (organization,)
                )
                
                if not vendors.empty:
                    vendor_options = {f"{row['vendor_id']} - {row['name']}": row['vendor_id'] for _, row in vendors.iterrows()}
                    vendor_display = ["Select Vendor"] + list(vendor_options.keys())
                    
                    selected_vendor = st.selectbox("Assign to Vendor", vendor_display, key="pm_vendor")
                    assigned_to = vendor_options[selected_vendor] if selected_vendor != "Select Vendor" else None
                else:
                    st.info("No approved vendors available")
                    assigned_to = None
                
                next_due = st.date_input("Next Due Date*", 
                    value=datetime.now() + timedelta(days=30),
                    key="pm_next_due")
                
                estimated_hours = st.number_input("Estimated Hours",
                    min_value=0.5, step=0.5, value=2.0, key="pm_hours")
            
            checklist = st.text_area("Checklist Items*",
                value="Inspect condition|Clean components|Test operation|Record readings",
                height=100, key="pm_checklist")
            
            submitted = st.form_submit_button("Create PM Schedule", type="primary")
            
            if submitted and asset_id:
                # Generate PM ID
                count = query_to_dataframe(
                    "SELECT COUNT(*) as count FROM preventive_maintenance WHERE organization = ?",
                    (organization,)
                ).iloc[0]['count']
                pm_id = f"PM-{organization[:3]}-{count+1:03d}"
                
                # Insert PM
                conn = get_db_connection()
                c = conn.cursor()
                c.execute("""
                    INSERT INTO preventive_maintenance 
                    (pm_id, asset_id, organization, frequency, checklist, 
                     assigned_to, estimated_duration_hours, next_due_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pm_id, asset_id, organization, frequency, checklist,
                    assigned_to, estimated_hours, next_due.strftime('%Y-%m-%d')
                ))
                conn.commit()
                conn.close()
                
                st.success(f"Preventive Maintenance {pm_id} scheduled!")
                st.rerun()
    
    with tabs[2]:  # Maintenance History
        st.subheader("📋 Maintenance History")
        
        # Get maintenance work orders
        history = query_to_dataframe("""
            SELECT wo.work_order_id, wo.title, wo.status, wo.actual_end,
                   wo.assigned_to, wo.actual_cost, wo.completion_notes
            FROM work_orders wo
            WHERE wo.organization = ?
            AND wo.title LIKE '%PM%'
            ORDER BY wo.actual_end DESC
            LIMIT 20
        """, (organization,))
        
        if not history.empty:
            for _, record in history.iterrows():
                with st.container():
                    col_a, col_b, col_c = st.columns([3, 2, 1])
                    
                    with col_a:
                        st.write(f"**{record['work_order_id']}**")
                        st.write(f"**{record['title']}**")
                        if record['completion_notes']:
                            st.caption(f"{record['completion_notes'][:100]}...")
                    
                    with col_b:
                        if record['actual_end']:
                            st.write(f"**Completed:** {record['actual_end'][:10]}")
                        if record['actual_cost'] > 0:
                            st.write(f"**Cost:** ₦{record['actual_cost']:,.0f}")
                    
                    with col_c:
                        if record['status'] == 'Completed':
                            st.success("✅ Completed")
                        else:
                            st.info(f"📊 {record['status']}")
                    
                    st.markdown("---")
        else:
            st.info("No maintenance history found")
    
    with tabs[3]:  # Due Soon
        st.subheader("⚠️ Maintenance Due Soon")
        
        # Get PM due in next 30 days
        due_soon = query_to_dataframe("""
            SELECT pm.pm_id, a.name as asset_name, pm.frequency, pm.next_due_date,
                   pm.assigned_to
            FROM preventive_maintenance pm
            LEFT JOIN assets a ON pm.asset_id = a.id
            WHERE pm.organization = ?
            AND pm.is_active = 1
            AND pm.next_due_date BETWEEN DATE('now') AND DATE('now', '+30 days')
            ORDER BY pm.next_due_date
        """, (organization,))
        
        if not due_soon.empty:
            for _, pm in due_soon.iterrows():
                with st.container():
                    col_a, col_b, col_c = st.columns([3, 2, 1])
                    
                    with col_a:
                        st.write(f"**{pm['pm_id']}**")
                        st.write(f"**Asset:** {pm['asset_name']}")
                        st.caption(f"Frequency: {pm['frequency']}")
                    
                    with col_b:
                        due_date = datetime.strptime(pm['next_due_date'], '%Y-%m-%d').date()
                        days_diff = (due_date - datetime.now().date()).days
                        st.write(f"**Due Date:** {pm['next_due_date']}")
                        st.write(f"**Due In:** {days_diff} days")
                    
                    with col_c:
                        if days_diff <= 7:
                            st.error("🔴 Urgent")
                        else:
                            st.warning("🟡 Due Soon")
                    
                    st.markdown("---")
        else:
            st.success("✅ No maintenance due in the next 30 days")

# ============================================================================
# VENDOR PORTAL - FIXED
# ============================================================================

def show_vendor_portal():
    """Display vendor portal"""
    st.markdown('<h1 class="main-header">👷 Vendor Portal</h1>', unsafe_allow_html=True)
    
    # Check if vendor is registered
    vendor_info = query_to_dataframe(
        "SELECT * FROM vendors WHERE email = ? AND organization = ?",
        (st.session_state.username, st.session_state.organization)
    )
    
    if vendor_info.empty:
        st.warning("Vendor profile not found. Please complete your vendor registration.")
        show_vendor_registration()
        return
    
    vendor = vendor_info.iloc[0]
    vendor_id = vendor['id']
    
    # Vendor dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        active_jobs = query_to_dataframe(
            "SELECT COUNT(*) as count FROM work_orders WHERE assigned_vendor_id = ? AND status IN ('Assigned', 'In Progress')",
            (vendor_id,)
        ).iloc[0]['count']
        st.metric("Active Jobs", active_jobs)
    
    with col2:
        completed_jobs = query_to_dataframe(
            "SELECT COUNT(*) as count FROM work_orders WHERE assigned_vendor_id = ? AND status = 'Completed'",
            (vendor_id,)
        ).iloc[0]['count']
        st.metric("Completed", completed_jobs)
    
    with col3:
        pending_invoices = query_to_dataframe(
            "SELECT COUNT(*) as count FROM vendor_invoices WHERE vendor_id = ? AND status = 'Pending'",
            (vendor_id,)
        ).iloc[0]['count']
        st.metric("Pending Invoices", pending_invoices)
    
    with col4:
        if vendor['is_approved']:
            st.success("✅ Approved")
        else:
            st.warning("⏳ Pending")
    
    tabs = st.tabs(["My Jobs", "Submit Invoice", "My Profile"])
    
    with tabs[0]:  # My Jobs
        st.subheader("📋 My Assigned Jobs")
        
        assigned_jobs = query_to_dataframe("""
            SELECT wo.work_order_id, wo.title, wo.status, wo.priority,
                   wo.scheduled_start, wo.scheduled_end, wo.estimated_cost,
                   wr.requested_by, wr.location
            FROM work_orders wo
            LEFT JOIN work_requests wr ON wo.work_request_id = wr.id
            WHERE wo.assigned_vendor_id = ?
            ORDER BY 
                CASE wo.status
                    WHEN 'In Progress' THEN 1
                    WHEN 'Assigned' THEN 2
                    WHEN 'Completed' THEN 3
                    ELSE 4
                END,
                wo.created_at DESC
        """, (vendor_id,))
        
        if not assigned_jobs.empty:
            for _, job in assigned_jobs.iterrows():
                with st.container():
                    col_a, col_b, col_c = st.columns([3, 2, 1])
                    
                    with col_a:
                        st.write(f"**{job['work_order_id']}**")
                        st.write(f"**{job['title']}**")
                        st.caption(f"📍 {job['location']}")
                        if job['scheduled_start']:
                            st.caption(f"📅 {job['scheduled_start'][:10]} to {job['scheduled_end'][:10]}")
                    
                    with col_b:
                        # Priority badge
                        priority_class = f"priority-{job['priority'].lower()}"
                        st.markdown(f'<span class="{priority_class}">{job["priority"]}</span>', unsafe_allow_html=True)
                        
                        if job['estimated_cost'] > 0:
                            st.caption(f"💰 ₦{job['estimated_cost']:,.0f}")
                    
                    with col_c:
                        if job['status'] == 'Assigned':
                            st.warning("🟡 Assigned")
                            if st.button("Start", key=f"start_{job['work_order_id']}"):
                                conn = get_db_connection()
                                c = conn.cursor()
                                c.execute("""
                                    UPDATE work_orders 
                                    SET status = 'In Progress', actual_start = ?
                                    WHERE work_order_id = ?
                                """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), job['work_order_id']))
                                conn.commit()
                                conn.close()
                                st.success("Job started!")
                                st.rerun()
                        
                        elif job['status'] == 'In Progress':
                            st.info("🔵 In Progress")
                            if st.button("Complete", key=f"complete_{job['work_order_id']}"):
                                st.session_state.completing_job = job['work_order_id']
                        
                        elif job['status'] == 'Completed':
                            st.success("✅ Completed")
                    
                    st.markdown("---")
            
            # Job completion form
            if st.session_state.get('completing_job'):
                wo_id = st.session_state.completing_job
                
                with st.form("job_completion_form"):
                    st.subheader(f"Complete Job: {wo_id}")
                    
                    completion_notes = st.text_area("Completion Notes*", height=150)
                    actual_cost = st.number_input("Actual Cost (₦)", min_value=0.0, value=0.0)
                    
                    submitted = st.form_submit_button("Submit Completion", type="primary")
                    
                    if submitted and completion_notes:
                        conn = get_db_connection()
                        c = conn.cursor()
                        c.execute("""
                            UPDATE work_orders 
                            SET status = 'Completed', 
                                actual_end = ?,
                                completion_notes = ?,
                                actual_cost = ?
                            WHERE work_order_id = ?
                        """, (
                            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            completion_notes,
                            actual_cost,
                            wo_id
                        ))
                        conn.commit()
                        conn.close()
                        
                        st.success("Job completion submitted!")
                        st.session_state.pop('completing_job', None)
                        st.rerun()
        else:
            st.info("No jobs assigned to you yet")
    
    with tabs[1]:  # Submit Invoice
        st.subheader("💰 Submit Invoice")
        
        # Get completed jobs without invoices
        completed_jobs = query_to_dataframe("""
            SELECT wo.work_order_id, wo.title, wo.actual_cost
            FROM work_orders wo
            WHERE wo.assigned_vendor_id = ?
            AND wo.status = 'Completed'
            AND wo.work_order_id NOT IN (SELECT work_order_id FROM vendor_invoices)
        """, (vendor_id,))
        
        if not completed_jobs.empty:
            with st.form("invoice_form"):
                selected_job = st.selectbox("Select Job", 
                    completed_jobs['work_order_id'].tolist(),
                    format_func=lambda x: f"{x} - {completed_jobs[completed_jobs['work_order_id'] == x]['title'].iloc[0]}",
                    key="invoice_job")
                
                job_info = completed_jobs[completed_jobs['work_order_id'] == selected_job].iloc[0]
                
                invoice_amount = st.number_input("Invoice Amount (₦)*",
                    min_value=0.0, value=float(job_info['actual_cost'] or 0),
                    key="invoice_amount")
                
                invoice_date = st.date_input("Invoice Date", value=datetime.now())
                due_date = st.date_input("Due Date", value=datetime.now() + timedelta(days=30))
                
                submitted = st.form_submit_button("Submit Invoice", type="primary")
                
                if submitted and invoice_amount > 0:
                    # Generate invoice ID
                    count = query_to_dataframe(
                        "SELECT COUNT(*) as count FROM vendor_invoices WHERE vendor_id = ?",
                        (vendor_id,)
                    ).iloc[0]['count']
                    invoice_id = f"INV-{vendor['vendor_id']}-{count+1:03d}"
                    
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute("""
                        INSERT INTO vendor_invoices 
                        (invoice_id, vendor_id, work_order_id, amount, invoice_date, due_date)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        invoice_id, vendor_id, selected_job, invoice_amount,
                        invoice_date.strftime('%Y-%m-%d'), due_date.strftime('%Y-%m-%d')
                    ))
                    conn.commit()
                    conn.close()
                    
                    st.success(f"Invoice {invoice_id} submitted successfully!")
                    st.rerun()
        else:
            st.info("No completed jobs available for invoicing")
        
        # Show existing invoices
        st.subheader("📄 My Invoices")
        invoices = query_to_dataframe("""
            SELECT vi.invoice_id, vi.amount, vi.invoice_date, vi.due_date, 
                   vi.status, vi.payment_date, wo.title as job_title
            FROM vendor_invoices vi
            LEFT JOIN work_orders wo ON vi.work_order_id = wo.work_order_id
            WHERE vi.vendor_id = ?
            ORDER BY vi.invoice_date DESC
        """, (vendor_id,))
        
        if not invoices.empty:
            st.dataframe(invoices, use_container_width=True)
        else:
            st.info("No invoices found")
    
    with tabs[2]:  # My Profile
        st.subheader("👤 My Profile")
        
        col_a, col_b = st.columns([2, 1])
        
        with col_a:
            st.write(f"**Vendor ID:** {vendor['vendor_id']}")
            st.write(f"**Company:** {vendor['name']}")
            st.write(f"**Contact:** {vendor['contact_person']}")
            st.write(f"**Email:** {vendor['email']}")
            st.write(f"**Phone:** {vendor['phone']}")
            st.write(f"**Address:** {vendor['address']}")
            st.write(f"**Service Type:** {vendor['vendor_type']}")
            st.write(f"**Specialties:** {vendor['specialties']}")
        
        with col_b:
            if vendor['is_approved']:
                st.success("✅ Approved Vendor")
                if vendor['approval_date']:
                    st.caption(f"Approved: {vendor['approval_date']}")
            else:
                st.warning("⏳ Pending Approval")
                st.caption("Your registration is under review")

# ============================================================================
# DASHBOARD
# ============================================================================

def show_dashboard():
    """Display main dashboard"""
    st.markdown('<h1 class="main-header">📊 Facilities Management Dashboard</h1>', unsafe_allow_html=True)
    
    organization = st.session_state.organization
    role = st.session_state.role
    
    # Welcome message
    role_icon = {
        "Admin": "👑",
        "Facility Manager": "👨‍💼",
        "Vendor": "👷",
        "End User": "👤"
    }.get(role, "👤")
    
    st.markdown(f"### {role_icon} Welcome back, {st.session_state.username}!")
    st.caption(f"Role: {role} | Organization: {organization}")
    
    # Quick Stats
    st.markdown("### 📈 Quick Stats")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_requests = query_to_dataframe(
            "SELECT COUNT(*) as count FROM work_requests WHERE organization = ?",
            (organization,)
        ).iloc[0]['count']
        st.metric("Work Requests", total_requests)
    
    with col2:
        active_orders = query_to_dataframe(
            "SELECT COUNT(*) as count FROM work_orders WHERE organization = ? AND status IN ('In Progress', 'Assigned')",
            (organization,)
        ).iloc[0]['count']
        st.metric("Active Orders", active_orders)
    
    with col3:
        due_pm = query_to_dataframe("""
            SELECT COUNT(*) as count FROM preventive_maintenance 
            WHERE organization = ? AND next_due_date <= date('now', '+7 days')
        """, (organization,)).iloc[0]['count']
        st.metric("Due PM", due_pm)
    
    with col4:
        pm_alerts = query_to_dataframe("""
            SELECT COUNT(DISTINCT g.generator_id) as count
            FROM generators g
            LEFT JOIN (
                SELECT generator_id, MAX(closing_hours_reading) as last_hours
                FROM diesel_tracking 
                GROUP BY generator_id
            ) dt ON g.generator_id = dt.generator_id
            WHERE g.organization = ?
            AND (g.total_hours_run - COALESCE(dt.last_hours, 0)) >= 200
        """, (organization,)).iloc[0]['count']
        st.metric("Gen PM Alerts", pm_alerts)
    
    # Recent Activities
    st.markdown("### 📋 Recent Activities")
    
    if role == 'Vendor':
        vendor_info = query_to_dataframe(
            "SELECT id FROM vendors WHERE email = ? AND organization = ?",
            (st.session_state.username, organization)
        )
        
        if not vendor_info.empty:
            vendor_id = vendor_info.iloc[0]['id']
            activities = query_to_dataframe("""
                SELECT wo.work_order_id, wo.title, wo.status, wo.created_at
                FROM work_orders wo
                WHERE wo.assigned_vendor_id = ?
                ORDER BY wo.created_at DESC
                LIMIT 5
            """, (vendor_id,))
    else:
        activities = query_to_dataframe("""
            SELECT request_id, title, status, created_at
            FROM work_requests 
            WHERE organization = ?
            ORDER BY created_at DESC
            LIMIT 5
        """, (organization,))
    
    if not activities.empty:
        for _, activity in activities.iterrows():
            with st.container():
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.write(f"**{activity['title']}**")
                    if 'request_id' in activity:
                        st.caption(f"ID: {activity['request_id']}")
                    elif 'work_order_id' in activity:
                        st.caption(f"WO: {activity['work_order_id']}")
                with col_b:
                    if activity['status'] == 'Completed':
                        st.success("✅ Completed")
                    elif activity['status'] == 'In Progress':
                        st.info("🔵 In Progress")
                    else:
                        st.warning("🟡 {activity['status']}")
                st.markdown("---")
    else:
        st.info("No recent activities")
    
    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    
    if role == 'End User':
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Create Request", use_container_width=True):
                st.session_state.current_page = "Work Management"
                st.rerun()
        with col2:
            if st.button("⚕️ Report Incident", use_container_width=True):
                st.session_state.current_page = "HSE Management"
                st.rerun()
    
    elif role == 'Facility Manager':
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👨‍💼 Manage Vendors", use_container_width=True):
                st.session_state.current_page = "Vendor Management"
                st.rerun()
        with col2:
            if st.button("⛽ Diesel Tracking", use_container_width=True):
                st.session_state.current_page = "Diesel Tracking"
                st.rerun()
    
    elif role == 'Vendor':
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📋 My Jobs", use_container_width=True):
                st.session_state.current_page = "Vendor Portal"
                st.rerun()
        with col2:
            if st.button("💰 Submit Invoice", use_container_width=True):
                st.session_state.current_page = "Vendor Portal"
                st.rerun()
    
    # Alerts
    st.markdown("### 🚨 Alerts")
    
    # Overdue PM
    overdue_pm = query_to_dataframe("""
        SELECT pm_id, next_due_date 
        FROM preventive_maintenance 
        WHERE organization = ? 
        AND next_due_date < date('now')
        AND is_active = 1
        LIMIT 3
    """, (organization,))
    
    if not overdue_pm.empty:
        for _, pm in overdue_pm.iterrows():
            st.error(f"**PM {pm['pm_id']}** - Overdue since {pm['next_due_date']}")
    
    # Generator PM alerts
    pm_alerts_list = query_to_dataframe("""
        SELECT g.generator_id, g.name, 
               (g.total_hours_run - COALESCE(dt.last_hours, 0)) as hours_since_pm
        FROM generators g
        LEFT JOIN (
            SELECT generator_id, MAX(closing_hours_reading) as last_hours
            FROM diesel_tracking 
            GROUP BY generator_id
        ) dt ON g.generator_id = dt.generator_id
        WHERE g.organization = ?
        AND (g.total_hours_run - COALESCE(dt.last_hours, 0)) >= 200
        LIMIT 3
    """, (organization,))
    
    if not pm_alerts_list.empty:
        for _, alert in pm_alerts_list.iterrows():
            st.error(f"**{alert['generator_id']}** - {alert['hours_since_pm']:.1f} hours since last PM")

# ============================================================================
# WORK MANAGEMENT
# ============================================================================

def show_work_management():
    """Display work management"""
    st.markdown('<h1 class="main-header">📋 Work Management</h1>', unsafe_allow_html=True)
    
    role = st.session_state.role
    
    if role == 'End User':
        tabs = ["Create Request", "My Requests"]
    elif role == 'Vendor':
        st.info("Vendor work management is available in the Vendor Portal")
        st.session_state.current_page = "Vendor Portal"
        st.rerun()
    else:
        tabs = ["All Requests", "Assign Work", "Approve Jobs"]
    
    tab_objects = st.tabs(tabs)
    
    if role == 'End User':
        with tab_objects[0]:  # Create Request
            st.subheader("📝 Create Work Request")
            
            with st.form("create_request_form"):
                title = st.text_input("Title*", key="request_title")
                description = st.text_area("Description*", height=150, key="request_desc")
                location = st.text_input("Location*", key="request_location")
                category = st.selectbox("Category*",
                    ["Electrical", "Plumbing", "HVAC", "General", "Cleaning", "Other"],
                    key="request_category")
                priority = st.selectbox("Priority",
                    ["Low", "Medium", "High", "Critical"],
                    key="request_priority")
                
                submitted = st.form_submit_button("Submit Request", type="primary")
                
                if submitted:
                    if title and description and location:
                        # Generate request ID
                        count = query_to_dataframe(
                            "SELECT COUNT(*) as count FROM work_requests WHERE organization = ?",
                            (st.session_state.organization,)
                        ).iloc[0]['count']
                        request_id = f"WR-{st.session_state.organization[:3]}-{count+1:04d}"
                        
                        # Insert request
                        conn = get_db_connection()
                        c = conn.cursor()
                        c.execute("""
                            INSERT INTO work_requests 
                            (request_id, title, description, requested_by, organization,
                             location, priority, category)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            request_id, title, description, st.session_state.username,
                            st.session_state.organization, location, priority, category
                        ))
                        conn.commit()
                        conn.close()
                        
                        st.success(f"✅ Work request submitted! Request ID: **{request_id}**")
                        st.balloons()
                    else:
                        st.error("Please fill in all required fields (*)")
        
        with tab_objects[1]:  # My Requests
            st.subheader("📋 My Requests")
            
            my_requests = query_to_dataframe("""
                SELECT request_id, title, status, priority, created_at
                FROM work_requests 
                WHERE requested_by = ? AND organization = ?
                ORDER BY created_at DESC
            """, (st.session_state.username, st.session_state.organization))
            
            if not my_requests.empty:
                for _, req in my_requests.iterrows():
                    with st.container():
                        col_a, col_b, col_c = st.columns([3, 1, 1])
                        with col_a:
                            st.write(f"**{req['request_id']}**")
                            st.write(f"**{req['title']}**")
                            st.caption(f"Created: {req['created_at'][:10]}")
                        with col_b:
                            priority_class = f"priority-{req['priority'].lower()}"
                            st.markdown(f'<span class="{priority_class}">{req["priority"]}</span>', unsafe_allow_html=True)
                        with col_c:
                            if req['status'] == 'Completed':
                                st.success("✅ Completed")
                            elif req['status'] == 'Approved':
                                st.info("📋 Approved")
                            else:
                                st.warning("⏳ {req['status']}")
                        st.markdown("---")
            else:
                st.info("You have no work requests")

# ============================================================================
# MAIN APP LOGIC
# ============================================================================

def main():
    """Main application logic"""
    # Initialize database and session state
    init_db()
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h1 style="color: white; margin-bottom: 0.5rem;">🏢</h1>
            <h3 style="color: white; margin: 0;">A-B FM Pro™</h3>
            <p style="color: rgba(255,255,255,0.8); font-size: 0.9rem;">Facilities Management</p>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.get("authenticated", False):
            # Login form
            st.markdown("---")
            st.markdown("### 🔐 Login")
            
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", type="primary", use_container_width=True):
                if authenticate_user(username, password):
                    st.session_state.current_page = "Dashboard"
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            
            st.markdown("---")
            st.caption("**Demo Accounts:**")
            st.caption("👑 Admin: `admin` / `admin123`")
            st.caption("👨‍💼 Manager: `manager` / `manager123`")
            st.caption("👤 User: `user` / `user123`")
            st.caption("👷 Vendor: `vendor` / `vendor123`")
        
        else:
            # User info
            role_icon = {
                "Admin": "👑",
                "Facility Manager": "👨‍💼",
                "Vendor": "👷",
                "End User": "👤"
            }.get(st.session_state.role, "👤")
            
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin: 1rem 0;">
                <div style="font-size: 2rem; text-align: center;">{role_icon}</div>
                <h4 style="color: white; text-align: center; margin: 0.5rem 0;">{st.session_state.username}</h4>
                <p style="color: rgba(255,255,255,0.8); text-align: center; margin: 0; font-size: 0.9rem;">
                    {st.session_state.role}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Navigation
            if st.session_state.role == "End User":
                nav_options = ["Dashboard", "Work Management"]
            elif st.session_state.role == "Vendor":
                nav_options = ["Dashboard", "Vendor Portal"]
            else:  # Admin or Facility Manager
                nav_options = ["Dashboard", "Work Management", "Vendor Management", 
                               "Preventive Maintenance", "Diesel Tracking"]
            
            # Ensure current_page is valid
            if st.session_state.current_page not in nav_options:
                st.session_state.current_page = "Dashboard"
            
            page = st.selectbox(
                "Navigate",
                nav_options,
                index=nav_options.index(st.session_state.current_page),
                key="nav_select"
            )
            
            st.session_state.current_page = page
            
            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
    
    # Main content
    if not st.session_state.get("authenticated", False):
        # Landing page
        st.markdown('<h1 class="main-header">A-B Facilities Management Pro™</h1>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### Complete Facilities Management Solution
            
            **Features:**
            
            ✅ Multi-role Workflow  
            ✅ Preventive Maintenance  
            ✅ Diesel & Generator Tracking  
            ✅ Vendor Management  
            ✅ Work Order Management  
            ✅ PDF Reports  
            
            **Get started by logging in with demo accounts.**
            """)
        
        with col2:
            st.markdown("### 🚀 Quick Start")
            st.info("**Demo Credentials:**")
            st.code("Admin: admin / admin123")
            st.code("Manager: manager / manager123")
            st.code("User: user / user123")
            st.code("Vendor: vendor / vendor123")
    
    else:
        # Authenticated view
        if st.session_state.current_page == "Dashboard":
            show_dashboard()
        elif st.session_state.current_page == "Work Management":
            show_work_management()
        elif st.session_state.current_page == "Vendor Management":
            show_vendor_portal()
        elif st.session_state.current_page == "Vendor Portal":
            show_vendor_portal()
        elif st.session_state.current_page == "Preventive Maintenance":
            show_preventive_maintenance()
        elif st.session_state.current_page == "Diesel Tracking":
            show_diesel_tracking()
        else:
            show_dashboard()

# ============================================================================
# RUN THE APP
# ============================================================================

if __name__ == "__main__":
    main()
