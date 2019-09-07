#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

setup(
    name='bupt-api',
    version='0.0.1',
    author='zekin',
    author_email='wzekin@gmail.com',
    url='https://zhuanlan.zhihu.com/p/26159930',
    description=u'北邮的一些api,陆续添加中',
    packages=['bupt-api'],
    install_requires=['beautifulsoup4', 'requests', 'ics'],
)