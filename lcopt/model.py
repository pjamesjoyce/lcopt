from lcopt_geo.io import *
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
        self.params = OrderedDict()
        self.ext_params = []
        self.matrix = None
        self.names = None
        self.parameter_sets = OrderedDict()
        self.model_matrices = OrderedDict()
        self.technosphere_matrices = OrderedDict()
        self.leontif_matrices = OrderedDict()
                
        # create partial version of io functions
        self.add_to_database = partial(add_to_specified_database, database = self.database)
        self.get_exchange = partial(get_exchange_from_database, database=self.database)
        self.exists_in_database = partial(exists_in_specific_database, database = self.database)
        self.get_name = partial(get_exchange_name_from_database, database=self.database)
        self.get_unit = partial(get_exchange_unit_from_database, database=self.database)
        
        # create a partial for saving that defaults to the name of the instance
        #self.save = partial(self.saveAs, filename = self.name)
        
        if load != None:
            self.load(load)
        
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
        except Exception:
            pass

    
        
    def create_product (self, name, location ='GLO', unit='kg'):
        """create a new product with md5 hash id in the model instances database"""
        new_product = item_factory(name=name, location=location, unit=unit, type='product')

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
            
            this_exchange = self.get_exchange(e[0])

            if this_exchange == None:
                if len(e)== 3:
                    my_unit = e[2]
                else:
                    my_unit = unit

                this_exchange = self.create_product(e[0], location, my_unit)

            found_exchanges.append(exchange_factory(this_exchange, e[1], 1, 1, '{} exchange of {}'.format(e[1], e[0])))

        new_process = item_factory(name=name, location=location, unit=unit, type='process', exchanges=found_exchanges)

        self.add_to_database(new_process)
        
        self.parameter_scan()

        return True
        
    def parameter_scan(self):
        """scan the database of the model instance to generate and expose parameters"""
    
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

        return True
        
        
    def add_parameter(self, param_name, description = None):
        if description == None:
            description = "Parameter called {}".format(param_name)
        self.ext_params.append((param_name, description))
        
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