import re
import sys
import ty_token
token_rule = [
    (r'[ \r\n\t]+', None),
    (r'#[^\n]*',   None),
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
    (r'[0-9]+.[0-9]+', ty_token.DOUBLE),
    (r'"[\u4e00-\u9fa5_a-zA-Z0-9]+"', ty_token.STRING),
    (r'[0-9]+', ty_token.INT),
    (r'(True|False)', ty_token.BOOL),
    (r'[A-Za-z][A-Za-z0-9_]*', ty_token.IDENTIFIER),

]


def make_token(input_code):
    cur = 0
    tokens = []
    while cur < len(input_code):
        match = None
        for i in token_rule:
            pattern, tag = i
            match = re.compile(pattern).match(input_code, cur)
            if match:
                data = match.group(0)
                if tag:
                    tokens.append((data, tag))
                break
        if not match:
            sys.stderr.write('Illegal character @ {}'.format(cur))
            sys.exit(-1)
        else:
            cur = match.end(0)
    return tokens
