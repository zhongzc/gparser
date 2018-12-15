# -*- coding: UTF-8 -*-

import sys

sys.path.append("..")

import gparser as gp

if __name__ == '__main__':
    pNum = (gp.regex('\d+(\.\d+)?').map(lambda n: float(n))).tk()
    pAdd = (gp.char('+') >> gp.just(lambda x, y: x + y)).tk()
    pSub = (gp.char('-') >> gp.just(lambda x, y: x - y)).tk()
    pMul = (gp.char('*') >> gp.just(lambda x, y: x * y)).tk()
    pDiv = (gp.char('/') >> gp.just(lambda x, y: x / y)).tk()

    pExp = gp.undef()
    pFactor = gp.undef()
    pTerm = gp.undef()

    # Exp = Factor (( '+' | '-' ) Factor)*
    pExp.assign(gp.chain_left(pFactor, pAdd | pSub).tk())

    # Factor = Term (( '*' | '/' ) Term)*
    pFactor.assign(gp.chain_left(pTerm, pMul | pDiv).tk())

    # Term = <数字> | '(' Exp ')'
    pTerm.assign(pNum | gp.between(gp.char('(').tk(), pExp, gp.char(')').tk()))

    assert pExp.run_strict('384.666 - 80 * (85.5 + 3)').result.value.get() == (384.666 - 80 * (85.5 + 3))
