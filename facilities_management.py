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
    
    /* Loading spinner */
    .loading-spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #3498db;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 2s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
""", unsafe_allow_html=True)

# Database setup with enhanced schema
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

# ==================== PERFORMANCE OPTIMIZATION ====================
# Connection pool for better performance
connection_pool = {}

def get_connection():
    thread_id = id(threading.current_thread())
    if thread_id not in connection_pool:
        connection_pool[thread_id] = sqlite3.connect('facilities_management.db', check_same_thread=False)
        connection_pool[thread_id].row_factory = sqlite3.Row
    return connection_pool[thread_id]

def execute_query(query, params=()):
    """Optimized query execution with caching"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        return results
    except Exception as e:
        st.error(f"Query error: {e}")
        return []
    finally:
        # Don't close connection, keep in pool
        pass

def execute_update(query, params=()):
    """Optimized update execution"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Database update error: {e}")
        return False
    finally:
        # Don't close connection, keep in pool
        pass

# Cache for frequently accessed data
@st.cache_data(ttl=60)  # Cache for 60 seconds
def get_cached_user_requests(username):
    return execute_query(
        'SELECT * FROM maintenance_requests WHERE created_by = ? ORDER BY created_date DESC',
        (username,)
    )

@st.cache_data(ttl=60)
def get_cached_all_requests():
    return execute_query('SELECT * FROM maintenance_requests ORDER BY created_date DESC')

@st.cache_data(ttl=60)
def get_cached_vendor_requests(vendor_username):
    return execute_query(
        'SELECT * FROM maintenance_requests WHERE assigned_vendor = ? ORDER BY created_date DESC',
        (vendor_username,)
    )

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_vendors():
    return execute_query('SELECT * FROM vendors ORDER BY company_name')

@st.cache_data(ttl=300)
def get_cached_preventive_maintenance():
    return execute_query('SELECT * FROM preventive_maintenance ORDER BY category, service_code')

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

# ==================== ORIGINAL FUNCTIONS THAT WERE MISSING ====================

def show_dashboard():
    with st.spinner('Loading dashboard...'):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.title("📊 Dashboard Overview")
        st.markdown('</div>', unsafe_allow_html=True)
        
        user = st.session_state.user
        role = user['role']
        
        if role == 'facility_user':
            show_user_dashboard()
        elif role == 'facility_manager':
            show_manager_dashboard()
        else:
            show_vendor_dashboard()

def show_user_dashboard():
    user_requests = get_cached_user_requests(st.session_state.user['username'])
    
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

def show_manager_dashboard():
    all_requests = get_cached_all_requests()
    
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

def show_vendor_dashboard():
    vendor_requests = get_cached_vendor_requests(st.session_state.user['username'])
    
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
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("❌ Failed to create request")

def show_my_requests():
    with st.spinner('Loading your requests...'):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.title("📋 My Maintenance Requests")
        st.markdown('</div>', unsafe_allow_html=True)
        
        user_requests = get_cached_user_requests(st.session_state.user['username'])
        
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
        st.dataframe(df, use_container_width=True, hide_index=True)

def show_manage_requests():
    with st.spinner('Loading requests...'):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.title("🛠️ Manage Maintenance Requests")
        st.markdown('</div>', unsafe_allow_html=True)
        
        all_requests = get_cached_all_requests()
        
        if not all_requests:
            st.info("📭 No maintenance requests found")
            return
        
        # Simple filter
        status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Assigned", "Completed", "Approved"])
        
        filtered_requests = all_requests
        if status_filter != "All":
            filtered_requests = [req for req in filtered_requests if safe_str(req.get('status')) == status_filter]
        
        st.subheader(f"📊 Showing {len(filtered_requests)} request(s)")
        
        for request in filtered_requests[:10]:  # Limit to 10 for performance
            with st.expander(f"Request #{safe_get(request, 'id')}: {safe_str(safe_get(request, 'title'), 'N/A')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**📋 Basic Information**")
                    st.write(f"**Title:** {safe_str(safe_get(request, 'title'), 'N/A')}")
                    st.write(f"**Description:** {safe_str(safe_get(request, 'description'), 'N/A')}")
                    st.write(f"**Location:** {safe_str(safe_get(request, 'location'), 'Common Area')}")
                    st.write(f"**Priority:** {safe_str(safe_get(request, 'priority'), 'N/A')}")
                    st.write(f"**Status:** {safe_str(safe_get(request, 'status'), 'N/A')}")
                
                with col2:
                    st.write("**🛠️ Management Actions**")
                    
                    if safe_get(request, 'status') == 'Pending':
                        if st.button("👥 Assign to Vendor", key=f"assign_{safe_get(request, 'id')}"):
                            st.session_state[f"assigning_{safe_get(request, 'id')}"] = True
                    
                    if st.session_state.get(f"assigning_{safe_get(request, 'id')}"):
                        facility_type = safe_str(safe_get(request, 'facility_type'))
                        vendors = get_cached_vendors()
                        if vendors:
                            vendor_options = [f"{vendor['company_name']}" for vendor in vendors]
                            selected_vendor = st.selectbox("Select Vendor", vendor_options, key=f"vendor_select_{safe_get(request, 'id')}")
                            if st.button("✅ Confirm Assignment", key=f"confirm_{safe_get(request, 'id')}"):
                                if execute_update(
                                    'UPDATE maintenance_requests SET status = ?, assigned_vendor = ? WHERE id = ?',
                                    ('Assigned', selected_vendor, safe_get(request, 'id'))
                                ):
                                    st.success(f"✅ Request assigned to {selected_vendor}!")
                                    st.cache_data.clear()
                                    st.rerun()

def show_vendor_management():
    with st.spinner('Loading vendor data...'):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.title("👥 Vendor Management")
        st.markdown('</div>', unsafe_allow_html=True)
        
        vendors = get_cached_vendors()
        
        if not vendors:
            st.info("📭 No vendors registered yet")
            return
        
        st.subheader(f"📊 Registered Vendors ({len(vendors)})")
        
        for vendor in vendors[:10]:  # Limit display for performance
            with st.expander(f"{safe_str(safe_get(vendor, 'company_name'))}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**🏢 Company Information**")
                    st.write(f"**Company Name:** {safe_str(safe_get(vendor, 'company_name'), 'N/A')}")
                    st.write(f"**Contact Person:** {safe_str(safe_get(vendor, 'contact_person'), 'N/A')}")
                    st.write(f"**Email:** {safe_str(safe_get(vendor, 'email'), 'N/A')}")
                    st.write(f"**Phone:** {safe_str(safe_get(vendor, 'phone'), 'N/A')}")
                    st.write(f"**Vendor Type:** {safe_str(safe_get(vendor, 'vendor_type'), 'N/A')}")
                
                with col2:
                    st.write("**🔧 Services & Details**")
                    st.write(f"**Services Offered:** {safe_str(safe_get(vendor, 'services_offered'), 'N/A')}")
                    st.write(f"**Address:** {safe_str(safe_get(vendor, 'address'), 'N/A')}")
                    st.write(f"**Registration Date:** {safe_str(safe_get(vendor, 'registration_date'), 'N/A')}")

def show_reports():
    with st.spinner('Generating reports...'):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.title("📈 Reports & Analytics")
        st.markdown('</div>', unsafe_allow_html=True)
        
        all_requests = get_cached_all_requests()
        
        if not all_requests:
            st.info("📭 No data available for reports")
            return
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Requests", len(all_requests))
        with col2:
            completed = len([r for r in all_requests if r['status'] == 'Completed'])
            st.metric("Completed", completed)
        with col3:
            pending = len([r for r in all_requests if r['status'] == 'Pending'])
            st.metric("Pending", pending)
        with col4:
            total_invoice = sum([safe_float(r.get('invoice_amount', 0)) for r in all_requests])
            st.metric("Total Invoice", format_naira(total_invoice))
        
        # Simple chart
        status_counts = {}
        for req in all_requests:
            status = req.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if status_counts:
            fig = px.pie(values=list(status_counts.values()), names=list(status_counts.keys()), 
                        title="Request Status Distribution")
            st.plotly_chart(fig, use_container_width=True)

def show_assigned_jobs():
    with st.spinner('Loading assigned jobs...'):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.title("🔧 Assigned Jobs")
        st.markdown('</div>', unsafe_allow_html=True)
        
        vendor_requests = get_cached_vendor_requests(st.session_state.user['username'])
        assigned_jobs = [r for r in vendor_requests if safe_get(r, 'status') == 'Assigned']
        
        if not assigned_jobs:
            st.success("🎉 No assigned jobs found - all caught up!")
            return
        
        st.subheader(f"📊 You have {len(assigned_jobs)} assigned job(s)")
        
        for job in assigned_jobs[:5]:  # Limit for performance
            with st.expander(f"Job #{safe_get(job, 'id')}: {safe_str(safe_get(job, 'title'), 'N/A')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**📍 Location:** {safe_str(safe_get(job, 'location'), 'Common Area')}")
                    st.write(f"**🏢 Facility Type:** {safe_str(safe_get(job, 'facility_type'), 'N/A')}")
                    st.write(f"**📄 Description:** {safe_str(safe_get(job, 'description'), 'N/A')}")
                
                with col2:
                    if st.button("✅ Complete Job", key=f"complete_{safe_get(job, 'id')}"):
                        st.session_state[f"completing_{safe_get(job, 'id')}"] = True
                    
                    if st.session_state.get(f"completing_{safe_get(job, 'id')}"):
                        completion_notes = st.text_area("Completion Notes", key=f"notes_{safe_get(job, 'id')}")
                        if st.button("Submit Completion", key=f"submit_{safe_get(job, 'id')}"):
                            if execute_update(
                                'UPDATE maintenance_requests SET status = ?, completion_notes = ?, completed_date = ? WHERE id = ?',
                                ('Completed', completion_notes, datetime.now().strftime('%Y-%m-%d'), safe_get(job, 'id'))
                            ):
                                st.success("✅ Job completed successfully!")
                                st.cache_data.clear()
                                st.rerun()

def show_completed_jobs():
    with st.spinner('Loading completed jobs...'):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.title("✅ Completed Jobs")
        st.markdown('</div>', unsafe_allow_html=True)
        
        vendor_requests = get_cached_vendor_requests(st.session_state.user['username'])
        completed_jobs = [r for r in vendor_requests if safe_get(r, 'status') in ['Completed', 'Approved']]
        
        if not completed_jobs:
            st.info("📭 No completed jobs found")
            return
        
        display_data = []
        for job in completed_jobs[:10]:  # Limit for performance
            display_data.append({
                'ID': safe_get(job, 'id'),
                'Title': safe_str(safe_get(job, 'title'), 'N/A'),
                'Location': safe_str(safe_get(job, 'location'), 'Common Area'),
                'Invoice Amount': format_naira(safe_get(job, 'invoice_amount')),
                'Status': safe_str(safe_get(job, 'status'), 'N/A')
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
            st.write("**🏢 Company Information**")
            st.write(f"**Company Name:** {safe_str(safe_get(vendor, 'company_name'), 'N/A')}")
            st.write(f"**Contact Person:** {safe_str(safe_get(vendor, 'contact_person'), 'N/A')}")
            st.write(f"**Email:** {safe_str(safe_get(vendor, 'email'), 'N/A')}")
        
        with col2:
            st.write("**🔧 Services & Details**")
            st.write(f"**Services Offered:** {safe_str(safe_get(vendor, 'services_offered'), 'N/A')}")
            st.write(f"**Vendor Type:** {safe_str(safe_get(vendor, 'vendor_type'), 'N/A')}")
            st.write(f"**Registration Date:** {safe_str(safe_get(vendor, 'registration_date'), 'N/A')}")
        
        return
    
    st.info("📝 Please complete your vendor registration details below:")
    
    with st.form("vendor_registration", clear_on_submit=True):
        company_name = st.text_input("🏢 Company Name *")
        contact_person = st.text_input("👤 Contact Person *")
        email = st.text_input("📧 Email *")
        phone = st.text_input("📞 Phone *")
        services_offered = st.text_area("🔧 Services Offered *", height=100)
        address = st.text_area("📍 Address *", height=80)
        
        submitted = st.form_submit_button("🚀 Register Vendor", use_container_width=True)
        
        if submitted:
            if not all([company_name, contact_person, email, phone, services_offered, address]):
                st.error("⚠️ Please fill in all required fields (*)")
            else:
                success = execute_update(
                    '''INSERT INTO vendors (company_name, contact_person, email, phone, vendor_type, services_offered, address, username) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (company_name, contact_person, email, phone, st.session_state.user['vendor_type'], 
                     services_offered, address, st.session_state.user['username'])
                )
                if success:
                    st.success("✅ Vendor registration completed successfully!")
                    st.cache_data.clear()
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
    
    with st.form("invoice_creation_form", clear_on_submit=True):
        invoice_number = st.text_input("🔢 Invoice Number *")
        invoice_date = st.date_input("📅 Invoice Date *", value=date.today())
        details_of_work = st.text_area("🔧 Details of Work Done *", height=100)
        quantity = st.number_input("📦 Quantity *", min_value=1, value=1)
        unit_cost = st.number_input("💵 Unit Cost (₦) *", min_value=0.0, step=0.01, format="%.2f")
        
        submitted = st.form_submit_button("📄 Create Invoice", use_container_width=True)
        
        if submitted:
            if not all([invoice_number, details_of_work]):
                st.error("⚠️ Please fill in all required fields (*)")
            else:
                amount = quantity * unit_cost
                existing_invoice = execute_query('SELECT * FROM invoices WHERE invoice_number = ?', (invoice_number,))
                if existing_invoice:
                    st.error("❌ Invoice number already exists.")
                else:
                    success = execute_update(
                        '''INSERT INTO invoices (invoice_number, vendor_username, invoice_date, 
                        details_of_work, quantity, unit_cost, amount, total_amount, currency) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (invoice_number, st.session_state.user['username'], 
                         invoice_date.strftime('%Y-%m-%d'), details_of_work, quantity, unit_cost, 
                         amount, amount, '₦')
                    )
                    
                    if success:
                        st.success("✅ Invoice created successfully!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("❌ Failed to create invoice")

def show_job_invoice_reports():
    with st.spinner('Loading reports...'):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.title("📋 Job & Invoice Reports")
        st.markdown('</div>', unsafe_allow_html=True)
        
        completed_jobs = execute_query('''
            SELECT mr.*, i.invoice_number, i.invoice_date, i.total_amount as invoice_total
            FROM maintenance_requests mr
            LEFT JOIN invoices i ON mr.id = i.request_id
            WHERE mr.status IN ('Completed', 'Approved')
            ORDER BY mr.completed_date DESC
            LIMIT 20
        ''')
        
        if not completed_jobs:
            st.info("📭 No completed jobs with invoices found")
            return
        
        display_data = []
        for job in completed_jobs:
            display_data.append({
                'ID': safe_get(job, 'id'),
                'Title': safe_str(safe_get(job, 'title'), 'N/A'),
                'Location': safe_str(safe_get(job, 'location'), 'Common Area'),
                'Status': safe_str(safe_get(job, 'status'), 'N/A'),
                'Invoice Number': safe_str(safe_get(job, 'invoice_number'), 'No Invoice'),
                'Invoice Amount': format_naira(safe_get(job, 'invoice_total'))
            })
        
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

# PDF Generation Functions (simplified for performance)
def generate_job_completion_invoice_report(job_data, invoice_data=None):
    try:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        
        # Add content
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, "Job Completion & Invoice Report")
        
        c.setFont("Helvetica", 12)
        c.drawString(100, 730, f"Job ID: {safe_get(job_data, 'id', 'N/A')}")
        c.drawString(100, 710, f"Title: {safe_str(safe_get(job_data, 'title', 'N/A'))}")
        
        if invoice_data:
            c.drawString(100, 690, f"Invoice Amount: {format_naira(safe_get(invoice_data, 'total_amount', 0))}")
        
        c.showPage()
        c.save()
        
        buffer.seek(0)
        return buffer.getvalue()
    except:
        return None

def generate_invoice_report_pdf(invoice_data, job_data=None):
    try:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, "Invoice Report")
        
        c.setFont("Helvetica", 12)
        c.drawString(100, 730, f"Invoice Number: {safe_str(safe_get(invoice_data, 'invoice_number', 'N/A'))}")
        c.drawString(100, 710, f"Amount: {format_naira(safe_get(invoice_data, 'total_amount', 0))}")
        
        c.showPage()
        c.save()
        
        buffer.seek(0)
        return buffer.getvalue()
    except:
        return None

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
    with st.spinner('Loading space management...'):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.title("🏢 Space Management")
        st.markdown('</div>', unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["📅 View Bookings", "➕ New Booking", "📊 Analytics"])
        
        with tab1:
            show_space_bookings()
        
        with tab2:
            show_new_booking()
        
        with tab3:
            show_space_analytics()

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
    
    for room in rooms:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{room['name']}**")
            st.write(f"📍 {room['location']}")
            st.write(f"👥 Capacity: {room['capacity']} people")
            st.write(f"🎯 Amenities: {room['amenities']}")
        with col2:
            if st.button("Book Now", key=f"book_{room['name']}"):
                st.info(f"Booking {room['name']}...")

def show_new_booking():
    st.subheader("➕ New Space Booking")
    
    with st.form("new_booking_form"):
        room_name = st.selectbox(
            "🏢 Select Room",
            ["Conference Room A - Executive Suite", 
             "Conference Room B - Innovation Hub", 
             "Conference Room C - Boardroom"]
        )
        booking_date = st.date_input("📅 Booking Date", min_value=date.today())
        start_time = st.time_input("⏰ Start Time")
        end_time = st.time_input("⏰ End Time")
        purpose = st.text_input("🎯 Purpose of Booking")
        
        if st.form_submit_button("📅 Book Now", use_container_width=True):
            st.success("✅ Room booking request submitted successfully!")

def show_space_analytics():
    st.subheader("📊 Space Utilization Analytics")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📅 Total Bookings This Month", "42")
        st.metric("🏢 Most Used Room", "Conference Room A")
    with col2:
        st.metric("⏰ Average Booking Duration", "2.5 hours")
        st.metric("📈 Utilization Rate", "68%")

# 3. Preventive Maintenance Section
def show_preventive_maintenance():
    with st.spinner('Loading preventive maintenance...'):
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
    
    pm_schedules = get_cached_preventive_maintenance()
    
    if pm_schedules:
        categories = list(set([safe_get(sched, 'category') for sched in pm_schedules]))
        
        for category in categories[:3]:  # Limit for performance
            category_schedules = [s for s in pm_schedules if safe_get(s, 'category') == category]
            
            st.markdown(f'**{category}**')
            for schedule in category_schedules[:5]:  # Limit per category
                st.write(f"• {safe_get(schedule, 'service_code')}: {safe_get(schedule, 'service_description')}")
                st.write(f"  Frequency: {safe_get(schedule, 'frequency')} | Status: {safe_get(schedule, 'status')}")
                st.markdown('---')
    else:
        st.info("No preventive maintenance schedules found")

def show_add_pm_schedule():
    st.subheader("➕ Add New Preventive Maintenance Schedule")
    
    with st.form("add_pm_schedule_form"):
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
        frequency = st.selectbox("📅 Frequency", ["DAILY", "WEEKLY", "MONTHLY", "QUARTERLY", "BI-ANNUALLY", "ANNUALLY"])
        
        if st.form_submit_button("➕ Add Schedule", use_container_width=True):
            st.success("✅ Preventive maintenance schedule added successfully!")

def show_pm_analytics():
    st.subheader("📊 Preventive Maintenance Analytics")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📋 Total Schedules", "28")
        st.metric("✅ Completed This Month", "15")
    with col2:
        st.metric("📅 Due This Week", "8")
        st.metric("📈 Compliance Rate", "92%")

# 4. Generator Records
def show_generator_records():
    with st.spinner('Loading generator records...'):
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
    
    # Mock data
    records = [
        {
            'generator_id': 'GEN-001',
            'date': date.today(),
            'runtime_hours': 10,
            'fuel_consumed': 250,
            'oil_level': 'Normal',
            'load_percentage': 75
        },
        {
            'generator_id': 'GEN-002',
            'date': date.today() - timedelta(days=1),
            'runtime_hours': 8,
            'fuel_consumed': 200,
            'oil_level': 'Low',
            'load_percentage': 60
        }
    ]
    
    for record in records:
        st.write(f"**{record['generator_id']}** - {record['date']}")
        st.write(f"Runtime: {record['runtime_hours']} hours | Fuel: {record['fuel_consumed']}L")
        st.write(f"Oil: {record['oil_level']} | Load: {record['load_percentage']}%")
        st.markdown('---')

def show_new_generator_record():
    st.subheader("➕ New Generator Record")
    
    with st.form("new_generator_record_form"):
        generator_id = st.selectbox("🔧 Generator ID", ["GEN-001", "GEN-002", "GEN-003"])
        record_date = st.date_input("📅 Record Date", value=date.today())
        runtime_hours = st.number_input("⏰ Runtime Hours", min_value=0.0, step=0.1)
        fuel_consumed = st.number_input("⛽ Fuel Consumed (liters)", min_value=0.0, step=0.1)
        
        if st.form_submit_button("💾 Save Record", use_container_width=True):
            st.success("✅ Generator record saved successfully!")

def show_generator_analytics():
    st.subheader("📊 Generator Analytics")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("⚡ Total Runtime", "1,250 hours")
        st.metric("⛽ Fuel Consumed", "31,250 liters")
    with col2:
        st.metric("💰 Fuel Cost", "₦18,750,000")
        st.metric("📈 Efficiency", "85%")

# 5. HSE Management
def show_hse_management():
    with st.spinner('Loading HSE management...'):
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
            'next_due': date.today() + timedelta(days=45),
            'responsible': 'Fire Safety Limited'
        },
        {
            'activity': 'First Aid Kit Inspection',
            'frequency': 'Monthly',
            'next_due': date.today() + timedelta(days=15),
            'responsible': 'HSE Department'
        }
    ]
    
    for schedule in hse_schedule:
        st.write(f"**{schedule['activity']}**")
        st.write(f"Frequency: {schedule['frequency']} | Next Due: {schedule['next_due']}")
        st.write(f"Responsible: {schedule['responsible']}")
        st.markdown('---')

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
            'status': 'Resolved'
        },
        {
            'id': 'INC-2024-002',
            'title': 'Electrical Panel Overheating',
            'date': date.today() - timedelta(days=15),
            'location': 'Electrical Room',
            'severity': 'Medium',
            'status': 'Under Investigation'
        }
    ]
    
    for incident in incidents:
        st.write(f"**{incident['title']}** ({incident['id']})")
        st.write(f"Date: {incident['date']} | Location: {incident['location']}")
        st.write(f"Severity: {incident['severity']} | Status: {incident['status']}")
        st.markdown('---')

def show_new_inspection():
    st.subheader("➕ New HSE Inspection")
    
    with st.form("new_hse_inspection_form"):
        inspection_type = st.selectbox("📋 Inspection Type", [
            "Fire Safety", "First Aid", "Electrical Safety", 
            "Chemical Safety", "Workplace Ergonomics", "General Safety"
        ])
        location = st.selectbox("📍 Location", [
            "Main Building", "Annex Building", "Production Area", 
            "Warehouse", "Car Park", "Common Areas"
        ])
        inspection_date = st.date_input("📅 Inspection Date", value=date.today())
        findings = st.text_area("🔍 Findings/Observations", height=100)
        
        if st.form_submit_button("📋 Submit Inspection Report", use_container_width=True):
            st.success("✅ HSE inspection report submitted successfully!")

# 6. Compliance Dashboard
def show_compliance_dashboard():
    with st.spinner('Loading compliance dashboard...'):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.title("📊 Compliance Dashboard")
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📈 Overall Compliance", "92%")
        with col2:
            st.metric("✅ Compliant Items", "46")
        with col3:
            st.metric("⚠️ Non-Compliant", "4")
        with col4:
            st.metric("📅 Due This Month", "8")

# 7. Management Requests
def show_management_requests():
    with st.spinner('Loading management requests...'):
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
    
    pending_requests = execute_query(
        'SELECT * FROM maintenance_requests WHERE status = "Pending" ORDER BY created_date DESC LIMIT 10'
    )
    
    if pending_requests:
        for request in pending_requests:
            with st.expander(f"Request #{safe_get(request, 'id')}: {safe_str(safe_get(request, 'title'))}"):
                st.write(f"**Description:** {safe_str(safe_get(request, 'description'))}")
                st.write(f"**Location:** {safe_str(safe_get(request, 'location'))}")
                
                if st.button("👥 Assign to Vendor", key=f"assign_{safe_get(request, 'id')}"):
                    st.info("Assignment feature would open vendor selection here")
    else:
        st.info("No pending requests to assign")

def show_approve_jobs():
    st.subheader("✅ Approve Completed Jobs")
    
    completed_jobs = execute_query('''
        SELECT * FROM maintenance_requests 
        WHERE status = 'Completed' 
        AND requesting_dept_approval = 1 
        AND facilities_manager_approval = 0
        ORDER BY completed_date DESC
        LIMIT 10
    ''')
    
    if completed_jobs:
        for job in completed_jobs:
            with st.expander(f"Job #{safe_get(job, 'id')}: {safe_str(safe_get(job, 'title'))}"):
                st.write(f"**Job Breakdown:** {safe_str(safe_get(job, 'job_breakdown'))}")
                if st.button("✅ Approve Job Completion", key=f"approve_{safe_get(job, 'id')}"):
                    st.success("Job approved successfully!")
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
        pm_assignments = execute_query(
            'SELECT * FROM preventive_maintenance WHERE category LIKE ? LIMIT 10',
            (f'%{vendor_type}%',)
        )
        
        if pm_assignments:
            for pm in pm_assignments:
                st.write(f"**{safe_get(pm, 'service_code')}**: {safe_str(safe_get(pm, 'service_description'), 'N/A')}")
                st.write(f"Category: {safe_str(safe_get(pm, 'category'))} | Status: {safe_str(safe_get(pm, 'status'))}")
                if st.button("✅ Mark as Complete", key=f"complete_pm_{safe_get(pm, 'id')}"):
                    st.success("Maintenance marked as complete!")
                st.markdown('---')
        else:
            st.info("No preventive maintenance assigned to you")
    else:
        st.warning("Vendor type not specified")

# ==================== MAIN APP FUNCTION ====================

import threading

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
    else:
        show_dashboard()  # Default fallback

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
    # Initialize all session state variables
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'selected_menu' not in st.session_state:
        st.session_state.selected_menu = "Dashboard"
    
    # Initialize all dynamic state variables
    all_requests = get_cached_all_requests()
    for req in all_requests[:20]:  # Initialize for first 20 requests
        if f"assigning_{req['id']}" not in st.session_state:
            st.session_state[f"assigning_{req['id']}"] = False
        if f"completing_{req['id']}" not in st.session_state:
            st.session_state[f"completing_{req['id']}"] = False
    
    if st.session_state.user is None:
        show_login()
    else:
        show_main_app()

if __name__ == "__main__":
    init_database()
    main()
