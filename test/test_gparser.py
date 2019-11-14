#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = 'Gaufoo, zhongzc_arch@outlook.com'

from gparser.parser import digit, char, number, string, alpha, space, spaces
from gparser.parser import just, ParseError, satisfy, label, one_of, regex
from gparser.parser import many, many1, skip, skip_many, sep_by, sep_by1
from gparser.parser import none_of, maybe, between
from .utils import check_fail_msg, check_succ_cont, check_type


def test_map():
    check_succ_cont((digit().map(int), '123'), 1, '23')
    check_succ_cont(
        (alpha().map(lambda x: x.upper()), 'abc'), 'A', 'bc')


def test_or():
    check_succ_cont(((digit() >> digit()) |
                     alpha(), '1abc'), 'a', 'bc')
    check_succ_cont(((digit() >> digit()) |
                     alpha(), '12abc'), '2', 'abc')
    check_succ_cont(((digit() >> digit())
                     | alpha(), 'abc'), 'a', 'bc')
    check_succ_cont(((digit() >> digit()) |
                     alpha(), '123abc'), '2', '3abc')
    check_succ_cont(
        (string('134') | string('23'), '123abc'), '23', 'abc')


def test_bind():
    p = digit().flatmap(lambda c1: digit()
                        .flatmap(lambda c2: digit()
                                 .flatmap(lambda c3:
                                          just(int(c1 + c2 + c3)))))
    check_succ_cont((p, '1234'), 123, '4')
    check_type((p, 'a4'), ParseError, 'a4')


def test_then():
    check_succ_cont((digit().then(digit()), '1234'), ('2'), '34')
    check_type((digit().then(alpha()), '1234'), ParseError, '234')
    check_succ_cont((digit() >> digit(), '1234'), ('2'), '34')
    check_type((digit() >> alpha(), '1234'), ParseError, '234')


def test_pleft():
    check_succ_cont((char('a') << char(')'), 'a)bc'), ('a'), 'bc')
    check_succ_cont(
        (char('(') >> char('a') << char(')'), '(a)bc'), ('a'), 'bc')


def test_satisfy():
    check_succ_cont((satisfy(lambda c: c == 'a'), 'abc'), ('a'), 'bc')
    check_type((satisfy(lambda c: c == 'b'), 'abc'), ParseError, 'abc')
    check_succ_cont((satisfy(str.isdigit), '123'), ('1'), '23')
    check_type((satisfy(str.isalnum), ''), ParseError, '')


def test_just():
    check_succ_cont((just('&'), '987'), ('&'), '987')
    check_succ_cont((just(999), 'cn'), (999), 'cn')


def test_char():
    check_succ_cont((char('['), '[abc]'), ('['), 'abc]')
    check_succ_cont((char('9'), '987654321'), ('9'), '87654321')
    check_type((char('a'), '[abc]'), ParseError, '[abc]')


def test_string():
    check_succ_cont((string('abcde'), 'abcdef'), ('abcde'), 'f')
    check_type((string('abcde'), 'abcdf'), ParseError, 'f')


def test_label():
    check_succ_cont((label(char('a'), '777'), 'abc'), ('a'), 'bc')
    check_fail_msg((label(char('b'), '777'), 'abc'), '777', 'abc')


def test_label2():
    check_succ_cont((char('a').label('777'), 'abc'), ('a'), 'bc')
    check_fail_msg((char('b').label('777'), 'abc'), '777', 'abc')


def test_space():
    check_succ_cont((space(), '  7'), (' '), ' 7')
    check_succ_cont((space(), '\t 7'), ('\t'), ' 7')
    check_succ_cont((space(), '\n 7'), ('\n'), ' 7')
    check_succ_cont((space(), '\r 7'), ('\r'), ' 7')
    check_type((space(), '\a 7'), ParseError, '\a 7')


def test_digit():
    check_succ_cont((digit(), '123'), ('1'), '23')
    check_succ_cont((digit(), '0?'), ('0'), '?')
    check_type((space(), 'abc'), ParseError, 'abc')


def test_alpha():
    check_succ_cont((alpha(), 'ZXY'), ('Z'), 'XY')
    check_succ_cont((alpha(), 'abc'), ('a'), 'bc')
    check_type((alpha(), '123'), ParseError, '123')


def test_regex():
    p = regex(r'[A-Za-z_][A-Za-z0-9_]*')
    check_succ_cont((p, '_iower3 = 2'), '_iower3', ' = 2')
    check_type((p, '42'), ParseError, '42')


def test_one_of():
    check_succ_cont((one_of('{}[]'), '[]'), ('['), ']')
    check_type((one_of('{}[]'), '${a}'), ParseError, '${a}')


def test_none_of():
    check_succ_cont((none_of('{}[]'), '${a}'), ('$'), '{a}')
    check_type((none_of('{}[]'), '[]'), ParseError, '[]')


def test_many():
    check_succ_cont((many(digit()), '123abc'),
                    (['1', '2', '3']), 'abc')
    check_succ_cont(
        (many(space()) >> digit(), '  \t\n12'), ('1'), '2')
    check_succ_cont((many(space()) >> digit(), '12'), ('1'), '2')


def test_many1():
    check_succ_cont((many1(digit()), '123abc'),
                    (['1', '2', '3']), 'abc')
    check_type((many1(space()) >> digit(), '12'), ParseError, '12')


def test_maybe():
    check_succ_cont((maybe(spaces()), '   123'),
                    ([' ', ' ', ' ']), '123')
    check_succ_cont((maybe(string('12')) |
                     string('13'), '133'), ('13'), '3')


def test_skip():
    check_succ_cont(
        (skip(spaces()) >> digit(), '   123'), ('1'), '23')
    check_succ_cont((skip(spaces()) >> digit(), '123'), ('1'), '23')


def test_skip_many():
    check_succ_cont((skip_many(digit()) >>
                     string('abc'), '9876abcd'), ('abc'), 'd')


def test_between():
    check_succ_cont(
        (between(char('['), string('abc'), char(']')), '[abc]'), 'abc', '')


def test_sep_by1():
    check_succ_cont((sep_by1(number(), spaces()),
                     '123 456 678'), [123, 456, 678], '')


def test_sep_by():
    check_succ_cont((sep_by(number(), spaces()),
                     '123 456 678'), [123, 456, 678], '')
    check_succ_cont((number().sep_by(spaces()),
                     '123 456 678'), [123, 456, 678], '')
    check_succ_cont((sep_by(number(), spaces()),
                     'abc ded aad'), [], 'abc ded aad')
