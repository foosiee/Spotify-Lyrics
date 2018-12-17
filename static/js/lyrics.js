let lastTrack = ''

function noTrack(){
    emptyDOM("#scriptTrack");
    emptyDOM("#scriptArtist");
    emptyDOM("#lyricBody");
    editDOM("#scriptTrack", "Nothing is playing");
    editDOM("#lyricBody", "nadda");
}

function notPlaying(){
    emptyDOM("#scriptTrack");
    emptyDOM("#lyricBody");
    editDOM("#lyricBody","nadda");
    editDOM("#scriptTrack", "Nothing Playing")
    emptyDOM("#scriptArtist");
}

function emptyDOM(identity){
    $(identity).empty();
}

function editDOM(identity, text){
    $(identity).append(text);
}

function isEmpty(obj) {
    for(var key in obj) {
    if(obj.hasOwnProperty(key))
        return false;
    }
    return true;
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
    $.get("/send", function(data) {
    lyrics = $.parseJSON(data);
    lyrics = lyrics.replace(/\n/g, "<br />");
    if(lyrics == ""){
        lyrics = "no lyrics found :(";
    }
    console.log(lyrics);
    emptyDOM("#lyricBody");
    editDOM("#lyricBody",lyrics)
    console.log("recieved")
    })
}

function sendData(track,artist){
    console.log("Sending data");
    $.post("/reciever", {
    trackName: track,
    artistName: artist
    });
    console.log("sent");
}

function extractTrack(track){
console.log(track);
trackName = track.item.name;
artistName = track.item.artists[0].name;
trackFormat = format(trackName);
console.log(trackFormat,artistName);
if (lastTrack != trackName){
    sendData(trackFormat,artistName);
    emptyDOM("#scriptTrack");
    emptyDOM("#scriptArtist");
    editDOM("#scriptTrack","Currently playing: " + trackName);
    editDOM("#scriptArtist", "By: " + artistName);
    setTimeout(recieveData,1000);
}
lastTrack = trackName
}
function getTrack(token){
    empty = false;
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
        extractTrack(data);
    })
    .catch(err => {
        console.log(err);
        noTrack();
    })
}
token = getToken();
getTrack(token);
setInterval(function() {
    getTrack(token);
}, 5000);