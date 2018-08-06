import json
import os

from bw2io.importers.base_lci import LCIImporter
from time import time
from bw2data import Database, config, databases
import functools
import warnings

from bw2io.strategies import (
    set_code_by_activity_hash,
    normalize_units,
    normalize_biosphere_categories,
    normalize_biosphere_names,
    link_iterable_by_fields,
    assign_only_product_as_production,
    link_technosphere_by_activity_hash,
)

class DisclosureExtractor(object):
    """Extractor used by the DisclosureImporter
    """
    @classmethod
    def extract(cls, filepath):
        assert os.path.exists(filepath), "Can't file file at path {}".format(filepath)
        with open(filepath, 'r') as j:
            data = json.load(j)
        return data

class DisclosureImporter(LCIImporter):
    """Generic Disclosure importer.

    A disclosure is a json document minimally describing an LCA foreground model.

    Parameters are not supported in disclosure files.

    The disclosure file should follow the following format:

    ::
        json dictionary with the following keys:
            'Af':{
                'data': [list of lists containing COO data describing foreground (Af) matrix in the format [[row, column], value]]
                'shape': shape as a 2 item list [rows, columns]
            },
            'Ad':{
                'data': [list of lists containing COO data describing background (Ad) matrix in the format [[row, column], value]]
                'shape': shape as a 2 item list [rows, columns]
            },
            'Bf':{
                'data': [list of lists containing COO data describing foreground emissions (Bf) matrix in the format [[row, column], value]]
                'shape': shape as a 2 item list [rows, columns]
            },
            'foreground flows': [ # list of dictionaries representing the indexed foreground flows in Af
                {
                    'index': Af index as integer
                    'location': as string,
                    'name': 'as string,
                    'unit': as string
                },
                ]
            'background flows': [ # list of dictionaries representing the indexed background flows in Ad
                {
                    'brightway_id': as list e.g. ['Ecoinvent3_3_cutoff','b80c575f22df17a0fbc7b4ae11f65dd2'],
                    'ecoinvent_id': as string e.g. '832cb6db-89ea-45a8-878b-42a580a3e33e',
                    'ecoinvent_name': as string e.g. 'market for electricity, medium voltage',
                    'index': Ad row index as integer,
                    'location': as string,
                    'unit': as string
                },
                ]
            'foreground emissions': [ # list of dictionaries representing the indexed foreground emissions in Bf
                {
                    'biosphere3_id': as list e.g. ['biosphere3','075e433b-4be4-448e-9510-9a5029c1ce94'],
                    'index': as integer,
                    'name': as string,
                    'unit': as string
                },
                ]

    """
    format = "Disclosure"
    extractor = DisclosureExtractor
    
    def __init__(self, filepath, db_name=None):
                      
        self.strategies = [
            normalize_units,
            normalize_biosphere_categories,
            normalize_biosphere_names,
            set_code_by_activity_hash,
            functools.partial(link_iterable_by_fields,
                other=Database(config.biosphere),
                kind='biosphere'
            ),
            assign_only_product_as_production,
            link_technosphere_by_activity_hash,
            self.match_required_databases
        ]
        start = time()
        data = self.extractor.extract(filepath)
        
        if db_name is None:
            self.db_name = "Disclosure_database"
        else:
            self.db_name = db_name
            
        self.metadata = {} # TODO: figure out what needs to go in here
        self.project_parameters = None # There are no parameters in a disclosure
        self.database_parameters = None # There are no parameters in a disclosure
        self.data = self.process_disclosure(data)
        self.required_databases = self.get_required_databases(data)
        
    def process_disclosure(self, data):

        new_data = []

        activities = data['foreground flows']
        technosphere = data['background flows']
        biosphere = data['foreground emissions']

        Af_dict = {(x[0][0],x[0][1]):x[1] for x in data['Af']['data']}
        Ad_dict = {(x[0][0],x[0][1]):x[1] for x in data['Ad']['data']}
        Bf_dict = {(x[0][0],x[0][1]):x[1] for x in data['Bf']['data']}

        Af_r, Af_c, Af_v = self.data_to_rcv(data['Af'])
        Ad_r, Ad_c, Ad_v = self.data_to_rcv(data['Ad'])
        Bf_r, Bf_c, Bf_v = self.data_to_rcv(data['Bf'])

        for a in activities:
            
            new_activity = {
                'comment':"",
                'location':a['location'],
                'production amount':1,
                'unit':a['unit'],
                'name':a['name'],
                'exchanges':[
                    {
                     'amount': 1.0,
                     'database': self.db_name,
                     'location': a['location'],
                     'name': a['name'],
                     'reference product': a['name'],
                     'type': 'production',
                     'unit': a['unit']
                    },
                ],
                'database':self.db_name
            }

            i = a['index']
            
            foreground_inputs = [Af_r[n] for n, x in enumerate(Af_c) if x == i]
            technosphere_inputs = [Ad_r[n] for n, x in enumerate(Ad_c) if x == i]
            biosphere_inputs = [Bf_r[n] for n, x in enumerate(Bf_c) if x == i]

            for f in foreground_inputs:
                new_activity['exchanges'].append(self.generate_exchange(database=self.db_name, amount=Af_dict[(f, i)], type='technosphere', **activities[f]))
            for t in technosphere_inputs:
                new_activity['exchanges'].append(self.generate_exchange(database=technosphere[t]['brightway_id'][0], amount=Ad_dict[(t, i)], type='technosphere', name=technosphere[t]['ecoinvent_name'], activity=technosphere[t]['ecoinvent_id'], **technosphere[t]))
            for b in biosphere_inputs:
                new_activity['exchanges'].append(self.generate_exchange(database=biosphere[b]['biosphere3_id'][0], amount=Bf_dict[(b, i)], type='biosphere', code=biosphere[b]['biosphere3_id'][1], **biosphere[b]))

            new_data.append(new_activity)

        return new_data
        
    def generate_exchange(self, **kwargs):
        if kwargs.get('type') == 'biosphere':
            new_exchange = {
                'amount': kwargs.get('amount'),
                'categories': kwargs.get('categories'),
                'database': kwargs.get('database'),
                'name': kwargs.get('name'),
                'type': kwargs.get('type'),
                'unit': kwargs.get('unit')
            }

        else:

            new_exchange = {
                'amount': kwargs.get('amount'),
                'database': kwargs.get('database'),
                'location': kwargs.get('location'),
                'name': kwargs.get('name'),
                'reference product': kwargs.get('name'),
                'type': kwargs.get('type'),
                'unit': kwargs.get('unit')
            }

        for k,v in kwargs.items():
            if k not in new_exchange.keys():
                new_exchange[k]=v


        return new_exchange
    
    def data_to_rcv(self, matrix):
        r = [x[0][0] for x in matrix['data']]
        c = [x[0][1] for x in matrix['data']]
        v = [x[1] for x in matrix['data']]

        return r, c, v
    
    def get_required_databases(self, data):
        disclosure_databases = []

        for x in data['background flows']:
            if x['brightway_id'][0] not in disclosure_databases:
                disclosure_databases.append(x['brightway_id'][0])

        for x in data['foreground emissions']:
            if x['biosphere3_id'][0] not in disclosure_databases:
                disclosure_databases.append(x['biosphere3_id'][0])

        return disclosure_databases
    
    def match_required_databases(self, data):
        for db in self.required_databases:
            if db in databases:
                if db == config.biosphere:
                    self.match_database(db, fields=('code',))
                else:
                    self.match_database(db, fields=('name', 'unit', 'location'))
            else:
                warnings.warn('Database "{}" does not exist in the current project, create/import this database and try again using <DisclosureImporter_instance>.apply_strategies()'.format(db) )
        return data
    