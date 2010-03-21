import os
from pkg_resources import resource_filename

from chameleon.zpt import language
from chameleon.zpt.template import PageTemplateFile

def cache(func):
    def load(self, *args):
        template = self.registry.get(args)
        if template is None:
            self.registry[args] = template = func(self, *args)
        return template
    return load

class TemplateError(Exception):
    pass

class ChameleonZPTTemplateLoader(object):
    parser = language.Parser()

    def __init__(self, search_path=None, auto_reload=False):
        if search_path is None:
            search_path = []
        if isinstance(search_path, basestring):
            search_path = [search_path]
        self.search_path = search_path
        self.auto_reload = auto_reload
        self.registry = {}
        self.notexists = {}

    @cache
    def load(self, filename):
        for path in self.search_path:
            path = os.path.join(path, filename)
            if (path in self.notexists) and (not self.auto_reload):
                raise TemplateError("Can not find template %s" % filename)
            try:
                return PageTemplateFile(path, parser=self.parser,
                                        auto_reload=self.auto_reload)
            except OSError:
                self.notexists[path] = True

        raise TemplateError("Can not find template %s" % filename)

def make_default_renderer():
    defaultdir = resource_filename('deform', 'templates') + '/'
    loader = ChameleonZPTTemplateLoader([defaultdir])

    def renderer(template, **kw):
        return loader.load(template)(**kw)

    return renderer

default_renderer = make_default_renderer()

