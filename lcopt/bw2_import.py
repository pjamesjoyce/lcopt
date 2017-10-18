from bw2io.package import BW2Package
from lcopt.model import LcoptModel, unnormalise_unit
from lcopt.interact import FlaskSandbox
from copy import deepcopy
from collections import OrderedDict
from warnings import warn
#import networkx as nx


def validate_imported_model(model):
    db = model.database['items']
    ecoinvent_name = model.ecoinventName
    ecoinvent_items = [x['items'] for x in model.external_databases if x['name'] == ecoinvent_name][0]
    ecoinvent_links = []

    for key, item in db.items():
        if item.get('ext_link'):
            if item['ext_link'][0] == ecoinvent_name:
                ecoinvent_links.append(item['ext_link'])

    for link in ecoinvent_links:
        if not ecoinvent_items.get(link):
            warn("{} not found in ecoinvent 3.3 cutoff database".format(link))
            return False

    return True   


def get_sandbox_root(links):
    froms = []
    tos = []
    
    for l in links:
        froms.append(l['sourceID'])
        tos.append(l['targetID'])
    
    fset = set(froms)
    tset = set(tos)
    roots = [x for x in tset if x not in fset] 

    #print(sorted(fset))
    #print(sorted(tset))

    if len(roots) == 1:
        return roots[0]
    else:
        print('Multiple roots found!')   
        return False


def get_sandbox_neighbours(sandbox_links, root):
    neighbours = []
    for x in sandbox_links:
        if x['targetID'] == root:
            neighbours.append(x['sourceID'])
            
    return neighbours   


def hierarchy_pos(links, root, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None, min_dx=0.03):
    '''If there is a cycle that is reachable from root, then this will see infinite recursion.
       G: the graph
       root: the root node of current branch
       width: horizontal space allocated for this branch - avoids overlap with other branches
       vert_gap: gap between levels of hierarchy
       vert_loc: vertical location of root
       xcenter: horizontal location of root
       pos: a dict saying where all nodes go if they have been assigned
       parent: parent of this branch.'''
    if pos is None:
        pos = {root: (xcenter, vert_loc)}
    else:
        pos[root] = (xcenter, vert_loc)

    neighbors = get_sandbox_neighbours(links, root)

    if len(neighbors) != 0:
        dx = max(width / len(neighbors), min_dx)
        #nextx = xcenter - width / 2 - dx / 2
        nextx = pos[root][0] - (len(neighbors) - 1) * dx / 2 - dx
        
        for neighbor in neighbors:
            nextx += dx
            pos = hierarchy_pos(links, neighbor, width=dx, vert_gap=vert_gap, 
                                vert_loc=vert_loc - vert_gap, xcenter=nextx, pos=pos, 
                                parent=root)
    return pos


def compute_layout(fs):
    #nx_nodes = []
    #n = deepcopy(nodes)
    #for x in n:
    #    i = x.pop('id')
    #    nx_nodes.append((i, x))

    #nx_links = []
    #l = deepcopy(links)
    #for x in l:
    #    from_id = x.pop('sourceID')
    #    to_id = x.pop('targetID')
    #    nx_links.append((from_id, to_id, x))

    #G = nx.Graph()
    #G.add_nodes_from(nx_nodes)
    #G.add_edges_from(nx_links)
    nodes = fs.nodes
    links = fs.links

    pos = hierarchy_pos(links, get_sandbox_root(links))
    pos90 = {k: (v[1], -v[0]) for k, v in pos.items()}

    xs = [v[0] for k, v in pos90.items()]
    ys = [v[1] for k, v in pos90.items()]

    s_xs = [(x - min(xs))for x in xs]
    s_ys = [(y - min(ys))for y in ys]

    row = 50
    col = 300
    max_height = 1000
    max_width = 1100

    height = min([max_height, len(set(ys)) * row])
    width = min([max_width, len(set(xs)) * col])

    pad_top = 20
    pad_left = 20

    pos_scaled = {k: ((v[0] - min(xs)) / max(s_xs) * width + pad_left, (v[1] - min(ys)) / max(s_ys) * height + pad_top) for k, v in pos90.items()}

    sandbox = {k: {'x': v[0], 'y': v[1]} for k, v in pos_scaled.items()}

    processes = [k for k, v in fs.reverse_process_output_map.items()]

    process_fudge_factor = 10 # process boxes are (generally) 20px taller than inputs, so if we shift these up 10 pixels it looks nicer...

    for k, v in sandbox.items():
        if k in processes:
            sandbox[k]['y'] -= process_fudge_factor

    return sandbox


def create_LcoptModel_from_BW2Package(import_filename):
    
    import_data = BW2Package.load_file(import_filename)
    orig_db = import_data[0]['data']
    db_name = import_data[0]['name']
    model = LcoptModel(db_name)
    db = deepcopy(orig_db)

    temp_param_set = []
    temp_production_param_set = []

    for k, v in db.items():
        exchanges = []
        production_amount = v.get('production amount', 1)

        if production_amount != 1:
            print("NOTE: Production amount for {} is not 1 unit ({})".format(v['name'], production_amount, production_amount))

        temp_production_param_set.append({'of': v['name'], 'amount': production_amount})

        """p_exs = [e for e in v['exchanges'] if e['type'] == 'production']
                                t_exs = [e for e in v['exchanges'] if e['type'] == 'technosphere']
                        
                                if len(p_exs) == 0:
                                    print(v['name'] + " has no production exchange")
                        
                                if len(p_exs) == 0 and len(t_exs) == 1:
                                    temp_tech_exc = deepcopy(t_exs[0])
                                    exc_name = temp_tech_exc.pop('name')
                                    exc_input = temp_tech_exc.pop('input')
                                    exc_unit = unnormalise_unit(temp_tech_exc.pop('unit'))
                                    exc_type = 'production'
                        
                                    this_exc = {
                                        'name': exc_name,
                                        'type': exc_type,
                                        'unit': exc_unit,
                                        'amount': 1,
                                        'lcopt_type': 'intermediate',
                                    }
                                    exchanges.append(this_exc)"""

        for e in v['exchanges']:

            exc_name = e.pop('name')
            exc_input = e.pop('input')
            exc_unit = unnormalise_unit(e.pop('unit'))
            exc_amount = e.pop('amount')
            exc_type = e.pop('type')

            temp_param_set.append({'from': exc_name, 'to': v['name'], 'amount': exc_amount})

            if e.get('location'):
                e.pop('location')

            if exc_type == 'production':
                this_exc = {
                    'name': exc_name,
                    'type': exc_type,
                    'unit': exc_unit,
                    'lcopt_type': 'intermediate',
                }
                this_exc = {**this_exc, **e}

                exchanges.append(this_exc)

            elif exc_type == 'technosphere':

                this_exc = {
                    'name': exc_name,
                    'type': exc_type,
                    'unit': exc_unit,
                }

                exc_db = exc_input[0]

                if exc_db == db_name:
                    this_exc['lcopt_type'] = 'intermediate'
                else:
                    this_exc['ext_link'] = ('Ecoinvent3_3_cutoff', exc_input[1])
                    this_exc['lcopt_type'] = 'input'

                this_exc = {**this_exc, **e}

                exchanges.append(this_exc)

            elif exc_type == 'biosphere':

                this_exc = {
                    'name': exc_name,
                    'type': 'technosphere',
                    'unit': exc_unit,
                }

                this_exc['ext_link'] = exc_input
                this_exc['lcopt_type'] = 'biosphere'

                this_exc = {**this_exc, **e}

                exchanges.append(this_exc)

        model.create_process(v['name'], exchanges)

    param_set = OrderedDict()

    #model.parameter_scan()

    #print (model.names)

    for p in temp_param_set:
        exc_from = model.names.index(p['from'])
        exc_to = model.names.index(p['to'])
        if exc_from != exc_to:
            parameter_id = "p_{}_{}".format(exc_from, exc_to)
            param_set[parameter_id] = p['amount']

    for p in temp_production_param_set:
        exc_of = model.names.index(p['of'])
        parameter_id = "p_{}_production".format(exc_of)
        param_set[parameter_id] = p['amount']

    model.parameter_sets[db_name] = param_set

    model.parameter_scan()

    fs = FlaskSandbox(model)

    model.sandbox_positions = compute_layout(fs)

    if validate_imported_model(model):
        print('\nModel created successfully')
        return model
    else:
        print('\nModel not valid - check the ecoinvent version in brightway2')
        return None
