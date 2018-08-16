from .data_store import storage
import yaml
import types


ALLOWED_TYPES = [str, bool, int, float]

class SettingsDict(object):
    
    _allowed_types = tuple([types.MethodType, tuple] + ALLOWED_TYPES)

    def __init__(self, contents, write_function, **kwargs):

        self._autowrite = False # disable autowriting for initialisation
        
        self.write = write_function # set the write function to the callback from the parent instantiation

        self._allowed_types = tuple(ALLOWED_TYPES)

        for k, v in contents.items(): # write the contents of the config dict to the SettingsDict
            setattr(self, k, str(v))

        self._autowrite = kwargs.get('autowrite', True) # set the autowrite attribute (default is True)

        

    def __repr__(self):

        string = "Lcopt settings section with the following entries:\n\n"

        for k, v in self.as_dict().items():
            string += "{}: {}\n".format(k,v)

        return string


    def __setattr__(self, name, value):

        if isinstance(value, self._allowed_types): # only allow certain types of variable to be specified 
            object.__setattr__(self, name, value) # run the default version from object
        else:
            raise TypeError("Attribute '{}' ({}) of type {} is not able to be stored in a SettingsDict.\nAllowed types are {}".format(name, value, type(value), self._allowed_types))
        
        # write the settings
        if self._autowrite:
            self.write()

    def delete(self, attr):
        try:
            delattr(self, attr)
            if self._autowrite:
                self.write()
        except AttributeError:
            raise AttributeError('{} does not exist'.format(attr))

    def as_dict(self):
        d = {}
        attributes = [a for a in dir(self) if not a.startswith('_') and not callable(getattr(self,a))]
        for k in attributes:#self._keys:
            d[k] = str(getattr(self, k))
        return d

class LcoptSettings(object):

    def __init__(self, **kwargs):

        self.refresh(**kwargs)
        self.write() # if floats get conveted to strings during setup, it might auto-overwite with a partial config - this makes sure it doesn't

    def as_dict(self):
        d = {}
        for k in self._sections:
            d[k] = getattr(self, k).as_dict()
        return d

    def __repr__(self):

        string = ""

        for section, content in self.as_dict().items():
            string += "{}:\n".format(section)
            for k, v in content.items():
                string += "\t{}: {}\n".format(k,v)

        return "Lcopt settings: \n\n{}".format(string)

    def refresh(self, **kwargs):

        self.config = storage.load_config()

        self._sections = []

        for section, content in self.config.items():
            setattr(self, section, SettingsDict(content, self.write, **kwargs))
            self._sections.append(section)


    def write(self):
        """write the current settings to the config file"""
        with open(storage.config_file, 'w') as cfg:
            yaml.dump(self.as_dict(), cfg, default_flow_style=False)

        storage.refresh()

    def launch_interact(self):
        from .settings_gui import FlaskSettingsGUI
        s = FlaskSettingsGUI()
        s.run()
        self.refresh()
        self.write()

settings = LcoptSettings()