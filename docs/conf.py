# -*- coding: utf-8 -*-
import pkg_resources

version = release = pkg_resources.get_distribution('lilac').version

extensions = ['sphinx.ext.autodoc']

source_suffix = '.rst' # The suffix of source filenames.
master_doc = 'index' # The master toctree document.

project = 'lilac'
copyright = '2014, Thomas and contributors'
exclude_patterns = ['jsonrpc-example-code/*']

modindex_common_prefix = ['lilac.']

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True


# html_favicon = ...
html_add_permalinks = False
#html_show_sourcelink = True # ?set to False?

# Content template for the index page.
#html_index = ''

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# Output file base name for HTML help builder.
htmlhelp_basename = 'lilacdoc'