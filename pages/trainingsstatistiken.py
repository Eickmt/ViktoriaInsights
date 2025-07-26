import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import os
import numpy as np
from database_helper import db
from timezone_helper import get_german_now, get_german_date_now, get_german_now_naive

def show():
    st.title("🏆 Trainingsspielsiege")
    st.subheader("Spielerleistung und Siegesanalyse")
    
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
    .stDateInput label {
        color: #212529 !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Load training victories data from database
    try:
        df_melted = db.get_training_victories()
        
        if df_melted is None or len(df_melted) == 0:
            st.warning("Keine Siegesdaten in der Datenbank gefunden.")
            st.info("Bitte fügen Sie zunächst Trainingsdaten über den entsprechenden Tab hinzu.")
            return
        
        # Ensure we have the right column names and data types
        if 'Sieg' not in df_melted.columns:
            st.error("❌ Spalte 'Sieg' nicht in den Daten gefunden!")
            return
        
        # Convert Sieg column to boolean if it's not already
        df_melted['Sieg'] = df_melted['Sieg'].astype(bool)
        
        # Get unique player names for UI
        spieler_namen = sorted(df_melted['Spieler'].unique().tolist())
        # Capitalize names for display but keep original for data processing
        spieler_namen_display = [name.capitalize() for name in spieler_namen]
        
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Daten aus der Datenbank: {str(e)}")
        st.info("Versuche Fallback zur CSV-Datei...")
        
        # Fallback to CSV if database fails
        try:
            df_siege = pd.read_csv("VB_Trainingsspielsiege.csv", sep=";")
            
            # Clean and process the data
            spieler_namen = df_siege['Spielername'].tolist()
            datum_spalten = [col for col in df_siege.columns if col != 'Spielername']
            
            # Convert date columns to datetime
            datum_mapping = {}
            
            # German month mapping for robustness
            german_months = {
                'Jan': 'Jan', 'Feb': 'Feb', 'Mrz': 'Mar', 'Apr': 'Apr',
                'Mai': 'May', 'Jun': 'Jun', 'Jul': 'Jul', 'Aug': 'Aug',
                'Sep': 'Sep', 'Okt': 'Oct', 'Nov': 'Nov', 'Dez': 'Dec'
            }
            
            for datum_str in datum_spalten:
                try:
                    # Parse dates - try different formats
                    datum_clean = datum_str.strip()
                    if datum_clean:
                        # Convert German months to English for pandas
                        datum_english = datum_clean
                        for de_month, en_month in german_months.items():
                            if de_month in datum_clean:
                                datum_english = datum_clean.replace(de_month, en_month)
                                break
                        
                        # Try format with year first (e.g., "14. Jan 2025")
                        if any(year in datum_english for year in ['2024', '2025', '2026']):
                            parsed_date = pd.to_datetime(datum_english, format="%d. %b %Y")
                        else:
                            # Fall back to format without year (e.g., "14. Jan") and assume current year
                            datum_with_year = f"{datum_english} 2024"
                            parsed_date = pd.to_datetime(datum_with_year, format="%d. %b %Y")
                        datum_mapping[datum_str] = parsed_date
                except Exception as e:
                    # Skip invalid dates and show which ones fail
                    st.sidebar.error(f"❌ Datum nicht erkannt: {datum_str}")
                    continue
            
            # Create a melted dataframe for easier analysis
            melted_data = []
            for _, row in df_siege.iterrows():
                spieler = row['Spielername']
                for datum_str in datum_spalten:
                    if datum_str in datum_mapping and pd.notna(row[datum_str]) and row[datum_str] == 1:
                        melted_data.append({
                            'Spieler': spieler,
                            'Datum': datum_mapping[datum_str],
                            'Sieg': 1
                        })
            
            df_melted = pd.DataFrame(melted_data)
            
            if len(df_melted) == 0:
                st.warning("Keine Siegesdaten gefunden. Bitte überprüfen Sie die CSV-Datei.")
                return
                
        except FileNotFoundError:
            st.error("❌ Datei 'VB_Trainingsspielsiege.csv' nicht gefunden und Datenbank nicht verfügbar!")
            st.info("Bitte stellen Sie sicher, dass entweder die Datenbank oder die CSV-Datei verfügbar ist.")
            return
        except Exception as e:
            st.error(f"❌ Fehler beim Laden der Daten: {str(e)}")
            return
    
    # Filter options
    st.sidebar.header("Zeitraum Filter")
    
    # Custom CSS for better sidebar contrast
    st.sidebar.markdown("""
    <style>
    .stSelectbox > div > div > div {
        background-color: white !important;
        color: black !important;
        border: 2px solid #ccc !important;
    }
    .stSelectbox > div > div > div > div {
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    filter_option = st.sidebar.selectbox(
        "Wählen Sie den Analysezeitraum:",
        ["Gesamtzeitraum", "Letzte 30 Tage", "Letzte 7 Tage"]
    )
    
    # Apply date filter
    heute = get_german_now_naive()
    if filter_option == "Letzte 7 Tage":
        start_datum = heute - timedelta(days=7)
        df_filtered = df_melted[df_melted['Datum'] >= start_datum]
        filter_text = "den letzten 7 Tagen"
    elif filter_option == "Letzte 30 Tage":
        start_datum = heute - timedelta(days=30)
        df_filtered = df_melted[df_melted['Datum'] >= start_datum]
    else:
        df_filtered = df_melted.copy()
        filter_text = "dem Gesamtzeitraum"
    
    # Calculate statistics
    if len(df_filtered) == 0:
        st.warning(f"Keine Daten für {filter_text} verfügbar.")
        return
    
    # Only count actual victories (where Sieg=True)
    df_victories = df_filtered[df_filtered['Sieg'] == True]
    gesamt_siege = len(df_victories)
    gesamt_teilnahmen = len(df_filtered)
    einzigartige_tage = df_filtered['Datum'].nunique()
    aktive_spieler = df_filtered['Spieler'].nunique()
    
    # Average players per training (based on victories × 2, since 2 teams play against each other)
    # Calculate average victories per training day, then multiply by 2
    if einzigartige_tage > 0:
        siege_pro_tag = gesamt_siege / einzigartige_tage
        durchschnitt_spieler_pro_training = siege_pro_tag * 2
    else:
        durchschnitt_spieler_pro_training = 0
    
    # Victory rate
    sieg_quote = (gesamt_siege / gesamt_teilnahmen * 100) if gesamt_teilnahmen > 0 else 0
    
    # Main metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🏆 Siege gesamt", gesamt_siege)
    
    with col2:
        st.metric("📅 Trainingstage", einzigartige_tage)
    
    with col3:
        st.metric("👥 Ø Spieler/Training", f"{durchschnitt_spieler_pro_training:.1f}")
    
    # Show current filter
    st.info(f"📊 Anzeige für: **{filter_text}** ({filter_option})")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["🏆 Spieler-Ranking", "📈 Trends & Analysen", "📋 Detailansicht"])
    
    with tab1:
        st.subheader("🏆 Spieler-Ranking")
        
        # Calculate player statistics
        spieler_stats = df_filtered.groupby('Spieler')['Sieg'].sum().reset_index()
        spieler_stats.columns = ['Spieler', 'Siege']
        spieler_stats = spieler_stats.sort_values('Siege', ascending=False)
        
        # Add all players (including those with 0 wins in the filtered period)
        alle_spieler_stats = []
        for spieler in spieler_namen:
            siege_count = spieler_stats[spieler_stats['Spieler'] == spieler]['Siege'].values
            siege = siege_count[0] if len(siege_count) > 0 else 0
            
            # Calculate percentage of training days won
            siege_quote = (siege / einzigartige_tage * 100) if einzigartige_tage > 0 else 0
            
            # Determine status
            if siege >= 3:
                status = '🔥'
            elif siege >= 1:
                status = '⚡'
            else:
                status = '😴'
            
            alle_spieler_stats.append({
                'Spieler': spieler,
                'Siege': siege,
                'Quote': siege_quote,
                'Status': status
            })
        
        spieler_ranking = pd.DataFrame(alle_spieler_stats).sort_values('Siege', ascending=False)
        
        # Display top performers
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🥇 Top Performer")
            if len(spieler_ranking) > 0:
                top_player = spieler_ranking.iloc[0]
                st.success(f"""
                **{top_player['Spieler'].capitalize()}**
                
                🏆 {top_player['Siege']} Siege
                
                📊 {top_player['Quote']:.1f}% der Trainingstage
                """)
        
        with col2:
            st.markdown("### 🔥 Heißester Spieler")
            # Find player with longest current winning streak
            if len(df_victories) > 0:
                # Get unique training dates sorted descending (newest first)
                unique_dates = sorted(df_victories['Datum'].unique(), reverse=True)
                
                # Calculate current winning streaks for each player
                player_streaks = {}
                for spieler in spieler_namen:
                    streak = 0
                    # Go through dates from newest to oldest
                    for datum in unique_dates:
                        # Count only actual victories on this date
                        player_wins_on_date = len(df_victories[(df_victories['Spieler'] == spieler) & 
                                                               (df_victories['Datum'] == datum) & 
                                                               (df_victories['Sieg'] == True)])
                        if player_wins_on_date > 0:
                            streak += player_wins_on_date
                        else:
                            # Check if player participated but didn't win
                            player_participated = len(df_filtered[(df_filtered['Spieler'] == spieler) & 
                                                                 (df_filtered['Datum'] == datum)]) > 0
                            if player_participated:
                                # Break streak if participated but didn't win
                                break
                            # If didn't participate, continue streak
                    player_streaks[spieler] = streak
                
                # Find player with highest current streak
                if player_streaks:
                    hottest_player = max(player_streaks, key=player_streaks.get)
                    hottest_streak = player_streaks[hottest_player]
                    
                    if hottest_streak > 0:
                        st.info(f"""
                        **{hottest_player.capitalize()}**
                        
                        🔥 {hottest_streak} Siege in Serie
                        
                        📈 Aktuell stark!
                        """)
                    else:
                        st.info("**Keine aktive Serie**\n\n🔥 0 Siege in Serie")
                else:
                    st.info("**Keine Daten**\n\n📊 Keine Serien verfügbar")
            else:
                st.info("**Keine Siege**\n\n🔥 Noch keine Siege verzeichnet")
        

        
        st.markdown("---")
        
        # Player ranking table
        st.subheader("📋 Detailliertes Ranking")
        
        # Calculate team average for dynamic thresholds
        siege_values = [player['Siege'] for player in alle_spieler_stats]
        if len(siege_values) > 0:
            team_average = np.mean(siege_values)
            
            # For players below average, split into 3/4 yellow and 1/4 red
            below_average_players = [s for s in siege_values if s < team_average]
            if len(below_average_players) > 0:
                # Calculate threshold for bottom 25% of below-average players
                red_threshold = np.percentile(below_average_players, 25)
            else:
                red_threshold = 0
            
        else:
            team_average = red_threshold = 0
        
        # Display player cards
        for i, (_, player) in enumerate(spieler_ranking.iterrows()):
            if i % 3 == 0:
                col1, col2, col3 = st.columns(3)
            
            col = [col1, col2, col3][i % 3]
            
            # 4-tier color coding system
            if i < 3:  # Top 3 positions
                border_color = "#051a0a"  # Very very dark green - Top 3
                bg_color = "#8fbc8f"  # Darker green background
                performance_level = f"🏆 Platz {i+1}"
            elif player['Siege'] >= team_average:
                border_color = "#28a745"  # Green - Above average
                bg_color = "#d4edda"  # Light green background
                performance_level = "Über Durchschnitt"
            elif player['Siege'] >= red_threshold:
                border_color = "#ffc107"  # Yellow - Below average but not bottom 25%
                bg_color = "#fff3cd"  # Light yellow background
                performance_level = "Unter Durchschnitt"
            else:
                border_color = "#dc3545"  # Red - Bottom 25% of below average
                bg_color = "#f8d7da"  # Light red background
                performance_level = "Untere 25%"
            
            with col:
                st.markdown(f"""
                <div style='
                    padding: 1.2rem;
                    border-left: 5px solid {border_color};
                    background-color: {bg_color};
                    border-radius: 8px;
                    margin: 0.5rem 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    border: 1px solid rgba(0,0,0,0.1);
                '>
                    <h4 style='
                        margin: 0 0 0.8rem 0;
                        color: #212529;
                        font-weight: bold;
                        font-size: 1.1rem;
                    '>#{i+1} {player['Status']} {player['Spieler'].capitalize()}</h4>
                    <p style='
                        margin: 0.3rem 0;
                        color: #495057;
                        font-size: 0.95rem;
                    '><strong style='color: #212529;'>Siege:</strong> {player['Siege']}</p>
                    <p style='
                        margin: 0.3rem 0;
                        color: #495057;
                        font-size: 0.95rem;
                    '><strong style='color: #212529;'>Quote:</strong> {player['Quote']:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        st.subheader("📈 Trends und Analysen")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Players per training day (victories * 2 because of 2 teams)
            if len(df_victories) > 0:
                # Calculate daily statistics based on actual victories
                daily_stats = df_victories.groupby('Datum').size().reset_index()
                daily_stats.columns = ['Datum', 'Siege']
                daily_stats['Spieler'] = daily_stats['Siege'] * 2  # 2 teams per training
                daily_stats = daily_stats.sort_values('Datum')
                
                if len(daily_stats) > 0:
                    fig1 = px.line(daily_stats, x='Datum', y='Spieler',
                                  title='Spieler pro Training (basierend auf Siegen)',
                                  line_shape='spline')
                    fig1.update_traces(line_color='#1e3c72', line_width=3, mode='lines+markers')
                    fig1.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        yaxis_title="Anzahl Spieler"
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                else:
                    st.info("Keine Siegesdaten für Chart verfügbar.")
            else:
                st.info("Keine Siegesdaten verfügbar.")
        
        with col2:
            # Player comparison bar chart (sorted descending - best on top)
            if len(spieler_ranking) > 0:
                # Show top 10 players, sorted descending (best first)
                top_players = spieler_ranking.head(10).sort_values('Siege', ascending=True)  # ascending=True for horizontal bar chart puts highest values on top
                
                fig2 = px.bar(top_players, x='Siege', y='Spieler',
                             title='Top 10 Spieler - Siege Vergleich',
                             orientation='h',
                             color='Siege',
                             color_continuous_scale='RdYlGn')
                fig2.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig2, use_container_width=True)
        
        # Weekly/Monthly analysis if enough data
        if len(df_victories) > 0:
            st.subheader("📊 Zeitraum-Analyse")
            
            # Group by week if we have enough data
            if df_victories['Datum'].nunique() > 1:  # Changed from 7 to 1 to show analysis even with few dates
                # Create a better weekly analysis based on victories only
                df_weekly = df_victories.copy()
                df_weekly['Woche'] = df_victories['Datum'].dt.to_period('W-MON')  # Week starting Monday
                
                # Get all weeks in the data
                all_weeks = sorted(df_weekly['Woche'].unique())
                
                # Show only top 5 performers for clarity
                top_performers = spieler_ranking.head(5)['Spieler'].tolist()
                
                # Create a complete dataset with all combinations
                weekly_data = []
                for week in all_weeks:
                    for player in top_performers:
                        # Count victories for this player in this week (only actual victories)
                        player_week_victories = len(df_weekly[
                            (df_weekly['Woche'] == week) & 
                            (df_weekly['Spieler'] == player) &
                            (df_weekly['Sieg'] == True)  # Only count actual victories
                        ])
                        weekly_data.append({
                            'Woche': str(week),
                            'Spieler': player,
                            'Siege': player_week_victories
                        })
                
                weekly_df = pd.DataFrame(weekly_data)
                
                if len(weekly_df) > 0 and weekly_df['Siege'].sum() > 0:
                    # Clean up week format for display - make it more readable
                    weekly_df['Woche_Display'] = weekly_df['Woche'].apply(
                        lambda x: f"KW {str(x).split('-W')[1]}" if '-W' in str(x) else str(x)
                    )
                    
                    fig3 = px.line(weekly_df, 
                                  x='Woche_Display', 
                                  y='Siege', 
                                  color='Spieler',
                                  title='Wöchentliche Siege - Top 5 Spieler',
                                  markers=True)
                    fig3.update_layout(
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        xaxis_title="Kalenderwoche",
                        yaxis_title="Anzahl Siege",
                        xaxis={'tickangle': 45}
                    )
                    fig3.update_traces(line_width=2, marker_size=6)
                    st.plotly_chart(fig3, use_container_width=True)
                else:
                    st.info("Nicht genügend Siegesdaten für Zeitraum-Analyse verfügbar.")
            else:
                st.info("Mindestens 2 verschiedene Trainingstage für Zeitraum-Analyse erforderlich.")
    
    with tab3:
        st.subheader("📋 Detailansicht")
        
        # Show raw data in a nice format
        if len(df_filtered) > 0:
            # Create a pivot table for better overview with individual dates
            pivot_table = df_filtered.pivot_table(
                index='Spieler', 
                columns='Datum', 
                values='Sieg', 
                aggfunc='sum',
                fill_value=0
            )
            
            # Format dates for column headers
            pivot_table.columns = [d.strftime("%d.%m.%Y") for d in pivot_table.columns]
            
            # Add total column
            pivot_table['Gesamt'] = pivot_table.sum(axis=1)
            
            # Sort by total
            pivot_table = pivot_table.sort_values('Gesamt', ascending=False)
            
            st.subheader("🗓️ Siege pro Spieler und Trainingstag")
            st.dataframe(pivot_table, use_container_width=True)
            
            # Summary statistics
            st.markdown("---")
            st.subheader("📊 Zusammenfassung")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Top 5 Spieler:**")
                for i, (spieler, siege) in enumerate(pivot_table['Gesamt'].head(5).items()):
                    st.write(f"{i+1}. {spieler.capitalize()}: {siege} Siege")
            
            with col2:
                st.markdown("**Aktivste Trainingstage:**")
                # Calculate based on victories × 2 (number of players per training)
                daily_victories = df_victories.groupby('Datum').size().reset_index()
                daily_victories.columns = ['Datum', 'Siege']
                daily_victories['Spieler'] = daily_victories['Siege'] * 2  # 2 teams per training
                daily_victories = daily_victories.sort_values('Spieler', ascending=False)
                
                for i, (_, row) in enumerate(daily_victories.head(5).iterrows()):
                    datum_str = row['Datum'].strftime('%d.%m.%Y')
                    spieler_count = row['Spieler']
                    siege_count = row['Siege']
                    st.write(f"{i+1}. {datum_str}: {spieler_count} Spieler ({siege_count} Siege)")
        else:
            st.info("Keine Daten für den gewählten Zeitraum verfügbar.")
    
 