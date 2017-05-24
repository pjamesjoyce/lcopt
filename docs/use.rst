========
Using LCOPT
========

# Using the GUI

There are 2 options for using lcopt's GUI (LCOPT INTERACT)

## Option 1. Jupyter notebooks (More complicated, more powerful)

Probably the best way to use lcopt is via a jupyter notebook. This gives you more access to the inner workings if you need to get at something you can't see in the GUI.

`cd` into whatever folder you want your notebooks and lcopt models to be stored in, then start jupyter e.g.

```
activate lcopt
cd C:\Users\pjjoyce\Documents\01_Lcopt_models
jupyter notebook
```

This will fire up the jupyter notebook server in your browser.
Create a new notebook, give it a meaningful name.

Then in the first cell import lcopt
```python
from lcopt import *
```

Next create your LcoptModel
```python
model = LcoptModel('MyFirstModel')
```

or load an existing one
```python
model = LcoptModel(load = 'MyFirstModel')
```

Then launch the interactive model creator/analyser
```python
model.launch_interact()
```

## Option 2. lcopt_launcher.py (Simpler, only access to GUI)

Using this option, you can type a couple of commands into the command line/console and use the GUI from then on

First, download `lcopt_launcher.py` from [here](https://raw.githubusercontent.com/pjamesjoyce/lcopt/master/lcopt_launcher.py)

Save it in the folder you want to store your models in

Open the console/command line

`cd` into your chosen folder and run `lcopt_launcher.py`

```
activate lcopt
cd C:\Users\pjjoyce\Documents\01_Lcopt_models
python lcopt_launcher.py
```

You'll get an option to either create a new model or open an exising one. Make your choice and the GUI will open in your default browser.

# LCOPT INTERACT - the GUI

Running the GUI via each of the options above launches a Flask server that gives you a nice UI to interact with the models. You can add processes, link them together, add biosphere and technosphere exchanges, and create parameter sets and functions using your parameters. It should be pretty intuitive, if you get stuck, try the 'more info...' buttons.

When your model's ready you can export it to SimaPro as a .csv file and the parameter sets you've created as an Excel file (Note: you need SimaPro developer to import the parameter sets from the Excel file).

To run the analyses interactively using brightway2 there's an additional setup step. See below.

The 'QUIT' button in the top right hand corner will shut down the Flask server and tell you to close the window.

If you're running from a jupyter notebook, this frees up the notebook again so you can run any commands you need to.

One useful command is `model.save()` which will save any unsaved changes (you can also save by clicking on the save button in LcoptInteract, but in case you forget you can use `model.save()`)

The model is saved as a .lcopt file in your working directory (its really a .pickle file, but the .lcopt extension makes it easier to filter on in the lcopt_launcher file picker)

NOTE: The next time you run the GUI from a notebook you need to use  
```python
model = LcoptModel(load = 'MyFirstModel')
```

If you don't it'll create a new blank model called 'MyFirstModel'. If you do do this by accident fear not - it won't overwrite your .lcopt file until you save it. 
Quit interact by hitting the QUIT button and go back and change your command (just don't click the save button or run `model.save()` in the meantime)
