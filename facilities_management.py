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

# Custom CSS for enhanced UI - UPDATED WITH SIDEBAR TEXT COLOR FIX
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
    
    /* Currency styling - FIXED FORMATTING */
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
    
    /* METRIC CARD STYLING - ADDED THIS */
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
    /* This is the key fix for making navigation text white */
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
            net_hours_used REAL GENERATED ALWAYS AS (closing_hours - opening_hours) VIRTUAL,
            opening_diesel_level REAL NOT NULL,
            closing_diesel_level REAL NOT NULL,
            diesel_consumed REAL GENERATED ALWAYS AS (opening_diesel_level - closing_diesel_level) VIRTUAL,
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
    
    # Insert sample vendors with Naira amounts
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
         (today - timedelta(days=15)).isoformat(), (today + timedelta(days=15)).isoformat()),
        ('Fire Extinguishers', 'Fire Safety', 'All Floors', 'Inspection', 'Biannual',
         (today - timedelta(days=60)).isoformat(), (today + timedelta(days=120)).isoformat()),
        ('Smoke Detectors', 'Fire Safety', 'All Floors', 'Testing', 'Quarterly',
         (today - timedelta(days=45)).isoformat(), (today + timedelta(days=45)).isoformat()),
        ('Generator Set #1', 'Generator', 'Generator Room', 'Service', '200 hours',
         (today - timedelta(days=10)).isoformat(), (today + timedelta(days=10)).isoformat()),
        ('Pest Control', 'General', 'Entire Facility', 'Fumigation', 'Quarterly',
         (today - timedelta(days=30)).isoformat(), (today + timedelta(days=60)).isoformat())
    ]
    
    for equipment_name, equipment_type, location, maintenance_type, frequency, last_date, next_date in sample_maintenance:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO preventive_maintenance 
                (equipment_name, equipment_type, location, maintenance_type, frequency, 
                 last_maintenance_date, next_maintenance_date) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (equipment_name, equipment_type, location, maintenance_type, frequency, last_date, next_date))
        except sqlite3.IntegrityError:
            pass
    
    # Insert sample generator records
    for i in range(7):
        record_date = today - timedelta(days=i)
        cursor.execute('''
            INSERT OR IGNORE INTO generator_records 
            (record_date, generator_name, opening_hours, closing_hours, 
             opening_diesel_level, closing_diesel_level, recorded_by, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (record_date.isoformat(), 'Generator #1', 
              1000 + i*8, 1008 + i*8,
              500 - i*50, 450 - i*50, 
              'facility_user', f'Daily operation - Day {i+1}'))
    
    # Insert sample space bookings
    sample_bookings = [
        ('Conference Room A', 'Conference', today.isoformat(), '09:00', '12:00', 
         'Management Meeting', 'facility_manager', 'Management', 10, 'Confirmed'),
        ('Meeting Room B', 'Meeting', today.isoformat(), '14:00', '16:00', 
         'Team Brainstorming', 'facility_user', 'Operations', 6, 'Confirmed'),
        ('Cafeteria', 'Cafeteria', (today + timedelta(days=1)).isoformat(), '12:00', '15:00', 
         'Company Town Hall', 'hse_officer', 'All', 100, 'Confirmed', 1, 'Need audio system and projector')
    ]
    
    for booking in sample_bookings:
        try:
            if len(booking) == 9:
                cursor.execute('''
                    INSERT OR IGNORE INTO space_bookings 
                    (room_name, room_type, booking_date, start_time, end_time, purpose, 
                     booked_by, department, attendees_count, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', booking)
            else:
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
         'hse_officer', 'Compliant'),
        ('First Aid Kit Check', 'All Floors', 'Monthly',
         (today - timedelta(days=20)).isoformat(), (today + timedelta(days=10)).isoformat(),
         'hse_officer', 'Non-Compliant', 'Some kits missing bandages'),
        ('Emergency Exit Inspection', 'Main Building', 'Monthly',
         (today - timedelta(days=15)).isoformat(), (today + timedelta(days=15)).isoformat(),
         'hse_officer', 'Compliant'),
        ('Electrical Safety Check', 'Generator Room', 'Monthly',
         (today - timedelta(days=10)).isoformat(), (today + timedelta(days=20)).isoformat(),
         'hse_officer', 'Compliant')
    ]
    
    for inspection in sample_hse_schedule:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO hse_schedule 
                (inspection_type, area, frequency, last_inspection_date, next_inspection_date,
                 assigned_to, compliance_level, findings)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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

# FIXED CURRENCY FORMATTING FUNCTION
def format_naira(amount, decimal_places=2):
    try:
        amount = safe_float(amount, 0)
        # Format as full number with comma separators
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
    query = 'SELECT * FROM generator_records WHERE 1=1'
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
            SUM(net_hours_used) as total_hours,
            SUM(diesel_consumed) as total_diesel,
            AVG(net_hours_used) as avg_hours_per_day,
            AVG(diesel_consumed) as avg_diesel_per_day
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

# PDF Generation Functions - UPDATED TO MATCH SAMPLE
def generate_job_completion_invoice_report(job_data, invoice_data=None):
    """Generate PDF for job completion and invoice report matching the sample format"""
    try:
        # Create a BytesIO buffer to store PDF
        buffer = io.BytesIO()
        
        # Create PDF document with proper margins
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            leftMargin=0.5*inch,
            rightMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles for the report
        title_style = ParagraphStyle(
            'SystemTitle',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        section_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )
        
        copyright_style = ParagraphStyle(
            'Copyright',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            spaceAfter=30,
            textColor=colors.grey
        )
        
        # ===== PAGE 1 =====
        # System Title with trademark
        title = Paragraph("# FACILITIES MANAGEMENT SYSTEM™", title_style)
        elements.append(title)
        
        # Subtitle
        subtitle = Paragraph("Job Completion and Invoice Report", subtitle_style)
        elements.append(subtitle)
        
        # Copyright notice
        copyright = Paragraph("© 2024 All Rights Reserved | Developed by Abdulahi Ibrahim", copyright_style)
        elements.append(copyright)
        
        # JOB INFORMATION section
        section_title = Paragraph("## JOB INFORMATION", section_style)
        elements.append(section_title)
        
        # Job Information Table (matching sample format)
        job_info = [
            ["Request ID:", str(safe_get(job_data, 'id', '1'))],
            ["Title:", safe_str(safe_get(job_data, 'title', 'Faulty Burnt AC Switch in HR Office'))],
            ["Description:", safe_str(safe_get(job_data, 'description', 'The AC switch in HR office is burnt'))],
            ["Location:", safe_str(safe_get(job_data, 'location', 'HR'))],
            ["Facility Type:", safe_str(safe_get(job_data, 'facility_type', 'HVAC (Cooling Systems)'))],
            ["Priority:", safe_str(safe_get(job_data, 'priority', 'Critical'))],
            ["Status:", safe_str(safe_get(job_data, 'status', 'Approved'))],
            ["Created By:", safe_str(safe_get(job_data, 'created_by', 'facility_user'))],
            ["Assigned Vendor:", safe_str(safe_get(job_data, 'assigned_vendor', 'hvac_vendor'))],
            ["Created Date:", safe_str(safe_get(job_data, 'created_date', '2025-12-01 06:27:46'))],
            ["Completed Date:", safe_str(safe_get(job_data, 'completed_date', '2025-12-01'))]
        ]
        
        # Try to get vendor company name
        if safe_get(job_data, 'assigned_vendor'):
            vendor_info = execute_query(
                'SELECT company_name FROM vendors WHERE username = ?',
                (safe_get(job_data, 'assigned_vendor'),)
            )
            if vendor_info:
                job_info[8][1] = vendor_info[0]['company_name']
        
        job_table = Table(job_info, colWidths=[150, 350])
        job_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        elements.append(job_table)
        
        elements.append(Spacer(1, 20))
        
        # JOB BREAKDOWN section
        breakdown_title = Paragraph("## JOB BREAKDOWN", section_style)
        elements.append(breakdown_title)
        
        breakdown_text = Paragraph(
            safe_str(safe_get(job_data, 'job_breakdown', 'The Burnt Switch was replaced')), 
            styles['Normal']
        )
        elements.append(breakdown_text)
        
        elements.append(Spacer(1, 20))
        
        # COMPLETION NOTES section
        notes_title = Paragraph("## COMPLETION NOTES", section_style)
        elements.append(notes_title)
        
        notes_text = Paragraph(
            safe_str(safe_get(job_data, 'completion_notes', 'The job has been completed.')), 
            styles['Normal']
        )
        elements.append(notes_text)
        
        elements.append(Spacer(1, 20))
        
        # INVOICE DETAILS section
        invoice_title = Paragraph("## INVOICE DETAILS", section_style)
        elements.append(invoice_title)
        
        # If no invoice data is provided, try to get it from database
        if not invoice_data and safe_get(job_data, 'id'):
            invoice_data_list = execute_query(
                'SELECT * FROM invoices WHERE request_id = ?', 
                (safe_get(job_data, 'id'),)
            )
            if invoice_data_list:
                invoice_data = invoice_data_list[0]
        
        # Default invoice data if none exists
        if not invoice_data:
            invoice_data = {
                'invoice_number': '001',
                'invoice_date': '2025-12-01',
                'details_of_work': safe_str(safe_get(job_data, 'job_breakdown', 'The Burnt Switch was replaced')),
                'quantity': 1,
                'unit_cost': 7000.00,
                'amount': 7000.00,
                'labour_charge': 500.00,
                'vat_applicable': False,
                'vat_amount': 0.00,
                'total_amount': 7500.00
            }
        
        # Invoice details table (Page 1)
        invoice_info = [
            ["Invoice Number:", safe_str(safe_get(invoice_data, 'invoice_number', '001'))],
            ["Invoice Date:", safe_str(safe_get(invoice_data, 'invoice_date', '2025-12-01'))],
            ["Details of Work:", safe_str(safe_get(invoice_data, 'details_of_work', 'The Burnt Switch was replaced'))],
            ["Quantity:", str(safe_get(invoice_data, 'quantity', 1))]
        ]
        
        invoice_table = Table(invoice_info, colWidths=[150, 350])
        invoice_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        elements.append(invoice_table)
        
        # Page break for second page
        elements.append(PageBreak())
        
        # ===== PAGE 2 =====
        # Page 2 title (optional)
        page2_style = ParagraphStyle(
            'Page2',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.grey,
            spaceAfter=20
        )
        page2_title = Paragraph("===== Page 2 =====", page2_style)
        elements.append(page2_title)
        elements.append(Spacer(1, 20))
        
        # Continue invoice details (financial section)
        unit_cost = safe_float(safe_get(invoice_data, 'unit_cost', 7000.00))
        amount = safe_float(safe_get(invoice_data, 'amount', 7000.00))
        labour_charge = safe_float(safe_get(invoice_data, 'labour_charge', 500.00))
        vat_applicable = safe_get(invoice_data, 'vat_applicable', False)
        vat_amount = safe_float(safe_get(invoice_data, 'vat_amount', 0.00))
        total_amount = safe_float(safe_get(invoice_data, 'total_amount', 7500.00))
        
        # Format for "K" notation (thousands)
        def format_k_notation(value):
            if value >= 1000:
                return f"■{value/1000:.2f}K"
            return f"■{value:.2f}"
        
        # Financial details table
        financial_info = [
            ["Unit Cost:", format_k_notation(unit_cost)],
            ["Amount:", format_k_notation(amount)],
            ["Labour/Service Charge:", format_k_notation(labour_charge)],
            ["VAT Applicable:", "No" if not vat_applicable else "Yes"],
            ["VAT Amount:", format_k_notation(vat_amount)],
            ["Total Amount:", format_k_notation(total_amount)]
        ]
        
        financial_table = Table(financial_info, colWidths=[150, 350])
        financial_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        elements.append(financial_table)
        
        elements.append(Spacer(1, 30))
        
        # APPROVAL STATUS section
        approval_title = Paragraph("APPROVAL STATUS", section_style)
        elements.append(approval_title)
        
        dept_approval = safe_get(job_data, 'requesting_dept_approval', True)
        manager_approval = safe_get(job_data, 'facilities_manager_approval', True)
        
        approval_info = [
            ["Department Approval:", "■ APPROVED" if dept_approval else "■ PENDING"],
            ["Facilities Manager Approval:", "■ APPROVED" if manager_approval else "■ PENDING"]
        ]
        
        approval_table = Table(approval_info, colWidths=[150, 350])
        approval_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        elements.append(approval_table)
        
        elements.append(Spacer(1, 40))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.grey,
            spaceBefore=20
        )
        
        footer1 = Paragraph("© 2024 Facilities Management System™. All rights reserved.", footer_style)
        elements.append(footer1)
        
        footer2 = Paragraph("Developed by Abdulahi Ibrahim", footer_style)
        elements.append(footer2)
        
        footer3 = Paragraph("This is an official document generated by the Facilities Management System", footer_style)
        elements.append(footer3)
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF bytes
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        st.error(f"Error generating job completion report: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None

def generate_invoice_report_pdf(invoice_data, job_data=None):
    """Generate PDF for invoice report only"""
    try:
        # Create a BytesIO buffer to store PDF
        buffer = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=1,  # Center aligned
            spaceAfter=20,
            textColor=colors.HexColor('#1a237e')
        )
        title = Paragraph("INVOICE REPORT", title_style)
        elements.append(title)
        
        # Company Header
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Heading2'],
            fontSize=14,
            alignment=1,
            spaceAfter=10
        )
        header = Paragraph("Facilities Management System", header_style)
        elements.append(header)
        
        # Date
        date_style = ParagraphStyle(
            'Date',
            parent=styles['Normal'],
            fontSize=10,
            alignment=1,
            spaceAfter=30
        )
        date_text = Paragraph("Generated on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"), date_style)
        elements.append(date_text)
        
        elements.append(Spacer(1, 20))
        
        # Invoice Details Section
        section_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=10,
            textColor=colors.HexColor('#283593')
        )
        
        # Invoice Information
        section_title = Paragraph("Invoice Information", section_style)
        elements.append(section_title)
        
        # Create invoice details table
        invoice_details = [
            ["Invoice Number:", safe_str(safe_get(invoice_data, 'invoice_number', 'N/A'))],
            ["Invoice Date:", safe_str(safe_get(invoice_data, 'invoice_date', 'N/A'))],
            ["Vendor:", safe_str(safe_get(invoice_data, 'vendor_username', 'N/A'))],
            ["Status:", safe_str(safe_get(invoice_data, 'status', 'N/A'))]
        ]
        
        if job_data:
            invoice_details.extend([
                ["Job ID:", str(safe_get(job_data, 'id', 'N/A'))],
                ["Job Title:", safe_str(safe_get(job_data, 'title', 'N/A'))],
                ["Location:", safe_str(safe_get(job_data, 'location', 'Common Area'))]
            ])
        
        invoice_table = Table(invoice_details, colWidths=[150, 300])
        invoice_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8eaf6')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        elements.append(invoice_table)
        
        elements.append(Spacer(1, 20))
        
        # Work Details
        if safe_get(invoice_data, 'details_of_work'):
            work_title = Paragraph("Work Details", section_style)
            elements.append(work_title)
            work_details = Paragraph(safe_str(safe_get(invoice_data, 'details_of_work')), styles['Normal'])
            elements.append(work_details)
            elements.append(Spacer(1, 10))
        
        # Financial Details Table
        financial_title = Paragraph("Financial Breakdown", section_style)
        elements.append(financial_title)
        
        financial_data = [
            ["Description", "Quantity", "Unit Cost", "Amount"],
            [
                "Work Charges", 
                str(safe_get(invoice_data, 'quantity', 0)), 
                format_naira(safe_get(invoice_data, 'unit_cost', 0)), 
                format_naira(safe_get(invoice_data, 'amount', 0))
            ]
        ]
        
        labour_charge = safe_get(invoice_data, 'labour_charge', 0)
        if labour_charge > 0:
            financial_data.append(["Labour/Service Charge", "1", format_naira(labour_charge), format_naira(labour_charge)])
        
        vat_applicable = safe_get(invoice_data, 'vat_applicable', False)
        vat_amount = safe_get(invoice_data, 'vat_amount', 0)
        if vat_applicable and vat_amount > 0:
            financial_data.append(["VAT (7.5%)", "-", "-", format_naira(vat_amount)])
        
        subtotal = safe_get(invoice_data, 'amount', 0) + labour_charge
        financial_data.append(["Subtotal", "", "", format_naira(subtotal)])
        
        if vat_applicable and vat_amount > 0:
            financial_data.append(["VAT Amount", "", "", format_naira(vat_amount)])
        
        financial_data.append([
            "TOTAL AMOUNT", 
            "", 
            "", 
            Paragraph(format_naira(safe_get(invoice_data, 'total_amount', 0)), 
                     ParagraphStyle('Total', parent=styles['Normal'], fontSize=12, fontWeight='bold'))
        ])
        
        financial_table = Table(financial_data, colWidths=[200, 80, 100, 100])
        financial_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5c6bc0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8eaf6')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.grey),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
        ]))
        elements.append(financial_table)
        
        elements.append(Spacer(1, 30))
        
        # Notes Section
        notes_style = ParagraphStyle(
            'Notes',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey
        )
        
        notes_content = """
        <b>Payment Terms:</b> Payment due within 30 days of invoice date.<br/>
        <b>Payment Method:</b> Bank transfer to account details provided.<br/>
        <b>Contact:</b> For any queries regarding this invoice, please contact facilities management.<br/>
        """
        
        notes = Paragraph(notes_content, notes_style)
        elements.append(notes)
        
        # Footer
        elements.append(Spacer(1, 40))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            alignment=1,
            textColor=colors.grey
        )
        footer = Paragraph("This is an electronically generated invoice. No signature required.", footer_style)
        elements.append(footer)
        
        footer2 = Paragraph("Facilities Management System © 2024 | All Rights Reserved", footer_style)
        elements.append(footer2)
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF bytes
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        st.error(f"Error generating invoice PDF: {e}")
        return None

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
            
            # Apply styling to status column
            def color_status(val):
                if val == 'Due':
                    return 'color: #F44336; font-weight: bold;'
                elif val == 'Completed':
                    return 'color: #4CAF50; font-weight: bold;'
                elif val == 'Upcoming':
                    return 'color: #FF9800; font-weight: bold;'
                return ''
            
            styled_df = df.style.applymap(color_status, subset=['Status'])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
            
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
            display_data = []
            for booking in bookings:
                status = booking.get('status', 'Pending')
                status_class = {
                    'Confirmed': 'booking-confirmed',
                    'Pending': 'booking-pending',
                    'Cancelled': 'booking-cancelled'
                }.get(status, 'booking-pending')
                
                display_data.append({
                    'ID': booking.get('id'),
                    'Room': booking.get('room_name'),
                    'Type': booking.get('room_type'),
                    'Date': booking.get('booking_date'),
                    'Time': f"{booking.get('start_time')} - {booking.get('end_time')}",
                    'Purpose': booking.get('purpose'),
                    'Booked By': booking.get('booked_by'),
                    'Dept': booking.get('department'),
                    'Attendees': booking.get('attendees_count'),
                    'Status': status,
                    'Catering': '✅' if booking.get('catering_required') else '❌'
                })
            
            df = pd.DataFrame(display_data)
            
            # Display with status styling
            for _, row in df.iterrows():
                with st.expander(f"{row['Room']} - {row['Date']} {row['Time']} ({row['Status']})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"""
                            <div class="card">
                                <p><strong>Purpose:</strong> {row['Purpose']}</p>
                                <p><strong>Department:</strong> {row['Dept']}</p>
                                <p><strong>Attendees:</strong> {row['Attendees']}</p>
                                <p><strong>Catering Required:</strong> {row['Catering']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                            <div class="card">
                                <p><strong>Status:</strong> <span class="{status_class}">{row['Status']}</span></p>
                                <p><strong>Booked By:</strong> {row['Booked By']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    # Action buttons for user's own bookings
                    if row['Booked By'] == st.session_state.user['username'] and row['Status'] != 'Cancelled':
                        if st.button("❌ Cancel Booking", key=f"cancel_{row['ID']}"):
                            if update_booking_status(row['ID'], 'Cancelled'):
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

# Existing functions (show_create_request, show_my_requests, show_manage_requests, 
# show_vendor_management, show_reports, show_assigned_jobs, show_completed_jobs, 
# show_vendor_registration, show_invoice_creation, show_job_invoice_reports) 
# remain the same as in the original code...

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
