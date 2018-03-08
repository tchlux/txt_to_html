import sys, os

# If no arguments were provided, give the usage.
if len(sys.argv) < 2:
    print("Usage:")
    print("  python -m "+os.path.basename(os.path.dirname(os.path.abspath(__file__)))+" <file_name> [output folder] [--online]")
    print()
    print("    Default behavior is to use local resources for displyaing HTML\n"+
          "    and to output in the current working director.")
    print()
    print("    If the [output directory] argument is given, output file is saved in that location.")
    print()
    print("    If the '--online' argument is given, resource files are internet-accessible and nonlocal.")
    exit()

use_local = True
output_folder = ""
# Get (if given) the command line arguments (output folder, online)
if (len(sys.argv) >= 3):
    if (sys.argv[2] == "--online"): 
        use_local = False
    else:
        output_folder = sys.argv[2]
        if ((len(sys.argv) >= 4) and (sys.argv[3] == "--online")):
            use_local = False

# Get the path of the input file, then parse and save it.
path = os.path.abspath(sys.argv[1])

from txt_to_html import parse_txt
parse_txt(path, output_folder, use_local=use_local)
