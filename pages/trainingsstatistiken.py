import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import os
import numpy as np

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
    
    # Load training victories data
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
        st.error("❌ Datei 'VB_Trainingsspielsiege.csv' nicht gefunden!")
        st.info("Bitte stellen Sie sicher, dass die CSV-Datei im Hauptverzeichnis liegt.")
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
    heute = datetime.now()
    if filter_option == "Letzte 7 Tage":
        start_datum = heute - timedelta(days=7)
        df_filtered = df_melted[df_melted['Datum'] >= start_datum]
        filter_text = "den letzten 7 Tagen"
    elif filter_option == "Letzte 30 Tage":
        start_datum = heute - timedelta(days=30)
        df_filtered = df_melted[df_melted['Datum'] >= start_datum]
        filter_text = "den letzten 30 Tagen"
    else:
        df_filtered = df_melted.copy()
        filter_text = "dem Gesamtzeitraum"
    
    # Calculate statistics
    if len(df_filtered) == 0:
        st.warning(f"Keine Daten für {filter_text} verfügbar.")
        return
    
    gesamt_siege = len(df_filtered)
    einzigartige_tage = df_filtered['Datum'].nunique()
    aktive_spieler = df_filtered['Spieler'].nunique()
    durchschnitt_spieler_pro_training = (gesamt_siege / einzigartige_tage * 2) if einzigartige_tage > 0 else 0
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏆 Siege gesamt", gesamt_siege)
    
    with col2:
        st.metric("📅 Trainingstage", einzigartige_tage)
    
    with col3:
        st.metric("👥 Aktive Spieler", aktive_spieler)
    
    with col4:
        st.metric("🏃 Ø Spieler/Training", f"{durchschnitt_spieler_pro_training:.1f}")
    
    # Show current filter
    st.info(f"📊 Anzeige für: **{filter_text}** ({filter_option})")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Spieler-Ranking", "📈 Trends & Analysen", "📋 Detailansicht", "➕ Neue Siege-Einträge"])
    
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
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🥇 Top Performer")
            if len(spieler_ranking) > 0:
                top_player = spieler_ranking.iloc[0]
                st.success(f"""
                **{top_player['Spieler']}**
                
                🏆 {top_player['Siege']} Siege
                
                📊 {top_player['Quote']:.1f}% der Trainingstage
                """)
        
        with col2:
            st.markdown("### 🔥 Heißester Spieler")
            # Find player with longest current winning streak
            if len(df_filtered) > 0:
                # Get unique training dates sorted descending (newest first)
                unique_dates = sorted(df_filtered['Datum'].unique(), reverse=True)
                
                # Calculate current winning streaks for each player
                player_streaks = {}
                for spieler in spieler_namen:
                    streak = 0
                    # Go through dates from newest to oldest
                    for datum in unique_dates:
                        player_wins_on_date = len(df_filtered[(df_filtered['Spieler'] == spieler) & (df_filtered['Datum'] == datum)])
                        if player_wins_on_date > 0:
                            streak += player_wins_on_date
                        else:
                            # Break the streak if no win on this date
                            break
                    player_streaks[spieler] = streak
                
                # Find player with highest current streak
                if player_streaks:
                    hottest_player = max(player_streaks, key=player_streaks.get)
                    hottest_streak = player_streaks[hottest_player]
                    
                    if hottest_streak > 0:
                        st.info(f"""
                        **{hottest_player}**
                        
                        🔥 {hottest_streak} Siege in Serie
                        
                        📈 Aktuell stark!
                        """)
                    else:
                        st.info("**Keine aktive Serie**\n\n🔥 0 Siege in Serie")
                else:
                    st.info("**Keine Daten**\n\n📊 Keine Serien verfügbar")
        
        with col3:
            st.markdown("### 📊 Durchschnitt")
            avg_siege = spieler_ranking['Siege'].mean()
            median_siege = spieler_ranking['Siege'].median()
            st.warning(f"""
            **Team-Statistik**
            
            📊 Ø {avg_siege:.1f} Siege
            
            📍 Median: {median_siege:.1f}
            """)
        
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
                    '>#{i+1} {player['Status']} {player['Spieler']}</h4>
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
            if len(df_filtered) > 0:
                daily_stats = df_filtered.groupby('Datum').size().reset_index()
                daily_stats.columns = ['Datum', 'Siege']
                daily_stats['Spieler'] = daily_stats['Siege'] * 2  # 2 teams per training
                daily_stats = daily_stats.sort_values('Datum')
                
                fig1 = px.line(daily_stats, x='Datum', y='Spieler',
                              title='Spieler pro Training',
                              line_shape='spline')
                fig1.update_traces(line_color='#1e3c72', line_width=3, mode='lines+markers')
                fig1.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    yaxis_title="Anzahl Spieler"
                )
                st.plotly_chart(fig1, use_container_width=True)
        
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
        if len(df_filtered) > 0:
            st.subheader("📊 Zeitraum-Analyse")
            
            # Group by week if we have enough data
            if df_filtered['Datum'].nunique() > 7:
                # Create a better weekly analysis
                df_weekly = df_filtered.copy()
                df_weekly['Woche'] = df_filtered['Datum'].dt.to_period('W-MON')  # Week starting Monday
                
                # Get all weeks in the data
                all_weeks = sorted(df_weekly['Woche'].unique())
                
                # Show only top 5 performers for clarity
                top_performers = spieler_ranking.head(5)['Spieler'].tolist()
                
                # Create a complete dataset with all combinations
                weekly_data = []
                for week in all_weeks:
                    for player in top_performers:
                        # Count victories for this player in this week
                        player_week_victories = len(df_weekly[
                            (df_weekly['Woche'] == week) & 
                            (df_weekly['Spieler'] == player)
                        ])
                        weekly_data.append({
                            'Woche': str(week),
                            'Spieler': player,
                            'Siege': player_week_victories
                        })
                
                weekly_df = pd.DataFrame(weekly_data)
                
                if len(weekly_df) > 0:
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
                    st.write(f"{i+1}. {spieler}: {siege} Siege")
            
            with col2:
                st.markdown("**Aktivste Trainingstage:**")
                daily_summary = df_filtered.groupby('Datum').size().sort_values(ascending=False)
                for i, (datum, siege) in enumerate(daily_summary.head(5).items()):
                    st.write(f"{i+1}. {datum.strftime('%d.%m.%Y')}: {siege} Siege")
        else:
            st.info("Keine Daten für den gewählten Zeitraum verfügbar.")
    
    with tab4:
        st.subheader("➕ Neue Siege-Einträge")
        
        st.info("📝 Hier können Sie neue Siege für einen Trainingstag hinzufügen.")
        
        # Date selection
        selected_date = st.date_input(
            "📅 Trainingstag auswählen:",
            value=datetime.now().date(),
            help="Wählen Sie das Datum des Trainings aus"
        )
        
        # Convert date to string format that matches CSV columns
        date_str = selected_date.strftime("%d. %b %Y")
        german_months = {
            'Jan': 'Jan', 'Feb': 'Feb', 'Mar': 'Mrz', 'Apr': 'Apr',
            'May': 'Mai', 'Jun': 'Jun', 'Jul': 'Jul', 'Aug': 'Aug',
            'Sep': 'Sep', 'Oct': 'Okt', 'Nov': 'Nov', 'Dec': 'Dez'
        }
        
        # Convert English months to German
        for en_month, de_month in german_months.items():
            if en_month in date_str:
                date_str = date_str.replace(en_month, de_month)
                break
        
        st.write(f"**Gewähltes Datum:** {date_str}")
        
        # Check if date already exists in CSV
        existing_columns = [col for col in df_siege.columns if col != 'Spielername']
        date_exists = date_str in existing_columns
        
        if date_exists:
            st.warning(f"⚠️ Das Datum {date_str} existiert bereits in der CSV-Datei!")
            
            # Show current entries for this date
            st.markdown("**Aktuelle Einträge für diesen Tag:**")
            current_entries = df_siege[['Spielername', date_str]].copy()
            current_entries.columns = ['Spieler', 'Siege']
            current_entries = current_entries[current_entries['Siege'] == 1]
            
            if len(current_entries) > 0:
                for _, player in current_entries.iterrows():
                    st.write(f"🏆 {player['Spieler']}")
            else:
                st.write("Keine Siege für diesen Tag eingetragen.")
        
        st.markdown("---")
        
        # Player selection
        st.subheader("👥 Spieler auswählen")
        st.write("Wählen Sie alle Spieler aus, die an diesem Tag Siege erhalten haben:")
        
        # Create checkboxes for all players
        col_count = 3
        cols = st.columns(col_count)
        selected_players = []
        
        for i, spieler in enumerate(spieler_namen):
            col_idx = i % col_count
            with cols[col_idx]:
                # Check if player already has an entry for this date
                current_value = False
                if date_exists:
                    try:
                        current_value = df_siege[df_siege['Spielername'] == spieler][date_str].iloc[0] == 1
                    except (IndexError, KeyError):
                        current_value = False
                
                is_selected = st.checkbox(
                    spieler, 
                    value=current_value,
                    key=f"player_{spieler}_{selected_date}"
                )
                
                if is_selected:
                    selected_players.append(spieler)
        
        st.markdown("---")
        
        # Summary
        if selected_players:
            st.subheader("📊 Zusammenfassung")
            st.write(f"**Datum:** {date_str}")
            st.write(f"**Anzahl Spieler mit Siegen:** {len(selected_players)}")
            st.write("**Gewählte Spieler:**")
            for player in selected_players:
                st.write(f"🏆 {player}")
        
        # Save button
        if st.button("💾 Einträge speichern", type="primary", use_container_width=True):
            try:
                # Load current CSV
                df_current = pd.read_csv("VB_Trainingsspielsiege.csv", sep=";")
                
                # Add new column if date doesn't exist
                if date_str not in df_current.columns:
                    df_current[date_str] = ""
                
                # Update entries for selected players
                for spieler in spieler_namen:
                    mask = df_current['Spielername'] == spieler
                    if spieler in selected_players:
                        df_current.loc[mask, date_str] = 1
                    else:
                        df_current.loc[mask, date_str] = ""
                
                # Save updated CSV
                df_current.to_csv("VB_Trainingsspielsiege.csv", sep=";", index=False)
                
                st.success(f"✅ Einträge für {date_str} erfolgreich gespeichert!")
                st.balloons()
                
                # Refresh page to show updated data
                st.info("🔄 Seite wird automatisch aktualisiert...")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Fehler beim Speichern: {str(e)}")
        
        # Data quality info
        st.info(f"""
        **📊 Aktuelle Datenbank:**
        - Verfügbare Trainingstage: {len(datum_spalten)}
        - Registrierte Spieler: {len(spieler_namen)}
        - Siege gesamt: {len(df_melted)}
        """) 