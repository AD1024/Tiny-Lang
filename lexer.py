import re
import sys
import ty_token
# BEGIN deprecated lexer function
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
# END deprecated lexer function

# keyword list
kw_list = [
    '+', '-', '*', '/', '%', '^', '|', '&', '~',
    'shl', 'div', ',',
    'shr',
    'func', 'return', '=>', 'array',
    'while', 'do',
    'for', 'if', 'then', 'else', 'end', 'not',
    '<*', '*>', '>', '<', '>=', '<=', '=', ':=', '!=', 'andalso', 'orelse',
    'True', 'False', ';', '(', ')', '[', ']', '{', '}',
]
# escape symbols
escape = ['\r', '\t', '\a', ' ', '\f']


class Reader:
    '''
        This class stores iterable object and it can return elements in the object position by position.
        This class is used to facilitate the tokenizer function below
    '''
    def __init__(self, data):
        self.data = data
        self.size = len(data)
        self.rng = range(0, self.size)
        self.cursor = 0
        self.line_number = 1
        self.line_pos = 0

    def update(self, data):
        '''
        Update the data in the reader
        :param data: iterable
        :return: None
        '''
        self.data = data
        self.size = len(data)
        self.rng = range(0, self.size)

    def __repr__(self):
        return 'LexerReader @ '.format(id(self))

    def has_next(self):
        '''
        Check whether any element remaining(has not been processed)
        :return:
        '''
        return self.cursor + 1 <= self.size

    def next(self):
        '''
        Return the data the cursor pointing and move the cursor to the next position
        :return:
        '''
        ans = self.data[self.cursor]
        self.cursor += 1
        self.line_pos += 1
        if ans == '\n':
            self.line_number += 1
            self.line_pos = 0
        return ans

    def prev(self):
        return self.from_cur(-1)

    def peek(self):
        return self.from_cur(1)

    def from_cur(self, step=0):
        '''
        Get data `step` far from the cursor
        :param step: int
        :return: element in the iterable object
        '''
        p_cur = self.cursor + step
        return self.data[p_cur] if p_cur in self.rng else None


def advanced_parse(input_code):
    '''
    Tokenizer
    :param input_code: string
    :return: token list
    '''
    token_list = []
    if input_code[-1] == '\n':
        input_code = input_code[:-1]
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
        if reader.has_next() and reader.from_cur() in ('.', 'e'):
            'Process decimal numbers'
            ans += reader.next()
            while reader.has_next() and (reader.from_cur().isdigit() or reader.from_cur() == '-'):
                if '-' in ans and reader.from_cur() == '-':
                    raise Exception('Invalid float @ line {}, {}'.format(reader.line_number, reader.line_pos))
                ans += reader.next()
            if not ans[-1].isdigit():
                raise Exception('Invalid float @ line {}, {}'.format(reader.line_number, reader.line_pos))
        return ans

    def read_word():
        ans = ''
        while reader.has_next() and reader.from_cur().isalpha() or reader.from_cur() in ('_', ):
            'read a word'
            ans += reader.next()
        return ans

    while reader.has_next():
        cur = reader.next()
        if cur == '\n':
            if token_list and token_list[-1][0] in ('func', '=>', '{', '(', 'do', 'then', 'else', '\n'):
                continue
            add_token('\n', ty_token.RESERVED)
            continue
        if cur in escape:
            continue
        if cur.isdigit():
            cur += read_number()
            add_token(cur, ty_token.DOUBLE if '.' in cur or 'e' in cur else ty_token.INT)
        elif cur in kw_list or cur == '!' or cur == ':':
            if cur in ('(', ')', '~', ';', '-', '[', ']', ','):
                'These are single-symbol reserved words. There cannot be any symbol related'
                'to these symbols after them'
                add_token(cur, ty_token.RESERVED)
            else:
                while reader.has_next() and reader.from_cur() in kw_list and reader.from_cur() not \
                        in ('(', ')', '~', ';', '-', '[', ']', ','):
                    'Process reserved words like `>=`, `<=`, which consist of two one-symbol reserved word'
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
                '`cur` is a reserved word e.g. `for`'
                if cur == 'True' or cur == 'False':
                    add_token(cur, ty_token.BOOL)
                else:
                    add_token(cur, ty_token.RESERVED)
            else:
                '`cur` is an identifier'
                add_token(cur, ty_token.IDENTIFIER)
        if token_list and token_list[-1][0] == 'end' and token_list[-2][0] == '\n':
            token_list.pop(-2)
    # for i in token_list:
    #     print(i)
    return token_list
