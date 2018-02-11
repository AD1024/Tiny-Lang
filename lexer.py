import re
import sys
import ty_token

token_rule = [
    (r'[ \r\n\t]+', None),
    (r'#[^\n]*', None),
    (r'"[\u4e00-\u9fa5_a-zA-Z0-9]+"', ty_token.STRING),
    (r'[0-9]+\.[0-9]+', ty_token.DOUBLE),
    (r'[0-9]+', ty_token.INT),
    (r'<\*', ty_token.BEGIN_COMMENT),
    (r'\*>', ty_token.END_COMMENT),
    (r'func', ty_token.RESERVED),
    (r'~',    ty_token.RESERVED),
    (r'=>', ty_token.RESERVED),
    (r'return', ty_token.RESERVED),
    (r',', ty_token.RESERVED),
    (r'\:=', ty_token.RESERVED),
    (r'\(', ty_token.RESERVED),
    (r'\)', ty_token.RESERVED),
    (r';', ty_token.RESERVED),
    (r'\+', ty_token.RESERVED),
    (r'-', ty_token.RESERVED),
    (r'\*', ty_token.RESERVED),
    (r'/', ty_token.RESERVED),
    (r'&', ty_token.RESERVED),
    (r'\|', ty_token.RESERVED),
    (r'shl', ty_token.RESERVED),
    (r'shr', ty_token.RESERVED),
    (r'\^', ty_token.RESERVED),
    (r'<=', ty_token.RESERVED),
    (r'>=', ty_token.RESERVED),
    (r'<', ty_token.RESERVED),
    (r'>', ty_token.RESERVED),
    (r'!=', ty_token.RESERVED),
    (r'=', ty_token.RESERVED),
    (r'andalso', ty_token.RESERVED),
    (r'orelse', ty_token.RESERVED),
    (r'if', ty_token.RESERVED),
    (r'then', ty_token.RESERVED),
    (r'else', ty_token.RESERVED),
    (r'not', ty_token.RESERVED),
    (r'for', ty_token.RESERVED),
    (r'while', ty_token.RESERVED),
    (r'do', ty_token.RESERVED),
    (r'end', ty_token.RESERVED),
    (r'(True|False)', ty_token.BOOL),
    (r'[A-Za-z][A-Za-z0-9_]*', ty_token.IDENTIFIER),

]


def make_token(input_code):
    cur = 0
    tokens = []
    cnt = 0
    while cur < len(input_code):
        match = None
        for i in token_rule:
            pattern, tag = i
            match = re.compile(pattern).match(input_code, cur)
            if match:
                data = match.group(0)
                if tag:
                    tokens.append((data, tag, cnt))
                    cnt += 1
                break
        if not match:
            sys.stderr.write('Illegal character @ {}'.format(cur))
            sys.exit(-1)
        else:
            cur = match.end(0)
    return tokens


kw_list = [
    '+', '-', '*', '/', '%', '^', '|', '&', '~',
    'shl',
    'shr',
    'func', 'return', '=>',
    'while', 'do',
    'for', 'if', 'then', 'else', 'end', 'not',
    '<*', '*>', '>', '<', '>=', '<=', '=', ':=', '!=', 'andalso', 'orelse',
    'True', 'False', ';', '(', ')',
]
escape = ['\n', '\r', '\t', '\a', ' ', '\f']


class Reader:
    def __init__(self, data):
        self.data = data
        self.size = len(data)
        self.rng = range(0, self.size)
        self.cursor = 0

    def update(self, data):
        self.data = data
        self.size = len(data)
        self.rng = range(0, self.size)

    def __repr__(self):
        return 'LexerReader @ '.format(id(self))

    def has_next(self):
        return self.cursor + 1 <= self.size

    def next(self):
        ans = self.data[self.cursor]
        self.cursor += 1
        return ans

    def prev(self):
        return self.from_cur(-1)

    def peek(self):
        return self.from_cur(1)

    def from_cur(self, step=0):
        p_cur = self.cursor + step
        return self.data[p_cur] if p_cur in self.rng else None


def advanced_parse(input_code):
    token_list = []
    reader = Reader(input_code)

    class Count:
        def __init__(self):
            self.cur = 0

        def next(self):
            ret = self.cur
            self.cur += 1
            return ret

    cnt = Count()

    def add_token(data, tag):
        token_list.append((data, tag, cnt.next()))

    def read_number():
        ans = ''
        while reader.has_next() and reader.from_cur().isdigit():
            ans += reader.next()
        if reader.has_next() and reader.from_cur() == '.':
            ans += reader.next()
            while reader.has_next() and reader.from_cur().isdigit():
                ans += reader.next()
        return ans

    def read_word():
        ans = ''
        while reader.has_next() and reader.from_cur().isalpha():
            ans += reader.next()
        return ans

    while reader.has_next():
        cur = reader.next()
        if cur in escape:
            continue
        if cur.isdigit():
            cur += read_number()
            add_token(cur, ty_token.DOUBLE if '.' in cur else ty_token.INT)
        elif cur in kw_list or cur == '!' or cur == ':':
            if cur in ('(', ')', '~', ';', '-'):
                add_token(cur, ty_token.RESERVED)
            else:
                while reader.has_next() and reader.from_cur() in kw_list:
                    cur += reader.next()
                if cur == '<*':
                    add_token(cur, ty_token.BEGIN_COMMENT)
                elif cur == '*>':
                    add_token(cur, ty_token.END_COMMENT)
                else:
                    add_token(cur, ty_token.RESERVED)
        elif cur.isalpha():
            cur += read_word()
            if cur in kw_list:
                if cur == 'True' or cur == 'False':
                    add_token(cur, ty_token.BOOL)
                else:
                    add_token(cur, ty_token.RESERVED)
            else:
                add_token(cur, ty_token.IDENTIFIER)
    return token_list
