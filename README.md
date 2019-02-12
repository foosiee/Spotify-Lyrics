# Spotify-Lyrics

a python flask App for obtaining the users current track and displaying its lyrics on the browser. 

## login
<img width="1304" alt="screen shot 2019-02-11 at 7 52 08 pm" src="https://user-images.githubusercontent.com/33300547/52603841-8c643580-2e36-11e9-995c-0e3f95023c7a.png">

## authorization
- Spotify-Lyrics follows Spotify's [authorization code flow](https://developer.spotify.com/documentation/general/guides/authorization-guide/).
- scope of authorization is for user-read-currently-playing
- a user authorization token is generated on the server and sent client side as json

## getting lyrics
- with the token now on the clients machine the code makes a request to the spotify api with the token
```
 fetch('https://api.spotify.com/v1/me/player/currently-playing', {
headers: {
    'Authorization': `Bearer ${token}`
}
```
- this api call will return a json object that contains all information to obtain the lyrics to the song
  - track
  - artist
- this information is then sent back server side
#### getting lyrics case 1 
- to obtain lyrics Spotify-Lyrics uses python package [tswift](https://github.com/brenns10/tswift)
- tswift is a very simple metrolyrics "api" to retrieve lyrics
- the first attempt to get lyrics is very simple
```
s = Song(track,artist)
```
- the song object from tswift is instantiatiated with the track and artist sent up from the client
- simply return s's lyrics property
```
return s.lyrics
````
- send lyrics back to client as json

#### getting lyrics case 2
- tswifts song object sometimes will not find the lyrics with track and artist arguments 
- to counter this you can provide a link to the song object
- to do this a google search is done using the [requests package](https://github.com/kennethreitz/requests)
- program finds first instance of metrolyrics
```
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
```

- Song object is created and lyrics are returned in a similar fashion
#### case 3
- if both these methods do not work
- we will generate a link to azlyrics 
- this link is generated in the same method as the metrolyrics link
- this link is sent down to the client as json

## displaying lyrics
- simple [jquery](https://github.com/jquery/jquery) is used

## result

<img width="1237" alt="screen shot 2018-12-05 at 5 08 54 pm" src="https://user-images.githubusercontent.com/33300547/49547617-2ea0f380-f8b1-11e8-97c8-0d46f095add3.png">

## bugs / additions
- website fails if the user refreshs the page because token is lost upon refresh
  - possible solution: send token down in a template
- need to implent refresh tokens so the users session is not over after an hour
