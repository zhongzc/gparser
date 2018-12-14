# -*- coding: UTF-8 -*-
from gparser.util.locatedText import LocatedText
from gparser.util.result import Success

__author__ = 'Gaufoo, zhongzc_arch@outlook.com'


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

    def __iter__(self):
        return iter([self.result, self.text])
