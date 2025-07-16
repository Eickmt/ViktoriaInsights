"""
Timezone Helper für deutsche Zeit (Europe/Berlin)
Zentrale Funktionen für konsistente Zeitzonenbehandlung in der gesamten Anwendung
"""

import pytz
from datetime import datetime


# Deutsche Zeitzone
GERMAN_TZ = pytz.timezone('Europe/Berlin')


def get_german_now():
    """
    Gibt die aktuelle Zeit in deutscher Zeitzone zurück.
    
    Returns:
        datetime: Aktueller Zeitpunkt in deutscher Zeitzone
    """
    return datetime.now(GERMAN_TZ)


def get_german_now_naive():
    """
    Gibt die aktuelle Zeit in deutscher Zeitzone als naive datetime zurück.
    Für Kompatibilität mit pandas und anderen Libraries.
    
    Returns:
        datetime: Aktueller Zeitpunkt in deutscher Zeitzone (naive)
    """
    return get_german_now().replace(tzinfo=None)


def convert_to_german_tz(dt):
    """
    Konvertiert einen datetime-Wert zur deutschen Zeitzone.
    
    Args:
        dt (datetime): Zu konvertierender datetime-Wert
        
    Returns:
        datetime: datetime-Wert in deutscher Zeitzone
    """
    if dt.tzinfo is None:
        # Naive datetime - assume it's already in German time
        return GERMAN_TZ.localize(dt)
    else:
        # Timezone-aware datetime - convert to German timezone
        return dt.astimezone(GERMAN_TZ)


def make_naive_german_datetime(year, month, day, hour=0, minute=0, second=0):
    """
    Erstellt ein naive datetime-Objekt in deutscher Zeit.
    Für Kompatibilität mit pandas und anderen Libraries.
    
    Args:
        year, month, day: Datum
        hour, minute, second: Zeit (optional, default 0)
        
    Returns:
        datetime: Naive datetime in deutscher Zeit
    """
    german_dt = GERMAN_TZ.localize(datetime(year, month, day, hour, minute, second))
    return german_dt.replace(tzinfo=None)


def format_german_datetime(dt, format_str='%d.%m.%Y %H:%M:%S'):
    """
    Formatiert einen datetime-Wert in deutscher Zeitzone.
    
    Args:
        dt (datetime): Zu formatierender datetime-Wert
        format_str (str): Format-String (default: '%d.%m.%Y %H:%M:%S')
        
    Returns:
        str: Formatierter datetime-String
    """
    if dt.tzinfo is None:
        dt = GERMAN_TZ.localize(dt)
    else:
        dt = dt.astimezone(GERMAN_TZ)
    
    return dt.strftime(format_str)


def get_german_date_now():
    """
    Gibt das aktuelle Datum in deutscher Zeitzone zurück (ohne Zeit).
    
    Returns:
        date: Aktuelles Datum in deutscher Zeitzone
    """
    return get_german_now().date()


def parse_german_date(date_str, format_str='%d.%m.%Y'):
    """
    Parst einen Datums-String und gibt einen timezone-aware datetime zurück.
    
    Args:
        date_str (str): Zu parsender Datums-String
        format_str (str): Format des Datums-Strings
        
    Returns:
        datetime: Timezone-aware datetime in deutscher Zeitzone
    """
    naive_dt = datetime.strptime(date_str, format_str)
    return GERMAN_TZ.localize(naive_dt)


def calculate_days_until_birthday(birthday_this_year_naive, today_naive=None):
    """
    Berechnet die Tage bis zum nächsten Geburtstag.
    Arbeitet mit naive datetime-Objekten für Kompatibilität.
    
    Args:
        birthday_this_year_naive: Geburtstag in diesem Jahr (naive datetime)
        today_naive: Aktueller Tag (optional, default: heute in deutscher Zeit)
        
    Returns:
        int: Tage bis zum Geburtstag
    """
    if today_naive is None:
        today_naive = get_german_now_naive()
    
    # Konvertiere zu date-Objekten (ohne Uhrzeit) für korrekte Tagesberechnung
    today_date = today_naive.date()
    birthday_date = birthday_this_year_naive.date()
    
    # Berechne Tage bis Geburtstag
    days_diff = (birthday_date - today_date).days
    if days_diff >= 0:
        return days_diff
    else:
        # Geburtstag war schon, nehme nächstes Jahr
        next_year_birthday = birthday_date.replace(year=birthday_date.year + 1)
        return (next_year_birthday - today_date).days 