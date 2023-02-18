from flask import Flask, render_template, request, redirect, jsonify, flash, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import requests
import json
from functools import wraps
import re
from flask_sqlalchemy import SQLAlchemy
import hmac
import os
from dotenv import load_dotenv

project_folder = os.path.expanduser('/home/kanaboard/kanaboard')
load_dotenv(os.path.join(project_folder, '.env'))

def safe_str_cmp(a: str, b: str) -> bool:
    """This function compares strings in somewhat constant time. This
    requires that the length of at least one string is known in advance.

    Returns `True` if the two strings are equal, or `False` if they are not.
    """

    if isinstance(a, str):
        a = a.encode("utf-8")  # type: ignore

    if isinstance(b, str):
        b = b.encode("utf-8")  # type: ignore

    return hmac.compare_digest(a, b)

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

# MySQL Database (PythonAnywhere)
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username=os.getenv("USERNAME"),
    password=os.getenv("SECRET_KEY"),
    hostname=os.getenv("MY_HOSTNAME"),
    databasename=os.getenv("MY_DBNAME"),
)  

app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
Base = db.Model

class Users(Base):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text)
    hash = db.Column(db.Text)

class Favorites(Base):
    __tablename__ = 'favorites'
    key = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    word = db.Column(db.Text)
    definition = db.Column(db.Text)
    reading = db.Column(db.Text)

class FavePhrases(Base):
    __tablename__ = 'fave_phrases'
    key = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    phrase = db.Column(db.Text)

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
                    if (session.get('user_id') is not None):
                        get_word = Favorites.query.filter_by(user_id=session["user_id"], word=word).first()

                        # Error checking
                        if (get_word != None):
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

        db.session.add(Favorites(user_id=session["user_id"], word=kanji_word, definition=kanji_def, reading=kanji_reading))
        db.session.commit()
        return jsonify(response=f"Successfully saved {kanji_word} to Favorites.")


@app.route("/kanjiDelete")
def kanji_delete():
    kanji_word = request.args.get("kanjiWord", 0, type=str)
    fetched = Favorites.query.filter_by(user_id=session["user_id"], word=kanji_word).first()
    db.session.delete(fetched)
    db.session.commit()

    return jsonify(response=f"Successfully deleted {kanji_word} in Favorites.")


@app.route("/phraseSave")
def phrase_save():
    if session.get("user_id") is None:
        return jsonify(response="Please log-in to save a phrase")

    else:
        phrase = request.args.get("phrase", 0, type=str)

        # Check first if user already saved the word
        get_word = FavePhrases.query.filter_by(user_id=session["user_id"], phrase=phrase).first()
        if (get_word != None):
            return jsonify(response="Already in favorites.")

        # Insert user's inputs to db
        db.session.add(FavePhrases(user_id=session["user_id"], phrase=phrase))
        db.session.commit()

        return jsonify(response=f'Successfully saved "{phrase}" to Favorites.')


@app.route("/phraseDelete")
def phrase_delete():
    phrase = request.args.get("phrase", 0, type=str)
    fetched = FavePhrases.query.filter_by(user_id=session["user_id"], phrase=phrase).first()
    db.session.delete(fetched)
    db.session.commit()

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
        get_name = Users.query.filter_by(username=name).first()
        if (get_name != None):
            errorbox = "username"
            flash(f'Username "{name}" already exists. Please try another one.')
            return render_template("signup.html", errorbox=errorbox)

        # Insert user's inputs to db
        db.session.add(Users(username=name, hash=hash_password))
        db.session.commit()

        fetched = Users.query.filter_by(username=name).first()
        get_id = int(fetched.id)
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
        name = request.form.get("username")
        fetched = Users.query.filter_by(username=name).first()

        # Ensure username exists and password is correct
        if fetched == None or not check_password_hash(fetched.hash, request.form.get("password")):
            flash("Invalid username/password.")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = fetched.id
        global USER_ID
        USER_ID = fetched.id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/getFavorites")
def get_favorites():
    fave_option = request.args.get("faveOption")

    if (fave_option == "words"):
        fetched = Favorites.query.filter_by(user_id=session["user_id"]).all()

        words_list = []
        words_reading = []
        words_def = []

        for kanji in fetched:
            words_list.append(kanji.word)
            words_reading.append(kanji.reading)
            words_def.append(kanji.definition)

        return jsonify(words=words_list, reading=words_reading, definition=words_def)

    elif (fave_option == "phrases"):
        fetched = FavePhrases.query.filter_by(user_id=session["user_id"]).all()
        phrases_list = []
        for phrase in fetched:
            phrases_list.append(phrase.phrase)

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