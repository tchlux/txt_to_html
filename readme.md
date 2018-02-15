|             |                                                                        |
|-------------|------------------------------------------------------------------------|
|**TITLE:**   | txt_to_html                                                            |
|**PURPOSE:** | A .txt to .html parser that makes pretty documents with quasi-markdown.|
|**AUTHOR:**  | Thomas C.H. Lux                                                        |
|**EMAIL:**   | thomas.ch.lux@gmail.com                                                |


## INSTALLATION:

    $ pip install txt_to_html

## PYTHON USAGE:

    import txt_to_html
    txt_to_html.parse_txt("<txt source file>")


## COMMAND LINE USAGE:

  The execution of the program looks like:

    $ python txt_to_html.py <source text file> [<output folder>]

  This outputs a <source text file>.html ready to be viewed in a browser.


## HOW IT WORKS:

  Reads the txt file into a heirarchical format of different "syntax"
  lists. Processes the syntax list with a series of "blocks". Outputs
  html document.

## VERSION HISTORY:

|Version and Date       | Description           |
|-----------------------|-----------------------|
| 0.0.0<br>February 2018 | Created a parser that produces Distill formatted <br> HTML files from TXT files with markdown style <br> syntax. |
| 0.0.0<br>February 2018 | Created a parser that produces Distill formatted <br> HTML files from TXT files with markdown style <br> syntax. |
| 0.0.1<br>February 2018 | Created a parser that produces Distill formatted <br> HTML files from TXT files with markdown style <br> syntax. |


## UPCOMING (checked means in development):

### BUGS

### USABILITY

- [ ] Write tests to verify the code.

### IMPROVEMENTS

- [ ] Add new features listed as "TODO".
