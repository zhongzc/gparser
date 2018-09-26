#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = 'Gaufoo, zhongzc_arch@outlook.com'

__see__ = 'http://www.cs.nott.ac.uk/~pszgmh/monparsing.pdf'

from collections import namedtuple
from typing import Callable
import copy


class LocatedText:
    """
    包含待解析字符串，以及字符串解析到的位置
    """
    __str = ...  # type: str
    __loc = ...  # type: int

    def __init__(self, inp: str, loc: int = 0):
        if loc > len(inp):
            raise RuntimeError('Invalid argument')
        self.__str = inp
        self.__loc = loc

    def __copy__(self):
        return LocatedText(self.__str, self.__loc)

    def remaining(self) -> str:
        """
        :return str: 剩余未解析的字符串
        """
        return self.__str[self.__loc:]

    def advance_one(self) -> None:
        """
        :return None: 成功解析一个字符后，负责前进一位
        """
        if self.isEOF():
            raise RuntimeError('Parsing has completed')
        self.__loc += 1

    def isEOF(self) -> bool:
        """
        :return bool: 字符串是否已经解析完成
        """
        return self.__loc == len(self.__str)

    def row(self) -> int:
        """
        :return int: 返回目前解析到的行数，以 1 开始计数
        """
        return self.__str[0: self.__loc].count('\n') + 1

    def col(self) -> int:
        """
        :return int: 返回目前解析到的列数，以 1 开始计数
        """
        l = self.__str[0: self.__loc].rfind('\n')
        if (l == -1):
            return self.__loc + 1
        else:
            return self.__loc - l

    def current_line(self) -> str:
        """
        :return str: 返回所解析到的完整行，以便输出错误信息
        例：
            '123\n456\n789'，若解析到'5'，则返回'456'
        """
        return self.__str.splitlines()[self.row() - 1]

    def column_caret(self) -> str:
        """
        :return str: 返回指示当前所解析字符的指针，以便输出错误信息
        例：
            '123\n456\n789'，若解析到'5'，则返回' ^'
            最终信息将显示：
            >> 456
            >>  ^
        """
        return (" " * (self.col() - 1)) + "^"

    def __repr__(self):
        return str({'loc': self.__loc, 'str': self.__str})

    def __str__(self):
        """
        :return str: 返回友好的解析位置信息
        例：
            '123\n456\n789'，若解析到'5'
            最终信息将显示：
            >> (2,2)
            >> 456
            >>  ^
        """
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


class State:
    """
    # State(result: T, text: LocatedText)

    解析后返回的状态，result的类型是(Success | ParseError)
    """

    def __init__(self, result, text: LocatedText):
        self.result = result
        self.text = text

    def is_successful(self):
        return isinstance(self.result, Success)

    def __repr__(self):
        return 'State({}, {})'.format(
            'result=' + repr(self.result),
            'text=' + repr(self.text)
        )

    def __str__(self):
        if self.is_successful():
            return 'Parsing succeed'
        else:
            return '{}\n{}'.format(
                self.result.msg,
                self.text
            )


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

    def __or__(self, other):
        """
        消耗or
        """

        def inner(loc: LocatedText) -> State:
            state = self.fn(loc)
            if state.is_successful():
                return state
            else:
                return other.fn(state.text)

        return Parser(inner)

    def flatmap(self, func):
        """
        Parser[A] -> (A -> Parser[B]) -> Parser[B]

        :see : https://en.wikipedia.org/wiki/Monad_(functional_programming)
        """

        def inner(loc: LocatedText) -> State:
            state = self.fn(loc)
            if state.is_successful():
                return func(state.result.value).fn(state.text)
            else:
                return state

        return Parser(inner)

    def map(self, func):
        return self.flatmap(lambda v: just(func(v)))

    def then(self, parser):
        return self.flatmap(lambda _: parser)

    def __rshift__(self, parser):
        return self.then(parser)

    def __lshift__(self, parser):
        return self.flatmap(lambda x: parser.flatmap(lambda _: just(x)))

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
        if state.is_successful():
            return state
        else:
            return State(ParseError(msg), state.text)

    return Parser(inner)


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
    assert len(x) == 1
    return label(satisfy(lambda c: c == x), 'Excepted: {}'.format(x))


def string(s: str) -> Parser:
    if s == '':
        return just('')
    else:
        return char(s[0]).flatmap(lambda x:
                                  string(s[1:]).flatmap(lambda xs:
                                                        just(x + xs)))


def space() -> Parser:
    """
    解析空格、\t、\n、\r等space值

    :return Parser: 解析space值的Parser
    """
    return label(satisfy(str.isspace), 'Excepted: space')


def spaces() -> Parser:
    return many(space())


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


def many(parser: Parser) -> Parser:
    return parser.flatmap(lambda x:
                          many(parser).flatmap(lambda xs:
                                               just([x] + xs))) | just([])


def many1(parser: Parser) -> Parser:
    return parser.flatmap(lambda x:
                          many(parser).flatmap(lambda xs:
                                               just([x] + xs)))


def skip(parser: Parser) -> Parser:
    return parser >> just(None)


def skip_many(parser: Parser) -> Parser:
    return many(parser) >> just(None)


def protect(parser: Parser) -> Parser:
    def inner(loc: LocatedText) -> State:
        pre_text = copy.copy(loc)
        state = parser.fn(loc)
        if state.is_successful():
            return state
        else:
            return State(state.result, pre_text)

    return Parser(inner)


if __name__ == '__main__':
    res1 = string('123456').run('123789456')
    res2 = string('123456').run('123456789')
    print(res1)
    print(res2)
