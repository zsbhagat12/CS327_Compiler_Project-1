import streamlit as st
import time
import lexer as lex
# import Parser as prs
from io import StringIO
from sim import *
import time
from streamlit.components.v1 import html

# import sys

st.write("""AZKABAN language""")


file = st.file_uploader("Pick a file")

if file is not None:
    stringio = StringIO(file.getvalue().decode("utf-8"))
    # st.write(stringio)
    string_data = stringio.read()
    # st.write(string_data)
    text = st.text_area('Please Enter Your Code Here', string_data)
else:
    text = st.text_area('Please Enter Your Code Here', "PRINT(3+4);")
# print(text)
start = time.time()
# text = "PRINT 3@(1/2) END"
# text = "3 > 4"
# text = "-2*(1---2)"
# text = "PRINT 2-+ +3 END"
# if len(text) != 0:
text = "BEGIN "+text+" END"

l = lex.Lexer(text)   
p = prs.Parser(l)
i = Interpreter(p)
# print(eval(i))


eval(i) 
st.write("Output:")

# html(open("eval.txt").read(), height=100, scrolling=True)

st.write(open("eval.txt","r").readlines())

st.write("Time taken", time.time()-start)
print("Time taken", time.time()-start)





