from functools import partial
import numpy as np
from collections import OrderedDict
from lcopt.io import defaultDatabase, get_name
import re



def parameter_scan_specific_database(database):
    
    parameter_set = OrderedDict()
    
    cr_list = []
    items = database['items']
    
    for i in items:
        if i['type'] == 'product':
            cr_list.append(i['code'])
            
    no_products = len(cr_list)
    
    names = [get_name(x) for x in cr_list]
    
    matrix = np.zeros((no_products, no_products))
    for i in items:
        if i['type']== 'process':
            inputs = []
            for e in i['exchanges']:
                if e['type']=='production':
                    col_code = cr_list.index(e['input'][1])

                elif e['type'] =='technosphere':
                    row_code = cr_list.index(e['input'][1])
                    inputs.append((row_code, e['amount']))

            for ip in inputs:
                matrix[(ip[0],col_code)] = ip[1]
                
    for c, column in enumerate(matrix.T):
        for r, i in enumerate(column):
            if i>0:
                p_from = cr_list[r]
                p_to = cr_list[c]
                coords = (r,c)
                print('{}\t| {} --> {}'.format(coords, get_name(p_from), get_name(p_to)))
                
                parameter_set['p_{}_{}'.format(coords[0],coords[1])] = {
                    'value':1,
                    'function' : None,
                    'description' : 'Input of {} to create {}'.format(get_name(p_from), get_name(p_to)),
                    'coords':coords
                }
                
    return parameter_set, matrix, names
                
parameter_scan = partial(parameter_scan_specific_database, database = defaultDatabase)

def interactive_parameter_scan(parameter_set):
    for pk in parameter_set:
        p = parameter_set[pk]
        value = input(p['description'])
        p['value'] = value
        
    return parameter_set


def parse_function(function):
    
    int_param_re_pattern = "(p_\d{1,}_\d{1,})"
    ext_param_re_pattern = "(ep_)([\d\w]*)"
    
    int_param_re = re.compile(int_param_re_pattern)
    ext_param_re = re.compile(ext_param_re_pattern)
    
    function = int_param_re.sub(r"params['\1']['value']", function)
    function = ext_param_re.sub(r"ext_params['\2']", function)
    
    return eval(function)

def matrix_update(matrix, params, ext_params):
    for pk in params:
        p=params[pk]
        if p['function'] == None:
            
            c = p['coords']
            
            matrix[c] = p['value']
        else:
            matrix[p['coords']] = parse_function(p['function'])
            
    return matrix