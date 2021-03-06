# coding: utf-8
# Created on: 01.03.2017
# Author: Roman Miroshnychenko aka Roman V.M. (roman1972@gmail.com)

import argparse
import os
import sys
from importlib import import_module
from subprocess import call
import pydocsgen

cwd = os.getcwd()


def parse_args():
    parser = argparse.ArgumentParser(
        description='Automated API documentation generator for Python programs')
    parser.add_argument('source_dir', nargs='?',
                        help='Source directory (required)',
                        action='store')
    parser.add_argument('-o', '--output',
                        help='Output directory (default: "docs")',
                        action='store', default='docs')
    parser.add_argument('-n', '--name',
                        help='Project name (default: source_dir name)',
                        action='store')
    parser.add_argument('-a', '--author',
                        help='Project author (default: "")',
                        action='store', default='')
    parser.add_argument('-v', '--version',
                        help='Project version (default: "")',
                        action='store', default='')
    parser.add_argument('-c', '--conf',
                        help='Generate project\'s conf.py and makefiles '
                             '(default: False)',
                        action='store_true')
    parser.add_argument('-m', '--make',
                        help='Run make <output> to generate output documentation',
                        action='store')
    parser.add_argument('-r', '--readme',
                        help='Add Readme file contents to the index page',
                        action='store', default=None)
    parser.add_argument('--no-header',
                        help='Do not add a header to the index.rst page',
                        action='store_true')
    parser.add_argument('--no-index',
                        help='Do not generate the index.rst page',
                        action='store_true')
    return parser.parse_args()


def main():
    args = parse_args()
    if args.source_dir:
        sys.path.insert(0, cwd)
        try:
            package = import_module(args.source_dir)
        except ImportError:
            package = None
        modules = pydocsgen.get_modules(cwd, args.source_dir, package)
        parsed_modules = pydocsgen.parse_modules(modules, package)
        project_name = args.name or os.path.basename(args.source_dir).capitalize()
        full_docs_dir = os.path.join(cwd, args.output)
        if args.conf:
            pydocsgen.write_sphinx_config(full_docs_dir,
                                          args.source_dir,
                                          parsed_modules,
                                          args.name,
                                          args.author,
                                          args.version
                                          )
        if args.no_header:
            project_name = None
        pydocsgen.write_docs(project_name, parsed_modules, full_docs_dir,
                             args.readme, args.no_index)
        if args.make:
            os.chdir(full_docs_dir)
            call(['make', args.make])
            os.chdir(cwd)
    else:
        raise RuntimeError('You must provide a source directory!')


if __name__ == '__main__':
    main()
