#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = 'Gaufoo, zhongzc_arch@outlook.com'

import unittest
from gparser.gparser import *


def test_type(t, inp: (Parser, str), res_type, remaining: str):
    state = run_parser(inp[0], inp[1])
    t.assertIsInstance(state.result, res_type)
    t.assertEqual(state.text.remaining(), remaining)


def test_succ_cont(t, inp: (Parser, str), result, remaining: str):
    state = run_parser(inp[0], inp[1])
    t.assertEqual(*state.result.value, result)
    t.assertEqual(state.text.remaining(), remaining)

def test_fail_msg(t, inp: (Parser, str), msg, remaining: str):
    state = run_parser(inp[0], inp[1])
    t.assertEqual(state.result.msg, msg)
    t.assertEqual(state.text.remaining(), remaining)

class ParserTest(unittest.TestCase):
    def test_map(self):
        test_succ_cont(self, (digit().map(int), '123'), 1, '23')
        test_succ_cont(self, (alpha().map(lambda x: x.upper()), 'abc'), 'A', 'bc')

    def test_or(self):
        test_succ_cont(self, ((digit() >> digit()) | alpha(), '1abc'), 'a', 'bc')
        test_succ_cont(self, ((digit() >> digit()) | alpha(), '12abc'), '2', 'abc')
        test_succ_cont(self, ((digit() >> digit()) | alpha(), 'abc'), 'a', 'bc')
        test_succ_cont(self, ((digit() >> digit()) | alpha(), '123abc'), '2', '3abc')
        test_succ_cont(self, (string('134') | string('23'), '123abc'), '23', 'abc')

    def test_bind(self):
        test_succ_cont(self, (digit().flatmap(lambda c1: digit()
                                            .flatmap(lambda c2: digit()
                                                     .flatmap(lambda c3:
                                                              just(int(c1 + c2 + c3))))), '1234'), 123, '4')
        test_type(self, (digit().flatmap(lambda c1: digit()
                                         .flatmap(lambda c2: digit()
                                                  .flatmap(lambda c3:
                                                           just(int(c1 + c2 + c3))))), '12a4'), ParseError, 'a4')

    def test_then(self):
        test_succ_cont(self, (digit().then(digit()), '1234'), ('2'), '34')
        test_type(self, (digit().then(alpha()), '1234'), ParseError, '234')
        test_succ_cont(self, (digit() >> digit(), '1234'), ('2'), '34')
        test_type(self, (digit() >> alpha(), '1234'), ParseError, '234')

    def test_pleft(self):
        test_succ_cont(self, (char('a') << char(')'), 'a)bc'), ('a'), 'bc')
        test_succ_cont(self, (char('(') >> char('a') << char(')'), '(a)bc'), ('a'), 'bc')

    def test_satisfy(self):
        test_succ_cont(self, (satisfy(lambda c: c == 'a'), 'abc'), ('a'), 'bc')
        test_type(self, (satisfy(lambda c: c == 'b'), 'abc'), ParseError, 'abc')
        test_succ_cont(self, (satisfy(str.isdigit), '123'), ('1'), '23')
        test_type(self, (satisfy(str.isalnum), ''), ParseError, '')

    def test_just(self):
        test_succ_cont(self, (just('&'), '987'), ('&'), '987')
        test_succ_cont(self, (just(999), 'cn'), (999), 'cn')

    def test_char(self):
        test_succ_cont(self, (char('['), '[abc]'), ('['), 'abc]')
        test_succ_cont(self, (char('9'), '987654321'), ('9'), '87654321')
        test_type(self, (char('a'), '[abc]'), ParseError, '[abc]')

    def test_string(self):
        test_succ_cont(self, (string('abcde'), 'abcdef'), ('abcde'), 'f')
        test_type(self, (string('abcde'), 'abcdf'), ParseError, 'f')

    def test_label(self):
        test_succ_cont(self, (label(char('a'), '777'), 'abc'), ('a'), 'bc')
        test_fail_msg(self, (label(char('b'), '777'), 'abc'), '777', 'abc')

    def test_label2(self):
        test_succ_cont(self, (char('a').label('777'), 'abc'), ('a'), 'bc')
        test_fail_msg(self, (char('b').label('777'), 'abc'), '777', 'abc')

    def test_space(self):
        test_succ_cont(self, (space(), '  7'), (' '), ' 7')
        test_succ_cont(self, (space(), '\t 7'), ('\t'), ' 7')
        test_succ_cont(self, (space(), '\n 7'), ('\n'), ' 7')
        test_succ_cont(self, (space(), '\r 7'), ('\r'), ' 7')
        test_type(self, (space(), '\a 7'), ParseError, '\a 7')

    def test_digit(self):
        test_succ_cont(self, (digit(), '123'), ('1'), '23')
        test_succ_cont(self, (digit(), '0?'), ('0'), '?')
        test_type(self, (space(), 'abc'), ParseError, 'abc')

    def test_alpha(self):
        test_succ_cont(self, (alpha(), 'ZXY'), ('Z'), 'XY')
        test_succ_cont(self, (alpha(), 'abc'), ('a'), 'bc')
        test_type(self, (alpha(), '123'), ParseError, '123')

    def test_one_of(self):
        test_succ_cont(self, (one_of('{}[]'), '[]'), ('['), ']')
        test_type(self, (one_of('{}[]'), '${a}'), ParseError, '${a}')

    def test_none_of(self):
        test_succ_cont(self, (none_of('{}[]'), '${a}'), ('$'), '{a}')
        test_type(self, (none_of('{}[]'), '[]'), ParseError, '[]')

    def test_many(self):
        test_succ_cont(self, (many(digit()), '123abc'), (['1', '2', '3']), 'abc')
        test_succ_cont(self, (many(space()) >> digit(), '  \t\n12'), ('1'), '2')
        test_succ_cont(self, (many(space()) >> digit(), '12'), ('1'), '2')

    def test_many1(self):
        test_succ_cont(self, (many1(digit()), '123abc'), (['1', '2', '3']), 'abc')
        test_type(self, (many1(space()) >> digit(), '12'), ParseError, '12')

    def test_maybe(self):
        test_succ_cont(self, (maybe(spaces()), '   123'), ([' ', ' ', ' ']), '123')
        test_succ_cont(self, (maybe(string('12')) | string('13'), '133'), ('13'), '3')

    def test_skip(self):
        test_succ_cont(self, (skip(spaces()) >> digit(), '   123'), ('1'), '23')
        test_succ_cont(self, (skip(spaces()) >> digit(), '123'), ('1'), '23')

    def test_skip_many(self):
        test_succ_cont(self, (skip_many(digit()) >> string('abc'), '9876abcd'), ('abc'), 'd')

    if __name__ == '__main__':
        unittest.main()


class LocatedTextTest(unittest.TestCase):
    test_str = '01234\n54321\nabcde'

    def test_row(self):
        self.assertEqual(LocatedText(self.test_str, 0).row(), 1)
        self.assertEqual(LocatedText(self.test_str, 5).row(), 1)
        self.assertEqual(LocatedText(self.test_str, 6).row(), 2)
        self.assertEqual(LocatedText(self.test_str, 12).row(), 3)
        self.assertEqual(LocatedText(self.test_str, 16).row(), 3)

    def test_col(self):
        self.assertEqual(LocatedText(self.test_str, 0).col(), 1)
        self.assertEqual(LocatedText(self.test_str, 4).col(), 5)
        self.assertEqual(LocatedText(self.test_str, 5).col(), 6)
        self.assertEqual(LocatedText(self.test_str, 6).col(), 1)
        self.assertEqual(LocatedText(self.test_str, 13).col(), 2)

    def test_current_line(self):
        self.assertEqual(LocatedText(self.test_str, 0).current_line(), '01234')
        self.assertEqual(LocatedText(self.test_str, 6).current_line(), '54321')
        self.assertEqual(LocatedText(self.test_str, 16).current_line(), 'abcde')

    def test_column_caret(self):
        self.assertEqual(LocatedText(self.test_str, 0).column_caret(), '^')
        self.assertEqual(LocatedText(self.test_str, 6).column_caret(), '^')
        self.assertEqual(LocatedText(self.test_str, 16).column_caret(), '    ^')
        self.assertEqual(LocatedText(self.test_str, 11).column_caret(), '     ^')
