from dataclasses import dataclass
import sys

# punctuators
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
NOTEQ         = 'NOTEQ'
GT            = 'GT'
LT            = 'LT'
GTEQ          = 'GTEQ'
LTEQ          = 'LTEQ'
MODULO        = 'MODULO'
AND           = "AND"
OR            = "OR"
PLUSEQ        = 'PLUSEQ'
MINUSEQ       = 'MINUSEQ'
POWEREQ       = 'POWEREQ'
MULEQ         = 'MULEQ'
FLOAT_DIVEQ   = "FLOAT_DIVEQ"
POWER         = 'POWER'

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
PRINT         = 'PRINT'
STRING        = 'STRING'
FUNCTION      = 'FUNCTION'
RETURN        = 'RETURN'
FOR           = 'FOR'
RANGE         = "RANGE"
BY            = "BY"
TO            = "TO"
BREAK         = "BREAK"
# literals
TRUE          = "TRUE"
FALSE         = "FALSE"

@dataclass
# class to store the token types and values
class Token:
    type: str
    value: object
    
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
    'FOR': Token('FOR', 'FOR'),
    'TRUE': Token('TRUE', True),
    'FALSE': Token('FALSE', False),
    'IF': Token('IF', 'IF'),
    'THEN': Token('THEN', 'THEN'),
    'ELSE': Token('ELSE', 'ELSE'),
    'PRINT': Token('PRINT', 'PRINT'),
    'WHILE': Token('WHILE', 'WHILE'),
    'DO': Token('DO', 'DO'),
    'STRING': Token('STRING', 'STRING'),
    'FUNCTION': Token('FUNCTION', 'FUNCTION'),
    'RETURN': Token('RETURN', 'RETURN'),
    'BY': Token('BY', 'BY'),
    'TO': Token("TO", "TO"),
    'BREAK': Token("BREAK", "BREAK"),
    # 'PRINT': Token('PRINT', ';'),
    
}


class Lexer(object):
    def __init__(self, text):
        
        self.text = text                        # stream of input
        self.pos = 0                            # current position in the stream
        self.lineNum = 1                        # line number in code
        self.curLinePos = 0                     # current position in current line of program
        if text == "":
            print("Empty Program")
            self.curChar = None
            
        else:
            self.curChar = self.text[self.pos]      # current character in the stream
        self.curLine = self.curChar             # current line of program read till now
        

    def error(self):
        sys.exit('Invalid character')

    def nextChar(self):                         # advances the pos pointer
        self.pos += 1
        self.curLinePos += 1
        
        if self.pos > len(self.text) - 1:       # end of input stream
            self.curChar = None                 
        else:
            self.curChar = self.text[self.pos]
            self.curLine += self.curChar

    def peek(self):                             # returns the lookahead character
        if self.pos + 1 > len(self.text) - 1:
            return None
        else:
            return self.text[self.pos + 1]

    def skipSpaces(self):                       # to skip white spacses
        while self.curChar is not None and self.curChar.isspace():
            if self.curChar == '\n':
                self.lineNum+=1
                self.curLine=""
                self.curLinePos=0
            self.nextChar()

    def skipComments(self):
        # while self.curChar != '}':
        #     self.nextChar()
        # self.nextChar()                         # to skip the closing curly brace as well
        noOfstartBraces = 1
        while noOfstartBraces != 0 :
            self.nextChar()
            if self.curChar == '{':
                noOfstartBraces+=1
            elif self.curChar == '}':
                noOfstartBraces-=1
        self.nextChar()                         # to skip the closing curly brace as well

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
                    return Token(ASSIGN, '=') # :=
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
                
            if self.curChar == "%":
                self.nextChar()
                return Token(MODULO, '%')

            if self.curChar == '=':
                self.nextChar()
                return Token(EQEQ, '==') # =

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