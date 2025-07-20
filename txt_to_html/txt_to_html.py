'''

                      txt_to_html


This module provides a text file parser that uses a heirarchical
grammar to parse "markdown" style text files into HTML documents.

LINE STARTS:
  New lines ---------> new paragraphs
  Spaces ------------> indentation
  "#+" --------------> Header levels (number of '#' is the level)
  "-" ---------------> unordered lists
  "1)" --------------> ordered lists
  "|" ---------------> table entries
  "----(-)*" --------> divider
  "====(=)*" --------> marks the rest of the document as a bibtex bibliography
  "^^^^(^)*" --------> new page (on print)
  "!+" --------------> new title
  "{{<path>}}" ------> include external file, supports [.png, .jpeg, .jpg, .html]
  "%%+" -------------> ignore rest of line (comments in file)

ANYWHERE:
  "((<footnote>))" --> footnote in line (will be in appendix as well)
  "[[<reference>]]" -> reference key in the bibliography
  "$<math>$" --------> in line math
  "$$<math>$$" ------> new line (centered) math
  "*<text>*" --------> italics
  "**<text>**" ------> bold
  "***<text>***" ----> underline
  "****<text>****" --> monospace
  "`<text>`" --------> monospace
  "@@<header>@@" ----> links in document to that header (verbatim name)
  "<< modifier >>" --> direct access to html parent element attribute settings
  "<(0-9)+>" --------> spacer with specified pixel width
  "@{text}{link}@" --> text with a hyperlink
  "{<color>}<text>{<color>} --> make all contained text "color".

USAGE:
  It is recommended that this program be used as a command-line
  utility. Place an alias of the following sort into the appropriate
  shell initialization file:

    alias html="python3 -m txt_to_html"

  Then execute with no arguments to get usage instructions. From
  code, the only externally provided function is called
  `txt_to_html.parse_txt`, see `help` documentation for details.

'''

import os, time

# A mutable string class that prevents copying when passed as an 
# argument. It is not perfectly efficient, as copies of pointers are
# still made, but it's faster than passing large strings.
class MutableString(str):
    # Internally store the data as a list of characters.
    def __init__(self, data):
        if (type(data) != list):
            self.data = list(data)
        else:
            self.data = data
    # Return the Python string representation.
    def __repr__(self):
        return "".join(self.data)
    # Square-bracket access (as in list type)
    def __setitem__(self, index, value):
        self.data[index] = value
    def __getitem__(self, index):
        if type(index) == slice:
            return type(self)(self.data[index])
        return self.data[index]
    def __delitem__(self, index):
        del self.data[index]
    # String-addition is list appending.
    def __add__(self, other):
        self.data.extend(list(other))
    def __len__(self):
        return len(self.data)
    def __str__(self):
        return "".join(self.data)

# Do a truncated print where the middle of long strings is replaced by ...
def INLINE(val, max_len=30):
    string = str(val)
    if (len(string) > max_len):
        string = string[:max_len//2] + " ... " + string[-max_len//2:]
    return [string]

# Print the type of a class (truncated to last component)
def TYPE(val):
    return INLINE( str(type(val)).split(".")[-1].split("'")[0] )

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
MAX_REGEX_LEN = 100
LAST_PRINT_TIME = time.time()
CHARS_PARSED = 0
UPDATE_FREQ_SEC = .1
TITLE = "Notes"
DESCRIPTION = ""
AA_BEGIN = "       - "
AUTHORS_AND_AFFILIATION = [
    # ("Thomas Lux: https://www.linkedin.com/in/thomas-ch-lux", "thomas.ch.lux@gmail.com"),
]

RESOURCE_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),"resources")
USE_LOCAL = True
FOUND_NOTE = False

# Format the author and affiliation block appropriately, return in
# dictionary to be used as the **kwargs of formatting HTML.
def FORMAT_AUTHORS():
    authors = ""
    affils = ""
    for auth, aff in AUTHORS_AND_AFFILIATION:
        authors += AA_BEGIN + auth + "\n"
        affils += AA_BEGIN + aff + "\n"
    return dict(authors=authors, affiliations=affils)

# Default bibliography block
BIBLIOGRAPHY = '''
<script type="text/bibliography">
</script>
'''

# Default appendix block
APPENDIX = '''
<dt-appendix>
</dt-appendix>
'''

JUSTIFY_CSS = '''
      dt-article p {
        text-align: justify;
      }
'''


def HTML(use_local=USE_LOCAL, resource_folder=RESOURCE_FOLDER):
    print(f"Formatting HTML {'' if use_local else 'not '}using local files and resources.")

    # Decide which HTML sources to use based on "local" or "not local".
    source_format = dict(
        local_start     = ""     if use_local else "<!--",
        local_end       = ""     if use_local else "-->",
        online_start    = "<!--" if use_local else "",
        online_end      = "-->"  if use_local else "",
        resource_folder = resource_folder,
    )

    # Source files for distill
    distill_source = '''
    <!-- Include Distill -->
    <!-- <script src="https://distill.pub/template.v1.js"></script> -->
    {online_start} <script src="https://tchlux.github.io/documents/distill.template.v1.no-banner.js"></script> {online_end}
    {local_start} <script src="{resource_folder}/distill.template.v1.no-banner.js"></script> {local_end}
    '''.format(**source_format)

    # Source files for mathjax
    mathjax_source = '''
    <!-- Include MathJax -->
    {online_start} <script type="text/javascript" async src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.2/MathJax.js?config=TeX-MML-AM_CHTML"> </script> {online_end}
    {local_start} <script type="text/javascript" async src="{resource_folder}/MathJax-2.7.2/MathJax.js?config=TeX-AMS-MML_HTMLorMML,local/local"></script> {local_end}
    '''.format(**source_format)

    # Source files for bootstrap
    bootstrap_source = '''
    <!-- Include bootstrap stylesheet -->>
    {online_start} <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/css/bootstrap.min.css"> {online_end}
    {online_start} <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script> {online_end}
    {online_start} <script type="text/javascript" rel="stylesheet" src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/js/bootstrap.min.js"></script> {online_end}
    <!-- Include bootstrap javascript (and dependency jquery) -->>
    {local_start} <link rel="stylesheet" href="{resource_folder}/bootstrap.min.css"> {local_end}
    {local_start} <script type="text/javascript" src="{resource_folder}/jquery.min.js"></script> {local_end}
    {local_start} <script type="text/javascript" src="{resource_folder}/bootstrap.min.js"></script> {local_end}
    '''.format(**source_format)

    # Default HTML
    html = '''
    <!doctype html>
    <meta charset="utf-8">

    %s
    %s
    %s

    <!-- Script for setting up the author block -->
    <script type="text/front-matter">
      title: {frontmatter_title}
      description: {frontmatter_description}
      authors:
{authors}
      affiliations:
{affiliations}
    </script>

    <style type="text/css">

{justify}

      dt-article ol, dt-article ul {{
        padding-left: 50px;
      }}

      dt-article ul {{
        list-style: none;
      }}

      dt-article h2 {{
        border-bottom: 1px solid #aaa;
      }}

      dt-article h3 {{
        font-style: normal;
      }}

      dt-article h4 {{
        font-size: 12pt;
      }}

      dt-article li {{
        margin-bottom: 10px;
      }}

      ul li:before {{
        content: "–  ";
        margin-left: -1em
      }}

      td {{
        padding-left: 10px !important;
        padding-right: 10px !important;
        padding-top: 7px !important;
        padding-bottom: 7px !important;
        line-height: 1.3 !important;
      }}

      p.caption {{
        line-height: 1.3;
        font-family: sans-serif;
        font-size: 15px;
        text-align: center;
        color: #777;
        margin-top: -30px;
        padding-top: 0px;
        padding-left: 30px;
        padding-right: 30px;
      }}

    span.header {{
      display: block;
      height: 3vh;
      margin-top: -3vh;
      visibility: hidden;
    }}

    span.caption {{
      display: block;
      height: 65vh;
      margin-top: -65vh;
      visibility: hidden;
    }}

    .jump {{
      color: #333;
      border-bottom: 1px solid #eee;
    }}

    .jump:hover {{
      color: #888;
      border-bottom: 1px dotted #eee;
    }}

    </style>

    <dt-article>
    <h1>{title}</h1>
    <p>{description}</p>
    <dt-byline></dt-byline>

    {body}

    </dt-article>

    {appendix}

    {bibliography}

    {notes}
    '''%(distill_source, mathjax_source, "") #bootstrap_source

    return html


NOTES = r'''
<!--
     ============================================= 
          DISTILL PROPER USAGE AND FORMATTING      
     ============================================= 

        Article Foundation (can use h2 for description)    
    =======================================================
    <dt-article>
      <h1> [title text] </h1>
      <p> [description text] </p>
      <dt-byline></dt-byline>
      [article content]
    </dt-article>
    <dt-appendix>
    </dt-appendix>
    <script type="text/bibliography">
      @article{,
      title={},
      author={},
      journal={},
      year={},
      url={}
      }
      ...
    </script>

        Body and Headers    
    ========================
    <p></p>
    <h1></h1>
    <h2></h2>
    <h3></h3>
    <h4></h4>

        Citations    
    =================
    <dt-cite key="[key name]"></dt-cite>

        Code (use block for multiple lines)    
    ===========================================
    <dt-code block language="[language]">
      [code]
    </dt-code>

        Footnotes    
    =================
    <dt-fn> [text] </dt-fn>

        Lists (unordered uses <ul> instead)    
    ===========================================
    <p>
      <ol>
	<li> [entry text]
      </ol>
    </p>

        Math    
    ============
    \( [inline math text] \)
    $$ [newline math text]  $$

        Styling    
    ===============
    <i> [italics] </i> 
    <b> [bold] </b>
    <br> [line break]
    <font color="[color]"> [colored text] </font>

        Tables    
    ==============
    <table>
      <tr> [table row]
	<td> [table column] </td> ...
      </tr>
    </table>

         Custom Widths for Tables     
    ==================================
    <style type="text/css">
      td {
        width: 200px;
        padding: 0px 0px 0px 50px;
        background-color: #eee;
      }
    </style>


    =======================
        EXAMPLE ARTICLE
    =======================

    <!doctype html>
    <meta charset="utf-8">
    <script src="https://distill.pub/template.v1.js"></script>

    <script type="text/front-matter">
      title: "Article Title"
      description: "Description of the post"
      authors:
      - Chris Olah: http://colah.github.io
      - Shan Carter: http://shancarter.com
      affiliations:
      - Google Brain: http://g.co/brain
      - Google Brain: http://g.co/brain
    </script>

    <dt-article>
      <h1>Hello World</h1>
      <h2>A description of the article</h2>
      <dt-byline></dt-byline>
      <p>This is the first paragraph of the article.</p>
      <p>We can also cite <dt-cite key="gregor2015draw"></dt-cite> external publications.</p>
    </dt-article>

    <dt-appendix>
    </dt-appendix>

    <script type="text/bibliography">
      @article{gregor2015draw,
      title={DRAW: A recurrent neural network for image generation},
      author={Gregor, Karol and Danihelka, Ivo and Graves, Alex and Rezende, Danilo Jimenez and Wierstra, Daan},
      journal={arXivreprint arXiv:1502.04623},
      year={2015},
      url={https://arxiv.org/pdf/1502.04623.pdf}
      }
    </script>

-->

'''

# Example of how to format the HTML document
# 
# HTML().format( frontmatter_title="", frontmatter_description, 
#                title="", description="", authors="", 
#                affiliations="", body="", bibliography="", 
#                appendix="", notes="")


# ====================================================================
# 
#                       regex C library
# 
# A fast regular expression matching code for Python, built on top of
# the 'regex.c' library. The main function provided here is:
# 
#   regex_match(regex, string) -> (start, end) or None or RegexError.
# 
# Regex language can be found in 'regex.c' file.


# Import ctypes for loading the underlying C regex library.
import ctypes
# --------------------------------------------------------------------
#                 Darwin (macOS) / Linux (Ubuntu) import
clib_bin = os.path.join(os.path.dirname(os.path.abspath(__file__)), "regex.so")
clib_source = os.path.join(os.path.dirname(os.path.abspath(__file__)), "regex.c")
# Import or compile the C file.
try:
    REGEX_CLIB = ctypes.CDLL(clib_bin)
except:
    # Configure for the compilation for the C code.
    c_compiler = "cc"
    compile_command = f"{c_compiler} -O3 -fPIC -shared -o '{clib_bin}' '{clib_source}'"
    # Compile and import.
    os.system(compile_command)
    REGEX_CLIB = ctypes.CDLL(clib_bin)
    # Clean up "global" variables.
    del(c_compiler, compile_command)
del(clib_bin, clib_source)
# --------------------------------------------------------------------

# Exception to raise when errors are reported by the regex library.
class RegexError(Exception): pass

# Given a regular expression in a Unix-like format, translate it to a
# regular experssion that is (roughly) equivalent in the language of
# the `regex.c` library.
def translate_regex(regex, case_sensitive=True):
    # Do substitutions that make the underlying regex implementation
    # behave more like common existing regex packages.
    if (len(regex) > 0):
        # Add a ".*" to the front of the regex if the beginning of the
        # string was not explicitly desired in the match pattern.
        if (regex[0] == "^"): regex = regex[1:]
        elif ((len(regex) < 2) or (regex[0] != ".") or (regex[1] != '*')): 
            regex = ".*" + regex
        # Add a "{.}" to the end of the regex if the end of the string
        # was explicitly requested in the pattern.
        if (regex[-1] == "$"): regex = regex[:-1] + "{.}"
    # Replace all alphebetical characters with token sets that include
    # all cases of that character.
    if (not case_sensitive):
        i = 0
        in_literal = False
        while (i < len(regex)):
            # Check for the beginning of a token set.
            if ((regex[i] == '[') and (not in_literal)):
                in_literal = True
                contains = set()
                missing = set()
            # Handle a currently-active token set.
            elif (in_literal):
                # Check for the end of this token set.
                if (regex[i] == ']'):
                    in_literal = False
                    # Add all the missing characters to this token set.
                    missing = ''.join(sorted(missing.difference(contains)))
                    regex = regex[:i] + missing + regex[i:]
                    # Increment i appropriately.
                    i += len(missing)-1
                # Add the paired-case if we see a cased character.
                elif (regex[i].isalpha()):
                    contains.add(regex[i])
                    if (regex[i].islower()):
                        missing.add(regex[i].upper())
                    else:
                        missing.add(regex[i].lower())
            # Otherwise replace this single character with a token set.
            elif (regex[i].isalpha()):
                if (regex[i].islower()):
                    token_set = f'[{regex[i]}{regex[i].upper()}]'
                else:
                    token_set = f'[{regex[i]}{regex[i].lower()}]'
                regex = regex[:i] + token_set + regex[i+1:]
                i += len(token_set)-1
            # Increment to the next token.
            i += 1
    # Return the now-prepared regular expression.
    return regex

# Translate 'start' and 'end' values that are returned by the `regex.c`
# library, raising appropriate errors as defined by the library.
def translate_return_values(regex, start, end):
    # Return appropriately (handling error flags).
    if (start >= 0): return (start, end)
    elif (start < 0):
        if (end == 0): return None # no match found
        elif (end == -1): return (0, 0) # empty regular expression
        elif ((start == -1) and (end == -5)): return None  # empty string
        elif (end < -1): # error code provided by C
            err = f"Invalid regular expression (code {-end})"
            if (start < -1):
                start -= sum(1 for c in str(regex,"utf-8") if c in "\n\t\r\0")
                err += f", error at position {-start-1}.\n"
                err += f"  {str([regex])[1:-1]}\n"
                err += f"  {(-start)*' '}^"
            else: err += "."
            raise(RegexError(err))

# Find a match for the given regex in string.
# 
#   match(regex, string) -> (start, end) or None or RegexError,
# 
# where "regex" is a string defining a regular expression and "string"
# is a string to be searched against. The function will return None
# if there is no match found. If a match is found, a tuple with
# integers "start" (inclusive index) and "end" (exclusive index) will
# be returned. If there is a problem with the regular expression,
# a RegexError will be raised.
#
# Some substitutions are made before passing the regular expressions
# "regex" to the "match" function in 'regex.c'. These substitutions
# include:
#
#  - If "^" is at the beginning of "regex", it will be removed (because
#    the underlying library implicitly assumes beginning-of-string.
#  - If no "^" is placed at the beginning of "regex", then ".*" will
#    be appened to the beginning of "regex" to behave like other 
#    regular expression libraries.
#  - If "$" is the last character of "regex", it will be substituted
#    with "{.}", the appropriate pattern for end-of-string matches.
# 
def regex_match(regex, string, **translate_kwargs):
    # Translate the regular expression to expected syntax.
    regex = translate_regex(regex, **translate_kwargs)
    # Call the C utillity.
    #   initialize memory storage for the start and end of a match
    start = ctypes.c_int()
    end = ctypes.c_int()
    #   convert strings into character arrays
    if (type(regex) == str): regex = regex.encode("utf-8")
    if (type(string) == str): string = string.encode("utf-8")
    c_regex = ctypes.c_char_p(regex);
    c_string = ctypes.c_char_p(string);
    #   execute the C function
    REGEX_CLIB.match(c_regex, c_string, ctypes.byref(start), ctypes.byref(end))
    del(c_regex, c_string, string)
    # Return the values from the C library (translating them appropriately)
    return translate_return_values(regex, start.value, end.value)
# ====================================================================


# Object oriented recursive tree-grammar parsing code

# ====================================================================
#                 Generic Recursive Syntax Parsing Class     
# ====================================================================

NEWLINE = "((\r\n)|\r|\n)"
ON_NEW_LINE = f"^{NEWLINE}"
ESCAPE_CHAR = "^\\"
EOF = "END_OF_ORIGINAL_FILE"
SPECIAL_HTML_CHARS = {"<":"&lt;", ">":"&gt;"}
class UnsupportedExtension(Exception): pass
class IncompleteSyntax(Exception): pass
class MissingFile(Exception): pass
class SyntaxError(Exception): pass
class AuthorError(Exception): pass

# Base class for defining a syntax in text.
class Syntax(list):
    start   = "^."      # The regex / string matching the start of this syntax
    end     = "^"+EOF   # The regex / string matching the end of this syntax
    extra_s = 0         # The number of extra characters matched by "start" regex.
    extra_e = 0         # The number of extra characters matched by "end" regex.
    match   = ""        # The string matched when this Syntax started
    grammar = []        # The grammar for processing this syntax (list of syntaxes)
    closed  = True      # True if this syntax must successfully end
    symmetric = False   # True if this syntax end must equal the start in length
    escapable = False   # True if "ESCAPE_CHAR" can be uesd to escape this syntax
    line_start = False  # True if this syntax must start on a new line
    allow_escape = True # True if escape characters are allowed in this syntax
    return_end = True   # True if the "end" regular expression should be returned
    modifiable = True   # True if "Modifier" class content is allowed to update "pack"
    
    # Function for handling unprocessed strings. If this syntax is
    # supposed to be closed then an error is raised, otherwise the
    # body is returned.
    def not_closed(self, body):
        if self.closed:
            raise(IncompleteSyntax(f"\n\n  {str(type(self))} {str(body)}"))
        else:
            return body, "", ""

    # Function for packing text into HTML (to be overwritten by subclasses)
    def pack(self, text):
        return text

    # Recursive function for rendering output text from nested strings
    # and Syntax objects to produce final processed output text.
    def render(self, spacing="", verbose=False):
        if verbose: print(spacing, "Rendering", TYPE(self), INLINE(self.match))
        text = ""
        modifier = ""
        for el in self:
            if type(el) == str:        text += el
            elif type(el) == Modifier: modifier += el.render(spacing+"  ", verbose)
            else:                      text += el.render(spacing+"  ", verbose)
        # Pack the output, modify if that is allowed
        output = self.pack(text)
        if (self.modifiable and (len(modifier) > 0)):
            # Add the modifier to the element
            output = output.replace(">",f" {modifier}>",1)
            if verbose: print(INLINE(output))
        return output

    # Returns the length of the match at the beginning of a string
    # that fits the "start" regular expression for this syntax.
    def starts(self, string):
        match = regex_match(self.start, str(string))
        if (match is not None): return True, string[match[0]:match[1]-self.extra_s]
        else:                   return False, ""

    # Returns the length of the match at the beginning of a string
    # that fits the "end" regular expression for this syntax.
    def ends(self, string, start):
        match = regex_match(self.end, str(string))
        if (match is not None):
            match = string[match[0]:match[1]-self.extra_e]
            if self.symmetric:
                if (len(start) == len(match)): 
                    return True, (start if self.return_end else "")
                else:
                    return False, ""
            else:
                return True, (match if self.return_end else "")
        else:
            return False, ""

    # Recursive function for processing a string into a Syntax heirarchy.
    def process(self, string, i, start="", spacing="", verbose=False):
        # Get the global variable for the last print time.
        global LAST_PRINT_TIME
        if verbose: print(spacing,"Begin",TYPE(self),INLINE(start))
        # Initialize a new copy of this class to hold contents (and keep match)
        body = type(self)([""])
        body.match = start
        new_line = regex_match(ON_NEW_LINE, str(start)) is not None
        escaped = self.allow_escape and (regex_match(ESCAPE_CHAR, str(start)) is not None)
        if (escaped): start = start[:-1]
        # Initialize remaining length of string (>0 to allow matching "")
        remaining = max(1, len(string)-i)
        # Search the string for the start and end of this syntax
        while remaining > 0:
            # First, check to see if this syntax has ended
            found, end = self.ends(string[i:i+MAX_REGEX_LEN], start)
            if found:
                # If this syntax has completed, return
                if verbose: print(spacing, " End", TYPE(self), INLINE(body))
                return body, str(string[i:i+len(end)]), string[i+len(end):]
            # Check for the beginnings of any sub-syntaxes
            for g, syntax in enumerate(self.grammar):
                # Skip syntax that requires being at the start of a new line
                if (syntax.line_start and (not new_line)): continue
                if (syntax.escapable  and (escaped)): continue
                # Search for the syntax at this part of the string
                found, syntax_start = syntax.starts(string[i:i+MAX_REGEX_LEN])
                if found:
                    assert len(syntax_start) > 0, (
                        "Expected nonzero length 'syntax_start'.\n\n"
                        f" {g} - {type(syntax)}\n"
                        f" Start: {repr(syntax.start)}\n"
                        f" End:   {repr(syntax.end)}\n"
                        f" Extra: {(syntax.extra_s, syntax.extra_e)}\n"
                        f" Match:  {repr(syntax_start)}\n"
                        f" String: {repr(string[i:i+MAX_REGEX_LEN])}"
                    )
                    # Update the global variable if a note was found.
                    if (type(syntax) == Note):
                        global FOUND_NOTE; FOUND_NOTE = True
                    contents, ends_on, string = syntax.process(
                        string[i+len(syntax_start):], 0, syntax_start, 
                        spacing+"  ", verbose)
                    i = 0
                    body.append(contents)
                    # Record whether or not we are currently on a new line
                    new_line = regex_match(ON_NEW_LINE, ends_on) is not None
                    new_line = new_line or (type(body[-1]) == NewLine)
                    # Record whether or not trailing character was ESCAPE_CHAR
                    escaped = self.allow_escape and (
                        regex_match(ESCAPE_CHAR, str(ends_on)) is not None)
                    break
            else:
                # Add string contents appropriately
                if (len(body) == 0) or (type(body[-1]) != str):
                    body.append(string[i])
                else:
                    body[-1] += string[i]
                # Record whether or not we are currently on a new line
                new_line = regex_match(ON_NEW_LINE, string[i]) is not None
                # Allow for the escaping of the escape character
                if not escaped:
                    # Record whether or not we are currently escaping
                    escaped = self.allow_escape and (regex_match(ESCAPE_CHAR, string[i]) is not None)
                    if (escaped): body[-1] = body[-1][:-1]
                else: 
                    # Otherwise, reset the current escaped status
                    escaped = False
                    # Check for special HTML characters that need to be
                    # automatically escaped (if escaping is allowed)
                    if (string[i] in SPECIAL_HTML_CHARS):
                        body[-1] = body[-1][:-1] + SPECIAL_HTML_CHARS[string[i]]
                # Transition string forward by one character
                i += 1
            # Update the stopping condition check
            remaining = len(string) - i
            if ((time.time() - LAST_PRINT_TIME) > UPDATE_FREQ_SEC):
                print(f"{remaining:9d}",end="\r")
                LAST_PRINT_TIME = time.time()
        if verbose:
            print(spacing," End", TYPE(self), INLINE(body))
        # "string" completed without closing this syntax, handle appropraitely
        return self.not_closed(body)
     
# Generic class for containing groups of of syntaxes (body, lists, etc.)
class Block:
    start  = []
    syntax = []
    blocks = []
    before = ""
    after  = ""
    requirements = {}

    # Function for packing text (to be overwritten by subclasses)
    def pack(self, text):
        return self.before + text + self.after

    # Recursive function for rendering output text from nested Syntaxes
    def render(self, body, spacing="", verbose=False):
        if verbose: print(spacing, "Begin", TYPE(self))
        text = ""
        while len(body) > 0:
            next_el = body[0]
            # First try and identify any sub-blocks in the body
            for b in self.blocks:
                if type(next_el) in b.start:
                    rendered_text, body = b().render(body, spacing+"  ", verbose)
                    text += rendered_text
                    break
            else:
                next_el_type = str(type(next_el))
                recognized_syntax = (type(next_el) in self.syntax)
                no_requirement_exists = (next_el_type not in self.requirements)
                requirement_met = no_requirement_exists or self.requirements[next_el_type](next_el)
                # If (this syntax is recognized) AND
                #     (there is not a requirement for the syntax) OR
                #     (the requirement for this syntax is met)
                if recognized_syntax and requirement_met:
                    # Check to see if this is just a string
                    if type(next_el) == str:
                        text += body.pop(0)
                    else:
                        # This syntax is accepted by this block
                        text += (body.pop(0)).render()
                else:
                    # This syntax is not accepted by this block
                    if verbose: 
                        print(spacing, " End (unfinished)", TYPE(self),
                              TYPE(next_el),
                              INLINE(next_el.match if not requirement_met else ""),
                              INLINE([text]))
                    # There was no recognized block nor syntax, return body
                    return self.pack(text), body
        if verbose: print(spacing, " End (finished)", TYPE(self), INLINE(text))
        return self.pack(text), body

# ====================================================================
#                        Grammar Definition     
# ====================================================================

BASE_GRAMMAR = []
LIST_GRAMMAR = []
TABLE_GRAMMAR = []

class Modifier(Syntax):
    start = "^<<" # <<
    end   = "^>>" # >>
    escapable = True

class Math(Syntax):
    start = "^$$*{$}" # $, $$, ...
    end   = "^$$*{$}" # $, $$, ...
    extra_s = 1
    extra_e = 1
    symmetric = True
    escapable = True
    allow_escape = False

    def pack(self, text):
        # Pack with or without new line appropriately.
        if len(self.match) == 1:
            return r"\(" + text + r"\)"
        elif len(self.match) == 2:
            return "\n$$" + text + "$$"

class Ref(Syntax):
    start = "^[[][[]" # [[
    end   = "^]]"     # ]]
    symmetric = True

    def pack(self, text):
        if len(self.match) == 2:
            return "<dt-cite key=\"" + text + "\"></dt-cite>"
        else:
            return text

class Jump(Syntax):
    start = "^@@" # @@
    end   = "^@@" # @@
    grammar = BASE_GRAMMAR
    escapable = True

    def pack(self, text):
        text = text.replace('"','\\"')
        return f'<a class="jump" href="#{text.replace(">","")}">{text}</a>'
        # return f'<a href="#{text}">Section \'<i>{text}</i>\'</a>'

class Link(Syntax):
    start = "^@[{]" # @{
    end   = "^[}]@" # }@
    escapable = True
    allow_escape = True

    def pack(self, contents):
        if "}" not in contents:
            raise(SyntaxError("\n\n  Expected format '@{<text>}{<link>}@', but missing inner '}'."))
        text = contents[:-contents[::-1].index("}")-1]
        if "{" not in contents:
            raise(SyntaxError("\n\n  Expected format '@{<text>}{<link>}@', but missing inner '{'."))
        link = contents[-contents[::-1].index("}")+1:]
        return f"<a href='{link}'>{text}</a>"

class Caption(Syntax):
    start = "^::"               # ::
    end   = f"^::{NEWLINE}" # :: followed by "\r\n", "\r", or "\n"
    extra_e = 1
    line_start = True
    grammar = BASE_GRAMMAR

    def pack(self, contents):
        values = contents.split("::")
        caption = values[0].strip()
        label = values[1].strip() if len(values) > 1 else ""
        # Determine additional attributes based on usage.
        id_str = jump_str = label_str = ""
        if (len(label) > 0):
            id_str = f" id='{label}'"
            jump_str = f"<span class='caption'{id_str}></span>"
            label_str = f"<b>{label}:</b> "
        return f"{jump_str}<p class='caption'{id_str}>{label_str}{caption}</p>"

class External(Syntax):
    start = "^[{][{]" # {{
    end   = "^[}][}]" # }}
    line_start = True
    symmetric = True
    
    def pack(self, path):
        path, height, width = (path.split("|") + ["420px", "100%"])[:3]
        extension = path[-path[::-1].find("."):]
        if extension in {"png","jpg","jpeg","svg"}:
            return f"<p style='margin-top:0; margin-bottom:0;'><img src='{path}' width='{width}' style='margin: 0px 20px 0px 20px; display: inline-block;'></p>"
        elif extension in {"html"}:
            # Try and read the best size for the iframe from the file.
            if os.path.exists(path):
                with open(path) as f:
                    contents = f.read()
                    # Get the 'style' declaration of the first div
                    contents = contents[contents.find("<div"):]
                    contents = contents[contents.find("style="):]
                    # Strip everything after the style declaration
                    contents = contents[:contents.find("class=")]
                    # Get the contents of the style declaration
                    contents = contents[contents.find('"')+1:]
                    contents = contents[:contents.find('"')]
                    # Set the default width and height, but check for declared
                    if ("height" in contents):
                        # Retreive the height from the style
                        new_height = contents[contents.index("height:") + len("height:"):]
                        new_height = new_height[:new_height.index(";")]
                        # If it's in pixels, add a 20 pixel pad
                        if ("px" in new_height):
                            new_height = new_height.replace("px","")
                            height = str(float(new_height.strip()) + 20) + "px"
                        # Otherwise, use the default height
                    if ("width" in contents):
                        # Retreive the width from the style
                        new_width = contents[contents.index("width:") + len("width:"):]
                        new_width = new_width[:new_width.index(";")]
                        # If it's in pixels, add a 10 pixel pad
                        if ("px" in new_width):
                            new_width = new_width.replace("px","")
                            width = str(float(new_width.strip()) + 10) + "px"
            iframe_style = f"left: 0; top: 0; position: absolute; height: 100%; width: {width};"
            return f"<p style='position: relative; height: {height};'><iframe src='{path}' frameBorder='0' style='{iframe_style}'></iframe></p>"
        else:
            raise(UnsupportedExtension(f"\n\n  External files with extension '{extension}' are not supported."))

class Spacer(Syntax):
    start = "^<[0123456789][0123456789]*>" # <1 or more digits>
    end   = "" # Matches everything and gives back ""
    escapable = True

    def pack(self, text):
        space_size = self.match[1:-1]
        return f"<div style='width: {space_size}px;'>"

class NewLine(Syntax):
    start = f"^{NEWLINE}{NEWLINE}*{{[\r\n]}}" 
    #        one or more new line followed by a non-(new line)
    end   = "" # Matches everything and gives back ""
    extra_s = 1

    def pack(self, text):
        return "\n" + text

class Ignore(Syntax):
    start = "^%%" # %%
    end   = f"^{NEWLINE}" # new line
    extra_e = 1
    escapable = True
    line_start = True

    def pack(self, text): return ""

class Divider(Syntax):
    start = "^(----)-*{-}" # at least 4 * '-'
    end   = f"^{NEWLINE}" # new line
    extra_s = 1
    extra_e = 1
    line_start = True
    return_end = False

    def pack(self, text):
        return "\n<hr>"+text+"\n"

class NewPage(Syntax):
    start = "^(^^^^)^*{^}" # at least 4 * '^'
    end   = f"^{NEWLINE}" # new line
    extra_s = 1
    extra_e = 1
    line_start = True
    return_end = False

    def pack(self, text):
        return '\n<p style="page-break-after: always;"></p>\n'

class Bibliography(Syntax):
    start = "^(====)=*{=}" # at least 4 * '='
    end   = "" # anything
    extra_s = 1
    line_start = True

    def pack(self, text):
        begin = '<script type="text/bibliography">\n'
        end = '\n</script>'
        return begin + text + end

class Note(Syntax):
    start = "^[(][(]" # ((
    end   = "^[)][)]" # ))
    symmetric = True
    grammar = BASE_GRAMMAR

    def pack(self, text):
        if len(self.match) == 2:
            return "<dt-fn>" + text + "</dt-fn>"
        elif len(self.match) == 3:
            return "("*len(self.match) + text + ")"*len(self.match)

class Emphasis(Syntax):
    start = "^[*][*]*{[*]}" # one or more * followed by (not *)
    end   = "^[*][*]*{[*]}" # one or more * followed by (not *)
    extra_s = 1
    extra_e = 1
    symmetric = True
    escapable = True
    grammar = BASE_GRAMMAR

    def pack(self, text):
        if len(self.match) == 1:
            return "<i>" + text + "</i>"
        elif len(self.match) == 2:
            return "<b>" + text + "</b>"
        elif len(self.match) == 3:
            return "<u>" + text + "</u>"
        elif len(self.match) == 4:
            return "<text style='font-family: monospace;'>" + text + "</text>"
        else:
            return text

class InlineCode(Syntax):
    start = "^`"
    end   = "^`"
    escapable = True
    grammar = BASE_GRAMMAR

    def pack(self, text):
        return "<text style='font-family: monospace;'>" + text + "</text>"


class Color(Syntax):
    start = "^[{]" # {
    end   = "^[}]" # }
    symmetric = True
    escapable = True
    grammar = BASE_GRAMMAR

    def pack(self, text):
        return "<font color='"+self.match[1:-1]+"'> " + text + " </font>"

class Title(Syntax):
    start = "^!!*{!}" # One or more !, followed by (not !)
    end   = f"^{NEWLINE}" # new line
    extra_s = 1
    extra_e = 1
    grammar = BASE_GRAMMAR
    escapable = True
    line_start = True
    return_end = False

    def pack(self, text):
        title_id = text.strip().replace('"','\\"').replace(">","")
        begin = f'<h1 id="{title_id}">'
        end   = "</h1>"
        return begin + text + end

class Header(Syntax):
    start = "^##*{#}" # One or more #, followed by (not #)
    end   = f"^{NEWLINE}" # new line
    extra_s = 1
    extra_e = 1
    grammar = BASE_GRAMMAR
    escapable = True
    line_start = True

    def pack(self, text):
        header_id = text.strip().replace('"','\\"').replace(">","")
        link = f"<span class='header' id='{header_id}'></span>"
        begin = f'<h{len(self.match)+1}>'
        end   = f"</h{len(self.match)+1}>"
        return link + begin + text + end

class Subtext(Syntax):
    start = "^  *{ }" # one or more spaces followed by a non-space
    end   = f"^{NEWLINE}" # new line
    extra_s = 1
    extra_e = 1
    grammar = BASE_GRAMMAR
    line_start = True
    return_end = False

    def pack(self, text):
        begin = f"<p style='padding-left: {15*(len(self.match))}px; margin-top: 0px; margin-bottom: 0px;'>"
        end   = "</p>"
        return begin + text + end

class UnorderedElement(Syntax):
    start = "^-  *{ }" # '-' followed by one or more spaces followed by a non-space
    end   = f"^{NEWLINE}" # new line
    extra_s = 1
    extra_e = 1
    grammar = BASE_GRAMMAR
    line_start = True
    return_end = False

    def pack(self, text):
        count = len(self.match) - 2
        return "<li>"+ text +"</li>"

class OrderedElement(Syntax):
    start = "^[0123456789][0123456789]*([)]|[.])"
    #       one or more digits followed by '.' or ')'
    end   = f"^{NEWLINE}" # new line
    extra_e = 1
    grammar = BASE_GRAMMAR
    line_start = True
    return_end = False

    def pack(self, text):
        return "<li>"+ text +"</li>"

class TableEntry(Syntax):
    start = "^[|]" # |
    end   = "^([|]|\n|\r|(\r\n))" # | or new line
    grammar = TABLE_GRAMMAR
    escapable = True
    return_end = False

    # If there were no contents, then assume this was the last on the line
    def pack(self, text):
        if len(text) > 0:
            return "<td>" + text + "</td>"
        else:
            return ""
    

BASE_GRAMMAR += [Modifier(), Math(), Emphasis(), InlineCode(),
                 Color(), Note(), Ref(), Jump(), Link(), Subtext(),
                 Ignore(), Spacer()]
TABLE_GRAMMAR += BASE_GRAMMAR + [Divider(), TableEntry()]
ALL_GRAMMAR = [NewLine(), Divider(), NewPage(), Header(), Title(),
               Bibliography(), External(), Caption(), UnorderedElement(),
               OrderedElement(), TableEntry()] + BASE_GRAMMAR

# ====================================================================
#                  Definition of Blocks of Syntaxes                   
# ====================================================================

class TableRow(Block):
    before = "\n<tr>"
    after  = "</tr>"
    start  = [TableEntry]
    syntax = [TableEntry]

class Table(Block):
    before = "\n<table>"
    after  = "</table>"
    start  = [TableEntry]
    blocks = [TableRow]
    syntax = [Divider, NewLine, Ignore]
    requirements = {str(NewLine):lambda nl: len(nl.match) == 1}

class OrderedList(Block):
    before = "\n<ol>"
    after  = "</ol>"
    start  = [OrderedElement]
    syntax = [OrderedElement, NewLine]
    requirements = {str(NewLine):lambda nl: len(nl.match) == 1}

class UnorderedList(Block):
    before = "\n<ul>"
    after  = "</ul>"
    start  = [UnorderedElement]
    syntax = [UnorderedElement, NewLine]
    requirements = {str(NewLine):lambda nl: len(nl.match) == 1}

class Paragraph(Block):
    before = "\n<p>"
    after  = "</p>"
    start  = [str]+[type(s) for s in ALL_GRAMMAR if (type(s) not in [TableEntry,NewLine,Header])]
    blocks = [OrderedList, UnorderedList]
    syntax = [str]+[type(s) for s in ALL_GRAMMAR if (type(s) not in [Header])]
    requirements = {str(NewLine):lambda nl: len(nl.match) == 1}

class Body(Block):
    syntax = [type(s) for s in ALL_GRAMMAR]
    blocks = [Paragraph, Table, OrderedList, UnorderedList]

# ====================================================================
#                        Text Parsing Function     
# ====================================================================

# Given a list of raw lines, parse out a title, description, and
# authors form the top of a text file (if given).
def parse_header(raw_lines):
    html_kwargs = {}
    found = []
    authors = ""
    affiliations = ""
    # Loop through until done processing frontmatter
    while (len(raw_lines) > 0) and (len(raw_lines[0][:-1]) > 0):
        if raw_lines[0][:2] == "::":
            # Process an author
            found.append("author")
            auth_line_split = [s.strip() for s in raw_lines.pop(0)[2:].split("::")]
            if len(auth_line_split) != 3:
                raise(AuthorError("\n\n  Expected author format ':: <name> :: <email> :: <web address>'."))
            name, email, web = auth_line_split
            authors += f"{AA_BEGIN}{name}: {web}\n"
            affiliations += f"{AA_BEGIN}{email}\n"
            continue
        elif ("title" not in found):
            # Process a title
            if ("title" in found): break
            found.append("title")
            html_kwargs["title"] = raw_lines.pop(0).strip()
            html_kwargs["frontmatter_title"] = html_kwargs["title"].replace(":","")
            continue
        elif ("description" not in found):
            # Process a description
            found.append("description")
            # If there is a description on the second line, use it
            html_kwargs["description"] = raw_lines.pop(0).strip()
            html_kwargs["frontmatter_description"] = html_kwargs["description"].replace(":","-")
            continue
        else: break
    # Update the authors and affiliations if they were provided
    if (len(authors) > 0):
        html_kwargs["authors"] = authors
        html_kwargs["affiliations"] = affiliations
    return html_kwargs

# Given a path to a text file, process that text file into an HTML
# document format. Arguments should be self-explanatory.
# 
#  (verbose = 1) -> status updates only
#  (verbose = 2) -> internal parsing updates included as well
# 
def parse_txt(path_name, output_folder='.', verbose=1,
              appendix=True, justify=False, use_local=USE_LOCAL,
              resource_folder=RESOURCE_FOLDER, show=True):
    if (verbose > 0): print(f"Processing '{path_name}'...")
    with open(path_name) as f:
        raw_lines = f.readlines()
    if len(raw_lines) == 0: return ""
    if (verbose > 0): print(f"Read text with {len(raw_lines)} lines.")
    # Initialize the document build keyword arguments
    html_kwargs = {"frontmatter_title":TITLE, "frontmatter_description":DESCRIPTION,
                   "title":TITLE, "description":DESCRIPTION,
                   "bibliography":BIBLIOGRAPHY, "appendix":APPENDIX,
                   "notes":NOTES, "justify":JUSTIFY_CSS}
    if not appendix: html_kwargs["appendix"] = ""
    # Add the formatted author block
    html_kwargs.update(FORMAT_AUTHORS())
    # If there is a title on the first line (minus '\n'), parse header
    if (len(raw_lines) > 0) and (len(raw_lines[0][:-1]) > 0):
        html_kwargs.update(parse_header(raw_lines))

    # ================================================================
    # Initialize a syntax processor that does not have to close and
    # captures all parts of the grammar
    processor = Syntax()
    processor.closed = False
    processor.grammar = ALL_GRAMMAR
    global FOUND_NOTE; FOUND_NOTE = False
    # Process the text into a heirarchical syntax format
    if (verbose > 0): print(f"Processing raw lines of text..")
    # all_text = bytes(("".join(raw_lines) + EOF).encode("UTF-8"))
    # all_text = MutableString("".join(raw_lines) + EOF)
    all_text = "".join(raw_lines) + EOF
    body, _, _ = processor.process(all_text, 0, verbose=(verbose > 1))
    # Check for a bibliography at the end of the body
    if type(body[-1]) == Bibliography:
        html_kwargs["bibliography"] = body.pop(-1).render()
    # Pop the appendix if there were no notes or bibliography
    elif not FOUND_NOTE:
        html_kwargs["appendix"] = ""
    # Remove justification if it is not desired.
    if not justify: html_kwargs["justify"] = ""
    if (verbose > 0): print(f"Rendering the HTML document..")
    # Render the heirarchical syntax into HTML text
    rendered_body, _ = Body().render(body, verbose=(verbose > 1))
    html_kwargs.update({"body":rendered_body})
    # Save the HTML document locally
    if (verbose > 0): print(f"Saving the HTML document..")
    file_name = os.path.basename(path_name)
    output_file = os.path.join(os.path.abspath(output_folder), 
                               file_name + ".html")
    html = HTML(use_local, resource_folder).format( **html_kwargs )
    with open(output_file, "w") as f:
        print(html, file=f)
    if (verbose > 0): print(f"Saved output in '{output_file}'.")
    # Show the resulting file in the webbrowser (if appropriate).
    if show: 
        import webbrowser
        if (verbose > 0): print(f"Opening " + "file://" + output_file + " in default web browser.")
        webbrowser.open("file://" + output_file)
    if (verbose > 0): print(f"Returning raw HTML as output.")
    # Return the HTML document (using formatted kwargs to insert text)
    return html


DOC_STRING = __doc__

# Define "all" the set of things that should be user-accessible 
# outside this package.
__all__ = [parse_txt, DOC_STRING]
