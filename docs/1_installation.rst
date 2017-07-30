============
Installation
============

.. highlight:: console

------------------
Basic Installation
------------------

For lcopt to work you should have the latest version of `brightway2 <https://brightwaylca.org/>`_ by Chris Mutel installed.
This will make sure most of lcopts dependencies are satisfied.

The instructions for installing brightway below are current as of April 2017, but check `here <https://docs.brightwaylca.org/installation.html>`_ for the latest ones.

On the command line/console, create a new environment called lcopt::

    conda create -n lcopt python=3.6


Then activate the lcopt environment using one of these::

    # Mac/Linux
    source activate lcopt
    # Windows
    activate lcopt


Then install brightway2::

	conda install -y -q -c conda-forge -c cmutel -c haasad brightway2 jupyter


On windows there's an extra dependency::

	conda install -y -q pywin32

Once brightway2 is ready to go, theres two more steps before installing lcopt itself...

Install pandas::

	conda install -y -q pandas

Update werkzeug (this is a python 3.6 thing...)::

	pip install -U werkzeug

Finally, install lcopt via pip::

	pip install lcopt

.. _bw2_setup_step:

-----------------------------------------------------
Setting up brightway2 for lcopt
-----------------------------------------------------

To use the interactive analysis feature, you need to set up brightway2 to play nicely with lcopt.

Lcopt needs to set up its own brightway project template so that it can create a new brightway project for each of your models using this template.

Step 1. Download the Ecoinvent 3.3 cutoff database (Ecoinvent license required)
--------------------------------------------------------------------------------------

.. note:: Note - if you don't have an ecoinvent license but want to try out lcopt, it can also be used with the freely available FORWAST database :ref:`forwast_setup_step`.


Log into `ecoinvent.org  <http://www.ecoinvent.org/login-databases.html>`_ and go to the Files tab

Download the file called ``ecoinvent 3.3_cutoff_ecoSpold02.7z``

Extract the file somewhere sensible on your machine, you might need to download `7-zip <http://www.7-zip.org/download.html>`_ to extract the files.

Make a note of the path of the folder that contains the .ecospold files, its probably ``<path/extracted/to>/datasets/``

Step 2a. Run the setup utility in a jupyter notebook/python shell
-----------------------------------------------------------------

.. highlight:: python

Fire up your chosen python shell, then use::

	from lcopt.utils import lcopt_bw2_setup
	ecospold_path = r'path/to/ecospold/files' # put your own path in here
	lcopt_bw2_setup(ecospold_path)

It'll take a while, but once its done it'll return ``True`` if it worked properly


Step 2b. Download lcopt_bw2_setup.py and use that instead
---------------------------------------------------------

Download the helper script from `here <https://raw.githubusercontent.com/pjamesjoyce/lcopt/master/lcopt_bw2_setup.py>`_


.. highlight:: console

At the command line type::

	cd folder/you/downloaded/it/to
	python lcopt_bw2_setup.py path/to/ecospold/files # use "" if there are spaces in your path


.. _forwast_setup_step:

---------------------------
Alternative setup - FORWAST
---------------------------

Lcopt can be used without an ecoinvent license by using the `FORWAST <http://forwast.brgm.fr/>`_ database instead.

Option 1. Run the setup utility in a jupyter notebook/python shell
-----------------------------------------------------------------

.. highlight:: python

Fire up your chosen python shell, then use::

	from lcopt.utils import lcopt_bw2_forwast_setup
	lcopt_bw2_forwast_setup()

It'll take a while, but once its done it'll return ``True`` if it worked properly


Option 2. Download lcopt_bw2_setup.py and use that instead
---------------------------------------------------------

Download the helper script from `here <https://raw.githubusercontent.com/pjamesjoyce/lcopt/master/lcopt_bw2_setup_forwast.py>`_

.. highlight:: console

At the command line type::

	cd folder/you/downloaded/it/to
	python lcopt_bw2_setup_forwast.py
