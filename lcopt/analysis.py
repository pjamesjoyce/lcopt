from lcopt.bw2_export import Bw2Exporter
from lcopt.utils import DEFAULT_DB_NAME, FORWAST_DB_NAME
from lcopt.mass_balance import recurse_mass
import brightway2 as bw2
from bw2analyzer.tagged import recurse_tagged_database, aggregate_tagged_graph
#from .tagged_copy import recurse_tagged_database, aggregate_tagged_graph
from copy import deepcopy
import time
import datetime

from bw2data.parameters import DatabaseParameter, ActivityParameter

#import presamples as ps
#import numpy as np

class Bw2Analysis():
    def __init__(self, modelInstance):
        self.modelInstance = modelInstance
        self.exporter = Bw2Exporter(modelInstance)
        
        self.bw2_database_name, self.bw2_database = self.exporter.export_to_bw2()
        
        if self.modelInstance.useForwast:
            self.bw2_project_name = '{}_FORWAST'.format(self.modelInstance.name)
        else:
            self.bw2_project_name = self.modelInstance.name
        
    def setup_bw2(self):

        if self.bw2_project_name in bw2.projects:
            bw2.projects.set_current(self.bw2_project_name)
            print('Switched to existing bw2 project - {}'.format(self.bw2_project_name))
            return True

        else:
        
            if self.modelInstance.useForwast:
                if FORWAST_DB_NAME in bw2.projects:
                    bw2.projects.set_current(FORWAST_DB_NAME)
                    bw2.projects.copy_project(self.bw2_project_name, switch=True)
                    print('Created new bw2 project - {}'.format(self.bw2_project_name))
                    return True

            elif DEFAULT_DB_NAME in bw2.projects:                                       # pragma: no cover
                bw2.projects.set_current(DEFAULT_DB_NAME)
                bw2.projects.copy_project(self.bw2_project_name, switch=True)
                print('Created new bw2 project - {}'.format(self.bw2_project_name))
                return True
        
            else:                                                                       # pragma: no cover
                print ("bw2 project setup failed, please create the 'LCOPT_Setup' or 'LCOPT_Setup_Forwast' project in advance with the biosphere and necessary external databases (e.g. 'Ecoinvent_3_3_cutoff') ")
                print ("To do this, run lcopt_bw_setup in lcopt.utils")
                return False
        
    def update_exchange_amounts(self, database, parameter_set):
        for i in database:

            for e in i.exchanges():

                if 'formula' in e.keys():
                    e['amount'] = parameter_set[e['formula']]
                    e.save()

    def multi_recurse(self, d):
    
        max_levels = 100

        this_d = d

        for i in range(max_levels):
            prev_d = this_d
            this_d = self.recurse(prev_d)
            if this_d == prev_d:
                #print('breaking after {} levels'.format(i+1))
                break

        return this_d

    def recurse(self, d):

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
                        to_return[k].append(self.recurse(e))
                    else:
                        to_return[k] = [self.recurse(e)]
                        
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

    def drop_level_recurse(self, d):

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
                        to_return[k].append(self.drop_level_recurse(e))
                    else:
                        to_return[k] = [self.drop_level_recurse(e)]

            elif k == 'activity':
                #print (k,v)
                to_return[k] = str(v)

            else:
                to_return[k] = v
            
        return to_return
    
    def run_analyses(self, demand_item, demand_item_code, amount=1, methods=[('IPCC 2013', 'climate change', 'GWP 100a')], top_processes=10, gt_cutoff=0.01, pie_cutoff=0.05):
        
        ready = self.setup_bw2()
        name = self.bw2_database_name
        
        if ready:
            if name in bw2.databases:
                del bw2.databases[name]
                print ('Rewriting database ({}) ...'.format(name))
            else:
                print ('Writing database ({})...'.format(name))                         # pragma: no cover
            new_db = bw2.Database(name)
            
            new_db.write(self.bw2_database)
            new_db.process()

            # This is where the parameter bit goes
            bw2_parameters = self.modelInstance.bw2_export_params
            bw2.parameters.new_database_parameters(bw2_parameters, name)

            #Group.create(name="all")

            for a in new_db:
                for e in a.exchanges():
                    if e.get('formula'):
                        bw2.parameters.add_exchanges_to_group("all", a)
                        break                

            ActivityParameter.recalculate_exchanges("all")
            
            #print ('trying to get {}'.format(demand_item_code))
            product_demand = new_db.get(demand_item_code)
            
            if product_demand is not False:
                
                fu = {product_demand: amount}
                parameter_sets = self.modelInstance.evaluated_parameter_sets

                """# This was the attempted presamples bit - but presamples and recurse_tagged_dataases are incompatible
                p_names = []
                indices = []
                for k, v in self.modelInstance.parameter_map.items():
                    p_names.append(v)
                    indices.append((k[0], k[1], 'technosphere'))

                pset_names = self.modelInstance.evaluated_parameter_sets.keys()
                ps_list = [[self.modelInstance.evaluated_parameter_sets[k][x] for x in p_names] for k in pset_names]
                assert len(ps_list[0]) == len(indices)

                params_for_presamples = np.transpose(np.array(ps_list))

                presamples_matrix = [(
                    params_for_presamples,
                    indices,
                    'technosphere'
                )]

                ps_id, ps_fp = ps.create_presamples_package(
                    matrix_data=presamples_matrix,
                    name='presamples_test_psets',
                    seed = 'sequential',
                    overwrite=True
                )
"""
                ts = time.time()
                ts_format = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
               
                result_dict = {
                    'settings': {
                        'pie_cutoff': pie_cutoff,
                        'methods': [str(method) for method in methods],
                        'method_names': [', '.join(method[1:]) for method in methods],
                        'method_units': [bw2.methods[method]['unit'] for method in methods],
                        'item': demand_item,
                        'item_code': demand_item_code,
                        'amount': amount,
                        'ps_names': [name for name in parameter_sets.keys()],
                        'item_unit': product_demand['unit'],
                        'timestamp': ts_format,
                    }
                }
                result_sets = []
                
                #initial_method = methods[0]
                #lca = bw2.LCA(fu, initial_method, presamples=[ps_fp])
                #for each parameter set in the model run the analysis

                for n, (parameter_set_name, parameter_set) in enumerate(parameter_sets.items()):
                    
                    # update the parameter_set values
                    print ('\nAnalysis {}\n'.format(n + 1))
                    
                    self.update_exchange_amounts(new_db, parameter_set)
                    
                    initial_method = methods[0]
                    # run the LCA
                    lca = bw2.LCA(fu, initial_method)
                    lca.lci(factorize=True)
                    lca.lcia()
                    
                    ps_results = []

                    for j, method in enumerate(methods):
                        lca.switch_method(method)
                        lca.redo_lcia(fu)
                        unit = bw2.methods[method]['unit']
                        
                        """if n == 0 and j == 0:
                            #print('first run')
                            lca.lci()
                            lca.lcia()
                        else:
                            if n > 0 and j == 0:
                                print("switching to next presamples parameter set")
                                lca.presamples.update_matrices(lca)
                                lca.redo_lci()

                            lca.switch_method(method)
                            lca.redo_lcia()
                        """

                        score = lca.score
                        #print('Analysis for {} {} of {}, using {}'.format(amount, product_demand['unit'], product_demand['name'], method))
                        #print ('{:.3g} {}'.format(score, unit))
                        
                        method_dict = {o[0]: o[1] for o in bw2.Method(method).load()}
                        default_tag = "other"

                        label = "lcopt_type"
                        type_graph = [recurse_tagged_database(key, amount, method_dict, lca, label, default_tag)
                                      for key, amount in fu.items()]
                        # type_result = aggregate_tagged_graph(type_graph)
                        
                        # for k,v in type_result.items():
                        #    print('{}\t\t{}'.format(k,v))
                        
                        label = "name"
                        foreground_graph = [recurse_tagged_database(key, amount, method_dict, lca, label, default_tag)
                                            for key, amount in fu.items()]
                        foreground_result = aggregate_tagged_graph(foreground_graph)
                        
                        #for k,v in foreground_result.items():
                        #    print('{}\t\t{}'.format(k,v))
                            
                        recursed_graph = self.multi_recurse(deepcopy(type_graph[0]))
                        dropped_graph = self.drop_level_recurse(deepcopy(type_graph[0]))
                        
                        result_set = {
                            'ps_name': parameter_set_name,
                            'method': str(method),
                            'unit': unit,
                            'score': score,
                            'foreground_results': foreground_result,
                            'graph': recursed_graph,
                            'dropped_graph': dropped_graph,
                            'original_graph': str(type_graph[0]),
                            'mass_flow': recurse_mass(type_graph[0])
                        }
                        
                        ps_results.append(result_set)
                        
                    result_sets.append(ps_results)

                result_dict['results'] = result_sets
                    
                return result_dict                                                
