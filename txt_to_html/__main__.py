import sys, os
from . import DIRECTORY

# Function for printing the help message.
def print_help_message():
    with open(os.path.join(DIRECTORY, "about", "usage.txt")) as f:
        print(f.read())

print("sys.argv:",sys.argv)

# If no arguments were provided, give the usage.
if len(sys.argv) <= 1:
    print_help_message()
    exit()

use_local = True
no_appendix = False
no_show = False
no_justify = False
output_folder = ""
# Get (if given) the command line arguments (output folder, online)
if (len(sys.argv) >= 3):
    # Check for "online"
    use_local = "--online" not in sys.argv
    if (not use_local): sys.argv.remove("--online")
    # Check for "no appendix"
    no_appendix = "--no-appendix" in sys.argv
    if no_appendix: sys.argv.remove("--no-appendix")
    # Check for "no show"
    no_show = "--no-show" in sys.argv
    if no_show: sys.argv.remove("--no-show")
    # Check for "justify"
    no_justify = "--no-justify" in sys.argv
    if no_justify: sys.argv.remove("--no-justify")
    # Check for an output folder
    if len(sys.argv) >= 3:
        output_folder = sys.argv[-1]

# Get the path of the input file, then parse and save it.
path = os.path.abspath(sys.argv[1])

from txt_to_html import parse_txt
parse_txt(path, output_folder, use_local=use_local,
          justify=(not no_justify), show=(not no_show),
          appendix=(not no_appendix))
