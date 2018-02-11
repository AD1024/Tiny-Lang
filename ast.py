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


class NumAexp(Aexp):
    __slots__ = ['v']

    def __init__(self, o):
        self.v = o

    def __repr__(self):
        return 'NumAexp({})'.format(self.v)

    def eval(self, env):
        return self.v


class StrAexp(Aexp):
    __slots__ = ['v']

    def __init__(self, o):
        self.v = o

    def __repr__(self):
        return 'StrAexp({})'.format(self.v)

    def eval(self, env):
        return self.v


class BoolAexp(Aexp):
    __slots__ = ['v']

    def __init__(self, o):
        self.v = o

    def __repr__(self):
        return 'BoolAexp({})'.format(self.v)

    def eval(self, env):
        return self.v


class VarAexp(Aexp):
    __slots__ = ['name']

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'VarAexp({})'.format(self.name)

    def eval(self, env):
        if self.name in env:
            return env[self.name]
        return 0


class BinopAexp(Aexp):
    __slots__ = ['op', 'left', 'right']

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return 'BinopAexp({},{},{})'.format(self.left, self.op, self.right)

    def eval(self, env):
        lv = self.left.eval(env)
        rv = self.right.eval(env)
        ret_dict = {
            '+': lambda: lv + rv,
            '-': lambda: lv - rv,
            '*': lambda: lv * rv,
            '/': lambda: lv / rv,
            '|': lambda: lv | rv,
            '&': lambda: lv & rv,
            '^': lambda: lv ^ rv,
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

    def eval(self, env):
        lv = self.left.eval(env)
        rv = self.right.eval(env)
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

    def eval(self, env):
        lv = self.left.eval(env)
        rv = self.right.eval(env)
        return lv and rv


class OrBexp(Bexp):
    __slots__ = ['left', 'right']

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return 'OrBexp({},{},{})'.format(self.left, '|', self.right)

    def eval(self, env):
        lv = self.left.eval(env)
        rv = self.right.eval(env)
        return lv or rv


class XorBexp(Bexp):
    __slots__ = ['left', 'right']

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return 'XorBexp({},{},{})'.format(self.left, '|', self.right)

    def eval(self, env):
        lv = self.left.eval(env)
        rv = self.right.eval(env)
        return lv ^ rv


class NotBexp(Bexp):
    __slots__ = ['exp']

    def __init__(self, exp):
        self.exp = exp

    def __repr__(self):
        return 'NotBexp({})'.format(self.exp)

    def eval(self, env):
        value = self.exp.eval(env)
        return not value


class AssigenmentStmt(Statement):
    def __init__(self, name, aexp):
        self.name = name
        self.aexp = aexp

    def __repr__(self):
        return 'AssignStatement({}, {})'.format(self.name, self.aexp)

    def eval(self, env):
        value = self.aexp.eval(env)
        env[self.name] = value


class CompoundStmt(Statement):
    def __init__(self, left, right):
        self.right = right
        self.left = left

    def __repr__(self):
        return 'CompoundStatement({},{})'.format(self.left, self.right)

    def eval(self, env):
        lv = self.left.eval(env)
        rv = self.right.eval(env)
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

    def eval(self, env):
        print(self.cond)
        cond_value = self.cond.eval(env)
        if cond_value:
            return self.true_body.eval(env)
        else:
            if self.false_body:
                return self.false_body.eval(env)


class WhileStmt(Statement):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body

    def __repr__(self):
        return 'WhileStatement(cond:{}, body:{})'.format(self.cond, self.body)

    def eval(self, env):
        cond_value = self.cond.eval(env)
        while cond_value:
            res = self.body.eval(env)
            if res:
                return res
            cond_value = self.cond.eval(env)


class ForStmt(Statement):
    def __init__(self, init, cond, body, post):
        self.init = init
        self.cond = cond
        self.body = body
        self.post = post

    def __repr__(self):
        return 'ForStatement(inital:{}, cond:{}, body:{}, post_act:{})' \
            .format(self.init, self.cond, self.body, self.post)

    def eval(self, env):
        if self.init:
            self.init.eval(env)
        cond_value = self.cond.eval(env)
        while cond_value:
            res = self.body.eval(env)
            if res:
                return res
            if self.post:
                self.post.eval(env)
            cond_value = self.cond.eval(env)


class Func:
    def __init__(self, name, param, body):
        self.name = name
        self.param = param
        self.body = body

    def __repr__(self):
        return 'Function: {}({})'.format(self.name, self.param)

    def eval(self, env, param_list=()):
        for i, j in zip(self.param, param_list):
            env[i] = j
        return self.body.eval(env)


class FuncCallStmt(Statement):
    def __init__(self, func_name, param_list):
        self.func_name = func_name
        self.param_list = param_list

    def __repr__(self):
        return 'Function Call for: {}({})'.format(self.func_name, self.param_list)

    def eval(self, env):
        func = env.get(self.func_name)
        if not func or not isinstance(func, Func):
            import sys
            sys.stderr.write('function {} is not declared')
            exit(-1)
        else:
            self.param_list = tuple(map(lambda x: x.eval(env), self.param_list))
            return func.eval(env, self.param_list)


class FuncDeclareStmt(Statement):
    def __init__(self, name, param, body):
        self.name = name
        self.param = tuple(param)
        self.body = body

    def __repr__(self):
        return 'Function-Declaration: {}{}'.format(self.name, self.param)

    def eval(self, env):
        env[self.name] = Func(self.name, self.param, self.body)


class ReturnExpression(Statement):
    def __init__(self, exp):
        self.exp = exp

    def __repr__(self):
        return 'ReturnStatement {}'.format(self.exp)

    def eval(self, env):
        return self.exp.eval(env)
