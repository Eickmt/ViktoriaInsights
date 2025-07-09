#!/usr/bin/env python3
"""
Debug-Skript für Umgebungsvariablen
"""

import os
from dotenv import load_dotenv

def debug_env():
    print("🔍 Debug Umgebungsvariablen")
    print("=" * 40)
    
    # .env laden
    load_dotenv(override=True)
    
    url = os.getenv('SUPABASE_URL', '')
    key = os.getenv('SUPABASE_ANON_KEY', '')
    
    print(f"SUPABASE_URL:")
    print(f"  Länge: {len(url)} Zeichen")
    print(f"  Beginnt mit: {url[:20]}..." if len(url) > 20 else f"  Vollständig: {url}")
    print(f"  Endet mit: ...{url[-10:]}" if len(url) > 20 else "")
    
    print(f"\nSUPABASE_ANON_KEY:")
    print(f"  Länge: {len(key)} Zeichen")
    print(f"  Beginnt mit: {key[:20]}..." if len(key) > 20 else f"  Vollständig: {key}")
    print(f"  Endet mit: ...{key[-10:]}" if len(key) > 20 else "")
    
    # Validierung
    print(f"\n✅ Validierung:")
    print(f"  URL Format: {'✅' if url.startswith('https://') and '.supabase.co' in url else '❌'}")
    print(f"  Key Format: {'✅' if len(key) > 100 and key.startswith('eyJ') else '❌'}")

if __name__ == "__main__":
    debug_env() 