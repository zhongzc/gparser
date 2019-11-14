# Gparser
[![PyPI](https://img.shields.io/pypi/v/gparser.svg)](https://pypi.python.org/pypi)
[![Build Status](https://travis-ci.com/zhongzc/gparser.svg?branch=master)](https://travis-ci.com/zhongzc/gparser)
[![codecov](https://codecov.io/gh/zhongzc/gparser/branch/master/graph/badge.svg)](https://codecov.io/gh/zhongzc/gparser)

## Parser Combinator Library

关于Python课程的Final Project，本人综合考虑了个人兴趣、项目难度等多个方面，并结合自身水平，最终决定用Python编写[Parser Combinator](https://en.wikipedia.org/wiki/Parser_combinator)库。希望通过编写这一Python Parser Combinator库，能够将自己心中对于易用性、简洁性、上手容易程度都颇为合理的Parser库的理解，用Python版API较好地呈现出来。

基于以上的目标，此Parser库会以用户最简单的上手程度、最少的心智负担为主要争取目标，同时提供更为强大的、更富表现力的表达式，来完成对任何字符组合的解析任务。因此，尽管此库运用了许多[函数式编程](https://en.wikipedia.org/wiki/Functional_programming)的概念，但是用户并不需要补充任何相关知识，也可较好地运用此库完成任务。


## Get Started

- 安装

```sh
$ pip install gparser
```

- 使用

```sh
$ python3                                
Python 3.6.7 (default, Oct 25 2018, 09:16:13) 
[GCC 5.4.0 20160609] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import gparser as gp
...
```

## Hello World

编写最简单的Parser：
```python
import gparser as gp             # (1)

dot = gp.char('.')               # (2)
result, restTxt = dot.run('./')  # (3)
print(result)
print(restTxt)                   # (4)
```
1. 将Gparser库引入到环境内，并取别名为`gp`
2. `char`函数能够解析一个字符，此处解析一个`.`字符，并返回一个`Parser`对象
3. `Parser`对象中的`run`方法可以应用于待解析的字符串，返回`State`对象。`State`包含解析结果（`Success | ParseError`）对象和剩余字符串（`LocatedText`）对象，可以用Python中的多值匹配语法进行赋值。此处`result`即为解析结果对象，`restTxt`即为剩余字符串对象
4. 打印解析结果和剩余字符串

输出如下：
```python
# print(result)
Success(value=Result('.'))  # (1)

# print(restTxt)
(1,2)                        # (2)
./
 ^                           # (3)
```
1. 解析成功，返回`Success`对象，里面包含`Result`对象，可供提取或者进一步的处理，如何进行进一步处理会在文档后面进行介绍
2. 表明解析到的位置坐标，这里表示解析到第1行第2列的`/`处
3. 用用户友好的方式展示解析到的行以及待解析字符所在位置

解析结果`result`的类型可能是`Success`或者`ParseError`，可以通过`get`方法提取解析成功结果，假设解析失败，`get`方法会抛出异常：
```python
...
print(result.get())
    
# 输出：
# .
```

要想运行`Parser`对象进行解析，还有另外一个函数`run_strict`，和`run`最大的区别是：`run`不进行字符串结尾（即`EOF`）进行检测，而`run_strict`如果解析到最后没有消耗完整个字符串，则视为解析错误。
```python
...
result, restTxt = dot.run_strict('.foo')
print(result)
print(restTxt)
```
输出结果如下：
```python
# print(result)
ParseError(msg='Excepted: <EOF>') # (1)

# print(restTxt)
(1,2)
.foo
 ^
```
1. 解析错误返回`ParseError`对象，里面包含错误信息`Excepted: <EOF>`，向用户提示解析错误的原因


## 更多

更多详细文档请查阅[Gparser Document](https://gaufoo.com/gparser/)
