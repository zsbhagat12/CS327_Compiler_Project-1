from dataclasses import dataclass
from fractions import Fraction
from typing import Union, Mapping, Optional, NewType


@dataclass
class BoolLiteral:
    value: bool
    def __init__(self, *args):
        self.value = bool(*args)
    # type: SimType = BoolType()

@dataclass
class NumLiteral:
    value: Fraction
    # type: SimType = NumType()
    def __init__(self, *args):
        self.value = Fraction(*args)

@dataclass
class StringLiteral:
    value : str
    def __init__(self, *args):
        self.value = str(*args)

@dataclass
class BinOp:
    operator: str
    left: 'AST'
    right: 'AST'


@dataclass
class Variable:
    name: str

@dataclass
class Let:
    var: 'AST'
    e1: 'AST'
    e2: 'AST'

@dataclass
class UnOp:
    operator: str
    mid: 'AST'




AST = NumLiteral | BinOp | Variable | Let | BoolLiteral | UnOp | StringLiteral

Value = Fraction
Val = bool

# Val_string = string

@dataclass
class InvalidProgram(Exception):
    pass

def eval(program: AST, environment: Mapping[str, Value] = None) -> Value:
    if environment is None:
        environment = {}
    match program:
        

        case NumLiteral(val):
            return val
        case Variable(name):
            if name in environment:
                return environment[name]
            raise InvalidProgram()
        case Let(Variable(name), e1, e2):
            v1 = eval(e1, environment)
            return eval(e2, environment | { name: v1})
        
        case BinOp("+", left, right):
            return eval(left, environment) + eval(right, environment)
        case BinOp("-", left, right):
            return eval(left, environment) - eval(right, environment)
        case BinOp("*", left, right):
            return eval(left, environment) * eval(right, environment)
        case BinOp("/", left, right):
            return eval(left, environment) / eval(right, environment)
        case UnOp("-", mid):
            return Fraction(-1)*eval(mid)
        case UnOp("++", mid):
            return eval(mid)+Fraction(1)
        case UnOp("--", mid):
            return eval(mid)-Fraction(1)
        case BinOp("<<", left, right):
            try:
                if(eval(right) < 0):
                    raise InvalidProgram(Exception)
            except InvalidProgram:
                print("Shift operator must be non negative") 
            return int(eval(left, environment)) << int(eval(right, environment))
        case BinOp(">>", left, right):
            try:
                if(eval(right) < 0):
                    raise InvalidProgram(Exception)
            except InvalidProgram:
                print("Shift operator must be non negative") 
            return int(eval(left, environment)) >> int(eval(right, environment))
        case BinOp("|", left, right):
            return eval(left, environment) | eval(right, environment)
        case BinOp("&", left, right):
            return eval(left, environment) & eval(right, environment)
        case BinOp("^", left, right):
            return eval(left, environment) ^ eval(right, environment)
        
    
    raise InvalidProgram()


def eval_string(program: AST) -> str:
    match program:
        case StringLiteral(val):
            return val
        case BinOp("+", left, right):
            return left + right
        # case BinOp("")
    raise InvalidProgram()
    

def eval_bool(program: AST) -> Val:
    match program:
        case BoolLiteral(value):
            return value
        case BinOp(">", left, right):
            return (eval(left)>eval(right))
        case BinOp("<", left, right):
            return (eval(left)<eval(right))
        case BinOp(">=", left, right):
            return (eval(left)>=eval(right))  
        case BinOp("<=", left, right):
            return (eval(left)<=eval(right))  
        case BinOp("!=", left, right):
            return (eval(left)!=eval(right))
        case UnOp("!", mid):
            return (not eval_bool(mid))
        case BinOp("&&", left, right):
            return eval_bool(left) and eval_bool(right)
        case BinOp("||", left, right):
            return eval_bool(left) or eval_bool(right)
    raise InvalidProgram()  


def test_eval():
    e1 = NumLiteral(2)
    e2 = NumLiteral(7)
    e3 = NumLiteral(9)
    e4 = NumLiteral(5)
    e5 = BinOp("+", e2, e3)
    e6 = BinOp("/", e5, e4)
    e7 = BinOp("*", e1, e6)
    assert eval(e7) == Fraction(32, 5)

def test_let_eval():
    a  = Variable("a")
    e1 = NumLiteral(5)
    e2 = BinOp("+", a, a)
    e  = Let(a, e1, e2)
    assert eval(e) == 10
    e  = Let(a, e1, Let(a, e2, e2))
    assert eval(e) == 20
    e  = Let(a, e1, BinOp("+", a, Let(a, e2, e2)))
    assert eval(e) == 25
    e  = Let(a, e1, BinOp("+", Let(a, e2, e2), a))
    assert eval(e) == 25
    e3 = NumLiteral(6)
    e  = BinOp("+", Let(a, e1, e2), Let(a, e3, e2))
    assert eval(e) == 22


def test_Logic():
    x1 = NumLiteral(5)
    x2 = NumLiteral(3)
    x3 = BinOp(">=",x1,x2)
    x4 = BinOp("<",x1,x2)
    x5 = BinOp("+", x1, x2)
    e = BinOp("<<", x1, x2)
    assert eval(e) == 40
    assert eval_bool(x3) == True
    assert eval_bool(x4) == False
    x1 = BoolLiteral(True)
    x2 = BoolLiteral(False)
    e = BinOp("&&", x1, x2)
    # print(e)
    assert eval_bool(e) == False
    e = UnOp("!", BoolLiteral(True))
    # print(eval_bool(e)) 
    assert eval_bool(e) == False  

    # assert eval_bool(e) == False
    # e = UnOp("!", False)
    # assert eval_bool(e) == True

test_Logic()

