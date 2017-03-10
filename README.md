# lcopt
Life cycle optimisation module

# Installation

For lcopt to work you should have the latest version of [brightway2](https://brightwaylca.org/) by Chris Mutel installed.
If you already have brightway installed, you can skip to the final step.

The best option is to use conda to create a separate environment, to avoid conflicts.

On the command line/console, create a new environment called lcopt

```
conda create -y -n lcopt python=3.5 lxml cytoolz numpy scipy pandas
```

Then activate the lcopt environment

```
activate lcopt
```

On windows there's an extra dependency
```
conda install -y pywin32
```

Then install brightway2 (and its dependecies)
```
conda install wheel && conda update pip wheel setuptools
conda install -q -y -c haasad pypardiso
conda install -q -y ipython ipython-notebook jupyter matplotlib flask requests docopt whoosh xlsxwriter xlrd unidecode appdirs future psutil unicodecsv wrapt
pip install --no-cache-dir eight brightway2
```

Once brightway2 is ready fo go,  install lcopt via pip:

```
pip install --no-cache-dir https://github.com/pjamesjoyce/lcopt/zipball/master
```

Note - because lcopt is a work in progress currently, if you're reinstalling to get the latest version make sure you use the --no-cache-dir flag

# Use

The easiest way to use lcopt is via a jupyter notebook.

`cd` into whatever folder you want your notebooks and lcopt models to be stored in, then start jupyter e.g.

```
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

Then launch the interactive model creator/analyser
```python
model.launch_interact()
```
This launches a Flask server that gives you a nice UI to interact with the models. You can add processes, link them together, add biosphere and technosphere exchanges, and create parameter sets and functions using your parameters. It should be pretty intuitive, if you get stuck, try the 'more info...' buttons.

When your model's ready you can export it to SimaPro as a .csv file and the parameter sets you've created as an Excel file (Note: you need SimaPro developer to import the parameter sets from the Excel file).

To run the analyses interactively using brightway2 there's an additional setup step. See below.

The 'QUIT' button in the top right hand corner will shut down the Flask server and tell you to close the window.

This frees up the notebook again so you can run any commands you need to. 

One useful command is `model.save()` which will save any unsaved changes (you can also save by clicking on the save button in LcoptInteract, but in case you forget you can use `model.save()`)

The model is saved as a .pickle file in your working directory.

NOTE: The next time you run your notebook you need to change 
```python
model = LcoptModel('MyFirstModel')
```
to 
```python
model = LcoptModel(load = 'MyFirstModel')
```

If you don't it'll create a new blank model called 'MyFirstModel'. If you do do this by accident fear not - it won't overwrite your .pickle file until you save it. 
Quit interact by hitting the QUIT button and go back and change your command (just don't click the save button or run `model.save()` in the meantime)


## Running the analyses in LcoptInteract with brightway2

To use the interactive analysis feature, you need to set up brightway2 to play nicely with lcopt.
Create a project in brightway called `setup_TO_COPY` which contains the biosphere3 database, the methods and the version of ecoinvent/any other external databases you want to use.
The default name that lcopt looks for for ecoinvent is `Ecoinvent3_3_cutoff` (i.e. its database keys need to look like this `('Ecoinvent3_3_cutoff', '41f548bf636724eec735138986b33229')`).

I'll try and add support for other versions asap.

