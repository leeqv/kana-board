import os
from flask import Flask, render_template, request, redirect, jsonify, flash, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash, safe_str_cmp
import sqlite3
import requests
import json
import urllib.parse
from functools import wraps
import re

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
app.config["SESSION_FILE_DIR"] = mkdtemp()
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

                    # Establish sqlite3 connection
                    conn = sqlite3.connect("kanaboard.db")
                    cur = conn.cursor()

                    # Check if user already saved the word
                    cur.execute("SELECT word FROM favorites WHERE user_id = ? AND word = ?", (USER_ID, word))
                    get_word = cur.fetchall()

                    # Error checking
                    if (len(get_word) > 0):
                        faves.append(word)

                    conn.close()

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

        # Establish sqlite3 connection
        conn = sqlite3.connect("kanaboard.db")
        cur = conn.cursor()

        # Check first if user already saved the word
        cur.execute("SELECT word FROM favorites WHERE user_id = ? AND word = ?", (USER_ID, kanji_word))
        get_word = cur.fetchall()

        # Insert user's inputs to db
        cur.execute("INSERT INTO favorites(user_id, word, definition, reading) VALUES(?, ?, ?, ?)",
                    (USER_ID, kanji_word, kanji_def, kanji_reading))
        conn.commit()

        conn.close()

        return jsonify(response=f"Successfully saved {kanji_word} to Favorites.")


@app.route("/kanjiDelete")
def kanji_delete():
    kanji_word = request.args.get("kanjiWord", 0, type=str)

    # Establish sqlite3 connection
    conn = sqlite3.connect("kanaboard.db")
    cur = conn.cursor()

    # Check first if user already saved the word
    cur.execute("DELETE FROM favorites WHERE user_id = ? AND word = ?", (USER_ID, kanji_word))
    conn.commit()

    conn.close()

    return jsonify(response=f"Successfully deleted {kanji_word} in Favorites.")


@app.route("/phraseSave")
def phrase_save():
    if session.get("user_id") is None:
        return jsonify(response="Please log-in to save a phrase")

    else:
        phrase = request.args.get("phrase", 0, type=str)

        # Establish sqlite3 connection
        conn = sqlite3.connect("kanaboard.db")
        cur = conn.cursor()

        # Check first if user already saved the word
        cur.execute("SELECT phrase FROM fave_phrases WHERE user_id = ? AND phrase = ?", (USER_ID, phrase))
        get_word = cur.fetchall()

        if (len(get_word) > 0):
            return jsonify(response="Already in favorites.")

        # Insert user's inputs to db
        cur.execute("INSERT INTO fave_phrases(user_id, phrase) VALUES(?, ?)", (USER_ID, phrase))
        conn.commit()

        conn.close()

        return jsonify(response=f'Successfully saved "{phrase}" to Favorites.')


@app.route("/phraseDelete")
def phrase_delete():
    phrase = request.args.get("phrase", 0, type=str)

    # Establish sqlite3 connection
    conn = sqlite3.connect("kanaboard.db")
    cur = conn.cursor()

    # Check first if user already saved the word
    cur.execute("DELETE FROM fave_phrases WHERE user_id = ? AND phrase = ?", (USER_ID, phrase))
    conn.commit()

    conn.close()

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

        # Establish sqlite3 connection
        conn = sqlite3.connect("kanaboard.db")
        cur = conn.cursor()

        cur.execute("SELECT username FROM users WHERE username = ?", (name,))
        get_name = cur.fetchall()

        # Error checking
        if (len(get_name) > 0):
            conn.close()
            errorbox = "username"
            flash(f'Username "{name}" already exists. Please try another one.')
            return render_template("signup.html", errorbox=errorbox)

        # Insert user's inputs to db
        cur.execute("INSERT INTO users(username, hash) VALUES(?, ?)", (name, hash_password))
        conn.commit()

        cur.execute("SELECT * FROM users WHERE username = ?", (name,))
        get_id = int(cur.fetchall()[0][0])
        session["user_id"] = get_id
        conn.close()

        global USER_ID
        USER_ID = get_id

        return redirect("/")

    else:
        return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Save previous input before logging in
    if request.method == "POST":
        conn = sqlite3.connect("kanaboard.db")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Query database for username
        username = request.form.get("username")
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        rows = cur.fetchall()

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

    # Establish sqlite3 connection
    conn = sqlite3.connect("kanaboard.db")
    cur = conn.cursor()

    if (fave_option == "words"):
        fave_words = []
        cur.execute("SELECT word,definition,reading FROM favorites WHERE user_id = ?", (USER_ID,))

        words_list = []
        words_reading = []
        words_def = []

        for word, definition, reading in cur.fetchall():
            words_list.append(word)
            words_reading.append(reading)
            words_def.append(definition)

        return jsonify(words=words_list, reading=words_reading, definition=words_def)

    elif (fave_option == "phrases"):
        cur.execute("SELECT phrase FROM fave_phrases WHERE user_id = ?", (USER_ID,))
        phrases_list = cur.fetchall()
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