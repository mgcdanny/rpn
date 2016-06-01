import re
import operator
import collections
import decimal

Token = collections.namedtuple(
    'Token', ['typ', 'val', 'prc', 'asc', 'func', 'is_oper'])


def parse(expr):
    grammer = {
        'NUM': {'asc': None, 'prc': None, 'func': decimal.Decimal, 'is_oper': False},
        'LPAREN': {'asc': 'L', 'prc': 0, 'func': None, 'is_oper': False},
        'RPAREN': {'asc': 'L', 'prc': 9, 'func': None, 'is_oper': False},
        'ADD': {'asc': 'L', 'prc': 2, 'func': operator.add, 'is_oper': True},
        'SUB': {'asc': 'L', 'prc': 2, 'func': operator.sub, 'is_oper': True},
        'MUL': {'asc': 'L', 'prc': 4, 'func': operator.mul, 'is_oper': True},
        'DIV': {'asc': 'L', 'prc': 4, 'func': operator.truediv, 'is_oper': True},
        'EXP': {'asc': 'R', 'prc': 6, 'func': operator.pow, 'is_oper': True}
    }

    token_spec = [('NUM', '\d+(\.\d*)?'), ('ADD', '\+|add'),
                  ('SUB', '-'), ('MUL', '\*'), ('DIV', '/'),
                  ('EXP', '\^'), ('LPAREN', '\('), ('RPAREN', '\)')]

    tok_regex = '|'.join('(?P<{}>{})'.format(
        pair[0], pair[1]) for pair in token_spec)

    tokens = []
    for mo in re.finditer(tok_regex, expr):
        meta = grammer[mo.lastgroup]
        tokens.append(
            Token(mo.lastgroup, mo.group(),
                  meta['prc'], meta['asc'], meta['func'], meta['is_oper']))
    return tokens


def shunt(tokens):
    """Shunting Yard algo"""

    STACK, Q = [], []

    for token in tokens:
        if token.typ == 'NUM':
            Q.append(token)
        elif token.is_oper:
            o1 = token
            while STACK:
                o2 = STACK[0]
                if (o2.is_oper) and (
                        (o1.asc == 'L' and o1.prc <= o2.prc) or
                        (o1.asc == 'R' and o1.prc < o2.prc)):
                    Q.append(STACK.pop(0))
                else:
                    break
            STACK.insert(0, token)
        elif token.typ == 'LPAREN':
            STACK.insert(0, token)
        elif token.typ == 'RPAREN':
            while STACK:
                if STACK[0].typ == 'LPAREN':
                    STACK.pop(0)
                    break
                else:
                    Q.append(STACK.pop(0))
    while STACK:
        Q.append(STACK.pop(0))

    return Q


def eval_rpn(rpn):
    """rpn is reverse polish notation"""
    stack = []
    for token in rpn:
        if token.typ == 'NUM':
            stack.append(token.func(token.val))
        elif token.is_oper:  # assume n == 2
            n1 = stack.pop()
            n2 = stack.pop()
            stack.append(token.func(n2, n1))
    return stack.pop()


def test_shunt():
    assert [t.val for t in shunt(parse('2+2'))] == ['2', '2', '+']

    assert ([t.val for t in shunt(parse('2+2*4'))] ==
            ['2', '2', '4', '*', '+'])

    assert ([t.val for t in shunt(parse('(2+2)*4'))] ==
            ['2', '2', '+', '4', '*'])

    assert [t.val for t in shunt(parse('2-2+3*4/2'))] == ['2', '2', '-',
                                                          '3', '4', '*', '2', '/', '+']

    assert [t.val for t in shunt(parse('2-(2+3)*4/2'))] == ['2', '2',
                                                            '3', '+', '4', '*', '2', '/', '-']
    print('test_shunt Success !!!!!!!!!!!!!!!')


def test_rpn():
    assert eval_rpn(shunt(parse('2+2'))) == 4

    assert eval_rpn(shunt(parse('2+2*4'))) == 10

    assert eval_rpn(shunt(parse('(2+2)*4'))) == 16

    assert eval_rpn(shunt(parse('2-2+3*4/2'))) == 6

    assert eval_rpn(shunt(parse('2-(2+3)*4/2'))) == -8

    assert eval_rpn(shunt(parse('2-(2 add 3)*4/2'))) == -8

    assert eval_rpn(shunt(parse('(((2+10) - (1 add 1)) * 4 / 2)'))) == 20

    print('test_rpn Success !!!!!!!!!!!!!!!')


test_shunt()
test_rpn()
