from dataclasses import dataclass
import sys

from lexer import *
# import sim 
from dataclasses_sim import *

@dataclass
class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.curr_token = self.lexer.get_token()
        self.lexer.lineNum = 0

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
        if self.curr_token.type != BEGIN and self.curr_token.type != IF and self.curr_token.type != WHILE and self.curr_token.type != FOR and self.curr_token.type != FUNCTION:
            true = self.parse()
            self.check_type(SEMI)
        else:    
            true = self.parse()
        self.check_type(ELSE)
        while self.curr_token.type == IF:
            self.check_type(IF)
            condition = self.logical()
            self.check_type(THEN)
            if self.curr_token.type != BEGIN and self.curr_token.type != IF and self.curr_token.type != WHILE and self.curr_token.type != FOR and self.curr_token.type != FUNCTION:
                true = self.parse()
                self.check_type(SEMI)
            else:    
                true = self.parse()
            self.check_type(ELSE)
        if self.curr_token.type != END:
            if self.curr_token.type != BEGIN and self.curr_token.type != IF and self.curr_token.type != WHILE and self.curr_token.type != FOR and self.curr_token.type != FUNCTION:
                false = self.parse()
                self.check_type(SEMI)
            else:
                false = self.parse()
        else:
            false = None
        self.check_type(END)
        node = IfElse(condition, true, false)
        return node     
    

    def parse_begin(self):
        """parse_begin : """
        self.check_type(BEGIN)
        if self.curr_token.type == END:
            self.check_type(END)
            return Seq([])
        # s = self.parse_list()
        ignoreSEMI = False
        if self.curr_token.type == IF or self.curr_token.type == WHILE or self.curr_token.type == FOR or self.curr_token.type == FUNCTION or self.curr_token.type == BEGIN:
            ignoreSEMI = True
        e = self.parse()
        if not ignoreSEMI:
            self.check_type(SEMI)
        ignoreSEMI = False
        token = self.curr_token
        Type = token.type
        seq = [e]
        
        while Type != END:
            
            # if self.curr_token.type == END:
            #     break
            
            if self.curr_token.type == IF or self.curr_token.type == WHILE or self.curr_token.type == FOR or self.curr_token.type == FUNCTION or self.curr_token.type == BEGIN:
                ignoreSEMI = True
            e = self.parse()
            if not ignoreSEMI:
                self.check_type(SEMI)
            
            ignoreSEMI = False
            
            seq.append(e)
            token = self.curr_token
            Type = token.type
        
        # if Type == SEMI: 
        #     self.check_type(SEMI)
        self.check_type(END)
        return Seq(seq)
        # return s
    
    def parse_for(self):
        self.check_type(FOR)
        if self.curr_token.type == SEMI:
            start = None
        else:
            start = self.parse()
        # print("Hi", start)
        self.check_type(SEMI)
        if self.curr_token.type == SEMI:
            condition = None
        else:
            condition = self.logical()
        # print("Hi2", end)
        self.check_type(SEMI)
        if self.curr_token.type == DO:
            increment = None
        else:
            increment = self.parse()
        # print("Hi3",jump)
        self.check_type(DO)
        if self.curr_token.type != BEGIN and self.curr_token.type != IF and self.curr_token.type != WHILE and self.curr_token.type != FOR and self.curr_token.type != FUNCTION:
            body = self.parse()
            self.check_type(SEMI)
            self.check_type(END)
            return ForLoop(start, condition, increment, body)
        body = self.parse()
        self.check_type(END)
        return ForLoop(start, condition, increment, body)
    
    def parse_while(self):
        self.check_type(WHILE)
        c = self.logical()
        self.check_type(DO)
        if self.curr_token.type != BEGIN and self.curr_token.type != IF and self.curr_token.type != WHILE and self.curr_token.type != FOR and self.curr_token.type != FUNCTION:
            b = self.parse()
            self.check_type(SEMI)
            self.check_type(END)
            return While(c, b)
        b = self.parse()
        self.check_type(END)
        return While(c, b)
    
    def parse_list_append(self):
        self.check_type(APPEND)
        self.check_type(LPAREN)
        var = self.variable()
        self.check_type(COMMA)
        item = self.parse()
        self.check_type(RPAREN)
        return list_append(var, item)
    

    
    def parse_list_slice(self, c):
     
        self.check_type(LSPAREN)
        if self.curr_token.type==COMMA:
            start = NumLiteral(0)
        else:
            start = self.parse()
        
        if self.curr_token.type==RSPAREN:
            index_type = True
            self.check_type(RSPAREN)

        elif self.curr_token.type==COMMA:
            index_type = False
            self.check_type(COMMA)
            end = self.parse()
        else:
            index_type = False
            end = self.parse()
        
    
        if index_type==False:
            if self.curr_token.type==COMMA:
                self.check_type(COMMA)
                if self.curr_token.type!=RSPAREN:
                    jump = self.parse()   
                else:
                    jump = NumLiteral(1)

            else:
                jump = NumLiteral(1)
            self.check_type(RSPAREN)
        else:
            end = None
            jump = None
        return list_Slicing(c, start, end, jump)



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
    
    def parse_len(self):
        
        self.check_type(LPAREN)
        c = self.parse()
        self.check_type(RPAREN)
        return length(c)
    
    def parse_head(self):
        
        self.check_type(LPAREN)
        c = self.parse()
        self.check_type(RPAREN)
        return list_head(c)
    
    def parse_tail(self):
        
        self.check_type(LPAREN)
        c = self.parse()
        self.check_type(RPAREN)
        return list_tail(c)
    
    def parse_isempty(self):
        
        self.check_type(LPAREN)
        c = self.parse()
        self.check_type(RPAREN)
        return list_isempty(c)
         
    
    def parse_slice(self, c):
     
        self.check_type(LSPAREN)
        if self.curr_token.type==COMMA:
            # self.check_type(COMMA)
            start = NumLiteral(0)
        else:
            start = self.parse()
        
        if self.curr_token.type==RSPAREN:
            index_type = True
            self.check_type(RSPAREN)

        elif self.curr_token.type==COMMA:
            index_type = False
            self.check_type(COMMA)
            if self.curr_token.type!=COMMA:
                end = self.parse()
            else:
                end = None
        else:
            index_type = False
            end = self.parse()
        
    
        if index_type==False:
            if self.curr_token.type==COMMA:
                self.check_type(COMMA)
                if self.curr_token.type!=RSPAREN:
                    jump = self.parse()   
                else:
                    jump = NumLiteral(1)

            else:
                jump = NumLiteral(1)
            self.check_type(RSPAREN)
        else:
            end = None
            jump = None
        return Slicing(c, start, end, jump)
    
   
    def parse_print(self):
        self.check_type(PRINT)
        self.check_type(LPAREN)
        if self.curr_token.type != RPAREN:
            e = self.logical()
        else:
            e = None
        # print(e)
        self.check_type(RPAREN)
        # if self.curr_token.type != END:
        #     e = self.logical()
        # else:
        #     e = None
        # # print(e)
        # self.check_type(END)
        return Statement("print", e)
        
    def parse_return(self):
        self.check_type(RETURN)
        
        e = self.logical()
        return Statement("return", e)
    
    def parse_list(self, Type):
        if Type != LSPAREN:
            # print("ENTER")
            self.check_type(COLON)
            
            token = self.curr_token
            self.check_type(INTEGER)
            Type = token.type
            datatype = Type

            # print(datatype)

        else:
            datatype = NONE


        self.check_type(LSPAREN)
        ele = self.parse()
        value =[ele]
        token = self.curr_token
        Type = token.type

        while Type!= RSPAREN:
            self.check_type(COMMA)
            ele = self.parse()
            value.append(ele)
            token = self.curr_token
            # print(token)
            Type = token.type
        self.check_type(RSPAREN)
        # print(type(datatype))

        # print("done and dusted")

        return Listing(value, datatype)
            



    def parse_func(self):
        self.check_type(FUNCTION)
        # name = self.variable("Variable")
        name = self.variable()
        self.check_type(LPAREN)
        # var = self.variable("Variable")
        var = self.variable()
        token = self.curr_token
        Type = token.type
        params = [var] if var != None else []
        
        while Type != RPAREN:
            self.check_type(COMMA)
            if self.curr_token.type == RPAREN:
                break
            # var = self.variable("Variable")
            var = self.variable()
            
            params.append(var)
            token = self.curr_token
            Type = token.type
        
        self.check_type(RPAREN)
        if self.curr_token.type == BEGIN:
            body = self.parse()
        else:
            self.check_type(BEGIN)
        

        
        
        return Function(name, params, body)

    def parse_func_call(self, n):
        node = n
        self.check_type(LPAREN)
        if self.curr_token.type == RPAREN:
            self.check_type(RPAREN)
            if self.curr_token.type == LPAREN:
                return self.parse_func_call(FunCall(node, []))
            return FunCall(node, [])
        var = self.logical()
        token = self.curr_token
        Type = token.type
        params = [var] if var != None else []
        
        while Type != RPAREN:
            self.check_type(COMMA)
            if self.curr_token.type == RPAREN:
                break
            var = self.logical()
            
            params.append(var)
            token = self.curr_token
            Type = token.type
        
        self.check_type(RPAREN)
        if self.curr_token.type == LPAREN:
            return self.parse_func_call(FunCall(node, params))

        return FunCall(node, params)

    def variable(self, ASTtype=None):
        token = self.curr_token
        Type = token.type
        if Type == ID:
            self.check_type(ID)
            if ASTtype=="Variable":
                token = self.curr_token
                Type = token.type
                #self.parse_slice(Variable(token.value), Type)
                return Variable(token.value)
                
            else:
                return MutVar(token.value)
            
        
    
    def precedence3(self):
        '''precedence3 : INTEGER | LPAREN precedence1 RPAREN | BoolLiteral | Indentifier| (+/-)precedence3 | StringLiteral'''
        token = self.curr_token
        Type = token.type
        if Type == PLUS:
            self.check_type(PLUS)
            node = UnOp(operator=token.value, mid=self.precedence3())
            return node
        elif Type == MINUS:
            self.check_type(MINUS)
            node = UnOp(operator=token.value, mid=self.precedence3())
            return node
        elif Type == LPAREN:
            self.check_type(LPAREN)
            # node = self.precedence1() 
            node = self.logical()
            self.check_type(RPAREN)
            return node
        elif Type == FRACTION_CONST:
            self.check_type(FRACTION_CONST)
            return NumLiteral(token.value)
        elif Type == REAL_CONST:
            self.check_type(REAL_CONST)
            return FloatLiteral(token.value)
        elif Type == INTEGER_CONST:
            self.check_type(INTEGER_CONST)
            return IntLiteral(token.value)        
        elif Type == TRUE or Type == FALSE:
            self.check_type(Type)
            return BoolLiteral(token.value)
        elif Type == LEN:
            self.check_type(LEN)
            return self.parse_len()
        elif Type == HEAD:
            self.check_type(HEAD)
            return self.parse_head
        elif Type == TAIL:
            self.check_type(TAIL)
            return self.parse_tail
        elif Type == ISEMPTY:
            self.check_type(ISEMPTY)
            return self.parse_isempty
        elif Type == LIST:
            self.check_type(LIST)
            if self.curr_token.type == COLON:
                return self.parse_list(self.curr_token.type)
            return self.parse_list(self.curr_token.type)
        elif Type == ID:
            self.check_type(ID)
            if self.curr_token.type == LPAREN:
                return self.parse_func_call(MutVar(token.value))
            elif self.curr_token.type == LSPAREN:
                return self.parse_slice(MutVar(token.value))
            return (MutVar(token.value))
        elif Type == STRING:    
            # Nothing new here, just eat the STRING token and return the String() AST.
            self.check_type(STRING)
            return StringLiteral(token.value)
        
        else:
            # if Type == END:
            #     self.check_type(END)
            #     return
            print("None of the suggested tokens found:", INTEGER_CONST, ID, LPAREN, STRING, TRUE, FALSE, "...")
            self.check_type(INTEGER_CONST)
            
    
        

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
                # print(e)
                l.append(e)
                Type = self.curr_token.type
                # e = self.precedence3()
            # print(l)
            
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
        """precedence2 : precedence3 | precedence3 MUL/DIV precedence3"""
        node = self.exponential()
        token = self.curr_token
        Type = token.type
        while (Type == MUL or  Type ==FLOAT_DIV  or Type == MODULO or Type == INT_DIV):
            token = self.curr_token
            if token.type == MUL:
                self.check_type(MUL)
            elif token.type == FLOAT_DIV:
                self.check_type(FLOAT_DIV)
            elif token.type == INT_DIV:
                self.check_type(INT_DIV)                
            elif token.type == MODULO:
                self.check_type(MODULO)
            elif token.type == INT_DIV:
                self.check_type(INT_DIV)
            node = BinOp(left=node, operator=token.value, right=self.exponential())
            Type = self.curr_token.type
        return node

    def precedence1(self):
        """precedence1 : precedence2 | precedence2 PLUS/MINUS precedence2"""
        node = self.precedence2()
        Type = self.curr_token.type
        while (Type == PLUS or  Type ==MINUS):
            token = self.curr_token
            if token.type == PLUS:
                self.check_type(PLUS)
            elif token.type == MINUS:
                self.check_type(MINUS)
            node = BinOp(left=node, operator=token.value, right=self.precedence2())
            Type = self.curr_token.type
        return node

    # def parse(self):
    #     return self.precedence1()
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
    
    def logical(self, n=None):
        """logical : relational | relational logicalOperator relational"""
        if n == None:
            node = self.relational()
        else:
            node = n
        # node = self.relational()
        Type = self.curr_token.type
        if(Type == OR or Type == AND):
            token = self.curr_token
            if token.type == AND:
                self.check_type(AND)
            elif token.type == OR:
                self.check_type(OR)
            node = BinOp(left=node, operator= token.value, right=self.relational())
        return node
    
    def assignment(self, n=None):
        """assignment : variable ASSIGN relational"""
        if n == None:
            node = self.variable()
        else:
            node = n
        Type = self.curr_token.type
        # token = self.curr_token
        # print(Type)

        
        # if Type == ASSIGN:
        #     self.check_type(ASSIGN)
        #     token = self.curr_token
        #     node = BinOp(left=node, operator=token.value, right=self.logical())
        # else:
        #     if isinstance(node,MutVar):
        #         node = self.logical(Get(node))  
        #     else:
        #         node = self.logical()  
        
        if(Type == ASSIGN or Type == PLUSEQ or Type == MINUSEQ or Type == FLOAT_DIVEQ or Type == MULEQ or Type == POWEREQ):
            token = self.curr_token
            if Type == ASSIGN:
                self.check_type(ASSIGN)
                node = BinOp(left=node, operator= token.value, right=self.logical())
            elif Type == MULEQ:
                self.check_type(MULEQ)
                # print(self.curr_token)
                node = BinOp(left=node, operator= token.value, right=self.logical())
            elif Type == MINUSEQ:
                self.check_type(MINUSEQ)
                # print(self.curr_token)
                node = BinOp(left=node, operator= token.value, right=self.logical())
            elif Type == FLOAT_DIVEQ:
                self.check_type(FLOAT_DIVEQ)
                # print(self.curr_token)
                node = BinOp(left=node, operator= token.value, right=self.logical())
            elif Type == PLUSEQ:
                self.check_type(PLUSEQ)
                # print(self.curr_token)
                node = BinOp(left=node, operator= token.value, right=self.logical())
            elif Type == POWEREQ:
                self.check_type(POWEREQ)
                # print(self.curr_token)
                node = BinOp(left=node, operator= token.value, right=self.logical())
        else:
            if isinstance(node,MutVar):
                node = self.logical(node)  
            else:
                node = self.logical()  

        return node
    

    def parse(self):
        """parse : parse_if | parse_print | parse_begin | assignment"""
        match self.curr_token.type:
            case 'IF':
                return self.parse_if()
            case 'WHILE':
                return self.parse_while()
            case 'FOR':
                return self.parse_for()
            case 'PRINT':
                return self.parse_print()
            case 'RETURN':
                return self.parse_return()
            case 'BEGIN':
                return self.parse_begin()
            case 'FUNCTION':
                return self.parse_func()
            case 'BREAK':
                self.check_type(BREAK)
                return Statement("break",NumLiteral(0))
            case 'INC':
                return self.parse_inc()
            case 'DEC':
                return self.parse_dec()
            case 'APPEND':
                return self.parse_list_append()
            # case 'SEMI':
            #     return
                # return self.parse()
            case _:
                node = self.variable()
                if self.curr_token.type == LPAREN:
                    return self.parse_func_call(node)
                
                # node = MutVar(node.name)
                return self.assignment(node)
