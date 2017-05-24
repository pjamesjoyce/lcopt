from lcopt.utils import *
from fixtures import *
import brightway2 as bw2

import os

def test_lcopt_bw_build():
	if IS_TRAVIS:
		pass
	else:
		assert lcopt_bw2_setup_local()

def lcopt_bw2_setup_local():
	
	script_path = os.path.dirname(os.path.realpath(__file__))
	ecospold_folder = "assets"
	ecospold_path = os.path.join(script_path, ecospold_folder)
	print(ecospold_path)
	assert lcopt_bw2_setup(ecospold_path, overwrite = True, db_name = 'LCOPT_TESTING_DO_NOT_USE')

	import brightway2 as bw2

	# tear down the testing project
	bw2.projects.delete_project(name=db_name, delete_dir=True)	

	assert db_name not in bw2.projects
	
	return True

