# Created on: 23.01.2017
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)

import inspect
import os
import pkgutil
import sys
from collections import namedtuple
from jinja2 import Template

current_dir = os.path.dirname(os.path.abspath(__file__))
templates = os.path.join(current_dir, 'templates')

ModuleContents = namedtuple('ModuleContents',
                            ['variables', 'functions', 'classes'])
ModuleData = namedtuple('ModuleData', ['name', 'docstring', 'contents'])


LITERALS = (int, float, str, tuple, list, dict, set)


class PydocsgenError(Exception):
    pass


def is_empty(mod):
    """
    Check if a module or a package contains a module-level docstring
    or vairables/functions/classes

    :param mod: :class:`ModuleInfo` object
    :type mod: ModuleInfo
    :return: ``True`` if a module/package is "empty"
    :rtype: bool
    """
    return not (mod.docstring or
                mod.contents.variables or
                mod.contents.functions or
                mod.contents.classes)


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
    return pkgutil.walk_packages([os.path.join(cwd, src_dir)], prefix=prefix)


def analyze_module(module):
    """
    Extract lists of variables/functions/classes
    from a module object

    :param module: module object
    :type module: types.ModuleType
    :return: contents of a module object
    :rtype: ModuleContents
    """
    contents = ModuleContents([], [], [])
    for name, obj in inspect.getmembers(module):
        try:
            imported = obj.__module__ != module.__name__
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
    Extract info from :class:`pkgutil.ModuleInfo` objects

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
        yield ModuleData(mod.name, inspect.getdoc(mod_obj), mod_contents)


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


def render_index(non_empty_modules, project_name=None, readme=None):
    """
    Render the index page

    :param non_empty_modules: the list of non-empty packages/modules
    :type non_empty_modules: list
    :param project_name: the name of the project
    :type project_name: str
    :param readme: project's Readme contents
    :type readme: str
    :return: rendered ``.rst`` for the index page
    :rtype: str
    """
    with open(os.path.join(templates, 'index.rst'), 'r', encoding='utf-8') as fo:
        raw_index = fo.read()
    template = Template(raw_index)
    if project_name is not None:
        header = 'Welcome to {0} documentation!'.format(project_name)
    else:
        header = ''
    return template.render(header=header,
                           underline='=' * len(header),
                           modules=non_empty_modules,
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
    non_empty_modules = [mod for mod in modules if not is_empty(mod)]
    if not os.path.exists(docs_dir):
        os.mkdir(docs_dir)
    for mod in non_empty_modules:
        mod_rst = render_module(mod)
        with open(os.path.join(docs_dir, mod.name + '.rst'),
                  'w', encoding='utf-8') as fo:
            fo.write(mod_rst)
    if readme_file is not None:
        with open(readme_file, 'r', encoding='utf-8') as fo:
            readme = fo.read()
    else:
        readme = None
    modules_rst = render_index(non_empty_modules)
    with open(os.path.join(docs_dir, 'modules.rst'),
              'w', encoding='utf-8') as fo:
        fo.write(modules_rst)
    index_rst = render_index(non_empty_modules, project_name, readme)
    with open(os.path.join(docs_dir, 'index.rst'), 'w', encoding='utf-8') as fo:
        fo.write(index_rst)
