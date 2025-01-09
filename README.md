# Part 2 of JSON Compiler

## Grammar:
**value:** dict | list | STRING | NUMBER | _true_ | _false_ | _null_
<br/>**list:** [ value, value* ]
<br/>**dict:** { pair, pair* }
<br/>**pair:** STRING : value


### Rules/Assumptions:
- All boolean values are lowercase as well as null
- boolean tokens are labeled as BOOLEAN (ex. <BOOLEAN,true>)
- number tokens are labeled as NUMBER (ex. <NUMBER,123>)
- Strings are tokenized without their parenthesis (ex. "hello" -> <STRING,hello>)
- There are no spaces inside the tokens with the token type
  - ex. <STRING, abc> is valid, <STRING ,abc> is not valid
- You can have empty strings, numbers, dictionaries and lists
    - ex. {} and [] is valid

## Using The Code
- At the start of the program, it will ask the user for the number of files that are being parsed (I provided 10 files) 
these files are named input and some number starting from 1 (ex. input1.txt)
- The parser will then parse one file at a time. Each file gets its own output file (ex. output1.txt)
- It parses it first by reading in all the tokens and adds it to a list. It then parses each value creating a 
  parse tree. If it finds a Syntax error, it will print the error before the tree is printed. The error will say what tokens caused it and the number they are found at in the input file
    - If an error is found, the program will try to recover and handle the error using 2 different methods of error recovery and it will adjust the parse tree accordingly
      - **Panic mode recovery**: ignores the invalid tokens until it hits a synchronizing token (",", "}", etc).
      - **Phrase level recovery**: fixes a token during run time if needed (ex. removing an extra comma or adding an end bracket to the end of a list)
