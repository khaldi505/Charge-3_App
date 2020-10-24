from flask import Flask, render_template, request, session, redirect, url_for
import spotipy
from spotipy import oauth2
from spotipy.oauth2 import SpotifyOAuth
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

SCOPE = "playlist-modify-public user-read-recently-played user-top-read" \
        " user-read-currently-playing user-follow-read user-follow-modify" \
        " user-modify-playback-state playlist-modify-private"
CACHE = '.spotifycache'
sp_oauth = oauth2.SpotifyOAuth(scope=SCOPE, cache_path=CACHE)


@app.route('/', methods=["GET"])
def home():
    return render_template("landing_page.html", image_file=url_for("static", filename="home.png"))


@app.route('/login')
def login():
    if not session.get("logged_in"):
        url = sp_oauth.get_authorize_url()
        return redirect(url)
    else:
        return redirect(url_for("profile"))

@app.route('/log_out')
def logout():
    session["logged_in"] = False
    return home()


@app.route("/profile")
def profile():
    return render_template("profile.html")


if __name__ == '__main__':
    app.run()
