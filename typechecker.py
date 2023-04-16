from dataclasses_sim import *
import Parser as prs
from resolver import *
import sys
import pprint
import copy
pp = pprint.PrettyPrinter()

def type_error():
        sys.exit('static type check error')

# Combining lexer parser
@dataclass
class Interpreter:
    parser: prs.Parser

def tcheck(program: AST, environment: Environment() = None) -> Value:
    if environment is None:
        environment = Environment()
    environment.program = program
    def tcheck_env(program):
        return tcheck(program, environment)
    
    def tcheck_bool_env(program):
        return tcheck_bool(program, environment)
    
    def tcheck_string_env(program):
        return tcheck_string(program, environment)

    match program:
        case Interpreter(p):
            tree = p.parse()
            sys.stdout = open('unresolved_tree', 'w')
            pp = pprint.PrettyPrinter(stream=sys.stdout)
            print("Unresolved Tree:")
            pp.pprint(tree)
            
            if resolverOn:
                tree = resolve(tree)
                sys.stdout = open('resolved_tree', 'w')
                pp = pprint.PrettyPrinter(stream=sys.stdout)
                pp.stream = sys.stdout
                print("Resolved Tree:")
                pp.pprint(tree)

            sys.stdout = open('tcheck.txt', 'w')
            e = tcheck(tree)
            sys.stdout = sys.__stdout__

            return e
        
        
        case Statement(command ,statement):
            match command:
                case "print":
                    # print(statement)
                    if isinstance(statement,StringLiteral) :
                        print(tcheck_string_env(statement))
                    elif isinstance(statement, type(None)):
                        print()
                    elif isinstance(statement, MutVar):
                        e = environment.get(statement.name).get()
                        if isinstance(e, Listing):
                            print(tcheck_env(e))
                        else:
                            print(e)
                    else:
                        e = tcheck_env(statement)
                        if isinstance(e, Listing):
                            print(tcheck_env(e))
                        
                        else:
                            print(e)
                        # print(tcheck_env(statement)) 
                case "return":
                    e = Statement(command, statement)

                    if isinstance(statement,StringLiteral) :
                        
                        e.statement = tcheck_string_env(statement)
                        
                    else:
                        e.statement = tcheck_env(statement)
                    return e
                case "break":
                    return program  
                
            return 

        case IfElse(c, b, e):
            match tcheck_bool_env(c):
                case True: 
                    return tcheck_env(b)
                case False: 
                    if e == None:
                        return
                    return tcheck_env(e)

        case Put(Variable(name), e):
            environment.update(name, tcheck_env(e))
            return environment.get(name)
        case Get(Variable(name)):
            return environment.get(name)
        
        case Put(MutVar(name), e):
            MutVar(name).put(tcheck(e))
            environment.update(name,MutVar(name))
            return MutVar(name).get()
        
        case Get(MutVar(name)):
            return environment.get(name).get()
        
        case Seq(things):
            environment.enter_scope()
            v = None
            for thing in things:
                v = tcheck_env(thing)
                if isinstance(v,Statement):
                    if v.command=="break":
                        break
                    if v.command=="return":
                         return v.statement
            environment.exit_scope()
            return v    
        
        case LetFun(Variable(name), params, body, expr):
            environment.enter_scope()
            environment.add(name, FnObject(params, body))
            v = tcheck_env(expr)
            environment.exit_scope()
            return v
        
        case FunCall(Variable(name), args):
            fn = environment.get(name)
            argv = []
            for arg in args:
                argv.append(tcheck_env(arg))
            environment.enter_scope()
            for param, arg in zip(fn.params, argv):
                environment.add(param.name, arg)
            v = tcheck_env(fn.body)
            environment.exit_scope()
            return v
        
        case FunCall(MutVar(name) as m, args):
            # not (environment.check(name) and environment.get(name) != None)
            if m.value == None and (not environment.check(name) or environment.get(name) == None):
                print(f"Function '{name}' not defined")
                sys.exit()
                # environment.add(name, MutVar(name))
                # environment.get(name).put(FnObject([],None))
            
            m.value = copy.deepcopy(m.value)
            fn = m.value if m.value != None else environment.get(name).get() #fn is FnObject
            # pp = pprint.PrettyPrinter()
            # pp.pprint(fn)
            # pp.pprint(environment.envs)
            # fn = FnObject(fn.params, fn.body)
            argv = []
            mtfo = [] #muttable function object
            for arg in args:
                if arg != None:
                    mtfo.append(arg)
                    #if isinstance(arg, MutVar) and isinstance(arg.value, FnObject):
                        # mtfo[arg.value] = arg
                    argv.append(tcheck_env(arg))
            environment.enter_scope()
            # print(name)
            # print(argv)
            # print(mtfo)
            # print(fn.params)
            # print(fn.body)
            for param, arg in zip(fn.params, argv):
                if isinstance(param, MutVar):
                    if isinstance(arg, FnObject):
                        e = mtfo[argv.index(arg)]
                        if environment.check(e.name):
                            environment.addWithOther(e.name, param.name, None)
                        # param.put(FnObject(arg.params, copy.deepcopy(arg.body)))
                        # param.put(copy.deepcopy(arg))
                        
                    else:
                        environment.add(param.name, param)
                    param.put(arg)
                else:
                    environment.add(param.name, arg)
            # print(fn, id(fn.body))
            v = tcheck_env(fn.body)
            
            environment.exit_scope()
            # print(name, v)
            return v
        
        case FunCall(FunCall(_,_) as funcall, args):
            # print(fncall)
            fn = tcheck_env(funcall)
            
            # not (environment.check(name) and environment.get(name) != None)
            # if m.value == None and (not environment.check(name) or environment.get(name) == None):
            #     print(f"Function '{name}' not defined")
            #     sys.exit()
            #     # environment.add(name, MutVar(name))
            #     # environment.get(name).put(FnObject([],None))
            # m.value = copy.deepcopy(m.value)
            # fn = m.value if m.value != None else environment.get(name).get() #fn is FnObject
            # fn = FnObject(fn.params, fn.body)
            argv = []
            mtfo = [] #muttable function object
            for arg in args:
                if arg != None:
                    mtfo.append(arg)
                    #if isinstance(arg, MutVar) and isinstance(arg.value, FnObject):
                        # mtfo[arg.value] = arg
                    argv.append(tcheck_env(arg))
            environment.enter_scope()
            # print(name)
            # print(argv)
            # print(mtfo)
            # print(fn.params)
            # print(fn.body)
            for param, arg in zip(fn.params, argv):
                if isinstance(param, MutVar):
                    if isinstance(arg, FnObject):
                        e = mtfo[argv.index(arg)]
                        if environment.check(e.name):
                            environment.addWithOther(e.name, param.name, None)
                        # param.put(FnObject(arg.params, copy.deepcopy(arg.body)))
                        # param.put(copy.deepcopy(arg))
                        
                    else:
                        environment.add(param.name, param)
                    param.put(arg)
                else:
                    environment.add(param.name, arg)
            # print(fn, id(fn.body))
            v = tcheck_env(fn.body)
            
            environment.exit_scope()
            return v
        
        case MutVar(name) as m:
            # if program.value != None:
            #     return program.get()
                
            # return
            if not environment.check(name):
                print(environment.envs)
                print(f"Mutable Variable '{name}' not defined")
                sys.exit()
                # environment.add(name, MutVar(name))
            
            # e = m if m.value != None else environment.get(name)
            e = m if environment.get(name).get() == None else environment.get(name)
            # e = environment.get(name)
            v = e.get()
            typesWithNotcheck = Fraction | FnObject | Listing | int | float | str | bool
            # if isinstance(v, Fraction) or isinstance(v, FnObject) or isinstance(v, Listing):
            if isinstance(v, typesWithNotcheck):
                return v
            else:
                v = tcheck_env(v)
                # e.put(v)
                return v

        case Increment(MutVar(name)):
            #print('Hi')
            temp = environment.get(name)
            if str(temp.value.__class__.__name__) != "Fraction" and str(temp.value.__class__.__name__) != "int" and str(temp.value.__class__.__name__) != "float":
                type_error() 
            
            e = tcheck_env(temp)
            #print('Hi')
            e = e + tcheck_env(IntLiteral(1))
            temp.put(e)
            environment.update(name, temp)
            return 
        
        case Decrement(MutVar(name)):
            temp = environment.get(name)
            if str(temp.value.__class__.__name__) != "Fraction" and str(temp.value.__class__.__name__) != "int" and str(temp.value.__class__.__name__) != "float":
                type_error() 

            e = tcheck_env(temp)
            e = e - tcheck_env(NumLiteral(1))
            temp.put(e)
            environment.update(name, temp)
            return 
        
        case length(MutVar(name)):
            temp = environment.get(name).get()
            # e = tcheck_env(temp)
            # return len(e.value)
            if isinstance(temp, Listing):
                return len(temp.value)
            else:
                type_error() 
            return len(temp)

        case list_head(MutVar(name)):
            temp = environment.get(name)
            if isinstance(temp, Listing):
                e = tcheck_env(temp)
                return e[0]
            else:
                type_error()
        
        case list_tail(MutVar(name)):
            temp = environment.get(name)
            if isinstance(temp, Listing):
                e = tcheck_env(temp)
                return e[1:]
            else:
                type_error()
        
        case list_isempty(MutVar(name)):
            temp = environment.get(name)
            if isinstance(temp, Listing):
                e = tcheck_env(temp)
                if len(e)==0:
                    return True
                return False
            else:
                type_error()
        
        case list_append(MutVar(var), item):
            if not environment.check(var):
                print(f"list '{var}' not defined")
                sys.exit()
            temp = environment.get(var).get().value
            if not isinstance(temp, list):
                type_error()
            tp = environment.get(var).get().datatype
            if tp == "INTEGER" and str(tcheck_env(item).__class__.__name__) != "int":
                type_error()
            if tp == "STRING" and str(tcheck_env(item).__class__.__name__) != "str":
                type_error()
            # print(temp.__class__.__name__, l.value.datatype.__class__.__name__, tcheck_env(item).__class__.__name__)
            # if str(l.value.datatype.__class__.__name__) != str(tcheck_env(item).__class__.__name__):
            #     type_error()
            # e1 = tcheck_env(temp)
            # e1.append(tcheck_env(item))
            e1 = temp
            e1.append(item)
            return e1


        
        case Listing(value, datatype):
            if datatype != "NONE":
                if datatype == "INTEGER":
                    temp = IntLiteral
                elif datatype == "STRING":
                    temp = StringLiteral
                elif datatype == "NONE":
                    temp = None
                for i in value:
                    if temp == "INTEGER" and str(tcheck_env(i).__class__.__name__) != "int":
                        type_error()
                    if temp == "STRING" and str(tcheck_env(i).__class__.__name__) != "str":
                        type_error()
                    else:
                        continue
       
            temp =[]
            for i in program.value:
                temp.append(tcheck_env(i))
       

            return temp


        case Slicing(name, start, end, jump):      
             
            e1 = tcheck_env(name)
            if isinstance(e1, Listing):
                e1 = tcheck_env(e1)
            e2 = tcheck_env(start)
            e2 = int(e2)
            if end!=None:
                e3 = tcheck_env(end)
                e3  = int(e3)

            if jump!=None:
                e4 = tcheck_env(jump)
                e4  = int(e4)
    
            if end == None and jump!=None:
                e = e1[e2::e4]
            elif jump==None:
                e = e1[e2]
            else:
                e = e1[e2:e3:e4]
            return e
        
        case list_Slicing(name, start, end, jump):       
            e1 = tcheck_env(name)
            e2 = tcheck_env(start)
            e2 = int(e2)
            if end!=None:
                e3 = tcheck_env(end)
                e3  = int(e3)

            if jump!=None:
                e4 = tcheck_env(jump)
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

            if start != None:
                if not isinstance(start,BinOp):
                    type_error()
                else:
                    if start.operator != "=":
                        type_error()
                tcheck_env(start)
            
            if increment != None:
                if not isinstance(start, BinOp):
                    type_error()
                else:
                    if start.operator not in ["=","+=","-=","*=","/=","**="]:
                        type_error()

            if(condition == None):
                while True:
                    v = tcheck_env(body)
                    if isinstance(v,Statement):
                        if v.command=="break":
                            break
                        if v.command=="return":
                            return v.statement
                    else:
                        if increment != None:
                            tcheck_env(increment)
            else:
                while(tcheck_bool_env(condition)):
                    v = tcheck_env(body)
                    if isinstance(v,Statement):
                        if v.command=="break":
                            break
                        if v.command=="return":
                            return v.statement
                    else:
                        if increment != None:
                            tcheck_env(increment)
            return
        
        case While(c, b):
            while (tcheck_bool_env(c)): # avoid recursion depth
                v = tcheck_env(b)
                if isinstance(v,Statement):
                    if v.command=="break":
                        break
                    if v.command=="return":
                        return v.statement
            return 

        case BinOp("=", MutVar(name) as m, val):
            if (not isinstance(val, Listing)):
                e = tcheck_env(val)
            else:
                e = val

            program.right = val
            # e = tcheck_env(val)
            # program.get_left().put(tcheck(val))
            if not environment.check(name):
                environment.add(name, m)
                mutvar = environment.get(name)
                mutvar.put(e)

            else:
                mutvar = environment.get(name)
                # environment.update(name, MutVar(name))
                mutvar.put(e)
                m.put(e)
            return mutvar.get() #Assignment as expression
        
        case BinOp("+=", MutVar(name) as left, right):
            e = tcheck_env(right) 
            # program.get_left().put(tcheck(val))
            if not environment.check(name):
                environment.add(name, left)
                mutvar = environment.get(name)
                e += mutvar.get()
                mutvar.put(e)

            else:
                if (str(tcheck_env(left).__class__.__name__) == "str" and str(tcheck_env(right).__class__.__name__) != "str") or (str(tcheck_env(left).__class__.__name__) != "str" and str(tcheck_env(right).__class__.__name__) == "str"):
                    type_error()
                if str(tcheck_env(left).__class__.__name__) in ["bool", "Listing"] or str(tcheck_env(right).__class__.__name__) in ["bool", "Listing"]:
                    type_error() 
                mutvar = environment.get(name)
                e += mutvar.get()
                # environment.update(name, MutVar(name))
                mutvar.put(e)
            return mutvar.get() #Assignment as expression
        

        case BinOp("-=", MutVar(name) as left, right) if op in ["-=","*=","/=","**="]:
            e = tcheck_env(val) 
            # program.get_left().put(tcheck(val))
            if not environment.check(name):
                environment.add(name, m)
                mutvar = environment.get(name)
                if op == "-=":
                    e -= mutvar.get()
                if op == "*=":
                    e -= mutvar.get()
                if op == "/=":
                    e -= mutvar.get()
                if op == "**=":
                    e -= mutvar.get()
                mutvar.put(e)

            else:
                if str(tcheck_env(left).__class__.__name__) in ["bool", "str", "Listing"] or str(tcheck_env(right).__class__.__name__) in ["bool", "str", "Listing"]:
                    type_error()
                mutvar = environment.get(name)
                if op == "-=":
                    e -= mutvar.get()
                if op == "*=":
                    e -= mutvar.get()
                if op == "/=":
                    e -= mutvar.get()
                if op == "**=":
                    e -= mutvar.get()
                # environment.update(name, MutVar(name))
                mutvar.put(e)
            return mutvar.get() #Assignment as expression
    
        case Function(MutVar(name) as m, params , body) | Function(Variable(name) as m, params , body):
            # environment.enter_scope()
            # environment.add(name, FnObject(params, body))
            if not environment.check(name):
                environment.add(name, m)
            else:
                environment.update(name, m)
            mutvar = environment.get(name)
            e = FnObject(params, body)
            mutvar.put(e)
            
            # if isinstance(program.name, MutVar):
            #     program.name.put(FnObject(params, body))
            # environment.exit_scope()
            return e

        case NumLiteral(val):
            return val
        case IntLiteral(val):
            return val
        case FloatLiteral(val):
            return val
        case BoolLiteral(val):
            return tcheck_bool_env(program)
        case StringLiteral(val):
            return tcheck_string_env(program)
        
        
        case Variable(name):
            # print(environment)
            # if name in environment:
            #     return environment[name]
            # raise InvalidProgram()
            return environment.get(name)
        
        # case Let(Variable(name), e1, e2):
        #     v1 = tcheck_env(e1)
        #     return tcheck(e2, environment | { name: v1})

        case Let(Variable(name), e1, e2) | LetMut(Variable(name), e1, e2) | Let(MutVar(name), e1, e2):
            # v1 = tcheck_env(e1)
            # return tcheck(e2, environment | { name: v1})
            v1 = tcheck_env(e1)
            environment.enter_scope()
            environment.add(name, v1)
            v2 = tcheck_env(e2)
            environment.exit_scope()
            return v2
        
        case BinOp(op, left, right) if op in ["+","-","*","/","//","%","**"]:
            tcheck_env(left)
            tcheck_env(right)
            if op == "+":
                if (str(tcheck_env(left).__class__.__name__) == "str" and str(tcheck_env(right).__class__.__name__) != "str") or (str(tcheck_env(left).__class__.__name__) != "str" and str(tcheck_env(right).__class__.__name__) == "str"):
                    type_error()
                if str(tcheck_env(left).__class__.__name__) in ["bool", "Listing"] or str(tcheck_env(right).__class__.__name__) in ["bool", "Listing"]:
                    type_error()                
                return tcheck_env(left) + tcheck_env(right)    
            else:            
                if str(tcheck_env(left).__class__.__name__) in ["bool", "str", "Listing"] or str(tcheck_env(right).__class__.__name__) in ["bool", "str", "Listing"]:
                    type_error()
                if op == "-":
                    return tcheck_env(left) - tcheck_env(right)
                if op == "*":
                    return tcheck_env(left) * tcheck_env(right)
                if op == "/":
                    if isinstance(tcheck_env(left), int) and isinstance(tcheck_env(right), int):
                        return tcheck_env(left) // tcheck_env(right)
                    else:
                        return tcheck_env(left) / tcheck_env(right)
                if op == "//":
                    return tcheck_env(left) // tcheck_env(right) 
                if op == "%":
                    return tcheck_env(left) % tcheck_env(right)  
                if op == "**":
                    return tcheck_env(left) ** tcheck_env(right)   

        case UnOp(op, mid) if op in ["+","-"]:
            tcheck_env(mid)
            if str(tcheck_env(mid).__class__.__name__) in ["bool", "str", "Listing"]:
                type_error()
            if op == "-":
                return -1*tcheck_env(mid)
            if op == "+":
                return tcheck_env(mid)  
        case _:
            return tcheck_string_env(program)

    raise InvalidProgram()


def tcheck_string(program: AST, environment: Environment() = None) -> str:
    if environment is None:
        environment = Environment()

    def tcheck_env(program):
        return tcheck(program, environment)
    
    def tcheck_bool_env(program):
        return tcheck_bool(program, environment)
    
    def tcheck_string_env(program):
        return tcheck_string(program, environment)

    match program:
        
        case StringLiteral(val):
            return val
        case BinOp("=", MutVar(name), val):
            e = tcheck_string_env(val)
            # program.get_left().put(tcheck(val))
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
            return tcheck_bool_env(program)

    raise InvalidProgram()
    

def tcheck_bool(program: AST, environment: Environment() = None) -> Val:
    if environment is None:
        environment = Environment()

    def tcheck_env(program):
        return tcheck(program, environment)
    def tcheck_bool_env(program):
        return tcheck_bool(program, environment)
    
    def tcheck_string_env(program):
        return tcheck_string(program, environment)
    match program:
        case BoolLiteral(value):
            return value
        case NumLiteral(value):
            type_error()
        case FloatLiteral(value):
            type_error()
        case IntLiteral(value):
            type_error()     
        case StringLiteral(value):
            type_error()                    
        case BinOp(op, left, right) if op in ["+","-","*","/","//","@","%"]:
            type_error()
        case UnOp(op,mid) if op in ["+","-","++","--","<<",">>"]:
            type_error()
        case BinOp(op, left, right) if op in ["==", "<", ">", ">=", "<=", "!="]:
            tcheck_env(left)
            tcheck_env(right)
            if (isinstance(tcheck_env(left), str) and not isinstance(tcheck_env(right), str)) or (not isinstance(tcheck_env(left), str) and isinstance(tcheck_env(right), str)):
                type_error()
            if (isinstance(tcheck_env(left), bool) or isinstance(tcheck_env(right), bool)):
                type_error()   
            if op == "==":         
                return (tcheck_env(left)==tcheck_env(right))
            if op == ">":         
                return (tcheck_env(left)>tcheck_env(right))
            if op == "<":         
                return (tcheck_env(left)<tcheck_env(right))
            if op == ">=":         
                return (tcheck_env(left)>=tcheck_env(right))
            if op == "<=":         
                return (tcheck_env(left)<=tcheck_env(right))
            if op == "!=":         
                return (tcheck_env(left)!=tcheck_env(right))
           
        case UnOp("!", mid):
            tcheck_env(mid)
            if str(tcheck_env(left).__class__.__name__) != "bool":
                type_error
            return (not tcheck_env(mid))
        
        case BinOp(op, left, right) if op in ["&&", "||"]:
            tcheck_env(left)
            tcheck_env(right)
            if str(tcheck_env(left).__class__.__name__) != "bool" or str(tcheck_env(right).__class__.__name__) != "bool":
                    type_error()  
            if op =="&&":
                return tcheck_env(left) and tcheck_env(right)
            else:      
                return tcheck_env(left) or tcheck_env(right) 
        
    sys.stdout = open('error_in_sim', 'w')    
    pp = pprint.PrettyPrinter(stream=sys.stdout)
    print("Current AST")   
    pp.pprint(program)
    
    print("Current Environment:")
    
    pp.pprint( environment.envs)
    raise InvalidProgram()