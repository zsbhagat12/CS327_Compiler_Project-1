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
            self.curr_token = self.lexer.get_token()
        else:
            print("Expected Token Type: ", Type)
            print("Got Token: ", self.curr_token)
            print("At line number:", self.lexer.lineNum)
            print(self.lexer.curLine)
            print(" "*(self.lexer.curLinePos-1),"^")
            sys.exit('Invalid character')
            
    def parse_if(self):
        
        self.check_type(IF)
        condition = self.logical()
        self.check_type(THEN)
        true = self.parse()
        self.check_type(ELSE)
        false = self.parse()
        self.check_type(END)
        node = IfElse(condition, true, false)
        return node 
   
    def parse_inc(self):
        self.check_type(INC)
        self.check_type(LPAREN)
        c = self.parse()
        self.check_type(RPAREN)
        return Increment(c)

    def parse_dec(self):
        self.check_type(DEC)
        self.check_type(LPAREN)
        c = self.parse()

        self.check_type(RPAREN)
        return Decrement(c)
    
    def parse_return(self):
        self.check_type(RETURN)
        e = self.logical()
        return Statement("return", e)
            
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
    
    def exponential(self):
        """exponential : precedence3 | precedence3 POWER precedence3"""
        node = self.precedence3()
        token = self.curr_token
        Type = token.type
        l = [node]
        if Type == POWER:
            while (Type == POWER):
                token = self.curr_token
                if token.type == POWER:
                    self.check_type(POWER)
                e = self.precedence3()
                l.append(e)
                Type = self.curr_token.type
            
            i = 1
            while len(l) > 0 :
                e = l.pop()
                if i==1:
                    
                    node = BinOp(left=l.pop(), operator=token.value, right=e)
                else:
                    node = BinOp(left=e, operator=token.value, right=node)
                i+=1
            
        return node

    def precedence2(self):
        node = self.exponential()
        token = self.curr_token
        Type = token.type
        while (Type == MUL or  Type ==DIV):
            token = self.curr_token
            if token.type == MUL:
                self.check_type(MUL)
            elif token.type == DIV:
                self.check_type(DIV)
            node = BinOp(left=node, op=token, right=self.exponential())
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

    def parse(self):
        match self.curr_token.type:
           case 'IF':
               return self.parse_if()
           case 'RETURN':
                return self.parse_return()
           case 'BEGIN':
                return self.parse_begin()
           case 'BREAK':
                self.check_type(BREAK)
                return Statement("break",NumLiteral(0))
           case 'INC':
                return self.parse_inc()
           case 'DEC':
                return self.parse_dec()
           case _:
               self.precedence1()
    

    
    
    
    
    
    
        
        
