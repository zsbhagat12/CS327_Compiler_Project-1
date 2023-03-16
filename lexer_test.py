from lexer import *

def main():

    text = open("lexer_input.txt","r").read()
    # text = "2 + 3 "
    
    lexer = Lexer(text)
    Token = lexer.get_token()
    while Token.type != EOF:
        # print(Token.value, Token.type)
        print(Token.__str__())
        Token = lexer.get_token()
    print(Token.value, Token.type)         # to check EOF

main()
