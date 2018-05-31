# lcopt
An interactive tool for creating fully parameterised Life Cycle Assessment (LCA) foreground models

[![Build Status](https://travis-ci.org/pjamesjoyce/lcopt.svg?branch=master)](https://travis-ci.org/pjamesjoyce/lcopt)

[![Coverage Status](https://coveralls.io/repos/github/pjamesjoyce/lcopt/badge.svg?branch=master)](https://coveralls.io/github/pjamesjoyce/lcopt?branch=master)

[![Publication](http://joss.theoj.org/papers/c0b544bee185c9ac75e96d24b8573547/status.svg)](http://joss.theoj.org/papers/c0b544bee185c9ac75e96d24b8573547)

Lcopt is a python module for creating fully parameterised LCA foreground models using a Flask based interactive GUI developed by [James Joyce](https://pjamesjoyce.github.io/)

It integrates with SimaPro and BrightWay2

You can export and share your model and results as an .lcoptview file, and share them with a wider audience using [lcoptview](http://lcoptview.rtfd.io)

Online documentation, including full installation instructions, is available [here](http://lcopt.readthedocs.io)

## Installation

### Basic Installation

The easiest way to install lcopt is via conda. This ensures the version of Python (3.6) is correct, all of the dependencies are correct and there are no conflicts.
You can also do it in only 3 commands.

If you don't have conda installed yet, first install Miniconda (available [here](https://conda.io/miniconda.html))

1) On the command line/console, create a new environment called lcopt:
```
conda create -n lcopt python=3.6
```

2) Activate the lcopt environment using one of these:
```
# Mac/Linux
source activate lcopt
# Windows
activate lcopt
```

3) Install lcopt:
```
conda install -y -q -c conda-forge -c cmutel -c haasad -c pjamesjoyce lcopt
```

### Development installation

Lcopt is continuing to develop, with new features and extensions being added. The `lcopt-dev` conda package is updated each time an update is pushed to the [`development` branch on github](https://github.com/pjamesjoyce/lcopt/tree/development).

It's recommended that you create a new environment separate from the one with `lcopt` in to install `lcopt-dev`, as they will overwrite one another.

Create a dev environment like this

```
conda create -y -n lcopt-dev -c conda-forge -c cmutel -c haasad -c pjamesjoyce lcopt-dev
```

Or to get the most up to date version of `lcopt-dev`:

```
activate lcopt-dev
conda update -c conda-forge -c cmutel -c haasad -c pjamesjoyce lcopt-dev
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

Open a command line/console and type:

```
lcopt-bw2-setup path/to/ecospold/files # use "" if there are spaces in your path
```

To set up lcopt to use FORWAST there's no download step (the script downloads the latest version of the database). At the command line/console simply use:

```
lcopt-bw2-setup-forwast
```

## Example Usage

Below are the basic commands to get lcopt's interactive GUI up and running to create your first model. A [Getting Started](https://lcopt.readthedocs.io/en/latest/2_Getting_Started.html) guide, including a [video runthrough](https://lcopt.readthedocs.io/en/latest/2_Getting_Started.html#video), as well as [more detailed instructions](https://lcopt.readthedocs.io/en/latest/3_use.html) are available in the [online documentation](https://lcopt.readthedocs.io/).

Lcopt saves models in your current working directory, so before launching it, `cd` to the folder you want to save your models in.

To launch lcopt and view an example model, at the command line use:
```
lcopt-launcher
```

Lcopt is written in Python, so you can also use it from within a Python shell. Open up a jupyter notebook or python shell and use the following commands:

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

To load a model, make sure the file (\*.lcopt) is in your working directory and use the model name (with or without the .lcopt extension) in this command:

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

For more details on using it, see the [documentation](https://lcopt.readthedocs.io/en/latest/3_use.html) or the [video](https://lcopt.readthedocs.io/en/latest/2_Getting_Started.html#video)

## Contribute

If you have any problems, questions, comments, feature requests etc. please [raise an issue here on github](https://github.com/pjamesjoyce/lcopt/issues)

If you want to contribute to Lcopt, you're more than welcome! Please fork the [github repository](https://github.com/pjamesjoyce/lcopt/) and open a pull request. 

Lcopt uses [py.test](https://docs.pytest.org/en/latest/index.html>) and Travis for automated testing, so please accompany any new features with corresponding tests. See the `tests` folder in the [source code](https://github.com/pjamesjoyce/lcopt/tree/master/tests) for examples.  

## Cite

Lcopt has been published in the [Journal of Open Source Software](http://joss.theoj.org/papers/10.21105/joss.00339).

[![Publication](http://joss.theoj.org/papers/c0b544bee185c9ac75e96d24b8573547/status.svg)](http://joss.theoj.org/papers/c0b544bee185c9ac75e96d24b8573547)

You can download the citation in BibTeX for use in LaTeX or importing into [Mendeley](https://www.mendeley.com/)/other reference management software from [here](http://www.doi2bib.org/#/doi/10.21105/joss.00339).

Or use the following citation:

Joyce, P.J., 2017. Lcopt - An interactive tool for creating fully parameterised Life Cycle Assessment (LCA) foreground models. Journal of Open Source Software, 2:16. doi:10.21105/joss.00339