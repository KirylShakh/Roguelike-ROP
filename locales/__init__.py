import os
import glob
import ntpath

from ruamel.yaml import YAML


class Locale:
    def __init__(self, locale=None):
        self.default_locale = 'en'

        if locale:
            self.locale = locale
        else:
            self.locale = self.default_locale

        self.setup()

    def setup(self):
        path = os.path.join('locales', self.locale, '*.yaml')
        locale_files = glob.glob(path)

        yaml = YAML(typ='safe')
        self.data = {}
        for filename in locale_files:
            f = open(filename, 'r')
            key = os.path.splitext(ntpath.basename(filename))[0]
            self.data[key] = yaml.load(f)

    def t(self, path, *args):
        keys = path.split('.')
        result = self.data
        for key in keys:
            result = result[key]
        return result.format(*args)

locale = Locale()
