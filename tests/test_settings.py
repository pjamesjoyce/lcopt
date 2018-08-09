import pytest
from lcopt.data_store import storage
from lcopt.settings import settings




def test_load_settings():

	print(settings)
	print(settings.ecoinvent)
	settings.write()

	assert list(settings.config.keys()) == list(storage.config.keys())

	for section, content in settings.config.items():
		for k, v in content.items():
			assert str(v) == str(storage.config[section][k])

def test_change_existing_string():
	expected = '3.3'
	settings.ecoinvent.version = '3.3'
	assert settings.ecoinvent.version == expected
	assert storage.config['ecoinvent']['version'] == expected

def test_change_existing_float():
	expected = '3.3'
	settings.ecoinvent.version = 3.3
	assert settings.as_dict()['ecoinvent']['version'] == expected
	assert storage.config['ecoinvent']['version'] == expected

def test_add_and_delete_new():
	expected = 'bar'
	settings.model_storage.foo = 'bar'
	assert settings.model_storage.foo == expected
	assert storage.config['model_storage']['foo'] == expected	

	settings.model_storage.delete('foo')

	assert settings.as_dict()['model_storage'].get('foo') is None
	assert  storage.config['model_storage'].get('foo') is None

def test_delete_nonexistant():
	with pytest.raises(AttributeError) as excinfo:
		settings.ecoinvent.delete('non_existent_attribute')
	assert 'does not exist' in str(excinfo.value)

def test_disallowed_type():
	def f():
		pass
	with pytest.raises(TypeError):
		settings.ecoinvent.some_function = f