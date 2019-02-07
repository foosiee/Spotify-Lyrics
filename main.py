import json
from flask import Flask,request, redirect, g, render_template, Response, session, send_from_directory
import requests
import os
import ssl
import base64
import urllib.parse
from tswift import Song
from googlesearch import search
 # Authentication Steps, paramaters, and responses are defined at https://developer.spotify.com/web-api/authorization-guide/
# Visit this url to see all the steps, parameters, and expected response. 
app = Flask(__name__)
app.secret_key = os.urandom(24)

 #  Client Keys
CLIENT_ID = ""
CLIENT_SECRET = ""
 # Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)
 # Server-side Parameters
CLIENT_SIDE_URL = "http://www.spotify-lyrics.com"
PORT = 80
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "user-read-currently-playing"
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

@app.route('/favicon.ico') 
def favicon(): 
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/")
def index():
    return render_template("main-v1.html")
@app.route("/login")
def login():
    # Auth Step 1: Authorization
    url_args = "&".join(["{}={}".format(key,urllib.parse.quote(val)) for key,val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)
@app.route("/callback/q")
def callback():
    # Auth Step 4: Requests refresh and access tokens
    session['auth_token'] = request.args['code']
    session['code_payload'] = {
        "grant_type": "authorization_code",
        "code": str(session['auth_token']),
        "redirect_uri": REDIRECT_URI
    }
    base = "{}:{}"
    format_client = base.format(CLIENT_ID,CLIENT_SECRET)
    base64encoded = base64.urlsafe_b64encode(format_client.encode()).decode()
    session['headers'] = {"Authorization": "Basic {}".format(base64encoded)}
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=session['code_payload'], headers=session['headers'])
     # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    session["access_token"] = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]
     # Auth Step 6: Use the access token to access Spotify API
    session['authorization_header'] = {"Authorization":"Bearer {}".format(session["access_token"])}
    
    return redirect("/lyrics")
    
@app.route("/sendtoken")
def sendToken():
    return json.dumps(session['access_token'])

@app.route("/lyrics")
def displayLyrics():
    try:
        return render_template("lyrics-v1.html")#,token=str(session["access_token"]))
    except Exception:
        return redirect("/login")
def lyricsLink(track,artist,website):

        track +=  " " + artist + ' ' + website
        name = urllib.parse.quote_plus(track)

        hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11'
            '(KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}

        url = 'http://www.google.com/search?q=' + name

        result = requests.get(url, headers=hdr).text
        if website == 'azlyrics':
            link_start = result.find('https://www.azlyrics.com')
        else:
            link_start = result.find('http://www.metrolyrics.com')
        link_end = result.find('.html', link_start + 1)
        link = result[link_start:link_end +5]
        return link

def getLyrics(track,artist):
    try:
        s = Song(track,artist)
        if not s.lyrics:
            azLink = lyricsLink(track,artist, 'azlyrics')
            return "no lyrics not found on metrolyrics redirect to azlyrics", azLink
        return s.lyrics
    except KeyError:
        metLink = lyricsLink(track,artist,'metrolyrics')
        try:
            s = Song(url=metLink)
            return s.lyrics
        except AttributeError:
            return "could not find lyrics:("

@app.route('/reciever', methods = ['POST'])
def getTrackInfo():
    session['postTrack'] = request.form['trackName']
    session['postArtist'] = request.form['artistName']
    session['lyrics'] = getLyrics(session['postTrack'],session['postArtist'])

    return "Track: {} Artist: {}".format(session['postTrack'],session['postArtist'])
@app.route('/send')
def sendLyrics():
    try:
        return json.dumps(session['lyrics'])
    except KeyError:
        return json.dumps("lyrics not found on metrolyrics:(")

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/", code=302)

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404-v1.html'), 404

if __name__ == "__main__":
    app.run(debug=True,port=PORT)
