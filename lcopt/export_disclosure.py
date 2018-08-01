import numpy as np
import json
from scipy.sparse import coo_matrix

def matrix_to_coo(m):
    m_coo = coo_matrix(m)
    return [[[int(m_coo.row[i]), int(m_coo.col[i])], float(m_coo.data[i])] for i, _ in enumerate(m_coo.data)]

def specify_matrix(model, ps_id):
    
    eps = model.evaluated_parameter_sets
    
    if isinstance(ps_id, str):
        ps = eps[ps_id]
    else:
        ps = eps[list(eps.keys())[ps_id]]
        
    matrix = model.matrix.copy()

    for k, v in ps.items():
        if k[:4] == "n_p_":
            coords = [int(x) for x in k.split("_")[-2:]]
            matrix[coords[0], coords[1]] = v

    return matrix

def export_disclosure(model, parameter_set=None):
    
    if parameter_set is None:
        matrix = model.matrix.copy()
        efn = '{}_unspecified.json'.format(model.name.replace(" ", "_"))
    else:
        matrix = specify_matrix(model, parameter_set)
        efn = '{}_ps_{}.json'.format(model.name.replace(" ", "_"), parameter_set)
    
    background = [(i, x) for i, x in enumerate(model.names) if list(matrix.sum(axis=0))[i] == 0]
    foreground = [(i, x) for i, x in enumerate(model.names) if list(matrix.sum(axis=0))[i] != 0]
    fu = [(i, x) for i, x in enumerate(model.names) if list(matrix.sum(axis=1))[i] == 0 and list(matrix.sum(axis=0))[i] != 0]
    unused = [(i, x) for i, x in enumerate(model.names) if list(matrix.sum(axis=1))[i] == 0 and list(matrix.sum(axis=0))[i] == 0]
    
    background = sorted(list(set(background) - set(unused))) # get rid of unused items
    foreground = sorted(list(set(foreground) - set(unused))) # get rid of unused items
    foreground = fu + [x for x in foreground if x not in fu] # set fu to be the first item in the foreground matrix
    
    #split background into technosphere and biosphere portions
    technosphere = [x for x in background if model.database['items'][model.get_exchange(x[1])]['lcopt_type'] == "input"]
    biosphere = [x for x in background if model.database['items'][model.get_exchange(x[1])]['lcopt_type'] == "biosphere"]
    
    # Create Af
    l = len(foreground)
    Af = np.zeros((l,l))
    
    for i, c in enumerate(foreground):
        c_lookup = c[0]
        for j, r in enumerate(foreground):
            r_lookup = r[0]
            Af[i, j] = matrix[c_lookup, r_lookup]
            
    # Create Ad
    Ad = np.zeros((len(background),l))
    
    Ad = np.zeros((len(technosphere),l))
    for i, c in enumerate(foreground):
        c_lookup = c[0]
        for j, r in enumerate(technosphere):
            r_lookup = r[0]
            Ad[j, i] = matrix[r_lookup,c_lookup ]
            
    # Create Bf
    Bf = np.zeros((len(biosphere),l))
    for i, c in enumerate(foreground):
        c_lookup = c[0]
        for j, r in enumerate(biosphere):
            r_lookup = r[0]
            Bf[j, i] = matrix[r_lookup,c_lookup]
    
    # Get technosphere and biosphere data from external links
    technosphere_links = [model.database['items'][model.get_exchange(x[1])].get('ext_link',(None, '{}'.format(x[1]))) for x in background if model.database['items'][model.get_exchange(x[1])]['lcopt_type'] == "input"]
    biosphere_links = [model.database['items'][model.get_exchange(x[1])]['ext_link'] for x in background if model.database['items'][model.get_exchange(x[1])]['lcopt_type'] == "biosphere"]
    
    # Get technosphere ids
    technosphere_ids = []
    for t in technosphere_links:
        y = t[0]
        if y is None:
            technosphere_ids.append((t[1], "cutoff exchange"))
        else:
            e = [i for i, x in enumerate (model.external_databases) if x['name'] == y][0]
            technosphere_ids.append((model.external_databases[e]['items'][t]['name'], model.external_databases[e]['items'][t]['activity']))
    
    # Get biosphere ids
    biosphere_ids = []
    for b in biosphere_links:
        y = b[0]
        e = [i for i, x in enumerate (model.external_databases) if x['name'] == y][0]
        biosphere_ids.append((model.external_databases[e]['items'][b]))
    
    # final preparations
    foreground_names = [(i, x[1]) for i, x in enumerate(foreground)]
    technosphere_names = [{'ecoinvent_name': technosphere_ids[i][0], 'ecoinvent_id':technosphere_ids[i][1], 'brightway_id':technosphere_links[i]} for i, x in enumerate(technosphere)]
    biosphere_names = [{'name':"{}, {}, {}".format(biosphere_ids[i]['name'], biosphere_ids[i]['type'],  ",".join(biosphere_ids[i]['categories'])),'biosphere3_id': biosphere_links[i]} for i, x in enumerate(biosphere)]
    
    # collate the data
    data = {
        'foreground flows':foreground_names,
        'Af':matrix_to_coo(Af),
        'background flows': technosphere_names,
        'Ad':matrix_to_coo(Ad),
        'Foreground emissions': biosphere_names,
        'Bf':matrix_to_coo(Bf)
    }
    
    # export the data   
    with open(efn, 'w') as f:
        json.dump(data, f)
        
    return efn
