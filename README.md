# About
This school project was created in Spring 2025 and led by Brian Wei. The other great contributors are Kelvin Nguyen and Suhaib Affaneh.
This is a compiler meant to be a lexer, parser, semantic analyzer, etc. for a fictional and simple programming language.

# Features and Output
The program's lexer classifies each lexeme as an identifier, integer, real, operator, keyword, and separator. 
  * **Identifier** - a variable that must start with a letter followed optionally by either letter(s), digit(s) or underscore(s). Ex: dd93_
  * **Integer** - a whole number. Ex: 100
  * **Real** - digit(s) followed by ".", and then followed by digit(s). Ex: 100.101
  * **Operator** - symbols used for comparison or adding, multiplying, subtracting, dividing. Ex: =, <
  * **Keyword** - words that are already defined by the language with its own purpose. Ex: endwhile, if
  * **Separator** - symbols that separate parts of code or to end statements. Ex: "$$", "{}", ";"

Any lexeme that does not fit into any of these categories are classified as an error. 

The syntax analyzer or parser analyzes what syntax rule the lines of the code follow. The syntax rule used is printed. If a part of the code does not follow a syntax rule, then an error is outputted.

The semantic analyzer analyzes if there are any semantic errors in the code.

A symbol table is outputted which lists every identifier and its memory location and type. The code is also translated into assembly language at the bottom of the output file.

# Files
  * **Final Compiler Project Documentation.docx.pdf** - The documentation for the project. Read here for more information.
  * **README.md** - This file. Contains basic information on the project.
  * **test_case[#].txt** and **output_test_case[#].txt** - The input code is in the test case files and its output is in the corresponding output files.
  * **rat25s_parser.py** - Contains the core logic of the lexer, syntax and semantic analyzer of the program.
  * **run_tests.exe** - Executable file for Windows users
  * **run_tests.py** - Contains logic to run the tests. For non-Windows users.

# How to Run
Download all the files into your local repository, and set a terminal to point to the folder that contains these files. Then:
1. If you have Windows, run `.\run_tests.exe`. You should then see the output in the three output files.
2. If you do not have Windows, then type `python run_tests.py`. Make sure you have Python already installed. You will then see the output in the output files.
