import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import calendar
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
import random

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

# Custom CSS for enhanced UI with new components
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
    
    /* Quick Action Buttons */
    .quick-action-btn {
        background: linear-gradient(45deg, #2196F3, #1976D2) !important;
        margin: 5px;
        padding: 15px !important;
        height: auto !important;
        min-height: 60px;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    .quick-action-btn span {
        font-size: 24px !important;
        margin-bottom: 5px !important;
    }
    
    .quick-action-text {
        font-size: 12px !important;
        line-height: 1.2 !important;
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
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        text-transform: uppercase;
    }
    
    .status-pending { background-color: #FFEAA7; color: #E17055; }
    .status-assigned { background-color: #74B9FF; color: #0984E3; }
    .status-completed { background-color: #55EFC4; color: #00B894; }
    .status-approved { background-color: #81ECEC; color: #00CEC9; }
    
    /* Schedule table styling */
    .schedule-table {
        background: white;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .schedule-header {
        background: linear-gradient(90deg, #1a237e, #283593);
        color: white;
        padding: 15px;
        font-weight: bold;
    }
    
    .schedule-row {
        padding: 12px 15px;
        border-bottom: 1px solid #eee;
    }
    
    .schedule-row:nth-child(even) {
        background-color: #f8f9fa;
    }
    
    /* Frequency badges */
    .frequency-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: bold;
    }
    
    .frequency-daily { background-color: #E3F2FD; color: #1976D2; }
    .frequency-weekly { background-color: #E8F5E9; color: #388E3C; }
    .frequency-monthly { background-color: #FFF3E0; color: #F57C00; }
    .frequency-quarterly { background-color: #FCE4EC; color: #C2185B; }
    .frequency-bi-annually { background-color: #F3E5F5; color: #7B1FA2; }
    .frequency-annually { background-color: #E0F2F1; color: #00796B; }
    
    /* Conference Room Card */
    .room-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 5px solid #4CAF50;
    }
    
    .room-card.booked {
        border-left: 5px solid #f44336;
    }
    
    .room-card.available {
        border-left: 5px solid #4CAF50;
    }
    
    /* HSE Incident Card */
    .incident-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 5px solid #FF9800;
    }
    
    .severity-high { border-left: 5px solid #f44336 !important; }
    .severity-medium { border-left: 5px solid #FF9800 !important; }
    .severity-low { border-left: 5px solid #4CAF50 !important; }
    
    /* Generator Record Card */
    .generator-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 5px solid #2196F3;
    }
    
    /* Compliance Dashboard */
    .compliance-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .compliance-score {
        font-size: 36px;
        font-weight: bold;
        color: #4CAF50;
    }
    
    .compliance-score.low {
        color: #f44336;
    }
    
    .compliance-score.medium {
        color: #FF9800;
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
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            certificate_incorporation BLOB,
            tax_clearance_certificate BLOB,
            audited_financial_statement BLOB
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
    
    # Space Management - Bookings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS space_bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_name TEXT NOT NULL,
            room_type TEXT NOT NULL,
            booking_date DATE NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            booked_by TEXT NOT NULL,
            purpose TEXT NOT NULL,
            attendees_count INTEGER DEFAULT 1,
            status TEXT DEFAULT 'Confirmed',
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Preventive Maintenance Schedule table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS preventive_maintenance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_code TEXT NOT NULL,
            service_description TEXT NOT NULL,
            category TEXT NOT NULL,
            frequency TEXT NOT NULL,
            last_performed DATE,
            next_due DATE,
            assigned_vendor TEXT,
            status TEXT DEFAULT 'Scheduled',
            notes TEXT
        )
    ''')
    
    # Generator Records table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS generator_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            generator_id TEXT NOT NULL,
            record_date DATE NOT NULL,
            start_time TIME,
            end_time TIME,
            runtime_hours REAL,
            fuel_consumed_liters REAL,
            oil_level TEXT,
            coolant_level TEXT,
            battery_status TEXT,
            load_percentage REAL,
            issues_noted TEXT,
            recorded_by TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # HSE Management table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hse_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_type TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT NOT NULL,
            date_occurred DATE NOT NULL,
            severity TEXT NOT NULL,
            reported_by TEXT NOT NULL,
            assigned_to TEXT,
            status TEXT DEFAULT 'Open',
            corrective_actions TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Compliance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS compliance_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requirement TEXT NOT NULL,
            category TEXT NOT NULL,
            due_date DATE NOT NULL,
            status TEXT NOT NULL,
            responsible_party TEXT,
            notes TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert sample users including new vendors
    sample_users = [
        ('facility_user', '0123456', 'facility_user', None),
        ('facility_manager', '0123456', 'facility_manager', None),
        ('provas_vendor', '123456', 'vendor', 'AIR CONDITIONING SYSTEM'),
        ('power_vendor', '123456', 'vendor', 'ELECTRICAL SYSTEMS INSPECTIONS'),
        ('fire_vendor', '123456', 'vendor', 'FIRE FIGHTING AND ALARM SYSTEMS'),
        ('env_vendor', '123456', 'vendor', 'ENVIRONMENTAL / CLEANING CARE'),
        ('water_vendor', '123456', 'vendor', 'WATER SYSTEM MAINTENANCE'),
        ('generator_vendor', '123456', 'vendor', 'GENERATOR MAINTENANCE AND REPAIRS')
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
        ('provas_vendor', 'Provas Limited', 'John HVAC', 'provas@example.com', '080-1234-5678', 'AIR CONDITIONING SYSTEM', 
         'HVAC installation, maintenance and repair services', 50000000.00, 'TIN123456', 'RC789012',
         'John Smith (CEO), Jane Doe (Operations Manager)', 'Bank: Zenith Bank, Acc: 1234567890', 
         'HVAC Certified', '123 HVAC Street, Lagos'),
        ('power_vendor', 'Power Solutions Ltd', 'Mike Power', 'power@example.com', '080-2345-6789', 'ELECTRICAL SYSTEMS INSPECTIONS',
         'Electrical systems inspection and maintenance', 30000000.00, 'TIN123457', 'RC789013',
         'Mike Johnson (Director)', 'Bank: First Bank, Acc: 9876543210', 
         'Electrical Engineer Certified', '456 Power Ave, Abuja'),
        ('fire_vendor', 'Fire Safety Limited', 'Sarah Fire', 'fire@example.com', '080-3456-7890', 'FIRE FIGHTING AND ALARM SYSTEMS',
         'Fire fighting equipment and alarm systems maintenance', 25000000.00, 'TIN123458', 'RC789014',
         'Sarah Wilson (Owner)', 'Bank: GTBank, Acc: 4561237890', 
         'Fire Safety Expert', '789 Fire Road, Port Harcourt'),
        ('env_vendor', 'Environmental Solutions Ltd', 'David Clean', 'env@example.com', '080-4567-8901', 'ENVIRONMENTAL / CLEANING CARE',
         'Environmental cleaning and pest control', 40000000.00, 'TIN123459', 'RC789015',
         'David Brown (Manager)', 'Bank: Access Bank, Acc: 7894561230', 
         'Environmental Certified', '321 Cleaners Lane, Kano'),
        ('water_vendor', 'Watreatment Lab Solutions', 'Peter Water', 'water@example.com', '080-5678-9012', 'WATER SYSTEM MAINTENANCE',
         'Water system maintenance and treatment', 35000000.00, 'TIN123460', 'RC789016',
         'Peter Miller (Director)', 'Bank: UBA, Acc: 6543219870', 
         'Water Treatment Expert', '654 Water Street, Ibadan'),
        ('generator_vendor', 'Generator Limited', 'James Generator', 'generator@example.com', '080-6789-0123', 'GENERATOR MAINTENANCE AND REPAIRS',
         'Generator maintenance and repairs', 45000000.00, 'TIN123461', 'RC789017',
         'James Wilson (Owner)', 'Bank: Sterling Bank, Acc: 3216549870', 
         'Generator Specialist', '987 Power Road, Benin')
    ]
    
    for vendor_data in sample_vendors:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO vendors 
                (username, company_name, contact_person, email, phone, vendor_type, services_offered, 
                 annual_turnover, tax_identification_number, rc_number, key_management_staff, 
                 account_details, certification, address) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', vendor_data)
        except sqlite3.IntegrityError:
            pass
    
    # Insert sample preventive maintenance data
    preventive_maintenance_data = [
        # AIR CONDITIONING SYSTEM
        ('PPM/AC/001', 'Routine Inspection of all AC units in the main block and common areas.', 'AIR CONDITIONING SYSTEM', 'MONTHLY'),
        ('PPM/AC/002', 'Routine Servicing of all split units in the common areas', 'AIR CONDITIONING SYSTEM', 'QUARTERLY'),
        ('PPM/AC/003', 'Routine Servicing of all standing AC Units', 'AIR CONDITIONING SYSTEM', 'QUARTERLY'),
        ('PPM/AC/004', 'Routine Servicing of all Central air-conditioning units in the main building', 'AIR CONDITIONING SYSTEM', 'QUARTERLY'),
        
        # ELECTRICAL SYSTEMS INSPECTIONS
        ('PPM/ELECT/001', 'Inspection of bulbs and lighting systems in offices and common areas / Cleaning of extractor fans', 'ELECTRICAL SYSTEMS INSPECTIONS', 'DAILY'),
        ('PPM/ELECT/002', 'Inspection, checks and cleaning of lighting systems in the common area, stairways,service buildings and perimeter fence', 'ELECTRICAL SYSTEMS INSPECTIONS', 'MONTHLY'),
        ('PPM/ELECT/003', 'Inspection/check performance of the generators (Connecting Hoses, Battery Status, Liquid Levels, Fuel, Lube Oil, Coolant Water, and Battery Distil Water Level, load, amperage.', 'ELECTRICAL SYSTEMS INSPECTIONS', 'WEEKLY'),
        
        # FIRE FIGHTING AND ALARM SYSTEMS
        ('PPM/FIRE/001', 'Check performances of the smoke detectors,heat detectors and break glasses', 'FIRE FIGHTING AND ALARM SYSTEMS', 'QUARTERLY'),
        ('PPM/FIRE/002', 'Routine servicing of the fire alarm systems', 'FIRE FIGHTING AND ALARM SYSTEMS', 'QUARTERLY'),
        ('PPM/FIRE/003', 'Routine servicing of the fire extinguishers in the main block & common areas', 'FIRE FIGHTING AND ALARM SYSTEMS', 'BI-ANNUALLY'),
        ('PPM/FIRE/004', 'Routine servicing of fire hose reels & equipments', 'FIRE FIGHTING AND ALARM SYSTEMS', 'BI-ANNUALLY'),
        ('PPM/FIRE/005', 'Inspection of fire fighting equipment', 'FIRE FIGHTING AND ALARM SYSTEMS', 'WEEKLY'),
        ('PPM/FIRE/006', 'Routine servicing of FM 200', 'FIRE FIGHTING AND ALARM SYSTEMS', 'QUARTERLY'),
        
        # ENVIRONMENTAL / CLEANING CARE
        ('PPM/CLEAN/001', 'Perform fumigation and rodent control exercise (external)', 'ENVIRONMENTAL / CLEANING CARE', 'QUARTERLY'),
        ('PPM/CLEAN/002', 'Perform fumigation and rodent control exercise (internal)', 'ENVIRONMENTAL / CLEANING CARE', 'QUARTERLY'),
        ('PPM/CLEAN/003', 'Daily cleaning of the premises', 'ENVIRONMENTAL / CLEANING CARE', 'DAILY'),
        ('PPM/CLEAN/004', 'Daily cleaning of the annex building', 'ENVIRONMENTAL / CLEANING CARE', 'DAILY'),
        ('PPM/CLEAN/005', 'Daily cleaning of the car park', 'ENVIRONMENTAL / CLEANING CARE', 'DAILY'),
        ('PPM/CLEAN/006', 'Inspection and cleaning of the rooftop gutters / Clearing of weeds around the building', 'ENVIRONMENTAL / CLEANING CARE', 'MONTHLY'),
        ('PPM/CLEAN/007', 'Pressure washing of granite tiles at the front of Cornation House and Stamp concrete floors at the car park basement', 'ENVIRONMENTAL / CLEANING CARE', 'ANNUALLY'),
        
        # WATER SYSTEM MAINTENANCE
        ('PPM/WSM/001', 'Daily check on water pumps and submersible pumps', 'WATER SYSTEM MAINTENANCE', 'DAILY'),
        ('PPM/WSM/002', 'Dosing of chemicals for water treatment plant', 'WATER SYSTEM MAINTENANCE', 'DAILY'),
        ('PPM/WSM/003', 'Chemicals for water treatment plant', 'WATER SYSTEM MAINTENANCE', 'MONTHLY'),
        ('PPM/WSM/004', 'Servicing of water pumps', 'WATER SYSTEM MAINTENANCE', 'QUARTERLY'),
        ('PPM/WSM/005', 'Routine Servicing of Borehole', 'WATER SYSTEM MAINTENANCE', 'ANNUALLY')
    ]
    
    for service_code, description, category, frequency in preventive_maintenance_data:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO preventive_maintenance 
                (service_code, service_description, category, frequency, status) 
                VALUES (?, ?, ?, ?, ?)
            ''', (service_code, description, category, frequency, 'Scheduled'))
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

# Helper functions
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

def format_naira(amount, decimal_places=2):
    try:
        amount = safe_float(amount, 0)
        return f"₦{amount:,.{decimal_places}f}"
    except:
        return "₦0.00"

# ==================== NEW FEATURES IMPLEMENTATION ====================

# 1. Quick Actions Dashboard
def show_quick_actions(role):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🚀 Quick Actions")
    
    if role == 'facility_user':
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("📝 Create Request", key="quick_create", use_container_width=True):
                st.session_state.selected_menu = "Create Request"
                st.rerun()
        with col2:
            if st.button("📋 My Requests", key="quick_myreq", use_container_width=True):
                st.session_state.selected_menu = "My Requests"
                st.rerun()
        with col3:
            if st.button("🏢 Space Booking", key="quick_space", use_container_width=True):
                st.session_state.selected_menu = "Space Management"
                st.rerun()
        with col4:
            if st.button("📊 Reports", key="quick_reports", use_container_width=True):
                st.session_state.selected_menu = "Reports"
                st.rerun()
    
    elif role == 'facility_manager':
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("🛠️ Manage Requests", key="quick_manage", use_container_width=True):
                st.session_state.selected_menu = "Manage Requests"
                st.rerun()
        with col2:
            if st.button("👥 Vendor Management", key="quick_vendor", use_container_width=True):
                st.session_state.selected_menu = "Vendor Management"
                st.rerun()
        with col3:
            if st.button("🏢 Space Management", key="quick_space_mgr", use_container_width=True):
                st.session_state.selected_menu = "Space Management"
                st.rerun()
        with col4:
            if st.button("📈 Analytics", key="quick_analytics", use_container_width=True):
                st.session_state.selected_menu = "Reports"
                st.rerun()
    
    else:  # Vendor
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("🔧 Assigned Jobs", key="quick_assigned", use_container_width=True):
                st.session_state.selected_menu = "Assigned Jobs"
                st.rerun()
        with col2:
            if st.button("✅ Completed Jobs", key="quick_completed", use_container_width=True):
                st.session_state.selected_menu = "Completed Jobs"
                st.rerun()
        with col3:
            if st.button("🧾 Create Invoice", key="quick_invoice", use_container_width=True):
                st.session_state.selected_menu = "Invoice Creation"
                st.rerun()
        with col4:
            if st.button("📊 My Performance", key="quick_perf", use_container_width=True):
                st.session_state.selected_menu = "Reports"
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# 2. Space Management Section
def show_space_management():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🏢 Space Management")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📅 View Bookings", "➕ New Booking", "📊 Analytics", "🎯 Quick Actions"])
    
    with tab1:
        show_space_bookings()
    
    with tab2:
        show_new_booking()
    
    with tab3:
        show_space_analytics()
    
    with tab4:
        show_space_quick_actions()

def show_space_bookings():
    st.subheader("📅 Conference Room Bookings")
    
    # Mock data for three conference rooms
    rooms = [
        {
            'name': 'Conference Room A - Executive Suite',
            'capacity': 20,
            'location': 'Main Building, 3rd Floor',
            'amenities': 'Projector, Whiteboard, Video Conferencing'
        },
        {
            'name': 'Conference Room B - Innovation Hub',
            'capacity': 15,
            'location': 'Annex Building, 2nd Floor',
            'amenities': 'Smart TV, Sound System, Coffee Station'
        },
        {
            'name': 'Conference Room C - Boardroom',
            'capacity': 12,
            'location': 'Main Building, 1st Floor',
            'amenities': 'Executive Chairs, Video Wall, Conference Phone'
        }
    ]
    
    # Mock bookings data
    today = date.today()
    bookings = [
        {'room': 'Conference Room A', 'date': today, 'time': '09:00-11:00', 'booked_by': 'John Doe', 'purpose': 'Management Meeting'},
        {'room': 'Conference Room A', 'date': today, 'time': '14:00-16:00', 'booked_by': 'Jane Smith', 'purpose': 'Client Presentation'},
        {'room': 'Conference Room B', 'date': today, 'time': '10:00-12:00', 'booked_by': 'IT Department', 'purpose': 'Team Planning'},
        {'room': 'Conference Room C', 'date': today + timedelta(days=1), 'time': '13:00-15:00', 'booked_by': 'HR Department', 'purpose': 'Interview Session'}
    ]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🏢 Available Conference Rooms")
        
        for room in rooms:
            room_bookings = [b for b in bookings if b['room'] == room['name'] and b['date'] == today]
            is_booked = len(room_bookings) > 0
            
            st.markdown(f'''
                <div class="room-card {'booked' if is_booked else 'available'}">
                    <h4 style="margin: 0 0 10px 0;">{room['name']}</h4>
                    <p style="margin: 5px 0;"><strong>📍 Location:</strong> {room['location']}</p>
                    <p style="margin: 5px 0;"><strong>👥 Capacity:</strong> {room['capacity']} people</p>
                    <p style="margin: 5px 0;"><strong>🎯 Amenities:</strong> {room['amenities']}</p>
                    <p style="margin: 5px 0;"><strong>📊 Status:</strong> {'🟡 Booked Today' if is_booked else '🟢 Available'}</p>
                </div>
            ''', unsafe_allow_html=True)
    
    with col2:
        st.subheader("📅 Today's Schedule")
        
        today_bookings = [b for b in bookings if b['date'] == today]
        if today_bookings:
            for booking in today_bookings:
                st.markdown(f'''
                    <div class="card">
                        <h5 style="margin: 0 0 5px 0;">{booking['room']}</h5>
                        <p style="margin: 5px 0;"><strong>⏰ Time:</strong> {booking['time']}</p>
                        <p style="margin: 5px 0;"><strong>👤 Booked by:</strong> {booking['booked_by']}</p>
                        <p style="margin: 5px 0;"><strong>🎯 Purpose:</strong> {booking['purpose']}</p>
                    </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("No bookings for today")

def show_new_booking():
    st.subheader("➕ New Space Booking")
    
    with st.form("new_booking_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            room_name = st.selectbox(
                "🏢 Select Room",
                ["Conference Room A - Executive Suite", 
                 "Conference Room B - Innovation Hub", 
                 "Conference Room C - Boardroom"]
            )
            booking_date = st.date_input("📅 Booking Date", min_value=date.today())
            purpose = st.text_input("🎯 Purpose of Booking")
        
        with col2:
            start_time = st.time_input("⏰ Start Time")
            end_time = st.time_input("⏰ End Time")
            attendees = st.number_input("👥 Number of Attendees", min_value=1, max_value=50)
        
        contact_person = st.text_input("👤 Contact Person")
        contact_email = st.text_input("📧 Contact Email")
        special_requirements = st.text_area("📝 Special Requirements")
        
        if st.form_submit_button("📅 Book Now", use_container_width=True):
            st.success("✅ Room booking request submitted successfully!")
            # Here you would save to database

def show_space_analytics():
    st.subheader("📊 Space Utilization Analytics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📅 Total Bookings This Month", "42")
        st.metric("🏢 Most Used Room", "Conference Room A")
    with col2:
        st.metric("⏰ Average Booking Duration", "2.5 hours")
        st.metric("👥 Average Attendees", "8")
    with col3:
        st.metric("📈 Utilization Rate", "68%")
        st.metric("💰 Revenue Generated", "₦250,000")
    
    # Sample analytics charts
    fig = go.Figure(data=[
        go.Bar(name='Conference Room A', x=['Mon', 'Tue', 'Wed', 'Thu', 'Fri'], y=[12, 15, 8, 10, 14]),
        go.Bar(name='Conference Room B', x=['Mon', 'Tue', 'Wed', 'Thu', 'Fri'], y=[8, 10, 6, 9, 12]),
        go.Bar(name='Conference Room C', x=['Mon', 'Tue', 'Wed', 'Thu', 'Fri'], y=[6, 8, 5, 7, 10])
    ])
    fig.update_layout(title='Weekly Room Utilization', barmode='group')
    st.plotly_chart(fig, use_container_width=True)

def show_space_quick_actions():
    st.subheader("🎯 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 View All Bookings", use_container_width=True):
            st.info("Showing all bookings...")
    
    with col2:
        if st.button("🔄 Check Availability", use_container_width=True):
            st.info("Checking room availability...")
    
    with col3:
        if st.button("📊 Generate Report", use_container_width=True):
            st.info("Generating space utilization report...")

# 3. Preventive Maintenance Section
def show_preventive_maintenance():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🔧 Preventive Maintenance")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📅 Schedule Overview", "➕ Add New Schedule", "📊 Analytics"])
    
    with tab1:
        show_pm_schedule_overview()
    
    with tab2:
        show_add_pm_schedule()
    
    with tab3:
        show_pm_analytics()

def show_pm_schedule_overview():
    st.subheader("📅 Preventive Maintenance Schedule")
    
    # Get PM data from database
    pm_schedules = execute_query('SELECT * FROM preventive_maintenance ORDER BY category, service_code')
    
    if pm_schedules:
        categories = list(set([safe_get(sched, 'category') for sched in pm_schedules]))
        
        for category in categories:
            category_schedules = [s for s in pm_schedules if safe_get(s, 'category') == category]
            
            st.markdown(f'<div class="schedule-header">{category}</div>', unsafe_allow_html=True)
            
            for schedule in category_schedules:
                frequency = safe_str(safe_get(schedule, 'frequency'))
                frequency_class = frequency.lower().replace('-', '_')
                
                col1, col2, col3 = st.columns([3, 1, 2])
                with col1:
                    st.write(f"**{safe_get(schedule, 'service_code')}**: {safe_get(schedule, 'service_description')}")
                with col2:
                    st.markdown(f'<span class="frequency-badge frequency-{frequency_class}">{frequency}</span>', unsafe_allow_html=True)
                with col3:
                    status = safe_get(schedule, 'status')
                    if status == 'Completed':
                        st.markdown(f'<span class="status-badge status-completed">✅ {status}</span>', unsafe_allow_html=True)
                    elif status == 'Overdue':
                        st.markdown(f'<span class="status-badge status-pending">⚠️ {status}</span>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<span class="status-badge status-assigned">📅 {status}</span>', unsafe_allow_html=True)
                
                st.markdown('<hr style="margin: 10px 0;">', unsafe_allow_html=True)
    
    else:
        st.info("No preventive maintenance schedules found")

def show_add_pm_schedule():
    st.subheader("➕ Add New Preventive Maintenance Schedule")
    
    with st.form("add_pm_schedule_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            service_code = st.text_input("🔢 Service Code (e.g., PPM/AC/005)")
            service_description = st.text_area("📝 Service Description", height=100)
            category = st.selectbox("🏢 Category", [
                "AIR CONDITIONING SYSTEM",
                "ELECTRICAL SYSTEMS INSPECTIONS",
                "FIRE FIGHTING AND ALARM SYSTEMS",
                "ENVIRONMENTAL / CLEANING CARE",
                "WATER SYSTEM MAINTENANCE",
                "GENERATOR MAINTENANCE AND REPAIRS"
            ])
        
        with col2:
            frequency = st.selectbox("📅 Frequency", [
                "DAILY", "WEEKLY", "MONTHLY", "QUARTERLY", "BI-ANNUALLY", "ANNUALLY"
            ])
            assigned_vendor = st.selectbox("👥 Assign to Vendor", 
                ["Provas Limited", "Power Solutions Ltd", "Fire Safety Limited", 
                 "Environmental Solutions Ltd", "Watreatment Lab Solutions", "Generator Limited"]
            )
            next_due = st.date_input("📅 Next Due Date")
        
        notes = st.text_area("📝 Additional Notes")
        
        if st.form_submit_button("➕ Add Schedule", use_container_width=True):
            st.success("✅ Preventive maintenance schedule added successfully!")

def show_pm_analytics():
    st.subheader("📊 Preventive Maintenance Analytics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📋 Total Schedules", "28")
        st.metric("✅ Completed This Month", "15")
    with col2:
        st.metric("📅 Due This Week", "8")
        st.metric("⚠️ Overdue", "3")
    with col3:
        st.metric("🏢 Most Active Category", "Electrical")
        st.metric("👥 Top Performing Vendor", "Provas Ltd")
    with col4:
        st.metric("💰 Cost Savings", "₦1,200,000")
        st.metric("📈 Compliance Rate", "92%")
    
    # Compliance chart
    compliance_data = pd.DataFrame({
        'Category': ['AC Systems', 'Electrical', 'Fire Safety', 'Cleaning', 'Water Systems', 'Generators'],
        'Compliance Rate': [95, 92, 88, 96, 90, 94]
    })
    
    fig = px.bar(compliance_data, x='Category', y='Compliance Rate', 
                 title='Preventive Maintenance Compliance by Category',
                 color='Compliance Rate', color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)

# 4. Generator Records
def show_generator_records():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("⚡ Generator Records")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📅 Daily Records", "➕ New Record", "📊 Analytics"])
    
    with tab1:
        show_generator_daily_records()
    
    with tab2:
        show_new_generator_record()
    
    with tab3:
        show_generator_analytics()

def show_generator_daily_records():
    st.subheader("📅 Daily Generator Records")
    
    # Mock data for generator records
    records = [
        {
            'generator_id': 'GEN-001',
            'date': date.today(),
            'start_time': '08:00',
            'end_time': '18:00',
            'runtime_hours': 10,
            'fuel_consumed': 250,
            'oil_level': 'Normal',
            'coolant_level': 'Normal',
            'battery_status': 'Good',
            'load_percentage': 75,
            'issues': 'None'
        },
        {
            'generator_id': 'GEN-002',
            'date': date.today() - timedelta(days=1),
            'start_time': '09:00',
            'end_time': '17:00',
            'runtime_hours': 8,
            'fuel_consumed': 200,
            'oil_level': 'Low',
            'coolant_level': 'Normal',
            'battery_status': 'Good',
            'load_percentage': 60,
            'issues': 'Oil needs topping up'
        }
    ]
    
    for record in records:
        st.markdown(f'''
            <div class="generator-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="margin: 0;">{record['generator_id']}</h4>
                    <span class="status-badge status-completed">📅 {record['date']}</span>
                </div>
                <div style="margin-top: 15px;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                        <div>
                            <p style="margin: 5px 0;"><strong>⏰ Runtime:</strong> {record['runtime_hours']} hours</p>
                            <p style="margin: 5px 0;"><strong>⛽ Fuel Consumed:</strong> {record['fuel_consumed']} liters</p>
                            <p style="margin: 5px 0;"><strong>🔋 Battery:</strong> {record['battery_status']}</p>
                        </div>
                        <div>
                            <p style="margin: 5px 0;"><strong>🛢️ Oil Level:</strong> {record['oil_level']}</p>
                            <p style="margin: 5px 0;"><strong>🌡️ Coolant:</strong> {record['coolant_level']}</p>
                            <p style="margin: 5px 0;"><strong>⚡ Load:</strong> {record['load_percentage']}%</p>
                        </div>
                    </div>
                    <p style="margin: 10px 0 0 0;"><strong>📝 Issues:</strong> {record['issues']}</p>
                </div>
            </div>
        ''', unsafe_allow_html=True)

def show_new_generator_record():
    st.subheader("➕ New Generator Record")
    
    with st.form("new_generator_record_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            generator_id = st.selectbox("🔧 Generator ID", ["GEN-001", "GEN-002", "GEN-003"])
            record_date = st.date_input("📅 Record Date", value=date.today())
            start_time = st.time_input("⏰ Start Time")
            end_time = st.time_input("⏰ End Time")
            fuel_consumed = st.number_input("⛽ Fuel Consumed (liters)", min_value=0.0, step=0.1)
        
        with col2:
            oil_level = st.selectbox("🛢️ Oil Level", ["Normal", "Low", "Very Low", "High"])
            coolant_level = st.selectbox("🌡️ Coolant Level", ["Normal", "Low", "Very Low", "High"])
            battery_status = st.selectbox("🔋 Battery Status", ["Good", "Needs Charging", "Replace Soon", "Poor"])
            load_percentage = st.slider("⚡ Load Percentage", 0, 100, 50)
        
        issues_noted = st.text_area("⚠️ Issues Noted")
        maintenance_needed = st.text_area("🔧 Maintenance Needed")
        recorded_by = st.text_input("👤 Recorded By", value=st.session_state.user['username'])
        
        if st.form_submit_button("💾 Save Record", use_container_width=True):
            st.success("✅ Generator record saved successfully!")

def show_generator_analytics():
    st.subheader("📊 Generator Analytics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("⚡ Total Runtime", "1,250 hours")
        st.metric("⛽ Fuel Consumed", "31,250 liters")
    with col2:
        st.metric("💰 Fuel Cost", "₦18,750,000")
        st.metric("📅 Avg Daily Runtime", "8.3 hours")
    with col3:
        st.metric("🛢️ Oil Changes", "12")
        st.metric("🔋 Battery Replacements", "3")
    with col4:
        st.metric("📈 Efficiency", "85%")
        st.metric("⚠️ Issues Reported", "8")
    
    # Fuel consumption chart
    fuel_data = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Fuel (liters)': [5200, 4800, 5100, 4900, 5300, 5200],
        'Cost (₦)': [3120000, 2880000, 3060000, 2940000, 3180000, 3120000]
    })
    
    fig = px.line(fuel_data, x='Month', y=['Fuel (liters)', 'Cost (₦)'],
                 title='Monthly Fuel Consumption & Cost',
                 markers=True)
    st.plotly_chart(fig, use_container_width=True)

# 5. HSE Management
def show_hse_management():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🛡️ HSE Management")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📅 HSE Schedule", "⚠️ Incident Reports", "➕ New Inspection"])
    
    with tab1:
        show_hse_schedule()
    
    with tab2:
        show_incident_reports()
    
    with tab3:
        show_new_inspection()

def show_hse_schedule():
    st.subheader("📅 HSE Inspection Schedule")
    
    # Mock HSE schedule data
    hse_schedule = [
        {
            'activity': 'Fire Drill & Evacuation Exercise',
            'frequency': 'Quarterly',
            'last_performed': date.today() - timedelta(days=45),
            'next_due': date.today() + timedelta(days=45),
            'responsible': 'Fire Safety Limited',
            'status': 'Scheduled'
        },
        {
            'activity': 'First Aid Kit Inspection',
            'frequency': 'Monthly',
            'last_performed': date.today() - timedelta(days=15),
            'next_due': date.today() + timedelta(days=15),
            'responsible': 'HSE Department',
            'status': 'Due Soon'
        }
    ]
    
    for schedule in hse_schedule:
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.write(f"**{schedule['activity']}**")
            st.write(f"Responsible: {schedule['responsible']}")
        
        with col2:
            st.write(f"**Frequency:** {schedule['frequency']}")
            st.write(f"**Next Due:** {schedule['next_due']}")
        
        with col3:
            if schedule['status'] == 'Scheduled':
                st.markdown('<span class="status-badge status-assigned">📅 Scheduled</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="status-badge status-pending">⚠️ Due Soon</span>', unsafe_allow_html=True)
        
        st.markdown('<hr style="margin: 10px 0;">', unsafe_allow_html=True)

def show_incident_reports():
    st.subheader("⚠️ HSE Incident Reports")
    
    # Mock incident data
    incidents = [
        {
            'id': 'INC-2024-001',
            'title': 'Minor Slip in Kitchen Area',
            'date': date.today() - timedelta(days=5),
            'location': 'Main Building Kitchen',
            'severity': 'Low',
            'status': 'Resolved',
            'description': 'Employee slipped on wet floor, no injuries reported'
        },
        {
            'id': 'INC-2024-002',
            'title': 'Electrical Panel Overheating',
            'date': date.today() - timedelta(days=15),
            'location': 'Electrical Room',
            'severity': 'Medium',
            'status': 'Under Investigation',
            'description': 'Electrical panel showing signs of overheating, temperature measured at 65°C'
        }
    ]
    
    for incident in incidents:
        severity_class = f"severity-{incident['severity'].lower()}"
        
        st.markdown(f'''
            <div class="incident-card {severity_class}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="margin: 0;">{incident['title']}</h4>
                    <span class="status-badge {'status-completed' if incident['status'] == 'Resolved' else 'status-pending'}">
                        {incident['status']}
                    </span>
                </div>
                <div style="margin-top: 10px;">
                    <p style="margin: 5px 0;"><strong>🔢 ID:</strong> {incident['id']}</p>
                    <p style="margin: 5px 0;"><strong>📅 Date:</strong> {incident['date']}</p>
                    <p style="margin: 5px 0;"><strong>📍 Location:</strong> {incident['location']}</p>
                    <p style="margin: 5px 0;"><strong>🚨 Severity:</strong> {incident['severity']}</p>
                    <p style="margin: 5px 0;"><strong>📝 Description:</strong> {incident['description']}</p>
                </div>
            </div>
        ''', unsafe_allow_html=True)

def show_new_inspection():
    st.subheader("➕ New HSE Inspection")
    
    with st.form("new_hse_inspection_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            inspection_type = st.selectbox("📋 Inspection Type", [
                "Fire Safety", "First Aid", "Electrical Safety", 
                "Chemical Safety", "Workplace Ergonomics", "General Safety"
            ])
            location = st.selectbox("📍 Location", [
                "Main Building", "Annex Building", "Production Area", 
                "Warehouse", "Car Park", "Common Areas"
            ])
            inspection_date = st.date_input("📅 Inspection Date", value=date.today())
        
        with col2:
            inspector = st.text_input("👤 Inspector Name")
            department = st.selectbox("🏢 Department", [
                "HSE Department", "Facilities", "Production", 
                "Warehouse", "Administration"
            ])
            priority = st.selectbox("🚨 Priority", ["Low", "Medium", "High"])
        
        findings = st.text_area("🔍 Findings/Observations", height=100)
        corrective_actions = st.text_area("🔧 Corrective Actions Required", height=100)
        recommendations = st.text_area("💡 Recommendations", height=100)
        
        if st.form_submit_button("📋 Submit Inspection Report", use_container_width=True):
            st.success("✅ HSE inspection report submitted successfully!")

# 6. Compliance Dashboard
def show_compliance_dashboard():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("📊 Compliance Dashboard")
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="compliance-card">', unsafe_allow_html=True)
        st.metric("📈 Overall Compliance", "92%")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="compliance-card">', unsafe_allow_html=True)
        st.metric("✅ Compliant Items", "46")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="compliance-card">', unsafe_allow_html=True)
        st.metric("⚠️ Non-Compliant", "4")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="compliance-card">', unsafe_allow_html=True)
        st.metric("📅 Due This Month", "8")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Compliance by category
    st.subheader("📋 Compliance by Category")
    
    compliance_data = pd.DataFrame({
        'Category': ['Fire Safety', 'Electrical', 'Environmental', 'Health & Safety', 'Building Code'],
        'Compliance Rate': [95, 90, 92, 88, 94],
        'Items': [20, 15, 12, 18, 10],
        'Status': ['Compliant', 'Compliant', 'Compliant', 'Needs Attention', 'Compliant']
    })
    
    fig = px.bar(compliance_data, x='Category', y='Compliance Rate',
                 color='Status', title='Compliance Rate by Category',
                 color_discrete_map={'Compliant': '#4CAF50', 'Needs Attention': '#FF9800'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Compliance calendar
    st.subheader("📅 Compliance Calendar")
    
    calendar_data = pd.DataFrame({
        'Date': pd.date_range(start='2024-01-01', end='2024-12-31', freq='M'),
        'Requirements': ['Fire Drill', 'Electrical Inspection', 'Environmental Audit', 
                        'Safety Training', 'Building Inspection', 'Equipment Calibration'],
        'Status': ['Completed', 'Completed', 'Scheduled', 'Overdue', 'Pending', 'Scheduled']
    })
    
    fig = px.timeline(calendar_data, x_start='Date', x_end='Date', y='Requirements',
                     color='Status', title='Upcoming Compliance Requirements',
                     color_discrete_map={'Completed': '#4CAF50', 'Scheduled': '#2196F3', 
                                       'Pending': '#FF9800', 'Overdue': '#f44336'})
    st.plotly_chart(fig, use_container_width=True)

# 7. Management Requests (Enhanced for Facility Manager)
def show_management_requests():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("👨‍💼 Management Requests")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Assign Jobs to Vendors", "✅ Approve Completed Jobs"])
    
    with tab1:
        show_assign_jobs()
    
    with tab2:
        show_approve_jobs()

def show_assign_jobs():
    st.subheader("📋 Assign Maintenance Jobs to Vendors")
    
    # Get pending requests
    pending_requests = execute_query(
        'SELECT * FROM maintenance_requests WHERE status = "Pending" ORDER BY created_date DESC'
    )
    
    if pending_requests:
        for request in pending_requests:
            with st.expander(f"Request #{safe_get(request, 'id')}: {safe_str(safe_get(request, 'title'))}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Description:** {safe_str(safe_get(request, 'description'))}")
                    st.write(f"**Location:** {safe_str(safe_get(request, 'location'))}")
                    st.write(f"**Priority:** {safe_str(safe_get(request, 'priority'))}")
                    st.write(f"**Created By:** {safe_str(safe_get(request, 'created_by'))}")
                
                with col2:
                    facility_type = safe_str(safe_get(request, 'facility_type'))
                    
                    # Get vendors for this facility type
                    vendors = execute_query(
                        'SELECT * FROM vendors WHERE vendor_type LIKE ?',
                        (f'%{facility_type}%',)
                    )
                    
                    if vendors:
                        vendor_options = [f"{vendor['company_name']} ({vendor['username']})" for vendor in vendors]
                        selected_vendor = st.selectbox(
                            f"Select vendor for {facility_type}",
                            vendor_options,
                            key=f"assign_vendor_{safe_get(request, 'id')}"
                        )
                        
                        if st.button(f"👥 Assign to Vendor", key=f"assign_btn_{safe_get(request, 'id')}"):
                            vendor_username = selected_vendor.split('(')[-1].rstrip(')')
                            if execute_update(
                                'UPDATE maintenance_requests SET status = ?, assigned_vendor = ? WHERE id = ?',
                                ('Assigned', vendor_username, safe_get(request, 'id'))
                            ):
                                st.success(f"✅ Job assigned to {vendor_username}!")
                                st.rerun()
                    else:
                        st.warning("No vendors available for this facility type")
    else:
        st.info("No pending requests to assign")

def show_approve_jobs():
    st.subheader("✅ Approve Completed Jobs")
    
    # Get completed jobs waiting for manager approval
    completed_jobs = execute_query('''
        SELECT * FROM maintenance_requests 
        WHERE status = 'Completed' 
        AND requesting_dept_approval = 1 
        AND facilities_manager_approval = 0
        ORDER BY completed_date DESC
    ''')
    
    if completed_jobs:
        for job in completed_jobs:
            with st.expander(f"Job #{safe_get(job, 'id')}: {safe_str(safe_get(job, 'title'))}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Job Breakdown:** {safe_str(safe_get(job, 'job_breakdown'))}")
                    st.write(f"**Completion Notes:** {safe_str(safe_get(job, 'completion_notes'))}")
                    st.write(f"**Completed Date:** {safe_str(safe_get(job, 'completed_date'))}")
                    
                    if safe_get(job, 'invoice_amount'):
                        st.write(f"**Invoice Amount:** {format_naira(safe_get(job, 'invoice_amount'))}")
                        st.write(f"**Invoice Number:** {safe_str(safe_get(job, 'invoice_number'))}")
                
                with col2:
                    if st.button("✅ Approve Job Completion", key=f"approve_{safe_get(job, 'id')}", use_container_width=True):
                        if execute_update(
                            'UPDATE maintenance_requests SET facilities_manager_approval = 1, status = "Approved" WHERE id = ?',
                            (safe_get(job, 'id'),)
                        ):
                            st.success("✅ Job approved successfully!")
                            st.rerun()
                    
                    # PDF Download button
                    if st.button("📋 Download Job Report", key=f"report_{safe_get(job, 'id')}", use_container_width=True):
                        # Get invoice data
                        invoice = execute_query('SELECT * FROM invoices WHERE request_id = ?', (safe_get(job, 'id'),))
                        invoice_data = invoice[0] if invoice else None
                        
                        pdf_data = generate_job_completion_invoice_report(job, invoice_data)
                        if pdf_data:
                            st.download_button(
                                label="⬇️ Download PDF",
                                data=pdf_data,
                                file_name=f"job_report_{safe_get(job, 'id')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf",
                                key=f"download_{safe_get(job, 'id')}"
                            )
    else:
        st.info("No jobs waiting for manager approval")

# 8. Vendor Login Information
def show_vendor_login_info():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🔐 Vendor Login Information")
    st.markdown('</div>', unsafe_allow_html=True)
    
    vendor_credentials = [
        {"SERVICE": "AIR CONDITIONING SYSTEM", "VENDOR": "Provas Limited", "USERNAME": "provas_vendor", "PASSWORD": "123456"},
        {"SERVICE": "ELECTRICAL SYSTEMS INSPECTIONS", "VENDOR": "Power Solutions Ltd", "USERNAME": "power_vendor", "PASSWORD": "123456"},
        {"SERVICE": "FIRE FIGHTING AND ALARM SYSTEMS", "VENDOR": "Fire Safety Limited", "USERNAME": "fire_vendor", "PASSWORD": "123456"},
        {"SERVICE": "ENVIRONMENTAL / CLEANING CARE", "VENDOR": "Environmental Solutions Ltd", "USERNAME": "env_vendor", "PASSWORD": "123456"},
        {"SERVICE": "WATER SYSTEM MAINTENANCE", "VENDOR": "Watreatment Lab Solutions", "USERNAME": "water_vendor", "PASSWORD": "123456"},
        {"SERVICE": "GENERATOR MAINTENANCE AND REPAIRS", "VENDOR": "Generator Limited", "USERNAME": "generator_vendor", "PASSWORD": "123456"}
    ]
    
    df = pd.DataFrame(vendor_credentials)
    st.dataframe(df, use_container_width=True, hide_index=True)

# 9. Vendor Assigned Preventive Maintenance
def show_assigned_preventive_maintenance():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🔧 Assigned Preventive Maintenance")
    st.markdown('</div>', unsafe_allow_html=True)
    
    user = st.session_state.user
    vendor_type = user.get('vendor_type')
    
    if vendor_type:
        # Get PM assigned to this vendor type
        pm_assignments = execute_query(
            'SELECT * FROM preventive_maintenance WHERE assigned_vendor LIKE ? OR category LIKE ?',
            (f'%{vendor_type}%', f'%{vendor_type}%')
        )
        
        if pm_assignments:
            for pm in pm_assignments:
                with st.expander(f"{safe_get(pm, 'service_code')}: {safe_str(safe_get(pm, 'service_description'), 'N/A')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Category:** {safe_str(safe_get(pm, 'category'))}")
                        st.write(f"**Frequency:** {safe_str(safe_get(pm, 'frequency'))}")
                        st.write(f"**Status:** {safe_str(safe_get(pm, 'status'))}")
                    
                    with col2:
                        if safe_get(pm, 'status') == 'Scheduled':
                            st.subheader("✅ Complete Maintenance")
                            with st.form(f"complete_pm_{safe_get(pm, 'id')}"):
                                completion_date = st.date_input("📅 Date Completed", value=date.today())
                                notes = st.text_area("📝 Completion Notes")
                                issues_found = st.text_area("⚠️ Issues Found (if any)")
                                
                                if st.form_submit_button("✅ Mark as Complete", use_container_width=True):
                                    # Update PM status
                                    execute_update(
                                        'UPDATE preventive_maintenance SET status = ?, last_performed = ?, notes = ? WHERE id = ?',
                                        ('Completed', completion_date, f"{notes}\\nIssues: {issues_found}", safe_get(pm, 'id'))
                                    )
                                    st.success("✅ Preventive maintenance marked as complete!")
                                    st.rerun()
        else:
            st.info("No preventive maintenance assigned to you")
    else:
        st.warning("Vendor type not specified")

# ==================== UPDATED MAIN APP FUNCTION ====================

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
    
    # Show Quick Actions
    show_quick_actions(role)
    
    with st.sidebar:
        st.markdown(f"""
            <div style="text-align: center; padding: 10px; background: linear-gradient(45deg, #4CAF50, #2E7D32); 
                     border-radius: 10px; margin-bottom: 20px;">
                <h3 style="color: white; margin: 0;">👋 Welcome</h3>
                <p style="color: white; margin: 5px 0;">{user['username']}</p>
                <p style="color: white; margin: 5px 0; font-size: 12px;">{role.replace('_', ' ').title()}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Initialize selected_menu in session state
        if 'selected_menu' not in st.session_state:
            st.session_state.selected_menu = "Dashboard"
        
        if role == 'facility_user':
            menu_options = [
                "Dashboard", "Create Request", "My Requests", 
                "Space Management", "Requests", "Manage Request",
                "Preventive Maintenance", "Generator Records", "HSE Management",
                "Compliance Dashboard", "Reports"
            ]
        elif role == 'facility_manager':
            menu_options = [
                "Dashboard", "Manage Requests", "Management Requests",
                "Vendor Management", "Space Management", "Reports",
                "Preventive Maintenance", "Generator Records", "HSE Management",
                "Job & Invoice Reports", "Vendor Login Info"
            ]
        else:  # Vendor
            menu_options = [
                "Dashboard", "Assigned Jobs", "Assigned Preventive Maintenance",
                "Completed Jobs", "Vendor Registration", "Invoice Creation",
                "Reports"
            ]
        
        selected_menu = st.radio("🗺️ Navigation", menu_options, 
                               index=menu_options.index(st.session_state.selected_menu),
                               key="navigation_menu", label_visibility="collapsed")
        
        # Update session state
        st.session_state.selected_menu = selected_menu
        
        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
        
        if st.button("🚪 Logout", type="secondary", use_container_width=True, key="logout_button"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Main content based on selected menu
    if selected_menu == "Dashboard":
        show_dashboard()
    elif selected_menu == "Create Request":
        show_create_request()
    elif selected_menu == "My Requests":
        show_my_requests()
    elif selected_menu == "Space Management":
        show_space_management()
    elif selected_menu == "Requests":
        show_my_requests()  # Reuse existing function
    elif selected_menu == "Manage Request":
        show_manage_requests()
    elif selected_menu == "Preventive Maintenance":
        show_preventive_maintenance()
    elif selected_menu == "Generator Records":
        show_generator_records()
    elif selected_menu == "HSE Management":
        show_hse_management()
    elif selected_menu == "Compliance Dashboard":
        show_compliance_dashboard()
    elif selected_menu == "Reports":
        show_reports()
    elif selected_menu == "Manage Requests":
        show_manage_requests()
    elif selected_menu == "Management Requests":
        show_management_requests()
    elif selected_menu == "Vendor Management":
        show_vendor_management()
    elif selected_menu == "Job & Invoice Reports":
        show_job_invoice_reports()
    elif selected_menu == "Vendor Login Info":
        show_vendor_login_info()
    elif selected_menu == "Assigned Jobs":
        show_assigned_jobs()
    elif selected_menu == "Assigned Preventive Maintenance":
        show_assigned_preventive_maintenance()
    elif selected_menu == "Completed Jobs":
        show_completed_jobs()
    elif selected_menu == "Vendor Registration":
        show_vendor_registration()
    elif selected_menu == "Invoice Creation":
        show_invoice_creation()

# ==================== AUTHENTICATION & MAIN FUNCTION ====================

def authenticate_user(username, password):
    users = execute_query('SELECT * FROM users WHERE username = ? AND password_hash = ?', (username, password))
    return users[0] if users else None

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
                        st.session_state.selected_menu = "Dashboard"
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
        
        🏢 **Vendors:**
        • Provas Limited (AC): provas_vendor / 123456
        • Power Solutions: power_vendor / 123456
        • Fire Safety: fire_vendor / 123456
        • Environmental: env_vendor / 123456
        • Water Treatment: water_vendor / 123456
        • Generator Limited: generator_vendor / 123456
        """
        st.code(credentials, language=None)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
            <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.2);">
                <p style="color: rgba(255,255,255,0.8); font-size: 12px;">
                    © 2024 Facilities Management System™ | Developed by Abdulahi Ibrahim<br>
                    All trademarks and copyrights belong to their respective owners
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    if st.session_state.user is None:
        show_login()
    else:
        show_main_app()

if __name__ == "__main__":
    init_database()
    main()
