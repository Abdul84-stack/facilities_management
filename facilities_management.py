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
import numpy as np

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
    
    .currency-symbol {
        font-weight: bold;
        color: #4CAF50;
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
    
    /* Dataframe styling */
    .dataframe {
        font-size: 14px;
    }
    
    /* Spinner container */
    .stSpinner > div {
        border-color: #4CAF50 !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50 !important;
        color: white !important;
    }
    
    /* Form improvements */
    .stForm {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        background: white;
    }
    
    /* Loading improvements */
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
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
    
    # Create maintenance_requests table with approval workflow
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
            facilities_manager_approval BOOLEAN DEFAULT 0,
            vendor_completion_approval BOOLEAN DEFAULT 0
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
            audited_financial_statement BLOB,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    
    # HSE Schedule and Inspections - Reduced to 5
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
    
    # HSE Incidents - Optimized for performance
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
    
    # Insert sample HSE schedule - Reduced to 5
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
        ('PPE Inspection', 'Workshop Area', 'Weekly',
         (today - timedelta(days=3)).isoformat(), (today + timedelta(days=4)).isoformat(),
         'hse_officer', 'Non-Compliant', 'Some PPE missing', 'Order new PPE', (today + timedelta(days=2)).isoformat()),
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
    
    # Create indexes for performance optimization
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_maintenance_requests_status ON maintenance_requests(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_hse_incidents_date ON hse_incidents(incident_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_space_bookings_date ON space_bookings(booking_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_generator_records_date ON generator_records(record_date)')
    
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
        if amount >= 1000000:
            return f"₦{amount/1000000:.{decimal_places}f}M"
        elif amount >= 1000:
            return f"₦{amount/1000:.{decimal_places}f}K"
        else:
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

# Vendor Management Functions
@st.cache_data(ttl=300)
def get_vendor_details(username):
    result = execute_query('SELECT * FROM vendors WHERE username = ?', (username,))
    return result[0] if result else None

def update_vendor_details(username, updates):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Build update query dynamically
    update_fields = []
    update_values = []
    
    for key, value in updates.items():
        if value is not None:
            update_fields.append(f"{key} = ?")
            update_values.append(value)
    
    update_values.append(username)  # For WHERE clause
    
    if update_fields:
        query = f"UPDATE vendors SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP WHERE username = ?"
        try:
            cursor.execute(query, update_values)
            conn.commit()
            return True
        except Exception as e:
            st.error(f"Error updating vendor: {e}")
            return False
    
    return False

# Request Management Functions
def create_maintenance_request(title, description, location, facility_type, priority, created_by):
    return execute_update('''
        INSERT INTO maintenance_requests 
        (title, description, location, facility_type, priority, created_by, status)
        VALUES (?, ?, ?, ?, ?, ?, 'Pending')
    ''', (title, description, location, facility_type, priority, created_by))

@st.cache_data(ttl=300)
def get_assigned_jobs(vendor_username):
    return execute_query('''
        SELECT * FROM maintenance_requests 
        WHERE assigned_vendor = ? AND status IN ('Assigned', 'In Progress')
        ORDER BY created_date DESC
    ''', (vendor_username,))

def complete_job(job_id, completion_notes):
    return execute_update('''
        UPDATE maintenance_requests 
        SET status = 'Completed', 
            completed_date = CURRENT_TIMESTAMP,
            completion_notes = ?,
            vendor_completion_approval = 1
        WHERE id = ?
    ''', (completion_notes, job_id))

def approve_job_completion(job_id):
    return execute_update('''
        UPDATE maintenance_requests 
        SET facilities_manager_approval = 1,
            status = 'Approved'
        WHERE id = ?
    ''', (job_id,))

def get_jobs_for_approval():
    return execute_query('''
        SELECT * FROM maintenance_requests 
        WHERE vendor_completion_approval = 1 
        AND (requesting_dept_approval = 0 OR facilities_manager_approval = 0)
        ORDER BY completed_date DESC
    ''')

# Invoice Creation Functions
def create_invoice(request_id, vendor_username, details_of_work, quantity, unit_cost, labour_charge=0, vat_applicable=False):
    amount = quantity * unit_cost
    subtotal = amount + labour_charge
    vat_amount = subtotal * 0.075 if vat_applicable else 0
    total_amount = subtotal + vat_amount
    
    # Generate invoice number
    invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{request_id:04d}"
    
    return execute_update('''
        INSERT INTO invoices 
        (invoice_number, request_id, vendor_username, details_of_work, quantity, 
         unit_cost, amount, labour_charge, vat_applicable, vat_amount, total_amount, currency)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '₦')
    ''', (invoice_number, request_id, vendor_username, details_of_work, quantity,
          unit_cost, amount, labour_charge, vat_applicable, vat_amount, total_amount))

@st.cache_data(ttl=300)
def get_vendor_invoices(vendor_username):
    return execute_query('''
        SELECT i.*, mr.title, mr.location 
        FROM invoices i
        JOIN maintenance_requests mr ON i.request_id = mr.id
        WHERE i.vendor_username = ?
        ORDER BY i.invoice_date DESC
    ''', (vendor_username,))

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

# Space Management Functions with Analytics
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

@st.cache_data(ttl=300)
def get_space_analytics():
    return execute_query('''
        SELECT 
            room_type,
            COUNT(*) as total_bookings,
            SUM(attendees_count) as total_attendees,
            AVG(attendees_count) as avg_attendees,
            SUM(CASE WHEN catering_required = 1 THEN 1 ELSE 0 END) as catering_requests
        FROM space_bookings 
        WHERE booking_date >= date('now', '-30 days')
        GROUP BY room_type
    ''')

def add_space_booking(room_name, room_type, booking_date, start_time, end_time, purpose,
                     booked_by, department, attendees_count, catering_required, special_requirements):
    return execute_update('''
        INSERT INTO space_bookings 
        (room_name, room_type, booking_date, start_time, end_time, purpose, 
         booked_by, department, attendees_count, catering_required, special_requirements)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (room_name, room_type, booking_date.isoformat(), start_time, end_time, purpose,
          booked_by, department, attendees_count, catering_required, special_requirements))

# HSE Schedule Functions - Optimized for performance
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
def get_hse_incidents_optimized(limit=50):
    return execute_query('''
        SELECT * FROM hse_incidents 
        ORDER BY incident_date DESC 
        LIMIT ?
    ''', (limit,))

@st.cache_data(ttl=300)
def get_hse_compliance_dashboard():
    return execute_query('''
        SELECT 
            inspection_type,
            COUNT(*) as total_inspections,
            SUM(CASE WHEN compliance_level = 'Compliant' THEN 1 ELSE 0 END) as compliant_count,
            SUM(CASE WHEN compliance_level = 'Non-Compliant' THEN 1 ELSE 0 END) as non_compliant_count,
            AVG(CASE WHEN compliance_level = 'Compliant' THEN 100 ELSE 0 END) as compliance_rate
        FROM hse_schedule 
        WHERE last_inspection_date >= date('now', '-90 days')
        GROUP BY inspection_type
    ''')

def add_hse_schedule(inspection_type, area, frequency, next_inspection_date, assigned_to):
    return execute_update('''
        INSERT INTO hse_schedule 
        (inspection_type, area, frequency, next_inspection_date, assigned_to)
        VALUES (?, ?, ?, ?, ?)
    ''', (inspection_type, area, frequency, next_inspection_date.isoformat(), assigned_to))

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
    
    # Approval Status
    story.append(Paragraph("APPROVAL STATUS", subtitle_style))
    approval_data = [
        ["Department Approval:", "✅ Approved" if job_data.get('requesting_dept_approval') else "⏳ Pending"],
        ["Facilities Manager Approval:", "✅ Approved" if job_data.get('facilities_manager_approval') else "⏳ Pending"],
        ["Vendor Completion:", "✅ Approved" if job_data.get('vendor_completion_approval') else "⏳ Pending"]
    ]
    
    approval_table = Table(approval_data, colWidths=[200, 300])
    approval_table.setStyle(TableStyle([
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
    
    story.append(approval_table)
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
            ["Currency:", "₦ (Nigerian Naira)"]
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
                    with st.spinner("Authenticating..."):
                        user = authenticate_user(username, password)
                        if user:
                            st.session_state.user = user
                            st.session_state.navigation_menu = "Dashboard"
                            st.success("Login successful! Redirecting...")
                            time.sleep(1)
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
    with st.spinner("Loading dashboard..."):
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
    st.subheader("🚀 Quick Actions")
    
    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
    
    with col_q1:
        if st.button("📋 Create Request", key="quick_create_request", use_container_width=True):
            st.session_state.navigation_menu = "Create Request"
            st.rerun()
    
    with col_q2:
        if st.button("📅 Book a Room", key="quick_book_room", use_container_width=True):
            st.session_state.navigation_menu = "Space Management"
            st.rerun()
    
    with col_q3:
        if st.button("⛽ Generator Records", key="quick_generator", use_container_width=True):
            st.session_state.navigation_menu = "Generator Records"
            st.rerun()
    
    with col_q4:
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
    with st.spinner("Loading dashboard..."):
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
    st.subheader("🚀 Management Quick Actions")
    
    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
    
    with col_q1:
        if st.button("📋 Manage Requests", key="quick_manage_requests", use_container_width=True):
            st.session_state.navigation_menu = "Manage Requests"
            st.rerun()
    
    with col_q2:
        if st.button("🔧 Maintenance Schedule", key="quick_maintenance", use_container_width=True):
            st.session_state.navigation_menu = "Preventive Maintenance"
            st.rerun()
    
    with col_q3:
        if st.button("🏢 Space Management", key="quick_space", use_container_width=True):
            st.session_state.navigation_menu = "Space Management"
            st.rerun()
    
    with col_q4:
        if st.button("🚨 HSE Dashboard", key="quick_hse", use_container_width=True):
            st.session_state.navigation_menu = "HSE Management"
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
    with st.spinner("Loading HSE dashboard..."):
        hse_schedule_data = get_hse_schedule()
        hse_incidents = get_hse_incidents_optimized()
    
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
    with st.spinner("Loading space dashboard..."):
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
    with st.spinner("Loading vendor dashboard..."):
        vendor_requests = get_vendor_requests(st.session_state.user['username'])
        invoices = get_vendor_invoices(st.session_state.user['username'])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        assigned_count = len([r for r in vendor_requests if safe_get(r, 'status') == 'Assigned'])
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<h4>Assigned Jobs</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3>{assigned_count}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        in_progress_count = len([r for r in vendor_requests if safe_get(r, 'status') == 'In Progress'])
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<h4>In Progress</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3>{in_progress_count}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        completed_count = len([r for r in vendor_requests if safe_get(r, 'status') == 'Completed'])
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<h4>Completed Jobs</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3>{completed_count}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        total_invoice_amount = sum([safe_float(inv.get('total_amount', 0)) for inv in invoices])
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<h4>Total Invoices</h4>', unsafe_allow_html=True)
        st.markdown(f'<h3 class="currency-naira">{format_naira(total_invoice_amount)}</h3>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    # WORKING QUICK ACTIONS FOR VENDORS
    st.subheader("⚡ Vendor Quick Actions")
    
    col_q1, col_q2, col_q3 = st.columns(3)
    
    with col_q1:
        if st.button("🛠️ Update Profile", key="vendor_update_profile", use_container_width=True):
            st.session_state.navigation_menu = "Vendor Management"
            st.rerun()
    
    with col_q2:
        if st.button("📋 Assigned Jobs", key="vendor_assigned_jobs", use_container_width=True):
            st.session_state.navigation_menu = "Assigned Jobs"
            st.rerun()
    
    with col_q3:
        if st.button("🧾 Create Invoice", key="vendor_create_invoice", use_container_width=True):
            st.session_state.navigation_menu = "Invoice Creation"
            st.rerun()
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)

# ========== NEW FEATURE: VENDOR MANAGEMENT ==========

def show_vendor_management():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🏢 Vendor Management")
    st.markdown('</div>', unsafe_allow_html=True)
    
    user = st.session_state.user
    vendor_details = get_vendor_details(user['username'])
    
    if not vendor_details:
        st.error("❌ Vendor profile not found")
        return
    
    tab1, tab2 = st.tabs(["📋 View/Update Profile", "📊 Performance"])
    
    with tab1:
        st.subheader("📋 Vendor Profile Information")
        
        with st.form("vendor_update_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                company_name = st.text_input("Company Name *", value=vendor_details.get('company_name', ''))
                contact_person = st.text_input("Contact Person *", value=vendor_details.get('contact_person', ''))
                email = st.text_input("Email *", value=vendor_details.get('email', ''))
                phone = st.text_input("Phone *", value=vendor_details.get('phone', ''))
                vendor_type = st.selectbox("Vendor Type *", 
                                         ["HVAC", "Generator", "Fixture and Fittings", 
                                          "Building Maintenance", "HSE", "Space Management"],
                                         index=["HVAC", "Generator", "Fixture and Fittings", 
                                                "Building Maintenance", "HSE", "Space Management"].index(vendor_details.get('vendor_type', 'HVAC')))
            
            with col2:
                services_offered = st.text_area("Services Offered *", value=vendor_details.get('services_offered', ''))
                tax_identification_number = st.text_input("Tax ID", value=vendor_details.get('tax_identification_number', ''))
                rc_number = st.text_input("RC Number", value=vendor_details.get('rc_number', ''))
                account_details = st.text_area("Account Details", value=vendor_details.get('account_details', ''))
                address = st.text_area("Address *", value=vendor_details.get('address', ''))
            
            submitted = st.form_submit_button("💾 Update Profile", use_container_width=True)
            
            if submitted:
                if not all([company_name, contact_person, email, phone, vendor_type, services_offered, address]):
                    st.error("⚠️ Please fill in all required fields (*)")
                else:
                    updates = {
                        'company_name': company_name,
                        'contact_person': contact_person,
                        'email': email,
                        'phone': phone,
                        'vendor_type': vendor_type,
                        'services_offered': services_offered,
                        'tax_identification_number': tax_identification_number,
                        'rc_number': rc_number,
                        'account_details': account_details,
                        'address': address
                    }
                    
                    if update_vendor_details(user['username'], updates):
                        st.success("✅ Vendor profile updated successfully!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("❌ Failed to update vendor profile")
    
    with tab2:
        st.subheader("📊 Vendor Performance")
        
        vendor_requests = get_vendor_requests(user['username'])
        invoices = get_vendor_invoices(user['username'])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_jobs = len(vendor_requests)
            st.metric("Total Jobs", total_jobs)
        
        with col2:
            completed_jobs = len([r for r in vendor_requests if r.get('status') == 'Completed'])
            st.metric("Completed Jobs", completed_jobs)
        
        with col3:
            total_invoices = len(invoices)
            st.metric("Total Invoices", total_invoices)
        
        with col4:
            total_revenue = sum([safe_float(inv.get('total_amount', 0)) for inv in invoices])
            st.metric("Total Revenue", format_naira(total_revenue))

# ========== NEW FEATURE: CREATE REQUEST ==========

def show_create_request():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("📋 Create Maintenance Request")
    st.markdown('</div>', unsafe_allow_html=True)
    
    with st.form("create_request_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Request Title *", placeholder="e.g., Leaking pipe in restroom")
            location = st.text_input("Location *", value="Common Area", 
                                   placeholder="e.g., Main Building, Floor 3, Room 301")
            facility_type = st.selectbox("Facility Type *", 
                                       ["HVAC", "Plumbing", "Electrical", "Generator", 
                                        "Building", "Security", "Other"])
        
        with col2:
            priority = st.selectbox("Priority *", ["Low", "Medium", "High", "Critical"])
            description = st.text_area("Description *", height=100,
                                     placeholder="Please provide detailed description of the issue...")
        
        submitted = st.form_submit_button("📤 Submit Request", use_container_width=True)
        
        if submitted:
            if not all([title, location, facility_type, priority, description]):
                st.error("⚠️ Please fill in all required fields (*)")
            else:
                with st.spinner("Submitting request..."):
                    if create_maintenance_request(title, description, location, facility_type, 
                                                 priority, st.session_state.user['username']):
                        st.success("✅ Maintenance request submitted successfully!")
                        time.sleep(2)
                        st.session_state.navigation_menu = "Dashboard"
                        st.rerun()
                    else:
                        st.error("❌ Failed to submit request")

# ========== NEW FEATURE: MANAGE REQUESTS ==========

def show_manage_requests():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("📋 Manage Maintenance Requests")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 All Requests", "✅ Approval Workflow"])
    
    with tab1:
        with st.spinner("Loading requests..."):
            all_requests = get_all_requests()
        
        if not all_requests:
            st.info("📭 No maintenance requests found")
        else:
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                status_filter = st.selectbox("Filter by Status", 
                                           ["All", "Pending", "Assigned", "In Progress", "Completed", "Approved"])
            with col2:
                priority_filter = st.selectbox("Filter by Priority", ["All", "Low", "Medium", "High", "Critical"])
            with col3:
                if st.button("🔄 Refresh", key="refresh_requests"):
                    st.cache_data.clear()
                    st.rerun()
            
            # Filter requests
            filtered_requests = all_requests
            if status_filter != "All":
                filtered_requests = [r for r in filtered_requests if safe_get(r, 'status') == status_filter]
            if priority_filter != "All":
                filtered_requests = [r for r in filtered_requests if safe_get(r, 'priority') == priority_filter]
            
            st.subheader(f"📊 Found {len(filtered_requests)} request(s)")
            
            for req in filtered_requests[:10]:  # Limit to 10 for performance
                with st.expander(f"Request #{safe_get(req, 'id')}: {safe_str(safe_get(req, 'title'))}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.write("**📋 Request Information**")
                        st.write(f"**Title:** {safe_str(safe_get(req, 'title'))}")
                        st.write(f"**Location:** {safe_str(safe_get(req, 'location'))}")
                        st.write(f"**Facility Type:** {safe_str(safe_get(req, 'facility_type'))}")
                        st.write(f"**Priority:** {safe_str(safe_get(req, 'priority'))}")
                        st.write(f"**Status:** {safe_str(safe_get(req, 'status'))}")
                        st.write(f"**Created By:** {safe_str(safe_get(req, 'created_by'))}")
                        st.write(f"**Description:** {safe_str(safe_get(req, 'description'))}")
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.write("**🛠️ Actions**")
                        
                        if st.session_state.user['role'] == 'facility_manager':
                            # Manager actions
                            if safe_get(req, 'status') == 'Pending':
                                if st.button("Assign Vendor", key=f"assign_{safe_get(req, 'id')}"):
                                    # Logic to assign vendor
                                    st.success("Vendor assignment feature coming soon!")
                            
                            if safe_get(req, 'status') == 'Completed' and not safe_get(req, 'facilities_manager_approval'):
                                if st.button("✅ Approve Completion", key=f"approve_{safe_get(req, 'id')}"):
                                    if approve_job_completion(safe_get(req, 'id')):
                                        st.success("✅ Job completion approved!")
                                        st.cache_data.clear()
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to approve job completion")
                        
                        elif st.session_state.user['role'] == 'facility_user':
                            # User actions
                            if safe_get(req, 'status') == 'Completed' and not safe_get(req, 'requesting_dept_approval'):
                                if st.button("✅ Approve Completion", key=f"dept_approve_{safe_get(req, 'id')}"):
                                    # Logic for department approval
                                    st.success("Department approval feature coming soon!")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.subheader("✅ Approval Workflow")
        
        jobs_for_approval = get_jobs_for_approval()
        
        if not jobs_for_approval:
            st.info("📭 No jobs pending approval")
        else:
            for job in jobs_for_approval:
                with st.expander(f"Job #{safe_get(job, 'id')}: {safe_str(safe_get(job, 'title'))}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Title:** {safe_str(safe_get(job, 'title'))}")
                        st.write(f"**Location:** {safe_str(safe_get(job, 'location'))}")
                        st.write(f"**Assigned Vendor:** {safe_str(safe_get(job, 'assigned_vendor'))}")
                        if safe_get(job, 'completion_notes'):
                            st.write(f"**Completion Notes:** {safe_str(safe_get(job, 'completion_notes'))}")
                    
                    with col2:
                        st.write("**Approval Status**")
                        st.write(f"**Department Approval:** {'✅ Approved' if safe_get(job, 'requesting_dept_approval') else '⏳ Pending'}")
                        st.write(f"**Manager Approval:** {'✅ Approved' if safe_get(job, 'facilities_manager_approval') else '⏳ Pending'}")
                        st.write(f"**Vendor Completion:** {'✅ Submitted' if safe_get(job, 'vendor_completion_approval') else '⏳ Pending'}")
                        
                        # Approval buttons for manager
                        if st.session_state.user['role'] == 'facility_manager':
                            if not safe_get(job, 'facilities_manager_approval'):
                                if st.button("✅ Approve Job", key=f"final_approve_{safe_get(job, 'id')}"):
                                    if approve_job_completion(safe_get(job, 'id')):
                                        st.success("✅ Job approved successfully!")
                                        st.cache_data.clear()
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to approve job")

# ========== NEW FEATURE: ASSIGNED JOBS ==========

def show_assigned_jobs():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🛠️ Assigned Jobs")
    st.markdown('</div>', unsafe_allow_html=True)
    
    user = st.session_state.user
    assigned_jobs = get_assigned_jobs(user['username'])
    
    if not assigned_jobs:
        st.info("📭 No assigned jobs found")
        return
    
    for job in assigned_jobs:
        with st.expander(f"Job #{safe_get(job, 'id')}: {safe_str(safe_get(job, 'title'))} - Status: {safe_str(safe_get(job, 'status'))}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.write("**📋 Job Details**")
                st.write(f"**Title:** {safe_str(safe_get(job, 'title'))}")
                st.write(f"**Location:** {safe_str(safe_get(job, 'location'))}")
                st.write(f"**Facility Type:** {safe_str(safe_get(job, 'facility_type'))}")
                st.write(f"**Priority:** {safe_str(safe_get(job, 'priority'))}")
                st.write(f"**Created By:** {safe_str(safe_get(job, 'created_by'))}")
                st.write(f"**Description:** {safe_str(safe_get(job, 'description'))}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.write("**✅ Job Completion**")
                
                if safe_get(job, 'status') in ['Assigned', 'In Progress']:
                    completion_notes = st.text_area("Completion Notes", 
                                                   placeholder="Describe work completed, materials used, etc.",
                                                   key=f"notes_{safe_get(job, 'id')}")
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("🔄 Mark as In Progress", key=f"progress_{safe_get(job, 'id')}"):
                            if execute_update("UPDATE maintenance_requests SET status = 'In Progress' WHERE id = ?", 
                                            (safe_get(job, 'id'),)):
                                st.success("✅ Job marked as In Progress!")
                                st.cache_data.clear()
                                st.rerun()
                    
                    with col_btn2:
                        if completion_notes and st.button("✅ Mark as Completed", key=f"complete_{safe_get(job, 'id')}"):
                            if complete_job(safe_get(job, 'id'), completion_notes):
                                st.success("✅ Job marked as completed! Awaiting approval.")
                                st.cache_data.clear()
                                st.rerun()
                elif safe_get(job, 'status') == 'Completed':
                    st.success("✅ Job completed and awaiting approval")
                    if safe_get(job, 'completion_notes'):
                        st.write(f"**Your Completion Notes:** {safe_str(safe_get(job, 'completion_notes'))}")
                
                st.markdown('</div>', unsafe_allow_html=True)

# ========== NEW FEATURE: INVOICE CREATION ==========

def show_invoice_creation():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🧾 Create Invoice")
    st.markdown('</div>', unsafe_allow_html=True)
    
    user = st.session_state.user
    
    # Get completed jobs by this vendor
    completed_jobs = execute_query('''
        SELECT * FROM maintenance_requests 
        WHERE assigned_vendor = ? AND status = 'Completed' 
        AND id NOT IN (SELECT request_id FROM invoices WHERE vendor_username = ?)
        ORDER BY completed_date DESC
    ''', (user['username'], user['username']))
    
    if not completed_jobs:
        st.info("📭 No completed jobs available for invoicing")
        return
    
    job_selection = st.selectbox(
        "Select Job to Invoice",
        options=[f"#{j['id']}: {j['title']} - {j['location']}" for j in completed_jobs],
        key="invoice_job_select"
    )
    
    if job_selection:
        job_id = int(job_selection.split("#")[1].split(":")[0])
        selected_job = next((j for j in completed_jobs if j['id'] == job_id), None)
        
        if selected_job:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write(f"**Job:** {selected_job['title']}")
            st.write(f"**Location:** {selected_job['location']}")
            st.write(f"**Description:** {selected_job['description']}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            with st.form("create_invoice_form"):
                st.subheader("📝 Invoice Details")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    details_of_work = st.text_area("Details of Work *", 
                                                  value=f"Completed: {selected_job['title']}",
                                                  height=100)
                    quantity = st.number_input("Quantity *", min_value=1, value=1, step=1)
                    unit_cost = st.number_input("Unit Cost (₦) *", min_value=0.0, value=0.0, step=100.0)
                
                with col2:
                    labour_charge = st.number_input("Labour/Service Charge (₦)", min_value=0.0, value=0.0, step=100.0)
                    vat_applicable = st.checkbox("Apply VAT (7.5%)", value=True)
                
                # Calculate preview
                amount = quantity * unit_cost
                subtotal = amount + labour_charge
                vat_amount = subtotal * 0.075 if vat_applicable else 0
                total_amount = subtotal + vat_amount
                
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.write("**💰 Invoice Preview**")
                st.write(f"**Amount:** {format_naira(amount)}")
                if labour_charge > 0:
                    st.write(f"**Labour Charge:** {format_naira(labour_charge)}")
                st.write(f"**Subtotal:** {format_naira(subtotal)}")
                if vat_applicable:
                    st.write(f"**VAT (7.5%):** {format_naira(vat_amount)}")
                st.write(f"**Total Amount:** {format_naira(total_amount)}")
                st.markdown('</div>', unsafe_allow_html=True)
                
                submitted = st.form_submit_button("🧾 Create Invoice", use_container_width=True)
                
                if submitted:
                    if not details_of_work or unit_cost <= 0:
                        st.error("⚠️ Please fill in all required fields (*)")
                    else:
                        with st.spinner("Creating invoice..."):
                            if create_invoice(job_id, user['username'], details_of_work, quantity, 
                                            unit_cost, labour_charge, vat_applicable):
                                st.success("✅ Invoice created successfully!")
                                time.sleep(2)
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                st.error("❌ Failed to create invoice")

# ========== SPACE MANAGEMENT WITH ANALYTICS ==========

def show_space_management():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🏢 Space Management")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📅 View Bookings", "➕ New Booking", "📊 Analytics"])
    
    with tab1:
        with st.spinner("Loading bookings..."):
            bookings = get_space_bookings()
        
        if not bookings:
            st.info("📭 No bookings found")
        else:
            display_data = []
            for booking in bookings[:10]:
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
                    with st.spinner("Booking room..."):
                        if add_space_booking(room_name, room_type, booking_date, 
                                           start_time.strftime("%H:%M"), 
                                           end_time.strftime("%H:%M"), 
                                           purpose, st.session_state.user['username'],
                                           department, attendees_count, catering_required, 
                                           special_requirements):
                            st.success("✅ Room booked successfully!")
                            st.cache_data.clear()
                            time.sleep(2)
                            st.rerun()
    
    with tab3:
        st.subheader("📊 Space Management Analytics")
        
        with st.spinner("Loading analytics..."):
            analytics = get_space_analytics()
        
        if analytics:
            df_analytics = pd.DataFrame(analytics)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                fig = px.bar(df_analytics, x='room_type', y='total_bookings',
                            title="📈 Bookings by Room Type",
                            color='room_type',
                            color_discrete_sequence=px.colors.sequential.Viridis)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                fig = px.pie(df_analytics, values='total_attendees', names='room_type',
                            title="👥 Attendees Distribution",
                            hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Statistics
            st.markdown('<div class="card">', unsafe_allow_html=True)
            col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
            
            total_bookings = df_analytics['total_bookings'].sum()
            total_attendees = df_analytics['total_attendees'].sum()
            avg_attendees = df_analytics['avg_attendees'].mean()
            catering_requests = df_analytics['catering_requests'].sum()
            
            with col_stats1:
                st.metric("Total Bookings", total_bookings)
            with col_stats2:
                st.metric("Total Attendees", total_attendees)
            with col_stats3:
                st.metric("Avg Attendees", f"{avg_attendees:.1f}")
            with col_stats4:
                st.metric("Catering Requests", catering_requests)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("📭 No analytics data available")

# ========== HSE MANAGEMENT - OPTIMIZED ==========

def show_hse_management():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🚨 HSE Management")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📅 Schedule", "🚨 Incidents", "➕ New Inspection", "📊 Compliance Dashboard"])
    
    with tab1:
        st.subheader("📅 HSE Inspection Schedule")
        
        with st.spinner("Loading schedule..."):
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
        
        with st.spinner("Loading incidents..."):
            incidents = get_hse_incidents_optimized(limit=20)
        
        if not incidents:
            st.info("📭 No incident reports found")
        else:
            display_data = []
            for incident in incidents[:10]:
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
                    with st.spinner("Scheduling inspection..."):
                        if add_hse_schedule(inspection_type, area, frequency, next_inspection_date, assigned_to):
                            st.success("✅ Inspection scheduled successfully!")
                            st.cache_data.clear()
                            time.sleep(2)
                            st.rerun()
    
    with tab4:
        st.subheader("📊 HSE Compliance Dashboard")
        
        with st.spinner("Loading compliance data..."):
            compliance_data = get_hse_compliance_dashboard()
        
        if compliance_data:
            df_compliance = pd.DataFrame(compliance_data)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                fig = px.bar(df_compliance, x='inspection_type', y='compliance_rate',
                            title="📈 Compliance Rate by Inspection Type",
                            color='compliance_rate',
                            color_continuous_scale='RdYlGn')
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                compliant_total = df_compliance['compliant_count'].sum()
                non_compliant_total = df_compliance['non_compliant_count'].sum()
                
                fig = go.Figure(data=[go.Pie(labels=['Compliant', 'Non-Compliant'],
                                           values=[compliant_total, non_compliant_total],
                                           hole=.3,
                                           marker_colors=['#4CAF50', '#F44336'])])
                fig.update_layout(title_text="Overall Compliance Status")
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Summary statistics
            st.markdown('<div class="card">', unsafe_allow_html=True)
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            
            total_inspections = df_compliance['total_inspections'].sum()
            overall_compliance_rate = df_compliance['compliance_rate'].mean()
            
            with col_stats1:
                st.metric("Total Inspections", total_inspections)
            with col_stats2:
                st.metric("Overall Compliance", f"{overall_compliance_rate:.1f}%")
            with col_stats3:
                st.metric("Non-Compliant", non_compliant_total)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("📭 No compliance data available")

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
                Currency: <strong class="currency-symbol">₦ (Nigerian Naira)</strong> | © 2024 Developed by Abdulahi Ibrahim
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
                <p style="margin: 0;"><strong>Currency:</strong> <span class="currency-symbol">₦ (Nigerian Naira)</span></p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
        
        # Navigation menu based on role
        if role == 'facility_user':
            menu_options = ["Dashboard", "Create Request", "Manage Requests", "Generator Records", 
                          "Space Management", "HSE Management", "Job & Invoice Reports"]
        elif role == 'facility_manager':
            menu_options = ["Dashboard", "Manage Requests", "Reports", "Job & Invoice Reports", 
                          "Preventive Maintenance", "Space Management", "Generator Records", 
                          "HSE Management"]
        elif role == 'hse_officer':
            menu_options = ["Dashboard", "HSE Management"]
        elif role == 'space_manager':
            menu_options = ["Dashboard", "Space Management"]
        elif role == 'vendor':
            menu_options = ["Dashboard", "Vendor Management", "Assigned Jobs", "Invoice Creation",
                          "Generator Records", "Job & Invoice Reports"]
        else:
            menu_options = ["Dashboard"]
        
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
        from reports import show_reports
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
    elif selected_menu == "Vendor Management":
        show_vendor_management()
    elif selected_menu == "Create Request":
        show_create_request()
    elif selected_menu == "Manage Requests":
        show_manage_requests()
    elif selected_menu == "Assigned Jobs":
        show_assigned_jobs()
    elif selected_menu == "Invoice Creation":
        show_invoice_creation()

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
