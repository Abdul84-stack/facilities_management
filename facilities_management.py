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
        max-width: 600px;
        margin: 0 auto;
    }
    
    .login-title {
        text-align: center;
        font-size: 2.5em;
        margin-bottom: 30px;
        color: white;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Button styling */
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
    
    /* Logout button specific styling */
    div[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
        background: linear-gradient(45deg, #f44336, #d32f2f) !important;
        color: white !important;
    }
    
    div[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {
        background: linear-gradient(45deg, #d32f2f, #b71c1c) !important;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(211, 47, 47, 0.4) !important;
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
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2c3e50, #34495e) !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
    }
    
    /* METRIC CARD STYLING */
    [data-testid="metric-container"] {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Custom separator */
    .separator {
        height: 4px;
        background: linear-gradient(90deg, #4CAF50, #2196F3);
        border-radius: 2px;
        margin: 20px 0;
    }
    
    /* FIX FOR SIDEBAR RADIO BUTTONS TEXT COLOR */
    [data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stRadio span {
        color: white !important;
        font-weight: 500 !important;
        font-size: 16px !important;
    }
    
    /* Make radio button circles visible */
    [data-testid="stSidebar"] .stRadio > div > label > div:first-child {
        background-color: white !important;
    }
    
    /* Style for selected radio button */
    [data-testid="stSidebar"] .stRadio > div > label > div:first-child > div {
        background-color: #4CAF50 !important;
    }
    
    /* Fix for all text in sidebar */
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Specific fix for radio labels */
    [data-testid="stSidebar"] label {
        color: white !important;
    }
    
    /* Fix for sidebar headings */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] h5,
    [data-testid="stSidebar"] h6,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] span {
        color: white !important;
    }
    
    /* Fix sidebar radio button container */
    [data-testid="stSidebar"] .stRadio > div {
        background-color: rgba(255,255,255,0.1);
        padding: 10px;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* Hover effect for radio buttons */
    [data-testid="stSidebar"] .stRadio > div:hover {
        background-color: rgba(255,255,255,0.15);
    }
    
    /* Footer styling */
    .app-footer {
        background: linear-gradient(90deg, #1a237e, #283593);
        color: white;
        text-align: center;
        padding: 10px;
        margin-top: 40px;
        border-radius: 5px;
        font-size: 12px;
    }
    
    /* Logout container styling */
    .logout-container {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 20px;
        background: transparent;
    }
    
    /* Metric card styling - separate class */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .metric-card h4 {
        color: #666;
        margin: 0 0 10px 0;
        font-size: 14px;
        text-transform: uppercase;
    }
    
    .metric-card h3 {
        color: #1a237e;
        margin: 0;
        font-size: 24px;
        font-weight: bold;
    }
    
    /* Make sure all streamlit metric text is visible */
    [data-testid="stMetricValue"], 
    [data-testid="stMetricLabel"] {
        color: #333 !important;
    }
    
    /* PDF Download button styling */
    .pdf-download-btn {
        background: linear-gradient(45deg, #2196F3, #1976D2) !important;
        margin-top: 10px;
    }
    
    /* Format for K notation */
    .k-notation {
        font-family: monospace;
        color: #1a237e;
        font-weight: bold;
    }
    
    /* Status indicators */
    .status-upcoming {
        color: #FF9800;
        font-weight: bold;
    }
    
    .status-due {
        color: #F44336;
        font-weight: bold;
    }
    
    .status-completed {
        color: #4CAF50;
        font-weight: bold;
    }
    
    /* Booking status */
    .booking-confirmed {
        background-color: #E8F5E9;
        padding: 5px 10px;
        border-radius: 5px;
        color: #2E7D32;
        font-weight: bold;
    }
    
    .booking-pending {
        background-color: #FFF3E0;
        padding: 5px 10px;
        border-radius: 5px;
        color: #EF6C00;
        font-weight: bold;
    }
    
    .booking-cancelled {
        background-color: #FFEBEE;
        padding: 5px 10px;
        border-radius: 5px;
        color: #C62828;
        font-weight: bold;
    }
    
    /* HSE status */
    .hse-compliant {
        background-color: #E8F5E9;
        color: #2E7D32;
        font-weight: bold;
        padding: 5px 10px;
        border-radius: 5px;
    }
    
    .hse-non-compliant {
        background-color: #FFEBEE;
        color: #C62828;
        font-weight: bold;
        padding: 5px 10px;
        border-radius: 5px;
    }
    
    /* Alert styling */
    .alert-warning {
        background-color: #FFF3CD;
        border-left: 4px solid #FFC107;
        padding: 15px;
        margin: 10px 0;
        border-radius: 4px;
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

# Database setup with enhanced schema - REDUCED SAMPLE DATA
def init_database():
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
    
    # ========== NEW TABLES FOR REQUESTED FEATURES ==========
    
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
        try:
            cursor.execute(
                'INSERT OR IGNORE INTO users (username, password_hash, role, vendor_type) VALUES (?, ?, ?, ?)',
                (username, password, role, vendor_type)
            )
        except sqlite3.IntegrityError:
            pass
    
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
    
    # Insert sample preventive maintenance data - REDUCED TO 3
    today = datetime.now().date()
    sample_maintenance = [
        ('Main HVAC System', 'HVAC', 'Main Building', 'Routine Check', 'Monthly', 
         (today - timedelta(days=15)).isoformat(), (today + timedelta(days=15)).isoformat(), 'HVAC Team', 'Regular monthly check'),
        ('Generator Set #1', 'Generator', 'Generator Room', 'Service', '200 hours',
         (today - timedelta(days=10)).isoformat(), (today + timedelta(days=10)).isoformat(), 'Generator Team', 'Full service required'),
        ('Fire Extinguishers', 'Fire Safety', 'All Floors', 'Inspection', 'Biannual',
         (today - timedelta(days=60)).isoformat(), (today + timedelta(days=120)).isoformat(), 'Safety Officer', 'Pressure check and refill')
    ]
    
    for equipment_name, equipment_type, location, maintenance_type, frequency, last_date, next_date, assigned_to, notes in sample_maintenance:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO preventive_maintenance 
                (equipment_name, equipment_type, location, maintenance_type, frequency, 
                 last_maintenance_date, next_maintenance_date, assigned_to, notes) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (equipment_name, equipment_type, location, maintenance_type, frequency, last_date, next_date, assigned_to, notes))
        except sqlite3.IntegrityError:
            pass
    
    # Insert sample generator records - REDUCED TO 2
    for i in range(2):  # Only 2 records
        record_date = today - timedelta(days=i)
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO generator_records 
                (record_date, generator_name, opening_hours, closing_hours, 
                 opening_diesel_level, closing_diesel_level, recorded_by, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (record_date.isoformat(), 'Generator #1', 
                  1000 + i*8, 1008 + i*8,
                  500 - i*50, 450 - i*50, 
                  'facility_user', f'Daily operation - Day {i+1}'))
        except sqlite3.IntegrityError:
            pass
    
    # Insert sample space bookings - REDUCED TO 3
    sample_bookings = [
        ('Conference Room A', 'Conference', today.isoformat(), '09:00', '12:00', 
         'Management Meeting', 'facility_manager', 'Management', 10, 'Confirmed', 0, None),
        ('Meeting Room B', 'Meeting', today.isoformat(), '14:00', '16:00', 
         'Team Brainstorming', 'facility_user', 'Operations', 6, 'Confirmed', 0, None),
        ('Cafeteria', 'Cafeteria', (today + timedelta(days=1)).isoformat(), '12:00', '15:00', 
         'Company Town Hall', 'hse_officer', 'All', 100, 'Confirmed', 1, 'Need audio system and projector')
    ]
    
    for booking in sample_bookings:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO space_bookings 
                (room_name, room_type, booking_date, start_time, end_time, purpose, 
                 booked_by, department, attendees_count, status, catering_required, special_requirements)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', booking)
        except sqlite3.IntegrityError:
            pass
    
    # Insert sample HSE schedule - REDUCED TO 5
    sample_hse_schedule = [
        ('Fire Safety Inspection', 'All Buildings', 'Quarterly', 
         (today - timedelta(days=45)).isoformat(), (today + timedelta(days=45)).isoformat(), 
         'hse_officer', 'Compliant', None, None, None),
        ('First Aid Kit Check', 'All Floors', 'Monthly',
         (today - timedelta(days=20)).isoformat(), (today + timedelta(days=10)).isoformat(),
         'hse_officer', 'Non-Compliant', 'Some kits missing bandages', 'Restock bandages', (today + timedelta(days=7)).isoformat()),
        ('Emergency Exit Inspection', 'Main Building', 'Monthly',
         (today - timedelta(days=15)).isoformat(), (today + timedelta(days=15)).isoformat(),
         'hse_officer', 'Compliant', None, None, None),
        ('Electrical Safety Check', 'Generator Room', 'Monthly',
         (today - timedelta(days=10)).isoformat(), (today + timedelta(days=20)).isoformat(),
         'hse_officer', 'Compliant', None, None, None),
        ('PPE Inspection', 'Production Area', 'Weekly',
         (today - timedelta(days=7)).isoformat(), today.isoformat(),
         'hse_officer', 'Compliant', None, None, None)
    ]
    
    for inspection in sample_hse_schedule:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO hse_schedule 
                (inspection_type, area, frequency, last_inspection_date, next_inspection_date,
                 assigned_to, compliance_level, findings, corrective_actions, follow_up_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', inspection)
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()

# Initialize database
init_database()

# Database functions with connection pooling
@st.cache_resource
def get_connection_pool():
    """Create a database connection pool"""
    return sqlite3.connect('facilities_management.db', check_same_thread=False)

def get_connection():
    return get_connection_pool()

def execute_query(query, params=()):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        return results
    except Exception as e:
        st.error(f"Query error: {e}")
        return []
    finally:
        # Don't close the connection in the pooled version
        pass

def execute_update(query, params=()):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Database update error: {e}")
        return False
    finally:
        # Don't close the connection in the pooled version
        pass

# Safe data access functions
def safe_get(data, key, default=None):
    if not data or not isinstance(data, dict):
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

def safe_date(value, default=None):
    try:
        if value is None:
            return default
        if isinstance(value, str):
            return datetime.strptime(value, '%Y-%m-%d').date()
        return value
    except:
        return default

# Currency formatting function
def format_naira(amount, decimal_places=2):
    try:
        amount = safe_float(amount, 0)
        return f"₦{amount:,.{decimal_places}f}"
    except:
        return "₦0.00"

# Cache expensive database queries
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_user_requests(username):
    return execute_query(
        'SELECT * FROM maintenance_requests WHERE created_by = ? ORDER BY created_date DESC LIMIT 100',
        (username,)
    )

@st.cache_data(ttl=300)
def get_all_requests():
    return execute_query('SELECT * FROM maintenance_requests ORDER BY created_date DESC LIMIT 100')

@st.cache_data(ttl=300)
def get_vendor_requests(vendor_username):
    return execute_query(
        'SELECT * FROM maintenance_requests WHERE assigned_vendor = ? ORDER BY created_date DESC LIMIT 100',
        (vendor_username,)
    )

# ========== NEW FUNCTIONS FOR REQUESTED FEATURES ==========

# Preventive Maintenance Functions
@st.cache_data(ttl=300)
def get_preventive_maintenance(filters=None):
    base_query = 'SELECT * FROM preventive_maintenance WHERE 1=1'
    params = []
    
    if filters:
        if filters.get('status'):
            base_query += ' AND status = ?'
            params.append(filters['status'])
        if filters.get('equipment_type'):
            base_query += ' AND equipment_type = ?'
            params.append(filters['equipment_type'])
        if filters.get('location'):
            base_query += ' AND location = ?'
            params.append(filters['location'])
    
    base_query += ' ORDER BY next_maintenance_date ASC LIMIT 50'
    return execute_query(base_query, params)

# Generator Records Functions
@st.cache_data(ttl=300)
def get_generator_records(start_date=None, end_date=None):
    query = '''
        SELECT 
            id, record_date, generator_name, opening_hours, closing_hours,
            opening_diesel_level, closing_diesel_level, recorded_by, notes, created_date,
            (closing_hours - opening_hours) as net_hours_used,
            (opening_diesel_level - closing_diesel_level) as diesel_consumed
        FROM generator_records 
        WHERE 1=1
    '''
    params = []
    
    if start_date:
        query += ' AND record_date >= ?'
        params.append(start_date.isoformat())
    if end_date:
        query += ' AND record_date <= ?'
        params.append(end_date.isoformat())
    
    query += ' ORDER BY record_date DESC LIMIT 50'
    return execute_query(query, params)

@st.cache_data(ttl=300)
def get_generator_summary():
    records = execute_query('''
        SELECT 
            generator_name,
            COUNT(*) as total_days,
            SUM(closing_hours - opening_hours) as total_hours,
            SUM(opening_diesel_level - closing_diesel_level) as total_diesel,
            AVG(closing_hours - opening_hours) as avg_hours_per_day,
            AVG(opening_diesel_level - closing_diesel_level) as avg_diesel_per_day
        FROM generator_records 
        WHERE record_date >= date('now', '-30 days')
        GROUP BY generator_name
    ''')
    return records

# Space Management Functions
@st.cache_data(ttl=300)
def get_space_bookings(filters=None):
    base_query = '''
        SELECT * FROM space_bookings 
        WHERE 1=1
    '''
    params = []
    
    if filters:
        if filters.get('room_type'):
            base_query += ' AND room_type = ?'
            params.append(filters['room_type'])
        if filters.get('status'):
            base_query += ' AND status = ?'
            params.append(filters['status'])
        if filters.get('booking_date'):
            base_query += ' AND booking_date = ?'
            params.append(filters['booking_date'].isoformat())
        if filters.get('booked_by'):
            base_query += ' AND booked_by = ?'
            params.append(filters['booked_by'])
    
    base_query += ' ORDER BY booking_date DESC, start_time ASC LIMIT 50'
    return execute_query(base_query, params)

# HSE Schedule Functions
@st.cache_data(ttl=300)
def get_hse_schedule(filters=None):
    base_query = 'SELECT * FROM hse_schedule WHERE 1=1'
    params = []
    
    if filters:
        if filters.get('status'):
            base_query += ' AND status = ?'
            params.append(filters['status'])
        if filters.get('compliance_level'):
            base_query += ' AND compliance_level = ?'
            params.append(filters['compliance_level'])
        if filters.get('inspection_type'):
            base_query += ' AND inspection_type = ?'
            params.append(filters['inspection_type'])
    
    base_query += ' ORDER BY next_inspection_date ASC LIMIT 50'
    return execute_query(base_query, params)

@st.cache_data(ttl=300)
def get_hse_incidents(filters=None):
    base_query = 'SELECT * FROM hse_incidents WHERE 1=1'
    params = []
    
    if filters:
        if filters.get('severity'):
            base_query += ' AND severity = ?'
            params.append(filters['severity'])
        if filters.get('status'):
            base_query += ' AND status = ?'
            params.append(filters['status'])
        if filters.get('start_date'):
            base_query += ' AND incident_date >= ?'
            params.append(filters['start_date'].isoformat())
        if filters.get('end_date'):
            base_query += ' AND incident_date <= ?'
            params.append(filters['end_date'].isoformat())
    
    base_query += ' ORDER BY incident_date DESC LIMIT 50'
    return execute_query(base_query, params)

# Authentication
def authenticate_user(username, password):
    users = execute_query('SELECT * FROM users WHERE username = ? AND password_hash = ?', (username, password))
    return users[0] if users else None

# ========== UPDATED DASHBOARD WITH WORKING QUICK ACTIONS ==========

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
    elif role == 'hse_officer':
        show_hse_dashboard()
    elif role == 'space_manager':
        show_space_dashboard()
    else:
        show_vendor_dashboard()

def show_user_dashboard():
    user_requests = get_user_requests(st.session_state.user['username'])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<h4>Total Requests</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3>{len(user_requests)}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        pending_count = len([r for r in user_requests if safe_get(r, 'status') == 'Pending'])
        st.markdown('<h4>Pending</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3>{pending_count}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        completed_count = len([r for r in user_requests if safe_get(r, 'status') == 'Completed'])
        st.markdown('<h4>Completed</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3>{completed_count}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # FIXED: Working Quick Access buttons
    st.subheader("🚀 Quick Access")
    
    col_q1, col_q2, col_q3 = st.columns(3)
    
    with col_q1:
        if st.button("📅 Book a Room", use_container_width=True, key="quick_book_room"):
            st.session_state.navigation_menu = "Space Management"
            st.rerun()
    
    with col_q2:
        if st.button("⛽ Generator Records", use_container_width=True, key="quick_generator"):
            st.session_state.navigation_menu = "Generator Records"
            st.rerun()
    
    with col_q3:
        if st.button("🚨 Report Incident", use_container_width=True, key="quick_incident"):
            st.session_state.navigation_menu = "HSE Management"
            st.rerun()
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
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
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<h4>Total Requests</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3>{len(all_requests)}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        pending_count = len([r for r in all_requests if safe_get(r, 'status') == 'Pending'])
        st.markdown('<h4>Pending</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3>{pending_count}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        assigned_count = len([r for r in all_requests if safe_get(r, 'status') == 'Assigned'])
        st.markdown('<h4>Assigned</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3>{assigned_count}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        completed_count = len([r for r in all_requests if safe_get(r, 'status') == 'Completed'])
        st.markdown('<h4>Completed</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3>{completed_count}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # FIXED: Working Quick Access buttons for managers
    st.subheader("🚀 Management Quick Access")
    
    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
    
    with col_q1:
        if st.button("📅 Maintenance Schedule", use_container_width=True, key="quick_maintenance"):
            st.session_state.navigation_menu = "Preventive Maintenance"
            st.rerun()
    
    with col_q2:
        if st.button("🏢 Space Management", use_container_width=True, key="quick_space"):
            st.session_state.navigation_menu = "Space Management"
            st.rerun()
    
    with col_q3:
        if st.button("🚨 HSE Dashboard", use_container_width=True, key="quick_hse"):
            st.session_state.navigation_menu = "HSE Management"
            st.rerun()
    
    with col_q4:
        if st.button("⛽ Generator Reports", use_container_width=True, key="quick_gen_reports"):
            st.session_state.navigation_menu = "Generator Records"
            st.rerun()
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
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

# ========== UPDATED PREVENTIVE MAINTENANCE ==========

def show_preventive_maintenance():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("📅 Planned Preventive Maintenance Schedule")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Schedule Overview", "➕ Add New Schedule", "📊 Reports & Analytics"])
    
    with tab1:
        st.subheader("🔧 Maintenance Schedule")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox("Filter by Status", ["All", "Upcoming", "Due", "Completed"], key="pm_status")
        with col2:
            equipment_filter = st.selectbox("Filter by Equipment Type", ["All", "HVAC", "Generator", "Fire Safety", "General"], key="pm_equipment")
        with col3:
            location_filter = st.selectbox("Filter by Location", ["All", "Main Building", "Generator Room", "All Floors", "Entire Facility"], key="pm_location")
        
        filters = {}
        if status_filter != "All":
            filters['status'] = status_filter
        if equipment_filter != "All":
            filters['equipment_type'] = equipment_filter
        if location_filter != "All":
            filters['location'] = location_filter
        
        # Add caching for better performance
        if 'maintenance_data' not in st.session_state or st.button("🔄 Refresh Data"):
            maintenance_schedule = get_preventive_maintenance(filters)
            st.session_state.maintenance_data = maintenance_schedule
        else:
            maintenance_schedule = st.session_state.maintenance_data
        
        if not maintenance_schedule:
            st.info("📭 No maintenance schedules found")
        else:
            # Display maintenance schedule with progress bar for better UX
            with st.spinner("Loading maintenance schedule..."):
                display_data = []
                for item in maintenance_schedule:
                    next_date = safe_date(item.get('next_maintenance_date'))
                    status = item.get('status', 'Upcoming')
                    
                    # Determine if overdue
                    if status != 'Completed' and next_date and next_date < datetime.now().date():
                        status = "Due"
                    
                    display_data.append({
                        'ID': item.get('id'),
                        'Equipment': item.get('equipment_name'),
                        'Type': item.get('equipment_type'),
                        'Location': item.get('location'),
                        'Maintenance Type': item.get('maintenance_type'),
                        'Frequency': item.get('frequency'),
                        'Last Done': item.get('last_maintenance_date', 'Never'),
                        'Next Due': next_date.strftime('%Y-%m-%d') if next_date else 'N/A',
                        'Status': status,
                        'Assigned To': item.get('assigned_to', 'Not assigned')
                    })
                
                df = pd.DataFrame(display_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Action buttons for each item
            st.subheader("🛠️ Maintenance Actions")
            selected_id = st.selectbox("Select maintenance item to update", [""] + [str(item.get('id')) for item in maintenance_schedule])
            
            if selected_id:
                item = next((i for i in maintenance_schedule if str(i.get('id')) == selected_id), None)
                if item:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.write(f"**Equipment:** {item.get('equipment_name')}")
                        st.write(f"**Type:** {item.get('equipment_type')}")
                        st.write(f"**Location:** {item.get('location')}")
                        st.write(f"**Maintenance Type:** {item.get('maintenance_type')}")
                        st.write(f"**Frequency:** {item.get('frequency')}")
                        st.write(f"**Next Due Date:** {item.get('next_maintenance_date')}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.write("**✅ Mark as Completed**")
                        
                        with st.form(f"complete_maintenance_{selected_id}"):
                            completion_notes = st.text_area("Completion Notes", 
                                                           placeholder="Describe what maintenance was performed...")
                            
                            # Calculate next maintenance date based on frequency
                            frequency = item.get('frequency', 'Monthly')
                            next_date = datetime.now().date()
                            
                            if frequency == 'Monthly':
                                next_date = next_date + timedelta(days=30)
                            elif frequency == 'Quarterly':
                                next_date = next_date + timedelta(days=90)
                            elif frequency == 'Biannual':
                                next_date = next_date + timedelta(days=180)
                            elif frequency == '200 hours':
                                next_date = next_date + timedelta(days=30)  # Approximate
                            
                            new_next_date = st.date_input("Next Maintenance Date", value=next_date)
                            
                            if st.form_submit_button("✅ Mark as Completed"):
                                today = datetime.now().date()
                                success = execute_update('''
                                    UPDATE preventive_maintenance 
                                    SET status = ?, completed_date = ?, completion_notes = ?, last_maintenance_date = ?
                                    WHERE id = ?
                                ''', ('Completed', today.isoformat(), completion_notes, today.isoformat(), int(selected_id)))
                                
                                if success:
                                    # Clear cache for fresh data
                                    if 'maintenance_data' in st.session_state:
                                        del st.session_state.maintenance_data
                                    st.success("✅ Maintenance marked as completed!")
                                    st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
        
        # Alerts for overdue items
        overdue_items = [i for i in maintenance_schedule if i.get('status') != 'Completed' 
                        and safe_date(i.get('next_maintenance_date')) 
                        and safe_date(i.get('next_maintenance_date')) < datetime.now().date()]
        
        if overdue_items:
            st.markdown('<div class="alert-danger">', unsafe_allow_html=True)
            st.warning(f"⚠️ **Alert:** {len(overdue_items)} maintenance item(s) are overdue!")
            for item in overdue_items[:3]:  # Show only 3 overdue items
                st.write(f"• {item.get('equipment_name')} at {item.get('location')} (Due: {item.get('next_maintenance_date')})")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.subheader("➕ Add New Preventive Maintenance Schedule")
        
        with st.form("add_maintenance_schedule"):
            col1, col2 = st.columns(2)
            
            with col1:
                equipment_name = st.text_input("Equipment Name *")
                equipment_type = st.selectbox("Equipment Type *", 
                                            ["HVAC", "Generator", "Fire Extinguisher", 
                                             "Smoke Detector", "Fire Alarm", "Pest Control", "Other"])
                location = st.text_input("Location *", value="Common Area")
                maintenance_type = st.selectbox("Maintenance Type *", 
                                              ["Routine Check", "Inspection", "Testing", 
                                               "Service", "Calibration", "Fumigation"])
            
            with col2:
                frequency = st.selectbox("Frequency *", 
                                       ["Daily", "Weekly", "Monthly", "Quarterly", 
                                        "Biannual", "Annual", "200 hours"])
                last_maintenance_date = st.date_input("Last Maintenance Date", value=datetime.now().date())
                next_maintenance_date = st.date_input("Next Maintenance Date *", 
                                                     value=datetime.now().date() + timedelta(days=30))
                assigned_to = st.text_input("Assigned To", placeholder="Name or department")
                notes = st.text_area("Notes")
            
            submitted = st.form_submit_button("✅ Add to Schedule", use_container_width=True)
            
            if submitted:
                if not all([equipment_name, equipment_type, location, maintenance_type, frequency]):
                    st.error("⚠️ Please fill in all required fields (*)")
                else:
                    success = execute_update('''
                        INSERT INTO preventive_maintenance 
                        (equipment_name, equipment_type, location, maintenance_type, frequency, 
                         last_maintenance_date, next_maintenance_date, assigned_to, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (equipment_name, equipment_type, location, maintenance_type, frequency,
                          last_maintenance_date.isoformat(), next_maintenance_date.isoformat(), 
                          assigned_to, notes))
                    if success:
                        # Clear cache for fresh data
                        if 'maintenance_data' in st.session_state:
                            del st.session_state.maintenance_data
                        st.success("✅ Preventive maintenance schedule added successfully!")
                        st.rerun()
    
    with tab3:
        st.subheader("📊 Maintenance Analytics")
        
        # Summary statistics with caching
        if 'all_maintenance' not in st.session_state:
            all_maintenance = get_preventive_maintenance()
            st.session_state.all_maintenance = all_maintenance
        else:
            all_maintenance = st.session_state.all_maintenance
        
        if all_maintenance:
            total_items = len(all_maintenance)
            completed_items = len([i for i in all_maintenance if i.get('status') == 'Completed'])
            upcoming_items = len([i for i in all_maintenance if i.get('status') == 'Upcoming'])
            due_items = len([i for i in all_maintenance if i.get('status') != 'Completed' 
                           and safe_date(i.get('next_maintenance_date')) 
                           and safe_date(i.get('next_maintenance_date')) < datetime.now().date()])
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Items", total_items)
            with col2:
                st.metric("Completed", completed_items)
            with col3:
                st.metric("Upcoming", upcoming_items)
            with col4:
                st.metric("Overdue", due_items, delta=f"-{due_items}", delta_color="inverse")
            
            # Equipment type distribution - simplified for performance
            equipment_counts = {}
            for item in all_maintenance:
                eq_type = item.get('equipment_type', 'Other')
                equipment_counts[eq_type] = equipment_counts.get(eq_type, 0) + 1
            
            if equipment_counts:
                fig = px.pie(values=list(equipment_counts.values()), 
                            names=list(equipment_counts.keys()),
                            title="Equipment Type Distribution")
                st.plotly_chart(fig, use_container_width=True)
            
            # Export options
            st.subheader("📤 Export Data")
            if st.button("📥 Export to CSV", use_container_width=True):
                df = pd.DataFrame(all_maintenance)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv,
                    file_name=f"preventive_maintenance_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

# ========== UPDATED SPACE MANAGEMENT ==========

def show_space_management():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🏢 Space Management & Room Booking")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Only show View Bookings tab as requested
    tab1, tab2 = st.tabs(["📅 View Bookings", "➕ New Booking"])
    
    with tab1:
        st.subheader("📅 Current Bookings")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            room_filter = st.selectbox("Filter by Room Type", ["All", "Conference", "Meeting", "Cafeteria", "Other"], key="space_type")
        with col2:
            status_filter = st.selectbox("Filter by Status", ["All", "Confirmed", "Pending", "Cancelled"], key="space_status")
        with col3:
            date_filter = st.date_input("Filter by Date", value=datetime.now().date(), key="space_date")
        
        filters = {}
        if room_filter != "All":
            filters['room_type'] = room_filter
        if status_filter != "All":
            filters['status'] = status_filter
        if date_filter:
            filters['booking_date'] = date_filter
        
        # For regular users, show only their bookings
        if st.session_state.user['role'] in ['facility_user', 'hse_officer']:
            filters['booked_by'] = st.session_state.user['username']
        
        # Cache bookings data
        if 'bookings_data' not in st.session_state or st.button("🔄 Refresh Bookings"):
            bookings = get_space_bookings(filters)
            st.session_state.bookings_data = bookings
        else:
            bookings = st.session_state.bookings_data
        
        if not bookings:
            st.info("📭 No bookings found")
        else:
            # Display only 3 bookings as requested
            for booking in bookings[:3]:
                status = booking.get('status', 'Pending')
                status_class = {
                    'Confirmed': 'booking-confirmed',
                    'Pending': 'booking-pending',
                    'Cancelled': 'booking-cancelled'
                }.get(status, 'booking-pending')
                
                with st.expander(f"{booking['room_name']} - {booking['booking_date']} {booking['start_time']} to {booking['end_time']} ({status})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"""
                            <div class="card">
                                <p><strong>Purpose:</strong> {booking['purpose']}</p>
                                <p><strong>Department:</strong> {booking['department']}</p>
                                <p><strong>Attendees:</strong> {booking['attendees_count']}</p>
                                <p><strong>Catering Required:</strong> {'✅ Yes' if booking.get('catering_required') else '❌ No'}</p>
                            </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                            <div class="card">
                                <p><strong>Status:</strong> <span class="{status_class}">{status}</span></p>
                                <p><strong>Booked By:</strong> {booking['booked_by']}</p>
                                <p><strong>Room Type:</strong> {booking['room_type']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    if booking.get('special_requirements'):
                        st.markdown(f"""
                            <div class="card">
                                <p><strong>Special Requirements:</strong> {booking['special_requirements']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    # Action buttons for user's own bookings
                    if booking['booked_by'] == st.session_state.user['username'] and booking['status'] != 'Cancelled':
                        if st.button("❌ Cancel Booking", key=f"cancel_{booking['id']}"):
                            if execute_update('''
                                UPDATE space_bookings 
                                SET status = ?, last_modified = CURRENT_TIMESTAMP
                                WHERE id = ?
                            ''', ('Cancelled', booking['id'])):
                                # Clear cache for fresh data
                                if 'bookings_data' in st.session_state:
                                    del st.session_state.bookings_data
                                st.success("✅ Booking cancelled!")
                                st.rerun()
    
    with tab2:
        st.subheader("➕ Book a Room")
        
        with st.form("new_booking_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                room_type = st.selectbox("Room Type *", ["Conference", "Meeting", "Cafeteria"])
                room_name = st.selectbox("Room Name *", 
                                       ["Conference Room A", "Conference Room B", 
                                        "Meeting Room 1", "Meeting Room 2", 
                                        "Cafeteria"] if room_type != "Cafeteria" else ["Cafeteria"])
                booking_date = st.date_input("Booking Date *", value=datetime.now().date())
                start_time = st.time_input("Start Time *", value=datetime.strptime("09:00", "%H:%M").time())
                end_time = st.time_input("End Time *", value=datetime.strptime("12:00", "%H:%M").time())
            
            with col2:
                purpose = st.text_input("Purpose *", placeholder="e.g., Team meeting, Training session...")
                department = st.selectbox("Department *", 
                                        ["Management", "Operations", "Finance", "HR", 
                                         "IT", "Facilities", "HSE", "All"])
                attendees_count = st.number_input("Number of Attendees *", min_value=1, max_value=500, value=10)
                catering_required = st.checkbox("Catering Required")
                special_requirements = st.text_area("Special Requirements", 
                                                  placeholder="Audio/visual equipment, specific setup, etc.")
            
            # Check availability
            if room_name and booking_date and start_time and end_time:
                conflicting_bookings = execute_query('''
                    SELECT * FROM space_bookings 
                    WHERE room_name = ? 
                    AND booking_date = ?
                    AND status = 'Confirmed'
                    AND ((? < end_time AND ? > start_time) OR (? <= start_time AND ? >= end_time))
                ''', (room_name, booking_date.isoformat(), start_time.strftime("%H:%M"), end_time.strftime("%H:%M"), 
                      start_time.strftime("%H:%M"), end_time.strftime("%H:%M")))
                
                is_available = len(conflicting_bookings) == 0
                
                if not is_available:
                    st.error("❌ This room is already booked for the selected time slot!")
                else:
                    st.success("✅ This time slot is available!")
            
            submitted = st.form_submit_button("📅 Book Room", use_container_width=True)
            
            if submitted:
                if not all([room_type, room_name, booking_date, purpose, department, attendees_count]):
                    st.error("⚠️ Please fill in all required fields (*)")
                elif end_time <= start_time:
                    st.error("❌ End time must be after start time")
                elif not is_available:
                    st.error("❌ Room not available for selected time slot")
                else:
                    if execute_update('''
                        INSERT INTO space_bookings 
                        (room_name, room_type, booking_date, start_time, end_time, purpose, 
                         booked_by, department, attendees_count, catering_required, special_requirements)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (room_name, room_type, booking_date.isoformat(), 
                         start_time.strftime("%H:%M"), end_time.strftime("%H:%M"), 
                         purpose, st.session_state.user['username'],
                         department, attendees_count, catering_required, 
                         special_requirements)):
                        # Clear cache for fresh data
                        if 'bookings_data' in st.session_state:
                            del st.session_state.bookings_data
                        st.success("✅ Room booked successfully!")
                        st.rerun()

# ========== UPDATED HSE MANAGEMENT ==========

def show_hse_management():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🚨 HSE (Health, Safety & Environment) Management")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📅 HSE Schedule", "🚨 Incident Reports", "➕ New Inspection", "📊 Compliance Dashboard"])
    
    with tab1:
        st.subheader("📅 HSE Inspection Schedule")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox("Filter by Status", ["All", "Upcoming", "Completed", "Overdue"], key="hse_status")
        with col2:
            compliance_filter = st.selectbox("Filter by Compliance", ["All", "Compliant", "Non-Compliant"], key="hse_compliance")
        
        filters = {}
        if status_filter != "All":
            filters['status'] = status_filter
        if compliance_filter != "All":
            filters['compliance_level'] = compliance_filter
        
        # Cache HSE schedule data for performance
        with st.spinner("Loading HSE schedule..."):
            hse_schedule = get_hse_schedule(filters)
        
        if not hse_schedule:
            st.info("📭 No HSE inspections scheduled")
        else:
            # Display schedule with progress bar
            progress_bar = st.progress(0)
            for idx, item in enumerate(hse_schedule):
                next_date = safe_date(item.get('next_inspection_date'))
                status = item.get('status', 'Upcoming')
                
                # Determine if overdue
                if status != 'Completed' and next_date and next_date < datetime.now().date():
                    status = "Overdue"
                
                with st.expander(f"{item['inspection_type']} - {item['area']} ({status})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.write(f"**Inspection Type:** {item.get('inspection_type')}")
                        st.write(f"**Area:** {item.get('area')}")
                        st.write(f"**Frequency:** {item.get('frequency')}")
                        st.write(f"**Last Inspection:** {item.get('last_inspection_date', 'Never')}")
                        st.write(f"**Next Inspection:** {item.get('next_inspection_date')}")
                        st.write(f"**Assigned To:** {item.get('assigned_to')}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        compliance_level = item.get('compliance_level', 'Not Assessed')
                        compliance_class = 'hse-compliant' if compliance_level == 'Compliant' else 'hse-non-compliant'
                        
                        st.write(f"**Compliance Level:** <span class='{compliance_class}'>{compliance_level}</span>", unsafe_allow_html=True)
                        
                        if item.get('findings'):
                            st.write(f"**Findings:** {item.get('findings')}")
                        if item.get('corrective_actions'):
                            st.write(f"**Corrective Actions:** {item.get('corrective_actions')}")
                        if item.get('follow_up_date'):
                            st.write(f"**Follow-up Date:** {item.get('follow_up_date')}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Action buttons for HSE officers
                    if st.session_state.user['role'] in ['hse_officer', 'facility_manager'] and status != 'Completed':
                        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
                        with st.form(f"complete_inspection_{item['id']}"):
                            st.write("**✅ Complete Inspection**")
                            
                            compliance = st.selectbox("Compliance Level", ["Compliant", "Non-Compliant"], 
                                                    key=f"comp_{item['id']}")
                            findings = st.text_area("Findings", key=f"find_{item['id']}")
                            corrective_actions = st.text_area("Corrective Actions", key=f"corr_{item['id']}")
                            follow_up_date = st.date_input("Follow-up Date", 
                                                          value=datetime.now().date() + timedelta(days=30),
                                                          key=f"follow_{item['id']}")
                            
                            if st.form_submit_button("✅ Mark as Completed"):
                                today = datetime.now().date()
                                if execute_update('''
                                    UPDATE hse_schedule 
                                    SET status = 'Completed',
                                        last_inspection_date = ?,
                                        compliance_level = ?,
                                        findings = ?,
                                        corrective_actions = ?,
                                        follow_up_date = ?
                                    WHERE id = ?
                                ''', (today.isoformat(), compliance, findings, corrective_actions, 
                                      follow_up_date.isoformat() if follow_up_date else None, item['id'])):
                                    st.success("✅ Inspection completed!")
                                    st.rerun()
                
                progress_bar.progress((idx + 1) / len(hse_schedule))
            
            progress_bar.empty()
        
        # Overdue inspections alert
        overdue_inspections = [i for i in hse_schedule if i.get('status') != 'Completed' 
                              and safe_date(i.get('next_inspection_date')) 
                              and safe_date(i.get('next_inspection_date')) < datetime.now().date()]
        
        if overdue_inspections:
            st.markdown('<div class="alert-danger">', unsafe_allow_html=True)
            st.error(f"⚠️ **CRITICAL:** {len(overdue_inspections)} HSE inspection(s) overdue!")
            for item in overdue_inspections[:3]:  # Show only 3
                st.write(f"• {item.get('inspection_type')} at {item.get('area')} (Due: {item.get('next_inspection_date')})")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.subheader("🚨 Incident Reports")
        
        # Filters for incidents
        col1, col2 = st.columns(2)
        with col1:
            severity_filter = st.selectbox("Filter by Severity", ["All", "Low", "Medium", "High", "Critical"], key="incident_severity")
        with col2:
            status_filter = st.selectbox("Filter by Status", ["All", "Open", "Under Investigation", "Closed"], key="incident_status")
        
        filters = {}
        if severity_filter != "All":
            filters['severity'] = severity_filter
        if status_filter != "All":
            filters['status'] = status_filter
        
        # Cache incidents data with progress indicator
        with st.spinner("Loading incident reports..."):
            incidents = get_hse_incidents(filters)
        
        if not incidents:
            st.info("📭 No incident reports found")
        else:
            # Display incidents with pagination concept
            page_size = 5
            if 'incident_page' not in st.session_state:
                st.session_state.incident_page = 0
            
            total_pages = (len(incidents) - 1) // page_size + 1
            
            # Show page navigation
            if total_pages > 1:
                col_nav1, col_nav2, col_nav3 = st.columns([1, 2, 1])
                with col_nav1:
                    if st.button("⬅️ Previous", disabled=st.session_state.incident_page == 0):
                        st.session_state.incident_page -= 1
                        st.rerun()
                with col_nav2:
                    st.write(f"Page {st.session_state.incident_page + 1} of {total_pages}")
                with col_nav3:
                    if st.button("Next ➡️", disabled=st.session_state.incident_page == total_pages - 1):
                        st.session_state.incident_page += 1
                        st.rerun()
            
            start_idx = st.session_state.incident_page * page_size
            end_idx = min(start_idx + page_size, len(incidents))
            
            for incident in incidents[start_idx:end_idx]:
                severity = incident.get('severity', 'Medium')
                severity_color = {
                    'Critical': '#C62828',
                    'High': '#EF6C00',
                    'Medium': '#FFC107',
                    'Low': '#4CAF50'
                }.get(severity, '#FFC107')
                
                with st.expander(f"Incident #{incident['id']}: {incident['incident_type']} ({severity})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.write(f"**Date & Time:** {incident['incident_date']} {incident['incident_time']}")
                        st.write(f"**Location:** {incident['location']}")
                        st.write(f"**Type:** {incident['incident_type']}")
                        st.write(f"**Severity:** <span style='color:{severity_color}; font-weight:bold;'>{severity}</span>", unsafe_allow_html=True)
                        st.write(f"**Reported By:** {incident['reported_by']}")
                        if incident.get('affected_persons'):
                            st.write(f"**Affected Persons:** {incident.get('affected_persons')}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.write(f"**Description:** {incident['description']}")
                        if incident.get('immediate_actions'):
                            st.write(f"**Immediate Actions:** {incident['immediate_actions']}")
                        st.write(f"**Investigation Status:** {incident.get('investigation_status', 'Open')}")
                        st.write(f"**Status:** {incident.get('status', 'Open')}")
                        if incident.get('corrective_measures'):
                            st.write(f"**Corrective Measures:** {incident.get('corrective_measures')}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Action buttons for HSE officers
                    if st.session_state.user['role'] in ['hse_officer', 'facility_manager']:
                        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
                        with st.form(f"update_incident_{incident['id']}"):
                            st.write("**🔄 Update Incident Status**")
                            
                            investigation_status = st.selectbox("Investigation Status", 
                                                              ["Open", "Under Investigation", "Resolved"],
                                                              key=f"inv_{incident['id']}")
                            corrective_measures = st.text_area("Corrective Measures", 
                                                             value=incident.get('corrective_measures', ''),
                                                             key=f"cm_{incident['id']}")
                            status = st.selectbox("Status", ["Open", "Closed"], 
                                                key=f"stat_{incident['id']}")
                            
                            if st.form_submit_button("💾 Update Incident"):
                                if execute_update('''
                                    UPDATE hse_incidents 
                                    SET investigation_status = ?,
                                        corrective_measures = ?,
                                        status = ?
                                    WHERE id = ?
                                ''', (investigation_status, corrective_measures, status, incident['id'])):
                                    st.success("✅ Incident updated!")
                                    st.rerun()
    
    with tab3:
        st.subheader("➕ Schedule New Inspection")
        
        if st.session_state.user['role'] in ['hse_officer', 'facility_manager']:
            with st.form("new_inspection_schedule"):
                col1, col2 = st.columns(2)
                
                with col1:
                    inspection_type = st.selectbox("Inspection Type *", 
                                                 ["Fire Safety Inspection", "First Aid Kit Check", 
                                                  "Emergency Exit Inspection", "Electrical Safety Check",
                                                  "PPE Inspection", "Workplace Safety Audit", "Other"])
                    area = st.text_input("Area *", placeholder="e.g., Main Building, Generator Room...")
                    frequency = st.selectbox("Frequency *", ["Daily", "Weekly", "Monthly", "Quarterly", "Annual"])
                
                with col2:
                    next_inspection_date = st.date_input("Next Inspection Date *", 
                                                        value=datetime.now().date() + timedelta(days=7))
                    assigned_to = st.text_input("Assigned To *", value=st.session_state.user['username'])
                
                submitted = st.form_submit_button("📅 Schedule Inspection", use_container_width=True)
                
                if submitted:
                    if not all([inspection_type, area, frequency, next_inspection_date, assigned_to]):
                        st.error("⚠️ Please fill in all required fields (*)")
                    else:
                        if execute_update('''
                            INSERT INTO hse_schedule 
                            (inspection_type, area, frequency, next_inspection_date, assigned_to)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (inspection_type, area, frequency, next_inspection_date.isoformat(), assigned_to)):
                            st.success("✅ Inspection scheduled successfully!")
                            st.rerun()
        else:
            st.info("🔒 Only HSE officers and facility managers can schedule new inspections")
    
    with tab4:
        st.subheader("📊 HSE Compliance Dashboard")
        
        # Get all HSE data with caching
        with st.spinner("Loading compliance data..."):
            all_inspections = get_hse_schedule()
            all_incidents = get_hse_incidents()
        
        if all_inspections:
            # Compliance statistics
            total_inspections = len(all_inspections)
            completed_inspections = len([i for i in all_inspections if i.get('status') == 'Completed'])
            compliant_inspections = len([i for i in all_inspections if i.get('compliance_level') == 'Compliant'])
            overdue_inspections = len([i for i in all_inspections if i.get('status') != 'Completed' 
                                     and safe_date(i.get('next_inspection_date')) 
                                     and safe_date(i.get('next_inspection_date')) < datetime.now().date()])
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Inspections", total_inspections)
            with col2:
                st.metric("Completed", completed_inspections)
            with col3:
                st.metric("Compliant", compliant_inspections)
            with col4:
                st.metric("Overdue", overdue_inspections, delta=f"-{overdue_inspections}", delta_color="inverse")
            
            # Compliance rate
            compliance_rate = (compliant_inspections / completed_inspections * 100) if completed_inspections > 0 else 0
            st.progress(compliance_rate / 100, text=f"Overall Compliance Rate: {compliance_rate:.1f}%")
            
            # Export options
            st.subheader("📤 Export Reports")
            col_exp1, col_exp2 = st.columns(2)
            
            with col_exp1:
                if st.button("📥 Export Inspection Data", use_container_width=True):
                    df = pd.DataFrame(all_inspections)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Download CSV",
                        data=csv,
                        file_name=f"hse_inspections_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            
            with col_exp2:
                if all_incidents and st.button("📥 Export Incident Data", use_container_width=True):
                    df = pd.DataFrame(all_incidents)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Download CSV",
                        data=csv,
                        file_name=f"hse_incidents_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )

# ========== MAIN APP WITH UPDATED NAVIGATION ==========

def show_main_app():
    user = st.session_state.user
    role = user['role']
    
    st.markdown(f"""
        <div class="header-container">
            <h1 style="margin: 0; display: flex; align-items: center; gap: 10px;">
                🏢 FACILITIES MANAGEMENT SYSTEM™
                <span style="font-size: 14px; background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 10px;">
                    v3.0
                </span>
            </h1>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">
                Welcome, <strong>{user['username']}</strong> | Role: {role.replace('_', ' ').title()} | 
                Currency: Nigerian Naira (₦) | © 2024 Developed by Abdulahi Ibrahim
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
        
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                <p style="margin: 0;"><strong>Role:</strong> {role.replace('_', ' ').title()}</p>
                {f'<p style="margin: 0;"><strong>Vendor Type:</strong> {user["vendor_type"]}</p>' if user.get('vendor_type') else ''}
                <p style="margin: 0;"><strong>Currency:</strong> Nigerian Naira (₦)</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
        
        # Navigation menu based on role
        if role == 'facility_user':
            menu_options = ["Dashboard", "Create Request", "My Requests", 
                          "Space Management", "Generator Records", "HSE Management"]
        elif role == 'facility_manager':
            menu_options = ["Dashboard", "Manage Requests", "Vendor Management", 
                          "Reports", "Job & Invoice Reports", "Preventive Maintenance",
                          "Space Management", "Generator Records", "HSE Management"]
        elif role == 'hse_officer':
            menu_options = ["Dashboard", "HSE Management"]
        elif role == 'space_manager':
            menu_options = ["Dashboard", "Space Management"]
        else:  # vendor
            menu_options = ["Dashboard", "Assigned Jobs", "Completed Jobs", 
                          "Vendor Registration", "Invoice Creation"]
        
        # Initialize navigation_menu in session state if not exists
        if 'navigation_menu' not in st.session_state:
            st.session_state.navigation_menu = "Dashboard"
        
        selected_menu = st.radio("🗺️ Navigation", menu_options, 
                               key="navigation_menu_radio", 
                               index=menu_options.index(st.session_state.navigation_menu)
                               if st.session_state.navigation_menu in menu_options else 0,
                               label_visibility="collapsed")
        
        # Update session state
        st.session_state.navigation_menu = selected_menu
        
        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
        
        # Fixed logout button
        if st.button("🚪 Logout", type="secondary", use_container_width=True, key="logout_button"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        # Simple copyright footer
        st.markdown("""
            <div style="margin-top: 30px; padding: 10px; text-align: center; font-size: 10px; color: rgba(255,255,255,0.6);">
                <hr style="margin: 10px 0;">
                © 2024 FMS™ v3.0<br>
                All Rights Reserved
            </div>
        """, unsafe_allow_html=True)
    
    # Route to the selected menu
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
    elif selected_menu == "Job & Invoice Reports":
        show_job_invoice_reports()
    elif selected_menu == "Assigned Jobs":
        show_assigned_jobs()
    elif selected_menu == "Completed Jobs":
        show_completed_jobs()
    elif selected_menu == "Vendor Registration":
        show_vendor_registration()
    elif selected_menu == "Invoice Creation":
        show_invoice_creation()
    elif selected_menu == "Preventive Maintenance":
        show_preventive_maintenance()
    elif selected_menu == "Space Management":
        show_space_management()
    elif selected_menu == "Generator Records":
        show_generator_diesel_records()
    elif selected_menu == "HSE Management":
        show_hse_management()

# ========== MAIN FUNCTION ==========

def main():
    # Initialize session state for user if not exists
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    if st.session_state.user is None:
        show_login()
    else:
        show_main_app()

if __name__ == "__main__":
    # Initialize fresh database
    init_database()
    
    # Run the app
    main()
