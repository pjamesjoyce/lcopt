from lcopt.bw2_export import Bw2Exporter
from lcopt.utils import DEFAULT_DB_NAME, FORWAST_DB_NAME
from .mass_balance import recurse_mass
from .multi_tagged import multi_traverse_tagged_databases, get_cum_impact, drop_pass_through_levels
import brightway2 as bw2
#from bw2analyzer.tagged import recurse_tagged_database, aggregate_tagged_graph
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

    
    def run_analyses(self, demand_item, demand_item_code, amount=1, methods=[('IPCC 2013', 'climate change', 'GWP 100a')], pie_cutoff=0.05, **kwargs):
        
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
                    
                    # Get overall scores for all methods
                    scores = []

                    for n, m in enumerate(methods):
                        if n == 0:
                            lca = bw2.LCA(fu, m)
                            lca.lci()
                            lca.lcia()
                        else:
                            lca.switch_method(m)
                            lca.redo_lcia(
                            )
                        scores.append(lca.score)

                    # method units at list
                    method_units = [bw2.methods[method]['unit'] for method in methods]

                    multi_foreground_result, multi_foreground_graph = multi_traverse_tagged_databases(fu, methods, label="name", default_tag="other", secondary_tags=[('lcopt_type', 'other')])

                    recursed_graph = get_cum_impact(deepcopy(multi_foreground_graph[0]))
                    dropped_graph = drop_pass_through_levels(deepcopy(multi_foreground_graph[0]))
                    mass_flow = recurse_mass(multi_foreground_graph[0], True)

                    result_set = {
                            'ps_name': parameter_set_name,
                            'methods': [str(method) for method in methods],
                            'units': method_units,
                            'scores': scores,
                            'foreground_results': multi_foreground_result,
                            'graph': recursed_graph,
                            'dropped_graph': dropped_graph,
                            'mass_flow': mass_flow
                        }

                    result_sets.append(result_set)

                result_dict['results'] = result_sets
                    
                return result_dict                                                
