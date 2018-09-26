#!/usr/bin/python
# -*- coding: UTF-8 -*-
__author__ = 'Gaufoo, zhongzc_arch@outlook.com'

__see__ = 'http://www.cs.nott.ac.uk/~pszgmh/monparsing.pdf'

from collections import namedtuple
from typing import Callable


class LocatedText:
    """
    字符串解析到的位置
    """
    __str = ...  # type: str
    __loc = ...  # type: int

    def __init__(self, inp: str, loc: int = 0):
        assert loc <= len(inp)
        self.__str = inp
        self.__loc = loc

    def remaining(self) -> str:
        return self.__str[self.__loc:]

    def advance_one(self) -> None:
        assert not self.isEOF()
        self.__loc += 1

    def isEOF(self) -> bool:
        return self.__loc == len(self.__str)

    def row(self) -> int:
        return self.__str[0: self.__loc].count('\n') + 1

    def col(self) -> int:
        l = self.__str[0: self.__loc].rfind('\n')
        if (l == -1):
            return self.__loc + 1
        else:
            return self.__loc - l

    def current_line(self) -> str:
        return self.__str.splitlines()[self.row() - 1]

    def column_caret(self) -> str:
        return (" " * (self.col() - 1)) + "^"

    def __repr__(self):
        return str({'loc': self.__loc, 'str': self.__str})

    def __str__(self):
        return '({},{})'.format(self.row(), self.col()) + '\n' + \
               self.current_line() + '\n' + \
               self.column_caret()


"""
# Success

解析成功后的State.result包含的值
"""
Success = namedtuple('Success', ['value'])

"""
# ParseError

解释失败后State.result包含的错误信息
"""
ParseError = namedtuple('ParseError', ['msg'])

"""
# State(result: T, text: LocatedText)

解析后返回的状态，result的类型是(Success | ParseError)
"""
State = namedtuple('State', ['result', 'text'])


class Parser:
    """
    Parser(fn: LocatedText -> State)

    解析器，运行时接受一个LocatedText，返回解析后的状态
    """
    fn = ...  # type: Callable[[LocatedText], State]

    def __init__(self, fn: Callable[[LocatedText], State]):
        self.fn = fn

    def run(self, inp: str) -> State:
        return self.fn(LocatedText(inp))

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)

    def flatmap(self, func):
        """
        Parser[A] -> (A -> Parser[B]) -> Parser[B]

        :see : https://en.wikipedia.org/wiki/Monad_(functional_programming)
        """

        def inner(loc: LocatedText) -> State:
            state = self.fn(loc)
            if isinstance(state.result, Success):
                return func(state.result.value).fn(state.text)
            else:
                return state

        return Parser(inner)

    def map(self, func):
        return self.flatmap(lambda v: just(func(v)))

    def then(self, parser):
        return self.flatmap(lambda _: parser)

    def __rshift__(self, func):
        return self.then(func)

    def label(self, msg):
        return label(self, msg)


def run_parser(parser: Parser, inp: str) -> State:
    """
    运行Parser

    :param parser: 构建好的解析器
    :param inp: 待解析字符串
    :return State: 解析完的状态，返回Success或者ParseError
    """
    return parser.run(inp)


def satisfy(pred: Callable[[str], bool]) -> Parser:
    """
    若下一个字符满足判断条件(pred)，则解析成功

    :param pred: 下一个字符该满足的条件
    :return Parser: 相应的Parser
    """

    def inner(loc: LocatedText) -> State:
        if loc.isEOF():
            return State(ParseError("再无输入可解析"), loc)
        else:
            c = loc.remaining()[0]
            if pred(c):
                loc.advance_one()
                return State(Success(c), loc)
            else:
                return State(ParseError("不满足条件"), loc)

    return Parser(inner)


def label(parser: Parser, msg: str) -> Parser:
    """
    为Parser提供进一步的错误信息

    :param parser: 需要修饰的Parser
    :param msg: 进一步的错误信息
    :return Parser: 修饰过的Parser
    """

    def inner(loc: LocatedText) -> State:
        state = parser.fn(loc)
        if isinstance(state.result, Success):
            return state
        else:
            return State(ParseError(msg), state.text)

    return Parser(inner)


# def label1(msg: str):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             def inner(loc: LocatedText) -> State:
#                 state = func(*args, **kwargs).fn(loc)
#                 if isinstance(state.result, Success):
#                     return state
#                 else:
#                     return State(ParseError(msg), state.text)
#
#             return Parser(inner)
#
#         return wrapper
#
#     return decorator


def just(v) -> Parser:
    """
    直接让v作为解析成功的值返回，且不消耗任何字符
    :param v: 返回的成功值
    :return Parser: 未改变的Parser状态，但解析成功的值变为v
    """

    def inner(loc: LocatedText) -> State:
        return State(Success(v), loc)

    return Parser(inner)


def char(x: str) -> Parser:
    """
    解析某一个字符

    :param x: 需要解析的字符
    :return Parser: 解析此字符的Parser
    """
    return label(satisfy(lambda c: c == x), 'Excepted: {}'.format(x))


def space() -> Parser:
    """
    解析空格、\t、\n、\r等space值

    :return Parser: 解析space值的Parser
    """
    return label(satisfy(str.isspace), 'Excepted: space')


def digit() -> Parser:
    """
    解析数字 [0-9]

    :return Parser: 解析数字的Parser
    """
    return label(satisfy(str.isdigit), 'Excepted: digit')


def alpha() -> Parser:
    """
    解析字母 [A-Za-z]

    :return Parser: 解析字母的Parser
    """
    return label(satisfy(str.isalpha), 'Excepted: alpha')


def one_of(chrs: str) -> Parser:
    """
    解析所给字符串里的其中一个字符
    :param chrs: 所述的待解析字符串
    :return Parser: 解析所给字符其中之一的Parser
    """
    return label(satisfy(lambda c: c in chrs), 'Excepted: one of ' + ','.join(chrs))


def none_of(chrs: str) -> Parser:
    """
    解析所给字符串以外的任意一个字符
    :param chrs: 所述的待排除字符串
    :return Parser: 解析所给字符以外字符的Parser
    """
    return label(satisfy(lambda c: c not in chrs), 'Excepted: none of ' + ', '.join(chrs))


# def many(parser: Parser) -> Parser:
#
#

if __name__ == '__main__':
    res = run_parser(one_of('{}[]'), '${a}')
    print(res)
    print(res.text)
