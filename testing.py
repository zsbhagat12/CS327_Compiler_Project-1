import lexer as lex
# import Parser as prs
from sim import *
import time

# text = "3 > 4"
# text = "-2*(1---2)"
# text = "PRINT 2-+ +3 END"
l = lex.Lexer(text)   
p = prs.Parser(l)
i = Interpreter(p)
# print(eval(i))7

eval(i)


# test_While()
# test_Logic()
# test_resolve()