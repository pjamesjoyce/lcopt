# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

#from .utils import python_2_unicode_compatible
import collections
import operator
import itertools

operators = {
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "is": operator.eq,  # Note: not pure python `is`!
    "iis": lambda x, y: x.lower() == y.lower(),
    "!=": operator.ne,
    "<>": operator.ne,
    "not": operator.ne,
    "inot": lambda x, y: x.lower() != y.lower(),
    ">=": operator.ge,
    ">": operator.gt,
    "has": operator.contains,
    "ihas": lambda x, y: y.lower() in x.lower(),
    "nothas": lambda x, y: not operator.contains(x, y),
    "in": lambda x, y: operator.contains(y, x),
    "notin": lambda x, y: not operator.contains(y, x),
    # No iin because in normally doesn't take string inputs
    "len": lambda x, y: len(x) == y,
}


def try_op(f, x, y):
    try:
        return f(x, y)
    except:
        return False


class Dictionaries(object):
    """Pretends to be a single dictionary when applying a ``Query`` to multiple databases.

    Usage:
        first_database = Database(...).load()
        second_database = Database(...).load()
        my_joined_dataset = Dictionaries(first_database, second_database)
        search_results = Query(filter_1, filter_2)(my_joined_dataset)

    """
    def __init__(self, *args):
        self.dicts = args

    def items(self):
        return itertools.chain(*[x.items() for x in self.dicts])


#@python_2_unicode_compatible
class Result(object):
    """A container that wraps a filtered dataset. Returned by a calling a ``Query`` object. A result object functions like a read-only dictionary; you can call ``Result[some_key]``, or ``some_key in Result``, or ``len(Result)``.

    The dataset can also be sorted, using ``sort(field)``; the underlying data is then a ``collections.OrderedDict``.

    Args:
        * *result* (dict): The filtered dataset.

    """
    def __init__(self, result):
        self.result = result
        if not isinstance(result, dict):
            raise ValueError(u"Must pass dictionary")

    def __str__(self):
        return "Query result with %i entries" % len(self.result)

    def __repr__(self):
        if not self.result:
            return u"Query result:\n\tNo query results found."
        data = list(self.result.items())[:20]
        return (u"Query result: (total %i)\n" % len(self.result) + \
            u"\n".join([u"%s: %s" % (k, v.get("name", "Unknown"))
                        for k, v in data])
            )

    def sort(self, field, reverse=False):
        """Sort the filtered dataset. Operates in place; does not return anything.

        Args:
            * *field* (str): The key used for sorting.
            * *reverse* (bool, optional): Reverse normal sorting order.

        """
        self.result = collections.OrderedDict(sorted(self.result.items(),
            key=lambda t: t[1].get(field, None), reverse=reverse))

    # Generic dictionary methods
    def __len__(self):
        return len(self.result)

    def __iter__(self):
        return iter(self.result)

    def keys(self):
        return self.result.keys()

    def items(self):
        return self.result.items()

    def items(self):
        return self.result.items()

    def __getitem__(self, key):
        return self.result[key]

    def __contains__(self, key):
        return key in self.result


class Query(object):
    """A container for a set of filters applied to a dataset.

    Filters are applied by calling the ``Query`` object, and passing the dataset to filter as the argument. Calling a ``Query`` with some data returns a ``Result`` object with the filtered dataset.

    Args:
        * *filters* (filters): One or more ``Filter`` objects.

    """
    def __init__(self, *filters):
        self.filters = list(filters)

    def add(self, filter_):
        """Add another filter.

        Args:
            *filter_* (``Filter``): A Filter object.

        """
        self.filters.append(filter_)

    def __call__(self, data):
        for filter_ in self.filters:
            data = filter_(data)
        return Result(data)


class Filter(object):
    """A filter on a dataset.

    The following functions are supported:

        * "<", "<=", "==", ">", ">=": Mathematical relations
        * "is", "not": Identity relations. Work on any Python object.
        * "in", "notin": List or string relations.
        * "iin", "iis", "inot": Case-insensitive string relations.
        * "len": Length relation.

    In addition, any function which defines a relationship between an input and an output can also be used.

    Examples:

        * All ``name`` values are *"foo"*: ``Filter("name", "is", "foo")``
        * All ``name`` values include the string *"foo"*: ``Filter("name", "has", "foo")``
        * Category (a list of categories and subcategories) includes *"foo"*: ``Filter("category", "has", "foo")``

    Args:
        * *key* (str): The field to filter on.
        * *function* (str or object): One of the pre-defined filters, or a callable object.
        * *value* (object): The value to test against.

    Returns:
        A ``Result`` object which wraps a new data dictionary.

    """
    def __init__(self, key, function, value):
        self.key = key
        self.function = function
        self.value = value
        if not callable(function):
            self.function = operators.get(function, None)
        if not self.function:
            raise ValueError("No valid function found")

    def __call__(self, data):
        return dict(((k, v) for k, v in data.items() if try_op(
            self.function, v.get(self.key, None), self.value)))


def NF(value):
    """Shortcut for a name filter"""
    return Filter(u"name", u"has", value)


def PF(value):
    """Shortcut for a reference product filter"""
    return Filter(u"reference product", u"has", value)
