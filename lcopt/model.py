"""
lcopt.model
-----------

Module containing the LcoptModel class.

"""

from lcopt.io import *
#from lcopt.ipython_interactive import IFS
from lcopt.interact import FlaskSandbox
from lcopt.bw2_export import Bw2Exporter
from lcopt.analysis import Bw2Analysis
from lcopt.data_store import storage
from .export_disclosure import export_disclosure

from .utils import check_for_config, lcopt_bw2_autosetup, bw2_project_exists, write_search_index, upgrade_old_default, lcopt_bw2_forwast_setup, forwast_autosetup, fix_mac_path_escapes
from .constants import DEFAULT_PROJECT_STEM, FORWAST_PROJECT_NAME, DEFAULT_ECOINVENT_VERSION, DEFAULT_ECOINVENT_SYSTEM_MODEL, LEGACY_SAVE_OPTION, DEFAULT_METHODS
# This is a copy straight from bw2data.query, extracted so as not to cause a dependency.
#from lcopt.bw2query import Query, Dictionaries, Filter
from bw2data.query import Query, Dictionaries, Filter

from functools import partial
from collections import OrderedDict
import numpy as np
import pickle
import random
import pandas as pd
import warnings
from random import randint

from jinja2 import Environment, PackageLoader

import os
import getpass

#From bw2 - edited to reinsert capitalisation of units

UNITS_NORMALIZATION = {
    "a": "year",  # Common in LCA circles; could be confused with acre
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
        
        un_units = list(filter(lambda x: UNITS_NORMALIZATION[x] == unit, UNITS_NORMALIZATION))
        #print (un_units)
        return un_units[0]


class LcoptModel(object):
    """
    This is the base model class.

    To create a new model, enter a name e.g. ``model = LcoptModel('My_Model')``

    To load an existing model use the ``load`` option e.g. ``model = LcoptModel(load = 'My_Model')``

    """

    def __init__(self, name=hex(random.getrandbits(128))[2:-1], load=None, useForwast=False, ecoinvent_version=None, ecoinvent_system_model=None, ei_username = None, ei_password = None, write_config=None, autosetup=True):
        super(LcoptModel, self).__init__()

        # name the instance
        self.name = name
        
        # set up the database, parameter dictionaries, the matrix and the names of the exchanges
        self.database = {'items': OrderedDict(), 'name': '{}_Database'.format(self.name)}
        self.external_databases = []
        self.params = OrderedDict()
        self.production_params = OrderedDict()
        self.allocation_params = OrderedDict()
        self.ext_params = []
        self.matrix = None
        self.names = None
        self.parameter_sets = OrderedDict()
        self.model_matrices = OrderedDict()
        self.technosphere_matrices = OrderedDict()
        self.leontif_matrices = OrderedDict()
        self.parameter_map = {}

        self.sandbox_positions = {}

        # If ecoinvent isn't specified in the setup, look for a default in the config and fall back on default set in constants
        if ecoinvent_version is None:
            self.ecoinvent_version = str(storage.ecoinvent_version)
        else:
            self.ecoinvent_version = ecoinvent_version

        if ecoinvent_system_model is None:
            self.ecoinvent_system_model = storage.ecoinvent_system_model
        else:
            self.ecoinvent_system_model = ecoinvent_system_model

        ei_name = "Ecoinvent{}_{}_{}".format(*self.ecoinvent_version.split("."), self.ecoinvent_system_model) #"Ecoinvent3_3_cutoff"

        self.ecoinventName = ei_name # "Ecoinvent3_3_cutoff"
        self.biosphereName = "biosphere3"
        self.ecoinventFilename = ei_name # "ecoinvent3_3"
        self.biosphereFilename = "biosphere3"
        self.forwastName = "forwast"
        self.forwastFilename = "forwast"
        self.useForwast = useForwast
        self.technosphere_databases = []
        #if self.useForwast:
        #    self.technosphere_databases = [self.forwastName]
        #else:
        #    self.technosphere_databases = [self.ecoinventName]

        #self.biosphere_databases = [self.biosphereName]
        self.biosphere_databases = []

        # default settings for bw2 analysis
        self.analysis_settings = {'amount': 1, 
                                  'methods': DEFAULT_METHODS,
                                  #'top_processes': 10, 
                                  #'gt_cutoff': 0.01, 
                                  'pie_cutoff': 0.05
                                  }

        self.allow_allocation = False

        # initialise with a blank result set
        self.result_set = None

        # set the save option, this defaults to the config value but should be overwritten on load for existing models
        self.save_option = storage.save_option
        
        if load is not None:
            self.load(load)

        # check if lcopt is set up, and if not, set it up
        is_setup = self.lcopt_setup(ei_username=ei_username, ei_password=ei_password, write_config=write_config,
                         ecoinvent_version=self.ecoinvent_version, ecoinvent_system_model = self.ecoinvent_system_model, autosetup=autosetup)

        if not is_setup:
            warnings.warn('lcopt autosetup did not run')

        asset_path = fix_mac_path_escapes(storage.search_index_dir) #os.path.join(os.path.dirname(os.path.realpath(__file__)), 'assets')
        ecoinventPath = os.path.join(asset_path, self.ecoinventFilename)
        biospherePath = os.path.join(asset_path, self.biosphereFilename)
        forwastPath = os.path.join(asset_path, self.forwastFilename)

        # Try and initialise the external databases if they're not there already
        if self.useForwast:
            if self.forwastName not in [x['name'] for x in self.external_databases]:
                self.import_external_db(forwastPath, 'technosphere')

        else:
            if self.ecoinventName not in [x['name'] for x in self.external_databases]:
                self.import_external_db(ecoinventPath, 'technosphere')

        if self.biosphereName not in [x['name'] for x in self.external_databases]:
            self.import_external_db(biospherePath, 'biosphere')

        # create partial version of io functions
        self.add_to_database = partial(add_to_specified_database, database=self.database)
        self.get_exchange = partial(get_exchange_from_database, database=self.database)
        self.exists_in_database = partial(exists_in_specific_database, database=self.database)
        self.get_name = partial(get_exchange_name_from_database, database=self.database)
        self.get_unit = partial(get_exchange_unit_from_database, database=self.database)

        self.parameter_scan()

    def lcopt_setup(self, ei_username, ei_password, write_config, ecoinvent_version, ecoinvent_system_model, autosetup):
        if not autosetup:
            return False

        if storage.project_type == 'single':

            if self.useForwast:

                forwast_autosetup()

            else:

                self.base_project_name = storage.single_project_name

                #if bw2_project_exists(self.base_project_name):
                lcopt_bw2_autosetup(ei_username = ei_username, ei_password = ei_password, write_config=write_config, ecoinvent_version=ecoinvent_version, ecoinvent_system_model = ecoinvent_system_model, overwrite=False)

        elif not self.useForwast:

            self.base_project_name = DEFAULT_PROJECT_STEM + self.ecoinventName
            old_default = DEFAULT_PROJECT_STEM[:-1]
            is_default = ecoinvent_version == "3.3" and ecoinvent_system_model == "cutoff"

            if bw2_project_exists(self.base_project_name):
                # make sure the search index file is there too
                write_search_index(self.base_project_name, self.ecoinventName)
            elif is_default and bw2_project_exists(old_default):
                upgrade_old_default()
            else:
                print("Lcopt needs to be set up to integrate with brightway2 - this only needs to be done once per version/system model combo")
                lcopt_bw2_autosetup(ei_username = ei_username, ei_password = ei_password, write_config=write_config, ecoinvent_version=ecoinvent_version, ecoinvent_system_model = ecoinvent_system_model, overwrite=True)

        else:
            forwast_autosetup()

        return True

    def rename(self, newname):
        """change the name of the model (i.e. what the .lcopt file will be saved as)"""
        self.name = newname
        
    #def saveAs(self, filename):
    #    """save the instance as a pickle"""
    #    pickle.dump(self, open("{}.pickle".format(filename), "wb"))
    
    def save(self):
        """save the instance as a .lcopt file"""
        if self.save_option == 'curdir':
            model_path = os.path.join(
                os.getcwd(),
                '{}.lcopt'.format(self.name)
            )
        else: # default to appdir
            model_path = os.path.join(
                storage.model_dir,
                '{}.lcopt'.format(self.name)
            )
        
        model_path = fix_mac_path_escapes(model_path)

        with open(model_path, 'wb') as model_file:
            pickle.dump(self, model_file)

    def load(self, filename):
        """load data from a saved .lcopt file"""
        if filename[-6:] != ".lcopt":
            filename += ".lcopt"
        try:
            savedInstance = pickle.load(open("{}".format(filename), "rb"))
        except FileNotFoundError:
            savedInstance = pickle.load(open(fix_mac_path_escapes(os.path.join(storage.model_dir, "{}".format(filename))), "rb"))
        
        attributes = ['name',
                      'database',
                      'params',
                      'production_params',
                      'allocation_params',
                      'ext_params',
                      'matrix',
                      'names',
                      'parameter_sets',
                      'model_matrices',
                      'technosphere_matrices',
                      'leontif_matrices',
                      'external_databases',
                      'parameter_map',
                      'sandbox_positions',
                      'ecoinventName',
                      'biosphereName',
                      'forwastName',
                      'analysis_settings',
                      'technosphere_databases',
                      'biosphere_databases',
                      'result_set',
                      'evaluated_parameter_sets',
                      'useForwast',
                      'base_project_name',
                      'save_option',
                      'allow_allocation',
                      'ecoinvent_version',
                      'ecoinvent_system_model',
                      ]

        for attr in attributes:

            if hasattr(savedInstance, attr):
                setattr(self, attr, getattr(savedInstance, attr))
            else:
                pass
                #print ("can't set {}".format(attr))

        # use legacy save option if this is missing from the model
        if not hasattr(savedInstance, 'save_option'):
            setattr(self, 'save_option', LEGACY_SAVE_OPTION)

        # figure out ecoinvent version and system model if these are missing from the model
        if not hasattr(savedInstance, 'ecoinvent_version') or not hasattr(savedInstance, 'ecoinvent_system_model'):
            
            parts = savedInstance.ecoinventName.split("_")
            main_version = parts[0][-1]
            sub_version = parts[1]
            system_model = parts[2]

            #print(parts)

            setattr(self, 'ecoinvent_version', '{}.{}'.format(main_version, sub_version))
            setattr(self, 'ecoinvent_system_model', system_model)



    def create_product (self, name, location='GLO', unit='kg', **kwargs):

        """
        Create a new product in the model database
        """

        new_product = item_factory(name=name, location=location, unit=unit, type='product', **kwargs)

        if not self.exists_in_database(new_product['code']):
            self.add_to_database(new_product)
            #print ('{} added to database'.format(name))
            return self.get_exchange(name)
        else:
            #print('{} already exists in this database'.format(name))
            return False

    def create_process(self, name, exchanges, location='GLO', unit='kg'):
        """
        Create a new process, including all new exchanges (in brightway2's exchange format) in the model database.

        Exchanges must have at least a name, type and unit field
        """

        found_exchanges = []
        for e in exchanges:

            exc_name = e.pop('name', None)
            exc_type = e.pop('type', None)

            this_exchange = self.get_exchange(exc_name)
            
            if this_exchange is False:
                my_unit = e.pop('unit', unit)
                    
                this_exchange = self.create_product(exc_name, location=location, unit=my_unit, **e)
            
            found_exchanges.append(exchange_factory(this_exchange, exc_type, 1, 1, '{} exchange of {}'.format(exc_type, exc_name)))
            
        new_process = item_factory(name=name, location=location, unit=unit, type='process', exchanges=found_exchanges)
        
        self.add_to_database(new_process)

        self.parameter_scan()

        return True

    def check_param_function_use(self, param_id):
    
        current_functions = {k: x['function'] for k, x in self.params.items() if x['function'] is not None}
        
        problem_list = []
        
        for k, f in current_functions.items():
            if param_id in f:
                problem_list.append((k, f))
                
        return problem_list

    def remove_input_link(self, process_code, input_code):

        """
        Remove an input (technosphere or biosphere exchange) from a process, resolving all parameter issues
        """
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
            #print('the following functions have been removed:')
            for p in problem_functions:
                self.params[p[0]]['function'] = None
                #print(p)

        process['exchanges'] = new_exchanges

        del self.params[param_id]

        self.parameter_scan()

        return initial_count - len(new_exchanges)

    def unlink_intermediate(self, sourceId, targetId):
        """
        Remove a link between two processes
        """
        
        source = self.database['items'][(self.database.get('name'), sourceId)]
        target = self.database['items'][(self.database.get('name'), targetId)]

        production_exchange = [x['input'] for x in source['exchanges'] if x['type'] == 'production'][0]

        new_exchanges = [x for x in target['exchanges'] if x['input'] != production_exchange]

        target['exchanges'] = new_exchanges

        self.parameter_scan()

        return True

    def parameter_scan(self):
        """
        Scan the database of the model instance to generate and expose parameters.
        
        This is called by other functions when items are added/removed from the model, but can be run by itself if you like
        """
        
        #self.parameter_map = {}
        #self.params = OrderedDict()

        cr_list = []
        items = self.database['items']
        #print(items)

        for key in items.keys():
            i = items[key]
            #print(i['name'], i['type'])
            if i['type'] == 'product':
                cr_list.append(i['code'])

        no_products = len(cr_list)

        self.names = [self.get_name(x) for x in cr_list]

        self.matrix = np.zeros((no_products, no_products))
        
        for key in items.keys():
            i = items[key]
            if i['type'] == 'process':
                inputs = []
                #print(i['name'])
                #print([(e['comment'], e['type']) for e in i['exchanges']])
                for e in i['exchanges']:
                    if e['type'] == 'production':
                        col_code = cr_list.index(e['input'][1])
                        if not 'p_{}_production'.format(col_code) in self.production_params:
                            self.production_params['p_{}_production'.format(col_code)] = {
                                'function': None,
                                'description': 'Production parameter for {}'.format(self.get_name(e['input'][1])),
                                'unit': self.get_unit(e['input'][1]),
                                'from': e['input'],
                                'from_name': self.get_name(e['input'][1]),
                                'type': 'production',
                            }
                        if not 'p_{}_allocation'.format(col_code) in self.allocation_params:
                            self.allocation_params['p_{}_allocation'.format(col_code)] = {
                                'function': None,
                                'description': 'Allocation parameter for {}'.format(self.get_name(e['input'][1])),
                                'unit': "% (as decimal)", 
                                'from': e['input'],
                                'from_name': self.get_name(e['input'][1]),
                                'type': 'allocation',
                            }

                    elif e['type'] == 'technosphere':
                        #print(cr_list)
                        row_code = cr_list.index(e['input'][1])
                        inputs.append((row_code, e['amount']))

                for ip in inputs:
                    self.matrix[(ip[0], col_code)] = ip[1]

        param_check_list = []

        for c, column in enumerate(self.matrix.T):
            for r, i in enumerate(column):
                if i > 0:
                    p_from = cr_list[r]
                    p_to = cr_list[c]
                    coords = (r, c)

                    from_item_type = self.database['items'][(self.database['name'], p_from)]['lcopt_type']
                    #print('{}\t| {} --> {}'.format(coords, self.get_name(p_from), self.get_name(p_to)))

                    param_check_list.append('p_{}_{}'.format(coords[0], coords[1]))

                    if not 'p_{}_{}'.format(coords[0], coords[1]) in self.params:
                        self.params['p_{}_{}'.format(coords[0], coords[1])] = {
                            'function': None,
                            'normalisation_parameter': '(p_{}_production / p_{}_allocation)'.format(coords[1], coords[1]),
                            'description': 'Input of {} to create {}'.format(self.get_name(p_from), self.get_name(p_to)),
                            'coords': coords,
                            'unit': self.get_unit(p_from),
                            'from': p_from,
                            'from_name': self.get_name(p_from),
                            'to': p_to,
                            'to_name': self.get_name(p_to),
                            'type': from_item_type,
                        }

                    #elif 'normalisation_parameter' not in self.params['p_{}_{}'.format(coords[0], coords[1])].keys():
                        #print("Adding normalisation_parameter to {}".format('p_{}_{}'.format(coords[0], coords[1])))
                        #self.params['p_{}_{}'.format(coords[0], coords[1])]['normalisation_parameter'] = '(p_{}_production / p_{}_allocation)'.format(coords[1], coords[1])
                        
                        #print('p_{}_{} already exists'.format(coords[0],coords[1]))

                    else:
                        pass  # print("SOMETHING WRONG HERE\n{}\n".format(self.params['p_{}_{}'.format(coords[0], coords[1])]))

                    # make sure the parameter is being normalised and allocated properly
                    self.params['p_{}_{}'.format(coords[0], coords[1])]['normalisation_parameter'] = '(p_{}_production / p_{}_allocation)'.format(coords[1], coords[1])

                    if not 'p_{}_{}'.format(coords[0], coords[1]) in self.parameter_map:
                        self.parameter_map[(p_from, p_to)] = 'p_{}_{}'.format(coords[0], coords[1])

        kill_list = []
        for k in self.params.keys():
            if k not in param_check_list:
                #print("{} may be obsolete".format(k))
                kill_list.append(k)

        for p in kill_list:
            #print("deleting parameter {}".format(p))
            del self.params[p]

        return True

    def generate_parameter_set_excel_file(self):
        """
        Generate an excel file containing the parameter sets in a format you can import into SimaPro Developer.

        The file will be called "ParameterSet_<ModelName>_input_file.xlsx"
        """
        
        parameter_sets = self.parameter_sets

        p_set = []
        filename = "ParameterSet_{}_input_file.xlsx".format(self.name)

        if self.save_option == 'curdir':
            base_dir = os.getcwd()
        else:
            base_dir = os.path.join(storage.simapro_dir, self.name.replace(" ", "_"))

        if not os.path.isdir(base_dir):
            os.mkdir(base_dir)

        p_set_name = os.path.join(base_dir, filename)

        p = self.params
        for k in p.keys():
            if p[k]['function'] is None:
                base_dict = {'id': k, 'name': p[k]['description'], 'unit': p[k]['unit']}

                for s in parameter_sets.keys():
                    base_dict[s] = parameter_sets[s][k]

                p_set.append(base_dict)
            else:
                pass
                #print("{} is determined by a function".format(p[k]['description']))

        for e in self.ext_params:
            base_dict = {'id': '{}'.format(e['name']), 'type': 'external', 'name': e['description'], 'unit': ''}

            for s in parameter_sets.keys():
                    base_dict[s] = parameter_sets[s][e['name']]

            p_set.append(base_dict)

        df = pd.DataFrame(p_set)

        with pd.ExcelWriter(p_set_name, engine='xlsxwriter') as writer:

            ps_columns = [k for k in parameter_sets.keys()]
            #print (ps_columns)
            my_columns = ['name', 'unit', 'id']
            
            my_columns.extend(ps_columns)
            #print (my_columns)

            #print(df)

            df.to_excel(writer, sheet_name=self.name, columns=my_columns, index=False, merge_cells=False)
       
        return p_set_name
        
    def add_parameter(self, param_name, description=None, default=0, unit=None):
        """
        Add a global parameter to the database that can be accessed by functions
        """

        if description is None:
            description = "Parameter called {}".format(param_name)

        if unit is None:
            unit = "-"
        
        name_check = lambda x: x['name'] == param_name
        name_check_list = list(filter(name_check, self.ext_params))
        if len(name_check_list) == 0:
            self.ext_params.append({'name': param_name, 'description': description, 'default': default, 'unit': unit})
        else:
            print('{} already exists - choose a different name'.format(param_name))

    def list_parameters_as_df(self):
        """
        Only really useful when running from a jupyter notebook.

        Lists the parameters in the model in a pandas dataframe

        Columns: id, matrix coordinates, description, function
        """
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

    def import_external_db(self, db_file, db_type=None):
        """
        Import an external database for use in lcopt

        db_type must be one of ``technosphere`` or ``biosphere``

        The best way to 'obtain' an external database is to 'export' it from brightway as a pickle file

        e.g.::

            import brightway2 as bw
            bw.projects.set_current('MyModel')
            db = bw.Database('MyDatabase')
            db_as_dict = db.load()
            import pickle
            with open('MyExport.pickle', 'wb') as f:
                pickle.dump(db_as_dict, f)

        NOTE: The Ecoinvent cutoff 3.3 database and the full biosphere database are included in the lcopt model as standard - no need to import those

        This can be useful if you have your own methods which require new biosphere flows that you want to analyse using lcopt

        """
        
        db = pickle.load(open("{}.pickle".format(db_file), "rb"))
        name = list(db.keys())[0][0]
        new_db = {'items': db, 'name': name}
        self.external_databases.append(new_db)

        if db_type is None:             # Assume its a technosphere database
            db_type = 'technosphere'

        if db_type == 'technosphere':
            self.technosphere_databases.append(name)
        elif db_type == 'biosphere':
            self.biosphere_databases.append(name)

        else:
            raise Exception
            print ("Database type must be 'technosphere' or 'biosphere'")

    def search_databases(self, search_term, location=None, markets_only=False, databases_to_search=None, allow_internal=False):

        """
        Search external databases linked to your lcopt model.

        To restrict the search to particular databases (e.g. technosphere or biosphere only) use a list of database names in the ``database_to_search`` variable
        """

        dict_list = []

        if allow_internal:
            internal_dict = {}
            for k, v in self.database['items'].items():
                if v.get('lcopt_type') == 'intermediate':
                    internal_dict[k] = v
            
            dict_list.append(internal_dict)

        if databases_to_search is None:
            #Search all of the databases available
            #data = Dictionaries(self.database['items'], *[x['items'] for x in self.external_databases])
            dict_list += [x['items'] for x in self.external_databases]
        else:
            #data = Dictionaries(self.database['items'], *[x['items'] for x in self.external_databases if x['name'] in databases_to_search])
            dict_list += [x['items'] for x in self.external_databases if x['name'] in databases_to_search]

        data = Dictionaries(*dict_list)
        #data = Dictionaries(self.database['items'], *[x['items'] for x in self.external_databases if x['name'] in databases_to_search])

        query = Query()

        if markets_only:
            market_filter = Filter("name", "has", "market for")
            query.add(market_filter)
        
        if location is not None:
            location_filter = Filter("location", "is", location)
            query.add(location_filter)
        
        query.add(Filter("name", "ihas", search_term))
        
        result = query(data)
        
        return result

    def database_to_SimaPro_csv(self):

        """
        Export the lcopt model as a SimaPro csv file.

        The file will be called "<ModelName>_database_export.csv"
        """
        self.parameter_scan()

        csv_args = {}
        csv_args['processes'] = []
        db = self.database['items']
        
        product_filter = lambda x: db[x]['type'] == 'product'
        process_filter = lambda x: db[x]['type'] == 'process'

        processes = list(filter(process_filter, db))
        products = list(filter(product_filter, db))

        created_exchanges = []

        project_input_params = []
        project_calc_params = []

        for k in processes:
            item = db[k]

            current = {}
            current['name'] = item['name']
            current['id'] = (self.name.replace(" ", "") + "XXXXXXXX")[:8] + ('00000000000' + str(randint(1, 99999999999)))[-11:]
            current['unit'] = item['unit']
            current['exchanges'] = []
            
            process_params = []
            
            production_filter = lambda x: x['type'] == 'production'
            
            output_code = list(filter(production_filter, item['exchanges']))[0]['input'][1]
            
            for e in item['exchanges']:

                if e['type'] == 'technosphere':
                    this_exchange = {}

                    this_code = e['input'][1]

                    formatted_name = self.get_name(this_code)
                    this_exchange['formatted_name'] = formatted_name
                    
                    param_key = (this_code,  output_code)
                    #print(param_key)
                    #param_check = (formatted_name, item['name'])
                    this_param = self.parameter_map[param_key]
                    
                    process_params.append(this_param)
                   
                    this_exchange['amount'] = this_param 

                    this_exchange['unit'] = self.get_unit(this_code)

                    current['exchanges'].append(this_exchange)

                elif e['type'] == 'production':
                    this_code = e['input'][1]
                    name = self.get_name(this_code)
                    current['output_name'] = name

                    created_exchanges.append(name)
                    
                # process parameters
                
            for p in process_params:
                if self.params[p]['function'] is None:
                    project_input_params.append({'name': p, 'comment': self.params[p]['description']})
                else:
                    project_calc_params.append({'name': p, 'comment': self.params[p]['description'], 'formula': self.params[p]['function']})

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
                current['id'] = (self.name.replace(" ", "") + "XXXXXXXX")[:8] + ('00000000000' + str(randint(1, 99999999999)))[-11:]
                current['unit'] = this_item['unit']
                #current['exchanges'] = []
                
                if 'ext_link' in this_item.keys():
                    
                    ext_link = this_item['ext_link']
                    if ext_link[0] != self.database['name']:
                        db_filter = lambda x: x['name'] == ext_link[0]
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
                            
                            current['exchanges'] = [{'formatted_name': simaPro_name, 'unit': unit, 'amount': 1}]
                        else:
                            #print('{} has a biosphere exchange - need to sort this out'.format(this_name))
                            #print(ext_item)
                            unit = unnormalise_unit(ext_item['unit'])
                            formatted_name = ext_item['name']

                            if 'air' in ext_item['categories']:
                                current['air_emissions'] = [{'formatted_name': formatted_name, 'subcompartment': '', 'unit': unit, 'amount': 1, 'comment': 'emission of {} to air'.format(formatted_name)}]

                            elif 'water' in ext_item['categories']:
                                current['water_emissions'] = [{'formatted_name': formatted_name, 'subcompartment': '', 'unit': unit, 'amount': 1, 'comment': 'emission of {} to water'.format(formatted_name)}]

                            elif 'soil' in ext_item['categories']:
                                current['soil_emissions'] = [{'formatted_name': formatted_name, 'subcompartment': '', 'unit': unit, 'amount': 1, 'comment': 'emission of {} to soil'.format(formatted_name)}]

                            else:
                                print('{} has a biosphere exchange that isnt to air water or soil')
                                print(ext_item)
                        
                    else:
                        warnings.warn('{} has NO internal or external link - it is burden free'.format(this_name))
                    
                csv_args['processes'].append(current)
                created_exchanges.append(this_name)
            
        #print(csv_args)
        #print(created_exchanges)
        
        csv_args['project'] = {}
        
        #NOTE - currently external parameters can only be constants

        csv_args['project']['calculated_parameters'] = project_calc_params
        
        #add the external parameters to the input parameter list        
        for p in self.ext_params:
            project_input_params.append({'name': p['name'], 'comment': p['description'], 'default': p['default']})
        
        csv_args['project']['input_parameters'] = project_input_params

        #print (csv_args)

        env = Environment(
            loader=PackageLoader('lcopt', 'templates'),
        )

        filename = "{}_database_export.csv".format(self.name.replace(" ", "_"))

        csv_template = env.get_template('export.csv')
        
        output = csv_template.render(**csv_args)

        if self.save_option == 'curdir':
            base_dir = os.getcwd()
        else:
            base_dir = os.path.join(storage.simapro_dir, self.name.replace(" ", "_"))

        if not os.path.isdir(base_dir):
            os.mkdir(base_dir)

        efn = os.path.join(base_dir, filename)

        with open(efn, "w") as f:
            f.write(output)
        
        return efn


# << Flask >> #

    def launch_interact(self):              # pragma: no cover
        """
        This is probably the most important method in the model - you use it to launch the GUI
        """
        my_flask = FlaskSandbox(self)
        my_flask.run()


# << Brightway2 >> #

    def export_to_bw2(self):
        """
        Export the lcopt model in the native brightway 2 format

        returns name, database

        to use it to export, then import to brightway::

            name, db = model.export_to_bw2()
            import brightway2 as bw
            bw.projects.set_current('MyProject')
            new_db = bw.Database(name)
            new_db.write(db)
            new_db.process()

        """
        my_exporter = Bw2Exporter(self)
        name, bw2db = my_exporter.export_to_bw2()
        return name, bw2db

    def analyse(self, demand_item, demand_item_code):
        """ Run the analyis of the model
            Doesn't return anything, but creates a new item ``LcoptModel.result_set`` containing the results
        """
        my_analysis = Bw2Analysis(self)
        self.result_set = my_analysis.run_analyses(demand_item, demand_item_code, **self.analysis_settings)

        return True

# << Disclosures >> #
    def export_disclosure(self, parameter_set=None, folder_path=None):
        return export_disclosure(self, parameter_set, folder_path)
