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
import threading

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
    
    /* Job card styling */
    .job-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 5px solid #2196F3;
    }
    
    .job-card.assigned {
        border-left: 5px solid #FF9800;
    }
    
    .job-card.completed {
        border-left: 5px solid #4CAF50;
    }
    </style>
""", unsafe_allow_html=True)

# Database setup with enhanced schema
def init_database():
    try:
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
        
        # Maintenance requests table - check and add missing columns
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
        
        # Check if assigned_vendor_username column exists, add if not
        cursor.execute("PRAGMA table_info(maintenance_requests)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'assigned_vendor_username' not in columns:
            cursor.execute('ALTER TABLE maintenance_requests ADD COLUMN assigned_vendor_username TEXT')
            print("Added assigned_vendor_username column to maintenance_requests")
        
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
        
        # Check if assigned_vendor_username column exists, add if not
        cursor.execute("PRAGMA table_info(preventive_maintenance)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'assigned_vendor_username' not in columns:
            cursor.execute('ALTER TABLE preventive_maintenance ADD COLUMN assigned_vendor_username TEXT')
            print("Added assigned_vendor_username column to preventive_maintenance")
        
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
            except sqlite3.IntegrityError as e:
                print(f"User {username} already exists: {e}")
                continue
        
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
            except sqlite3.IntegrityError as e:
                print(f"Vendor {vendor_data[0]} already exists: {e}")
                continue
        
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
            except sqlite3.IntegrityError as e:
                print(f"PM schedule {service_code} already exists: {e}")
                continue
        
        # Check if we have any existing maintenance requests
        cursor.execute('SELECT COUNT(*) FROM maintenance_requests')
        count = cursor.fetchone()[0]
        
        # Only insert sample requests if table is empty
        if count == 0:
            sample_requests = [
                ('Faulty AC in HR Office', 'AC not cooling properly in HR office', 'HR', 'HVAC (Cooling Systems)', 'High', 'Assigned', 'facility_user', 'Provas Limited', 'provas_vendor'),
                ('Generator Maintenance Needed', 'Generator making unusual noise', 'Generator Room', 'Generator Maintenance', 'Critical', 'Assigned', 'facility_user', 'Generator Limited', 'generator_vendor'),
                ('Electrical Fault in Admin', 'Lights flickering in admin building', 'Admin', 'ELECTRICAL SYSTEMS INSPECTIONS', 'Medium', 'Assigned', 'facility_user', 'Power Solutions Ltd', 'power_vendor'),
                ('Fire Extinguisher Check', 'Monthly fire extinguisher inspection', 'Common Area', 'FIRE FIGHTING AND ALARM SYSTEMS', 'Low', 'Assigned', 'facility_user', 'Fire Safety Limited', 'fire_vendor'),
                ('Cleaning Services Required', 'Deep cleaning needed in common areas', 'Common Area', 'ENVIRONMENTAL / CLEANING CARE', 'Medium', 'Assigned', 'facility_user', 'Environmental Solutions Ltd', 'env_vendor'),
                ('Water Pump Issue', 'Water pressure low in main building', 'Water Treatment Plant', 'WATER SYSTEM MAINTENANCE', 'High', 'Assigned', 'facility_user', 'Watreatment Lab Solutions', 'water_vendor'),
            ]
            
            for title, description, location, facility_type, priority, status, created_by, assigned_vendor, assigned_vendor_username in sample_requests:
                try:
                    cursor.execute('''
                        INSERT INTO maintenance_requests 
                        (title, description, location, facility_type, priority, status, created_by, assigned_vendor, assigned_vendor_username) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (title, description, location, facility_type, priority, status, created_by, assigned_vendor, assigned_vendor_username))
                except Exception as e:
                    print(f"Error inserting sample request: {e}")
                    # Try without assigned_vendor_username if column doesn't exist yet
                    try:
                        cursor.execute('''
                            INSERT INTO maintenance_requests 
                            (title, description, location, facility_type, priority, status, created_by, assigned_vendor) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (title, description, location, facility_type, priority, status, created_by, assigned_vendor))
                    except Exception as e2:
                        print(f"Error with fallback insert: {e2}")
        
        conn.commit()
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        st.error(f"Database initialization error: {e}")
        # Try to create a fresh database if there's an error
        try:
            if 'conn' in locals():
                conn.close()
            os.remove('facilities_management.db') if os.path.exists('facilities_management.db') else None
            print("Created fresh database")
        except:
            pass
    finally:
        if 'conn' in locals():
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
    """Get jobs assigned to vendor by username"""
    # Try with new column first, fall back to old column
    try:
        result = execute_query(
            'SELECT * FROM maintenance_requests WHERE assigned_vendor_username = ? ORDER BY created_date DESC',
            (vendor_username,)
        )
        if not result:
            # Fallback to checking assigned_vendor field for company name
            vendor_info = get_vendor_by_username(vendor_username)
            if vendor_info:
                company_name = vendor_info.get('company_name')
                if company_name:
                    result = execute_query(
                        'SELECT * FROM maintenance_requests WHERE assigned_vendor = ? ORDER BY created_date DESC',
                        (company_name,)
                    )
        return result
    except:
        return []

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cached_vendors():
    return execute_query('SELECT * FROM vendors ORDER BY company_name')

@st.cache_data(ttl=300)
def get_cached_preventive_maintenance():
    return execute_query('SELECT * FROM preventive_maintenance ORDER BY category, service_code')

@st.cache_data(ttl=60)
def get_vendor_by_username(username):
    """Get vendor details by username"""
    result = execute_query('SELECT * FROM vendors WHERE username = ?', (username,))
    return result[0] if result else None

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

# ==================== ORIGINAL FUNCTIONS ====================

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
    
    # Show assigned jobs
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    st.subheader("🔧 Your Assigned Jobs")
    
    assigned_jobs = [r for r in vendor_requests if safe_get(r, 'status') == 'Assigned']
    
    if assigned_jobs:
        for job in assigned_jobs[:5]:  # Show first 5
            st.markdown(f'''
                <div class="job-card assigned">
                    <h4 style="margin: 0 0 10px 0;">{safe_str(safe_get(job, 'title'))}</h4>
                    <p style="margin: 5px 0;"><strong>📍 Location:</strong> {safe_str(safe_get(job, 'location'))}</p>
                    <p style="margin: 5px 0;"><strong>🚨 Priority:</strong> {safe_str(safe_get(job, 'priority'))}</p>
                    <p style="margin: 5px 0;"><strong>📅 Created:</strong> {safe_str(safe_get(job, 'created_date'))[:10]}</p>
                    <p style="margin: 5px 0;"><strong>📝 Description:</strong> {safe_str(safe_get(job, 'description'))[:100]}...</p>
                </div>
            ''', unsafe_allow_html=True)
    else:
        st.info("📭 No assigned jobs at the moment")

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
                'Assigned To': safe_str(safe_get(req, 'assigned_vendor'), 'Not assigned'),
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
            with st.expander(f"Request #{safe_get(request, 'id')}: {safe_str(safe_get(request, 'title'), 'N/A')} - Status: {safe_str(safe_get(request, 'status'), 'N/A')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**📋 Basic Information**")
                    st.write(f"**Title:** {safe_str(safe_get(request, 'title'), 'N/A')}")
                    st.write(f"**Description:** {safe_str(safe_get(request, 'description'), 'N/A')}")
                    st.write(f"**Location:** {safe_str(safe_get(request, 'location'), 'Common Area')}")
                    st.write(f"**Priority:** {safe_str(safe_get(request, 'priority'), 'N/A')}")
                    st.write(f"**Status:** {safe_str(safe_get(request, 'status'), 'N/A')}")
                    st.write(f"**Created By:** {safe_str(safe_get(request, 'created_by'), 'N/A')}")
                
                with col2:
                    st.write("**🛠️ Management Actions**")
                    
                    if safe_get(request, 'status') == 'Pending':
                        if st.button("👥 Assign to Vendor", key=f"assign_{safe_get(request, 'id')}"):
                            st.session_state[f"assigning_{safe_get(request, 'id')}"] = True
                    
                    if st.session_state.get(f"assigning_{safe_get(request, 'id')}"):
                        facility_type = safe_str(safe_get(request, 'facility_type'))
                        vendors = get_cached_vendors()
                        
                        # Filter vendors by facility type
                        filtered_vendors = []
                        for vendor in vendors:
                            vendor_type = safe_str(safe_get(vendor, 'vendor_type'))
                            if facility_type.upper() in vendor_type.upper() or vendor_type.upper() in facility_type.upper():
                                filtered_vendors.append(vendor)
                        
                        if filtered_vendors:
                            vendor_options = [f"{vendor['company_name']} ({vendor['username']})" for vendor in filtered_vendors]
                            selected_vendor = st.selectbox("Select Vendor", vendor_options, key=f"vendor_select_{safe_get(request, 'id')}")
                            
                            if st.button("✅ Confirm Assignment", key=f"confirm_{safe_get(request, 'id')}"):
                                # Extract vendor username from selection
                                vendor_username = selected_vendor.split('(')[-1].rstrip(')')
                                vendor_name = selected_vendor.split('(')[0].strip()
                                
                                if execute_update(
                                    'UPDATE maintenance_requests SET status = ?, assigned_vendor = ?, assigned_vendor_username = ? WHERE id = ?',
                                    ('Assigned', vendor_name, vendor_username, safe_get(request, 'id'))
                                ):
                                    st.success(f"✅ Request assigned to {vendor_name}!")
                                    st.cache_data.clear()
                                    st.rerun()
                        else:
                            st.warning(f"No vendors found for {facility_type}")

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
                    st.write(f"**Username:** {safe_str(safe_get(vendor, 'username'), 'N/A')}")

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
            st.info("📭 No assigned jobs at the moment")
            return
        
        st.subheader(f"📊 You have {len(assigned_jobs)} assigned job(s)")
        
        for job in assigned_jobs:
            st.markdown(f'''
                <div class="job-card assigned">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div style="flex: 1;">
                            <h4 style="margin: 0 0 10px 0;">{safe_str(safe_get(job, 'title'), 'N/A')}</h4>
                            <p style="margin: 5px 0;"><strong>📅 Request ID:</strong> #{safe_get(job, 'id')}</p>
                            <p style="margin: 5px 0;"><strong>📍 Location:</strong> {safe_str(safe_get(job, 'location'), 'Common Area')}</p>
                            <p style="margin: 5px 0;"><strong>🏢 Facility Type:</strong> {safe_str(safe_get(job, 'facility_type'), 'N/A')}</p>
                            <p style="margin: 5px 0;"><strong>🚨 Priority:</strong> {safe_str(safe_get(job, 'priority'), 'N/A')}</p>
                            <p style="margin: 5px 0;"><strong>📅 Created:</strong> {safe_str(safe_get(job, 'created_date'), 'N/A')[:10]}</p>
                            <p style="margin: 5px 0;"><strong>👤 Created By:</strong> {safe_str(safe_get(job, 'created_by'), 'N/A')}</p>
                        </div>
                        <div style="margin-left: 20px;">
                            <span class="status-badge status-assigned">ASSIGNED</span>
                        </div>
                    </div>
                    
                    <div style="margin-top: 15px; padding: 15px; background: #f8f9fa; border-radius: 5px;">
                        <p style="margin: 0 0 10px 0; font-weight: bold;">📝 Description:</p>
                        <p style="margin: 0;">{safe_str(safe_get(job, 'description'), 'No description provided')}</p>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
            
            # Complete Job Form
            with st.expander(f"✅ Complete Job #{safe_get(job, 'id')}", expanded=False):
                with st.form(f"complete_job_{safe_get(job, 'id')}"):
                    completion_notes = st.text_area("📝 Completion Notes", 
                                                   placeholder="Describe what work was completed...",
                                                   height=100)
                    job_breakdown = st.text_area("🔧 Job Breakdown", 
                                                placeholder="Detailed breakdown of work done...",
                                                height=100)
                    completion_date = st.date_input("📅 Completion Date", value=date.today())
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        invoice_amount = st.number_input("💰 Invoice Amount (₦)", min_value=0.0, step=0.01, format="%.2f")
                    with col2:
                        invoice_number = st.text_input("🔢 Invoice Number", placeholder="e.g., INV-001")
                    
                    submitted = st.form_submit_button("✅ Mark as Complete", use_container_width=True)
                    
                    if submitted:
                        if not completion_notes:
                            st.error("Please provide completion notes")
                        else:
                            if execute_update(
                                '''UPDATE maintenance_requests SET status = ?, completion_notes = ?, job_breakdown = ?, 
                                completed_date = ?, invoice_amount = ?, invoice_number = ? WHERE id = ?''',
                                ('Completed', completion_notes, job_breakdown, 
                                 completion_date.strftime('%Y-%m-%d'), invoice_amount, 
                                 invoice_number, safe_get(job, 'id'))
                            ):
                                st.success("✅ Job marked as complete! Waiting for approval.")
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
        WHERE mr.assigned_vendor_username = ? AND mr.status = 'Completed' AND i.id IS NULL
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
                    # Get the first job that needs an invoice
                    job = vendor_jobs[0]
                    success = execute_update(
                        '''INSERT INTO invoices (invoice_number, request_id, vendor_username, invoice_date, 
                        details_of_work, quantity, unit_cost, amount, total_amount, currency) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (invoice_number, job['id'], st.session_state.user['username'], 
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

# ==================== SIMPLIFIED FEATURES (for performance) ====================

def show_space_management():
    with st.spinner('Loading space management...'):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.title("🏢 Space Management")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.subheader("📅 Conference Room Bookings")
        st.info("Space Management feature is available. More details coming soon!")

def show_preventive_maintenance():
    with st.spinner('Loading preventive maintenance...'):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.title("🔧 Preventive Maintenance")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.subheader("📅 Preventive Maintenance Schedule")
        st.info("Preventive Maintenance feature is available. More details coming soon!")

def show_generator_records():
    with st.spinner('Loading generator records...'):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.title("⚡ Generator Records")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.subheader("📅 Daily Generator Records")
        st.info("Generator Records feature is available. More details coming soon!")

def show_hse_management():
    with st.spinner('Loading HSE management...'):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.title("🛡️ HSE Management")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.subheader("📅 HSE Inspection Schedule")
        st.info("HSE Management feature is available. More details coming soon!")

def show_compliance_dashboard():
    with st.spinner('Loading compliance dashboard...'):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.title("📊 Compliance Dashboard")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.subheader("Overall Compliance Status")
        st.info("Compliance Dashboard feature is available. More details coming soon!")

def show_management_requests():
    with st.spinner('Loading management requests...'):
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.title("👨‍💼 Management Requests")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.subheader("Assign & Approve Jobs")
        st.info("Management Requests feature is available. More details coming soon!")

def show_assigned_preventive_maintenance():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🔧 Assigned Preventive Maintenance")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.subheader("Your Preventive Maintenance Tasks")
    st.info("Assigned Preventive Maintenance feature is available. More details coming soon!")

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

# ==================== MAIN APP FUNCTION ====================

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
                "Space Management", "Manage Request",
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
    
    if st.session_state.user is None:
        show_login()
    else:
        show_main_app()

if __name__ == "__main__":
    init_database()
    main()
