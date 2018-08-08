from .data_store import storage
import yaml

class SettingsDict(object):
    def __init__(self, contents):

        for k, v in contents.items():
            setattr(self, k, v)

    def __repr__(self):

        string = "Lcopt settings section with the following entries:\n\n"

        for k, v in self.as_dict().items():
            string += "{}: {}\n".format(k,v)

        return string

    def __getattr__(self, name, value=None):
        """edit __getattr__ to allow dot notation writing of attributes to a SettingsDict object"""
        try:
            ret_value = object.__getattribute__(self, name)    

        except AttributeError:
            if value is not None:
                setattr(self, name, value)
                
        ret_value = object.__getattribute__(self, name)

        return ret_value

    def delete(self, attr):
        try:
            delattr(self, attr)
        except AttributeError:
            raise AttributeError('{} does not exist'.format(attr))

    def as_dict(self):
        d = {}
        attributes = [a for a in dir(self) if not a.startswith('_') and not callable(getattr(self,a))]
        for k in attributes:#self._keys:
            d[k] = getattr(self, k)
        return d

class LcoptSettings(object):

    def __init__(self):

        self.config = storage.load_config()

        self._sections = []

        for section, content in self.config.items():
            setattr(self, section, SettingsDict(content))
            self._sections.append(section)

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


    def write(self):
        """write the current settings to the config file"""
        with open(storage.config_file, 'w') as cfg:
            yaml.dump(self.as_dict(), cfg, default_flow_style=False)

        storage.refresh()

settings = LcoptSettings()