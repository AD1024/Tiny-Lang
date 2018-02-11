from math import *
from random import *

func_list = dir() + ['println', 'print', 'scan', 'int']


def scan():
    return input()


def call_built_in(func_name, param):
    if func_name not in func_list:
        sys.stderr.write('function {} is not defined'.format(func_name))
        sys.exit(-1)
    else:
        return eval(func_name + str(tuple(param)))
