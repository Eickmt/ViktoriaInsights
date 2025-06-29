import streamlit as st
import hashlib
import json
import os

# Default admin credentials (should be changed in production)
DEFAULT_ADMIN_USER = "admin"
DEFAULT_ADMIN_PASSWORD = "admin"

# File to store user credentials
CREDENTIALS_FILE = "user_credentials.json"

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_credentials():
    """Load user credentials from file"""
    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_credentials(credentials):
    """Save user credentials to file"""
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump(credentials, f, indent=2)

def initialize_default_admin():
    """Initialize default admin user if no credentials exist"""
    credentials = load_credentials()
    
    if not credentials:
        # Create default admin user
        credentials[DEFAULT_ADMIN_USER] = {
            "password_hash": hash_password(DEFAULT_ADMIN_PASSWORD),
            "role": "admin",
            "name": "Administrator"
        }
        save_credentials(credentials)
        st.success("🔐 Standard-Admin-Account erstellt!")
        st.info(f"Benutzername: {DEFAULT_ADMIN_USER}")
        st.info(f"Passwort: {DEFAULT_ADMIN_PASSWORD}")
        st.warning("⚠️ Bitte ändern Sie das Standard-Passwort!")

def verify_credentials(username, password):
    """Verify user credentials"""
    credentials = load_credentials()
    
    if username in credentials:
        stored_hash = credentials[username]["password_hash"]
        return stored_hash == hash_password(password)
    
    return False

def get_user_role(username):
    """Get user role"""
    credentials = load_credentials()
    if username in credentials:
        return credentials[username].get("role", "user")
    return None

def add_user(username, password, role="user", name=""):
    """Add a new user"""
    credentials = load_credentials()
    
    if username in credentials:
        return False, "Benutzer existiert bereits"
    
    credentials[username] = {
        "password_hash": hash_password(password),
        "role": role,
        "name": name or username
    }
    
    save_credentials(credentials)
    return True, "Benutzer erfolgreich erstellt"

def change_password(username, old_password, new_password):
    """Change user password"""
    credentials = load_credentials()
    
    if username not in credentials:
        return False, "Benutzer nicht gefunden"
    
    if not verify_credentials(username, old_password):
        return False, "Aktuelles Passwort ist falsch"
    
    credentials[username]["password_hash"] = hash_password(new_password)
    save_credentials(credentials)
    return True, "Passwort erfolgreich geändert"

def show_login_form():
    """Show login form and return authentication status"""
    st.markdown("### 🔐 Anmeldung erforderlich")
    st.info("Sie müssen sich anmelden, um Strafen hinzufügen zu können.")
    
    # Initialize default admin if needed
    initialize_default_admin()
    
    with st.form("login_form"):
        username = st.text_input("👤 Benutzername", placeholder="Benutzername eingeben")
        password = st.text_input("🔒 Passwort", type="password", placeholder="Passwort eingeben")
        
        col1, col2 = st.columns(2)
        with col1:
            login_button = st.form_submit_button("🚀 Anmelden", use_container_width=True)
        with col2:
            register_button = st.form_submit_button("📝 Registrieren", use_container_width=True)
    
    # Handle login
    if login_button and username and password:
        if verify_credentials(username, password):
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.user_role = get_user_role(username)
            st.success(f"✅ Willkommen, {username}!")
            st.rerun()
        else:
            st.error("❌ Falscher Benutzername oder Passwort!")
    
    # Handle registration
    if register_button:
        st.session_state.show_register = True
        st.rerun()
    
    # Show registration form if requested
    if st.session_state.get("show_register", False):
        show_register_form()
    
    return False

def show_register_form():
    """Show user registration form"""
    st.markdown("### 📝 Neue Benutzer registrieren")
    
    with st.form("register_form"):
        new_username = st.text_input("👤 Neuer Benutzername", placeholder="Benutzername eingeben")
        new_password = st.text_input("🔒 Neues Passwort", type="password", placeholder="Passwort eingeben")
        confirm_password = st.text_input("🔒 Passwort bestätigen", type="password", placeholder="Passwort wiederholen")
        full_name = st.text_input("📝 Vollständiger Name", placeholder="Vor- und Nachname")
        
        col1, col2 = st.columns(2)
        with col1:
            create_button = st.form_submit_button("✅ Benutzer erstellen", use_container_width=True)
        with col2:
            back_button = st.form_submit_button("⬅️ Zurück zur Anmeldung", use_container_width=True)
    
    if create_button:
        if not new_username or not new_password:
            st.error("❌ Benutzername und Passwort sind erforderlich!")
        elif new_password != confirm_password:
            st.error("❌ Passwörter stimmen nicht überein!")
        elif len(new_password) < 6:
            st.error("❌ Passwort muss mindestens 6 Zeichen lang sein!")
        else:
            success, message = add_user(new_username, new_password, "user", full_name)
            if success:
                st.success(f"✅ {message}")
                st.session_state.show_register = False
                st.rerun()
            else:
                st.error(f"❌ {message}")
    
    if back_button:
        st.session_state.show_register = False
        st.rerun()

def show_user_management():
    """Show user management interface for admins"""
    if not st.session_state.get("authenticated", False):
        return
    
    if st.session_state.get("user_role") != "admin":
        st.error("❌ Sie haben keine Berechtigung für diese Funktion!")
        return
    
    st.markdown("### 👥 Benutzerverwaltung")
    
    credentials = load_credentials()
    
    # Display current users
    st.markdown("#### 📋 Aktuelle Benutzer:")
    for username, user_data in credentials.items():
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        with col1:
            st.write(f"**{username}**")
        with col2:
            st.write(user_data.get("name", ""))
        with col3:
            st.write(user_data.get("role", "user"))
        with col4:
            if username != st.session_state.get("username"):
                if st.button(f"🗑️ Löschen", key=f"delete_{username}"):
                    del credentials[username]
                    save_credentials(credentials)
                    st.success(f"Benutzer {username} gelöscht!")
                    st.rerun()
    
    st.markdown("---")
    
    # Add new user
    st.markdown("#### ➕ Neuen Benutzer hinzufügen:")
    with st.form("admin_add_user"):
        admin_username = st.text_input("Benutzername")
        admin_password = st.text_input("Passwort", type="password")
        admin_role = st.selectbox("Rolle", ["user", "admin"])
        admin_name = st.text_input("Vollständiger Name")
        
        if st.form_submit_button("Benutzer hinzufügen"):
            if admin_username and admin_password:
                success, message = add_user(admin_username, admin_password, admin_role, admin_name)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Benutzername und Passwort sind erforderlich!")

def require_auth():
    """Decorator to require authentication for functions"""
    if not st.session_state.get("authenticated", False):
        show_login_form()
        return False
    return True

def show_logout():
    """Show logout button and handle logout"""
    if st.session_state.get("authenticated", False):
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🚪 Abmelden", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.user_role = None
                st.success("✅ Sie wurden erfolgreich abgemeldet!")
                st.rerun()
        
        with col1:
            st.info(f"👤 Angemeldet als: **{st.session_state.get('username')}** ({st.session_state.get('user_role', 'user')})") 