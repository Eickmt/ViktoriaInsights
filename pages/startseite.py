import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import os
import requests

@st.cache_data(ttl=600)  # Cache für 10 Minuten
def get_weather_data(city="Buchholz", api_key=None):
    """
    Fetch weather data from OpenWeatherMap API
    Cached for 10 minutes to avoid excessive API calls
    """
    if not api_key:
        return None
    
    try:
        # OpenWeatherMap API endpoint
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': f"{city},DE",
            'appid': api_key,
            'units': 'metric',
            'lang': 'de'
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            weather_info = {
                'temperature': round(data['main']['temp']),
                'description': data['weather'][0]['description'].title(),
                'humidity': data['main']['humidity'],
                'wind_speed': round(data['wind']['speed'] * 3.6, 1),  # Convert m/s to km/h
                'emoji': get_weather_emoji(data['weather'][0]['main'])
            }
            
            return weather_info
        else:
            return None
            
    except Exception as e:
        return None

def get_weather_emoji(weather_main):
    """
    Get emoji based on weather condition
    """
    weather_emojis = {
        'Clear': '☀️',
        'Clouds': '☁️',
        'Rain': '🌧️',
        'Drizzle': '🌦️',
        'Thunderstorm': '⛈️',
        'Snow': '❄️',
        'Mist': '🌫️',
        'Fog': '🌫️'
    }
    return weather_emojis.get(weather_main, '🌤️')

def show():
    st.title("⚽ Willkommen bei ViktoriaInsights")
    
    # Load real birthday data from CSV for next birthday calculation
    next_birthday_name = "Niemand"
    next_birthday_days = 0
    
    # Debug information
    debug_info = []
    
    try:
        csv_path = "VB_Geburtstage.csv"
        debug_info.append(f"🔍 Suche CSV-Datei: {csv_path}")
        
        if os.path.exists(csv_path):
            debug_info.append("✅ CSV-Datei gefunden")
            
            # Try different encodings
            encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
            df_geburtstage_raw = None
            
            for encoding in encodings_to_try:
                try:
                    df_geburtstage_raw = pd.read_csv(csv_path, sep=';', encoding=encoding)
                    debug_info.append(f"✅ CSV gelesen mit {encoding}")
                    break
                except Exception as e:
                    debug_info.append(f"❌ Fehler mit {encoding}: {str(e)[:50]}")
                    continue
            
            if df_geburtstage_raw is not None:
                debug_info.append(f"📊 {len(df_geburtstage_raw)} Einträge gefunden")
                debug_info.append(f"🔧 Spalten: {list(df_geburtstage_raw.columns)}")
                
                # Show first few entries for debugging
                if len(df_geburtstage_raw) > 0:
                    first_entry = df_geburtstage_raw.iloc[0]
                    debug_info.append(f"📝 Erstes Beispiel: {first_entry['Name']} - {first_entry['Geburtstag']}")
                
                # Convert to our expected format
                geburtstage = []
                for _, row in df_geburtstage_raw.iterrows():
                    try:
                        geburtstag_str = str(row['Geburtstag']).strip()
                        debug_info.append(f"🔄 Verarbeite: {row['Name']} - {geburtstag_str}")
                        
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
                                
                                geburtstage.append({
                                    "Name": str(row['Name']).strip(),
                                    "Datum": iso_date
                                })
                                debug_info.append(f"✅ Erfolgreich: {row['Name']} - {iso_date}")
                            else:
                                debug_info.append(f"❌ Ungültiges Datumsformat: {geburtstag_str}")
                        else:
                            debug_info.append(f"❌ Kein Punkt im Datum gefunden: {geburtstag_str}")
                    except Exception as e:
                        debug_info.append(f"❌ Fehler bei {row.get('Name', 'UNBEKANNT')}: {str(e)}")
                        continue
                
                debug_info.append(f"🎯 {len(geburtstage)} Geburtstage erfolgreich verarbeitet")
                
                if geburtstage:
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
                    
                    # Get next birthday
                    df_geburtstage = df_geburtstage.sort_values('Tage_bis_Geburtstag')
                    if len(df_geburtstage) > 0:
                        next_birthday = df_geburtstage.iloc[0]
                        next_birthday_name = next_birthday['Name']
                        next_birthday_days = next_birthday['Tage_bis_Geburtstag']
                        debug_info.append(f"🎉 Nächster Geburtstag: {next_birthday_name} in {next_birthday_days} Tagen")
                else:
                    debug_info.append("❌ Keine gültigen Geburtstage gefunden")
            else:
                debug_info.append("❌ CSV konnte mit keinem Encoding gelesen werden")
        else:
            debug_info.append("❌ CSV-Datei nicht gefunden")
            debug_info.append(f"📁 Aktuelles Verzeichnis: {os.getcwd()}")
            debug_info.append(f"📋 Dateien im Verzeichnis: {os.listdir('.')}")
    except Exception as e:
        debug_info.append(f"❌ Unerwarteter Fehler: {str(e)}")
    
    # Load real training data for training quote calculation
    training_participants = 0
    training_delta = 0
    training_delta_text = ""
    
    try:
        # Load training victories data
        df_training = pd.read_csv("VB_Trainingsspielsiege.csv", sep=";")
        
        # Get date columns (exclude Spielername)
        date_columns = [col for col in df_training.columns if col != 'Spielername']
        
        if len(date_columns) > 0:
            # Convert date columns to datetime for sorting
            date_mapping = {}
            german_months = {
                'Jan': 'Jan', 'Feb': 'Feb', 'Mrz': 'Mar', 'Apr': 'Apr',
                'Mai': 'May', 'Jun': 'Jun', 'Jul': 'Jul', 'Aug': 'Aug',
                'Sep': 'Sep', 'Okt': 'Oct', 'Nov': 'Nov', 'Dez': 'Dec'
            }
            
            for date_str in date_columns:
                try:
                    # Convert German months to English
                    date_english = date_str
                    for de_month, en_month in german_months.items():
                        if de_month in date_str:
                            date_english = date_str.replace(de_month, en_month)
                            break
                    
                    # Parse date
                    if any(year in date_english for year in ['2024', '2025', '2026']):
                        parsed_date = pd.to_datetime(date_english, format="%d. %b %Y")
                    else:
                        date_with_year = f"{date_english} 2024"
                        parsed_date = pd.to_datetime(date_with_year, format="%d. %b %Y")
                    
                    date_mapping[date_str] = parsed_date
                except:
                    continue
            
            if date_mapping:
                # Sort dates to get the most recent training
                sorted_dates = sorted(date_mapping.items(), key=lambda x: x[1], reverse=True)
                
                # Get participants for latest training (2 * number of victories)
                latest_training_date = sorted_dates[0][0]
                latest_victories = df_training[latest_training_date].sum()
                training_participants = int(latest_victories * 2) if pd.notna(latest_victories) else 0
                
                # Calculate delta compared to previous training
                if len(sorted_dates) > 1:
                    previous_training_date = sorted_dates[1][0]
                    previous_victories = df_training[previous_training_date].sum()
                    previous_participants = int(previous_victories * 2) if pd.notna(previous_victories) else 0
                    
                    training_delta = training_participants - previous_participants
                    if training_delta > 0:
                        training_delta_text = f"+ {training_delta}"
                    elif training_delta < 0:
                        training_delta_text = f"{training_delta}"
                    else:
                        training_delta_text = "±0"
                else:
                    training_delta_text = "Erstes Training"
        
    except Exception as e:
        # Fallback to default values if CSV can't be loaded
        training_participants = 0
        training_delta_text = "Keine Daten"
    
    # Calculate current donkey of the week based on penalties
    current_donkey = "Niemand"
    donkey_penalty_amount = 0
    donkey_penalty_count = 0
    
    try:
        # Load penalty data
        df_penalties = pd.read_csv("VB_Strafen.csv", sep=";", encoding="utf-8")
        df_penalties['Datum'] = pd.to_datetime(df_penalties['Datum'], format='%d.%m.%Y')
        
        # Calculate last week's period (Monday to Sunday)
        today = datetime.now()
        days_since_monday = today.weekday()  # Monday = 0, Sunday = 6
        
        # Last week's Monday
        last_week_monday = today - timedelta(days=days_since_monday + 7)
        # Last week's Sunday  
        last_week_sunday = last_week_monday + timedelta(days=6)
        
        # Filter penalties from last week
        last_week_penalties = df_penalties[
            (df_penalties['Datum'] >= last_week_monday) & 
            (df_penalties['Datum'] <= last_week_sunday)
        ]
        
        if len(last_week_penalties) > 0:
            # Calculate penalty stats per player for last week
            penalty_stats = last_week_penalties.groupby('Spieler').agg({
                'Betrag': ['sum', 'count']
            }).round(2)
            penalty_stats.columns = ['Gesamt_Betrag', 'Anzahl_Strafen']
            penalty_stats = penalty_stats.reset_index().sort_values('Gesamt_Betrag', ascending=False)
            
            # Get the player with highest penalty amount
            if len(penalty_stats) > 0:
                current_donkey = penalty_stats.iloc[0]['Spieler']
                donkey_penalty_amount = penalty_stats.iloc[0]['Gesamt_Betrag']
                donkey_penalty_count = int(penalty_stats.iloc[0]['Anzahl_Strafen'])
        
    except Exception as e:
        # Fallback if penalty data can't be loaded
        current_donkey = "Keine Daten"
        donkey_penalty_amount = 0
        donkey_penalty_count = 0

    # Quick stats overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if next_birthday_days == 0:
            delta_text = "Heute! 🎉"
        elif next_birthday_days == 1:
            delta_text = "Morgen"
        else:
            delta_text = f"in {next_birthday_days} Tagen"
            
        st.metric(
            label="🎂 Nächster Geburtstag",
            value=next_birthday_name,
            delta=delta_text
        )
    
    with col2:
        st.metric(
            label="💰 Mannschaftskasse",
            value="€ 100.00",
            delta="Stand 24.12.2024"
        )
    
    with col3:
        st.metric(
            label="👥 Letztes Training",
            value=f"{training_participants} Teilnehmer",
            delta=training_delta_text
        )
    
    with col4:
        # Dynamic donkey calculation
        if current_donkey != "Niemand" and current_donkey != "Keine Daten":
            delta_text = f"€{donkey_penalty_amount:.2f} ({donkey_penalty_count} Strafen)"
        elif current_donkey == "Niemand":
            delta_text = "Letzte Woche: Alle brav! 🎉"
        else:
            delta_text = "Strafen-DB nicht verfügbar"
            
        st.metric(
            label="🤡 Esel der Woche",
            value=current_donkey,
            delta=delta_text
        )
    
    st.markdown("---")
    
    # Main content area
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📈 Aktuelle Saison-Übersicht")
        
        # Load Fieberkurve data for season overview
        try:
            df_fieberkurve = pd.read_csv("Fieberkurve.csv", sep=";")
            
            # Create Fieberkurve chart
            fig = px.line(df_fieberkurve, x='Spieltag', y='Platzierung', 
                         title='Fieberkurve - Tabellenplatzierung Saison 2024/25',
                         line_shape='spline')
            fig.update_traces(line_color='#1e3c72', line_width=3, mode='lines+markers')
            
            # Invert y-axis so that position 1 is at the top
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#333',
                yaxis=dict(autorange='reversed', title='Tabellenplatz'),
                xaxis=dict(title='Spieltag')
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            # Fallback if CSV can't be loaded
            st.error(f"❌ Fieberkurve-Daten konnten nicht geladen werden: {str(e)}")
            
            # Fallback to sample data
            performance_data = {
                'Monat': ['August', 'September', 'Oktober', 'November', 'Dezember'],
                'Trainingsquote': [85, 88, 82, 90, 87],
                'Spiele': [4, 5, 3, 4, 2],
                'Siege': [3, 3, 2, 3, 1]
            }
            
            df = pd.DataFrame(performance_data)
            
            # Training attendance chart
            fig = px.line(df, x='Monat', y='Trainingsquote', 
                         title='Trainingsquote der letzten Monate',
                         line_shape='spline')
            fig.update_traces(line_color='#1e3c72', line_width=3)
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#333'
            )
            st.plotly_chart(fig, use_container_width=True)
        
    with col_right:
        # Team info box
        st.subheader("🏆 Teaminfos")
        st.info("""
        **Saison 2024/25**
        - Liga: Bezirksliga
        - Tabellenplatz: 8.
        - Punkte: 44
        - Torverhältnis: 61:62
        - Nächstes Spiel: Sonntag 15:30
        """)
        
        # Weather widget with real API data
        st.subheader("🌤️ Wetter für's Training")
        
        # Get API key from Streamlit secrets
        try:
            # TEMPORÄR ZUM TESTEN: API Key hier eintragen
            #api_key = "bd29dad094220635ed7c50cbb1e3061c"
            
            api_key = st.secrets["OPENWEATHER_API_KEY"]
            weather_data = get_weather_data("Buchholz", api_key)
            
            if weather_data:
                # Display real weather data
                st.success(f"""
                **Aktuelles Wetter in Buchholz:**
                
                {weather_data['emoji']} {weather_data['temperature']}°C - {weather_data['description']}
                
                💨 Wind: {weather_data['wind_speed']} km/h | 💧 Luftfeuchtigkeit: {weather_data['humidity']}%
                
                {'🟢 Perfekt für Training!' if weather_data['temperature'] > 5 and 'rain' not in weather_data['description'].lower() else '🟡 Training möglich, aber Wetter beachten!'}
                """)
            else:
                # Fallback if API call fails
                st.warning("⚠️ Wetterdaten konnten nicht abgerufen werden.")
                st.info("Bitte aktuelles Wetter selbst prüfen!")
                
        except Exception as e:
            # Fallback if no API key or other error
            st.info("""
            **🔧 API-Key konfigurieren:**
            
            Für echte Wetterdaten bitte `OPENWEATHER_API_KEY` in den Streamlit Secrets hinterlegen.
            
            Bis dahin: Wetter selbst prüfen! ️
            """)
        
        # Training times
        st.subheader("⏰ Trainingszeiten")
        st.info("""
        **Wöchentliche Trainings:**
        - Dienstag: 18:30
        - Donnerstag: 19:45
        - Freitag: 18:45
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>ViktoriaInsights v1.0 | Viktoria Buchholz - Erste Mannschaft</p>
    </div>
    """, unsafe_allow_html=True) 