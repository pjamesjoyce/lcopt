from lcopt.bw2_import import create_LcoptModel_from_BW2Package
from lcopt.model import LcoptModel
import os

BW2PACKAGE_NAME = "Sample_Db.1499a346648778a2d15b5c7e7e9d82d2.bw2package"


def test_import():

    bw2package_path = r"assets/{}".format(BW2PACKAGE_NAME)
    script_path = os.path.dirname(os.path.realpath(__file__))
    loadpath = os.path.join(script_path, bw2package_path)
    imported_model = create_LcoptModel_from_BW2Package(loadpath)

    assert type(imported_model) == LcoptModel
