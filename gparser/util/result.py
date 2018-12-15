# -*- coding: UTF-8 -*-
__author__ = 'Gaufoo, zhongzc_arch@outlook.com'

from collections import namedtuple


class Result:
    def __init__(self, *l):
        self.__lst = l

    def __iter__(self):
        for i in self.__lst:
            yield i

    def __add__(self, other):
        return Result(*(self.__lst + other.__lst))

    def __repr__(self):
        return 'Result({})'.format(', '.join(map(repr, self.__lst)))


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
