import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, date
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

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

# Custom CSS (keep your existing CSS, it's fine)
st.markdown("""
    <style>
    /* Your existing CSS styles here - keep them as they are good for UI */
    .main {
        background-color: #f8f9fa;
    }
    .login-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        color: white;
        max-width: 600px;
        margin: 0 auto;
    }
    /* ... rest of your CSS ... */
    </style>
""", unsafe_allow_html=True)

# Database setup - MINIMAL VERSION (NO SAMPLE DATA)
def init_database():
    """Initialize database with empty tables only - no sample data"""
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
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    
    # MINIMAL USER SETUP - Only essential users (NO sample vendors or data)
    essential_users = [
        ('facility_user', '0123456', 'facility_user', None),
        ('facility_manager', '0123456', 'facility_manager', None),
    ]
    
    for username, password, role, vendor_type in essential_users:
        cursor.execute(
            'INSERT OR IGNORE INTO users (username, password_hash, role, vendor_type) VALUES (?, ?, ?, ?)',
            (username, password, role, vendor_type)
        )
    
    conn.commit()
    conn.close()

# Initialize database (FAST - no sample data)
init_database()

# Database functions
def get_connection():
    return sqlite3.connect('facilities_management.db', check_same_thread=False)

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

def safe_date(value, default=None):
    try:
        if value is None:
            return default
        if isinstance(value, str):
            return datetime.strptime(value, '%Y-%m-%d').date()
        return value
    except:
        return default

# Currency formatting
def format_naira(amount, decimal_places=2):
    try:
        amount = safe_float(amount, 0)
        return f"₦{amount:,.{decimal_places}f}"
    except:
        return "₦0.00"

# Authentication
def authenticate_user(username, password):
    users = execute_query('SELECT * FROM users WHERE username = ? AND password_hash = ?', (username, password))
    return users[0] if users else None

# ========== PREVENTIVE MAINTENANCE FUNCTIONS ==========
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

# ========== GENERATOR RECORDS FUNCTIONS ==========
def get_generator_records(start_date=None, end_date=None):
    query = '''
        SELECT * FROM generator_records 
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
    if closing_hours < opening_hours:
        return False, "Closing hours cannot be less than opening hours"
    
    if opening_diesel_level < 0 or closing_diesel_level < 0:
        return False, "Diesel levels cannot be negative"
    
    success = execute_update('''
        INSERT INTO generator_records 
        (record_date, generator_name, opening_hours, closing_hours, 
         opening_diesel_level, closing_diesel_level, recorded_by, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (record_date.isoformat(), generator_name, opening_hours, closing_hours,
          opening_diesel_level, closing_diesel_level, recorded_by, notes))
    
    return success, "Record saved successfully" if success else "Failed to save record"

# ========== SPACE MANAGEMENT FUNCTIONS ==========
def get_space_bookings(filters=None):
    base_query = 'SELECT * FROM space_bookings WHERE 1=1'
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

# ========== HSE MANAGEMENT FUNCTIONS ==========
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
    
    base_query += ' ORDER BY next_inspection_date ASC'
    return execute_query(base_query, params)

def add_hse_schedule(inspection_type, area, frequency, next_inspection_date, assigned_to):
    return execute_update('''
        INSERT INTO hse_schedule 
        (inspection_type, area, frequency, next_inspection_date, assigned_to)
        VALUES (?, ?, ?, ?, ?)
    ''', (inspection_type, area, frequency, next_inspection_date.isoformat(), assigned_to))

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

# ========== SIMPLIFIED PAGES ==========

def show_preventive_maintenance():
    """Simplified Preventive Maintenance Page"""
    st.title("📅 Planned Preventive Maintenance")
    
    tab1, tab2 = st.tabs(["📋 Schedule", "➕ Add New"])
    
    with tab1:
        st.subheader("Maintenance Schedule")
        
        # Simple filter
        status_filter = st.selectbox("Filter by Status", ["All", "Upcoming", "Completed"], key="pm_status")
        
        filters = {}
        if status_filter != "All":
            filters['status'] = status_filter
        
        schedule = get_preventive_maintenance(filters)
        
        if schedule:
            df = pd.DataFrame(schedule)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("📭 No maintenance schedules found. Add your first schedule!")
    
    with tab2:
        st.subheader("Add Maintenance Schedule")
        
        with st.form("add_maintenance"):
            col1, col2 = st.columns(2)
            
            with col1:
                equipment_name = st.text_input("Equipment Name *")
                equipment_type = st.selectbox("Equipment Type *", 
                                            ["HVAC", "Generator", "Fire Safety", "Electrical", "Plumbing", "Other"])
                location = st.text_input("Location *", value="Main Building")
            
            with col2:
                maintenance_type = st.selectbox("Maintenance Type *", 
                                              ["Routine Check", "Inspection", "Service", "Calibration", "Repair"])
                frequency = st.selectbox("Frequency *", 
                                       ["Daily", "Weekly", "Monthly", "Quarterly", "Biannual", "Annual"])
                next_maintenance_date = st.date_input("Next Maintenance Date *", 
                                                     value=datetime.now().date() + timedelta(days=30))
            
            assigned_to = st.text_input("Assigned To")
            notes = st.text_area("Notes")
            
            if st.form_submit_button("Add to Schedule"):
                if all([equipment_name, equipment_type, location, maintenance_type, frequency]):
                    add_preventive_maintenance(
                        equipment_name, equipment_type, location, maintenance_type,
                        frequency, None, next_maintenance_date.isoformat(), assigned_to, notes
                    )
                    st.success("✅ Schedule added!")
                    st.rerun()

def show_generator_diesel_records():
    """Simplified Generator Records Page"""
    st.title("⛽ Generator & Diesel Records")
    
    tab1, tab2 = st.tabs(["📝 Records", "➕ New Record"])
    
    with tab1:
        st.subheader("Generator Records")
        
        records = get_generator_records()
        
        if records:
            df = pd.DataFrame(records)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("📭 No records found. Add your first record!")
    
    with tab2:
        st.subheader("Add Daily Record")
        
        with st.form("add_generator_record"):
            record_date = st.date_input("Record Date", value=datetime.now().date())
            generator_name = st.text_input("Generator Name", value="Generator #1")
            
            col1, col2 = st.columns(2)
            with col1:
                opening_hours = st.number_input("Opening Hours", min_value=0.0, step=0.1, format="%.1f")
                opening_diesel_level = st.number_input("Opening Diesel (L)", min_value=0.0, step=0.1, format="%.1f")
            
            with col2:
                closing_hours = st.number_input("Closing Hours", min_value=0.0, step=0.1, format="%.1f")
                closing_diesel_level = st.number_input("Closing Diesel (L)", min_value=0.0, step=0.1, format="%.1f")
            
            recorded_by = st.text_input("Recorded By", value=st.session_state.user.get('username', ''))
            notes = st.text_area("Notes")
            
            if st.form_submit_button("Save Record"):
                success, message = add_generator_record(
                    record_date, generator_name, opening_hours, closing_hours,
                    opening_diesel_level, closing_diesel_level, recorded_by, notes
                )
                if success:
                    st.success("✅ Record saved!")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")

def show_space_management():
    """Simplified Space Management Page"""
    st.title("🏢 Space Management")
    
    tab1, tab2 = st.tabs(["📅 Bookings", "➕ New Booking"])
    
    with tab1:
        st.subheader("Room Bookings")
        
        bookings = get_space_bookings()
        
        if bookings:
            df = pd.DataFrame(bookings)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("📭 No bookings found. Create your first booking!")
    
    with tab2:
        st.subheader("Book a Room")
        
        with st.form("new_booking"):
            room_name = st.text_input("Room Name", value="Conference Room A")
            room_type = st.selectbox("Room Type", ["Conference", "Meeting", "Training", "Cafeteria"])
            booking_date = st.date_input("Booking Date", value=datetime.now().date())
            
            col1, col2 = st.columns(2)
            with col1:
                start_time = st.time_input("Start Time", value=datetime.strptime("09:00", "%H:%M").time())
            with col2:
                end_time = st.time_input("End Time", value=datetime.strptime("12:00", "%H:%M").time())
            
            purpose = st.text_input("Purpose")
            department = st.text_input("Department", value="Operations")
            attendees_count = st.number_input("Attendees", min_value=1, value=10)
            
            if st.form_submit_button("Book Room"):
                if check_room_availability(room_name, booking_date, 
                                         start_time.strftime("%H:%M"), 
                                         end_time.strftime("%H:%M")):
                    add_space_booking(
                        room_name, room_type, booking_date,
                        start_time.strftime("%H:%M"), end_time.strftime("%H:%M"),
                        purpose, st.session_state.user['username'], department,
                        attendees_count, False, ""
                    )
                    st.success("✅ Room booked successfully!")
                    st.rerun()
                else:
                    st.error("❌ Room not available for selected time")

def show_hse_management():
    """Simplified HSE Management Page"""
    st.title("🚨 HSE Management")
    
    tab1, tab2, tab3 = st.tabs(["📅 Inspections", "🚨 Incidents", "➕ New"])
    
    with tab1:
        st.subheader("HSE Inspections")
        
        inspections = get_hse_schedule()
        
        if inspections:
            df = pd.DataFrame(inspections)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("📭 No inspections scheduled. Schedule your first inspection!")
    
    with tab2:
        st.subheader("HSE Incidents")
        
        incidents = get_hse_incidents()
        
        if incidents:
            df = pd.DataFrame(incidents)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("📭 No incident reports. Report your first incident!")
    
    with tab3:
        st.subheader("Add New")
        
        option = st.radio("What would you like to add?", ["Inspection Schedule", "Incident Report"])
        
        if option == "Inspection Schedule":
            with st.form("add_inspection"):
                inspection_type = st.text_input("Inspection Type", value="Fire Safety")
                area = st.text_input("Area", value="Main Building")
                frequency = st.selectbox("Frequency", ["Daily", "Weekly", "Monthly", "Quarterly"])
                next_inspection_date = st.date_input("Next Inspection Date", value=datetime.now().date() + timedelta(days=7))
                assigned_to = st.text_input("Assigned To", value=st.session_state.user['username'])
                
                if st.form_submit_button("Schedule Inspection"):
                    add_hse_schedule(inspection_type, area, frequency, next_inspection_date, assigned_to)
                    st.success("✅ Inspection scheduled!")
                    st.rerun()
        
        else:  # Incident Report
            with st.form("add_incident"):
                incident_date = st.date_input("Incident Date", value=datetime.now().date())
                incident_time = st.time_input("Incident Time", value=datetime.now().time())
                location = st.text_input("Location", value="Main Building")
                incident_type = st.selectbox("Incident Type", 
                                           ["Near Miss", "First Aid", "Medical Treatment", "Property Damage"])
                severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
                description = st.text_area("Description")
                reported_by = st.text_input("Reported By", value=st.session_state.user['username'])
                
                if st.form_submit_button("Submit Report"):
                    add_hse_incident(
                        incident_date, incident_time.strftime("%H:%M"), location,
                        incident_type, severity, description, reported_by, "", ""
                    )
                    st.success("✅ Incident reported!")
                    st.rerun()

# ========== SIMPLIFIED DASHBOARD ==========

def show_dashboard():
    """Simplified Dashboard"""
    st.title("📊 Dashboard")
    
    user = st.session_state.user
    role = user['role']
    
    st.write(f"Welcome, **{user['username']}**! You're logged in as **{role.replace('_', ' ').title()}**")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        maintenance_count = len(get_preventive_maintenance())
        st.metric("Maintenance Items", maintenance_count)
    
    with col2:
        generator_records = len(get_generator_records())
        st.metric("Generator Records", generator_records)
    
    with col3:
        bookings_count = len(get_space_bookings())
        st.metric("Room Bookings", bookings_count)
    
    with col4:
        inspections_count = len(get_hse_schedule())
        st.metric("HSE Inspections", inspections_count)
    
    st.markdown("---")
    
    # Quick access buttons
    st.subheader("🚀 Quick Access")
    
    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
    
    with col_q1:
        if st.button("📅 Maintenance", use_container_width=True):
            st.session_state.navigation_menu = "Preventive Maintenance"
            st.rerun()
    
    with col_q2:
        if st.button("⛽ Generator", use_container_width=True):
            st.session_state.navigation_menu = "Generator Records"
            st.rerun()
    
    with col_q3:
        if st.button("🏢 Space", use_container_width=True):
            st.session_state.navigation_menu = "Space Management"
            st.rerun()
    
    with col_q4:
        if st.button("🚨 HSE", use_container_width=True):
            st.session_state.navigation_menu = "HSE Management"
            st.rerun()

# ========== SIMPLIFIED LOGIN ==========

def show_login():
    """Simplified Login Page"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        st.markdown('<h1 class="login-title">🏢 FACILITIES MANAGEMENT</h1>', unsafe_allow_html=True)
        st.markdown('<h4 style="text-align: center; color: rgba(255,255,255,0.9);">Login</h4>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Login", use_container_width=True):
                if username and password:
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials")
                else:
                    st.warning("⚠️ Enter username and password")
        
        # Simple credentials
        st.markdown("""
            <div style="margin-top: 20px; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px;">
                <p style="color: white; margin: 0;"><strong>Demo Credentials:</strong></p>
                <p style="color: white; margin: 5px 0;">Username: <code>facility_user</code></p>
                <p style="color: white; margin: 5px 0;">Password: <code>0123456</code></p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ========== SIMPLIFIED MAIN APP ==========

def show_main_app():
    """Simplified Main Application"""
    user = st.session_state.user
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown(f"**Welcome, {user['username']}**")
        st.markdown("---")
        
        # Simple navigation options
        nav_options = ["Dashboard", "Preventive Maintenance", "Generator Records", 
                      "Space Management", "HSE Management"]
        
        if 'navigation_menu' not in st.session_state:
            st.session_state.navigation_menu = "Dashboard"
        
        selected = st.radio("Navigation", nav_options, 
                          index=nav_options.index(st.session_state.navigation_menu) 
                          if st.session_state.navigation_menu in nav_options else 0)
        
        st.session_state.navigation_menu = selected
        st.markdown("---")
        
        if st.button("Logout", type="secondary", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Route to selected page
    if selected == "Dashboard":
        show_dashboard()
    elif selected == "Preventive Maintenance":
        show_preventive_maintenance()
    elif selected == "Generator Records":
        show_generator_diesel_records()
    elif selected == "Space Management":
        show_space_management()
    elif selected == "HSE Management":
        show_hse_management()

# ========== MAIN FUNCTION ==========

def main():
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    if st.session_state.user is None:
        show_login()
    else:
        show_main_app()

if __name__ == "__main__":
    main()
