============
Installation
============

.. highlight:: console

------------------
Basic Installation
------------------

Recommended Installation
------------------------

The easiest way to install lcopt is via conda. This ensures the version of Python (3.6) is correct, all of the dependencies are correct and there are no conflicts.
You can also do it in only 3 commands.

If you don't have conda installed yet, first install Miniconda (available `here <https://conda.io/miniconda.html>`_)

1) On the command line/console, create a new environment called lcopt::

    conda create -n lcopt python=3.6

2) Activate the lcopt environment using one of these::

    # Mac/Linux
    source activate lcopt
    # Windows
    activate lcopt

3) Install lcopt::

	conda install -y -q -c conda-forge -c cmutel -c haasad -c pjamesjoyce lcopt

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

Step 2a. lcopt-bw2-setup at the command line
--------------------------------------------

.. highlight:: console

At the command line type::

	lcopt-bw2-setup path/to/ecospold/files # use "" if there are spaces in your path


Step 2b. Or run the setup utility in a jupyter notebook/python shell
--------------------------------------------------------------------

.. highlight:: python

Fire up your chosen python shell, then use::

	from lcopt.utils import lcopt_bw2_setup
	ecospold_path = r'path/to/ecospold/files' # put your own path in here
	lcopt_bw2_setup(ecospold_path)

It'll take a while, but once its done it'll return ``True`` if it worked properly.

Running the setup utility in a python shell also allows you to overwrite your existing configuration if something has gone wrong by using ``lcopt_bw2_setup(ecospold_path, overwrite=True)``

.. _forwast_setup_step:

---------------------------
Alternative setup - FORWAST
---------------------------

Lcopt can be used without an ecoinvent license by using the `FORWAST <http://forwast.brgm.fr/>`_ database instead.

Option 1. Download lcopt_bw2_setup.py and use that instead
----------------------------------------------------------

.. highlight:: console

At the command line type::

	lcopt-bw2-setup-forwast

Option 2. Run the setup utility in a jupyter notebook/python shell
------------------------------------------------------------------

.. highlight:: python

Fire up your chosen python shell, then use::

	from lcopt.utils import lcopt_bw2_forwast_setup
	lcopt_bw2_forwast_setup()

It'll take a while, but once its done it'll return ``True`` if it worked properly.

As above, you can overwrite an existing configuration using ``overwrite=True``
