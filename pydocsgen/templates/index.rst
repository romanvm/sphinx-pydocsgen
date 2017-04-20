{%- if header %}
{{ header }}
{{ underline }}
{% endif %}
{% if readme %}
{{ readme }}
{% endif %}

API Reference
-------------

.. toctree::
  :maxdepth: 2

{% for module in modules %}
  {{ module.name }}
{% endfor %}

{% if header or readme %}
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
{% endif %}
