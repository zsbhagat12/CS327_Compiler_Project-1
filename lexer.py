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
MODULO        = 'MODULO'
POWER         = 'POWER'
EQEQ          = 'EQEQ'
NOTEQ         = 'NOTEQ'
GT            = 'GT'
LT            = 'LT'
GTEQ          = 'GTEQ'
LTEQ          = 'LTEQ'
AND           = 'AND'
OR            = 'OR'
PLUSEQ        = 'PLUSEQ'
MINUSEQ       = 'MINUSEQ'
MULEQ         = 'MULEQ'
FLOAT_DIVEQ   = 'FLOAT_DIVEQ'
MODULOEQ      = 'MODULOEQ'
POWEREQ       = 'POWEREQ'

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
STRING        = 'STRING'

# literals
TRUE          = "TRUE"
FALSE         = "FALSE"

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
    'END': Token('END', 'END'),
    'TRUE': Token('TRUE', True),
    'FALSE': Token('FALSE', False),
    'STRING': Token('STRING', 'STRING')
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
        if self.pos + 1 > len(self.text) - 1:
            return None
        else:
            return self.text[self.pos + 1]

    def number(self):                           
        # Consume all the consecutive digits and decimal if present.
        result = ''
        while self.curChar is not None and self.curChar.isdigit():
            result += self.curChar
            self.nextChar()

        if self.curChar == '.':
            result += self.curChar
            self.nextChar()

            while (
                self.curChar is not None and
                self.curChar.isdigit()
            ):
                result += self.curChar
                self.nextChar()

            token = Token('REAL_CONST', float(result))
        else:
            token = Token('INTEGER_CONST', int(result))

        return token

    def _id(self):
        # Handles identifiers and reserved keywords
        result = ''
        while self.curChar is not None and self.curChar.isalnum():
            result += self.curChar
            self.nextChar()

        token = KEYWORDS.get(result, Token(ID, result))
        return token
    
    def Stringlex(self):
        # Handles strings
        result = ''
        while self.curChar != '"':
            result += self.curChar
            self.nextChar()
        
        self.nextChar()
        token = Token('STRING', result)
        return token

    def get_token(self):
        # returns the token and token type
        while self.curChar is not None:

            if self.curChar.isspace():
                self.skipSpaces()
                continue

            if self.curChar == '{':
                self.nextChar()
                self.skipComments()
                continue

            if self.curChar.isalpha():
                return self._id()

            if self.curChar.isdigit():
                return self.number()
        
            if self.curChar == ':':
                if self.peek() == '=':
                    self.nextChar()
                    self.nextChar()
                    return Token(ASSIGN, ':=')
                else:
                    self.nextChar()
                    return Token(COLON, ':')
                
            if self.curChar == "|":
                if self.peek() == "|":
                    self.nextChar()
                    self.nextChar()
                    return Token(OR, "||")
            

            if self.curChar == "&":
                if self.peek() == "&":
                    self.nextChar()
                    self.nextChar()
                    return Token(AND, "&&")
                
            if self.curChar == '>':
                if self.peek() == '=':
                    self.nextChar()
                    self.nextChar()
                    return Token(GTEQ, '>=')
                else:
                    self.nextChar()
                    return Token(GT, '>')

            if self.curChar == '<':
                if self.peek() == '=':
                    self.nextChar()
                    self.nextChar()
                    return Token(LTEQ, '<=')
                elif self.peek() == '>':
                    self.nextChar()
                    self.nextChar()
                    return Token(NOTEQ, '!=') # <>
                else:
                    self.nextChar()
                    return Token(LT, '<')

            if self.curChar == '@':
                if self.peek() == '=':
                    self.nextChar()
                    self.nextChar()
                    return Token(POWEREQ, '**=')
                else:
                    self.nextChar()
                    return Token(POWER, '**')
                    
            if self.curChar == '%':
                if self.peek() == '=':
                    self.nextChar()
                    self.nextChar()
                    return Token(MODULOEQ, '%=')
                else:
                    self.nextChar()
                    return Token(MODULO, '%')                    
                    
            if self.curChar == '=':
                self.nextChar()
                return Token(EQEQ, '=')

            if self.curChar == '+':
                if self.peek() == '=':
                    self.nextChar()
                    self.nextChar()
                    return Token(PLUSEQ, '+=')
                else:
                    self.nextChar()
                return Token(PLUS, '+')

            if self.curChar == '-':
                if self.peek() == '=':
                    self.nextChar()
                    self.nextChar()
                    return Token(MINUSEQ, '-=')
                else:
                    self.nextChar()
                return Token(MINUS, '-')

            if self.curChar == '*':
                if self.peek() == '=':
                    self.nextChar()
                    self.nextChar()
                    return Token(MULEQ, '*=')
                else:
                    self.nextChar()
                return Token(MUL, '*')

            if self.curChar == '/':
                if self.peek() == "=":
                    self.nextChar()
                    self.nextChar()
                    return Token(FLOAT_DIVEQ, '/=')
                else:
                    self.nextChar()
                return Token(FLOAT_DIV, '/')

            if self.curChar == '(':
                self.nextChar()
                return Token(LPAREN, '(')

            if self.curChar == ')':
                self.nextChar()
                return Token(RPAREN, ')')

            if self.curChar == ';':
                self.nextChar()
                return Token(SEMI, ';')

            if self.curChar == '.':
                self.nextChar()
                return Token(DOT, '.')

            if self.curChar == ',':
                self.nextChar()
                return Token(COMMA, ',')
  
            if self.curChar == '"':
                self.nextChar()
                return self.Stringlex()  

            self.error()

        return Token(EOF, None)
