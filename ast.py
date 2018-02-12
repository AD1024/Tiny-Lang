from built_in_functions import call_built_in, func_list


def find_variable(env, call_frame, name):
    t_tree = env.copy()
    while name not in t_tree[call_frame] and -1 in t_tree[call_frame]:
        t_tree[call_frame] = t_tree[call_frame][-1]
    return t_tree[call_frame].get(name)


class Equality:
    def __eq__(self, other):
        return isinstance(other, self.__class__) and \
               self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


class Aexp(Equality):
    pass


class Bexp(Equality):
    pass


class Statement(Equality):
    pass


class Subscriptable:
    pass


class NumAexp(Aexp):
    __slots__ = ['v']

    def __init__(self, o):
        self.v = o

    def __repr__(self):
        return 'NumAexp({})'.format(self.v)

    def eval(self, env, call_frame=None):
        return self.v


class StrAexp(Aexp):
    __slots__ = ['v']

    def __init__(self, o):
        self.v = o

    def __repr__(self):
        return 'StrAexp({})'.format(self.v)

    def eval(self, env, call_frame=None):
        return self.v


class BoolAexp(Aexp):
    __slots__ = ['v']

    def __init__(self, o):
        self.v = o

    def __repr__(self):
        return 'BoolAexp({})'.format(self.v)

    def eval(self, env, call_frame=None):
        return self.v


class VarAexp(Aexp):
    __slots__ = ['name']

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'VarAexp({})'.format(self.name)

    def eval(self, env, call_frame=None):
        if not call_frame:
            if self.name in env:
                return env[self.name]
        else:
            return find_variable(env, call_frame, self.name)
            # if self.name in env[call_frame]:
            #     return env[call_frame][self.name]
        return 0


class SubscriptExp:
    def __init__(self, obj, idx):
        self.obj = obj
        self.idx = idx

    def __repr__(self):
        return '{}{}'.format(self.obj, self.idx)

    def get_target(self):
        return self.obj, self.idx

    def eval(self, env, call_frame=None):
        if call_frame:
            tar = find_variable(env, call_frame, self.obj)
        else:
            tar = env[self.obj]
        if isinstance(tar, (Bexp, Aexp, SubscriptExp, Statement, VarAexp)):
            value = tar.eval(env, call_frame=call_frame)
        else:
            value = tar
        for i in self.idx:
            index = i.eval(env, call_frame=call_frame)
            value = value[index]
        return value


class BinopAexp(Aexp):
    __slots__ = ['op', 'left', 'right']

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return 'BinopAexp({},{},{})'.format(self.left, self.op, self.right)

    def eval(self, env, call_frame=None):
        lv = self.left.eval(env, call_frame=call_frame)
        rv = self.right.eval(env, call_frame=call_frame)
        ret_dict = {
            '+': lambda: lv + rv,
            '-': lambda: lv - rv,
            '*': lambda: lv * rv,
            '/': lambda: lv / rv,
            '|': lambda: lv | rv,
            '&': lambda: lv & rv,
            '^': lambda: lv ^ rv,
            'div': lambda: lv // rv,
            'shl': lambda: lv << rv,
            'shr': lambda: lv >> rv,
            '%': lambda: lv % rv,
        }
        if self.op in ret_dict:
            return ret_dict[self.op]()
        else:
            raise RuntimeError('Unknown operator: {}'.format(self.op))


class RelopBexp(Aexp):
    __slots__ = ['op', 'left', 'right']

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return 'RelopAexp({},{},{})'.format(self.left, self.op, self.right)

    def eval(self, env, call_frame=None):
        lv = self.left.eval(env, call_frame=call_frame)
        rv = self.right.eval(env, call_frame=call_frame)
        ret_dict = {
            '>': lambda: lv > rv,
            '<': lambda: lv < rv,
            '>=': lambda: lv >= rv,
            '<=': lambda: lv <= rv,
            '=': lambda: lv == rv,
            '!=': lambda: lv != rv,
        }
        if self.op in ret_dict:
            return ret_dict[self.op]()
        else:
            raise RuntimeError('Unknown operator: {}'.format(self.op))


class AndBexp(Bexp):
    __slots__ = ['left', 'right']

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return 'AndBexp({},{},{})'.format(self.left, '&&', self.right)

    def eval(self, env, call_frame=None):
        lv = self.left.eval(env, call_frame=call_frame)
        rv = self.right.eval(env, call_frame=call_frame)
        return lv and rv


class OrBexp(Bexp):
    __slots__ = ['left', 'right']

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return 'OrBexp({},{},{})'.format(self.left, '|', self.right)

    def eval(self, env, call_frame=None):
        lv = self.left.eval(env, call_frame=call_frame)
        rv = self.right.eval(env, call_frame=call_frame)
        return lv or rv


class XorBexp(Bexp):
    __slots__ = ['left', 'right']

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return 'XorBexp({},{},{})'.format(self.left, '|', self.right)

    def eval(self, env, call_frame=None):
        lv = self.left.eval(env, call_frame=call_frame)
        rv = self.right.eval(env, call_frame=call_frame)
        return lv ^ rv


class NotBexp(Bexp):
    __slots__ = ['exp']

    def __init__(self, exp):
        self.exp = exp

    def __repr__(self):
        return 'NotBexp({})'.format(self.exp)

    def eval(self, env, call_frame=None):
        value = self.exp.eval(env, call_frame=call_frame)
        return not value


class AssigenmentStmt(Statement):
    def __init__(self, name, aexp):
        self.name = name
        self.aexp = aexp

    def __repr__(self):
        return 'AssignStatement({}, {})'.format(self.name, self.aexp)

    def eval(self, env, call_frame=None):
        value = self.aexp.eval(env, call_frame=call_frame)
        if isinstance(self.name, SubscriptExp):
            obj, idx = self.name.get_target()
            idx = list(map(lambda i: i.eval(env, call_frame=call_frame), idx))
            if call_frame:
                obj = find_variable(env, call_frame, obj)
            else:
                obj = env[obj]

            def modify(xs, i):
                if len(i) == 1:
                    xs[i[0]] = value
                else:
                    return modify(xs[i[0]], i[1:])
            modify(obj, idx)
        elif call_frame:
            env[call_frame][self.name] = value
        else:
            env[self.name] = value


class CompoundStmt(Statement):
    def __init__(self, left, right):
        self.right = right
        self.left = left

    def __repr__(self):
        return 'CompoundStatement({},{})'.format(self.left, self.right)

    def eval(self, env, call_frame=None):
        lv = self.left.eval(env, call_frame=call_frame)
        rv = self.right.eval(env, call_frame=call_frame)
        if lv:
            return lv
        elif rv:
            return rv


class IfStmt(Statement):
    def __init__(self, cond, true_body, false_body):
        self.cond = cond
        self.true_body = true_body
        self.false_body = false_body

    def __repr__(self):
        return 'IfStatement(if:{}, then:{}, else:{})'.format(self.cond, self.true_body, self.false_body)

    def eval(self, env, call_frame=None):
        cond_value = self.cond.eval(env, call_frame=call_frame)
        if cond_value:
            return self.true_body.eval(env, call_frame=call_frame)
        else:
            if self.false_body:
                return self.false_body.eval(env, call_frame=call_frame)


class WhileStmt(Statement):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

    def __repr__(self):
        return 'WhileStatement(cond:{}, body:{})'.format(self.cond, self.body)

    def eval(self, env, call_frame=None):
        cond_value = self.cond.eval(env, call_frame=call_frame)
        while cond_value:
            res = self.body.eval(env, call_frame=call_frame)
            if res:
                return res
            cond_value = self.cond.eval(env, call_frame=call_frame)


class ForStmt(Statement):
    def __init__(self, init, cond, body, post):
        self.init = init
        self.cond = cond
        self.body = body
        self.post = post

    def __repr__(self):
        return 'ForStatement(inital:{}, cond:{}, body:{}, post_act:{})' \
            .format(self.init, self.cond, self.body, self.post)

    def eval(self, env, call_frame=None):
        if self.init:
            self.init.eval(env, call_frame=call_frame)
        cond_value = self.cond.eval(env, call_frame=call_frame)
        while cond_value:
            res = self.body.eval(env, call_frame=call_frame)
            if res:
                return res
            if self.post:
                self.post.eval(env, call_frame=call_frame)
            cond_value = self.cond.eval(env, call_frame=call_frame)


class NegateStmt(Statement):
    def __init__(self, target):
        self.tar = target

    def __repr__(self):
        return 'Negation {}'.format(self.tar)

    def eval(self, env, call_frame=None):
        var = self.tar.eval(env, call_frame=call_frame)
        return -var


class Func:
    def __init__(self, name, param, body, caller=None):
        self.name = name
        self.param = param
        self.body = body
        self.func_id = id(self)
        self.caller_id = caller

    def __repr__(self):
        return 'Function: {}({})'.format(self.name, self.param)

    def eval(self, env, param_list=(), call_frame=None):
        env[self.func_id] = {}
        env[self.func_id][self.name] = self
        if not call_frame:
            env[self.func_id].update({-1: dict(filter(lambda x: x[0] != self.func_id, env.items()))})
        if self.caller_id and self.caller_id in env:
            env[self.func_id].update({-1: env[self.caller_id]})
        if param_list:
            param_list = tuple(map(lambda x: x.eval(env, call_frame=call_frame) if isinstance(x, Statement)
                                                                                   or isinstance(x, Aexp)
                                                                                   or isinstance(x, Bexp)
                                                                                   or isinstance(x, SubscriptExp)
            else x,
                                   param_list))
        if self.name in func_list:
            return call_built_in(self.name, param_list)
        for i, j in zip(self.param, param_list):
            env[self.func_id][i] = j
        ans = self.body.eval(env, call_frame=self.func_id)
        # env.pop(self.func_id)
        return ans


class Array(Subscriptable):
    def __init__(self, size, init_value):
        self.size = size
        self.init_value = init_value
        self.data = []
        if init_value is None:
            init_value = 0
        if isinstance(init_value, Array):
            for i in range(0, size):
                self.data.append(init_value.copy())
        else:
            self.data = [init_value] * size

    def __repr__(self):
        return 'Array of {}'.format(self.data)

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value

    def copy(self):
        ret = Array(self.size, self.init_value)
        ret.data = self.data.copy()
        return ret

    def eval(self, env, call_frame=None):
        return self.data


class FuncCallStmt(Statement):
    def __init__(self, func_name, param_list):
        self.func_name = func_name
        self.param_list = param_list

    def __repr__(self):
        return 'Function Call for: {}({})'.format(self.func_name, self.param_list)

    def eval(self, env, call_frame=None):
        func = None
        if call_frame:
            # func = env[call_frame].get(self.func_name)
            func = find_variable(env, call_frame, self.func_name)
            if func:
                func.caller_id = call_frame
        else:
            func = env.get(self.func_name)
        if self.func_name not in func_list and (not func or not isinstance(func, Func)):
            import sys
            sys.stderr.write('function {} is not declared'.format(self.func_name))
            exit(-1)
        else:
            if call_frame is not None and func is not None and self.func_name == func.name:
                func = Func(self.func_name, func.param, func.body, caller=call_frame)
            if not self.param_list:
                self.param_list = ()
            if self.func_name in func_list:
                func = Func(self.func_name, None, None)
            return func.eval(env, self.param_list, call_frame=call_frame)


class FuncDeclareStmt(Statement):
    def __init__(self, name, param, body):
        self.name = name
        self.param = tuple(param) if param else ()
        self.body = body

    def __repr__(self):
        return 'Function-Declaration: {}{}'.format(self.name, self.param)

    def eval(self, env, call_frame=None):
        if call_frame:
            env[call_frame][self.name] = Func(self.name, self.param, self.body)
        else:
            env[self.name] = Func(self.name, self.param, self.body)


class ArrayInitStmt(Statement):
    def __init__(self, size, init_value=None):
        self.size = size
        self.init_value = init_value

    def __repr__(self):
        return 'ArrayInit({})'.format(self.size)

    def eval(self, env, call_frame=None):
        init_size = self.size.eval(env, call_frame=call_frame)
        if self.init_value:
            init_value = self.init_value.eval(env, call_frame=call_frame)
        else:
            init_value = None
        return Array(init_size, init_value)


class ReturnExpression(Statement):
    def __init__(self, exp):
        self.exp = exp

    def __repr__(self):
        return 'ReturnStatement {}'.format(self.exp)

    def eval(self, env, call_frame=None):
        return self.exp.eval(env, call_frame=call_frame)
