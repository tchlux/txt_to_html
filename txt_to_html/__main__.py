import sys, os
from . import DIRECTORY

# Function for printing the help message.
def print_help_message():
    print('''

USAGE:
  python -m txt_to_html <source text file> [--online] [--no-appendix] [--no-show] [--no-justify] [output folder]

This outputs a <source text file>.html ready to be viewed in a browser.

Default behavior is to use local resources for displyaing HTML and to output in the current working director.

If the `--online` argument is given, resource files are internet-accessible and nonlocal.

If the `--no-appendix` argument is given, the appendix section is removed from the html document.

If the `--no-show` argument is given, the resulting HTML file is *not* opened in a browser upon completion.

If the `--no-justify` argument is given, the resulting HTML file has body text which will *not* be justified (layout that normalizes line width).

If the `[output directory]` argument is given, output file is saved in that directory, which *must* already exist.
    ''')



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


# import pprofile
# # Deterministic profiler
# p = pprofile.Profile()
# with p():
#     from txt_to_html import parse_txt
#     parse_txt(path, output_folder, use_local=use_local,
#               justify=(not no_justify), show=(not no_show),
#               appendix=(not no_appendix))
# # p.print_stats()
# with open("/Users/thomaslux/Desktop/pprofile-results.out", "w") as f:
#     p.callgrind(f)


# def run():
#     from txt_to_html import parse_txt
#     parse_txt(path, output_folder, use_local=use_local,
#               justify=(not no_justify), show=(not no_show),
#               appendix=(not no_appendix))
# import cProfile
# cProfile.run("run()", sort="time")
