# -*- coding: UTF-8 -*-
from setuptools import setup, find_packages

setup(
    name = 'Gparser',
    version = '0.0.1',
    description = 'am expressive parser library',
    license = 'MIT License',
    url = 'https://github.com/zhongzc/gparser',
    author = 'Gaufoo',
    author_email = 'zhongzc_arch@outlook.com',
    packages = find_packages(exclude=["test.*", "test"]),
    include_package_data = True,
    platforms = 'any',
    install_requires = [],
)