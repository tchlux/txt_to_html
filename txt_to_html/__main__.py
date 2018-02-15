import sys, os
from txt_to_html import parse_txt

# If no arguments were provided, give the usage.
if len(sys.argv) < 2:
    print("Usage:")
    print("  python -m "+os.path.basename(os.path.dirname(os.path.abspath(__file__)))+" <file_name>")
    exit()

# Get (if given) the output folder
if (len(sys.argv) == 3):
    output_folder = sys.argv[2]
else:
    output_folder = ""

# Get the path of the input file, then parse and save it.
path = os.path.abspath(sys.argv[1])
parse_txt(path, output_folder)
