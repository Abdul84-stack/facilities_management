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

# Database setup with enhanced schema
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
    
    # Insert sample preventive maintenance data
    today = datetime.now().date()
    sample_maintenance = [
        ('Main HVAC System', 'HVAC', 'Main Building', 'Routine Check', 'Monthly', 
         (today - timedelta(days=15)).isoformat(), (today + timedelta(days=15)).isoformat(), None, None),
        ('Fire Extinguishers', 'Fire Safety', 'All Floors', 'Inspection', 'Biannual',
         (today - timedelta(days=60)).isoformat(), (today + timedelta(days=120)).isoformat(), None, None),
        ('Smoke Detectors', 'Fire Safety', 'All Floors', 'Testing', 'Quarterly',
         (today - timedelta(days=45)).isoformat(), (today + timedelta(days=45)).isoformat(), None, None),
        ('Generator Set #1', 'Generator', 'Generator Room', 'Service', '200 hours',
         (today - timedelta(days=10)).isoformat(), (today + timedelta(days=10)).isoformat(), None, None),
        ('Pest Control', 'General', 'Entire Facility', 'Fumigation', 'Quarterly',
         (today - timedelta(days=30)).isoformat(), (today + timedelta(days=60)).isoformat(), None, None)
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
    for i in range(7):
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
        ('Electrical Safety Check', 'Generator Room', 'Monthly',
         (today - timedelta(days=10)).isoformat(), (today + timedelta(days=20)).isoformat(),
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

# Database functions
def get_connection():
    return sqlite3.connect('facilities_management.db')

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
        if conn:
            conn.close()

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

# ========== NEW FUNCTIONS FOR REQUESTED FEATURES ==========

# Preventive Maintenance Functions
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
    
    base_query += ' ORDER BY next_maintenance_date ASC'
    return execute_query(base_query, params)

def add_preventive_maintenance(equipment_name, equipment_type, location, maintenance_type, 
                              frequency, last_maintenance_date, next_maintenance_date, assigned_to, notes):
    return execute_update('''
        INSERT INTO preventive_maintenance 
        (equipment_name, equipment_type, location, maintenance_type, frequency, 
         last_maintenance_date, next_maintenance_date, assigned_to, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (equipment_name, equipment_type, location, maintenance_type, frequency,
          last_maintenance_date, next_maintenance_date, assigned_to, notes))

def update_preventive_maintenance(maintenance_id, status, completion_notes=None):
    today = datetime.now().date()
    if status == 'Completed':
        return execute_update('''
            UPDATE preventive_maintenance 
            SET status = ?, completed_date = ?, completion_notes = ?
            WHERE id = ?
        ''', (status, today.isoformat(), completion_notes, maintenance_id))
    else:
        return execute_update('''
            UPDATE preventive_maintenance 
            SET status = ?
            WHERE id = ?
        ''', (status, maintenance_id))

# Generator Records Functions
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
    
    query += ' ORDER BY record_date DESC'
    return execute_query(query, params)

def add_generator_record(record_date, generator_name, opening_hours, closing_hours, 
                        opening_diesel_level, closing_diesel_level, recorded_by, notes):
    return execute_update('''
        INSERT INTO generator_records 
        (record_date, generator_name, opening_hours, closing_hours, 
         opening_diesel_level, closing_diesel_level, recorded_by, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (record_date.isoformat(), generator_name, opening_hours, closing_hours,
          opening_diesel_level, closing_diesel_level, recorded_by, notes))

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
    
    base_query += ' ORDER BY booking_date DESC, start_time ASC'
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

def update_booking_status(booking_id, status):
    return execute_update('''
        UPDATE space_bookings 
        SET status = ?, last_modified = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (status, booking_id))

def check_room_availability(room_name, booking_date, start_time, end_time, exclude_booking_id=None):
    query = '''
        SELECT * FROM space_bookings 
        WHERE room_name = ? 
        AND booking_date = ?
        AND status = 'Confirmed'
        AND ((? < end_time AND ? > start_time) OR (? <= start_time AND ? >= end_time))
    '''
    params = [room_name, booking_date.isoformat(), start_time, end_time, start_time, end_time]
    
    if exclude_booking_id:
        query += ' AND id != ?'
        params.append(exclude_booking_id)
    
    conflicting_bookings = execute_query(query, params)
    return len(conflicting_bookings) == 0

# HSE Schedule Functions
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
    
    base_query += ' ORDER BY next_inspection_date ASC'
    return execute_query(base_query, params)

def add_hse_schedule(inspection_type, area, frequency, next_inspection_date, assigned_to):
    return execute_update('''
        INSERT INTO hse_schedule 
        (inspection_type, area, frequency, next_inspection_date, assigned_to)
        VALUES (?, ?, ?, ?, ?)
    ''', (inspection_type, area, frequency, next_inspection_date.isoformat(), assigned_to))

def update_hse_inspection(inspection_id, compliance_level, findings, corrective_actions, follow_up_date):
    today = datetime.now().date()
    return execute_update('''
        UPDATE hse_schedule 
        SET status = 'Completed',
            last_inspection_date = ?,
            compliance_level = ?,
            findings = ?,
            corrective_actions = ?,
            follow_up_date = ?
        WHERE id = ?
    ''', (today.isoformat(), compliance_level, findings, corrective_actions, 
          follow_up_date.isoformat() if follow_up_date else None, inspection_id))

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
    
    base_query += ' ORDER BY incident_date DESC'
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

def update_incident_status(incident_id, investigation_status, corrective_measures, status):
    return execute_update('''
        UPDATE hse_incidents 
        SET investigation_status = ?,
            corrective_measures = ?,
            status = ?
        WHERE id = ?
    ''', (investigation_status, corrective_measures, status, incident_id))

# Authentication
def authenticate_user(username, password):
    users = execute_query('SELECT * FROM users WHERE username = ? AND password_hash = ?', (username, password))
    return users[0] if users else None

# ========== NEW PAGES FOR REQUESTED FEATURES ==========

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
        
        maintenance_schedule = get_preventive_maintenance(filters)
        
        if not maintenance_schedule:
            st.info("📭 No maintenance schedules found")
        else:
            # Display maintenance schedule
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
                                if update_preventive_maintenance(int(selected_id), 'Completed', completion_notes):
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
            for item in overdue_items:
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
                    if add_preventive_maintenance(equipment_name, equipment_type, location, 
                                                 maintenance_type, frequency, 
                                                 last_maintenance_date.isoformat(), 
                                                 next_maintenance_date.isoformat(), 
                                                 assigned_to, notes):
                        st.success("✅ Preventive maintenance schedule added successfully!")
                        st.rerun()
    
    with tab3:
        st.subheader("📊 Maintenance Analytics")
        
        # Summary statistics
        all_maintenance = get_preventive_maintenance()
        
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
            
            # Equipment type distribution
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
            start_date = st.date_input("Start Date", value=datetime.now().date() - timedelta(days=7))
        with col2:
            end_date = st.date_input("End Date", value=datetime.now().date())
        
        records = get_generator_records(start_date, end_date)
        
        if not records:
            st.info("📭 No records found for the selected date range")
        else:
            # Display records
            display_data = []
            total_hours = 0
            total_diesel = 0
            
            for record in records:
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
                    'Recorded By': record.get('recorded_by'),
                    'Notes': record.get('notes', '')
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
        
        with st.form("add_generator_record"):
            col1, col2 = st.columns(2)
            
            with col1:
                record_date = st.date_input("Record Date *", value=datetime.now().date())
                generator_name = st.selectbox("Generator Name *", ["Generator #1", "Generator #2", "Generator #3"])
                opening_hours = st.number_input("Opening Hours *", min_value=0.0, step=0.1, format="%.1f")
                closing_hours = st.number_input("Closing Hours *", min_value=opening_hours, step=0.1, format="%.1f")
            
            with col2:
                opening_diesel_level = st.number_input("Opening Diesel Level (L) *", min_value=0.0, step=0.1, format="%.1f")
                closing_diesel_level = st.number_input("Closing Diesel Level (L) *", min_value=0.0, max_value=opening_diesel_level, step=0.1, format="%.1f")
                recorded_by = st.text_input("Recorded By *", value=st.session_state.user['username'])
                notes = st.text_area("Notes")
            
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
            
            submitted = st.form_submit_button("💾 Save Record", use_container_width=True)
            
            if submitted:
                if not all([record_date, generator_name, opening_hours, closing_hours, 
                          opening_diesel_level, closing_diesel_level, recorded_by]):
                    st.error("⚠️ Please fill in all required fields (*)")
                elif closing_hours < opening_hours:
                    st.error("❌ Closing hours cannot be less than opening hours")
                elif closing_diesel_level > opening_diesel_level:
                    st.error("❌ Closing diesel level cannot be greater than opening level")
                else:
                    if add_generator_record(record_date, generator_name, opening_hours, closing_hours,
                                          opening_diesel_level, closing_diesel_level, recorded_by, notes):
                        st.success("✅ Generator record saved successfully!")
                        st.rerun()
    
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
            
            # Diesel consumption chart
            st.subheader("⛽ Diesel Consumption Trend")
            records_30d = get_generator_records(datetime.now().date() - timedelta(days=30), datetime.now().date())
            
            if records_30d:
                chart_data = []
                for record in records_30d:
                    chart_data.append({
                        'Date': record['record_date'],
                        'Diesel Consumed': safe_float(record['diesel_consumed']),
                        'Net Hours': safe_float(record['net_hours_used'])
                    })
                
                chart_df = pd.DataFrame(chart_data)
                if not chart_df.empty:
                    fig = px.line(chart_df, x='Date', y='Diesel Consumed', 
                                 title="Daily Diesel Consumption (Last 30 Days)",
                                 markers=True)
                    st.plotly_chart(fig, use_container_width=True)
        
        # Inventory alert
        st.subheader("⚠️ Inventory Alerts")
        recent_records = get_generator_records(datetime.now().date() - timedelta(days=3), datetime.now().date())
        
        if recent_records:
            avg_daily_consumption = sum(safe_float(r['diesel_consumed']) for r in recent_records) / len(recent_records)
            current_level = safe_float(recent_records[0]['closing_diesel_level']) if recent_records else 0
            
            days_remaining = current_level / avg_daily_consumption if avg_daily_consumption > 0 else 0
            
            if days_remaining < 2:
                st.markdown('<div class="alert-danger">', unsafe_allow_html=True)
                st.error(f"🚨 CRITICAL: Diesel inventory very low! Only {days_remaining:.1f} days remaining.")
                st.markdown('</div>', unsafe_allow_html=True)
            elif days_remaining < 5:
                st.markdown('<div class="alert-warning">', unsafe_allow_html=True)
                st.warning(f"⚠️ WARNING: Diesel inventory low. {days_remaining:.1f} days remaining.")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-success">', unsafe_allow_html=True)
                st.success(f"✅ Diesel inventory sufficient. {days_remaining:.1f} days remaining.")
                st.markdown('</div>', unsafe_allow_html=True)

def show_space_management():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🏢 Space Management & Room Booking")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📅 View Bookings", "➕ New Booking", "🏢 Room Management"])
    
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
        
        bookings = get_space_bookings(filters)
        
        if not bookings:
            st.info("📭 No bookings found")
        else:
            # Display bookings
            for booking in bookings:
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
                            if update_booking_status(booking['id'], 'Cancelled'):
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
                is_available = check_room_availability(room_name, booking_date, 
                                                      start_time.strftime("%H:%M"), 
                                                      end_time.strftime("%H:%M"))
                
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
                    if add_space_booking(room_name, room_type, booking_date, 
                                       start_time.strftime("%H:%M"), 
                                       end_time.strftime("%H:%M"), 
                                       purpose, st.session_state.user['username'],
                                       department, attendees_count, catering_required, 
                                       special_requirements):
                        st.success("✅ Room booked successfully!")
                        st.rerun()
    
    with tab3:
        st.subheader("🏢 Room Management")
        
        if st.session_state.user['role'] in ['facility_manager', 'space_manager']:
            # Room availability calendar view
            st.write("### 📅 Room Availability Calendar")
            
            selected_date = st.date_input("Select Date to View", value=datetime.now().date(), key="calendar_date")
            room_types = ["Conference Room A", "Conference Room B", "Meeting Room 1", "Meeting Room 2", "Cafeteria"]
            
            for room in room_types:
                st.write(f"#### {room}")
                
                # Get bookings for this room on selected date
                room_bookings = get_space_bookings({'room_name': room, 'booking_date': selected_date})
                
                if not room_bookings:
                    st.success("✅ No bookings - Room available all day")
                else:
                    # Display time slots
                    slots = []
                    for booking in room_bookings:
                        if booking.get('status') == 'Confirmed':
                            slots.append(f"⛔ {booking['start_time']} - {booking['end_time']}: {booking['purpose']}")
                    
                    if slots:
                        st.warning("🚫 Booked time slots:")
                        for slot in slots:
                            st.write(f"• {slot}")
                    else:
                        st.success("✅ Room available all day")
        
        # Statistics
        st.subheader("📊 Booking Statistics")
        
        all_bookings = get_space_bookings()
        if all_bookings:
            total_bookings = len(all_bookings)
            confirmed_bookings = len([b for b in all_bookings if b.get('status') == 'Confirmed'])
            cancelled_bookings = len([b for b in all_bookings if b.get('status') == 'Cancelled'])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Bookings", total_bookings)
            with col2:
                st.metric("Confirmed", confirmed_bookings)
            with col3:
                st.metric("Cancelled", cancelled_bookings)

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
        
        hse_schedule = get_hse_schedule(filters)
        
        if not hse_schedule:
            st.info("📭 No HSE inspections scheduled")
        else:
            # Display schedule
            for item in hse_schedule:
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
                                if update_hse_inspection(item['id'], compliance, findings, 
                                                       corrective_actions, follow_up_date):
                                    st.success("✅ Inspection completed!")
                                    st.rerun()
        
        # Overdue inspections alert
        overdue_inspections = [i for i in hse_schedule if i.get('status') != 'Completed' 
                              and safe_date(i.get('next_inspection_date')) 
                              and safe_date(i.get('next_inspection_date')) < datetime.now().date()]
        
        if overdue_inspections:
            st.markdown('<div class="alert-danger">', unsafe_allow_html=True)
            st.error(f"⚠️ **CRITICAL:** {len(overdue_inspections)} HSE inspection(s) overdue!")
            for item in overdue_inspections:
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
        
        incidents = get_hse_incidents(filters)
        
        if not incidents:
            st.info("📭 No incident reports found")
        else:
            for incident in incidents:
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
                            st.write(f"**Affected Persons:** {incident['affected_persons']}")
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
                                if update_incident_status(incident['id'], investigation_status, 
                                                         corrective_measures, status):
                                    st.success("✅ Incident updated!")
                                    st.rerun()
        
        # Add new incident button
        if st.session_state.user['role'] in ['hse_officer', 'facility_user', 'facility_manager']:
            st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
            if st.button("➕ Report New Incident", use_container_width=True):
                st.session_state['show_new_incident'] = True
        
        # New incident form
        if st.session_state.get('show_new_incident', False):
            st.subheader("➕ Report New Incident")
            
            with st.form("new_incident_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    incident_date = st.date_input("Incident Date *", value=datetime.now().date())
                    incident_time = st.time_input("Incident Time *", value=datetime.now().time())
                    location = st.text_input("Location *", placeholder="e.g., Generator Room, Office Building...")
                    incident_type = st.selectbox("Incident Type *", 
                                               ["Near Miss", "First Aid Case", "Medical Treatment Case", 
                                                "Lost Time Injury", "Property Damage", "Environmental", "Other"])
                
                with col2:
                    severity = st.selectbox("Severity *", ["Low", "Medium", "High", "Critical"])
                    reported_by = st.text_input("Reported By *", value=st.session_state.user['username'])
                    affected_persons = st.text_input("Affected Persons", placeholder="Names and departments...")
                
                description = st.text_area("Description of Incident *", 
                                         placeholder="Provide detailed description of what happened...")
                immediate_actions = st.text_area("Immediate Actions Taken", 
                                               placeholder="First aid, evacuation, containment, etc.")
                
                col_submit1, col_submit2, col_submit3 = st.columns([1, 2, 1])
                with col_submit2:
                    submitted = st.form_submit_button("🚨 Submit Incident Report", use_container_width=True)
                
                if submitted:
                    if not all([incident_date, incident_time, location, incident_type, severity, description, reported_by]):
                        st.error("⚠️ Please fill in all required fields (*)")
                    else:
                        if add_hse_incident(incident_date, incident_time.strftime("%H:%M"), 
                                          location, incident_type, severity, description, 
                                          reported_by, affected_persons, immediate_actions):
                            st.success("✅ Incident report submitted successfully!")
                            st.session_state['show_new_incident'] = False
                            st.rerun()
            
            if st.button("❌ Cancel", key="cancel_incident"):
                st.session_state['show_new_incident'] = False
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
                        if add_hse_schedule(inspection_type, area, frequency, next_inspection_date, assigned_to):
                            st.success("✅ Inspection scheduled successfully!")
                            st.rerun()
        else:
            st.info("🔒 Only HSE officers and facility managers can schedule new inspections")
    
    with tab4:
        st.subheader("📊 HSE Compliance Dashboard")
        
        # Get all HSE data
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
            
            # Incident statistics
            if all_incidents:
                st.subheader("🚨 Incident Statistics")
                
                incident_by_severity = {}
                for incident in all_incidents:
                    severity = incident.get('severity', 'Unknown')
                    incident_by_severity[severity] = incident_by_severity.get(severity, 0) + 1
                
                col1, col2 = st.columns(2)
                with col1:
                    if incident_by_severity:
                        fig1 = px.pie(values=list(incident_by_severity.values()), 
                                     names=list(incident_by_severity.keys()),
                                     title="Incidents by Severity")
                        st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    # Monthly incident trend
                    incident_dates = [safe_date(i.get('incident_date')) for i in all_incidents if i.get('incident_date')]
                    if incident_dates:
                        date_counts = {}
                        for d in incident_dates:
                            if d:
                                month_key = d.strftime('%Y-%m')
                                date_counts[month_key] = date_counts.get(month_key, 0) + 1
                        
                        if date_counts:
                            fig2 = px.bar(x=list(date_counts.keys()), y=list(date_counts.values()),
                                         title="Monthly Incident Trend")
                            st.plotly_chart(fig2, use_container_width=True)
            
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

# Login Page
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
        • Fixture Masters: fixture_vendor / 0123456
        • Building Care: building_vendor / 0123456
        """
        st.code(credentials, language=None)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
            <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.2);">
                <p style="color: rgba(255,255,255,0.8); font-size: 12px;">
                    © 2024 Facilities Management System™ v3.0 | Developed by Abdulahi Ibrahim<br>
                    All trademarks and copyrights belong to their respective owners
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer at bottom of page
    st.markdown("""
        <div class="app-footer">
            FACILITIES MANAGEMENT SYSTEM™ v3.0 © 2024 | Currency: Nigerian Naira (₦) | Developed by Abdulahi Ibrahim
        </div>
    """, unsafe_allow_html=True)

# Dashboard Functions - UPDATED TO INCLUDE NEW FEATURES
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
    
    # Quick access to new features
    st.subheader("🚀 Quick Access")
    
    col_q1, col_q2, col_q3 = st.columns(3)
    
    with col_q1:
        if st.button("📅 Book a Room", use_container_width=True):
            st.session_state.navigation_menu = "Space Management"
            st.rerun()
    
    with col_q2:
        if st.button("⛽ Generator Records", use_container_width=True):
            st.session_state.navigation_menu = "Generator Records"
            st.rerun()
    
    with col_q3:
        if st.button("🚨 Report Incident", use_container_width=True):
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
    
    # Quick access to new features for managers
    st.subheader("🚀 Management Quick Access")
    
    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
    
    with col_q1:
        if st.button("📅 Maintenance Schedule", use_container_width=True):
            st.session_state.navigation_menu = "Preventive Maintenance"
            st.rerun()
    
    with col_q2:
        if st.button("🏢 Space Management", use_container_width=True):
            st.session_state.navigation_menu = "Space Management"
            st.rerun()
    
    with col_q3:
        if st.button("🚨 HSE Dashboard", use_container_width=True):
            st.session_state.navigation_menu = "HSE Management"
            st.rerun()
    
    with col_q4:
        if st.button("⛽ Generator Reports", use_container_width=True):
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

def show_hse_dashboard():
    st.subheader("🚨 HSE Officer Dashboard")
    
    # Get HSE data
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
        if st.button("➕ Schedule Inspection", use_container_width=True):
            st.session_state.navigation_menu = "HSE Management"
            st.rerun()
    
    with col_q2:
        if st.button("🚨 Report Incident", use_container_width=True):
            st.session_state.navigation_menu = "HSE Management"
            st.rerun()
    
    with col_q3:
        if st.button("📊 View Compliance", use_container_width=True):
            st.session_state.navigation_menu = "HSE Management"
            st.rerun()
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # Urgent items
    col_urg1, col_urg2 = st.columns(2)
    
    with col_urg1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("⚠️ Overdue Inspections")
        overdue_items = [i for i in hse_schedule_data if i.get('status') != 'Completed' 
                        and safe_date(i.get('next_inspection_date')) 
                        and safe_date(i.get('next_inspection_date')) < datetime.now().date()]
        
        if overdue_items:
            for item in overdue_items[:5]:
                st.write(f"• **{item['inspection_type']}** at {item['area']} (Due: {item['next_inspection_date']})")
            if len(overdue_items) > 5:
                st.write(f"... and {len(overdue_items) - 5} more")
        else:
            st.success("✅ No overdue inspections")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_urg2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🚨 Recent Incidents")
        if hse_incidents:
            for incident in hse_incidents[:5]:
                st.write(f"• **{incident['incident_type']}** at {incident['location']} ({incident['severity']})")
            if len(hse_incidents) > 5:
                st.write(f"... and {len(hse_incidents) - 5} more")
        else:
            st.success("✅ No recent incidents")
        st.markdown('</div>', unsafe_allow_html=True)

def show_space_dashboard():
    st.subheader("🏢 Space Manager Dashboard")
    
    # Get space booking data
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
        if st.button("➕ New Booking", use_container_width=True):
            st.session_state.navigation_menu = "Space Management"
            st.rerun()
    
    with col_q2:
        if st.button("📅 View All Bookings", use_container_width=True):
            st.session_state.navigation_menu = "Space Management"
            st.rerun()
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # Today's schedule
    st.subheader("📅 Today's Schedule")
    
    today = datetime.now().date().isoformat()
    todays_bookings = [b for b in bookings if b.get('booking_date') == today and b.get('status') == 'Confirmed']
    
    if todays_bookings:
        for booking in todays_bookings:
            with st.expander(f"{booking['room_name']} - {booking['start_time']} to {booking['end_time']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Purpose:** {booking['purpose']}")
                    st.write(f"**Department:** {booking['department']}")
                    st.write(f"**Attendees:** {booking['attendees_count']}")
                with col2:
                    st.write(f"**Booked By:** {booking['booked_by']}")
                    if booking.get('catering_required'):
                        st.write("**Catering:** ✅ Required")
                    if booking.get('special_requirements'):
                        st.write(f"**Special:** {booking['special_requirements']}")
    else:
        st.info("📭 No bookings scheduled for today")

def show_vendor_dashboard():
    vendor_requests = get_vendor_requests(st.session_state.user['username'])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        assigned_count = len([r for r in vendor_requests if safe_get(r, 'status') == 'Assigned'])
        st.markdown('<h4>Assigned Jobs</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3>{assigned_count}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        completed_count = len([r for r in vendor_requests if safe_get(r, 'status') == 'Completed'])
        st.markdown('<h4>Completed Jobs</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3>{completed_count}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<h4>Total Jobs</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3>{len(vendor_requests)}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
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

# Existing functions that remain the same (shortened for brevity)
def show_create_request():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("📝 Create Maintenance Request")
    st.markdown('</div>', unsafe_allow_html=True)
    
    with st.form("create_request_form", clear_on_submit=True):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("📌 Request Title", placeholder="Enter request title", key="req_title")
            location = st.selectbox(
                "📍 Location",
                ["Water Treatment Plant", "Finance", "HR", "Admin", "Common Area", 
                 "Production", "Warehouse", "Office Building", "Laboratory"],
                key="req_location"
            )
            facility_type = st.selectbox(
                "🏢 Facility Type",
                ["HVAC (Cooling Systems)", "Generator Maintenance", "Fixture and Fittings", 
                 "Building Maintenance", "HSE", "Space Management"],
                key="req_facility"
            )
        
        with col2:
            priority = st.selectbox("🚨 Priority", ["Low", "Medium", "High", "Critical"], key="req_priority")
        
        description = st.text_area("📄 Description of the Request", height=100, 
                                 placeholder="Please provide detailed description of the maintenance request...",
                                 key="req_description")
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
                    st.rerun()
                else:
                    st.error("❌ Failed to create request")

def show_my_requests():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("📋 My Maintenance Requests")
    st.markdown('</div>', unsafe_allow_html=True)
    
    user_requests = get_user_requests(st.session_state.user['username'])
    
    if not user_requests:
        st.info("📭 No maintenance requests found")
        return
    
    display_data = []
    for req in user_requests:
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
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        status_options = ["All"] + list(df['Status'].unique())
        status_filter = st.selectbox("Filter by Status", status_options, key="status_filter")
    with col2:
        priority_options = ["All"] + list(df['Priority'].unique())
        priority_filter = st.selectbox("Filter by Priority", priority_options, key="priority_filter")
    with col3:
        facility_options = ["All"] + list(df['Facility'].unique())
        facility_filter = st.selectbox("Filter by Facility Type", facility_options, key="facility_filter")
    with col4:
        location_options = ["All"] + list(df['Location'].unique())
        location_filter = st.selectbox("Filter by Location", location_options, key="location_filter")
    
    filtered_df = df
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['Status'] == status_filter]
    if priority_filter != "All":
        filtered_df = filtered_df[filtered_df['Priority'] == priority_filter]
    if facility_filter != "All":
        filtered_df = filtered_df[filtered_df['Facility'] == facility_filter]
    if location_filter != "All":
        filtered_df = filtered_df[filtered_df['Location'] == location_filter]
    
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    st.subheader("📄 Request Details")
    selected_id = st.selectbox("Select Request to View Details", [""] + [str(safe_get(req, 'id')) for req in user_requests], key="request_select")
    
    if selected_id:
        request = next((r for r in user_requests if str(safe_get(r, 'id')) == selected_id), None)
        if request:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.write("**📋 Basic Information**")
                st.write(f"**Title:** {safe_str(safe_get(request, 'title'), 'N/A')}")
                st.write(f"**Description:** {safe_str(safe_get(request, 'description'), 'N/A')}")
                st.write(f"**Location:** {safe_str(safe_get(request, 'location'), 'Common Area')}")
                st.write(f"**Facility Type:** {safe_str(safe_get(request, 'facility_type'), 'N/A')}")
                st.write(f"**Priority:** {safe_str(safe_get(request, 'priority'), 'N/A')}")
                st.write(f"**Status:** {safe_str(safe_get(request, 'status'), 'N/A')}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.write("**📊 Additional Information**")
                st.write(f"**Created Date:** {safe_str(safe_get(request, 'created_date'), 'N/A')}")
                if safe_get(request, 'assigned_vendor'):
                    vendor_info = execute_query(
                        'SELECT company_name FROM vendors WHERE username = ?',
                        (safe_get(request, 'assigned_vendor'),)
                    )
                    vendor_name = vendor_info[0]['company_name'] if vendor_info else safe_get(request, 'assigned_vendor')
                    st.write(f"**Assigned Vendor:** {vendor_name}")
                if safe_get(request, 'completion_notes'):
                    st.write(f"**Completion Notes:** {safe_str(safe_get(request, 'completion_notes'))}")
                if safe_get(request, 'job_breakdown'):
                    st.write(f"**Job Breakdown:** {safe_str(safe_get(request, 'job_breakdown'))}")
                if safe_get(request, 'invoice_amount'):
                    st.write(f"**Invoice Amount:** {format_naira(safe_get(request, 'invoice_amount'))}")
                    st.write(f"**Invoice Number:** {safe_str(safe_get(request, 'invoice_number'), 'N/A')}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            if (safe_get(request, 'status') == 'Completed' and 
                not safe_get(request, 'requesting_dept_approval') and
                safe_get(request, 'created_by') == st.session_state.user['username']):
                
                st.markdown('<div class="card">', unsafe_allow_html=True)
                if st.button("✅ Approve (Department)", use_container_width=True, key=f"approve_{safe_get(request, 'id')}"):
                    if execute_update(
                        'UPDATE maintenance_requests SET requesting_dept_approval = 1 WHERE id = ?',
                        (safe_get(request, 'id'),)
                    ):
                        st.success("✅ Department approval granted!")
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

def show_manage_requests():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🛠️ Manage Maintenance Requests")
    st.markdown('</div>', unsafe_allow_html=True)
    
    all_requests = get_all_requests()
    
    if not all_requests:
        st.info("📭 No maintenance requests found")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        status_options = ["All"] + ["Pending", "Assigned", "Completed", "Approved"]
        status_filter = st.selectbox("Filter by Status", status_options, key="mgr_status")
    with col2:
        priority_options = ["All"] + ["Low", "Medium", "High", "Critical"]
        priority_filter = st.selectbox("Filter by Priority", priority_options, key="mgr_priority")
    with col3:
        facility_types = list(set(safe_str(req.get('facility_type')) for req in all_requests))
        facility_options = ["All"] + facility_types
        facility_filter = st.selectbox("Filter by Facility Type", facility_options, key="mgr_facility")
    with col4:
        locations = list(set(safe_str(req.get('location'), 'Common Area') for req in all_requests))
        location_options = ["All"] + locations
        location_filter = st.selectbox("Filter by Location", location_options, key="mgr_location")
    
    filtered_requests = all_requests
    if status_filter != "All":
        filtered_requests = [req for req in filtered_requests if safe_str(req.get('status')) == status_filter]
    if priority_filter != "All":
        filtered_requests = [req for req in filtered_requests if safe_str(req.get('priority')) == priority_filter]
    if facility_filter != "All":
        filtered_requests = [req for req in filtered_requests if safe_str(req.get('facility_type')) == facility_filter]
    if location_filter != "All":
        filtered_requests = [req for req in filtered_requests if safe_str(req.get('location'), 'Common Area') == location_filter]
    
    st.subheader(f"📊 Showing {len(filtered_requests)} request(s)")
    
    for request in filtered_requests:
        with st.expander(f"Request #{safe_get(request, 'id')}: {safe_str(safe_get(request, 'title'), 'N/A')} - {safe_str(safe_get(request, 'status'), 'N/A')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.write("**📋 Basic Information**")
                st.write(f"**Title:** {safe_str(safe_get(request, 'title'), 'N/A')}")
                st.write(f"**Description:** {safe_str(safe_get(request, 'description'), 'N/A')}")
                st.write(f"**Location:** {safe_str(safe_get(request, 'location'), 'Common Area')}")
                st.write(f"**Facility Type:** {safe_str(safe_get(request, 'facility_type'), 'N/A')}")
                st.write(f"**Priority:** {safe_str(safe_get(request, 'priority'), 'N/A')}")
                st.write(f"**Status:** {safe_str(safe_get(request, 'status'), 'N/A')}")
                st.write(f"**Created By:** {safe_str(safe_get(request, 'created_by'), 'N/A')}")
                st.write(f"**Created Date:** {safe_str(safe_get(request, 'created_date'), 'N/A')}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.write("**🛠️ Management Actions**")
                
                if safe_get(request, 'status') == 'Pending':
                    st.subheader("👥 Assign to Vendor")
                    
                    facility_type = safe_str(safe_get(request, 'facility_type'))
                    
                    facility_to_vendor_map = {
                        "HVAC (Cooling Systems)": "HVAC",
                        "Generator Maintenance": "Generator",
                        "Fixture and Fittings": "Fixture and Fittings",
                        "Building Maintenance": "Building Maintenance",
                        "HSE": "HSE",
                        "Space Management": "Space Management"
                    }
                    
                    vendor_type = facility_to_vendor_map.get(facility_type, facility_type)
                    
                    vendors = execute_query('''
                        SELECT v.*, u.username 
                        FROM vendors v 
                        JOIN users u ON v.username = u.username 
                        WHERE u.vendor_type = ? OR v.vendor_type = ?
                    ''', (vendor_type, vendor_type))
                    
                    if vendors:
                        vendor_options = {f"{vendor['company_name']} ({vendor['username']})": vendor['username'] for vendor in vendors}
                        selected_vendor_key = st.selectbox(
                            f"Select vendor for {facility_type}",
                            options=list(vendor_options.keys()),
                            key=f"vendor_{safe_get(request, 'id')}"
                        )
                        
                        if selected_vendor_key:
                            selected_vendor = vendor_options[selected_vendor_key]
                            
                            if st.button(f"👥 Assign to {selected_vendor}", key=f"assign_{safe_get(request, 'id')}"):
                                if execute_update(
                                    'UPDATE maintenance_requests SET status = ?, assigned_vendor = ? WHERE id = ?',
                                    ('Assigned', selected_vendor, safe_get(request, 'id'))
                                ):
                                    st.success(f"✅ Request assigned to {selected_vendor}!")
                                    st.rerun()
                    else:
                        st.warning(f"⚠️ No registered vendors found for {facility_type}")
                
                elif safe_get(request, 'status') == 'Completed':
                    st.subheader("✅ Manager Approval")
                    
                    if safe_get(request, 'requesting_dept_approval'):
                        st.success("✅ Department approval received")
                        
                        if not safe_get(request, 'facilities_manager_approval'):
                            if st.button("✅ Approve as Facilities Manager", key=f"approve_{safe_get(request, 'id')}"):
                                if execute_update(
                                    'UPDATE maintenance_requests SET status = ?, facilities_manager_approval = ? WHERE id = ?',
                                    ('Approved', True, safe_get(request, 'id'))
                                ):
                                    st.success("✅ Facilities manager approval granted!")
                                    st.rerun()
                        else:
                            st.success("✅ Facilities manager approval granted")
                    else:
                        st.warning("⏳ Waiting for department approval")
                
                if safe_get(request, 'assigned_vendor'):
                    vendor_info = execute_query(
                        'SELECT company_name FROM vendors WHERE username = ?',
                        (safe_get(request, 'assigned_vendor'),)
                    )
                    vendor_name = vendor_info[0]['company_name'] if vendor_info else safe_get(request, 'assigned_vendor')
                    st.write(f"**👥 Assigned Vendor:** {vendor_name}")
                
                if safe_get(request, 'completion_notes'):
                    st.write(f"**📝 Completion Notes:** {safe_str(safe_get(request, 'completion_notes'))}")
                
                if safe_get(request, 'job_breakdown'):
                    st.write(f"**🔧 Job Breakdown:** {safe_str(safe_get(request, 'job_breakdown'))}")
                
                if safe_get(request, 'completed_date'):
                    st.write(f"**📅 Completed Date:** {safe_str(safe_get(request, 'completed_date'))}")
                
                if safe_get(request, 'invoice_amount'):
                    st.write(f"**💰 Invoice Amount:** {format_naira(safe_get(request, 'invoice_amount'))}")
                
                if safe_get(request, 'invoice_number'):
                    st.write(f"**🔢 Invoice Number:** {safe_str(safe_get(request, 'invoice_number'))}")
                st.markdown('</div>', unsafe_allow_html=True)

def show_vendor_management():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("👥 Vendor Management")
    st.markdown('</div>', unsafe_allow_html=True)
    
    vendors = execute_query('SELECT * FROM vendors ORDER BY company_name')
    
    if not vendors:
        st.info("📭 No vendors registered yet")
        return
    
    st.subheader(f"📊 Registered Vendors ({len(vendors)})")
    
    for vendor in vendors:
        with st.expander(f"{safe_str(safe_get(vendor, 'company_name'))} - {safe_str(safe_get(vendor, 'vendor_type'))}"):
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
                st.write(f"**Username:** {safe_str(safe_get(vendor, 'username'), 'N/A')}")
                st.markdown('</div>', unsafe_allow_html=True)

def show_reports():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("📈 Reports & Analytics")
    st.markdown('</div>', unsafe_allow_html=True)
    
    all_requests = get_all_requests()
    
    if not all_requests:
        st.info("📭 No data available for reports")
        return
    
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
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if not df.empty:
            status_counts = df['status'].value_counts()
            fig = px.pie(values=status_counts.values, names=status_counts.index, 
                        title="📊 Request Status Distribution")
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if not df.empty:
            priority_counts = df['priority'].value_counts()
            fig = px.bar(x=priority_counts.index, y=priority_counts.values,
                        title="🚨 Requests by Priority", labels={'x': 'Priority', 'y': 'Count'})
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if not df.empty:
            facility_counts = df['facility_type'].value_counts()
            fig = px.bar(y=facility_counts.index, x=facility_counts.values,
                        title="🏢 Requests by Facility Type", orientation='h',
                        labels={'x': 'Count', 'y': 'Facility Type'})
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if not df.empty:
            location_counts = df['location'].value_counts().head(10)
            fig = px.bar(y=location_counts.index, x=location_counts.values,
                        title="📍 Top 10 Locations", orientation='h',
                        labels={'x': 'Count', 'y': 'Location'})
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📅 Monthly Trends")
    if not df.empty and 'created_date' in df.columns:
        df['month'] = df['created_date'].dt.to_period('M')
        monthly_trends = df.groupby('month').size().reset_index(name='count')
        monthly_trends['month'] = monthly_trends['month'].astype(str)
        
        fig = px.line(monthly_trends, x='month', y='count', 
                     title="📈 Monthly Request Trends", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    st.subheader("📤 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export to CSV", use_container_width=True, key="export_csv"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"facilities_management_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key="download_csv"
            )
    
    with col2:
        if st.button("📄 Export to PDF", use_container_width=True, key="export_pdf"):
            # Generate a summary PDF report
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            
            # Add content to PDF
            c.setFont("Helvetica-Bold", 16)
            c.drawString(100, 750, "Facilities Management System - Report")
            
            c.setFont("Helvetica", 12)
            c.drawString(100, 730, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            c.drawString(100, 710, f"Total Requests: {len(df)}")
            c.drawString(100, 690, f"Completed: {len(df[df['status'] == 'Completed'])}")
            c.drawString(100, 670, f"Pending: {len(df[df['status'] == 'Pending'])}")
            c.drawString(100, 650, f"Total Invoice Amount: {format_naira(df['invoice_amount'].sum())}")
            
            c.showPage()
            c.save()
            
            buffer.seek(0)
            st.download_button(
                label="⬇️ Download PDF Report",
                data=buffer,
                file_name=f"facilities_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                key="download_pdf"
            )

def show_assigned_jobs():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🔧 Assigned Jobs")
    st.markdown('</div>', unsafe_allow_html=True)
    
    vendor_requests = get_vendor_requests(st.session_state.user['username'])
    assigned_jobs = [r for r in vendor_requests if safe_get(r, 'status') == 'Assigned']
    
    if not assigned_jobs:
        st.success("🎉 No assigned jobs found - all caught up!")
        return
    
    st.subheader(f"📊 You have {len(assigned_jobs)} assigned job(s)")
    
    for job in assigned_jobs:
        with st.expander(f"Job #{safe_get(job, 'id')}: {safe_str(safe_get(job, 'title'), 'N/A')} - {safe_str(safe_get(job, 'priority'), 'N/A')} Priority"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.write(f"**📍 Location:** {safe_str(safe_get(job, 'location'), 'Common Area')}")
                st.write(f"**🏢 Facility Type:** {safe_str(safe_get(job, 'facility_type'), 'N/A')}")
                st.write(f"**📄 Description:** {safe_str(safe_get(job, 'description'), 'N/A')}")
                st.write(f"**👤 Created By:** {safe_str(safe_get(job, 'created_by'), 'N/A')}")
                st.write(f"**📅 Created Date:** {safe_str(safe_get(job, 'created_date'), 'N/A')}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("✅ Complete Job")
                with st.form(f"complete_job_{safe_get(job, 'id')}", clear_on_submit=True):
                    completion_notes = st.text_area("📝 Completion Notes")
                    job_breakdown = st.text_area("🔧 Breakdown of Job Done", height=100, 
                                               placeholder="Provide detailed breakdown of work completed...")
                    completion_date = st.date_input("📅 Date Completed")
                    invoice_amount = st.number_input("💰 Invoice Amount (₦)", min_value=0.0, step=0.01, format="%.2f")
                    invoice_number = st.text_input("🔢 Invoice Number")
                    
                    submit_button = st.form_submit_button("✅ Submit Completion", use_container_width=True)
                    
                    if submit_button:
                        if not all([completion_notes, job_breakdown, completion_date, invoice_amount, invoice_number]):
                            st.error("⚠️ Please fill in all fields")
                        else:
                            if execute_update(
                                '''UPDATE maintenance_requests SET status = ?, completion_notes = ?, job_breakdown = ?, 
                                completed_date = ?, invoice_amount = ?, invoice_number = ? WHERE id = ?''',
                                ('Completed', completion_notes, job_breakdown, completion_date.strftime('%Y-%m-%d'), 
                                 invoice_amount, invoice_number, safe_get(job, 'id'))
                            ):
                                st.success("✅ Job completed successfully! Waiting for approvals.")
                                st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

def show_completed_jobs():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("✅ Completed Jobs")
    st.markdown('</div>', unsafe_allow_html=True)
    
    vendor_requests = get_vendor_requests(st.session_state.user['username'])
    completed_jobs = [r for r in vendor_requests if safe_get(r, 'status') in ['Completed', 'Approved']]
    
    if not completed_jobs:
        st.info("📭 No completed jobs found")
        return
    
    st.subheader(f"📊 You have completed {len(completed_jobs)} job(s)")
    
    display_data = []
    for job in completed_jobs:
        display_data.append({
            'ID': safe_get(job, 'id'),
            'Title': safe_str(safe_get(job, 'title'), 'N/A'),
            'Location': safe_str(safe_get(job, 'location'), 'Common Area'),
            'Facility': safe_str(safe_get(job, 'facility_type'), 'N/A'),
            'Invoice Amount': format_naira(safe_get(job, 'invoice_amount')),
            'Invoice Number': safe_str(safe_get(job, 'invoice_number'), 'N/A'),
            'Status': safe_str(safe_get(job, 'status'), 'N/A'),
            'Completed Date': safe_str(safe_get(job, 'completed_date'), 'N/A')[:10]
        })
    
    df = pd.DataFrame(display_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

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
        
        submitted = st.form_submit_button("🚀 Register Vendor", use_container_width=True)
        
        if submitted:
            if not all([company_name, contact_person, email, phone, services_offered, address]):
                st.error("⚠️ Please fill in all required fields (*)")
            else:
                success = execute_update(
                    '''INSERT INTO vendors 
                    (username, company_name, contact_person, email, phone, vendor_type, services_offered, 
                    annual_turnover, tax_identification_number, rc_number, key_management_staff, 
                    account_details, certification, address) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (st.session_state.user['username'], company_name, contact_person, email, phone, 
                     st.session_state.user['vendor_type'], services_offered, annual_turnover, 
                     tax_identification_number, rc_number, key_management_staff, 
                     account_details, certification, address)
                )
                if success:
                    st.success("✅ Vendor registration completed successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to complete registration")

def show_invoice_creation():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🧾 Invoice Creation")
    st.markdown('</div>', unsafe_allow_html=True)
    
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
    selected_job_key = st.selectbox("Choose a completed job", list(job_options.keys()), key="invoice_job_select")
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
        
        with st.form("invoice_creation_form", clear_on_submit=True):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            
            with col1:
                invoice_number = st.text_input("🔢 Invoice Number *")
                invoice_date = st.date_input("📅 Invoice Date *")
                details_of_work = st.text_area("🔧 Details of Work Done *", height=100,
                                             value=safe_str(safe_get(selected_job, 'job_breakdown'), ''))
                quantity = st.number_input("📦 Quantity *", min_value=1, value=1)
            
            with col2:
                unit_cost = st.number_input("💵 Unit Cost (₦) *", min_value=0.0, step=0.01, format="%.2f")
                labour_charge = st.number_input("👷 Labour/Service Charge (₦)", min_value=0.0, step=0.01, format="%.2f")
                vat_applicable = st.checkbox("🏛️ Apply VAT (7.5%)")
            
            amount = quantity * unit_cost
            subtotal = amount + labour_charge
            vat_amount = subtotal * 0.075 if vat_applicable else 0
            total_amount = subtotal + vat_amount
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
            st.subheader("🧮 Invoice Summary")
            
            calc_col1, calc_col2, calc_col3, calc_col4 = st.columns(4)
            with calc_col1:
                st.markdown(f'<div class="metric-card"><h4>Amount</h4><h3 class="currency-naira">{format_naira(amount)}</h3></div>', unsafe_allow_html=True)
            with calc_col2:
                st.markdown(f'<div class="metric-card"><h4>Labour Charge</h4><h3 class="currency-naira">{format_naira(labour_charge)}</h3></div>', unsafe_allow_html=True)
            with calc_col3:
                st.markdown(f'<div class="metric-card"><h4>VAT Amount</h4><h3 class="currency-naira">{format_naira(vat_amount)}</h3></div>', unsafe_allow_html=True)
            with calc_col4:
                st.markdown(f'<div class="metric-card"><h4>Total Amount</h4><h3 class="currency-naira">{format_naira(total_amount)}</h3></div>', unsafe_allow_html=True)
            
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
                            st.rerun()
                        else:
                            st.error("❌ Failed to create invoice")

def show_job_invoice_reports():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("📋 Job & Invoice Reports")
    st.markdown('</div>', unsafe_allow_html=True)
    
    completed_jobs = execute_query('''
        SELECT mr.*, i.invoice_number, i.invoice_date, i.total_amount as invoice_total, i.status as invoice_status
        FROM maintenance_requests mr
        LEFT JOIN invoices i ON mr.id = i.request_id
        WHERE mr.status IN ('Completed', 'Approved')
        ORDER BY mr.completed_date DESC
    ''')
    
    if not completed_jobs:
        st.info("📭 No completed jobs with invoices found")
        return
    
    col1, col2, col3 = st.columns(3)
    with col1:
        status_options = ["All"] + list(set(safe_str(safe_get(job, 'status')) for job in completed_jobs))
        status_filter = st.selectbox("Filter by Job Status", status_options, key="job_status")
    with col2:
        location_options = ["All"] + list(set(safe_str(safe_get(job, 'location'), 'Common Area') for job in completed_jobs))
        location_filter = st.selectbox("Filter by Location", location_options, key="job_location")
    with col3:
        has_invoice_filter = st.selectbox("Filter by Invoice", ["All", "With Invoice", "Without Invoice"], key="job_invoice")
    
    filtered_jobs = completed_jobs
    if status_filter != "All":
        filtered_jobs = [job for job in filtered_jobs if safe_str(safe_get(job, 'status')) == status_filter]
    if location_filter != "All":
        filtered_jobs = [job for job in filtered_jobs if safe_str(safe_get(job, 'location'), 'Common Area') == location_filter]
    if has_invoice_filter == "With Invoice":
        filtered_jobs = [job for job in filtered_jobs if safe_get(job, 'invoice_number') is not None]
    elif has_invoice_filter == "Without Invoice":
        filtered_jobs = [job for job in filtered_jobs if safe_get(job, 'invoice_number') is None]
    
    st.subheader(f"📊 Found {len(filtered_jobs)} job(s)")
    
    for job in filtered_jobs:
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
                else:
                    st.write("**No invoice created yet**")
                
                st.write("**✅ Approval Status**")
                st.write(f"**Department Approval:** {'✅ Approved' if safe_get(job, 'requesting_dept_approval') else '⏳ Pending'}")
                st.write(f"**Manager Approval:** {'✅ Approved' if safe_get(job, 'facilities_manager_approval') else '⏳ Pending'}")
                st.markdown('</div>', unsafe_allow_html=True)

# Updated navigation menu to include new features
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


