from fixtures import *


def test_createModel(blank_model):
    
    assert isinstance(blank_model, LcoptModel)
    assert blank_model.name == MODEL_NAME


def test_createForwastModel(forwast_model):
    assert isinstance(forwast_model, LcoptModel)
    assert forwast_model.name == MODEL_NAME


def test_rename(blank_model):
    blank_model.rename('new_name')
    assert blank_model.name == 'new_name'


def test_create_process(blank_model):
    
    name = 'test_process'
    unit = 'kilogram'
    output_name = 'test_output'
    exchanges = [{'name': output_name, 'type': 'production', 'unit': unit, 'lcopt_type': 'intermediate'}]
    location = 'GLO'
    assert blank_model.create_process(name, exchanges, location, unit)


def test_createPopulatedModel(populated_model):

    assert isinstance(populated_model, LcoptModel)
    assert len(populated_model.database['items']) == 4


def test_parameter_scan(populated_model):
    assert populated_model.parameter_scan()


def test_get_exchange(populated_model):
    exc = populated_model.get_exchange('test_process_1')
    
    assert exc is not False


def test_dont_get_name(blank_model):
    exc = blank_model.get_name('blah')
    
    assert exc is None


def test_dont_get_unit(blank_model):
    exc = blank_model.get_unit('blah')
    
    assert exc is None


def test_existing_exchange(populated_model):
    look_for = populated_model.get_exchange('test_process_1')[1]
    exc = populated_model.exists_in_database(look_for)

    assert exc


def test_link_processes(populated_model):

    db = populated_model.database
    source = populated_model.get_exchange('test_process_1')

    source_exc = db['items'][source]['exchanges']
    
    source_output = [x['input'] for x in source_exc if x['type'] == 'production'][0]

    target = populated_model.get_exchange('test_process_2')

    assert len([x for x in db['items'][target]['exchanges'] if x['type'] == 'technosphere']) == 0

    new_exchange = {'amount': 1,
                    'comment': 'technosphere exchange of {}'.format('test'),
                    'input': source_output,
                    'type': 'technosphere',
                    'uncertainty type': 1}
    
    db['items'][target]['exchanges'].append(new_exchange)
    
    assert len([x for x in db['items'][target]['exchanges'] if x['type'] == 'technosphere']) > 0


def test_database_to_SimaPro_csv(linked_model):
    expected = "{}_database_export.csv".format(linked_model.name)
    observed = linked_model.database_to_SimaPro_csv()
    assert observed == expected


def test_generate_parameter_set_excel_file(linked_model):
    expected = "ParameterSet_{}_input_file.xlsx".format(linked_model.name) 
    observed = linked_model.generate_parameter_set_excel_file()
    assert observed == expected


def test_database_to_SimaPro_csv_ext_params(parameterised_model):
    expected = "{}_database_export.csv".format(parameterised_model.name)
    observed = parameterised_model.database_to_SimaPro_csv()
    assert observed == expected


def test_generate_parameter_set_excel_file_ext_params(parameterised_model):
    expected = "ParameterSet_{}_input_file.xlsx".format(parameterised_model.name) 
    observed = parameterised_model.generate_parameter_set_excel_file()
    assert observed == expected     


def test_database_to_SimaPro_csv_ff_model(fully_formed_model):
    expected = "{}_database_export.csv".format(fully_formed_model.name)
    observed = fully_formed_model.database_to_SimaPro_csv()
    assert observed == expected


def test_generate_parameter_set_excel_file_ff_model(fully_formed_model):
    expected = "ParameterSet_{}_input_file.xlsx".format(fully_formed_model.name) 
    observed = fully_formed_model.generate_parameter_set_excel_file()
    assert observed == expected     


def test_add_parameter(linked_model):
    assert len(linked_model.ext_params) == 0
    linked_model.add_parameter('test_parameter', description='test description', default=1)
    assert len(linked_model.ext_params) > 0


def test_add_undescribed_parameter(linked_model):
    assert len(linked_model.ext_params) == 0
    linked_model.add_parameter('test_parameter', default=1)
    assert len(linked_model.ext_params) > 0


def test_add_function(linked_model):
    assert len(linked_model.params) == 1
    param_ids = [x for x in linked_model.params]
    assert len(param_ids) == 1

    e_param_name = 'test_parameter'

    assert len(linked_model.ext_params) == 0
    linked_model.add_parameter(e_param_name, description='test description', default=1)
    assert len(linked_model.ext_params) > 0

    new_function = "{}*2".format(e_param_name)
    parameter = linked_model.params[param_ids[0]]
    parameter['function'] = new_function

    model_has_functions = len([x for k, x in linked_model.params.items() if x['function'] is not None]) != 0

    assert model_has_functions


def test_list_parameters_as_df(linked_model):

    from pandas import DataFrame
    df = linked_model.list_parameters_as_df()
    assert isinstance(df, DataFrame)


def test_list_parameters_as_df_with_external(parameterised_model):

    from pandas import DataFrame
    df = parameterised_model.list_parameters_as_df()
    assert isinstance(df, DataFrame)

#def test_save(linked_model):
#   import os.path
#   linked_model.save()
#   fname = '{}.lcopt'.format(MODEL_NAME)
#   
#   assert os.path.isfile(fname) 

#def test_load(linked_model):
#   expected = repr(linked_model.__dict__)
#   loaded_model = LcoptModel(load = MODEL_NAME)
#   observed = repr(loaded_model.__dict__)
#   assert observed == expected 


def test_search_all_databases(linked_model):

    results = linked_model.search_databases('electricity')
    
    assert len(results) > 0


def test_search_specific_database(linked_model):
    ecoinvent = linked_model.ecoinventName
    
    results = linked_model.search_databases('electricity', databases_to_search=[ecoinvent])
    
    assert len(results) > 0


def test_search_specific_database_markets(linked_model):
    ecoinvent = linked_model.ecoinventName
    
    results = linked_model.search_databases('electricity', markets_only=True, databases_to_search=[ecoinvent])
    
    assert len(results) > 0


def test_search_specific_database_location(linked_model):
    ecoinvent = linked_model.ecoinventName
    
    results = linked_model.search_databases('electricity', location='DE', markets_only=True, databases_to_search=[ecoinvent])
    
    assert len(results) > 0


def test_remove_input_link(fully_formed_model):
    
    input_code = fully_formed_model.get_exchange(EXISTING_INPUT_NAME)
    process_code = fully_formed_model.get_exchange(EXISTING_PROCESS_NAME)

    assert fully_formed_model.remove_input_link(process_code, input_code) == 1


def test_unlink_intermediate(fully_formed_model):

    sourceId = fully_formed_model.get_exchange(EXISTING_PROCESS_NAME)[1]
    targetId = fully_formed_model.get_exchange(EXISTING_PROCESS_NAME_2)[1]

    assert fully_formed_model.unlink_intermediate(sourceId, targetId)


def test_analyse(fully_formed_model):

    demand_item_name = FINAL_PROCESS_NAME
    demand_item_id = fully_formed_model.get_exchange(FINAL_PROCESS_NAME)[1]

    assert fully_formed_model.analyse(demand_item_name, demand_item_id)


def test_export_to_bw2(fully_formed_model):

    name, bw2db = fully_formed_model.export_to_bw2()
    
    assert len(bw2db) != 0
