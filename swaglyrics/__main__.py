import argparse
import sys
import time

import requests
from SwSpotify import spotify, SpotifyNotRunning

from swaglyrics import SameSongPlaying, __version__ as version, backend_url
from swaglyrics.cli import clear
from swaglyrics.swaglyrics import SwagLyrics
from swaglyrics.tab import app, swaglyrics_web_init

from swaglyrics.config.config import ConfigManager


cfgmgr = ConfigManager()


def check_new_version():
    try:
        v = requests.get(f'{backend_url}/version')
        ver = v.text
        if ver > version:
            print("New version of SwagLyrics available: v{ver}\nPlease update :)".format(ver=ver))
            print("To update, execute \npip install -U swaglyrics\n")
    except requests.exceptions.RequestException:
        pass


def show_tab() -> None:
    """
    Opens a web browser tab with Swaglyrics flask web app
    :return:
    :rtype:
    """
    from threading import Timer
    from webbrowser import open
    print('Firing up a browser tab!')
    port = 5042  # random
    url = f"http://127.0.0.1:{port}"
    Timer(1.25, open, args=[url]).start()
    app.run(port=port)


def show_cli(make_issue: bool = False) -> None:
    try:
        song, artist = spotify.current()  # get currently playing song, artist
        print(lyrics(song, artist, make_issue))
        print('\n(Press Ctrl+C to quit)')
    except SpotifyNotRunning as e:
        print(e)
        print('\n(Press Ctrl+C to quit)')
        song, artist = None, None
    while True:
        # refresh every 5s to check whether song changed
        # if changed, display the new lyrics
        try:
            try:
                if spotify.current() == (song, artist):
                    raise SameSongPlaying
                else:
                    song, artist = spotify.current()
                    clear()
                    print(lyrics(song, artist, make_issue))
                    print('\n(Press Ctrl+C to quit)')
            except (SpotifyNotRunning, SameSongPlaying):
                time.sleep(5)
        except KeyboardInterrupt:
            print('\nSure boss, exiting.')
            sys.exit()


def main() -> None:
    # print(r"""
    #  ____                     _               _
    # / ___|_      ____ _  __ _| |   _   _ _ __(_) ___ ___
    # \___ \ \ /\ / / _` |/ _` | |  | | | | '__| |/ __/ __|
    #  ___) \ V  V / (_| | (_| | |__| |_| | |  | | (__\__ \
    # |____/ \_/\_/ \__,_|\__, |_____\__, |_|  |_|\___|___/
    #                     |___/      |___/
    # 	""")
    # print('\n')

    parser = argparse.ArgumentParser(
        description="Get lyrics for the currently playing song on Spotify. Either --tab or --cli is required.")

    parser.add_argument('-t', '--tab', action='store_true', help='Display lyrics in a browser tab.')
    parser.add_argument('-c', '--cli', action='store_true', help='Display lyrics in the command-line.')
    parser.add_argument('-n', '--no-issue', action='store_false', help='Disable issue-making on cli.')
    parser.add_argument('-u', '--update-check', action='store_true', help='Force check for updates.')
    args = parser.parse_args()

    if args.tab or args.cli:
        check_new_version()
        if args.update_check:
            cfgmgr.update_database()

    if args.tab:
        show_tab()
    elif args.cli:
        make_issue = args.no_issue
        show_cli(make_issue)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
