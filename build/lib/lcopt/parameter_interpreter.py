from lcopt.bw2_parameter_utils import get_symbols, EXISTING_SYMBOLS, isstr, isidentifier

from asteval import Interpreter
from collections import OrderedDict

class ParameterInterpreter():

    def __init__(self, modelInstance):

        self.modelInstance = modelInstance

        self.params = self.modelInstance.params
        self.global_params = {item['name']: item for item in self.modelInstance.ext_params}
        #print (self.global_params)
        
        self.parameter_sets = self.modelInstance.parameter_sets
        
        self.references = self.get_references()

        #for name, references in self.references.items():
        #    if name in references:
        #        raise SelfReference(
        #            u"Formula for parameter {} references itself".format(name)
        #        )

        self.order = self.get_order()



    def get_references(self):
        """Create dictionary of parameter references"""
        refs = {key: get_symbols(value['function'])
                if value.get('function') else set()
                for key, value in self.params.items()}
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
                                      u"\n{}\nExisting references:\n{}").format(
                                      pformat(refs, indent=2),
                                      pformat(sorted(order), indent=2)
                ))

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
            
            for key in self.order:
                
                if key in self.global_params:
                    if key not in ps.keys():
                        ps[key] = self.global_params[key]['default']

                    aeval.symtable[key] = this_ps[key] = ps[key]
                    
                elif self.params[key].get('function'):
                    value = aeval(self.params[key]['function'])
                    aeval.symtable[key] = this_ps[key] = value
                    
                else:
                    if key not in ps.keys():
                        ps[key] = 0
                    aeval.symtable[key] = this_ps[key] = ps[key]
                    
            
            evaluated_parameter_sets[ps_name]=this_ps
            
        #print(evaluated_parameter_sets)
        
        self.modelInstance.evaluated_parameter_sets = evaluated_parameter_sets
        
        return(evaluated_parameter_sets)