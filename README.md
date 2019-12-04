# Gparser
[![PyPI](https://img.shields.io/pypi/v/gparser.svg)](https://pypi.python.org/pypi)
[![Build Status](https://travis-ci.com/zhongzc/gparser.svg?branch=master)](https://travis-ci.com/zhongzc/gparser)
[![codecov](https://codecov.io/gh/zhongzc/gparser/branch/master/graph/badge.svg)](https://codecov.io/gh/zhongzc/gparser)

Parsec-like thinking model + Python DSL = an intuitive and easy-to-use parser library ^^

## Get Started

- Install

```sh
$ pip install gparser
```

- Run

```sh
$ python3                                
Python 3.6.7 (default, Oct 25 2018, 09:16:13) 
[GCC 5.4.0 20160609] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import gparser as gp
...
```

## Hello World

A toy parser:
```python
import gparser as gp             # (1) import gparser

dot = gp.char('.')               # (2) define a dot parser 
result, restTxt = dot.run('./')  # (3) run the parser

print(result)                    # (4) print the result
# Success(value=Result('.'))

print(result.get())
# .

print(restTxt)
# (1,2)
# ./
#  ^
```

Use `run_strict` to parse the entire input:
```python
...
result, restTxt = dot.run_strict('.foo')

print(result)
# ParseError(msg='Excepted: <EOF>')

print(restTxt)
# (1,2)
# .foo
#  ^
```

## More

For more detailed documentation, see [Gparser Document](https://gaufoo.com/gparser/)
