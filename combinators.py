class Result:
    '''
    This class stores the result parsed by parsers
    and the position of the start point of remaining tokens
    '''
    __slots__ = ['value', 'pos']

    def __init__(self, v, p):
        self.value = v
        self.pos = p

    def __repr__(self):
        return "Result of ({}, {})".format(self.value, self.pos)


class Parser:
    '''
    Parser base class:
        `P_a` + `P_b`
        means that the pattern that can be
        parsed by `P_a` and `P_b` must be adjacent to each other

        `P_a` | `P_b`
        means that one of the patterns that can be parsed by `P_a` and `P_b` must occur
        at the position

        `P_a` * `P_b`
        will take `P_a` as separator and return elements on two sides of the pattern that can be parsed
        by `P_a` into a `CompoundStmt` wrapper. This class is used to deal with left recursion

        `Lazy(p_func)`
        is designed for lazy calculation, which is not natively supported by Python. The parser will
        be generated when it is needed.

        `P_a ^ func`
        will return the result of `func`, which takes the parsed result proceeded by `P_a`
    '''
    def __call__(self, value, pos):
        return None

    def __add__(self, other):
        return Concat(self, other)

    def __mul__(self, other):
        return Exp(self, other)

    def __or__(self, other):
        return Alternate(self, other)

    def __xor__(self, func):
        return Process(self, func)


class Reserved(Parser):
    '''
    Reserved parser will match both `data`
    and `tag` in a token. Usually it is used to
    match Keywords that only have signal function rather
    than actual effect on the program(For example, `for`, 'while', and 'if')
    '''
    __slots__ = ['data', 'tag']

    def __init__(self, data, tag):
        self.value = data
        self.tag = tag

    def __call__(self, tokens, pos):
        if pos < len(tokens) and self.value == tokens[pos][0] and self.tag is tokens[pos][1]:
            return Result(tokens[pos][0], pos + 1)
        return None


class Tag(Parser):
    '''
    Tag parser will only match tokens with certain `tag`
    '''
    __slots__ = ['tag']

    def __init__(self, tag):
        self.tag = tag

    def __call__(self, tokens, pos):
        if pos < len(tokens) and tokens[pos][1] is self.tag:
            return Result(tokens[pos][0], pos + 1)
        return None


class Concat(Parser):
    __slots__ = ['lchild', 'rchild']

    def __init__(self, l, r):
        self.lchild = l
        self.rchild = r

    def __call__(self, tokens, pos):
        left_result = self.lchild(tokens, pos)
        if left_result:
            right_result = self.rchild(tokens, left_result.pos)
            if right_result:
                return Result((left_result.value, right_result.value), right_result.pos)
        return None


class Alternate(Parser):
    __slots__ = ['lchild', 'rchild']

    def __init__(self, l, r):
        self.lchild = l
        self.rchild = r

    def __call__(self, tokens, pos):
        left_result = self.lchild(tokens, pos)
        if left_result:
            return left_result
        else:
            right_result = self.rchild(tokens, pos)
            return right_result


class Opt(Parser):
    __slots__ = ['parser']

    def __init__(self, parser):
        self.parser = parser

    def __call__(self, tokens, pos):
        result = self.parser(tokens, pos)
        return result if result else Result(None, pos)


class Rep(Parser):
    __slots__ = ['parser']

    def __init__(self, parser):
        self.parser = parser

    def __call__(self, tokens, pos):
        results = []
        res = self.parser(tokens, pos)
        while res:
            results.append(res)
            pos = res.pos
            res = self.parser(tokens, pos)
        return Result(results, pos) if results else None


class Process(Parser):
    __slots__ = ['parser', 'func']

    def __init__(self, parser, func):
        self.parser = parser
        self.func = func

    def __call__(self, tokens, pos):
        result = self.parser(tokens, pos)
        if result:
            result.value = self.func(result.value)
            return result


class Lazy(Parser):
    __slots__ = ['parser', 'parser_func']

    def __init__(self, parser_func):
        self.parser = None
        self.parser_func = parser_func

    def __call__(self, tokens, pos):
        if not self.parser:
            self.parser = self.parser_func()
        return self.parser(tokens, pos)


class Phrase(Parser):
    '''
    Phrase combinator will check
    whether parsing is successful
    '''
    __slots__ = ['parser']

    def __init__(self, parser):
        self.parser = parser

    def __call__(self, tokens, pos):
        result = self.parser(tokens, pos)
        if result and result.pos == len(tokens):
            return result
        return None


class Exp(Parser):
    __slots__ = ['parser', 'separator']

    def __init__(self, parser, separator):
        self.parser = parser
        self.separator = separator

    def __call__(self, tokens, pos):
        result = self.parser(tokens, pos)

        def process_next(parsed):
            (sepfunc, right) = parsed
            return sepfunc(result.value, right)

        next_parser = self.separator + self.parser ^ process_next

        next_result = result
        while next_result:
            next_result = next_parser(tokens, result.pos)
            if next_result:
                result = next_result
        return result
