from setuptools import setup, find_packages
import os

version = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 
    'agsci', 'photogallery', 'version.txt')).read().strip()

setup(name='agsci.photogallery',
    version=version,
    description="A Plone package of the Tympanus photo gallery",
    long_description=open("README.txt").read() + "\n" +
                     open("HISTORY.txt").read(),
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
      "Framework :: Plone",
      "Programming Language :: Python",
      "Topic :: Software Development :: Libraries :: Python Modules",
      ],
    keywords='',
    author='Tim Simkins',
    author_email='trs22@psu.edu',
    url='http://agsci.psu.edu/',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['agsci'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
      'setuptools',
      # -*- Extra requirements: -*-
      ],
    entry_points="""
      # -*- Entry points: -*-
      """,
    )

