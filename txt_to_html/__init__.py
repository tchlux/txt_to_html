# Get the version number from the setup file
import os

DIRECTORY = os.path.dirname(os.path.abspath(__file__))
ABOUT_DIR = os.path.join(DIRECTORY, "about")
with open(os.path.join(ABOUT_DIR,"version.txt")) as f:
    __version__ = f.read().strip()

# Load the module contents from the python file txt_to_html
from .txt_to_html import parse_txt, DOC_STRING

# Assign the documentation for this package from that file.
__doc__ = DOC_STRING

# Only encourage usage of the "parse_txt" function from outside this package.
__all__ = [parse_txt]
