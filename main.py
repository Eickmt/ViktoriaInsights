import streamlit as st
from streamlit_option_menu import option_menu
import sys
import os
import pandas as pd
from datetime import datetime

# Add the pages directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'pages'))

from pages import startseite, teamkalender, trainingsstatistiken, esel_der_woche
from database_helper import db
from timezone_helper import get_german_date_now

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
    
    /* Better text contrast for selectboxes */
    .stSelectbox > div > div > div {
        color: #000000 !important;
    }
    
    /* Input field text color */
    .stSelectbox [data-baseweb="select"] > div {
        color: #000000 !important;
    }
    
    /* Selected option text color */
    .stSelectbox [data-baseweb="select"] [aria-selected="true"] {
        color: #000000 !important;
    }
    
    /* Dropdown option text colors */
    .stSelectbox [data-baseweb="popover"] [role="option"] {
        color: #000000 !important;
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
    
    # Create tabs for different functions
    tab1, tab2 = st.tabs(["➕ Neue Strafe", "🔧 Strafen verwalten"])
    
    with tab1:
        # Load penalty types from database instead of hardcoding
        try:
            penalty_data = db.get_penalty_types()
            penalty_types = [p['description'] for p in penalty_data]
            strafe_beträge = {p['description']: float(p['default_amount_eur']) for p in penalty_data}
        except Exception as e:
            st.error(f"❌ Fehler beim Laden der Strafenarten: {str(e)}")
            # Fallback to basic penalty types if database fails
            penalty_types = ["Sonstige"]
            strafe_beträge = {"Sonstige": 10.00}

        st.markdown("### 📝 Strafe eingeben")

        # Penalty input form
        col1, col2 = st.columns(2)

        with col1:
            spieler = st.selectbox("👤 Spieler auswählen", 
                                 real_players,
                                 help="Wählen Sie den Spieler aus der Mannschaftsliste")

        with col2:
            datum = st.date_input("📅 Datum", value=get_german_date_now(),
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
                                      value=get_german_date_now(),
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

    with tab2:
        st.markdown("### 🔧 Strafen verwalten")
        st.warning("⚠️ **Vorsicht:** Hier können Sie Strafen dauerhaft löschen!")
        
        # Load penalties from database
        try:
            df_strafen = db.get_penalties()
            
            if df_strafen is None or len(df_strafen) == 0:
                st.info("📋 Keine Strafen in der Datenbank gefunden.")
            else:
                # Display current penalty count
                st.metric("📊 Strafen in der Datenbank", len(df_strafen))
                
                # Filters for better management
                st.markdown("#### 🔍 Filter")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Player filter
                    unique_players = sorted(df_strafen['Spieler'].unique())
                    player_filter = st.selectbox("👤 Spieler", ["Alle"] + [p.capitalize() for p in unique_players], key="manage_player_filter")
                
                with col2:
                    # Date range filter
                    date_filter = st.selectbox("📅 Zeitraum", 
                                             ["Alle", "Letzte 7 Tage", "Letzte 30 Tage", "Diesen Monat"], key="manage_date_filter")
                
                with col3:
                    # Number of entries to show
                    show_count = st.selectbox("📄 Anzeigen", [20, 50, 100, "Alle"], key="manage_show_count")
                
                # Apply filters
                filtered_df = df_strafen.copy()
                
                # Player filter
                if player_filter != "Alle":
                    original_name = unique_players[[p.capitalize() for p in unique_players].index(player_filter)]
                    filtered_df = filtered_df[filtered_df['Spieler'] == original_name]
                
                # Date filter
                if date_filter == "Letzte 7 Tage":
                    from datetime import datetime, timedelta
                    cutoff_date = datetime.now() - timedelta(days=7)
                    filtered_df = filtered_df[filtered_df['Datum'] >= cutoff_date]
                elif date_filter == "Letzte 30 Tage":
                    from datetime import datetime, timedelta
                    cutoff_date = datetime.now() - timedelta(days=30)
                    filtered_df = filtered_df[filtered_df['Datum'] >= cutoff_date]
                elif date_filter == "Diesen Monat":
                    from datetime import datetime, timedelta
                    current_month = datetime.now().replace(day=1)
                    filtered_df = filtered_df[filtered_df['Datum'] >= current_month]
                
                # Limit number of entries
                if show_count != "Alle":
                    filtered_df = filtered_df.head(show_count)
                
                st.markdown("---")
                st.markdown("#### 📋 Strafen zum Löschen auswählen")
                
                if len(filtered_df) > 0:
                    # Initialize session state for selected penalties
                    if 'selected_penalties_token' not in st.session_state:
                        st.session_state.selected_penalties_token = []
                    
                    # Select/Deselect all buttons
                    col1, col2, col3 = st.columns([1, 1, 2])
                    with col1:
                        if st.button("✅ Alle auswählen", use_container_width=True, key="select_all_penalties"):
                            st.session_state.selected_penalties_token = list(range(len(filtered_df)))
                            st.rerun()
                    
                    with col2:
                        if st.button("❌ Alle abwählen", use_container_width=True, key="deselect_all_penalties"):
                            st.session_state.selected_penalties_token = []
                            st.rerun()
                    
                    with col3:
                        selected_count = len(st.session_state.selected_penalties_token)
                        st.info(f"📝 {selected_count} Strafen ausgewählt")
                    
                    st.markdown("---")
                    
                    # Display penalties with checkboxes
                    for idx, (_, penalty) in enumerate(filtered_df.iterrows()):
                        col1, col2, col3, col4, col5, col6 = st.columns([0.5, 2, 2, 1.5, 1, 2])
                        
                        with col1:
                            is_selected = st.checkbox("Auswählen", 
                                                     value=idx in st.session_state.selected_penalties_token,
                                                     key=f"penalty_checkbox_token_{idx}",
                                                     label_visibility="collapsed")
                            
                            # Update selection state
                            if is_selected and idx not in st.session_state.selected_penalties_token:
                                st.session_state.selected_penalties_token.append(idx)
                            elif not is_selected and idx in st.session_state.selected_penalties_token:
                                st.session_state.selected_penalties_token.remove(idx)
                        
                        with col2:
                            st.write(f"**{penalty['Spieler'].capitalize()}**")
                        
                        with col3:
                            # Truncate long penalty names
                            penalty_name = penalty['Strafe']
                            if len(penalty_name) > 30:
                                penalty_name = penalty_name[:30] + "..."
                            st.write(penalty_name)
                        
                        with col4:
                            st.write(f"**€{penalty['Betrag']:.2f}**")
                        
                        with col5:
                            st.write(penalty['Datum'].strftime('%d.%m.%Y'))
                        
                        with col6:
                            if penalty['Zusatzinfo'] and str(penalty['Zusatzinfo']).strip():
                                zusatz_short = str(penalty['Zusatzinfo'])
                                if len(zusatz_short) > 20:
                                    zusatz_short = zusatz_short[:20] + "..."
                                st.write(f"_{zusatz_short}_")
                            else:
                                st.write("_Keine Info_")
                    
                    st.markdown("---")
                    
                    # Delete button with confirmation
                    if len(st.session_state.selected_penalties_token) > 0:
                        st.markdown("#### 🗑️ Ausgewählte Strafen löschen")
                        
                        # Show what will be deleted
                        st.warning(f"⚠️ **{len(st.session_state.selected_penalties_token)} Strafen** werden gelöscht:")
                        
                        total_amount = 0
                        for idx in st.session_state.selected_penalties_token:
                            penalty = filtered_df.iloc[idx]
                            total_amount += penalty['Betrag']
                            penalty_short = penalty['Strafe']
                            if len(penalty_short) > 40:
                                penalty_short = penalty_short[:40] + "..."
                            st.write(f"• {penalty['Spieler'].capitalize()}: {penalty_short} (€{penalty['Betrag']:.2f})")
                        
                        st.error(f"💰 **Gesamtbetrag:** €{total_amount:.2f}")
                        
                        # Direct delete button - no confirmation text needed
                        st.markdown("---")
                        if st.button("🗑️ AUSGEWÄHLTE STRAFEN LÖSCHEN", type="primary", use_container_width=True, key="final_delete_token"):
                            # Sammle penalty_ids für die Löschung
                            penalty_ids_to_delete = []
                            for idx in st.session_state.selected_penalties_token:
                                penalty = filtered_df.iloc[idx]
                                if 'penalty_id' in penalty:
                                    penalty_ids_to_delete.append(penalty['penalty_id'])
                                else:
                                    st.error(f"❌ Penalty ID fehlt für Strafe: {penalty['Spieler']} - {penalty['Strafe']}")
                            
                            if penalty_ids_to_delete:
                                # Lösche Strafen aus der Datenbank
                                try:
                                    success, message = db.delete_multiple_penalties(penalty_ids_to_delete)
                                    
                                    if success:
                                        st.success(f"✅ {len(penalty_ids_to_delete)} Strafen wurden erfolgreich gelöscht!")
                                        st.balloons()
                                        
                                        # Clear selection
                                        st.session_state.selected_penalties_token = []
                                        
                                        # Refresh page
                                        st.info("🔄 Seite wird aktualisiert...")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Fehler beim Löschen: {message}")
                                        
                                except Exception as e:
                                    st.error(f"❌ Unerwarteter Fehler beim Löschen: {str(e)}")
                            else:
                                st.error("❌ Keine gültigen Penalty-IDs gefunden zum Löschen!")
                                
                            st.rerun()
                    else:
                        st.info("📝 Wählen Sie Strafen zum Löschen aus")
                
                else:
                    st.info("📋 Keine Strafen gefunden (Filter angepasst)")
        
        except Exception as e:
            st.error(f"❌ Fehler beim Laden der Strafen: {str(e)}")
    
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
                    "Trainingsstatistiken", "Esel der Woche"],
            icons=["house", "calendar", "bar-chart", 
                  "person-x"],
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

if __name__ == "__main__":
    main() 