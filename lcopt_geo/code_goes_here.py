""" Outputs from the market manipulation module """

from .utils import get_dataset_by_id, get_dataset_by_code
from ocelot.transformations.utils import get_single_reference_product
import pandas as pd

def list_techno_inputs(id, data):
   
    ds = get_dataset_by_id(id, data)
    
    inputs = [i for i in ds['exchanges'] if i['type'] == "from technosphere"]
    print('There are {} inputs to the technosphere in {} {}'.format(len(inputs), ds['name'], ds['location']))

    to_df =[]

    if len(inputs) > 0:
        for e in inputs:
            a =  e['amount']
            u = e['unit']
            item = get_dataset_by_code(e['code'], data)
            ref_product = get_single_reference_product(item)
            pv = ref_product['production volume']['amount']
            to_df.append({'name': item['name'], 'location':item['location'], 'amount': "{0:.4f}".format(a), 'unit' : u, 'percentage': "{0:.2f}%".format(a*100)}) 
        df = pd.DataFrame(to_df)
        df.sort_values(['name','percentage'], ascending = False, inplace = True)
        
        cols = ['name', 'location', 'amount', 'unit', 'percentage']
        #print(df[cols])
    return df[cols]