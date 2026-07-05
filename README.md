# System Zarządzania Biblioteką (Library - Books & Movies)

Niniejszy projekt implementuje prosty system zarządzania biblioteką, obejmujący media (**książki, filmy**), **użytkowników** oraz podstawowe operacje takie jak **dodawanie, wypożyczanie, zwracanie i sortowanie**.

System został zaprojektowany z pełnym uwzględnieniem zasad programowania obiektowego (OOP) oraz sprawdzonych wzorców projektowych.

---

## 🛠 Realizacja Wymagań Projektowych

### 1. Paradygmaty i Struktura Obiektowa (OOP)

- **Użycie klas:** W projekcie zastosowano liczne klasy reprezentujące różne abstrakcje i elementy systemu: `Media`, `Book`, `Movie`, `User`, `SingletonLibrary`, `SortStrategy`, `SortByTitle`, `SortByYear`, `Command`, `BorrowCommand`, `CommandManager` oraz `MediaUnavailableError`.
- **Użycie dziedziczenia:** Klasy `Book` i `Movie` dziedziczą po klasie bazowej `Media`. Pozwala to na ponowne wykorzystanie wspólnych atrybutów (`title`, `year`, `is_available`, `borrower`) oraz metod (`get_info`, `borrow`, `return_item`, `to_dict`, `from_dict`), a także na dodawanie specyficznych cech dla każdego typu multimediów.
- **Enkapsulacja (Settery i Gettery):** W klasie `User` zastosowano enkapsulację dla atrybutu prywatnego `_username`. Zdefiniowano metodę `@property username` jako getter oraz metodę `@username.setter username` jako setter, który dodatkowo waliduje, czy wprowadzana nazwa użytkownika nie jest pusta.
- **Polimorfizm:** Metoda `get_info()` w klasie `Media` wywołuje polimorficzną metodę `_extra_info()`. Dzięki temu podczas iteracji po liście obiektów typu `Media` (która może zawierać wymieszane obiekty `Book` i `Movie`) wywoływana jest odpowiednia, specyficzna implementacja `_extra_info()` dla danego typu medium. Pozwala to na wyświetlanie unikalnych danych w ujednolicony sposób.

### 2. Zaawansowane Mechanizmy i Konstruktory

- **Nadpisywanie atrybutów w klasach potomnych:** Klasa `Media` definiuje atrybut klasy `category = "Generic"`. Klasy potomne nadpisują ten atrybut, ustawiając odpowiednio `category = "Książka"` (w `Book`) oraz `category = "Film"` (w `Movie`).
- **Nadpisywanie metod i wykorzystanie `super()`:** \* Klasa bazowa `Media` posiada pustą metodę `_extra_info()`, którą `Book` i `Movie` nadpisują, aby dodać specyficzne informacje (autor i ISBN dla książki, reżyser i czas trwania dla filmu).
  - Metoda `to_dict` jest nadpisywana w klasach potomnych, aby uwzględnić dodatkowe pola, jednocześnie wywołując `super().to_dict()` w celu pobrania i podstawowej inicjalizacji danych z klasy rodzica.
  - W konstruktorach (`__init__`) klas `Book` i `Movie` użyto `super().__init__(title, year)` do prawidłowej inicjalizacji wspólnych atrybutów bazowych.
- **Dekoratory `@classmethod` oraz `@staticmethod`:** W klasie `Media` oraz jej podklasach użyto dekoratora `@classmethod` w metodach `from_dict`. W klasie `Book` zastosowano go również w metodzie `from_string`. Umożliwia to tworzenie instancji klas przy użyciu alternatywnych konstruktorów.
- **Klasa zawierająca więcej niż jeden konstruktor:** Klasa `Book` posiada dwa konstruktory: standardowy `__init__` oraz alternatywny konstruktor klasy `from_string`, który automatycznie tworzy i parsuje obiekt `Book` na podstawie przekazanego ciągu znaków.

### 3. Obsługa Błędów

- **Własna klasa wyjątku:** Zdefiniowano własny wyjątek `MediaUnavailableError`, który dziedziczy z wbudowanej klasy `Exception`. Jest on rzucany w metodzie `borrow` klasy `Media`, gdy użytkownik próbuje wypożyczyć pozycję, która jest aktualnie niedostępna, co zapewnia precyzyjną kontrolę i obsługę błędów w aplikacji.

---

## 📐 Zastosowane Wzorce Projektowe

| Wzorzec Projektowy         | Klasy Implementujące                         | Opis i Rola w Systemie                                                                                                                                                                                                                |
| :------------------------- | :------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Strategia** _(Strategy)_ | `SortStrategy`, `SortByTitle`, `SortByYear`  | Umożliwia dynamiczną zmianę algorytmu sortowania zbiorów mediów (np. po tytule lub roku wydania) w klasie `SingletonLibrary` bez konieczności modyfikacji jej kodu źródłowego.                                                        |
| **Polecenie** _(Command)_  | `Command`, `BorrowCommand`, `CommandManager` | Hermetyzuje operację wypożyczenia zasobu w obiekcie `BorrowCommand`. Pozwala to na parametryzowanie wywołań, kolejkowanie operacji oraz łatwe cofanie ostatnich akcji (`undo`) za pomocą managera.                                    |
| **Singleton**              | `SingletonLibrary`                           | Gwarantuje, że w całej aplikacji istnieje tylko jedna, współdzielona instancja klasy zarządzającej zasobami biblioteki. Zapewnia ona globalny punkt dostępu do bazy danych mediów i użytkowników poprzez nadpisanie metody `__new__`. |

---

_Projekt przygotowany w ramach zaliczenia przedmiotu._
