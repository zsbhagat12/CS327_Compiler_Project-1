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
        
    def unary_check(self):  #still to be implemented
        node = self.precedence3()
        token = self.current_token
        Type = token.type
        if Type == MINUS or Type == PLUS:
            self.eat(Type)
            node = UnOp(mid = node, op = token)
            
        return node

    def check_type(self, Type):
        if self.curr_token.type == Type:
            self.curr_token = self.lexer.get_next_token()
        else:
            sys.exit('Invalid character')
            
    def parse_print(self):
        self.check_type(PRINT)
        # node = self.logical()
        # if self.curr_token.type == LPAREN:
        #     if isinstance(node, f):
        #         node = node.var
        #     e = self.parse_func_call(node)
        # else:
        #     e = self.logical(node)
        if self.curr_token.type != END:
            e = self.logical()
        else:
            e = None
        # print(e)
        self.check_type(END)
        return Statement("print", e)
       
   
    def precedence3(self):
        token = self.curr_token
        Type = token.type
        if Type == LPAREN:
            self.check_type(LPAREN)
            node = self.precedence1()
            self.check_type(RPAREN)
            return node
        elif Type == INTEGER:
            self.check_type(INTEGER)
            return Num(token)

    def precedence2(self):
        node = self.precedence3()
        token = self.curr_token
        Type = token.type
        while (Type == MUL or  Type ==DIV):
            token = self.curr_token
            if token.type == MUL:
                self.check_type(MUL)
            elif token.type == DIV:
                self.check_type(DIV)
            node = BinOp(left=node, op=token, right=self.precedence3())
            Type = self.curr_token.type
        return node

    def precedence1(self):
        node = self.precedence2()
        Type = self.curr_token.type
        while (Type == PLUS or  Type ==MINUS):
            token = self.curr_token
            if token.type == PLUS:
                self.check_type(PLUS)
            elif token.type == MINUS:
                self.check_type(MINUS)
            node = BinOp(left=node, op=token, right=self.precedence2())
            Type = self.curr_token.type
        return node
   
   def relational(self, n=None):
        """relational : precedence1 | precedence1 relationalOperator precedence1"""
        if n == None:
            node = self.precedence1()
        else:
            node = n
        Type = self.curr_token.type
        # print(Type)
        # while(Type == GT or Type == GTEQ or Type == LT or Type == LTEQ):
        if(Type == GT or Type == GTEQ or Type == LT or Type == LTEQ or Type == EQEQ or Type == NOTEQ):
            token = self.curr_token
            if token.type == GT:
                self.check_type(GT)
            elif token.type == GTEQ:
                self.check_type(GTEQ)
            elif token.type == LT:
                self.check_type(LT)
            elif token.type == LTEQ:
                self.check_type(LTEQ)
            elif token.type == EQEQ:
                self.check_type(EQEQ)
            elif token.type == NOTEQ:
                self.check_type(NOTEQ)
            node = BinOp(left=node, operator=token.value, right=self.precedence1())
        # Type = self.curr_token.type
        return node

    def parse(self):
        return self.precedence1()
    
