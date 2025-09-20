import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import os
import sys
import requests

from dotenv import load_dotenv


load_dotenv()



# Add the parent directory to the path to import database helper

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_helper import db

from timezone_helper import get_german_now, get_german_now_naive, make_naive_german_datetime, calculate_days_until_birthday

import team_scraper



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

    

    # Load real birthday data from database

    next_birthday_name = "Niemand"

    next_birthday_days = 0

    

    try:

        # Lade Geburtstage aus der Datenbank

        df_geburtstage_raw = db.get_birthdays()

        

        if df_geburtstage_raw is not None and len(df_geburtstage_raw) > 0:

            # Convert to our expected format

            geburtstage = []

            for _, row in df_geburtstage_raw.iterrows():

                try:

                    geburtstage.append({

                        "Name": str(row['Name']).strip(),

                        "Datum": row['Geburtstag_parsed'].strftime('%Y-%m-%d')

                    })

                except Exception as e:

                    continue

            

            if geburtstage:

                df_geburtstage = pd.DataFrame(geburtstage)

                df_geburtstage['Datum'] = pd.to_datetime(df_geburtstage['Datum'])

                df_geburtstage['Geburtstag_dieses_Jahr'] = df_geburtstage['Datum'].apply(

                    lambda x: make_naive_german_datetime(get_german_now().year, x.month, x.day)

                )

                

                # Calculate days until birthday

                today = get_german_now_naive()

                df_geburtstage['Tage_bis_Geburtstag'] = df_geburtstage['Geburtstag_dieses_Jahr'].apply(

                    lambda x: calculate_days_until_birthday(x, today)

                )

                

                # Get next birthday

                df_geburtstage = df_geburtstage.sort_values('Tage_bis_Geburtstag')

                if len(df_geburtstage) > 0:

                    # Prüfe ob heute jemand Geburtstag hat (0 Tage)

                    today_birthdays = df_geburtstage[df_geburtstage['Tage_bis_Geburtstag'] == 0]

                    if len(today_birthdays) > 0:

                        # Jemand hat heute Geburtstag

                        today_birthday = today_birthdays.iloc[0]

                        next_birthday_name = f"{today_birthday['Name'].capitalize()} (HEUTE!)"

                        next_birthday_days = 0

                    else:

                        # Nächster Geburtstag (nicht heute)

                        next_birthday = df_geburtstage.iloc[0]

                        next_birthday_name = next_birthday['Name'].capitalize()

                        next_birthday_days = next_birthday['Tage_bis_Geburtstag']

        

    except Exception as e:

        st.error(f"❌ Fehler beim Laden der Geburtstagsdaten: {str(e)}")

        next_birthday_name = "Keine Daten"

        next_birthday_days = 0

    

    # Load real training data from database

    try:

        training_stats = db.get_training_statistics()

        training_participants = training_stats['latest_training_participants']

        training_delta = training_stats['training_delta']

        training_delta_text = training_stats['training_delta_text']

    except Exception as e:

        # Fallback to default values if database can't be loaded

        training_participants = 0

        training_delta = 0

        training_delta_text = "Keine Daten"

    

    # Calculate current donkey of the week based on penalties

    current_donkey = "Niemand"

    donkey_penalty_amount = 0

    donkey_penalty_count = 0

    

    try:

        # Get donkey of last week from database using week_nr

        donkey_name, donkey_amount, donkey_count = db.get_last_week_donkey()

        

        if donkey_name:

            current_donkey = donkey_name.capitalize()

            donkey_penalty_amount = donkey_amount

            donkey_penalty_count = donkey_count

        

    except Exception as e:

        # Fallback if donkey data can't be loaded

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

            delta="Stand 01.07.2025"

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

            delta_text = "Letzte Woche: Kein Esel! 🎉"

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

            standings_history = db.get_team_standings_history()

            if standings_history is None or standings_history.empty:

                raise ValueError("Keine Standings-Daten gefunden")



            df_fieberkurve = standings_history.copy()

            match_day = pd.to_numeric(df_fieberkurve['match_day'], errors='coerce')

            games_played = pd.to_numeric(df_fieberkurve['games_played'], errors='coerce')

            df_fieberkurve['Spieltag'] = match_day.fillna(games_played)

            df_fieberkurve['Platzierung'] = pd.to_numeric(df_fieberkurve['position'], errors='coerce')

            df_fieberkurve['Aktualisiert'] = pd.to_datetime(df_fieberkurve['scraped_at'], errors='coerce', utc=True)



            df_fieberkurve = df_fieberkurve.dropna(subset=['Spieltag', 'Platzierung'])
            df_fieberkurve = df_fieberkurve.sort_values(['Spieltag', 'Aktualisiert'])
            df_fieberkurve = df_fieberkurve.drop_duplicates(subset=['Spieltag'], keep='last')
            df_fieberkurve = df_fieberkurve[df_fieberkurve['Spieltag'] >= 1]

            if df_fieberkurve.empty:
                raise ValueError("Keine Standings-Daten verfügbar (nach Filterung)")

            df_fieberkurve['Spieltag'] = df_fieberkurve['Spieltag'].astype(int)
            df_fieberkurve['Platzierung'] = df_fieberkurve['Platzierung'].astype(int)
            df_fieberkurve['Aktualisiert_fmt'] = df_fieberkurve['Aktualisiert'].dt.tz_convert('Europe/Berlin').dt.strftime('%d.%m.%Y %H:%M')

            max_match_day = int(df_fieberkurve['Spieltag'].max())
            max_match_day = max(max_match_day, 1)

            fig = px.line(df_fieberkurve, x='Spieltag', y='Platzierung',
                         title='Fieberkurve - Tabellenplatzierung Saison 2025/26',
                         line_shape='linear')
            fig.update_traces(
                line_color='#1e3c72',
                line_width=3,
                mode='lines+markers',
                line_shape='linear',
                customdata=df_fieberkurve[['Aktualisiert_fmt']],
                hovertemplate='Spieltag %{x}<br>Platz %{y}<br>Stand: %{customdata[0]} Uhr<extra></extra>'
            )

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#333',
                xaxis=dict(
                    title='Spieltag',
                    range=[1, max_match_day],
                    tickmode='linear',
                    tick0=1,
                    dtick=1,
                    showgrid=True,
                    gridcolor='rgba(30,60,114,0.15)',
                    gridwidth=1,
                    zeroline=False
                ),
                yaxis=dict(
                    title='Tabellenplatz',
                    range=[18.5, 0.5],
                    tickmode='linear',
                    tick0=1,
                    dtick=1,
                    showgrid=True,
                    gridcolor='rgba(30,60,114,0.15)',
                    gridwidth=1,
                    zeroline=False
                )
            )

            st.plotly_chart(fig, use_container_width=True)


        except Exception as e:

            # Fallback if Supabase data can't be loaded

            st.error(f"❌ Live-Daten konnten nicht geladen werden: {str(e)}")

            

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

        # Team info box with automatic scraping

        st.subheader("🏆 Teaminfos")

        

        try:

            # Lade aktuelle Teamdaten über den Team-Scraper

            viktoria_info, data_source = team_scraper.get_team_data()

            formatted_info = team_scraper.format_team_info(viktoria_info, data_source)

            st.info(formatted_info)

                

        except Exception as e:

            # Fallback bei Fehlern

            st.info("""

            **Saison 2024/25**

            - Liga: Bezirksliga

            - Tabellenplatz: 8.

            - Punkte: 44

            - Torverhältnis: 61:62

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

        - Montag (in der Vorbereitung): 18:45

        - Dienstag: 18:30

        - Donnerstag: 19:45

        - Freitag: 18:45

        """)

    

    # Footer

    st.markdown("---")

    footer_html = (
        "<div style='text-align: center; color: #666; padding: 1rem;'>"
        "<p>ViktoriaInsights v1.0 | Viktoria Buchholz - Erste Mannschaft</p>"
        "</div>"
    )
    st.markdown(footer_html, unsafe_allow_html=True)
