from dataclasses_sim import *
import Parser as prs
from type_checking import *
import sys

def type_error():
        sys.exit('Dynamic type check error')

# Combining lexer parser
@dataclass
class Interpreter:
    parser: prs.Parser

def eval(program: AST, environment: Environment() = None) -> Value:
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
            print(tree)
            # typecheck(tree)
            return eval(tree)
        
        
        case Statement(command ,statement):
            match command:
                case "print":
                    if isinstance(statement,StringLiteral) :
                        print(eval_string_env(statement))
                    elif isinstance(statement, type(None)):
                        print()
                    else:
                        print(eval_env(statement)) 
                case "return":
                    if isinstance(statement,StringLiteral) :
                        return eval_string_env(statement)
                    else:
                        return eval_env(statement)
                case "break":
                    return "break"    
                
            return 

        case IfElse(c, b, e):
            match eval_env(c):
                case True: 
                    return eval_env(b)
                case False: 
                    if e == None:
                        return
                    return eval_env(e)

        case Put(Variable(name), e):
            environment.update(name, eval_env(e))
            return environment.get(name)
        case Get(Variable(name)):
            return environment.get(name)
        
        case Put(MutVar(name), e):
            MutVar(name).put(eval(e))
            environment.update(name,MutVar(name))
            return MutVar(name).get()
        
        case Get(MutVar(name)):
            return environment.get(name).get()
        
        case Seq(things):
            environment.enter_scope()
            v = None
            for thing in things:
                v = eval_env(thing)
                if v=="break":
                    break
            environment.exit_scope()
            return v
        
        case LetFun(Variable(name), params, body, expr):
            environment.enter_scope()
            environment.add(name, FnObject(params, body))
            v = eval_env(expr)
            environment.exit_scope()
            return v
        
        case FunCall(Variable(name), args):
            fn = environment.get(name)
            argv = []
            for arg in args:
                argv.append(eval_env(arg))
            environment.enter_scope()
            for param, arg in zip(fn.params, argv):
                environment.add(param.name, arg)
            v = eval_env(fn.body)
            environment.exit_scope()
            return v
        
        case FunCall(MutVar(name), args):
            fn = environment.get(name)
            argv = []
            for arg in args:
                argv.append(eval_env(arg))
            environment.enter_scope()
            for param, arg in zip(fn.params, argv):
                if isinstance(param, MutVar):
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

        case Increment(MutVar(name)):
            #print('Hi')
            temp = environment.get(name)
            e = eval_env(temp)
            #print('Hi')
            e = e + eval_env(NumLiteral(1))
            temp.put(e)
            environment.update(name, temp)
            return 
        
        case Decrement(MutVar(name)):
            temp = environment.get(name)
            e = eval_env(temp)
            e = e - eval_env(NumLiteral(1))
            temp.put(e)
            environment.update(name, temp)
            return 
        
        case Str_len(MutVar(name)):
            temp = environment.get(name)
            e = eval_env(temp)
            return len(e)
        
        case Slicing(name, start, end, jump):       
            e1 = eval_env(name)
            e2 = eval_env(start)
            e2 = int(e2)
            if end!=None:
                e3 = eval_env(end)
                e3  = int(e3)

            if jump!=None:
                e4 = eval_env(jump)
                e4  = int(e4)
    
            if end == None and jump!=None:
                e = e1[e2::e4]
            elif jump==None:
                e = e1[e2]
            else:
                e = e1[e2:e3:e4]
            return e
        
        
        case ForLoop(start, condition, increment, body):
            # print("Zeeshan", condition)

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
        

        # def for_loop_helper(en, condition):
        # # print(jump)
        # flag = eval_env(condition)
        # # if(flag < en):
        # #     eval_env(body)
        # #     return for_loop_helper(en, jump)
        # # while(flag != en):
        # #     eval_env(body)
        # #     flag = eval_env(condition)
        # while(eval_env(condition)):
        #     eval_env(body)
        #     eval_env(en)
        # return

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
            environment.add(name, FnObject(params, body))
            # if isinstance(program.name, MutVar):
            #     program.name.put(FnObject(params, body))
            # environment.exit_scope()

            
            return 

        case NumLiteral(val):
            return val
        case BoolLiteral(val):
            return eval_bool_env(program)
        case StringLiteral(val):
            return eval_string_env(program)
        
        
        case Variable(name):
            # print(environment)
            # if name in environment:
            #     return environment[name]
            # raise InvalidProgram()
            return environment.get(name)
        
        # case Let(Variable(name), e1, e2):
        #     v1 = eval_env(e1)
        #     return eval(e2, environment | { name: v1})

        case Let(Variable(name), e1, e2) | LetMut(Variable(name), e1, e2) | Let(MutVar(name), e1, e2):
            # v1 = eval_env(e1)
            # return eval(e2, environment | { name: v1})
            v1 = eval_env(e1)
            environment.enter_scope()
            environment.add(name, v1)
            v2 = eval_env(e2)
            environment.exit_scope()
            return v2
        
        
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


def eval_string(program: AST, environment: Environment() = None) -> str:
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
            return eval_string(tree)
        case StringLiteral(val):
            return val
        case BinOp("=", MutVar(name), val):
            e = eval_string_env(val)
            # program.get_left().put(eval(val))
            if not environment.check(name):
                environment.add(name, MutVar(name))
                mutvar = environment.get(name)
                mutvar.put(e)

            else:
                mutvar = environment.get(name)
                # environment.update(name, MutVar(name))
                mutvar.put(e)
            return
        
        case BinOp("+", left, right):
            return left + right
        # case BinOp("")
        case _:
            return eval_bool_env(program)

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

def test_letmut():
    a = Variable("a")
    b = Variable("b")
    e1 = LetMut(b, NumLiteral(2), Put(a, BinOp("+", Get(a), Get(b))))
    e2 = LetMut(a, NumLiteral(1), Seq([e1, Get(a)]))
    assert eval(e2) == 3

# test_letmut()

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
    e = Seq([p_g, i_g,While(cond, Seq([x3, x4]))])
    eval(e)
    print(p.get(), i.get())

# test_While()

def test_MutVar_Get_Put():
    p = MutVar('p')
    p_g = BinOp("=", p, NumLiteral(1))
    i = MutVar('i')
    i_g = BinOp("=", i, NumLiteral(1))
    e = Seq([p_g, i_g, Statement('print',Get('i')), Statement('print',Get('p')) ])
# test_MutVar_Get_Put()

def test_Function():
    e1 = BinOp("+", NumLiteral(2), NumLiteral(1))
    f1 = Function('add', e1, [])
    e2 = BinOp("-", NumLiteral(2), NumLiteral(1))
    f2 = Function('sub', e2, [])
    eval(f1)
    eval(f2)
    e = Seq([f1,f2,])


# test_Function()

def test_letfun():
    a = Variable("a")
    b = Variable("b")
    f = Variable("f")
    g = BinOp (
        "*",
        FunCall(f, [NumLiteral(15), NumLiteral(2)]),
        FunCall(f, [NumLiteral(12), NumLiteral(3)])
    )
    e = LetFun(
        f, [a, b], BinOp("+", a, b),
        g
    )
    assert eval(e) == (15+2)*(12+3)
    print(eval(e))

# test_letfun()

def test_letfun2():
    fact = Variable("fact")
    g = Variable("g")
    n = Variable("n")
    e2 = LetFun(fact, [n], NumLiteral(0), FunCall(g, [NumLiteral(3)] ))
    e1 = LetFun(g, [n], FunCall(fact, [n]), e2)
    e = LetFun(fact, [n], 
               IfElse(BinOp("==",n,NumLiteral(0)),
                      NumLiteral(1),
                      FunCall(fact, [BinOp("-",n, NumLiteral(1))])), 
                e1)
    print(eval(e))





# test_letfun2()