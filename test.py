import lexer
from tiny_parser import *
import ty_token
import sys

if __name__ == '__main__':
    f = open('hello.ty', 'r')
    input_code = f.read()
    f.close()
    token_list = lexer.advanced_parse(input_code)
    if token_list:
        ast = ty_parse(token_list)
        ast = ast.value
        env = {}
        ast.eval(env)
    # for i in env:
    #     print('{}: {}'.format(i, env[i]))
