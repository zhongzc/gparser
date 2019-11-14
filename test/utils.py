#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = 'Gaufoo, zhongzc_arch@outlook.com'

from gparser.parser import Parser, Result, run_parser


def check_type(inp: (Parser, str), res_type, remaining: str):
    state = run_parser(inp[0], inp[1])
    assert type(state.result) == res_type
    assert state.text.remaining() == remaining


def check_succ_cont(inp: (Parser, str), result, remaining: str):
    state = run_parser(inp[0], inp[1])
    assert state.result.value == Result(result)
    assert state.text.remaining() == remaining


def check_fail_msg(inp: (Parser, str), msg, remaining: str):
    state = run_parser(inp[0], inp[1])
    assert state.result.msg == msg
    assert state.text.remaining() == remaining
