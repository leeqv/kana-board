import os
from flask import Flask, render_template, request, redirect, jsonify, flash, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash, safe_str_cmp
import requests
import json
import urllib.parse
from functools import wraps
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# Configure application
app = Flask(__name__)

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
#app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Global variable USER_ID, initialize to zero
USER_ID = 0


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/kanjiGet")
def kanji_get():
    kana_input = request.args.get("kanaInput", 0, type=str)

    # Get kanji from jisho
    url = 'http://jisho.org/api/v1/search/words?keyword=\"' + kana_input + '\"'

    response = requests.get(url)
    response.raise_for_status()
    termData = json.loads(response.text)
    data = termData["data"]
    len_t = len(data)
    kanji_list = []
    kanji_no = []
    kanji_def = []
    faves = []

    if (len_t < 1):
        return jsonify(result=[], index=[], definitions=[])

    for i in range(0, len_t, 1):
        len_t_i = len(data[i]["japanese"])
        for j in range(0, len_t_i, 1):
            if (data[i]["japanese"][j]["reading"] == kana_input):
                kanji_no.append(i)

                if "word" in data[i]["japanese"][j]:
                    word = data[i]["japanese"][j]["word"]
                    kanji_list.append(word)

                    # Check if user already saved the word
                    get_word = db.execute("SELECT word FROM favorites WHERE user_id = ? AND word = ?", USER_ID, word)

                    # Error checking
                    if (len(get_word) > 0):
                        faves.append(word)


    for i in range(0, len_t, 1):
        kanji_def.append(data[i]["senses"][0]["english_definitions"])

    return jsonify(result=kanji_list, index=kanji_no, definitions=kanji_def, faves=faves)


@app.route("/kanjiSave")
def kanji_save():
    if session.get("user_id") is None:
        return jsonify(response="Please log-in to save a word", logged="no")

    else:
        kanji_word = request.args.get("kanjiWord", 0, type=str)
        kanji_def = request.args.get("kanjiDef")
        kanji_reading = request.args.get("kanjiReading", 0, type=str)

        # Check first if user already saved the word
        get_word = db.execute("SELECT word FROM favorites WHERE user_id = ? AND word = ?", USER_ID, kanji_word)
        # Insert user's inputs to db
        db.execute("INSERT INTO favorites(user_id, word, definition, reading) VALUES(?, ?, ?, ?)", USER_ID, kanji_word, kanji_def, kanji_reading)

        return jsonify(response=f"Successfully saved {kanji_word} to Favorites.")


@app.route("/kanjiDelete")
def kanji_delete():
    kanji_word = request.args.get("kanjiWord", 0, type=str)
    db.execute("DELETE FROM favorites WHERE user_id = ? AND word = ?", USER_ID, kanji_word)

    return jsonify(response=f"Successfully deleted {kanji_word} in Favorites.")


@app.route("/phraseSave")
def phrase_save():
    if session.get("user_id") is None:
        return jsonify(response="Please log-in to save a phrase")

    else:
        phrase = request.args.get("phrase", 0, type=str)

        # Check first if user already saved the word
        get_word = db.execute("SELECT phrase FROM fave_phrases WHERE user_id = ? AND phrase = ?", USER_ID, phrase)
        if (len(get_word) > 0):
            return jsonify(response="Already in favorites.")

        # Insert user's inputs to db
        db.execute("INSERT INTO fave_phrases(user_id, phrase) VALUES(?, ?)", USER_ID, phrase)

        return jsonify(response=f'Successfully saved "{phrase}" to Favorites.')


@app.route("/phraseDelete")
def phrase_delete():
    phrase = request.args.get("phrase", 0, type=str)
    db.execute("DELETE FROM fave_phrases WHERE user_id = ? AND phrase = ?", USER_ID, phrase)

    return jsonify(response=f"Successfully deleted {phrase} in Favorites.")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Error checking
        if not name or not password or not confirmation:
            errorbox = "username"
            flash("Blank field")
            return render_template("signup.html", errorbox=errorbox)

        if not(safe_str_cmp(password, confirmation)):
            flash("Passwords did not match")
            return redirect("/signup")

        # Password strength
        regex = "^(?=.*[a-zA-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
        compiled_reg = re.compile(regex)

        strong_pwd = re.search(compiled_reg, password)

        if not strong_pwd:
            flash("Password must be 6-20 alphanumeric characters and contain at least 1 special character.")
            return redirect("/signup")

        # Make hash
        hash_password = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)

        # Error checking
        get_name = db.execute("SELECT username FROM users WHERE username = ?", (name,))
        if (len(get_name) > 0):
            errorbox = "username"
            flash(f'Username "{name}" already exists. Please try another one.')
            return render_template("signup.html", errorbox=errorbox)

        # Insert user's inputs to db
        db.execute("INSERT INTO users(username, hash) VALUES(?, ?)", name, hash_password)
        fetched = db.execute("SELECT * FROM users WHERE username = ?", (name,))
        get_id = int(fetched[0]["id"])
        session["user_id"] = get_id

        global USER_ID
        USER_ID = get_id

        return redirect("/")

    else:
        return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Save previous input before logging in
    if request.method == "POST":
        # Query database for username
        username = request.form.get("username")
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid username/password.")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        global USER_ID
        USER_ID = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/getFavorites")
def get_favorites():
    fave_option = request.args.get("faveOption")

    if (fave_option == "words"):
        fave_words = []
        fetched = db.execute("SELECT word,definition,reading FROM favorites WHERE user_id = ?", USER_ID)

        words_list = []
        words_reading = []
        words_def = []

        for kanji in fetched:
            words_list.append(kanji["word"])
            words_reading.append(kanji["reading"])
            words_def.append(kanji["definition"])

        return jsonify(words=words_list, reading=words_reading, definition=words_def)

    elif (fave_option == "phrases"):
        fetched = db.execute("SELECT phrase FROM fave_phrases WHERE user_id = ?", USER_ID)
        phrases_list = []
        for phrase in fetched:
            phrases_list.append(phrase["phrase"])

        return jsonify(phrases=phrases_list)


@app.route("/favorites")
@login_required
def favorites():
    return render_template("favorites.html")


@app.route("/logout")
def logout():
    global USER_ID
    USER_ID = 0

    # Forget any user_id
    session.clear()

    return jsonify(status="success")