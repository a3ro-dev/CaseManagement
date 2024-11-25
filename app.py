import streamlit as st
import os  # Add import for environment variables
# Set page config must be the first Streamlit command
st.set_page_config(
    page_title="Case Manager",
    page_icon="assets/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': """
        ## About
        Case Management System for Vijay Singh Kushwaha.

        Created with ❤️ by [a3ro-dev](https://github.com/a3ro-dev)
        """
    }
)

import asyncio
import pandas as pd
import shutil
import time
import datetime
from modules.dbCon import Database
from streamlit_cookies_manager import EncryptedCookieManager

# Initialize the database
db = Database()
asyncio.run(db.connect())

# Initialize the cookie manager with a password
cookies = EncryptedCookieManager(
    prefix='case_manager/',
    password='your-secure-password-here'  # Replace with a secure password
)

if not cookies.ready():
    # Wait for the component to load and send us current cookies.
    st.stop()

# Function to log actions
def log_action(action, user):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ip_address = st.session_state.get('ip_address', 'Unknown')
    log_entry = f"{timestamp} - {user} - {ip_address} - {action}\n"
    os.makedirs('logs', exist_ok=True)
    with open('logs/logs.txt', 'a') as f:
        f.write(log_entry)

# Authentication
def authenticate(username, password):
    admin_username = os.environ.get('ADMIN_USERNAME')
    admin_password = os.environ.get('ADMIN_PASSWORD')
    staff_username = os.environ.get('STAFF_USERNAME')
    staff_password = os.environ.get('STAFF_PASSWORD')
    
    if username == admin_username and password == admin_password:
        return 'admin'
    elif username == staff_username and password == staff_password:
        return 'staff'
    else:
        return None

# Main app
def main():
    if 'authenticated' not in st.session_state:
        if cookies.get('remember_me') == 'True':
            # Retrieve user info from cookies
            st.session_state['authenticated'] = True
            st.session_state['role'] = cookies.get('role')
            st.session_state['username'] = cookies.get('username')
        else:
            st.session_state['authenticated'] = False

    if not st.session_state['authenticated']:
        st.title("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        remember_me = st.checkbox("Remember Me")
        if st.button("Login"):
            role = authenticate(username, password)
            if role:
                st.session_state['authenticated'] = True
                st.session_state['role'] = role
                st.session_state['username'] = username
                if remember_me:
                    # Save credentials in cookies
                    cookies['remember_me'] = 'True'
                    cookies['username'] = username
                    cookies['role'] = role
                    cookies.save()
                else:
                    cookies['remember_me'] = 'False'
                    cookies.save()
                st.rerun()
            else:
                st.error("Invalid credentials")
    else:
        # Initialize change counter and edit flag in session state
        if 'change_count' not in st.session_state:
            st.session_state['change_count'] = 0
        if 'edit_made' not in st.session_state:
            st.session_state['edit_made'] = False
        role = st.session_state['role']
        username = st.session_state['username']
        # Change favicon based on user role
        change_favicon(role)
        if role == 'admin':
            admin_dashboard(username)
        elif role == 'staff':
            staff_dashboard()
        st.sidebar.button("Logout", on_click=logout)

def change_favicon(role):
    if role == 'admin':
        favicon_path = 'assets/admin.png'
    elif role == 'staff':
        favicon_path = 'assets/staff.png'
    else:
        favicon_path = 'assets/favicon.png'  # Default favicon
    st.markdown(f"""
        <head>
            <link rel="shortcut icon" href="{favicon_path}">
        </head>
        """, unsafe_allow_html=True)

def logout():
    st.session_state['authenticated'] = False
    st.session_state['role'] = None
    st.session_state['username'] = None
    if 'remember_me' in st.session_state:
        del st.session_state['remember_me']
    # Clear cookies on logout
    cookies['remember_me'] = 'False'
    # Replace cookies.delete() with del statement
    del cookies['username']
    del cookies['role']
    cookies.save()
    st.rerun()

def admin_dashboard(username):
    st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h1>Welcome Vijay</h1>
            <img src='assets/admin.png' width='50' style='margin: 1rem 0;'>
        </div>
    """, unsafe_allow_html=True)
    
    # Analytics with better spacing
    with st.container():
        st.markdown("<div style='margin: 2rem 0;'>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        cases = asyncio.run(db.get_all_cases())
        df = pd.DataFrame(cases, columns=['Serial Number', 'District', 'Case Number', 'Party Name', 'Status'])
        
        with col1:
            st.metric("Total Cases", len(cases))
        with col2:
            st.metric("Active Cases", len(df[df['Status'].str.lower() == 'active'].dropna()))
        with col3:
            st.metric("Districts", len(df['District'].unique()))
        with col4:
            st.metric("Recent Additions", len(df[df['Serial Number'] > len(df) - 5]))
        st.markdown("</div>", unsafe_allow_html=True)

    # Main Interface
    tab1, tab2, tab3 = st.tabs(["Database", "Logs", "Backups"])
    
    with tab1:
        manage_database()
    with tab2:
        view_logs()
    with tab3:
        manage_backups()

def staff_dashboard():
    # Update welcome message to display the staff user's name
    st.markdown(f"""
        <div style='text-align: center;'>
            <h1>Welcome {st.session_state['username'].title()}</h1>
            <img src='assets/staff.png' width='50'>
        </div>
        """, unsafe_allow_html=True)
    st.header("Case List")
    view_cases()
    footer()

def manage_database():
    st.header("Database Management")
    # Display the database contents
    cases = asyncio.run(get_all_cases())
    df = pd.DataFrame(cases, columns=['Serial Number', 'District', 'Case Number', 'Party Name', 'Status'])
    edited_df = st.data_editor(df, num_rows="dynamic", key="data_editor")
    
    # Check if any edits were made
    if not edited_df.equals(df):
        st.session_state['edit_made'] = True

    if st.session_state['edit_made']:
        if st.button("Save Changes", type="primary"):
            # Save the edited dataframe back to the database
            asyncio.run(update_cases(edited_df))
            st.success("Changes saved successfully!")
            log_action("Database edited", st.session_state['username'])
            # Increment change counter
            increment_change_counter()
            st.session_state['edit_made'] = False

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Download Database"):
            with open(db.db_file, 'rb') as f:
                st.download_button('Download Database', f, file_name='cases.db')
    with col2:
        uploaded_file = st.file_uploader("Upload Database", type="db")
        if uploaded_file:
            with open(db.db_file, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            st.success("Database uploaded")
            log_action("Database uploaded", st.session_state['username'])

def view_cases():
    st.header("Case Management")
    
    # Callback function to clear the search box
    def clear_search_callback():
        st.session_state.search_box = ""
    
    # Search interface
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("Search across all fields...", key="search_box")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing for alignment
        clear_search = st.button("Clear Search", on_click=clear_search_callback)
    
    # Display search results or all cases
    if search_query:
        cases = asyncio.run(db.search_all_fields(search_query))
    else:
        cases = asyncio.run(db.get_all_cases())

    if cases:
        df = pd.DataFrame(cases, columns=['Serial Number', 'District', 'Case Number', 'Party Name', 'Status'])
        
        # Style the dataframe
        st.write("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
        st.dataframe(
            df,
            width=800,
            height=600,
            use_container_width=False,
            hide_index=True,
            column_config={
                "Serial Number": st.column_config.NumberColumn(format="%d"),
                "Status": st.column_config.TextColumn(help="Current status of the case"),
            }
        )
        st.write("</div>", unsafe_allow_html=True)
        
        st.info(f"Found {len(cases)} cases")
    else:
        st.warning("No cases found")

    # Add new case interface
    with st.expander("Add New Case"):
        col1, col2 = st.columns(2)
        with col1:
            district = st.text_input("District*")
            case_number = st.text_input("Case Number*")
        with col2:
            party_name = st.text_input("Party Name*")
            status = st.text_input("Status")
        
        if st.button("Add Case", type="primary", use_container_width=True):
            if district and case_number and party_name:
                asyncio.run(db.add_case(district, case_number, party_name, status))
                st.success("✅ Case added successfully!")
                log_action("New case added", st.session_state['username'])
                time.sleep(1)
                st.rerun()
            else:
                st.error("Please fill in all required fields")
            # Increment change counter
            increment_change_counter()

def view_logs():
    st.header("Logs")
    if os.path.exists('logs/logs.txt'):
        with open('logs/logs.txt', 'r') as f:
            logs = f.read()
        st.text_area("Logs", logs, height=300)
    else:
        st.write("No logs available")

def manage_backups():
    st.header("Database Backups")
    backup_dir = 'backups'
    os.makedirs(backup_dir, exist_ok=True)
    backups = sorted(os.listdir(backup_dir), reverse=True)

    if st.button("Create Backup"):
        backup_file = os.path.join(backup_dir, f"cases_backup_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.db")
        shutil.copy(db.db_file, backup_file)
        st.success("Backup created")
        log_action("Backup created", st.session_state['username'])
    st.write("Available Backups (Last 3):")
    # Align backup download buttons
    for backup in backups[:3]:
        st.write(backup)
        with open(os.path.join(backup_dir, backup), 'rb') as f:
            st.download_button(f"Download {backup}", f, file_name=backup)
    # Delete backups older than 3 days
    for backup in backups:
        backup_path = os.path.join(backup_dir, backup)
        if os.path.isfile(backup_path):
            creation_time = os.path.getctime(backup_path)
            if (datetime.datetime.now() - datetime.datetime.fromtimestamp(creation_time)).days > 3:
                os.remove(backup_path)

def apply_backup():
    st.header("Apply Backup")
    backup_dir = 'backups'
    backups = sorted(os.listdir(backup_dir), reverse=True)
    selected_backup = st.selectbox("Select a backup to restore", backups)
    if st.button("Restore Backup"):
        backup_path = os.path.join(backup_dir, selected_backup)
        shutil.copy(backup_path, db.db_file)
        st.success(f"Backup '{selected_backup}' has been restored.")
        log_action(f"Backup '{selected_backup}' restored", st.session_state['username'])
        st.rerun()

async def get_all_cases():
    cursor = await db.connection.execute("SELECT * FROM cases")
    cases = await cursor.fetchall()
    return cases

async def update_cases(df):
    await db.connection.execute("DELETE FROM cases")
    await db.connection.commit()
    for index, row in df.iterrows():
        await db.add_case(row['District'], row['Case Number'], row['Party Name'], row['Status'])

def increment_change_counter():
    # Increment the change counter
    st.session_state['change_count'] += 1
    if st.session_state['change_count'] >= 3:
        # Create automatic backup
        create_backup()
        st.session_state['change_count'] = 0  # Reset counter

def create_backup():
    backup_dir = 'backups'
    os.makedirs(backup_dir, exist_ok=True)
    backup_file = os.path.join(backup_dir, f"cases_autobackup_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.db")
    shutil.copy(db.db_file, backup_file)
    st.info("An automatic backup has been created.")
    log_action("Automatic backup created", st.session_state['username'])
    # Delete backups older than 3 days
    delete_old_backups()

def delete_old_backups():
    backup_dir = 'backups'
    backups = os.listdir(backup_dir)
    for backup in backups:
        backup_path = os.path.join(backup_dir, backup)
        if os.path.isfile(backup_path):
            creation_time = os.path.getctime(backup_path)
            if (datetime.datetime.now() - datetime.datetime.fromtimestamp(creation_time)).days > 3:
                os.remove(backup_path)

# Update CSS styles
st.markdown("""
    <style>
    /* Main container styles */
    .main {
        padding: 2rem 4rem;  /* Adjusted padding for better alignment */
    }
    
    /* Center containers */
    .block-container {
        max-width: 1200px;
        padding: 2rem 1rem;
        margin: 0 auto;
    }
    
    /* Dashboard metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        text-align: center;
    }
    
    /* Data editor alignment */
    .stDataFrame {
        width: 100% !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background-color: #2E2E2E;
        border: 1px solid #444444;
        color: #FAFAFA;
        padding: 0.5rem;
    }
    
    /* Buttons */
    .stButton > button {
        width: auto;
        padding: 0.5rem 1rem;
        background-color: #444444;
        color: #FAFAFA;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        justify-content: center;
    }
    
    /* Headers */
    h1, h2, h3 {
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    /* Containers */
    [data-testid="column"] {
        padding: 0 0.5rem;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {        background-color: #2E2E2E;        border-radius: 4px;    }        /* Remove default padding from containers */
    .css-1544g2n {
        padding: 1rem 1rem !important;
    }
    
    /* Adjust padding for mobile */
    @media (max-width: 768px) {
        .main {
            padding: 0.5rem;
        }
        .block-container {
            padding: 1rem 0.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# Update CSS styles
st.markdown("""
    <style>
    /* ...existing styles... */

    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main {
            padding: 0.5rem !important;
        }
        .block-container {
            padding: 1rem 0.5rem !important;
        }
        /* Adjust font sizes for mobile */
        h1 {
            font-size: 2rem;
        }
        h2 {
            font-size: 1.5rem;
        }
        h3 {
            font-size: 1.2rem;
        }
        /* Adjust button sizes */
        .stButton > button {
            padding: 0.5rem 1rem;
        }
    }

    /* Add visual effects */
    body {
        scroll-behavior: smooth;
        background-color: #f5f5f5;
    }
    .stButton > button:hover {
        background-color: #555555;
        transition: background-color 0.3s ease;
    }
    h1, h2, h3 {
        animation: fadeIn 1s ease-in-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Optimize performance */
    /* Minimize CSS reflows by grouping selectors */
    .main, .block-container, .stButton > button, h1, h2, h3 {
        will-change: auto;
    }

    </style>
    """, unsafe_allow_html=True)

def footer():
    st.markdown("""
    <hr style='border-top: 1px solid #FF4B4B;'>
    <center>
        Created with ❤️ by <a href='https://github.com/a3ro-dev' target='_blank'>a3ro-dev</a>
    </center>
    """, unsafe_allow_html=True)

if __name__ == '__main__':
    main()