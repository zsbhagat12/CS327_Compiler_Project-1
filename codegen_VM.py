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
        localID: int

    @dataclass
    class STORE:
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
)

@dataclass
class ByteCode:
    insns: List[Instruction]

    def __init__(self):
        self.insns = []

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

    def __init__(self):
        MAX_LOCALS = 32
        self.locals = [None] * MAX_LOCALS

class VM:
    bytecode: ByteCode
    ip: int
    data: List[Value]
    currentFrame: Frame

    def load(self, bytecode):
        self.bytecode = bytecode
        self.restart()

    def restart(self):
        self.ip = 0
        self.data = []
        self.currentFrame = Frame()

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
                case I.LOAD(localID):
                    self.data.append(self.currentFrame.locals[localID])
                    self.ip += 1
                case I.STORE(localID):
                    v = self.data.pop()
                    self.currentFrame.locals[localID] = v
                    self.ip += 1
                case I.PRINT():
                    op = self.data.pop()
                    print(op)
                    self.ip += 1
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
        "<": I.LT(),
        ">": I.GT(),
        # "≤": I.LE(),
        # "≥": I.GE(),
        "<=": I.LE(),
        ">=": I.GE(),
        "=": I.EQ(),
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
                tree = resolve(tree)
                sys.stdout = open('resolved_tree', 'w')
                pp = pprint.PrettyPrinter(stream=sys.stdout)
                pp.stream = sys.stdout
                print("Resolved Tree:")
                pp.pprint(tree)

            # typecheck(tree)
            sys.stdout = open('eval.txt', 'w')
            # e = codegen_(tree)
            e = codegen(tree)
            v = VM()
            v.load(e)
            v.execute()
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
        case BinOp("and", left, right):
            E = code.label()
            codegen_(left)
            code.emit(I.DUP())
            code.emit(I.JMP_IF_FALSE(E))
            code.emit(I.POP())
            codegen_(right)
            code.emit_label(E)
        case BinOp("or", left, right):
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
            for thing in things:
                codegen_(thing)
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
            code.emit_label(B)
            codegen_(cond)
            code.emit(I.JMP_IF_FALSE(E))
            codegen_(body)
            code.emit(I.JMP(B))
            code.emit_label(E)
        case Statement(command, statement):
            if command == "print":
                codegen_(statement)
                code.emit(I.DUP())
                code.emit(I.PRINT())
            elif command == "return":
                codegen_(statement)
                code.emit(I.RETURN())
            elif command == "break":
                code.emit(I.BREAK())
            elif command == "continue":
                code.emit(I.CONTINUE())
        case (Variable() as v) | UnOp("!", Variable() as v):
            code.emit(I.LOAD(v.localID))
        case Put(Variable() as v, e):
            codegen_(e)
            code.emit(I.STORE(v.localID))
        case Let(Variable() as v, e1, e2) | LetMut(Variable() as v, e1, e2):
            codegen_(e1)
            code.emit(I.STORE(v.localID))
            codegen_(e2)
        # case TypeAssertion(expr, _):
        #     codegen_(expr)

