# Created on: 23.01.2017
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)

import inspect
import os
import pkgutil
import sys
from collections import namedtuple
from jinja2 import Template

this_dir = os.path.dirname(os.path.abspath(__file__))
templates = os.path.join(this_dir, 'templates')

ModuleContents = namedtuple('ModuleContents',
                            ['variables', 'functions', 'classes'])
ModuleData = namedtuple('ModuleData', ['name', 'docstring', 'contents'])
ModuleInfo = namedtuple('ModuleInfo', ['module_finder', 'name', 'ispkg'])


LITERALS = (int, float, str, tuple, list, dict, set)


def not_empty(mod_data):
    """
    Check if a module or a package contains a module-level docstring
    or vairables/functions/classes

    :param mod_data: :class:`ModuleData` object
    :type mod_data: ModuleData
    :return: ``True`` if a module/package contains some data
    :rtype: bool
    """
    return (mod_data.docstring or
            mod_data.contents.variables or
            mod_data.contents.functions or
            mod_data.contents.classes)


def get_modules(cwd, src_dir, is_package):
    """
    Get module objects from a source directory

    :param cwd: current working directory
    :type cwd: str
    :param src_dir: source directory
    :type src_dir: str
    :param is_package: if this is a package
    :type is_package: bool
    :return: generator of :class:`pkgutil.ModuleInfo` objects
    :rtype: types.GeneratorType
    """
    if is_package:
        prefix = src_dir + '.'
    else:
        prefix = ''
    pkg_gen = pkgutil.walk_packages([os.path.join(cwd, src_dir)], prefix=prefix)
    if hasattr(pkgutil, 'ModuleInfo'):  # Python 3.6+
        return pkg_gen
    else:
        return (ModuleInfo(*item) for item in pkg_gen)


def analyze_module(mod):
    """
    Extract lists of variables/functions/classes
    from a module object

    :param mod: module object
    :type mod: types.ModuleType
    :return: contents of a module object
    :rtype: ModuleContents
    """
    contents = ModuleContents([], [], [])
    for name, obj in inspect.getmembers(mod):
        try:
            imported = obj.__module__ != mod.__name__
        except AttributeError:
            imported = False
        if not (name.startswith('_') or imported):
            if isinstance(obj, LITERALS):
                contents.variables.append(name)
            elif inspect.isfunction(obj):
                contents.functions.append(name)
            elif inspect.isclass(obj):
                contents.classes.append(name)
    return contents


def parse_modules(module_infos, package_obj=None):
    """
    Extract info from :class:`pkgutil.ModuleInfo` objects and yield info
    for non-empty modules

    :param module_infos: generator of :class:`pkgutil.ModuleInfo` objects
    :type module_infos: types.GeneratorType
    :param package_obj: root package object
    :type package_obj: types.ModuleObject
    :return: generator of :class:`ModuleInfo` objects
    :rtype: types.GeneratorType
    """
    if package_obj is not None:
        mod_contents = analyze_module(package_obj)
        yield ModuleData(package_obj.__name__,
                         inspect.getdoc(package_obj),
                         mod_contents)
    for mod in module_infos:
        if mod.ispkg:
            sys.path.append(mod.module_finder.path)
        try:
            mod_obj = mod.module_finder.find_module(mod.name).load_module(mod.name)
        except ModuleNotFoundError:
            pass
        mod_contents = analyze_module(mod_obj)
        data = ModuleData(mod.name, inspect.getdoc(mod_obj), mod_contents)
        if not_empty(data):
            yield data


def render_module(mod_data):
    """
    Render a ``.rst`` file with Sphinx autodoc directives for a module

    :param mod_data: module data object
    :type mod_data: ModuleData
    :return: rendered ``.rst`` for a module.
    :rtype: str
    """
    with open(os.path.join(templates, 'module.rst'),
              'r', encoding='utf-8') as fo:
        raw_template = fo.read()
    template = Template(raw_template)
    return template.render(module=mod_data, underline='=' * len(mod_data.name))


def render_index(modules, project_name=None, readme=None, filename='index.rst'):
    """
    Render the index page

    :param modules: the list of packages/modules
    :type modules: list or types.GeneratorType
    :param project_name: the name of the project
    :type project_name: str
    :param readme: project's Readme contents
    :type readme: str
    :param filename: template file name
    :type filename: str
    :return: rendered ``.rst`` for the index page
    :rtype: str
    """
    with open(os.path.join(templates, filename), 'r', encoding='utf-8') as fo:
        raw_index = fo.read()
    template = Template(raw_index)
    if project_name is not None:
        header = 'Welcome to {0} documentation!'.format(project_name)
    else:
        header = ''
    return template.render(header=header,
                           underline='=' * len(header),
                           modules=modules,
                           readme=readme)


def write_docs(project_name, modules, docs_dir, readme_file=None):
    """
    Write ``.rst`` files for the docs

    :param project_name: project name
    :type project_name: str
    :param modules: generator of :class:`ModuleData` objects
    :type modules: types.GeneratorType
    :param docs_dir: output directory for the docs
    :type docs_dir: str
    :param readme_file: path to the project's readme file
    :type readme_file: str
    """
    if not os.path.exists(docs_dir):
        os.mkdir(docs_dir)
    for mod in modules:
        mod_rst = render_module(mod)
        with open(os.path.join(docs_dir, mod.name + '.rst'),
                  'w', encoding='utf-8') as fo:
            fo.write(mod_rst)
    if readme_file is not None:
        with open(readme_file, 'r', encoding='utf-8') as fo:
            readme = fo.read()
    else:
        readme = None
    modules_rst = render_index(modules)
    with open(os.path.join(docs_dir, 'modules.rst'),
              'w', encoding='utf-8') as fo:
        fo.write(modules_rst)
    index_rst = render_index(modules, project_name, readme)
    with open(os.path.join(docs_dir, 'index.rst'), 'w', encoding='utf-8') as fo:
        fo.write(index_rst)
