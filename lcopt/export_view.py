import pickle


class LcoptView(object):
    def __init__(self, modelInstance):
        
        self.modelInstance = modelInstance 

        self.view_data = {}

        attributes = ['name',
                      'database',
                      'params',
                      'ext_params',
                      'names',
                      'parameter_sets',
                      'external_databases',
                      'parameter_map',
                      'sandbox_positions',
                      'ecoinventName',
                      'biosphereName',
                      'analysis_settings',
                      'technosphere_databases',
                      'biosphere_databases',
                      'result_set',
                      'evaluated_parameter_sets'
                      ]

        for attr in attributes:
            if hasattr(self.modelInstance, attr):
                self.view_data[attr] = getattr(self.modelInstance, attr)

        if hasattr(self.modelInstance, 'matrix'):
            self.view_data['matrix'] = getattr(self.modelInstance, 'matrix').tolist()

    def export(self, filename=None):
        if filename is None:
            filename = self.modelInstance.name.replace(" ", "_")

        if filename[-10:] != '.lcoptview':
            filename += '.lcoptview'

        pickle.dump(self.view_data, open(filename, "wb"))
