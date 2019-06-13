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
    cdf: "{floatCdf: {xs: " samples "}}
    samples: "[" [atom ("," atom)*] "]"
    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS_INLINE
    %ignore WS_INLINE
"""