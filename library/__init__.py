from abc import ABC, abstractmethod
import json
from datetime import datetime
from typing import List, Optional

# -----------------------------
# Wzorzec: Strategia
# -----------------------------
# Interfejs strategii sortowania
class SortStrategy(ABC):
    @abstractmethod
    def sort(self, media_list: List['Media']) -> List['Media']:
        """Sortuje listę obiektów Media."""
        pass

# Strategia sortowania po tytule
class SortByTitle(SortStrategy):
    def sort(self, media_list: List['Media']) -> List['Media']:
        return sorted(media_list, key=lambda m: m.title.lower()) # Sortowanie bez uwzględniania wielkości liter

# Strategia sortowania po roku
class SortByYear(SortStrategy):
    def sort(self, media_list: List['Media']) -> List['Media']:
        return sorted(media_list, key=lambda m: m.year)

# -----------------------------
# Wzorzec: Command
# -----------------------------
# Interfejs komendy
class Command(ABC):
    @abstractmethod
    def execute(self):
        """Wykonuje operację komendy."""
        pass

    @abstractmethod
    def undo(self):
        """Cofa wykonaną operację komendy."""
        pass

# Komenda wypożyczenia media
class BorrowCommand(Command):
    def __init__(self, library: 'SingletonLibrary', user: 'User', media: 'Media'):
        self.library = library
        self.user = user
        self.media = media
        self.was_borrowed_by_user = False # Flaga do śledzenia czy faktycznie doszło do wypożyczenia

    def execute(self):
        try:
            # Sprawdź dostępność przed próbą wypożyczenia
            if self.media.is_available:
                self.media.borrow(self.user)
                print(f"{self.user.username} wypożyczył {self.media.title}")
                self.was_borrowed_by_user = True
            else:
                print(f"Nie można wypożyczyć: {self.media.title} jest już wypożyczony.")
        except MediaUnavailableError as e:
            print(f"Nie można wypożyczyć: {e}")
            self.was_borrowed_by_user = False # Upewnij się, że flaga jest ustawiona na False w przypadku błędu

    def undo(self):
        if self.was_borrowed_by_user: # Cofaj tylko jeśli operacja została wykonana pomyślnie
            self.user.return_item(self.media)
            print(f"Cofnięto wypożyczenie: {self.media.title} przez {self.user.username}.")
        else:
            print(f"Nie można cofnąć, ponieważ {self.media.title} nie zostało faktycznie wypożyczone przez {self.user.username}.")


# Zarządzanie historią komend
class CommandManager:
    def __init__(self):
        self.history: List[Command] = []

    def execute_command(self, command: Command):
        command.execute()
        # Dodajemy komendę do historii tylko jeśli wykonanie było udane (lub chcemy śledzić próby)
        # W tym przypadku BorrowCommand ustawia was_borrowed_by_user, co jest lepsze
        if isinstance(command, BorrowCommand) and command.was_borrowed_by_user:
             self.history.append(command)
        elif not isinstance(command, BorrowCommand): # Dla innych komend, które zawsze "działają"
            self.history.append(command)


    def undo_last(self):
        if self.history:
            command = self.history.pop()
            command.undo()
        else:
            print("Brak komend do cofnięcia.")

# -----------------------------
# Własny wyjątek dziedziczący z Exception
# -----------------------------
class MediaUnavailableError(Exception):
    """Wyjątek rzucany, gdy próbuje się wypożyczyć niedostępne medium."""
    pass

# -----------------------------
# Klasa bazowa Media (dziedziczenie, super(), @classmethod, polimorfizm)
# -----------------------------
class Media:
    category = "Generic"  # Atrybut klasy, nadpisywany w podklasach

    def __init__(self, title: str, year: int):
        self.title = title
        self.year = year
        self.is_available = True
        self.borrower: Optional['User'] = None # Typowanie dla atrybutu borrower

    def get_info(self) -> str:
        """Zwraca podstawowe informacje o medium."""
        base = f"{self.title} ({self.year}) - Status: {'Dostępne' if self.is_available else 'Wypożyczone'}"
        # Polimorficzne rozszerzenie o dodatkowe informacje specyficzne dla podklasy
        return base + self._extra_info()

    def _extra_info(self) -> str:
        """Metoda do nadpisania w podklasach, dodająca specyficzne informacje."""
        return ""

    @classmethod
    def from_dict(cls, data: dict) -> 'Media':
        """Alternatywny konstruktor tworzący obiekt Media ze słownika."""
        # Ta metoda jest podstawowa; podklasy nadpiszą ją, aby obsłużyć dodatkowe pola
        return cls(data["title"], data["year"])

    def to_dict(self) -> dict:
        """Serializuje obiekt Media do słownika dla celów zapisu."""
        return {
            "type": self.__class__.__name__, # Dodaj typ medium dla deserializacji
            "title": self.title,
            "year": self.year,
            "is_available": self.is_available,
            # Zapisz nazwę użytkownika, jeśli istnieje, w przeciwnym razie None
            "borrower_username": self.borrower.username if self.borrower else None
        }

    def borrow(self, user: 'User'):
        """Wypożycza medium określonemu użytkownikowi."""
        if not self.is_available:
            raise MediaUnavailableError(f"'{self.title}' jest już wypożyczony.")
        self.is_available = False
        self.borrower = user
        user.borrowed_items.append(self)
        user.history.append((self, datetime.now(), "borrowed"))

    def return_item(self):
        """Zwraca medium, ustawiając je jako dostępne."""
        self.is_available = True
        self.borrower = None

# -----------------------------
# Klasy dziedziczące (Book, Movie)
# -----------------------------
class Book(Media):
    category = "Książka"

    def __init__(self, title: str, year: int, author: str, isbn: str):
        super().__init__(title, year) # Wywołanie konstruktora klasy bazowej
        self.author = author
        self.isbn = isbn

    def _extra_info(self) -> str:  # Nadpisanie metody z klasy Media
        return f" Autor: {self.author}, ISBN: {self.isbn}"

    @classmethod
    def from_string(cls, data_str: str) -> 'Book':  # Drugi konstruktor
        """Alternatywny konstruktor tworzący obiekt Book z ciągu znaków."""
        parts = [p.strip() for p in data_str.split(",")]
        if len(parts) != 4:
            raise ValueError("Nieprawidłowy format ciągu dla Książki. Oczekiwano: Tytuł, Rok, Autor, ISBN")
        title, year, author, isbn = parts
        return cls(title, int(year), author, isbn)

    @classmethod
    def from_dict(cls, data: dict) -> 'Book':
        """Tworzy obiekt Book ze słownika, uwzględniając specyficzne pola."""
        return cls(data["title"], data["year"], data["author"], data["isbn"])

    def to_dict(self) -> dict: # Nadpisanie metody to_dict dla Book
        data = super().to_dict()
        data.update({
            "author": self.author,
            "isbn": self.isbn
        })
        return data

class Movie(Media):
    category = "Film"

    def __init__(self, title: str, year: int, director: str, duration: int):
        super().__init__(title, year) # Wywołanie konstruktora klasy bazowej
        self.director = director
        self.duration = duration

    def _extra_info(self) -> str: # Nadpisanie metody z klasy Media
        return f", Reżyser: {self.director}, Czas trwania: {self.duration} min"

    @classmethod
    def from_dict(cls, data: dict) -> 'Movie':
        """Tworzy obiekt Movie ze słownika, uwzględniając specyficzne pola."""
        return cls(data["title"], data["year"], data["director"], data["duration"])

    def to_dict(self) -> dict: # Nadpisanie metody to_dict dla Movie
        data = super().to_dict()
        data.update({
            "director": self.director,
            "duration": self.duration
        })
        return data

# -----------------------------
# Singleton - wzorzec projektowy
# -----------------------------
class SingletonLibrary:
    _instance: Optional['SingletonLibrary'] = None

    def __new__(cls) -> 'SingletonLibrary':
        if cls._instance is None:
            cls._instance = super(SingletonLibrary, cls).__new__(cls)
            cls._instance.media_list: List[Media] = []
            cls._instance.users: List['User'] = []
            # Inicjalizacja tutaj, jeśli _instance jest tworzone po raz pierwszy
        return cls._instance

    def add_media(self, media: Media):
        """Dodaje medium do biblioteki."""
        self.media_list.append(media)
        print(f"Dodano '{media.title}' do biblioteki.")

    def add_user(self, user: 'User'):
        """Dodaje użytkownika do biblioteki."""
        # Sprawdź, czy użytkownik o takiej nazwie już istnieje
        if any(u.username == user.username for u in self.users):
            print(f"Użytkownik o nazwie '{user.username}' już istnieje.")
            return
        self.users.append(user)
        print(f"Dodano użytkownika: {user.username}.")


    def find_media_by_title(self, title: str) -> Optional[Media]:
        """Wyszukuje medium po tytule."""
        return next((m for m in self.media_list if m.title.lower() == title.lower()), None)

    def find_user_by_username(self, username: str) -> Optional['User']:
        """Wyszukuje użytkownika po nazwie."""
        return next((u for u in self.users if u.username.lower() == username.lower()), None)

    def show_all_media(self):
        """Wyświetla listę wszystkich mediów w bibliotece."""
        print("\n--- Wszystkie media w bibliotece ---")
        if not self.media_list:
            print("Brak mediów w bibliotece.")
            return
        for i, media in enumerate(self.media_list):
            print(f"{i+1}. {media.get_info()}")
        print("------------------------------------")


    def show_all_users(self):
        """Wyświetla listę zarejestrowanych użytkowników."""
        print("\n--- Zarejestrowani użytkownicy ---")
        if not self.users:
            print("Brak zarejestrowanych użytkowników.")
            return
        for i, user in enumerate(self.users):
            print(f"{i+1}. {user.get_info()}")
            if user.borrowed_items:
                print(f"   Wypożyczone: {[item.title for item in user.borrowed_items]}")
        print("----------------------------------")

    def sort_media(self, strategy: SortStrategy):  # Strategia sortowania
        """Sortuje listę mediów za pomocą podanej strategii."""
        self.media_list = strategy.sort(self.media_list)
        print("Media zostały posortowane.")

    def borrow_media(self, user: 'User', media: 'Media'):
        """Zarządza procesem wypożyczenia media."""
        # Przeniesiono logikę borrow() do klasy Media, ale SingletonLibrary koordynuje.
        # Ta metoda jest głównie punktem wejścia dla komendy.
        try:
            media.borrow(user)
            # Komenda już wypisuje komunikat o powodzeniu
        except MediaUnavailableError as e:
            print(f"Nie można wypożyczyć: {e}")

    def save_media_to_file(self, filename: str = "media.json"):
        """Zapisuje listę mediów do pliku JSON."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump([media.to_dict() for media in self.media_list], f, indent=4)
            print(f"Zapisano media do '{filename}'.")
        except IOError as e:
            print(f"Błąd zapisu mediów do pliku {filename}: {e}")

    def load_media_from_file(self, filename: str = "media.json"):
        """Wczytuje listę mediów z pliku JSON."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.media_list.clear() # Wyczyść bieżącą listę przed wczytaniem
                for item_data in data:
                    media_type = item_data.pop("type", "Generic") # Domyślny typ 'Generic'
                    if media_type == "Book":
                        media_obj = Book.from_dict(item_data)
                    elif media_type == "Movie":
                        media_obj = Movie.from_dict(item_data)
                    else:
                        # Można rozważyć logowanie błędu lub pomijanie nieznanych typów
                        print(f"Nieznany typ medium '{media_type}' w pliku. Pomijam.")
                        continue

                    # Odtwarzanie stanu dostępności i wypożyczającego (tylko nazwa użytkownika)
                    media_obj.is_available = item_data.get("is_available", True)
                    borrower_username = item_data.get("borrower_username")
                    if not media_obj.is_available and borrower_username:
                        # W prawdziwym systemie, należałoby tu znaleźć prawdziwy obiekt User
                        # Na potrzeby tego przykładu, po prostu ustawiamy borrower=None,
                        # ponieważ Userzy są ładowani oddzielnie i nie ma gwarancji ich kolejności.
                        # Realna implementacja wymagałaby mapowania ID lub późniejszego łączenia.
                        pass # Zakładamy, że stan is_available jest wystarczający

                    self.media_list.append(media_obj)
            print(f"Wczytano {len(self.media_list)} mediów z '{filename}'.")
        except FileNotFoundError:
            print(f"Plik '{filename}' nie znaleziono. Rozpoczynam z pustą biblioteką mediów.")
        except json.JSONDecodeError:
            print(f"Błąd dekodowania JSON z pliku '{filename}'. Plik może być uszkodzony.")
        except Exception as e:
            print(f"Wystąpił nieoczekiwany błąd podczas wczytywania mediów: {e}")

    def save_users_to_file(self, filename: str = "users.json"):
        """Zapisuje listę użytkowników do pliku JSON."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump([user.to_dict() for user in self.users], f, indent=4)
            print(f"Zapisano użytkowników do '{filename}'.")
        except IOError as e:
            print(f"Błąd zapisu użytkowników do pliku {filename}: {e}")

    def load_users_from_file(self, filename: str = "users.json"):
        """Wczytuje listę użytkowników z pliku JSON."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.users.clear() # Wyczyść bieżącą listę użytkowników
                for user_data in data:
                    self.users.append(User(user_data["username"]))
            print(f"Wczytano {len(self.users)} użytkowników z '{filename}'.")
        except FileNotFoundError:
            print(f"Plik '{filename}' nie znaleziono. Rozpoczynam bez zarejestrowanych użytkowników.")
        except json.JSONDecodeError:
            print(f"Błąd dekodowania JSON z pliku '{filename}'. Plik może być uszkodzony.")
        except Exception as e:
            print(f"Wystąpił nieoczekiwany błąd podczas wczytywania użytkowników: {e}")


# -----------------------------
# Klasa User - enkapsulacja (gettery, settery)
# -----------------------------
class User:
    def __init__(self, username: str):
        self._username = username
        self.borrowed_items: List[Media] = []
        # Historia przechowuje krotki: (medium, data_czas, typ_akcji)
        self.history: List[tuple['Media', datetime, str]] = []

    @property
    def username(self) -> str:
        """Getter dla nazwy użytkownika."""
        return self._username

    @username.setter
    def username(self, new_name: str):
        """Setter dla nazwy użytkownika z walidacją."""
        if not new_name:
            raise ValueError("Nazwa użytkownika nie może być pusta.")
        self._username = new_name

    def get_info(self) -> str:
        """Zwraca informacje o użytkowniku."""
        return f"Użytkownik: {self.username}"

    def return_item(self, item: Media):
        """Zwraca wypożyczony przedmiot."""
        if item in self.borrowed_items:
            self.borrowed_items.remove(item)
            self.history.append((item, datetime.now(), "returned"))
            item.return_item()
            print(f"{self.username} zwrócił '{item.title}'.")
        else:
            print(f"Użytkownik {self.username} nie wypożyczył '{item.title}'.")

    def to_dict(self) -> dict:
        """Serializuje obiekt User do słownika dla celów zapisu."""
        return {
            "username": self._username,
            # Obecnie nie zapisujemy wypożyczonych przedmiotów ani historii w User,
            # ponieważ wymagałoby to bardziej złożonej logiki deserializacji
            # do ponownego powiązania z obiektami Media.
        }

# -----------------------------
# Prosty interfejs użytkownika (CLI)
# -----------------------------

def _add_book_interactive(library: SingletonLibrary):
    """Interaktywne dodawanie książki."""
    print("\n--- Dodaj książkę ---")
    t = input("Tytuł: ")
    try:
        y = int(input("Rok wydania: "))
    except ValueError:
        print("Błąd: Rok musi być liczbą całkowitą.")
        return
    a = input("Autor: ")
    i = input("ISBN: ")
    library.add_media(Book(t, y, a, i))

def _add_movie_interactive(library: SingletonLibrary):
    """Interaktywne dodawanie filmu."""
    print("\n--- Dodaj film ---")
    t = input("Tytuł: ")
    try:
        y = int(input("Rok produkcji: "))
        dur = int(input("Czas trwania (minuty): "))
    except ValueError:
        print("Błąd: Rok i czas trwania muszą być liczbami całkowitymi.")
        return
    d = input("Reżyser: ")
    library.add_media(Movie(t, y, d, dur))

def _borrow_media_interactive(library: SingletonLibrary, command_manager: CommandManager):
    """Interaktywne wypożyczanie mediów."""
    print("\n--- Wypożycz media ---")
    uname = input("Nazwa użytkownika: ")
    title = input("Tytuł media do wypożyczenia: ")

    user = library.find_user_by_username(uname)
    media = library.find_media_by_title(title)

    if not user:
        print(f"Błąd: Użytkownik '{uname}' nie znaleziony.")
        return
    if not media:
        print(f"Błąd: Medium '{title}' nie znalezione.")
        return

    command = BorrowCommand(library, user, media)
    command_manager.execute_command(command)

def _sort_media_interactive(library: SingletonLibrary):
    """Interaktywne sortowanie mediów."""
    print("\n--- Sortuj media ---")
    print("1. Sortuj po tytule")
    print("2. Sortuj po roku")
    sort_choice = input("Wybierz opcję sortowania: ") 

    if sort_choice == '1':
        library.sort_media(SortByTitle())
    elif sort_choice == '2':
        library.sort_media(SortByYear())
    else:
        print("Nieprawidłowa opcja sortowania.")

def main_menu():
    """Główne menu aplikacji bibliotecznej."""
    library = SingletonLibrary()
    command_manager = CommandManager()

    # Wczytaj dane przy starcie
    library.load_media_from_file("media.json")
    library.load_users_from_file("users.json")

    while True:
        print("\n===== Biblioteka - Menu Główne =====")
        print("1. Dodaj książkę")
        print("2. Dodaj film")
        print("3. Pokaż wszystkie media")
        print("4. Dodaj użytkownika")
        print("5. Pokaż wszystkich użytkowników")
        print("6. Wypożycz media")
        print("7. Cofnij ostatnie wypożyczenie")
        print("8. Sortuj media")
        print("9. Zapisz i wyjdź")
        print("====================================")

        choice = input("Wybierz opcję: ")

        if choice == '1':
            _add_book_interactive(library)
        elif choice == '2':
            _add_movie_interactive(library)
        elif choice == '3':
            library.show_all_media()
        elif choice == '4':
            uname = input("Podaj nazwę nowego użytkownika: ")
            if uname:
                library.add_user(User(uname))
            else:
                print("Nazwa użytkownika nie może być pusta.")
        elif choice == '5':
            library.show_all_users()
        elif choice == '6':
            _borrow_media_interactive(library, command_manager)
        elif choice == '7':
            command_manager.undo_last()
        elif choice == '8':
            _sort_media_interactive(library)
        elif choice == '9':
            library.save_media_to_file("media.json")
            library.save_users_to_file("users.json")
            print("Dane zostały zapisane. Do widzenia!")
            break
        else:
            print("Nieprawidłowa opcja. Wybierz numer z listy.")


if __name__ == "__main__":
    main_menu()