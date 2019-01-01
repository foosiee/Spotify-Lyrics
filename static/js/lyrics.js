let lastTrack = ''

function podcast(){
    emptyDOM("all");
    editDOM("#scriptTrack", "Listening to podcast");
    editDOM("#lyricBody", "no lyrics or annotation");
 }

function noTrack(){
    emptyDOM("all")
    editDOM("#scriptTrack", "Nothing is playing");
    editDOM("#lyricBody", "nadda");
 }

function emptyDOM(identity){
    if(identity == "all"){
        emptyDOM("#scriptTrack");
        emptyDOM("#scriptArtist");
        emptyDOM("#lyricBody");
     }
    $(identity).empty();
 }
 
 function editDOM(identity, text){
    $(identity).append(text);
 }

function format(track){
    track = track.split('-')[0];
    track = track.replace(/[^\w\s]/gi, '');
    track = track.toLowerCase();
 
    return track
 }

function getToken(){
    console.log("getting token");
    $.get("/sendtoken", function(data){
       token = $.parseJSON(data);
       console.log("token recieved: " + token);
       getTrack(token);
       return token;
    })
 }
function recieveData(){
        console.log("Recieving data")
        $.get("/send", function(data) {
        lyrics = $.parseJSON(data);
        lyrics = lyrics.replace(/\n/g, "<br />");
        if(lyrics == ""){
            lyrics = "no lyrics found :(";
        }
        console.log(lyrics)
        editDOM("#lyricBody",lyrics)
        })
    }
function sendData(track,artist){
        console.log("Sending data");
        $.post("/reciever", {
        trackName: track,
        artistName: artist
        })
    }
function extractTrack(track){
    console.log(track);
    trackName = track.item.name;
    artistName = track.item.artists[0].name;
    trackFormat = format(trackName);
    console.log(trackFormat,artistName);
    if (lastTrack != trackName){
        emptyDOM("all");
        editDOM("#scriptTrack","Currently playing: " + trackName);
        editDOM("#scriptArtist", "By: " + artistName);
        sendData(trackFormat,artistName);
        setTimeout(recieveData,2500);
    }
lastTrack = trackName
    }
function getTrack(token){
        console.log(token);
        fetch('https://api.spotify.com/v1/me/player/currently-playing', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => {
            return response.json();
        })
        .then(data => {
            // if(data.currently_playing_type == "track"){
            extractTrack(data);
            //  }
            //  else{
            //     podcast();
            //  }
        })
        .catch(err => {
            console.log(err);
            noTrack();
      })
    }
token = getToken();
console.log(token);
getTrack(token);
setInterval(function() {
    getTrack(token);
}, 5000);