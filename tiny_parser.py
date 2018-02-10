from combinators import *
from ast import *
from ty_token import *
from functools import reduce

arithmetic_exp_levels = [
    ['%', ],
    ['*', '/'],
    ['+', '-'],
    ['|', '&', '^'],
    ['shl', 'shr'],
]

bool_exp_levels = [
    ['not'],
    ['andalso', 'orelse'],
]


def keyword(kw):
    return Reserved(kw, RESERVED)


num = (Tag(INT) ^ (lambda x: int(x))) | (Tag(DOUBLE) ^ (lambda x: float(x)))
string = (Tag(STRING) ^ (lambda x: str(x)))
boolean = (Tag(BOOL) ^ (lambda x: True if x == 'True' else False))
identifier = Tag(IDENTIFIER)


def ty_parse(tokens):
    return build_parser()(tokens, 0)


def build_parser():
    return Phrase(stmt_list())


def assignment_stmt():
    def process(result):
        ((name, _), exp) = result
        return AssigenmentStmt(name, exp)

    return identifier + keyword(':=') + aexp() ^ process


def if_stmt():
    def processor(parsed):
        (((((_, condition), _), true_stmt), false_parsed), _) = parsed
        if false_parsed:
            (_, false_stmt) = false_parsed
        else:
            false_stmt = None
        return IfStmt(condition, true_stmt, false_stmt)
    return keyword('if') + bexp() + keyword('then') \
           + Lazy(stmt_list) \
           + Opt(keyword('else') + Lazy(stmt_list)) + keyword('end') ^ processor


def while_stmt():
    def processor(parsed):
        ((((_, condition), _), body), _) = parsed
        return WhileStmt(condition, body)

    return keyword('while') + bexp() + keyword('do') + Lazy(stmt_list) + keyword('end') ^ processor


def for_stmt():
    def processor(parsed):
        print(parsed)
        ((((((((((_, _), init), _), cond), _), post_act), _), _,), body), _) = parsed
        return ForStmt(init, cond, body, post_act)

    return keyword('for') + keyword('(') \
           + Opt(Lazy(assignment_stmt)) + keyword(';') + Opt(bexp()) + keyword(';') \
           + Opt(Lazy(assignment_stmt)) \
           + keyword(')') + keyword('do') + Lazy(stmt_list) + keyword('end') ^ processor


def stmt():
    return assignment_stmt() | if_stmt() | while_stmt() | for_stmt()


def stmt_list():
    sep = keyword(';') ^ (lambda x: lambda l, r: CompoundStmt(l, r))
    return Exp(stmt(), sep)


def process_tuple(parsed):
    ((_, data), _) = parsed
    return data


def get_parser_from_list(lst):
    op_parsers = [keyword(x) for x in lst]
    combined_parser = reduce(lambda l, r: l | r, op_parsers)
    return combined_parser


def precedence_combinator(value_parser, precedence_level, post_processor):
    def get_op_parser(p_level):
        return get_parser_from_list(p_level) ^ post_processor

    ret = value_parser * get_op_parser(precedence_level[0])
    for i in precedence_level[1:]:
        ret = ret * get_op_parser(i)
    return ret


def aexp():
    return precedence_combinator(aexp_term(), arithmetic_exp_levels, process_binop)


def aexp_term():
    return aexp_tuple() | aexp_value()


def aexp_tuple():
    return keyword('(') + Lazy(aexp) + keyword(')')


def aexp_value():
    return (num ^ (lambda x: NumAexp(x))) | \
           (identifier ^ (lambda x: VarAexp(x))) | \
           (string ^ (lambda x: StrAexp(x))) | \
           (boolean ^ (lambda x: BoolAexp(x)))


def bexp():
    return precedence_combinator(bexp_term(), bool_exp_levels, process_logic_exp)


def bexp_term():
    return bexp_not() | bexp_relation_op() | bexp_tuple() | (boolean ^ (lambda x: BoolAexp(x)))


def bexp_not():
    return keyword('not') + Lazy(bexp_term) ^ (lambda x: NotBexp(x[-1]))


def bexp_relation_op():
    rel_op = ['>', '<', '>=', '<=', '=', '!=']
    return (aexp() + get_parser_from_list(rel_op) + aexp()) ^ process_relop


def bexp_tuple():
    return keyword('(') + Lazy(bexp) + keyword(')') ^ process_tuple


def process_binop(op):
    return lambda l, r: BinopAexp(op, l, r)


def process_relop(p):
    ((l, op), r) = p
    return RelopBexp(op, l, r)


def process_logic_exp(op):
    ret_dict = {
        'andalso': lambda l, r: AndBexp(l, r),
        'orelse': lambda l, r: OrBexp(l, r),
    }
    ret = ret_dict.get(op, None)
    if ret:
        return ret
    raise RuntimeError('Unknown logic expression {}'.format(op))
