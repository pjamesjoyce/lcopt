from lcopt.io import *
from functools import partial
from collections import OrderedDict
import numpy as np
import re
import pickle
import random
from copy import deepcopy
import pandas as pd
from flask import Flask, request, render_template
import webbrowser
import warnings
from random import randint

from jinja2 import Environment, PackageLoader

#From bw2 - edited to reinsert capitalisation of units

UNITS_NORMALIZATION = {
    "a": "year",  # Common in LCA circles; could be confused with are
    "Bq": "Becquerel",
    "g": "gram",
    "Gj": "gigajoule",
    "h": "hour",
    "ha": "hectare",
    "hr": "hour",
    "kBq": "kilo Becquerel",
    "kg": "kilogram",
    "kgkm": "kilogram kilometer",
    "km": "kilometer",
    "kj": "kilojoule",
    "kWh": "kilowatt hour",
    "l": "litre",
    "lu": "livestock unit",
    "m": "meter",
    "m*year": "meter-year",
    "m2": "square meter",
    "m2*year": "square meter-year",
    "m2a": "square meter-year",
    "m2y": "square meter-year",
    "m3": "cubic meter",
    "m3*year": "cubic meter-year",
    "m3a": "cubic meter-year",
    "m3y": "cubic meter-year",
    "ma": "meter-year",
    "metric ton*km": "ton kilometer",
    "MJ": "megajoule",
    "my": "meter-year",
    "nm3": "cubic meter",
    "p": "unit",
    "personkm": "person kilometer",
    "person*km": "person kilometer",
    "pkm": "person kilometer",
    "tkm": "ton kilometer",
    "vkm": "vehicle kilometer",
    'kg sw': "kilogram separative work unit",
    'km*year': "kilometer-year",
    'metric ton*km': "ton kilometer",
    'person*km': "person kilometer",
    'Wh': 'watt hour',
}

def unnormalise_unit(unit):
    if unit in UNITS_NORMALIZATION.keys():
        return unit
    else:
        
        un_units = list(filter(lambda x:UNITS_NORMALIZATION[x]==unit, UNITS_NORMALIZATION))
        #print (un_units)
        return un_units[0]


DISABLE_SEARCH = False
# This is a copy straight from bw2data.query, extracted so as not to cause a dependency.
try:
    from lcopt.bw2query import Query, Dictionaries, Filter
except ImportError:
    warnings.warn("bw2data module not found. Search functions will not work")
    DISABLE_SEARCH = True




# This is the decorator for functions to be disabled if bw2data isn't found
def req_bw2data(my_function):
    def req_check(*args,**kwargs):
        #print ("checking requirements are met...")
        if DISABLE_SEARCH:
            warnings.warn("bw2data module not found. Search functions do not work")
        else:
            ret = my_function(*args, **kwargs)
            return ret
    return req_check


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

#PARAMETER_TEMPLATE = read template file as string?

def loadModel(modelName):
    return pickle.load(open("{}.pickle".format(modelName), "rb"))

class LcoptModel(object):
    """docstring for LcoptModel"""
    def __init__(self, name = hex(random.getrandbits(128))[2:-1], load = None):
        super(LcoptModel, self).__init__()
        
        # name the instance
        self.name = name
        
        # set up the database, parameter dictionaries, the matrix and the names of the exchanges
        self.database = {'items': {}, 'name': '{}_Database'.format(self.name)}
        self.external_databases = []
        self.params = OrderedDict()
        self.ext_params = []
        self.matrix = None
        self.names = None
        self.parameter_sets = OrderedDict()
        self.model_matrices = OrderedDict()
        self.technosphere_matrices = OrderedDict()
        self.leontif_matrices = OrderedDict()
        self.parameter_map = {}
         
        if load != None:
            self.load(load)
                    
        # create partial version of io functions
        self.add_to_database = partial(add_to_specified_database, database = self.database)
        self.get_exchange = partial(get_exchange_from_database, database=self.database)
        self.exists_in_database = partial(exists_in_specific_database, database = self.database)
        self.get_name = partial(get_exchange_name_from_database, database=self.database)
        self.get_unit = partial(get_exchange_unit_from_database, database=self.database)
        
        # create a partial for saving that defaults to the name of the instance
        #self.save = partial(self.saveAs, filename = self.name)
        
        
        
    def rename(self,newname):
        """change the name of the class"""
        self.name = newname
        
    #def saveAs(self, filename):
    #    """save the instance as a pickle"""
    #    pickle.dump(self, open("{}.pickle".format(filename), "wb"))
    
    def save(self):
        """save the instance as a pickle"""
        pickle.dump(self, open("{}.pickle".format(self.name), "wb"))
        
    def load(self, filename):
        """load data from another instance - allows older versions to be loaded into the newer version of the class"""
        savedInstance = pickle.load(open("{}.pickle".format(filename), "rb"))
        
        try:
            # name the instance
            self.name = savedInstance.name

            # set up the database, parameter dictionaries, the matrix and the names of the exchanges
            self.database = savedInstance.database
            self.params = savedInstance.params
            self.ext_params = savedInstance.ext_params
            self.matrix = savedInstance.matrix
            self.names = savedInstance.names
            self.parameter_sets = savedInstance.parameter_sets
            self.model_matrices = savedInstance.model_matrices
            self.technosphere_matrices = savedInstance.technosphere_matrices
            self.leontif_matrices = savedInstance.leontif_matrices
            self.external_databases = savedInstance.external_databases
            self.parameter_map = savedInstance.parameter_map
        except Exception:
            pass

    
        
    def create_product (self, name, location ='GLO', unit='kg', **kwargs):
        """create a new product with md5 hash id in the model instances database"""
        new_product = item_factory(name=name, location=location, unit=unit, type='product', **kwargs)

        if not exists_in_database(new_product['code']):
            self.add_to_database(new_product)
            print ('{} added to database'.format(name))
            return self.get_exchange(name)
        else:
            #print('{} already exists in this database'.format(name))
            return False

    def create_process(self, name, exchanges, location ='GLO', unit='kg'):
        """create a new process, including all new exchanges in the model instance database"""
        found_exchanges = []
        for e in exchanges:

            exc_name = e.pop('name', None)
            exc_type = e.pop('type', None)

            this_exchange = get_exchange(exc_name)
            
            if this_exchange == None:
                my_unit = e.pop('unit', unit)
                    
                this_exchange = self.create_product(exc_name, location=location, unit=my_unit, **e)
            
            found_exchanges.append(exchange_factory(this_exchange, exc_type, 1, 1, '{} exchange of {}'.format(exc_type, exc_name)))
            
        new_process = item_factory(name=name, location=location, unit=unit, type='process', exchanges=found_exchanges)
        
        self.add_to_database(new_process)

        self.parameter_scan()

        return True


    def parameter_scan(self):
        """scan the database of the model instance to generate and expose parameters"""
        
        #self.parameter_map = {}
        #self.params = OrderedDict()

        cr_list = []
        items = self.database['items']

        for key in items.keys():
            i = items[key]
            if i['type'] == 'product':
                cr_list.append(i['code'])

        no_products = len(cr_list)

        self.names = [self.get_name(x) for x in cr_list]

        self.matrix = np.zeros((no_products, no_products))
        
        for key in items.keys():
            i = items[key]
            if i['type']== 'process':
                inputs = []
                for e in i['exchanges']:
                    if e['type']=='production':
                        col_code = cr_list.index(e['input'][1])

                    elif e['type'] =='technosphere':
                        row_code = cr_list.index(e['input'][1])
                        inputs.append((row_code, e['amount']))

                for ip in inputs:
                    self.matrix[(ip[0],col_code)] = ip[1]

        for c, column in enumerate(self.matrix.T):
            for r, i in enumerate(column):
                if i>0:
                    p_from = cr_list[r]
                    p_to = cr_list[c]
                    coords = (r,c)
                    #print('{}\t| {} --> {}'.format(coords, self.get_name(p_from), self.get_name(p_to)))

                    if not 'p_{}_{}'.format(coords[0],coords[1]) in self.params:
                        self.params['p_{}_{}'.format(coords[0],coords[1])] = {
                            'function' : None,
                            'description' : 'Input of {} to create {}'.format(self.get_name(p_from), self.get_name(p_to)),
                            'coords':coords,
                            'unit' : self.get_unit(p_from)
                        }

                    else:
                        pass
                        #print('p_{}_{} already exists'.format(coords[0],coords[1]))

                    if not 'p_{}_{}'.format(coords[0],coords[1]) in self.parameter_map:
                        self.parameter_map[(p_from,p_to)] = 'p_{}_{}'.format(coords[0],coords[1])

        return True
        
        
    def add_parameter(self, param_name, description = None, default = 0):
        if description == None:
            description = "Parameter called {}".format(param_name)
        
        name_check = lambda x:x['name'] == param_name
        name_check_list = list(filter(name_check, self.ext_params))
        if len(name_check_list) == 0:
            self.ext_params.append({'name':param_name, 'description': description, 'default': default})
        else:
            print('{} already exists - choose a different name'.format(param_name))
        
    def create_parameter_set(self):
        p_set = OrderedDict()
        p_set_name = "ParameterSet_{}".format(len(self.parameter_sets)+1)
        p = self.params
        for k in p.keys():
            if p[k]['function'] == None:
                p_set[k] = float(input("{} >  ".format(p[k]['description'])))
            else:
                print("{} is determined by a function".format(p[k]['description']))

        for e in self.ext_params:
            p_set['e_{}'.format(e[0])] = float(input("value for {} >  ".format(e[1])))
            
        self.parameter_sets[p_set_name] = p_set
        
     # convert parameter sets into matrices   
        
    def parse_function(self, function, parameter_set):

        int_param_re_pattern = "(p_\d{1,}_\d{1,})"
        ext_param_re_pattern = "(e_[\d\w_]{1,})"

        int_param_re = re.compile(int_param_re_pattern)
        ext_param_re = re.compile(ext_param_re_pattern)

        function = int_param_re.sub(r"parameter_set['\1']", function)
        function = ext_param_re.sub(r"parameter_set['\1']", function)
        
        #print(function)

        return eval(function)
    
    def generate_matrices(self):
        
        #overwrite old matrices
        self.model_matrices = OrderedDict()
        self.technosphere_matrices = OrderedDict()
        self.leontif_matrices = OrderedDict()
        
        #generate coefficient matrices
        for ps_k in self.parameter_sets.keys():
            ps = self.parameter_sets[ps_k]
            matrix_copy = deepcopy(self.matrix)

            for pk in self.params:
                p = self.params[pk]
                
                if p['function'] == None:
                    c = p['coords']
                    matrix_copy[c] = ps[pk]
                else:
                    matrix_copy[p['coords']] = self.parse_function(p['function'], ps)
                    
            self.model_matrices[ps_k] = matrix_copy
        
        #generate technosphere matrices
        for ps_k in self.parameter_sets.keys():
            self.technosphere_matrices[ps_k] = self.model_matrices[ps_k] - np.identity(len(self.model_matrices[ps_k]))

        #generate leontif matrices
        for ps_k in self.parameter_sets.keys():
            self.leontif_matrices[ps_k] = np.linalg.inv(np.identity(len(self.model_matrices[ps_k]))-self.model_matrices[ps_k])
    
    def list_parameters_as_df(self):
        to_df = []

        for i, e in enumerate(self.ext_params):
            row = {}
            row['id'] = e[0]
            row['coords'] = "n/a"
            row['description'] = e[1]
            row['function'] = "n/a"

            to_df.append(row)

        for pk in self.params:
            p = self.params[pk]
            row = {}
            row['id'] = pk
            row['coords'] = p['coords']
            row['description'] = p['description']
            row['function'] = p['function']

            to_df.append(row)

        df = pd.DataFrame(to_df)
        
        return df

    def matrix_as_df(self, matrix):

        df = pd.DataFrame(data = matrix, index=self.names, columns = self.names)

        return df

    def import_external_db(self, db_file):
        db = pickle.load(open("{}.pickle".format(db_file), "rb"))
        name = list(db.keys())[0][0]
        new_db = {'items': db, 'name': name}
        self.external_databases.append(new_db)


    @req_bw2data
    def search_databases(self, search_term, location = None, markets_only=False):

        data = Dictionaries(self.database['items'], *[x['items'] for x in self.external_databases])

        query = Query()

        if markets_only:
            market_filter = Filter("name", "has", "market for")
            query.add(market_filter)
        
        if location is not None:
            location_filter = Filter("location", "has", location)
            query.add(location_filter)
        
        query.add(Filter("name", "has", search_term))
        
        result = query(data)
        
        return result


### Database to SimaPro ###

    def database_to_SimaPro_csv(self):

        csv_args = {}
        csv_args['processes']=[]
        db = self.database['items']
        

        product_filter = lambda x:db[x]['type'] == 'product'
        process_filter = lambda x:db[x]['type'] == 'process'

        processes = list(filter(process_filter, db))
        products = list(filter(product_filter, db))


        created_exchanges = []

        for k in processes:
            item = db[k]

            current = {}
            current['name'] = item['name']
            current['id'] = (self.name.replace(" ", "") + "XXXXXXXX")[:8] + ('00000000000' + str(randint(1,99999999999)))[-11:]
            current['unit'] = item['unit']
            current['exchanges'] = []

            for e in item['exchanges']:

                if e['type'] == 'technosphere':
                    this_exchange = {}

                    this_code = e['input'][1]

                    formatted_name = self.get_name(this_code)
                    this_exchange['formatted_name'] = formatted_name

                    # TODO: Make the amount look for parameters
                    this_exchange['amount'] = e['amount']

                    this_exchange['unit'] = self.get_unit(this_code)

                    current['exchanges'].append(this_exchange)

                elif e['type'] == 'production':
                    this_code = e['input'][1]
                    name = self.get_name(this_code)
                    current['output_name']=name

                    created_exchanges.append(name)

            csv_args['processes'].append(current)
            
            
        for k in products:
            this_item = db[k]
            this_name = this_item['name']
            
            if this_item['name'] in created_exchanges:
                #print ('{} already created'.format(this_name))
                pass
            else:
                #print ('Need to create {}'.format(this_name))
                
                current = {}
                current['name'] = this_name
                current['output_name'] = this_name
                current['id'] = (self.name.replace(" ", "") + "XXXXXXXX")[:8] + ('00000000000' + str(randint(1,99999999999)))[-11:]
                current['unit'] = this_item['unit']
                #current['exchanges'] = []
                
                if 'ext_link' in this_item.keys():
                    
                    ext_link = this_item['ext_link']
                    db_filter = lambda x:x['name'] == ext_link[0]
                    extdb = list(filter(db_filter, self.external_databases))[0]['items']
                    ext_item = extdb[ext_link]
                    ref_prod = ext_item['reference product']
                    name = ext_item['name'].replace(" " + ref_prod, "")
                    location = ext_item['location']
                    system_model = "Alloc Def"
                    process_type = "U"
                    unit = unnormalise_unit(ext_item['unit'])

                    simaPro_name = "{} {{{}}}| {} | {}, {}".format(ref_prod.capitalize(), location, name, system_model, process_type)

                    print ('{} has an external link to {}'.format(this_name, simaPro_name))
                    
                    current['exchanges'] = [{'formatted_name':simaPro_name, 'unit':unit, 'amount':1}]
                    
                    
                else:
                    warnings.warn('{} has NO internal or external link - it is burden free'.format(this_name))
                    
                csv_args['processes'].append(current)
                created_exchanges.append(this_name)
            
            
        #print(csv_args)
        #print(created_exchanges)

        env = Environment(
            loader=PackageLoader('lcopt', 'templates'),
        )

        fname = "{}_database_export.csv".format(self.name)

        csv_template = env.get_template('export.csv')
        
        output = csv_template.render(**csv_args)

        with open(fname, "w") as f:
            f.write(output)
        
        return fname


### Flask ###

    def create_parameter_set_flask(self):
    
        app = Flask(__name__)
        print(__name__)

        @app.route('/')
        def parameter_setup():
            
            parameters = []
            p = self.params
            for k in p.keys():
                if p[k]['function'] == None:
                    parameters.append({'id':k, 'name': p[k]['description'], 'value': '', 'unit':p[k]['unit']})
                else:
                    print("{} is determined by a function".format(p[k]['description']))

            for e in self.ext_params:
                parameters.append({'id':'e_{}'.format(e[0]), 'type':'external', 'name': e[1], 'value': '', 'unit':'?'})
            
            return render_template('index.html', 
                                  title = 'Parameter set',
                                  items = parameters)
        
        
        @app.route('/', methods=['POST'])
        def parameter_parsing():
            
            p_set = OrderedDict()
            p_set_name = "ParameterSet_{}".format(len(self.parameter_sets)+1)

            myjson = request.json
            
            for i in myjson:
                try:
                    p_set[i['id']] = float(i['value'])
                except ValueError:
                    p_set[i['id']] = str(i['value'])
                
            self.parameter_sets[p_set_name] = p_set
            
            shutdown_server()
            return 'Server shutting down... Please close this tab'
            
        if __name__ == 'lcopt_geo.model':
            url = 'http://127.0.0.1:5000'
            webbrowser.open_new(url)
            app.run(debug=False)