#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = 'Gaufoo, zhongzc_arch@outlook.com'

import unittest
from gparser.gparser import *


def test_type(t, inp: (Parser, str), res_type, remaining: str):
    state = run_parser(inp[0], inp[1])
    t.assertIsInstance(state.result, res_type)
    t.assertEqual(state.text.remaining(), remaining)


def test_context(t, inp: (Parser, str), result, remaining: str):
    state = run_parser(inp[0], inp[1])
    t.assertEqual(state.result, result)
    t.assertEqual(state.text.remaining(), remaining)


class ParserTest(unittest.TestCase):
    def test_map(self):
        test_context(self, (digit().map(eval), '123'), Success(1), '23')
        test_context(self, (alpha().map(lambda x: x.upper()), 'abc'), Success('A'), 'bc')

    def test_bind(self):
        test_context(self, (digit().flatmap(lambda c1: digit()
                                            .flatmap(lambda c2: digit()
                                                     .flatmap(lambda c3:
                                                              just(int(c1 + c2 + c3))))), '1234'), Success(123), '4')
        test_type(self, (digit().flatmap(lambda c1: digit()
                                         .flatmap(lambda c2: digit()
                                                  .flatmap(lambda c3:
                                                           just(int(c1 + c2 + c3))))), '12a4'), ParseError, 'a4')


    def test_then(self):
        test_context(self, (digit().then(digit()), '1234'), Success('2'), '34')
        test_type(self, (digit().then(alpha()), '1234'), ParseError, '234')
        test_context(self, (digit() >> digit(), '1234'), Success('2'), '34')
        test_type(self, (digit() >> alpha(), '1234'), ParseError, '234')

    def test_satisfy(self):
        test_context(self, (satisfy(lambda c: c == 'a'), 'abc'), Success('a'), 'bc')
        test_type(self, (satisfy(lambda c: c == 'b'), 'abc'), ParseError, 'abc')
        test_context(self, (satisfy(str.isdigit), '123'), Success('1'), '23')
        test_type(self, (satisfy(str.isalnum), ''), ParseError, '')

    def test_just(self):
        test_context(self, (just('&'), '987'), Success('&'), '987')
        test_context(self, (just(999), 'cn'), Success(999), 'cn')

    def test_char(self):
        test_context(self, (char('['), '[abc]'), Success('['), 'abc]')
        test_context(self, (char('9'), '987654321'), Success('9'), '87654321')
        test_type(self, (char('a'), '[abc]'), ParseError, '[abc]')

    def test_label(self):
        test_context(self, (label(char('a'), '777'), 'abc'), Success('a'), 'bc')
        test_context(self, (label(char('b'), '777'), 'abc'), ParseError('777'), 'abc')

    def test_space(self):
        test_context(self, (space(), '  7'), Success(' '), ' 7')
        test_context(self, (space(), '\t 7'), Success('\t'), ' 7')
        test_context(self, (space(), '\n 7'), Success('\n'), ' 7')
        test_context(self, (space(), '\r 7'), Success('\r'), ' 7')
        test_type(self, (space(), '\a 7'), ParseError, '\a 7')

    def test_digit(self):
        test_context(self, (digit(), '123'), Success('1'), '23')
        test_context(self, (digit(), '0?'), Success('0'), '?')
        test_type(self, (space(), 'abc'), ParseError, 'abc')

    def test_alpha(self):
        test_context(self, (alpha(), 'ZXY'), Success('Z'), 'XY')
        test_context(self, (alpha(), 'abc'), Success('a'), 'bc')
        test_type(self, (alpha(), '123'), ParseError, '123')

    def test_one_of(self):
        test_context(self, (one_of('{}[]'), '[]'), Success('['), ']')
        test_type(self, (one_of('{}[]'), '${a}'), ParseError, '${a}')

    def test_none_of(self):
        test_context(self, (none_of('{}[]'), '${a}'), Success('$'), '{a}')
        test_type(self, (none_of('{}[]'), '[]'), ParseError, '[]')

    if __name__ == '__main__':
        unittest.main()
