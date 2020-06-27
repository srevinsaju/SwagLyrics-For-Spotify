"""
Tools used only for command line interface
"""

import os


def clear() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')  # clear command window
