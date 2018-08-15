"""
lcopt.utils
-----------

Module containing the utility function to set up brightway2 to work with lcopt

"""

import tempfile
import requests
import zipfile
import io
import os
import eidl
from functools import partial
import yaml
import pickle
import getpass

try:
    import brightway2 as bw2
except:                                                         # pragma: no cover
    raise ImportError('Please install the brightway2 package first')

from .data_store import storage
from .constants import (DEFAULT_PROJECT_STEM,
                        DEFAULT_BIOSPHERE_PROJECT,
                        DEFAULT_DB_NAME,
                        FORWAST_PROJECT_NAME,
                        FORWAST_URL,
                        ASSET_PATH,
                        DEFAULT_CONFIG,
                        DEFAULT_SINGLE_PROJECT)



def lcopt_bw2_setup(ecospold_path, overwrite=False, db_name=DEFAULT_DB_NAME):  # pragma: no cover

    """
    Utility function to set up brightway2 to work correctly with lcopt.

    It requires the path to the ecospold files containing the Ecoinvent 3.3 cutoff database.

    If you don't have these files, log into `ecoinvent.org  <http://www.ecoinvent.org/login-databases.html>`_ and go to the Files tab

    Download the file called ``ecoinvent 3.3_cutoff_ecoSpold02.7z``

    Extract the file somewhere sensible on your machine, you might need to download `7-zip <http://www.7-zip.org/download.html>`_ to extract the files.

    Make a note of the path of the folder that contains the .ecospold files, its probably ``<path/extracted/to>/datasets/``

    Use this path (as a string) as the first parameter in this function

    To overwrite an existing version, set overwrite=True
    """
    if db_name in bw2.projects:
        if overwrite:                                           
            bw2.projects.delete_project(name=db_name, delete_dir=True)
        else:
            print('Looks like bw2 is already set up - if you want to overwrite the existing version run lcopt.utils.lcopt_bw2_setup in a python shell using overwrite = True')
            return False

    bw2.projects.set_current(db_name)
    bw2.bw2setup()
    ei = bw2.SingleOutputEcospold2Importer(ecospold_path, "Ecoinvent3_3_cutoff")
    ei.apply_strategies()
    ei.statistics()
    ei.write_database()

    return True

def bw2_project_exists(project_name):
    return project_name in bw2.projects

def upgrade_old_default():

    default_ei_name = "Ecoinvent3_3_cutoff"
    bw2.projects.set_current(DEFAULT_PROJECT_STEM[:-1])
    bw2.projects.copy_project(DEFAULT_PROJECT_STEM + default_ei_name, switch=True)
    write_search_index(DEFAULT_PROJECT_STEM + default_ei_name, default_ei_name)
    print('Copied old lcopt setup project')
    return True

def check_for_config():

    config = None

    try:
        config = storage.config
    except:
        pass

    return config

def write_search_index(project_name, ei_name, overwrite=False):
    si_fp = os.path.join(storage.search_index_dir, '{}.pickle'.format(ei_name)) #os.path.join(ASSET_PATH, '{}.pickle'.format(ei_name))

    if not os.path.isfile(si_fp) or overwrite:

        search_index = create_search_index(project_name, ei_name)

        with open(si_fp, 'wb') as handle:
            print("Writing {} search index to search folder".format(ei_name))
            pickle.dump(search_index, handle)
    #else:
    #    print("{} search index already exists in assets folder".format(ei_name))


def lcopt_biosphere_setup():
    print("Running bw2setup for lcopt - this only needs to be done once")
    bw2.projects.set_current(DEFAULT_BIOSPHERE_PROJECT)
    bw2.bw2setup()



def lcopt_bw2_autosetup(ei_username=None, ei_password=None, write_config=None, ecoinvent_version='3.3', ecoinvent_system_model = "cutoff", overwrite=False):  

    """
    Utility function to automatically set up brightway2 to work correctly with lcopt.

    It requires a valid username and password to login to the ecoinvent website.

    These can be entered directly into the function using the keyword arguments `ei_username` and `ei_password` or entered interactively by using no arguments.
    
    `ecoinvent_version` needs to be a string representation of a valid ecoinvent database, at time of writing these are "3.01", "3.1", "3.2", "3.3", "3.4"

    `ecoinvent_system_model` needs to be one of "cutoff", "apos", "consequential"

    To overwrite an existing version, set overwrite=True
    """

    ei_name = "Ecoinvent{}_{}_{}".format(*ecoinvent_version.split('.'), ecoinvent_system_model)

    config = check_for_config()
    # If, for some reason, there's no config file, write the defaults
    if config is None:
        config = DEFAULT_CONFIG
        with open(storage.config_file, "w") as cfg:
            yaml.dump(config, cfg, default_flow_style=False)

    store_option = storage.project_type

    # Check if there's already a project set up that matches the current configuration
    
    if store_option == 'single':

        project_name = storage.single_project_name

        if bw2_project_exists(project_name):
            bw2.projects.set_current(project_name)
            if ei_name in bw2.databases and overwrite == False:
                #print ('{} is already set up'.format(ei_name))
                return True

    else: # default to 'unique'
        project_name = DEFAULT_PROJECT_STEM + ei_name

        if bw2_project_exists(project_name):
            if overwrite:                                           
                bw2.projects.delete_project(name=project_name, delete_dir=True)

    auto_ecoinvent = partial(eidl.get_ecoinvent,db_name=ei_name, auto_write=True, version=ecoinvent_version, system_model=ecoinvent_system_model)

    # check for a config file (lcopt_config.yml)

    if config is not None:
        if "ecoinvent" in config:
            if ei_username is None:
                ei_username = config['ecoinvent'].get('username')
            if ei_password is None:
                ei_password = config['ecoinvent'].get('password')
            write_config = False

    if ei_username is None:
        ei_username = input('ecoinvent username: ')
    if ei_password is None:
        ei_password = getpass.getpass('ecoinvent password: ')
    if write_config is None:
        write_config = input('store username and password on this computer? y/[n]') in ['y', 'Y', 'yes', 'YES', 'Yes']

    if write_config:

        config['ecoinvent'] = {
            'username': ei_username,
            'password': ei_password
        }
        with open(storage.config_file, "w") as cfg:
            yaml.dump(config, cfg, default_flow_style=False)

    # no need to keep running bw2setup - we can just copy a blank project which has been set up before

    if store_option == 'single':
        if bw2_project_exists(project_name):
            bw2.projects.set_current(project_name)
        else:
            bw2.projects.set_current(project_name)
            bw2.bw2setup()

    else:    #if store_option == 'unique':

        if not bw2_project_exists(DEFAULT_BIOSPHERE_PROJECT):
            lcopt_biosphere_setup()
        
        bw2.projects.set_current(DEFAULT_BIOSPHERE_PROJECT)
        bw2.projects.copy_project(project_name, switch=True)
            
    if ei_username is not None and ei_password is not None:
        auto_ecoinvent(username=ei_username, password=ei_password)
    else:
        auto_ecoinvent()

    write_search_index(project_name, ei_name, overwrite=overwrite)

    return True

def forwast_autodownload(FORWAST_URL):      

    """
    Autodownloader for forwast database package for brightway. Used by `lcopt_bw2_forwast_setup` to get the database data. Not designed to be used on its own
    """
    dirpath = tempfile.mkdtemp()
    r = requests.get(FORWAST_URL)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(dirpath)
    return os.path.join(dirpath, 'forwast.bw2package')


def lcopt_bw2_forwast_setup(use_autodownload=True, forwast_path=None, db_name=FORWAST_PROJECT_NAME, overwrite=False):        

    """
    Utility function to set up brightway2 to work correctly with lcopt using the FORWAST database instead of ecoinvent

    By default it'll try and download the forwast database as a .bw2package file from lca-net

    If you've downloaded the forwast .bw2package file already you can set use_autodownload=False and forwast_path to point to the downloaded file

    To overwrite an existing version, set overwrite=True
    """

    if use_autodownload:
        
        forwast_filepath = forwast_autodownload(FORWAST_URL)

    elif forwast_path is not None:

        forwast_filepath = forwast_path

    else:
        raise ValueError('Need a path if not using autodownload')

    if storage.project_type  == 'single':
        db_name = storage.single_project_name
        if bw2_project_exists(db_name):
            bw2.projects.set_current(db_name)
        else:
            bw2.projects.set_current(db_name)
            bw2.bw2setup()

    else:
    
        if db_name in bw2.projects:
            if overwrite:                                           
                bw2.projects.delete_project(name=db_name, delete_dir=True)
            else:
                print('Looks like bw2 is already set up for the FORWAST database - if you want to overwrite the existing version run lcopt.utils.lcopt_bw2_forwast_setup in a python shell using overwrite = True')
                return False

        # no need to keep running bw2setup - we can just copy a blank project which has been set up before
        if not bw2_project_exists(DEFAULT_BIOSPHERE_PROJECT):
            lcopt_biosphere_setup()
        
        bw2.projects.set_current(DEFAULT_BIOSPHERE_PROJECT)
        bw2.projects.copy_project(db_name, switch=True)

    bw2.BW2Package.import_file(forwast_filepath)

    return True

def create_search_index(project_name, ei_name):
    
    keep = ['database',
            'location',
            'name',
            'reference product',
            'unit',
            'production amount',
            'code',
            'activity']

    bw2.projects.set_current(project_name)
    db = bw2.Database(ei_name)

    print("Creating {} search index".format(ei_name))

    search_dict = {k: {xk: xv for xk, xv in v.items() if xk in keep} for k, v in db.load().items()}

    return search_dict


