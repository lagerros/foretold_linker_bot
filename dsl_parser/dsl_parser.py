from lark import Lark, Transformer, v_args
from cdf import CDF
import os 

dsl_grammar = """
    ?start: sum
          | NAME "=" sum    -> assign_var
    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub
    ?product: atom
        | product "*" atom  -> mul
        | product "/" atom  -> div
    ?atom: NUMBER           -> number
         | "-" atom         -> neg
         | NAME             -> var
         | "(" sum ")"
    cdf: "{xs: " list ", ys: " list "}"
    list: "[" [atom ("," atom)*] "]"
    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS_INLINE
    %ignore WS_INLINE
"""

@v_args(inline=True)
class DSLParser(Transformer):
    from operator import add, sub, mul, truediv as div, neg
    number = float
    cdf = CDF

    def __init__(self, vars={}):
        self.vars = vars

    def assign_var(self, name, value):
        self.vars[name] = value
        return value

    def var(self, name):
        return self.vars[name]


def interface(file: str, m_cdfs):
    # take the m_cdfs, maybe add to the top of the file as variables?
    # Need to expand the language to include CDF variables
    # Grammar: Take each measurable's measurements, aggregate
    """Input of m_cdfs is CDF[] w/ each an aggregation of measurements"""
    vars = {f"n{idx}": v for idx, v in enumerate(m_cdfs)}

    dsl = Lark(dsl_grammar, parser='lalr', transformer=DSLParser(vars))
    
    with open(file, 'r') as file:
        for line in file:
            print(dsl.parse(line.strip()))


def main():
    dsl = Lark(dsl_grammar, parser='lalr', transformer=DSLParser())
    with open("dsl_parser/test.txt", 'r') as file:
        # Only handles first line of file
        for l in file:
            print(dsl.parse(l.strip()))


if __name__ == "__main__":
    cdfA = CDF([1, 2, 3, 4, 5], [.1, .2, .3, .2, .1])
    cdfB = CDF([1, 2, 5, 7, 8], [.3, .5, .5, .3, .02])
    interface("dsl_parser/test.txt", [cdfA, cdfB])
