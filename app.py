import os
from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session
import spotipy
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path():
    return caches_folder + session.get('uuid')

@app.route('/')
def index():
    return render_template("landing_page.html", image_file=url_for("static", filename="home.png"))


auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing user-library-modify playlist-read-private playlist-modify-private user-library-read',
                                                show_dialog=True)


@app.route('/login')
def login():
    if not session.get('uuid'):
	# assign the new user session with unique id
        session['uuid'] = str(uuid.uuid4())    
    url = auth_manager.get_authorize_url()
    return redirect(url)

@app.route("/callback/")
def callback():
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-private', 
                                                cache_path=session_cache_path(), show_dialog=True)
    if request.args.get("code"):
	# get the code qurey from the url and passe it to the access token
        auth_manager.get_access_token(request.args.get("code"))
	# when it's done redirect to the profile page
    return redirect("/profile")

@app.route('/profile', methods=["GET", "POST"])
def profile():
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=session_cache_path())
    result = spotipy.Spotify(auth_manager=auth_manager)
    tracks = result.current_user_saved_tracks()
    result = result.me()

    return render_template("profile_2.html", user_name=result["display_name"], followers=result["followers"]["total"], tracks=tracks, profile_pic=url_for("static", filename="profile.jpg"))


@app.route('/top_tracks')
def top_tracks():
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=session_cache_path())
    result = spotipy.Spotify(auth_manager=auth_manager)
    results = result.current_user_saved_tracks()
    user = result.me()
    return render_template("top_tracks.html", results=results, username=user["display_name"])


@app.route('/add_new_playlist')
def add():
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=session_cache_path())
    Spotify = spotipy.Spotify(auth_manager=auth_manager)

    user_id = Spotify.me()['id']
    user_saved_tracks = Spotify.current_user_saved_tracks()
    ids = []
    for idx, item in enumerate(user_saved_tracks['items']):
        ids.append(item['track']['artists'][0]['id'])
    recommendations_result = Spotify.recommendations(seed_artists=ids[0:5])
    recommendations_result = recommendations_result["tracks"] 
    return render_template("add_new_playlist.html", recommendations_result=recommendations_result)

@app.route("/about")
def about():
    return render_template("about.html", image_file=url_for("static", filename="home.png"))

@app.route('/logout')
def logout():
    os.remove(session_cache_path())
    session.clear()
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.rmdir(caches_folder)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/')

if __name__ == '__main__':
	app.run(threaded=True, port=int(os.environ.get("PORT", 5000)))
