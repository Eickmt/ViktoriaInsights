import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import random

def show():
    st.title("⭐ Team Gimmicks")
    st.subheader("Spaß und Gemeinschaft für Viktoria Buchholz")
    
    # Tabs for different gimmick features
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎲 Zufalls-Generator", "💬 Sprüche des Tages", "📊 Team-Umfragen", "📸 Fotogalerie", "🎮 Team-Spiele"])
    
    with tab1:
        st.subheader("🎲 Zufalls-Generator")
        st.write("Zufällige Entscheidungen für das Team!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🍕 Was essen wir nach dem Spiel?")
            
            restaurant_optionen = [
                "Pizza Mario", "Burger King", "Döner Ali", "China-Restaurant Lotus",
                "Griechisches Restaurant Athena", "Schnitzelhaus", "Subway",
                "KFC", "Mexican Cantina", "Steakhouse", "Italiener Da Luigi"
            ]
            
            if st.button("🎯 Restaurant wählen", use_container_width=True):
                gewähltes_restaurant = random.choice(restaurant_optionen)
                st.success(f"🍴 **{gewähltes_restaurant}** wurde ausgewählt!")
                st.balloons()
            
            st.markdown("### 🏃‍♂️ Wer holt die Bälle?")
            
            spieler_namen = ["Thomas Schmidt", "Max Mustermann", "Michael Weber", 
                           "Stefan König", "Andreas Müller", "Christian Bauer"]
            
            if st.button("👆 Ballholer bestimmen", use_container_width=True):
                ballholer = random.choice(spieler_namen)
                st.warning(f"🥅 **{ballholer}** ist heute dran mit Bälle holen!")
            
            st.markdown("### 🚗 Wer fährt?")
            
            if st.button("🔑 Fahrer wählen", use_container_width=True):
                fahrer = random.choice(spieler_namen)
                st.info(f"🚙 **{fahrer}** ist heute der Fahrer!")
        
        with col2:
            st.markdown("### 🎯 Trainingsübung wählen")
            
            übungen = [
                "Passspiel im Dreieck", "Sprint-Training", "Koordinationsleiter",
                "Torschuss-Training", "1 gegen 1", "Kopfball-Training",
                "Elfmeter-Schießen", "Ausdauerlauf", "Technik am Ball",
                "Flanken und Verwertung", "Spielaufbau aus der Abwehr"
            ]
            
            if st.button("🏃‍♂️ Übung des Tages", use_container_width=True):
                übung = random.choice(übungen)
                st.success(f"⚽ **{übung}** ist heute dran!")
            
            st.markdown("### 🎵 Kabinen-Musik")
            
            playlist = [
                "Eye of the Tiger", "We Will Rock You", "Seven Nation Army",
                "Kernkraft 400", "Chelsea Dagger", "Don't Stop Believin'",
                "Pump It", "Till I Collapse", "Thunder", "Believer"
            ]
            
            if st.button("🎧 Song wählen", use_container_width=True):
                song = random.choice(playlist)
                st.success(f"🎶 **{song}** läuft in der Kabine!")
            
            st.markdown("### 🏆 Motivationsspruch")
            
            sprüche = [
                "Gebt alles, auch wenn es weh tut!",
                "Ein Team, ein Traum, ein Ziel!",
                "Heute zeigen wir, was in uns steckt!",
                "Der Ball ist rund und das Spiel dauert 90 Minuten!",
                "Wer kämpft, kann verlieren. Wer nicht kämpft, hat schon verloren!"
            ]
            
            if st.button("💪 Motivation tanken", use_container_width=True):
                spruch = random.choice(sprüche)
                st.success(f"🔥 **{spruch}**")
    
    with tab2:
        st.subheader("💬 Sprüche des Tages")
        st.write("Die besten (und schlechtesten) Zitate aus der Mannschaft!")
        
        # Sample quotes data
        sprüche_data = [
            {"Datum": "2024-12-01", "Spieler": "Thomas Schmidt", "Spruch": "Ich hab den Ball gar nicht gesehen!", "Kontext": "Nach einem Eigentor", "Votes": 15},
            {"Datum": "2024-11-30", "Spieler": "Max Mustermann", "Spruch": "Das war Absicht!", "Kontext": "Nach einem Glückstreffer", "Votes": 12},
            {"Datum": "2024-11-29", "Spieler": "Michael Weber", "Spruch": "Trainer, ich bin nicht müde!", "Kontext": "Völlig außer Atem", "Votes": 18},
            {"Datum": "2024-11-28", "Spieler": "Stefan König", "Spruch": "Links oder rechts?", "Kontext": "Steht allein vor dem Tor", "Votes": 9},
            {"Datum": "2024-11-27", "Spieler": "Andreas Müller", "Spruch": "Das hätte Messi auch nicht gemacht!", "Kontext": "Nach einem Fehlpass", "Votes": 21},
            {"Datum": "2024-11-26", "Spieler": "Christian Bauer", "Spruch": "Ich dachte, das ist Training...", "Kontext": "Im Punktspiel", "Votes": 14},
        ]
        
        df_sprüche = pd.DataFrame(sprüche_data)
        df_sprüche['Datum'] = pd.to_datetime(df_sprüche['Datum'])
        df_sprüche = df_sprüche.sort_values('Votes', ascending=False)
        
        # Display top quote
        top_spruch = df_sprüche.iloc[0]
        
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #667eea, #764ba2);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            color: white;
            margin: 2rem 0;
        '>
            <h2 style='margin: 0;'>🏆 Spruch der Woche</h2>
            <h3 style='margin: 1rem 0; font-style: italic; color: #fff200;'>"{top_spruch['Spruch']}"</h3>
            <p style='margin: 0.5rem 0; font-size: 1.2rem;'>- {top_spruch['Spieler']}</p>
            <p style='margin: 0; opacity: 0.8;'>{top_spruch['Kontext']} | {top_spruch['Votes']} Votes</p>
        </div>
        """, unsafe_allow_html=True)
        
        # All quotes
        st.subheader("📜 Alle Sprüche")
        
        for _, spruch in df_sprüche.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([4, 1, 1])
                
                with col1:
                    st.markdown(f"**\"{spruch['Spruch']}\"**")
                    st.markdown(f"*- {spruch['Spieler']} ({spruch['Kontext']})*")
                
                with col2:
                    st.metric("👍 Votes", spruch['Votes'])
                
                with col3:
                    if st.button("👍", key=f"vote_{spruch['Datum']}"):
                        st.success("Vote gezählt!")
                
                st.markdown("---")
        
        # Add new quote
        st.subheader("➕ Neuen Spruch hinzufügen")
        
        with st.form("add_quote"):
            col1, col2 = st.columns(2)
            
            with col1:
                sprecher = st.selectbox("Wer hat's gesagt?", spieler_namen)
                spruch_text = st.text_input("Der Spruch")
            
            with col2:
                kontext = st.text_input("Kontext/Situation")
                datum = st.date_input("Datum", value=datetime.now().date())
            
            submitted = st.form_submit_button("Spruch hinzufügen")
            
            if submitted and spruch_text:
                st.success(f"✅ Spruch von {sprecher} wurde hinzugefügt!")
                st.info(f"💬 \"{spruch_text}\" - {sprecher}")
                st.balloons()
    
    with tab3:
        st.subheader("📊 Team-Umfragen")
        st.write("Aktuelle Abstimmungen und Meinungsbilder")
        
        # Current polls
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏆 Wer wird Torschützenkönig?")
            
            torjäger_votes = {
                "Stefan König": 8,
                "Max Mustermann": 12,
                "Michael Weber": 6,
                "Thomas Schmidt": 3,
                "Andreas Müller": 5,
                "Christian Bauer": 2
            }
            
            for spieler, votes in torjäger_votes.items():
                progress = votes / sum(torjäger_votes.values())
                st.write(f"**{spieler}**: {votes} Stimmen")
                st.progress(progress)
            
            meine_stimme = st.selectbox("Deine Stimme:", list(torjäger_votes.keys()), key="torjäger")
            if st.button("Abstimmen", key="vote_torjäger"):
                st.success(f"✅ Stimme für {meine_stimme} abgegeben!")
        
        with col2:
            st.markdown("### 🍕 Wo feiern wir den Aufstieg?")
            
            locations = {
                "Vereinsheim": 15,
                "Restaurant": 8,
                "Beachclub": 12,
                "Zuhause bei Thomas": 3,
                "Kneipe": 7
            }
            
            fig = px.pie(values=list(locations.values()), names=list(locations.keys()),
                        title="Abstimmung: Feier-Location")
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
            
            meine_location = st.selectbox("Deine Wahl:", list(locations.keys()), key="location")
            if st.button("Abstimmen", key="vote_location"):
                st.success(f"✅ Stimme für {meine_location} abgegeben!")
        
        # New poll creation
        st.markdown("---")
        st.subheader("➕ Neue Umfrage erstellen")
        
        with st.form("create_poll"):
            poll_title = st.text_input("Umfrage-Titel")
            
            col1, col2 = st.columns(2)
            with col1:
                option1 = st.text_input("Option 1")
                option2 = st.text_input("Option 2")
            with col2:
                option3 = st.text_input("Option 3 (optional)")
                option4 = st.text_input("Option 4 (optional)")
            
            poll_duration = st.selectbox("Laufzeit", ["1 Tag", "3 Tage", "1 Woche", "1 Monat"])
            
            submitted = st.form_submit_button("Umfrage erstellen")
            
            if submitted and poll_title and option1 and option2:
                st.success(f"✅ Umfrage '{poll_title}' wurde erstellt!")
                st.info("💡 In einer echten App würde die Umfrage jetzt für alle sichtbar sein.")
    
    with tab4:
        st.subheader("📸 Team-Fotogalerie")
        st.write("Erinnerungen und Highlights der Mannschaft")
        
        # Photo categories
        photo_tabs = st.tabs(["🏆 Siege", "🎉 Feiern", "💪 Training", "😂 Lustige Momente"])
        
        with photo_tabs[0]:
            st.markdown("### 🏆 Unsere Siege")
            
            siege_fotos = [
                {"Titel": "Sieg gegen SV Muster", "Datum": "2024-11-24", "Ergebnis": "3:1"},
                {"Titel": "Derbysieg!", "Datum": "2024-11-17", "Ergebnis": "2:0"},
                {"Titel": "Pokalrunde überstanden", "Datum": "2024-11-10", "Ergebnis": "4:2"},
            ]
            
            for foto in siege_fotos:
                with st.container():
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.image("https://via.placeholder.com/200x150/28a745/white?text=SIEG", 
                               caption=foto['Titel'])
                    with col2:
                        st.markdown(f"**{foto['Titel']}**")
                        st.write(f"📅 {foto['Datum']}")
                        st.write(f"⚽ Endstand: {foto['Ergebnis']}")
                        if st.button(f"👍 Like", key=f"like_sieg_{foto['Datum']}"):
                            st.success("👍 Gefällt dir!")
                    st.markdown("---")
        
        with photo_tabs[1]:
            st.markdown("### 🎉 Mannschaftsfeiern")
            
            st.image("https://via.placeholder.com/600x300/ff6b6b/white?text=MANNSCHAFTSFEIER", 
                    caption="Saisonabschluss 2024")
            
            st.write("🍻 **Unvergessliche Nacht!** - Die ganze Mannschaft hat bis in die frühen Morgenstunden gefeiert.")
            
            if st.button("📷 Mehr Fotos hochladen"):
                st.info("📱 In einer echten App könntest du hier Fotos hochladen!")
        
        with photo_tabs[2]:
            st.markdown("### 💪 Trainingsmomente")
            
            training_momente = [
                "Intensive Konditionseinheit im Regen",
                "Neuer Trick von Stefan König",
                "Torwart-Training mit Max",
                "Taktikschulung auf dem Platz"
            ]
            
            for i, moment in enumerate(training_momente):
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(f"https://via.placeholder.com/200x150/1e3c72/white?text=TRAINING+{i+1}")
                with col2:
                    st.write(f"📸 **{moment}**")
                    st.write("💪 Harte Arbeit zahlt sich aus!")
        
        with photo_tabs[3]:
            st.markdown("### 😂 Lustige Momente")
            
            st.image("https://via.placeholder.com/400x300/ffc107/white?text=FAIL", 
                    caption="Thomas' Eigentor beim Training 😂")
            
            st.write("🤣 **Der Moment des Jahres!** Thomas wollte den Ball wegschlagen und trifft ins eigene Tor.")
            
            if st.button("😂 Mehr lustige Momente"):
                st.info("Sammelt mehr lustige Clips für die Saisonabschluss-Show!")
    
    with tab5:
        st.subheader("🎮 Team-Spiele & Challenges")
        st.write("Interaktive Spiele und Herausforderungen")
        
        game_tabs = st.tabs(["🎯 Tippspiel", "🧠 Fußball-Quiz", "⚽ Skill Challenge", "🏆 Leaderboard"])
        
        with game_tabs[0]:
            st.markdown("### 🎯 Bundesliga-Tippspiel")
            
            # Sample matches for tipping
            spiele = [
                {"Heim": "Bayern München", "Gast": "Borussia Dortmund", "Datum": "2024-12-07"},
                {"Heim": "RB Leipzig", "Gast": "Bayer Leverkusen", "Datum": "2024-12-08"},
                {"Heim": "SC Freiburg", "Gast": "VfB Stuttgart", "Datum": "2024-12-08"},
            ]
            
            for spiel in spiele:
                with st.container():
                    st.markdown(f"**{spiel['Heim']} vs {spiel['Gast']}** ({spiel['Datum']})")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        heim_tore = st.number_input(f"Tore {spiel['Heim']}", 0, 10, 1, key=f"heim_{spiel['Datum']}")
                    with col2:
                        st.write("**:**")
                    with col3:
                        gast_tore = st.number_input(f"Tore {spiel['Gast']}", 0, 10, 1, key=f"gast_{spiel['Datum']}")
                    
                    if st.button(f"Tipp abgeben", key=f"tipp_{spiel['Datum']}"):
                        st.success(f"✅ Tipp {heim_tore}:{gast_tore} für {spiel['Heim']} vs {spiel['Gast']} abgegeben!")
                    
                    st.markdown("---")
            
            # Tippspiel standings
            st.markdown("### 🏆 Tippspiel-Tabelle")
            
            tippspieler = [
                {"Name": "Max Mustermann", "Punkte": 24, "Richtige": 8},
                {"Name": "Thomas Schmidt", "Punkte": 21, "Richtige": 7},
                {"Name": "Michael Weber", "Punkte": 18, "Richtige": 6},
                {"Name": "Stefan König", "Punkte": 15, "Richtige": 5},
                {"Name": "Andreas Müller", "Punkte": 12, "Richtige": 4},
            ]
            
            df_tipp = pd.DataFrame(tippspieler)
            st.dataframe(df_tipp, use_container_width=True, hide_index=True)
        
        with game_tabs[1]:
            st.markdown("### 🧠 Fußball-Quiz")
            
            # Quiz questions
            quiz_fragen = [
                {
                    "Frage": "Wer gewann die WM 2014?",
                    "Optionen": ["Deutschland", "Argentinien", "Brasilien", "Spanien"],
                    "Richtig": "Deutschland"
                },
                {
                    "Frage": "Wie viele Spieler stehen gleichzeitig auf dem Platz?",
                    "Optionen": ["20", "22", "24", "18"],
                    "Richtig": "22"
                },
                {
                    "Frage": "Welcher Verein hat die meisten Champions League Titel?",
                    "Optionen": ["Real Madrid", "Barcelona", "Bayern München", "AC Milan"],
                    "Richtig": "Real Madrid"
                }
            ]
            
            if 'quiz_score' not in st.session_state:
                st.session_state.quiz_score = 0
                st.session_state.quiz_question = 0
            
            if st.session_state.quiz_question < len(quiz_fragen):
                aktuelle_frage = quiz_fragen[st.session_state.quiz_question]
                
                st.markdown(f"**Frage {st.session_state.quiz_question + 1}:** {aktuelle_frage['Frage']}")
                
                antwort = st.radio("Wähle deine Antwort:", aktuelle_frage['Optionen'])
                
                if st.button("Antwort bestätigen"):
                    if antwort == aktuelle_frage['Richtig']:
                        st.success("✅ Richtig!")
                        st.session_state.quiz_score += 1
                    else:
                        st.error(f"❌ Falsch! Richtige Antwort: {aktuelle_frage['Richtig']}")
                    
                    st.session_state.quiz_question += 1
                    st.experimental_rerun()
            else:
                st.success(f"🎉 Quiz beendet! Du hast {st.session_state.quiz_score}/{len(quiz_fragen)} Punkte erreicht!")
                
                if st.button("Quiz neu starten"):
                    st.session_state.quiz_score = 0
                    st.session_state.quiz_question = 0
                    st.experimental_rerun()
        
        with game_tabs[2]:
            st.markdown("### ⚽ Skill Challenge")
            st.write("Teste deine Fußball-Skills!")
            
            challenges = [
                {"Name": "Jonglier-Challenge", "Beschreibung": "Wie viele Ballkontakte schaffst du?", "Rekord": "78 (Max Mustermann)"},
                {"Name": "Freistoß-Präzision", "Beschreibung": "Triff das Lattenkreuz!", "Rekord": "3/5 (Stefan König)"},
                {"Name": "Sprint-Challenge", "Beschreibung": "30m in Bestzeit", "Rekord": "4.2s (Michael Weber)"},
                {"Name": "Kopfball-Duell", "Beschreibung": "Kopfball-Weitschuss", "Rekord": "23m (Christian Bauer)"},
            ]
            
            for challenge in challenges:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**{challenge['Name']}**")
                        st.write(challenge['Beschreibung'])
                        st.write(f"🏆 Rekord: {challenge['Rekord']}")
                    
                    with col2:
                        if st.button("🎯 Starten", key=f"challenge_{challenge['Name']}"):
                            st.info("Challenge startet in der nächsten Trainingseinheit!")
                    
                    st.markdown("---")
        
        with game_tabs[3]:
            st.markdown("### 🏆 Gesamt-Leaderboard")
            
            # Combined leaderboard from all activities
            leaderboard_data = [
                {"Spieler": "Max Mustermann", "Tippspiel": 24, "Quiz": 85, "Challenges": 3, "Gesamt": 112},
                {"Spieler": "Stefan König", "Tippspiel": 15, "Quiz": 90, "Challenges": 4, "Gesamt": 109},
                {"Spieler": "Thomas Schmidt", "Tippspiel": 21, "Quiz": 75, "Challenges": 2, "Gesamt": 98},
                {"Spieler": "Michael Weber", "Tippspiel": 18, "Quiz": 80, "Challenges": 3, "Gesamt": 101},
                {"Spieler": "Andreas Müller", "Tippspiel": 12, "Quiz": 70, "Challenges": 1, "Gesamt": 83},
                {"Spieler": "Christian Bauer", "Tippspiel": 9, "Quiz": 65, "Challenges": 2, "Gesamt": 76},
            ]
            
            df_leaderboard = pd.DataFrame(leaderboard_data).sort_values('Gesamt', ascending=False)
            df_leaderboard.index = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣', '6️⃣']
            
            st.dataframe(df_leaderboard, use_container_width=True)
            
            # Achievements
            st.markdown("### 🏅 Errungenschaften")
            
            achievements = [
                {"Titel": "Quiz-Master", "Beschreibung": "Alle Quiz-Fragen richtig beantwortet", "Spieler": "Stefan König"},
                {"Titel": "Tipp-König", "Beschreibung": "Beste Tippspiel-Performance", "Spieler": "Max Mustermann"},
                {"Titel": "Challenge-Champion", "Beschreibung": "Meiste Challenge-Siege", "Spieler": "Stefan König"},
                {"Titel": "Allrounder", "Beschreibung": "Top 3 in allen Kategorien", "Spieler": "Max Mustermann"},
            ]
            
            for achievement in achievements:
                st.success(f"🏅 **{achievement['Titel']}** - {achievement['Spieler']}: {achievement['Beschreibung']}")
        
        # Fun facts
        st.markdown("---")
        st.subheader("🎉 Fun Facts")
        
        fun_facts = [
            "🏃‍♂️ Die Mannschaft ist zusammen schon über 500km gelaufen!",
            "⚽ Insgesamt wurden 127 Tore in dieser Saison geschossen",
            "🤡 Thomas Schmidt führt die Esel-der-Woche Statistik mit 4 Auszeichnungen an",
            "💰 Die Mannschaftskasse ist seit Saisonbeginn um 500€ gewachsen",
            "📸 In der Fotogalerie sind bereits 89 Bilder gespeichert",
            "🎯 Max Mustermann führt das Tippspiel seit 8 Wochen an"
        ]
        
        for fact in fun_facts:
            st.info(fact) 