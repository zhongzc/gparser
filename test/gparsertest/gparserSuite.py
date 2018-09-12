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
    def test_satisfy(self):
        test_context(self, (satisfy(lambda c: c == 'a'), 'abc'), Success('a'), 'bc')
        test_type(self, (satisfy(lambda c: c == 'b'), 'abc'), ParseError, 'abc')
        test_context(self, (satisfy(str.isdigit), '123'), Success('1'), '23')
        test_type(self, (satisfy(str.isalnum), ''), ParseError, '')

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

    if __name__ == '__main__':
        unittest.main()
