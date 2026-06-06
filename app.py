from flask import Flask, render_template, session
import random
from telemetry import track_event

DICE_FACES = {
    1: "⚀",
    2: "⚁",
    3: "⚂",
    4: "⚃",
    5: "⚄",
    6: "⚅"
}

app = Flask(__name__)
app.secret_key = "dice21-secret-key"


def reset_game():
    session["player_score"] = 0
    session["computer_score"] = 0
    session["message"] = ""
    session["game_over"] = False
    session["last_roll"] = None
    session["dice_face"] = "🎲"

    if "games_played" not in session:
        session["games_played"] = 0

    if "wins" not in session:
        session["wins"] = 0

    if "losses" not in session:
        session["losses"] = 0

    if "draws" not in session:
        session["draws"] = 0

    track_event("GameStarted")


@app.route("/")
def home():
    if "player_score" not in session:
        reset_game()

    games_played = session.get("games_played", 0)
    wins = session.get("wins", 0)

    if games_played > 0:
        win_rate = round((wins / games_played) * 100, 1)
    else:
        win_rate = 0

    return render_template(
        "index.html",
        player_score=session.get("player_score", 0),
        computer_score=session.get("computer_score", 0),
        message=session.get("message", ""),
        game_over=session.get("game_over", False),
        last_roll=session.get("last_roll"),
        dice_face=session.get("dice_face", "🎲"),
        games_played=games_played,
        wins=session.get("wins", 0),
        losses=session.get("losses", 0),
        draws=session.get("draws", 0),
        win_rate=win_rate
    )


@app.route("/roll", methods=["POST"])
def roll():

    if session.get("game_over"):
        return home()

    dice = random.randint(1, 6)

    session["last_roll"] = dice
    session["dice_face"] = DICE_FACES[dice]
    session["player_score"] += dice

    track_event(
        "DiceRolled",
        dice_value=dice,
        current_score=session["player_score"]
    )

    session["message"] = f"You rolled {session['dice_face']} ({dice})"

    if session["player_score"] > 21:

        track_event(
            "PlayerBust",
            final_score=session["player_score"]
        )

        track_event(
            "GameLost",
            player_score=session["player_score"],
            computer_score=session["computer_score"]
        )

        session["games_played"] += 1
        session["losses"] += 1

        session["message"] += " - Bust! You lose."
        session["game_over"] = True

    elif session["player_score"] == 21:

        track_event(
            "GameWon",
            player_score=21
        )

        session["games_played"] += 1
        session["wins"] += 1

        session["message"] += " - Exactly 21! You win!"
        session["game_over"] = True

    return home()


@app.route("/hold", methods=["POST"])
def hold():

    if session.get("game_over"):
        return home()

    track_event(
        "PlayerHeld",
        player_score=session["player_score"]
    )

    player_score = session["player_score"]

    computer_score = 0

    while computer_score < 17:
        computer_score += random.randint(1, 6)

    session["computer_score"] = computer_score

    if computer_score > 21:

        track_event(
            "GameWon",
            player_score=player_score,
            computer_score=computer_score
        )

        session["games_played"] += 1
        session["wins"] += 1

        session["message"] = (
            f"Computer busted with {computer_score}. You win!"
        )

    elif player_score > computer_score:

        track_event(
            "GameWon",
            player_score=player_score,
            computer_score=computer_score
        )

        session["games_played"] += 1
        session["wins"] += 1

        session["message"] = (
            f"You win! {player_score} vs {computer_score}"
        )

    elif player_score < computer_score:

        track_event(
            "GameLost",
            player_score=player_score,
            computer_score=computer_score
        )

        session["games_played"] += 1
        session["losses"] += 1

        session["message"] = (
            f"Computer wins! {computer_score} vs {player_score}"
        )

    else:

        track_event(
            "GameDraw",
            player_score=player_score,
            computer_score=computer_score
        )

        session["games_played"] += 1
        session["draws"] += 1

        session["message"] = "Draw!"

    session["game_over"] = True

    return home()


@app.route("/new_game", methods=["POST"])
def new_game():
    reset_game()
    return home()


if __name__ == "__main__":
    app.run(debug=True)