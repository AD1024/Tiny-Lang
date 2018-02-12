import lexer
from tiny_parser import *
import ty_token
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
    # Process comment blocks
    stk = []
    comment_seg = []
    for i, j in enumerate(token_list):
        if j[1] is ty_token.BEGIN_COMMENT:
            stk.append((i, ty_token.BEGIN_COMMENT))
        elif j[1] is ty_token.END_COMMENT:
            if stk:
                beg = stk.pop()
                if beg[1] is ty_token.BEGIN_COMMENT:
                    start = beg[0]
                    end = i
                    comment_seg.append((start, end))
                else:
                    sys.stderr.write('Comment mismatch')
                    exit(-1)
            else:
                sys.stderr.write('Comment mismatch')
                exit(-1)
    if stk:
        sys.stderr.write('Comment mismatch')
        exit(-1)
    comment_seg.sort(key=lambda p: p[0], reverse=True)
    if comment_seg:
        cur = comment_seg.pop()
        apply_comment = [cur]
        while comment_seg:
            while comment_seg and comment_seg[-1][0] > cur[0] and comment_seg[-1][1] < cur[1]:
                comment_seg.pop()
            if comment_seg:
                cur = comment_seg.pop()
                apply_comment.append(cur)
        for i in apply_comment:
            token_list = list(filter(lambda x: x[-1] not in range(i[0], i[1] + 1), token_list))
    ast = ty_parse(token_list)
    if ast is None:
        sys.stderr.write('Parsing Error! Please check the syntax\n')
        sys.exit(-1)
    ast = ast.value
    env = {}
    ast.eval(env)