from flask import Flask, render_template, session, redirect, url_for, request
from flask_session import Session
from tempfile import mkdtemp
import redisHelp
import copy
import redis
import os

app = Flask(__name__)
app.session_interface = RedisSessionInterface()

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
redis = redis.from_url(redis_url)


app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/", methods=["GET", "POST"])
def board():
    if "board" not in session or "turn" not in session:
        session["board"] = [[None, None, None], [None, None, None], [None, None, None]]
        session["turn"] = "X"
    elif check(session["board"], session["turn"]) != 0:   # works based on a conveniency, the turn is technically wrong
        return render_template("game.html", game=session["board"], turn=session["turn"], over=True)
    elif len(getMoves(session["board"])) == 0:
        return render_template("game.html", game=session["board"], turn=session["turn"], full=True)
    elif session["turn"] is "X":
        session["turn"] = "O"
    else:
        session["turn"] = "X"
    return render_template("game.html", game=session["board"], turn=session["turn"])

@app.route("/reset", methods=["GET", "POST"])
def res():
    session.clear()
    return redirect("/")

@app.route("/move", methods=["POST"])
def move():
    turn = session["turn"]

    board = copy.deepcopy(session["board"])

    if turn is "X":
        moveX(board)
    else:
        moveO(board)

    return redirect("/")


@app.route("/play/<int:row>/<int:col>")
def play(row, col):
    session["board"][row][col] = session["turn"]
    return redirect(url_for("board"))


def moveX(board):
    moves = getMoves(board)

    if (len(moves) == 0):
        return
    if (check(board, "O")):
        return
    if (check(board, "X")):
        return

    values = list()

    for move in moves:
        board[move[0]][move[1]] = "X"
        values.append(minimax(board, 1, 1))
        board[move[0]][move[1]] = None

    highest = values[0]
    ind = 0

    for i in range(len(values)):
        if values[i] > highest:
            highest = values[i]
            ind = i

    session["board"][moves[ind][0]][moves[ind][1]] = "X"


def moveO(board):
    moves = getMoves(board)

    if (len(moves) == 0):
        return
    if (check(board, "O")):
        return
    if (check(board, "X")):
        return
    values = list()

    for move in moves:
        board[move[0]][move[1]] = "O"
        values.append(minimax(board, -1, 1))
        board[move[0]][move[1]] = None

    lowest = values[0]
    ind = 0
    for i in range(len(values)):
        if values[i] < lowest:
            lowest = values[i]
            ind = i

    session["board"][moves[ind][0]][moves[ind][1]] = "O"

def minimax(board, desired, depth):

    moves = getMoves(board)
    turn = "X"
    if desired < 0: #if desired is -1, then it's X's turn
        turn = "X"
    else:
        turn = "O"


    if (check(board, "X")):
        return 10 - depth
    if (check(board, "O")):
        return -10 + depth
    if (len(moves) == 0):
        return 0

    values = list()
    for move in moves:
        board[move[0]][move[1]] = turn
        values.append(minimax(board, -desired, depth + 1))
        board[move[0]][move[1]] = None

    if desired < 0: # We're worried about the best X move then
        highest = values[0]
        for i in range(len(values)):
            if values[i] > highest:
                highest = values[i]
        return highest
    else:
        lowest = values[0]
        for i in range(len(values)):
            if values[i] < lowest:
                lowest = values[i]
        return lowest

def getMoves(board):
    moves = list()
    for i in range(3):
        for j in range(3):
            if board[i][j] is None: # if there is no move, board is not full
                moves.append((i, j))
    return moves

# search through all possible gamestates, assigning a value to each possible move *if you find the winning case, make that move* otherwise, make the next best move.


def check(board, turn):
    # Check each horizontal
    value = 0
    full = True
    if turn is "X":
        value = 1
    else:
        value = -1

    for i in range(3):
        ck = True
        for j in range(3):
            if board[i][j] is not turn:
                ck = False
                break
        if ck:
            return value


    # Check each vertical
    for i in range(3):
        ck = True
        for j in range(3):
            if board[j][i] is not turn:
                ck = False
                break
        if ck:
            return value

    # Check diagonal 1
    ck = True
    for i in range(3):
        if board[i][i] is not turn:
            ck = False
            break
    if ck:
        return value

    # Check diagonal 2
    for i in range(3):
        ck = True
        if board[i][2 - i] is not turn:
            ck = False
            break
    if ck:
        return value
    return 0

