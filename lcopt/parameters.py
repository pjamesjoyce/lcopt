from bw2parameters.parameter_set import ParameterSet
from collections import OrderedDict
from copy import deepcopy

class LcoptParameterSet(ParameterSet):
    """
    Subclass of `bw2parameters.parameter_set.ParameterSet` that takes a `lcopt.LcoptModel` and delegates parameter ordering and evaluation to `bw2parameters`
    
    TODO: Add more documentation and write tests
    """
    
    def __init__(self, modelInstance):
        
        self.modelInstance = modelInstance
        
        self.norm_params = self.normalise_parameters()
        
        self.all_params = {**self.modelInstance.params, **self.modelInstance.production_params, **self.norm_params}
        
        self.bw2_params, self.bw2_global_params, self.bw2_export_params = self.lcopt_to_bw2_params(0)
        
        
        super().__init__(self.bw2_params, self.bw2_global_params)
        
        self.evaluated_parameter_sets = self.preevaluate_exchange_params()
        
    def lcopt_to_bw2_params(self, ps_key):
        
        k0 = list(self.modelInstance.parameter_sets.keys())[ps_key]
        ps1 = self.modelInstance.parameter_sets[k0]
        
        bw2_params = {k:{(x if x != 'function' else 'formula'):y for x, y in v.items()} for k,v in self.all_params.items()}
        
        for k in bw2_params.keys():
            bw2_params[k]['amount'] = ps1.get(k,0)
            
        bw2_global_params = {x['name']: ps1[x['name']] for x in self.modelInstance.ext_params}

        bw2_export_params = []

        for k, v in bw2_params.items():
            to_append = {'name': k}
            if v.get('formula'):
                to_append['formula'] = v['formula']
            else:
                to_append['amount'] = v['amount']
                
            bw2_export_params.append(to_append)
            
        for k, v in bw2_global_params.items():
            bw2_export_params.append({'name':k, 'amount':v})
        
        return bw2_params, bw2_global_params, bw2_export_params
    
    def normalise_parameters(self):
        
        param_copy = deepcopy(self.modelInstance.params)
        production_params = deepcopy(self.modelInstance.production_params)
        norm_params = OrderedDict()
        for k, v in param_copy.items():
            norm_params['n_{}'.format(k)] = {}
            for key, item in v.items():
                if key == 'function':
                    if not item:
                        norm_function = '{} / {}'.format(k, v['normalisation_parameter'])
                    else:
                        norm_function = '({}) / {}'.format(item, v['normalisation_parameter'])
                    
                    norm_params['n_{}'.format(k)][key] = norm_function
                else:
                    norm_params['n_{}'.format(k)][key] = item
        return norm_params
    
    def preevaluate_exchange_params(self):
        
        evaluated_params = OrderedDict()
        
        for n, k in enumerate(self.modelInstance.parameter_sets.keys()):
            
            self.params, self.global_params, _ = self.lcopt_to_bw2_params(n)
            self.evaluate_and_set_amount_field()
            
            this_set = {}
            
            for j, v in self.params.items():
                this_set[j] = v['amount']
                
            evaluated_params[k] = this_set
                
        self.params, self.global_params , _ = self.lcopt_to_bw2_params(0)
        self.evaluate_and_set_amount_field()
        
            
            
        return evaluated_params