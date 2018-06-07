def multi_recurse(d, max_levels=100):

    this_d = d

    for i in range(max_levels):
        prev_d = this_d
        this_d = recurse(prev_d)
        if this_d == prev_d:
            #print('breaking after {} levels'.format(i+1))
            break

    return this_d

def recurse(d):

    to_return = {}
    cum_impact = 0

    for k, v in d.items():
        if k == 'technosphere':
            #print('technosphere')
            for e in v:
                #print (e['activity'])
                cum_impact += e['impact']
                if 'cum_impact' in e.keys():
                    cum_impact += e['cum_impact']

                if k in to_return.keys():
                    to_return[k].append(recurse(e))
                else:
                    to_return[k] = [recurse(e)]
                    
        elif k == 'biosphere':
            to_return[k] = v
            if len(v) != 0:
                for b in v:
                    cum_impact += b['impact']
                    
        elif k == 'activity':
            #print (k,v)
            to_return[k] = str(v)
        #elif k == 'impact':
        #   print('impact of {} = {}'.format(d['activity'], v))

        else:
            to_return[k] = v
    #print('cum_impact of {} = {}'.format(d['activity'], cum_impact))
    to_return['cum_impact'] = cum_impact
        
    return to_return

def drop_level_recurse(d):

    to_return = {}
    
    if d['tag'] == 'intermediate':
        #print('this needs to be dropped')
        #print ('Dropping {}'.format(d['activity']))
        for key in d.keys():
            if key != 'technosphere':
                if key == 'activity':
                    d[key] = str(d['technosphere'][0][key])
                #print(key, d[key], d['technosphere'][0][key])
                d[key] = d['technosphere'][0][key]
        if 'technosphere' in d['technosphere'][0].keys():
            d['technosphere'] = d['technosphere'][0]['technosphere']

    for k, v in d.items():
        #print (k)
        if k == 'technosphere':
            #print('technosphere')
            for e in v:
                
                if k in to_return.keys():
                    to_return[k].append(drop_level_recurse(e))
                else:
                    to_return[k] = [drop_level_recurse(e)]

        elif k == 'activity':
            #print (k,v)
            to_return[k] = str(v)

        else:
            to_return[k] = v
        
    return to_return