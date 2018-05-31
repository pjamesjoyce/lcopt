import pytest
import os
import brightway2 as bw2

TEST_MODEL_NAME = "Test_model"

@pytest.fixture(scope="session", autouse=True)
def setup_fixtures(request):

	print('RUNNING SETUP FIXTURE')
	bw2.projects.purge_deleted_directories()
	if TEST_MODEL_NAME in bw2.projects:
		bw2.projects.delete_project(name=TEST_MODEL_NAME, delete_dir=True)

	bw2.projects.set_current(TEST_MODEL_NAME)
	bw2.bw2setup()
	

	script_path = os.path.dirname(os.path.realpath(__file__))
	ecospold_folder = os.path.join("tests", "assets", "datasets")
	ecospold_path = os.path.join(script_path, ecospold_folder)
	print(ecospold_path)

	ei = bw2.SingleOutputEcospold2Importer(ecospold_path, "Ecoinvent3_3_cutoff")
	ei.apply_strategies()
	ei.statistics()
	ei.write_database()

	bw2.projects.set_current('default')
	
	def teardown_fixtures():
		print('TEAR IT DOWN!!')
		bw2.projects.set_current('default')
		
		if TEST_MODEL_NAME in bw2.projects:
			bw2.projects.delete_project(name=TEST_MODEL_NAME)#, delete_dir=True)
			#bw2.projects.purge_deleted_directories()
	
	request.addfinalizer(teardown_fixtures)




