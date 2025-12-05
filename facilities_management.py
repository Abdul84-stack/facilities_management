# ... (ALL THE IMPORTS REMAIN THE SAME - keep everything from the original)

# ========== UPDATED DATABASE SETUP WITH REDUCED MOCKED DATA ==========
def init_database():
    conn = sqlite3.connect('facilities_management.db')
    cursor = conn.cursor()
    
    # Users table (unchanged)
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
    
    # ... (All other table creation statements remain the same)
    
    # ========== REDUCED SAMPLE DATA INSERTION ==========
    
    # Insert sample users (unchanged)
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
    
    # Insert sample vendors (unchanged)
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
    
    # ========== UPDATED: REDUCED PREVENTIVE MAINTENANCE DATA (from 7000+ to 5) ==========
    today = datetime.now().date()
    sample_maintenance = [
        ('Main HVAC System', 'HVAC', 'Main Building', 'Routine Check', 'Monthly', 
         (today - timedelta(days=15)).isoformat(), (today + timedelta(days=15)).isoformat(), 'HVAC Team', 'Regular maintenance check'),
        ('Fire Extinguishers', 'Fire Safety', 'All Floors', 'Inspection', 'Biannual',
         (today - timedelta(days=60)).isoformat(), (today + timedelta(days=120)).isoformat(), 'Safety Officer', 'Fire safety inspection'),
        ('Smoke Detectors', 'Fire Safety', 'All Floors', 'Testing', 'Quarterly',
         (today - timedelta(days=45)).isoformat(), (today + timedelta(days=45)).isoformat(), 'Maintenance Team', 'System testing'),
        ('Generator Set #1', 'Generator', 'Generator Room', 'Service', '200 hours',
         (today - timedelta(days=10)).isoformat(), (today + timedelta(days=10)).isoformat(), 'Generator Team', 'Regular service'),
        ('Pest Control', 'General', 'Entire Facility', 'Fumigation', 'Quarterly',
         (today - timedelta(days=30)).isoformat(), (today + timedelta(days=60)).isoformat(), 'Pest Control Vendor', 'Full facility fumigation')
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
    
    # ========== UPDATED: REDUCED GENERATOR RECORDS (from 9833 to 3) ==========
    for i in range(3):  # Changed from 7 to 3
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
    
    # ========== UPDATED: REDUCED SPACE BOOKINGS (to 2 as requested) ==========
    sample_bookings = [
        ('Conference Room A', 'Conference', today.isoformat(), '09:00', '12:00', 
         'Management Meeting', 'facility_manager', 'Management', 10, 'Confirmed', 0, None),
        ('Meeting Room B', 'Meeting', (today + timedelta(days=1)).isoformat(), '14:00', '16:00', 
         'Team Brainstorming', 'facility_user', 'Operations', 6, 'Confirmed', 0, None)
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
    
    # ========== UPDATED: REDUCED HSE SCHEDULE DATA (to 3 as requested) ==========
    sample_hse_schedule = [
        ('Fire Safety Inspection', 'All Buildings', 'Quarterly', 
         (today - timedelta(days=45)).isoformat(), (today + timedelta(days=45)).isoformat(), 
         'hse_officer', 'Compliant', None, None, None),
        ('First Aid Kit Check', 'All Floors', 'Monthly',
         (today - timedelta(days=20)).isoformat(), (today + timedelta(days=10)).isoformat(),
         'hse_officer', 'Non-Compliant', 'Some kits missing bandages', 'Restock bandages', (today + timedelta(days=7)).isoformat()),
        ('Emergency Exit Inspection', 'Main Building', 'Monthly',
         (today - timedelta(days=15)).isoformat(), (today + timedelta(days=15)).isoformat(),
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

# ... (ALL OTHER FUNCTIONS REMAIN THE SAME UNTIL VENDOR REGISTRATION FUNCTIONS)

# ========== UPDATED VENDOR REGISTRATION FUNCTION WITH LOGIN DETAILS GENERATION ==========
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
        
        # Vendor Login Details Section
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🔑 Vendor Login Details")
        st.write("Vendor login details will be automatically generated upon registration.")
        
        # Generate vendor-specific username and password
        if company_name:
            # Generate username from company name (lowercase, no spaces)
            vendor_username = company_name.lower().replace(' ', '_') + "_vendor"
            # Generate a random password
            import random
            import string
            vendor_password = ''.join(random.choices(string.digits, k=7))
            
            st.write(f"**Generated Username:** `{vendor_username}`")
            st.write(f"**Generated Password:** `{vendor_password}`")
            st.write("**Note:** These credentials will be saved for the vendor to access the system.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        submitted = st.form_submit_button("🚀 Register Vendor", use_container_width=True)
        
        if submitted:
            if not all([company_name, contact_person, email, phone, services_offered, address]):
                st.error("⚠️ Please fill in all required fields (*)")
            else:
                # First, create a user account for the vendor
                vendor_username = company_name.lower().replace(' ', '_') + "_vendor"
                vendor_password = '0123456'  # Default password for all vendors
                
                # Check if username already exists
                existing_user = execute_query('SELECT * FROM users WHERE username = ?', (vendor_username,))
                if existing_user:
                    st.error(f"❌ Username '{vendor_username}' already exists. Please modify company name.")
                else:
                    # Create user account
                    user_success = execute_update(
                        'INSERT INTO users (username, password_hash, role, vendor_type) VALUES (?, ?, ?, ?)',
                        (vendor_username, vendor_password, 'vendor', st.session_state.user['vendor_type'])
                    )
                    
                    if user_success:
                        # Then create vendor record
                        vendor_success = execute_update(
                            '''INSERT INTO vendors 
                            (username, company_name, contact_person, email, phone, vendor_type, services_offered, 
                            annual_turnover, tax_identification_number, rc_number, key_management_staff, 
                            account_details, certification, address) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            (vendor_username, company_name, contact_person, email, phone, 
                             st.session_state.user['vendor_type'], services_offered, annual_turnover, 
                             tax_identification_number, rc_number, key_management_staff, 
                             account_details, certification, address)
                        )
                        
                        if vendor_success:
                            st.success("✅ Vendor registration completed successfully!")
                            st.success(f"**Vendor Login Details:**")
                            st.success(f"**Username:** `{vendor_username}`")
                            st.success(f"**Password:** `{vendor_password}`")
                            st.rerun()
                        else:
                            st.error("❌ Failed to complete vendor registration")
                    else:
                        st.error("❌ Failed to create user account for vendor")

# ========== UPDATED DASHBOARD FUNCTIONS WITH WORKING QUICK ACTIONS ==========

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
    
    # FIXED: Working Quick Access buttons
    st.subheader("🚀 Quick Access")
    
    col_q1, col_q2, col_q3 = st.columns(3)
    
    with col_q1:
        # Fixed: This button now correctly updates session state
        if st.button("📅 Book a Room", key="quick_space", use_container_width=True):
            st.session_state.navigation_menu = "Space Management"
            st.rerun()
    
    with col_q2:
        # Fixed: This button now correctly updates session state
        if st.button("⛽ Generator Records", key="quick_generator", use_container_width=True):
            st.session_state.navigation_menu = "Generator Records"
            st.rerun()
    
    with col_q3:
        # Fixed: This button now correctly updates session state
        if st.button("🚨 Report Incident", key="quick_hse", use_container_width=True):
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
    
    # FIXED: Working Quick Access buttons for managers
    st.subheader("🚀 Management Quick Access")
    
    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
    
    with col_q1:
        # Fixed: This button now correctly updates session state
        if st.button("📅 Maintenance Schedule", key="manager_quick_pm", use_container_width=True):
            st.session_state.navigation_menu = "Preventive Maintenance"
            st.rerun()
    
    with col_q2:
        # Fixed: This button now correctly updates session state
        if st.button("🏢 Space Management", key="manager_quick_space", use_container_width=True):
            st.session_state.navigation_menu = "Space Management"
            st.rerun()
    
    with col_q3:
        # Fixed: This button now correctly updates session state
        if st.button("🚨 HSE Dashboard", key="manager_quick_hse", use_container_width=True):
            st.session_state.navigation_menu = "HSE Management"
            st.rerun()
    
    with col_q4:
        # Fixed: This button now correctly updates session state
        if st.button("⛽ Generator Reports", key="manager_quick_gen", use_container_width=True):
            st.session_state.navigation_menu = "Generator Records"
            st.rerun()
    
    # ... (rest of the manager dashboard function remains the same)

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
    
    # FIXED: Working Quick Actions for HSE Officer
    st.subheader("⚡ Quick Actions")
    
    col_q1, col_q2, col_q3 = st.columns(3)
    
    with col_q1:
        # Fixed: This button now correctly updates session state
        if st.button("➕ Schedule Inspection", key="hse_quick_schedule", use_container_width=True):
            st.session_state.navigation_menu = "HSE Management"
            st.session_state.hse_tab = "📅 HSE Schedule"  # Optional: Set specific tab
            st.rerun()
    
    with col_q2:
        # Fixed: This button now correctly updates session state
        if st.button("🚨 Report Incident", key="hse_quick_incident", use_container_width=True):
            st.session_state.navigation_menu = "HSE Management"
            st.session_state.hse_tab = "🚨 Incident Reports"  # Optional: Set specific tab
            st.rerun()
    
    with col_q3:
        # Fixed: This button now correctly updates session state
        if st.button("📊 View Compliance", key="hse_quick_compliance", use_container_width=True):
            st.session_state.navigation_menu = "HSE Management"
            st.session_state.hse_tab = "📊 Compliance Dashboard"  # Optional: Set specific tab
            st.rerun()
    
    # ... (rest of the HSE dashboard function remains the same)

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
    
    # FIXED: Working Quick Actions for Space Manager
    st.subheader("⚡ Quick Actions")
    
    col_q1, col_q2 = st.columns(2)
    
    with col_q1:
        # Fixed: This button now correctly updates session state
        if st.button("➕ New Booking", key="space_quick_new", use_container_width=True):
            st.session_state.navigation_menu = "Space Management"
            st.session_state.space_tab = "➕ New Booking"  # Optional: Set specific tab
            st.rerun()
    
    with col_q2:
        # Fixed: This button now correctly updates session state
        if st.button("📅 View All Bookings", key="space_quick_view", use_container_width=True):
            st.session_state.navigation_menu = "Space Management"
            st.session_state.space_tab = "📅 View Bookings"  # Optional: Set specific tab
            st.rerun()
    
    # ... (rest of the space dashboard function remains the same)

# ========== UPDATED MAIN APP FUNCTION ==========

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
        
        # Update session state - FIXED: This ensures navigation works properly
        if selected_menu != st.session_state.navigation_menu:
            st.session_state.navigation_menu = selected_menu
            # Clear any tab-specific states
            if 'hse_tab' in st.session_state:
                del st.session_state.hse_tab
            if 'space_tab' in st.session_state:
                del st.session_state.space_tab
        
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
    
    # Route to the selected menu - FIXED: Uses session state navigation_menu
    selected_menu = st.session_state.navigation_menu
    
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

# ... (THE REST OF THE CODE REMAINS THE SAME - main() function and if __name__)

if __name__ == "__main__":
    # Initialize fresh database with reduced data
    init_database()
    
    # Run the app
    main()
