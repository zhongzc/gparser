# -*- coding: UTF-8 -*-
__author__ = 'Gaufoo, zhongzc_arch@outlook.com'
__see__ = 'http://www.cs.nott.ac.uk/~pszgmh/monparsing.pdf'

from gparser.util.state import State
from gparser.util.locatedText import LocatedText
from gparser.util.result import Result, Success, ParseError
from typing import Callable
from functools import reduce
import re
import copy


class Parser:
    """
    Parser(fn: LocatedText -> State)

    解析器，运行时接受一个LocatedText，返回解析后的状态
    """

    def __init__(self, fn: Callable[[LocatedText], State]):
        self.fn = fn

    def assign(self, parser):
        self.fn = parser.fn

    def run(self, inp: str) -> State:
        return self.fn(LocatedText(inp))

    def run_strict(self, inp: str) -> State:
        return (self << eof()).run(inp)

    def __call__(self, *args, **kwargs):
        return self.run(*args, **kwargs)

    def __or__(self, other):
        """
        消耗or
        """

        @Parser
        def inner(loc: LocatedText) -> State:
            state = self.fn(loc)
            if state.is_successful():
                return state
            else:
                return other.fn(state.text)

        return inner

    def flatmap(self, func):
        """
        Parser[A] -> (A -> Parser[B]) -> Parser[B]

        :see : https://en.wikipedia.org/wiki/Monad_(functional_programming)
        """

        @Parser
        def inner(loc: LocatedText) -> State:
            state = self.fn(loc)
            if state.is_successful():
                return func(*state.result.value).fn(state.text)
            else:
                return state

        return inner

    def __add__(self, other):
        return self.flatmap(lambda *x: other.flatmap(
            lambda *y: _trick_just(x + y)))

    def map(self, func):
        return self.flatmap(lambda *v: just(func(*v)))

    def then(self, parser):
        return self.flatmap(lambda *_: parser)

    def __rshift__(self, parser):
        return self.then(parser)

    def __lshift__(self, parser):
        return self.flatmap(lambda x: parser.flatmap(lambda *_: just(x)))

    def __invert__(self):
        return skip(self)

    def label(self, msg):
        return label(self, msg)

    def sep_by(self, sep):
        return sep_by(self, sep)

    def tk(self):
        return token(self)

    def or_not(self):
        return maybe(self) | _trick_just(Result())

    def maybe(self):
        return maybe(self)


def undef() -> Parser:
    @Parser
    def inner(_: LocatedText):
        raise NotImplementedError('该Parser并未实现，请调用assign进行赋值')

    return inner


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

    @Parser
    def inner(loc: LocatedText) -> State:
        if loc.isEOF():
            return State(ParseError("再无输入可解析"), loc)
        else:
            c = loc.remaining()[0]
            if pred(c):
                loc.advance()
                return State(Success(Result(c)), loc)
            else:
                return State(ParseError("不满足条件"), loc)

    return inner


def eof() -> Parser:
    @Parser
    def inner(loc: LocatedText) -> State:
        if loc.isEOF():
            return State(Success(Result()), loc)
        else:
            return State(ParseError("Excepted: <EOF>"), loc)

    return inner


def label(parser: Parser, msg: str) -> Parser:
    """
    为Parser提供进一步的错误信息

    :param parser: 需要修饰的Parser
    :param msg: 进一步的错误信息
    :return Parser: 修饰过的Parser
    """

    @Parser
    def inner(loc: LocatedText) -> State:
        state = parser.fn(loc)
        if state.is_successful():
            return state
        else:
            return State(ParseError(msg), state.text)

    return inner


def just(v) -> Parser:
    """
    直接让v作为解析成功的值返回，且不消耗任何字符
    :param v: 返回的成功值
    :return Parser: 未改变的Parser状态，但解析成功的值变为v
    """

    @Parser
    def inner(loc: LocatedText) -> State:
        return State(Success(Result(v)), loc)

    return inner


def fail(msg: str = "", back_step: int = 0) -> Parser:
    """
    直接导致解析错误，且不消耗任何字符
    :param back_step: number of back steps
    :param msg: 解析错误信息
    :return: Parser: 未改变的Parser状态，但直接解析错误
    """
    @Parser
    def inner(loc: LocatedText) -> State:
        loc.back(back_step)
        return State(ParseError(msg), loc)

    return inner


def _trick_just(r: Result) -> Parser:
    @Parser
    def inner(loc: LocatedText) -> State:
        return State(Success(r), loc)

    return inner


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
        return (char(s[0]) + string(s[1:])).map(lambda x, xs: x + xs)


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


def regex(rex) -> Parser:
    @Parser
    def inner(loc: LocatedText) -> State:
        res = re.match(rex, loc.remaining())
        if res is None:
            return State(ParseError("不满足正则条件"), loc)
        else:
            e = res.end()
            loc.advance(e)
            return State(Success(Result(res.group())), loc)

    return inner


def one_of(chrs: str) -> Parser:
    """
    解析所给字符串里的其中一个字符
    :param chrs: 所述的待解析字符串
    :return Parser: 解析所给字符其中之一的Parser
    """
    return label(satisfy(lambda c: c in chrs),
                 'Excepted: one of ' + ','.join(chrs))


def none_of(chrs: str) -> Parser:
    """
    解析所给字符串以外的任意一个字符
    :param chrs: 所述的待排除字符串
    :return Parser: 解析所给字符以外字符的Parser
    """
    return label(satisfy(lambda c: c not in chrs),
                 'Excepted: none of ' + ', '.join(chrs))


def many(parser: Parser) -> Parser:
    return parser.flatmap(lambda x:
                          many(parser).flatmap(lambda xs:
                                               just([x] + xs))) | just([])


def many1(parser: Parser) -> Parser:
    return (parser + many(parser)).map(lambda x, xs: [x] + xs)


def skip(parser: Parser) -> Parser:
    return parser >> _trick_just(Result())


def skip_many(parser: Parser) -> Parser:
    return many(parser) >> _trick_just(Result())


def skip_many1(parser: Parser) -> Parser:
    return many1(parser) >> _trick_just(Result())


def maybe(parser: Parser) -> Parser:
    """
    for backtracking
    """

    @Parser
    def inner(loc: LocatedText) -> State:
        pre_text = copy.copy(loc)
        state = parser.fn(loc)
        if state.is_successful():
            return state
        else:
            return State(state.result, pre_text)

    return inner


def between(lf: Parser, cont: Parser, rt: Parser) -> Parser:
    # return ~lf + cont + ~rt
    return lf >> cont << rt


def sep_by1(cont: Parser, sep: Parser) -> Parser:
    return (cont + many(sep >> cont)).map(lambda x, xs: [x] + xs)


def sep_by(cont: Parser, sep: Parser) -> Parser:
    return sep_by1(cont, sep) | just([])


def token(parser: Parser) -> Parser:
    # return ~spaces() + parser + ~spaces()
    return spaces() >> parser << spaces()


def chain_left(node: Parser, op: Parser) -> Parser:
    aux = (op + node).map(lambda fn, n: lambda x: fn(x, n))
    return (node + many(aux)).map(lambda fst, nps:
                                  reduce((lambda x, cmb: cmb(x)), [fst] + nps))


def chain_right(node: Parser, op: Parser) -> Parser:
    return node.flatmap(lambda l:
                        (op + chain_right(node, op)).map(lambda fn, r:
                                                         fn(l, r)) | just(l))


def number() -> Parser:
    ps = (char('-') | just('+'))
    pd = many1(digit()).map(lambda dlst: ''.join(dlst))
    return (ps + pd).map(lambda s, d: int(s + d))


def concat(*s):
    return ''.join(list(s))
