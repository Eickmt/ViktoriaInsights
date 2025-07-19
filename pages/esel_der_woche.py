import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Add the parent directory to the path to import auth module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import require_auth, show_logout, show_user_management
from database_helper import db
from timezone_helper import get_german_now, get_german_now_naive

def show():
    st.title("🤡 Esel der Woche")
    st.subheader("Strafen und der Esel der Woche")
    
    # Show logout button if authenticated
    show_logout()
    
    # Load real penalty data from database
    try:
        df_strafen = db.get_penalties()
        
        if df_strafen is None or len(df_strafen) == 0:
            # Create sample data if no data exists
            strafen_data = [
                {"Datum": "2024-12-01", "Spieler": "Thomas Schmidt", "Strafe": "Verspätung Training/Spiel (auf dem Platz) - ab 5 Min.", "Betrag": 5.00, "Zusatzinfo": ""},
                {"Datum": "2024-11-30", "Spieler": "Luca Motuzzi", "Strafe": "Handynutzung nach der Besprechung", "Betrag": 5.00, "Zusatzinfo": ""},
                {"Datum": "2024-11-29", "Spieler": "Ben", "Strafe": "Beini in der Ecke", "Betrag": 1.00, "Zusatzinfo": ""},
                {"Datum": "2024-11-28", "Spieler": "Max Mustermann", "Strafe": "Verspätung Training/Spiel (auf dem Platz) - ab 30 Min.", "Betrag": 15.00, "Zusatzinfo": ""},
                {"Datum": "2024-11-25", "Spieler": "Michael Weber", "Strafe": "Rote Karte (Alles außer Foulspiel)", "Betrag": 50.00, "Zusatzinfo": "Schiedsrichterbeleidigung"},
            ]
            df_strafen = pd.DataFrame(strafen_data)
            df_strafen['Datum'] = pd.to_datetime(df_strafen['Datum'])
        
        df_strafen = df_strafen.sort_values('Datum', ascending=False)
        
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Strafendaten: {str(e)}")
        # Fallback to empty DataFrame
        df_strafen = pd.DataFrame(columns=['Datum', 'Spieler', 'Strafe', 'Betrag', 'Zusatzinfo'])
        df_strafen['Datum'] = pd.to_datetime(df_strafen['Datum'])
    
    # Calculate last week's donkey using week_nr from database
    try:
        aktueller_esel, esel_betrag, esel_anzahl = db.get_last_week_donkey()
        
        if not aktueller_esel:
            aktueller_esel = "Niemand"
            esel_betrag = 0
            esel_anzahl = 0
            
    except Exception as e:
        st.error(f"❌ Fehler beim Laden des Esels der letzten Woche: {str(e)}")
        aktueller_esel = "Niemand"
        esel_betrag = 0
        esel_anzahl = 0
    
    # PROMINENT DONKEY DISPLAY
    st.markdown("---")
    
    # Big attention-grabbing display for current donkey
    if aktueller_esel != "Niemand":
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #ff6b6b, #ee5a52);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            color: white;
            box-shadow: 0 8px 25px rgba(238, 90, 82, 0.3);
            margin: 2rem 0;
            border: 3px solid #ff4757;
        '>
            <h1 style='margin: 0; font-size: 3rem;'>🤡</h1>
            <h2 style='margin: 0.5rem 0; font-size: 2.5rem; font-weight: bold;'>ESEL DER WOCHE</h2>
            <h1 style='margin: 1rem 0; font-size: 3rem; color: #fff200; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);'>{aktueller_esel.capitalize()}</h1>
            <div style='font-size: 1.5rem; margin-top: 1rem;'>
                <p style='margin: 0.5rem 0;'>💰 <strong>€{esel_betrag:.2f}</strong> in Strafen</p>
                <p style='margin: 0.5rem 0;'>📊 <strong>{int(esel_anzahl)}</strong> Strafen letzte Woche</p>
            </div>
            <p style='font-size: 1.2rem; margin-top: 1.5rem; opacity: 0.9;'>
                👑 Herzlichen Glückwunsch zum Titel! 👑
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        st.success("🎉 Letzte Woche gab es noch keinen Esel!")
    
    st.markdown("---")
    
    # Statistics and tracking
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        gesamt_strafen = len(df_strafen)
        st.metric("📊 Strafen gesamt", gesamt_strafen)
    
    with col2:
        gesamt_betrag = df_strafen['Betrag'].sum()
        st.metric("💰 Strafen-Summe", f"€{gesamt_betrag:.2f}")
    
    with col3:
        letzte_30_tage = df_strafen[df_strafen['Datum'] >= (get_german_now_naive() - timedelta(days=30))]
        strafen_30_tage = len(letzte_30_tage)
        st.metric("📅 Letzte 30 Tage", strafen_30_tage)
    
    with col4:
        durchschnitt = df_strafen['Betrag'].mean()
        st.metric("📈 Ø Strafe", f"€{durchschnitt:.2f}")
    
    # Tabs for detailed analysis
    tab_names = ["📋 Strafen-Liste", "📊 Statistiken", "🏆 Esel-Historie", "📜 Regelwerk"]
    
    # Add user management tab for admins
    if st.session_state.get("authenticated", False) and st.session_state.get("user_role") == "admin":
        tab_names.append("👥 Benutzerverwaltung")
    
    tabs = st.tabs(tab_names)
    
    tab1, tab2, tab3, tab4 = tabs[:4]
    
    # Get the user management tab if it exists
    tab5 = tabs[4] if len(tabs) > 4 else None
    
    with tab1:
        # TOP 3 CURRENT WEEK PENALTIES
        st.subheader("🚨 Top 3 Strafen dieser Woche")
        
        # Calculate current week penalties
        try:
            from datetime import datetime
            current_week = get_german_now_naive().isocalendar()[1]
            current_year = get_german_now_naive().year
            
            # Filter penalties for current week
            current_week_penalties = df_strafen[
                (df_strafen['Datum'].dt.isocalendar().week == current_week) &
                (df_strafen['Datum'].dt.year == current_year)
            ]
            
            if len(current_week_penalties) > 0:
                # Calculate player stats for current week
                week_stats = current_week_penalties.groupby('Spieler').agg({
                    'Betrag': ['sum', 'count']
                }).round(2)
                week_stats.columns = ['Gesamt', 'Anzahl']
                week_stats = week_stats.reset_index().sort_values('Gesamt', ascending=False)
                
                # Display top 3
                col1, col2, col3 = st.columns(3)
                
                for i, col in enumerate([col1, col2, col3]):
                    if i < len(week_stats):
                        player = week_stats.iloc[i]
                        rank_emoji = ["🥇", "🥈", "🥉"][i]
                        rank_color = ["#FFD700", "#C0C0C0", "#CD7F32"][i]  # Gold, Silver, Bronze
                        
                        with col:
                            st.markdown(f"""
                            <div style='
                                background: linear-gradient(135deg, {rank_color}33, {rank_color}22);
                                border-left: 4px solid {rank_color};
                                padding: 1rem;
                                border-radius: 8px;
                                text-align: center;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                            '>
                                <div style='font-size: 2rem; margin-bottom: 0.5rem;'>{rank_emoji}</div>
                                <h4 style='margin: 0; color: #ffffff; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);'>{player['Spieler'].capitalize()}</h4>
                                <p style='margin: 0.3rem 0; color: #ffffff; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);'><strong>€{player['Gesamt']:.2f}</strong></p>
                                <p style='margin: 0; color: #ffffff; font-size: 0.9rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.5);'>{int(player['Anzahl'])} Strafen</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        with col:
                            st.info(f"**{['🥇 Platz 1', '🥈 Platz 2', '🥉 Platz 3'][i]}**\n\nNoch keine Strafen")
            else:
                st.success(f"🎉 Noch keine Strafen in KW {current_week}! Alle waren brav!")
                
        except Exception as e:
            st.error(f"❌ Fehler beim Laden der aktuellen Woche: {str(e)}")
        
        st.markdown("---")
        st.subheader("📋 Alle Strafen")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            # Capitalize player names for display in selectbox
            unique_players = sorted(df_strafen['Spieler'].unique())
            unique_players_display = [player.capitalize() for player in unique_players]
            spieler_filter_display = st.selectbox("Spieler", ["Alle"] + unique_players_display)
            
            # Map back to original case for filtering
            if spieler_filter_display != "Alle":
                spieler_filter = unique_players[unique_players_display.index(spieler_filter_display)]
            else:
                spieler_filter = "Alle"
        with col2:
            zeitraum = st.selectbox("Zeitraum", ["Alle", "Diese Woche", "Dieser Monat", "Letzte 3 Monate"])
        with col3:
            anzahl_anzeigen = st.selectbox("Anzeigen", [10, 20, 50, "Alle"], index=1)
        
        # Apply filters
        filtered_df = df_strafen.copy()
        
        if spieler_filter != "Alle":
            filtered_df = filtered_df[filtered_df['Spieler'] == spieler_filter]
        
        if zeitraum == "Diese Woche":
            filtered_df = filtered_df[filtered_df['Datum'] >= (get_german_now_naive() - timedelta(days=7))]
        elif zeitraum == "Dieser Monat":
            filtered_df = filtered_df[filtered_df['Datum'] >= (get_german_now_naive() - timedelta(days=30))]
        elif zeitraum == "Letzte 3 Monate":
            filtered_df = filtered_df[filtered_df['Datum'] >= (get_german_now_naive() - timedelta(days=90))]
        
        if anzahl_anzeigen != "Alle":
            filtered_df = filtered_df.head(anzahl_anzeigen)
        
        # Display table
        display_df = filtered_df.copy()
        display_df['Spieler'] = display_df['Spieler'].str.capitalize()
        display_df['Datum'] = display_df['Datum'].dt.strftime("%d.%m.%Y")
        display_df['Betrag'] = display_df['Betrag'].apply(lambda x: f"€{x:.2f}")
        
        # Reorder columns for better display
        column_order = ['Datum', 'Spieler', 'Strafe', 'Betrag', 'Zusatzinfo']
        display_df = display_df[column_order]
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        if len(filtered_df) > 0:
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                summe_gefiltert = filtered_df['Betrag'].sum()
                st.metric("Summe (gefiltert)", f"€{summe_gefiltert:.2f}")
            with col2:
                anzahl_gefiltert = len(filtered_df)
                st.metric("Anzahl (gefiltert)", anzahl_gefiltert)
    
    with tab2:
        st.subheader("📊 Strafen-Statistiken")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top offenders
            spieler_stats = df_strafen.groupby('Spieler').agg({
                'Betrag': ['sum', 'count', 'mean']
            }).round(2)
            spieler_stats.columns = ['Gesamt', 'Anzahl', 'Durchschnitt']
            spieler_stats = spieler_stats.reset_index().sort_values('Gesamt', ascending=True)
            # Capitalize player names for display
            spieler_stats['Spieler'] = spieler_stats['Spieler'].str.capitalize()
            
            fig1 = px.bar(spieler_stats, x='Gesamt', y='Spieler', 
                         title='Strafen-Gesamtsumme pro Spieler',
                         orientation='h')
            fig1.update_traces(marker_color='#ff6b6b')
            fig1.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Penalty types
            strafen_typen = df_strafen.groupby('Strafe')['Betrag'].sum().reset_index()
            
            fig2 = px.pie(strafen_typen, values='Betrag', names='Strafe',
                         title='Verteilung nach Strafenart')
            fig2.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig2, use_container_width=True)
        
        # Timeline
        st.subheader("📈 Strafen-Verlauf")
        
        timeline_df = df_strafen.copy()
        # Calculate ISO calendar week (KW)
        timeline_df['KW'] = timeline_df['Datum'].dt.isocalendar().week
        timeline_df['Jahr'] = timeline_df['Datum'].dt.year
        timeline_df['KW_Label'] = 'KW ' + timeline_df['KW'].astype(str) + '/' + timeline_df['Jahr'].astype(str).str[-2:]
        
        weekly_penalties = timeline_df.groupby(['KW', 'Jahr', 'KW_Label'])['Betrag'].sum().reset_index()
        weekly_penalties = weekly_penalties.sort_values(['Jahr', 'KW'])
        
        fig3 = px.line(weekly_penalties, x='KW_Label', y='Betrag',
                      title='Wöchentliche Strafen-Entwicklung',
                      line_shape='spline')
        fig3.update_traces(line_color='#ff6b6b', line_width=3, mode='lines+markers')
        fig3.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_title='Kalenderwoche',
            yaxis_title='Strafenbetrag (€)'
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        # Hall of Fame
        st.subheader("🏆 Strafen-Rangliste")
        
        hall_of_fame = spieler_stats.sort_values('Gesamt', ascending=False)
        
        for i, (_, row) in enumerate(hall_of_fame.head(5).iterrows()):
            emoji = ["👑", "🥈", "🥉", "4️⃣", "5️⃣"][i]
            platz = ["Champion", "Vize", "Bronze", "4. Platz", "5. Platz"][i]
            
            with st.container():
                col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
                with col1:
                    st.markdown(f"### {emoji}")
                with col2:
                    st.markdown(f"**{row['Spieler'].capitalize()}**\n{platz}")
                with col3:
                    st.metric("Gesamt", f"€{row['Gesamt']:.2f}")
                with col4:
                    st.metric("Anzahl", f"{int(row['Anzahl'])}")
    
    with tab3:
        st.subheader("🏆 Esel der Woche - Historie")
        
        # Generate weekly donkey history based on actual calendar weeks
        all_weeks = []
        current_date = get_german_now_naive()
        current_week = current_date.isocalendar()[1]
        current_year = current_date.year
        
        for i in range(8):  # Last 8 completed calendar weeks
            # Calculate the week number for i weeks ago (starting with last week)
            target_week = current_week - (i + 1)
            target_year = current_year
            
            # Handle year transition
            if target_week <= 0:
                target_year -= 1
                # Get the last week of the previous year (52 or 53)
                last_week_prev_year = datetime(target_year, 12, 28).isocalendar()[1]
                target_week = last_week_prev_year + target_week
            
            # Filter penalties for this specific calendar week
            week_penalties = df_strafen[
                (df_strafen['Datum'].dt.isocalendar().week == target_week) &
                (df_strafen['Datum'].dt.year == target_year)
            ]
            
            if len(week_penalties) > 0:
                week_stats = week_penalties.groupby('Spieler')['Betrag'].sum()
                week_donkey = week_stats.idxmax()
                donkey_amount = week_stats.max()
                
                # Calculate the actual start and end dates of this calendar week
                # Find first day of this week (Monday)
                jan4 = datetime(target_year, 1, 4)  # January 4th is always in week 1
                week1_monday = jan4 - timedelta(days=jan4.weekday())
                target_monday = week1_monday + timedelta(weeks=target_week - 1)
                target_sunday = target_monday + timedelta(days=6)
            else:
                week_donkey = "Niemand"
                donkey_amount = 0
                
                # Calculate week dates even if no penalties
                jan4 = datetime(target_year, 1, 4)
                week1_monday = jan4 - timedelta(days=jan4.weekday())
                target_monday = week1_monday + timedelta(weeks=target_week - 1)
                target_sunday = target_monday + timedelta(days=6)
            
            all_weeks.append({
                "Woche": f"KW {target_week}/{str(target_year)[-2:]}",
                "Datum": f"{target_monday.strftime('%d.%m.')} - {target_sunday.strftime('%d.%m.%Y')}",
                "Esel": week_donkey.capitalize() if week_donkey != "Niemand" else "Niemand",
                "Betrag": f"€{donkey_amount:.2f}" if donkey_amount > 0 else "€0.00"
            })
        
        # Display as table
        historie_df = pd.DataFrame(all_weeks)
        st.dataframe(historie_df, use_container_width=True, hide_index=True)
        
        # Donkey frequency analysis
        st.subheader("📊 Häufigste Esel")
        
        esel_häufigkeit = {}
        for week in all_weeks:
            if week['Esel'] != "Niemand":
                esel_häufigkeit[week['Esel']] = esel_häufigkeit.get(week['Esel'], 0) + 1
        
        if esel_häufigkeit:
            häufigkeit_df = pd.DataFrame(list(esel_häufigkeit.items()), 
                                       columns=['Spieler', 'Anzahl_Wochen'])
            häufigkeit_df = häufigkeit_df.sort_values('Anzahl_Wochen', ascending=False)
            # Capitalize player names for display
            häufigkeit_df['Spieler'] = häufigkeit_df['Spieler'].str.capitalize()
            
            fig4 = px.bar(häufigkeit_df, x='Spieler', y='Anzahl_Wochen',
                         title='Esel der Woche - Häufigkeit',
                         color='Anzahl_Wochen',
                         color_continuous_scale='Reds')
            fig4.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("Noch keine Esel-Historie vorhanden!")
    
    with tab4:
        st.subheader("📜 Regelwerk & Kataloge")
        
        # Sub-tabs for Biersatzung and Strafenkatalog
        regelwerk_tab1, regelwerk_tab2 = st.tabs(["🍺 Biersatzung", "📊 Strafenkatalog"])
        
        with regelwerk_tab1:
            st.subheader("🍺 Biersatzung")
            
            # Load Biersatzung from file
            try:
                with open("Biersatzung.txt", "r", encoding="utf-8") as f:
                    biersatzung_content = f.read()
                
                # Parse and format the beer regulations
                lines = biersatzung_content.split('\n')
                

                
                # Extract introduction and rules
                introduction = []
                rules = []
                current_section = "intro"
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Check if this is a numbered rule
                    if line[0].isdigit() and '.' in line[:5]:
                        current_section = "rules"
                        rules.append(line)
                    elif current_section == "intro":
                        introduction.append(line)
                    elif "Wenn jemand" in line or "€" in line:
                        # Additional important info
                        introduction.append(line)
                
                # Display introduction
                if introduction:
                    st.markdown("#### 📜 Grundlagen:")
                    for intro_line in introduction[:3]:  # Show first few lines
                        if intro_line and not intro_line.startswith("Im Folgenden"):
                            st.info(f"📋 {intro_line}")
                
                # Display rules in a more attractive format
                if rules:
                    st.markdown("#### 🎯 Kisten-Pflicht bei folgenden Anlässen:")
                    
                    # Create cards for rules
                    cols_per_row = 2
                    for i in range(0, len(rules), cols_per_row):
                        cols = st.columns(cols_per_row)
                        
                        for j, col in enumerate(cols):
                            if i + j < len(rules):
                                rule = rules[i + j]
                                
                                # Extract rule number and description
                                parts = rule.split('.', 1)
                                if len(parts) == 2:
                                    rule_num = parts[0].strip()
                                    rule_text = parts[1].strip()
                                    
                                    # Color coding for different types of rules
                                    if any(keyword in rule_text.lower() for keyword in ["geburtstag", "heirat", "vater"]):
                                        color = "#2ed573"  # Green for celebrations
                                        icon = "🎉"
                                    elif any(keyword in rule_text.lower() for keyword in ["strafe", "esel", "falsche"]):
                                        color = "#ff4757"  # Red for penalties
                                        icon = "⚠️"
                                    elif any(keyword in rule_text.lower() for keyword in ["tor", "hattrick", "kapitän"]):
                                        color = "#ffa502"  # Orange for sports achievements
                                        icon = "⚽"
                                    else:
                                        color = "#3742fa"  # Blue for regular rules
                                        icon = "🍺"
                                    
                                    with col:
                                        st.markdown(f"""
                                        <div style='
                                            background: linear-gradient(135deg, {color}33, {color}22);
                                            border-left: 4px solid {color};
                                            padding: 1rem;
                                            border-radius: 8px;
                                            margin: 0.5rem 0;
                                            box-shadow: 0 2px 4px rgba(0,0,0,0.15);
                                            border: 1px solid {color}44;
                                        '>
                                            <div style='display: flex; align-items: center; margin-bottom: 0.5rem;'>
                                                <span style='font-size: 1.2rem; margin-right: 0.5rem;'>{icon}</span>
                                                <strong style='color: #ffffff; font-size: 1.1rem; font-weight: 800; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);'>Regel {rule_num}</strong>
                                            </div>
                                            <p style='margin: 0; color: #ffffff; font-size: 0.9rem; line-height: 1.4; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);'>
                                                {rule_text}
                                            </p>
                                        </div>
                                        """, unsafe_allow_html=True)
                
                # Important notes section
                st.markdown("---")
                st.markdown("#### ⚠️ Wichtige Hinweise:")
                
                important_notes = [
                    "🍺 Ausschließlich König Pilsener (24 x 0,33l)",
                    "⏰ Bei Vergessen: 15€ Strafe",
                    "🥤 Softgetränke nur nach Absprache",
                    "🍻 Stubbis nur in besonderen Einzelfällen"
                ]
                
                for note in important_notes:
                    st.info(note)
                
            except FileNotFoundError:
                st.error("❌ Biersatzung.txt nicht gefunden!")
                st.info("Bitte stellen Sie sicher, dass die Datei 'Biersatzung.txt' im Hauptverzeichnis liegt.")
            except Exception as e:
                st.error(f"❌ Fehler beim Laden der Biersatzung: {str(e)}")
        
        with regelwerk_tab2:
            # Load penalty catalog from database instead of hardcoding
            st.markdown("### 🚨 Aktueller Strafenkatalog Saison 2025/26")
            
            try:
                penalty_data = db.get_penalty_types()
                penalty_catalog = [
                    {
                        "Beschreibung": p['description'], 
                        "Betrag": f"{p['default_amount_eur']:.2f} €".replace('.', ',')
                    } 
                    for p in penalty_data
                ]
            except Exception as e:
                st.error(f"❌ Fehler beim Laden des Strafenkatalogs: {str(e)}")
                penalty_catalog = [{"Beschreibung": "Fehler beim Laden", "Betrag": "0,00 €"}]
            
            # Display formatted penalties
            st.markdown("#### 💰 Strafen im Überblick:")
            
            # Display as cards
            cols_per_row = 2
            for i in range(0, len(penalty_catalog), cols_per_row):
                cols = st.columns(cols_per_row)
                
                for j, col in enumerate(cols):
                    if i + j < len(penalty_catalog):
                        penalty = penalty_catalog[i + j]
                        
                        # Color coding based on penalty amount
                        amount_str = penalty["Betrag"].replace("€", "").replace(",", ".")
                        try:
                            amount = float(amount_str)
                            if amount >= 50:
                                color = "#ff4757"  # Red for high penalties
                                icon = "🚨"
                            elif amount >= 20:
                                color = "#ffa502"  # Orange for medium penalties
                                icon = "⚠️"
                            elif amount >= 10:
                                color = "#ffda79"  # Yellow for low-medium penalties
                                icon = "💰"
                            elif amount >= 5:
                                color = "#7bed9f"  # Light green for medium-low penalties
                                icon = "💡"
                            else:
                                color = "#70a1ff"  # Blue for low penalties
                                icon = "📝"
                        except:
                            color = "#ddd"
                            icon = "📋"
                        
                        with col:
                            st.markdown(f"""
                            <div style='
                                background: linear-gradient(135deg, {color}33, {color}22);
                                border-left: 4px solid {color};
                                padding: 1rem;
                                border-radius: 8px;
                                margin: 0.5rem 0;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.15);
                                border: 1px solid {color}44;
                            '>
                                <div style='display: flex; align-items: center; margin-bottom: 0.5rem;'>
                                    <span style='font-size: 1.2rem; margin-right: 0.5rem;'>{icon}</span>
                                    <strong style='color: #ffffff; font-size: 1.1rem; font-weight: 800; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);'>{penalty["Betrag"]}</strong>
                                </div>
                                <p style='margin: 0; color: #ffffff; font-size: 0.9rem; line-height: 1.4; font-weight: 600; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);'>
                                    {penalty["Beschreibung"]}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
            
            # Important information sections
            st.markdown("---")
            st.markdown("#### 📋 Wichtige Regelungen:")
            
            # Important notes from the catalog
            important_notes = [
                "⚖️ Strafen bzgl. Karten gelten auch für die Trainer",
                "⏰ Zahlungsfrist: 4 Wochen ab Bekanntgabe durch Kassenwart",
                "💰 Nach Fristablauf: 5,00€ monatliche Verzugszinsen",
                "📞 Verspätungen können durch rechtzeitige Mitteilung gelindert werden",
                "👥 Entscheidungen obliegen Kassenwart, Mannschaftsrat und Trainern",
                "🍺 Strafen bzgl. Kisten siehe Biersatzung",
                "🏠 Nach Heimspiel: 1 Stunde Anwesenheit am Platz für Gespräche"
            ]
            
            for note in important_notes:
                st.info(note)
            
            # Outfit requirements
            st.markdown("---")
            st.markdown("#### 👕 Outfit-Regelungen:")
            
            outfit_info = """
            **Training:**
            - Shirt/Pulli/Regenjacke: grün
            - Hose: schwarz  
            - Stutzen/Socken: grün, schwarz oder weiß
            
            **Spiel:**
            - Präsentationsanzug komplett
            - Bei Verletzung: Präsentationsjacke/-shirt
            """
            
            st.markdown(outfit_info)
            
            # Beer penalty reference
            st.markdown("---")
            st.warning("🍺 **Bierstrafen:** Separate Verpflichtungen gemäß Biersatzung (siehe Biersatzung-Tab)")
        
        # Additional info
        st.markdown("---")
        st.info("""
        **📋 Wichtige Hinweise:**
        - Alle Strafen werden dem Mannschaftsrat gemeldet
        - Bierstrafen sind separate Verpflichtungen 
        - Bei Unstimmigkeiten entscheidet der Mannschaftsrat
        - Strafen müssen bis zum nächsten Spiel beglichen werden
        """)
    
    # User management tab for admins
    if tab5 is not None:
        with tab5:
            show_user_management() 