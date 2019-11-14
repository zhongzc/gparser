# -*- coding: UTF-8 -*-
import gparser as gp
from collections import namedtuple

JNull = namedtuple('JNull', [])
JTrue = namedtuple('JTrue', [])
JFalse = namedtuple('JFalse', [])
JNum = namedtuple('JNum', ['value'])
JStr = namedtuple('JStr', ['value'])
JObj = namedtuple('JObj', ['value'])
JPair = namedtuple('JPair', ['key', 'value'])
JArr = namedtuple('JArr', ['value'])

if __name__ == '__main__':
    digits = gp.regex(r'[0-9]+')
    exponent = (gp.one_of('eE') + gp.one_of('-+').or_not() +
                digits).map(gp.concat)
    fractional = (gp.char('.') + digits).map(gp.concat)
    integral = gp.char('0') | gp.regex(r'[1-9][0-9]*')
    number = (gp.one_of('-+').or_not() + integral + fractional.or_not() +
              exponent.or_not()).map(gp.concat).map(lambda n:
                                                    JNum(float(n))).tk()
    null = gp.string('null') >> gp.just(JNull()).tk()
    false = gp.string('false') >> gp.just(JFalse()).tk()
    true = gp.string('true') >> gp.just(JTrue()).tk()
    string = gp.between(gp.char('"'), gp.many(gp.none_of('"')), gp.char('"')) \
        .map(lambda cs: ''.join(cs)).map(JStr).tk()

    jExp = gp.undef()

    array = gp.between(gp.char('['), jExp.sep_by(
        gp.char(',').tk()), gp.char(']')).map(JArr).tk()
    pair = (string + ~gp.char(':') + jExp).map(lambda k, v: JPair(k, v)).tk()
    obj = gp.between(gp.char('{'), pair.sep_by(
        gp.char(',').tk()), gp.char('}')).map(JObj).tk()

    jExp.assign((obj | array | string | true | false | null | number).tk())

    str = """{
    "firstName": "John",
    "lastName": "Smith",
    "age": 25,
    "address": {
        "streetAddress": "21 2nd Street",
        "city": "New York",
        "state": "NY",
        "postalCode": 10021
    },
    "phoneNumbers": [
        {
            "type": "home",
            "number": "212 555-1234"
        },
        {
            "type": "fax",
            "number": "646 555-4567"
        }
    ]
}"""
    res, t = jExp.run(str)
    print(res.get())
