def recurse_mass(d, allow_no_mass = False, checkSecondary = True):

    to_return = {}
    #cum_impact = 0
    isBiosphere = d['tag'] == 'biosphere'

    if not isBiosphere and checkSecondary:
        isBiosphere = 'biosphere' in d['secondary_tags']
    
    for k, v in d.items():
        if k == 'amount' and isBiosphere:
            #print (k, -v)
            to_return[k] = -v
            
        elif k == 'technosphere':
            #print('technosphere')
            #print(len(to_return), d['activity'], d['activity']['unit'])
            if d['activity']['unit'] in ['kg', 'g'] or allow_no_mass:
                for e in v:
                    #print (e['activity'])
                    #cum_impact += e['impact']
                    #if 'cum_impact' in e.keys():
                    #    cum_impact += e['cum_impact']

                    if k in to_return.keys():
                        to_return[k].append(recurse_mass(e, False))
                    else:
                        to_return[k] = [recurse_mass(e, False)]

        elif k in['biosphere', 'impact']:
            pass

        elif k == 'activity':
            #print (k,v)
            #activity_list = v.split('(')
            activity = v['name'] # activity_list[0].strip()
            unit = v['unit'] # activity_list[1].split(',')[0]
            #print(activity, unit)
            to_return['activity'] = str(activity)
            to_return['unit'] = unit
            if unit in ['kg', 'g'] or allow_no_mass:
                to_return['is_mass'] = True
            else:
                to_return['is_mass'] = False
            
        #elif k == 'impact':
        #   print('impact of {} = {}'.format(d['activity'], v))

        else:
            to_return[k] = v
    #print('cum_impact of {} = {}'.format(d['activity'], cum_impact))
    #to_return['cum_impact'] = cum_impact

    return to_return
