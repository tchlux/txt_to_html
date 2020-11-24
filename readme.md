<p align="center">
  <h1 align="center">txt_to_html</h1>
</p>

<p align="center">
A <code>.txt</code> to <code>.html</code> parser that makes pretty documents with quasi-markdown.
</p>


## INSTALLATION:

  Install the latest stable release (tested on macOS and Ubuntu) with:

```bash
pip install https://github.com/tchlux/txt_to_html/archive/1.1.1.zip
```

  In order to install the current files in this repository
  (less stable) use:

```bash
pip install git+https://github.com/tchlux/txt_to_html.git
```

## USAGE:

### COMMAND LINE:

  The execution of the program looks like:

```bash
python -m txt_to_html <source text file> [--online] [--no-appendix] [--no-show] [--no-justify] [output folder]
```

  This outputs a <source text file>.html ready to be viewed in a browser.

  Default behavior is to use local resources for displyaing HTML and to output in the current working director.

  If the `--online` argument is given, resource files are internet-accessible and nonlocal.

  If the `--no-appendix` argument is given, the appendix section is removed from the html document.

  If the `--no-show` argument is given, the resulting HTML file is *not* opened in a browser upon completion.

  If the `--no-justify` argument is given, the resulting HTML file has body text which will *not* be justified (layout that normalizes line width).

  If the `[output directory]` argument is given, output file is saved in that directory, which *must* already exist.


### PYTHON:

```python
import txt_to_html
txt_to_html.parse_txt("<txt source file>")
```

## HOW IT WORKS:

Reads the txt file into a heirarchical format of different "syntax" lists. Processes the syntax list with a series of "blocks". Outputs html document. Uses custom markdown syntax and a custom regex implementation (prohibits Windows usage and requires `cc` to point to valid C compiler). See `help(txt_to_html)` for listing of the acceptable quasi-markdown syntax.


## VERSION HISTORY:

See [this file](txt_to_html/about/version_history.md) for full list.

### BUGS

- [ ] Not having an extra newline after ordered list causes
      incorrect parse (line without paragraph wrapper).
- [ ] Unordered and ordered lists do not work within subtext block,
      all things at same indent level should be in same subtext.
- [ ] The "<< >>" doesn't seem to be working properly, won't
      overwrite existing properties.

### IMPROVEMENTS

- [ ] Redo the "text with a hyperlink" to be "(text){{link}}"
- [ ] Make subtext line that is empty behave like an empty new line.
- [ ] Adjust print format settings to make margins and justification.
- [ ] Make *all* new lines matter. Get rid of the Latex
      double-new-line for paragraph and extras are ignored.
- [ ] Generate a "Table of Contents" with links
- [ ] Generate one 'test' file that demonstrates all Syntax.
- [ ] The algorithm used in this implementation is generally slow in
      Python because it relies heavily on recursion and slicing,
      some attempts have been made to improve speed, but a different
      approach is required for linear complexity (currently at least
      quadratic complexity is exhibited with document size).
