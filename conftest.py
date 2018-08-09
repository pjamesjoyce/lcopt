import pytest
import os
import brightway2 as bw2
from lcopt.data_store import storage
import yaml
from copy import deepcopy

from lcopt.constants import DEFAULT_BIOSPHERE_PROJECT
from lcopt.utils import bw2_project_exists

TEST_MODEL_NAME = "Test_model"

#print(storage.config_file)

#with open(storage.config_file, 'r') as f:
#    ORIGINAL_CONFIG = yaml.load(f)

#print(ORIGINAL_CONFIG)

ORIGINAL_CONFIG = deepcopy(storage.config)

FULL_SETUP = True

@pytest.fixture(scope="session", autouse=True)
def setup_fixtures(request):

    print('RUNNING SETUP FIXTURE')
    
    storage.config['ecoinvent']['version'] = '3.3'
    storage.config['ecoinvent']['system_model'] = 'cutoff'
    storage.config['model_storage']['project'] = 'unique'
    storage.config['model_storage']['location'] = 'currdir'



    if FULL_SETUP:
        bw2.projects.purge_deleted_directories()
        if TEST_MODEL_NAME in bw2.projects:
            bw2.projects.delete_project(name=TEST_MODEL_NAME, delete_dir=True)

        if bw2_project_exists(DEFAULT_BIOSPHERE_PROJECT):
            bw2.projects.set_current(DEFAULT_BIOSPHERE_PROJECT)
            bw2.projects.copy_project(TEST_MODEL_NAME, switch=True)
        else:
            bw2.projects.set_current(TEST_MODEL_NAME)
            bw2.bw2setup()
        

        script_path = os.path.dirname(os.path.realpath(__file__))
        ecospold_folder = os.path.join("tests", "assets", "datasets")
        ecospold_path = os.path.join(script_path, ecospold_folder)
        print(ecospold_path)

        ei = bw2.SingleOutputEcospold2Importer(ecospold_path, "Ecoinvent3_3_cutoff")
        ei.apply_strategies()
        ei.statistics()
        ei.write_database()

        bw2.projects.set_current('default')
    
    def teardown_fixtures():
        print('TEAR IT DOWN!!')

        print('cleaning up brightway')

        bw2.projects.set_current('default')
        
        if TEST_MODEL_NAME in bw2.projects:
            bw2.projects.delete_project(name=TEST_MODEL_NAME)#, delete_dir=True)
            #bw2.projects.purge_deleted_directories()


        print('rewriting original config')

        storage.write_config(ORIGINAL_CONFIG)

        assert storage.config == ORIGINAL_CONFIG
    
    request.addfinalizer(teardown_fixtures)




