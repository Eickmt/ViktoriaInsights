import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import calendar

def show():
    st.title("📊 Trainingsstatistiken")
    st.subheader("Anwesenheit und Leistungsanalyse")
    
    # Sample training data
    trainings_data = [
        {"Datum": "2024-12-03", "Thomas Schmidt": True, "Max Mustermann": True, "Michael Weber": False, "Stefan König": True, "Andreas Müller": True, "Christian Bauer": True},
        {"Datum": "2024-12-01", "Thomas Schmidt": False, "Max Mustermann": True, "Michael Weber": True, "Stefan König": True, "Andreas Müller": False, "Christian Bauer": True},
        {"Datum": "2024-11-29", "Thomas Schmidt": True, "Max Mustermann": True, "Michael Weber": True, "Stefan König": False, "Andreas Müller": True, "Christian Bauer": True},
        {"Datum": "2024-11-26", "Thomas Schmidt": True, "Max Mustermann": False, "Michael Weber": True, "Stefan König": True, "Andreas Müller": True, "Christian Bauer": False},
        {"Datum": "2024-11-24", "Thomas Schmidt": True, "Max Mustermann": True, "Michael Weber": False, "Stefan König": True, "Andreas Müller": True, "Christian Bauer": True},
        {"Datum": "2024-11-22", "Thomas Schmidt": False, "Max Mustermann": True, "Michael Weber": True, "Stefan König": True, "Andreas Müller": True, "Christian Bauer": True},
        {"Datum": "2024-11-19", "Thomas Schmidt": True, "Max Mustermann": True, "Michael Weber": True, "Stefan König": False, "Andreas Müller": False, "Christian Bauer": True},
        {"Datum": "2024-11-17", "Thomas Schmidt": True, "Max Mustermann": True, "Michael Weber": True, "Stefan König": True, "Andreas Müller": True, "Christian Bauer": True},
        {"Datum": "2024-11-15", "Thomas Schmidt": True, "Max Mustermann": False, "Michael Weber": True, "Stefan König": True, "Andreas Müller": True, "Christian Bauer": True},
        {"Datum": "2024-11-12", "Thomas Schmidt": True, "Max Mustermann": True, "Michael Weber": False, "Stefan König": True, "Andreas Müller": True, "Christian Bauer": False},
    ]
    
    df_training = pd.DataFrame(trainings_data)
    df_training['Datum'] = pd.to_datetime(df_training['Datum'])
    df_training = df_training.sort_values('Datum', ascending=False)
    
    # Get player names (excluding date column)
    spieler_namen = [col for col in df_training.columns if col != 'Datum']
    
    # Calculate attendance statistics
    gesamt_trainings = len(df_training)
    
    # Overall stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        durchschnittliche_anwesenheit = df_training[spieler_namen].sum().sum() / (len(spieler_namen) * gesamt_trainings) * 100
        st.metric("📈 Ø Anwesenheit", f"{durchschnittliche_anwesenheit:.1f}%")
    
    with col2:
        letztes_training = df_training.iloc[0]
        anwesende_letztes = sum(letztes_training[spieler_namen])
        st.metric("🏃 Letztes Training", f"{anwesende_letztes}/{len(spieler_namen)}")
    
    with col3:
        st.metric("📅 Trainings gesamt", gesamt_trainings)
    
    with col4:
        # Best attendance this month
        dieser_monat = df_training[df_training['Datum'] >= (datetime.now() - timedelta(days=30))]
        if len(dieser_monat) > 0:
            monatliche_anwesenheit = dieser_monat[spieler_namen].sum().sum() / (len(spieler_namen) * len(dieser_monat)) * 100
            st.metric("📊 Dieser Monat", f"{monatliche_anwesenheit:.1f}%")
        else:
            st.metric("📊 Dieser Monat", "0%")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Spieler-Übersicht", "📈 Trends & Analysen", "📋 Training eintragen", "⚙️ Einstellungen"])
    
    with tab1:
        st.subheader("👥 Individuelle Anwesenheitsstatistiken")
        
        # Calculate individual stats
        spieler_stats = []
        for spieler in spieler_namen:
            anwesenheit = df_training[spieler].sum()
            quote = (anwesenheit / gesamt_trainings) * 100
            
            # Streak calculation
            streak = 0
            for _, row in df_training.iterrows():
                if row[spieler]:
                    streak += 1
                else:
                    break
            
            # Last 5 trainings
            letzte_5 = df_training.head(5)[spieler].sum()
            letzte_5_quote = (letzte_5 / min(5, gesamt_trainings)) * 100
            
            spieler_stats.append({
                'Spieler': spieler,
                'Anwesenheit': anwesenheit,
                'Quote': quote,
                'Letzte_5': letzte_5_quote,
                'Aktuelle_Serie': streak,
                'Status': '🔥' if streak >= 3 else '⚡' if streak >= 1 else '😴'
            })
        
        spieler_df = pd.DataFrame(spieler_stats).sort_values('Quote', ascending=False)
        
        # Display player cards
        for i, (_, player) in enumerate(spieler_df.iterrows()):
            if i % 2 == 0:
                col1, col2 = st.columns(2)
            
            col = col1 if i % 2 == 0 else col2
            
            with col:
                # Color coding based on attendance
                if player['Quote'] >= 90:
                    border_color = "#28a745"  # Green
                elif player['Quote'] >= 75:
                    border_color = "#ffc107"  # Yellow
                else:
                    border_color = "#dc3545"  # Red
                
                st.markdown(f"""
                <div style='
                    padding: 1rem;
                    border-left: 4px solid {border_color};
                    background-color: #f8f9fa;
                    border-radius: 5px;
                    margin: 0.5rem 0;
                '>
                    <h4 style='margin: 0 0 0.5rem 0;'>{player['Status']} {player['Spieler']}</h4>
                    <p style='margin: 0.2rem 0;'><strong>Gesamt:</strong> {player['Quote']:.1f}% ({player['Anwesenheit']}/{gesamt_trainings})</p>
                    <p style='margin: 0.2rem 0;'><strong>Letzte 5:</strong> {player['Letzte_5']:.1f}%</p>
                    <p style='margin: 0.2rem 0;'><strong>Serie:</strong> {player['Aktuelle_Serie']} Trainings</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Attendance table
        st.subheader("📅 Trainings-Übersicht")
        
        # Format training data for display
        display_training = df_training.copy()
        display_training['Datum'] = display_training['Datum'].dt.strftime("%d.%m.%Y")
        
        # Replace True/False with emojis
        for spieler in spieler_namen:
            display_training[spieler] = display_training[spieler].apply(lambda x: '✅' if x else '❌')
        
        # Add attendance count per training
        anwesenheit_pro_training = []
        for _, row in df_training.iterrows():
            count = sum(row[spieler_namen])
            anwesenheit_pro_training.append(f"{count}/{len(spieler_namen)}")
        
        display_training['Anwesend'] = anwesenheit_pro_training
        
        st.dataframe(display_training, use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader("📈 Trends und Analysen")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Attendance trend over time
            df_trend = df_training.copy()
            df_trend['Anwesenheit_Gesamt'] = df_trend[spieler_namen].sum(axis=1)
            df_trend['Anwesenheit_Prozent'] = (df_trend['Anwesenheit_Gesamt'] / len(spieler_namen)) * 100
            df_trend = df_trend.sort_values('Datum')
            
            fig1 = px.line(df_trend, x='Datum', y='Anwesenheit_Prozent',
                          title='Anwesenheitstrend über Zeit',
                          line_shape='spline')
            fig1.update_traces(line_color='#1e3c72', line_width=3, mode='lines+markers')
            fig1.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                yaxis_title="Anwesenheit (%)",
                yaxis=dict(range=[0, 100])
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Individual attendance comparison
            attendance_data = []
            for spieler in spieler_namen:
                quote = (df_training[spieler].sum() / gesamt_trainings) * 100
                attendance_data.append({'Spieler': spieler, 'Quote': quote})
            
            fig2 = px.bar(attendance_data, x='Quote', y='Spieler',
                         title='Anwesenheitsquote pro Spieler',
                         orientation='h',
                         color='Quote',
                         color_continuous_scale='RdYlGn')
            fig2.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(range=[0, 100])
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Weekly analysis
        st.subheader("📊 Wöchentliche Analyse")
        
        # Group by week
        df_weekly = df_training.copy()
        df_weekly['Woche'] = df_weekly['Datum'].dt.to_period('W')
        weekly_stats = df_weekly.groupby('Woche')[spieler_namen].mean() * 100
        weekly_stats = weekly_stats.reset_index()
        weekly_stats['Woche'] = weekly_stats['Woche'].astype(str)
        
        # Melt for visualization
        weekly_melted = weekly_stats.melt(id_vars=['Woche'], 
                                        value_vars=spieler_namen,
                                        var_name='Spieler', 
                                        value_name='Anwesenheit')
        
        fig3 = px.line(weekly_melted, x='Woche', y='Anwesenheit', 
                      color='Spieler',
                      title='Wöchentliche Anwesenheit pro Spieler',
                      line_shape='spline')
        fig3.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(range=[0, 100]),
            xaxis_title="Kalenderwoche",
            yaxis_title="Anwesenheit (%)"
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        # Best/Worst performers
        st.subheader("🏆 Top & Flop")
        
        col1, col2, col3 = st.columns(3)
        
        best_player = spieler_df.iloc[0]
        worst_player = spieler_df.iloc[-1]
        most_consistent = spieler_df.loc[spieler_df['Letzte_5'].idxmax()]
        
        with col1:
            st.success(f"""
            **🥇 Beste Anwesenheit**
            
            {best_player['Spieler']}
            
            {best_player['Quote']:.1f}% Anwesenheit
            """)
        
        with col2:
            st.info(f"""
            **🔥 Heißeste Serie**
            
            {spieler_df.loc[spieler_df['Aktuelle_Serie'].idxmax(), 'Spieler']}
            
            {spieler_df['Aktuelle_Serie'].max()} Trainings in Folge
            """)
        
        with col3:
            st.warning(f"""
            **⚠️ Braucht Motivation**
            
            {worst_player['Spieler']}
            
            {worst_player['Quote']:.1f}% Anwesenheit
            """)
    
    with tab3:
        st.subheader("📋 Neues Training eintragen")
        
        with st.form("add_training"):
            col1, col2 = st.columns(2)
            
            with col1:
                training_datum = st.date_input("Trainingsdatum", value=datetime.now().date())
                training_typ = st.selectbox("Trainingsart", 
                                          ["Mannschaftstraining", "Konditionstraining", "Techniktraining", "Torwarttraining"])
            
            with col2:
                wetter = st.selectbox("Wetter", ["Sonnig ☀️", "Bewölkt ☁️", "Regen 🌧️", "Schnee ❄️"])
                intensität = st.slider("Trainingsintensität", 1, 10, 7)
            
            st.markdown("### Anwesenheit")
            
            anwesenheit = {}
            cols = st.columns(3)
            
            for i, spieler in enumerate(spieler_namen):
                col = cols[i % 3]
                with col:
                    anwesenheit[spieler] = st.checkbox(spieler, value=True)
            
            notizen = st.text_area("Trainingsnotizen (optional)")
            
            submitted = st.form_submit_button("Training speichern")
            
            if submitted:
                anwesende = sum(anwesenheit.values())
                st.success(f"✅ Training vom {training_datum.strftime('%d.%m.%Y')} wurde gespeichert!")
                st.info(f"📊 Anwesenheit: {anwesende}/{len(spieler_namen)} Spieler")
                st.info("💡 In einer echten App würde dieses Training in der Datenbank gespeichert.")
                
                # Show impact on statistics
                for spieler, anwesend in anwesenheit.items():
                    if not anwesend:
                        aktuelle_quote = (df_training[spieler].sum() / gesamt_trainings) * 100
                        neue_quote = (df_training[spieler].sum() / (gesamt_trainings + 1)) * 100
                        st.warning(f"⚠️ {spieler} fehlt - Quote sinkt von {aktuelle_quote:.1f}% auf {neue_quote:.1f}%")
        
        st.markdown("---")
        
        # Quick actions
        st.subheader("⚡ Schnellaktionen")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ Alle anwesend", use_container_width=True):
                st.info("Vollständige Anwesenheit würde eingetragen")
        
        with col2:
            if st.button("📋 Template laden", use_container_width=True):
                st.info("Letztes Training als Vorlage würde geladen")
        
        with col3:
            if st.button("❌ Training abgesagt", use_container_width=True):
                st.info("Training-Absage würde vermerkt")
    
    with tab4:
        st.subheader("⚙️ Trainingseinstellungen")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📅 Trainingszeiten**")
            
            trainingszeiten = {
                "Dienstag": "19:00 - 20:30",
                "Donnerstag": "19:00 - 20:30", 
                "Sonntag (Spieltag)": "Nach Ansetzung"
            }
            
            for tag, zeit in trainingszeiten.items():
                st.write(f"**{tag}:** {zeit}")
            
            st.markdown("---")
            
            st.markdown("**🎯 Anwesenheitsziele**")
            
            ziel_quote = st.slider("Team-Anwesenheitsziel (%)", 60, 100, 85)
            individuelles_ziel = st.slider("Individuelles Mindest-Ziel (%)", 50, 95, 75)
            
            if st.button("Ziele speichern"):
                st.success("✅ Anwesenheitsziele gespeichert!")
        
        with col2:
            st.markdown("**🏆 Anwesenheits-Belohnungen**")
            
            belohnungen = {
                "100% im Monat": "Freigetränk",
                "95%+ in der Saison": "Team-Dinner",
                "Beste Quote": "MVP-Auszeichnung",
                "Längste Serie": "Bonus-Freizeit"
            }
            
            for kriterium, belohnung in belohnungen.items():
                st.write(f"**{kriterium}:** {belohnung}")
            
            st.markdown("---")
            
            st.markdown("**📊 Export & Reports**")
            
            if st.button("📈 Monatsreport", use_container_width=True):
                st.info("Monatsreport würde erstellt")
            
            if st.button("📋 Anwesenheitsliste", use_container_width=True):
                st.info("Excel-Export würde gestartet")
            
            if st.button("📧 Email-Reminder", use_container_width=True):
                st.info("Erinnerung würde an alle gesendet")
        
        st.markdown("---")
        
        # Performance tracking
        st.subheader("📈 Leistungstracking (Zukunft)")
        
        st.info("""
        **Geplante Funktionen:**
        - 🏃‍♂️ Laufzeiten und Fitness-Tests
        - ⚽ Torschüsse und Passgenauigkeit
        - 🎯 Individuelle Leistungsziele
        - 📊 Fortschritts-Visualisierung
        - 🏆 Leistungsvergleiche
        """)
        
        if st.button("🔔 Benachrichtigung bei neuen Features"):
            st.success("✅ Du wirst über neue Tracking-Features informiert!") 