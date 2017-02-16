from ipywidgets import widgets
from IPython.display import display

class IFS():
    def __init__(self, modelInstance):
        self.modelInstance = modelInstance
        self.db = self.modelInstance.database['items']
        self.processes = list(filter(lambda x:self.db[x]['type'] == 'process', self.db))
        
        
        self.process_options = {self.db[x]['name'] : x for x in self.processes}
        self.dropdownProcess = widgets.Dropdown(description='Choose a process', options=self.process_options)
        self.dropdownInput = widgets.Dropdown(description='Choose an input')
        
        self.textParameterFunction = widgets.Text(description="Enter function here")
        self.buttonSave = widgets.Button(description='Save')
        
        self.defaultProcess = self.process_options[list(self.process_options.keys())[0]]
        self.chosenProcess = self.defaultProcess
        self.chosenProcessOutputCode = self.output_code(self.chosenProcess)
        self.chosenInput = None
        self.chosenParameterId = None
        
        self.dropdownProcess.observe(self.handle_event)
        self.dropdownInput.observe(self.handle_event)
        self.textParameterFunction.observe(self.handle_event)
        self.buttonSave.on_click(self.button_click)
        
        self.dropdownInput.options = self.get_input_list(self.defaultProcess)
        
        display(self.dropdownProcess, self.dropdownInput,self.textParameterFunction, self.buttonSave)
        
    def output_code(self, process_id):
        
        exchanges = self.modelInstance.database['items'][process_id]['exchanges']
        
        production_filter = lambda x:x['type'] == 'production'
           
        code = list(filter(production_filter, exchanges))[0]['input'][1]
        
        return code
        
        
    def get_parameter_id(self):
        #print('getting parameter id')
        try:
            code_tuple = (self.chosenInput[1], self.chosenProcessOutputCode)
            #print (code_tuple)
            self.chosenParameterId = self.modelInstance.parameter_map[code_tuple]
            #print(self.chosenParameterId)
            
            return self.chosenParameterId
        except:
            print('not working')
            
    
    def get_input_list(self, process = None):
        if process == None:
            process = self.chosenProcess
            
        exchanges = self.db[process]['exchanges']
        input_filter = lambda x:x['type']=='technosphere'
        inputs = list(filter(input_filter, exchanges))
        input_codes = [x['input'] for x in inputs]
        input_names = [self.modelInstance.get_name(x[1]) for x in input_codes]
        new_options = dict(zip(input_names, input_codes))
        return new_options
    
    def handle_event(self, event):
        if event['type'] == 'change' and event['name'] == 'value':
            if event['owner'] == self.dropdownProcess:
                #print ('Event from dropdownProcess')
                #print ('setting chosenProcess to {}'.format(event['new']))
                self.chosenProcess = event['new']
                self.chosenProcessOutputCode = self.output_code(event['new'])
                
                #self.dropdownProcess.disabled=True
                
                new_options = self.get_input_list()
                
                self.dropdownInput.options=new_options
                
                #display(self.dropdownInput)
            elif event['owner'] == self.dropdownInput:
                #print ('Event from dropdownInput')
                #print ('setting chosenInput to {}'.format(event['new']))
                self.chosenInput = event['new']
                
            parameter_id = self.get_parameter_id()
            try:
                self.textParameterFunction.description = parameter_id
                self.textParameterFunction.disabled=False
            except:
                self.textParameterFunction.description = "parameter_id"
                self.textParameterFunction.disabled=True
                
        #elif event['owner'] == self.textParameterFunction:
            #print('event from textParameterFunction')
            #print(event)
                
    def button_click(self, button):
        new_function = self.textParameterFunction.value
        parameter = self.modelInstance.params[self.chosenParameterId]
        parameter['function'] = new_function
        
        self.dropdownProcess.close()
        self.dropdownInput.close()
        self.textParameterFunction.close()
        button.close()
        
        print('Updated function for {} ({}) to be {}'.format(parameter['description'], self.chosenParameterId, new_function))
        