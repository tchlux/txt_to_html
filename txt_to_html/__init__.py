# Get the version number from the setup file
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from setup import read
__version__ = read("version.txt")[0]
sys.path.pop(-1)

# Load the module contents from the python file txt_to_html
from .txt_to_html import *
