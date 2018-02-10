import lexer
from tiny_parser import *

if __name__ == '__main__':
    f = open('hello.ty', 'r')
    a = f.read()
    f.close()
    a = lexer.make_token(a)
    for i in a:
        print(i)

    ast = ty_parse(a)
    ast = ast.value
    print(ast)
    env = {}
    ast.eval(env)
    for i, j in env.items():
        print('{}: {}'.format(i, j))
