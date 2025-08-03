#!/usr/bin/env python3
"""
Debug-Script für Supabase-Credentials
Zeigt alle verfügbaren Credential-Quellen an
"""

import os

def debug_credentials():
    """Debugge alle Credential-Quellen"""
    print("🔍 Debug: Supabase-Credentials")
    print("=" * 50)
    
    # 1. Umgebungsvariablen
    print("📍 Umgebungsvariablen:")
    supabase_url_env = os.getenv("SUPABASE_URL")
    supabase_key_env = os.getenv("SUPABASE_ANON_KEY")
    
    if supabase_url_env:
        print(f"  SUPABASE_URL: {supabase_url_env}")
    else:
        print("  SUPABASE_URL: ❌ Nicht gesetzt")
    
    if supabase_key_env:
        print(f"  SUPABASE_ANON_KEY: {supabase_key_env[:20]}... (gekürzt)")
    else:
        print("  SUPABASE_ANON_KEY: ❌ Nicht gesetzt")
    
    # 2. Streamlit Secrets (falls verfügbar)
    print("\n📍 Streamlit Secrets:")
    try:
        import streamlit as st
        
        # Direkte Secrets
        supabase_url_direct = st.secrets.get("SUPABASE_URL")
        supabase_key_direct = st.secrets.get("SUPABASE_ANON_KEY")
        
        if supabase_url_direct:
            print(f"  SUPABASE_URL (direkt): {supabase_url_direct}")
        else:
            print("  SUPABASE_URL (direkt): ❌ Nicht gesetzt")
        
        if supabase_key_direct:
            print(f"  SUPABASE_ANON_KEY (direkt): {supabase_key_direct[:20]}... (gekürzt)")
        else:
            print("  SUPABASE_ANON_KEY (direkt): ❌ Nicht gesetzt")
        
        # Nested Secrets
        supabase_section = st.secrets.get("supabase", {})
        supabase_url_nested = supabase_section.get("SUPABASE_URL")
        supabase_key_nested = supabase_section.get("SUPABASE_ANON_KEY")
        
        if supabase_url_nested:
            print(f"  SUPABASE_URL (nested): {supabase_url_nested}")
        else:
            print("  SUPABASE_URL (nested): ❌ Nicht gesetzt")
        
        if supabase_key_nested:
            print(f"  SUPABASE_ANON_KEY (nested): {supabase_key_nested[:20]}... (gekürzt)")
        else:
            print("  SUPABASE_ANON_KEY (nested): ❌ Nicht gesetzt")
            
    except ImportError:
        print("  ❌ Streamlit nicht verfügbar")
    except Exception as e:
        print(f"  ❌ Fehler beim Laden: {e}")
    
    # 3. DatabaseHelper-Logik testen
    print("\n📍 DatabaseHelper-Logik:")
    try:
        from database_helper import db
        
        # Force connection attempt
        db._ensure_connected()
        
        if db.connected:
            print("  ✅ DatabaseHelper erfolgreich verbunden")
            
            # Test connection info
            info = db.get_connection_info()
            print(f"  🔧 Connection Info:")
            print(f"    - Supabase verfügbar: {info['supabase_available']}")
            print(f"    - Verbindung versucht: {info['connection_attempted']}")
            print(f"    - Verbunden: {info['connected']}")
            
            for source, available in info['env_sources'].items():
                print(f"    - {source}: {'✅' if available else '❌'}")
        else:
            print("  ❌ DatabaseHelper konnte keine Verbindung herstellen")
            
    except Exception as e:
        print(f"  ❌ DatabaseHelper-Fehler: {e}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    debug_credentials()