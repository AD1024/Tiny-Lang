import lexer
from tiny_parser import *
import sys


def usage():
    sys.stderr.write('Usage: tiny filename\n')
    sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage()
    filename = sys.argv[1]
    f = open(filename, 'r')
    input_code = f.read()
    f.close()
    token_list = lexer.advanced_parse(input_code)
    ast = ty_parse(token_list)
    if ast is None:
        sys.stderr.write('Parsing Error! Please check the syntax\n')
        sys.exit(-1)
    ast = ast.value
    env = {}
    ast.eval(env)
