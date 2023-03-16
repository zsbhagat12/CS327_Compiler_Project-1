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

    def parse(self):
        return self.precedence1()
    
@dataclass 
class Traversal (object):
    def __init__(self, parser):
        self.parser = parser
        
    def travel_node(self, node):
        return (getattr(self, 'Type_operation', self.error))(node)

@dataclass
class Evaluator (Traversal):  
    def Type_operation(self, node):
        if type(node).__name__ == "BinOp":
            if node.op.type == PLUS:
                value = self.travel_node(node.left) + self.travel_node(node.right)
            elif node.op.type == MINUS:
                value = self.travel_node(node.left) - self.travel_node(node.right)
            elif node.op.type == MUL:
                value = self.travel_node(node.left) * self.travel_node(node.right)
            elif node.op.type == DIV:
                value = self.travel_node(node.left) / self.travel_node(node.right)
        
        elif type(node).__name__ == "UnOp":
            if node.op.type == PLUS:
                value = self.visit(node.mid)
            elif node.op.type == MINUS:
                value = -1*self.visit(node.mid)
            
        elif type(node).__name__ == "Num":
            value = node.val
            
        return value
        
  
    
    def error(self):
        sys.exit("Invalid visit")

    def AST_evaluation(self):
        tree = self.parser.parse()
        return self.travel_node(tree)

    
    
    
    
    
    
        
        
