{%- if header %}
{{ header }}
{{ underline }}
{% endif %}
{%- if readme %}
.. include:: {{ readme }}
{% endif %}

API Reference
-------------

.. toctree::
  :maxdepth: 2

{% for module in modules %}
  {{ module.name }}
{% endfor %}

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
