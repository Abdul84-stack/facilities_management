import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import time
import threading
import os

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
    </style>
""", unsafe_allow_html=True)

# Database setup with enhanced schema
def init_database():
    try:
        # Remove old database to avoid column conflicts
        if os.path.exists('facilities_management.db'):
            os.remove('facilities_management.db')
        
        conn = sqlite3.connect('facilities_management.db', check_same_thread=False)
        cursor = conn.cursor()
        
        # Users table - simplified version
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
        
        # Insert sample users
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
                cursor.execute('''
                    INSERT OR IGNORE INTO users (username, password_hash, role, vendor_type) 
                    VALUES (?, ?, ?, ?)
                ''', (username, password, role, vendor_type))
            except Exception as e:
                print(f"Error inserting user {username}: {e}")
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
            except Exception as e:
                print(f"Error inserting vendor: {e}")
                continue
        
        # Insert sample conference rooms
        conference_rooms = [
            ('Conference Room A', 'Large Conference', 30, 3, 'Main Building', 
             'Projector, Whiteboard, Video Conferencing, WiFi', 5000.00, 'Available', None),
            ('Conference Room B', 'Medium Conference', 15, 3, 'Main Building', 
             'TV Screen, Whiteboard, WiFi', 3000.00, 'Available', None),
            ('Board Room', 'Executive Boardroom', 12, 5, 'Executive Wing', 
             'Smart TV, Video Conferencing, Coffee Machine, WiFi', 8000.00, 'Available', None)
        ]
        
        for room_data in conference_rooms:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO conference_rooms 
                    (room_name, room_type, capacity, floor, building, amenities, hourly_rate, status, image_url) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', room_data)
            except Exception as e:
                print(f"Error inserting conference room: {e}")
                continue
        
        # Insert sample preventive maintenance
        pm_schedules = [
            ('PPM/AC/001', 'Routine Inspection of all AC units in the main block and common areas.', 
             'AIR CONDITIONING SYSTEM', 'MONTHLY', None, '2024-12-01', 'Provas Limited', 'provas_vendor', 'Scheduled', 4, 'HVAC Certified', 'Safety Gloves, Goggles', 'Check all units'),
            ('PPM/AC/002', 'Routine Servicing of all split units in the common areas', 
             'AIR CONDITIONING SYSTEM', 'QUARTERLY', '2024-09-01', '2024-12-01', 'Provas Limited', 'provas_vendor', 'Scheduled', 8, 'HVAC Technician', 'All safety gear', 'Full service'),
            ('PPM/ELECT/001', 'Inspection of bulbs and lighting systems in offices and common areas', 
             'ELECTRICAL SYSTEMS INSPECTIONS', 'DAILY', '2024-11-25', '2024-11-26', 'Power Solutions Ltd', 'power_vendor', 'Completed', 2, 'Electrician', 'Insulated tools', 'Daily check'),
        ]
        
        for pm_data in pm_schedules:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO preventive_maintenance 
                    (service_code, service_description, category, frequency, last_performed, next_due, 
                     assigned_vendor, assigned_vendor_username, status, estimated_hours, required_skills, safety_requirements, notes) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', pm_data)
            except Exception as e:
                print(f"Error inserting PM schedule: {e}")
                continue
        
        # Insert sample space bookings
        sample_bookings = [
            ('Conference Room A', 'Large Conference', '2024-12-28', '09:00', '11:00', 
             'John Doe', 'Quarterly Business Review', 15, 'Confirmed', 'facility_manager'),
            ('Board Room', 'Executive Boardroom', '2024-12-28', '14:00', '16:00', 
             'Jane Smith', 'Executive Meeting', 8, 'Confirmed', 'facility_manager'),
        ]
        
        for booking_data in sample_bookings:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO space_bookings 
                    (room_name, room_type, booking_date, start_time, end_time, booked_by, purpose, attendees_count, status, approved_by) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', booking_data)
            except Exception as e:
                print(f"Error inserting booking: {e}")
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
            except Exception as e:
                print(f"Error inserting generator record: {e}")
                continue
        
        # Insert sample HSE records
        hse_records = [
            ('Inspection', 'Fire Safety Inspection', 'Monthly fire safety equipment check', 
             'Main Building', '2024-11-25', 'Low', 'facility_manager', 'Safety Officer', 
             'Closed', 'All fire extinguishers checked and tagged', 'Quarterly inspection schedule', 'All equipment functional', '2024-11-25'),
            ('Incident', 'Slip and Fall Incident', 'Employee slipped in wet corridor', 
             'Ground Floor Corridor', '2024-11-24', 'Medium', 'facility_user', 'HSE Manager', 
             'Open', 'Wet floor signs placed, floor dried', 'Implement non-slip mats', 'Investigation ongoing', None),
        ]
        
        for hse_data in hse_records:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO hse_records 
                    (record_type, title, description, location, date_occurred, severity, reported_by, assigned_to, 
                     status, corrective_actions, preventive_measures, investigation_report, closed_date) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', hse_data)
            except Exception as e:
                print(f"Error inserting HSE record: {e}")
                continue
        
        # Insert sample maintenance requests
        maintenance_requests = [
            ('AC Not Cooling', 'AC in office 301 not cooling properly', 'Office 301', 'HVAC (Cooling Systems)', 'High', 'Pending', 'facility_user', None, None, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), None, None, None, 0, None, 0, 0, 0),
            ('Generator Maintenance', 'Generator needs routine maintenance', 'Generator Room', 'Generator Maintenance', 'Medium', 'Assigned', 'facility_user', 'Generator Limited', 'generator_vendor', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), None, None, None, 0, None, 0, 0, 0),
            ('Electrical Fault', 'Lights flickering in hallway', 'Main Hallway', 'ELECTRICAL SYSTEMS INSPECTIONS', 'Low', 'Completed', 'facility_user', 'Power Solutions Ltd', 'power_vendor', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), '2024-11-25', 'Replaced faulty ballast', 'Replaced 2 ballasts, tested all lights', 25000.00, 'INV-001', 1, 1, 1),
        ]
        
        for request_data in maintenance_requests:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO maintenance_requests 
                    (title, description, location, facility_type, priority, status, created_by, assigned_vendor, assigned_vendor_username, created_date, completed_date, completion_notes, job_breakdown, invoice_amount, invoice_number, requesting_dept_approval, facilities_manager_approval, user_approval) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', request_data)
            except Exception as e:
                print(f"Error inserting maintenance request: {e}")
                continue
        
        conn.commit()
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
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
        print(f"Query error: {e}")
        return []

def execute_update(query, params=()):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        return True
    except Exception as e:
        print(f"Database update error: {e}")
        return False

# Helper functions
def safe_get(data, key, default=None):
    if not data or not isinstance(data, dict):
        return default
    return data.get(key, default)

def format_naira(amount):
    try:
        if amount is None:
            return "₦0.00"
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
        
        # Display sample credentials
        st.markdown('<div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px;">', unsafe_allow_html=True)
        st.markdown('<h4 style="color: white;">📋 Sample Credentials</h4>', unsafe_allow_html=True)
        
        credentials = """
        👥 Facility User: facility_user / 0123456
        👨‍💼 Facility Manager: facility_manager / 0123456
        🏢 Vendors:
        • Provas Limited: provas_vendor / 123456
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

# ==================== QUICK ACTIONS ====================

def show_quick_actions(role):
    st.markdown("""
        <div class="modern-card">
            <h3 style="margin: 0 0 20px 0; color: #1a237e;">🚀 Quick Actions</h3>
    """, unsafe_allow_html=True)
    
    if role == 'facility_user':
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📝 Create Request", use_container_width=True):
                st.session_state.selected_menu = "Create Request"
                st.rerun()
        with col2:
            if st.button("📋 My Requests", use_container_width=True):
                st.session_state.selected_menu = "My Requests"
                st.rerun()
        with col3:
            if st.button("🏢 Space Management", use_container_width=True):
                st.session_state.selected_menu = "Space Management"
                st.rerun()
    elif role == 'facility_manager':
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🛠️ Manage Requests", use_container_width=True):
                st.session_state.selected_menu = "Manage Requests"
                st.rerun()
        with col2:
            if st.button("👨‍💼 Management", use_container_width=True):
                st.session_state.selected_menu = "Management Requests"
                st.rerun()
        with col3:
            if st.button("👥 Vendors", use_container_width=True):
                st.session_state.selected_menu = "Vendor Management"
                st.rerun()
    else:  # Vendor
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔧 Assigned Jobs", use_container_width=True):
                st.session_state.selected_menu = "Assigned Jobs"
                st.rerun()
        with col2:
            if st.button("✅ Completed Jobs", use_container_width=True):
                st.session_state.selected_menu = "Completed Jobs"
                st.rerun()
        with col3:
            if st.button("🧾 Create Invoice", use_container_width=True):
                st.session_state.selected_menu = "Invoice Creation"
                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# ==================== DASHBOARDS ====================

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
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Requests", len(user_requests))
    with col2:
        pending = len([r for r in user_requests if r['status'] == 'Pending'])
        st.metric("Pending", pending)
    with col3:
        completed = len([r for r in user_requests if r['status'] == 'Completed'])
        st.metric("Completed", completed)
    with col4:
        assigned = len([r for r in user_requests if r['status'] == 'Assigned'])
        st.metric("Assigned", assigned)
    
    show_quick_actions('facility_user')

def show_manager_dashboard():
    all_requests = execute_query('SELECT * FROM maintenance_requests ORDER BY created_date DESC')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Requests", len(all_requests))
    with col2:
        pending = len([r for r in all_requests if r['status'] == 'Pending'])
        st.metric("Pending", pending)
    with col3:
        assigned = len([r for r in all_requests if r['status'] == 'Assigned'])
        st.metric("Assigned", assigned)
    with col4:
        completed = len([r for r in all_requests if r['status'] == 'Completed'])
        st.metric("Completed", completed)
    
    show_quick_actions('facility_manager')

def show_vendor_dashboard():
    vendor_requests = execute_query(
        'SELECT * FROM maintenance_requests WHERE assigned_vendor_username = ? ORDER BY created_date DESC',
        (st.session_state.user['username'],)
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        assigned = len([r for r in vendor_requests if r['status'] == 'Assigned'])
        st.metric("Assigned Jobs", assigned)
    with col2:
        completed = len([r for r in vendor_requests if r['status'] == 'Completed'])
        st.metric("Completed", completed)
    with col3:
        total_invoice = sum([r.get('invoice_amount', 0) or 0 for r in vendor_requests])
        st.metric("Total Invoice", format_naira(total_invoice))
    
    show_quick_actions('vendor')

# ==================== CORE FEATURES ====================

def show_create_request():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.title("📝 Create Maintenance Request")
    st.markdown('</div>', unsafe_allow_html=True)
    
    with st.form("create_request_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("📌 Request Title", placeholder="Enter request title")
            location = st.selectbox(
                "📍 Location",
                ["Office 301", "Main Hallway", "Generator Room", "Common Area", "Water Treatment Plant", "Admin Building"]
            )
            facility_type = st.selectbox(
                "🏢 Facility Type",
                ["HVAC (Cooling Systems)", "Generator Maintenance", "ELECTRICAL SYSTEMS INSPECTIONS", 
                 "FIRE FIGHTING AND ALARM SYSTEMS", "ENVIRONMENTAL / CLEANING CARE", "WATER SYSTEM MAINTENANCE"]
            )
        
        with col2:
            priority = st.selectbox("🚨 Priority", ["Low", "Medium", "High", "Critical"])
        
        description = st.text_area("📄 Description", height=100, 
                                 placeholder="Please provide detailed description of the maintenance request...")
        
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

def show_my_requests():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.title("📋 My Maintenance Requests")
    st.markdown('</div>', unsafe_allow_html=True)
    
    user_requests = execute_query(
        'SELECT * FROM maintenance_requests WHERE created_by = ? ORDER BY created_date DESC',
        (st.session_state.user['username'],)
    )
    
    if user_requests:
        for request in user_requests:
            status_color = {
                'Pending': '#FF9800',
                'Assigned': '#2196F3',
                'Completed': '#4CAF50',
                'Approved': '#00B894'
            }.get(request['status'], '#666')
            
            card_html = f'''
            <div class="modern-card">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <h4 style="margin: 0 0 5px 0;">{request['title']}</h4>
                        <p style="margin: 5px 0; font-size: 12px; color: #666;">
                            📍 {request['location']} | 🏢 {request['facility_type']}
                        </p>
                    </div>
                    <span style="padding: 4px 12px; background: {status_color}; color: white; 
                            border-radius: 15px; font-size: 12px; font-weight: 600;">
                        {request['status']}
                    </span>
                </div>
                <p style="margin: 10px 0;">{request['description']}</p>
                <div style="display: flex; gap: 20px; margin-top: 10px;">
                    <div>
                        <p style="margin: 3px 0; font-size: 12px;"><strong>🚨 Priority:</strong> {request['priority']}</p>
                        <p style="margin: 3px 0; font-size: 12px;"><strong>📅 Created:</strong> {request['created_date'][:10]}</p>
                    </div>
                    <div>
                        <p style="margin: 3px 0; font-size: 12px;"><strong>👥 Vendor:</strong> {request['assigned_vendor'] or 'Not Assigned'}</p>
                    </div>
                </div>
            </div>
            '''
            st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.info("📭 No maintenance requests found")

def show_manage_requests():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.title("🛠️ Manage Maintenance Requests")
    st.markdown('</div>', unsafe_allow_html=True)
    
    all_requests = execute_query('SELECT * FROM maintenance_requests ORDER BY created_date DESC')
    
    if all_requests:
        for request in all_requests:
            with st.expander(f"Request #{request['id']}: {request['title']} - {request['status']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Title:** {request['title']}")
                    st.write(f"**Description:** {request['description']}")
                    st.write(f"**Location:** {request['location']}")
                    st.write(f"**Priority:** {request['priority']}")
                    st.write(f"**Status:** {request['status']}")
                    st.write(f"**Created By:** {request['created_by']}")
                
                with col2:
                    if request['status'] == 'Pending':
                        vendors = execute_query('SELECT * FROM vendors')
                        if vendors:
                            vendor_options = [f"{v['company_name']} ({v['username']})" for v in vendors]
                            selected_vendor = st.selectbox(f"Select Vendor for Request #{request['id']}", 
                                                          vendor_options, key=f"vendor_{request['id']}")
                            
                            if st.button(f"Assign to Vendor", key=f"assign_{request['id']}"):
                                vendor_username = selected_vendor.split('(')[-1].rstrip(')')
                                vendor_name = selected_vendor.split('(')[0].strip()
                                
                                execute_update(
                                    'UPDATE maintenance_requests SET status = ?, assigned_vendor = ?, assigned_vendor_username = ? WHERE id = ?',
                                    ('Assigned', vendor_name, vendor_username, request['id'])
                                )
                                st.success(f"✅ Request assigned to {vendor_name}")
                                st.rerun()
    else:
        st.info("📭 No maintenance requests found")

# ==================== NEW FEATURES ====================

def show_space_management():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.title("🏢 Space Management")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📅 View Bookings", "➕ New Booking", "📊 Analytics"])
    
    with tab1:
        st.subheader("Conference Room Bookings")
        
        bookings = execute_query('SELECT * FROM space_bookings ORDER BY booking_date, start_time')
        
        if bookings:
            for booking in bookings:
                status_class = "booked" if booking['status'] == 'Confirmed' else "available"
                card_html = f'''
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
                '''
                st.markdown(card_html, unsafe_allow_html=True)
        else:
            st.info("No bookings found")
    
    with tab2:
        st.subheader("Book a Conference Room")
        
        with st.form("new_booking_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                room_name = st.selectbox("Room", ["Conference Room A", "Conference Room B", "Board Room"])
                booking_date = st.date_input("Date", min_value=date.today())
                start_time = st.time_input("Start Time")
                attendees = st.number_input("Number of Attendees", min_value=1, max_value=50)
            
            with col2:
                purpose = st.text_area("Purpose of Meeting")
            
            if st.form_submit_button("Book Room"):
                # Check availability
                available = execute_query('''
                    SELECT * FROM space_bookings 
                    WHERE room_name = ? AND booking_date = ? 
                    AND NOT (end_time <= ? OR start_time >= ?)
                ''', (room_name, booking_date.strftime('%Y-%m-%d'), start_time.strftime('%H:%M'), start_time.strftime('%H:%M')))
                
                if not available:
                    execute_update('''
                        INSERT INTO space_bookings 
                        (room_name, room_type, booking_date, start_time, end_time, booked_by, purpose, attendees_count)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (room_name, "Conference Room", booking_date, start_time, start_time, 
                          st.session_state.user['username'], purpose, attendees))
                    st.success("✅ Room booked successfully!")
                else:
                    st.error("❌ Room not available at selected time")
    
    with tab3:
        st.subheader("Space Utilization Analytics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_bookings = len(execute_query("SELECT * FROM space_bookings"))
            st.metric("Total Bookings", total_bookings)
        
        with col2:
            upcoming = len(execute_query("SELECT * FROM space_bookings WHERE booking_date >= date('now')"))
            st.metric("Upcoming Bookings", upcoming)
        
        with col3:
            popular_room = execute_query('''
                SELECT room_name, COUNT(*) as bookings 
                FROM space_bookings 
                GROUP BY room_name 
                ORDER BY bookings DESC LIMIT 1
            ''')
            if popular_room:
                st.metric("Most Popular Room", popular_room[0]['room_name'])

def show_preventive_maintenance():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.title("🔧 Preventive Maintenance")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📅 Schedule Overview", "➕ Add New Schedule", "📊 Analytics"])
    
    with tab1:
        st.subheader("Preventive Maintenance Schedule")
        
        schedules = execute_query('SELECT * FROM preventive_maintenance ORDER BY next_due, category')
        
        for schedule in schedules:
            frequency_class = get_frequency_color(schedule['frequency'])
            card_html = f'''
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
            '''
            st.markdown(card_html, unsafe_allow_html=True)
    
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
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_pm = len(execute_query("SELECT * FROM preventive_maintenance"))
        completed = len(execute_query("SELECT * FROM preventive_maintenance WHERE status = 'Completed'"))
        scheduled = len(execute_query("SELECT * FROM preventive_maintenance WHERE status = 'Scheduled'"))
        
        with col1:
            st.metric("Total Schedules", total_pm)
        with col2:
            st.metric("Completed", completed)
        with col3:
            st.metric("Scheduled", scheduled)
        with col4:
            completion_rate = (completed / total_pm * 100) if total_pm > 0 else 0
            st.metric("Completion Rate", f"{completion_rate:.1f}%")

def show_generator_records():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.title("⚡ Generator Records")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 Daily Records", "➕ New Record", "📊 Analytics"])
    
    with tab1:
        st.subheader("Generator Daily Records")
        
        records = execute_query('SELECT * FROM generator_records ORDER BY record_date DESC LIMIT 10')
        
        for record in records:
            card_html = f'''
            <div class="modern-card">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <h5 style="margin: 0 0 5px 0;">{record['generator_name']} ({record['generator_id']})</h5>
                        <p style="margin: 5px 0; font-size: 12px; color: #666;">
                            📅 {record['record_date']} | ⏰ {record['runtime_hours']} hours runtime
                        </p>
                    </div>
                    <div style="text-align: right;">
                        <p style="margin: 0; font-weight: bold; color: #2196F3;">{record['load_percentage']}%</p>
                        <p style="margin: 0; font-size: 12px;">Load</p>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-top: 15px;">
                    <div>
                        <p style="margin: 0; font-size: 12px; color: #666;">Fuel Used</p>
                        <p style="margin: 0; font-weight: bold;">{record['fuel_consumed_liters']}L</p>
                    </div>
                    <div>
                        <p style="margin: 0; font-size: 12px; color: #666;">Voltage</p>
                        <p style="margin: 0; font-weight: bold;">{record['voltage_output']}V</p>
                    </div>
                    <div>
                        <p style="margin: 0; font-size: 12px; color: #666;">Oil Level</p>
                        <p style="margin: 0; font-weight: bold;">{record['oil_level']}</p>
                    </div>
                    <div>
                        <p style="margin: 0; font-size: 12px; color: #666;">Battery</p>
                        <p style="margin: 0; font-weight: bold;">{record['battery_status']}</p>
                    </div>
                </div>
            </div>
            '''
            st.markdown(card_html, unsafe_allow_html=True)
    
    with tab2:
        st.subheader("Add New Generator Record")
        
        with st.form("new_generator_record"):
            col1, col2 = st.columns(2)
            
            with col1:
                generator_id = st.selectbox("Generator", ["GEN-001", "GEN-002", "GEN-003"])
                generator_name = st.text_input("Generator Name", value="Main Generator")
                record_date = st.date_input("Record Date", value=date.today())
                runtime_hours = st.number_input("Runtime Hours", min_value=0.0, step=0.1, value=8.0)
                fuel_consumed = st.number_input("Fuel Consumed (Liters)", min_value=0.0, step=0.1, value=80.0)
            
            with col2:
                oil_level = st.selectbox("Oil Level", ["Normal", "Low", "High", "Critical"])
                coolant_level = st.selectbox("Coolant Level", ["Normal", "Low", "High"])
                battery_status = st.selectbox("Battery Status", ["Good", "Fair", "Poor", "Replace"])
                load_percentage = st.slider("Load Percentage (%)", 0, 100, 75)
                issues_noted = st.text_area("Issues Noted")
            
            if st.form_submit_button("Save Record"):
                execute_update('''
                    INSERT INTO generator_records 
                    (generator_id, generator_name, record_date, runtime_hours, 
                     fuel_consumed_liters, oil_level, coolant_level, battery_status, load_percentage, 
                     issues_noted, recorded_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (generator_id, generator_name, record_date, runtime_hours,
                      fuel_consumed, oil_level, coolant_level, battery_status, load_percentage,
                      issues_noted, st.session_state.user['username']))
                st.success("✅ Generator record saved successfully!")
    
    with tab3:
        st.subheader("Generator Analytics")
        
        col1, col2, col3 = st.columns(3)
        
        total_runtime = sum([r.get('runtime_hours', 0) or 0 for r in execute_query("SELECT runtime_hours FROM generator_records")])
        total_fuel = sum([r.get('fuel_consumed_liters', 0) or 0 for r in execute_query("SELECT fuel_consumed_liters FROM generator_records")])
        
        with col1:
            st.metric("Total Runtime", f"{total_runtime:.1f} hours")
        with col2:
            st.metric("Total Fuel Used", f"{total_fuel:.1f} L")
        with col3:
            st.metric("Records Count", len(execute_query("SELECT * FROM generator_records")))

def show_hse_management():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.title("🛡️ HSE Management")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📅 HSE Schedule", "📋 Incident Reports", "➕ New Inspection"])
    
    with tab1:
        st.subheader("HSE Inspection Schedule")
        
        inspections = execute_query('SELECT * FROM hse_inspections ORDER BY inspection_date DESC')
        
        if inspections:
            for inspection in inspections:
                card_html = f'''
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
                </div>
                '''
                st.markdown(card_html, unsafe_allow_html=True)
        else:
            st.info("No HSE inspections scheduled")
    
    with tab2:
        st.subheader("Incident Reports")
        
        incidents = execute_query('SELECT * FROM hse_records WHERE record_type = "Incident" ORDER BY date_occurred DESC')
        
        for incident in incidents:
            severity_color = {
                'High': '#f44336',
                'Medium': '#FF9800',
                'Low': '#4CAF50'
            }.get(incident['severity'], '#666')
            
            card_html = f'''
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
                </div>
            </div>
            '''
            st.markdown(card_html, unsafe_allow_html=True)
    
    with tab3:
        st.subheader("New HSE Inspection")
        
        with st.form("new_hse_inspection"):
            col1, col2 = st.columns(2)
            
            with col1:
                inspection_type = st.selectbox("Inspection Type*", [
                    "Fire Safety Inspection", "Electrical Safety Inspection", 
                    "Workplace Safety Audit", "Environmental Compliance Check"
                ])
                location = st.text_input("Location*", value="Main Building")
                inspection_date = st.date_input("Inspection Date*", value=date.today())
            
            with col2:
                inspector = st.text_input("Inspector Name*", value=st.session_state.user['username'])
                status = st.selectbox("Status", ["Scheduled", "In Progress", "Completed"])
            
            findings = st.text_area("Findings")
            recommendations = st.text_area("Recommendations")
            
            if st.form_submit_button("Save Inspection"):
                execute_update('''
                    INSERT INTO hse_inspections 
                    (inspection_type, location, inspection_date, inspector, findings, recommendations, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (inspection_type, location, inspection_date, inspector, findings,
                      recommendations, status))
                st.success("✅ HSE inspection saved successfully!")

def show_compliance_dashboard():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.title("📊 Compliance Dashboard")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Mock compliance data
    compliance_rate = 84.5
    compliant = 42
    non_compliant = 5
    pending = 3
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Overall Compliance", f"{compliance_rate}%")
    with col2:
        st.metric("Compliant", compliant)
    with col3:
        st.metric("Non-Compliant", non_compliant)
    with col4:
        st.metric("Pending Review", pending)
    
    st.subheader("Compliance by Category")
    
    categories = {
        "Health & Safety": 92,
        "Environmental": 85,
        "Quality": 78,
        "Legal": 95,
        "Operational": 80
    }
    
    for category, score in categories.items():
        st.write(f"**{category}**")
        progress_html = f'''
            <div style="background: #e0e0e0; border-radius: 10px; height: 10px; margin: 5px 0 15px 0;">
                <div style="background: #4CAF50; width: {score}%; height: 100%; border-radius: 10px;"></div>
            </div>
        '''
        st.markdown(progress_html, unsafe_allow_html=True)
        st.caption(f"{score}% compliance")

def show_management_requests():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.title("👨‍💼 Management Requests")
    st.markdown('</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 Assign Jobs", "✅ Approve Completion"])
    
    with tab1:
        st.subheader("Assign Jobs to Vendors")
        
        pending_requests = execute_query('SELECT * FROM maintenance_requests WHERE status = "Pending" ORDER BY priority DESC')
        
        for request in pending_requests:
            with st.expander(f"Request #{request['id']}: {request['title']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Location:** {request['location']}")
                    st.write(f"**Facility Type:** {request['facility_type']}")
                    st.write(f"**Created By:** {request['created_by']}")
                
                with col2:
                    vendors = execute_query('SELECT * FROM vendors')
                    if vendors:
                        vendor_options = [f"{v['company_name']} ({v['username']})" for v in vendors]
                        selected_vendor = st.selectbox(f"Select Vendor", vendor_options, key=f"vendor_{request['id']}")
                        
                        if st.button(f"Assign to Vendor", key=f"assign_{request['id']}"):
                            vendor_username = selected_vendor.split('(')[-1].rstrip(')')
                            vendor_name = selected_vendor.split('(')[0].strip()
                            
                            execute_update(
                                'UPDATE maintenance_requests SET status = "Assigned", assigned_vendor = ?, assigned_vendor_username = ? WHERE id = ?',
                                (vendor_name, vendor_username, request['id'])
                            )
                            st.success(f"✅ Request assigned to {vendor_name}")
                            st.rerun()
    
    with tab2:
        st.subheader("Approve Completed Jobs")
        
        completed_jobs = execute_query('SELECT * FROM maintenance_requests WHERE status = "Completed"')
        
        for job in completed_jobs:
            card_html = f'''
            <div class="modern-card">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <h5 style="margin: 0 0 5px 0;">{job['title']}</h5>
                        <p style="margin: 5px 0; font-size: 12px; color: #666;">
                            Completed: {job['completed_date'] or 'N/A'}
                        </p>
                    </div>
                    <span class="status-badge status-completed">COMPLETED</span>
                </div>
                
                <div style="margin-top: 10px;">
                    <p><strong>Completion Notes:</strong> {job['completion_notes'] or 'No notes'}</p>
                    <p><strong>Invoice Amount:</strong> {format_naira(job['invoice_amount'])}</p>
                </div>
            </div>
            '''
            st.markdown(card_html, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✅ Approve", key=f"approve_{job['id']}"):
                    execute_update('UPDATE maintenance_requests SET status = "Approved" WHERE id = ?', (job['id'],))
                    st.success("✅ Job approved!")
                    st.rerun()
            
            with col2:
                if st.button(f"❌ Reject", key=f"reject_{job['id']}"):
                    execute_update('UPDATE maintenance_requests SET status = "Revision Required" WHERE id = ?', (job['id'],))
                    st.warning("⚠️ Job rejected, revision requested")
                    st.rerun()

def show_assigned_preventive_maintenance():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.title("🔧 Assigned Preventive Maintenance")
    st.markdown('</div>', unsafe_allow_html=True)
    
    user = st.session_state.user
    
    pm_tasks = execute_query('''
        SELECT * FROM preventive_maintenance 
        WHERE assigned_vendor_username = ? 
        ORDER BY next_due
    ''', (user['username'],))
    
    if pm_tasks:
        for task in pm_tasks:
            with st.expander(f"{task['service_description']} - Due: {task['next_due']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Service Code:** {task['service_code']}")
                    st.write(f"**Category:** {task['category']}")
                    st.write(f"**Frequency:** {task['frequency']}")
                
                with col2:
                    st.write(f"**Status:** {task['status']}")
                    st.write(f"**Estimated Hours:** {task['estimated_hours'] or 2}")
                
                if task['status'] != 'Completed':
                    with st.form(f"complete_pm_{task['id']}"):
                        completion_date = st.date_input("Completion Date", value=date.today())
                        work_performed = st.text_area("Work Performed")
                        
                        if st.form_submit_button("Mark as Completed"):
                            execute_update('''
                                UPDATE preventive_maintenance 
                                SET status = 'Completed', last_performed = ?, notes = ?
                                WHERE id = ?
                            ''', (completion_date.strftime('%Y-%m-%d'), work_performed, task['id']))
                            st.success("✅ Preventive maintenance task completed!")
                            st.rerun()
    else:
        st.info("No preventive maintenance tasks assigned to you")

def show_job_invoice_reports():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.title("🧾 Job & Invoice Reports")
    st.markdown('</div>', unsafe_allow_html=True)
    
    jobs = execute_query('''
        SELECT mr.*, v.company_name as vendor_name
        FROM maintenance_requests mr
        LEFT JOIN vendors v ON mr.assigned_vendor_username = v.username
        WHERE mr.status IN ('Completed', 'Approved')
        ORDER BY mr.completed_date DESC
    ''')
    
    if jobs:
        col1, col2, col3, col4 = st.columns(4)
        
        total_invoice = sum([j.get('invoice_amount', 0) or 0 for j in jobs])
        completed_jobs = len([j for j in jobs if j['status'] == 'Completed'])
        approved_jobs = len([j for j in jobs if j['status'] == 'Approved'])
        
        with col1:
            st.metric("Total Jobs", len(jobs))
        with col2:
            st.metric("Total Invoice Value", format_naira(total_invoice))
        with col3:
            st.metric("Completed Jobs", completed_jobs)
        with col4:
            st.metric("Approved Jobs", approved_jobs)
        
        st.subheader("Job Details")
        
        display_data = []
        for job in jobs:
            display_data.append({
                'Job ID': job['id'],
                'Title': job['title'],
                'Vendor': job['vendor_name'] or 'N/A',
                'Completed Date': job['completed_date'][:10] if job['completed_date'] else 'N/A',
                'Invoice Amount': format_naira(job['invoice_amount']),
                'Status': job['status']
            })
        
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No completed jobs found")

def show_vendor_management():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.title("👥 Vendor Management")
    st.markdown('</div>', unsafe_allow_html=True)
    
    vendors = execute_query('SELECT * FROM vendors ORDER BY company_name')
    
    if vendors:
        for vendor in vendors:
            with st.expander(f"{vendor['company_name']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Company Name:** {vendor['company_name']}")
                    st.write(f"**Contact Person:** {vendor['contact_person']}")
                    st.write(f"**Email:** {vendor['email']}")
                    st.write(f"**Phone:** {vendor['phone']}")
                    st.write(f"**Vendor Type:** {vendor['vendor_type']}")
                
                with col2:
                    st.write(f"**Services Offered:** {vendor['services_offered']}")
                    st.write(f"**Address:** {vendor['address']}")
                    st.write(f"**Registration Date:** {vendor['registration_date'][:10]}")
                    st.write(f"**Status:** {vendor['status']}")
    else:
        st.info("No vendors found")

def show_reports():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.title("📈 Reports & Analytics")
    st.markdown('</div>', unsafe_allow_html=True)
    
    all_requests = execute_query('SELECT * FROM maintenance_requests')
    
    if all_requests:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Requests", len(all_requests))
        with col2:
            pending = len([r for r in all_requests if r['status'] == 'Pending'])
            st.metric("Pending", pending)
        with col3:
            completed = len([r for r in all_requests if r['status'] == 'Completed'])
            st.metric("Completed", completed)
        with col4:
            total_invoice = sum([r.get('invoice_amount', 0) or 0 for r in all_requests])
            st.metric("Total Invoice", format_naira(total_invoice))
        
        # Status distribution chart
        status_counts = {}
        for req in all_requests:
            status = req['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if status_counts:
            fig = px.pie(values=list(status_counts.values()), 
                        names=list(status_counts.keys()),
                        title="Request Status Distribution",
                        color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for reports")

def show_assigned_jobs():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.title("🔧 Assigned Jobs")
    st.markdown('</div>', unsafe_allow_html=True)
    
    vendor_requests = execute_query(
        'SELECT * FROM maintenance_requests WHERE assigned_vendor_username = ? AND status = "Assigned" ORDER BY created_date DESC',
        (st.session_state.user['username'],)
    )
    
    if vendor_requests:
        for job in vendor_requests:
            card_html = f'''
            <div class="modern-card">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <h4 style="margin: 0 0 5px 0;">{job['title']}</h4>
                        <p style="margin: 5px 0; font-size: 12px; color: #666;">
                            📍 {job['location']} | 🏢 {job['facility_type']}
                        </p>
                    </div>
                    <span class="status-badge status-assigned">ASSIGNED</span>
                </div>
                <p style="margin: 10px 0;">{job['description']}</p>
            </div>
            '''
            st.markdown(card_html, unsafe_allow_html=True)
            
            with st.form(f"complete_{job['id']}"):
                completion_notes = st.text_area("Completion Notes", key=f"notes_{job['id']}")
                invoice_amount = st.number_input("Invoice Amount (₦)", min_value=0.0, key=f"amount_{job['id']}")
                
                if st.form_submit_button("Mark as Complete"):
                    execute_update('''
                        UPDATE maintenance_requests 
                        SET status = "Completed", completion_notes = ?, invoice_amount = ?, completed_date = ?
                        WHERE id = ?
                    ''', (completion_notes, invoice_amount, datetime.now().strftime('%Y-%m-%d'), job['id']))
                    st.success("✅ Job marked as complete!")
                    st.rerun()
    else:
        st.info("📭 No assigned jobs at the moment")

def show_completed_jobs():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.title("✅ Completed Jobs")
    st.markdown('</div>', unsafe_allow_html=True)
    
    vendor_requests = execute_query(
        'SELECT * FROM maintenance_requests WHERE assigned_vendor_username = ? AND status IN ("Completed", "Approved") ORDER BY completed_date DESC',
        (st.session_state.user['username'],)
    )
    
    if vendor_requests:
        display_data = []
        for job in vendor_requests:
            display_data.append({
                'ID': job['id'],
                'Title': job['title'],
                'Location': job['location'],
                'Completed Date': job['completed_date'][:10] if job['completed_date'] else 'N/A',
                'Invoice Amount': format_naira(job['invoice_amount']),
                'Status': job['status']
            })
        
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("📭 No completed jobs found")

def show_vendor_registration():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.title("🏢 Vendor Registration")
    st.markdown('</div>', unsafe_allow_html=True)
    
    existing_vendor = execute_query(
        'SELECT * FROM vendors WHERE username = ?',
        (st.session_state.user['username'],)
    )
    
    if existing_vendor:
        vendor = existing_vendor[0]
        st.success("✅ You are already registered as a vendor!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🏢 Company Information**")
            st.write(f"**Company Name:** {vendor['company_name']}")
            st.write(f"**Contact Person:** {vendor['contact_person']}")
            st.write(f"**Email:** {vendor['email']}")
        
        with col2:
            st.write("**🔧 Services & Details**")
            st.write(f"**Services Offered:** {vendor['services_offered']}")
            st.write(f"**Vendor Type:** {vendor['vendor_type']}")
            st.write(f"**Registration Date:** {vendor['registration_date'][:10]}")
        
        # Update form
        st.subheader("Update Vendor Information")
        with st.form("update_vendor_form"):
            contact_person = st.text_input("Contact Person", value=vendor['contact_person'])
            email = st.text_input("Email", value=vendor['email'])
            phone = st.text_input("Phone", value=vendor['phone'])
            services_offered = st.text_area("Services Offered", value=vendor['services_offered'])
            address = st.text_area("Address", value=vendor['address'])
            
            if st.form_submit_button("Update Information"):
                execute_update('''
                    UPDATE vendors SET contact_person = ?, email = ?, phone = ?, services_offered = ?, address = ?
                    WHERE username = ?
                ''', (contact_person, email, phone, services_offered, address, st.session_state.user['username']))
                st.success("✅ Vendor information updated successfully!")
                st.rerun()
    else:
        st.info("📝 Please complete your vendor registration details below:")
        
        with st.form("vendor_registration"):
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
                    execute_update('''
                        INSERT INTO vendors (company_name, contact_person, email, phone, vendor_type, services_offered, address, username) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (company_name, contact_person, email, phone, st.session_state.user['vendor_type'], 
                         services_offered, address, st.session_state.user['username']))
                    st.success("✅ Vendor registration completed successfully!")
                    st.rerun()

def show_invoice_creation():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.title("🧾 Invoice Creation")
    st.markdown('</div>', unsafe_allow_html=True)
    
    vendor_jobs = execute_query('''
        SELECT mr.* 
        FROM maintenance_requests mr
        WHERE mr.assigned_vendor_username = ? AND mr.status = 'Completed'
        ORDER BY mr.completed_date DESC
    ''', (st.session_state.user['username'],))
    
    if not vendor_jobs:
        st.info("📭 No completed jobs available for invoicing")
        return
    
    with st.form("invoice_creation_form"):
        job_options = [f"{j['id']}: {j['title']}" for j in vendor_jobs]
        job_id = st.selectbox("Select Job", job_options)
        invoice_number = st.text_input("🔢 Invoice Number *", value=f"INV-{datetime.now().strftime('%Y%m%d')}-001")
        invoice_date = st.date_input("📅 Invoice Date *", value=date.today())
        details_of_work = st.text_area("🔧 Details of Work Done *", height=100)
        quantity = st.number_input("📦 Quantity *", min_value=1, value=1)
        unit_cost = st.number_input("💵 Unit Cost (₦) *", min_value=0.0, step=0.01, value=10000.00)
        
        submitted = st.form_submit_button("📄 Create Invoice", use_container_width=True)
        
        if submitted:
            if not all([invoice_number, details_of_work]):
                st.error("⚠️ Please fill in all required fields (*)")
            else:
                amount = quantity * unit_cost
                execute_update('''
                    INSERT INTO invoices (invoice_number, request_id, vendor_username, invoice_date, 
                    details_of_work, quantity, unit_cost, amount, total_amount, currency) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (invoice_number, int(job_id.split(':')[0]), st.session_state.user['username'], 
                     invoice_date.strftime('%Y-%m-%d'), details_of_work, quantity, unit_cost, 
                     amount, amount, 'NGN'))
                st.success("✅ Invoice created successfully!")

def show_vendor_login_info():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
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
    
    header_html = f"""
    <div class="header-container">
        <h1 style="margin: 0; display: flex; align-items: center; gap: 10px;">
            🏢 FACILITIES MANAGEMENT SYSTEM™
            <span style="font-size: 14px; background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 10px;">
                v4.0
            </span>
        </h1>
        <p style="margin: 5px 0 0 0; opacity: 0.9;">
            Welcome, <strong>{user['username']}</strong> | Role: {role.replace('_', ' ').title()}
        </p>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
    
    show_quick_actions(role)
    
    with st.sidebar:
        sidebar_html = f"""
        <div style="text-align: center; padding: 15px; background: linear-gradient(45deg, #4CAF50, #2E7D32); 
                 border-radius: 10px; margin-bottom: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
            <div style="font-size: 32px; margin-bottom: 10px;">👋</div>
            <h3 style="color: white; margin: 0;">{user['username']}</h3>
            <p style="color: white; margin: 5px 0; font-size: 12px;">{role.replace('_', ' ').title()}</p>
        </div>
        """
        st.markdown(sidebar_html, unsafe_allow_html=True)
        
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
        
        st.session_state.selected_menu = selected_menu
        
        st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
        
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Menu routing
    menu_functions = {
        "Dashboard": show_dashboard,
        "Create Request": show_create_request,
        "My Requests": show_my_requests,
        "Space Management": show_space_management,
        "Manage Requests": show_manage_requests,
        "Management Requests": show_management_requests,
        "Vendor Management": show_vendor_management,
        "Reports": show_reports,
        "Preventive Maintenance": show_preventive_maintenance,
        "Generator Records": show_generator_records,
        "HSE Management": show_hse_management,
        "Compliance Dashboard": show_compliance_dashboard,
        "Job & Invoice Reports": show_job_invoice_reports,
        "Vendor Login Info": show_vendor_login_info,
        "Assigned Jobs": show_assigned_jobs,
        "Assigned Preventive Maintenance": show_assigned_preventive_maintenance,
        "Completed Jobs": show_completed_jobs,
        "Vendor Registration": show_vendor_registration,
        "Invoice Creation": show_invoice_creation,
    }
    
    if selected_menu in menu_functions:
        menu_functions[selected_menu]()
    else:
        show_dashboard()

def main():
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
