# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from bw2data import databases, methods, get_activity, Method
from bw2calc import LCA
from collections import defaultdict

def traverse_tagged_databases(functional_unit, method, label="tag",
                              default_tag="other"):
    """Traverse a functional unit throughout its foreground database(s), and
    group impacts by tag label.

    Contribution analysis work by linking impacts to individual activities.
    However, you also might want to group impacts in other ways. For example,
    give individual biosphere exchanges their own grouping, or aggregate two
    activities together.

    Consider this example system, where the letters are the tag labels, and the
    numbers are exchange amounts. The functional unit is one unit of the tree
    root.

    .. image:: images/tagged-traversal.png
       :alt: Example tagged supply chain

    In this supply chain, tags are applied to activities and biosphere exchanges.
    If a biosphere exchange is not tagged, it inherits the tag of its producing
    activity. Similarly, links to other databases are assessed with the usual
    LCA machinery, and the total LCA score is tagged according to its consuming
    activity. If an activity does not have a tag, a default tag is applied.

    We can change our visualization to show the use of the default tags:

    .. image:: images/tagged-traversal-2.png
       :alt: Example tagged supply chain

    And then we can manually calculate the tagged impacts. Normally we would
    need to know the actual biosphere flows and their respective
    characterization factors (CF), but in this example we assume that each
    CF is one. Our result, group by tags, would therefore be:

        * **A**: :math:`6 + 27 = 33`
        * **B**: :math:`30 + 44 = 74`
        * **C**: :math:`5 + 16 + 48 = 69`
        * **D**: :math:`14`

    This function will only traverse the foreground database, i.e. the
    database of the functional unit activity. A functional unit can have
    multiple starting nodes; in this case, all foreground databases are
    traversed.

    Input arguments:
        * ``functional_unit``: A functional unit dictionary, e.g. ``{("foo", "bar"): 42}``.
        * ``method``: A method name, e.g. ``("foo", "bar")``
        * ``label``: The label of the tag classifier. Default is ``"tag"``
        * ``default_tag``: The tag classifier to use if none was given. Default is ``"other"``

    Returns:

        Aggregated tags dictionary from ``aggregate_tagged_graph``, and tagged supply chain graph from ``recurse_tagged_database``.

    """
    lca = LCA(functional_unit, method)
    lca.lci(factorize=True)
    lca.lcia()

    method_dict = {o[0]: o[1] for o in Method(method).load()}

    graph = [recurse_tagged_database(key, amount, method_dict, lca, label, default_tag)
             for key, amount in functional_unit.items()]

    return aggregate_tagged_graph(graph), graph

def aggregate_tagged_graph(graph):
    """Aggregate a graph produced by ``recurse_tagged_database`` by the provided tags.

    Outputs a dictionary with keys of tags and numeric values.

    .. code-block:: python

        {'a tag': summed LCIA scores}

    """
    def recursor(obj, scores):
        scores[obj['tag']] += obj['impact']
        for flow in obj['biosphere']:
            scores[flow['tag']] += flow['impact']
        for exc in obj['technosphere']:
            scores = recursor(exc, scores)
        return scores

    scores = defaultdict(int)
    for obj in graph:
        scores = recursor(obj, scores)
    return scores

def recurse_tagged_database(activity, amount, method_dict, lca, label, default_tag):
    """Traverse a foreground database and assess activities and biosphere flows by tags.

    Input arguments:

        * ``activity``: Activity tuple or object
        * ``amount``: float
        * ``method_dict``: Dictionary of biosphere flow tuples to CFs, e.g. ``{("biosphere", "foo"): 3}``
        * ``lca``: An ``LCA`` object that is already initialized, i.e. has already calculated LCI and LCIA with same method as in ``method_dict``
        * ``label``: string
        * ``default_tag``: string

    Returns:

    .. code-block:: python

        {
            'activity': activity object,
            'amount': float,
            'tag': string,
            'impact': float (impact of inputs from outside foreground database),
            'biosphere': [{
                'amount': float,
                'impact': float,
                'tag': string
            }],
            'technosphere': [this data structure]
        }

    """
    if isinstance(activity, tuple):
        activity = get_activity(activity)

    inputs = list(activity.technosphere())
    inside = [exc for exc in inputs
              if exc['input'][0] == activity['database']]
    outside = {exc['input']: exc['amount'] * amount
               for exc in inputs
               if exc['input'][0] != activity['database']}

    if outside:
        lca.redo_lcia(outside)
        outside_score = lca.score
    else:
        outside_score = 0

    return {
        'activity': activity,
        'amount': amount,
        'tag': activity.get(label) or default_tag,
        'impact': outside_score,
        'biosphere': [{
            'amount': exc['amount'] * amount,
            'impact': exc['amount'] * amount * method_dict.get(exc['input'], 0),
            'tag': exc.get(label) or activity.get(label) or default_tag
        } for exc in activity.biosphere()],
        'technosphere': [recurse_tagged_database(exc.input, exc['amount'] * amount,
                                                 method_dict, lca, label, default_tag)
                         for exc in inside]
    }
