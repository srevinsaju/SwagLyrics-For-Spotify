import os

from SwSpotify import spotify, SpotifyNotRunning
from flask import Flask, render_template

from swaglyrics import SameSongPlaying
from swaglyrics.swaglyrics import SwagLyrics


# Define custom Swaglyrics subtype to defer __init__
class SwagLyricsWebApp(SwagLyrics):
    def __init__(self):  # noqa:
        # the super init is moved to init() method so that
        # it can be called later
        # this is to workaround the Flask implementation
        # as creating flask subclasses are a mess
        pass

    def init(self):
        super().__init__()


sl = SwagLyricsWebApp()  # initialize an empty subclass of SwagLyrics

# initialize flask app and set attributes
app = Flask(__name__)
app.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app.static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

song = None
artist = None


@app.route('/')
def tab() -> str:
    # format lyrics for the browser tab template
    global song, artist
    try:
        song, artist = spotify.current()
        current_lyrics = sl.get_lyrics(song, artist)
    except SpotifyNotRunning:
        current_lyrics = ('Nothing playing at the moment.', '')

    return render_template('lyrics.html', lyrics=current_lyrics, song=song, artist=artist)


@app.route('/songChanged', methods=['GET'])
def song_changed() -> str:
    # to refresh lyrics when song changed
    global song, artist
    try:
        if spotify.current() == (song, artist):
            raise SameSongPlaying
        else:
            return 'yes'
    except (SpotifyNotRunning, SameSongPlaying):
        return 'no'


def swaglyrics_web_init(port=None):
    sl.init()  # call SwagLyrics.__init__
    app.run(port=port)


if __name__ == '__main__':
    swaglyrics_web_init()
