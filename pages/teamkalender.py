import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os

def show():
    st.title("📅 Teamkalender")
    st.subheader("Geburtstage und wichtige Termine")
    
    # Load real birthday data from CSV
    try:
        # Try to load the CSV file
        csv_path = "VB_Geburtstage.csv"
        if os.path.exists(csv_path):
            # Try different encodings, starting with latin-1 since we know it works
            encodings_to_try = ['latin-1', 'utf-8-sig', 'utf-8', 'cp1252']
            df_geburtstage_raw = None
            
            for encoding in encodings_to_try:
                try:
                    df_geburtstage_raw = pd.read_csv(csv_path, sep=';', encoding=encoding)
                    break
                except Exception:
                    continue
            
            if df_geburtstage_raw is not None:
                # Convert to our expected format
                geburtstage = []
                for _, row in df_geburtstage_raw.iterrows():
                    # Parse German date format DD.MM.YYYY
                    try:
                        geburtstag_str = str(row['Geburtstag']).strip()
                        
                        # Handle different date formats
                        if '.' in geburtstag_str:
                            parts = geburtstag_str.split('.')
                            if len(parts) == 3:
                                day, month, year = parts
                                # Clean up parts
                                day = day.zfill(2)
                                month = month.zfill(2)
                                
                                # Handle 2-digit years
                                if len(year) == 2:
                                    year = f"19{year}" if int(year) > 50 else f"20{year}"
                                
                                iso_date = f"{year}-{month}-{day}"
                                
                                # Determine position based on age (just for display purposes)
                                birth_year = int(year)
                                current_year = datetime.now().year
                                age = current_year - birth_year
                                
                                if age <= 20:
                                    position = "Baby"
                                elif age <= 25:
                                    position = "Youngster"
                                elif age <= 30:
                                    position = "Prime Time"
                                elif age <= 35:
                                    position = "Routinier"
                                else:
                                    position = "Opa"
                                
                                geburtstage.append({
                                    "Name": str(row['Name']).strip(),
                                    "Datum": iso_date,
                                    "Position": position
                                })
                    except Exception as e:
                        # Skip entries that can't be parsed, but continue with others
                        continue
            else:
                st.error("❌ CSV konnte mit keinem Encoding gelesen werden!")
                # Fallback to sample data
                geburtstage = [
                    {"Name": "Max Mustermann", "Datum": "1995-12-15", "Position": "Torwart"},
                    {"Name": "Thomas Schmidt", "Datum": "1992-01-22", "Position": "Verteidiger"},
                    {"Name": "Michael Weber", "Datum": "1993-03-08", "Position": "Mittelfeld"},
                    {"Name": "Stefan König", "Datum": "1991-07-14", "Position": "Stürmer"},
                ]
        else:
            st.error("❌ VB_Geburtstage.csv nicht gefunden! Verwende Beispieldaten.")
            # Fallback to sample data
            geburtstage = [
                {"Name": "Max Mustermann", "Datum": "1995-12-15", "Position": "Torwart"},
                {"Name": "Thomas Schmidt", "Datum": "1992-01-22", "Position": "Verteidiger"},
                {"Name": "Michael Weber", "Datum": "1993-03-08", "Position": "Mittelfeld"},
                {"Name": "Stefan König", "Datum": "1991-07-14", "Position": "Stürmer"},
            ]
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Geburtstagsdaten: {e}")
        # Fallback to sample data
        geburtstage = [
            {"Name": "Max Mustermann", "Datum": "1995-12-15", "Position": "Torwart"},
            {"Name": "Thomas Schmidt", "Datum": "1992-01-22", "Position": "Verteidiger"},
        ]
    
    # Convert to DataFrame
    df_geburtstage = pd.DataFrame(geburtstage)
    df_geburtstage['Datum'] = pd.to_datetime(df_geburtstage['Datum'])
    df_geburtstage['Geburtstag_dieses_Jahr'] = df_geburtstage['Datum'].apply(
        lambda x: datetime(datetime.now().year, x.month, x.day)
    )
    
    # Calculate days until birthday
    today = datetime.now()
    df_geburtstage['Tage_bis_Geburtstag'] = df_geburtstage['Geburtstag_dieses_Jahr'].apply(
        lambda x: (x - today).days if (x - today).days >= 0 else (x.replace(year=x.year + 1) - today).days
    )
    
    # Sort by next birthday
    df_geburtstage = df_geburtstage.sort_values('Tage_bis_Geburtstag')
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["🎂 Anstehende Geburtstage", "📊 Geburtstagsübersicht", "➕ Neuen Geburtstag hinzufügen"])
    
    with tab1:
        st.subheader("Nächste Geburtstage")
        
        # Next 5 birthdays (or all if less than 5)
        next_birthdays = min(5, len(df_geburtstage))
        for i, row in df_geburtstage.head(next_birthdays).iterrows():
            tage = row['Tage_bis_Geburtstag']
            
            if tage == 0:
                delta_text = "Heute! 🎉"
                delta_color = "normal"
            elif tage == 1:
                delta_text = "Morgen"
                delta_color = "normal"
            else:
                delta_text = f"in {tage} Tagen"
                delta_color = "normal"
            
            # Calculate age
            alter = datetime.now().year - row['Datum'].year
            if datetime.now() < datetime(datetime.now().year, row['Datum'].month, row['Datum'].day):
                alter -= 1  # Birthday hasn't happened this year yet
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                # Special styling for today's birthday
                if tage == 0:
                    st.markdown(f"""
                    <div style='
                        background: linear-gradient(135deg, #ff6b6b, #ee5a52);
                        padding: 0.5rem 1rem;
                        border-radius: 8px;
                        color: white;
                        margin: 0.2rem 0;
                        border-left: 4px solid #ffffff;
                    '>
                        <div style='display: flex; align-items: center; gap: 0.5rem;'>
                            <span style='font-size: 1.2rem;'>🎉</span>
                            <div>
                                <strong style='font-size: 1rem;'>{row['Name']}</strong>
                                <div style='font-size: 0.9rem; opacity: 0.9;'>wird heute {alter + 1} Jahre alt!</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.metric(
                        label=f"🎂 {row['Name']}",
                        value=f"{alter + 1} Jahre",
                        delta=delta_text
                    )
            with col2:
                st.write(f"**Kategorie:** {row['Position']}")
            with col3:
                geburtstag_formatted = row['Geburtstag_dieses_Jahr'].strftime("%d.%m.%Y")
                st.write(f"**Datum:** {geburtstag_formatted}")
        
        st.markdown("---")
        
        # All birthdays table
        st.subheader("Alle Geburtstage")
        
        # Format data for display
        display_df = df_geburtstage.copy()
        display_df['Geburtstag'] = display_df['Geburtstag_dieses_Jahr'].dt.strftime("%d.%m.%Y")
        display_df['Alter'] = display_df['Datum'].apply(
            lambda x: datetime.now().year - x.year if datetime.now() >= datetime(datetime.now().year, x.month, x.day) 
            else datetime.now().year - x.year - 1
        )
        display_df['Tage bis Geburtstag'] = display_df['Tage_bis_Geburtstag']
        
        # Add emoji indicators
        display_df['Status'] = display_df['Tage_bis_Geburtstag'].apply(
            lambda x: "🎉 HEUTE!" if x == 0 else "🔥 Morgen" if x == 1 else f"📅 {x} Tage"
        )
        
        st.dataframe(
            display_df[['Name', 'Position', 'Geburtstag', 'Alter', 'Status']],
            use_container_width=True,
            hide_index=True
        )
    
    with tab2:
        # Birthday statistics
        st.subheader("📊 Geburtstagsstatistiken")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Birthdays by month
            df_geburtstage['Monat'] = df_geburtstage['Datum'].dt.month
            monat_counts = df_geburtstage.groupby('Monat').size()
            
            monat_namen = {
                1: 'Januar', 2: 'Februar', 3: 'März', 4: 'April',
                5: 'Mai', 6: 'Juni', 7: 'Juli', 8: 'August',
                9: 'September', 10: 'Oktober', 11: 'November', 12: 'Dezember'
            }
            
            monat_data = []
            for monat in range(1, 13):
                monat_data.append({
                    'Monat': monat_namen[monat],
                    'Anzahl': monat_counts.get(monat, 0)
                })
            
            import plotly.express as px
            fig = px.bar(monat_data, x='Monat', y='Anzahl', 
                        title='Geburtstage nach Monaten')
            fig.update_traces(marker_color='#1e3c72')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis={'categoryorder': 'array', 'categoryarray': [monat_namen[i] for i in range(1, 13)]}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Age distribution
            alter_data = df_geburtstage['Datum'].apply(
                lambda x: datetime.now().year - x.year if datetime.now() >= datetime(datetime.now().year, x.month, x.day) 
                else datetime.now().year - x.year - 1
            )
            
            # Create age groups for better visualization
            age_groups = []
            for age in alter_data:
                if age < 20:
                    age_groups.append("Baby")
                elif age < 25:
                    age_groups.append("Youngster")
                elif age < 30:
                    age_groups.append("Prime Time")
                elif age < 35:
                    age_groups.append("Routinier")
                else:
                    age_groups.append("Opa")
            
            age_group_counts = pd.Series(age_groups).value_counts()
            
            fig2 = px.pie(values=age_group_counts.values, names=age_group_counts.index,
                         title='Altersverteilung im Team')
            fig2.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig2, use_container_width=True)
        
        # Fun facts
        st.subheader("🎯 Geburtstagsinfos")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            ältester = df_geburtstage.loc[df_geburtstage['Datum'].idxmin()]
            ältester_alter = datetime.now().year - ältester['Datum'].year
            st.metric("👴 Ältester Spieler", ältester['Name'], 
                     f"{ältester_alter} Jahre")
        
        with col2:
            jüngster = df_geburtstage.loc[df_geburtstage['Datum'].idxmax()]
            jüngster_alter = datetime.now().year - jüngster['Datum'].year
            if datetime.now() < datetime(datetime.now().year, jüngster['Datum'].month, jüngster['Datum'].day):
                jüngster_alter -= 1
            st.metric("👶 Jüngster Spieler", jüngster['Name'], 
                     f"{jüngster_alter} Jahre")
        
        with col3:
            nächster = df_geburtstage.iloc[0]
            st.metric("🎂 Nächster Geburtstag", nächster['Name'], 
                     f"in {nächster['Tage_bis_Geburtstag']} Tagen")
        
        # Additional statistics
        st.markdown("---")
        st.subheader("📈 Weitere Statistiken")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            durchschnittsalter = alter_data.mean()
            st.metric("📊 Durchschnittsalter", f"{durchschnittsalter:.1f} Jahre")
        
        with col2:
            geburtstage_nächste_30_tage = len(df_geburtstage[df_geburtstage['Tage_bis_Geburtstag'] <= 30])
            st.metric("📅 Nächste 30 Tage", f"{geburtstage_nächste_30_tage} Geburtstage")
        
        with col3:
            geburtstage_diesen_monat = len(df_geburtstage[df_geburtstage['Datum'].dt.month == datetime.now().month])
            st.metric("🗓️ Diesen Monat", f"{geburtstage_diesen_monat} Geburtstage")
        
        with col4:
            st.metric("👥 Spieler gesamt", len(df_geburtstage))
    
    with tab3:
        st.subheader("➕ Neuen Geburtstag hinzufügen")
        
        with st.form("add_birthday"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Name des Spielers")
            
            with col2:
                geburtsdatum = st.date_input("Geburtsdatum")
            
            submitted = st.form_submit_button("Geburtstag hinzufügen")
            
            if submitted:
                if name and geburtsdatum:
                    try:
                        # Format the new entry
                        csv_format = f"{name};{geburtsdatum.strftime('%d.%m.%Y')}"
                        
                        # Check if CSV file exists
                        csv_path = "VB_Geburtstage.csv"
                        if os.path.exists(csv_path):
                            # Read existing file to check for duplicates
                            try:
                                existing_df = pd.read_csv(csv_path, sep=';', encoding='latin-1')
                                
                                # Check if name already exists
                                if name in existing_df['Name'].values:
                                    st.warning(f"⚠️ {name} ist bereits in der Liste vorhanden!")
                                else:
                                    # Try to append new entry to the CSV file
                                    try:
                                        with open(csv_path, 'a', encoding='latin-1', newline='') as file:
                                            file.write(f"\n{csv_format}")
                                        
                                        st.success(f"✅ {name} wurde erfolgreich hinzugefügt!")
                                        st.balloons()
                                        
                                        # Show the added entry
                                        st.info(f"📝 Neuer Eintrag: {csv_format}")
                                        
                                        # Suggest refreshing the page to see changes
                                        st.info("🔄 Aktualisieren Sie die Seite, um den neuen Eintrag in der Liste zu sehen.")
                                        
                                    except PermissionError:
                                        st.error("❌ **Permission-Fehler:** Kann nicht in die CSV-Datei schreiben!")
                                        st.warning("🔒 **Mögliche Lösungen:**")
                                        st.write("• Schließen Sie Excel oder andere Programme, die die CSV-Datei verwenden")
                                        st.write("• Überprüfen Sie, ob die Datei schreibgeschützt ist")
                                        st.write("• Starten Sie die App als Administrator")
                                        st.info("💡 **Manuelle Eingabe:** Fügen Sie diese Zeile zur CSV-Datei hinzu:")
                                        st.code(csv_format)
                                        
                                    except Exception as write_error:
                                        st.error(f"❌ Schreibfehler: {write_error}")
                                        st.info("💡 **Manuelle Eingabe erforderlich:**")
                                        st.code(f"Für CSV-Datei: {csv_format}")
                                     
                            except Exception as e:
                                st.error(f"❌ Fehler beim Lesen der bestehenden Datei: {e}")
                                st.info("💡 Fallback: Manuelle Eingabe erforderlich")
                                st.code(f"Für CSV-Datei: {csv_format}")
                        
                    except Exception as e:
                        st.error(f"❌ Unerwarteter Fehler: {e}")
                        # Fallback to manual instructions
                        csv_format = f"{name};{geburtsdatum.strftime('%d.%m.%Y')}"
                        st.info("💡 Bitte manuell zur CSV-Datei hinzufügen:")
                        st.code(f"Für CSV-Datei: {csv_format}")
                        
                else:
                    st.error("❌ Bitte alle Felder ausfüllen.") 