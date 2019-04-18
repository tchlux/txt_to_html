|             |                |
|-------------|----------------|
|**TITLE:**   | txt_to_html         |
|**PURPOSE:** | A .txt to .html parser that makes pretty documents with quasi-markdown.|      |
|**AUTHOR:**  | Thomas C.H. Lux  |
|**EMAIL:**   | thomas.ch.lux@gmail.com |


## INSTALLATION:

    $ pip install git+https://github.com/tchlux/txt_to_html.git

## USAGE:

### PYTHON:

    import txt_to_html
    txt_to_html.parse_txt("<txt source file>")

### COMMAND LINE:

  The execution of the program looks like:

    $ python -m txt_to_html <source text file> [--online] [--no-appendix] [--no-show] [--no-justify] [output folder]

  This outputs a <source text file>.html ready to be viewed in a browser.

  Default behavior is to use local resources for displyaing HTML and to output in the current working director.

  If the `--online` argument is given, resource files are internet-accessible and nonlocal.

  If the `--no-appendix` argument is given, the appendix section is removed from the html document.

  If the `--no-show` argument is given, the resulting HTML file is *not* opened in a browser upon completion.

  If the `--no-justify` argument is given, the resulting HTML file has body text which will *not* be justified (layout that normalizes line width).

  If the `[output directory]` argument is given, output file is saved in that directory, which *must* already exist.


## HOW IT WORKS:

Reads the txt file into a heirarchical format of different "syntax" lists. Processes the syntax list with a series of "blocks". Outputs html document.

## VERSION HISTORY:

|Version and Date       | Description           |
|-----------------------|-----------------------|
| 0.0.0<br>February 2018 | Created a parser that produces Distill formatted <br> HTML files from TXT files with markdown style <br> syntax. |

| 0.0.6<br>April 2019 | Reorganized code and fixed some minor bugs that were <br> preventing install on other machines. Now the <br> package should operate correctly if installed via <br> the recommended instructions. |

| 0.0.9<br>April 2019 | Added a `--no-justify` option to the build and set <br> the default compilation to justify the output body <br> text. |
| 0.0.10<br>April 2019 | Added a `--no-justify` option to the build and set <br> the default compilation to justify the output body <br> text. |
| 0.0.10<br>April 2019 | Added a `--no-justify` option to the build and set <br> the default compilation to justify the output body <br> text. |

### BUGS

- [ ] Not having an extra newline after ordered list causes
      incorrect parse (line without paragraph wrapper).
- [ ] Unordered and ordered lists do not work within subtext block,
      all things at same indent level should be in same subtext.
- [ ] The "<< >>" doesn't seem to be working properly, won't
      overwrite existing properties.

### IMPROVEMENTS

- [ ] Make {{file.txt}} import a txt file in place into the document.
- [ ] Make a syntax for inserting python code '>>>'
- [ ] Redo the "text with a hyperlink" to be "(text){{link}}"
- [ ] Make line starts work --> "(or strictly after spaces)"
- [ ] Make subtext line that is empty behave like an empty new line.
- [ ] Adjust print format settings to make margins and justification.
- [ ] Create custom "ordered list" using manual trick that allows
      for the control of list item names in line.
- [ ] Make *all* new lines matter. Get rid of the Latex
      double-new-line for paragraph and extras are ignored.
- [ ] Extra new lines should be treated the same a new lines, for
      spacing out the contents of the file.
- [ ] Generate a "Table of Contents" with links
- [ ] Generate one 'test' file that demonstrates all Syntax.
- [ ] Processing is too slow, The amount of python logic
      per-character in the source document is too high. Appears to
      have quadratic complexity, but it shouldn't. Only need to
      process as many characters of the string as the longest
      syntax allows.