"""
    Disassembler for GalaxyScript bytecode.

    The MIT License (MIT)

    Copyright (c) 2015 Joel Hoener <athre0z@zyantific.com>

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:
    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""

class Register(object):
    BP = 30
    SP = 31

    def __init__(self, idx):
        assert 0 <= idx <= 31
        self.idx = idx

    def textual(self):
        if self.idx == self.BP:
            return 'bp'
        if self.idx == self.SP:
            return 'sp'
        return 'r' + str(self.idx)

    def __repr__(self):
        return 'Register(idx: {})'.format(self.idx)


class Immediate(object):
    CONST = 1
    CONST_BOOL = 2
    FIXED = 3

    def __init__(self, val, bits, val_type=CONST):
        assert val_type in (self.CONST, self.CONST_BOOL, self.FIXED)
        self.val = val
        self.bits = bits
        self.type = val_type

    def textual(self):
        if self.type == self.CONST:
            return '#{:02X}h'.format(self.val)
        if self.type == self.CONST_BOOL:
            return 'true' if self.val != 0 else 'false'
        if self.type == self.FIXED:
            return '#{}.{}'.format(self.val >> 11, self.val & 0x7ff)
        raise IndexError()

    def __repr__(self):
        return 'Immediate(val: {}, bits: {})'.format(self.val, self.bits)


class Expression(object):
    def __init__(self, lhs, rhs, operator):
        self.lhs = lhs
        self.rhs = rhs
        self.operator = operator

    def textual(self):
        return self.lhs.textual() + self.operator + self.rhs.textual()


def make_expression_type(operator):
    class Expr(Expression):
        def __init__(self, lhs, rhs):
            super(Expr, self).__init__(lhs, rhs, operator)
    return Expr

AddExpression = make_expression_type('+')
SubExpression = make_expression_type('-')
LeftShiftExpression = make_expression_type('<<')
RightShiftExpression = make_expression_type('>>')


class Reference(object):
    CODE = 1
    GLOBAL = 2
    UNIFIED = 3
    STACK = 4

    def __init__(self, expr, ref_type, ip_relative=False):
        assert ref_type in (self.CODE, self.GLOBAL, self.UNIFIED, self.STACK)
        self.expr = expr
        self.type = ref_type
        self.ip_relative = ip_relative

    def prefix(self):
        return {
            self.CODE: 'c',
            self.GLOBAL: 'g',
            self.UNIFIED: 'u',
            self.STACK: 's',
        }[self.type]

    def expression(self):
        return ('+' if self.ip_relative else '') + self.expr.textual()

    def textual(self):
        return self.prefix() + '::[' + self.expression() + ']'
