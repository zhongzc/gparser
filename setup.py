# -*- coding: UTF-8 -*-
from setuptools import setup, find_packages

install_requires = []
tests_require = ['pytest', 'pytest-cov']
setup_requires = ['pytest-runner']

setup(
    name='gparser',
    version='0.1.1',
    description='am expressive parser library',
    license='MIT License',
    url='https://github.com/zhongzc/gparser',
    author='Gaufoo',
    author_email='zhongzc_arch@outlook.com',
    install_requires=install_requires,
    tests_require=tests_require,
    setup_requires=setup_requires,
    packages=find_packages(),
)
