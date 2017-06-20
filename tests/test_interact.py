import hashlib
from fixtures import *
import json


def test_app(app):
    assert repr(app)


def test_client(flask_client):
    assert repr(flask_client)


def test_index(flask_client):
    rv = flask_client.get('/')
    assert rv.status_code == 200


def test_blank_launch(blank_flask_client):
    rv = blank_flask_client.get('/')
    assert rv.status_code == 200


def test_status(flask_client):
    rv = flask_client.get('/status.json')
    assert rv.status_code == 200


def test_parameters_json(flask_client):
    rv = flask_client.get('/parameters.json')
    assert rv.status_code == 200


def test_inputs(flask_client):
    rv = flask_client.get('/inputs.json')
    assert rv.status_code == 200


def test_biosphere(flask_client):
    rv = flask_client.get('/biosphere.json')
    assert rv.status_code == 200


def test_functions(flask_client):
    rv = flask_client.get('/functions')
    assert rv.status_code == 200


def test_parameters(flask_client):
    rv = flask_client.get('/parameters')
    assert rv.status_code == 200


def test_settings(flask_client):
    rv = flask_client.get('/settings')
    assert rv.status_code == 200


def test_methods(flask_client):
    rv = flask_client.get('/methods.json')
    assert rv.status_code == 200


def test_post(flask_client):
    response = flask_client.post('/process_post', data=dict(action='echo'))
    assert b'Hello from echo' in response.data


def test_model_updates(flask_client, fully_formed_model):
    items_0 = [v['name'] for k,v in fully_formed_model.database['items'].items()]
    
    process_name = NEW_PROCESS_NAME
    unit = 'kilogram'
    output_name = NEW_OUTPUT_NAME

    to_hash = '{}process{}GLO'.format(process_name, unit)
    
    uuid = hashlib.md5(to_hash.encode('utf-8')).hexdigest()

    postData = dict(
            action = 'newProcess',
            uuid = uuid,
            process_name = process_name,
            unit = unit,
            output_name = output_name
        )

    response = flask_client.post('/process_post', data=postData)

    items_1 = [v['name'] for k, v in fully_formed_model.database['items'].items()]
        
    assert response.status_code == 200

    assert items_0 != items_1

    # test connections
    
    source_name = FINAL_PROCESS_NAME
    source = fully_formed_model.get_exchange(source_name)
    sourceId = source[1]
    target = fully_formed_model.get_exchange(process_name)
    targetId = target[1]
    label = 'test_label'

    target_prior = str(fully_formed_model.database['items'][target])
    
    postData = dict(
        action = 'newConnection',
        sourceId = sourceId,
        targetId = targetId,
        label = label,
        )

    response = flask_client.post('/process_post', data=postData)

    assert response.status_code == 200

    target_post = str(fully_formed_model.database['items'][target])

    assert target_prior != target_post


def test_move_item(flask_client, fully_formed_model):

    from random import randint

    item_name = EXISTING_PROCESS_NAME
    item = fully_formed_model.get_exchange(item_name)
    item_code = item[1]

    new_x = str(randint(0, 500))
    new_y = str(randint(0, 500))


    postData = dict(
        action = 'savePosition',
        uuid = item_code,
        y = new_y,
        x = new_x,
    );
   
    response = flask_client.post('/process_post', data=postData)
    assert response.status_code == 200

    assert fully_formed_model.sandbox_positions[item_code]['x'] == new_x
    assert fully_formed_model.sandbox_positions[item_code]['y'] == new_y


def test_add_unlinked_input(flask_client, fully_formed_model):
    
    target_name = EXISTING_PROCESS_NAME
    target = fully_formed_model.get_exchange(target_name)
    targetId = target[1]

    name = 'unlinked_input'
    type_ = 'product'
    unit = 'kilogram'
    location = 'GLO'
    to_hash = '{}{}{}{}'.format(name, type_, unit, location)
    code = hashlib.md5(to_hash.encode('utf-8')).hexdigest()

    postData = dict(
        action= 'addInput',
        targetId= targetId,
        name= name,
        type= type_,
        unit= unit,
        location= location,
        code=code,
        #ext_link_name = inputModal.getData(ext_link_name),
        #ext_link= inputModal.getData(code),
        lcopt_type= 'input'
    )

    response = flask_client.post('/process_post', data=postData)

    assert response.status_code == 200

    target_exchanges = fully_formed_model.database['items'][target]['exchanges']
    new_input = fully_formed_model.get_exchange(name)

    assert str(new_input) in str(target_exchanges)


def test_add_linked_input(flask_client, fully_formed_model):

    ext_link_name = ELECTRICITY_NAME
    ext_link_id = ELECTRICITY_ID

    target_name = EXISTING_PROCESS_NAME
    target = fully_formed_model.get_exchange(target_name)
    targetId = target[1]

    name = 'linked_input'
    type_ = 'product'
    unit = 'kilogram'
    location = 'GLO'
    to_hash = '{}{}{}{}'.format(name, type_, unit, location)
    code = hashlib.md5(to_hash.encode('utf-8')).hexdigest()

    postData = dict(
        action= 'addInput',
        targetId= targetId,
        name= name,
        type= type_,
        unit= unit,
        location= location,
        code=code,
        ext_link_name = ext_link_name,
        ext_link= ext_link_id,
        lcopt_type= 'input'
    )

    response = flask_client.post('/process_post', data = postData)

    assert response.status_code == 200

    target_exchanges = fully_formed_model.database['items'][target]['exchanges']
    new_input = fully_formed_model.get_exchange(name)

    assert str(new_input) in str(target_exchanges)

    assert fully_formed_model.database['items'][new_input]['ext_link'] != None

def test_add_biosphere_input(flask_client, fully_formed_model):

    ext_link_name = CO2_NAME
    ext_link_id = CO2_ID

    target_name = EXISTING_PROCESS_NAME
    target = fully_formed_model.get_exchange(target_name)
    targetId = target[1]

    name = 'linked_input'
    type_ = 'product'
    unit = 'kilogram'
    location = 'GLO'
    to_hash = '{}{}{}{}'.format(name, type_, unit, location)
    code = hashlib.md5(to_hash.encode('utf-8')).hexdigest()

    postData = dict(
        action= 'addInput',
        targetId= targetId,
        name= name,
        type= type_,
        unit= unit,
        location= location,
        code=code,
        ext_link_name = ext_link_name,
        ext_link= ext_link_id,
        lcopt_type= 'biosphere'
    )

    response = flask_client.post('/process_post', data = postData)

    assert response.status_code == 200

    target_exchanges = fully_formed_model.database['items'][target]['exchanges']
    new_input = fully_formed_model.get_exchange(name)

    assert str(new_input) in str(target_exchanges)

    assert fully_formed_model.database['items'][new_input]['ext_link'] != None

def test_inputLookup_technosphere_linked(flask_client, fully_formed_model):
    

    ext_link_name = ELECTRICITY_NAME
    ext_link_id = ELECTRICITY_ID

    target_name = EXISTING_PROCESS_NAME
    target = fully_formed_model.get_exchange(target_name)
    targetId = target[1]

    name = 'linked_input'
    type_ = 'product'
    unit = 'kilogram'
    location = 'GLO'
    to_hash = '{}{}{}{}'.format(name, type_, unit, location)
    code = hashlib.md5(to_hash.encode('utf-8')).hexdigest()

    postData = dict(
        action= 'addInput',
        targetId= targetId,
        name= name,
        type= type_,
        unit= unit,
        location= location,
        code=code,
        ext_link_name = ext_link_name,
        ext_link= ext_link_id,
        lcopt_type= 'input'
    )

    response = flask_client.post('/process_post', data = postData)

    assert response.status_code == 200

    new_input = fully_formed_model.get_exchange(name)

    postData ={
        'action': 'inputLookup',
        'code': new_input[1],
        'format' : 'ecoinvent',
    }

    response = flask_client.post('/process_post', data = postData)

    assert response.status_code == 200

def test_inputLookup_technosphere_unlinked(flask_client, fully_formed_model):
    
    target_name = EXISTING_PROCESS_NAME
    target = fully_formed_model.get_exchange(target_name)
    targetId = target[1]

    name = 'unlinked_input'
    type_ = 'product'
    unit = 'kilogram'
    location = 'GLO'
    to_hash = '{}{}{}{}'.format(name, type_, unit, location)
    code = hashlib.md5(to_hash.encode('utf-8')).hexdigest()

    postData = dict(
        action= 'addInput',
        targetId= targetId,
        name= name,
        type= type_,
        unit= unit,
        location= location,
        code=code,
        lcopt_type= 'input'
    )

    response = flask_client.post('/process_post', data = postData)

    assert response.status_code == 200

    new_input = fully_formed_model.get_exchange(name)

    postData ={
        'action': 'inputLookup',
        'code': new_input[1],
        'format' : 'ecoinvent',
    }

    response = flask_client.post('/process_post', data = postData)

    assert response.status_code == 200

def test_inputLookup_biosphere_input(flask_client, fully_formed_model):

    ext_link_name = CO2_NAME
    ext_link_id = CO2_ID

    target_name = EXISTING_PROCESS_NAME
    target = fully_formed_model.get_exchange(target_name)
    targetId = target[1]

    name = 'linked_input'
    type_ = 'product'
    unit = 'kilogram'
    location = 'GLO'
    to_hash = '{}{}{}{}'.format(name, type_, unit, location)
    code = hashlib.md5(to_hash.encode('utf-8')).hexdigest()

    postData = dict(
        action= 'addInput',
        targetId= targetId,
        name= name,
        type= type_,
        unit= unit,
        location= location,
        code=code,
        ext_link_name = ext_link_name,
        ext_link= ext_link_id,
        lcopt_type= 'biosphere'
    )

    response = flask_client.post('/process_post', data = postData)

    assert response.status_code == 200

    new_input = fully_formed_model.get_exchange(name)

    postData ={
        'action': 'inputLookup',
        'code': new_input[1],
        'format' : 'biosphere',
    }

    response = flask_client.post('/process_post', data = postData)

    assert response.status_code == 200

def test_searchEcoinvent(flask_client, fully_formed_model):
    
    search_term = 'electricity'
    location = 'DE'
    markets_only = 'True'

    postData = {
        'action': 'searchEcoinvent',
        'search_term': search_term,
        'location': location, 
        'markets_only': markets_only,
    }

    response = flask_client.post('/process_post', data = postData)

    assert response.status_code == 200

def test_searchBiosphere(flask_client, fully_formed_model):
    
    search_term = 'carbon dioxide, fossil'
    location = ''
    markets_only = ''

    postData = {
        'action': 'searchBiosphere',
        'search_term': search_term,
        'location': location, 
        'markets_only': markets_only,
    }

    response = flask_client.post('/process_post', data = postData)

    assert response.status_code == 200

def test_parameter_parsing(flask_client):

    postData = dict(
        action = 'parse_parameters',
        data = PARAMETER_DATA
        )
    response = flask_client.post('/process_post', data = postData)

    assert response.status_code == 200


def test_unlink_input(flask_client, fully_formed_model):
    
    targetId = fully_formed_model.get_exchange(EXISTING_PROCESS_NAME)[1]
    sourceId = "{}__0".format(fully_formed_model.get_exchange(EXISTING_INPUT_NAME)[1])
    postData = {
        'action': 'removeInput',
        'targetId': targetId,
        'sourceId': sourceId, 
    }

    response = flask_client.post('/process_post', data = postData)

    assert response.status_code == 200

def test_unlink_intermediate(flask_client, fully_formed_model):
    
    targetId = fully_formed_model.get_exchange(EXISTING_PROCESS_NAME)[1]
    sourceId = fully_formed_model.get_exchange(EXISTING_PROCESS_NAME_2)[1]
    postData = {
        'action': 'unlinkIntermediate',
        'targetId': targetId,
        'sourceId': sourceId, 
    }

    response = flask_client.post('/process_post', data = postData)

    assert response.status_code == 200


def test_analyse(flask_client, fully_formed_model):
    root_url = '/analyse'
    item = FINAL_PROCESS_NAME.replace(" ", "%20")
    item_code = fully_formed_model.get_exchange(FINAL_PROCESS_NAME)[1]

    full_url = '{}?item={}&item_code={}'.format(root_url, item, item_code)

    rv = flask_client.get(full_url, follow_redirects=True)
    assert rv.status_code == 200

def test_analysis(flask_client, fully_formed_model):

    root_url = '/analysis'
    item = FINAL_PROCESS_NAME.replace(" ", "%20")
    item_code = fully_formed_model.get_exchange(FINAL_PROCESS_NAME)[1]

    full_url = '{}?item={}&item_code={}'.format(root_url, item, item_code)

    rv = flask_client.get(full_url, follow_redirects=True)
    assert rv.status_code == 200
    assert fully_formed_model.result_set

    rv = flask_client.get('/testing', follow_redirects=True)
    assert rv.status_code == 200

def test_alter_methods(flask_client, fully_formed_model):
    
    method_list = [('ReCiPe Midpoint (H)', 'climate change', 'GWP100'),
                    ('ReCiPe Midpoint (H)', 'human toxicity', 'HTPinf'),
                    ('ReCiPe Midpoint (H)', 'particulate matter formation', 'PMFP')]

    method_json = json.dumps(method_list)

    postData = {
        'action' : 'update_settings',
        'settings_amount' : 1,
        'settings_methods' : method_json
    }

    response = flask_client.post('/process_post', data = postData)

    assert response.status_code == 200


def test_export_table(flask_client, fully_formed_model):

    root_url = '/analysis'
    item = FINAL_PROCESS_NAME.replace(" ", "%20")
    item_code = fully_formed_model.get_exchange(FINAL_PROCESS_NAME)[1]

    full_url = '{}?item={}&item_code={}'.format(root_url, item, item_code)

    rv = flask_client.get(full_url, follow_redirects=True)
    assert rv.status_code == 200
    assert fully_formed_model.result_set

    export_type = "summary"
    m = 0
    p = 0
    filename = "{}_summary_results.xlsx".format(fully_formed_model.name)

    fr = flask_client.get("/excel_export?type={}&ps={}&m={}".format(export_type, p, m))

    print(fr.headers['Content-Disposition'])

    assert filename in fr.headers['Content-Disposition'] 

    export_type = "method"
    filename = "{}_{}_results.xlsx".format(fully_formed_model.name, fully_formed_model.result_set['settings']['method_names'][m])

    fr = flask_client.get("/excel_export?type={}&ps={}&m={}".format(export_type, p, m))

    print(fr.headers['Content-Disposition'])

    assert filename in fr.headers['Content-Disposition'] 
