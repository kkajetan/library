from flask import Flask, render_template, request, redirect, url_for, flash
from  library import SingletonLibrary, Book, Movie, User, CommandManager, BorrowCommand, SortByTitle, SortByYear
command_manager = CommandManager()

app = Flask(__name__)
app.secret_key = 'tajny_klucz'

library = SingletonLibrary()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/media')
def show_media():
    return render_template('media_list.html', media_list=library.media_list)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        try:
            title = request.form['title']
            year = int(request.form['year'])
            author = request.form['author']
            isbn = request.form['isbn']
            library.add_media(Book(title, year, author, isbn))
            flash("Książka została dodana.")
            return redirect(url_for('show_media'))
        except Exception as e:
            flash(str(e))
    return render_template('add_book.html')

@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    if request.method == 'POST':
        try:
            title = request.form['title']
            year = int(request.form['year'])
            director = request.form['director']
            duration = int(request.form['duration'])
            library.add_media(Movie(title, year, director, duration))
            flash("Film został dodany.")
            return redirect(url_for('show_media'))
        except Exception as e:
            flash(str(e))
    return render_template('add_movie.html')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        if library.find_user_by_username(username):
            flash("Taki użytkownik już istnieje.")
        else:
            library.add_user(User(username))
            flash("Zarejestrowano użytkownika.")
        return redirect(url_for('index'))
    return render_template('register_user.html')

@app.route('/show_users')
def show_users():
    users = library.users
    return render_template("user_list.html", users=users)

@app.route("/borrow_media", methods=["GET", "POST"])
def borrow_media():
    if request.method == "POST":
        uname = request.form["username"]
        title = request.form["title"]

        user = library.find_user_by_username(uname)
        media = library.find_media_by_title(title)

        if not user:
            flash(f"Błąd: Użytkownik '{uname}' nie znaleziony.", "error")
        elif not media:
            flash(f"Błąd: Medium '{title}' nie znalezione.", "error")
        else:
            command = BorrowCommand(library, user, media)
            command_manager.execute_command(command)
            flash(f"Medium '{title}' zostało wypożyczone przez '{uname}'.", "success")
            return redirect(url_for("borrow_media"))

    return render_template("borrow.html")

@app.route("/undo", methods=["GET", "POST"])
def undo_last_command():
    if request.method == "POST":
        if command_manager.history:
            command_manager.undo_last()
            flash("Ostatnia operacja została cofnięta.", "success")
        else:
            flash("Brak komend do cofnięcia.", "error")
        return redirect(url_for("undo_last_command"))

    return render_template("undo_last.html")

@app.route("/sort_media", methods=["GET", "POST"])
def sort_media():
    if request.method == "POST":
        sort_choice = request.form.get("sort_choice")
        if sort_choice == "title":
            library.sort_media(SortByTitle())
            flash("Posortowano media po tytule.", "success")
        elif sort_choice == "year":
            library.sort_media(SortByYear())
            flash("Posortowano media po roku.", "success")
        else:
            flash("Nieprawidłowa opcja sortowania.", "error")
        return redirect(url_for("sort_media"))

    return render_template("sort_media.html", media_list=library.media_list)


@app.route('/save_media', methods=['POST'])
def save_media():
    try:
        library.save_media_to_file()
        flash("Media zapisane do pliku.", "success")
    except Exception as e:
        flash(f"Błąd zapisu mediów: {e}", "error")
    return redirect(url_for('index'))

@app.route('/load_media', methods=['POST'])
def load_media():
    try:
        library.load_media_from_file()
        flash("Media wczytane z pliku.", "success")
    except Exception as e:
        flash(f"Błąd wczytywania mediów: {e}", "error")
    return redirect(url_for('index'))

@app.route('/save_users', methods=['POST'])
def save_users():
    try:
        library.save_users_to_file()
        flash("Użytkownicy zapisani do pliku.", "success")
    except Exception as e:
        flash(f"Błąd zapisu użytkowników: {e}", "error")
    return redirect(url_for('index'))

@app.route('/load_users', methods=['POST'])
def load_users():
    try:
        library.load_users_from_file()
        flash("Użytkownicy wczytani z pliku.", "success")
    except Exception as e:
        flash(f"Błąd wczytywania użytkowników: {e}", "error")
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)
