from lcopt.bw2_parameter_utils import get_symbols, CapitalizationError, ParameterError 
from asteval import Interpreter
from collections import OrderedDict
from pprint import pformat
from copy import deepcopy

class ParameterInterpreter():

    def __init__(self, modelInstance):

        self.modelInstance = modelInstance

        self.params = self.modelInstance.params
        self.global_params = {item['name']: item for item in self.modelInstance.ext_params}
        self.production_params = self.modelInstance.production_params
        self.normalised_params = self.normalise_parameters()
        #print (self.global_params)
        
        self.parameter_sets = self.modelInstance.parameter_sets
        
        self.references = self.get_references()

        #for name, references in self.references.items():
        #    if name in references:
        #        raise SelfReference(
        #            u"Formula for parameter {} references itself".format(name)
        #        )

        self.order = self.get_order()

    def normalise_parameters(self):
        
        param_copy = deepcopy(self.params)
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

    def get_references(self):
        """Create dictionary of parameter references"""
        refs = {key: get_symbols(value['function'])
                if value.get('function') else set()
                for key, value in self.params.items()}
        refs.update({key: get_symbols(value['function'])
                     if value.get('function') else set()
                     for key, value in self.normalised_params.items()})
        refs.update({key: get_symbols(value['function'])
                     if value.get('function') else set()
                     for key, value in self.production_params.items()})
        refs.update({key: set() for key in self.global_params})
        return refs

    def get_order(self):
        """Get a list of parameter name in an order that they can be safely evaluated"""
        order = []
        seen = set()
        refs = self.references.copy()

        while refs:
            last_iteration = set(refs.keys())
            for k, v in refs.items():
                if not v.difference(seen):
                    seen.add(k)
                    order.append(k)
                    refs.pop(k)
                    break
            if not last_iteration.difference(set(refs.keys())):
                seen_lower_case = {x.lower() for x in seen}
                # Iterate over all remaining references,
                # and see if references would match if lower cased
                wrong_case = [
                    (k, v)
                    for k, v in refs.items()
                    if not {x.lower() for x in v}.difference(seen_lower_case)
                ]
                if wrong_case:
                    raise CapitalizationError((
                        u"Possible errors in upper/lower case letters for some parameters.\n"
                        u"Unmatched references:\n{}\nMatched references:\n{}"
                    ).format(pformat(refs, indent=2), pformat(sorted(seen), indent=2))
                    )
                raise ParameterError((u"Undefined or circular references for the following:"
                                      u"\n{}\nExisting references:\n{}").format(pformat(refs, indent=2), pformat(sorted(order), indent=2)))

        return order

    def evaluate_parameter_sets(self):
        """ 
        This takes the parameter sets of the model instance and evaluates any formulas using the parameter values to create a 
        fixed, full set of parameters for each parameter set in the model
        """
        
        evaluated_parameter_sets = OrderedDict()
        
        for ps_name, ps in self.parameter_sets.items():
            
            #print(ps_name)
            
            this_ps = {}
            aeval = Interpreter()

            all_params = dict(self.params)
            all_params.update(dict(self.normalised_params))
            all_params.update(dict(self.production_params))
            
            for key in self.order:
                
                if key in self.global_params:
                    if key not in ps.keys():
                        ps[key] = self.global_params[key]['default']

                    aeval.symtable[key] = this_ps[key] = ps[key]
                    
                elif all_params[key].get('function'):
                    value = aeval(all_params[key]['function'])
                    aeval.symtable[key] = this_ps[key] = value
                    
                else:
                    if key not in ps.keys():
                        if key in self.production_params.keys():
                            ps[key] = 1
                        else:
                            ps[key] = 0
                    aeval.symtable[key] = this_ps[key] = ps[key]
            
            evaluated_parameter_sets[ps_name] = this_ps
            
        #print(evaluated_parameter_sets)
        
        self.modelInstance.evaluated_parameter_sets = evaluated_parameter_sets
        
        return(evaluated_parameter_sets)
