============
Introduction
============

What does it do?
----------------

LCOPT is designed to provide a simple and intuitive way to create 'fully parameterised' Life Cycle Inventory foreground models.

What's a Life Cycle Inventory foreground model?
------------------------------------------------

To conduct a Life Cycle Assessment (LCA) we need to create a model of the life cycle of a given product or process which we can then use to estimate the potential environmental impact which results. This includes extraction of raw materials, processing, transport, use, disposal etc. etc. 

Because each item used in a life cycle has it's own set upstream processes the LCA model tends to be split into the *foreground system* - the processes under the control of the person doing the LCA - and the *background system* - the rest of the industrial economy which provides the materials and services required by the foreground system.

Background system models are either determined by data providers (e.g. `ecoinvent <http://www.ecoinvent.org/database/system-models-in-ecoinvent-3/system-models-in-ecoinvent-3.html>`_) or can be customised using `Ocelot <https://ocelot.space/>`_.

The foreground model is a set of linked *unit processes*. A unit process describes a stage in the life cycle. It is basically a list of the *exchanges* required to produce one unit of an intermediate (or final) product. These exchanges can either be inputs from the *technosphere* - the human constructed industrial economy - or resources from or emissions to the *biosphere*. Technosphere exchanges can either come from the background system or other processes in the foreground system.

For example, when you make a cup of tea you *make* some boiling water, add this to some tea leaves, add some milk, then use/drink it.

.. sidebar:: Flow chart

    .. image:: assets/tea_flow_chart.jpg

The boiling water is created in the unit process *kettle* which takes inputs from the background system of *water* and *electricity* and emits a small amount of *water vapour* to the biosphere.

The next unit process is *teapot*. This takes an input of *boiling water* from our first process, and *tea leaves* from the background system to produce *black tea*. 

Finally, *teacup* takes an input of *black tea* from the *teapot* process and *milk* from the background system *Note : we're making a proper British cup of tea!*

We now have a foreground model for our cup of tea LCA.

Why use LCOPT for creating foreground models?
---------------------------------------------

How you create your foreground model is up to you. 

Simple models can be constructed in Excel. More complex models can be created in commercially available softwares such as `SimaPro <https://simapro.com/>`_ or `GaBi <http://www.gabi-software.com/international/index/>`_, or freeware such as `OpenLCA <http://www.openlca.org>`_.

These fully featured software packages have a steep learning curve, can cost a lot of money, or require administrator rights to run (which can be an issue with university or company owned computers).

Lcopt is free, open source and written in Python. You can install it without admin rights and it runs in a normal web browser. It's designed to be simple and intuitive, but powerful enough to conduct *proper* LCAs.

How do you create foreground models in LCOPT?
---------------------------------------------

When you start an LCA, its usually a good idea to draw out a flow diagram of the system you're modelling on a piece of paper. This helps you identify the unit processes involved, the inputs they use and the extent of the *foreground system* you might be able to get primary data for.

Creating foreground models in Lcopt is as simple as drawing out your flow chart.

Instead of having to write out lists of exchanges to describe each unit process, you simply draw out a flow sheet of your process. You can add processes, link them together and add inputs and outputs. In the background Lcopt compiles these exchange lists, and gives each link a parameter. When you've finished your drawing you have a *fully parameterised* foreground model.

What does *fully parameterised* mean?
-------------------------------------

In order to analyse your LCA model, you need to know how much of each exchange is required by each unit process. In most softwares the default is to *hard code* these values in the unit process itself. This is great for a one-off model, but can be a real hassle if there are multiple variants of your system which you want to assess and compare.

Taking the example from above, some people like their tea with milk, some like it black. Some people like strong tea (with more tea leaves) others like it weaker. If you want to compare weak milky tea with strong black tea you'd need to create two different *teapot* processes (one for weak, one for strong) and two different *teacup* processes (one for milky, one for black), with the correct exchange amounts, and links to the version of *teapot* with the correct output.

If you then decide you want to model strong milky tea or weak black tea you need to create more unit processes...

Most LCA softwares allow you to replace the values in the unit processes with parameters, which you can then vary externally to create scenarios. Choosing, typing out and remembering parameters can be a boring and time consuming task though. With Lcopt it's all done automatically in the background. Every link in the model is given a parameter instead of a value. By default, the model is 'fully parameterised'. 

This makes creating the model a lot quicker and the modelling and analysis a lot more flexible.

How do you go from a flow sheet to a model?
-------------------------------------------

To go from an unquantified flow sheet to a meaningful LCA model, the first thing you need to do is create a *parameter set*. This provides a value for each link in a given scenario.

You can either enter an explicit value, or you can tell the model to generate its own value based on a function/formula. To help this you can also create *global parameters* to use in these functions.

For example, the amount of electrity (kWh) a kettle uses to boil a litre of water can be determined by it's power rating (kW) and the amount of time it takes to boil (minutes). 

You can create a global parameter for *power rating* and another one for *boil minutes*. You can then tell the model to generate a value for the input of *electricity* to *kettle* using the function ``power_rating * boil_mins / 60``.

Now you can easily compare different kettles in your cup of tea LCA.

You can use any parameter in a function, including inputs to any process. For example, if you want to add transport of an input (in units of kg.km) you could create a 'transport distance' parameter, and tell Lcopt to work out the amount of 'transport' required by multiplying the amount of your input (kg) by the distance (km). Now whenever you change the amount of your input, the transport of that input automatically changes too.

Once you have a 'default' parameter set you can duplicate it and edit whichever parameters you need to describe a new scenario. 

For example you can change the parameter for the input of *milk* to *teacup* to zero to model a black tea scenario, or increase the input of *tea leaves* to *teapot* to model a strong tea scenario.

How do you analyse a model?
---------------------------

.. sidebar:: Hotspot chart

    .. image:: assets/hotspot_chart_tea_sm.png

To analyse the model you have two options. 

If you have a copy of SimaPro and are using lcopt as an easy way to generate a fully parameterised foreground model, you can export the model as a SimaPro .csv file and the parameter sets as an .xlsx file.

The second option is to run the analysis directly from Lcopt. This uses `Brightway <https://brightwaylca.org/>`_ to do the calcuations. Brightway is an open source LCA software also written in Python.

When you analyse a model from within Lcopt for the first time it creates a Brightway project. The foreground model is stored as it's own separate database within the project, with links to the biosphere and technosphere databases.

Lcopt calculates all of the parameters for each parameter set and then modifies the exchanges in the Brightway database before running the LCA calculations for that scenario.

.. sidebar:: Tree diagram

    .. image:: assets/tree_sm.png

You can choose from over 700 different impact assessment methods (don't worry, there is a search function), and use as many as you like in one go. The default set is climate change (IPCC 2013 100a) and human toxicity (USEtox).

Lcopt's results screens contain bar charts, pie charts, tree diagrams, hotspot charts and tables. Charts can be exported to image files (300 dpi .png with transparent backgrounds) and the tables exported as Excel files.

Once the analysis has been run you can open the model in Brightway as you would any other project if you need to conduct a more detailed analysis. Note however that Brightway will only 'remember' the last scenario you ran so to do this it might be best to create your model with only one parameter set.

How do I get started?
---------------------

To get started, follow the :doc:`installation instructions <1_installation>` on the next page, learn how to launch lcopt in your browser in the :doc:`usage instructions <2_use>` then check out the :doc:`video runthrough <3_video_runthrough>` to see how to make the *cup of tea* model using Lcopt.