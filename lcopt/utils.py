"""
lcopt.utils
-----------

Module containing the utility function to set up brightway2 to work with lcopt

"""

try:
    import brightway2 as bw2
except:															# pragma: no cover
    raise ImportError('Please install the brightway2 package first')

DEFAULT_DB_NAME = "LCOPT_Setup"

def lcopt_bw2_setup(ecospold_path, overwrite = False, db_name = DEFAULT_DB_NAME): # pragma: no cover

	"""
	Utility function to set up brightway2 to work correctly with lcopt.

	It requires the path to the ecospold files containing the Ecoinvent 3.3 cutoff database.

	If you don't have these files, log into `ecoinvent.org  <http://www.ecoinvent.org/login-databases.html>`_ and go to the Files tab

	Download the file called ``ecoinvent 3.3_cutoff_ecoSpold02.7z``

	Extract the file somewhere sensible on your machine, you might need to download `7-zip <http://www.7-zip.org/download.html>`_ to extract the files.

	Make a note of the path of the folder that contains the .ecospold files, its probably ``<path/extracted/to>/datasets/``

	Use this path (as a string) as the first parameter in this function
	"""

	if db_name in bw2.projects:
		if overwrite:											
			bw2.projects.delete_project(name=db_name, delete_dir=True)
		else:
			print('Looks like bw2 is already set up - if you want to overwrite the existing version, use overwrite = True')
			return False

	bw2.projects.set_current(db_name)
	bw2.bw2setup()
	ei = bw2.SingleOutputEcospold2Importer(ecospold_path, "Ecoinvent3_3_cutoff")
	ei.apply_strategies()
	ei.statistics()
	ei.write_database()

	return True




