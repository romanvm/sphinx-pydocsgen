#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import datetime

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, os.path.join(basedir, '{{ dirname }}'))

{% for module in modules %}
import {{ module.name }}
{% endfor %}

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.autosummary',
]

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

project = '{{ project_name }}'
copyright = '{0}, {{ author }}'.format(datetime.datetime.now().year)
author = '{{ author }}'

version = '{{ version }}'
release = version

language = None

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

pygments_style = 'sphinx'

todo_include_todos = False

html_theme = 'alabaster'

html_theme_options = {
    'font_family': 'Georgia',
}

html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',
        'searchbox.html',
    ]
}

html_static_path = ['_static']

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

latex_documents = [
    (master_doc, '{{ project_name }}.tex', '{{ project_name }} Documentation',
     author, 'manual'),
]

man_pages = [
    (master_doc, '{{ project_name }}', '{{ project_name }} Documentation',
     [author], 1)
]

texinfo_documents = [
    (master_doc, '{{ project_name }}', '{{ project_name }} Documentation',
     author, '{{ project_name }}', 'One line description of project.',
     'Miscellaneous'),
]

epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

epub_exclude_files = ['search.html']

intersphinx_mapping = {
    'https://docs.python.org/{0}.{1}'.format(sys.version[0], sys.version[1]): None
}
