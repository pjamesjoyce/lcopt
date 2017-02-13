from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
import flowdata.views as v
import flowdata.models as m
import sandbox.models as sm
import uuid
import argparse as ap


# Create your views here.

def sandbox_main(request):

    args={}
    system_id = int(request.session['currentSystemID'])
    system = m.FlowSystem.objects.get(id=system_id)
    #processList, processNames, techOutputNames  = v.scantree(system_id)
    #args['processList']=processList
    #args['processNames'] = processNames
    #args['techOutputNames'] = techOutputNames
    #print processList, processNames, techOutputNames
    #args['dotString'] = v.getDotString(processList, system_id)

    allInputs = m.FlowInputSubstance.objects.all()
    allOutputs = m.FlowOutputSubstance.objects.all()
    allIntermediates = m.FlowTechnosphere.objects.all()

    args['allInputs'] = allInputs
    args['allOutputs'] = allOutputs
    args['allIntermediates'] = allIntermediates

    args['system'] = system
    args['system_id'] = system_id

    nodes, links = sandboxScan(system_id)

    args['nodes'] = nodes
    args['links'] = links

    can_edit_all = request.user.groups.filter(name='SuperEditors').exists()
    args['can_edit_all']=can_edit_all

    return render(request, 'sandbox.html', args)

def save_position(uuid,x,y):
    values = {'uuid':uuid, 'x':x, 'y':y}

    print uuid, x, y

    obj, created = sm.SandboxPositions.objects.update_or_create(uuid=uuid, defaults=values)

    return created

def save_input_membership(transform_id, input_id, amount, system_id, note, uuid):

    transformation = m.FlowTransformation.objects.get(uuid=transform_id)
    inputsubstance = m.FlowInputSubstance.objects.get(id=input_id)
    partOfSystem = m.FlowSystem.objects.get(id=system_id)

    values = {'transformation':transformation, 'inputsubstance':inputsubstance, 'amount_required':float(amount), 'partOfSystem':partOfSystem, 'note':note, 'uuid':uuid}

    obj, created = m.FlowInputMembership.objects.update_or_create(uuid=uuid, defaults=values)

def save_output_membership(transform_id, output_id, amount, system_id, note, uuid):

    transformation = m.FlowTransformation.objects.get(uuid=transform_id)
    #print transform_id
    outputsubstance = m.FlowOutputSubstance.objects.get(id=output_id)
    partOfSystem = m.FlowSystem.objects.get(id=system_id)

    values = {'transformation':transformation, 'outputsubstance':outputsubstance, 'amount_required':float(amount), 'partOfSystem':partOfSystem, 'note':note, 'uuid':uuid}
    #print values
    obj, created = m.FlowOutputMembership.objects.update_or_create(uuid=uuid, defaults=values)

    #return created


def sandbox_pos_update(request):
    tempuuid = uuid.uuid4()
    id = request.POST.get("uuid","168effce-c763-4169-acfe-185b19f89c9d")
    x = request.POST.get("x",290.00002670288086)
    y = request.POST.get("y",210)

    save_position(id,int(float(x)),int(float(y)))

    return HttpResponse("OK")

def sandbox_new_input(request):

    transform_id = request.POST.get("transform_id","")
    input_id = request.POST.get("input_id","")
    amount = request.POST.get("amount","")
    system_id = request.POST.get("system_id","")
    note = request.POST.get("note","")
    uuid = request.POST.get("uuid","")
    x = request.POST.get("x","")
    y = request.POST.get("y","")

    #print transform_id, input_id, amount, system_id, note, uuid, x, y
    save_input_membership(transform_id, input_id, amount, system_id, note, uuid)
    print uuid
    print int(float(x))
    print int(float(y))
    save_position(uuid,int(float(x)),int(float(y)))

    return HttpResponse("OK")


def sandbox_new_output(request):

    transform_id = request.POST.get("transform_id","")
    output_id = request.POST.get("output_id","")
    amount = request.POST.get("amount","")
    system_id = request.POST.get("system_id","")
    note = request.POST.get("note","")
    uuid = request.POST.get("uuid","")
    x = request.POST.get("x","")
    y = request.POST.get("y","")

    #print transform_id, input_id, amount, system_id, note, uuid, x, y
    save_output_membership(transform_id, output_id, amount, system_id, note, uuid)
    print uuid
    print int(float(x))
    print int(float(y))
    save_position(uuid,int(float(x)),int(float(y)))

    return HttpResponse("OK")


def sandbox_new_connection(request):
    sourceId = request.POST.get('sourceId','')
    targetId = request.POST.get('targetId','')
    intermediateId = request.POST.get('intermediateId','')
    amount_required = request.POST.get('amount_required','')
    system_id = request.POST.get('system_id','')
    input_uuid = request.POST.get('input_uuid','')
    output_uuid = request.POST.get('output_uuid','')

    source = m.FlowTransformation.objects.get(uuid = sourceId)
    target = m.FlowTransformation.objects.get(uuid = targetId)
    system = m.FlowSystem.objects.get(id = system_id)
    intermediate = m.FlowTechnosphere.objects.get(id = intermediateId)

    # create the output side of the connection
    newOutput = m.FlowTechnosphereMembershipOutput(transformation = source, techFlow = intermediate, amount_required = amount_required, partOfSystem = system, note=' ', uuid = input_uuid)
    newOutput.save()
    # create the input side of the connection
    newInput = m.FlowTechnosphereMembershipInput(transformation = target, techFlow = intermediate, amount_required = amount_required, partOfSystem = system, note=' ', uuid = output_uuid)
    newInput.save()

    return HttpResponse("OK")

def sandbox_compute_link(request):

    mySource = request.POST.get("source","918dfcda-1e7c-4d33-a33e-ffe05b8a41ef")
    myTarget = request.POST.get("target","2a926071-e56a-4b10-8e3f-eab9ca45e304")
    system_id = request.POST.get("system_id",30)

    system = m.FlowSystem.objects.get(id = system_id)
    linkFrom = m.FlowTransformation.objects.get(uuid = mySource)
    linkTo = m.FlowTransformation.objects.get(uuid = myTarget)

    possibleOutputs = m.FlowTechnosphereMembershipOutput.objects.filter(partOfSystem = system).filter(transformation = linkFrom)
    possibleInputs = m.FlowTechnosphereMembershipInput.objects.filter(partOfSystem = system).filter(transformation = linkTo)

    op = [x.techFlow for x in possibleOutputs]
    ip = [x.techFlow for x in possibleInputs]

    candidates = []

    for i in op:
        if i in ip:
            candidates.append(i)

    if len(candidates) == 1:
        intermediate = candidates[0]

        getRidInput = possibleInputs.get(techFlow = intermediate)
        getRidOutput = possibleOutputs.get(techFlow = intermediate)

        getRidInput.delete()
        getRidOutput.delete()


    return HttpResponse("OK")


def sandbox_delete_item(request):
    uuid = request.POST.get("uuid","")
    type = request.POST.get("type","")
    system_id = request.POST.get("system_id","")

    #uuid = '43281763-cdab-42ed-9885-fde29010696c'
    #type = 'transformation'
    #system_id = 20

    if type == 'input':
        thisItem = m.FlowInputMembership.objects.get(uuid=uuid)
        print thisItem
        thisItem.delete()
        print "Deleted " + uuid
    elif type == 'output':
        thisItem = m.FlowOutputMembership.objects.get(uuid=uuid)
        print thisItem
        thisItem.delete()
        print "Deleted " + uuid
    elif type == 'transformation':
        print 'Deleting transformation ' + uuid
        thisItem = m.FlowTransformation.objects.get(uuid=uuid)
        thisSystem = m.FlowSystem.objects.get(id = system_id)
        deletedSystem = m.FlowSystem.objects.get(name = 'DELETED_SYSTEM')
        print thisSystem
        print deletedSystem
        print thisItem.partOfSystem.remove(thisSystem)
        if len(thisItem.partOfSystem.all())==0:
            thisItem.partOfSystem.add(deletedSystem)



    return HttpResponse("OK")

def sandbox_new_item(request):
    tempuuid = uuid.uuid4()

    type = request.POST.get("type","process")
    name = request.POST.get("name","test2")
    unit = request.POST.get("unit","kg")
    system_id = request.POST.get("system_id",22)
    id = request.POST.get("uuid",tempuuid)
    x = request.POST.get("x",250)
    y = request.POST.get("y",250)

    print id,x,y
    save_position(id,x,y)


    #uuid = '43281763-cdab-42ed-9885-fde29010696c'
    #type = 'transformation'
    #system_id = 20

    if type == 'input':

        emission_factor = 0
        thisItem = m.FlowInputSubstance(name = name, unit = unit, emission_factor = emission_factor)
        thisItem.save()

        print 'saved an ' + type

    elif type == 'output':
        emission_factor = 0
        thisItem = m.FlowOutputSubstance(name = name, unit = unit, emission_factor = emission_factor)
        thisItem.save()

        print 'saved an ' + type

    elif type == 'transformation':
        thisItem = m.FlowTechnosphere(name = name, unit = unit)
        thisItem.save()

        print 'saved a ' + type

    elif type == 'process':
        author = request.user
        system = m.FlowSystem.objects.get(id=system_id)
        thisItem = m.FlowTransformation(name = name, unit = unit, author = author, category = 'Uncategorized',  uuid =id )
        thisItem.save()
        thisItem.partOfSystem.add(system)
        thisItem.save()

        print 'saved a ' + type



    response_data = {'id':thisItem.id}

    return JsonResponse(response_data)

def sandbox_rename_process(request):

    id = request.POST.get("id","")
    newName = request.POST.get("newName","newName")

    print id
    print newName

    thisProcess = m.FlowTransformation.objects.get(uuid = id)
    thisProcess.name = newName
    thisProcess.save()



    return HttpResponse("OK")


def sandbox_edit_quantity(request):

    id = request.POST.get("id","")
    type = request.POST.get("type","")
    newAmount = request.POST.get("newAmount","")

    print id, type, newAmount

    if type == 'input':
        thisItem = m.FlowInputMembership.objects.get(uuid = id)
    else:
        thisItem = m.FlowOutputMembership.objects.get(uuid = id)

    thisItem.amount_required = newAmount
    thisItem.save()

    return HttpResponse("OK")

def sandboxScan(system_id):

    system  = m.FlowSystem.objects.get(id=system_id)
    nodes, links = {},{}
    techInputs, techOutputs = {},{}
    nodeID = 0
    linkID = 0

    for checknum,process in enumerate(m.FlowTransformation.objects.filter(partOfSystem = system)):
        processId = process.uuid

        try:
            sbPos = sm.SandboxPositions.objects.get(uuid=processId)
            print sbPos.x, sbPos.y
        except ObjectDoesNotExist:
            sbDict = {'x':10, 'y':10}
            sbPos = ap.Namespace(**sbDict)


        nodes.update({nodeID:{'name':process.name, 'type':'transformation', 'id':processId, 'initX':sbPos.x, 'initY':sbPos.y}}) # add to nodes
        nodeID+=1

        for i in process.inputflows.all().distinct():

            input_meta = i.flowinputmembership_set.filter(transformation = process).filter(partOfSystem = system) # filter the flows by system and process

            thisID = input_meta[0].uuid

            try:
                sbPos = sm.SandboxPositions.objects.get(uuid=thisID)
                print sbPos.x, sbPos.y
            except ObjectDoesNotExist:
                sbDict = {'x':10, 'y':10}
                sbPos = ap.Namespace(**sbDict)

            nodes.update({nodeID:{'name':i.name, 'type':'input', 'id':thisID, 'initX':sbPos.x, 'initY':sbPos.y}}) # add to nodes
            nodeID+=1


            links.update({linkID:{'source':i.name, 'sourceID': thisID,'target':process.name, 'targetID': processId,'amount':input_meta[0].amount_required,'type':'input','text':'%d %s' % (input_meta[0].amount_required,i.unit)}})
            linkID+=1

        for o in process.outputflows.all().distinct():

            output_meta = o.flowoutputmembership_set.filter(transformation = process).filter(partOfSystem = system) # filter the flows by system and process
            thisID = output_meta[0].uuid

            try:
                sbPos = sm.SandboxPositions.objects.get(uuid=thisID)
                print sbPos.x, sbPos.y
            except ObjectDoesNotExist:
                sbDict = {'x':10, 'y':10}
                sbPos = ap.Namespace(**sbDict)

            nodes.update({nodeID:{'name':o.name, 'type':'output', 'id':thisID, 'initX':sbPos.x, 'initY':sbPos.y}}) # add to nodes
            nodeID+=1



            links.update({linkID:{'source':process.name, 'sourceID':processId, 'target':o.name, 'targetID':thisID,'amount':output_meta[0].amount_required,'type':'output','text':'%d %s' % (output_meta[0].amount_required,o.unit)}})
            linkID+=1

        for ti in process.technosphereInputs.all().distinct():

            input_meta = ti.flowtechnospheremembershipinput_set.filter(transformation = process).filter(partOfSystem = system)

            techInputs.update({ti.name: {'process':process.name, 'processID':processId, 'amount': input_meta[0].amount_required, 'unit':ti.unit}})

        for to in process.technosphereOutputs.all().distinct():

            output_meta = to.flowtechnospheremembershipoutput_set.filter(transformation = process).filter(partOfSystem = system)

            techOutputs.update({to.name: {'process':process.name, 'processID':processId, 'amount': output_meta[0].amount_required, 'unit':to.unit}})

    for i in techOutputs.iterkeys():
        try:
            thisOutput = techOutputs[i]
            matchInput = techInputs[i]
            print thisOutput
            print matchInput
            source = thisOutput['process']
            sourceID = thisOutput['processID']
            target = matchInput['process']
            targetID = matchInput['processID']
            amount = thisOutput['amount']
            unit = thisOutput['unit']


            links.update({linkID:{'source':source, 'sourceID': sourceID, 'target':target, 'targetID':targetID, 'amount':amount,'type':'intermediate','text':'%s (%d %s)' % (i,amount,unit)}})
            linkID+=1
        except KeyError:
            pass


    return nodes, links
