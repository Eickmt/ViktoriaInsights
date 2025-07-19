import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import sys

# Add the parent directory to the path to import database helper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database_helper import db
from timezone_helper import get_german_now, get_german_now_naive, make_naive_german_datetime, calculate_days_until_birthday



def calculate_age(birth_date):
    """Berechnet das Alter basierend auf dem Geburtsdatum in deutscher Zeit"""
    today = get_german_now()
    birth_this_year = make_naive_german_datetime(today.year, birth_date.month, birth_date.day)
    age = today.year - birth_date.year
    if get_german_now_naive() < birth_this_year:
        age -= 1  # Birthday hasn't happened this year yet
    return age

def show():
    st.title("📅 Teamkalender & Geburtstage")
    st.subheader("Termine, Events und Geburtstage der Mannschaft")
    
    # Add CSS for better input field contrast
    st.markdown("""
    <style>
    /* Selectbox styling */
    .stSelectbox > div > div {
        background-color: #ffffff !important;
        border: 2px solid #dee2e6 !important;
        border-radius: 8px !important;
        color: #212529 !important;
        font-weight: 600 !important;
    }
    .stSelectbox > div > div:focus-within {
        border-color: #0d6efd !important;
        box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25) !important;
    }
    
    /* Dropdown options styling */
    .stSelectbox [data-baseweb="select"] {
        background-color: #ffffff !important;
    }
    .stSelectbox [data-baseweb="popover"] {
        background-color: #ffffff !important;
    }
    .stSelectbox [role="option"] {
        background-color: #ffffff !important;
        color: #212529 !important;
        font-weight: 500 !important;
    }
    .stSelectbox [role="option"]:hover {
        background-color: #f8f9fa !important;
        color: #000000 !important;
    }
    .stSelectbox [aria-selected="true"] {
        background-color: #e3f2fd !important;
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    /* ENHANCED Dropdown search input styling with multiple selectors */
    .stSelectbox [data-baseweb="input"] input,
    .stSelectbox input[type="text"],
    .stSelectbox input,
    div[data-baseweb="select"] input,
    div[data-baseweb="popover"] input,
    [data-testid="stSelectbox"] input {
        background-color: #ffffff !important;
        color: #212529 !important;
        border: 1px solid #dee2e6 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }
    
    .stSelectbox [data-baseweb="input"] input:focus,
    .stSelectbox input[type="text"]:focus,
    .stSelectbox input:focus,
    div[data-baseweb="select"] input:focus,
    div[data-baseweb="popover"] input:focus,
    [data-testid="stSelectbox"] input:focus {
        background-color: #ffffff !important;
        color: #212529 !important;
        border-color: #0d6efd !important;
        outline: none !important;
        box-shadow: 0 0 0 2px rgba(13, 110, 253, 0.25) !important;
    }
    
    .stSelectbox [data-baseweb="input"] input::placeholder,
    .stSelectbox input[type="text"]::placeholder,
    .stSelectbox input::placeholder,
    div[data-baseweb="select"] input::placeholder,
    div[data-baseweb="popover"] input::placeholder,
    [data-testid="stSelectbox"] input::placeholder {
        color: #6c757d !important;
        opacity: 1 !important;
    }
    
    /* Universal input styling within selectbox */
    .stSelectbox * input {
        background-color: #ffffff !important;
        color: #212529 !important;
        border: 1px solid #dee2e6 !important;
        font-weight: 600 !important;
    }
    
    .stSelectbox * input:focus {
        background-color: #ffffff !important;
        color: #212529 !important;
        border-color: #0d6efd !important;
        outline: none !important;
    }
    
    /* Text input styling */
    .stTextInput > div > div > input {
        background-color: #ffffff !important;
        border: 2px solid #dee2e6 !important;
        border-radius: 8px !important;
        color: #212529 !important;
        font-weight: 600 !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #0d6efd !important;
        box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25) !important;
    }
    
    /* Date input styling */
    .stDateInput > div > div > input {
        background-color: #ffffff !important;
        border: 2px solid #dee2e6 !important;
        border-radius: 8px !important;
        color: #212529 !important;
        font-weight: 600 !important;
    }
    .stDateInput > div > div > input:focus {
        border-color: #0d6efd !important;
        box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25) !important;
    }
    
    /* Labels styling */
    .stTextInput label, .stDateInput label {
        color: #212529 !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Load birthday data from database
    try:
        # Lade Geburtstage aus der Datenbank
        df_geburtstage_raw = db.get_birthdays()
        
        if df_geburtstage_raw is not None and len(df_geburtstage_raw) > 0:
            # Convert to our expected format
            geburtstage = []
            for _, row in df_geburtstage_raw.iterrows():
                try:
                    # Determine position based on age (just for display purposes)
                    birth_year = row['Geburtstag_parsed'].year
                    current_year = get_german_now().year
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
                        "Datum": row['Geburtstag_parsed'].strftime('%Y-%m-%d'),
                        "Position": position,
                        "Rolle": row['Rolle'] if pd.notna(row['Rolle']) else "Unbekannt"
                    })
                except Exception as e:
                    # Skip entries that can't be parsed, but continue with others
                    st.warning(f"⚠️ Fehler beim Verarbeiten eines Geburtstagseintrags: {e}")
                    continue
        else:
            st.error("❌ Keine Geburtstage in der Datenbank gefunden")
            return
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Geburtstagsdaten: {e}")
        return
    
    # Convert to DataFrame and ensure we have data
    if not geburtstage:
        st.error("❌ Keine gültigen Geburtstagsdaten verfügbar")
        return
        
    df_geburtstage = pd.DataFrame(geburtstage)
    
    # Ensure the 'Datum' column exists
    if 'Datum' not in df_geburtstage.columns:
        st.error("❌ Fehler: 'Datum' Spalte nicht gefunden in den Geburtstagsdaten")
        st.write("Verfügbare Spalten:", df_geburtstage.columns.tolist())
        return
    
    df_geburtstage['Datum'] = pd.to_datetime(df_geburtstage['Datum'])
    df_geburtstage['Geburtstag_dieses_Jahr'] = df_geburtstage['Datum'].apply(
        lambda x: make_naive_german_datetime(get_german_now().year, x.month, x.day)
    )
    
    # Calculate days until birthday
    today = get_german_now_naive()
    df_geburtstage['Tage_bis_Geburtstag'] = df_geburtstage['Geburtstag_dieses_Jahr'].apply(
        lambda x: calculate_days_until_birthday(x, today)
    )
    
    # Sort by next birthday
    df_geburtstage = df_geburtstage.sort_values('Tage_bis_Geburtstag')
    
    # Tabs for different views
    tab1, tab2 = st.tabs(["🎂 Anstehende Geburtstage", "📊 Geburtstagsübersicht"])
    
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
            alter = calculate_age(row['Datum'])
            
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
                                <strong style='font-size: 1rem;'>{row['Name'].capitalize()}</strong>
                                <div style='font-size: 0.9rem; opacity: 0.9;'>wird heute {alter + 1} Jahre alt!</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.metric(
                        label=f"🎂 {row['Name'].capitalize()}",
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
        display_df['Name'] = display_df['Name'].str.capitalize()
        display_df['Geburtstag'] = display_df['Geburtstag_dieses_Jahr'].dt.strftime("%d.%m.%Y")
        display_df['Alter'] = display_df['Datum'].apply(
            lambda x: calculate_age(x)
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
        # Kalender
        st.subheader("📅 Kalender")
        
        # Monatsselektor
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            current_date = get_german_now_naive()
            selected_year = st.selectbox(
                "Jahr", 
                options=list(range(current_date.year - 2, current_date.year + 3)), 
                index=2,  # Aktuelles Jahr als Standard
                key="calendar_year"
            )
        
        with col2:
            month_names = {
                1: 'Januar', 2: 'Februar', 3: 'März', 4: 'April',
                5: 'Mai', 6: 'Juni', 7: 'Juli', 8: 'August',
                9: 'September', 10: 'Oktober', 11: 'November', 12: 'Dezember'
            }
            month_options = [(i, month_names[i]) for i in range(1, 13)]
            selected_month = st.selectbox(
                "Monat",
                options=month_options,
                format_func=lambda x: x[1],
                index=current_date.month - 1,  # Aktueller Monat als Standard
                key="calendar_month"
            )[0]
        
        with col3:
            # Info über Navigation
            st.info("💡 Verwenden Sie die Dropdowns oben, um Monat/Jahr zu ändern")
        
        # Einfacher statischer Kalender ohne externe Komponenten
        st.write("---")
        
        # Kalender für den gewählten Monat erstellen
        cal = calendar.Calendar(firstweekday=0)  # Montag als erster Tag der Woche
        month_days = cal.monthdayscalendar(selected_year, selected_month)
        
        # Deutsche Monatsnamen
        month_names_de = {
            1: 'Januar', 2: 'Februar', 3: 'März', 4: 'April',
            5: 'Mai', 6: 'Juni', 7: 'Juli', 8: 'August',
            9: 'September', 10: 'Oktober', 11: 'November', 12: 'Dezember'
        }
        
        # Geburtstage für den gewählten Monat filtern
        birthdays_this_month = df_geburtstage[df_geburtstage['Datum'].dt.month == selected_month]
        birthday_dict = {}
        for _, row in birthdays_this_month.iterrows():
            day = row['Datum'].day
            if day not in birthday_dict:
                birthday_dict[day] = []
            birthday_dict[day].append(row['Name'].capitalize())
        
        # Heutiges Datum
        today = get_german_now_naive()
        is_current_month = (today.year == selected_year and today.month == selected_month)
        today_day = today.day if is_current_month else None
        
        # Kalender-Header
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #2d5016 0%, #3e6b1f 100%);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            color: white;
            font-size: 1.5rem;
            font-weight: bold;
            margin: 15px 0;
        ">
            📅 {month_names_de[selected_month]} {selected_year}
        </div>
        """, unsafe_allow_html=True)
        
        # Wochentage-Header
        weekdays = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
        header_cols = st.columns(7)
        for i, weekday in enumerate(weekdays):
            with header_cols[i]:
                st.markdown(f"""
                <div style="
                    background: #2d5016;
                    color: white;
                    text-align: center;
                    padding: 8px;
                    font-weight: bold;
                    border-radius: 5px;
                    margin: 2px;
                ">{weekday}</div>
                """, unsafe_allow_html=True)
        
        # Kalendertage
        for week in month_days:
            week_cols = st.columns(7)
            for i, day in enumerate(week):
                with week_cols[i]:
                    if day == 0:
                        # Leerer Tag
                        st.markdown('<div style="height: 60px;"></div>', unsafe_allow_html=True)
                    else:
                        # Bestimme Farben und Status
                        is_today = (day == today_day)
                        has_birthday = (day in birthday_dict)
                        
                        if is_today and has_birthday:
                            bg_color = "#ff6b6b"
                            text_color = "white"
                            border = "3px solid #ffd700"
                            emoji = "🎉"
                        elif is_today:
                            bg_color = "#ff6b6b"
                            text_color = "white"
                            border = "2px solid white"
                            emoji = "📅"
                        elif has_birthday:
                            bg_color = "#2d5016"
                            text_color = "white"
                            border = "2px solid #4a7c23"
                            emoji = "🎂"
                        else:
                            bg_color = "white"
                            text_color = "#333"
                            border = "1px solid #ddd"
                            emoji = ""
                        
                        # Namen für Anzeige
                        names_display = ""
                        if has_birthday:
                            names = birthday_dict[day]
                            if len(names) == 1:
                                name = names[0]
                                if len(name) > 8:
                                    names_display = f'<div style="font-size: 0.7rem; margin-top: 3px;">{name[:8]}...</div>'
                                else:
                                    names_display = f'<div style="font-size: 0.7rem; margin-top: 3px;">{name}</div>'
                            else:
                                names_display = f'<div style="font-size: 0.7rem; margin-top: 3px;">{len(names)} 🎂</div>'
                        
                        st.markdown(f"""
                        <div style="
                            background: {bg_color};
                            color: {text_color};
                            text-align: center;
                            padding: 8px 4px;
                            border-radius: 8px;
                            min-height: 60px;
                            border: {border};
                            margin: 2px;
                            display: flex;
                            flex-direction: column;
                            justify-content: center;
                        " title="{', '.join(birthday_dict.get(day, []))}">
                            <div style="font-size: 1rem; font-weight: bold;">{day}</div>
                            {names_display}
                        </div>
                        """, unsafe_allow_html=True)
        
        st.write("---")
            
        # Einfache Geburtstagsliste für den gewählten Monat
        birthdays_selected_month = df_geburtstage[df_geburtstage['Datum'].dt.month == selected_month]
        if len(birthdays_selected_month) > 0:
            st.markdown("### 🎂 Geburtstage in diesem Monat")
            for _, row in birthdays_selected_month.sort_values('Datum').iterrows():
                day = row['Datum'].day
                age_next = calculate_age(row['Datum']) + 1
                st.write(f"📅 **{day}.{selected_month}.** {row['Name'].capitalize()} wird **{age_next} Jahre** alt")
        else:
            st.info("📭 Keine Geburtstage in diesem Monat")
        

        
        st.markdown("---")
        
        # Geburtstagsinfos (KPIs)
        st.subheader("🎯 Geburtstagsinfos")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            # Filter nur auf Rolle "Spieler" für KPI "Ältester Spieler"
            spieler_nur = df_geburtstage[df_geburtstage['Rolle'] == 'Spieler']
            if len(spieler_nur) > 0:
                ältester = spieler_nur.loc[spieler_nur['Datum'].idxmin()]
                ältester_alter = calculate_age(ältester['Datum'])
                st.metric("👴 Ältester Spieler", ältester['Name'].capitalize(), 
                         f"{ältester_alter} Jahre")
            else:
                st.metric("👴 Ältester Spieler", "Keine Daten", "—")
        
        with col2:
            jüngster = df_geburtstage.loc[df_geburtstage['Datum'].idxmax()]
            jüngster_alter = calculate_age(jüngster['Datum'])
            st.metric("👶 Jüngster Spieler", jüngster['Name'].capitalize(), 
                     f"{jüngster_alter} Jahre")
        
        with col3:
            nächster = df_geburtstage.iloc[0]
            st.metric("🎂 Nächster Geburtstag", nächster['Name'].capitalize(), 
                     f"in {nächster['Tage_bis_Geburtstag']} Tagen")
        
        st.markdown("---")
        
        # Geburtstagsstatistiken (Diagramme)
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
                lambda x: calculate_age(x)
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
        
        st.markdown("---")
        
        # Weitere Statistiken
        st.subheader("📈 Weitere Statistiken")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Filter nur auf Rolle "Spieler" für Durchschnittsalter
            spieler_nur = df_geburtstage[df_geburtstage['Rolle'] == 'Spieler']
            if len(spieler_nur) > 0:
                spieler_alter_data = spieler_nur['Datum'].apply(lambda x: calculate_age(x))
                durchschnittsalter = spieler_alter_data.mean()
                st.metric("📊 Durchschnittsalter", f"{durchschnittsalter:.1f} Jahre")
            else:
                st.metric("📊 Durchschnittsalter", "Keine Daten", "—")
        
        with col2:
            geburtstage_nächste_30_tage = len(df_geburtstage[df_geburtstage['Tage_bis_Geburtstag'] <= 30])
            st.metric("📅 Nächste 30 Tage", f"{geburtstage_nächste_30_tage} Geburtstage")
        
        with col3:
            geburtstage_diesen_monat = len(df_geburtstage[df_geburtstage['Datum'].dt.month == get_german_now().month])
            st.metric("🗓️ Diesen Monat", f"{geburtstage_diesen_monat} Geburtstage") 