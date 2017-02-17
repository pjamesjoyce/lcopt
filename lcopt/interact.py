from flask import Flask, request, render_template
import webbrowser
import json

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
            'newConnection': self.newConnection,
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
        
        products = list(filter(lambda x:db[x]['type'] == 'product', db))
        #print([(db[x]['name'], x[1]) for x in products])
        product_codes = [x[1] for x in products]
        processes = list(filter(lambda x:db[x]['type'] == 'process', db))
        process_codes = [x[1] for x in processes]
        process_name_map = dict(zip(process_codes, [db[(m.database['name'],x[1])]['name'] for x in processes]))
        
        #note this maps from output code to process
        process_output_map = {self.output_code(x): x[1] for x in processes}
        self.reverse_process_output_map = {value:key for key, value in process_output_map.items()}
                
        intermediates = [self.output_code(x) for x in processes]
        intermediate_map = dict(zip(intermediates, [db[(m.database['name'],x)]['name'] for x in intermediates]))
        
        process_output_name_map = dict(zip(process_codes, [db[(m.database['name'],x)]['name'] for x in intermediates]))
        
        inputs = [x for x in product_codes if x not in intermediates]
        input_map = dict(zip(inputs, [db[(m.database['name'],x)]['name'] for x in inputs]))
        
        label_map = {**input_map, **process_output_name_map}
        
        self.outputlabels = [{'process_id': x, 'output_name':process_output_name_map[x]} for x in process_codes]
        #print (self.outputlabels)
        
        link_indices = [process_output_map[x] if x in intermediates else x for x in product_codes]
               
        #print(link_indices)
        
        # compute the nodes
        # TODO: figure out how to duplicate nodes with multiple uses (e.g. energy, electricity)
        i = 1
        self.nodes = []
        for t in process_codes:
            self.nodes.append({'name':process_name_map[t],'type':'transformation','id':t,'initX':i*100,'initY':i*100})
            i+=1
        
        i=1
        for p in inputs:
            self.nodes.append({'name':input_map[p],'type':'input','id':p+"__0",'initX':i*50+150,'initY':i*50})
            i+=1
            
        # compute links
        self.links=[]
        
        input_duplicates = []
        
        for c, column in enumerate(matrix.T):
            for r, i in enumerate(column):
                if i>0:
                    p_from = link_indices[r]
                    p_to = link_indices[c]
                    if p_from in inputs:
                        suffix = "__" + str(input_duplicates.count(p_from))
                        input_duplicates.append(p_from)
                        p_type = 'input'
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
        exchanges = [{'name':output_name, 'type':'production', 'unit':unit}]
        location ='GLO'
        m.create_process(name, exchanges, location, unit)
        
        print (m.database['items'][(m.database['name'], postData['uuid'])])
        
        return "OK"
    
    def newConnection(self, postData):
        db = self.modelInstance.database
        source = postData['sourceId']
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
    
    def echo(self, postData):
        data = {'message':'Hello from echo'}
        return json.dumps(data)
        
    def searchEcoinvent(self, postData):
        search_term = postData['search_term']
        location = postData['location']
        markets_only = postData['markets_only'] in ['True', 'true', 'on']
        m = self.modelInstance
        #print(type(markets_only))
        result = m.search_databases(search_term, location,  markets_only)
        
        json_dict = {str(k):v for k, v in dict(result).items()}
        
        data = {'message':'hello from ecoinvent', 'search_term':search_term, 'result':json_dict}
        return json.dumps(data)
    
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
            f = request.form
            
            action = self.postActions[f['action']]
            return action(f)
            
            #return "OK"

        @app.route('/shutdown')
        def shutdown():
            self.shutdown_server()
            return render_template('shutdown.html')

        url = 'http://127.0.0.1:5000'
        webbrowser.open_new(url)
        
        app.run()