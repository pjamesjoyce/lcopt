import os
import yaml
import glob
import shutil

import appdirs

from .constants import (ASSET_PATH,
                        BIOSPHERE_SI, 
                        FORWAST_SI, 
                        ECOINVENT_EXAMPLE, 
                        FORWAST_EXAMPLE,
                        DEFAULT_CONFIG,
                        DEFAULT_SINGLE_PROJECT,
                        DEFAULT_ECOINVENT_VERSION,
                        DEFAULT_ECOINVENT_SYSTEM_MODEL,
                        DEFAULT_SAVE_OPTION,
                        DEFAULT_PROJECT_TYPE)

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

        # Copy the example models
        if not os.path.isfile(os.path.join(self.model_dir, ECOINVENT_EXAMPLE)):
            shutil.copy(os.path.join(ASSET_PATH, ECOINVENT_EXAMPLE), os.path.join(self.model_dir, ECOINVENT_EXAMPLE))

        if not os.path.isfile(os.path.join(self.model_dir, FORWAST_EXAMPLE)):
            shutil.copy(os.path.join(ASSET_PATH, FORWAST_EXAMPLE), os.path.join(self.model_dir, FORWAST_EXAMPLE))

        # config
        self.config_file = os.path.join(self.lcopt_dir, 'lcopt_config.yml')
        if not os.path.exists(self.config_file):
            self.write_default_config()

        self.config = self.load_config()

        # Search indices
        self.search_index_dir = os.path.join(self.lcopt_dir, 'search')
        if not os.path.isdir(self.search_index_dir):
            os.mkdir(self.search_index_dir)

        # copy the default search indices
        if not os.path.isfile(os.path.join(self.search_index_dir, BIOSPHERE_SI)):
            shutil.copy(os.path.join(ASSET_PATH, BIOSPHERE_SI), os.path.join(self.search_index_dir, BIOSPHERE_SI))

        if not os.path.isfile(os.path.join(self.search_index_dir, FORWAST_SI)):
            shutil.copy(os.path.join(ASSET_PATH, FORWAST_SI), os.path.join(self.search_index_dir, FORWAST_SI))

        # lcoptview files
        self.lcoptview_dir = os.path.join(self.lcopt_dir, 'lcoptview')
        if not os.path.isdir(self.lcoptview_dir):
            os.mkdir(self.lcoptview_dir)

        # disclosures
        self.disclosures_dir = os.path.join(self.lcopt_dir, 'disclosures')
        if not os.path.isdir(self.disclosures_dir):
            os.mkdir(self.disclosures_dir)

        # simapro
        self.simapro_dir = os.path.join(self.lcopt_dir, 'simapro')
        if not os.path.isdir(self.simapro_dir):
            os.mkdir(self.simapro_dir)

    def load_config(self):
        with open(self.config_file, 'r') as cf:
            config = yaml.safe_load(cf)
        if config is None:
            self.write_default_config()
            config = DEFAULT_CONFIG
        return config

    def refresh(self):
        with open(self.config_file, 'r') as cf:
            self.config = yaml.safe_load(cf)

    def write_default_config(self):
        self.write_config(DEFAULT_CONFIG)

    def write_config(self, config):
         with open(self.config_file, 'w') as cfg:
                yaml.dump(config, cfg, default_flow_style=False)
                self.refresh()


    @property
    def models(self):
        models = glob.glob(os.path.join(self.model_dir, '*.lcopt'))
        return models

    @property
    def search_indices(self):
        search_indices = glob.glob(os.path.join(self.search_index_dir, '*.pickle'))
        return search_indices

    @property
    def project_type(self):
        if 'model_storage' in self.config:
            store_option = self.config['model_storage'].get('project', DEFAULT_PROJECT_TYPE)
        else:
            store_option = 'unique'
        return store_option

    @property
    def single_project_name(self):

        project_name = None
        
        if 'model_storage' in self.config:
            if self.config['model_storage'].get('project') == 'single':
                project_name = self.config['model_storage'].get('single_project_name', DEFAULT_SINGLE_PROJECT)
       
        return project_name

    @property
    def ecoinvent_version(self):

        version = None

        if 'ecoinvent' in self.config:
            version = self.config['ecoinvent'].get('version', DEFAULT_ECOINVENT_VERSION)

        return version
    
    @property
    def ecoinvent_system_model(self):

        system_model = None

        if 'ecoinvent' in self.config:
            system_model = self.config['ecoinvent'].get('system_model', DEFAULT_ECOINVENT_SYSTEM_MODEL)

        return system_model

    @property
    def save_option(self):

        save_option = None

        if 'model_storage' in self.config:
            save_option = self.config['ecoinvent'].get('location', DEFAULT_SAVE_OPTION)

        return save_option


storage = LcoptStorage()
