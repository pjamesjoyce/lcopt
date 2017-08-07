# lcopt
An interactive tool for creating fully parameterised Life Cycle Assessment (LCA) foreground models

[![Build Status](https://travis-ci.org/pjamesjoyce/lcopt.svg?branch=master)](https://travis-ci.org/pjamesjoyce/lcopt)

[![Coverage Status](https://coveralls.io/repos/github/pjamesjoyce/lcopt/badge.svg?branch=master)](https://coveralls.io/github/pjamesjoyce/lcopt?branch=master)

Lcopt is a python module for creating fully parameterised LCA foreground models using a Flask based interactive GUI developed by [James Joyce](https://pjamesjoyce.github.io/)
It integrates with SimaPro and BrightWay2

Online documentation, including full installation instructions, is available [here](http://lcopt.readthedocs.io)

## Installation

### Basic Installation

For lcopt to work you should have the latest version of [brightway2](https://brightwaylca.org/) by Chris Mutel installed.
This will make sure most of lcopts dependencies are satisfied.

The instructions for installing brightway below are current as of April 2017, but check [here](https://docs.brightwaylca.org/installation.html) for the latest ones.

On the command line/console, create a new environment called lcopt:

```
conda create -n lcopt python=3.6
```


Then activate the lcopt environment using one of these:
```
# Mac/Linux
source activate lcopt
# Windows
activate lcopt
```

Then install brightway2:
```
conda install -y -q -c conda-forge -c cmutel -c haasad brightway2 jupyter
```

On windows there's an extra dependency:
```
conda install -y -q pywin32
```

Once brightway2 is ready to go, theres two more steps before installing lcopt itself...

Install pandas:
```
conda install -y -q pandas
```

Update werkzeug (this is a python 3.6 thing...):
```
pip install -U werkzeug
```

Finally, install lcopt via pip::
```
pip install lcopt
```

### Linking lcopt to brightway

To analyse any of the models you create in lcopt in brightway, there's an extra installation step to set up the default project and databases.

Full details of this step are in the [documentation](https://lcopt.readthedocs.io/en/latest/1_installation.html#setting-up-brightway2-for-lcopt)

Lcopt can create models using external LCI data from the [ecoinvent 3.3 cutoff database](http://www.ecoinvent.org/database/ecoinvent-33/ecoinvent-33.html) (ecoinvent license required) or the [FORWAST database](http://forwast.brgm.fr/)

Briefly, to set up lcopt to use ecoinvent 3.3:

Log into [ecoinvent.org](http://www.ecoinvent.org/login-databases.html) and go to the Files tab

Download the file called `ecoinvent 3.3_cutoff_ecoSpold02.7z`

Extract the file somewhere sensible on your machine, you might need to download [7-zip](http://www.7-zip.org/download.html) to extract the files.

Make a note of the folder path that contains the .ecospold files, its probably `<path/extracted/to>/datasets/`

Open a python console or jupyter notebook and use the setup utility function below:

```python
from lcopt.utils import lcopt_bw2_setup
ecospold_path = r'path/to/ecospold/files' # put your own path in here
lcopt_bw2_setup(ecospold_path)
```

To set up lcopt to use FORWAST there's no download step (the utility function downloads the latest version of the database). Simply use:

```python
from lcopt.utils import lcopt_bw2_forwast_setup
lcopt_bw2_forwast_setup()
```

## Example Usage

Below are the basic commands to get lcopt's interactive GUI up and running to create your first model. More detailed instructions are available in the [online documentation](https://lcopt.readthedocs.io/en/latest/2_use.html), including a [video runthrough](https://lcopt.readthedocs.io/en/latest/3_video_runthrough.html) of creating a simple model using the ecoinvent 3.3 database.

Lcopt saves models in your current working directory, so before launching it, `cd` to the folder you want to save your models in.

Lcopt is written in Python, so to use it open up a jupyter notebook or python shell and use the following commands

### Importing Lcopt

To import lcopt use 

```python
from lcopt import *
```

### Creating a new model

To create a model, you need to create an instance of the LcoptModel class using the model name as the first argument:

```python
model = LcoptModel('My First Model')
```

By default the model will be populated in the background with the details to link to the ecoinvent 3.3 datasets. If you want your model to use FORWAST instead use:

```python
model = LcoptModel('My First FORWAST Model', useForwast=True)
```

### Loading an existing model

To load a model, make sure the file (*.lcopt) is in your working directory and use the model name (with or without the .lcopt extension) in this command:

```python
model = LcoptModel(load='My First Model')
```

Note : If you accidentally forget to use `load=` and you see a blank model don't panic. Lcopt won't overwrite your saved model unless you tell it to. Simply don't save the model and re-run the command with `load=`

### Launching the GUI

To launch the GUI for your model simply call the `launch_interact` method of your newly created model instance:

```python
model.launch_interact()
```

This will start a Flask server and launch your web browser to access the GUI. If it doesn't or you accidentally close the GUI tab, simply go to [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

Information on how to use the GUI is located in 'More info...' panels dotted around at sensible locations within it.

For more details on using it, see the [documentation](https://lcopt.readthedocs.io/en/latest/2_use.html) or the [video](https://lcopt.readthedocs.io/en/latest/3_video_runthrough.html)

## Contribute

If you have any problems, questions, comments, feature requests etc. please [raise an issue here on github](https://github.com/pjamesjoyce/lcopt/issues)

If you want to contribute to Lcopt, you're more than welcome! Please fork the [github repository](https://github.com/pjamesjoyce/lcopt/) and open a pull request. 

Lcopt uses [py.test](https://docs.pytest.org/en/latest/index.html>) and Travis for automated testing, so please accompany any new features with corresponding tests. See the `tests` folder in the [source code](https://github.com/pjamesjoyce/lcopt/tree/master/tests) for examples.  