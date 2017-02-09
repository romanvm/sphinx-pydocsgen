{{ module.name }}
{{ underline }}

.. automodule:: {{ module.name }}
{% if module.contents.variables %}
  .. rubric:: Variables

  .. autosummary::
{% for variable in module.contents.variables %}
    {{ variable }}
{%- endfor %}
{%- endif %}

{% if module.contents.functions %}
  .. rubric:: Functions

  .. autosummary::
{% for function in module.contents.functions %}
    {{ function }}
{%- endfor %}
{%- endif %}

{% if module.contents.classes %}
  .. rubric:: Classes

  .. autosummary::

{% for class in module.contents.classes %}
    {{ class }}
{%- endfor %}
{%- endif %}

{% if module.contents.variables or module.contents.functions or module.contents.classes %}
-----
{% endif %}

{% for variable in module.contents.variables %}
.. autodata:: {{ variable }}
{% endfor %}

{% for function in module.contents.functions %}
.. autofunction:: {{ function }}
{% endfor %}

{% for class in module.contents.classes %}
.. autoclass:: {{ class }}
  :members:
  :undoc-members:
  :show-inheritance:
  :special-members: __init__
{% endfor %}
