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
DEFAULT_ECOINVENT_VERSION = '3.3'
DEFAULT_ECOINVENT_SYSTEM_MODEL = 'cutoff'
DEFAULT_SAVE_OPTION = 'appdir'
DEFAULT_PROJECT_TYPE = 'unique'
LEGACY_SAVE_OPTION = 'curdir'

DEFAULT_CONFIG = {
    'ecoinvent':{
        'version': DEFAULT_ECOINVENT_VERSION,
        'system_model': DEFAULT_ECOINVENT_SYSTEM_MODEL,
    },
    'model_storage': {
        'location': DEFAULT_SAVE_OPTION,
        'project': DEFAULT_PROJECT_TYPE,
        },
    }