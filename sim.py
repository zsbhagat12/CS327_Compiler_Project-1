from dataclasses import dataclass
from fractions import Fraction
from typing import Union, Mapping, Optional, NewType, List


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
    def get_left(self):
        return self.left
    def get_right(self):
        return self.right


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

@dataclass
class Statement:
    command: str
    statement : "AST"

@dataclass
class IfElse:
    condition: 'AST'
    then_body: 'AST'
    else_body: 'AST' 

@dataclass
class Seq:
    statement1: 'AST'
    statement2: 'AST'

@dataclass
class MutVar:
    name: str
    value: 'AST'
    def __init__(self, name) -> None:
        self.value = None
        self.name = name
    def get(self):
        return self.value
    def put(self, val):
        self.value = val


@dataclass
class While:
    condition: 'AST'
    body: 'AST'

@dataclass
class Function:
    name: str
    body: 'AST'
    params: dict

@dataclass
class CallStack:
    clstk: List

    

class Environment:
    envs: List

    def __init__(self):
        self.envs = [{}]

    def enter_scope(self):
        self.envs.append({})

    def exit_scope(self):
        assert self.envs
        self.envs.pop()

    def add(self, name, value):
        assert name not in self.envs[-1]
        self.envs[-1][name] = value

    def get(self, name):
        for env in reversed(self.envs):
            if name in env:
                return env[name]
        raise KeyError()

    def update(self, name, value):
        for env in reversed(self.envs):
            if name in env:
                env[name] = value
                return
        raise KeyError()

AST = NumLiteral | BinOp | Variable | Let | BoolLiteral | UnOp | Statement | StringLiteral | IfElse | MutVar | While | Seq | Function

Value = Fraction
Val = bool

# Val_string = string

@dataclass
class InvalidProgram(Exception):
    pass

def eval(program: AST, environment: Mapping[str, Value] = None) -> Value:
    if environment is None:
        environment = {}
        
    def eval_env(program):
        return eval(program, environment)
    def eval_bool_env(program):
        return eval_bool(program, environment)
    
    def eval_string_env(program):
        return eval_string(program, environment)
    match program:
        
        case Statement(command , statement):
            match command:
                case "print":
                    if isinstance(statement,StringLiteral) :
                        print(eval_string(statement))
                    else:
                        print(eval(statement)) 
            return 

        case IfElse(c, b, e):
            match eval_bool(c):
                case True: 
                    return eval(b)
                case False: 
                    return eval(e)
            
        case Seq(s1, s2):
            s1 = eval(s1)
            s2 = eval(s2)
            return 
		
		case FunCall(MutVar(name), args):
            if not environment.check(name):
                environment.add(name, MutVar(name))
                environment.get(name).put(FnObject([],None))
            fn = environment.get(name).get()
            argv = []
            mtfo = []
            for arg in args:
                if arg != None:
                    mtfo.append(arg)
                    #if isinstance(arg, MutVar) and isinstance(arg.value, FnObject):
                        # mtfo[arg.value] = arg
                    argv.append(eval_env(arg))
            environment.enter_scope()
            
            for param, arg in zip(fn.params, argv):
                if isinstance(param, MutVar):
                    if isinstance(arg, FnObject):
                        e = mtfo[argv.index(arg)]
                        if environment.check(e.name):
                            environment.addWithOther(e.name, param.name, arg)
                    else:
                        environment.add(param.name, param)
                        param.put(arg)
                else:
                    environment.add(param.name, arg)
            v = eval_env(fn.body)
            
            environment.exit_scope()
            return v
        case MutVar(name):
            # if program.value != None:
            #     return program.get()
            # return
            return environment.get(name).get()
        
        case ForLoop(start, condition, increment, body):
#             print("Zeeshan", condition)

            eval_env(start)
            if(condition == None):
                while True:
                    e = eval_env(body)
                    if e == "break":
                        break
                    else:
                        eval_env()
            else:
                while(eval_env(condition)):
                    e = eval_env(body)
                    if e == "break":
                        break
                    else:
                        eval_env(increment)
                return
        


        case While(c, b):
            # if eval_bool_env(c):
            #     eval_env(b)
            #     eval_env(While(c, b))
            while (eval_env(c)): # avoid recursion depth
                e = eval_env(b)
                if e == "break":
                    break
            return 

        case BinOp("=", MutVar(name), val):
            e = eval_env(val)
            # program.get_left().put(eval(val))
            if not environment.check(name):
                environment.add(name, MutVar(name))
                mutvar = environment.get(name)
                mutvar.put(e)

            else:
                mutvar = environment.get(name)
                # environment.update(name, MutVar(name))
                mutvar.put(e)
            return mutvar.get() #Assignment as expression
        
        case BinOp("+=", MutVar(name), val):
            e = eval_env(val) 
            # program.get_left().put(eval(val))
            if not environment.check(name):
                environment.add(name, MutVar(name))
                mutvar = environment.get(name)
                e += mutvar.get()
                mutvar.put(e)

            else:
                mutvar = environment.get(name)
                e += mutvar.get()
                # environment.update(name, MutVar(name))
                mutvar.put(e)
            return mutvar.get() #Assignment as expression
        

        case BinOp("-=", MutVar(name), val):
            e = eval_env(val) 
            # program.get_left().put(eval(val))
            if not environment.check(name):
                environment.add(name, MutVar(name))
                mutvar = environment.get(name)
                e -= mutvar.get()
                mutvar.put(e)

            else:
                mutvar = environment.get(name)
                e -= mutvar.get()
                # environment.update(name, MutVar(name))
                mutvar.put(e)
            return mutvar.get() #Assignment as expression
        

    
        case BinOp("/=", MutVar(name), val):
            e = eval_env(val) 
            # program.get_left().put(eval(val))
            if not environment.check(name):
                environment.add(name, MutVar(name))
                mutvar = environment.get(name)
                e /= mutvar.get()
                mutvar.put(e)

            else:
                mutvar = environment.get(name)
                e /= mutvar.get()
                # environment.update(name, MutVar(name))
                mutvar.put(e)
            return mutvar.get() #Assignment as expression
        

        case BinOp("**=", MutVar(name), val):
            e = eval_env(val) 
            # program.get_left().put(eval(val))
            if not environment.check(name):
                environment.add(name, MutVar(name))
                mutvar = environment.get(name)
                e **= mutvar.get()
                mutvar.put(e)

            else:
                mutvar = environment.get(name)
                e **= mutvar.get()
                # environment.update(name, MutVar(name))
                mutvar.put(e)
            return mutvar.get() #Assignment as expression
        

        case Function(MutVar(name), params , body) | Function(Variable(name), params , body):
            # environment.enter_scope()
            # environment.add(name, FnObject(params, body))
            if not environment.check(name):
                environment.add(name, MutVar(name))
            else:
                environment.update(name, MutVar(name))
            mutvar = environment.get(name)
            e = FnObject(params, body)
            mutvar.put(e)
            
            # if isinstance(program.name, MutVar):
            #     program.name.put(FnObject(params, body))
            # environment.exit_scope()

            
            return e

        case NumLiteral(val):
            return val
        case Variable(name):
            if name in environment:
                return environment[name]
            raise InvalidProgram()
        
        case Let(Variable(name), e1, e2):
            v1 = eval(e1, environment)
            return eval(e2, environment | { name: v1})
        case Let(MutVar(name), e1, e2):
            v1 = eval(e1, environment)
            return eval(e2, environment | { name: v1})
                case BinOp("+", left, right):
            # if (isinstance(right, NumLiteral) == False):
            #     type_error()
            return eval_env(left) + eval_env(right)
        
        case BinOp("-", left, right):
            return eval_env(left) - eval_env(right)
        case BinOp("*", left, right):
            return eval_env(left) * eval_env(right)
        case BinOp("/", left, right):
            return eval_env(left) / eval_env(right)
        case BinOp("%", left, right):
            return eval_env(left) % eval_env(right)
        case UnOp("-", mid):
            return Fraction(-1)*eval(mid)
        case UnOp("+", mid):
            return eval(mid)
        case UnOp("++", mid):
            return eval_env(mid)+Fraction(1)
        case UnOp("--", mid):
            return eval_env(mid)-Fraction(1)
        case BinOp("<<", left, right):
            try:
                if(eval_env(right) < 0):
                    raise InvalidProgram(Exception)
            except InvalidProgram:
                print("Shift operator must be non negative") 
            return int(eval_env(left)) << int(eval_env(right))
        case BinOp(">>", left, right):
            try:
                if(eval_env(right) < 0):
                    raise InvalidProgram(Exception)
            except InvalidProgram:
                print("Shift operator must be non negative") 
            return int(eval_env(left)) >> int(eval_env(right))
        case BinOp("|", left, right):
            return eval_env(left) | eval_env(right)
        case BinOp("&", left, right):
            return eval_env(left) & eval_env(right)
        case BinOp("^", left, right):
            return eval_env(left) ^ eval_env(right)
        case BinOp("**", left, right):
            return eval_env(left) ** eval_env(right)
        case _:
            return eval_string_env(program)
        
    
    raise InvalidProgram()


def eval_string(program: AST) -> str:
    
    def eval_env(program):
        return eval(program, environment)
    def eval_bool_env(program):
        return eval_bool(program, environment)
    
    def eval_string_env(program):
        return eval_string(program, environment)
    
    match program:
        case StringLiteral(val):
            return val
        case BinOp("+", left, right):
            return left + right
        
        case _:
            return eval_bool_env(program)

        # case BinOp("")
    raise InvalidProgram()
    

def eval_bool(program: AST, environment: Environment() = None) -> Val:
    if environment is None:
        environment = Environment()

    def eval_env(program):
        return eval(program, environment)
    def eval_bool_env(program):
        return eval_bool(program, environment)
    
    def eval_string_env(program):
        return eval_string(program, environment)
    match program:
        case Interpreter(p):
            tree = p.parse()
            # print(tree)
            return eval_bool(tree)
        case BoolLiteral(value):
            return value
        case BinOp("==", left, right):
            return (eval_env(left)==eval_env(right))
        case BinOp(">", left, right):
            return (eval_env(left)>eval_env(right))
        case BinOp("<", left, right):
            return (eval_env(left)<eval_env(right))
        case BinOp(">=", left, right):
            return (eval_env(left)>=eval_env(right))  
        case BinOp("<=", left, right):
            return (eval_env(left)<=eval_env(right))  
        case BinOp("!=", left, right):
            return (eval_env(left)!=eval_env(right))
        case UnOp("!", mid):
            return (not eval_env(mid))
        case BinOp("&&", left, right):
            return eval_env(left) and eval_env(right)
        case BinOp("||", left, right):
            return eval_env(left) or eval_env(right) 
        
    print("Current AST", program)   
    print("Current Environment", environment.envs)
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

# test_let_eval()

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
    e = Statement("print", x5)
    eval(e)

    e = Statement("print",StringLiteral("karthikeya"))
    eval(e)

    # print("print(\"karthikeya\")".split())
    # print("")

# test_Logic()

def test_IfElse():
    a = NumLiteral(2)
    b = NumLiteral(5)
    c = Variable('c')
    x1 = BinOp("==", a, b)
    x2 = Let(c,BinOp("+", a, b),c)
    x3 = Let(c,BinOp("*", a, b),c)
    e1 = IfElse(x1, x2, x3)
    print(eval(e1))
    # print(eval(c))

# test_IfElse()

def test_While():
    p = MutVar('p')
    p_g = BinOp("=", p, NumLiteral(1))
    i = MutVar('i')
    i_g = BinOp("=", i, NumLiteral(1))
    
    # print(p.get(), i.get())
    cond = BinOp("<=", i, NumLiteral(10))
    x1 = BinOp("*", p, i)
    x2 = BinOp("+", i, NumLiteral(1))
    x3 = BinOp("=", p, x1)
    x4 = BinOp("=", i, x2)
    e = Seq(Seq(p_g, i_g),While(cond, Seq(x3, x4)))
    eval(e)
    print(p.get(), i.get())

# test_While()

def test_Function():
    e1 = BinOp("+", NumLiteral(2), NumLiteral(1))
    f1 = Function('add', e1, [])
    e2 = BinOp("-", NumLiteral(2), NumLiteral(1))
    f2 = Function('sub', e2, [])
    eval(f1)
    eval(f2)
    e = Seq(f1,Seq(f2,Seq()))

test_Function()
