from lcopt.io import exchange_factory
from copy import deepcopy
from asteval import Interpreter
from itertools import groupby

class Bw2Exporter():
    
    def __init__(self, modelInstance):
        self.modelInstance = modelInstance

        # set up the parameter hook dictionary
        self.evaluate_parametersets()
        self.create_parameter_map()
        
    def evaluate_parametersets(self):
        """ 
        This takes the parameter sets of the model instance and evaluates any formulas using the parameter values to create a 
        fixed, full set of parameters for each parameter set in the model
        """
        
        evaluated_parameter_sets = []
    
        aeval = Interpreter()
        
        parameter_sets = self.modelInstance.parameter_sets
        parameters = self.modelInstance.params
        ext_params = self.modelInstance.ext_params

        has_function = lambda x: parameters[x]['function'] is not None
        sorted_keys = sorted(parameters, key = has_function)

        ext_param_list = [x['name'] for x in ext_params]

        for ps_name, ps in parameter_sets.items():
            this_ps = {}
            
            #print (ps_name)
            #print()
            #print('External parameters')
            for p in ext_param_list:
                aeval.symtable[p] = ps[p]
                #print(p, ps[p])
                this_ps[p]=ps[p]

            for key, group in groupby(sorted_keys, has_function):

                if key == False:
                    #print()
                    #print('Fixed parameters')
                    for item in group:
                        try:
                            aeval.symtable[item] = ps[item]
                        except KeyError:
                            ps[item] = 0
                            print ('{} not found in {}, setting to zero'.format(item, ps_name))
                            aeval.symtable[item] = ps[item]

                        #print(item, ps[item])
                        this_ps[item]=ps[item]
                else:
                    #print()
                    #print('Calculated Parameters')
                    for item in group:

                        amount = aeval(self.modelInstance.params[item]['function'])
                        aeval.symtable[item] = amount
                        #print(item, amount)
                        this_ps[item]=amount
            #print()
            #print()
            evaluated_parameter_sets.append(this_ps)
        
        self.evaluated_parameter_sets = evaluated_parameter_sets
        #return evaluated_parameter_sets

    def create_parameter_map(self):
        """
        Creates a parameter map which takes a tuple of the exchange 'from' and exchange 'to' codes 
        and returns the parameter name for that exchange
        """
        names = self.modelInstance.names
        db = self.modelInstance.database['items']
        parameter_map = {}
        
        def get_names_index(my_thing):
            return[i for i,x in enumerate(names) if x == my_thing][0]
        
        for k, this_item in db.items():
            if this_item['type'] == 'process':
                production_id = [x['input'] for x in  this_item['exchanges'] if x['type'] == 'production'][0]
                input_ids = [x['input'] for x in  this_item['exchanges'] if x['type'] == 'technosphere']
                production_index = get_names_index(db[production_id]['name'])
                input_indexes = [get_names_index(db[x]['name']) for x in input_ids]
                parameter_ids = ['p_{}_{}'.format(x, production_index) for x in input_indexes]
                parameter_map_items = {(input_ids[n],k):parameter_ids[n] for n, x in enumerate(input_ids)}
                #check = [self.modelInstance.params[x]['description'] for x in parameter_ids]
                #print(check)
                #print(parameter_map_items)
                parameter_map.update(parameter_map_items)
                
        self.parameter_map = parameter_map
        #return parameter_map
        
        
        
    def get_output(self, process_id):
        
        exchanges = self.modelInstance.database['items'][process_id]['exchanges']
        
        production_filter = lambda x:x['type'] == 'production'
           
        code = list(filter(production_filter, exchanges))[0]['input']
        
        name = self.modelInstance.database['items'][code]['name']
        
        return code
    
    
        
    def export_to_bw2(self):
        
        db = self.modelInstance.database['items']
        name = self.modelInstance.database['name']

        altbw2database = deepcopy(db)

        products = list(filter(lambda x: altbw2database[x]['type']=='product', altbw2database))
        processes = list(filter(lambda x: altbw2database[x]['type']=='process', altbw2database))
        
        
        #for i in processes:
         #   print(self.get_output(i))
        #intermediates = [self.output_code(x) for x in processes]
        intermediate_map = {self.get_output(x): x for x in processes}
        #print (intermediate_map)

        
        for p in products:
            product = altbw2database[p]
            product['type'] = 'process'
            new_exchanges = [x for x in product['exchanges'] if x['type']!='production']                
            
            product['exchanges']=new_exchanges
            
            #link to intermediate generator
            if p in intermediate_map.keys():
                #print (db[p]['name'])
                product['exchanges'].append(exchange_factory(intermediate_map[p], 'technosphere', 1, 1, 'intermediate link'))

            #add external links
            if 'ext_link' in product.keys():
                if product['ext_link'][0] == 'biosphere3':
                    product['exchanges'].append(exchange_factory(product['ext_link'], 'biosphere', 1, 1, 'external link to {}'.format(product['ext_link'][0])))
                else:    
                    product['exchanges'].append(exchange_factory(product['ext_link'], 'technosphere', 1, 1, 'external link to {}'.format(product['ext_link'][0])))
        
        
        
        for p in processes:
            process = altbw2database[p]
            new_exchanges = [x for x in process['exchanges'] if x['type']!='production']    
            #print (new_exchanges)
            
            # add parameter hooks
            for e in new_exchanges:
                #print (self.parameter_map[(e['input'], p)])
                e['parameter_hook'] = self.parameter_map[(e['input'], p)]
            
            
            process['exchanges']=new_exchanges
                    
        return name, altbw2database