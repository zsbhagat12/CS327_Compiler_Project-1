from dataclasses_sim import *

lateBinding = {}
def resolve(program: AST, environment: Environment = None) -> AST:
    if environment is None:
        environment = Environment()
    environment.program = program
    def resolve_(program: AST) -> AST:
        return resolve(program, environment)
    
    match program:
        case IntLiteral(_) as I:
            return I
        case NumLiteral(_) as N:
            return N
        case BoolLiteral(_) as B:
            return B
        case StringLiteral(_) as SL:
            return SL
        case BinOp("=" as aop, MutVar(name) as m, right) :
            r = resolve_(right)
            if not environment.check(name):
                environment.add(name, m)
            else:
                environment.update(name, m)
            # environment.enter_scope()
            m = resolve_(m)
            mutvar = environment.get(name)
            # r = resolve_(right)
            mutvar.put(r)
            
            # environment.exit_scope()
            return BinOp(aop, m, r)
        case BinOp("+="as aop, MutVar(name)as m, right) | BinOp("-="as aop, MutVar(name)as m, right) | BinOp("/="as aop, MutVar(name)as m, right) | BinOp("*="as aop, MutVar(name)as m, right) | BinOp("**="as aop, MutVar(name)as m, right):
            r = resolve_(right)
            if not environment.check(name):
                environment.add(name, m)
            # environment.enter_scope()
            m = resolve_(m)
            mutvar = environment.get(name)
            # r = resolve_(right)
            mutvar.put(r)
            
            # environment.exit_scope()
            return BinOp(aop, m, r)
        case BinOp(o, left, right):
            return BinOp(o, resolve_(left), resolve_(right))
        case UnOp(o, mid):
            return UnOp(o, resolve_(mid))
        case Variable(name):
            return environment.get(name)
        case MutVar(name) as m :
            if not environment.check(name):
                environment.add(name, m)
            return environment.get(name)
        case Let(Variable(name) as v, e1, e2):
            re1 = resolve_(e1)
            environment.enter_scope()
            environment.add(name, v)
            re2 = resolve_(e2)
            environment.exit_scope()
            return Let(v, re1, re2)
        case Statement(command ,statement):
            return Statement(command, resolve_(statement))
                
                
       

        case IfElse(c, b, e):
            return IfElse(resolve_(c), resolve_(b), resolve_(e))
        case LetFun(Variable(name) as v, params, body, expr):
            environment.enter_scope()
            environment.add(name, v)
            environment.enter_scope()
            for param in params:
                environment.add(param.name, param)
            rbody = resolve_(body)
            environment.exit_scope()
            rexpr = resolve_(expr)
            environment.exit_scope()
            return LetFun(v, params, rbody, rexpr)
        case Function(MutVar(name) as m, params , body) | Function(Variable(name) as m, params , body):
            new = False
            # environment.add(name, m)
            if not environment.check(name):
                environment.add(name, m)
                if name in lateBinding:
                    lateBinding[name].fn.id = m.id
                    # lateBinding.pop(name)
                    new = True
            else:   
                if name in lateBinding:
                    lateBinding[name].fn.id = m.id
                    lateBinding[name].fn.put(m.value)
                    lateBinding.pop(name)
                environment.update(name, m)
            mutvar = environment.get(name)
            
            environment.enter_scope()
            # rparams = []
            for param in params:
                environment.add(param.name, param)
        
                # rparams.append(resolve_(param))
            rbody = resolve_(body)
            environment.exit_scope()
            e = FnObject(params, rbody)
            mutvar.put(e)
            if new:
                lateBinding[name].fn.put(e)
                lateBinding.pop(name)
            return Function(mutvar, params, rbody)
        case Seq(things):
            environment.enter_scope()
            v = []
            for thing in things:
                v.append(resolve_(thing))
                
            environment.exit_scope()
            return Seq(v)
        case FunCall(MutVar(name) as m, args):
            if not environment.check(name):
                lateBinding[name] = program
            m = resolve_(m)
            fn = environment.get(name).get()
            m.put(fn)
            argv = []
            
            for arg in args:
                argv.append(resolve_(arg))
            return FunCall(m, argv)
        case FunCall(fn, args):
            rfn = resolve_(fn)
            rargs = []
            for arg in args:
                rargs.append(resolve_(arg))
            return FunCall(rfn, rargs)
        
            
        case While(c, b):
            
            return While(resolve_(c), resolve_(b))
        case ForLoop(start, condition, increment, body):
            return ForLoop(resolve_(start), resolve_(condition), resolve_(increment), resolve_(body))
        
        case Listing(value, datatype):
            for i in range(len(value)):
                value[i] = resolve_(value[i])
            return Listing(value, datatype)
        
        case Slicing(name, start, end, jump):   
            return Slicing(resolve_(name), resolve_(start), resolve_(end), resolve_(jump))
        
        case list_append(MutVar(var), item):
            if not environment.check(var):
                environment.add(var, MutVar(var))
            return list_append(environment.get(var), resolve_(item))
        case list_update(MutVar(var), start, end, jump, item):
            if not environment.check(var):
                environment.add(var, MutVar(var))
            return list_update(environment.get(var), resolve_(start), resolve_(end), resolve_(jump), resolve_(item))


        # case list_index_update(MutVar(var), start, value):
        #     if not environment.check(var):
        #         environment.add(var, MutVar(var))
        #     return list_index_update(environment.get(var), resolve_(start), resolve_(value))
        case length(MutVar(var)):
            if not environment.check(var):
                environment.add(var, MutVar(var))
            return length(resolve_(environment.get(var)))
        case Increment(MutVar(var)):
            return Increment(resolve_(environment.get(var)))
        case Decrement(MutVar(var)):
            return Decrement(resolve_(environment.get(var)))

        


        
# def eval(program: AST, environment: Environment = None) -> Value:
#     if environment is None:
#         environment = Environment()

#     def eval_(program):
#         return eval(program, environment)

#     match program:
#         case NumLiteral(value):
#             return value
#         case Variable(_) as v:
#             return environment.get(v)
#         case Let(Variable(_) as v, e1, e2) | LetMut(Variable(_) as v, e1, e2):
#             v1 = eval_(e1)
#             environment.enter_scope()
#             environment.add(v, v1)
#             v2 = eval_(e2)
#             environment.exit_scope()
#             return v2
#         case BinOp("+", left, right):
#             return eval_(left) + eval_(right)
#         case BinOp("-", left, right):
#             return eval_(left) - eval_(right)
#         case BinOp("*", left, right):
#             return eval_(left) * eval_(right)
#         case BinOp("/", left, right):
#             return eval_(left) / eval_(right)
#         case Put(Variable(_) as v, e):
#             environment.update(v, eval_(e))
#             return environment.get(v)
#         case Get(Variable(_) as v):
#             return environment.get(v)
#         case Seq(things):
#             v = None
#             for thing in things:
#                 v = eval_(thing)
#             return v
#         case LetFun(Variable(_) as v, params, body, expr):
#             environment.enter_scope()
#             environment.add(v, FnObject(params, body))
#             v = eval_(expr)
#             environment.exit_scope()
#             return v
#         case FunCall(Variable(_) as v, args):
#             fn = environment.get(v)
#             argv = []
#             for arg in args:
#                 argv.append(eval_(arg))
#             environment.enter_scope()
#             for param, arg in zip(fn.params, argv):
#                 environment.add(param, arg)
#             v = eval_(fn.body)
#             environment.exit_scope()
#             return v
#     raise InvalidProgram()

def test_resolve():
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    e = Let(Variable.make("a"), NumLiteral(0), Variable.make("a"))
    # pp.pprint(e)
    re = resolve(e)
    # pp.pprint(re)

    e = LetFun(Variable.make("foo"), [Variable.make("a")], FunCall(Variable.make("foo"), [Variable.make("a")]),
               Let(Variable.make("g"), Variable.make("foo"),
                   LetFun(Variable.make("foo"), [Variable.make("a")], NumLiteral(0),
                          FunCall(Variable.make("g"), [NumLiteral(0)]))))
    pp.pprint(e)
    pp.pprint(r := resolve(e))
    print(eval(r))

# test_resolve()