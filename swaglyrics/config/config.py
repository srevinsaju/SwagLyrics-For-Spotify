"""
GUISCRCPY by srevinsaju
Get it on : https://github.com/srevinsaju/guiscrcpy
Licensed under GNU Public License

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import json
import os
import time

import requests

from swaglyrics import backend_url
from swaglyrics.platform import platform


class ConfigManager:
    def __init__(self, mode='w'):
        self.os = platform.System()
        self.cfgpath = self.os.cfgpath()
        self.paths = self.os.paths()
        self.config = ""
        self.cfgfile = 'unsupported.txt'

    def init(self):
        self.check_file()

    def set_config(self, x):
        self.config = x

    def get_config(self):
        return self.config

    def get_cfgpath(self):
        return self.cfgpath

    def read_file(self):
        with open(os.path.join(self.cfgpath, self.cfgfile), 'r') as f:
            try:
                last_updated = float(f.readline())
                if not time.time() - last_updated < 86400:  # 86400 seconds in a day
                    self.update_database()
            except ValueError:  # would occur if first line string, on initial versions of unsupported.txt
                self.update_database()
                self.update_database()

        with open(os.path.join(self.cfgpath, self.cfgfile), 'r') as f:
            config = f.read()
        self.set_config(config)

    def append_data(self, data):
        with open(os.path.join(self.cfgpath, self.cfgfile), 'a') as f:
            f.write(data)

    def update_database(self):
        print('Updating unsupported.txt from server.')
        with open(os.path.join(self.cfgpath, self.cfgfile), 'w') as f:
            try:
                unsupported_songs = requests.get(f'{backend_url}/master_unsupported')
                last_updated = time.time()
                f.write(f'{last_updated}\n')
                f.write(unsupported_songs.text)
                print("Updated unsupported.txt successfully.")
            except requests.exceptions.RequestException as e:
                print("Could not update unsupported.txt successfully.", e)

    def check_file(self):
        if not os.path.exists(self.cfgpath):
            os.mkdir(self.cfgpath)
        if not os.path.exists(os.path.join(self.cfgpath, self.cfgfile)):
            self.update_database()
        self.read_file()

    def reset_config(self):
        os.remove(os.path.join(self.get_cfgpath(), self.cfgfile))
        return True