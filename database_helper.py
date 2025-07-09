import os
import pandas as pd
from datetime import datetime
import streamlit as st

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

class DatabaseHelper:
    def __init__(self):
        self.supabase = None
        self.connected = False
        self._connection_attempted = False
    
    def _connect(self):
        """Verbindung zu Supabase herstellen"""
        if self._connection_attempted:
            return
            
        self._connection_attempted = True
        
        if not SUPABASE_AVAILABLE:
            return
            
        try:
            # Umgebungsvariablen laden (mehrere Quellen)
            supabase_url = (
                os.getenv("SUPABASE_URL") or 
                st.secrets.get("SUPABASE_URL") or
                st.secrets.get("supabase", {}).get("SUPABASE_URL")
            )
            supabase_key = (
                os.getenv("SUPABASE_ANON_KEY") or 
                st.secrets.get("SUPABASE_ANON_KEY") or
                st.secrets.get("supabase", {}).get("SUPABASE_ANON_KEY")
            )
            
            if not supabase_url or not supabase_key:
                return
            
            # Supabase Client erstellen
            self.supabase: Client = create_client(supabase_url, supabase_key)
            self.connected = True
            
        except Exception as e:
            self.connected = False
    
    def _ensure_connected(self):
        """Stelle sicher, dass eine Verbindung besteht"""
        if not self._connection_attempted:
            self._connect()
    
    def get_birthdays(self):
        """Lade alle Geburtstage aus Supabase"""
        self._ensure_connected()
        
        if not self.connected:
            return pd.DataFrame(columns=['Name', 'Geburtstag', 'Geburtstag_parsed'])
        
        try:
            # Korrekte Tabelle: "Geburtstage" (Großbuchstaben)
            response = self.supabase.table('Geburtstage').select('*').execute()
            
            if response.data:
                df = pd.DataFrame(response.data)
                
                # Datum konvertieren - behandle None-Werte
                if 'Geburtstag' in df.columns:
                    # Filtere None-Werte heraus und bereinige Strings
                    df = df.dropna(subset=['Geburtstag'])
                    # Entferne führende/nachfolgende Leerzeichen
                    df['Geburtstag'] = df['Geburtstag'].astype(str).str.strip()
                    df['Geburtstag_parsed'] = pd.to_datetime(df['Geburtstag'], format='%d.%m.%Y', errors='coerce')
                    df = df.dropna(subset=['Geburtstag_parsed'])  # Entferne fehlgeschlagene Konvertierungen
                    
                    # Sortieren nach Name
                    df = df.sort_values('Name')
                    
                    return df[['Name', 'Geburtstag', 'Geburtstag_parsed']]
                
                return pd.DataFrame(columns=['Name', 'Geburtstag', 'Geburtstag_parsed'])
            else:
                return pd.DataFrame(columns=['Name', 'Geburtstag', 'Geburtstag_parsed'])
                
        except Exception as e:
            print(f"Fehler beim Laden der Geburtstage aus Supabase: {e}")
            return pd.DataFrame(columns=['Name', 'Geburtstag', 'Geburtstag_parsed'])
    

    
    def get_player_names(self):
        """Hole alle Spielernamen (sortiert)"""
        df = self.get_birthdays()
        return sorted(df['Name'].tolist())
    
    def get_available_tables(self):
        """Hole verfügbare Tabellen aus Supabase"""
        self._ensure_connected()
        
        if not self.connected:
            return []
        
        try:
            # Versuche verschiedene bekannte Tabellen
            known_tables = ['Geburtstage', 'geburtstage', 'Strafen', 'strafen', 'trainingsspielsiege', 'Trainingsspielsiege']
            available_tables = []
            
            for table_name in known_tables:
                try:
                    response = self.supabase.table(table_name).select('*').limit(1).execute()
                    if response.data is not None:
                        available_tables.append(table_name)
                except:
                    continue
            
            return available_tables
            
        except Exception as e:
            return []
    
    def test_penalties_table(self):
        """Teste Zugriff auf Strafen-Tabelle"""
        self._ensure_connected()
        
        if not self.connected:
            return {"error": "Keine Verbindung zur Datenbank"}
        
        try:
            # Teste die korrekte Tabelle "strafen"
            response = self.supabase.table('strafen').select('*').limit(3).execute()
            
            if response.data:
                return {
                    "success": True,
                    "table_name": "strafen",
                    "count": len(response.data),
                    "sample_data": response.data[:2],
                    "columns": list(response.data[0].keys()) if response.data else []
                }
            else:
                return {
                    "success": False,
                    "table_name": "strafen",
                    "error": "Tabelle ist leer"
                }
                
        except Exception as e:
            return {
                "success": False,
                "table_name": "strafen",
                "error": str(e)
            }

    def get_penalties(self):
        """Lade alle Strafen aus Supabase"""
        self._ensure_connected()
        
        if not self.connected:
            return self._fallback_penalties()
        
        try:
            # Korrekte Tabelle: "strafen" (kleinbuchstaben)
            response = self.supabase.table('strafen').select('*').order('datum', desc=True).execute()
            
            if response.data:
                df = pd.DataFrame(response.data)
                
                # Datum konvertieren (Format: "07.07.2025")
                if 'datum' in df.columns:
                    df['datum'] = pd.to_datetime(df['datum'], format='%d.%m.%Y', errors='coerce')
                
                # Spalten umbenennen für Kompatibilität mit der Anwendung
                column_mapping = {
                    'datum': 'Datum',
                    'spieler': 'Spieler', 
                    'strafe': 'Strafe',
                    'betrag': 'Betrag',
                    'zusatzinfo': 'Zusatzinfo'
                }
                
                # Nur umbenennen wenn Spalte existiert
                rename_dict = {old: new for old, new in column_mapping.items() if old in df.columns}
                if rename_dict:
                    df = df.rename(columns=rename_dict)
                
                return df.dropna(subset=['Datum'])
                
        except Exception as e:
            print(f"Fehler beim Laden der Strafen aus Supabase: {e}")
            return self._fallback_penalties()
        
        # Fallback wenn Tabelle leer ist
        return self._fallback_penalties()
    
    def add_penalty(self, penalty_data):
        """Füge eine neue Strafe hinzu"""
        self._ensure_connected()
        
        if not self.connected:
            return self._fallback_save_penalty(penalty_data)
        
        try:
            # Spaltennamen für Supabase anpassen
            db_penalty_data = {
                'datum': penalty_data.get('Datum'),
                'spieler': penalty_data.get('Spieler'),
                'strafe': penalty_data.get('Strafe'),
                'betrag': penalty_data.get('Betrag'),
                'zusatzinfo': penalty_data.get('Zusatzinfo', '')
            }
            
            # Daten in Supabase speichern (Tabelle: "strafen")
            response = self.supabase.table('strafen').insert(db_penalty_data).execute()
            
            if response.data:
                return True
            else:
                return self._fallback_save_penalty(penalty_data)
                
        except Exception as e:
            print(f"Fehler beim Speichern der Strafe in Supabase: {e}")
            return self._fallback_save_penalty(penalty_data)
    
    def _fallback_save_penalty(self, penalty_data):
        """Fallback: Speichere Strafe in CSV"""
        try:
            # Lade bestehende CSV
            try:
                df_existing = pd.read_csv("VB_Strafen.csv", sep=";", encoding="utf-8")
            except FileNotFoundError:
                df_existing = pd.DataFrame(columns=['Datum', 'Spieler', 'Strafe', 'Betrag', 'Zusatzinfo'])
            
            # Neue Strafe hinzufügen
            df_new = pd.concat([df_existing, pd.DataFrame([penalty_data])], ignore_index=True)
            
            # In CSV speichern
            df_new.to_csv("VB_Strafen.csv", sep=";", index=False, encoding="utf-8")
            
            return True
            
        except Exception as e:
            return False
    
    def _fallback_penalties(self):
        """Fallback: Lade Strafen aus CSV"""
        try:
            df = pd.read_csv("VB_Strafen.csv", sep=";", encoding="utf-8")
            df['Datum'] = pd.to_datetime(df['Datum'], format='%d.%m.%Y', errors='coerce')
            return df.dropna(subset=['Datum']).sort_values('Datum', ascending=False)
        except Exception as e:
            return pd.DataFrame(columns=['Datum', 'Spieler', 'Strafe', 'Betrag', 'Zusatzinfo'])
    
    def get_training_victories(self):
        """Lade alle Trainingsspielsiege aus Supabase"""
        self._ensure_connected()
        
        if not self.connected:
            return self._fallback_training_victories()
        
        try:
            # Korrekte Tabelle: "trainingsspielsiege" (kleinbuchstaben)
            response = self.supabase.table('trainingsspielsiege').select('*').order('datum', desc=True).execute()
            
            if response.data:
                df = pd.DataFrame(response.data)
                
                # Datum konvertieren
                if 'datum' in df.columns:
                    df['datum'] = pd.to_datetime(df['datum'], errors='coerce')
                
                # Spalten umbenennen für Kompatibilität
                df = df.rename(columns={
                    'spielername': 'Spieler',
                    'datum': 'Datum',
                    'hat_gewonnen': 'Sieg'
                })
                
                return df.dropna(subset=['Datum'])
            else:
                return self._fallback_training_victories()
                
        except Exception as e:
            print(f"Fehler beim Laden der Trainingsspielsiege aus Supabase: {e}")
            return self._fallback_training_victories()
    
    def add_training_victory(self, victory_data):
        """Füge einen neuen Trainingsspielsieg hinzu"""
        self._ensure_connected()
        
        if not self.connected:
            return self._fallback_save_training_victory(victory_data)
        
        try:
            # Spaltennamen für Supabase anpassen
            db_victory_data = {
                'spielername': victory_data.get('Spieler'),
                'datum': victory_data.get('Datum'),
                'hat_gewonnen': victory_data.get('Sieg', False)
            }
            
            # Daten in Supabase speichern (mit UPSERT für Updates)
            response = self.supabase.table('trainingsspielsiege').upsert(db_victory_data).execute()
            
            if response.data:
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Fehler beim Speichern des Trainingssiegs: {e}")
            return self._fallback_save_training_victory(victory_data)

    def add_training_day_entries(self, datum, spieler_mit_sieg, alle_spieler):
        """Füge Einträge für einen kompletten Trainingstag hinzu"""
        self._ensure_connected()
        
        if not self.connected:
            return False, "Keine Datenbankverbindung"
        
        try:
            # Erst alle bestehenden Einträge für diesen Tag löschen
            delete_response = self.supabase.table('trainingsspielsiege').delete().eq('datum', datum).execute()
            
            # Neue Einträge für alle Spieler hinzufügen
            neue_eintraege = []
            for spieler in alle_spieler:
                hat_gewonnen = spieler in spieler_mit_sieg
                neue_eintraege.append({
                    'spielername': spieler,
                    'datum': datum,
                    'hat_gewonnen': hat_gewonnen
                })
            
            # Alle Einträge in einem Batch hinzufügen
            if neue_eintraege:
                response = self.supabase.table('trainingsspielsiege').insert(neue_eintraege).execute()
                
                if response.data:
                    return True, f"✅ {len(neue_eintraege)} Einträge erfolgreich gespeichert"
                else:
                    return False, "❌ Fehler beim Speichern in der Datenbank"
            else:
                return False, "❌ Keine Einträge zum Speichern"
                
        except Exception as e:
            return False, f"❌ Fehler: {str(e)}"

    def get_training_day_entries(self, datum):
        """Lade alle Einträge für einen bestimmten Trainingstag"""
        self._ensure_connected()
        
        if not self.connected:
            return []
        
        try:
            response = self.supabase.table('trainingsspielsiege').select('*').eq('datum', datum).execute()
            
            if response.data:
                return response.data
            else:
                return []
                
        except Exception as e:
            print(f"Fehler beim Laden der Trainingseinträge: {e}")
            return []

    def delete_training_day(self, datum):
        """Lösche alle Einträge für einen Trainingstag"""
        self._ensure_connected()
        
        if not self.connected:
            return False, "Keine Datenbankverbindung"
        
        try:
            response = self.supabase.table('trainingsspielsiege').delete().eq('datum', datum).execute()
            return True, f"✅ Trainingstag {datum} erfolgreich gelöscht"
            
        except Exception as e:
            return False, f"❌ Fehler beim Löschen: {str(e)}"
    
    def get_training_statistics(self):
        """Hole Trainingsstatistiken aus der Datenbank"""
        df = self.get_training_victories()
        
        if df is None or len(df) == 0:
            return {
                'total_trainings': 0,
                'total_victories': 0,
                'latest_training_participants': 0,
                'training_delta': 0,
                'training_delta_text': "Keine Daten"
            }
        
        # Statistiken berechnen
        total_trainings = len(df['Datum'].unique())
        total_victories = len(df[df['Sieg'] == True])
        
        # Letzte zwei Trainings für Delta-Berechnung
        latest_dates = df['Datum'].unique()
        latest_dates = sorted(latest_dates, reverse=True)
        
        latest_training_participants = 0
        training_delta = 0
        training_delta_text = "Keine Daten"
        
        if len(latest_dates) > 0:
            # Teilnehmer des letzten Trainings (2 × Anzahl Siege)
            latest_training = df[df['Datum'] == latest_dates[0]]
            latest_victories = len(latest_training[latest_training['Sieg'] == True])
            latest_training_participants = latest_victories * 2
            
            if len(latest_dates) > 1:
                # Teilnehmer des vorletzten Trainings (2 × Anzahl Siege)
                previous_training = df[df['Datum'] == latest_dates[1]]
                previous_victories = len(previous_training[previous_training['Sieg'] == True])
                previous_participants = previous_victories * 2
                
                training_delta = latest_training_participants - previous_participants
                if training_delta > 0:
                    training_delta_text = f"+ {training_delta}"
                elif training_delta < 0:
                    training_delta_text = f"{training_delta}"
                else:
                    training_delta_text = "±0"
            else:
                training_delta_text = "Erstes Training"
        
        return {
            'total_trainings': total_trainings,
            'total_victories': total_victories,
            'latest_training_participants': latest_training_participants,
            'training_delta': training_delta,
            'training_delta_text': training_delta_text
        }
    
    def _fallback_training_victories(self):
        """Fallback: Lade Trainingsspielsiege aus CSV"""
        try:
            df = pd.read_csv("VB_Trainingsspielsiege.csv", sep=";")
            
            # CSV-Format konvertieren (Spalten = Datum, Zeilen = Spieler)
            spieler_namen = df['Spielername'].tolist()
            datum_spalten = [col for col in df.columns if col != 'Spielername']
            
            # In normalisiertes Format konvertieren
            melted_data = []
            for _, row in df.iterrows():
                spieler = row['Spielername']
                for datum_str in datum_spalten:
                    if pd.notna(row[datum_str]) and row[datum_str] == 1:
                        # Datum parsen
                        try:
                            # Deutsche Monate ersetzen
                            datum_english = datum_str
                            german_months = {
                                'Jan': 'Jan', 'Feb': 'Feb', 'Mrz': 'Mar', 'Apr': 'Apr',
                                'Mai': 'May', 'Jun': 'Jun', 'Jul': 'Jul', 'Aug': 'Aug',
                                'Sep': 'Sep', 'Okt': 'Oct', 'Nov': 'Nov', 'Dez': 'Dec'
                            }
                            for de_month, en_month in german_months.items():
                                if de_month in datum_str:
                                    datum_english = datum_str.replace(de_month, en_month)
                                    break
                            
                            # Datum parsen
                            if any(year in datum_english for year in ['2024', '2025', '2026']):
                                parsed_date = pd.to_datetime(datum_english, format="%d. %b %Y")
                            else:
                                datum_with_year = f"{datum_english} 2024"
                                parsed_date = pd.to_datetime(datum_with_year, format="%d. %b %Y")
                            
                            melted_data.append({
                                'Spieler': spieler,
                                'Datum': parsed_date,
                                'Sieg': True
                            })
                        except:
                            continue
            
            return pd.DataFrame(melted_data)
            
        except Exception as e:
            return pd.DataFrame(columns=['Spieler', 'Datum', 'Sieg'])
    
    def _fallback_save_training_victory(self, victory_data):
        """Fallback: Speichere Trainingsspielsieg in CSV (komplex wegen CSV-Format)"""
        # Für CSV-Fallback ist das sehr komplex, da das Format anders ist
        # Empfehlung: Nutze die Datenbank für neue Einträge
        return False
    
    def test_connection(self):
        """Teste die Datenbankverbindung"""
        self._ensure_connected()
        
        if not self.connected:
            return False, "Nicht verbunden"
        
        try:
            # Einfache Testabfrage
            response = self.supabase.table('Geburtstage').select('Name').limit(1).execute()
            
            if response.data is not None:
                return True, f"✅ Verbindung erfolgreich - {len(response.data)} Einträge gefunden"
            else:
                return False, "❌ Keine Daten erhalten"
                
        except Exception as e:
            return False, f"❌ Verbindungstest fehlgeschlagen: {str(e)}"
    
    def get_connection_info(self):
        """Debug-Informationen über die Verbindung"""
        info = {
            'dotenv_available': DOTENV_AVAILABLE,
            'supabase_available': SUPABASE_AVAILABLE,
            'connection_attempted': self._connection_attempted,
            'connected': self.connected
        }
        
        # Verfügbare Umgebungsvariablen prüfen
        info['env_sources'] = {}
        
        # .env Datei
        info['env_sources']['SUPABASE_URL_env'] = bool(os.getenv("SUPABASE_URL"))
        info['env_sources']['SUPABASE_ANON_KEY_env'] = bool(os.getenv("SUPABASE_ANON_KEY"))
        
        # Streamlit secrets
        try:
            info['env_sources']['SUPABASE_URL_secrets'] = bool(st.secrets.get("SUPABASE_URL"))
            info['env_sources']['SUPABASE_ANON_KEY_secrets'] = bool(st.secrets.get("SUPABASE_ANON_KEY"))
        except:
            info['env_sources']['SUPABASE_URL_secrets'] = False
            info['env_sources']['SUPABASE_ANON_KEY_secrets'] = False
        
        # Streamlit nested secrets
        try:
            supabase_section = st.secrets.get("supabase", {})
            info['env_sources']['SUPABASE_URL_nested'] = bool(supabase_section.get("SUPABASE_URL"))
            info['env_sources']['SUPABASE_ANON_KEY_nested'] = bool(supabase_section.get("SUPABASE_ANON_KEY"))
        except:
            info['env_sources']['SUPABASE_URL_nested'] = False
            info['env_sources']['SUPABASE_ANON_KEY_nested'] = False
        
        return info

# Globale Instanz
db = DatabaseHelper() 