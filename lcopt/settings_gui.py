from flask import Flask, request, render_template, redirect, send_file
import webbrowser
from .settings import LcoptSettings
from .constants import DEFAULT_SINGLE_PROJECT
from .utils import find_port


KNOWN_SETTINGS = {
                    'ecoinvent':['username', 'password', 'version', 'system_model'],
                    'model_storage': ['location', 'project', 'single_project_name']
                 }

KNOWN_SETTINGS_META = {
                        ('ecoinvent', 'username'): {'type':'text', 'label':'username'},
                        ('ecoinvent', 'password'): {'type': 'password', 'label':'password'},
                        ('ecoinvent', 'version'): {'type':'select', 'label':'version', 'options':[('3.01', '3.01'),('3.1', '3.1'),('3.2', '3.2'),('3.3', '3.3'),('3.4', '3.4'),]},
                        ('ecoinvent', 'system_model'): {'type':'select', 'label':'system model', 'options':[('cutoff', 'Cut-off'), ('apos', 'Allocation at the Point of Substitution (APOS)'), ('consequential', 'Consequential')]},
                        ('model_storage', 'location'): {'type':'select', 'label':'save location', 'options':[('appdir', 'Application directory'), ('curdir', 'Current directory')]},
                        ('model_storage', 'project'): {'type':'select', 'label':'project setup', 'options':[('single', 'One project containing all lcopt models'), ('unique', 'Each lcopt model has a separate project')]},
                        ('model_storage', 'single_project_name'): {'type':'text', 'label':'single project name'},
                      }                



class FlaskSettingsGUI():
    
    def __init__(self):
        self.settings = LcoptSettings(autowrite=False)

    def shutdown_server(self):                             # pragma: no cover
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()

    def create_app(self):

        app = Flask(__name__)

        def uc_first(string):
            return string[0].upper() + string[1:]

        app.jinja_env.filters['uc_first'] = uc_first

        @app.route('/')
        def index():
            settings_dict = self.settings.as_dict()
            if 'single_project_name' not in settings_dict['model_storage'].keys():
                settings_dict['model_storage']['single_project_name'] = DEFAULT_SINGLE_PROJECT

            args = {
                    'settings':settings_dict,
                    'known_settings':KNOWN_SETTINGS,
                    'known_settings_meta':KNOWN_SETTINGS_META,
                    }
            return render_template('lcopt_settings.html', args=args)


        @app.route('/shutdown')
        def shutdown():                             # pragma: no cover
            self.shutdown_server()
            return render_template('shutdown.html')

        @app.route('/save_settings', methods=['POST'])
        def save_settings():

            f = request.form

            for k, v in f.items():
                section, item = k.split("|")
                setattr(getattr(self.settings, section), item, v)

            self.settings.write()

            self.shutdown_server()
            
            return render_template('settings_saved.html')

        @app.route('/settings_cancel')
        def cancel_settings():                             # pragma: no cover
            self.shutdown_server()
            return render_template('settings_cancel.html')

        return app

    def run(self, port=None, open_browser=True):                      # pragma: no cover
        app = self.create_app()

        if port is None:
            port = find_port()

        if open_browser:
            url = 'http://127.0.0.1:{}/'.format(port)
            webbrowser.open_new(url)

        app.run(port=port)


settingsGUI = FlaskSettingsGUI()
