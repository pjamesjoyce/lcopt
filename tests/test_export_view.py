from fixtures import *
from lcopt.export_view import LcoptView


def test_export_view(fully_formed_model):

    myView = LcoptView(fully_formed_model)
    assert isinstance(myView, LcoptView)

    myView.export()
    assert 1
