# This module provides a text file parser that uses a heirarchical
# grammar to parse "markdown" style text files into HTML documents.
# 
# LINE STARTS:
#   New lines ---------> paragraphs
#   Spaces ------------> indentation
#   "#+" --------------> Header levels (number of '#' is the level)
#   "-" ---------------> unordered lists
#   "1)" --------------> ordered lists
#   "|" ---------------> table entries
#   "----(-)*" --------> divider
#   "====(=)*" --------> marks the rest of the document as a bibtex bibliography
#   "!+" --------------> new title
#   "{{<path>}}" ------> include external file, supports [.png, .jpeg, .jpg, .html]
# 
# ANYWHERE:
#   "((<footnote>))" --> footnote in line (will be in appendix as well)
#   "[[<reference>]]" -> reference key in the bibliography
#   "$<math>$" --------> in line math
#   "$$<math>$$" ------> new line (centered) math
#   "*<text>*" --------> italics
#   "**<text>**" ------> bold
# 
# TODO:  Make a syntax for providing links (to inside document and out) @@<text>
# TODO:  Make a syntax for setting attributes of objects                <<>>
# TODO:  Not having an extra newline after ordered list causes
#        incorrect parse (line without paragraph wrapper).

import os, re

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
TITLE = "Notes"
DESCRIPTION = ""
AA_BEGIN = "   - "
AUTHORS_AND_AFFILIATION = [
    # ("Thomas Lux: https://www.linkedin.com/in/thomas-ch-lux", 
    #  "thomas.ch.lux@gmail.com"),
]
RESOURCE_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"resources")
USE_LOCAL = True

# Format the author and affiliation block appropriately, return in
# dictionary to be used as the **kwargs of formatting HTML.
def FORMAT_AUTHORS():
    authors = ""
    affils = ""
    for auth, aff in AUTHORS_AND_AFFILIATION:
        authors += AA_BEGIN + auth + "\n"
        affils += AA_BEGIN + aff + "\n"
    return dict([("authors",authors), ("affiliations",affils)])

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

def HTML(use_local=USE_LOCAL, resource_folder=RESOURCE_FOLDER):
    print("Formatting HTML %susing local files and resources."%(
        "" if use_local else "not "))

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
    {online_start} <script src="http://people.cs.vt.edu/tchlux/distill.template.v1.no-banner.js"></script> {online_end}
    {local_start} <script src="{resource_folder}/distill.template.v1.no-banner.js"></script> {local_end}
    '''.format(**source_format)

    # Source files for mathjax
    mathjax_source = '''
    <!-- Include MathJax -->
    {online_start} <script type="text/javascript" async src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.2/MathJax.js?config=TeX-MML-AM_CHTML"> </script> {online_end}
    {local_start} <script type="text/javascript" async src="{resource_folder}/MathJax-2.7.2/MathJax.js?config=TeX-AMS-MML_HTMLorMML,local/local"></script> {local_end}
    '''.format(**source_format)

    # Default HTML
    html = '''
    <!doctype html>
    <meta charset="utf-8">

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
      dt-article ol, dt-article ul {{
        padding-left: 50px;
      }}

      dt-article ul {{
        list-style: none;
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
    '''%(distill_source, mathjax_source)

    return html


NOTES = '''
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

# Object oriented recursive tree-grammar parsing code

# ====================================================================
#                 Generic Recursive Syntax Parsing Class     
# ====================================================================

ON_NEW_LINE = r"(\r\n|\r|\n)$"
ESCAPE_CHAR = r"\\$"
SPECIAL_HTML_CHARS = {"<":"&lt;", ">":"&gt;"}
class IncompleteSyntax(Exception): pass
class UnsupportedExtension(Exception): pass
class MissingFile(Exception): pass

# Class for defining a syntax in text.
class Syntax(list):
    start   = r"^$"     # The regex matching the start of this syntax
    end     = r"^$"     # The regex matching the end of this syntax
    match   = ""        # The string matched when this Syntax started
    grammar = []        # The grammar for processing this syntax (list of syntaxes)
    closed  = True      # True if this syntax must successfully end
    symmetric = False   # True if this syntax end must equal the start in length
    escapable = False   # True if "ESCAPE_CHAR" can be uesd to escape this syntax
    line_start = False  # True if this syntax must start on a new line
    allow_escape = True # True if escape characters are allowed in this syntax
    return_end = True   # True if the "end" regular expression should be returned
    
    # Function for handling unprocessed strings. If this syntax is
    # closed then an error is raised, otherwise the body is returned.
    def not_closed(self, body):
        if self.closed:
            raise(IncompleteSyntax(str(type(self)) +" "+ str(body)))
        else:
            return body, "", ""

    # Function for packing text (to be overwritten by subclasses)
    def pack(self, text):
        return text

    # Recursive function for rendering output text from nested strings
    # and Syntax objects to produce final processed output text.
    def render(self, spacing="", verbose=False):
        if verbose: print(spacing, "Rendering", type(self), [self.match])
        text = ""
        for el in self:
            if type(el) == str: text += el
            else:               text += el.render(spacing+"  ", verbose)
        return self.pack(text)

    # Returns the length of the match at the beginning of a string
    # that fits the "start" regular expression for this syntax.
    def starts(self, string):
        match = re.match(self.start, string)
        if match: return True, match.group()
        else:     return False, ""

    # Returns the length of the match at the beginning of a string
    # that fits the "end" regular expression for this syntax.
    def ends(self, string, start):
        match = re.match(self.end, string)
        if match:
            if self.symmetric:
                if (len(start) == len(match.group())): 
                    return True, (start if self.return_end else "")
                else:
                    return False, ""
            else:
                return True, (match.group() if self.return_end else "")
        else:
            return False, ""

    # Recursive function for processing a string into a Syntax heirarchy.
    def process(self, string, start="", spacing="", verbose=False):
        if verbose: print(spacing,"Begin",type(self),[start])
        # Initialize a new copy of this class to hold contents (and keep match)
        body = type(self)([""])
        body.match = start
        new_line = re.match(ON_NEW_LINE, start) != None
        escaped = (re.match(ESCAPE_CHAR, start) != None) and self.allow_escape
        if (escaped): start = start[:-1]
        # Initialize remaining length of string (>0 to allow matching "")
        remaining = max(1, len(string))
        # Search the string for the start and end of this syntax
        while remaining > 0:
            # First, check to see if this syntax has ended
            found, end = self.ends(string, start)
            if found:
                # If this syntax has completed, return
                if verbose: print(spacing, " End", type(self), body)
                return body, string[:len(end)], string[len(end):]
            # Check for the beginnings of any sub-syntaxes
            for syntax in self.grammar:
                # Skip syntax that requires being at the start of a new line
                if (syntax.line_start and (not new_line)): continue
                if (syntax.escapable  and (escaped)): continue
                # Search for the syntax at this part of the string
                found, syntax_start = syntax.starts(string)
                if found:
                    contents, ends_on, string = syntax.process(
                        string[len(syntax_start):], syntax_start, 
                        spacing+"  ", verbose)
                    body.append(contents)
                    # Record whether or not we are currently on a new line
                    new_line = re.match(ON_NEW_LINE, ends_on) != None
                    new_line = new_line or (type(body[-1]) == NewLine)
                    # Record whether or not trailing character was ESCAPE_CHAR
                    escaped = (re.match(ESCAPE_CHAR, ends_on) != None) and self.allow_escape
                    break
            else:
                # Add string contents appropriately
                if (len(body) == 0) or (type(body[-1]) != str):
                    body.append(string[0])
                else:
                    body[-1] += string[0]
                # Record whether or not we are currently on a new line
                new_line = re.match(ON_NEW_LINE, string[0]) != None
                # Allow for the escaping of the escape character
                if not escaped:
                    # Record whether or not we are currently escaping
                    escaped = (re.match(ESCAPE_CHAR, string[0]) != None) and self.allow_escape
                    if (escaped): body[-1] = body[-1][:-1]
                else: 
                    # Otherwise, reset the current escaped status
                    escaped = False
                    # Check for special HTML characters that need to be
                    # automatically escaped (if escaping is allowed)
                    if (string[0] in SPECIAL_HTML_CHARS):
                        body[-1] = body[-1][:-1] + SPECIAL_HTML_CHARS[string[0]]
                # Transition string forward by one character
                string = string[1:]
            # Update the stopping condition check
            remaining = len(string)
        if verbose:
            print(spacing," End",type(self),body)
            print(spacing,body)
            print(spacing,string)
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
        if verbose: print(spacing, "Begin", type(self))
        text = ""
        while len(body) > 0:
            # First try and identify any sub-blocks in the body
            for b in self.blocks:
                if type(body[0]) in b.start:
                    rendered_text, body = b().render(body, spacing+"  ", verbose)
                    text += rendered_text
                    break
            else:
                recognized_syntax = (type(body[0]) in self.syntax)
                no_requirement_exists = (str(type(body[0])) not in self.requirements)
                requirement_met = no_requirement_exists or self.requirements[str(type(body[0]))](body[0])
                # If (this syntax is recognized) AND
                #     (there is not a requirement for the syntax) OR
                #     (the requirement for this syntax is met)
                if recognized_syntax and requirement_met:
                    # Check to see if this is just a string
                    if type(body[0]) == str:
                        text += body.pop(0)
                    else:
                        # This syntax is accepted by this block
                        text += (body.pop(0)).render()
                else:
                    # This syntax is not accepted by this block
                    if verbose: 
                        print(spacing, "End (unfinished)", type(self),
                              recognized_syntax, requirement_met, 
                              [body[0].match if not requirement_met else ""], 
                              type(body[0]), [text])
                    # There was no recognized block nor syntax, return body
                    return self.pack(text), body
        if verbose: print(spacing, "End (finished)", type(self), [text])
        return self.pack(text), body

# ====================================================================
#                        Grammar Definition     
# ====================================================================

BASE_GRAMMAR = []
LIST_GRAMMAR = []
TABLE_GRAMMAR = []

class Math(Syntax):
    start = r"^\$+"
    end   = r"^\$+"
    symmetric = True
    escapable = True
    allow_escape = False

    def pack(self, text):
        # Pack with or without new line appropriately.
        if len(self.match) == 1:
            return "\(" + text + "\)"
        elif len(self.match) == 2:
            return "\n$$" + text + "$$"

class Ref(Syntax):
    start = r"^\[\[+"
    end   = r"^\]\]+"
    symmetric = True

    def pack(self, text):
        if len(self.match) == 2:
            return "<dt-cite key=\"" + text + "\"></dt-cite>"
        else:
            return text

class External(Syntax):
    start = r"{{"
    end   = r"}}"
    line_start = True
    symmetric = True
    
    def pack(self, path):
        extension = path[-path[::-1].find("."):]
        if extension in {"png","jpg","jpeg"}:
            return f"<img src='{path}' width='90%' style='margin: 20px; display: inline-block;'>"
        elif extension in {"html"}:
            return f"<iframe src='{path}' frameBorder='0' style='width:100%; height:60vh; margin: -20px'></iframe>"
        else:
            raise(UnsupportedExtension(f"External files with extension '{extension}' are not supported."))

class Spacer(Syntax):
    start = r"^<[0-9]+>"
    end   = r"^(@EMPTY MATCH@)*"
    escapable = True

    def pack(self, text):
        space_size = self.match[1:-1]
        return "<div style='width: %spx;'>"%(space_size)

class NewLine(Syntax):
    start = r"^(\r\n|\r|\n)+"
    end   = r"^(@EMPTY MATCH@)*"

    def pack(self, text):
        return "\n" + text

class Ignore(Syntax):
    start = r"^%%"
    end   = r"^(\r\n|\r|\n)"
    escapable = True
    line_start = True

    def pack(self, text): return ""

class Divider(Syntax):
    start = r"^(----)-*"
    end   = r"^(\r\n|\r|\n)"
    line_start = True
    return_end = False

    def pack(self, text):
        return "\n<hr>"+text+"\n"

class Bibliography(Syntax):
    start = r"^(====)=*"
    end = r"^$"
    line_start = True

    def pack(self, text):
        begin = '<script type="text/bibliography">\n'
        end = '\n</script>'
        return begin + text + end

class Note(Syntax):
    start = r"^\(\(+"
    end   = r"^\)\)+"
    symmetric = True
    grammar = BASE_GRAMMAR

    def pack(self, text):
        if len(self.match) == 2:
            return "<dt-fn>" + text + "</dt-fn>"
        elif len(self.match) == 3:
            return "("*len(self.match) + text + ")"*len(self.match)

class Emphasis(Syntax):
    start = r"^\*+"
    end   = r"^\*+"
    symmetric = True
    escapable = True
    grammar = BASE_GRAMMAR

    def pack(self, text):
        if len(self.match) == 1:
            return "<i>" + text + "</i>"
        elif len(self.match) == 2:
            return "<b>" + text + "</b>"
        elif len(self.match) == 3:
            return "<b><i>" + text + "</i></b>"
        elif len(self.match) == 4:
            return "<text style='color: #aaa; font-family: monospace;'>" + text + "</text>"
        else:
            return text

class Title(Syntax):
    start = r"^!+"
    end   = r"^(\r\n|\r|\n)"
    grammar = BASE_GRAMMAR
    escapable = True
    line_start = True
    return_end = False

    def pack(self, text):
        begin = "<h1>"
        end   = "</h1>"
        return begin + text + end

class Header(Syntax):
    start = r"^#+"
    end   = r"^(\r\n|\r|\n)"
    grammar = BASE_GRAMMAR
    escapable = True
    line_start = True

    def pack(self, text):
        begin = "<h"+str(len(self.match)+1)+">"
        end   = "</h"+str(len(self.match)+1)+">"
        return begin + text + end

class Subtext(Syntax):
    start = r" +"
    end   = r"^(\r\n|\r|\n)"
    grammar = BASE_GRAMMAR
    line_start = True
    return_end = False

    def pack(self, text):
        begin = "<p style='padding-left: %spx; margin-top: 0px; margin-bottom: 0px;'>"%(15*(len(self.match)))
        end   = "</p>"
        return begin + text + end

class UnorderedElement(Syntax):
    start = r"^- +"
    end   = r"^(\r\n|\r|\n)"
    grammar = BASE_GRAMMAR
    line_start = True
    return_end = False

    def pack(self, text):
        count = len(self.match) - 2
        return "<li>"+ text +"</li>"

class OrderedElement(Syntax):
    start = r"^[0-9]+\)"
    end   = r"^(\r\n|\r|\n)"
    grammar = BASE_GRAMMAR
    line_start = True
    return_end = False

    def pack(self, text):
        return "<li>"+ text +"</li>"

class TableEntry(Syntax):
    start = r"^\|"
    end   = r"^(\||\r\n|\r|\n)"
    grammar = TABLE_GRAMMAR
    escapable = True
    return_end = False

    # If there were no contents, then assume this was the last on the line
    def pack(self, text):
        if len(text) > 0:
            return "<td>" + text + "</td>"
        else:
            return ""
    

BASE_GRAMMAR += [Math(), Emphasis(), Note(), Ref(), Subtext(),
                 Ignore(), Spacer()]
TABLE_GRAMMAR += BASE_GRAMMAR + [Divider(), TableEntry()]
ALL_GRAMMAR = [NewLine(), Divider(), Header(), Title(),
               Bibliography(), External(), UnorderedElement(),
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

# Given a path to a text file, process that text file into an HTML
# document format.
def parse_txt(path_name, output_folder='', verbose=True,
              use_local=USE_LOCAL, resource_folder=RESOURCE_FOLDER):
    if verbose: print("Processing '%s'..."%path_name)
    with open(path_name) as f:
        raw_lines = f.readlines()
    if len(raw_lines) == 0: return ""
    if verbose: print("Read text with %i lines."%len(raw_lines))
    # Initialize the document build keyword arguments
    html_kwargs = {"frontmatter_title":TITLE, "frontmatter_description":DESCRIPTION,
                   "title":TITLE, "description":DESCRIPTION,
                   "bibliography":BIBLIOGRAPHY, "appendix":APPENDIX,
                   "notes":NOTES}
    # Add the formatted author block
    html_kwargs.update(FORMAT_AUTHORS())
    # If there is a title on the first line, use it
    if (len(raw_lines) > 0) and (len(raw_lines[0]) > 0):
        html_kwargs["title"] = raw_lines.pop(0).strip()
        html_kwargs["frontmatter_title"] = html_kwargs["title"].replace(":","")
    # If there is a description on the second line, use it
    if (len(raw_lines) > 0) and (len(raw_lines[0]) > 0):
        html_kwargs["description"] = raw_lines.pop(0).strip()
        html_kwargs["frontmatter_description"] = html_kwargs["description"].replace(":","-")
    if (len(raw_lines) > 0) and (len(raw_lines[0]) == 0): raw_lines.pop(0)
    # ================================================================
    # Initialize a syntax processor that does not have to close and
    # captures all parts of the grammar
    processor = Syntax()
    processor.closed = False
    processor.grammar = ALL_GRAMMAR
    # Process the text into a heirarchical syntax format
    body, _, _ = processor.process("".join(raw_lines))
    # Check for a bibliography at the end of the body
    if type(body[-1]) == Bibliography:
        html_kwargs["bibliography"] = body.pop(-1).render()
    # Render the heirarchical syntax into HTML text
    rendered_body, _ = Body().render(body)
    html_kwargs.update({"body":rendered_body})
    # Save the HTML document locally
    file_name = os.path.basename(path_name)
    output_file = os.path.join(output_folder, file_name + ".html")
    html = HTML(use_local, resource_folder).format( **html_kwargs )
    with open(output_file, "w") as f:
        print(html, file=f)
    if verbose: print("Saved output in '%s'."%output_file)
    # Return the HTML document (using formatted kwargs to insert text)
    return html

