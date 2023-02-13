from dataclasses import dataclass
import sys

EOF           = 'EOF'
ID            = 'ID'
INTEGER_CONST = 'INTEGER_CONST'
REAL_CONST    = 'REAL_CONST'
LPAREN        = 'LPAREN'
RPAREN        = 'RPAREN'
SEMI          = 'SEMI'
DOT           = 'DOT'
COLON         = 'COLON'
COMMA         = 'COMMA'

# operators
ASSIGN        = 'ASSIGN'
PLUS          = 'PLUS'
MINUS         = 'MINUS'
MUL           = 'MUL'
FLOAT_DIV     = 'FLOAT_DIV'
EQEQ          = 'EQEQ'
GT            = 'GT'
LT            = 'LT'
GTEQ          = 'GTEQ'
LTEQ          = 'LTEQ'

# keywords
PROGRAM       = 'PROGRAM'
VAR           = 'VAR'
INTEGER       = 'INTEGER'
REAL          = 'REAL'
INTEGER_DIV   = 'INTEGER_DIV'
READ          = 'READ'
WRITE         = 'WRITE'
BEGIN         = 'BEGIN'
END           = 'END'
IF            = 'IF'
THEN          = 'THEN'
ELSE          = 'ELSE'
WHILE         = 'WHILE'
DO            = 'DO'


@dataclass
class Token:
    type: str
    value: object
    # an example for the representation of a class instance: Token(PLUS,'+') 
    def __str__(self):
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )
    
    def __repr__(self):
        return self.__str__()

KEYWORDS = {
    'PROGRAM': Token('PROGRAM', 'PROGRAM'),
    'VAR': Token('VAR', 'VAR'),
    'INTEGER': Token('INTEGER', 'INTEGER'),
    'REAL': Token('REAL', 'REAL'),
    'DIV': Token('INTEGER_DIV', 'DIV'),
    'BEGIN': Token('BEGIN', 'BEGIN'),
    'END': Token('END', 'END')
}


class Lexer(object):
    def __init__(self, text):
        self.text = text                        # stream of input
        self.pos = 0                            # current position in the stream
        self.curChar = self.text[self.pos]      # current character in the stream

    def error(self):
        sys.exit('Invalid character')

    def nextChar(self):                         # advances the pos pointer
        self.pos += 1
        if self.pos > len(self.text) - 1:       # end of input stream
            self.curChar = None                 
        else:
            self.curChar = self.text[self.pos]

    def skipSpaces(self):                       # to skip white spacses
        while self.curChar is not None and self.curChar.isspace():
            self.nextChar()

    def skipComments(self):
        while self.curChar != '}':
            self.nextChar()
        self.nextChar()                         # to skip the closing curly brace as well

    def peek(self):                             
        # returns the lookahead character
        pass

    def number(self):                           
        # Consume all the consecutive digits and decimal if present.
        pass

    def _id(self):
        # Handles identifiers and reserved keywords
        pass

    def get_token(self):
        # returns the token and token type
        pass