from flask import Flask, request, render_template, redirect
import webbrowser
import json
from ast import literal_eval
from lcopt.io import exchange_factory
import mpld3
from collections import OrderedDict
from itertools import groupby

from lcopt.bw2_export import Bw2Exporter

class FlaskSandbox():
    
    def __init__(self, modelInstance):
        
        self.modelInstance = modelInstance
        self.get_sandbox_variables()
        
        # Set up the dictionary of actions that can be processed by POST requests
        self.postActions = {
            'savePosition':self.savePosition,
            'saveModel':self.saveModel,
            'newProcess':self.newProcess,
            'echo':self.echo,
            'searchEcoinvent':self.searchEcoinvent,
            'searchBiosphere':self.searchBiosphere,
            'newConnection': self.newConnection,
            'addInput':self.addInput,
            'inputLookup':self.inputLookup,
            'parse_parameters': self.parameter_parsing,
            'create_function': self.create_function,
            'add_parameter': self.add_parameter,
        }
        
        #print (self.modelInstance.newVariable)
        
    def shutdown_server(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        
    def output_code(self, process_id):
        
        exchanges = self.modelInstance.database['items'][process_id]['exchanges']
        
        production_filter = lambda x:x['type'] == 'production'
           
        code = list(filter(production_filter, exchanges))[0]['input'][1]
        
        return code
    
    def get_sandbox_variables(self):
        m = self.modelInstance
        db = m.database['items']
        matrix = m.matrix
        
        sandbox_positions = m.sandbox_positions


        products = OrderedDict((k,v) for k, v in db.items() if v['type'] == 'product')
        product_codes = [k[1] for k in products.keys()]


        processes = OrderedDict((k,v) for k, v in db.items() if v['type'] == 'process')
        process_codes = [k[1] for k in processes.keys()]
        process_name_map = {k[1]:v['name'] for k, v in processes.items()}


        #note this maps from output code to process
        process_output_map = {self.output_code(x): x[1] for x in processes.keys()}
        self.reverse_process_output_map = {value:key for key, value in process_output_map.items()}


        intermediates = {k:v for k, v in products.items() if v['lcopt_type'] == 'intermediate'}
        intermediate_codes = [k[1] for k in intermediates.keys()]
        intermediate_map = {k[1]: v['name'] for k, v in intermediates.items()}

        #process_output_name_map = {process_code: output_name for x in processes.keys()}
        process_output_name_map = {x[1]: intermediate_map[self.reverse_process_output_map[x[1]]] for x in processes.keys()}


        inputs = OrderedDict((k,v) for k, v in products.items() if v['lcopt_type'] == 'input')
        input_codes = [k[1] for k in inputs.keys()]
        input_map = {k[1]: v['name'] for k, v in inputs.items()}
        self.reverse_input_map = {value:key for key, value in input_map.items()}


        biosphere = OrderedDict((k,v) for k, v in products.items() if v['lcopt_type'] == 'biosphere')
        biosphere_codes = [k[1] for k in biosphere.keys()]
        biosphere_map = {k[1]: v['name'] for k, v in biosphere.items()}
        self.reverse_biosphere_map = {value:key for key, value in biosphere_map.items()}


        label_map = {**input_map, **process_output_name_map, **biosphere_map}

        #print('label_map = {}\n'.format(label_map))
        
        self.outputlabels = [{'process_id': x, 'output_name':process_output_name_map[x]} for x in process_codes]
        
        link_indices = [process_output_map[x] if x in intermediate_codes else x for x in product_codes]
               
        
        # compute the nodes
        i = 1
        self.nodes = []
        for t in process_codes:
            self.nodes.append({'name':process_name_map[t],'type':'transformation','id':t,'initX':i*100,'initY':i*100})
            i+=1
        
        i=1
        for p in input_codes:
            
            self.nodes.append({'name':input_map[p],'type':'input','id':p+"__0",'initX':i*50+150,'initY':i*50})
            i+=1

        i=1
        for p in biosphere_codes:
            
            self.nodes.append({'name':biosphere_map[p],'type':'biosphere','id':p+"__0",'initX':i*50+150,'initY':i*50})
            i+=1
            
        # compute links
        self.links=[]
        
        input_duplicates = []
        biosphere_duplicates =[]
        
        #check there is a matrix (new models won't have one until parameter_scan() is run)
        if matrix is not None:
            for c, column in enumerate(matrix.T):
                for r, i in enumerate(column):
                    if i>0:
                        p_from = link_indices[r]
                        p_to = link_indices[c]
                        if p_from in input_codes:
                            suffix = "__" + str(input_duplicates.count(p_from))
                            input_duplicates.append(p_from)
                            p_type = 'input'
                        elif p_from in biosphere_codes:
                            suffix = "__" + str(biosphere_duplicates.count(p_from))
                            biosphere_duplicates.append(p_from)
                            p_type = 'biosphere'
                        else:
                            suffix = ""
                            p_type = 'intermediate'
                        
                        self.links.append({'sourceID':p_from + suffix, 'targetID':p_to, 'type':p_type, 'amount':1, 'label':label_map[p_from]})
                    
        #add extra nodes
        while len(input_duplicates)>0:
            p = input_duplicates.pop()
            count = input_duplicates.count(p)
            if count>0:
                suffix = "__" + str(count)
                self.nodes.append({'name':input_map[p],'type':'input','id':p+suffix,'initX':i*50+150,'initY':i*50})
                i+=1
                

        while len(biosphere_duplicates)>0:
            p = biosphere_duplicates.pop()
            count = biosphere_duplicates.count(p)
            if count>0:
                suffix = "__" + str(count)
                self.nodes.append({'name':biosphere_map[p],'type':'biosphere','id':p+suffix,'initX':i*50+150,'initY':i*50})
                i+=1
                
            
        #try and reset the locations
        
        for n in self.nodes:
            node_id = n['id']
            if node_id in sandbox_positions:
                n['initX'] = sandbox_positions[node_id]['x']
                n['initY'] = sandbox_positions[node_id]['y']
                
        #print(self.nodes)
        #print(inputs)
        #print(process_name_map)
        
    def savePosition(self, f):
        
        if f['uuid'] not in self.modelInstance.sandbox_positions:
            self.modelInstance.sandbox_positions[f['uuid']]={}
        self.modelInstance.sandbox_positions[f['uuid']]['x'] = f['x']
        self.modelInstance.sandbox_positions[f['uuid']]['y'] = f['y']
        #print('Setting {} to ({},{})'.format(f['uuid'], f['x'], f['y']))
        return "OK"
    
    def saveModel(self, postData):
        #print ("this is where we save the model")
        self.modelInstance.save()
        return "OK"
    
    def newProcess(self, postData):
        #print ("this is where we're going to create the process, using...")
        #print (postData)
        m = self.modelInstance
        name = postData['process_name']
        unit = postData['unit']
        output_name  = postData['output_name']
        exchanges = [{'name':output_name, 'type':'production', 'unit':unit, 'lcopt_type':'intermediate'}]
        location ='GLO'
        m.create_process(name, exchanges, location, unit)
        self.modelInstance.parameter_scan()
        print (m.database['items'][(m.database['name'], postData['uuid'])])
        
        return "OK"
    
    def newConnection(self, postData):

        #print(postData)
        db = self.modelInstance.database
        self.get_sandbox_variables()

        source = postData['sourceId']
        #print(self.reverse_process_output_map[source])

        target = postData['targetId']
        label = postData['label']
        new_exchange = {'amount': 1,
                 'comment': 'technosphere exchange of {}'.format(label),
                 'input': (db['name'], self.reverse_process_output_map[source]),
                 'type': 'technosphere',
                 'uncertainty type': 1}
        
        db['items'][(db['name'], target)]['exchanges'].append(new_exchange)
        
        self.modelInstance.parameter_scan()
        
        #print (db['items'][(db['name'], target)]['exchanges'])
        
        return "OK"
    
    def addInput(self, postData):
        #print(postData)
        my_targetId = postData['targetId']
        
        my_name = postData['name']
        my_type = postData['type']
        my_unit = postData['unit']
        my_location = postData['location']
        
        m = self.modelInstance

        exchange_to_link = m.get_exchange(my_name)

        if exchange_to_link == False:
        
            #Create the new product
            kwargs ={}

            if 'ext_link' in postData.keys():
                my_ext_link = literal_eval(postData['ext_link'])
                kwargs['ext_link'] = my_ext_link

                #exchange_to_link = m.create_product (name = my_name, location =my_location , unit=my_unit, ext_link = my_ext_link)
                #print('created linked product')
            #else:
            if 'lcopt_type' in postData.keys():
                lcopt_type = postData['lcopt_type']
                kwargs['lcopt_type'] = lcopt_type

            exchange_to_link = m.create_product (name = my_name, location =my_location , unit=my_unit, **kwargs)
                #print('created unlinked product')

        #link the product
        #this_exchange = m.get_exchange(my_name)
        #print(this_exchange)
        this_exchange_object = exchange_factory(exchange_to_link, 'technosphere', 1, 1, '{} exchange of {}'.format('technosphere', my_name))
        #print (this_exchange_object)
        
        target_item = m.database['items'][(m.database['name'], my_targetId)]
        #[print(target_item)]
        target_item['exchanges'].append(this_exchange_object)
        
        #run the parameter scan
        m.parameter_scan()
        
        
        return "OK"
    
    def inputLookup(self, postData):
        m = self.modelInstance
        myInput = m.database['items'][(m.database['name'], postData['code'])]
        
        return_data = {}
        
        if 'ext_link' in myInput.keys():
            ext_link = myInput['ext_link']
            ext_db = [x['items'] for x in m.external_databases if x['name'] == ext_link[0]][0]
            full_link = ext_db[ext_link]
            if postData['format'] == 'ecoinvent':
                full_link_string = "{} {{{}}} [{}]".format(full_link['name'], full_link['location'], full_link['unit'])
            elif postData['format'] == 'biosphere':
                if full_link['type'] == 'emission':
                    full_link_string = '{} (emission to {}) [{}]'.format(full_link['name'], ", ".join(full_link['categories']), full_link['unit'])
                else:
                    full_link_string = '{} ({}) [{}]'.format(full_link['name'], ", ".join(full_link['categories']), full_link['unit'])
            
            return_data['isLinked']=True
            return_data['ext_link']=str(ext_link)
            return_data['ext_link_string'] = full_link_string
            return_data['ext_link_unit'] = full_link['unit']
        else:
            print('This is an unlinked product')
            return_data['isLinked']=False
            return_data['unlinked_unit'] = myInput['unit']
        
        return json.dumps(return_data)
    
    def echo(self, postData):
        data = {'message':'Hello from echo'}
        return json.dumps(data)
        
    def searchEcoinvent(self, postData):
        search_term = postData['search_term']
        location = postData['location']
        markets_only = postData['markets_only'] in ['True', 'true', 'on']
        m = self.modelInstance
        #print(type(markets_only))
        #print(location)
        if location == "":
            #print ('no location')
            location = None
            
        result = m.search_databases(search_term, location,  markets_only, databases_to_search = [m.ecoinventName])
        
        json_dict = {str(k):v for k, v in dict(result).items()}
        
        data = {'message':'hello from ecoinvent', 'search_term':search_term, 'result':json_dict, 'format': 'ecoinvent'}
        return json.dumps(data)

    def searchBiosphere(self, postData):
        
        search_term = postData['search_term']
        
        m = self.modelInstance
            
        result = m.search_databases(search_term, databases_to_search = [m.biosphereName])
        
        json_dict = {str(k):v for k, v in dict(result).items()}
        
        data = {'message':'hello from biosphere3', 'search_term':search_term, 'result':json_dict, 'format': 'biosphere'}
        #print (json_dict)
        return json.dumps(data)

    def create_function(self, postData):

        print(postData)
        new_function = postData['my_function']
        parameter = self.modelInstance.params[postData['for']]
        parameter['function'] = new_function

        return "OK"

    def parameter_sorting(self):
        parameters = self.modelInstance.params


        # create a default parameter set if there isn't one yet
        if len(self.modelInstance.parameter_sets) == 0:
            print ('No parameter sets - creating a default set')
            self.modelInstance.parameter_sets['ParameterSet_1'] = {}
            for param in parameters:
                self.modelInstance.parameter_sets['ParameterSet_1'][param] = 0


        exporter = Bw2Exporter(self.modelInstance)
        exporter.evaluate_parameter_sets()
        evaluated_parameters = self.modelInstance.evaluated_parameter_sets
        

        subsectionTitles = {
            'input':"Inputs from the 'technosphere'",
            'intermediate':"Inputs from other processes",
            'biosphere': "Direct emissions to the environment"
        }
        
        to_name = lambda x: parameters[x]['to_name']
        input_order = lambda x: parameters[x]['coords'][1]
        type_of = lambda x : parameters[x]['type']

        sorted_keys = sorted(parameters, key = input_order)

        sorted_parameters = []

        for target, items in groupby(sorted_keys, to_name):
            #print(target)
            
            section = {'name': target, 'my_items':[]}

            sorted_exchanges = sorted(items, key = type_of)

            #print sorted_exchanges
            for type, exchanges in groupby(sorted_exchanges, type_of):
                #print('\t{}'.format(type))
                subsection = {'name':subsectionTitles[type], 'my_items':[]}
                for exchange in exchanges:

                    if parameters[exchange].get('function'):
                        print ('{} determined by a function'.format(exchange))
                        values = ['{} = {:.3g}'.format(parameters[exchange]['function'], e_ps[exchange]) for e_ps_name, e_ps in evaluated_parameters.items()]
                        isFunction = True
                    else:
                        values = [ps[exchange] if exchange in ps.keys() else '' for ps_name, ps in self.modelInstance.parameter_sets.items()]
                        isFunction = False

                    #print('\t\t{} ({}) {}'.format(parameters[exchange]['from_name'], exchange, values))

                    subsection['my_items'].append({'id':exchange, 'name': parameters[exchange]['from_name'], 'existing_values': values, 'unit':parameters[exchange]['unit'], 'isFunction':isFunction})
                
                
                
                section['my_items'].append(subsection)
            
            db_code = (self.modelInstance.database['name'], parameters[exchange]['to'])
            #print(db_code)
            
            unit = self.modelInstance.database['items'][db_code]['unit']
            section['name'] = "{}\t(1 {})".format(target, unit)
            sorted_parameters.append(section)

        ext_section ={'name':'Global Parameters', 'my_items':[{'name':'User created', 'my_items':[]}]}
        for e_p in self.modelInstance.ext_params:
            values = [ps[e_p['name']] if e_p['name'] in ps.keys() else e_p['default'] for ps_name, ps in self.modelInstance.parameter_sets.items()]
            ext_section['my_items'][0]['my_items'].append({'id':e_p['name'], 'name': e_p['description'], 'existing_values': values, 'unit':'', 'isFunction':False})

        sorted_parameters.append(ext_section)

        return sorted_parameters

    def parameter_parsing(self, postData):
            
            myjson = json.loads(postData['data'])
            #print(myjson[0])
            
            for line in myjson:
                line_id = line['id']
                if line['Name'] != '':
                    for k in line.keys():
                        if k[:13] == 'ParameterSet_':
                            if line[k] == '':
                                line[k] = 0
                                
                            if k in self.modelInstance.parameter_sets.keys():
                                self.modelInstance.parameter_sets[k][line_id] = float(line[k])
                            else:
                                self.modelInstance.parameter_sets[k] = OrderedDict()
                                self.modelInstance.parameter_sets[k][line_id] = float(line[k])
                        
                
            
            self.modelInstance.save()       

            print('parameters saved')    
            
            return 'OK'
            #return redirect("/")

    def add_parameter(self, postData):

        self.modelInstance.add_parameter(postData['param_id'], postData['param_description'], float(postData['param_default']))
        print ('Added {} (default {}) added to global parameters'.format(postData['param_id'], postData['param_default']))

        return "OK"
            
        
    def run(self):
        
        app = Flask(__name__)

        @app.route('/')
        def index():
            name = self.modelInstance.name
            
            self.get_sandbox_variables()
                        
            args = {'model':{'name': name}, 'nodes':self.nodes, 'links':self.links, 'outputlabels':self.outputlabels}
            return render_template('sandbox.html', args = args)
        
        @app.route('/process_post', methods=['POST'])
        def process_post():
            try:
                f = request.form
            except:
                f = request.get_json()

            #print(f)
            
            action = self.postActions[f['action']]
            return action(f)
            
            #return "OK"

        @app.route('/shutdown')
        def shutdown():
            self.shutdown_server()
            return render_template('shutdown.html')
        
        @app.route('/inputs.json')
        def inputs_as_json():
            """creates a json file of the reverse input map to send from the server"""
            self.get_sandbox_variables()
            # to_json = [x for x in self.reverse_input_map.keys()]
            #to_json = reverse_input_map
            to_json = [{'name':k, 'code': v} for k,v in self.reverse_input_map.items()]
            input_json = json.dumps(to_json)
            return input_json

        @app.route('/biosphere.json')
        def biosphere_as_json():
            """creates a json file of the reverse biosphere map to send from the server"""
            self.get_sandbox_variables()
            # to_json = [x for x in self.reverse_input_map.keys()]
            #to_json = reverse_input_map
            to_json = [{'name':k, 'code': v} for k,v in self.reverse_biosphere_map.items()]
            biosphere_json = json.dumps(to_json)
            return biosphere_json
        
        @app.route('/testing')
        def testbed():
            #import time
            #time.sleep(5)
            args = {'model':{'name': self.modelInstance.name}}
            #args['result_sets'] = self.modelInstance.result_set
           
            return render_template('testbed.html', args=args)
        
        @app.route('/functions')
        def function_editor():
            
            args = {'model':{'name': self.modelInstance.name}}
            
            return render_template('create_functions.html', args=args)

        @app.route('/results.json')
        def results_as_json():
            
            send_to_json = ['json', 
                            'contributionAnalysis', 
                            'model_edges', 
                            'model_nodes', 
                            'full_edges', 
                            'pie_data', 
                            'model_nodes_split', 
                            'model_edges_split', 
                            'full_nodes']
            
            json_dataset = []
            
            for ds in self.modelInstance.result_set:
                filtered_ds = {}
                for k, v in ds.items():
                    if k in send_to_json:
                        filtered_ds[k]=v
                json_dataset.append(filtered_ds)
            
            return json.dumps(json_dataset)

        @app.route('/parameters.json')
        def parameter_json():
            sorted_parameters = self.parameter_sorting()
            return json.dumps(sorted_parameters)

        @app.route('/status.json')
        def status():

            db = self.modelInstance.database['items']
            products = OrderedDict((k,v) for k, v in db.items() if v['type'] == 'product')
            inputs = OrderedDict((k,v) for k, v in products.items() if v['lcopt_type'] == 'input')
            ext_linked_inputs = OrderedDict((k,v) for k, v in inputs.items() if v.get('ext_link'))
            biosphere = OrderedDict((k,v) for k, v in products.items() if v['lcopt_type'] == 'biosphere')

            has_model = len(db) != 0
            model_has_impacts = len(ext_linked_inputs) + len(biosphere) != 0
            model_has_parameters = len (self.modelInstance.parameter_sets) != 0
            model_is_runnable = all([has_model, model_has_impacts, model_has_parameters])
            model_has_functions = len([x for k, x in self.modelInstance.params.items() if x['function'] is not None]) != 0
            model_is_fully_formed = all([has_model, model_has_impacts, model_has_parameters, model_has_functions])


            status_object = {
                'has_model':has_model,
                'model_has_impacts':model_has_impacts,
                'model_has_parameters':model_has_parameters,
                'model_has_functions':model_has_functions,
                'model_is_runnable':model_is_runnable,
                'model_is_fully_formed':model_is_fully_formed,
            }

            return json.dumps(status_object)


        # TODO: Make these responsive
        @app.route('/analyse')
        def analyse_preload():
            
            args = {'model':{'name': self.modelInstance.name}}
            item = request.args.get('item')
            item_code = request.args.get('item_code')
            print(request.args)

            args['item'] = item
            args['item_code'] = item_code

            print('PRELOAD {}'.format(args['item_code']))
            
            #self.modelInstance.analyse(item)
            return render_template('analysis_preload.html', args = args)
        
        @app.route('/analysis')
        def analysis():
            
            item_code = request.args.get('item_code')
            item = request.args.get('item')

            self.modelInstance.analyse(item, item_code)
            
            args = {'model':{'name': self.modelInstance.name}}
            
            args['item'] = item
            args['result_sets'] = self.modelInstance.result_set
            
            
            return render_template('analysis.html', args = args)
            #return render_template('testbed.html', args = args)
            

        @app.route('/network.json')
        def network_as_json():
            parameter_set = request.args.get('ps')
            return self.modelInstance.result_set[int(parameter_set)]['json']
        
        @app.route('/parameters')
        def sorted_parameter_setup():
            
            sorted_parameters = self.parameter_sorting()
                
            args = {'title':'Parameter set'}
            args['sorted_parameters'] = sorted_parameters
            args['ps_names'] = [x for x in self.modelInstance.parameter_sets.keys()]
            
            return render_template('parameter_set_table_sorted.html',
                                 args = args)


        url = 'http://127.0.0.1:5000/'
        webbrowser.open_new(url)
        print ("running from the module")
        app.run()

        