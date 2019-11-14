# -*- coding: UTF-8 -*-
__author__ = 'Gaufoo, zhongzc_arch@outlook.com'


class LocatedText:
    """
    包含待解析字符串，以及字符串解析到的位置
    """
    __str = ...  # type: str
    __loc = ...  # type: int

    def __init__(self, inp: str, loc: int = 0):
        if loc > len(inp):
            raise RuntimeError('Invalid argument')
        self.__str = inp
        self.__loc = loc

    def __copy__(self):
        return LocatedText(self.__str, self.__loc)

    def remaining(self) -> str:
        """
        :return str: 剩余未解析的字符串
        """
        return self.__str[self.__loc:]

    def advance(self, n=1) -> None:
        """
        :return None: 成功解析一个字符后，负责前进一位
        """
        if self.isEOF():
            raise RuntimeError('Parsing has completed')
        self.__loc += n

    def back(self, n=1) -> None:
        if self.__loc - n < 0:
            raise RuntimeError('Back too much')
        self.__loc -= n

    def isEOF(self) -> bool:
        """
        :return bool: 字符串是否已经解析完成
        """
        return self.__loc == len(self.__str)

    def row(self) -> int:
        """
        :return int: 返回目前解析到的行数，以 1 开始计数
        """
        return self.__str[0: self.__loc].count('\n') + 1

    def col(self) -> int:
        """
        :return int: 返回目前解析到的列数，以 1 开始计数
        """
        loc = self.__str[0: self.__loc].rfind('\n')
        if (loc == -1):
            return self.__loc + 1
        else:
            return self.__loc - loc

    def current_line(self) -> str:
        """
        :return str: 返回所解析到的完整行，以便输出错误信息
        例：
            '123\n456\n789'，若解析到'5'，则返回'456'
        """
        return self.__str.splitlines()[self.row() - 1]

    def column_caret(self) -> str:
        """
        :return str: 返回指示当前所解析字符的指针，以便输出错误信息
        例：
            '123\n456\n789'，若解析到'5'，则返回' ^'
            最终信息将显示：
            >> 456
            >>  ^
        """
        return (" " * (self.col() - 1)) + "^"

    def __repr__(self):
        return str({'loc': self.__loc, 'str': self.__str})

    def __str__(self):
        """
        :return str: 返回友好的解析位置信息
        例：
            '123\n456\n789'，若解析到'5'
            最终信息将显示：
            >> (2,2)
            >> 456
            >>  ^
        """
        return '({},{})'.format(self.row(), self.col()) + '\n' + \
               self.current_line() + '\n' + \
               self.column_caret()
