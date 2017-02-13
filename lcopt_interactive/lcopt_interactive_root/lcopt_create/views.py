from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from brightway2 import *
from . import models as m
import hashlib

# TODO: Make this user changeable
projects.set_current('bw2_lcopt_default')
# bw2setup() #only needed on the first run 
# NOTE: Ecoinvent3_3_cutoff database has been preinstalled into the bw2_lcopt_default project

# Create your views here.

def lcopt_bw2(request):
    args={}
    args['bw2project'] = projects.current
    args['bw2databases'] = list(databases)
    args['bw2methods'] = methods

    ecoinvent = Database('Ecoinvent3_3_cutoff')
    fu = {ecoinvent.random():1}
    m = ('IPCC 2013', 'climate change', 'GWP 100a')

    lca = LCA(fu, m)
    lca.lci(factorize=True)
    lca.lcia()

    print(lca.demand)
    print(lca.score)

    args['bw2demand'] = lca.demand
    args['bw2score'] = lca.score


    return render(request, 'bw2.html', args)


def sandbox_main(request, model_id):

    args={}
    model = m.LcoptModel.objects.get(id=model_id)

    args['model'] = model
    args['model_id'] = model_id

    nodes = []
    links = []

    args['nodes'] = nodes
    args['links'] = links

    return render(request, 'sandbox.html', args)

def save_position(uuid,x,y):
    values = {'uuid':uuid, 'x':x, 'y':y}

    print (uuid, x, y)

    obj, created = m.SandboxPositions.objects.update_or_create(uuid=uuid, defaults=values)

    return created

def sandbox_new_item(request):

    print ('CALLED: sandbox_new_item')
    name = request.POST.get("name","default")
    type = request.POST.get("type","process")
    
    categories = []
    location = "GLO"
    unit = request.POST.get("unit","kg")
    model_id = request.POST.get("model_id",1)

    to_hash = name + type + unit + location
    temp_code = hashlib.md5(to_hash.encode('utf-8')).hexdigest()

    code = request.POST.get("code",temp_code)
    x = request.POST.get("x",50)
    y = request.POST.get("y",50)

    
    save_position(code,x,y)

    print (type)

    if type == 'input':

        #TODO: This
        #emission_factor = 0
        #thisItem = m.FlowInputSubstance(name = name, unit = unit, emission_factor = emission_factor)
        #thisItem.save()

        print ('saved an ' + type)

    elif type == 'output':
        #TODO: This
        #emission_factor = 0
        #thisItem = m.FlowOutputSubstance(name = name, unit = unit, emission_factor = emission_factor)
        #thisItem.save()

        print ('saved an ' + type)

    elif type == 'transformation':
        thisItem = m.FlowTechnosphere(name = name, unit = unit)
        thisItem.save()

        print ('saved a ' + type)

    elif type == 'process':
        model = m.LcoptModel.objects.get(id=model_id)
        model_db = "lcopt_model_{}".format(model_id)
        bw2_id = "({},{})".format(model_db, code)
        thisItem = m.LcoptProcess(name = name, unit = unit, category = 'Uncategorized', belongsTo =  model, code = code, bw2_id = bw2_id)
        thisItem.save()

        print ('saved a ' + type)

    response_data = {'code':thisItem.code}

    return JsonResponse(response_data)
