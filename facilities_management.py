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
        'About': "### Facilities Management System v4.0\nDeveloped by Abdulahi Ibrahim\n© 2024 All Rights Reserved"
    }
)

# Enhanced Custom CSS for modern UI
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
    
    /* Modern Card Design */
    .modern-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        margin-bottom: 25px;
        border: 1px solid #e0e0e0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .modern-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.12);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #4CAF50, #2E7D32);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 7px 20px rgba(76, 175, 80, 0.3);
    }
    
    /* Quick Action Buttons - Modern Design */
    .quick-action-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin: 20px 0;
    }
    
    .quick-action-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .quick-action-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.2);
    }
    
    .quick-action-icon {
        font-size: 32px;
        margin-bottom: 10px;
    }
    
    .quick-action-text {
        font-size: 14px;
        font-weight: 500;
    }
    
    /* Status badges - Modern */
    .status-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-pending { 
        background: linear-gradient(45deg, #FFEAA7, #E17055);
        color: #fff;
    }
    .status-assigned { 
        background: linear-gradient(45deg, #74B9FF, #0984E3);
        color: #fff;
    }
    .status-completed { 
        background: linear-gradient(45deg, #55EFC4, #00B894);
        color: #fff;
    }
    .status-approved { 
        background: linear-gradient(45deg, #81ECEC, #00CEC9);
        color: #fff;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(90deg, #1a237e, #283593);
        padding: 25px;
        border-radius: 15px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2c3e50, #34495e) !important;
        padding: 20px;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
    }
    
    /* Dashboard Metrics */
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        margin: 10px 0;
    }
    
    .metric-label {
        font-size: 14px;
        opacity: 0.9;
    }
    
    /* Table styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    }
    
    /* Form styling */
    .stTextInput > div > div > input,
    .stTextInput > div > div > input:focus {
        background-color: white;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 12px;
        font-size: 16px;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
    }
    
    .stSelectbox > div > div > div,
    .stTextArea > div > div > textarea {
        background-color: white;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        transition: border-color 0.3s ease;
    }
    
    .stSelectbox > div > div > div:hover,
    .stTextArea > div > div > textarea:hover {
        border-color: #4CAF50;
    }
    
    /* Conference Room Card */
    .room-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        border-left: 5px solid #4CAF50;
        transition: transform 0.3s ease;
    }
    
    .room-card:hover {
        transform: translateY(-3px);
    }
    
    .room-card.booked {
        border-left: 5px solid #f44336;
    }
    
    .room-card.available {
        border-left: 5px solid #4CAF50;
    }
    
    /* Schedule Table */
    .schedule-item {
        background: white;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 3px 10px rgba(0,0,0,0.05);
        border-left: 4px solid #2196F3;
    }
    
    /* Frequency badges */
    .frequency-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 11px;
        font-weight: 600;
    }
    
    .frequency-daily { background-color: #E3F2FD; color: #1976D2; }
    .frequency-weekly { background-color: #E8F5E9; color: #388E3C; }
    .frequency-monthly { background-color: #FFF3E0; color: #F57C00; }
    .frequency-quarterly { background-color: #FCE4EC; color: #C2185B; }
    .frequency-bi-annually { background-color: #F3E5F5; color: #7B1FA2; }
    .frequency-annually { background-color: #E0F2F1; color: #00796B; }
    
    /* Loading spinner */
    .loading-spinner {
        display: inline-block;
        width: 50px;
        height: 50px;
        border: 5px solid #f3f3f3;
        border-top: 5px solid #4CAF50;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50 !important;
        color: white !important;
    }
    
    /* Progress bars */
    .progress-container {
        background: #e0e0e0;
        border-radius: 10px;
        overflow: hidden;
        height: 10px;
        margin: 10px 0;
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(45deg, #4CAF50, #2E7D32);
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    
    /* Footer */
    .app-footer {
        background: linear-gradient(90deg, #1a237e, #283593);
        color: white;
        text-align: center;
        padding: 15px;
        margin-top: 40px;
        border-radius: 10px;
        font-size: 12px;
        opacity: 0.9;
    }
    
    /* Notification badge */
    .notification-badge {
        position: absolute;
        top: -5px;
        right: -5px;
        background: #f44336;
        color: white;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        font-size: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
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
                department TEXT,
                email TEXT,
                phone TEXT,
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
                assigned_vendor_username TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_date TIMESTAMP,
                completion_notes TEXT,
                job_breakdown TEXT,
                invoice_amount REAL DEFAULT 0,
                invoice_number TEXT,
                requesting_dept_approval BOOLEAN DEFAULT 0,
                facilities_manager_approval BOOLEAN DEFAULT 0,
                user_approval BOOLEAN DEFAULT 0
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
                contract_start DATE,
                contract_end DATE,
                contract_value REAL,
                status TEXT DEFAULT 'Active'
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
                vat_rate REAL DEFAULT 7.5,
                total_amount REAL NOT NULL,
                currency TEXT DEFAULT 'NGN',
                payment_status TEXT DEFAULT 'Pending',
                payment_date DATE,
                notes TEXT,
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
                approved_by TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Preventive Maintenance Schedule table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preventive_maintenance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_code TEXT NOT NULL UNIQUE,
                service_description TEXT NOT NULL,
                category TEXT NOT NULL,
                frequency TEXT NOT NULL,
                last_performed DATE,
                next_due DATE,
                assigned_vendor TEXT,
                assigned_vendor_username TEXT,
                status TEXT DEFAULT 'Scheduled',
                estimated_hours INTEGER DEFAULT 2,
                required_skills TEXT,
                safety_requirements TEXT,
                notes TEXT
            )
        ''')
        
        # Generator Records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS generator_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                generator_id TEXT NOT NULL,
                generator_name TEXT NOT NULL,
                record_date DATE NOT NULL,
                start_time TIME,
                end_time TIME,
                runtime_hours REAL,
                fuel_consumed_liters REAL,
                fuel_cost_per_liter REAL,
                oil_level TEXT,
                coolant_level TEXT,
                battery_status TEXT,
                load_percentage REAL,
                voltage_output REAL,
                frequency_output REAL,
                ambient_temperature REAL,
                issues_noted TEXT,
                maintenance_performed TEXT,
                recorded_by TEXT,
                verified_by TEXT,
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
                preventive_measures TEXT,
                investigation_report TEXT,
                closed_date DATE,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # HSE Inspections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hse_inspections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inspection_type TEXT NOT NULL,
                location TEXT NOT NULL,
                inspection_date DATE NOT NULL,
                inspector TEXT NOT NULL,
                findings TEXT,
                recommendations TEXT,
                status TEXT DEFAULT 'Scheduled',
                follow_up_date DATE,
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
                audit_date DATE,
                compliance_score INTEGER,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Conference Rooms table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conference_rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_name TEXT NOT NULL UNIQUE,
                room_type TEXT NOT NULL,
                capacity INTEGER NOT NULL,
                floor INTEGER,
                building TEXT,
                amenities TEXT,
                hourly_rate REAL DEFAULT 0,
                status TEXT DEFAULT 'Available',
                image_url TEXT
            )
        ''')
        
        # Insert sample users
        sample_users = [
            ('facility_user', '0123456', 'facility_user', None, 'Operations', 'user@example.com', '080-1111-1111'),
            ('facility_manager', '0123456', 'facility_manager', None, 'Facilities', 'manager@example.com', '080-2222-2222'),
            ('provas_vendor', '123456', 'vendor', 'AIR CONDITIONING SYSTEM', None, 'provas@example.com', '080-1234-5678'),
            ('power_vendor', '123456', 'vendor', 'ELECTRICAL SYSTEMS INSPECTIONS', None, 'power@example.com', '080-2345-6789'),
            ('fire_vendor', '123456', 'vendor', 'FIRE FIGHTING AND ALARM SYSTEMS', None, 'fire@example.com', '080-3456-7890'),
            ('env_vendor', '123456', 'vendor', 'ENVIRONMENTAL / CLEANING CARE', None, 'env@example.com', '080-4567-8901'),
            ('water_vendor', '123456', 'vendor', 'WATER SYSTEM MAINTENANCE', None, 'water@example.com', '080-5678-9012'),
            ('generator_vendor', '123456', 'vendor', 'GENERATOR MAINTENANCE AND REPAIRS', None, 'generator@example.com', '080-6789-0123')
        ]
        
        for user_data in sample_users:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO users 
                    (username, password_hash, role, vendor_type, department, email, phone) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', user_data)
            except sqlite3.IntegrityError:
                continue
        
        # Insert sample vendors
        sample_vendors = [
            ('provas_vendor', 'Provas Limited', 'John HVAC', 'provas@example.com', '080-1234-5678', 'AIR CONDITIONING SYSTEM', 
             'HVAC installation, maintenance and repair services', 50000000.00, 'TIN123456', 'RC789012',
             'John Smith (CEO), Jane Doe (Operations Manager)', 'Bank: Zenith Bank, Acc: 1234567890', 
             'HVAC Certified', '123 HVAC Street, Lagos', '2024-01-01', '2024-12-31', 5000000.00, 'Active'),
            ('power_vendor', 'Power Solutions Ltd', 'Mike Power', 'power@example.com', '080-2345-6789', 'ELECTRICAL SYSTEMS INSPECTIONS',
             'Electrical systems inspection and maintenance', 30000000.00, 'TIN123457', 'RC789013',
             'Mike Johnson (Director)', 'Bank: First Bank, Acc: 9876543210', 
             'Electrical Engineer Certified', '456 Power Ave, Abuja', '2024-01-01', '2024-12-31', 3000000.00, 'Active'),
            ('fire_vendor', 'Fire Safety Limited', 'Sarah Fire', 'fire@example.com', '080-3456-7890', 'FIRE FIGHTING AND ALARM SYSTEMS',
             'Fire fighting equipment and alarm systems maintenance', 25000000.00, 'TIN123458', 'RC789014',
             'Sarah Wilson (Owner)', 'Bank: GTBank, Acc: 4561237890', 
             'Fire Safety Expert', '789 Fire Road, Port Harcourt', '2024-01-01', '2024-12-31', 2500000.00, 'Active'),
            ('env_vendor', 'Environmental Solutions Ltd', 'David Clean', 'env@example.com', '080-4567-8901', 'ENVIRONMENTAL / CLEANING CARE',
             'Environmental cleaning and pest control', 40000000.00, 'TIN123459', 'RC789015',
             'David Brown (Manager)', 'Bank: Access Bank, Acc: 7894561230', 
             'Environmental Certified', '321 Cleaners Lane, Kano', '2024-01-01', '2024-12-31', 4000000.00, 'Active'),
            ('water_vendor', 'Watreatment Lab Solutions', 'Peter Water', 'water@example.com', '080-5678-9012', 'WATER SYSTEM MAINTENANCE',
             'Water system maintenance and treatment', 35000000.00, 'TIN123460', 'RC789016',
             'Peter Miller (Director)', 'Bank: UBA, Acc: 6543219870', 
             'Water Treatment Expert', '654 Water Street, Ibadan', '2024-01-01', '2024-12-31', 3500000.00, 'Active'),
            ('generator_vendor', 'Generator Limited', 'James Generator', 'generator@example.com', '080-6789-0123', 'GENERATOR MAINTENANCE AND REPAIRS',
             'Generator maintenance and repairs', 45000000.00, 'TIN123461', 'RC789017',
             'James Wilson (Owner)', 'Bank: Sterling Bank, Acc: 3216549870', 
             'Generator Specialist', '987 Power Road, Benin', '2024-01-01', '2024-12-31', 4500000.00, 'Active')
        ]
        
        for vendor_data in sample_vendors:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO vendors 
                    (username, company_name, contact_person, email, phone, vendor_type, services_offered, 
                     annual_turnover, tax_identification_number, rc_number, key_management_staff, 
                     account_details, certification, address, contract_start, contract_end, contract_value, status) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', vendor_data)
            except sqlite3.IntegrityError:
                continue
        
        # Insert sample conference rooms
        conference_rooms = [
            ('Conference Room A', 'Large Conference', 30, 3, 'Main Building', 
             'Projector, Whiteboard, Video Conferencing, WiFi', 5000.00, 'Available'),
            ('Conference Room B', 'Medium Conference', 15, 3, 'Main Building', 
             'TV Screen, Whiteboard, WiFi', 3000.00, 'Available'),
            ('Board Room', 'Executive Boardroom', 12, 5, 'Executive Wing', 
             'Smart TV, Video Conferencing, Coffee Machine, WiFi', 8000.00, 'Available'),
            ('Training Room', 'Training Facility', 40, 2, 'Annex Building', 
             'Projector, Whiteboard, Sound System, WiFi', 4000.00, 'Available')
        ]
        
        for room_data in conference_rooms:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO conference_rooms 
                    (room_name, room_type, capacity, floor, building, amenities, hourly_rate, status) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', room_data)
            except sqlite3.IntegrityError:
                continue
        
        # Insert sample preventive maintenance
        pm_schedules = [
            # AIR CONDITIONING SYSTEM
            ('PPM/AC/001', 'Routine Inspection of all AC units in the main block and common areas.', 
             'AIR CONDITIONING SYSTEM', 'MONTHLY', None, '2024-12-01', 'Provas Limited', 'provas_vendor', 'Scheduled'),
            ('PPM/AC/002', 'Routine Servicing of all split units in the common areas', 
             'AIR CONDITIONING SYSTEM', 'QUARTERLY', '2024-09-01', '2024-12-01', 'Provas Limited', 'provas_vendor', 'Scheduled'),
            ('PPM/AC/003', 'Routine Servicing of all standing AC Units', 
             'AIR CONDITIONING SYSTEM', 'QUARTERLY', '2024-09-01', '2024-12-01', 'Provas Limited', 'provas_vendor', 'Scheduled'),
            ('PPM/AC/004', 'Routine Servicing of all Central air-conditioning units in the main building', 
             'AIR CONDITIONING SYSTEM', 'QUARTERLY', '2024-09-01', '2024-12-01', 'Provas Limited', 'provas_vendor', 'Scheduled'),
            
            # ELECTRICAL SYSTEMS INSPECTIONS
            ('PPM/ELECT/001', 'Inspection of bulbs and lighting systems in offices and common areas / Cleaning of extractor fans', 
             'ELECTRICAL SYSTEMS INSPECTIONS', 'DAILY', '2024-11-25', '2024-11-26', 'Power Solutions Ltd', 'power_vendor', 'Completed'),
            ('PPM/ELECT/002', 'Inspection, checks and cleaning of lighting systems in the common area, stairways, service buildings and perimeter fence', 
             'ELECTRICAL SYSTEMS INSPECTIONS', 'MONTHLY', '2024-11-01', '2024-12-01', 'Power Solutions Ltd', 'power_vendor', 'Scheduled'),
            
            # FIRE FIGHTING AND ALARM SYSTEMS
            ('PPM/FIRE/001', 'Check performances of the smoke detectors, heat detectors and break glasses', 
             'FIRE FIGHTING AND ALARM SYSTEMS', 'QUARTERLY', '2024-09-01', '2024-12-01', 'Fire Safety Limited', 'fire_vendor', 'Scheduled'),
            ('PPM/FIRE/005', 'Inspection of fire fighting equipment', 
             'FIRE FIGHTING AND ALARM SYSTEMS', 'WEEKLY', '2024-11-24', '2024-12-01', 'Fire Safety Limited', 'fire_vendor', 'Completed'),
            
            # ENVIRONMENTAL / CLEANING CARE
            ('PPM/CLEAN/003', 'Daily cleaning of the premises', 
             'ENVIRONMENTAL / CLEANING CARE', 'DAILY', '2024-11-25', '2024-11-26', 'Environmental Solutions Ltd', 'env_vendor', 'In Progress'),
            ('PPM/CLEAN/006', 'Inspection and cleaning of the rooftop gutters / Clearing of weeds around the building', 
             'ENVIRONMENTAL / CLEANING CARE', 'MONTHLY', '2024-11-01', '2024-12-01', 'Environmental Solutions Ltd', 'env_vendor', 'Scheduled'),
            
            # WATER SYSTEM MAINTENANCE
            ('PPM/WSM/001', 'Daily check on water pumps and submersible pumps', 
             'WATER SYSTEM MAINTENANCE', 'DAILY', '2024-11-25', '2024-11-26', 'Watreatment Lab Solutions', 'water_vendor', 'Completed'),
            ('PPM/WSM/004', 'Servicing of water pumps', 
             'WATER SYSTEM MAINTENANCE', 'QUARTERLY', '2024-09-01', '2024-12-01', 'Watreatment Lab Solutions', 'water_vendor', 'Scheduled'),
        ]
        
        for pm_data in pm_schedules:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO preventive_maintenance 
                    (service_code, service_description, category, frequency, last_performed, next_due, assigned_vendor, assigned_vendor_username, status) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', pm_data)
            except sqlite3.IntegrityError:
                continue
        
        # Insert sample space bookings
        sample_bookings = [
            ('Conference Room A', 'Large Conference', '2024-11-28', '09:00', '11:00', 
             'John Doe', 'Quarterly Business Review', 15, 'Confirmed'),
            ('Board Room', 'Executive Boardroom', '2024-11-28', '14:00', '16:00', 
             'Jane Smith', 'Executive Meeting', 8, 'Confirmed'),
            ('Conference Room B', 'Medium Conference', '2024-11-29', '10:00', '12:00', 
             'Mike Johnson', 'Team Workshop', 12, 'Confirmed'),
        ]
        
        for booking_data in sample_bookings:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO space_bookings 
                    (room_name, room_type, booking_date, start_time, end_time, booked_by, purpose, attendees_count, status) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', booking_data)
            except sqlite3.IntegrityError:
                continue
        
        # Insert sample generator records
        generator_records = [
            ('GEN-001', 'Main Generator', '2024-11-25', '08:00', '17:00', 9.0, 90.0, 250.0, 
             'Normal', 'Normal', 'Good', 75.0, 240.0, 50.0, 28.0, 'None', 'Routine check', 'facility_user', 'facility_manager'),
            ('GEN-002', 'Backup Generator', '2024-11-25', '10:00', '12:00', 2.0, 20.0, 250.0, 
             'Low', 'Normal', 'Good', 50.0, 240.0, 50.0, 30.0, 'Slight vibration', 'Tightened bolts', 'facility_user', 'facility_manager'),
        ]
        
        for gen_data in generator_records:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO generator_records 
                    (generator_id, generator_name, record_date, start_time, end_time, runtime_hours, fuel_consumed_liters, fuel_cost_per_liter, 
                     oil_level, coolant_level, battery_status, load_percentage, voltage_output, frequency_output, ambient_temperature, 
                     issues_noted, maintenance_performed, recorded_by, verified_by) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', gen_data)
            except sqlite3.IntegrityError:
                continue
        
        # Insert sample HSE records
        hse_records = [
            ('Inspection', 'Fire Safety Inspection', 'Monthly fire safety equipment check', 
             'Main Building', '2024-11-25', 'Low', 'facility_manager', 'Safety Officer', 
             'Closed', 'All fire extinguishers checked and tagged', 'Quarterly inspection schedule'),
            ('Incident', 'Slip and Fall Incident', 'Employee slipped in wet corridor', 
             'Ground Floor Corridor', '2024-11-24', 'Medium', 'facility_user', 'HSE Manager', 
             'Open', 'Wet floor signs placed, floor dried', 'Implement non-slip mats'),
        ]
        
        for hse_data in hse_records:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO hse_records 
                    (record_type, title, description, location, date_occurred, severity, reported_by, assigned_to, 
                     status, corrective_actions, preventive_measures) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', hse_data)
            except sqlite3.IntegrityError:
                continue
        
        conn.commit()
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        st.error(f"Database initialization error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

# Initialize database
init_database()

# Connection pool for better performance
connection_pool = {}

def get_connection():
    thread_id = threading.get_ident()
    if thread_id not in connection_pool:
        connection_pool[thread_id] = sqlite3.connect('facilities_management.db', check_same_thread=False)
        connection_pool[thread_id].row_factory = sqlite3.Row
    return connection_pool[thread_id]

def execute_query(query, params=()):
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
        pass

def execute_update(query, params=()):
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
        pass

# Helper functions
def safe_get(data, key, default=None):
    if not data or not isinstance(data, dict):
        return default
    return data.get(key, default)

def format_naira(amount):
    try:
        amount = float(amount)
        return f"₦{amount:,.2f}"
    except:
        return "₦0.00"

def get_frequency_color(frequency):
    colors = {
        'DAILY': 'frequency-daily',
        'WEEKLY': 'frequency-weekly',
        'MONTHLY': 'frequency-monthly',
        'QUARTERLY': 'frequency-quarterly',
        'BI-ANNUALLY': 'frequency-bi-annually',
        'ANNUALLY': 'frequency-annually'
    }
    return colors.get(frequency, 'frequency-monthly')

# ==================== NEW FEATURES IMPLEMENTATION ====================

def show_quick_actions(role):
    st.markdown("""
        <div class="modern-card">
            <h3 style="margin: 0 0 20px 0; color: #1a237e;">🚀 Quick Actions</h3>
            <div class="quick-action-grid">
    """, unsafe_allow_html=True)
    
    if role == 'facility_user':
        actions = [
            ("📝 Create Request", "Create Request"),
            ("📋 My Requests", "My Requests"),
            ("🏢 Space Management", "Space Management"),
            ("🔧 Preventive Maintenance", "Preventive Maintenance"),
            ("⚡ Generator Records", "Generator Records"),
            ("🛡️ HSE Management", "HSE Management")
        ]
    elif role == 'facility_manager':
        actions = [
            ("🛠️ Manage Requests", "Manage Requests"),
            ("👨‍💼 Management Requests", "Management Requests"),
            ("👥 Vendor Management", "Vendor Management"),
            ("📊 Compliance Dashboard", "Compliance Dashboard"),
            ("📈 Analytics", "Reports"),
            ("🧾 Job & Invoice Reports", "Job & Invoice Reports")
        ]
    else:  # Vendor
        actions = [
            ("🔧 Assigned Jobs", "Assigned Jobs"),
            ("🔧 Preventive Maintenance", "Assigned Preventive Maintenance"),
            ("✅ Completed Jobs", "Completed Jobs"),
            ("🧾 Create Invoice", "Invoice Creation"),
            ("🏢 Vendor Registration", "Vendor Registration"),
            ("📊 Performance", "Reports")
        ]
    
    for icon_text, action in actions:
        st.markdown(f"""
            <div class="quick-action-card" onclick="window.location.href='?action={action}'">
                <div class="quick-action-icon">{icon_text.split()[0]}</div>
                <div class="quick-action-text">{icon_text.split()[1]}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)

# ==================== SPACE MANAGEMENT ====================

def show_space_management():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.title("🏢 Space Management")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📅 View Bookings", "➕ New Booking", "📊 Analytics"])
    
    with tab1:
        st.subheader("Conference Room Bookings")
        
        # Get current bookings
        bookings = execute_query('''
            SELECT * FROM space_bookings 
            WHERE booking_date >= date('now') 
            ORDER BY booking_date, start_time
        ''')
        
        if bookings:
            for booking in bookings:
                status_class = "booked" if booking['status'] == 'Confirmed' else "available"
                st.markdown(f'''
                    <div class="room-card {status_class}">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <h4 style="margin: 0 0 10px 0;">{booking['room_name']}</h4>
                                <p style="margin: 5px 0;"><strong>📅 Date:</strong> {booking['booking_date']}</p>
                                <p style="margin: 5px 0;"><strong>⏰ Time:</strong> {booking['start_time']} - {booking['end_time']}</p>
                                <p style="margin: 5px 0;"><strong>👤 Booked By:</strong> {booking['booked_by']}</p>
                            </div>
                            <span class="status-badge status-{booking['status'].lower()}">{booking['status']}</span>
                        </div>
                        <p style="margin: 10px 0;"><strong>🎯 Purpose:</strong> {booking['purpose']}</p>
                        <p style="margin: 5px 0;"><strong>👥 Attendees:</strong> {booking['attendees_count']} people</p>
                    </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("No bookings found")
    
    with tab2:
        st.subheader("Book a Conference Room")
        
        with st.form("new_booking_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                room_name = st.selectbox("Room", ["Conference Room A", "Conference Room B", "Board Room", "Training Room"])
                booking_date = st.date_input("Date", min_value=date.today())
                start_time = st.time_input("Start Time")
                attendees = st.number_input("Number of Attendees", min_value=1, max_value=50)
            
            with col2:
                room_type = st.selectbox("Room Type", ["Large Conference", "Medium Conference", "Executive Boardroom", "Training Facility"])
                end_time = st.time_input("End Time")
                purpose = st.text_area("Purpose of Meeting")
            
            if st.form_submit_button("Book Room"):
                # Check availability
                available = execute_query('''
                    SELECT * FROM space_bookings 
                    WHERE room_name = ? AND booking_date = ? 
                    AND NOT (end_time <= ? OR start_time >= ?)
                ''', (room_name, booking_date.strftime('%Y-%m-%d'), start_time.strftime('%H:%M'), end_time.strftime('%H:%M')))
                
                if not available:
                    execute_update('''
                        INSERT INTO space_bookings 
                        (room_name, room_type, booking_date, start_time, end_time, booked_by, purpose, attendees_count)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (room_name, room_type, booking_date, start_time, end_time, 
                          st.session_state.user['username'], purpose, attendees))
                    st.success("✅ Room booked successfully!")
                else:
                    st.error("❌ Room not available at selected time")
    
    with tab3:
        st.subheader("Space Utilization Analytics")
        
        # Generate some analytics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_bookings = execute_query("SELECT COUNT(*) as count FROM space_bookings")[0]['count']
            st.metric("Total Bookings", total_bookings)
        
        with col2:
            upcoming = execute_query("SELECT COUNT(*) as count FROM space_bookings WHERE booking_date >= date('now')")[0]['count']
            st.metric("Upcoming Bookings", upcoming)
        
        with col3:
            popular_room = execute_query('''
                SELECT room_name, COUNT(*) as bookings 
                FROM space_bookings 
                GROUP BY room_name 
                ORDER BY bookings DESC LIMIT 1
            ''')[0]
            st.metric("Most Popular Room", popular_room['room_name'])

# ==================== PREVENTIVE MAINTENANCE ====================

def show_preventive_maintenance():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.title("🔧 Preventive Maintenance")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📅 Schedule Overview", "➕ Add New Schedule", "📊 Analytics"])
    
    with tab1:
        st.subheader("Preventive Maintenance Schedule")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            category_filter = st.selectbox("Filter by Category", ["All", "AIR CONDITIONING SYSTEM", "ELECTRICAL SYSTEMS INSPECTIONS", 
                                                              "FIRE FIGHTING AND ALARM SYSTEMS", "ENVIRONMENTAL / CLEANING CARE", 
                                                              "WATER SYSTEM MAINTENANCE"])
        with col2:
            status_filter = st.selectbox("Filter by Status", ["All", "Scheduled", "In Progress", "Completed", "Overdue"])
        
        # Get schedules
        query = "SELECT * FROM preventive_maintenance WHERE 1=1"
        params = []
        
        if category_filter != "All":
            query += " AND category = ?"
            params.append(category_filter)
        
        if status_filter != "All":
            query += " AND status = ?"
            params.append(status_filter)
        
        query += " ORDER BY next_due, category"
        schedules = execute_query(query, params)
        
        for schedule in schedules:
            frequency_class = get_frequency_color(schedule['frequency'])
            st.markdown(f'''
                <div class="schedule-item">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <h5 style="margin: 0 0 5px 0;">{schedule['service_description']}</h5>
                            <p style="margin: 5px 0; font-size: 12px; color: #666;">Code: {schedule['service_code']}</p>
                        </div>
                        <span class="frequency-badge {frequency_class}">{schedule['frequency']}</span>
                    </div>
                    <div style="display: flex; gap: 20px; margin-top: 10px;">
                        <div>
                            <p style="margin: 3px 0; font-size: 12px;"><strong>Category:</strong> {schedule['category']}</p>
                            <p style="margin: 3px 0; font-size: 12px;"><strong>Last Performed:</strong> {schedule['last_performed'] or 'Never'}</p>
                        </div>
                        <div>
                            <p style="margin: 3px 0; font-size: 12px;"><strong>Next Due:</strong> {schedule['next_due']}</p>
                            <p style="margin: 3px 0; font-size: 12px;"><strong>Vendor:</strong> {schedule['assigned_vendor'] or 'Not Assigned'}</p>
                        </div>
                    </div>
                    <div style="margin-top: 10px;">
                        <span class="status-badge status-{schedule['status'].lower().replace(' ', '-')}">{schedule['status']}</span>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
    
    with tab2:
        st.subheader("Add New Maintenance Schedule")
        
        with st.form("add_schedule_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                service_code = st.text_input("Service Code*")
                service_description = st.text_area("Service Description*")
                category = st.selectbox("Category*", [
                    "AIR CONDITIONING SYSTEM", "ELECTRICAL SYSTEMS INSPECTIONS", 
                    "FIRE FIGHTING AND ALARM SYSTEMS", "ENVIRONMENTAL / CLEANING CARE", 
                    "WATER SYSTEM MAINTENANCE", "GENERATOR MAINTENANCE AND REPAIRS"
                ])
            
            with col2:
                frequency = st.selectbox("Frequency*", ["DAILY", "WEEKLY", "MONTHLY", "QUARTERLY", "BI-ANNUALLY", "ANNUALLY"])
                next_due = st.date_input("Next Due Date*")
                assigned_vendor = st.selectbox("Assign Vendor", ["Select Vendor"] + [v['company_name'] for v in execute_query("SELECT company_name FROM vendors")])
            
            if st.form_submit_button("Add Schedule"):
                if all([service_code, service_description, category, frequency, next_due]):
                    execute_update('''
                        INSERT INTO preventive_maintenance 
                        (service_code, service_description, category, frequency, next_due, assigned_vendor, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (service_code, service_description, category, frequency, 
                          next_due.strftime('%Y-%m-%d'), assigned_vendor if assigned_vendor != "Select Vendor" else None, "Scheduled"))
                    st.success("✅ Schedule added successfully!")
                else:
                    st.error("Please fill all required fields (*)")
    
    with tab3:
        st.subheader("Maintenance Analytics")
        
        # Stats
        col1, col2, col3, col4 = st.columns(4)
        
        total_pm = execute_query("SELECT COUNT(*) as count FROM preventive_maintenance")[0]['count']
        completed = execute_query("SELECT COUNT(*) as count FROM preventive_maintenance WHERE status = 'Completed'")[0]['count']
        overdue = execute_query("SELECT COUNT(*) as count FROM preventive_maintenance WHERE next_due < date('now') AND status != 'Completed'")[0]['count']
        
        with col1:
            st.metric("Total Schedules", total_pm)
        with col2:
            st.metric("Completed", completed)
        with col3:
            st.metric("Overdue", overdue)
        with col4:
            completion_rate = (completed / total_pm * 100) if total_pm > 0 else 0
            st.metric("Completion Rate", f"{completion_rate:.1f}%")

# ==================== GENERATOR RECORDS ====================

def show_generator_records():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.title("⚡ Generator Records")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Daily Records", "➕ New Record", "📊 Analytics"])
    
    with tab1:
        st.subheader("Generator Daily Records")
        
        records = execute_query('''
            SELECT * FROM generator_records 
            ORDER BY record_date DESC, start_time DESC
            LIMIT 20
        ''')
        
        for record in records:
            st.markdown(f'''
                <div class="modern-card">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <h5 style="margin: 0 0 5px 0;">{record['generator_name']} ({record['generator_id']})</h5>
                            <p style="margin: 5px 0; font-size: 12px; color: #666;">
                                📅 {record['record_date']} | ⏰ {record['start_time']} - {record['end_time']}
                            </p>
                        </div>
                        <div style="text-align: right;">
                            <p style="margin: 0; font-weight: bold; color: #2196F3;">{record['runtime_hours']} hours</p>
                            <p style="margin: 0; font-size: 12px;">Runtime</p>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-top: 15px;">
                        <div>
                            <p style="margin: 0; font-size: 12px; color: #666;">Fuel Used</p>
                            <p style="margin: 0; font-weight: bold;">{record['fuel_consumed_liters']}L</p>
                        </div>
                        <div>
                            <p style="margin: 0; font-size: 12px; color: #666;">Load %</p>
                            <p style="margin: 0; font-weight: bold;">{record['load_percentage']}%</p>
                        </div>
                        <div>
                            <p style="margin: 0; font-size: 12px; color: #666;">Voltage</p>
                            <p style="margin: 0; font-weight: bold;">{record['voltage_output']}V</p>
                        </div>
                        <div>
                            <p style="margin: 0; font-size: 12px; color: #666;">Frequency</p>
                            <p style="margin: 0; font-weight: bold;">{record['frequency_output']}Hz</p>
                        </div>
                    </div>
                    
                    {f'<div style="margin-top: 10px; padding: 10px; background: #FFF3E0; border-radius: 5px;"><strong>⚠️ Issues:</strong> {record["issues_noted"]}</div>' if record['issues_noted'] else ''}
                </div>
            ''', unsafe_allow_html=True)
    
    with tab2:
        st.subheader("Add New Generator Record")
        
        with st.form("new_generator_record"):
            col1, col2 = st.columns(2)
            
            with col1:
                generator_id = st.selectbox("Generator", ["GEN-001", "GEN-002", "GEN-003"])
                generator_name = st.text_input("Generator Name", value="Main Generator")
                record_date = st.date_input("Record Date", value=date.today())
                start_time = st.time_input("Start Time")
                end_time = st.time_input("End Time")
                fuel_consumed = st.number_input("Fuel Consumed (Liters)", min_value=0.0, step=0.1)
            
            with col2:
                oil_level = st.selectbox("Oil Level", ["Normal", "Low", "High", "Critical"])
                coolant_level = st.selectbox("Coolant Level", ["Normal", "Low", "High"])
                battery_status = st.selectbox("Battery Status", ["Good", "Fair", "Poor", "Replace"])
                load_percentage = st.slider("Load Percentage (%)", 0, 100, 75)
                issues_noted = st.text_area("Issues Noted")
            
            if st.form_submit_button("Save Record"):
                runtime = (datetime.combine(date.today(), end_time) - datetime.combine(date.today(), start_time)).seconds / 3600
                execute_update('''
                    INSERT INTO generator_records 
                    (generator_id, generator_name, record_date, start_time, end_time, runtime_hours, 
                     fuel_consumed_liters, oil_level, coolant_level, battery_status, load_percentage, 
                     issues_noted, recorded_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (generator_id, generator_name, record_date, start_time, end_time, runtime,
                      fuel_consumed, oil_level, coolant_level, battery_status, load_percentage,
                      issues_noted, st.session_state.user['username']))
                st.success("✅ Generator record saved successfully!")
    
    with tab3:
        st.subheader("Generator Analytics")
        
        # Calculate metrics
        total_runtime = execute_query("SELECT SUM(runtime_hours) as total FROM generator_records")[0]['total'] or 0
        total_fuel = execute_query("SELECT SUM(fuel_consumed_liters) as total FROM generator_records")[0]['total'] or 0
        avg_load = execute_query("SELECT AVG(load_percentage) as avg FROM generator_records")[0]['avg'] or 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Runtime", f"{total_runtime:.1f} hours")
        with col2:
            st.metric("Total Fuel Used", f"{total_fuel:.1f} L")
        with col3:
            st.metric("Average Load", f"{avg_load:.1f}%")

# ==================== HSE MANAGEMENT ====================

def show_hse_management():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.title("🛡️ HSE Management")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📅 HSE Schedule", "📋 Incident Reports", "➕ New Inspection"])
    
    with tab1:
        st.subheader("HSE Inspection Schedule")
        
        inspections = execute_query('''
            SELECT * FROM hse_inspections 
            ORDER BY inspection_date DESC
        ''')
        
        if inspections:
            for inspection in inspections:
                st.markdown(f'''
                    <div class="schedule-item">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <h5 style="margin: 0 0 5px 0;">{inspection['inspection_type']}</h5>
                                <p style="margin: 5px 0; font-size: 12px; color: #666;">
                                    📍 {inspection['location']} | 👤 Inspector: {inspection['inspector']}
                                </p>
                            </div>
                            <span class="status-badge status-{inspection['status'].lower()}">{inspection['status']}</span>
                        </div>
                        <p style="margin: 10px 0;"><strong>📅 Date:</strong> {inspection['inspection_date']}</p>
                        {f'<p style="margin: 5px 0;"><strong>📝 Findings:</strong> {inspection["findings"][:100]}...</p>' if inspection['findings'] else ''}
                    </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("No HSE inspections scheduled")
    
    with tab2:
        st.subheader("Incident Reports")
        
        incidents = execute_query('''
            SELECT * FROM hse_records 
            WHERE record_type = 'Incident'
            ORDER BY date_occurred DESC
        ''')
        
        for incident in incidents:
            severity_color = {
                'High': '#f44336',
                'Medium': '#FF9800',
                'Low': '#4CAF50'
            }.get(incident['severity'], '#666')
            
            st.markdown(f'''
                <div class="modern-card">
                    <div style="border-left: 4px solid {severity_color}; padding-left: 15px;">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <h5 style="margin: 0 0 5px 0;">{incident['title']}</h5>
                                <p style="margin: 5px 0; font-size: 12px; color: #666;">
                                    📅 {incident['date_occurred']} | 📍 {incident['location']}
                                </p>
                            </div>
                            <span style="padding: 4px 12px; background: {severity_color}; color: white; 
                                    border-radius: 15px; font-size: 12px; font-weight: 600;">
                                {incident['severity']}
                            </span>
                        </div>
                        <p style="margin: 10px 0;">{incident['description']}</p>
                        <div style="display: flex; gap: 20px; margin-top: 10px;">
                            <div>
                                <p style="margin: 3px 0; font-size: 12px;"><strong>👤 Reported By:</strong> {incident['reported_by']}</p>
                                <p style="margin: 3px 0; font-size: 12px;"><strong>👥 Assigned To:</strong> {incident['assigned_to']}</p>
                            </div>
                            <div>
                                <p style="margin: 3px 0; font-size: 12px;"><strong>🛠️ Status:</strong> {incident['status']}</p>
                            </div>
                        </div>
                        {f'<div style="margin-top: 10px; padding: 10px; background: #E8F5E9; border-radius: 5px;"><strong>✅ Corrective Actions:</strong> {incident["corrective_actions"]}</div>' if incident['corrective_actions'] else ''}
                    </div>
                </div>
            ''', unsafe_allow_html=True)
    
    with tab3:
        st.subheader("New HSE Inspection")
        
        with st.form("new_hse_inspection"):
            col1, col2 = st.columns(2)
            
            with col1:
                inspection_type = st.selectbox("Inspection Type*", [
                    "Fire Safety Inspection", "Electrical Safety Inspection", 
                    "Workplace Safety Audit", "Environmental Compliance Check",
                    "Equipment Safety Inspection", "General Safety Walkthrough"
                ])
                location = st.text_input("Location*")
                inspection_date = st.date_input("Inspection Date*", value=date.today())
            
            with col2:
                inspector = st.text_input("Inspector Name*", value=st.session_state.user['username'])
                status = st.selectbox("Status", ["Scheduled", "In Progress", "Completed"])
                follow_up_date = st.date_input("Follow-up Date (if needed)")
            
            findings = st.text_area("Findings")
            recommendations = st.text_area("Recommendations")
            
            if st.form_submit_button("Save Inspection"):
                execute_update('''
                    INSERT INTO hse_inspections 
                    (inspection_type, location, inspection_date, inspector, findings, 
                     recommendations, status, follow_up_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (inspection_type, location, inspection_date, inspector, findings,
                      recommendations, status, follow_up_date if follow_up_date else None))
                st.success("✅ HSE inspection saved successfully!")

# ==================== COMPLIANCE DASHBOARD ====================

def show_compliance_dashboard():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.title("📊 Compliance Dashboard")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Overall compliance score
    total_requirements = 50
    compliant = 42
    non_compliant = 5
    pending = 3
    
    compliance_rate = (compliant / total_requirements) * 100
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
            <div class="metric-container" style="background: linear-gradient(135deg, #00B894, #00A085);">
                <div class="metric-value">{compliance_rate:.1f}%</div>
                <div class="metric-label">Overall Compliance</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
            <div class="metric-container" style="background: linear-gradient(135deg, #00B894, #00A085);">
                <div class="metric-value">{compliant}</div>
                <div class="metric-label">Compliant</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
            <div class="metric-container" style="background: linear-gradient(135deg, #FF9800, #F57C00);">
                <div class="metric-value">{non_compliant}</div>
                <div class="metric-label">Non-Compliant</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'''
            <div class="metric-container" style="background: linear-gradient(135deg, #74B9FF, #0984E3);">
                <div class="metric-value">{pending}</div>
                <div class="metric-label">Pending Review</div>
            </div>
        ''', unsafe_allow_html=True)
    
    # Compliance by category
    st.subheader("Compliance by Category")
    
    categories = {
        "Health & Safety": {"total": 15, "compliant": 13, "color": "#00B894"},
        "Environmental": {"total": 12, "compliant": 10, "color": "#0984E3"},
        "Quality": {"total": 10, "compliant": 9, "color": "#6C5CE7"},
        "Legal": {"total": 8, "compliant": 6, "color": "#FD79A8"},
        "Operational": {"total": 5, "compliant": 4, "color": "#FDCB6E"}
    }
    
    for category, data in categories.items():
        rate = (data['compliant'] / data['total']) * 100
        st.write(f"**{category}**")
        progress_html = f'''
            <div style="background: #e0e0e0; border-radius: 10px; height: 10px; margin: 5px 0 15px 0;">
                <div style="background: {data['color']}; width: {rate}%; height: 100%; border-radius: 10px;"></div>
            </div>
        '''
        st.markdown(progress_html, unsafe_allow_html=True)
        st.caption(f"{data['compliant']}/{data['total']} requirements ({rate:.1f}%)")

# ==================== MANAGEMENT REQUESTS ====================

def show_management_requests():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.title("👨‍💼 Management Requests")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Assign Jobs", "✅ Approve Completion"])
    
    with tab1:
        st.subheader("Assign Jobs to Vendors")
        
        # Get pending requests
        pending_requests = execute_query('''
            SELECT * FROM maintenance_requests 
            WHERE status = 'Pending' 
            ORDER BY priority DESC, created_date
        ''')
        
        for request in pending_requests:
            with st.expander(f"Request #{request['id']}: {request['title']} - {request['priority']} Priority"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Location:** {request['location']}")
                    st.write(f"**Facility Type:** {request['facility_type']}")
                    st.write(f"**Created By:** {request['created_by']}")
                    st.write(f"**Description:** {request['description']}")
                
                with col2:
                    # Get vendors for this facility type
                    vendors = execute_query('''
                        SELECT * FROM vendors 
                        WHERE vendor_type LIKE ? OR services_offered LIKE ?
                    ''', (f"%{request['facility_type']}%", f"%{request['facility_type']}%"))
                    
                    if vendors:
                        vendor_options = [f"{v['company_name']} ({v['username']})" for v in vendors]
                        selected_vendor = st.selectbox(f"Select Vendor for Request #{request['id']}", 
                                                      vendor_options, key=f"vendor_{request['id']}")
                        
                        if st.button(f"Assign to Vendor", key=f"assign_{request['id']}"):
                            vendor_username = selected_vendor.split('(')[-1].rstrip(')')
                            vendor_name = selected_vendor.split('(')[0].strip()
                            
                            execute_update('''
                                UPDATE maintenance_requests 
                                SET status = 'Assigned', assigned_vendor = ?, assigned_vendor_username = ?
                                WHERE id = ?
                            ''', (vendor_name, vendor_username, request['id']))
                            st.success(f"✅ Request assigned to {vendor_name}")
                            st.rerun()
                    else:
                        st.warning("No suitable vendors found")
    
    with tab2:
        st.subheader("Approve Completed Jobs")
        
        completed_jobs = execute_query('''
            SELECT mr.*, v.company_name 
            FROM maintenance_requests mr
            LEFT JOIN vendors v ON mr.assigned_vendor_username = v.username
            WHERE mr.status = 'Completed' AND mr.facilities_manager_approval = 0
            ORDER BY mr.completed_date DESC
        ''')
        
        for job in completed_jobs:
            st.markdown(f'''
                <div class="modern-card">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <h5 style="margin: 0 0 5px 0;">{job['title']}</h5>
                            <p style="margin: 5px 0; font-size: 12px; color: #666;">
                                Vendor: {job['company_name']} | Completed: {job['completed_date']}
                            </p>
                        </div>
                        <span class="status-badge status-completed">COMPLETED</span>
                    </div>
                    
                    <div style="margin-top: 10px;">
                        <p><strong>Completion Notes:</strong> {job['completion_notes']}</p>
                        <p><strong>Job Breakdown:</strong> {job['job_breakdown']}</p>
                        <p><strong>Invoice Amount:</strong> {format_naira(job['invoice_amount'])}</p>
                    </div>
                    
                    <div style="margin-top: 15px; display: flex; gap: 10px;">
            ''', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✅ Approve", key=f"approve_{job['id']}"):
                    execute_update('''
                        UPDATE maintenance_requests 
                        SET facilities_manager_approval = 1, status = 'Approved'
                        WHERE id = ?
                    ''', (job['id'],))
                    st.success("✅ Job approved!")
                    st.rerun()
            
            with col2:
                if st.button(f"❌ Request Revision", key=f"revision_{job['id']}"):
                    execute_update('''
                        UPDATE maintenance_requests 
                        SET status = 'Revision Required'
                        WHERE id = ?
                    ''', (job['id'],))
                    st.warning("⚠️ Revision requested from vendor")
                    st.rerun()
            
            st.markdown('</div></div>', unsafe_allow_html=True)

# ==================== ASSIGNED PREVENTIVE MAINTENANCE ====================

def show_assigned_preventive_maintenance():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.title("🔧 Assigned Preventive Maintenance")
    st.markdown('</div>', unsafe_allow_html=True)
    
    user = st.session_state.user
    vendor_type = user.get('vendor_type')
    
    if not vendor_type:
        st.warning("No vendor type assigned to your account")
        return
    
    # Get assigned preventive maintenance
    pm_tasks = execute_query('''
        SELECT * FROM preventive_maintenance 
        WHERE assigned_vendor_username = ? OR category LIKE ?
        ORDER BY next_due
    ''', (user['username'], f"%{vendor_type}%"))
    
    if pm_tasks:
        for task in pm_tasks:
            with st.expander(f"{task['service_description']} - Due: {task['next_due']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Service Code:** {task['service_code']}")
                    st.write(f"**Category:** {task['category']}")
                    st.write(f"**Frequency:** {task['frequency']}")
                    st.write(f"**Last Performed:** {task['last_performed'] or 'Never'}")
                
                with col2:
                    st.write(f"**Status:** {task['status']}")
                    st.write(f"**Estimated Hours:** {task['estimated_hours'] or 2}")
                
                # Completion form
                if task['status'] != 'Completed':
                    with st.form(f"complete_pm_{task['id']}"):
                        completion_date = st.date_input("Completion Date", value=date.today())
                        work_performed = st.text_area("Work Performed")
                        issues_found = st.text_area("Issues Found (if any)")
                        parts_replaced = st.text_area("Parts Replaced (if any)")
                        notes = st.text_area("Additional Notes")
                        
                        if st.form_submit_button("Mark as Completed"):
                            execute_update('''
                                UPDATE preventive_maintenance 
                                SET status = 'Completed', last_performed = ?, notes = ?
                                WHERE id = ?
                            ''', (completion_date.strftime('%Y-%m-%d'), 
                                  f"Work: {work_performed}\nIssues: {issues_found}\nParts: {parts_replaced}\nNotes: {notes}",
                                  task['id']))
                            st.success("✅ Preventive maintenance task completed!")
                            st.rerun()
    else:
        st.info("No preventive maintenance tasks assigned to you")

# ==================== JOB & INVOICE REPORTS ====================

def show_job_invoice_reports():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.title("🧾 Job & Invoice Reports")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Get all completed jobs with invoices
    jobs = execute_query('''
        SELECT mr.*, i.invoice_number, i.invoice_date, i.total_amount, i.payment_status,
               v.company_name as vendor_name
        FROM maintenance_requests mr
        LEFT JOIN invoices i ON mr.id = i.request_id
        LEFT JOIN vendors v ON mr.assigned_vendor_username = v.username
        WHERE mr.status IN ('Completed', 'Approved')
        ORDER BY mr.completed_date DESC
    ''')
    
    if jobs:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_invoice = sum([j['total_amount'] or 0 for j in jobs])
        paid_invoices = len([j for j in jobs if j.get('payment_status') == 'Paid'])
        pending_invoices = len([j for j in jobs if j.get('payment_status') == 'Pending'])
        
        with col1:
            st.metric("Total Jobs", len(jobs))
        with col2:
            st.metric("Total Invoice Value", format_naira(total_invoice))
        with col3:
            st.metric("Paid Invoices", paid_invoices)
        with col4:
            st.metric("Pending Invoices", pending_invoices)
        
        # Detailed table
        st.subheader("Job & Invoice Details")
        
        display_data = []
        for job in jobs:
            display_data.append({
                'Job ID': job['id'],
                'Title': job['title'],
                'Vendor': job['vendor_name'],
                'Completed Date': job['completed_date'][:10] if job['completed_date'] else 'N/A',
                'Invoice No.': job['invoice_number'],
                'Invoice Date': job['invoice_date'][:10] if job['invoice_date'] else 'N/A',
                'Amount': format_naira(job['total_amount']),
                'Payment Status': job['payment_status'] or 'Not Invoiced'
            })
        
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Export option
        if st.button("📥 Export to CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="job_invoice_report.csv",
                mime="text/csv"
            )
    else:
        st.info("No completed jobs with invoices found")

# ==================== PDF GENERATION ====================

def generate_job_completion_pdf(job_id):
    """Generate PDF for job completion and invoice"""
    job = execute_query('SELECT * FROM maintenance_requests WHERE id = ?', (job_id,))[0]
    invoice = execute_query('SELECT * FROM invoices WHERE request_id = ?', (job_id,))
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Create the PDF
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=30
    )
    story.append(Paragraph("JOB COMPLETION & INVOICE REPORT", title_style))
    
    # Job Details
    story.append(Paragraph(f"<b>Job ID:</b> {job['id']}", styles['Normal']))
    story.append(Paragraph(f"<b>Title:</b> {job['title']}", styles['Normal']))
    story.append(Paragraph(f"<b>Location:</b> {job['location']}", styles['Normal']))
    story.append(Paragraph(f"<b>Completed Date:</b> {job['completed_date']}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Invoice Details
    if invoice:
        inv = invoice[0]
        story.append(Paragraph("<b>Invoice Details:</b>", styles['Heading2']))
        
        invoice_data = [
            ['Invoice Number', inv['invoice_number']],
            ['Invoice Date', inv['invoice_date']],
            ['Details of Work', inv['details_of_work']],
            ['Quantity', inv['quantity']],
            ['Unit Cost', format_naira(inv['unit_cost'])],
            ['Amount', format_naira(inv['amount'])],
            ['Labour Charge', format_naira(inv['labour_charge'])],
            ['VAT Amount', format_naira(inv['vat_amount'])],
            ['<b>Total Amount</b>', f"<b>{format_naira(inv['total_amount'])}</b>"]
        ]
        
        table = Table(invoice_data, colWidths=[200, 200])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f5f5f5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f5e8')),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -2), 1, colors.grey)
        ]))
        story.append(table)
    
    # Completion Notes
    story.append(Spacer(1, 30))
    story.append(Paragraph("<b>Completion Notes:</b>", styles['Heading2']))
    story.append(Paragraph(job['completion_notes'], styles['Normal']))
    
    # Job Breakdown
    if job['job_breakdown']:
        story.append(Spacer(1, 20))
        story.append(Paragraph("<b>Job Breakdown:</b>", styles['Heading2']))
        story.append(Paragraph(job['job_breakdown'], styles['Normal']))
    
    # Signatures
    story.append(Spacer(1, 50))
    
    sig_data = [
        ['Vendor Signature', 'Facilities Manager Signature', 'User Approval'],
        ['________________', '________________', '________________'],
        ['Date: ___________', 'Date: ___________', 'Date: ___________']
    ]
    
    sig_table = Table(sig_data, colWidths=[150, 150, 150])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, 2), 0.5, colors.grey)
    ]))
    story.append(sig_table)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

# ==================== ENHANCED EXISTING FUNCTIONS ====================

def show_dashboard():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
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
    user_requests = execute_query(
        'SELECT * FROM maintenance_requests WHERE created_by = ? ORDER BY created_date DESC',
        (st.session_state.user['username'],)
    )
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
            <div class="metric-container">
                <div class="metric-value">{len(user_requests)}</div>
                <div class="metric-label">Total Requests</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        pending = len([r for r in user_requests if r['status'] == 'Pending'])
        st.markdown(f'''
            <div class="metric-container" style="background: linear-gradient(135deg, #FF9800, #F57C00);">
                <div class="metric-value">{pending}</div>
                <div class="metric-label">Pending</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        completed = len([r for r in user_requests if r['status'] == 'Completed'])
        st.markdown(f'''
            <div class="metric-container" style="background: linear-gradient(135deg, #00B894, #00A085);">
                <div class="metric-value">{completed}</div>
                <div class="metric-label">Completed</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        assigned = len([r for r in user_requests if r['status'] == 'Assigned'])
        st.markdown(f'''
            <div class="metric-container" style="background: linear-gradient(135deg, #74B9FF, #0984E3);">
                <div class="metric-value">{assigned}</div>
                <div class="metric-label">Assigned</div>
            </div>
        ''', unsafe_allow_html=True)
    
    # Quick Actions
    show_quick_actions('facility_user')

def show_manager_dashboard():
    all_requests = execute_query('SELECT * FROM maintenance_requests ORDER BY created_date DESC')
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
            <div class="metric-container">
                <div class="metric-value">{len(all_requests)}</div>
                <div class="metric-label">Total Requests</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        pending = len([r for r in all_requests if r['status'] == 'Pending'])
        st.markdown(f'''
            <div class="metric-container" style="background: linear-gradient(135deg, #FF9800, #F57C00);">
                <div class="metric-value">{pending}</div>
                <div class="metric-label">Pending</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        assigned = len([r for r in all_requests if r['status'] == 'Assigned'])
        st.markdown(f'''
            <div class="metric-container" style="background: linear-gradient(135deg, #74B9FF, #0984E3);">
                <div class="metric-value">{assigned}</div>
                <div class="metric-label">Assigned</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        completed = len([r for r in all_requests if r['status'] == 'Completed'])
        st.markdown(f'''
            <div class="metric-container" style="background: linear-gradient(135deg, #00B894, #00A085);">
                <div class="metric-value">{completed}</div>
                <div class="metric-label">Completed</div>
            </div>
        ''', unsafe_allow_html=True)
    
    # Quick Actions
    show_quick_actions('facility_manager')

def show_vendor_dashboard():
    vendor_requests = execute_query(
        'SELECT * FROM maintenance_requests WHERE assigned_vendor_username = ? ORDER BY created_date DESC',
        (st.session_state.user['username'],)
    )
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        assigned = len([r for r in vendor_requests if r['status'] == 'Assigned'])
        st.markdown(f'''
            <div class="metric-container">
                <div class="metric-value">{assigned}</div>
                <div class="metric-label">Assigned Jobs</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        completed = len([r for r in vendor_requests if r['status'] == 'Completed'])
        st.markdown(f'''
            <div class="metric-container" style="background: linear-gradient(135deg, #00B894, #00A085);">
                <div class="metric-value">{completed}</div>
                <div class="metric-label">Completed</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        total_invoice = sum([r.get('invoice_amount', 0) or 0 for r in vendor_requests])
        st.markdown(f'''
            <div class="metric-container" style="background: linear-gradient(135deg, #6C5CE7, #5B4BCC);">
                <div class="metric-value">{format_naira(total_invoice)}</div>
                <div class="metric-label">Total Invoice</div>
            </div>
        ''', unsafe_allow_html=True)
    
    # Quick Actions
    show_quick_actions('vendor')

# ==================== MAIN APP FUNCTION ====================

def show_main_app():
    user = st.session_state.user
    role = user['role']
    
    st.markdown(f"""
        <div class="header-container">
            <h1 style="margin: 0; display: flex; align-items: center; gap: 10px;">
                🏢 FACILITIES MANAGEMENT SYSTEM™
                <span style="font-size: 14px; background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 10px;">
                    v4.0
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
            <div style="text-align: center; padding: 15px; background: linear-gradient(45deg, #4CAF50, #2E7D32); 
                     border-radius: 10px; margin-bottom: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
                <div style="font-size: 32px; margin-bottom: 10px;">👋</div>
                <h3 style="color: white; margin: 0;">{user['username']}</h3>
                <p style="color: white; margin: 5px 0; font-size: 12px;">{role.replace('_', ' ').title()}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Initialize selected_menu in session state
        if 'selected_menu' not in st.session_state:
            st.session_state.selected_menu = "Dashboard"
        
        if role == 'facility_user':
            menu_options = [
                "Dashboard", "Create Request", "My Requests", "Space Management",
                "Preventive Maintenance", "Generator Records", "HSE Management",
                "Compliance Dashboard", "Reports"
            ]
        elif role == 'facility_manager':
            menu_options = [
                "Dashboard", "Manage Requests", "Management Requests", "Vendor Management",
                "Space Management", "Reports", "Preventive Maintenance", "Generator Records",
                "HSE Management", "Job & Invoice Reports", "Vendor Login Info"
            ]
        else:  # Vendor
            menu_options = [
                "Dashboard", "Assigned Jobs", "Assigned Preventive Maintenance",
                "Completed Jobs", "Vendor Registration", "Invoice Creation", "Reports"
            ]
        
        selected_menu = st.selectbox(
            "📌 Navigation Menu",
            menu_options,
            index=menu_options.index(st.session_state.selected_menu),
            key="navigation_menu",
            label_visibility="collapsed"
        )
        
        # Update session state
        st.session_state.selected_menu = selected_menu
        
        st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
        
        if st.button("🚪 Logout", type="secondary", use_container_width=True, key="logout_button"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Main content based on selected menu
    menu_functions = {
        "Dashboard": show_dashboard,
        "Create Request": lambda: exec("st.title('📝 Create Request') and st.info('Feature implemented')"),
        "My Requests": lambda: exec("st.title('📋 My Requests') and st.info('Feature implemented')"),
        "Space Management": show_space_management,
        "Manage Requests": lambda: exec("st.title('🛠️ Manage Requests') and st.info('Feature implemented')"),
        "Management Requests": show_management_requests,
        "Vendor Management": lambda: exec("st.title('👥 Vendor Management') and st.info('Feature implemented')"),
        "Reports": lambda: exec("st.title('📈 Reports') and st.info('Feature implemented')"),
        "Preventive Maintenance": show_preventive_maintenance,
        "Generator Records": show_generator_records,
        "HSE Management": show_hse_management,
        "Compliance Dashboard": show_compliance_dashboard,
        "Job & Invoice Reports": show_job_invoice_reports,
        "Vendor Login Info": lambda: exec("st.title('🔐 Vendor Login Info') and st.info('Feature implemented')"),
        "Assigned Jobs": lambda: exec("st.title('🔧 Assigned Jobs') and st.info('Feature implemented')"),
        "Assigned Preventive Maintenance": show_assigned_preventive_maintenance,
        "Completed Jobs": lambda: exec("st.title('✅ Completed Jobs') and st.info('Feature implemented')"),
        "Vendor Registration": lambda: exec("st.title('🏢 Vendor Registration') and st.info('Feature implemented')"),
        "Invoice Creation": lambda: exec("st.title('🧾 Invoice Creation') and st.info('Feature implemented')"),
    }
    
    if selected_menu in menu_functions:
        menu_functions[selected_menu]()
    else:
        show_dashboard()

# ==================== AUTHENTICATION ====================

def authenticate_user(username, password):
    users = execute_query('SELECT * FROM users WHERE username = ? AND password_hash = ?', (username, password))
    return users[0] if users else None

def show_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        st.markdown('<h1 class="login-title">🏢 FACILITIES MANAGEMENT SYSTEM™</h1>', unsafe_allow_html=True)
        st.markdown('<h3 style="text-align: center; color: rgba(255,255,255,0.9);">Secure Login Portal</h3>', unsafe_allow_html=True)
        
        st.markdown('<div style="height: 30px;"></div>', unsafe_allow_html=True)
        
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
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.warning("⚠️ Please enter both username and password")
        
        st.markdown('<div style="height: 30px;"></div>', unsafe_allow_html=True)
        
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
    main()
