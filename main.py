import streamlit as st
from streamlit_option_menu import option_menu
import sys
import os
import pandas as pd
from datetime import datetime

# Add the pages directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'pages'))

from pages import startseite, teamkalender, trainingsstatistiken, esel_der_woche, database_debug
from database_helper import db

# Page configuration
st.set_page_config(
    page_title="ViktoriaInsights",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Hide the automatic Streamlit navigation */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    .main-header {
        background: linear-gradient(90deg, #2e7d32, #4caf50);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .stSelectbox > div > div {
        background-color: #f0f2f6;
    }
    
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #2e7d32;
        margin: 1rem 0;
    }
    
    .token-input-header {
        background: linear-gradient(135deg, #ff6b6b, #ee5a52);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        border: 2px solid #ff4757;
    }
</style>
""", unsafe_allow_html=True)

def show_token_penalty_input():
    """Special page for token-based penalty input without authentication"""
    
    # Header for token input mode
    st.markdown("""
    <div class="token-input-header">
        <h1>⚡ Schnelle Strafen-Eingabe</h1>
        <p>Direkte Eingabe ohne Anmeldung</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load real player names from database
    try:
        real_players = db.get_player_names()
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Spielernamen: {str(e)}")
        # Fallback to default players if database can't be loaded
        real_players = ["Thomas Schmidt", "Max Mustermann", "Michael Weber", 
                       "Stefan König", "Andreas Müller", "Christian Bauer"]
    
    # Enhanced penalty types with more options
    penalty_types = [
        "18. oder 19. Kontakt in der Ecke vergeigt",
        "20 Kontakte in der Ecke",
        "Abmeldung vom Spiel nicht persönlich bei Trainer",
        "Abmeldung vom Training nicht persönlich bei Trainer",
        "Alkohol im Trikot",
        "Ball über Zaun",
        "Beini in der Ecke",
        "Beitrag Mannschaftskasse - pro Monat",
        "Falscher Einwurf",
        "Falsches Kleidungsstück beim Präsentationsanzug - pro Stück",
        "Falsches Outfit beim Training - pro Stück",
        "Gegentor (Spieler)",
        "Gelb-Rote Karte (Alles außer Foulspiel)",
        "Gelbe Karte (Alles außer Foulspiel)",
        "Gerätedienst nicht richtig erfüllt - pro Person",
        "Geschossenes Tor (Trainer)",
        "Handy klingelt während Besprechung",
        "Handynutzung nach der Besprechung",
        "Kein Präsentationsanzug beim Spiel",
        "Kiste Bier vergessen",
        "Nicht Duschen (ohne triftigen Grund)",
        "Rauchen im Trikot",
        "Rauchen in der Kabine",
        "Rote Karte (Alles außer Foulspiel)",
        "Shampoo/Badelatschen etc. vergessen - pro Teil",
        "Stange/Hürde o. anderes Trainingsutensil umwerfen",
        "Unentschuldigtes Fehlen bei Mannschaftsabend oder Event",
        "Unentschuldigtes Fehlen beim Spiel",
        "Unentschuldigtes Fehlen beim Training",
        "Unentschuldigtes Fehlen nach Heimspiel (ca. 1 Stunde nach Abpfiff)",
        "Vergessene Gegenstände/Kleidungsstücke - pro Teil",
        "Verspätung Training/Spiel (auf dem Platz) - ab 30 Min.",
        "Verspätung Training/Spiel (auf dem Platz) - ab 5 Min.",
        "Verspätung Training/Spiel (auf dem Platz) - pro Min.",
        "Sonstige"
    ]
    
    # Predefined penalty amounts from the catalog
    strafe_beträge = {
        "Verspätung Training/Spiel (auf dem Platz) - pro Min.": 1.00,
        "Verspätung Training/Spiel (auf dem Platz) - ab 5 Min.": 5.00,
        "Verspätung Training/Spiel (auf dem Platz) - ab 30 Min.": 15.00,
        "Gelbe Karte (Alles außer Foulspiel)": 15.00,
        "Gelb-Rote Karte (Alles außer Foulspiel)": 30.00,
        "Rote Karte (Alles außer Foulspiel)": 50.00,
        "Unentschuldigtes Fehlen beim Training": 25.00,
        "Unentschuldigtes Fehlen beim Spiel": 100.00,
        "Unentschuldigtes Fehlen nach Heimspiel (ca. 1 Stunde nach Abpfiff)": 5.00,
        "Abmeldung vom Training nicht persönlich bei Trainer": 5.00,
        "Abmeldung vom Spiel nicht persönlich bei Trainer": 10.00,
        "Unentschuldigtes Fehlen bei Mannschaftsabend oder Event": 10.00,
        "Kein Präsentationsanzug beim Spiel": 10.00,
        "Falsches Kleidungsstück beim Präsentationsanzug - pro Stück": 3.00,
        "Falsches Outfit beim Training - pro Stück": 1.00,
        "Rauchen in der Kabine": 25.00,
        "Rauchen im Trikot": 25.00,
        "Alkohol im Trikot": 25.00,
        "Handy klingelt während Besprechung": 15.00,
        "Handynutzung nach der Besprechung": 5.00,
        "Shampoo/Badelatschen etc. vergessen - pro Teil": 1.00,
        "Nicht Duschen (ohne triftigen Grund)": 5.00,
        "Gerätedienst nicht richtig erfüllt - pro Person": 1.00,
        "Ball über Zaun": 1.00,
        "Beini in der Ecke": 1.00,
        "20 Kontakte in der Ecke": 1.00,
        "18. oder 19. Kontakt in der Ecke vergeigt": 0.50,
        "Falscher Einwurf": 0.50,
        "Stange/Hürde o. anderes Trainingsutensil umwerfen": 1.00,
        "Vergessene Gegenstände/Kleidungsstücke - pro Teil": 1.00,
        "Gegentor (Spieler)": 0.50,
        "Geschossenes Tor (Trainer)": 1.00,
        "Beitrag Mannschaftskasse - pro Monat": 5.00,
        "Kiste Bier vergessen": 15.00
    }
    
    st.markdown("### 📝 Strafe eingeben")
    
    # Penalty input form
    col1, col2 = st.columns(2)
    
    with col1:
        spieler = st.selectbox("👤 Spieler auswählen", 
                             real_players,
                             help="Wählen Sie den Spieler aus der Mannschaftsliste")
    
    with col2:
        datum = st.date_input("📅 Datum", value=datetime.now().date(),
                            help="Datum an dem die Strafe aufgetreten ist")
    
    # Penalty type selection
    strafe_typ = st.selectbox("⚖️ Strafenart", 
                            penalty_types,
                            help="Wählen Sie die Art der Strafe aus dem kompletten Katalog")
    
    # Amount field that updates automatically based on penalty type
    if strafe_typ == "Sonstige":
        st.info("📝 **Individuelle Strafe:** Betrag frei wählbar")
        betrag = st.number_input("💰 Individueller Betrag (€)", 
                               min_value=0.01, 
                               step=0.01,
                               value=1.00,
                               help="Geben Sie den gewünschten Strafbetrag ein")
    else:
        default_betrag = strafe_beträge.get(strafe_typ, 10.00)
        st.info(f"📋 **Standard-Katalogstrafe:** €{default_betrag:.2f}")
        betrag = st.number_input("💰 Standard-Betrag (€) - anpassbar", 
                               value=default_betrag,
                               step=0.01,
                               help=f"Katalog-Standard: €{default_betrag:.2f} - kann bei Bedarf angepasst werden")
    
    # Additional info
    zusatz_info = st.text_area("📝 Zusätzliche Informationen (optional)",
                             help="Weitere Details zur Strafe (z.B. Umstände, Minuten bei Verspätung)")
    
    # Submit button
    if st.button("💾 Strafe hinzufügen", type="primary", use_container_width=True):
        st.success(f"✅ Strafe für **{spieler}** wurde hinzugefügt!")
        
        # Enhanced info display
        info_card = f"""
        <div style='
            background: linear-gradient(135deg, #17a2b8, #138496);
            padding: 1rem;
            border-radius: 8px;
            color: white;
            margin: 1rem 0;
            border-left: 4px solid #ffffff;
        '>
            <div style='display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;'>
                <span style='font-size: 1.2rem;'>📋</span>
                <strong>Strafendetails</strong>
            </div>
            <p style='margin: 0.2rem 0;'><strong>Spieler:</strong> {spieler}</p>
            <p style='margin: 0.2rem 0;'><strong>Strafenart:</strong> {strafe_typ}</p>
            <p style='margin: 0.2rem 0;'><strong>Betrag:</strong> €{betrag:.2f}</p>
            <p style='margin: 0.2rem 0;'><strong>Datum:</strong> {datum.strftime('%d.%m.%Y')}</p>
            {f"<p style='margin: 0.2rem 0;'><strong>Zusatzinfo:</strong> {zusatz_info}</p>" if zusatz_info else ""}
        </div>
        """
        st.markdown(info_card, unsafe_allow_html=True)
        
        # Save penalty to database
        try:
            # Create new penalty entry
            new_penalty = {
                'Datum': datum.strftime('%d.%m.%Y'),
                'Spieler': spieler,
                'Strafe': strafe_typ,
                'Betrag': betrag,
                'Zusatzinfo': zusatz_info if zusatz_info else 'Token-Eingabe'
            }
            
            # Save to database
            success = db.add_penalty(new_penalty)
            
            if success:
                st.success("💾 Strafe wurde in der Datenbank gespeichert!")
                
                # Refresh the page to show updated data
                st.info("🔄 Seite wird aktualisiert...")
                st.rerun()
            else:
                st.error("❌ Fehler beim Speichern in der Datenbank!")
                st.info("💡 Die Strafe konnte nicht gespeichert werden, bitte versuchen Sie es erneut.")
            
        except Exception as e:
            st.error(f"❌ Fehler beim Speichern: {str(e)}")
            st.info("💡 Die Strafe konnte nicht gespeichert werden, bitte versuchen Sie es erneut.")
    
    st.markdown("---")
    
    # Quick penalty buttons
    st.markdown("### ⚡ Schnell-Strafen")
    st.write("Spieler und Datum auswählen, dann Schnell-Strafe anklicken:")
    
    # Player and date selection for quick penalties
    col_select1, col_select2 = st.columns(2)
    
    with col_select1:
        quick_spieler = st.selectbox("👤 Spieler für Schnell-Strafe", 
                                   real_players,
                                   key="quick_penalty_player",
                                   help="Spieler für Schnell-Strafen auswählen")
    
    with col_select2:
        quick_datum = st.date_input("📅 Datum für Schnell-Strafe", 
                                  value=datetime.now().date(),
                                  key="quick_penalty_date",
                                  help="Datum für Schnell-Strafen auswählen")
    
    # Function to add quick penalty
    def add_quick_penalty(spieler, datum, strafe_typ, betrag):
        try:
            # Create new penalty entry
            new_penalty = {
                'Datum': datum.strftime('%d.%m.%Y'),
                'Spieler': spieler,
                'Strafe': strafe_typ,
                'Betrag': betrag,
                'Zusatzinfo': 'Token-Schnell-Strafe'
            }
            
            # Save to database
            success = db.add_penalty(new_penalty)
            
            if success:
                st.success(f"✅ Schnell-Strafe für **{spieler}** hinzugefügt: {strafe_typ} (€{betrag:.2f})")
                st.info("🔄 Seite wird aktualisiert...")
                st.rerun()
            else:
                st.error("❌ Fehler beim Speichern in der Datenbank!")
            
        except Exception as e:
            st.error(f"❌ Fehler beim Speichern: {str(e)}")
    
    # First row - Common penalties
    st.markdown("#### 🚨 Häufige Strafen")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⏰ Verspätung ab 5 Min. (€5)", use_container_width=True, key="quick_lateness_5"):
            add_quick_penalty(quick_spieler, quick_datum, "Verspätung Training/Spiel (auf dem Platz) - ab 5 Min.", 5.0)
    
    with col2:
        if st.button("📱 Handy in Besprechung (€15)", use_container_width=True, key="quick_phone_meeting"):
            add_quick_penalty(quick_spieler, quick_datum, "Handy klingelt während Besprechung", 15.0)
    
    with col3:
        if st.button("🍺 Kiste Bier vergessen (€15)", use_container_width=True, key="quick_beer_forgot"):
            add_quick_penalty(quick_spieler, quick_datum, "Kiste Bier vergessen", 15.0)
    
    # Second row - Training-specific penalties
    st.markdown("#### 🏃‍♂️ Training-Übungen")
    col4, col5, col6 = st.columns(3)
    
    with col4:
        if st.button("🦵 Beini in der Ecke (€1)", use_container_width=True, key="quick_beini"):
            add_quick_penalty(quick_spieler, quick_datum, "Beini in der Ecke", 1.0)
    
    with col5:
        if st.button("⚽ 20 Kontakte in der Ecke (€1)", use_container_width=True, key="quick_20_contacts"):
            add_quick_penalty(quick_spieler, quick_datum, "20 Kontakte in der Ecke", 1.0)
    
    with col6:
        if st.button("😵 18./19. Kontakt vergeigt (€0.50)", use_container_width=True, key="quick_contact_fail"):
            add_quick_penalty(quick_spieler, quick_datum, "18. oder 19. Kontakt in der Ecke vergeigt", 0.5)
    
    # Third row - Minor penalties
    st.markdown("#### 💡 Kleine Strafen")
    col7, col8, col9 = st.columns(3)
    
    with col7:
        if st.button("⚽ Ball über Zaun (€1)", use_container_width=True, key="quick_ball_over_fence"):
            add_quick_penalty(quick_spieler, quick_datum, "Ball über Zaun", 1.0)
    
    with col8:
        if st.button("❌ Falscher Einwurf (€0.50)", use_container_width=True, key="quick_wrong_throw"):
            add_quick_penalty(quick_spieler, quick_datum, "Falscher Einwurf", 0.5)
    
    with col9:
        if st.button("🏃‍♂️ Stange umgeworfen (€1)", use_container_width=True, key="quick_pole_down"):
            add_quick_penalty(quick_spieler, quick_datum, "Stange/Hürde o. anderes Trainingsutensil umwerfen", 1.0)
    
    # Link back to main app
    st.markdown("---")
    st.info("🔗 **Zur Hauptanwendung:** Entfernen Sie die URL-Parameter um zur normalen Ansicht zu gelangen.")

def main():
    # Get URL parameters
    try:
        params = st.query_params
        mode = params.get("mode", "")
        token = params.get("token", "")
    except:
        # Fallback for older Streamlit versions
        params = st.experimental_get_query_params()
        mode = params.get("mode", [""])[0]
        token = params.get("token", [""])[0]
    
    # Check for token-based access
    if mode == "input_hidden":
        # Define your secret token here
        SECRET_TOKEN = "Kasse"
        
        if token != SECRET_TOKEN:
            st.error("❌ Zugriff verweigert")
            st.warning("🔒 Ungültiger Token für die Strafen-Eingabe")
            st.info("💡 Bitte verwenden Sie den korrekten Link oder gehen Sie zur Hauptanwendung.")
            st.stop()
        
        # Show the token-based penalty input
        show_token_penalty_input()
        return
    
    # Normal application flow
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>VB Insights</h1>
        <p>Erste Mannschaft - Viktoria Buchholz</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation in Sidebar
    with st.sidebar:
        st.image("VB_Logo.png", 
                caption="Viktoria Buchholz", width=150)
        
        selected = option_menu(
            menu_title="Navigation",
            options=["Startseite", "Teamkalender", 
                    "Trainingsstatistiken", "Esel der Woche", "Datenbank Debug"],
            icons=["house", "calendar", "bar-chart", 
                  "person-x", "gear"],
            menu_icon="list",
            default_index=0,
            styles={
                "container": {
                    "padding": "0!important", 
                    "background-color": "#2e7d32",
                    "border-radius": "5px"
                },
                "icon": {
                    "color": "white", 
                    "font-size": "18px"
                },
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "padding": "1rem",
                    "color": "white",
                    "background-color": "transparent",
                    "--hover-color": "#4caf50"
                },
                "nav-link-selected": {
                    "background-color": "white",
                    "color": "#2e7d32",
                    "font-weight": "bold"
                },
            }
        )
    
    # Page routing
    if selected == "Startseite":
        startseite.show()
    elif selected == "Teamkalender":
        teamkalender.show()
    elif selected == "Trainingsstatistiken":
        trainingsstatistiken.show()
    elif selected == "Esel der Woche":
        esel_der_woche.show()
    elif selected == "Datenbank Debug":
        database_debug.show()

if __name__ == "__main__":
    main() 