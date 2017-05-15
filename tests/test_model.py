from brightway2 import *
from lcopt import *

model = LcoptModel('testModel')

def test_createModel():
	
	assert isinstance(model, LcoptModel)
	assert model.name == 'testModel'


def test_rename():
	model.rename('new_name')
	assert model.name == 'new_name'

def test_create_process():
    
    name = 'test_process'
    unit = 'kilogram'
    output_name  = 'test_output'
    exchanges = [{'name':output_name, 'type':'production', 'unit':unit, 'lcopt_type':'intermediate'}]
    location ='GLO'
    model.create_process(name, exchanges, location, unit)
    
    assert len(model.database['items'])==2

'''
def test_load():
	assert 1

def test_add_parameter():
	model.add_parameter()

def test_analyse():
	assert 1

def test_create_parameter_set():
	assert 1

def test_create_parameter_set_flask():
	assert 1

def test_create_process():
	assert 1

def test_create_product():
	assert 1

def test_database_to_SimaPro_csv():
	assert 1

def test_export_to_bw2():
	assert 1

def test_generate_matrices():
	assert 1

def test_generate_parameter_set_excel_file():
	assert 1

def test_import_external_db():
	assert 1

def test_launch_interact():
	assert 1

def test_list_parameters_as_df():
	assert 1

def test_load():
	assert 1

def test_matrix_as_df():
	assert 1

def test_parameter_scan():
	assert 1

def test_parse_function():
	assert 1



def test_save():
	assert 1

def test_search_databases():
	assert 1
'''