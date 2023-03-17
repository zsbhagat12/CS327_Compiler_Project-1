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
class UnOp:
    operator: str
    mid: 'AST'
    def get_mid(self):
        return self.mid

@dataclass
class Variable:
    name: str

@dataclass
class Let:
    var: 'AST'
    e1: 'AST'
    e2: 'AST'

@dataclass
class LetMut:
    var: 'AST'
    e1: 'AST'
    e2: 'AST'

@dataclass
class Put:
    var: 'AST'
    e1: 'AST'

@dataclass
class Get:
    var: 'AST'

@dataclass
class LetFun:
    name: 'AST'
    params: List['AST']
    body: 'AST'
    expr: 'AST'

@dataclass
class FunCall:
    fn: 'AST'
    args: List['AST']


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
    statements: List['AST']

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
class ForLoop:
    start : 'AST'
    end : 'AST'
    increment : 'AST'
    body : 'AST'
    
@dataclass
class While:
    condition: 'AST'
    body: 'AST'

@dataclass
class Function:
    name: 'AST'
    params: List['AST']
    body: 'AST'
    

@dataclass
class CallStack:
    clstk: List

@dataclass
class Increment:
    var_literal : 'AST'

@dataclass
class Decrement:
    var_literal : 'AST'


@dataclass
class Slicing:
    name : 'AST'
    start : 'AST'
    end : 'AST'
    jump : 'AST'

@dataclass
class Str_len:
    name: 'AST'   

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
    
    def check(self, name):
        for env in reversed(self.envs):

            if name in env:
                return True
        else:
            return False
        # raise KeyError()

AST = NumLiteral | BinOp | Variable | Let | BoolLiteral | UnOp | StringLiteral | IfElse | MutVar | While | Seq | Function | LetFun | FunCall | Slicing

@dataclass
class FnObject:
    params: List['AST']
    body: 'AST'

Value = Fraction
Val = bool



# Val_string = string

@dataclass
class InvalidProgram(Exception):
    pass


