===========
Using Lcopt
===========

------------------------------------
Creating and loading your own models
------------------------------------

There are 2 options for using lcopt's GUI (LCOPT INTERACT) to create and view your own models

Option 1. lcopt-launcher command line entry point *(Simpler, only access to GUI)*
---------------------------------------------------------------------------------

Using this option, you can launch lcopt from the command line/console and use the GUI from then on.

Open the console/command line.

.. highlight:: console

Activate your *lcopt* environment, ``cd`` into the folder you want to store your model in then simply use ``lcopt-launcher`` ::

	activate lcopt
	cd C:\Users\pjjoyce\Documents\01_Lcopt_models
	lcopt-launcher


You'll get an option to either create a new model or load an existing one (or to view the example model). 

If you choose to create a model you will be prompted for a name - this will be the model's name and the default filename.

If you choose to load a model a file dialog will open and allow you to choose an existing ``.lcopt`` file.

Once you've made your choice, the GUI will open in your default browser.

Option 2. Jupyter notebooks *(More complicated, more powerful)*
---------------------------------------------------------------

Probably the best way to use lcopt is via a jupyter notebook. This gives you more access to the inner workings if you need to get at something you can't see in the GUI.

.. highlight:: console

``cd`` into whatever folder you want your notebooks and lcopt models to be stored in, then start jupyter e.g.::

	activate lcopt
	cd C:\Users\pjjoyce\Documents\01_Lcopt_models
	jupyter notebook

This will fire up the jupyter notebook server in your browser.
Create a new notebook, give it a meaningful name.

.. highlight:: python

Then in the first cell import lcopt::

	from lcopt import *

Next create your LcoptModel::

	model = LcoptModel('MyFirstModel')

or load an existing one::

	model = LcoptModel(load = 'MyFirstModel')

.. note::  If you are using FORWAST instead of ecoinvent, you need to add the argument `useForwast=True` e.g. `model = LcoptModel(load = 'MyFirstModel', useForwast=True)`

Then launch the interactive model creator/analyser::

	model.launch_interact()

------------------------
LCOPT INTERACT - the GUI
------------------------

Running the GUI via each of the options above launches a Flask server that gives you a nice UI to interact with the models. You can add processes, link them together, add biosphere and technosphere exchanges, and create parameter sets and functions using your parameters. It should be pretty intuitive, if you get stuck, try the 'more info...' buttons.

See the :ref:`video <video>` in the :ref:`getting_started` page for a runthrough of the functionality of the GUI.

When your model's ready you can export it to SimaPro as a .csv file and the parameter sets you've created as an Excel file (Note: you need SimaPro developer to import the parameter sets from the Excel file).

To run the analyses interactively using brightway2, make sure you've completed the additional setup step (:ref:`bw2_setup_step`).

The 'QUIT' button in the top right hand corner will shut down the Flask server and tell you to close the window.

If you're running from a jupyter notebook, this frees up the notebook again so you can run any commands you need to.

One useful command is ``model.save()`` which will save any unsaved changes (you can also save by clicking on the save button in LcoptInteract, but in case you forget you can use ``model.save()``)

The model is saved as a .lcopt file in your working directory (its really a .pickle file, but the .lcopt extension makes it easier to filter on in the lcopt_launcher file picker)

.. highlight:: python

NOTE: The next time you run the GUI from a notebook you need to use::

	model = LcoptModel(load = 'MyFirstModel')

If you don't it'll create a new blank model called 'MyFirstModel'. If you do do this by accident fear not - it won't overwrite your .lcopt file until you save it. 
Quit interact by hitting the QUIT button and go back and change your command (just don't click the save button or run `model.save()` in the meantime)
