from lexer import *

def main():

    text = open("lexer_input.txt","r").read()
    lexer = Lexer(text)
    Token = lexer.get_token()
    while Token.type != EOF:
        print(Token.value, Token.type)
        Token = lexer.get_token()
    print(Token.value, Token.type)         # to check EOF

main()