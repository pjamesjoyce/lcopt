from bw2io.package import BW2Package
from lcopt.model import LcoptModel, unnormalise_unit
from copy import deepcopy
from collections import OrderedDict
from warnings import warn


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


def create_LcoptModel_from_BW2Package(import_filename):
    
    import_data = BW2Package.load_file(import_filename)
    orig_db = import_data[0]['data']
    db_name = import_data[0]['name']
    model = LcoptModel(db_name)
    db = deepcopy(orig_db)

    temp_param_set = []

    for k, v in db.items():
        exchanges = []
        production_amount = v['production amount']

        if production_amount != 1:
            print("NOTE: Production amount for {} is not 1 unit ({}). Parameters for this process will be divided by {} to normalise to one unit of output".format(v['name'], production_amount, production_amount))

        for e in v['exchanges']:

            exc_name = e.pop('name')
            exc_input = e.pop('input')
            exc_unit = unnormalise_unit(e.pop('unit'))
            exc_amount = e.pop('amount') / production_amount
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

    for p in temp_param_set:
        exc_from = model.names.index(p['from'])
        exc_to = model.names.index(p['to'])
        if exc_from != exc_to:
            parameter_id = "p_{}_{}".format(exc_from, exc_to)
            param_set[parameter_id] = p['amount']

    model.parameter_sets[db_name] = param_set

    if validate_imported_model(model):
        print('\nModel created successfully')
        return model
    else:
        print('\nModel not valid - check the ecoinvent version in brightway2')
        return None
