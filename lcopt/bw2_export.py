from lcopt.io import exchange_factory
from copy import deepcopy

class Bw2Exporter():
    
    def __init__(self, modelInstance):
        self.modelInstance = modelInstance
        
    def export_to_bw2(self):
        
        db = self.modelInstance.database['items']
        name = self.modelInstance.database['name']

        altbw2database = deepcopy(db)

        products = list(filter(lambda x: altbw2database[x]['type']=='product', altbw2database))
        processes = list(filter(lambda x: altbw2database[x]['type']=='process', altbw2database))


        for p in products:
            product = altbw2database[p]
            product['type'] = 'process'
            new_exchanges = [x for x in product['exchanges'] if x['type']!='production']
            product['exchanges']=new_exchanges

            #add external links
            if 'ext_link' in product.keys():
                product['exchanges'].append(exchange_factory(product['ext_link'], 'technosphere', 1, 1, 'external link to {}'.format(product['ext_link'][0])))

        for p in processes:
            process = altbw2database[p]
            for e in process['exchanges']:
                if e['type'] == 'production':
                    e['type'] = 'technosphere'
                    
        return name, altbw2database