from bw2data import databases, methods, get_activity, Method
from bw2calc import LCA
from collections import defaultdict

def multi_traverse_tagged_databases(functional_unit, methods, label="tag", default_tag="other", secondary_tags=[]):

    lca = LCA(functional_unit, methods[0])
    lca.lci()#factorize=True)
    lca.lcia()

    method_dicts = [{o[0]: o[1] for o in Method(method).load()} for method in methods]

    graph = [multi_recurse_tagged_database(key, amount, methods, method_dicts, lca, label, default_tag, secondary_tags)
             for key, amount in functional_unit.items()]

    return multi_aggregate_tagged_graph(graph), graph


def multi_aggregate_tagged_graph(graph):

    def recursor(obj, scores):
        if not scores.get(obj['tag']):
            scores[obj['tag']] = [x for x in obj['impact']]
        else:
            scores[obj['tag']] = [sum(x) for x in zip(scores[obj['tag']], obj['impact'])]
            
        for flow in obj['biosphere']:
            if not scores.get(flow['tag']):
                scores[flow['tag']] = [x for x in flow['impact']]
            else:
                scores[flow['tag']] = [sum(x) for x in zip(scores[flow['tag']], flow['impact'])]
            
        for exc in obj['technosphere']:
            scores = recursor(exc, scores)
        return scores

    scores = defaultdict(int)
    for obj in graph:
        scores = recursor(obj, scores)
    return scores

def multi_recurse_tagged_database(activity, amount, methods, method_dicts, lca, label, default_tag, secondary_tags=[]):
   
    if isinstance(activity, tuple):
        activity = get_activity(activity)

    inputs = list(activity.technosphere())
    inside = [exc for exc in inputs
              if exc['input'][0] == activity['database']]
    outside = {exc['input']: exc['amount'] * amount
               for exc in inputs
               if exc['input'][0] != activity['database']}

    if outside:
        outside_scores = []
        for n, m in enumerate(methods):
            lca.switch_method(m)
            lca.redo_lcia(outside)
            outside_scores.append(lca.score)
    else:
        outside_scores = [0] * len(methods)
        
    return {
        'activity': activity,
        'amount': amount,
        'tag': activity.get(label) or default_tag,
        'secondary_tags':[activity.get(t[0]) or t[1] for t in secondary_tags],
        'impact': outside_scores,
        'biosphere': [{
            'amount': exc['amount'] * amount,
            'impact': [exc['amount'] * amount * method_dict.get(exc['input'], 0) for method_dict in method_dicts],
            'tag': exc.get(label) or activity.get(label) or default_tag,
            'secondary_tags':[exc.get(t[0]) or activity.get(t[0]) or t[1] for t in secondary_tags]
        } for exc in activity.biosphere()],
        'technosphere': [multi_recurse_tagged_database(exc.input, exc['amount'] * amount, methods,
                                                 method_dicts, lca, label, default_tag, secondary_tags)
                         for exc in inside]
    }



def get_cum_impact(d, max_levels=100):

    this_d = d
    
    def cum_impact_recurse(d):

        to_return = {}
        cum_impact = [0] * len(d['impact'])

        for k, v in d.items():
            if k == 'technosphere':
                #print('technosphere')
                for e in v:
                    #print (e['activity'])
                    #cum_impact += e['impact']
                    cum_impact = [sum(x) for x in zip(cum_impact, e['impact'])]
                    if 'cum_impact' in e.keys():
                        #cum_impact += e['cum_impact']
                        cum_impact = [sum(x) for x in zip(cum_impact, e['cum_impact'])]

                    if k in to_return.keys():
                        to_return[k].append(cum_impact_recurse(e))
                    else:
                        to_return[k] = [cum_impact_recurse(e)]

            elif k == 'biosphere':
                to_return[k] = v
                if len(v) != 0:
                    for b in v:
                        #cum_impact += b['impact']
                        cum_impact = [sum(x) for x in zip(cum_impact, b['impact'])]

            elif k == 'activity':
                #print (k,v)
                to_return[k] = str(v)
            #elif k == 'impact':
            #   print('impact of {} = {}'.format(d['activity'], v))

            else:
                to_return[k] = v
        #print('cum_impact of {} = {}'.format(d['activity'], cum_impact))
        to_return['cum_impact'] = cum_impact

        return to_return

    for i in range(max_levels):
        prev_d = this_d
        this_d = cum_impact_recurse(prev_d)
        if this_d == prev_d:
            #print('breaking after {} levels'.format(i+1))
            break

    return this_d

def drop_pass_through_levels(d, checkSecondary = True):

    to_return = {}

    inSecondary = False
    if checkSecondary:
        inSecondary = 'intermediate' in d['secondary_tags']

    if d['tag'] == 'intermediate' or inSecondary:
        #print('this needs to be dropped')
        #print ('Dropping {}'.format(d['activity']))
        for key in d.keys():
            if key != 'technosphere':
                if key == 'activity':
                    d[key] = str(d['technosphere'][0][key])
                #print(key, d[key], d['technosphere'][0][key])
                d[key] = d['technosphere'][0][key]
        if 'technosphere' in d['technosphere'][0].keys():
            d['technosphere'] = d['technosphere'][0]['technosphere']

    for k, v in d.items():
        #print (k)
        if k == 'technosphere':
            #print('technosphere')
            for e in v:

                if k in to_return.keys():
                    to_return[k].append(drop_pass_through_levels(e, checkSecondary))
                else:
                    to_return[k] = [drop_pass_through_levels(e, checkSecondary)]

        elif k == 'activity':
            #print (k,v)
            to_return[k] = str(v)

        else:
            to_return[k] = v

    return to_return