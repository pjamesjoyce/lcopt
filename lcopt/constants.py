import os

DEFAULT_PROJECT_STEM = "LCOPT_Setup_"
DEFAULT_BIOSPHERE_PROJECT = "LCOPT_Setup_biosphere"
DEFAULT_SINGLE_PROJECT = "LCOPT_Models"
#DEFAULT_DB_NAME = "LCOPT_Setup"
DEFAULT_DB_NAME = DEFAULT_PROJECT_STEM[:-1]
FORWAST_PROJECT_NAME = DEFAULT_PROJECT_STEM + "Forwast"
FORWAST_URL = r"https://lca-net.com/wp-content/uploads/forwast.bw2package.zip"
ASSET_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'assets')
BIOSPHERE_SI = 'biosphere3.pickle'
FORWAST_SI = 'forwast.pickle'
ECOINVENT_EXAMPLE = 'ecoinvent_example.lcopt'
FORWAST_EXAMPLE = 'forwast_example.lcopt'
DEFAULT_CONFIG = {
    'ecoinvent':{
        'version':'3.3',
        'system_model': 'cutoff',
    }
    'model_storage': {
        'location': 'appdir',
        'project': 'unique',
        },
    }