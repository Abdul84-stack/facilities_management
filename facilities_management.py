# ========== SPACE MANAGEMENT ==========

def show_space_management():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🏢 Space Management System")
    st.markdown('</div>', unsafe_allow_html=True)
    
    user_role = st.session_state.user['role']
    
    tab1, tab2, tab3, tab4 = st.tabs(["📅 Room Bookings", "➕ New Booking", "📋 Booking Calendar", "⚙️ Room Management"])
    
    with tab1:
        st.subheader("📅 Current Bookings")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            room_type_filter = st.selectbox("Room Type", ["All", "Conference", "Meeting", "Cafeteria", "Training"], key="room_type_filter")
        with col2:
            status_filter = st.selectbox("Status", ["All", "Confirmed", "Pending", "Cancelled"], key="booking_status_filter")
        with col3:
            date_filter = st.date_input("Booking Date", value=datetime.now().date(), key="booking_date_filter")
        
        # Get filtered bookings
        filters = {}
        if room_type_filter != "All":
            filters['room_type'] = room_type_filter
        if status_filter != "All":
            filters['status'] = status_filter
        if date_filter:
            filters['booking_date'] = date_filter
        
        bookings = get_space_bookings(filters)
        
        if not bookings:
            st.info("📭 No bookings found matching your criteria")
        else:
            for booking in bookings[:10]:  # Limit to 10 for performance
                with st.expander(f"{booking['room_name']} - {booking['booking_date']} ({booking['start_time']} to {booking['end_time']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Purpose:** {booking['purpose']}")
                        st.write(f"**Booked By:** {booking['booked_by']}")
                        st.write(f"**Department:** {booking['department']}")
                        st.write(f"**Attendees:** {booking['attendees_count']}")
                    
                    with col2:
                        status_class = f"booking-{booking['status'].lower()}"
                        st.markdown(f'<div class="{status_class}">{booking["status"]}</div>', unsafe_allow_html=True)
                        
                        if booking.get('catering_required'):
                            st.write("🍽️ **Catering:** Required")
                        if booking.get('special_requirements'):
                            st.write(f"📋 **Special Requirements:** {booking['special_requirements']}")
                    
                    # Action buttons for managers and space managers
                    if user_role in ['facility_manager', 'space_manager']:
                        col_act1, col_act2 = st.columns(2)
                        with col_act1:
                            if booking['status'] != 'Confirmed':
                                if st.button("✅ Confirm Booking", key=f"confirm_{booking['id']}"):
                                    if update_booking_status(booking['id'], 'Confirmed'):
                                        st.success("✅ Booking confirmed!")
                                        st.rerun()
                        with col_act2:
                            if booking['status'] != 'Cancelled':
                                if st.button("❌ Cancel Booking", key=f"cancel_{booking['id']}"):
                                    if update_booking_status(booking['id'], 'Cancelled'):
                                        st.success("⚠️ Booking cancelled!")
                                        st.rerun()
    
    with tab2:
        st.subheader("➕ Create New Booking")
        
        with st.form("new_booking_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                room_name = st.selectbox("Room Name *", 
                    ["Conference Room A", "Conference Room B", "Meeting Room 1", 
                     "Meeting Room 2", "Training Room", "Cafeteria", "Auditorium"], 
                    key="new_room_name")
                room_type = st.selectbox("Room Type *", 
                    ["Conference", "Meeting", "Training", "Cafeteria", "Auditorium"], 
                    key="new_room_type")
                booking_date = st.date_input("Booking Date *", 
                    value=datetime.now().date(), 
                    key="new_booking_date")
                start_time = st.time_input("Start Time *", 
                    value=datetime.strptime("09:00", "%H:%M"), 
                    key="new_start_time")
            
            with col2:
                end_time = st.time_input("End Time *", 
                    value=datetime.strptime("10:00", "%H:%M"), 
                    key="new_end_time")
                purpose = st.text_input("Purpose *", 
                    placeholder="Meeting purpose/agenda", 
                    key="new_purpose")
                department = st.selectbox("Department *", 
                    ["Management", "HR", "Finance", "Operations", "IT", "All"], 
                    key="new_department")
                attendees_count = st.number_input("Number of Attendees *", 
                    min_value=1, max_value=500, value=10, 
                    key="new_attendees")
            
            # Additional options
            st.markdown('<div class="card">', unsafe_allow_html=True)
            col_opt1, col_opt2 = st.columns(2)
            with col_opt1:
                catering_required = st.checkbox("Catering Required", key="new_catering")
            with col_opt2:
                special_requirements = st.text_area("Special Requirements", 
                    placeholder="Audio/visual equipment, whiteboard, etc.", 
                    key="new_special_req")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Check availability
            if room_name and booking_date and start_time and end_time:
                is_available = check_room_availability(room_name, booking_date, 
                                                      start_time.strftime("%H:%M"), 
                                                      end_time.strftime("%H:%M"))
                
                if not is_available:
                    st.error("❌ Room is already booked during this time slot")
                else:
                    st.success("✅ Room is available!")
            
            submitted = st.form_submit_button("📅 Book Room", use_container_width=True)
            
            if submitted:
                if not all([room_name, room_type, booking_date, start_time, end_time, purpose, department]):
                    st.error("⚠️ Please fill in all required fields (*)")
                elif end_time <= start_time:
                    st.error("❌ End time must be after start time")
                elif not is_available:
                    st.error("❌ Room is not available during selected time")
                else:
                    success = add_space_booking(
                        room_name, room_type, booking_date,
                        start_time.strftime("%H:%M"), end_time.strftime("%H:%M"),
                        purpose, st.session_state.user['username'],
                        department, attendees_count,
                        catering_required, special_requirements
                    )
                    
                    if success:
                        st.success("✅ Booking created successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to create booking")
    
    with tab3:
        st.subheader("📅 Booking Calendar View")
        
        # Show today's bookings in a timeline
        today = datetime.now().date()
        todays_bookings = [b for b in bookings if b.get('booking_date') == today.isoformat()]
        
        if todays_bookings:
            # Create a timeline visualization
            for booking in todays_bookings:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{booking['room_name']}**")
                    st.write(f"*{booking['purpose']}*")
                with col2:
                    st.write(f"**{booking['start_time']} - {booking['end_time']}**")
                with col3:
                    status_class = f"booking-{booking['status'].lower()}"
                    st.markdown(f'<div class="{status_class}">{booking["status"]}</div>', unsafe_allow_html=True)
                st.markdown('---')
        else:
            st.info("📭 No bookings scheduled for today")
    
    with tab4:
        if user_role in ['facility_manager', 'space_manager']:
            st.subheader("⚙️ Room Management")
            
            # Room configuration
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write("**Available Rooms Configuration**")
            
            room_data = [
                {"Room": "Conference Room A", "Type": "Conference", "Capacity": 20, "Amenities": "Projector, Whiteboard"},
                {"Room": "Conference Room B", "Type": "Conference", "Capacity": 15, "Amenities": "TV Screen, Whiteboard"},
                {"Room": "Meeting Room 1", "Type": "Meeting", "Capacity": 8, "Amenities": "Whiteboard"},
                {"Room": "Meeting Room 2", "Type": "Meeting", "Capacity": 6, "Amenities": "Whiteboard"},
                {"Room": "Training Room", "Type": "Training", "Capacity": 30, "Amenities": "Projector, Sound System"},
                {"Room": "Cafeteria", "Type": "Cafeteria", "Capacity": 100, "Amenities": "Kitchen, Sound System"},
                {"Room": "Auditorium", "Type": "Auditorium", "Capacity": 200, "Amenities": "Stage, Full AV System"}
            ]
            
            st.dataframe(pd.DataFrame(room_data), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Add new room option
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write("**Add New Room**")
            
            with st.form("add_room_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_room_name = st.text_input("Room Name", key="new_room")
                    new_room_type = st.selectbox("Room Type", ["Conference", "Meeting", "Training", "Cafeteria", "Auditorium"], key="new_room_type_admin")
                with col2:
                    new_capacity = st.number_input("Capacity", min_value=1, max_value=500, value=10, key="new_capacity")
                    new_amenities = st.text_input("Amenities", placeholder="Separate with commas", key="new_amenities")
                
                if st.form_submit_button("➕ Add Room", use_container_width=True):
                    st.success("✅ Room added to configuration (Note: This is a demo. In production, this would update the database.)")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("🔒 Room management features are only available to facility managers and space managers")

# ========== HSE MANAGEMENT ==========

def show_hse_management():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🚨 Health, Safety & Environment Management")
    st.markdown('</div>', unsafe_allow_html=True)
    
    user_role = st.session_state.user['role']
    
    tab1, tab2, tab3, tab4 = st.tabs(["📅 Inspection Schedule", "➕ New Incident", "📋 Incident Reports", "📊 Compliance Dashboard"])
    
    with tab1:
        st.subheader("📅 HSE Inspection Schedule")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox("Filter by Status", ["All", "Upcoming", "Due", "Completed"], key="hse_status_filter")
        with col2:
            compliance_filter = st.selectbox("Filter by Compliance", ["All", "Compliant", "Non-Compliant"], key="hse_compliance_filter")
        
        # Get filtered schedule
        filters = {}
        if status_filter != "All":
            filters['status'] = status_filter
        if compliance_filter != "All":
            filters['compliance_level'] = compliance_filter
        
        hse_schedule = get_hse_schedule(filters)
        
        if not hse_schedule:
            st.info("📭 No HSE inspections found")
        else:
            for inspection in hse_schedule[:10]:  # Limit to 10
                with st.expander(f"{inspection['inspection_type']} - {inspection['area']} (Due: {inspection['next_inspection_date']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Area:** {inspection['area']}")
                        st.write(f"**Frequency:** {inspection['frequency']}")
                        st.write(f"**Assigned To:** {inspection['assigned_to']}")
                        st.write(f"**Last Inspection:** {inspection.get('last_inspection_date', 'Never')}")
                        
                        status = inspection.get('status', 'Upcoming')
                        if status == 'Completed':
                            st.success(f"✅ Status: {status}")
                        elif status == 'Due':
                            st.error(f"⚠️ Status: {status}")
                        else:
                            st.info(f"📅 Status: {status}")
                    
                    with col2:
                        compliance = inspection.get('compliance_level', 'Compliant')
                        compliance_class = "hse-compliant" if compliance == 'Compliant' else "hse-non-compliant"
                        st.markdown(f'<div class="{compliance_class}">Compliance: {compliance}</div>', unsafe_allow_html=True)
                        
                        if inspection.get('findings'):
                            st.write(f"**Findings:** {inspection['findings']}")
                        if inspection.get('corrective_actions'):
                            st.write(f"**Corrective Actions:** {inspection['corrective_actions']}")
                        if inspection.get('follow_up_date'):
                            st.write(f"**Follow-up Date:** {inspection['follow_up_date']}")
                    
                    # Action buttons for HSE officers and managers
                    if user_role in ['hse_officer', 'facility_manager'] and inspection['status'] != 'Completed':
                        st.markdown("---")
                        st.subheader("📝 Record Inspection Results")
                        
                        with st.form(f"inspection_form_{inspection['id']}"):
                            compliance = st.selectbox("Compliance Level", 
                                ["Compliant", "Non-Compliant"], 
                                key=f"comp_{inspection['id']}")
                            findings = st.text_area("Findings/Observations", 
                                key=f"findings_{inspection['id']}")
                            corrective_actions = st.text_area("Corrective Actions Taken", 
                                key=f"actions_{inspection['id']}")
                            follow_up_date = st.date_input("Follow-up Date (if needed)", 
                                value=datetime.now().date() + timedelta(days=30),
                                key=f"followup_{inspection['id']}")
                            
                            if st.form_submit_button("✅ Complete Inspection", use_container_width=True):
                                if update_hse_inspection(inspection['id'], compliance, findings, 
                                                        corrective_actions, follow_up_date):
                                    st.success("✅ Inspection completed!")
                                    st.rerun()
        
        # Add new inspection schedule (HSE officers and managers only)
        if user_role in ['hse_officer', 'facility_manager']:
            st.markdown("---")
            st.subheader("➕ Schedule New Inspection")
            
            with st.form("new_inspection_form"):
                col1, col2 = st.columns(2)
                with col1:
                    inspection_type = st.text_input("Inspection Type *", 
                        placeholder="Fire Safety, First Aid, Electrical Safety", 
                        key="new_inspection_type")
                    area = st.text_input("Area *", 
                        placeholder="Main Building, Generator Room, All Floors", 
                        key="new_inspection_area")
                with col2:
                    frequency = st.selectbox("Frequency *", 
                        ["Daily", "Weekly", "Monthly", "Quarterly", "Annual"], 
                        key="new_inspection_freq")
                    next_date = st.date_input("Next Inspection Date *", 
                        value=datetime.now().date() + timedelta(days=7), 
                        key="new_inspection_date")
                
                if st.form_submit_button("📅 Schedule Inspection", use_container_width=True):
                    if not all([inspection_type, area, frequency, next_date]):
                        st.error("⚠️ Please fill in all required fields (*)")
                    else:
                        success = add_hse_schedule(inspection_type, area, frequency, 
                                                  next_date, st.session_state.user['username'])
                        if success:
                            st.success("✅ Inspection scheduled!")
                            st.rerun()
    
    with tab2:
        st.subheader("🚨 Report New Incident")
        
        with st.form("new_incident_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                incident_date = st.date_input("Incident Date *", 
                    value=datetime.now().date(), 
                    key="new_incident_date")
                incident_time = st.time_input("Incident Time *", 
                    value=datetime.now().time(), 
                    key="new_incident_time")
                location = st.text_input("Location *", 
                    placeholder="Where did it happen?", 
                    key="new_incident_location")
                incident_type = st.selectbox("Incident Type *", 
                    ["Near Miss", "First Aid Case", "Medical Treatment", "Lost Time", "Fatality"], 
                    key="new_incident_type")
            
            with col2:
                severity = st.selectbox("Severity Level *", 
                    ["Low", "Medium", "High", "Critical"], 
                    key="new_incident_severity")
                affected_persons = st.text_input("Affected Persons", 
                    placeholder="Names/roles of affected persons", 
                    key="new_affected_persons")
                reported_by = st.text_input("Reported By *", 
                    value=st.session_state.user['username'], 
                    key="new_incident_reporter")
            
            description = st.text_area("Incident Description *", 
                placeholder="Describe what happened in detail...", 
                height=150, 
                key="new_incident_desc")
            
            immediate_actions = st.text_area("Immediate Actions Taken", 
                placeholder="What immediate actions were taken?", 
                key="new_immediate_actions")
            
            submitted = st.form_submit_button("🚨 Report Incident", use_container_width=True)
            
            if submitted:
                if not all([incident_date, incident_time, location, incident_type, 
                           severity, description, reported_by]):
                    st.error("⚠️ Please fill in all required fields (*)")
                else:
                    success = add_hse_incident(incident_date, incident_time, location, 
                                              incident_type, severity, description,
                                              reported_by, affected_persons, 
                                              immediate_actions)
                    if success:
                        st.success("✅ Incident reported successfully!")
                        st.rerun()
    
    with tab3:
        st.subheader("📋 Incident Reports")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            severity_filter = st.selectbox("Severity", ["All", "Low", "Medium", "High", "Critical"], key="incident_severity_filter")
        with col2:
            status_filter = st.selectbox("Status", ["All", "Open", "Under Investigation", "Closed"], key="incident_status_filter")
        with col3:
            start_date = st.date_input("From Date", value=datetime.now().date() - timedelta(days=30), key="incident_start_date")
        
        # Get filtered incidents
        filters = {}
        if severity_filter != "All":
            filters['severity'] = severity_filter
        if status_filter != "All":
            filters['status'] = status_filter
        if start_date:
            filters['start_date'] = start_date
        
        incidents = get_hse_incidents(filters)
        
        if not incidents:
            st.info("📭 No incidents found")
        else:
            for incident in incidents[:10]:  # Limit to 10
                with st.expander(f"{incident['incident_type']} - {incident['location']} ({incident['incident_date']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Date & Time:** {incident['incident_date']} {incident['incident_time']}")
                        st.write(f"**Location:** {incident['location']}")
                        st.write(f"**Type:** {incident['incident_type']}")
                        st.write(f"**Reported By:** {incident['reported_by']}")
                        
                        # Color-code severity
                        severity = incident['severity']
                        if severity == 'Critical':
                            st.error(f"**Severity:** {severity}")
                        elif severity == 'High':
                            st.warning(f"**Severity:** {severity}")
                        elif severity == 'Medium':
                            st.info(f"**Severity:** {severity}")
                        else:
                            st.success(f"**Severity:** {severity}")
                    
                    with col2:
                        st.write(f"**Description:** {incident['description']}")
                        if incident.get('affected_persons'):
                            st.write(f"**Affected Persons:** {incident['affected_persons']}")
                        if incident.get('immediate_actions'):
                            st.write(f"**Immediate Actions:** {incident['immediate_actions']}")
                        
                        st.write(f"**Investigation Status:** {incident.get('investigation_status', 'Open')}")
                        st.write(f"**Incident Status:** {incident.get('status', 'Open')}")
                    
                    # Update incident status (HSE officers and managers only)
                    if user_role in ['hse_officer', 'facility_manager']:
                        st.markdown("---")
                        st.subheader("📝 Update Investigation")
                        
                        with st.form(f"update_incident_{incident['id']}"):
                            col_up1, col_up2 = st.columns(2)
                            with col_up1:
                                investigation_status = st.selectbox("Investigation Status", 
                                    ["Open", "Under Investigation", "Resolved"], 
                                    key=f"inv_stat_{incident['id']}")
                            with col_up2:
                                incident_status = st.selectbox("Incident Status", 
                                    ["Open", "Closed"], 
                                    key=f"inc_stat_{incident['id']}")
                            
                            corrective_measures = st.text_area("Corrective Measures Taken", 
                                key=f"corr_meas_{incident['id']}")
                            
                            if st.form_submit_button("💾 Update Incident", use_container_width=True):
                                success = update_incident_status(incident['id'], investigation_status, 
                                                                corrective_measures, incident_status)
                                if success:
                                    st.success("✅ Incident updated!")
                                    st.rerun()
    
    with tab4:
        st.subheader("📊 HSE Compliance Dashboard")
        
        # Get HSE data
        all_inspections = get_hse_schedule()
        all_incidents = get_hse_incidents()
        
        if all_inspections:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_inspections = len(all_inspections)
                st.metric("Total Inspections", total_inspections)
            
            with col2:
                completed = len([i for i in all_inspections if i.get('status') == 'Completed'])
                st.metric("Completed", completed)
            
            with col3:
                compliant = len([i for i in all_inspections if i.get('compliance_level') == 'Compliant'])
                compliance_rate = (compliant / completed * 100) if completed > 0 else 0
                st.metric("Compliance Rate", f"{compliance_rate:.1f}%")
            
            with col4:
                st.metric("Total Incidents", len(all_incidents))
            
            # Charts
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                if all_inspections:
                    status_counts = {}
                    for insp in all_inspections:
                        status = insp.get('status', 'Unknown')
                        status_counts[status] = status_counts.get(status, 0) + 1
                    
                    if status_counts:
                        fig = px.pie(values=list(status_counts.values()), 
                                    names=list(status_counts.keys()),
                                    title="Inspection Status Distribution",
                                    color_discrete_sequence=px.colors.sequential.RdBu)
                        st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col_chart2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                if all_incidents:
                    severity_counts = {}
                    for inc in all_incidents:
                        severity = inc.get('severity', 'Unknown')
                        severity_counts[severity] = severity_counts.get(severity, 0) + 1
                    
                    if severity_counts:
                        colors = {'Critical': '#FF0000', 'High': '#FF6B00', 
                                 'Medium': '#FFD700', 'Low': '#00FF00'}
                        color_list = [colors.get(sev, '#808080') for sev in severity_counts.keys()]
                        
                        fig = px.bar(x=list(severity_counts.values()), 
                                    y=list(severity_counts.keys()),
                                    title="Incidents by Severity",
                                    orientation='h',
                                    color=severity_counts.keys(),
                                    color_discrete_sequence=color_list)
                        st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Overdue inspections
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("⚠️ Overdue Inspections")
            
            today = datetime.now().date()
            overdue = [i for i in all_inspections 
                      if i.get('status') != 'Completed' 
                      and safe_date(i.get('next_inspection_date')) 
                      and safe_date(i.get('next_inspection_date')) < today]
            
            if overdue:
                for insp in overdue[:5]:
                    days_overdue = (today - safe_date(insp['next_inspection_date'])).days
                    st.warning(f"• **{insp['inspection_type']}** at {insp['area']} - {days_overdue} days overdue")
                
                if len(overdue) > 5:
                    st.write(f"... and {len(overdue) - 5} more")
            else:
                st.success("✅ No overdue inspections")
            st.markdown('</div>', unsafe_allow_html=True)

# ========== PREVENTIVE MAINTENANCE ==========

def show_preventive_maintenance():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🔧 Planned Preventive Maintenance")
    st.markdown('</div>', unsafe_allow_html=True)
    
    user_role = st.session_state.user['role']
    
    tab1, tab2, tab3 = st.tabs(["📅 Maintenance Schedule", "➕ New Schedule", "📈 Equipment Analytics"])
    
    with tab1:
        st.subheader("📅 Maintenance Schedule")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox("Status", ["All", "Upcoming", "Due", "Completed"], key="pm_status_filter")
        with col2:
            equipment_filter = st.selectbox("Equipment Type", ["All", "HVAC", "Generator", "Electrical", "Plumbing", "Fire Safety"], key="pm_equipment_filter")
        with col3:
            location_filter = st.selectbox("Location", ["All", "Main Building", "Generator Room", "All Floors", "Production Area"], key="pm_location_filter")
        
        # Get filtered maintenance
        filters = {}
        if status_filter != "All":
            filters['status'] = status_filter
        if equipment_filter != "All":
            filters['equipment_type'] = equipment_filter
        if location_filter != "All":
            filters['location'] = location_filter
        
        maintenance_list = get_preventive_maintenance(filters)
        
        if not maintenance_list:
            st.info("📭 No maintenance schedules found")
        else:
            for maintenance in maintenance_list[:10]:  # Limit to 10
                with st.expander(f"{maintenance['equipment_name']} - {maintenance['location']} (Due: {maintenance['next_maintenance_date']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Equipment Type:** {maintenance['equipment_type']}")
                        st.write(f"**Location:** {maintenance['location']}")
                        st.write(f"**Maintenance Type:** {maintenance['maintenance_type']}")
                        st.write(f"**Frequency:** {maintenance['frequency']}")
                        st.write(f"**Assigned To:** {maintenance['assigned_to']}")
                    
                    with col2:
                        st.write(f"**Last Maintenance:** {maintenance.get('last_maintenance_date', 'Never')}")
                        st.write(f"**Next Maintenance:** {maintenance['next_maintenance_date']}")
                        
                        status = maintenance.get('status', 'Upcoming')
                        if status == 'Completed':
                            st.success(f"✅ Status: {status}")
                            if maintenance.get('completion_notes'):
                                st.write(f"**Completion Notes:** {maintenance['completion_notes']}")
                        elif status == 'Due':
                            st.error(f"⚠️ Status: {status}")
                        else:
                            st.info(f"📅 Status: {status}")
                        
                        if maintenance.get('notes'):
                            st.write(f"**Notes:** {maintenance['notes']}")
                    
                    # Mark as completed (managers and vendors)
                    if user_role in ['facility_manager', 'vendor'] and maintenance['status'] != 'Completed':
                        st.markdown("---")
                        with st.form(f"complete_maintenance_{maintenance['id']}"):
                            completion_notes = st.text_area("Completion Notes", 
                                placeholder="Describe work done, parts replaced, etc.",
                                key=f"comp_notes_{maintenance['id']}")
                            
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.form_submit_button("✅ Mark as Completed", use_container_width=True):
                                    if update_preventive_maintenance(maintenance['id'], 'Completed', completion_notes):
                                        st.success("✅ Maintenance completed!")
                                        st.rerun()
                            with col_btn2:
                                if st.form_submit_button("📅 Reschedule", use_container_width=True):
                                    # For demo purposes
                                    st.info("Reschedule feature would be implemented here")
        
        # Add new maintenance schedule (managers only)
        if user_role in ['facility_manager']:
            st.markdown("---")
            st.subheader("➕ Schedule New Maintenance")
            
            with st.form("new_maintenance_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    equipment_name = st.text_input("Equipment Name *", 
                        placeholder="e.g., Main HVAC System, Generator #1", 
                        key="new_equipment_name")
                    equipment_type = st.selectbox("Equipment Type *", 
                        ["HVAC", "Generator", "Electrical", "Plumbing", "Fire Safety", "Other"], 
                        key="new_equipment_type")
                    location = st.text_input("Location *", 
                        placeholder="e.g., Main Building, Generator Room", 
                        key="new_maintenance_location")
                    maintenance_type = st.selectbox("Maintenance Type *", 
                        ["Routine Check", "Service", "Inspection", "Calibration", "Repair"], 
                        key="new_maintenance_type")
                
                with col2:
                    frequency = st.selectbox("Frequency *", 
                        ["Weekly", "Monthly", "Quarterly", "Biannual", "Annual", "200 hours", "500 hours"], 
                        key="new_maintenance_freq")
                    last_maintenance = st.date_input("Last Maintenance Date", 
                        value=datetime.now().date() - timedelta(days=30), 
                        key="new_last_maintenance")
                    next_maintenance = st.date_input("Next Maintenance Date *", 
                        value=datetime.now().date() + timedelta(days=30), 
                        key="new_next_maintenance")
                    assigned_to = st.text_input("Assigned To *", 
                        placeholder="Team or individual responsible", 
                        key="new_maintenance_assigned")
                
                notes = st.text_area("Notes", 
                    placeholder="Special instructions, parts needed, etc.", 
                    key="new_maintenance_notes")
                
                if st.form_submit_button("📅 Schedule Maintenance", use_container_width=True):
                    if not all([equipment_name, equipment_type, location, maintenance_type, 
                               frequency, next_maintenance, assigned_to]):
                        st.error("⚠️ Please fill in all required fields (*)")
                    else:
                        success = add_preventive_maintenance(
                            equipment_name, equipment_type, location, maintenance_type,
                            frequency, last_maintenance, next_maintenance, assigned_to, notes
                        )
                        if success:
                            st.success("✅ Maintenance scheduled!")
                            st.rerun()
    
    with tab2:
        st.subheader("📊 Equipment Analytics")
        
        # Get all maintenance data
        all_maintenance = get_preventive_maintenance()
        
        if all_maintenance:
            # Convert to DataFrame for analysis
            df_maintenance = pd.DataFrame(all_maintenance)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_equipment = len(df_maintenance['equipment_name'].unique())
                st.metric("Total Equipment", total_equipment)
            
            with col2:
                upcoming = len(df_maintenance[df_maintenance['status'] == 'Upcoming'])
                st.metric("Upcoming Maintenance", upcoming)
            
            with col3:
                due = len(df_maintenance[df_maintenance['status'] == 'Due'])
                st.metric("Due Maintenance", due)
            
            # Charts
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                if not df_maintenance.empty:
                    equipment_counts = df_maintenance['equipment_type'].value_counts()
                    fig = px.pie(values=equipment_counts.values, 
                                names=equipment_counts.index,
                                title="Equipment Type Distribution",
                                color_discrete_sequence=px.colors.sequential.Viridis)
                    st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col_chart2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                if not df_maintenance.empty:
                    location_counts = df_maintenance['location'].value_counts()
                    fig = px.bar(x=location_counts.values, y=location_counts.index,
                                title="Maintenance by Location",
                                orientation='h',
                                color=location_counts.values,
                                color_continuous_scale='Plasma')
                    st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Upcoming maintenance timeline
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("📅 Upcoming Maintenance Timeline")
            
            upcoming_maint = df_maintenance[df_maintenance['status'].isin(['Upcoming', 'Due'])]
            if not upcoming_maint.empty:
                # Sort by next maintenance date
                upcoming_maint['next_maintenance_date'] = pd.to_datetime(upcoming_maint['next_maintenance_date'])
                upcoming_maint = upcoming_maint.sort_values('next_maintenance_date')
                
                for _, row in upcoming_maint.head(10).iterrows():
                    days_until = (row['next_maintenance_date'] - pd.Timestamp(datetime.now().date())).days
                    
                    if days_until < 0:
                        status_text = f"⚠️ **{days_until} days overdue**"
                    elif days_until <= 7:
                        status_text = f"🔴 **Due in {days_until} days**"
                    elif days_until <= 14:
                        status_text = f"🟡 **Due in {days_until} days**"
                    else:
                        status_text = f"🟢 **Due in {days_until} days**"
                    
                    st.write(f"• **{row['equipment_name']}** ({row['equipment_type']}) at {row['location']} - {status_text}")
            else:
                st.success("✅ No upcoming maintenance scheduled")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("📭 No maintenance data available for analytics")

# ========== MAIN APPLICATION ROUTING ==========

def main():
    # Initialize session state
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    if 'navigation_menu' not in st.session_state:
        st.session_state.navigation_menu = "Dashboard"
    
    # Show login if not authenticated
    if not st.session_state.user:
        show_login()
        return
    
    # User is authenticated - show main application
    user = st.session_state.user
    role = user['role']
    username = user['username']
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"""
            <div style="text-align: center; padding: 20px 0;">
                <h3 style="color: white; margin-bottom: 5px;">🏢 FMS v3.0</h3>
                <p style="color: rgba(255,255,255,0.8); margin: 0;">
                    <strong>{username}</strong><br>
                    <small>{role.upper()}</small>
                </p>
            </div>
            <div class="separator"></div>
        """, unsafe_allow_html=True)
        
        # Navigation options based on role
        nav_options = ["Dashboard", "Job & Invoice Reports", "Reports & Analytics"]
        
        if role == 'facility_user':
            nav_options.extend(["Generator Records", "Space Management", "HSE Management"])
        
        elif role == 'facility_manager':
            nav_options.extend(["Preventive Maintenance", "Generator Records", 
                              "Space Management", "HSE Management"])
        
        elif role == 'hse_officer':
            nav_options.extend(["HSE Management", "Generator Records", "Space Management"])
        
        elif role == 'space_manager':
            nav_options.extend(["Space Management", "Generator Records"])
        
        elif role == 'vendor':
            vendor_type = user.get('vendor_type', 'General')
            nav_options.extend(["Generator Records"])
            if 'HSE' in vendor_type:
                nav_options.extend(["HSE Management"])
            if 'Space' in vendor_type:
                nav_options.extend(["Space Management"])
        
        # Navigation radio buttons with proper styling
        st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
        selected_menu = st.radio(
            "📌 NAVIGATION",
            nav_options,
            index=nav_options.index(st.session_state.navigation_menu) if st.session_state.navigation_menu in nav_options else 0,
            key="navigation_radio",
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Update session state
        if selected_menu != st.session_state.navigation_menu:
            st.session_state.navigation_menu = selected_menu
            st.rerun()
        
        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
        
        # Quick stats in sidebar
        if role in ['facility_manager', 'hse_officer', 'facility_user']:
            st.markdown('<div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 20px 0;">', unsafe_allow_html=True)
            st.markdown('<h4 style="color: white; margin-bottom: 15px;">📊 Quick Stats</h4>', unsafe_allow_html=True)
            
            if role == 'facility_manager':
                all_requests = get_all_requests()
                pending = len([r for r in all_requests if safe_get(r, 'status') == 'Pending'])
                st.markdown(f'<p style="color: white;">Pending Requests: <strong>{pending}</strong></p>', unsafe_allow_html=True)
            
            # Show today's bookings for space-related roles
            if role in ['facility_manager', 'space_manager', 'facility_user']:
                today = datetime.now().date().isoformat()
                bookings = get_space_bookings({'booking_date': today})
                todays_bookings = len([b for b in bookings if b.get('status') == 'Confirmed'])
                st.markdown(f'<p style="color: white;">Today\'s Bookings: <strong>{todays_bookings}</strong></p>', unsafe_allow_html=True)
            
            # Show overdue inspections for HSE roles
            if role in ['facility_manager', 'hse_officer']:
                hse_schedule = get_hse_schedule()
                today = datetime.now().date()
                overdue = len([i for i in hse_schedule 
                             if i.get('status') != 'Completed' 
                             and safe_date(i.get('next_inspection_date')) 
                             and safe_date(i.get('next_inspection_date')) < today])
                st.markdown(f'<p style="color: white;">Overdue Inspections: <strong style="color: #FF6B6B;">{overdue}</strong></p>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Logout button at bottom
        st.markdown('<div class="logout-container">', unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            st.session_state.user = None
            st.session_state.navigation_menu = "Dashboard"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content area based on selected menu
    if st.session_state.navigation_menu == "Dashboard":
        show_dashboard()
    
    elif st.session_state.navigation_menu == "Job & Invoice Reports":
        show_job_invoice_reports()
    
    elif st.session_state.navigation_menu == "Reports & Analytics":
        show_reports()
    
    elif st.session_state.navigation_menu == "Preventive Maintenance":
        show_preventive_maintenance()
    
    elif st.session_state.navigation_menu == "Generator Records":
        show_generator_diesel_records()
    
    elif st.session_state.navigation_menu == "Space Management":
        show_space_management()
    
    elif st.session_state.navigation_menu == "HSE Management":
        show_hse_management()
    
    # Footer
    st.markdown("""
        <div class="app-footer">
            FACILITIES MANAGEMENT SYSTEM™ v3.0 © 2024 | Currency: Nigerian Naira (₦) | Developed by Abdulahi Ibrahim
        </div>
    """, unsafe_allow_html=True)

# ========== RUN THE APPLICATION ==========

if __name__ == "__main__":
    main()
