from gparser.parser import LocatedText

test_str = '01234\n54321\nabcde'


def test_row():
    assert LocatedText(test_str, 0).row() == 1
    assert LocatedText(test_str, 5).row() == 1
    assert LocatedText(test_str, 6).row() == 2
    assert LocatedText(test_str, 12).row() == 3
    assert LocatedText(test_str, 16).row() == 3


def test_col():
    assert LocatedText(test_str, 0).col() == 1
    assert LocatedText(test_str, 4).col() == 5
    assert LocatedText(test_str, 5).col() == 6
    assert LocatedText(test_str, 6).col() == 1
    assert LocatedText(test_str, 13).col() == 2


def test_current_line():
    assert LocatedText(test_str, 0).current_line() == '01234'
    assert LocatedText(test_str, 6).current_line() == '54321'
    assert LocatedText(test_str, 16).current_line() == 'abcde'


def test_column_caret():
    assert LocatedText(test_str, 0).column_caret() == '^'
    assert LocatedText(test_str, 6).column_caret() == '^'
    assert LocatedText(test_str, 16).column_caret() == '    ^'
    assert LocatedText(test_str, 11).column_caret() == '     ^'
