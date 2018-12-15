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

    def get(self):
        for i in self:
            return i

        return None


"""
# Success

解析成功后的State.result包含的值
"""


class Success:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return 'Success(value={})'.format(self.value)

    def get(self):
        return self.value.get()


"""
# ParseError

解释失败后State.result包含的错误信息
"""
class ParseError:
    def __init__(self, msg):
        self.msg = msg

    def __repr__(self):
        return 'ParseError(msg={})'.format(self.msg)

    def get(self):
        raise RuntimeError('ParseError: {}'.format(self.msg))