import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

def show():
    st.title("🤡 Esel der Woche")
    st.subheader("Strafen und der aktuelle Wochenesel")
    
    # Sample penalty data
    strafen_data = [
        {"Datum": "2024-12-01", "Spieler": "Thomas Schmidt", "Strafe": "Zu spät zum Training", "Betrag": 10.00},
        {"Datum": "2024-11-30", "Spieler": "Thomas Schmidt", "Strafe": "Handy im Training", "Betrag": 5.00},
        {"Datum": "2024-11-29", "Spieler": "Thomas Schmidt", "Strafe": "Vergessene Schuhe", "Betrag": 15.00},
        {"Datum": "2024-11-28", "Spieler": "Max Mustermann", "Strafe": "Zu spät zum Spiel", "Betrag": 25.00},
        {"Datum": "2024-11-25", "Spieler": "Michael Weber", "Strafe": "Unsportliches Verhalten", "Betrag": 50.00},
        {"Datum": "2024-11-24", "Spieler": "Stefan König", "Strafe": "Zu spät zum Training", "Betrag": 10.00},
        {"Datum": "2024-11-22", "Spieler": "Andreas Müller", "Strafe": "Handy im Training", "Betrag": 5.00},
        {"Datum": "2024-11-20", "Spieler": "Thomas Schmidt", "Strafe": "Vergessene Ausrüstung", "Betrag": 15.00},
        {"Datum": "2024-11-18", "Spieler": "Christian Bauer", "Strafe": "Zu spät zum Training", "Betrag": 10.00},
        {"Datum": "2024-11-15", "Spieler": "Max Mustermann", "Strafe": "Handy im Training", "Betrag": 5.00},
    ]
    
    df_strafen = pd.DataFrame(strafen_data)
    df_strafen['Datum'] = pd.to_datetime(df_strafen['Datum'])
    df_strafen = df_strafen.sort_values('Datum', ascending=False)
    
    # Calculate current week's donkey
    heute = datetime.now()
    woche_start = heute - timedelta(days=7)
    aktuelle_woche = df_strafen[df_strafen['Datum'] >= woche_start]
    
    if len(aktuelle_woche) > 0:
        esel_stats = aktuelle_woche.groupby('Spieler').agg({
            'Betrag': ['sum', 'count']
        }).round(2)
        esel_stats.columns = ['Gesamt_Betrag', 'Anzahl_Strafen']
        esel_stats = esel_stats.reset_index().sort_values('Gesamt_Betrag', ascending=False)
        
        aktueller_esel = esel_stats.iloc[0]['Spieler']
        esel_betrag = esel_stats.iloc[0]['Gesamt_Betrag']
        esel_anzahl = esel_stats.iloc[0]['Anzahl_Strafen']
    else:
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
            <h1 style='margin: 1rem 0; font-size: 3rem; color: #fff200; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);'>{aktueller_esel}</h1>
            <div style='font-size: 1.5rem; margin-top: 1rem;'>
                <p style='margin: 0.5rem 0;'>💰 <strong>€{esel_betrag:.2f}</strong> in Strafen</p>
                <p style='margin: 0.5rem 0;'>📊 <strong>{int(esel_anzahl)}</strong> Strafen diese Woche</p>
            </div>
            <p style='font-size: 1.2rem; margin-top: 1.5rem; opacity: 0.9;'>
                👑 Herzlichen Glückwunsch zum Titel! 👑
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Fun animations and effects
        st.balloons()
        
        # Donkey "Hall of Shame" this week
        if len(esel_stats) > 1:
            st.subheader("🏆 Top-Esel diese Woche")
            
            col1, col2, col3 = st.columns(3)
            
            for i, (_, row) in enumerate(esel_stats.head(3).iterrows()):
                col = [col1, col2, col3][i]
                emoji = ["🥇", "🥈", "🥉"][i]
                
                with col:
                    st.metric(
                        label=f"{emoji} {row['Spieler']}",
                        value=f"€{row['Gesamt_Betrag']:.2f}",
                        delta=f"{int(row['Anzahl_Strafen'])} Strafen"
                    )
    else:
        st.success("🎉 Diese Woche gab es noch keinen Esel! Alle waren brav!")
    
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
        letzte_30_tage = df_strafen[df_strafen['Datum'] >= (datetime.now() - timedelta(days=30))]
        strafen_30_tage = len(letzte_30_tage)
        st.metric("📅 Letzte 30 Tage", strafen_30_tage)
    
    with col4:
        durchschnitt = df_strafen['Betrag'].mean()
        st.metric("📈 Ø Strafe", f"€{durchschnitt:.2f}")
    
    # Tabs for detailed analysis
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Strafen-Liste", "📊 Statistiken", "➕ Neue Strafe", "🏆 Esel-Historie"])
    
    with tab1:
        st.subheader("📋 Alle Strafen")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            spieler_filter = st.selectbox("Spieler", ["Alle"] + list(df_strafen['Spieler'].unique()))
        with col2:
            zeitraum = st.selectbox("Zeitraum", ["Alle", "Diese Woche", "Dieser Monat", "Letzte 3 Monate"])
        with col3:
            anzahl_anzeigen = st.selectbox("Anzeigen", [10, 20, 50, "Alle"], index=1)
        
        # Apply filters
        filtered_df = df_strafen.copy()
        
        if spieler_filter != "Alle":
            filtered_df = filtered_df[filtered_df['Spieler'] == spieler_filter]
        
        if zeitraum == "Diese Woche":
            filtered_df = filtered_df[filtered_df['Datum'] >= (datetime.now() - timedelta(days=7))]
        elif zeitraum == "Dieser Monat":
            filtered_df = filtered_df[filtered_df['Datum'] >= (datetime.now() - timedelta(days=30))]
        elif zeitraum == "Letzte 3 Monate":
            filtered_df = filtered_df[filtered_df['Datum'] >= (datetime.now() - timedelta(days=90))]
        
        if anzahl_anzeigen != "Alle":
            filtered_df = filtered_df.head(anzahl_anzeigen)
        
        # Display table
        display_df = filtered_df.copy()
        display_df['Datum'] = display_df['Datum'].dt.strftime("%d.%m.%Y")
        display_df['Betrag'] = display_df['Betrag'].apply(lambda x: f"€{x:.2f}")
        
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
        timeline_df['Woche'] = timeline_df['Datum'].dt.to_period('W')
        weekly_penalties = timeline_df.groupby('Woche')['Betrag'].sum().reset_index()
        weekly_penalties['Woche'] = weekly_penalties['Woche'].astype(str)
        
        fig3 = px.line(weekly_penalties, x='Woche', y='Betrag',
                      title='Wöchentliche Strafen-Entwicklung',
                      line_shape='spline')
        fig3.update_traces(line_color='#ff6b6b', line_width=3, mode='lines+markers')
        fig3.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        # Hall of Fame
        st.subheader("🏆 Strafen-Rangliste")
        
        hall_of_fame = spieler_stats.sort_values('Gesamt', ascending=False)
        
        for i, (_, row) in enumerate(hall_of_fame.head(5).iterrows()):
            emoji = ["👑", "🥈", "🥉", "4️⃣", "5️⃣"][i]
            platz = ["Esel-König", "Vize-Esel", "Bronze-Esel", "4. Platz", "5. Platz"][i]
            
            with st.container():
                col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
                with col1:
                    st.markdown(f"### {emoji}")
                with col2:
                    st.markdown(f"**{row['Spieler']}**\n{platz}")
                with col3:
                    st.metric("Gesamt", f"€{row['Gesamt']:.2f}")
                with col4:
                    st.metric("Anzahl", f"{int(row['Anzahl'])}")
    
    with tab3:
        st.subheader("➕ Neue Strafe eingeben")
        
        with st.form("add_penalty"):
            col1, col2 = st.columns(2)
            
            with col1:
                spieler = st.selectbox("Spieler", 
                                     ["Thomas Schmidt", "Max Mustermann", "Michael Weber", 
                                      "Stefan König", "Andreas Müller", "Christian Bauer"])
                strafe_typ = st.selectbox("Strafenart", 
                                        ["Zu spät zum Training", "Zu spät zum Spiel", 
                                         "Handy im Training", "Vergessene Ausrüstung", 
                                         "Unsportliches Verhalten", "Sonstige"])
            
            with col2:
                datum = st.date_input("Datum", value=datetime.now().date())
                if strafe_typ == "Sonstige":
                    betrag = st.number_input("Betrag (€)", min_value=0.01, step=0.01)
                else:
                    # Predefined penalty amounts
                    strafe_beträge = {
                        "Zu spät zum Training": 10.00,
                        "Zu spät zum Spiel": 25.00,
                        "Handy im Training": 5.00,
                        "Vergessene Ausrüstung": 15.00,
                        "Unsportliches Verhalten": 50.00
                    }
                    betrag = st.number_input("Betrag (€)", 
                                           value=strafe_beträge.get(strafe_typ, 10.00),
                                           step=0.01)
            
            zusatz_info = st.text_area("Zusätzliche Informationen (optional)")
            
            submitted = st.form_submit_button("Strafe hinzufügen")
            
            if submitted:
                st.success(f"✅ Strafe für {spieler} wurde hinzugefügt!")
                st.info(f"📋 {strafe_typ} - €{betrag:.2f}")
                
                # Check if this makes them the new donkey
                # (In real app, this would update the database)
                st.warning(f"⚠️ {spieler} ist jetzt ein heißer Kandidat für den Esel der Woche!")
                st.info("💡 In einer echten App würde diese Strafe in der Datenbank gespeichert.")
        
        st.markdown("---")
        
        # Quick penalty buttons
        st.subheader("⚡ Schnell-Strafen")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("⏰ Zu spät (€10)", use_container_width=True):
                st.info("Schnelle 'Zu spät' Strafe würde hinzugefügt")
        
        with col2:
            if st.button("📱 Handy (€5)", use_container_width=True):
                st.info("Handy-Strafe würde hinzugefügt")
        
        with col3:
            if st.button("👕 Ausrüstung (€15)", use_container_width=True):
                st.info("Ausrüstungs-Strafe würde hinzugefügt")
    
    with tab4:
        st.subheader("🏆 Esel der Woche - Historie")
        
        # Generate weekly donkey history
        all_weeks = []
        current_date = datetime.now()
        
        for i in range(8):  # Last 8 weeks
            week_start = current_date - timedelta(days=7*(i+1))
            week_end = current_date - timedelta(days=7*i)
            
            week_penalties = df_strafen[
                (df_strafen['Datum'] >= week_start) & 
                (df_strafen['Datum'] < week_end)
            ]
            
            if len(week_penalties) > 0:
                week_stats = week_penalties.groupby('Spieler')['Betrag'].sum()
                week_donkey = week_stats.idxmax()
                donkey_amount = week_stats.max()
            else:
                week_donkey = "Niemand"
                donkey_amount = 0
            
            all_weeks.append({
                "Woche": f"KW {week_start.isocalendar()[1]}",
                "Datum": f"{week_start.strftime('%d.%m.')} - {week_end.strftime('%d.%m.%Y')}",
                "Esel": week_donkey,
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