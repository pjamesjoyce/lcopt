from lcopt import *

def test_createModel():
	model = LcoptModel('testModel')

	assert isinstance(model, LcoptModel)