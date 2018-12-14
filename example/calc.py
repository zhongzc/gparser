# -*- coding: UTF-8 -*-

import sys
sys.path.append("..")

import gparser as gp

if __name__ == '__main__':
    pNum = gp.many1(gp.digit()).map(lambda ds: int(''.join(ds)))
    pAdd = gp.char('+') >> gp.just(lambda x, y: x + y)
    pSub = gp.char('-') >> gp.just(lambda x, y: x - y)
    pMul = gp.char('*') >> gp.just(lambda x, y: x * y)
    pDiv = gp.char('/') >> gp.just(lambda x, y: x / y)

    pExp = gp.undef()
    pFactor = gp.undef()
    pTerm = gp.undef()

    # Exp = Factor (( '+' | '-' ) Factor)*
    pExp.assign(gp.chain_left(pFactor, pAdd | pSub))

    # Factor = Term (( '*' | '/' ) Term)*
    pFactor.assign(gp.chain_left(pTerm, pMul | pDiv))

    # Term = <数字> | '(' Exp ')'
    pTerm.assign(pNum | gp.between(gp.char('('), pExp, gp.char(')')))