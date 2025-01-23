# PC System Monitoring Asystent

## Opis projektu

**PC System Monitoring Asystent** to aplikacja webowa stworzona w Pythonie przy użyciu frameworka Flask. Umożliwia monitorowanie parametrów systemowych komputera, takich jak:
- Informacje o systemie operacyjnym,
- Statyczne i dynamiczne dane CPU, GPU, RAM,
- Monitorowanie przestrzeni dyskowej,
- Informacje o sieci,
- Stan baterii (jeśli dostępna),
- Sesje użytkowników.

Aplikacja korzysta z bazy danych PostgreSQL do przechowywania statycznych i dynamicznych danych o systemie.

---

## Funkcjonalności
- **Przegląd systemu:**
  - Informacje o systemie operacyjnym,
  - Architektura procesora,
  - Model CPU i GPU,
  - Ilość pamięci RAM i przestrzeni dyskowej.
- **Monitorowanie dynamiczne:**
  - Zużycie CPU, GPU, RAM,
  - Stan dysków i sieci,
  - Aktywne sesje użytkowników.
- **Wykresy:**
  - Dynamiczne wizualizacje danych systemowych.
- **Alerty:**
  - Alerty przekroczeń parametrów sprzętowych,
  - Konfiguracja progów przekroczeń z poziomu użytkownika.

---

## Instalacja i konfiguracja

### Wymagania
1. Python 3.10+
2. PostgreSQL 12+

---

## Technologie użyte w projekcie
- **Backend:** Flask
- **Frontend:** Flask-Bootstrap, HTML, CSS, jQuery, Chart.js
- **Baza danych:** PostgreSQL
- **Inne biblioteki:**
  - `psutil` – monitorowanie zasobów systemowych,
  - `py-cpuinfo` – szczegóły procesora,
  - `GPUtil` – monitorowanie GPU,
  - `matplotlib` – generowanie wykresów,
  - `datetime` – operacje na datach i czasach,
  - `platform` – informacje o systemie operacyjnym.

---

### Instrukcja instalacji

1. Sklonuj repozytorium:
   ```bash
   git clone https://github.com/Ola2195/PC-System-Monitoring-Asystent.git
   cd Pc-System-Monitoring-Asystent
   ```

2. Stwórz i aktywuj wirtualne środowisko:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/MacOS
   venv\Scripts\activate    # Windows
   ```

3. Zainstaluj wymagane biblioteki:
   ```bash
   pip install -r requirements.txt
   ```

4. Skonfiguruj bazę danych PostgreSQL:
   - Zaloguj się do PostgreSQL i wykonaj poniższe polecenia:
     ```sql
     CREATE DATABASE system_monitoring;
     
     CREATE TABLE systems (
         id SERIAL PRIMARY KEY,
         node_name VARCHAR(100) NOT NULL,
         os_name VARCHAR(100) NOT NULL,
         release_version VARCHAR(20),
         architecture VARCHAR(20),
         processor_type VARCHAR(100)
     );
     
     CREATE TABLE systems_dynamic (
         id SERIAL PRIMARY KEY,
         system_id INT NOT NULL,
         timestamp TIMESTAMP NOT NULL,
         boot_time INTERVAL,
         FOREIGN KEY (system_id) REFERENCES systems(id) ON DELETE CASCADE
     );

     -- Dodaj pozostałe tabele zgodnie z plikiem setup.sql
     ```

5. Skonfiguruj plik `db_config.json`:
   Edytuj plik `db_config.json` w katalogu głównym, uzupełniając go danymi połączenia z bazą danych:
   ```json
   {
       "DATABASE": {
           "host": "localhost",
           "port": 5432,
           "user": "twoja_nazwa_użytkownika",
           "password": "twoje_hasło",
           "db_name": "system_monitoring"
       }
   }
   ```

6. Uruchom aplikację:
   ```bash
   python main.py
   ```
   Aplikacja będzie dostępna pod adresem: `http://127.0.0.1:5000`

---

### Pliki i foldery
- `main.py` – plik uruchamiający aplikację.
- `db_config.json` – plik konfiguracji bazy danych.
- `alerts_config.json` – plik konfiguracji progów alarmowych.
- `app/` – katalog główny aplikacji zawierający moduły, szablony i statyczne pliki.
- `templates/` – szablony HTML używane w aplikacji.
- `static/` – statyczne zasoby (np. CSS).

---

## Strony aplikacji
- **`/`** - Strona główna
- **`/cpu`** - Informacje o procesorze
- **`/gpu`** - Informacje o karcie graficznej
- **`/ram`** - Informacje o pamięci RAM
- **`/disks`** - Informacje o dyskach
- **`/network`** - Informacje o sieci
- **`/config`** - Konfiguracja systemu alarmowego