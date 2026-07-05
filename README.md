## 🚀 Jak uruchomić projekt

Projekt opiera się na aplikacji webowej napisanej w języku Python z wykorzystaniem frameworka **Flask**.

### Wymagania

- Zainstalowany **Python 3.x**
- (Zalecane) Środowisko wirtualne (venv)

### Instrukcja krok po kroku

1. **Otwórz terminal** i przejdź do głównego folderu projektu (tam, gdzie znajduje się plik `app.py`).

2. **(Opcjonalnie) Utwórz i aktywuj środowisko wirtualne:**

   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Zainstaluj framework Flask:**
   Z racji tego, że w strukturze nie widać pliku `requirements.txt`, wystarczy ręcznie zainstalować Flaska:

   ```powershell
   pip install Flask
   ```

4. **Uruchom aplikację:**
   Głównym plikiem jest `app.py`, więc wystarczy wpisać komendę:

   ```powershell
   python app.py
   ```

5. **Otwórz projekt w przeglądarce:**
   Domyślnie serwer uruchomi się na lokalnym porcie 5000. W przeglądarce wpisz adres:
   `http://127.0.0.1:5000/`
