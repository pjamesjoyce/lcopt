import numpy as np
import json
from scipy.sparse import coo_matrix
import os
from .data_store import storage

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

def export_disclosure(model, parameter_set=None, folder_path=None):
    
    if parameter_set is None:
        matrix = model.matrix.copy()
        filename = '{}_unspecified.json'.format(model.name.replace(" ", "_"))

    else:
        matrix = specify_matrix(model, parameter_set)
        filename = '{}_ps_{}.json'.format(model.name.replace(" ", "_"), parameter_set)

    if model.save_option == 'curdir':
        base_dir = os.getcwd()
    else:
        base_dir = storage.disclosures_dir

    if isinstance(folder_path, str):
        export_folder = os.path.join(base_dir, folder_path)
        if not os.path.isdir(export_folder):
            os.mkdir(export_folder)
    else:
        export_folder = base_dir            
    
    efn = os.path.join(export_folder, filename)

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
    Af_shape = (l,l)
    Af = np.zeros(Af_shape)

    
    for i, c in enumerate(foreground):
        c_lookup = c[0]
        for j, r in enumerate(foreground):
            r_lookup = r[0]
            Af[i, j] = matrix[c_lookup, r_lookup]
            
    # Create Ad
    Ad_shape = (len(technosphere),l)
    Ad = np.zeros(Ad_shape)
    
    for i, c in enumerate(foreground):
        c_lookup = c[0]
        for j, r in enumerate(technosphere):
            r_lookup = r[0]
            Ad[j, i] = matrix[r_lookup,c_lookup ]
            
    # Create Bf
    Bf_shape = (len(biosphere),l)
    Bf = np.zeros(Bf_shape)
    for i, c in enumerate(foreground):
        c_lookup = c[0]
        for j, r in enumerate(biosphere):
            r_lookup = r[0]
            Bf[j, i] = matrix[r_lookup,c_lookup]
    
    # Get extra info about the foreground flows
    foreground_info = [model.database['items'][model.get_exchange(x[1])] for x in foreground]

    # Get technosphere and biosphere data from external links
    technosphere_links = [model.database['items'][model.get_exchange(x[1])].get('ext_link',(None, '{}'.format(x[1]))) for x in background if model.database['items'][model.get_exchange(x[1])]['lcopt_type'] == "input"]
    biosphere_links = [model.database['items'][model.get_exchange(x[1])]['ext_link'] for x in background if model.database['items'][model.get_exchange(x[1])]['lcopt_type'] == "biosphere"]
    
    # Get technosphere ids
    technosphere_info = []
    for t in technosphere_links:
        y = t[0]
        if y is None:
            technosphere_info.append(model.database['items'][model.get_exchange(t[1])])
        else:
            e = [i for i, x in enumerate (model.external_databases) if x['name'] == y][0]
            technosphere_info.append(model.external_databases[e]['items'][t])
    
    # Get biosphere ids
    biosphere_ids = []
    for b in biosphere_links:
        y = b[0]
        e = [i for i, x in enumerate (model.external_databases) if x['name'] == y][0]
        biosphere_ids.append((model.external_databases[e]['items'][b]))
    
    # final preparations
    foreground_names = [{'index':i,'name': x[1], 'unit':foreground_info[i]['unit'], 'location':foreground_info[i]['location']} for i, x in enumerate(foreground)]
    technosphere_names = [{'index':i, 'ecoinvent_name': technosphere_info[i].get('name', 'n/a'), 'ecoinvent_id':technosphere_info[i].get('activity', 'n/a'), 'brightway_id':technosphere_links[i], 'unit':technosphere_info[i].get('unit', 'n/a'), 'location':technosphere_info[i].get('location', 'n/a')} for i, x in enumerate(technosphere)]
    biosphere_names = [{'index':i, 'name':"{}, {}, {}".format(biosphere_ids[i]['name'], biosphere_ids[i]['type'],  ",".join(biosphere_ids[i]['categories'])),'biosphere3_id': biosphere_links[i], 'unit': biosphere_ids[i]['unit']} for i, x in enumerate(biosphere)]
    
    # collate the data
    data = {
        'foreground flows':foreground_names,
        'Af':{'shape': Af_shape, 'data': matrix_to_coo(Af)},
        'background flows': technosphere_names,
        'Ad':{'shape': Ad_shape, 'data': matrix_to_coo(Ad)},
        'foreground emissions': biosphere_names,
        'Bf':{'shape': Bf_shape, 'data': matrix_to_coo(Bf)}
    }
    
    # export the data   
    with open(efn, 'w') as f:
        json.dump(data, f)
        
    return efn
