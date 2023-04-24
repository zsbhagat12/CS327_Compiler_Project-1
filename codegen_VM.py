from dataclasses_sim import *
import Parser as prs
from type_checking import *
from resolver import *
import sys
import pprint

stack_VM_On = False # set to False to turn off stack VM


@dataclass
class Compiler:
    parser: prs.Parser

@dataclass
class Executor:
    parser: prs.Parser

@dataclass
class CompiledFunction:
    entry: int

class RunTimeError(Exception):
    pass

class BUG(Exception):
    pass

@dataclass
class Label:
    target: int

class I:
    """The instructions for our stack VM."""
    @dataclass
    class PUSH:
        what: Value

    @dataclass
    class UMINUS:
        pass

    @dataclass
    class ADD:
        pass

    @dataclass
    class SUB:
        pass

    @dataclass
    class MUL:
        pass

    @dataclass
    class DIV:
        pass

    @dataclass
    class QUOT:
        pass

    @dataclass
    class REM:
        pass

    @dataclass
    class EXP:
        pass

    @dataclass
    class EQ:
        pass

    @dataclass
    class NEQ:
        pass

    @dataclass
    class LT:
        pass

    @dataclass
    class GT:
        pass

    @dataclass
    class LE:
        pass

    @dataclass
    class GE:
        pass

    @dataclass
    class JMP:
        label: Label

    @dataclass
    class JMP_IF_FALSE:
        label: Label

    @dataclass
    class JMP_IF_TRUE:
        label: Label

    @dataclass
    class NOT:
        pass

    @dataclass
    class DUP:
        pass

    @dataclass
    class POP:
        pass

    @dataclass
    class LOAD:
        fdepth: int
        localID: int

    @dataclass
    class STORE:
        fdepth: int
        localID: int
    
    @dataclass
    class PUSHFN:
        entry: Label

    @dataclass
    class CALL:
        pass

    @dataclass
    class RETURN:
        pass

    @dataclass
    class PRINT:
        pass

    @dataclass
    class LENGTH:
        pass

    @dataclass
    class APPEND:
        pass

    @dataclass
    class SLICE:
        pass

    @dataclass
    class UPDATE:
        pass

    # @dataclass
    # class BREAK:
    #     pass

    # @dataclass
    # class CONTINUE:
    #     pass

    @dataclass
    class HALT:
        pass

Instruction = (
      I.PUSH
    | I.ADD
    | I.SUB
    | I.MUL
    | I.DIV
    | I.QUOT
    | I.REM
    | I.NOT
    | I.UMINUS
    | I.JMP
    | I.JMP_IF_FALSE
    | I.JMP_IF_TRUE
    | I.DUP
    | I.POP
    | I.HALT
    | I.EQ
    | I.NEQ
    | I.LT
    | I.GT
    | I.LE
    | I.GE
    | I.LOAD
    | I.STORE
    | I.PUSHFN
    | I.CALL
    | I.RETURN
    
)

@dataclass
class ByteCode:
    insns: List[Instruction]
    loopTracker: List
    varNameTracker: List
    def __init__(self):
        self.insns = []
        self.loopTracker = []
        self.varNameTracker = {}

    def label(self):
        return Label(-1)

    def emit(self, instruction):
        self.insns.append(instruction)

    def emit_label(self, label):
        label.target = len(self.insns)

def print_bytecode(code: ByteCode):
    for i, insn in enumerate(code.insns):
        match insn:
            case I.JMP(Label(offset)) | I.JMP_IF_TRUE(Label(offset)) | I.JMP_IF_FALSE(Label(offset)):
                print(f"{i:=4} {insn.__class__.__name__:<15} {offset}")
            case I.LOAD(localID) | I.STORE(localID):
                print(f"{i:=4} {insn.__class__.__name__:<15} {localID}")
            case I.PUSH(value):
                print(f"{i:=4} {'PUSH':<15} {value}")
            case I.PUSHFN(Label(offset)):
                print(f"{i:=4} {'PUSHFN':<15} {offset}")
            case _:
                print(f"{i:=4} {insn.__class__.__name__:<15}")
class Frame:
    locals: List[Value]
    retaddr: int
    dynamicLink: 'Frame'
    staticLink: 'Frame'

    def __init__(self, retaddr = -1, dynamicLink = None, staticLink = None):
        MAX_LOCALS = 32
        self.locals = [None] * MAX_LOCALS
        self.retaddr = retaddr
        self.dynamicLink = dynamicLink
        self.staticLink = staticLink

class VM:
    bytecode: ByteCode
    ip: int
    data: List[Value]
    currentFrame: Frame
    fdepthCountVal: int
    recursionDepthCountVal: int

    def load(self, bytecode):
        self.bytecode = bytecode
        self.restart()

    def restart(self):
        self.ip = 0
        self.data = []
        self.currentFrame = Frame()
        self.fdepthCountVal = 0
        self.recursionDepthCountVal = 0
    
    def fdepthCount(self):
        count = 0
        frame = self.currentFrame
        while frame != None:
            count += 1
            frame = frame.staticLink
        return count
    
    def recursionDepthCount(self):
        count = 0
        frame = self.currentFrame
        while frame != None:
            count += 1
            frame = frame.dynamicLink
        return count

    def execute(self) -> Value:
        while True:
            assert self.ip < len(self.bytecode.insns)
            match self.bytecode.insns[self.ip]:
                case I.PUSH(val):
                    self.data.append(val)
                    self.ip += 1
                case I.PUSHFN(Label(offset)):
                    self.data.append(CompiledFunction(offset))
                    self.ip += 1
                case I.CALL():
                    self.currentFrame = Frame (
                        retaddr=self.ip + 1,
                        dynamicLink=self.currentFrame,
                        staticLink=self.currentFrame if self.currentFrame.staticLink==None else self.currentFrame.staticLink
                            
                        
                    )
                    self.fdepthCountVal = self.fdepthCount()
                    self.recursionDepthCountVal = self.recursionDepthCount()
                    cf = self.data.pop()
                    self.ip = cf.entry
                case I.RETURN():
                    self.ip = self.currentFrame.retaddr
                    self.currentFrame = self.currentFrame.dynamicLink
                    self.fdepthCountVal = self.fdepthCount()
                    self.recursionDepthCountVal = self.recursionDepthCount()
                case I.UMINUS():
                    op = self.data.pop()
                    self.data.append(-op)
                    self.ip += 1
                case I.ADD():
                    right = self.data.pop()
                    left = self.data.pop()
                    self.data.append(left+right)
                    self.ip += 1
                case I.SUB():
                    right = self.data.pop()
                    left = self.data.pop()
                    self.data.append(left-right)
                    self.ip += 1
                case I.MUL():
                    right = self.data.pop()
                    left = self.data.pop()
                    self.data.append(left*right)
                    self.ip += 1
                case I.DIV():
                    right = self.data.pop()
                    left = self.data.pop()
                    self.data.append(left/right)
                    self.ip += 1
                case I.EXP():
                    right = self.data.pop()
                    left = self.data.pop()
                    self.data.append(left**right)
                    self.ip += 1
                case I.QUOT():
                    right = self.data.pop()
                    left = self.data.pop()
                    if left.denominator != 1 or right.denominator != 1:
                        raise RunTimeError()
                    left, right = int(left), int(right)
                    self.data.append(Fraction(left // right, 1))
                    self.ip += 1
                case I.REM():
                    right = self.data.pop()
                    left = self.data.pop()
                    if left.denominator != 1 or right.denominator != 1:
                        raise RunTimeError()
                    left, right = int(left), int(right)
                    self.data.append(Fraction(left % right, 1))
                    self.ip += 1
                case I.EQ():
                    right = self.data.pop()
                    left = self.data.pop()
                    self.data.append(left==right)
                    self.ip += 1
                case I.NEQ():
                    right = self.data.pop()
                    left = self.data.pop()
                    self.data.append(left!=right)
                    self.ip += 1
                case I.LT():
                    right = self.data.pop()
                    left = self.data.pop()
                    self.data.append(left<right)
                    self.ip += 1
                case I.GT():
                    right = self.data.pop()
                    left = self.data.pop()
                    self.data.append(left>right)
                    self.ip += 1
                case I.LE():
                    right = self.data.pop()
                    left = self.data.pop()
                    self.data.append(left<=right)
                    self.ip += 1
                case I.GE():
                    right = self.data.pop()
                    left = self.data.pop()
                    self.data.append(left>=right)
                    self.ip += 1
                case I.JMP(label):
                    self.ip = label.target
                case I.JMP_IF_FALSE(label):
                    op = self.data.pop()
                    if not op:
                        self.ip = label.target
                    else:
                        self.ip += 1
                case I.JMP_IF_TRUE(label):
                    op = self.data.pop()
                    if op:
                        self.ip = label.target
                    else:
                        self.ip += 1
                case I.NOT():
                    op = self.data.pop()
                    self.data.append(not op)
                    self.ip += 1
                case I.DUP():
                    op = self.data.pop()
                    self.data.append(op)
                    self.data.append(op)
                    self.ip += 1
                case I.POP():
                    self.data.pop()
                    self.ip += 1
                case I.LOAD(fdepth, localID):
                    current_fdepth = self.fdepthCountVal
                    if current_fdepth == fdepth + 1:
                        self.data.append(self.currentFrame.locals[localID])
                    else:
                        frame = self.currentFrame
                        for i in range(current_fdepth - fdepth - 1):
                            frame = frame.staticLink
                        self.data.append(frame.locals[localID])
                    self.ip += 1
                # case I.LOAD(localID):
                #     self.data.append(self.currentFrame.locals[localID])
                #     self.ip += 1
                case I.STORE(fdepth, localID):
                    v = self.data.pop()
                    current_fdepth = self.fdepthCountVal
                    if current_fdepth == fdepth + 1:
                        self.currentFrame.locals[localID] = v
                    else:
                        frame = self.currentFrame
                        for i in range(current_fdepth - fdepth - 1):
                            frame = frame.staticLink
                        frame.locals[localID] = v
                    self.ip += 1
                # case I.STORE(localID):
                #     v = self.data.pop()
                #     self.currentFrame.locals[localID] = v
                #     self.ip += 1
                case I.PRINT():
                    op = self.data.pop()
                    # sys.stdout = open('eval.txt','w')
                    if isinstance(op, tuple):
                        op = list(op)
                    print(op)
                    # sys.stdout = sys.__stdout__
                    self.ip += 1
                case I.LENGTH():
                    op = self.data.pop()
                    self.data.append(len(op))
                    self.ip += 1
                case I.APPEND():
                    e = self.data.pop()
                    listing = self.data.pop()
                    # listing = list(listing)
                    listing.append(e)
                    # tuple concat
                    # listing = listing + (e,)
                    # listing = tuple(listing)
                    self.data.append(listing)
                    self.ip += 1
                case I.SLICE():
                    jump = self.data.pop()
                    end = self.data.pop()
                    start = self.data.pop()
                    listing = self.data.pop()
                    start = int(start)
                    if end != None:
                        end = int(end)
                    if jump != None:
                        jump = int(jump)
                    if end == None and jump!=None:
                        e = listing[start::jump]
                    elif jump==None:
                        e = listing[start]
                    else:
                        e = listing[start:end:jump]
                    # return e
                    self.data.append(e)
                    self.ip += 1
                case I.UPDATE():
                    e = self.data.pop()
                    jump = self.data.pop()
                    end = self.data.pop()
                    start = self.data.pop()
                    listing = self.data.pop()
                    # listing = list(listing)
                    start = int(start)
                    if end != None:
                        end = int(end)
                    if jump != None:
                        jump = int(jump)
                    if end == None and jump!=None:
                        listing[start::jump] = e
                        # tuple concat, consider jump
                        # while start < len(listing):
                        #     listing = listing[:start] + e + listing[start+jump:]
                        #     start += jump

                    # elif jump==None and end!=None:
                    #     # listing[start:end] = e
                    #     # tuple concat 
                    #     listing = listing[:start] + e + listing[end:]

                    elif jump==None:
                        listing[start] = e
                        # in tuple concat
                        # listing = listing[:start] + (e,) + listing[start+1:]
                    
                    else:
                        listing[start:end:jump] = e
                        # tuple concat, consider jump
                        # while start < end:
                        #     listing = listing[:start] + e + listing[start+jump:]
                        #     start += jump

                    # listing = tuple(listing)
                    self.data.append(listing)
                    self.ip += 1
                # case I.BREAK():
                #     # import pdb; pdb.set_trace()

                #     self.ip += 1
                case I.HALT():
                    return self.data.pop()

def codegen(program: AST) -> ByteCode:
    code = ByteCode()
    do_codegen(program, code)
    code.emit(I.HALT())
    return code

def do_codegen (
        program: AST,
        code: ByteCode
) -> None:
    def codegen_(program):
        do_codegen(program, code)

    simple_ops = {
        "+": I.ADD(),
        "-": I.SUB(),
        "*": I.MUL(),
        "/": I.DIV(),
        # "quot": I.QUOT(),
        # "rem": I.REM(),
        "//": I.QUOT(),
        "%": I.REM(),
        "**": I.EXP(),
        "<": I.LT(),
        ">": I.GT(),
        # "≤": I.LE(),
        # "≥": I.GE(),
        "<=": I.LE(),
        ">=": I.GE(),
        "==": I.EQ(),
        # "≠": I.NEQ(),
        "!=": I.NEQ(),
        "not": I.NOT()
    }

    match program:
        case Compiler(p):
            tree = p.parse()
            sys.stdout = open('unresolved_tree', 'w')
            pp = pprint.PrettyPrinter(stream=sys.stdout)
            print("Unresolved Tree:")
            pp.pprint(tree)
            

            if resolverOn:
                init_resolver()
                tree = resolve(tree)
                sys.stdout = open('resolved_tree', 'w')
                pp = pprint.PrettyPrinter(stream=sys.stdout)
                pp.stream = sys.stdout
                print("Resolved Tree:")
                pp.pprint(tree)

            # typecheck(tree)
            sys.stdout = open('eval.txt', 'w')
            # e = codegen_(tree)
            e = codegen_(tree)
            # v = VM()
            # v.load(e)
            # v.execute()
            # sys.stdout = sys.__stdout__

            return e
            
        case Executor(p):
            tree = p.parse()
            sys.stdout = open('unresolved_tree', 'w')
            pp = pprint.PrettyPrinter(stream=sys.stdout)
            print("Unresolved Tree:")
            pp.pprint(tree)
            
            if resolverOn:
                init_resolver()
                tree = resolve(tree)
                sys.stdout = open('resolved_tree', 'w')
                pp = pprint.PrettyPrinter(stream=sys.stdout)
                pp.stream = sys.stdout
                print("Resolved Tree:")
                pp.pprint(tree)

            # typecheck(tree)
            sys.stdout = open('bytecodeList', 'w')
            
            # e = codegen_(tree)
            try:
                e = codegen(tree)
            except:
                sys.stdout = open('error_in_sim', 'w')    
                pp = pprint.PrettyPrinter(stream=sys.stdout)
                print("Current AST")   
                pp.pprint(program)
                
                print("Current Instructions:")
                
                pp.pprint( code.insns)
                raise InvalidProgram() 
            pp = pprint.PrettyPrinter(stream=sys.stdout)
            print("Byte Code List:")
            print("varNameTracker Format: (id, localID): varName")
            pp.pprint(e)
            # print_bytecode(e)
            sys.stdout = open('eval.txt', 'w')
            v = VM()
            v.load(e)
            try:
                v.execute()
                # print(v)
                # sys.stdout = open('error_in_sim', 'w')
                pp.pprint("Data Stack:")
                pp.pprint(v.data)
                pp.pprint("Current Frame Locals:")
                pp.pprint(v.currentFrame.locals)
            except:
                # sys.stdout = open('error_in_sim', 'w')    
                # pp = pprint.PrettyPrinter(stream=sys.stdout)
                # print("Current AST")   
                # pp.pprint(program)
                
                # print("Current Instructions:")
                
                # pp.pprint( code.insns)
                # raise InvalidProgram() 
                pp.pprint("Data Stack:")
                pp.pprint(v.data)
                pp.pprint("Current Frame Locals:")
                pp.pprint(v.currentFrame.locals)
                pp.pprint("Current Instruction Pointer:")
                pp.pprint(v.ip)
                # pass
            sys.stdout = sys.__stdout__

            # return e
            return 
        case NumLiteral(what) | BoolLiteral(what) | StringLiteral(what) | IntLiteral(what) | FloatLiteral(what):
            code.emit(I.PUSH(what))
        # case UnitLiteral():
        #     code.emit(I.PUSH(None))
        case BinOp(op, left, right) if op in simple_ops:
            codegen_(left)
            codegen_(right)
            code.emit(simple_ops[op])
        case BinOp("&&", left, right):
            E = code.label()
            codegen_(left)
            code.emit(I.DUP())
            code.emit(I.JMP_IF_FALSE(E))
            code.emit(I.POP())
            codegen_(right)
            code.emit_label(E)
        case BinOp("||", left, right):
            E = code.label()
            codegen_(left)
            code.emit(I.DUP())
            code.emit(I.JMP_IF_TRUE(E))
            code.emit(I.POP())
            codegen_(right)
            code.emit_label(E)
        case UnOp("-", operand):
            codegen_(operand)
            code.emit(I.UMINUS())
        case Seq(things):
            if not things: raise BUG()
            last, rest = things[-1], things[:-1]
            for thing in rest:
                codegen_(thing)
                # code.emit(I.POP())
            codegen_(last)
        case IfElse(cond, iftrue, iffalse):
            E = code.label()
            F = code.label()
            codegen_(cond)
            code.emit(I.JMP_IF_FALSE(F))
            codegen_(iftrue)
            code.emit(I.JMP(E))
            code.emit_label(F)
            codegen_(iffalse)
            code.emit_label(E)
        case While(cond, body):
            B = code.label()
            E = code.label()
            code.loopTracker.append((B, E))
            code.emit_label(B)
            codegen_(cond)
            code.emit(I.JMP_IF_FALSE(E))
            codegen_(body)
            code.emit(I.JMP(B))
            # code.emit(I.POP())
            code.emit_label(E)
            code.loopTracker.pop()
            # code.emit(I.PUSH(None))
        case ForLoop(start, condition, step, body):
            B = code.label()
            E = code.label()
            code.loopTracker.append((B, E))
            codegen_(start)
            code.emit_label(B)
            if condition == None:
                code.emit(I.PUSH(True))
            else:
                codegen_(condition)
            code.emit(I.JMP_IF_FALSE(E))
            codegen_(body)
            codegen_(step)
            code.emit(I.JMP(B))
            code.emit_label(E)
            code.loopTracker.pop()
            # code.emit(I.PUSH(None))
        case Statement(command, statement):
            if command == "print":
                codegen_(statement)
                # code.emit(I.DUP())
                code.emit(I.PRINT())
                code.emit(I.PUSH(None))
            elif command == "return":
                codegen_(statement)
                code.emit(I.RETURN())
            elif command == "break":
                code.emit(I.JMP(code.loopTracker[-1][1]))
            elif command == "continue":
                code.emit(I.JMP(code.loopTracker[-1][0]))
        case (Variable() as v) | UnOp("!", Variable() as v):
            code.emit(I.LOAD(v.localID))
        case Put(Variable() as v, e):
            codegen_(e)
            code.emit(I.STORE(v.localID))
            code.emit(I.PUSH(None))
        case Let(Variable() as v, e1, e2) | LetMut(Variable() as v, e1, e2):
            codegen_(e1)
            code.emit(I.STORE(v.localID))
            codegen_(e2)
        case LetFun(fv, params, _, body, expr):
            EXPRBEGIN = code.label()
            FBEGIN = code.label()
            code.emit(I.JMP(EXPRBEGIN))
            code.emit_label(FBEGIN)
            for param in reversed(params):
                match param:
                    case TypeAssertion(Variable() as v, _):
                        code.emit(I.STORE(v.localID))
                    case _:
                        raise BUG()
            codegen_(body)
            code.emit(I.PUSH(None))
            code.emit(I.RETURN())
            code.emit_label(EXPRBEGIN)
            code.emit(I.PUSHFN(FBEGIN))
            code.emit(I.STORE(fv.localID))
            codegen_(expr)
        case Function(name, params, body):
            EXPRBEGIN = code.label()
            FBEGIN = code.label()
            code.emit(I.JMP(EXPRBEGIN))
            code.emit_label(FBEGIN)
            for param in reversed(params):
                match param:
                    case MutVar() as m:
                        # code.emit(I.STORE(param.localID))
                        code.emit(I.STORE(param.fdepth, param.localID))
                        code.varNameTracker[(param.id, param.fdepth, param.localID)] = param.name
                    case _:
                        raise BUG()
            codegen_(body)
            code.emit(I.RETURN())
            code.emit_label(EXPRBEGIN)
            code.emit(I.PUSHFN(FBEGIN))
            # code.emit(I.STORE(name.localID))
            code.emit(I.STORE(name.fdepth, name.localID))
            code.varNameTracker[(name.id, name.fdepth, name.localID)] = name.name

        case FunCall(fn, args):
            for arg in args:
                codegen_(arg)
            # code.emit(I.LOAD(fn.localID))
            code.emit(I.LOAD(fn.fdepth, fn.localID))
            code.emit(I.CALL())
        # case TypeAssertion(expr, _):
        #     codegen_(expr)

        case MutVar(name) as m:
            # code.emit(I.LOAD(m.localID))
            code.emit(I.LOAD(m.fdepth, m.localID))

        case BinOp("=", MutVar(name) as m, e):
            codegen_(e)
            # code.emit(I.STORE(m.localID))
            code.emit(I.STORE(m.fdepth, m.localID))
            code.varNameTracker[(m.id, m.fdepth, m.localID)] = m.name
            # code.emit(I.PUSH(None))
        case BinOp(op, MutVar(name) as m, e) if op in ["+=", "-=", "*=", "/=", "**="]:
            # code.emit(I.LOAD(m.localID))
            code.emit(I.LOAD(m.fdepth, m.localID))
            codegen_(e)
            code.emit(simple_ops[op[:-1]])
            # code.emit(I.STORE(m.localID))
            code.emit(I.STORE(m.fdepth, m.localID))
            # code.emit(I.PUSH(None))


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
        
        case length(MutVar(name) as m):
            # temp = environment.get(name).get()
            # code.emit(I.LOAD(m.fdepth, m.localID))
            codegen_(m)
            code.emit(I.LENGTH())
            # e = eval_env(temp)
            # return len(e.value)
            # if isinstance(temp, Listing):
            #     return len(temp.value)
            # return len(temp)

        case list_head(MutVar(name)):
            temp = environment.get(name)
            e = eval_env(temp)
            return e[0]
        
        case list_tail(MutVar(name)):
            temp = environment.get(name)
            e = eval_env(temp)
            return e[1:]
        
        case list_isempty(MutVar(name)):
            temp = environment.get(name)
            e = eval_env(temp)
            if len(e)==0:
                return True
            return False
        
        case list_append(MutVar(var) as m, item):
         
            # if not environment.check(var):
            #     print(f"list '{var}' not defined")
            #     sys.exit()
            # temp = environment.get(var).get().value
            # e1 = eval_env(temp)
            # e1.append(eval_env(item))
            # bytecode
            # code.emit(I.LOAD(m.fdepth, m.localID))
            codegen_(m)
            codegen_(item)
            code.emit(I.APPEND())
            code.emit(I.STORE(m.fdepth, m.localID))

            # e1 = temp
            # e1.append(item)
            # return e1


        
        case Listing(value, datatype):
            if datatype != "NONE":
                if datatype == "INTEGER":
                    temp = IntLiteral
                elif datatype == "STRING":
                    temp = StringLiteral
                elif datatype == "NONE":
                    temp = None
                for i in value:
                    if isinstance(i, temp):
                        continue
                    else:
                        print("Value of Invalid type in Listing")
                        raise InvalidProgram()
       
            temp =[]
            for i in program.value:
                # temp.append(eval_env(i))
                temp.append(i.value)
            # temp = tuple(temp)
            code.emit(I.PUSH(temp))

            # return temp


        case Slicing(name, start, end, jump):      
            #bytecode
            codegen_(name)
            if start!=None:
                codegen_(start)
            else:
                code.emit(I.PUSH(None))
            if end!=None:
                codegen_(end)
            else:
                code.emit(I.PUSH(None))   
            if jump!=None:
                codegen_(jump)
            else:
                code.emit(I.PUSH(None))
            code.emit(I.SLICE())


        case list_update(MutVar(name) as m, start, end, jump, value):
            #bytecode
            codegen_(m)
            # codegen_(index)
            if start!=None:
                codegen_(start)
            else:
                code.emit(I.PUSH(None))
            if end!=None:
                codegen_(end)
            else:
                code.emit(I.PUSH(None))
            if jump!=None:
                codegen_(jump)
            else:
                code.emit(I.PUSH(None))
                
            codegen_(value)
            code.emit(I.UPDATE())
            code.emit(I.STORE(m.fdepth, m.localID))
        
        case list_Slicing(name, start, end, jump):       
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
     

