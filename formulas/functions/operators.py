#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2016-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

"""
Python equivalents of Excel operators.
"""
import datetime
import schedula as sh
import functools
import collections
import re
from . import (
    replace_empty, not_implemented, wrap_func, wrap_ufunc, Error, value_return
)
from .text import _str
from .look import _get_type_id

OPERATORS = collections.defaultdict(lambda: not_implemented)

numeric_wrap = functools.partial(wrap_ufunc, return_func=value_return)

# noinspection PyTypeChecker
OPERATORS.update({k: numeric_wrap(v) for k, v in {
    '+': lambda x, y: x + y,
    '-': lambda x, y: x - y,
    'U-': lambda x: -x,
    '*': lambda x, y: x * y,
    '/': lambda x, y: (x / y) if y else Error.errors['#DIV/0!'],
    '^': lambda x, y: x ** y,
    '%': lambda x: x / 100.0,
}.items()})
OPERATORS['U+'] = wrap_ufunc(
    lambda x: x, input_parser=lambda *a: a, return_func=value_return
)


def logic_input_parser(x, y):
    if x is sh.EMPTY:
        x = '' if isinstance(y, str) else 0
    if y is sh.EMPTY:
        y = '' if isinstance(x, str) else 0
    return (_get_type_id(x), x), (_get_type_id(y), y)


logic_wrap = functools.partial(
    wrap_ufunc, input_parser=logic_input_parser, return_func=value_return,
    args_parser=lambda *a: a
)


class DateTime:

    @staticmethod
    def get_datetime_from_str(date_str):
        if "-" in date_str:
            [yyyy, mm, dd] = date_str.split("-")
        elif "/" in date:
            [yyyy, mm, dd] = date_str.split("/")
        elif re.match('[1-2]\\d{3}年[0-1]{1}[0-9]{1}月[0-3]{1}[0-9]{1}日', date_str):
            yyyy = date[:4]
            mm = date[5:7]
            dd = date[8:10]
        else:
            raise ValueError("invalid date_str %s", date_str)

        return datetime.date(int(yyyy), int(mm), int(dd))


class CustomOperation:
    def __init__(self, x, y):
        try:
            self._x, self._y = x[1], y[1]
            date_pattern = re.compile("[1-2]\\d{3}[-/.][0-1]{1}[0-9]{1}[-/.][0-3]{1}[0-9]{1}")
            if date_pattern.match(self._x):
                self._x = DateTime.get_datetime_from_str(_x)
            if date_pattern.match(self._y):
                self._y = DateTime.get_datetime_from_str(_y)

        except Exception:
            self._x, self._y = x, y

    def gt(self):
        print('gt', self._x, self._y)
        return self._x > self._y


LOGIC_OPERATORS = collections.OrderedDict([
    ('>=', lambda x, y: x >= y),
    ('<=', lambda x, y: x <= y),
    ('!=', lambda x, y: x != y),
    ('<', lambda x, y: x < y),
    ('>', lambda x, y: CustomOperation(x, y).gt(),
    ('=', lambda x, y: x == y),
])
OPERATORS.update({k: logic_wrap(v) for k, v in LOGIC_OPERATORS.items()})
OPERATORS['&'] = wrap_ufunc(
    lambda x, y: x + y, input_parser=lambda *a: map(_str, a),
    args_parser=lambda *a: (replace_empty(v, '') for v in a),
    return_func=value_return
)
OPERATORS.update({k: wrap_func(v, ranges=True) for k, v in {
    ',': lambda x, y: x | y,
    ' ': lambda x, y: x & y,
    ':': lambda x, y: x + y
}.items()})
