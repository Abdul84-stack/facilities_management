import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, date
import base64
import io
import tempfile
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from io import BytesIO
import random
import string

# Page configuration with enhanced UI
st.set_page_config(
    page_title="Facilities Management System",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "### Facilities Management System v3.0\nDeveloped by Abdulahi Ibrahim\n© 2024 All Rights Reserved"
    }
)

# ========== DATABASE PATH FIX FOR STREAMLIT CLOUD ==========
import sqlite3
import os

def get_db_path():
    """Get the correct database path for local vs Streamlit Cloud"""
    # Check if we're on Streamlit Cloud
    if 'STREAMLIT_SHARING' in os.environ:
        # On Streamlit Cloud, use /tmp directory
        return '/tmp/facilities_management.db'
    else:
        # Local development
        return 'facilities_management.db'

def get_connection():
    """Get database connection with correct path"""
    db_path = get_db_path()
    return sqlite3.connect(db_path)

# ... (ALL THE CUSTOM CSS REMAINS THE SAME - keep the entire <style> section)

# Database setup with enhanced schema
def init_database():
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
    
    # Create maintenance_requests table
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
    
    # Create vendors table
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
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            certificate_incorporation BLOB,
            tax_clearance_certificate BLOB,
            audited_financial_statement BLOB
        )
    ''')
    
    # Create invoices table with Naira currency
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
    
    # Planned Preventive Maintenance Schedule
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
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_date DATE,
            completion_notes TEXT
        )
    ''')
    
    # Generator Diesel Daily Record
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
    
    # Space Management (Room Bookings)
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
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # HSE Schedule and Inspections
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
    
    # HSE Incidents
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
    
    # ========== REDUCED SAMPLE DATA INSERTION ==========
    
    # Check if users already exist to avoid duplicates
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    
    if user_count == 0:
        # Insert sample users
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
    
    # Check if vendors already exist
    cursor.execute('SELECT COUNT(*) FROM vendors')
    vendor_count = cursor.fetchone()[0]
    
    if vendor_count == 0:
        # Insert sample vendors
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
            cursor.execute('''
                INSERT INTO vendors 
                (username, company_name, contact_person, email, phone, vendor_type, services_offered, 
                 annual_turnover, tax_identification_number, rc_number, key_management_staff, 
                 account_details, certification, address) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, company_name, contact_person, email, phone, vendor_type, services_offered,
                  annual_turnover, tax_id, rc_number, key_staff, account_details, certification, address))
    
    # Check if preventive maintenance data already exists
    cursor.execute('SELECT COUNT(*) FROM preventive_maintenance')
    pm_count = cursor.fetchone()[0]
    
    if pm_count == 0:
        # Reduced preventive maintenance data (5 records)
        today = datetime.now().date()
        sample_maintenance = [
            ('Main HVAC System', 'HVAC', 'Main Building', 'Routine Check', 'Monthly', 
             (today - timedelta(days=15)).isoformat(), (today + timedelta(days=15)).isoformat(), 'HVAC Team', 'Regular maintenance check'),
            ('Fire Extinguishers', 'Fire Safety', 'All Floors', 'Inspection', 'Biannual',
             (today - timedelta(days=60)).isoformat(), (today + timedelta(days=120)).isoformat(), 'Safety Officer', 'Fire safety inspection'),
            ('Smoke Detectors', 'Fire Safety', 'All Floors', 'Testing', 'Quarterly',
             (today - timedelta(days=45)).isoformat(), (today + timedelta(days=45)).isoformat(), 'Maintenance Team', 'System testing'),
            ('Generator Set #1', 'Generator', 'Generator Room', 'Service', '200 hours',
             (today - timedelta(days=10)).isoformat(), (today + timedelta(days=10)).isoformat(), 'Generator Team', 'Regular service'),
            ('Pest Control', 'General', 'Entire Facility', 'Fumigation', 'Quarterly',
             (today - timedelta(days=30)).isoformat(), (today + timedelta(days=60)).isoformat(), 'Pest Control Vendor', 'Full facility fumigation')
        ]
        
        for equipment_name, equipment_type, location, maintenance_type, frequency, last_date, next_date, assigned_to, notes in sample_maintenance:
            cursor.execute('''
                INSERT INTO preventive_maintenance 
                (equipment_name, equipment_type, location, maintenance_type, frequency, 
                 last_maintenance_date, next_maintenance_date, assigned_to, notes) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (equipment_name, equipment_type, location, maintenance_type, frequency, last_date, next_date, assigned_to, notes))
    
    # Check if generator records already exist
    cursor.execute('SELECT COUNT(*) FROM generator_records')
    gen_count = cursor.fetchone()[0]
    
    if gen_count == 0:
        # Reduced generator records (3 records)
        today = datetime.now().date()
        for i in range(3):
            record_date = today - timedelta(days=i)
            cursor.execute('''
                INSERT INTO generator_records 
                (record_date, generator_name, opening_hours, closing_hours, 
                 opening_diesel_level, closing_diesel_level, recorded_by, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (record_date.isoformat(), 'Generator #1', 
                  1000 + i*8, 1008 + i*8,
                  500 - i*50, 450 - i*50, 
                  'facility_user', f'Daily operation - Day {i+1}'))
    
    # Check if space bookings already exist
    cursor.execute('SELECT COUNT(*) FROM space_bookings')
    space_count = cursor.fetchone()[0]
    
    if space_count == 0:
        # Reduced space bookings (2 records)
        today = datetime.now().date()
        sample_bookings = [
            ('Conference Room A', 'Conference', today.isoformat(), '09:00', '12:00', 
             'Management Meeting', 'facility_manager', 'Management', 10, 'Confirmed', 0, None),
            ('Meeting Room B', 'Meeting', (today + timedelta(days=1)).isoformat(), '14:00', '16:00', 
             'Team Brainstorming', 'facility_user', 'Operations', 6, 'Confirmed', 0, None)
        ]
        
        for booking in sample_bookings:
            cursor.execute('''
                INSERT INTO space_bookings 
                (room_name, room_type, booking_date, start_time, end_time, purpose, 
                 booked_by, department, attendees_count, status, catering_required, special_requirements)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', booking)
    
    # Check if HSE schedule already exists
    cursor.execute('SELECT COUNT(*) FROM hse_schedule')
    hse_count = cursor.fetchone()[0]
    
    if hse_count == 0:
        # Reduced HSE schedule (3 records)
        today = datetime.now().date()
        sample_hse_schedule = [
            ('Fire Safety Inspection', 'All Buildings', 'Quarterly', 
             (today - timedelta(days=45)).isoformat(), (today + timedelta(days=45)).isoformat(), 
             'hse_officer', 'Compliant', None, None, None),
            ('First Aid Kit Check', 'All Floors', 'Monthly',
             (today - timedelta(days=20)).isoformat(), (today + timedelta(days=10)).isoformat(),
             'hse_officer', 'Non-Compliant', 'Some kits missing bandages', 'Restock bandages', (today + timedelta(days=7)).isoformat()),
            ('Emergency Exit Inspection', 'Main Building', 'Monthly',
             (today - timedelta(days=15)).isoformat(), (today + timedelta(days=15)).isoformat(),
             'hse_officer', 'Compliant', None, None, None)
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

# ... (ALL OTHER FUNCTIONS REMAIN THE SAME - keep all the existing code)

# ... (Continue with all the other functions like execute_query, execute_update, etc.)

# ========== UPDATED VENDOR REGISTRATION FUNCTION ==========
def show_vendor_registration():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🏢 Vendor Registration")
    st.markdown('</div>', unsafe_allow_html=True)
    
    existing_vendor = execute_query(
        'SELECT * FROM vendors WHERE username = ?',
        (st.session_state.user['username'],)
    )
    
    if existing_vendor:
        st.success("✅ You are already registered as a vendor!")
        vendor = existing_vendor[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write("**🏢 Company Information**")
            st.write(f"**Company Name:** {safe_str(safe_get(vendor, 'company_name'), 'N/A')}")
            st.write(f"**Contact Person:** {safe_str(safe_get(vendor, 'contact_person'), 'N/A')}")
            st.write(f"**Email:** {safe_str(safe_get(vendor, 'email'), 'N/A')}")
            st.write(f"**Phone:** {safe_str(safe_get(vendor, 'phone'), 'N/A')}")
            st.write(f"**Vendor Type:** {safe_str(safe_get(vendor, 'vendor_type'), 'N/A')}")
            annual_turnover = safe_get(vendor, 'annual_turnover')
            if annual_turnover:
                st.write(f"**Annual Turnover:** {format_naira(annual_turnover)}")
            else:
                st.write("**Annual Turnover:** Not specified")
            tax_id = safe_get(vendor, 'tax_identification_number')
            st.write(f"**Tax ID:** {safe_str(tax_id)}" if tax_id else "**Tax ID:** Not specified")
            rc_number = safe_get(vendor, 'rc_number')
            st.write(f"**RC Number:** {safe_str(rc_number)}" if rc_number else "**RC Number:** Not specified")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write("**🔧 Services & Details**")
            st.write(f"**Services Offered:** {safe_str(safe_get(vendor, 'services_offered'), 'N/A')}")
            key_staff = safe_get(vendor, 'key_management_staff')
            st.write(f"**Key Management Staff:** {safe_str(key_staff)}" if key_staff else "**Key Management Staff:** Not specified")
            account_details = safe_get(vendor, 'account_details')
            st.write(f"**Account Details:** {safe_str(account_details)}" if account_details else "**Account Details:** Not specified")
            st.write(f"**Certification:** {safe_str(safe_get(vendor, 'certification'), 'Not specified')}")
            st.write(f"**Address:** {safe_str(safe_get(vendor, 'address'), 'N/A')}")
            st.write(f"**Registration Date:** {safe_str(safe_get(vendor, 'registration_date'), 'N/A')}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        return
    
    st.info("📝 Please complete your vendor registration details below:")
    
    with st.form("vendor_registration", clear_on_submit=True):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("🏢 Company Name *")
            contact_person = st.text_input("👤 Contact Person *")
            email = st.text_input("📧 Email *")
            phone = st.text_input("📞 Phone *")
            vendor_type = st.text_input("🔧 Vendor Type", value=st.session_state.user['vendor_type'], disabled=True)
            annual_turnover = st.number_input("💰 Annual Turnover (₦)", min_value=0.0, step=1000.0, format="%.2f")
            tax_identification_number = st.text_input("🏛️ Tax Identification Number")
            rc_number = st.text_input("📄 RC Number")
        
        with col2:
            services_offered = st.text_area("🔧 Services Offered *", height=100)
            key_management_staff = st.text_area("👥 Key Management Staff", height=80, 
                                              placeholder="List key management staff and their positions...")
            account_details = st.text_area("🏦 Account Details", height=80, 
                                         placeholder="Bank name, account number, routing number...")
            certification = st.text_input("📜 Certification (Optional)")
            address = st.text_area("📍 Address *", height=80)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Vendor Login Details Section
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🔑 Vendor Login Details")
        st.write("Vendor login details will be automatically generated upon registration.")
        
        # Generate vendor-specific username and password
        if company_name:
            # Generate username from company name (lowercase, no spaces)
            vendor_username = company_name.lower().replace(' ', '_').replace('.', '').replace(',', '') + "_vendor"
            # Generate a random password
            vendor_password = '0123456'  # Default password for consistency
            
            st.write(f"**Generated Username:** `{vendor_username}`")
            st.write(f"**Generated Password:** `{vendor_password}`")
            st.write("**Note:** These credentials will be saved for the vendor to access the system.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        submitted = st.form_submit_button("🚀 Register Vendor", use_container_width=True)
        
        if submitted:
            if not all([company_name, contact_person, email, phone, services_offered, address]):
                st.error("⚠️ Please fill in all required fields (*)")
            else:
                # First, create a user account for the vendor
                vendor_username = company_name.lower().replace(' ', '_').replace('.', '').replace(',', '') + "_vendor"
                vendor_password = '0123456'  # Default password for all vendors
                
                # Check if username already exists
                existing_user = execute_query('SELECT * FROM users WHERE username = ?', (vendor_username,))
                if existing_user:
                    st.error(f"❌ Username '{vendor_username}' already exists. Please modify company name.")
                else:
                    # Create user account
                    user_success = execute_update(
                        'INSERT INTO users (username, password_hash, role, vendor_type) VALUES (?, ?, ?, ?)',
                        (vendor_username, vendor_password, 'vendor', st.session_state.user['vendor_type'])
                    )
                    
                    if user_success:
                        # Then create vendor record
                        vendor_success = execute_update(
                            '''INSERT INTO vendors 
                            (username, company_name, contact_person, email, phone, vendor_type, services_offered, 
                            annual_turnover, tax_identification_number, rc_number, key_management_staff, 
                            account_details, certification, address) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            (vendor_username, company_name, contact_person, email, phone, 
                             st.session_state.user['vendor_type'], services_offered, annual_turnover, 
                             tax_identification_number, rc_number, key_management_staff, 
                             account_details, certification, address)
                        )
                        
                        if vendor_success:
                            st.success("✅ Vendor registration completed successfully!")
                            st.success(f"**Vendor Login Details:**")
                            st.success(f"**Username:** `{vendor_username}`")
                            st.success(f"**Password:** `{vendor_password}`")
                            st.rerun()
                        else:
                            st.error("❌ Failed to complete vendor registration")
                    else:
                        st.error("❌ Failed to create user account for vendor")

# ... (ALL OTHER FUNCTIONS REMAIN THE SAME - make sure you keep all the existing code)

def main():
    # Initialize session state for user if not exists
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    if st.session_state.user is None:
        show_login()
    else:
        show_main_app()

if __name__ == "__main__":
    # Initialize database (only creates tables if they don't exist)
    init_database()
    
    # Run the app
    main()
