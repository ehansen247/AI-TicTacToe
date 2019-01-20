from flask import Flask, render_template, session, redirect, url_for, request
from flask_session import Session
from tempfile import mkdtemp

app = Flask(__name__)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/", methods=["GET", "POST"])
def board():
    if request.method == "POST":
        session["board"] = [[None, None, None], [None, None, None], [None, None, None]]
        session["turn"] = "X"
        return redirect("/")
    else:
        if "board" not in session or "turn" not in session:
            session["board"] = [[None, None, None], [None, None, None], [None, None, None]]
            session["turn"] = "X"
        elif check(session["turn"]):
            return render_template("over.html", turn=session["turn"])
        elif session["turn"] is "X":
            session["turn"] = "O"
        else:
            session["turn"] = "X"
        return render_template("game.html", game=session["board"], turn=session["turn"])

@app.route("/play/<int:row>/<int:col>")
def play(row, col):

    session["board"][row][col] = session["turn"]
    return redirect(url_for("board"))

def check(turn):
    # Check each horizontal
    for i in range(3):
        ck = True
        for j in range(3):
            if session["board"][i][j] is not turn:
                ck = False
                break
        if ck:
            print("reached1")
            return True

    # Check each vertical
    for i in range(3):
        ck = True
        for j in range(3):
            if session["board"][j][i] is not turn:
                ck = False
                break
        if ck:
            print("reached2")
            return True

    # Check diagonal 1
    ck = True
    for i in range(3):
        if session["board"][i][i] is not turn:
            ck = False
            break
    if ck:
        print("reached3")
        return True

    # Check diagonal 2
    for i in range(3):
        ck = True
        if session["board"][i][2 - i] is not turn:
            ck = False
            break
    if ck:
        print("reached4")
        return True
    return False

# Reset Game Button
# Update board after each move
