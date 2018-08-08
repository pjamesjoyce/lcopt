from fixtures import *
from lcopt.export_view import LcoptView
from lcopt.export_disclosure import export_disclosure
import os

def test_export_view(fully_formed_model):

    fully_formed_model.save_option = 'appdir'

    myView = LcoptView(fully_formed_model)
    assert isinstance(myView, LcoptView)

    efn = myView.export()
    
    assert  os.path.isfile(efn)


def test_export_disclosure(fully_formed_model):

    fully_formed_model.save_option = 'appdir'

    efn = export_disclosure(fully_formed_model, parameter_set=0, folder_path='tests')

    assert os.path.isfile(efn)