# -*- coding: UTF-8 -*-
from setuptools import setup, find_packages

setup(
    name = 'gparser',
    version = '0.0.2',
    description = 'am expressive parser library',
    license = 'MIT License',
    url = 'https://github.com/zhongzc/gparser',
    author = 'Gaufoo',
    author_email = 'zhongzc_arch@outlook.com',
    packages = find_packages(exclude=["test.*", "test", "example.*", "example"]),
    include_package_data = True,
    platforms = 'any',
    install_requires = [],
)
