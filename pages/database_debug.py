import streamlit as st
import pandas as pd
import sys
import os

# Add the parent directory to the path to import database helper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database_helper import db
from auth import require_auth

def show():
    st.title("🔧 Datenbank Debug")
    st.subheader("Supabase-Verbindung testen und konfigurieren")
    
    # Authentication required
    if not require_auth():
        st.stop()
    
    # Connection info
    st.markdown("### 📊 Verbindungsstatus")
    
    try:
        conn_info = db.get_connection_info()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if conn_info['supabase_available']:
                st.success("✅ Supabase-Client verfügbar")
            else:
                st.error("❌ Supabase-Client nicht installiert")
                st.code("pip install supabase")
        
        with col2:
            if conn_info['dotenv_available']:
                st.success("✅ python-dotenv verfügbar")
            else:
                st.warning("⚠️ python-dotenv nicht installiert")
                st.code("pip install python-dotenv")
        
        with col3:
            if conn_info['connected']:
                st.success("✅ Datenbank verbunden")
            else:
                st.error("❌ Keine Datenbankverbindung")
        
        # Environment variables sources
        st.markdown("### 🔑 Umgebungsvariablen-Quellen")
        
        env_sources = conn_info['env_sources']
        
        # Create a detailed table
        sources_data = [
            {"Quelle": "🗂️ .env Datei", 
             "SUPABASE_URL": "✅" if env_sources['SUPABASE_URL_env'] else "❌",
             "SUPABASE_ANON_KEY": "✅" if env_sources['SUPABASE_ANON_KEY_env'] else "❌"},
            {"Quelle": "📄 .streamlit/secrets.toml (root)", 
             "SUPABASE_URL": "✅" if env_sources['SUPABASE_URL_secrets'] else "❌",
             "SUPABASE_ANON_KEY": "✅" if env_sources['SUPABASE_ANON_KEY_secrets'] else "❌"},
            {"Quelle": "📁 .streamlit/secrets.toml [supabase]", 
             "SUPABASE_URL": "✅" if env_sources['SUPABASE_URL_nested'] else "❌",
             "SUPABASE_ANON_KEY": "✅" if env_sources['SUPABASE_ANON_KEY_nested'] else "❌"}
        ]
        
        df_sources = pd.DataFrame(sources_data)
        st.dataframe(df_sources, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Fehler beim Abrufen der Verbindungsinfo: {str(e)}")
    
    st.markdown("---")
    
    # Connection test
    st.markdown("### 🧪 Verbindungstest")
    
    if st.button("🔗 Datenbankverbindung testen", type="primary"):
        with st.spinner("Teste Verbindung..."):
            success, message = db.test_connection()
            
            if success:
                st.success(message)
            else:
                st.error(message)
    
    st.markdown("---")
    
    # Configuration display
    st.markdown("### ⚙️ Aktuelle Konfiguration")
    
    # Check all possible environment variable sources
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**SUPABASE_URL:**")
        
        # Check .env
        env_url = os.getenv("SUPABASE_URL")
        if env_url:
            st.info(f"🗂️ .env: {env_url[:50]}...")
        else:
            st.warning("🗂️ .env: Nicht gefunden")
        
        # Check streamlit secrets (root)
        try:
            secrets_url = st.secrets.get("SUPABASE_URL")
            if secrets_url:
                st.info(f"📄 secrets (root): {secrets_url[:50]}...")
            else:
                st.warning("📄 secrets (root): Nicht gefunden")
        except:
            st.warning("📄 secrets (root): Fehler beim Laden")
        
        # Check streamlit secrets (nested)
        try:
            nested_url = st.secrets.get("supabase", {}).get("SUPABASE_URL")
            if nested_url:
                st.info(f"📁 secrets [supabase]: {nested_url[:50]}...")
            else:
                st.warning("📁 secrets [supabase]: Nicht gefunden")
        except:
            st.warning("📁 secrets [supabase]: Fehler beim Laden")
    
    with col2:
        st.markdown("**SUPABASE_ANON_KEY:**")
        
        # Check .env
        env_key = os.getenv("SUPABASE_ANON_KEY")
        if env_key:
            st.info(f"🗂️ .env: {env_key[:30]}...")
        else:
            st.warning("🗂️ .env: Nicht gefunden")
        
        # Check streamlit secrets (root)
        try:
            secrets_key = st.secrets.get("SUPABASE_ANON_KEY")
            if secrets_key:
                st.info(f"📄 secrets (root): {secrets_key[:30]}...")
            else:
                st.warning("📄 secrets (root): Nicht gefunden")
        except:
            st.warning("📄 secrets (root): Fehler beim Laden")
        
        # Check streamlit secrets (nested)
        try:
            nested_key = st.secrets.get("supabase", {}).get("SUPABASE_ANON_KEY")
            if nested_key:
                st.info(f"📁 secrets [supabase]: {nested_key[:30]}...")
            else:
                st.warning("📁 secrets [supabase]: Nicht gefunden")
        except:
            st.warning("📁 secrets [supabase]: Fehler beim Laden")
    
    st.markdown("---")
    
    # Database content preview
    st.markdown("### 📊 Datenbank-Inhalte")
    
    # Birthday data
    with st.expander("🎂 Geburtstage"):
        try:
            df_birthdays = db.get_birthdays()
            if df_birthdays is not None and len(df_birthdays) > 0:
                st.success(f"✅ {len(df_birthdays)} Geburtstage gefunden")
                st.dataframe(df_birthdays)
                
                # Show source
                if db.connected:
                    st.info("📊 **Quelle:** Supabase-Datenbank")
                else:
                    st.info("📄 **Quelle:** CSV-Fallback")
            else:
                st.warning("⚠️ Keine Geburtstage gefunden")
        except Exception as e:
            st.error(f"❌ Fehler beim Laden der Geburtstage: {str(e)}")
    
    # Player names
    with st.expander("👥 Spielernamen"):
        try:
            player_names = db.get_player_names()
            if player_names:
                st.success(f"✅ {len(player_names)} Spieler gefunden")
                st.write(", ".join(player_names))
                
                # Show source
                if db.connected:
                    st.info("📊 **Quelle:** Supabase-Datenbank")
                else:
                    st.info("📄 **Quelle:** CSV-Fallback")
            else:
                st.warning("⚠️ Keine Spielernamen gefunden")
        except Exception as e:
            st.error(f"❌ Fehler beim Laden der Spielernamen: {str(e)}")
    
    # Available tables
    with st.expander("📋 Verfügbare Tabellen"):
        if st.button("📊 Tabellen auflisten", key="list_tables"):
            available_tables = db.get_available_tables()
            
            if available_tables:
                st.success(f"✅ Gefundene Tabellen: {', '.join(available_tables)}")
                
                for table in available_tables:
                    st.write(f"- **{table}**")
            else:
                st.error("❌ Keine Tabellen gefunden oder Verbindung fehlgeschlagen")
    
    # Penalty table test
    with st.expander("💰 Strafen-Tabelle Test"):
        if st.button("🧪 Strafen-Tabelle testen", key="test_penalties"):
            success, message = db.test_penalties_table()
            
            if success:
                st.success(message)
            else:
                st.error(message)
                st.info("💡 Erstellen Sie eine Tabelle namens 'strafen' oder 'Strafen' mit den Spalten: datum, spieler, strafe, betrag, zusatzinfo")
                
                # Show SQL for creating table
                sql_code = """
CREATE TABLE strafen (
    id SERIAL PRIMARY KEY,
    datum TEXT NOT NULL,
    spieler TEXT NOT NULL,
    strafe TEXT NOT NULL,
    betrag DECIMAL(10,2) NOT NULL,
    zusatzinfo TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT NOW()
);"""
                st.code(sql_code, language="sql")
    
    # Penalties
    with st.expander("🤡 Strafen"):
        try:
            df_penalties = db.get_penalties()
            if df_penalties is not None and len(df_penalties) > 0:
                st.success(f"✅ {len(df_penalties)} Strafen gefunden")
                st.dataframe(df_penalties.head(10))  # Show only first 10
                
                # Show source
                if db.connected:
                    st.info("📊 **Quelle:** Supabase-Datenbank")
                else:
                    st.info("📄 **Quelle:** CSV-Fallback")
            else:
                st.warning("⚠️ Keine Strafen gefunden")
        except Exception as e:
            st.error(f"❌ Fehler beim Laden der Strafen: {str(e)}")
    
    st.markdown("---")
    
    # Setup instructions
    st.markdown("### 📖 Setup-Anleitung")
    
    st.markdown("""
    #### 🔧 Option 1: .env Datei (Lokale Entwicklung)
    Erstelle eine `.env` Datei im Projektroot:
    ```env
    SUPABASE_URL=https://your-project.supabase.co
    SUPABASE_ANON_KEY=your-anon-key-here
    ```
    
    #### 🔧 Option 2: .streamlit/secrets.toml (Lokal & Cloud)
    
    **Variante A - Root-Level:**
    ```toml
    SUPABASE_URL = "https://your-project.supabase.co"
    SUPABASE_ANON_KEY = "your-anon-key-here"
    ```
    
    **Variante B - Nested (empfohlen):**
    ```toml
    [supabase]
    SUPABASE_URL = "https://your-project.supabase.co"
    SUPABASE_ANON_KEY = "your-anon-key-here"
    ```
    
    #### ☁️ Streamlit Cloud
    1. Gehe zu App-Einstellungen → Secrets
    2. Verwende eine der obigen Varianten
    
    #### 🗄️ Supabase Tabellen
    
    **Geburtstage-Tabelle:**
    ```sql
    CREATE TABLE Geburtstage (
        id SERIAL PRIMARY KEY,
        Name TEXT NOT NULL,
        Geburtstag TEXT NOT NULL
    );
    ```
    
    **Strafen-Tabelle (optional):**
    ```sql
    CREATE TABLE Strafen (
        id SERIAL PRIMARY KEY,
        Datum TEXT NOT NULL,
        Spieler TEXT NOT NULL,
        Strafe TEXT NOT NULL,
        Betrag DECIMAL(10,2) NOT NULL,
        Zusatzinfo TEXT
    );
    ```
    """)
    
    st.markdown("---")
    
    # File system info
    st.markdown("### 📁 Dateisystem-Check")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Konfigurationsdateien:**")
        
        if os.path.exists(".env"):
            st.success("✅ .env Datei gefunden")
        else:
            st.info("ℹ️ .env Datei nicht vorhanden")
        
        if os.path.exists(".streamlit/secrets.toml"):
            st.success("✅ .streamlit/secrets.toml gefunden")
        else:
            st.info("ℹ️ .streamlit/secrets.toml nicht vorhanden")
    
    with col2:
        st.markdown("**CSV-Dateien:**")
        
        if os.path.exists("VB_Geburtstage.csv"):
            st.success("✅ VB_Geburtstage.csv gefunden")
        else:
            st.warning("⚠️ VB_Geburtstage.csv nicht gefunden")
        
        if os.path.exists("VB_Strafen.csv"):
            st.success("✅ VB_Strafen.csv gefunden")
        else:
            st.info("ℹ️ VB_Strafen.csv nicht vorhanden")
    
    # Installation commands
    st.markdown("---")
    st.markdown("### 🛠️ Installation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Abhängigkeiten installieren:**")
        st.code("pip install supabase python-dotenv", language="bash")
    
    with col2:
        st.markdown("**Requirements aktualisieren:**")
        st.code("pip install -r requirements.txt", language="bash") 