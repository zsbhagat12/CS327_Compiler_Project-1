# from fractions import Fraction
# from dataclasses import dataclass
# from typing import Optional, NewType
from dataclasses_sim import *
# A minimal example to illustrate typechecking.

# @dataclass
# class NumType:
#     pass

# @dataclass
# class BoolType:
#     pass

# SimType = NumType | BoolType

# @dataclass
# class NumLiteral:
#     value: Fraction
# #     type: SimType = NumType()

# @dataclass
# class BoolLiteral:
#     value: bool
# #     type: SimType = BoolType()

# @dataclass
# class BinOp:
#     operator: str
#     left: 'AST'
#     right: 'AST'
# #     type: Optional[SimType] = None

# @dataclass
# class IfElse:
#     condition: 'AST'
#     iftrue: 'AST'
#     iffalse: 'AST'
# #     type: Optional[SimType] = None

# AST = NumLiteral | BoolLiteral | BinOp | IfElse

@dataclass
class TypeError(Exception):
    pass

# Since we don't have variables, environment is not needed.
def typecheck(program: AST, env = None):
    match program:
        case NumLiteral() as t: # already typed.
            return t
        case BoolLiteral() as t: # already typed.
            return t
        case BinOp(op, left, right) if op in ["+", "*"]:
            tleft = typecheck(left)
            tright = typecheck(right)

            print(isinstance(tleft, NumLiteral), isinstance(tright, NumLiteral))
            if isinstance(tleft, NumLiteral) != True or isinstance(tright, NumLiteral) != True:
                raise TypeError()
            return NumLiteral();
        
        
#         case BinOp("<", left, right):
#             tleft = typecheck(left)
#             tright = typecheck(right)
#             if tleft.type != NumType() or tright.type != NumType():
#                 raise TypeError()
#             return BinOp("<", left, right, BoolType())
#         case BinOp("=", left, right):
#             tleft = typecheck(left)
#             tright = typecheck(right)
#             if tleft.type != tright.type:
#                 raise TypeError()
#             return BinOp("=", left, right, BoolType())
#         case IfElse(c, t, f): # We have to typecheck both branches.
#             tc = typecheck(c)
#             if tc.type != BoolType():
#                 raise TypeError()
#             tt = typecheck(t)
#             tf = typecheck(f)
#             if tt.type != tf.type: # Both branches must have the same type.
#                 raise TypeError()
#             return IfElse(tc, tt, tf, tt.type) # The common type becomes the type of the if-else.
        case _:
             raise TypeError()

def test_typecheck():
#     import pytest
    typecheck(BinOp("+", NumLiteral(2), BoolLiteral(False)))
#     assert te.type == NumType()
#     te = typecheck(BinOp("<", NumLiteral(2), NumLiteral(3)))
#     assert te.type == BoolType()
#     with pytest.raises(TypeError):
#         typecheck(BinOp("+", BinOp("*", NumLiteral(2), NumLiteral(3)), BinOp("<", NumLiteral(2), NumLiteral(3))))
        
# test_typecheck()