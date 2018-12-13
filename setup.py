#!/usr/bin/env python
# Based on astropy affiliated package template's setup.py
# Licensed under a 3-clause BSD style license - see LICENSE.md
from __future__ import print_function

import glob
import os
import sys
import imp
import ast

__packagename__ = 'webbpsf'
__minimum_python_version__ = "3.5"

print("*************************************************")
print("*************************************************")
print("*************************************************")
print("*************************************************")
print("*************************************************")
print("*************************************************")
print("*************************************************")
print("*************************************************")


# Enforce Python version check - this is the same check as in __init__.py but
# this one has to happen before importing ah_bootstrap.
if sys.version_info < tuple((int(val) for val in __minimum_python_version__.split('.'))):
    sys.stderr.write("ERROR: {} requires Python {} or later\n".format(__packagename__, __minimum_python_version__))
    sys.exit(1)

try:
    import numpy
except ImportError:
    print("""
WARNING: NumPy was not found! setup.py will attempt to install it if asked, but
\tyou may experience issues. Try installing NumPy first, separately.
\tSee https://github.com/numpy/numpy/issues/2434 for details.
""")

#import ah_bootstrap
from setuptools import setup, Command
from setuptools.command.test import test as TestCommand

#A dirty hack to get around some early import/configurations ambiguities
if sys.version_info[0] >= 3:
    import builtins
else:
    import __builtin__ as builtins
builtins._ASTROPY_SETUP_ = True

##from astropy_helpers.setup_helpers import (
##    register_commands, get_debug_option, get_package_info)
##from astropy_helpers.git_helpers import get_git_devstr
##from astropy_helpers.version_helpers import generate_version_py

# Get some values from the setup.cfg
try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

conf = ConfigParser()
conf.read(['setup.cfg'])
metadata = dict(conf.items('metadata'))

PACKAGENAME = metadata.get('package_name', 'packagename')
DESCRIPTION = metadata.get('description', 'Astropy affiliated package')
AUTHOR = metadata.get('author', '')
AUTHOR_EMAIL = metadata.get('author_email', '')
LICENSE = metadata.get('license', 'unknown')
URL = metadata.get('url', 'http://astropy.org')

# Get the long description from the package's docstring
_, module_path, _ = imp.find_module(PACKAGENAME)
with open(os.path.join(module_path, '__init__.py')) as f:
    module_ast = ast.parse(f.read())
LONG_DESCRIPTION = ast.get_docstring(module_ast)

# Store the package name in a built-in variable so it's easy
# to get from other parts of the setup infrastructure
builtins._ASTROPY_PACKAGE_NAME_ = PACKAGENAME

# VERSION should be PEP386 compatible (http://www.python.org/dev/peps/pep-0386)
VERSION = '0.7.1dev'

# Indicates if this version is a release version
RELEASE = 'dev' not in VERSION

if not RELEASE:
    VERSION += get_git_devstr(False)

# Populate the dict of setup command overrides; this should be done before
# invoking any other functionality from distutils since it can potentially
# modify distutils' behavior.
##cmdclassd = register_commands(PACKAGENAME, VERSION, RELEASE)
##
##
### Freeze build information in version.py
##generate_version_py(PACKAGENAME, VERSION, RELEASE,
                    get_debug_option(PACKAGENAME))

# Treat everything in scripts except README.rst as a script to be installed
scripts = [fname for fname in glob.glob(os.path.join('scripts', '*'))
           if os.path.basename(fname) != 'README.rst']


# Get configuration information from all of the various subpackages.
# See the docstring for setup_helpers.update_package_files for more
# details.
##package_info = get_package_info()

# Add the project-global data
package_info['package_data'].setdefault(PACKAGENAME, [])
package_info['package_data'][PACKAGENAME].append('data/*')
package_info['package_data'][PACKAGENAME].append('otelm/*')

# Include all .c files, recursively, including those generated by
# Cython, since we can not do this in MANIFEST.in with a "dynamic"
# directory name.
c_files = []
for root, dirs, files in os.walk(PACKAGENAME):
    for filename in files:
        if filename.endswith('.c'):
            c_files.append(
                os.path.join(
                    os.path.relpath(root, PACKAGENAME), filename))
package_info['package_data'][PACKAGENAME].extend(c_files)


# allows you to build sphinx docs from the pacakge
# main directory with python setup.py build_sphinx

try:
    from sphinx.cmd.build import build_main
    from sphinx.setup_command import BuildDoc

    class BuildSphinx(BuildDoc):
        """Build Sphinx documentation after compiling C source files"""

        description = 'Build Sphinx documentation'

        def initialize_options(self):
            BuildDoc.initialize_options(self)

        def finalize_options(self):
            BuildDoc.finalize_options(self)

        def run(self):
            build_cmd = self.reinitialize_command('build_ext')
            build_cmd.inplace = 1
            self.run_command('build_ext')
            build_main(['-b', 'html', './docs', './docs/_build/html'])

except ImportError:
    class BuildSphinx(Command):
        user_options = []

        def initialize_options(self):
            pass

        def finalize_options(self):
            pass

        def run(self):
            print('!\n! Sphinx is not installed!\n!', file=sys.stderr)
            exit(1)


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['packagename/tests']
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(name=PACKAGENAME,
      version=VERSION,
      description=DESCRIPTION,
      scripts=scripts,
      python_requires='>=' + __minimum_python_version__,
      install_requires=[
          'numpy>=1.10.0',
          'matplotlib>=1.5.0',
          'scipy>=0.16.0',
          'poppy>=0.7.0',
          'astropy>=1.3.0',
          'jwxml>=0.3.0',
          'pysiaf>=0.1.8', 'six',
      ],
      provides=[PACKAGENAME],
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      license=LICENSE,
      url=URL,
      long_description=LONG_DESCRIPTION,
      cmdclass=cmdclassd,
      zip_safe=False,
      **package_info
)
