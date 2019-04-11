import sys, os
from . import DIRECTORY

# Function for printing the help message.
def print_help_message():
    with open(os.path.join(DIRECTORY, "about", "usage.txt")) as f:
        print(f.read())

# If no arguments were provided, give the usage.
if len(sys.argv) <= 2:
    print_help_message()
    exit()

import sys, os

# If no arguments were provided, give the usage.
if len(sys.argv) < 2:
    print("Usage:")
    print("  python -m "+os.path.basename(os.path.dirname(os.path.abspath(__file__)))+
          " <file_name> [--online] [--no-appendix] [--no-show] [output folder]")
    print()
    print("    Default behavior is to use local resources for displyaing HTML\n"+
          "    and to output in the current working director.")
    print()
    print("    If the '--online' argument is given, resource files are internet-accessible and nonlocal.")
    print()
    print("    If the '--no-appendix' argument is given, the appendix section is removed from the html document.")
    print()
    print("    If the '--no-show' argument is given, the resulting HTML file is *not* opened in a browser upon completion.")
    print()
    print("    If the [output directory] argument is given, output file is saved in that directory.")
    print()
    exit()


use_local = True
no_appendix = False
no_show = False
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
    # Check for an output folder
    if len(sys.argv) > 2:
        output_folder = sys.argv[-1]

# Get the path of the input file, then parse and save it.
path = os.path.abspath(sys.argv[1])

from txt_to_html import parse_txt
parse_txt(path, output_folder, use_local=use_local, 
          appendix=(not no_appendix), show=(not no_show))
