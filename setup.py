from setuptools import setup, find_packages
import sys
from lilac import __version__

setup(
    name = 'lilac',
    version = __version__,
    author = "Thomas Huang",
    author_email='lyanghwy@gmail.com',
    description = "A Python Distributed Task System",
    license = "GPL",
    keywords = "Python Distributed Task System",
    url='https://github.com/thomashuang/Lilac',
    long_description=open('README.rst').read(),
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    package_data = {
              # Non-.py files to distribute as part of each package
              'lilac': ['assets/css/*','assets/js/*', 'views/*']
    },
    install_requires = ['setuptools', 'solo', 'dbpy'],
    test_suite='unittests',
    classifiers=(
        "Development Status :: Production/Alpha",
        "License :: GPL",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Scheduler"
        )
    )
