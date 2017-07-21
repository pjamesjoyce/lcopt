import pytest
from lcopt import LcoptModel
from lcopt.interact import FlaskSandbox
from lcopt.utils import DEFAULT_DB_NAME
import os
import brightway2 as bw2

MODEL_NAME = 'modelName'

PARAMETER_DATA = '[{"id":"p_3_2","Name":"Tea leaves","Unit":"kg","Normal tea":"0.01","Black tea":"0.01"},{"id":"p_0_2","Name":"Boiling water","Unit":"l","Normal tea":"1","Black tea":"1"},{"id":"p_2_4","Name":"Black tea","Unit":"l","Normal tea":"0.8","Black tea":"0.8"},{"id":"kettle_power","Name":"Power rating of kettle, kW","Unit":"","Normal tea":"1.5","Black tea":"1.5"},{"id":"boil_time","Name":"Kettle boiling time, mins","Unit":"","Normal tea":"3","Black tea":"3"},{"id":"milk_density","Name":"Density of milk","Unit":"","Normal tea":"1.035","Black tea":"1.035"},{"id":"milk_amount","Name":"Amount of milk, l","Unit":"","Normal tea":"0.02","Black tea":"0"}]'

EXISTING_PROCESS_NAME = 'Process 1'
EXISTING_PROCESS_NAME_2 = 'Process 2'
FINAL_PROCESS_NAME = 'Process 3'
NEW_PROCESS_NAME = 'Process 4'
NEW_OUTPUT_NAME = 'Output 4'

EXISTING_INPUT_NAME = 'Input 2'

ELECTRICITY_NAME = "market for electricity, medium voltage {DE} [kilowatt hour]"
ELECTRICITY_ID = "('Ecoinvent3_3_cutoff', '8a1ef516cc78d560d3a677357b366de2')"

CO2_NAME = "Carbon dioxide, fossil (emission to air) [kilogram]"
CO2_ID = "('biosphere3', '349b29d1-3e58-4c66-98b9-9d1a076efd2e')"

TEST_MODEL_NAME = "Test_model"

FULL_MODEL_PATH = r"assets/{}".format(TEST_MODEL_NAME)

IS_TRAVIS = 'TRAVIS' in os.environ


@pytest.fixture
def blank_model():
    
    return LcoptModel(MODEL_NAME)


@pytest.fixture
def forwast_model():

    return LcoptModel(MODEL_NAME, useForwast=True)

@pytest.fixture
def populated_model(blank_model):

    model = blank_model

    name = 'test_process_1'
    unit = 'kilogram'
    output_name  = 'test_output_1'
    exchanges = [{'name':output_name, 'type':'production', 'unit':unit, 'lcopt_type':'intermediate'}]
    location ='GLO'

    model.create_process(name, exchanges, location, unit)

    name = 'test_process_2'
    unit = 'kilogram'
    output_name  = 'test_output_2'
    exchanges = [{'name':output_name, 'type':'production', 'unit':unit, 'lcopt_type':'intermediate'}]
    location ='GLO'

    model.create_process(name, exchanges, location, unit)

    return model


@pytest.fixture
def linked_model(populated_model):

    db = populated_model.database

    source = populated_model.get_exchange('test_process_1')

    source_exc = db['items'][source]['exchanges']
    
    source_output = [x['input'] for x in source_exc if x['type'] == 'production'][0]

    target = populated_model.get_exchange('test_process_2')

    new_exchange = {'amount': 1,
             'comment': 'technosphere exchange of {}'.format('test'),
             'input': source_output,
             'type': 'technosphere',
             'uncertainty type': 1}
    
    db['items'][target]['exchanges'].append(new_exchange)

    populated_model.parameter_scan()
    
    return populated_model

@pytest.fixture
def parameterised_model(linked_model):
    linked_model.add_parameter('test_parameter', description = 'test description', default = 1)
    param_ids = [x for x in linked_model.params]

    e_param_name = 'test_parameter'

    linked_model.add_parameter(e_param_name, description = 'test description', default = 1)

    new_function = "{}*2".format(e_param_name)
    parameter = linked_model.params[param_ids[0]]
    parameter['function'] = new_function

    return linked_model




@pytest.fixture
def fully_formed_model():
    
    script_path = os.path.dirname(os.path.realpath(__file__))
    loadpath = os.path.join(script_path, FULL_MODEL_PATH)
    return LcoptModel(load = loadpath)

@pytest.fixture
def blank_app(blank_model):
    sandbox = FlaskSandbox(blank_model)
    return sandbox.create_app()

@pytest.fixture
def blank_flask_client(blank_app):
    blank_app.config['TESTING'] = True
    return blank_app.test_client()

@pytest.fixture
def app(fully_formed_model):
    sandbox = FlaskSandbox(fully_formed_model)
    app = sandbox.create_app()
    return app

@pytest.fixture
def flask_client(app):
    app.config['TESTING'] = True
    return app.test_client()
