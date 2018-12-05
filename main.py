import json
from flask import Flask, request, redirect, g, render_template, Response
import requests
import base64
import urllib.parse
from tswift import Song

# Authentication Steps, paramaters, and responses are defined at https://developer.spotify.com/web-api/authorization-guide/
# Visit this url to see all the steps, parameters, and expected response. 


app = Flask(__name__)


#  Client Keys
CLIENT_ID = "435590f455b842eea1ef3857916f96c8"
CLIENT_SECRET = "231bc6d0d7a7450db915dd2f4689d0bb"

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)


# Server-side Parameters
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 5555
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "playlist-modify-public playlist-modify-private user-read-currently-playing"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()


auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    # Auth Step 1: Authorization
    url_args = "&".join(["{}={}".format(key,urllib.parse.quote(val)) for key,val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)


@app.route("/callback/q")
def callback():
    # Auth Step 4: Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI
    }
    base = "{}:{}"
    format_client = base.format(CLIENT_ID,CLIENT_SECRET)
    base64encoded = base64.urlsafe_b64encode(format_client.encode()).decode()
    headers = {"Authorization": "Basic {}".format(base64encoded)}
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload, headers=headers)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)

    global access_token
    access_token = response_data["access_token"]

    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    # Auth Step 6: Use the access token to access Spotify API
    global authorization_header
    authorization_header = {"Authorization":"Bearer {}".format(access_token)}
    
    return redirect("/lyrics")


@app.route("/lyrics")
def displayLyrics():
    return render_template("lyrics.html",token=str(access_token))

def getLyrics(track,artist):
    s = Song(track,artist)
    return s.lyrics

@app.route('/reciever', methods = ['POST'])
def getTrackInfo():
    global postTrack
    postTrack = request.form['trackName']

    global postArtist
    postArtist = request.form['artistName']
    return "Recieved"

@app.route('/send')
def sendLyrics():
    track = postTrack
    artist = postArtist
    lyrics = getLyrics(track,artist)
    return json.dumps(lyrics)

if __name__ == "__main__":
    app.run(debug=True,port=PORT)

