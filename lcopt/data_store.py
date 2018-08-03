import os
import yaml
import glob

import appdirs


class LcoptStorage():
    def __init__(self):
        self.lcopt_dir = appdirs.user_data_dir(
            appname='Lcopt',
            appauthor='Lcopt'
        )
        if not os.path.isdir(self.lcopt_dir):
            os.makedirs(self.lcopt_dir)

        # Models
        self.model_dir = os.path.join(self.lcopt_dir, 'models')
        if not os.path.isdir(self.model_dir):
            os.mkdir(self.model_dir)

        # config
        self.config_file = os.path.join(self.lcopt_dir, 'lcopt_config.yml')
        if not os.path.exists(self.config_file):
            with open(self.config_file, 'w') as cfg:
                cfg.write("")

        self.config = self.load_config()

    def load_config(self):
        with open(self.config_file, 'r') as cf:
            config = yaml.load(cf)
            return config

    @property
    def models(self):
        models = glob.glob(os.path.join(self.model_dir, '*.lcopt'))
        return models


storage = LcoptStorage()
