#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = 'Gaufoo, zhongzc_arch@outlook.com'

from collections import namedtuple
from typing import Callable


class LocatedText:
    """
    字符串解析到的位置
    """
    __str = ...  # type: str
    __loc = ...  # type: int

    def __init__(self, inp: str):
        self.__str = inp
        self.__loc = 0

    def remaining(self) -> str:
        return self.__str[self.__loc:]

    def advance_one(self) -> None:
        self.__loc += 1

    def isEOF(self) -> bool:
        return self.__loc == len(self.__str)

    def __repr__(self):
        return self.__str[self.__loc:]


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


"""
# Parser(fn: LocatedText -> State)

解析器，接受一个LocatedText，返回解析后的状态
"""
Parser = namedtuple('Parser', ['fn'])


def run_parser(parser: Parser, inp: str) -> State:
    """
    运行Parser

    :param parser: 构建好的解析器
    :param inp: 待解析字符串
    :return: 解析完的状态，返回Success或者ParseError
    """
    return parser.fn(LocatedText(inp))


def satisfy(pred: Callable[[str], bool]) -> Parser:
    """
    若下一个字符满足判断条件(pred)，则解析成功

    :param pred: 下一个字符该满足的条件
    :return: 相应的Parser
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
    :return: 修饰过的Parser
    """
    def inner(loc: LocatedText) -> State:
        state = parser.fn(loc)
        if isinstance(state.result, Success):
            return state
        else:
            return State(ParseError(msg), state.text)
    return Parser(inner)


def char(x: str) -> Parser:
    """
    解析某一个字符

    :param x: 需要解析的字符
    :return: 解析此字符的Parser
    """
    return label(satisfy(lambda c: c == x), 'Excepted: {}'.format(x))


def space() -> Parser:
    """
    解析空格、\t、\n、\r等space值

    :return: 解析space值的Parser
    """
    return label(satisfy(str.isspace), 'Excepted: space')


if __name__ == '__main__':
    print(run_parser(char('a'), 'abc'))
