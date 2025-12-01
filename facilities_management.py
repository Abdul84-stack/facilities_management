import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime
import base64
import io
import tempfile
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Page configuration with enhanced UI
st.set_page_config(
    page_title="Facilities Management System",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "### Facilities Management System v2.0\nDeveloped by Abdulahi Ibrahim\n© 2024 All Rights Reserved"
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
    </style>
""", unsafe_allow_html=True)

# Database setup with schema migration
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
    
    # Insert sample users
    sample_users = [
        ('facility_user', '0123456', 'facility_user', None),
        ('facility_manager', '0123456', 'facility_manager', None),
        ('hvac_vendor', '0123456', 'vendor', 'HVAC'),
        ('generator_vendor', '0123456', 'vendor', 'Generator'),
        ('fixture_vendor', '0123456', 'vendor', 'Fixture and Fittings'),
        ('building_vendor', '0123456', 'vendor', 'Building Maintenance'),
        ('hse_vendor', '0123456', 'vendor', 'HSE'),
        ('space_vendor', '0123456', 'vendor', 'Space Management')
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

# PDF Generation Functions
def generate_completion_report_pdf(job_data):
    """Generate PDF for job completion report"""
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
            fontSize=16,
            alignment=1,  # Center aligned
            spaceAfter=30
        )
        title = Paragraph("JOB COMPLETION REPORT", title_style)
        elements.append(title)
        
        # Separator
        elements.append(Spacer(1, 20))
        
        # Company Info
        company_style = ParagraphStyle(
            'CompanyInfo',
            parent=styles['Normal'],
            fontSize=10,
            alignment=1
        )
        company_info = Paragraph("Facilities Management System<br/>Generated on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"), company_style)
        elements.append(company_info)
        
        elements.append(Spacer(1, 30))
        
        # Job Details Section
        section_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=10
        )
        
        # Job Information
        section_title = Paragraph("Job Information", section_style)
        elements.append(section_title)
        
        # Create job details table
        job_details = [
            ["Job ID:", str(safe_get(job_data, 'id', 'N/A'))],
            ["Title:", safe_str(safe_get(job_data, 'title', 'N/A'))],
            ["Location:", safe_str(safe_get(job_data, 'location', 'Common Area'))],
            ["Facility Type:", safe_str(safe_get(job_data, 'facility_type', 'N/A'))],
            ["Priority:", safe_str(safe_get(job_data, 'priority', 'N/A'))],
            ["Status:", safe_str(safe_get(job_data, 'status', 'N/A'))],
            ["Created By:", safe_str(safe_get(job_data, 'created_by', 'N/A'))],
            ["Created Date:", safe_str(safe_get(job_data, 'created_date', 'N/A'))],
            ["Completed Date:", safe_str(safe_get(job_data, 'completed_date', 'N/A'))]
        ]
        
        if safe_get(job_data, 'assigned_vendor'):
            vendor_info = execute_query(
                'SELECT company_name FROM vendors WHERE username = ?',
                (safe_get(job_data, 'assigned_vendor'),)
            )
            vendor_name = vendor_info[0]['company_name'] if vendor_info else safe_get(job_data, 'assigned_vendor')
            job_details.append(["Assigned Vendor:", vendor_name])
        
        job_table = Table(job_details, colWidths=[150, 300])
        job_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        elements.append(job_table)
        
        elements.append(Spacer(1, 20))
        
        # Description
        if safe_get(job_data, 'description'):
            desc_title = Paragraph("Description", section_style)
            elements.append(desc_title)
            desc = Paragraph(safe_str(safe_get(job_data, 'description')), styles['Normal'])
            elements.append(desc)
            elements.append(Spacer(1, 10))
        
        # Job Breakdown
        if safe_get(job_data, 'job_breakdown'):
            breakdown_title = Paragraph("Job Breakdown", section_style)
            elements.append(breakdown_title)
            breakdown = Paragraph(safe_str(safe_get(job_data, 'job_breakdown')), styles['Normal'])
            elements.append(breakdown)
            elements.append(Spacer(1, 10))
        
        # Completion Notes
        if safe_get(job_data, 'completion_notes'):
            notes_title = Paragraph("Completion Notes", section_style)
            elements.append(notes_title)
            notes = Paragraph(safe_str(safe_get(job_data, 'completion_notes')), styles['Normal'])
            elements.append(notes)
            elements.append(Spacer(1, 20))
        
        # Financial Information
        if safe_get(job_data, 'invoice_amount'):
            financial_title = Paragraph("Financial Information", section_style)
            elements.append(financial_title)
            
            financial_details = [
                ["Invoice Amount:", format_naira(safe_get(job_data, 'invoice_amount'))],
                ["Invoice Number:", safe_str(safe_get(job_data, 'invoice_number', 'N/A'))]
            ]
            
            financial_table = Table(financial_details, colWidths=[150, 300])
            financial_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            elements.append(financial_table)
            elements.append(Spacer(1, 20))
        
        # Approval Status
        approval_title = Paragraph("Approval Status", section_style)
        elements.append(approval_title)
        
        approval_details = [
            ["Department Approval:", "✅ Approved" if safe_get(job_data, 'requesting_dept_approval') else "⏳ Pending"],
            ["Manager Approval:", "✅ Approved" if safe_get(job_data, 'facilities_manager_approval') else "⏳ Pending"]
        ]
        
        approval_table = Table(approval_details, colWidths=[150, 300])
        approval_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        elements.append(approval_table)
        
        # Footer
        elements.append(Spacer(1, 50))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            alignment=1,
            textColor=colors.grey
        )
        footer = Paragraph("Generated by Facilities Management System © 2024", footer_style)
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF bytes
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        st.error(f"Error generating PDF: {e}")
        return None

def generate_invoice_report_pdf(invoice_data, job_data=None):
    """Generate PDF for invoice report"""
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
                    © 2024 Facilities Management System™ | Developed by Abdulahi Ibrahim<br>
                    All trademarks and copyrights belong to their respective owners
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer at bottom of page
    st.markdown("""
        <div class="app-footer">
            FACILITIES MANAGEMENT SYSTEM™ © 2024 | Currency: Nigerian Naira (₦) | Developed by Abdulahi Ibrahim
        </div>
    """, unsafe_allow_html=True)

# Dashboard Functions
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
                    # Force a rerun to clear the form
                    st.rerun()
                else:
                    st.error("❌ Failed to create request")

def show_my_requests():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("📋 My Maintenance Requests")
    st.markdown('</div>', unsafe_allow_html=True)
    
    user_requests = get_user_requests(st.session_state.user['username'])
    
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
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        status_options = ["All"] + list(df['Status'].unique())
        status_filter = st.selectbox("Filter by Status", status_options, key="status_filter")
    with col2:
        priority_options = ["All"] + list(df['Priority'].unique())
        priority_filter = st.selectbox("Filter by Priority", priority_options, key="priority_filter")
    with col3:
        facility_options = ["All"] + list(df['Facility'].unique())
        facility_filter = st.selectbox("Filter by Facility Type", facility_options, key="facility_filter")
    with col4:
        location_options = ["All"] + list(df['Location'].unique())
        location_filter = st.selectbox("Filter by Location", location_options, key="location_filter")
    
    filtered_df = df
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['Status'] == status_filter]
    if priority_filter != "All":
        filtered_df = filtered_df[filtered_df['Priority'] == priority_filter]
    if facility_filter != "All":
        filtered_df = filtered_df[filtered_df['Facility'] == facility_filter]
    if location_filter != "All":
        filtered_df = filtered_df[filtered_df['Location'] == location_filter]
    
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    st.subheader("📄 Request Details")
    selected_id = st.selectbox("Select Request to View Details", [""] + [str(safe_get(req, 'id')) for req in user_requests], key="request_select")
    
    if selected_id:
        request = next((r for r in user_requests if str(safe_get(r, 'id')) == selected_id), None)
        if request:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.write("**📋 Basic Information**")
                st.write(f"**Title:** {safe_str(safe_get(request, 'title'), 'N/A')}")
                st.write(f"**Description:** {safe_str(safe_get(request, 'description'), 'N/A')}")
                st.write(f"**Location:** {safe_str(safe_get(request, 'location'), 'Common Area')}")
                st.write(f"**Facility Type:** {safe_str(safe_get(request, 'facility_type'), 'N/A')}")
                st.write(f"**Priority:** {safe_str(safe_get(request, 'priority'), 'N/A')}")
                st.write(f"**Status:** {safe_str(safe_get(request, 'status'), 'N/A')}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.write("**📊 Additional Information**")
                st.write(f"**Created Date:** {safe_str(safe_get(request, 'created_date'), 'N/A')}")
                if safe_get(request, 'assigned_vendor'):
                    vendor_info = execute_query(
                        'SELECT company_name FROM vendors WHERE username = ?',
                        (safe_get(request, 'assigned_vendor'),)
                    )
                    vendor_name = vendor_info[0]['company_name'] if vendor_info else safe_get(request, 'assigned_vendor')
                    st.write(f"**Assigned Vendor:** {vendor_name}")
                if safe_get(request, 'completion_notes'):
                    st.write(f"**Completion Notes:** {safe_str(safe_get(request, 'completion_notes'))}")
                if safe_get(request, 'job_breakdown'):
                    st.write(f"**Job Breakdown:** {safe_str(safe_get(request, 'job_breakdown'))}")
                if safe_get(request, 'invoice_amount'):
                    st.write(f"**Invoice Amount:** {format_naira(safe_get(request, 'invoice_amount'))}")
                    st.write(f"**Invoice Number:** {safe_str(safe_get(request, 'invoice_number'), 'N/A')}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            if (safe_get(request, 'status') == 'Completed' and 
                not safe_get(request, 'requesting_dept_approval') and
                safe_get(request, 'created_by') == st.session_state.user['username']):
                
                st.markdown('<div class="card">', unsafe_allow_html=True)
                if st.button("✅ Approve (Department)", use_container_width=True, key=f"approve_{safe_get(request, 'id')}"):
                    if execute_update(
                        'UPDATE maintenance_requests SET requesting_dept_approval = 1 WHERE id = ?',
                        (safe_get(request, 'id'),)
                    ):
                        st.success("✅ Department approval granted!")
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

def show_manage_requests():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🛠️ Manage Maintenance Requests")
    st.markdown('</div>', unsafe_allow_html=True)
    
    all_requests = get_all_requests()
    
    if not all_requests:
        st.info("📭 No maintenance requests found")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        status_options = ["All"] + ["Pending", "Assigned", "Completed", "Approved"]
        status_filter = st.selectbox("Filter by Status", status_options, key="mgr_status")
    with col2:
        priority_options = ["All"] + ["Low", "Medium", "High", "Critical"]
        priority_filter = st.selectbox("Filter by Priority", priority_options, key="mgr_priority")
    with col3:
        facility_types = list(set(safe_str(req.get('facility_type')) for req in all_requests))
        facility_options = ["All"] + facility_types
        facility_filter = st.selectbox("Filter by Facility Type", facility_options, key="mgr_facility")
    with col4:
        locations = list(set(safe_str(req.get('location'), 'Common Area') for req in all_requests))
        location_options = ["All"] + locations
        location_filter = st.selectbox("Filter by Location", location_options, key="mgr_location")
    
    filtered_requests = all_requests
    if status_filter != "All":
        filtered_requests = [req for req in filtered_requests if safe_str(req.get('status')) == status_filter]
    if priority_filter != "All":
        filtered_requests = [req for req in filtered_requests if safe_str(req.get('priority')) == priority_filter]
    if facility_filter != "All":
        filtered_requests = [req for req in filtered_requests if safe_str(req.get('facility_type')) == facility_filter]
    if location_filter != "All":
        filtered_requests = [req for req in filtered_requests if safe_str(req.get('location'), 'Common Area') == location_filter]
    
    st.subheader(f"📊 Showing {len(filtered_requests)} request(s)")
    
    for request in filtered_requests:
        with st.expander(f"Request #{safe_get(request, 'id')}: {safe_str(safe_get(request, 'title'), 'N/A')} - {safe_str(safe_get(request, 'status'), 'N/A')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.write("**📋 Basic Information**")
                st.write(f"**Title:** {safe_str(safe_get(request, 'title'), 'N/A')}")
                st.write(f"**Description:** {safe_str(safe_get(request, 'description'), 'N/A')}")
                st.write(f"**Location:** {safe_str(safe_get(request, 'location'), 'Common Area')}")
                st.write(f"**Facility Type:** {safe_str(safe_get(request, 'facility_type'), 'N/A')}")
                st.write(f"**Priority:** {safe_str(safe_get(request, 'priority'), 'N/A')}")
                st.write(f"**Status:** {safe_str(safe_get(request, 'status'), 'N/A')}")
                st.write(f"**Created By:** {safe_str(safe_get(request, 'created_by'), 'N/A')}")
                st.write(f"**Created Date:** {safe_str(safe_get(request, 'created_date'), 'N/A')}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.write("**🛠️ Management Actions**")
                
                if safe_get(request, 'status') == 'Pending':
                    st.subheader("👥 Assign to Vendor")
                    
                    facility_type = safe_str(safe_get(request, 'facility_type'))
                    
                    facility_to_vendor_map = {
                        "HVAC (Cooling Systems)": "HVAC",
                        "Generator Maintenance": "Generator",
                        "Fixture and Fittings": "Fixture and Fittings",
                        "Building Maintenance": "Building Maintenance",
                        "HSE": "HSE",
                        "Space Management": "Space Management"
                    }
                    
                    vendor_type = facility_to_vendor_map.get(facility_type, facility_type)
                    
                    vendors = execute_query('''
                        SELECT v.*, u.username 
                        FROM vendors v 
                        JOIN users u ON v.username = u.username 
                        WHERE u.vendor_type = ? OR v.vendor_type = ?
                    ''', (vendor_type, vendor_type))
                    
                    if vendors:
                        vendor_options = {f"{vendor['company_name']} ({vendor['username']})": vendor['username'] for vendor in vendors}
                        selected_vendor_key = st.selectbox(
                            f"Select vendor for {facility_type}",
                            options=list(vendor_options.keys()),
                            key=f"vendor_{safe_get(request, 'id')}"
                        )
                        
                        if selected_vendor_key:
                            selected_vendor = vendor_options[selected_vendor_key]
                            
                            if st.button(f"👥 Assign to {selected_vendor}", key=f"assign_{safe_get(request, 'id')}"):
                                if execute_update(
                                    'UPDATE maintenance_requests SET status = ?, assigned_vendor = ? WHERE id = ?',
                                    ('Assigned', selected_vendor, safe_get(request, 'id'))
                                ):
                                    st.success(f"✅ Request assigned to {selected_vendor}!")
                                    st.rerun()
                    else:
                        st.warning(f"⚠️ No registered vendors found for {facility_type}")
                
                elif safe_get(request, 'status') == 'Completed':
                    st.subheader("✅ Manager Approval")
                    
                    if safe_get(request, 'requesting_dept_approval'):
                        st.success("✅ Department approval received")
                        
                        if not safe_get(request, 'facilities_manager_approval'):
                            if st.button("✅ Approve as Facilities Manager", key=f"approve_{safe_get(request, 'id')}"):
                                if execute_update(
                                    'UPDATE maintenance_requests SET status = ?, facilities_manager_approval = ? WHERE id = ?',
                                    ('Approved', True, safe_get(request, 'id'))
                                ):
                                    st.success("✅ Facilities manager approval granted!")
                                    st.rerun()
                        else:
                            st.success("✅ Facilities manager approval granted")
                    else:
                        st.warning("⏳ Waiting for department approval")
                
                if safe_get(request, 'assigned_vendor'):
                    vendor_info = execute_query(
                        'SELECT company_name FROM vendors WHERE username = ?',
                        (safe_get(request, 'assigned_vendor'),)
                    )
                    vendor_name = vendor_info[0]['company_name'] if vendor_info else safe_get(request, 'assigned_vendor')
                    st.write(f"**👥 Assigned Vendor:** {vendor_name}")
                
                if safe_get(request, 'completion_notes'):
                    st.write(f"**📝 Completion Notes:** {safe_str(safe_get(request, 'completion_notes'))}")
                
                if safe_get(request, 'job_breakdown'):
                    st.write(f"**🔧 Job Breakdown:** {safe_str(safe_get(request, 'job_breakdown'))}")
                
                if safe_get(request, 'completed_date'):
                    st.write(f"**📅 Completed Date:** {safe_str(safe_get(request, 'completed_date'))}")
                
                if safe_get(request, 'invoice_amount'):
                    st.write(f"**💰 Invoice Amount:** {format_naira(safe_get(request, 'invoice_amount'))}")
                
                if safe_get(request, 'invoice_number'):
                    st.write(f"**🔢 Invoice Number:** {safe_str(safe_get(request, 'invoice_number'))}")
                st.markdown('</div>', unsafe_allow_html=True)

def show_vendor_management():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("👥 Vendor Management")
    st.markdown('</div>', unsafe_allow_html=True)
    
    vendors = execute_query('SELECT * FROM vendors ORDER BY company_name')
    
    if not vendors:
        st.info("📭 No vendors registered yet")
        return
    
    st.subheader(f"📊 Registered Vendors ({len(vendors)})")
    
    for vendor in vendors:
        with st.expander(f"{safe_str(safe_get(vendor, 'company_name'))} - {safe_str(safe_get(vendor, 'vendor_type'))}"):
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
                st.write(f"**Username:** {safe_str(safe_get(vendor, 'username'), 'N/A')}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            vendor_requests = execute_query(
                'SELECT * FROM maintenance_requests WHERE assigned_vendor = ?',
                (safe_get(vendor, 'username'),)
            )
            
            if vendor_requests:
                total_jobs = len(vendor_requests)
                completed_jobs = len([r for r in vendor_requests if safe_get(r, 'status') == 'Completed'])
                completion_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
                
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.write("**📊 Performance Statistics**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.markdown('<h4>Total Jobs</h4>', unsafe_allow_html=True)
                    st.markdown(f'<h3>{total_jobs}</h3>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.markdown('<h4>Completed Jobs</h4>', unsafe_allow_html=True)
                    st.markdown(f'<h3>{completed_jobs}</h3>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                with col3:
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.markdown('<h4>Completion Rate</h4>', unsafe_allow_html=True)
                    st.markdown(f'<h3>{completion_rate:.1f}%</h3>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

def show_reports():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("📈 Reports & Analytics")
    st.markdown('</div>', unsafe_allow_html=True)
    
    all_requests = get_all_requests()
    
    if not all_requests:
        st.info("📭 No data available for reports")
        return
    
    report_data = []
    for req in all_requests:
        report_data.append({
            'id': safe_get(req, 'id'),
            'title': safe_str(safe_get(req, 'title'), 'N/A'),
            'location': safe_str(safe_get(req, 'location'), 'Common Area'),
            'facility_type': safe_str(safe_get(req, 'facility_type'), 'N/A'),
            'priority': safe_str(safe_get(req, 'priority'), 'N/A'),
            'status': safe_str(safe_get(req, 'status'), 'N/A'),
            'created_by': safe_str(safe_get(req, 'created_by'), 'N/A'),
            'assigned_vendor': safe_str(safe_get(req, 'assigned_vendor'), 'Not assigned'),
            'created_date': safe_str(safe_get(req, 'created_date'), 'N/A'),
            'completed_date': safe_str(safe_get(req, 'completed_date'), ''),
            'invoice_amount': safe_float(safe_get(req, 'invoice_amount'))
        })
    
    df = pd.DataFrame(report_data)
    
    if not df.empty:
        df['created_date'] = pd.to_datetime(df['created_date'], errors='coerce')
        df['completed_date'] = pd.to_datetime(df['completed_date'], errors='coerce')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_requests = len(df)
        st.markdown(f'<div class="metric-card"><h4>Total Requests</h4><h3>{total_requests}</h3></div>', unsafe_allow_html=True)
    
    with col2:
        completed_requests = len(df[df['status'] == 'Completed'])
        st.markdown(f'<div class="metric-card"><h4>Completed</h4><h3>{completed_requests}</h3></div>', unsafe_allow_html=True)
    
    with col3:
        pending_requests = len(df[df['status'] == 'Pending'])
        st.markdown(f'<div class="metric-card"><h4>Pending</h4><h3>{pending_requests}</h3></div>', unsafe_allow_html=True)
    
    with col4:
        total_invoice_amount = df['invoice_amount'].sum()
        st.markdown(f'<div class="metric-card"><h4>Total Invoice Amount</h4><h3 class="currency-naira">{format_naira(total_invoice_amount)}</h3></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if not df.empty:
            status_counts = df['status'].value_counts()
            fig = px.pie(values=status_counts.values, names=status_counts.index, 
                        title="📊 Request Status Distribution")
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if not df.empty:
            priority_counts = df['priority'].value_counts()
            fig = px.bar(x=priority_counts.index, y=priority_counts.values,
                        title="🚨 Requests by Priority", labels={'x': 'Priority', 'y': 'Count'})
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if not df.empty:
            facility_counts = df['facility_type'].value_counts()
            fig = px.bar(y=facility_counts.index, x=facility_counts.values,
                        title="🏢 Requests by Facility Type", orientation='h',
                        labels={'x': 'Count', 'y': 'Facility Type'})
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        if not df.empty:
            location_counts = df['location'].value_counts().head(10)
            fig = px.bar(y=location_counts.index, x=location_counts.values,
                        title="📍 Top 10 Locations", orientation='h',
                        labels={'x': 'Count', 'y': 'Location'})
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📅 Monthly Trends")
    if not df.empty and 'created_date' in df.columns:
        df['month'] = df['created_date'].dt.to_period('M')
        monthly_trends = df.groupby('month').size().reset_index(name='count')
        monthly_trends['month'] = monthly_trends['month'].astype(str)
        
        fig = px.line(monthly_trends, x='month', y='count', 
                     title="📈 Monthly Request Trends", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("👥 Vendor Performance")
    vendor_stats = df[df['assigned_vendor'] != 'Not assigned'].groupby('assigned_vendor').agg({
        'id': 'count',
        'status': lambda x: (x == 'Completed').sum()
    }).rename(columns={'id': 'total_jobs', 'status': 'completed_jobs'})
    
    if not vendor_stats.empty:
        vendor_stats['completion_rate'] = (vendor_stats['completed_jobs'] / vendor_stats['total_jobs'] * 100).round(2)
        st.dataframe(vendor_stats, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    st.subheader("📤 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export to CSV", use_container_width=True, key="export_csv"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"facilities_management_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key="download_csv"
            )
    
    with col2:
        if st.button("📄 Export to PDF", use_container_width=True, key="export_pdf"):
            # Generate a summary PDF report
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            
            # Add content to PDF
            c.setFont("Helvetica-Bold", 16)
            c.drawString(100, 750, "Facilities Management System - Report")
            
            c.setFont("Helvetica", 12)
            c.drawString(100, 730, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            c.drawString(100, 710, f"Total Requests: {len(df)}")
            c.drawString(100, 690, f"Completed: {len(df[df['status'] == 'Completed'])}")
            c.drawString(100, 670, f"Pending: {len(df[df['status'] == 'Pending'])}")
            c.drawString(100, 650, f"Total Invoice Amount: {format_naira(df['invoice_amount'].sum())}")
            
            # Add summary table
            y_position = 600
            c.setFont("Helvetica-Bold", 10)
            c.drawString(100, y_position, "Summary by Status:")
            y_position -= 20
            
            c.setFont("Helvetica", 10)
            status_summary = df['status'].value_counts()
            for status, count in status_summary.items():
                c.drawString(120, y_position, f"{status}: {count}")
                y_position -= 15
            
            c.showPage()
            c.save()
            
            buffer.seek(0)
            st.download_button(
                label="⬇️ Download PDF Report",
                data=buffer,
                file_name=f"facilities_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                key="download_pdf"
            )

def show_assigned_jobs():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("🔧 Assigned Jobs")
    st.markdown('</div>', unsafe_allow_html=True)
    
    vendor_requests = get_vendor_requests(st.session_state.user['username'])
    assigned_jobs = [r for r in vendor_requests if safe_get(r, 'status') == 'Assigned']
    
    if not assigned_jobs:
        st.success("🎉 No assigned jobs found - all caught up!")
        return
    
    st.subheader(f"📊 You have {len(assigned_jobs)} assigned job(s)")
    
    for job in assigned_jobs:
        with st.expander(f"Job #{safe_get(job, 'id')}: {safe_str(safe_get(job, 'title'), 'N/A')} - {safe_str(safe_get(job, 'priority'), 'N/A')} Priority"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.write(f"**📍 Location:** {safe_str(safe_get(job, 'location'), 'Common Area')}")
                st.write(f"**🏢 Facility Type:** {safe_str(safe_get(job, 'facility_type'), 'N/A')}")
                st.write(f"**📄 Description:** {safe_str(safe_get(job, 'description'), 'N/A')}")
                st.write(f"**👤 Created By:** {safe_str(safe_get(job, 'created_by'), 'N/A')}")
                st.write(f"**📅 Created Date:** {safe_str(safe_get(job, 'created_date'), 'N/A')}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.subheader("✅ Complete Job")
                with st.form(f"complete_job_{safe_get(job, 'id')}", clear_on_submit=True):
                    completion_notes = st.text_area("📝 Completion Notes")
                    job_breakdown = st.text_area("🔧 Breakdown of Job Done", height=100, 
                                               placeholder="Provide detailed breakdown of work completed...")
                    completion_date = st.date_input("📅 Date Completed")
                    invoice_amount = st.number_input("💰 Invoice Amount (₦)", min_value=0.0, step=0.01, format="%.2f")
                    invoice_number = st.text_input("🔢 Invoice Number")
                    
                    submit_button = st.form_submit_button("✅ Submit Completion", use_container_width=True)
                    
                    if submit_button:
                        if not all([completion_notes, job_breakdown, completion_date, invoice_amount, invoice_number]):
                            st.error("⚠️ Please fill in all fields")
                        else:
                            if execute_update(
                                '''UPDATE maintenance_requests SET status = ?, completion_notes = ?, job_breakdown = ?, 
                                completed_date = ?, invoice_amount = ?, invoice_number = ? WHERE id = ?''',
                                ('Completed', completion_notes, job_breakdown, completion_date.strftime('%Y-%m-%d'), 
                                 invoice_amount, invoice_number, safe_get(job, 'id'))
                            ):
                                st.success("✅ Job completed successfully! Waiting for approvals.")
                                st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

def show_completed_jobs():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("✅ Completed Jobs")
    st.markdown('</div>', unsafe_allow_html=True)
    
    vendor_requests = get_vendor_requests(st.session_state.user['username'])
    completed_jobs = [r for r in vendor_requests if safe_get(r, 'status') in ['Completed', 'Approved']]
    
    if not completed_jobs:
        st.info("📭 No completed jobs found")
        return
    
    st.subheader(f"📊 You have completed {len(completed_jobs)} job(s)")
    
    display_data = []
    for job in completed_jobs:
        display_data.append({
            'ID': safe_get(job, 'id'),
            'Title': safe_str(safe_get(job, 'title'), 'N/A'),
            'Location': safe_str(safe_get(job, 'location'), 'Common Area'),
            'Facility': safe_str(safe_get(job, 'facility_type'), 'N/A'),
            'Invoice Amount': format_naira(safe_get(job, 'invoice_amount')),
            'Invoice Number': safe_str(safe_get(job, 'invoice_number'), 'N/A'),
            'Status': safe_str(safe_get(job, 'status'), 'N/A'),
            'Completed Date': safe_str(safe_get(job, 'completed_date'), 'N/A')[:10]
        })
    
    df = pd.DataFrame(display_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    st.subheader("📄 Job Details")
    selected_id = st.selectbox("Select Job to View Details", [""] + [str(safe_get(job, 'id')) for job in completed_jobs], key="completed_select")
    
    if selected_id:
        job = next((j for j in completed_jobs if str(safe_get(j, 'id')) == selected_id), None)
        if job:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.write("**📋 Job Information**")
                st.write(f"**Title:** {safe_str(safe_get(job, 'title'), 'N/A')}")
                st.write(f"**Description:** {safe_str(safe_get(job, 'description'), 'N/A')}")
                st.write(f"**Location:** {safe_str(safe_get(job, 'location'), 'Common Area')}")
                st.write(f"**Facility Type:** {safe_str(safe_get(job, 'facility_type'), 'N/A')}")
                st.write(f"**Job Breakdown:** {safe_str(safe_get(job, 'job_breakdown'), 'Not provided')}")
                st.write(f"**Completion Notes:** {safe_str(safe_get(job, 'completion_notes'), 'Not provided')}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.write("**💰 Financial & Status**")
                st.write(f"**Invoice Amount:** {format_naira(safe_get(job, 'invoice_amount'))}")
                st.write(f"**Invoice Number:** {safe_str(safe_get(job, 'invoice_number'), 'N/A')}")
                st.write(f"**Status:** {safe_str(safe_get(job, 'status'), 'N/A')}")
                st.write(f"**Completed Date:** {safe_str(safe_get(job, 'completed_date'), 'N/A')}")
                st.write(f"**Department Approval:** {'✅ Approved' if safe_get(job, 'requesting_dept_approval') else '⏳ Pending'}")
                st.write(f"**Manager Approval:** {'✅ Approved' if safe_get(job, 'facilities_manager_approval') else '⏳ Pending'}")
                
                # PDF Download Button for Job Completion Report
                st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
                st.subheader("📄 Download Reports")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📋 Job Completion Report", key=f"job_report_{safe_get(job, 'id')}", use_container_width=True):
                        pdf_data = generate_completion_report_pdf(job)
                        if pdf_data:
                            st.download_button(
                                label="⬇️ Download PDF",
                                data=pdf_data,
                                file_name=f"job_completion_{safe_get(job, 'id')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                                mime="application/pdf",
                                key=f"download_job_{safe_get(job, 'id')}"
                            )
                
                with col2:
                    # Check if invoice exists for this job
                    invoice = execute_query('SELECT * FROM invoices WHERE request_id = ?', (safe_get(job, 'id'),))
                    if invoice:
                        invoice = invoice[0]
                        if st.button("🧾 Invoice Report", key=f"invoice_report_{safe_get(job, 'id')}", use_container_width=True):
                            pdf_data = generate_invoice_report_pdf(invoice, job)
                            if pdf_data:
                                st.download_button(
                                    label="⬇️ Download PDF",
                                    data=pdf_data,
                                    file_name=f"invoice_{safe_get(invoice, 'invoice_number')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                                    mime="application/pdf",
                                    key=f"download_invoice_{safe_get(job, 'id')}"
                                )
                    else:
                        st.info("No invoice generated for this job yet")
                
                st.markdown('</div>', unsafe_allow_html=True)

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
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📎 Attachments")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            certificate_incorporation = st.file_uploader("📄 Certificate of Incorporation", type=['pdf', 'doc', 'docx'])
        with col2:
            tax_clearance_certificate = st.file_uploader("🏛️ Tax Clearance Certificate", type=['pdf', 'doc', 'docx'])
        with col3:
            audited_financial_statement = st.file_uploader("📊 Audited Financial Statement (Optional)", type=['pdf', 'doc', 'docx'])
        st.markdown('</div>', unsafe_allow_html=True)
        
        submitted = st.form_submit_button("🚀 Register Vendor", use_container_width=True)
        
        if submitted:
            if not all([company_name, contact_person, email, phone, services_offered, address]):
                st.error("⚠️ Please fill in all required fields (*)")
            else:
                cert_inc_data = certificate_incorporation.read() if certificate_incorporation else None
                tax_clear_data = tax_clearance_certificate.read() if tax_clearance_certificate else None
                audited_fin_data = audited_financial_statement.read() if audited_financial_statement else None
                
                success = execute_update(
                    '''INSERT INTO vendors (company_name, contact_person, email, phone, vendor_type, services_offered, 
                    annual_turnover, tax_identification_number, rc_number, key_management_staff, account_details, 
                    certification, address, username, certificate_incorporation, tax_clearance_certificate, audited_financial_statement) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (company_name, contact_person, email, phone, st.session_state.user['vendor_type'], services_offered,
                     annual_turnover, tax_identification_number, rc_number, key_management_staff, account_details,
                     certification, address, st.session_state.user['username'], cert_inc_data, tax_clear_data, audited_fin_data)
                )
                if success:
                    st.success("✅ Vendor registration completed successfully!")
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
    
    st.subheader("📋 Select Job for Invoice Creation")
    job_options = {f"#{safe_get(job, 'id')}: {safe_str(safe_get(job, 'title'), 'N/A')} - {safe_str(safe_get(job, 'location'), 'Common Area')}": safe_get(job, 'id') for job in vendor_jobs}
    selected_job_key = st.selectbox("Choose a completed job", list(job_options.keys()), key="invoice_job_select")
    selected_job_id = job_options[selected_job_key]
    
    selected_job = next((job for job in vendor_jobs if safe_get(job, 'id') == selected_job_id), None)
    
    if selected_job:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write(f"**📌 Job Details:** {safe_str(safe_get(selected_job, 'title'), 'N/A')}")
        st.write(f"**📍 Location:** {safe_str(safe_get(selected_job, 'location'), 'Common Area')}")
        st.write(f"**📄 Description:** {safe_str(safe_get(selected_job, 'description'), 'N/A')}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
        st.subheader("💰 Invoice Details")
        
        with st.form("invoice_creation_form", clear_on_submit=True):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            
            with col1:
                invoice_number = st.text_input("🔢 Invoice Number *")
                invoice_date = st.date_input("📅 Invoice Date *")
                details_of_work = st.text_area("🔧 Details of Work Done *", height=100,
                                             value=safe_str(safe_get(selected_job, 'job_breakdown'), ''))
                quantity = st.number_input("📦 Quantity *", min_value=1, value=1)
            
            with col2:
                unit_cost = st.number_input("💵 Unit Cost (₦) *", min_value=0.0, step=0.01, format="%.2f")
                labour_charge = st.number_input("👷 Labour/Service Charge (₦)", min_value=0.0, step=0.01, format="%.2f")
                vat_applicable = st.checkbox("🏛️ Apply VAT (7.5%)")
            
            amount = quantity * unit_cost
            subtotal = amount + labour_charge
            vat_amount = subtotal * 0.075 if vat_applicable else 0
            total_amount = subtotal + vat_amount
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
            st.subheader("🧮 Invoice Summary")
            
            calc_col1, calc_col2, calc_col3, calc_col4 = st.columns(4)
            with calc_col1:
                st.markdown(f'<div class="metric-card"><h4>Amount</h4><h3 class="currency-naira">{format_naira(amount)}</h3></div>', unsafe_allow_html=True)
            with calc_col2:
                st.markdown(f'<div class="metric-card"><h4>Labour Charge</h4><h3 class="currency-naira">{format_naira(labour_charge)}</h3></div>', unsafe_allow_html=True)
            with calc_col3:
                st.markdown(f'<div class="metric-card"><h4>VAT Amount</h4><h3 class="currency-naira">{format_naira(vat_amount)}</h3></div>', unsafe_allow_html=True)
            with calc_col4:
                st.markdown(f'<div class="metric-card"><h4>Total Amount</h4><h3 class="currency-naira">{format_naira(total_amount)}</h3></div>', unsafe_allow_html=True)
            
            submitted = st.form_submit_button("📄 Create Invoice", use_container_width=True)
            
            if submitted:
                if not all([invoice_number, details_of_work]):
                    st.error("⚠️ Please fill in all required fields (*)")
                else:
                    existing_invoice = execute_query('SELECT * FROM invoices WHERE invoice_number = ?', (invoice_number,))
                    if existing_invoice:
                        st.error("❌ Invoice number already exists. Please use a different invoice number.")
                    else:
                        success = execute_update(
                            '''INSERT INTO invoices (invoice_number, request_id, vendor_username, invoice_date, 
                            details_of_work, quantity, unit_cost, amount, labour_charge, vat_applicable, vat_amount, total_amount, currency) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            (invoice_number, selected_job_id, st.session_state.user['username'], 
                             invoice_date.strftime('%Y-%m-%d'), details_of_work, quantity, unit_cost, 
                             amount, labour_charge, vat_applicable, vat_amount, total_amount, '₦')
                        )
                        
                        if success:
                            st.success("✅ Invoice created successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to create invoice")

def show_job_invoice_reports():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.title("📋 Job & Invoice Reports")
    st.markdown('</div>', unsafe_allow_html=True)
    
    completed_jobs = execute_query('''
        SELECT mr.*, i.invoice_number, i.invoice_date, i.total_amount as invoice_total, i.status as invoice_status
        FROM maintenance_requests mr
        LEFT JOIN invoices i ON mr.id = i.request_id
        WHERE mr.status IN ('Completed', 'Approved')
        ORDER BY mr.completed_date DESC
    ''')
    
    if not completed_jobs:
        st.info("📭 No completed jobs with invoices found")
        return
    
    col1, col2, col3 = st.columns(3)
    with col1:
        status_options = ["All"] + list(set(safe_str(safe_get(job, 'status')) for job in completed_jobs))
        status_filter = st.selectbox("Filter by Job Status", status_options, key="job_status")
    with col2:
        location_options = ["All"] + list(set(safe_str(safe_get(job, 'location'), 'Common Area') for job in completed_jobs))
        location_filter = st.selectbox("Filter by Location", location_options, key="job_location")
    with col3:
        has_invoice_filter = st.selectbox("Filter by Invoice", ["All", "With Invoice", "Without Invoice"], key="job_invoice")
    
    filtered_jobs = completed_jobs
    if status_filter != "All":
        filtered_jobs = [job for job in filtered_jobs if safe_str(safe_get(job, 'status')) == status_filter]
    if location_filter != "All":
        filtered_jobs = [job for job in filtered_jobs if safe_str(safe_get(job, 'location'), 'Common Area') == location_filter]
    if has_invoice_filter == "With Invoice":
        filtered_jobs = [job for job in filtered_jobs if safe_get(job, 'invoice_number') is not None]
    elif has_invoice_filter == "Without Invoice":
        filtered_jobs = [job for job in filtered_jobs if safe_get(job, 'invoice_number') is None]
    
    st.subheader(f"📊 Found {len(filtered_jobs)} job(s)")
    
    for job in filtered_jobs:
        with st.expander(f"Job #{safe_get(job, 'id')}: {safe_str(safe_get(job, 'title'), 'N/A')} - {safe_str(safe_get(job, 'location'), 'Common Area')} - {safe_str(safe_get(job, 'status'), 'N/A')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.write("**📋 Job Information**")
                st.write(f"**Title:** {safe_str(safe_get(job, 'title'), 'N/A')}")
                st.write(f"**Location:** {safe_str(safe_get(job, 'location'), 'Common Area')}")
                st.write(f"**Facility Type:** {safe_str(safe_get(job, 'facility_type'), 'N/A')}")
                st.write(f"**Priority:** {safe_str(safe_get(job, 'priority'), 'N/A')}")
                st.write(f"**Status:** {safe_str(safe_get(job, 'status'), 'N/A')}")
                st.write(f"**Created By:** {safe_str(safe_get(job, 'created_by'), 'N/A')}")
                st.write(f"**Assigned Vendor:** {safe_str(safe_get(job, 'assigned_vendor'), 'Not assigned')}")
                if safe_get(job, 'job_breakdown'):
                    st.write(f"**Job Breakdown:** {safe_str(safe_get(job, 'job_breakdown'))}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.write("**🧾 Invoice Information**")
                if safe_get(job, 'invoice_number'):
                    st.write(f"**Invoice Number:** {safe_str(safe_get(job, 'invoice_number'))}")
                    st.write(f"**Invoice Date:** {safe_str(safe_get(job, 'invoice_date'))}")
                    st.write(f"**Invoice Amount:** {format_naira(safe_get(job, 'invoice_total'))}")
                    st.write(f"**Invoice Status:** {safe_str(safe_get(job, 'invoice_status'), 'N/A')}")
                    
                    invoice_details = execute_query(
                        'SELECT * FROM invoices WHERE invoice_number = ?', 
                        (safe_get(job, 'invoice_number'),)
                    )
                    if invoice_details:
                        invoice = invoice_details[0]
                        st.write("**Invoice Details:**")
                        st.write(f"Details of Work: {safe_str(safe_get(invoice, 'details_of_work'), 'N/A')}")
                        st.write(f"Quantity: {safe_str(safe_get(invoice, 'quantity'), '0')}")
                        st.write(f"Unit Cost: {format_naira(safe_get(invoice, 'unit_cost'))}")
                        st.write(f"Amount: {format_naira(safe_get(invoice, 'amount'))}")
                        st.write(f"Labour Charge: {format_naira(safe_get(invoice, 'labour_charge'))}")
                        st.write(f"VAT Applied: {'Yes' if safe_get(invoice, 'vat_applicable') else 'No'}")
                        st.write(f"VAT Amount: {format_naira(safe_get(invoice, 'vat_amount'))}")
                        st.write(f"Total Amount: {format_naira(safe_get(invoice, 'total_amount'))}")
                        
                        # PDF Download Button for Invoice Report
                        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
                        if st.button("📄 Download Invoice Report", key=f"invoice_download_{safe_get(job, 'id')}", use_container_width=True):
                            pdf_data = generate_invoice_report_pdf(invoice, job)
                            if pdf_data:
                                st.download_button(
                                    label="⬇️ Download PDF",
                                    data=pdf_data,
                                    file_name=f"invoice_{safe_get(invoice, 'invoice_number')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                                    mime="application/pdf",
                                    key=f"download_invoice_full_{safe_get(job, 'id')}"
                                )
                else:
                    st.write("**No invoice created yet**")
                
                st.write("**✅ Approval Status**")
                st.write(f"**Department Approval:** {'✅ Approved' if safe_get(job, 'requesting_dept_approval') else '⏳ Pending'}")
                st.write(f"**Manager Approval:** {'✅ Approved' if safe_get(job, 'facilities_manager_approval') else '⏳ Pending'}")
                st.markdown('</div>', unsafe_allow_html=True)

def show_main_app():
    user = st.session_state.user
    role = user['role']
    
    st.markdown(f"""
        <div class="header-container">
            <h1 style="margin: 0; display: flex; align-items: center; gap: 10px;">
                🏢 FACILITIES MANAGEMENT SYSTEM™
                <span style="font-size: 14px; background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 10px;">
                    v2.0
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
        
        if role == 'facility_user':
            menu_options = ["Dashboard", "Create Request", "My Requests"]
        elif role == 'facility_manager':
            menu_options = ["Dashboard", "Manage Requests", "Vendor Management", 
                          "Reports", "Job & Invoice Reports"]
        else:
            menu_options = ["Dashboard", "Assigned Jobs", "Completed Jobs", 
                          "Vendor Registration", "Invoice Creation"]
        
        selected_menu = st.radio("🗺️ Navigation", menu_options, key="navigation_menu", label_visibility="collapsed")
        
        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
        
        # Fixed logout button - using kind="secondary" with custom CSS
        if st.button("🚪 Logout", type="secondary", use_container_width=True, key="logout_button"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        # Simple copyright footer
        st.markdown("""
            <div style="margin-top: 30px; padding: 10px; text-align: center; font-size: 10px; color: rgba(255,255,255,0.6);">
                <hr style="margin: 10px 0;">
                © 2024 FMS™<br>
                All Rights Reserved
            </div>
        """, unsafe_allow_html=True)
    
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
