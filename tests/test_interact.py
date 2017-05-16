from lcopt.interact import FlaskSandbox
import pytest
import hashlib
from fixtures import *

@pytest.fixture
def app(parameterised_model):
	sandbox = FlaskSandbox(parameterised_model)
	app = sandbox.create_app()
	return app

@pytest.fixture
def flask_client(app):
	app.config['TESTING'] = True
	return app.test_client()

def test_app(app):
	assert repr(app)

def test_client(flask_client):
	assert repr(flask_client)

def test_index(flask_client):
	rv = flask_client.get('/')
	assert rv.status_code == 200

def test_status(flask_client):
	rv = flask_client.get('/status.json')
	assert rv.status_code == 200

def test_parameters(flask_client):
	rv = flask_client.get('/parameters.json')
	assert rv.status_code == 200


def test_post(flask_client):
	response = flask_client.post('/process_post', data=dict(action='echo'))
	assert b'Hello from echo' in response.data

def test_model_updates(flask_client, parameterised_model):
	items_0 = [v['name'] for k,v in parameterised_model.database['items'].items()]
	
	process_name = 'test_process_3'
	unit = 'kilogram'
	output_name = 'test_output_3'

	to_hash = '{}process{}GLO'.format(process_name, unit)
	
	uuid = hashlib.md5(to_hash.encode('utf-8')).hexdigest()

	postData = dict(
			action = 'newProcess',
			uuid = uuid,
			process_name = process_name,
			unit = unit,
			output_name = output_name
		)

	response = flask_client.post('/process_post', data = postData)

	items_1 = [v['name'] for k,v in parameterised_model.database['items'].items()]
		
	assert response.status_code == 200

	assert items_0 != items_1

	# test connections
	
	source_name = 'test_process_2'
	source = parameterised_model.get_exchange(source_name)
	sourceId = source[1]
	target = parameterised_model.get_exchange(process_name)
	targetId = target[1]
	label = 'test_label'

	target_prior = str(parameterised_model.database['items'][target])
	
	postData = dict(
		action = 'newConnection',
		sourceId = sourceId,
		targetId = targetId,
		label = label,
		)

	response = flask_client.post('/process_post', data = postData)

	assert response.status_code == 200

	target_post = str(parameterised_model.database['items'][target])

	assert target_prior != target_post


def test_move_item(flask_client, parameterised_model):

	from random import randint

	item_name = 'test_process_1'
	item = parameterised_model.get_exchange(item_name)
	item_code = item[1]

	new_x = str(randint(0,500))
	new_y = str(randint(0,500))


	postData = dict(
		action = 'savePosition',
		uuid = item_code,
		y = new_y,
		x = new_x,
	);
   

	response = flask_client.post('/process_post', data = postData)
	assert response.status_code == 200

	assert parameterised_model.sandbox_positions[item_code]['x'] == new_x
	assert parameterised_model.sandbox_positions[item_code]['y'] == new_y


def test_add_unlinked_input(flask_client, parameterised_model):
	
	target_name = 'test_process_1'
	target = parameterised_model.get_exchange(target_name)
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

	response = flask_client.post('/process_post', data = postData)

	assert response.status_code == 200

	target_exchanges = parameterised_model.database['items'][target]['exchanges']
	new_input = parameterised_model.get_exchange(name)

	assert str(new_input) in str(target_exchanges)


def test_add_linked_input(flask_client, parameterised_model):

	ext_link_name = "market for electricity, medium voltage {DE} [kilowatt hour]"
	ext_link_id = "('Ecoinvent3_3_cutoff', '8a1ef516cc78d560d3a677357b366de2')"

	target_name = 'test_process_1'
	target = parameterised_model.get_exchange(target_name)
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

	target_exchanges = parameterised_model.database['items'][target]['exchanges']
	new_input = parameterised_model.get_exchange(name)

	assert str(new_input) in str(target_exchanges)

	assert parameterised_model.database['items'][new_input]['ext_link'] != None

def test_add_biosphere_input(flask_client, parameterised_model):

	ext_link_name = "Carbon dioxide, fossil (emission to air) [kilogram]"
	ext_link_id = "('biosphere3', '349b29d1-3e58-4c66-98b9-9d1a076efd2e')"

	target_name = 'test_process_1'
	target = parameterised_model.get_exchange(target_name)
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

	target_exchanges = parameterised_model.database['items'][target]['exchanges']
	new_input = parameterised_model.get_exchange(name)

	assert str(new_input) in str(target_exchanges)

	assert parameterised_model.database['items'][new_input]['ext_link'] != None

def test_inputLookup_technosphere_linked(flask_client, parameterised_model):
	

	ext_link_name = "market for electricity, medium voltage {DE} [kilowatt hour]"
	ext_link_id = "('Ecoinvent3_3_cutoff', '8a1ef516cc78d560d3a677357b366de2')"

	target_name = 'test_process_1'
	target = parameterised_model.get_exchange(target_name)
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

	new_input = parameterised_model.get_exchange(name)

	postData ={
		'action': 'inputLookup',
		'code': new_input[1],
		'format' : 'ecoinvent',
	}

	response = flask_client.post('/process_post', data = postData)

	assert response.status_code == 200

def test_inputLookup_technosphere_unlinked(flask_client, parameterised_model):
	
	target_name = 'test_process_1'
	target = parameterised_model.get_exchange(target_name)
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

	new_input = parameterised_model.get_exchange(name)

	postData ={
		'action': 'inputLookup',
		'code': new_input[1],
		'format' : 'ecoinvent',
	}

	response = flask_client.post('/process_post', data = postData)

	assert response.status_code == 200

def test_inputLookup_biosphere_input(flask_client, parameterised_model):

	ext_link_name = "Carbon dioxide, fossil (emission to air) [kilogram]"
	ext_link_id = "('biosphere3', '349b29d1-3e58-4c66-98b9-9d1a076efd2e')"

	target_name = 'test_process_1'
	target = parameterised_model.get_exchange(target_name)
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

	new_input = parameterised_model.get_exchange(name)

	postData ={
		'action': 'inputLookup',
		'code': new_input[1],
		'format' : 'biosphere',
	}

	response = flask_client.post('/process_post', data = postData)

	assert response.status_code == 200

def test_searchEcoinvent(flask_client, parameterised_model):
	
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

def test_searchBiosphere(flask_client, parameterised_model):
	
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
