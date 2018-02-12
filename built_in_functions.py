from math import *
from random import *
from ast import *

func_list = dir() + ['println', 'print', 'scan', 'int', 'len']


def scan():
    return input()


def call_built_in(func_name, param):
    if func_name not in func_list:
        sys.stderr.write('function {} is not defined'.format(func_name))
        sys.exit(-1)
    else:
        if func_name == 'print':
            for i in param:
                print(i, end=' ')
            return None
        elif func_name == 'len':
            return param[0].size
        return eval(func_name + str(tuple(param)))
