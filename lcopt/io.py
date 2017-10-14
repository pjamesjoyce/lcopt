"""
IO module
"""

import hashlib

defaultDatabase = {
    'name': 'DefaultDatabase',
    'items': {}
}


# add an item to a specified database
def add_to_specified_database(item, database):
    """ add an item to a database"""
    database['items'][(database['name'], item['code'])] = item


# get an item from the database in the exchange format
def get_exchange_from_database(name, database):
    for key in database['items'].keys():
        item = database['items'][key]
        if item['name'] == name:
            return (database.get('name'), item.get('code'))
    return False


# check if something already exists
def exists_in_specific_database(code, database):
    for key in database['items'].keys():
        item = database['items'][key]
        if item['code'] == code:
            return True
    return False


# get an item from the database in the exchange format
def get_exchange_name_from_database(code, database):
    #print(database['name'])
    for key in database['items'].keys():
        item = database['items'][key]
        if item['code'] == code:
            return item.get('name')
    return None


# get an item from the database in the exchange format
def get_exchange_unit_from_database(code, database):
    for key in database['items'].keys():
        item = database['items'][key]
        if item['code'] == code:
            return item.get('unit')
    return None


# Create an exchange data structure
def exchange_factory(input, type, amount, uncertainty, comment, **kwargs):
    data_structure = {
        'input': input,
        'type': type,
        'amount': amount,
        'uncertainty type': uncertainty,
        'comment': comment,
    }

    for kw in kwargs:
        data_structure[kw] = kwargs[kw]
        
    return data_structure


# Create an item data structure
def item_factory(name, type, unit='kg', exchanges=None, location='GLO', categories=None, **kwargs):

    if exchanges is None:
        exchanges = []

    if categories is None:
        categories = []
        
    to_hash = name + type + unit + location
    code = hashlib.md5(to_hash.encode('utf-8')).hexdigest()
    data_structure = {
        'name': name,
        'code': code,
        'type': type,
        'categories': categories,
        'location': location,
        'unit': unit,
        'exchanges': exchanges
    }

    for kw in kwargs:
        data_structure[kw] = kwargs[kw]

    return data_structure
