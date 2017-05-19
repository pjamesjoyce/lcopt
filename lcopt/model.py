from lcopt.io import *
#from lcopt.ipython_interactive import IFS
from lcopt.interact import FlaskSandbox
from lcopt.bw2_export import Bw2Exporter
from lcopt.analysis import Bw2Analysis

from functools import partial
from collections import OrderedDict
import numpy as np
import re
import pickle
import random
from copy import deepcopy
import pandas as pd
import xlsxwriter
from flask import Flask, request, render_template
import webbrowser
import warnings
from random import randint

from jinja2 import Environment, PackageLoader

import os

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

# This is a copy straight from bw2data.query, extracted so as not to cause a dependency.
from lcopt.bw2query import Query, Dictionaries, Filter


class LcoptModel(object):
    """docstring for LcoptModel"""
    def __init__(self, name = hex(random.getrandbits(128))[2:-1], load = None):
        super(LcoptModel, self).__init__()
        
        # name the instance
        self.name = name
        
        # set up the database, parameter dictionaries, the matrix and the names of the exchanges
        self.database = {'items': OrderedDict(), 'name': '{}_Database'.format(self.name)}
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

        self.sandbox_positions = {}

        # set the default names of the external databases - these can be changed if needs be
        self.ecoinventName = "Ecoinvent3_3_cutoff"
        self.biosphereName = "biosphere3"
        self.ecoinventFilename = "ecoinvent3_3"
        self.biosphereFilename = "biosphere3"

        # default settings for bw2 analysis
        self.analysis_settings = {
                                'amount' : 1,
                                'methods' : [('IPCC 2013', 'climate change', 'GWP 100a'), ('USEtox', 'human toxicity', 'total')],
                                'top_processes': 10,
                                'gt_cutoff' : 0.01,
                                'pie_cutoff' : 0.05,
                            }
         
        if load != None:
            self.load(load)
                    
        asset_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'assets')
        ecoinventPath = os.path.join(asset_path, self.ecoinventFilename)
        biospherePath = os.path.join(asset_path, self.biosphereFilename)

        # Try and initialise the external databases if they're not there already
        if self.ecoinventName not in [x['name'] for x in self.external_databases]:
            self.import_external_db(ecoinventPath)
        if self.biosphereName not in [x['name'] for x in self.external_databases]:
            self.import_external_db(biospherePath)

        # create partial version of io functions
        self.add_to_database = partial(add_to_specified_database, database = self.database)
        self.get_exchange = partial(get_exchange_from_database, database=self.database)
        self.exists_in_database = partial(exists_in_specific_database, database = self.database)
        self.get_name = partial(get_exchange_name_from_database, database=self.database)
        self.get_unit = partial(get_exchange_unit_from_database, database=self.database)

       
        
        
    def rename(self,newname):
        """change the name of the class"""
        self.name = newname
        
    #def saveAs(self, filename):
    #    """save the instance as a pickle"""
    #    pickle.dump(self, open("{}.pickle".format(filename), "wb"))
    
    def save(self):
        """save the instance as a pickle"""
        pickle.dump(self, open("{}.lcopt".format(self.name), "wb"))
        
    def load(self, filename):
        """load data from another instance - allows older versions to be loaded into the newer version of the class"""
        if filename[-6:] != ".lcopt":
            filename += ".lcopt"
        savedInstance = pickle.load(open("{}".format(filename), "rb"))
        
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

            self.sandbox_positions = savedInstance.sandbox_positions


            self.ecoinventName = savedInstance.ecoinventName
            self.biosphereName = savedInstance.biosphereName

            self.analysis_settings =savedInstance.analysis_settings

        except Exception:
            pass

    
        
    def create_product (self, name, location ='GLO', unit='kg', **kwargs):
        """create a new product with md5 hash id in the model instances database"""
        new_product = item_factory(name=name, location=location, unit=unit, type='product', **kwargs)

        if not self.exists_in_database(new_product['code']):
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

            this_exchange = self.get_exchange(exc_name)
            
            if this_exchange == False:
                my_unit = e.pop('unit', unit)
                    
                this_exchange = self.create_product(exc_name, location=location, unit=my_unit, **e)
            
            found_exchanges.append(exchange_factory(this_exchange, exc_type, 1, 1, '{} exchange of {}'.format(exc_type, exc_name)))
            
        new_process = item_factory(name=name, location=location, unit=unit, type='process', exchanges=found_exchanges)
        
        self.add_to_database(new_process)

        self.parameter_scan()

        return True

    def check_param_function_use(self, param_id):
    
        current_functions = {k:x['function'] for k, x in self.params.items() if x['function'] is not None}
        
        problem_list = []
        
        for k, f in current_functions.items():
            if param_id in f:
                problem_list.append((k, f))
                
        return problem_list

    def remove_input_link(self, process_code, input_code):
        # 1. find correct process
        # 2. find correct exchange
        # 3. remove that exchange
        # 4. check for parameter conflicts?
        # 4. run parameter scan to rebuild matrices?
        
        #print(process_code, input_code)
        
        process = self.database['items'][process_code]
        exchanges = process['exchanges']
        
        initial_count = len(exchanges)
        
        new_exchanges = [e for e in exchanges if e['input'] != input_code]
        
        product_code = [e['input'] for e in exchanges if e['type'] == 'production'][0]
        
        #print(product_code)
        
        param_id = [k for k, v in self.params.items() if (v['from'] == input_code[1] and v['to'] == product_code[1])][0]
        
        #print (param_id)
        
        problem_functions = self.check_param_function_use(param_id)
        
        
        if len(problem_functions) != 0:
            print('the following functions have been removed:')
            for p in problem_functions:
                self.params[p[0]]['function'] = None
                print(p)

        process['exchanges'] = new_exchanges

        del self.params[param_id]

        self.parameter_scan()

        return initial_count - len(new_exchanges)

    def unlink_intermediate(self, sourceId, targetId):
        
        source = self.database['items'][(self.database.get('name'), sourceId)]
        target = self.database['items'][(self.database.get('name'), targetId)]

        production_exchange = [x['input'] for x in source['exchanges'] if x['type'] == 'production'][0]

        new_exchanges = [x for x in target['exchanges'] if x['input'] != production_exchange]

        target['exchanges'] = new_exchanges

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
                        #print(e)
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

                    from_item_type = self.database['items'][(self.database['name'], p_from)]['lcopt_type']
                    #print('{}\t| {} --> {}'.format(coords, self.get_name(p_from), self.get_name(p_to)))

                    if not 'p_{}_{}'.format(coords[0],coords[1]) in self.params:
                        self.params['p_{}_{}'.format(coords[0],coords[1])] = {
                            'function' : None,
                            'description' : 'Input of {} to create {}'.format(self.get_name(p_from), self.get_name(p_to)),
                            'coords':coords,
                            'unit' : self.get_unit(p_from),
                            'from': p_from,
                            'from_name': self.get_name(p_from),
                            'to': p_to,
                            'to_name': self.get_name(p_to),
                            'type' : from_item_type,
                        }

                    else:
                        pass
                        #print('p_{}_{} already exists'.format(coords[0],coords[1]))

                    if not 'p_{}_{}'.format(coords[0],coords[1]) in self.parameter_map:
                        self.parameter_map[(p_from,p_to)] = 'p_{}_{}'.format(coords[0],coords[1])

        return True
        

    def generate_parameter_set_excel_file(self):
        
        parameter_sets = self.parameter_sets

        p_set = []
        p_set_name = "ParameterSet_{}_input_file.xlsx".format(self.name)
        p = self.params
        for k in p.keys():
            if p[k]['function'] == None:
                base_dict = {'id':k, 'name': p[k]['description'], 'unit':p[k]['unit']}

                for s in parameter_sets.keys():
                    base_dict[s] = parameter_sets[s][k]

                p_set.append(base_dict)
            else:
                print("{} is determined by a function".format(p[k]['description']))

        for e in self.ext_params:
            base_dict = {'id':'{}'.format(e['name']), 'type':'external', 'name': e['description'], 'unit':''}

            for s in parameter_sets.keys():
                    base_dict[s] = parameter_sets[s][e['name']]

            p_set.append(base_dict)

        df = pd.DataFrame(p_set)

        writer = pd.ExcelWriter(p_set_name, engine='xlsxwriter')

        ps_columns = [k for k in parameter_sets.keys()]
        print (ps_columns)
        my_columns = ['name', 'unit', 'id']
        
        my_columns.extend(ps_columns)
        print (my_columns)

        df.to_excel(writer, sheet_name=self.name, columns =  my_columns, index= False, merge_cells = False)
       
        return p_set_name

        
    def add_parameter(self, param_name, description = None, default = 0):
        if description == None:
            description = "Parameter called {}".format(param_name)
        
        name_check = lambda x:x['name'] == param_name
        name_check_list = list(filter(name_check, self.ext_params))
        if len(name_check_list) == 0:
            self.ext_params.append({'name':param_name, 'description': description, 'default': default})
        else:
            print('{} already exists - choose a different name'.format(param_name))

    def list_parameters_as_df(self):
        to_df = []

        for i, e in enumerate(self.ext_params):
            row = {}
            row['id'] = e['name']
            row['coords'] = "n/a"
            row['description'] = e['description']
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


    def import_external_db(self, db_file):
        db = pickle.load(open("{}.pickle".format(db_file), "rb"))
        name = list(db.keys())[0][0]
        new_db = {'items': db, 'name': name}
        self.external_databases.append(new_db)

    def search_databases(self, search_term, location = None, markets_only=False, databases_to_search = None):

        if databases_to_search is None:
            #Search all of the databases available
            data = Dictionaries(self.database['items'], *[x['items'] for x in self.external_databases])
        else:
            data = Dictionaries(*[x['items'] for x in self.external_databases if x['name'] in databases_to_search ])

        query = Query()

        if markets_only:
            market_filter = Filter("name", "has", "market for")
            query.add(market_filter)
        
        if location is not None:
            location_filter = Filter("location", "has", location)
            query.add(location_filter)
        
        query.add(Filter("name", "ihas", search_term))
        
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

        project_input_params = []
        project_calc_params = []

        for k in processes:
            item = db[k]

            current = {}
            current['name'] = item['name']
            current['id'] = (self.name.replace(" ", "") + "XXXXXXXX")[:8] + ('00000000000' + str(randint(1,99999999999)))[-11:]
            current['unit'] = item['unit']
            current['exchanges'] = []
            
            process_params = []
            
            production_filter = lambda x:x['type'] == 'production'
            
            output_code = list(filter(production_filter, item['exchanges']))[0]['input'][1]
            

            for e in item['exchanges']:

                if e['type'] == 'technosphere':
                    this_exchange = {}

                    this_code = e['input'][1]

                    formatted_name = self.get_name(this_code)
                    this_exchange['formatted_name'] = formatted_name
                    
                    param_key = (this_code, output_code)
                    #param_check = (formatted_name, item['name'])
                    this_param = self.parameter_map[param_key]
                    
                    process_params.append(this_param)
                   
                    this_exchange['amount'] = this_param #e['amount']

                    this_exchange['unit'] = self.get_unit(this_code)

                    current['exchanges'].append(this_exchange)

                elif e['type'] == 'production':
                    this_code = e['input'][1]
                    name = self.get_name(this_code)
                    current['output_name']=name

                    created_exchanges.append(name)
                    
                    
                #process parameters
                
            for p in process_params:
                if self.params[p]['function'] == None:
                    project_input_params.append({'name':p, 'comment':self.params[p]['description']})
                else:
                    project_calc_params.append({'name':p, 'comment':self.params[p]['description'], 'formula':self.params[p]['function']})
                
                
                        

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
                    if ext_link[0] != self.biosphereName:
                        ref_prod = ext_item['reference product']
                        name = ext_item['name'].replace(" " + ref_prod, "")
                        location = ext_item['location']
                        system_model = "Alloc Def"
                        process_type = "U"
                        unit = unnormalise_unit(ext_item['unit'])

                        simaPro_name = "{} {{{}}}| {} | {}, {}".format(ref_prod.capitalize(), location, name, system_model, process_type)

                        #print ('{} has an external link to {}'.format(this_name, simaPro_name))
                        
                        current['exchanges'] = [{'formatted_name':simaPro_name, 'unit':unit, 'amount':1}]
                    else:
                        #print('{} has a biosphere exchange - need to sort this out'.format(this_name))
                        #print(ext_item)
                        unit = unnormalise_unit(ext_item['unit'])
                        formatted_name = ext_item['name']

                        if 'air' in ext_item['categories']:
                            current['air_emissions'] = [{'formatted_name':formatted_name, 'subcompartment':'', 'unit':unit, 'amount':1, 'comment': 'emission of {} to air'.format(formatted_name)}]

                        elif 'water' in ext_item['categories']:
                            current['water_emissions'] = [{'formatted_name':formatted_name, 'subcompartment':'', 'unit':unit, 'amount':1, 'comment': 'emission of {} to water'.format(formatted_name)}]

                        elif 'soil' in ext_item['categories']:
                            current['soil_emissions'] = [{'formatted_name':formatted_name, 'subcompartment':'', 'unit':unit, 'amount':1, 'comment': 'emission of {} to soil'.format(formatted_name)}]

                        else:
                            print('{} has a biosphere exchange that isnt to air water or soil')
                            print(ext_item)
                    
                    
                else:
                    warnings.warn('{} has NO internal or external link - it is burden free'.format(this_name))
                    
                csv_args['processes'].append(current)
                created_exchanges.append(this_name)
            
            
        #print(csv_args)
        #print(created_exchanges)
        
        csv_args['project']={}
        
        #NOTE - currently external parameters can only be constants

        csv_args['project']['calculated_parameters']=project_calc_params
        
        #add the external parameters to the input parameter list        
        for p in self.ext_params:
            project_input_params.append({'name':p['name'], 'comment':p['description'], 'default':p['default']})
        
        csv_args['project']['input_parameters']=project_input_params

        #print (csv_args)

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


    def launch_interact(self):
        my_flask = FlaskSandbox(self)
        my_flask.run()


### Brightway2 ###

    def export_to_bw2(self):
        my_exporter = Bw2Exporter(self)
        name, bw2db = my_exporter.export_to_bw2()
        return name, bw2db

    def analyse(self, demand_item, demand_item_code):
        my_analysis = Bw2Analysis(self)
        self.result_set = my_analysis.run_analyses(demand_item, demand_item_code,  **self.analysis_settings)

        return True

