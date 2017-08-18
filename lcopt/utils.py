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

try:
    import brightway2 as bw2
except:                                                         # pragma: no cover
    raise ImportError('Please install the brightway2 package first')

DEFAULT_DB_NAME = "LCOPT_Setup"
FORWAST_DB_NAME = "LCOPT_Setup_Forwast"
FORWAST_URL = r"https://lca-net.com/wp-content/uploads/forwast.bw2package.zip"


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


def forwast_autodownload(FORWAST_URL):      # pragma: no cover 

    """
    Autodowloader for forwast database package for brightway. Used by `lcopt_bw2_forwast_setup` to get the database data. Not designed to be used on its own
    """
    dirpath = tempfile.mkdtemp()
    r = requests.get(FORWAST_URL)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(dirpath)
    return os.path.join(dirpath, 'forwast.bw2package')


def lcopt_bw2_forwast_setup(use_autodownload=True, forwast_path=None, db_name=FORWAST_DB_NAME, overwrite=False):        # pragma: no cover 

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

    print(db_name)
    
    if db_name in bw2.projects:
        if overwrite:                                           
            bw2.projects.delete_project(name=db_name, delete_dir=True)
        else:
            print('Looks like bw2 is already set up for the FORWAST database - if you want to overwrite the existing version run lcopt.utils.lcopt_bw2_forwast_setup in a python shell using overwrite = True')
            return False

    bw2.projects.set_current(db_name)
    bw2.bw2setup()

    bw2.BW2Package.import_file(forwast_filepath)

    return True
