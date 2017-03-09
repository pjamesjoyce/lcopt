from lcopt.bw2_export import Bw2Exporter

import brightway2 as bw2
import bw2analyzer

import matplotlib.pyplot as plt


import networkx as nx

from copy import deepcopy
from itertools import groupby

import json

plt.style.use('ggplot')
plt.rcParams['figure.figsize'] = (5, 5)

class Bw2Analysis():
    def __init__(self, modelInstance):
        self.modelInstance = modelInstance
        self.exporter = Bw2Exporter(modelInstance)
        
        self.bw2_database_name, self.bw2_database = self.exporter.export_to_bw2()
        
        self.bw2_project_name = self.modelInstance.name
        
    def setup_bw2(self):
        if self.bw2_project_name in bw2.projects:
            bw2.projects.set_current(self.bw2_project_name)
            print ('Switched to existing bw2 project - {}'.format(self.bw2_project_name))
            return True
            
        elif 'setup_TO_COPY' in bw2.projects:
            bw2.projects.set_current('setup_TO_COPY')
            bw2.projects.copy_project(self.bw2_project_name, switch = True)
            print ('Created new bw2 project - {}'.format(self.bw2_project_name))
            return True
        
        else:
            print ("bw2 project setup failed, please create the 'setup_TO_COPY' project in advance with the biosphere and necessary external databases (e.g. 'Ecoinvent_3_3_cutoff') ")
            return False
        
    def update_exchange_amounts(self, database, parameter_set):
        for i in database:

            for e in i.exchanges():

                if 'parameter_hook' in e.keys():
                    #print (i)
                    #print("\t {}".format(e))
                    #print("\t\t {}".format(e['parameter_hook']))
                    #print("\t\t {}".format(e.amount))
                    e['amount'] = parameter_set[e['parameter_hook']]
                    #print("\t\t {}".format(e.amount))
                    e.save()
        
    def run_analyses(self, demand_item, demand_item_code,  amount = 1, method = ('IPCC 2013', 'climate change', 'GWP 100a'), top_processes = 10, gt_cutoff = 0.01, pie_cutoff =0.05):
        
        ready = self.setup_bw2()
        name = self.bw2_database_name
        
        
        if ready:
            if name in bw2.databases:
                del bw2.databases[name]
                print ('Rewriting database ({}) ...'.format(name))
            else:
                print ('Writing database ({})...'.format(name))
            new_db = bw2.Database(name)
            
            new_db.write(self.bw2_database)
            new_db.process()
            
            def get_product(search_term):
                my_results = new_db.search(search_term)
                if len(my_results) == 0:
                    print('No item found to analyse called {}... aborting'.format(search_term))
                    return False
                elif len(my_results) > 1:
                    print('Multiple items found containing {}'.format(search_term))
                    print (my_results)
                    print ()
                    print('Going with the first one in the list - {}'.format(my_results[0]))
                    print ()
                    return my_results[0]
                else:
                    return my_results[0]
            
            #get the product to assess
            #product_demand = get_product(demand_item)
            #try this with get
            print ('trying to get {}'.format(demand_item_code))
            product_demand = new_db.get(demand_item_code)
            
            if product_demand != False:
                
                fu = {product_demand:amount}
                
                print('Running analysis for {} {} of {}, using {}'.format(amount, product_demand['unit'], product_demand, method))

                result_sets = []
                parameter_sets = self.modelInstance.evaluated_parameter_sets

                #for each parameter set in the model run the analysis

                for n, (parameter_set_name, parameter_set) in enumerate(parameter_sets.items()):
                    
                    result_set = {}
                    
                    # update the parameter_set values
                    print ('\nAnalysis {}\n'.format(n+1))
                    
                    self.update_exchange_amounts(new_db, parameter_set)
                    
                    # run the LCA
                    lca = bw2.LCA(fu, method)
                    lca.lci()
                    lca.lcia()
                    
                    result_set['lca']=lca
                    
                    # run the contribution analysis
                    ca = bw2analyzer.ContributionAnalysis().annotated_top_processes(lca)
                    result_set['contributionAnalysis'] = ca
                    
                    # create the contribution pie chart
                    
                    # this deals with low scores - if the total is less than one, the pie chart treats them as %
                    scalar = 1
                    if lca.score < 1:
                        scalar = 1/lca.score
                        #print (scalar)
                        
                    topprocesses = [ca[n][0]*scalar for n, x in enumerate(ca) if n<=top_processes]
                    topprocesses_names = [ca[n][2] for n, x in enumerate(ca) if n<=top_processes]
                    covered = sum(topprocesses)/scalar
                    #print(covered)
                    remainder = lca.score - covered
                    topprocesses.append(remainder*scalar)
                    topprocesses_names.append('remaining processes')
                    
                    """
                    # Not bothering with the plots - better to recreate them from the data in d3
                    fig1, ax1 = plt.subplots()
                    ax1.pie(topprocesses, labels=topprocesses_names, autopct = '%1.1f%%', startangle=90)
                    
                    ax1.axis('equal')
                    
                    result_set['pie_chart'] = fig1
                    """

                    max_processes = 4
            
                
                    pie_data = [{'label':x[2], 'value': x[0], 'percent_label' : "{:.1f}%".format(x[0]/lca.score*100)} for x in ca if x[0]/lca.score >=pie_cutoff]
                    pie_coverage = sum([x[0] for x in ca if x[0]/lca.score >=pie_cutoff ])
                    pie_remainder = lca.score - pie_coverage
                    pie_data.append({'label':'remaining processes', 'value':pie_remainder, 'percent_label' : "{:.1f}%".format(pie_remainder/lca.score*100) })
                    result_set['pie_data'] = pie_data
                    print (pie_data)
                    
                    # Graph traversal

                    gt = bw2.GraphTraversal()
                    gt_result = gt.calculate(fu ,method, cutoff=gt_cutoff)

                    edges = gt_result['edges']
                    nodes = gt_result['nodes']
                    G = nx.DiGraph()

                    def get_node_data(node, model, lca):
                        activities, products, biosphere = lca.reverse_dict()

                        if node == -1:
                            return {'name':'Final demand'}
                        else:
                            db_id = activities[node]
                            try:
                                data = model.external_databases[0]['items'][db_id]
                            except:
                                data = model.database['items'][db_id]
                        return data

                    node_constructor = []
                    for node_key, node_data in nodes.items():

                        node_data_copy = deepcopy(node_data)
                        node_data_copy.update(get_node_data(node_key, self.modelInstance, lca))

                        node_constructor.append((node_key, node_data_copy))

                    non_eco = [x for x in node_constructor if 'database' not in x[1].keys()]

                    G.add_nodes_from(non_eco)

                    edge_list = [(x['from'], x['to'],x) for x in edges]
                    non_eco_edges = [(x['from'], x['to'],x) for x in edges if x['from'] in G.nodes() and x['to'] in G.nodes()]

                    #G.add_edges_from(non_eco_edges)

                    #start_pos = {x[0]:[0.1,n/100] for n, x in enumerate(node_constructor)}
                    #start_pos[-1] = [0.5,0.5]
                    #fixed = {-1:[0.5,0.5]}

                    #pos = nx.spring_layout(G, pos = start_pos, fixed = fixed, weight = 'amount')

                    #labels = {x[0]:x[1]['name'] for x in G.nodes(data=True)}
                    #node_sizes = [(x[1]['cum']/lca.score)*300 for x in G.nodes(data=True)]


                    """
                    # Not bothering with the plots - better to recreate them from the data in d3
                    fig2, ax2 = plt.subplots()

                    ax2.axis('off')

                    nx.draw_networkx(G, pos, labels = labels, font_size=6, node_size=node_sizes, ax= ax2)

                    result_set['network'] = fig2
                    """
                    
                    result_set['full_nodes'] = node_constructor
                    result_set['model_nodes'] = non_eco
                    result_set['full_edges'] = edge_list
                    result_set['model_edges'] = non_eco_edges
                    
                    # Split the multiply linked nodes and create the json files
                    
                    sorted_edges = sorted(non_eco_edges, key=lambda x: x[0])

                    nodes_to_duplicate = {}
                    new_edges = []

                    for key, group in groupby(sorted_edges, lambda x: x[0]):
                        lengroup = deepcopy(group)
                        length = sum(1 for x in lengroup)

                        if length==1:
                            for thing in group:
                                new_edges.append(thing)
                                #print('{} ({}) only links to one thing {} ({})'.format(key, key, thing[1], thing[1]))
                                #print()
                        else:
                            nodes_to_duplicate[key] = length

                            #print('{} ({})links to the following'.format(key, key))
                            for n, thing in enumerate(group):
                                #print ("\t{} ({})" .format(thing[1], thing[1]))
                                new_thing = ("{}__{}".format(thing[0], n),thing[1], thing[2])
                                new_edges.append(new_thing)
                                #print(new_edges)
                            #print (" ")
                    new_nodes = []

                    for n in non_eco:
                        if n[0] in nodes_to_duplicate.keys():
                            #print('{} is duplicated {} times'.format(n[0], nodes_to_duplicate[n[0]]))
                            for i in range(nodes_to_duplicate[n[0]]):
                                new_nodes.append(('{}__{}'.format(n[0], i), n[1]))
                                #print ('{}__{}'.format(n[0], i))
                        else:
                            new_nodes.append(n)
                            
                    node_names = {}

                    for i, n in enumerate(new_nodes):
                        node_names[n[1]['name']] = i
                    
                    
                    #G2 = nx.DiGraph()
                    
                    #G2.add_nodes_from(new_nodes)
                    #G2.add_edges_from(new_edges)
                    
                    #start_pos2 = {x[0]:[0.1,n/100] for n, x in enumerate(new_nodes)}
                    #start_pos2[-1] = [0.5,0.5]
                    #fixed2 = {-1:[0.5,0.5]}

                    #pos2 = nx.spring_layout(G2, pos = start_pos2, fixed = fixed2, weight = 'amount')

                    #labels2 = {x[0]:x[1]['name'] for x in G2.nodes(data=True)}
                    #node_sizes2 = [(x[1]['cum']/lca.score)*300 for x in G2.nodes(data=True)]


                    #fig3, ax3 = plt.subplots()

                    #ax3.axis('off')

                    #nx.draw_networkx(G2, pos2, labels = labels2, font_size=6, node_size=node_sizes2, ax= ax3)

                    #result_set['network_split'] = fig3
                    
                    # Create the json string for the split network
                    
                    json_nodes = [{'id': x[0], 'data':x[1], 'group':node_names[x[1]['name']], 'radius' : x[1]['cum']/lca.score*10} for x in new_nodes]
                    json_links = [{"source": x[0], "target": x[1], "value": (x[2]['impact']/lca.score)*6} for x in new_edges]

                    to_json = {'nodes':json_nodes, 'links':json_links}

                    json_data = json.dumps(to_json)
                    
                    result_set['json'] = json_data
                    result_set['model_nodes_split'] = new_nodes
                    result_set['model_edges_split'] = new_edges
                    
                    # append the results to the dataset
                    
                    result_sets.append(result_set)
                    
                    
                
                print('Analysis complete, results have the following keys:')
                for k in result_sets[0].keys():
                    print ('\t{}'.format(k))
                    
                return result_sets
                    
            
            
        