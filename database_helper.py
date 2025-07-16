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
        """Lade alle Geburtstage aus Supabase (neue Tabellenstruktur: dim_player)"""
        self._ensure_connected()
        
        if not self.connected:
            return pd.DataFrame(columns=['Name', 'Geburtstag', 'Geburtstag_parsed'])
        
        try:
            # Neue Tabelle: "dim_player" - nur aktive Spieler mit Geburtstag
            response = self.supabase.table('dim_player').select('name, birthday').eq('active_flag', True).execute()
            
            if response.data:
                df = pd.DataFrame(response.data)
                
                # Prüfe ob Daten vorhanden sind und birthday-Spalte existiert
                if len(df) > 0 and 'birthday' in df.columns:
                    # Filtere None-Werte bei birthday heraus
                    df = df.dropna(subset=['birthday'])
                    
                    # Konvertiere birthday (bereits date) zu datetime für Kompatibilität
                    df['Geburtstag_parsed'] = pd.to_datetime(df['birthday'], errors='coerce')
                    df = df.dropna(subset=['Geburtstag_parsed'])  # Entferne fehlgeschlagene Konvertierungen
                    
                    # Erstelle Geburtstag-String im erwarteten Format DD.MM.YYYY
                    df['Geburtstag'] = df['Geburtstag_parsed'].dt.strftime('%d.%m.%Y')
                    
                    # Spalte name zu Name umbenennen für Kompatibilität
                    df = df.rename(columns={'name': 'Name'})
                    
                    # Sortieren nach Name
                    df = df.sort_values('Name')
                    
                    return df[['Name', 'Geburtstag', 'Geburtstag_parsed']]
                
                return pd.DataFrame(columns=['Name', 'Geburtstag', 'Geburtstag_parsed'])
            else:
                return pd.DataFrame(columns=['Name', 'Geburtstag', 'Geburtstag_parsed'])
                
        except Exception as e:
            print(f"Fehler beim Laden der Geburtstage aus Supabase (dim_player): {e}")
            return pd.DataFrame(columns=['Name', 'Geburtstag', 'Geburtstag_parsed'])
    

    
    def get_player_names(self):
        """Hole alle Spielernamen (sortiert) aus dim_player"""
        self._ensure_connected()
        
        if not self.connected:
            # Fallback zu Geburtstagsdaten wenn keine DB-Verbindung
            df = self.get_birthdays()
            return sorted(df['Name'].tolist())
        
        try:
            # Direkt aus dim_player Tabelle - alle aktiven Spieler
            response = self.supabase.table('dim_player').select('name').eq('active_flag', True).order('name').execute()
            
            if response.data:
                player_names = [row['name'] for row in response.data if row.get('name')]
                return sorted(player_names)
            else:
                # Fallback zu Geburtstagsdaten wenn dim_player leer ist
                df = self.get_birthdays()
                return sorted(df['Name'].tolist())
                
        except Exception as e:
            print(f"Fehler beim Laden der Spielernamen aus dim_player: {e}")
            # Fallback zu Geburtstagsdaten bei Fehlern
            df = self.get_birthdays()
            return sorted(df['Name'].tolist())
    
    def get_available_tables(self):
        """Hole verfügbare Tabellen aus Supabase"""
        self._ensure_connected()
        
        if not self.connected:
            return []
        
        try:
            # Versuche neue normalisierte Tabellen
            known_tables = ['dim_player', 'dim_penalty_type', 'dim_date', 'fact_penalty', 'fact_training_win']
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
        """Teste Zugriff auf Strafen-Tabellen (neue Struktur: fact_penalty mit JOINs)"""
        self._ensure_connected()
        
        if not self.connected:
            return {"error": "Keine Verbindung zur Datenbank"}
        
        try:
            # Teste die neue Faktentabelle mit JOINs
            response = self.supabase.table('fact_penalty').select('''
                *,
                dim_player(name),
                dim_penalty_type(description),
                dim_date(full_date)
            ''').limit(3).execute()
            
            if response.data:
                return {
                    "success": True,
                    "table_name": "fact_penalty (mit JOINs)",
                    "count": len(response.data),
                    "sample_data": response.data[:2],
                    "columns": ["penalty_id", "date_key", "player_key", "penalty_type_key", "amount_eur", "note", "player_name", "penalty_description", "penalty_date"]
                }
            else:
                return {
                    "success": False,
                    "table_name": "fact_penalty",
                    "error": "Tabelle ist leer"
                }
                
        except Exception as e:
            return {
                "success": False,
                "table_name": "fact_penalty",
                "error": str(e)
            }

    def get_penalties(self):
        """Lade alle Strafen aus Supabase (neue Tabellenstruktur mit JOINs)"""
        self._ensure_connected()
        
        if not self.connected:
            return self._fallback_penalties()
        
        try:
            # Komplexe Abfrage mit JOINs über fact_penalty, dim_player, dim_penalty_type, dim_date
            response = self.supabase.table('fact_penalty').select('''
                *,
                dim_player(name),
                dim_penalty_type(description),
                dim_date(full_date)
            ''').order('penalty_id', desc=True).execute()
            
            if response.data:
                # Verarbeite die verschachtelten Daten
                processed_data = []
                for row in response.data:
                    try:
                        # Extrahiere Daten aus den JOINs
                        player_name = row.get('dim_player', {}).get('name', 'Unbekannt') if row.get('dim_player') else 'Unbekannt'
                        penalty_desc = row.get('dim_penalty_type', {}).get('description', 'Unbekannte Strafe') if row.get('dim_penalty_type') else 'Unbekannte Strafe'
                        penalty_date = row.get('dim_date', {}).get('full_date', None) if row.get('dim_date') else None
                        
                        processed_data.append({
                            'Spieler': player_name,
                            'Strafe': penalty_desc,
                            'Betrag': float(row.get('amount_eur', 0)),
                            'Zusatzinfo': row.get('note', ''),
                            'Datum': penalty_date
                        })
                    except Exception as e:
                        print(f"Fehler bei der Verarbeitung einer Strafe: {e}")
                        continue
                
                if processed_data:
                    df = pd.DataFrame(processed_data)
                    
                    # Datum konvertieren
                    if 'Datum' in df.columns:
                        df['Datum'] = pd.to_datetime(df['Datum'], errors='coerce')
                    
                    return df.dropna(subset=['Datum']).sort_values('Datum', ascending=False)
                
        except Exception as e:
            print(f"Fehler beim Laden der Strafen aus Supabase (neue Struktur): {e}")
            return self._fallback_penalties()
        
        # Fallback wenn Tabelle leer ist
        return self._fallback_penalties()
    
    def add_penalty(self, penalty_data):
        """Füge eine neue Strafe hinzu (neue Tabellenstruktur mit Lookups)"""
        self._ensure_connected()
        
        if not self.connected:
            return self._fallback_save_penalty(penalty_data)
        
        try:
            # 1. Player Key finden
            player_name = penalty_data.get('Spieler')
            player_response = self.supabase.table('dim_player').select('player_key').eq('name', player_name).execute()
            
            if not player_response.data:
                print(f"Spieler '{player_name}' nicht in dim_player gefunden")
                return self._fallback_save_penalty(penalty_data)
            
            player_key = player_response.data[0]['player_key']
            
            # 2. Penalty Type Key finden oder erstellen
            penalty_desc = penalty_data.get('Strafe')
            penalty_amount = penalty_data.get('Betrag')
            
            penalty_type_response = self.supabase.table('dim_penalty_type').select('penalty_type_key').eq('description', penalty_desc).execute()
            
            if penalty_type_response.data:
                penalty_type_key = penalty_type_response.data[0]['penalty_type_key']
            else:
                # Neuen Penalty Type erstellen
                new_penalty_type = {
                    'description': penalty_desc,
                    'default_amount_eur': penalty_amount
                }
                new_penalty_response = self.supabase.table('dim_penalty_type').insert(new_penalty_type).execute()
                
                if not new_penalty_response.data:
                    print(f"Fehler beim Erstellen von Penalty Type '{penalty_desc}'")
                    return self._fallback_save_penalty(penalty_data)
                
                penalty_type_key = new_penalty_response.data[0]['penalty_type_key']
            
            # 3. Date Key finden oder erstellen
            penalty_date = penalty_data.get('Datum')
            if isinstance(penalty_date, str):
                # Konvertiere String-Datum zu Date-Objekt
                from datetime import datetime
                penalty_date_obj = datetime.strptime(penalty_date, '%d.%m.%Y').date()
            else:
                penalty_date_obj = penalty_date
            
            # Datum zu Integer-Key konvertieren (YYYYMMDD Format)
            date_key = int(penalty_date_obj.strftime('%Y%m%d'))
            
            # Prüfe ob Date-Eintrag existiert
            date_response = self.supabase.table('dim_date').select('date_key').eq('date_key', date_key).execute()
            
            if not date_response.data:
                # Neuen Date-Eintrag erstellen
                new_date = {
                    'date_key': date_key,
                    'full_date': penalty_date_obj.isoformat(),
                    'year': penalty_date_obj.year,
                    'month_nr': penalty_date_obj.month,
                    'month_name': penalty_date_obj.strftime('%B')[:10],
                    'quarter': (penalty_date_obj.month - 1) // 3 + 1,
                    'week_nr': penalty_date_obj.isocalendar()[1],
                    'weekday_nr': penalty_date_obj.weekday() + 1,
                    'weekday_name': penalty_date_obj.strftime('%A')[:10],
                    'is_weekend': penalty_date_obj.weekday() >= 5
                }
                date_insert_response = self.supabase.table('dim_date').insert(new_date).execute()
                
                if not date_insert_response.data:
                    print(f"Fehler beim Erstellen von Date-Eintrag für {penalty_date_obj}")
                    return self._fallback_save_penalty(penalty_data)
            
            # 4. Fact Penalty erstellen
            fact_penalty_data = {
                'date_key': date_key,
                'player_key': player_key,
                'penalty_type_key': penalty_type_key,
                'amount_eur': penalty_amount,
                'penalty_cnt': 1,
                'note': penalty_data.get('Zusatzinfo', '')
            }
            
            # Daten in fact_penalty speichern
            response = self.supabase.table('fact_penalty').insert(fact_penalty_data).execute()
            
            if response.data:
                return True
            else:
                return self._fallback_save_penalty(penalty_data)
                
        except Exception as e:
            print(f"Fehler beim Speichern der Strafe in Supabase (neue Struktur): {e}")
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
        """Lade alle Trainingsspielsiege aus Supabase (neue Tabellenstruktur mit JOINs)"""
        self._ensure_connected()
        
        if not self.connected:
            return self._fallback_training_victories()
        
        try:
            # Komplexe Abfrage mit JOINs über fact_training_win, dim_player, dim_date
            response = self.supabase.table('fact_training_win').select('''
                *,
                dim_player(name),
                dim_date(full_date)
            ''').order('date_key', desc=True).execute()
            
            if response.data:
                # Verarbeite die verschachtelten Daten
                processed_data = []
                for row in response.data:
                    try:
                        # Extrahiere Daten aus den JOINs
                        player_name = row.get('dim_player', {}).get('name', 'Unbekannt') if row.get('dim_player') else 'Unbekannt'
                        training_date = row.get('dim_date', {}).get('full_date', None) if row.get('dim_date') else None
                        
                        # win_cnt > 0 bedeutet Sieg
                        hat_gewonnen = row.get('win_cnt', 0) > 0
                        
                        processed_data.append({
                            'Spieler': player_name,
                            'Datum': training_date,
                            'Sieg': hat_gewonnen
                        })
                    except Exception as e:
                        print(f"Fehler bei der Verarbeitung eines Trainingseintrags: {e}")
                        continue
                
                if processed_data:
                    df = pd.DataFrame(processed_data)
                    
                    # Datum konvertieren
                    if 'Datum' in df.columns:
                        df['Datum'] = pd.to_datetime(df['Datum'], errors='coerce')
                    
                    return df.dropna(subset=['Datum']).sort_values('Datum', ascending=False)
                
        except Exception as e:
            print(f"Fehler beim Laden der Trainingsspielsiege aus Supabase (neue Struktur): {e}")
            return self._fallback_training_victories()
        
        # Fallback wenn Tabelle leer ist
        return self._fallback_training_victories()
    
    def add_training_victory(self, victory_data):
        """Füge einen neuen Trainingssieg hinzu (neue Tabellenstruktur mit Lookups)"""
        self._ensure_connected()
        
        if not self.connected:
            return self._fallback_save_training_victory(victory_data)
        
        try:
            # 1. Player Key finden
            player_name = victory_data.get('Spieler')
            player_response = self.supabase.table('dim_player').select('player_key').eq('name', player_name).execute()
            
            if not player_response.data:
                print(f"Spieler '{player_name}' nicht in dim_player gefunden")
                return self._fallback_save_training_victory(victory_data)
            
            player_key = player_response.data[0]['player_key']
            
            # 2. Date Key erstellen/finden
            training_date = victory_data.get('Datum')
            if isinstance(training_date, str):
                from datetime import datetime
                training_date_obj = datetime.strptime(training_date, '%Y-%m-%d').date()
            else:
                training_date_obj = training_date
            
            # Datum zu Integer-Key konvertieren (YYYYMMDD Format)
            date_key = int(training_date_obj.strftime('%Y%m%d'))
            
            # Prüfe ob Date-Eintrag existiert, falls nicht erstelle ihn
            date_response = self.supabase.table('dim_date').select('date_key').eq('date_key', date_key).execute()
            
            if not date_response.data:
                # Neuen Date-Eintrag erstellen
                new_date = {
                    'date_key': date_key,
                    'full_date': training_date_obj.isoformat(),
                    'year': training_date_obj.year,
                    'month_nr': training_date_obj.month,
                    'month_name': training_date_obj.strftime('%B')[:10],
                    'quarter': (training_date_obj.month - 1) // 3 + 1,
                    'week_nr': training_date_obj.isocalendar()[1],
                    'weekday_nr': training_date_obj.weekday() + 1,
                    'weekday_name': training_date_obj.strftime('%A')[:10],
                    'is_weekend': training_date_obj.weekday() >= 5
                }
                date_insert_response = self.supabase.table('dim_date').insert(new_date).execute()
                
                if not date_insert_response.data:
                    print(f"Fehler beim Erstellen von Date-Eintrag für {training_date_obj}")
                    return self._fallback_save_training_victory(victory_data)
            
            # 3. Fact Training Win erstellen/aktualisieren
            hat_gewonnen = victory_data.get('Sieg', False)
            win_cnt = 1 if hat_gewonnen else 0
            
            fact_training_data = {
                'date_key': date_key,
                'player_key': player_key,
                'played_cnt': 1,
                'win_cnt': win_cnt
            }
            
            # UPSERT für Updates (kombinierter Primary Key: date_key, player_key)
            response = self.supabase.table('fact_training_win').upsert(fact_training_data).execute()
            
            if response.data:
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Fehler beim Speichern des Trainingssiegs (neue Struktur): {e}")
            return self._fallback_save_training_victory(victory_data)

    def add_training_day_entries(self, datum, spieler_mit_sieg, alle_spieler):
        """Füge Einträge für einen kompletten Trainingstag hinzu (neue Tabellenstruktur)"""
        self._ensure_connected()
        
        if not self.connected:
            return False, "Keine Datenbankverbindung"
        
        try:
            # 1. Datum zu date_key konvertieren und dim_date sicherstellen
            if isinstance(datum, str):
                from datetime import datetime
                # Versuche verschiedene Datumsformate
                try:
                    date_obj = datetime.strptime(datum, '%Y-%m-%d').date()
                except:
                    try:
                        date_obj = datetime.strptime(datum, '%d.%m.%Y').date()
                    except:
                        return False, f"❌ Ungültiges Datumsformat: {datum}"
            else:
                date_obj = datum
            
            date_key = int(date_obj.strftime('%Y%m%d'))
            
            # Sicherstellen, dass dim_date Eintrag existiert
            date_response = self.supabase.table('dim_date').select('date_key').eq('date_key', date_key).execute()
            
            if not date_response.data:
                # Neuen Date-Eintrag erstellen
                new_date = {
                    'date_key': date_key,
                    'full_date': date_obj.isoformat(),
                    'year': date_obj.year,
                    'month_nr': date_obj.month,
                    'month_name': date_obj.strftime('%B')[:10],
                    'quarter': (date_obj.month - 1) // 3 + 1,
                    'week_nr': date_obj.isocalendar()[1],
                    'weekday_nr': date_obj.weekday() + 1,
                    'weekday_name': date_obj.strftime('%A')[:10],
                    'is_weekend': date_obj.weekday() >= 5
                }
                date_insert_response = self.supabase.table('dim_date').insert(new_date).execute()
                
                if not date_insert_response.data:
                    return False, f"❌ Fehler beim Erstellen von Date-Eintrag für {date_obj}"
            
            # 2. Alle Spieler zu player_keys umwandeln
            player_keys = {}
            for spieler in alle_spieler:
                player_response = self.supabase.table('dim_player').select('player_key').eq('name', spieler).execute()
                if player_response.data:
                    player_keys[spieler] = player_response.data[0]['player_key']
                else:
                    print(f"Warnung: Spieler '{spieler}' nicht in dim_player gefunden, wird übersprungen")
            
            if not player_keys:
                return False, "❌ Keine gültigen Spieler gefunden"
            
            # 3. Erst alle bestehenden Einträge für diesen Tag löschen
            delete_response = self.supabase.table('fact_training_win').delete().eq('date_key', date_key).execute()
            
            # 4. Neue Einträge für alle Spieler hinzufügen
            neue_eintraege = []
            for spieler, player_key in player_keys.items():
                hat_gewonnen = spieler in spieler_mit_sieg
                win_cnt = 1 if hat_gewonnen else 0
                
                neue_eintraege.append({
                    'date_key': date_key,
                    'player_key': player_key,
                    'played_cnt': 1,
                    'win_cnt': win_cnt
                })
            
            # Alle Einträge in einem Batch hinzufügen
            if neue_eintraege:
                response = self.supabase.table('fact_training_win').insert(neue_eintraege).execute()
                
                if response.data:
                    return True, f"✅ {len(neue_eintraege)} Einträge erfolgreich gespeichert (date_key: {date_key})"
                else:
                    return False, "❌ Fehler beim Speichern in der Datenbank"
            else:
                return False, "❌ Keine Einträge zum Speichern"
                
        except Exception as e:
            return False, f"❌ Fehler: {str(e)}"

    def get_training_day_entries(self, datum):
        """Lade alle Einträge für einen bestimmten Trainingstag (neue Tabellenstruktur)"""
        self._ensure_connected()
        
        if not self.connected:
            return []
        
        try:
            # Konvertiere Datum zu date_key (YYYYMMDD Format)
            if isinstance(datum, str):
                from datetime import datetime
                # Versuche verschiedene Datumsformate
                try:
                    date_obj = datetime.strptime(datum, '%Y-%m-%d').date()
                except:
                    try:
                        date_obj = datetime.strptime(datum, '%d.%m.%Y').date()
                    except:
                        print(f"Fehler: Ungültiges Datumsformat: {datum}")
                        return []
            else:
                date_obj = datum
            
            date_key = int(date_obj.strftime('%Y%m%d'))
            
            # Abfrage mit JOINs für komplette Daten
            response = self.supabase.table('fact_training_win').select('''
                *,
                dim_player(name)
            ''').eq('date_key', date_key).execute()
            
            if response.data:
                # Konvertiere zurück zum erwarteten Format für Kompatibilität
                converted_data = []
                for row in response.data:
                    try:
                        player_name = row.get('dim_player', {}).get('name', 'Unbekannt') if row.get('dim_player') else 'Unbekannt'
                        hat_gewonnen = row.get('win_cnt', 0) > 0
                        
                        converted_data.append({
                            'spielername': player_name,
                            'datum': date_obj.isoformat(),
                            'hat_gewonnen': hat_gewonnen,
                            'date_key': date_key,
                            'player_key': row.get('player_key'),
                            'played_cnt': row.get('played_cnt', 1),
                            'win_cnt': row.get('win_cnt', 0)
                        })
                    except Exception as e:
                        print(f"Fehler bei der Verarbeitung eines Trainingseintrags: {e}")
                        continue
                
                return converted_data
            else:
                return []
                
        except Exception as e:
            print(f"Fehler beim Laden der Trainingseinträge (neue Struktur): {e}")
            return []

    def delete_training_day(self, datum):
        """Lösche alle Einträge für einen Trainingstag (neue Tabellenstruktur)"""
        self._ensure_connected()
        
        if not self.connected:
            return False, "Keine Datenbankverbindung"
        
        try:
            # Konvertiere Datum zu date_key (YYYYMMDD Format)
            if isinstance(datum, str):
                from datetime import datetime
                # Versuche verschiedene Datumsformate
                try:
                    date_obj = datetime.strptime(datum, '%Y-%m-%d').date()
                except:
                    try:
                        date_obj = datetime.strptime(datum, '%d.%m.%Y').date()
                    except:
                        return False, f"❌ Ungültiges Datumsformat: {datum}"
            else:
                date_obj = datum
            
            date_key = int(date_obj.strftime('%Y%m%d'))
            
            # Lösche alle fact_training_win Einträge für diesen date_key
            response = self.supabase.table('fact_training_win').delete().eq('date_key', date_key).execute()
            return True, f"✅ Trainingstag {datum} erfolgreich gelöscht (date_key: {date_key})"
            
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
            # Einfache Testabfrage an neue Tabellenstruktur
            response = self.supabase.table('dim_player').select('name').limit(1).execute()
            
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