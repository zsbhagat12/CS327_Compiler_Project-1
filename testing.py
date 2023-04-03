import lexer as lex
# import Parser as prs
from sim import *
import time

# Combining lexer parser
# text = "IF 2 > 1 THEN 3+5 ELSE 41 END"
# text = "a := 3"
# text = "BEGIN PRINT 4+4 END; PRINT 7 END; END"
# text = """
#         BEGIN 
#             i:=1;
#             j:=1;
#             PRINT i END; 
#             WHILE i<6
#             DO 
#                 BEGIN 
#                 j:=j*i;
#                 i:=i+1;   
#                 PRINT j END;            
#                 PRINT i END;

#                 END
#             END;
#             j:=j*i;
#             PRINT j END;
#         END"""

# text =  """
#         k:="stri";
#         """

# text = "-2*(1---2)"

# text = """PRINT 3 < 6 && 4 < 3 END""" 

    # for i:= 1 to 10 by 1 do writeln(i);
# text = """BEGIN 
#             p:=1;
#             q:=1;
#             FOR i:= 1 TO 1560 BY i := i + 1 
#             DO 
#                 BEGIN 
#                 q:=q*p;
#                 p:=p+1;   
#                 {PRINT p END;}          
#                 PRINT q END;
#                 PRINT i END;
#                 END 
#             END; 
#         END""" 
# text = """BEGIN
#         IF 3 % 4 = 0 || 3 % 5 = 0 THEN BEGIN PRINT 5 END; END ELSE BEGIN PRINT 6 END; END END;
#         IF 3 % 4 = 0 || 5 % 5 = 0 THEN BEGIN PRINT 5 END; END ELSE BEGIN PRINT 6 END; END END;
#         IF 4 % 4 = 0 && 3 % 5 = 0 THEN BEGIN PRINT 5 END; END ELSE BEGIN PRINT 6 END; END END;
#         END
#         """
# text = """
#         BEGIN
#             p := 2;
#            {PRINT 2@3@2 END;}
#             PRINT 4@3@2 END;
#             a:=3@2;
#             {p := p @ 3;}
#             PRINT 4@a END;
#             PRINT a END;
#         END
#         """
start = time.time()

text = open("input.txt","r").read()
# text = "PRINT 3@(1/2) END"
# text = "3 > 4"
# text = "-2*(1---2)"
# text = "PRINT 2-+ +3 END"
# if len(text) != 0:
text = "BEGIN"+text+"END"

l = lex.Lexer(text)   
p = prs.Parser(l)
i = Interpreter(p)
# print(eval(i))

eval(i)
# print(open("eval.txt").read()==open("solution.txt").read())
print("Time taken", time.time()-start)

# test_While()
# test_Logic()
# test_resolve()