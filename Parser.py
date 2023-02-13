from dataclasses import dataclass
import sys


@dataclass
class AST(object):
   pass

@dataclass
class BinOp(AST):
    op: str
    mid : 'AST'
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
        

@dataclass
class UnOp:
    op: str
    mid: 'AST'
    def __init__(self, mid, op):
        #self.left = left
        self.op = op
        self.mid = mid

@dataclass
class Num(AST):
    def __init__(self, token):
        self.token = token
        self.val = token.val

@dataclass
class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.curr_token = self.lexer.get_next_token()
        
    

    def check_type(self, Type):
        if self.curr_token.type == Type:
            self.curr_token = self.lexer.get_next_token()
        else:
            sys.exit('Invalid character')
            
   
    

    