import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
import time

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
    
    /* Quick action buttons */
    .quick-action-btn {
        background: linear-gradient(45deg, #2196F3, #1976D2) !important;
        color: white !important;
        border: none;
        padding: 15px !important;
        border-radius: 10px;
        font-weight: bold;
        font-size: 14px;
        transition: all 0.3s ease;
        height: 100px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    .quick-action-btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(33, 150, 243, 0.3) !important;
    }
    
    .quick-action-btn span {
        font-size: 24px;
        margin-bottom: 8px;
    }
    
    /* Animation for success messages */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .success-message {
        animation: fadeIn 0.5s ease-in-out;
        background: linear-gradient(45deg, #4CAF50, #2E7D32);
        color: white;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ========== DATABASE SETUP ==========

def init_database():
    """Initialize database with all tables and sample data"""
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
    
    # Insert sample users if not exists
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
    
    # Insert sample preventive maintenance data
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
    
    # Insert sample generator records
    for i in range(3):
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
    
    # Insert sample space bookings
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
    
    # Insert sample HSE schedule
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

# ========== DATABASE FUNCTIONS ==========

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
@st.cache_data(ttl=300)
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

# ========== NEW FEATURES FUNCTIONS ==========

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

def add_preventive_maintenance(equipment_name, equipment_type, location, maintenance_type, 
                              frequency, last_maintenance_date, next_maintenance_date, assigned_to, notes):
    return execute_update('''
        INSERT INTO preventive_maintenance 
        (equipment_name, equipment_type, location, maintenance_type, frequency, 
         last_maintenance_date, next_maintenance_date, assigned_to, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (equipment_name, equipment_type, location, maintenance_type, frequency,
          last_maintenance_date.isoformat() if last_maintenance_date else None, 
          next_maintenance_date.isoformat(), assigned_to, notes))

# Generator Records Functions - FIXED ADD FUNCTION
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

def add_generator_record(record_date, generator_name, opening_hours, closing_hours, 
                        opening_diesel_level, closing_diesel_level, recorded_by, notes):
    if closing_hours < opening_hours:
        return False, "Closing hours cannot be less than opening hours"
    
    if opening_diesel_level < 0 or closing_diesel_level < 0:
        return False, "Diesel levels cannot be negative"
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO generator_records 
            (record_date, generator_name, opening_hours, closing_hours, 
             opening_diesel_level, closing_diesel_level, recorded_by, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (record_date.isoformat(), generator_name, opening_hours, closing_hours,
              opening_diesel_level, closing_diesel_level, recorded_by, notes))
        conn.commit()
        return True, "Record saved successfully"
    except Exception as e:
        return False, f"Failed to save record: {str(e)}"

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

def add_space_booking(room_name, room_type, booking_date, start_time, end_time, purpose,
                     booked_by, department, attendees_count, catering_required, special_requirements):
    return execute_update('''
        INSERT INTO space_bookings 
        (room_name, room_type, booking_date, start_time, end_time, purpose, 
         booked_by, department, attendees_count, catering_required, special_requirements)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (room_name, room_type, booking_date.isoformat(), start_time, end_time, purpose,
          booked_by, department, attendees_count, catering_required, special_requirements))

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

def add_hse_schedule(inspection_type, area, frequency, next_inspection_date, assigned_to):
    return execute_update('''
        INSERT INTO hse_schedule 
        (inspection_type, area, frequency, next_inspection_date, assigned_to)
        VALUES (?, ?, ?, ?, ?)
    ''', (inspection_type, area, frequency, next_inspection_date.isoformat(), assigned_to))

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

def add_hse_incident(incident_date, incident_time, location, incident_type, severity, 
                    description, reported_by, affected_persons, immediate_actions):
    return execute_update('''
        INSERT INTO hse_incidents 
        (incident_date, incident_time, location, incident_type, severity, 
         description, reported_by, affected_persons, immediate_actions)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (incident_date.isoformat(), incident_time, location, incident_type, severity,
          description, reported_by, affected_persons, immediate_actions))

# Authentication
def authenticate_user(username, password):
    users = execute_query('SELECT * FROM users WHERE username = ? AND password_hash = ?', (username, password))
    return users[0] if users else None

# ========== ENHANCED PDF REPORT GENERATION ==========

def generate_job_invoice_pdf(job_data, invoice_data=None):
    """Generate a professional PDF report for job and invoice"""
    buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#283593'),
        spaceAfter=20,
        alignment=TA_LEFT
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=12
    )
    
    # Build the story (content)
    story = []
    
    # Title
    story.append(Paragraph("FACILITIES MANAGEMENT SYSTEM", title_style))
    story.append(Paragraph("Job Completion & Invoice Report", styles['Title']))
    story.append(Spacer(1, 20))
    
    # Report details
    story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    story.append(Spacer(1, 20))
    
    # Job Details Section
    story.append(Paragraph("JOB DETAILS", subtitle_style))
    
    job_details_data = [
        ["Job ID:", f"#{job_data.get('id', 'N/A')}"],
        ["Title:", job_data.get('title', 'N/A')],
        ["Location:", job_data.get('location', 'Common Area')],
        ["Facility Type:", job_data.get('facility_type', 'N/A')],
        ["Priority:", job_data.get('priority', 'N/A')],
        ["Status:", job_data.get('status', 'N/A')],
        ["Created By:", job_data.get('created_by', 'N/A')],
        ["Assigned Vendor:", job_data.get('assigned_vendor', 'Not assigned')],
        ["Created Date:", job_data.get('created_date', 'N/A')],
        ["Completed Date:", job_data.get('completed_date', 'N/A')]
    ]
    
    job_table = Table(job_details_data, colWidths=[200, 300])
    job_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#424242')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0'))
    ]))
    
    story.append(job_table)
    story.append(Spacer(1, 20))
    
    # Job Description
    story.append(Paragraph("DESCRIPTION", subtitle_style))
    description = job_data.get('description', 'No description provided')
    story.append(Paragraph(description, normal_style))
    story.append(Spacer(1, 20))
    
    # Job Breakdown if exists
    if job_data.get('job_breakdown'):
        story.append(Paragraph("WORK PERFORMED", subtitle_style))
        breakdown = job_data.get('job_breakdown')
        story.append(Paragraph(breakdown, normal_style))
        story.append(Spacer(1, 20))
    
    # Completion Notes if exists
    if job_data.get('completion_notes'):
        story.append(Paragraph("COMPLETION NOTES", subtitle_style))
        notes = job_data.get('completion_notes')
        story.append(Paragraph(notes, normal_style))
        story.append(Spacer(1, 20))
    
    # If we have invoice data, add invoice section
    if invoice_data:
        story.append(PageBreak())
        
        # Invoice Header
        story.append(Paragraph("INVOICE DETAILS", title_style))
        story.append(Spacer(1, 20))
        
        # Invoice Information
        invoice_info_data = [
            ["Invoice Number:", invoice_data.get('invoice_number', 'N/A')],
            ["Invoice Date:", invoice_data.get('invoice_date', 'N/A')],
            ["Vendor:", invoice_data.get('vendor_username', 'N/A')],
            ["Status:", invoice_data.get('status', 'N/A')],
            ["Currency:", invoice_data.get('currency', '₦')]
        ]
        
        invoice_info_table = Table(invoice_info_data, colWidths=[200, 300])
        invoice_info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#424242')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0'))
        ]))
        
        story.append(invoice_info_table)
        story.append(Spacer(1, 20))
        
        # Work Details
        story.append(Paragraph("WORK DETAILS", subtitle_style))
        work_details = invoice_data.get('details_of_work', 'No details provided')
        story.append(Paragraph(work_details, normal_style))
        story.append(Spacer(1, 20))
        
        # Cost Breakdown
        story.append(Paragraph("COST BREAKDOWN", subtitle_style))
        
        quantity = invoice_data.get('quantity', 1)
        unit_cost = safe_float(invoice_data.get('unit_cost', 0))
        amount = safe_float(invoice_data.get('amount', 0))
        labour_charge = safe_float(invoice_data.get('labour_charge', 0))
        vat_applicable = invoice_data.get('vat_applicable', False)
        vat_amount = safe_float(invoice_data.get('vat_amount', 0))
        total_amount = safe_float(invoice_data.get('total_amount', 0))
        
        cost_data = [
            ["Description", "Quantity", "Unit Cost", "Amount"],
            ["Main Work", str(quantity), format_naira(unit_cost), format_naira(amount)]
        ]
        
        if labour_charge > 0:
            cost_data.append(["Labour/Service Charge", "1", format_naira(labour_charge), format_naira(labour_charge)])
        
        subtotal = amount + labour_charge
        cost_data.append(["", "", "Subtotal:", format_naira(subtotal)])
        
        if vat_applicable:
            cost_data.append(["", "", "VAT (7.5%):", format_naira(vat_amount)])
        
        cost_data.append(["", "", "TOTAL AMOUNT:", f"<b>{format_naira(total_amount)}</b>"])
        
        cost_table = Table(cost_data, colWidths=[200, 80, 100, 120])
        cost_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#4CAF50')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (-2, -1), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -2), 1, colors.HexColor('#e0e0e0')),
            ('LINEABOVE', (-2, -1), (-1, -1), 2, colors.white)
        ]))
        
        story.append(cost_table)
    
    # Footer
    story.append(Spacer(1, 40))
    story.append(Paragraph(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, 
                                       textColor=colors.gray, alignment=TA_CENTER)))
    story.append(Paragraph("Facilities Management System v3.0 © 2024", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, 
                                       textColor=colors.gray, alignment=TA_CENTER)))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

# ========== LOGIN PAGE ==========

def show_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        st.markdown('<h1 class="login-title">🏢 FACILITIES MANAGEMENT SYSTEM™</h1>', unsafe_allow_html=True)
        st.markdown('<h3 style="text-align: center; color: rgba(255,255,255,0.9);">Secure Login Portal</h3>', unsafe_allow_html=True)
        
        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=True):
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
                        st.session_state.navigation_menu = "Dashboard"
                        st.success("Login successful! Redirecting...")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.warning("⚠️ Please enter both username and password")
        
        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
        
        st.markdown('<div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin-top: 20px;">', unsafe_allow_html=True)
        st.markdown('<h4 style="color: white;">📋 Sample Credentials</h4>', unsafe_allow_html=True)
        
        credentials = """
        👥 **Facility User:** 
        • Username: facility_user
        • Password: 0123456
        
        👨‍💼 **Facility Manager:** 
        • Username: facility_manager
        • Password: 0123456
        
        🚨 **HSE Officer:** 
        • Username: hse_officer
        • Password: 0123456
        
        🏢 **Space Manager:** 
        • Username: space_manager
        • Password: 0123456
        
        🏢 **Vendors:**
        • HVAC Solutions: hvac_vendor / 0123456
        • Generator Pros: generator_vendor / 0123456
        """
        st.code(credentials, language=None)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ========== DASHBOARD WITH WORKING QUICK ACTIONS ==========

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
    elif role == 'vendor':
        show_vendor_dashboard()
    else:
        st.warning("Unknown role")

def show_user_dashboard():
    user_requests = get_user_requests(st.session_state.user['username'])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<h4>Total Requests</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3>{len(user_requests)}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        pending_count = len([r for r in user_requests if safe_get(r, 'status') == 'Pending'])
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<h4>Pending</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3>{pending_count}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        completed_count = len([r for r in user_requests if safe_get(r, 'status') == 'Completed'])
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<h4>Completed</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3>{completed_count}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # WORKING QUICK ACCESS BUTTONS
    st.subheader("🚀 Quick Access")
    
    col_q1, col_q2, col_q3 = st.columns(3)
    
    with col_q1:
        if st.button("📅 Book a Room", key="quick_book_room", use_container_width=True):
            st.session_state.navigation_menu = "Space Management"
            st.rerun()
    
    with col_q2:
        if st.button("⛽ Generator Records", key="quick_generator", use_container_width=True):
            st.session_state.navigation_menu = "Generator Records"
            st.rerun()
    
    with col_q3:
        if st.button("🚨 Report Incident", key="quick_incident", use_container_width=True):
            st.session_state.navigation_menu = "HSE Management"
            st.rerun()
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📋 Recent Requests")
    if user_requests:
        display_data = []
        for req in user_requests[:5]:
            display_data.append({
                'ID': safe_get(req, 'id'),
                'Title': safe_str(safe_get(req, 'title'), 'N/A'),
                'Location': safe_str(safe_get(req, 'location'), 'Common Area'),
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
        pending_count = len([r for r in all_requests if safe_get(r, 'status') == 'Pending'])
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<h4>Pending</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3>{pending_count}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        assigned_count = len([r for r in all_requests if safe_get(r, 'status') == 'Assigned'])
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<h4>Assigned</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3>{assigned_count}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        completed_count = len([r for r in all_requests if safe_get(r, 'status') == 'Completed'])
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<h4>Completed</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3>{completed_count}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # WORKING QUICK ACCESS BUTTONS FOR MANAGERS
    st.subheader("🚀 Management Quick Access")
    
    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
    
    with col_q1:
        if st.button("📅 Maintenance Schedule", key="quick_maintenance", use_container_width=True):
            st.session_state.navigation_menu = "Preventive Maintenance"
            st.rerun()
    
    with col_q2:
        if st.button("🏢 Space Management", key="quick_space", use_container_width=True):
            st.session_state.navigation_menu = "Space Management"
            st.rerun()
    
    with col_q3:
        if st.button("🚨 HSE Dashboard", key="quick_hse", use_container_width=True):
            st.session_state.navigation_menu = "HSE Management"
            st.rerun()
    
    with col_q4:
        if st.button("⛽ Generator Reports", key="quick_gen_reports", use_container_width=True):
            st.session_state.navigation_menu = "Generator Records"
            st.rerun()
    
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
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📋 Recent Requests")
    if all_requests:
        display_data = []
        for req in all_requests[:5]:
            display_data.append({
                'ID': safe_get(req, 'id'),
                'Title': safe_str(safe_get(req, 'title'), 'N/A'),
                'Location': safe_str(safe_get(req, 'location'), 'Common Area'),
                'Facility': safe_str(safe_get(req, 'facility_type'), 'N/A'),
                'Priority': safe_str(safe_get(req, 'priority'), 'N/A'),
                'Status': safe_str(safe_get(req, 'status'), 'N/A'),
                'Created By': safe_str(safe_get(req, 'created_by'), 'N/A')
            })
        
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("📭 No maintenance requests found")
    st.markdown('</div>', unsafe_allow_html=True)

def show_hse_dashboard():
    st.subheader("🚨 HSE Officer Dashboard")
    
    hse_schedule_data = get_hse_schedule()
    hse_incidents = get_hse_incidents()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<h4>Total Inspections</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3>{len(hse_schedule_data)}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        overdue = len([i for i in hse_schedule_data if i.get('status') != 'Completed' 
                      and safe_date(i.get('next_inspection_date')) 
                      and safe_date(i.get('next_inspection_date')) < datetime.now().date()])
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<h4>Overdue Inspections</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3 style="color: #F44336;">{overdue}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<h4>Total Incidents</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3>{len(hse_incidents)}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        open_incidents = len([i for i in hse_incidents if i.get('status') == 'Open'])
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<h4>Open Incidents</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3 style="color: #FF9800;">{open_incidents}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    
    col_q1, col_q2, col_q3 = st.columns(3)
    
    with col_q1:
        if st.button("➕ Schedule Inspection", key="hse_schedule_inspection", use_container_width=True):
            st.session_state.navigation_menu = "HSE Management"
            st.rerun()
    
    with col_q2:
        if st.button("🚨 Report Incident", key="hse_report_incident", use_container_width=True):
            st.session_state.navigation_menu = "HSE Management"
            st.rerun()
    
    with col_q3:
        if st.button("📊 View Compliance", key="hse_view_compliance", use_container_width=True):
            st.session_state.navigation_menu = "HSE Management"
            st.rerun()
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

def show_space_dashboard():
    st.subheader("🏢 Space Manager Dashboard")
    
    bookings = get_space_bookings()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<h4>Total Bookings</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3>{len(bookings)}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        today_bookings = len([b for b in bookings if b.get('booking_date') == datetime.now().date().isoformat()])
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<h4>Today\'s Bookings</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3>{today_bookings}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        confirmed_bookings = len([b for b in bookings if b.get('status') == 'Confirmed'])
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<h4>Confirmed</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3>{confirmed_bookings}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    
    col_q1, col_q2 = st.columns(2)
    
    with col_q1:
        if st.button("➕ New Booking", key="space_new_booking", use_container_width=True):
            st.session_state.navigation_menu = "Space Management"
            st.rerun()
    
    with col_q2:
        if st.button("📅 View All Bookings", key="space_view_bookings", use_container_width=True):
            st.session_state.navigation_menu = "Space Management"
            st.rerun()
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

def show_vendor_dashboard():
    st.subheader("🔧 Vendor Dashboard")
    
    vendor_requests = get_vendor_requests(st.session_state.user['username'])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        assigned_count = len([r for r in vendor_requests if safe_get(r, 'status') == 'Assigned'])
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<h4>Assigned Jobs</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3>{assigned_count}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        completed_count = len([r for r in vendor_requests if safe_get(r, 'status') == 'Completed'])
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<h4>Completed Jobs</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3>{completed_count}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<h4>Total Jobs</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3>{len(vendor_requests)}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# ========== GENERATOR RECORDS - FIXED ADD FUNCTION ==========

def show_generator_diesel_records():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("⛽ Generator & Diesel Daily Records")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📝 Daily Records", "➕ New Record", "📈 Reports & Analysis"])
    
    with tab1:
        st.subheader("📅 Daily Generator Records")
        
        # Date range filter
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=datetime.now().date() - timedelta(days=7), key="gen_start_date")
        with col2:
            end_date = st.date_input("End Date", value=datetime.now().date(), key="gen_end_date")
        
        if st.button("🔄 Refresh Records", key="refresh_generator"):
            st.cache_data.clear()
            st.rerun()
        
        records = get_generator_records(start_date, end_date)
        
        if not records:
            st.info("📭 No records found for the selected date range")
        else:
            display_data = []
            total_hours = 0
            total_diesel = 0
            
            for record in records[:5]:  # Show 5 records
                net_hours = safe_float(record.get('net_hours_used', 0))
                diesel_consumed = safe_float(record.get('diesel_consumed', 0))
                
                display_data.append({
                    'Date': record.get('record_date'),
                    'Generator': record.get('generator_name'),
                    'Opening Hours': f"{safe_float(record.get('opening_hours', 0)):.1f}",
                    'Closing Hours': f"{safe_float(record.get('closing_hours', 0)):.1f}",
                    'Net Hours': f"{net_hours:.1f}",
                    'Opening Diesel': f"{safe_float(record.get('opening_diesel_level', 0)):.1f} L",
                    'Closing Diesel': f"{safe_float(record.get('closing_diesel_level', 0)):.1f} L",
                    'Diesel Consumed': f"{diesel_consumed:.1f} L",
                    'Recorded By': record.get('recorded_by')
                })
                
                total_hours += net_hours
                total_diesel += diesel_consumed
            
            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Summary statistics
            st.subheader("📊 Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Records", len(records))
            with col2:
                st.metric("Total Hours", f"{total_hours:.1f}")
            with col3:
                st.metric("Total Diesel Used", f"{total_diesel:.1f} L")
    
    with tab2:
        st.subheader("➕ Add New Daily Record")
        
        with st.form("add_generator_record", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                record_date = st.date_input("Record Date *", value=datetime.now().date(), key="gen_record_date")
                generator_name = st.selectbox("Generator Name *", ["Generator #1", "Generator #2", "Generator #3"], key="gen_name")
                opening_hours = st.number_input("Opening Hours *", min_value=0.0, step=0.1, format="%.1f", key="gen_opening_hours", value=0.0)
                closing_hours = st.number_input("Closing Hours *", min_value=0.0, step=0.1, format="%.1f", key="gen_closing_hours", value=0.0)
            
            with col2:
                opening_diesel_level = st.number_input("Opening Diesel Level (L) *", min_value=0.0, step=0.1, format="%.1f", key="gen_opening_diesel", value=0.0)
                closing_diesel_level = st.number_input("Closing Diesel Level (L) *", min_value=0.0, step=0.1, format="%.1f", key="gen_closing_diesel", value=0.0)
                recorded_by = st.text_input("Recorded By *", value=st.session_state.user['username'], key="gen_recorded_by")
                notes = st.text_area("Notes", key="gen_notes")
            
            # Calculate preview
            net_hours = closing_hours - opening_hours if closing_hours > opening_hours else 0
            diesel_consumed = opening_diesel_level - closing_diesel_level if opening_diesel_level > closing_diesel_level else 0
            
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write("**📊 Preview**")
            col_preview1, col_preview2 = st.columns(2)
            with col_preview1:
                st.write(f"**Net Hours Used:** {net_hours:.1f}")
            with col_preview2:
                st.write(f"**Diesel Consumed:** {diesel_consumed:.1f} L")
            st.markdown('</div>', unsafe_allow_html=True)
            
            submitted = st.form_submit_button("💾 Save Record", use_container_width=True, key="gen_submit")
            
            if submitted:
                if not all([record_date, generator_name, recorded_by]):
                    st.error("⚠️ Please fill in all required fields (*)")
                elif closing_hours < opening_hours:
                    st.error("❌ Closing hours cannot be less than opening hours")
                elif opening_diesel_level < 0 or closing_diesel_level < 0:
                    st.error("❌ Diesel levels cannot be negative")
                else:
                    success, message = add_generator_record(record_date, generator_name, opening_hours, closing_hours,
                                          opening_diesel_level, closing_diesel_level, recorded_by, notes)
                    if success:
                        st.success("✅ " + message)
                        # Clear cache for fresh data
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("❌ " + message)
    
    with tab3:
        st.subheader("📈 Analysis & Reports")
        
        # Get summary data
        summary = get_generator_summary()
        
        if summary:
            for gen in summary:
                st.markdown(f'<div class="card">', unsafe_allow_html=True)
                st.write(f"**{gen['generator_name']}**")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Days Operated", int(gen['total_days']))
                with col2:
                    st.metric("Total Hours", f"{safe_float(gen['total_hours']):.1f}")
                with col3:
                    st.metric("Total Diesel", f"{safe_float(gen['total_diesel']):.1f} L")
                with col4:
                    st.metric("Avg Daily Hours", f"{safe_float(gen['avg_hours_per_day']):.1f}")
                st.markdown('</div>', unsafe_allow_html=True)

# ========== ENHANCED REPORTS WITH GRAPHICAL ANALYTICS ==========

def show_reports():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("📈 Reports & Analytics")
    st.markdown('</div>', unsafe_allow_html=True)
    
    all_requests = get_all_requests()
    
    if not all_requests:
        st.info("📭 No data available for reports")
        return
    
    # Convert to DataFrame for analysis
    report_data = []
    for req in all_requests:
        report_data.append({
            'id': safe_get(req, 'id'),
            'title': safe_str(safe_get(req, 'title'), 'N/A'),
            'location': safe_str(safe_get(req, 'location'), 'Common Area'),
            'facility_type': safe_str(safe_get(req, 'facility_type'), 'N/A'),
            'priority': safe_str(safe_get(req, 'priority'), 'N/A'),
            'status': safe_str(safe_get(req, 'status'), 'N/A'),
            'created_by': safe_str(safe_get(req, 'created_by'), 'N/A'),
            'assigned_vendor': safe_str(safe_get(req, 'assigned_vendor'), 'Not assigned'),
            'created_date': safe_str(safe_get(req, 'created_date'), 'N/A'),
            'completed_date': safe_str(safe_get(req, 'completed_date'), ''),
            'invoice_amount': safe_float(safe_get(req, 'invoice_amount'))
        })
    
    df = pd.DataFrame(report_data)
    
    if not df.empty:
        df['created_date'] = pd.to_datetime(df['created_date'], errors='coerce')
        df['completed_date'] = pd.to_datetime(df['completed_date'], errors='coerce')
        df['month'] = df['created_date'].dt.to_period('M')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_requests = len(df)
        st.markdown(f'<div class="metric-card"><h4>Total Requests</h4><h3>{total_requests}</h3></div>', unsafe_allow_html=True)
    
    with col2:
        completed_requests = len(df[df['status'] == 'Completed'])
        st.markdown(f'<div class="metric-card"><h4>Completed</h4><h3>{completed_requests}</h3></div>', unsafe_allow_html=True)
    
    with col3:
        pending_requests = len(df[df['status'] == 'Pending'])
        st.markdown(f'<div class="metric-card"><h4>Pending</h4><h3>{pending_requests}</h3></div>', unsafe_allow_html=True)
    
    with col4:
        total_invoice_amount = df['invoice_amount'].sum()
        st.markdown(f'<div class="metric-card"><h4>Total Invoice Amount</h4><h3 class="currency-naira">{format_naira(total_invoice_amount)}</h3></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # Enhanced Graphical Analytics
    st.subheader("📊 Graphical Analytics")
    
    # Row 1: Status and Priority Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if not df.empty:
            status_counts = df['status'].value_counts()
            fig = px.pie(values=status_counts.values, names=status_counts.index, 
                        title="📈 Request Status Distribution",
                        color_discrete_sequence=px.colors.sequential.RdBu,
                        hole=0.3)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if not df.empty:
            priority_counts = df['priority'].value_counts()
            colors = ['#FF6B6B', '#FFD166', '#06D6A0', '#118AB2']
            fig = px.bar(x=priority_counts.index, y=priority_counts.values,
                        title="🚨 Requests by Priority", 
                        labels={'x': 'Priority', 'y': 'Count'},
                        color=priority_counts.index,
                        color_discrete_sequence=colors)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Row 2: Facility Type and Location Analysis
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if not df.empty:
            facility_counts = df['facility_type'].value_counts().head(10)
            fig = px.bar(y=facility_counts.index, x=facility_counts.values,
                        title="🏢 Top 10 Facility Types", 
                        orientation='h',
                        labels={'x': 'Count', 'y': 'Facility Type'},
                        color=facility_counts.values,
                        color_continuous_scale='Viridis')
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if not df.empty:
            location_counts = df['location'].value_counts().head(10)
            fig = px.bar(y=location_counts.index, x=location_counts.values,
                        title="📍 Top 10 Locations", 
                        orientation='h',
                        labels={'x': 'Count', 'y': 'Location'},
                        color=location_counts.values,
                        color_continuous_scale='Plasma')
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Row 3: Monthly Trends and Completion Time Analysis
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📅 Monthly Trends & Performance")
    
    col5, col6 = st.columns(2)
    
    with col5:
        if not df.empty and 'month' in df.columns:
            monthly_trends = df.groupby('month').size().reset_index(name='count')
            monthly_trends['month'] = monthly_trends['month'].astype(str)
            
            fig = px.line(monthly_trends, x='month', y='count', 
                         title="📈 Monthly Request Trends", 
                         markers=True,
                         line_shape='spline')
            fig.update_layout(xaxis_title="Month", yaxis_title="Number of Requests")
            st.plotly_chart(fig, use_container_width=True)
    
    with col6:
        if not df.empty and 'created_date' in df.columns and 'completed_date' in df.columns:
            # Calculate completion times for completed requests
            completed_df = df[df['status'] == 'Completed'].copy()
            if not completed_df.empty:
                completed_df['completion_days'] = (completed_df['completed_date'] - completed_df['created_date']).dt.days
                avg_completion = completed_df['completion_days'].mean()
                
                fig = go.Figure()
                fig.add_trace(go.Indicator(
                    mode="number+delta",
                    value=avg_completion,
                    title={"text": "Avg Completion Time (days)"},
                    delta={'reference': 14, 'relative': False},
                    domain={'x': [0, 1], 'y': [0, 1]}
                ))
                fig.update_layout(height=200)
                st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Export Section
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    st.subheader("📤 Export Data & Reports")
    
    col_exp1, col_exp2, col_exp3 = st.columns(3)
    
    with col_exp1:
        if st.button("📊 Export Analytics Dashboard", use_container_width=True, key="export_dashboard"):
            # Create a comprehensive analytics report
            with st.spinner("Generating analytics report..."):
                summary_report = f"""
                FACILITIES MANAGEMENT ANALYTICS REPORT
                Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                
                SUMMARY STATISTICS:
                • Total Requests: {total_requests}
                • Completed Requests: {completed_requests}
                • Pending Requests: {pending_requests}
                • Total Invoice Amount: {format_naira(total_invoice_amount)}
                
                STATUS DISTRIBUTION:
                """
                
                for status, count in status_counts.items():
                    summary_report += f"• {status}: {count} ({count/total_requests*100:.1f}%)\n"
                
                st.download_button(
                    label="📥 Download Analytics Summary",
                    data=summary_report,
                    file_name=f"analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    key="download_analytics"
                )
    
    with col_exp2:
        if st.button("📄 Export to PDF Report", use_container_width=True, key="export_pdf_report"):
            # Generate a PDF report
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            
            # Add content to PDF
            c.setFont("Helvetica-Bold", 16)
            c.drawString(100, 750, "Facilities Management Analytics Report")
            
            c.setFont("Helvetica", 12)
            c.drawString(100, 730, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            c.drawString(100, 710, f"Total Requests: {total_requests}")
            c.drawString(100, 690, f"Completed: {completed_requests}")
            c.drawString(100, 670, f"Pending: {pending_requests}")
            c.drawString(100, 650, f"Total Invoice Amount: {format_naira(total_invoice_amount)}")
            
            c.showPage()
            c.save()
            
            buffer.seek(0)
            st.download_button(
                label="📥 Download PDF Report",
                data=buffer,
                file_name=f"analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                key="download_pdf_report"
            )
    
    with col_exp3:
        if st.button("📈 Export Raw Data (CSV)", use_container_width=True, key="export_csv"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"facilities_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="download_csv"
            )

# ========== ENHANCED JOB & INVOICE REPORTS WITH PDF DOWNLOAD ==========

def show_job_invoice_reports():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("📋 Job & Invoice Reports")
    st.markdown('</div>', unsafe_allow_html=True)
    
    completed_jobs = execute_query('''
        SELECT mr.*, i.invoice_number, i.invoice_date, i.total_amount as invoice_total, 
               i.status as invoice_status, i.details_of_work, i.vendor_username
        FROM maintenance_requests mr
        LEFT JOIN invoices i ON mr.id = i.request_id
        WHERE mr.status IN ('Completed', 'Approved')
        ORDER BY mr.completed_date DESC
    ''')
    
    if not completed_jobs:
        st.info("📭 No completed jobs with invoices found")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_options = ["All"] + list(set(safe_str(safe_get(job, 'status')) for job in completed_jobs))
        status_filter = st.selectbox("Filter by Job Status", status_options, key="job_status_filter")
    with col2:
        has_invoice_filter = st.selectbox("Filter by Invoice", ["All", "With Invoice", "Without Invoice"], key="job_invoice_filter")
    with col3:
        if st.button("🔄 Refresh Reports", key="refresh_job_reports"):
            st.cache_data.clear()
            st.rerun()
    
    filtered_jobs = completed_jobs
    if status_filter != "All":
        filtered_jobs = [job for job in filtered_jobs if safe_str(safe_get(job, 'status')) == status_filter]
    if has_invoice_filter == "With Invoice":
        filtered_jobs = [job for job in filtered_jobs if safe_get(job, 'invoice_number') is not None]
    elif has_invoice_filter == "Without Invoice":
        filtered_jobs = [job for job in filtered_jobs if safe_get(job, 'invoice_number') is None]
    
    st.subheader(f"📊 Found {len(filtered_jobs)} job(s)")
    
    for job in filtered_jobs[:5]:  # Limit to 5 for performance
        with st.expander(f"Job #{safe_get(job, 'id')}: {safe_str(safe_get(job, 'title'), 'N/A')} - {safe_str(safe_get(job, 'location'), 'Common Area')} - {safe_str(safe_get(job, 'status'), 'N/A')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.write("**📋 Job Information**")
                st.write(f"**Title:** {safe_str(safe_get(job, 'title'), 'N/A')}")
                st.write(f"**Location:** {safe_str(safe_get(job, 'location'), 'Common Area')}")
                st.write(f"**Facility Type:** {safe_str(safe_get(job, 'facility_type'), 'N/A')}")
                st.write(f"**Priority:** {safe_str(safe_get(job, 'priority'), 'N/A')}")
                st.write(f"**Status:** {safe_str(safe_get(job, 'status'), 'N/A')}")
                st.write(f"**Created By:** {safe_str(safe_get(job, 'created_by'), 'N/A')}")
                st.write(f"**Assigned Vendor:** {safe_str(safe_get(job, 'assigned_vendor'), 'Not assigned')}")
                if safe_get(job, 'job_breakdown'):
                    st.write(f"**Job Breakdown:** {safe_str(safe_get(job, 'job_breakdown'))}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.write("**🧾 Invoice Information**")
                if safe_get(job, 'invoice_number'):
                    st.write(f"**Invoice Number:** {safe_str(safe_get(job, 'invoice_number'))}")
                    st.write(f"**Invoice Date:** {safe_str(safe_get(job, 'invoice_date'))}")
                    st.write(f"**Invoice Amount:** {format_naira(safe_get(job, 'invoice_total'))}")
                    st.write(f"**Invoice Status:** {safe_str(safe_get(job, 'invoice_status'), 'N/A')}")
                    st.write(f"**Vendor:** {safe_str(safe_get(job, 'vendor_username'), 'N/A')}")
                    if safe_get(job, 'details_of_work'):
                        st.write(f"**Work Details:** {safe_str(safe_get(job, 'details_of_work'))}")
                else:
                    st.write("**No invoice created yet**")
                
                st.write("**✅ Approval Status**")
                st.write(f"**Department Approval:** {'✅ Approved' if safe_get(job, 'requesting_dept_approval') else '⏳ Pending'}")
                st.write(f"**Manager Approval:** {'✅ Approved' if safe_get(job, 'facilities_manager_approval') else '⏳ Pending'}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # PDF Generation Section with Enhanced UI/UX
            st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
            st.subheader("📄 Generate Professional Reports")
            
            col_pdf1, col_pdf2 = st.columns(2)
            
            with col_pdf1:
                if st.button(f"📥 Generate Job Report (PDF)", key=f"job_pdf_{safe_get(job, 'id')}", 
                           use_container_width=True):
                    with st.spinner("Generating professional job report..."):
                        time.sleep(1)  # Simulate processing
                        
                        # Generate PDF
                        pdf_buffer = generate_job_invoice_pdf(job)
                        
                        # Create download button with success message
                        st.success("✅ Report generated successfully!")
                        
                        # Display download button
                        st.download_button(
                            label="⬇️ Download Job Report PDF",
                            data=pdf_buffer,
                            file_name=f"Job_Report_{safe_get(job, 'id')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                            key=f"download_job_{safe_get(job, 'id')}",
                            use_container_width=True
                        )
            
            with col_pdf2:
                if safe_get(job, 'invoice_number'):
                    if st.button(f"🧾 Generate Invoice Report (PDF)", key=f"invoice_pdf_{safe_get(job, 'id')}", 
                               use_container_width=True):
                        with st.spinner("Generating professional invoice report..."):
                            time.sleep(1)  # Simulate processing
                            
                            # Generate PDF with invoice
                            pdf_buffer = generate_job_invoice_pdf(job, job)
                            
                            # Create download button with success message
                            st.success("✅ Invoice report generated successfully!")
                            
                            # Display download button
                            st.download_button(
                                label="⬇️ Download Invoice Report PDF",
                                data=pdf_buffer,
                                file_name=f"Invoice_Report_{safe_get(job, 'invoice_number')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf",
                                key=f"download_invoice_{safe_get(job, 'id')}",
                                use_container_width=True
                            )
                else:
                    st.info("ℹ️ No invoice available for this job")

# ========== PREVENTIVE MAINTENANCE ==========

def show_preventive_maintenance():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🔧 Planned Preventive Maintenance")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📅 Schedule", "➕ Add New"])
    
    with tab1:
        st.subheader("📅 Maintenance Schedule")
        
        maintenance_list = get_preventive_maintenance()
        
        if not maintenance_list:
            st.info("📭 No maintenance schedules found")
        else:
            display_data = []
            for maintenance in maintenance_list[:5]:
                display_data.append({
                    'ID': maintenance['id'],
                    'Equipment': maintenance['equipment_name'],
                    'Type': maintenance['equipment_type'],
                    'Location': maintenance['location'],
                    'Maintenance Type': maintenance['maintenance_type'],
                    'Frequency': maintenance['frequency'],
                    'Last Done': maintenance.get('last_maintenance_date', 'Never'),
                    'Next Due': maintenance['next_maintenance_date'],
                    'Status': maintenance.get('status', 'Upcoming'),
                    'Assigned To': maintenance.get('assigned_to', 'Not assigned')
                })
            
            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader("➕ Add New Maintenance Schedule")
        
        with st.form("add_maintenance_schedule"):
            col1, col2 = st.columns(2)
            
            with col1:
                equipment_name = st.text_input("Equipment Name *", key="pm_equipment_name")
                equipment_type = st.selectbox("Equipment Type *", 
                                            ["HVAC", "Generator", "Fire Safety", "General"],
                                            key="pm_equipment_type")
                location = st.text_input("Location *", value="Common Area", key="pm_location_input")
                maintenance_type = st.selectbox("Maintenance Type *", 
                                              ["Routine Check", "Service", "Inspection"],
                                              key="pm_maintenance_type")
            
            with col2:
                frequency = st.selectbox("Frequency *", 
                                       ["Weekly", "Monthly", "Quarterly", "Biannual", "Annual"],
                                       key="pm_frequency")
                next_maintenance_date = st.date_input("Next Maintenance Date *", 
                                                     value=datetime.now().date() + timedelta(days=30),
                                                     key="pm_next_date")
                assigned_to = st.text_input("Assigned To", placeholder="Name or department", key="pm_assigned_to")
                notes = st.text_area("Notes", key="pm_notes")
            
            submitted = st.form_submit_button("✅ Add to Schedule", use_container_width=True, key="pm_submit")
            
            if submitted:
                if not all([equipment_name, equipment_type, location, maintenance_type, frequency]):
                    st.error("⚠️ Please fill in all required fields (*)")
                else:
                    if add_preventive_maintenance(equipment_name, equipment_type, location, 
                                                 maintenance_type, frequency, 
                                                 None,  # last_maintenance_date
                                                 next_maintenance_date, 
                                                 assigned_to, notes):
                        st.success("✅ Preventive maintenance schedule added successfully!")
                        st.cache_data.clear()
                        st.rerun()

# ========== SPACE MANAGEMENT ==========

def show_space_management():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🏢 Space Management")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📅 View Bookings", "➕ New Booking"])
    
    with tab1:
        st.subheader("📅 Current Bookings")
        
        bookings = get_space_bookings()
        
        if not bookings:
            st.info("📭 No bookings found")
        else:
            display_data = []
            for booking in bookings[:5]:
                display_data.append({
                    'ID': booking['id'],
                    'Room': booking['room_name'],
                    'Type': booking['room_type'],
                    'Date': booking['booking_date'],
                    'Time': f"{booking['start_time']} - {booking['end_time']}",
                    'Purpose': booking['purpose'],
                    'Booked By': booking['booked_by'],
                    'Status': booking['status']
                })
            
            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader("➕ Book a Room")
        
        with st.form("new_booking_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                room_type = st.selectbox("Room Type *", ["Conference", "Meeting", "Cafeteria"], key="new_room_type")
                room_name = st.selectbox("Room Name *", 
                                       ["Conference Room A", "Conference Room B", 
                                        "Meeting Room 1", "Meeting Room 2", 
                                        "Cafeteria"] if room_type != "Cafeteria" else ["Cafeteria"],
                                       key="new_room_name")
                booking_date = st.date_input("Booking Date *", value=datetime.now().date(), key="new_booking_date")
                start_time = st.time_input("Start Time *", value=datetime.strptime("09:00", "%H:%M").time(), key="new_start_time")
                end_time = st.time_input("End Time *", value=datetime.strptime("12:00", "%H:%M").time(), key="new_end_time")
            
            with col2:
                purpose = st.text_input("Purpose *", placeholder="e.g., Team meeting, Training session...", key="new_purpose")
                department = st.selectbox("Department *", 
                                        ["Management", "Operations", "Finance", "HR", 
                                         "IT", "Facilities", "HSE", "All"],
                                        key="new_department")
                attendees_count = st.number_input("Number of Attendees *", min_value=1, max_value=500, value=10, key="new_attendees")
                catering_required = st.checkbox("Catering Required", key="new_catering")
                special_requirements = st.text_area("Special Requirements", 
                                                  placeholder="Audio/visual equipment, specific setup, etc.",
                                                  key="new_special_req")
            
            submitted = st.form_submit_button("📅 Book Room", use_container_width=True, key="new_booking_submit")
            
            if submitted:
                if not all([room_type, room_name, booking_date, purpose, department, attendees_count]):
                    st.error("⚠️ Please fill in all required fields (*)")
                elif end_time <= start_time:
                    st.error("❌ End time must be after start time")
                else:
                    if add_space_booking(room_name, room_type, booking_date, 
                                       start_time.strftime("%H:%M"), 
                                       end_time.strftime("%H:%M"), 
                                       purpose, st.session_state.user['username'],
                                       department, attendees_count, catering_required, 
                                       special_requirements):
                        st.success("✅ Room booked successfully!")
                        st.cache_data.clear()
                        st.rerun()

# ========== HSE MANAGEMENT ==========

def show_hse_management():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🚨 HSE Management")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📅 Schedule", "🚨 Incidents", "➕ New Inspection"])
    
    with tab1:
        st.subheader("📅 HSE Inspection Schedule")
        
        hse_schedule = get_hse_schedule()
        
        if not hse_schedule:
            st.info("📭 No HSE inspections scheduled")
        else:
            display_data = []
            for item in hse_schedule[:5]:
                display_data.append({
                    'ID': item['id'],
                    'Inspection Type': item['inspection_type'],
                    'Area': item['area'],
                    'Frequency': item['frequency'],
                    'Last Inspection': item.get('last_inspection_date', 'Never'),
                    'Next Inspection': item['next_inspection_date'],
                    'Status': item.get('status', 'Upcoming'),
                    'Compliance': item.get('compliance_level', 'Not Assessed')
                })
            
            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader("🚨 Incident Reports")
        
        incidents = get_hse_incidents()
        
        if not incidents:
            st.info("📭 No incident reports found")
        else:
            display_data = []
            for incident in incidents[:5]:
                display_data.append({
                    'ID': incident['id'],
                    'Date': incident['incident_date'],
                    'Time': incident['incident_time'],
                    'Location': incident['location'],
                    'Type': incident['incident_type'],
                    'Severity': incident['severity'],
                    'Status': incident.get('status', 'Open')
                })
            
            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    with tab3:
        st.subheader("➕ Schedule New Inspection")
        
        with st.form("new_inspection_schedule"):
            col1, col2 = st.columns(2)
            
            with col1:
                inspection_type = st.selectbox("Inspection Type *", 
                                             ["Fire Safety Inspection", "First Aid Kit Check", 
                                              "Emergency Exit Inspection", "Electrical Safety Check",
                                              "PPE Inspection", "Other"],
                                             key="new_inspection_type")
                area = st.text_input("Area *", placeholder="e.g., Main Building, Generator Room...", key="new_inspection_area")
                frequency = st.selectbox("Frequency *", ["Daily", "Weekly", "Monthly", "Quarterly", "Annual"], key="new_inspection_freq")
            
            with col2:
                next_inspection_date = st.date_input("Next Inspection Date *", 
                                                    value=datetime.now().date() + timedelta(days=7),
                                                    key="new_inspection_date")
                assigned_to = st.text_input("Assigned To *", value=st.session_state.user['username'], key="new_inspection_assigned")
            
            submitted = st.form_submit_button("📅 Schedule Inspection", use_container_width=True, key="new_inspection_submit")
            
            if submitted:
                if not all([inspection_type, area, frequency, next_inspection_date, assigned_to]):
                    st.error("⚠️ Please fill in all required fields (*)")
                else:
                    if add_hse_schedule(inspection_type, area, frequency, next_inspection_date, assigned_to):
                        st.success("✅ Inspection scheduled successfully!")
                        st.cache_data.clear()
                        st.rerun()

# ========== MAIN APP ROUTING ==========

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
            menu_options = ["Dashboard", "Generator Records", "Space Management", "HSE Management"]
        elif role == 'facility_manager':
            menu_options = ["Dashboard", "Reports", "Job & Invoice Reports", "Preventive Maintenance",
                          "Space Management", "Generator Records", "HSE Management"]
        elif role == 'hse_officer':
            menu_options = ["Dashboard", "HSE Management"]
        elif role == 'space_manager':
            menu_options = ["Dashboard", "Space Management"]
        else:  # vendor
            menu_options = ["Dashboard", "Generator Records"]
        
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
    elif selected_menu == "Reports":
        show_reports()
    elif selected_menu == "Job & Invoice Reports":
        show_job_invoice_reports()
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
